#!/usr/bin/env python3
"""安装或核验工作台中文、品牌配置与全轨同步补丁。"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import stat
import tempfile
import html


PATCH_ID = "pv-sync-cut-1"
VERSION = "0.8.164"
ASSETS = Path(__file__).resolve().parents[1] / "assets" / "hyperframes-patches" / VERSION
BRAND_PATH = "dist/studio/icons/pv-workbench-brand.js"
BRAND_PREFIX = "window.__PV_WORKBENCH_BRAND__=Object.freeze("
DEFAULT_BRAND = {"name": "视频制作", "mark": "视频"}


class PatchError(ValueError):
    """补丁前置条件不满足。"""


def digest(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def safe_path(root: Path, relative: str = ".", *, must_exist: bool = True) -> Path:
    fragment = Path(relative)
    if fragment.is_absolute() or ".." in fragment.parts:
        raise PatchError(f"补丁路径越界：{relative}")
    path = root.absolute() / fragment
    current = Path(path.anchor)
    for part in path.parts[1:]:
        current = current / part
        try:
            info = current.lstat()
        except FileNotFoundError:
            if must_exist:
                raise PatchError(f"文件不存在：{current}") from None
            continue
        if stat.S_ISLNK(info.st_mode):
            raise PatchError(f"不接受符号链接：{current}")
    return path


def atomic_write(path: Path, data: bytes, mode: int = 0o644) -> None:
    # 所有目标的父目录在预检中确认存在，不创建未知运行时结构。
    descriptor, temporary = tempfile.mkstemp(prefix=".pv-patch-", dir=path.parent)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
            os.fchmod(handle.fileno(), mode)
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def normalize_brand(value: dict) -> dict:
    if not isinstance(value, dict):
        raise PatchError("工作台品牌必须是对象")
    result = {}
    for key, limit in (("name", 32), ("mark", 4)):
        text = value.get(key)
        if not isinstance(text, str) or not text.strip() or len(text) > limit or any(ord(c) < 32 for c in text):
            raise PatchError(f"品牌 {key} 必须是 1 到 {limit} 字的单行文字")
        result[key] = text.strip()
    return result


def brand_script(value: dict) -> bytes:
    brand = normalize_brand(value)
    # 只序列化两项文字；路径、人物、音色等私有档案字段不会进入浏览器。
    svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">'
           '<rect width="64" height="64" rx="15" fill="#b84c2c"/>'
           '<text x="32" y="42" text-anchor="middle" font-family="sans-serif" '
           'font-size="30" font-weight="700" fill="white">' + html.escape(brand['mark']) + '</text></svg>')
    script = BRAND_PREFIX + json.dumps(brand, ensure_ascii=False) + ");\n"
    script += 'document.title=window.__PV_WORKBENCH_BRAND__.name;\n'
    script += 'document.querySelector(\'link[rel="icon"]\').href="data:image/svg+xml,"+encodeURIComponent(' + json.dumps(svg, ensure_ascii=False) + ');\n'
    return script.encode("utf-8")


def read_installed_brand(data: bytes) -> dict:
    try:
        text = data.decode("utf-8")
        if not text.startswith(BRAND_PREFIX):
            raise ValueError("未知格式")
        value, _ = json.JSONDecoder().raw_decode(text[len(BRAND_PREFIX):])
        brand = normalize_brand(value)
        if brand_script(brand) != data:
            raise ValueError("内容不匹配")
        return brand
    except (UnicodeError, ValueError) as error:
        raise PatchError("品牌配置不是本工具生成的有效文件，未作修改") from error


def patch_runtime(runtime: str | Path, *, check: bool = False, assets: Path = ASSETS, brand: dict | None = None) -> dict:
    root = safe_path(Path(runtime).expanduser())
    package = json.loads(safe_path(root, "package.json").read_text())
    if package.get("name") != "hyperframes" or package.get("version") != VERSION:
        raise PatchError(f"仅支持 hyperframes {VERSION}")
    manifest = json.loads(safe_path(assets, "manifest.json").read_text())
    if manifest.get("patch_id") != PATCH_ID or manifest.get("version") != VERSION:
        raise PatchError("补丁清单版本不匹配")
    changes = []
    seen = set()
    for entry in manifest["files"]:
        relative = entry["path"]
        if relative in seen:
            raise PatchError(f"重复补丁目标：{relative}")
        seen.add(relative)
        path = safe_path(root, relative, must_exist=False)
        safe_path(path.parent)
        before = path.read_bytes() if path.exists() and path.is_file() else None
        if path.exists() and not path.is_file():
            raise PatchError(f"目标不是文件：{relative}")
        current_hash = digest(before) if before is not None else None
        if current_hash == entry["after_sha256"]:
            continue
        migration = next((item for item in entry.get("upgrades", []) if item["before_sha256"] == current_hash), None)
        if current_hash != entry.get("before_sha256") and migration is None:
            raise PatchError(f"未知文件哈希，未作任何修改：{relative}")
        if check:
            raise PatchError("运行时尚未安装当前工作台补丁；先运行 workbench_runtime_patch.py")
        if "payload" in entry:
            after = safe_path(assets, entry["payload"]).read_bytes()
        else:
            if before is None:
                raise PatchError(f"缺少原始文件：{relative}")
            text = before.decode("utf-8")
            for replacement in (migration or entry)["replacements"]:
                old, new = replacement["before"], replacement["after"]
                if not old or text.count(old) != 1:
                    raise PatchError(f"补丁定位不唯一：{relative}")
                text = text.replace(old, new, 1)
            after = text.encode("utf-8")
        if digest(after) != entry["after_sha256"]:
            raise PatchError(f"补丁产物哈希不匹配：{relative}")
        changes.append((path, before, after, stat.S_IMODE(path.stat().st_mode) if before is not None else 0o644))
    # 独立配置不写入公开补丁。只接受工具已知格式，并和程序文件一起预检、回滚。
    if manifest.get("private_brand") is True:
        path = safe_path(root, BRAND_PATH, must_exist=False)
        safe_path(path.parent)
        if path.exists() and not path.is_file():
            raise PatchError("品牌配置位置不是文件")
        before = path.read_bytes() if path.exists() else None
        existing = read_installed_brand(before) if before is not None else DEFAULT_BRAND
        chosen = normalize_brand(brand) if brand is not None else existing
        after = brand_script(chosen)
        if before != after:
            if check:
                raise PatchError("品牌配置缺失或与请求不符")
            changes.append((path, before, after, 0o644))
    applied = []
    try:
        for path, before, after, mode in changes:
            # 拒绝预检后被外部进程修改的文件。
            safe_path(root, path.relative_to(root).as_posix(), must_exist=before is not None)
            current = path.read_bytes() if path.exists() else None
            if current != before:
                raise PatchError(f"运行时文件正在变化：{path.name}")
            atomic_write(path, after, mode)
            applied.append((path, before, after, mode))
    except Exception as error:
        rollback_errors = []
        for path, before, installed, mode in reversed(applied):
            try:
                safe_path(root, path.relative_to(root).as_posix())
                if path.read_bytes() != installed:
                    raise PatchError(f"回滚前文件已被其他进程修改，保留当前内容：{path.name}")
                if before is None:
                    path.unlink()
                else:
                    atomic_write(path, before, mode)
            except Exception as rollback_error:
                rollback_errors.append(str(rollback_error))
        if rollback_errors:
            raise PatchError(f"安装失败：{error}；" + "；".join(rollback_errors)) from error
        raise
    return {"patch_id": PATCH_ID, "version": VERSION, "ui_version": manifest.get("ui_version"), "verified": True,
            "changed_files": len(changes), "runtime": str(root), "restart_required": bool(changes)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("runtime", type=Path, help="node_modules/hyperframes 的真实目录")
    parser.add_argument("--check", action="store_true", help="只核验，不写入")
    parser.add_argument("--brand-profile", type=Path, help="包外私有风格档案；只读取 editing_workbench.brand.name / mark")
    args = parser.parse_args()
    try:
        brand = None
        if args.brand_profile:
            profile = safe_path(args.brand_profile.expanduser())
            if profile.stat().st_size > 1024 * 1024:
                raise PatchError("品牌档案过大")
            brand = normalize_brand(json.loads(profile.read_text())["editing_workbench"]["brand"])
        print(json.dumps({"ok": True, **patch_runtime(args.runtime, check=args.check, brand=brand)}, ensure_ascii=False, indent=2))
        return 0
    except (PatchError, OSError, ValueError, KeyError) as error:
        print(json.dumps({"ok": False, "error": str(error)}, ensure_ascii=False))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

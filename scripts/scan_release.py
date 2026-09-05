#!/usr/bin/env python3
"""发布前扫描开源 Skill 中的个人标识和本机路径。"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path


DEFAULT_BANNED = (
    "/" + "Users" + "/",
    "/" + "home" + "/",
    "C:" + "\\Users\\",
    "wx" + "id_",
    "file:" + "//",
)
SECRET_PATTERNS = (
    re.compile(r"(?i)\b(?:api[_-]?key|access[_-]?token|secret[_-]?key|bearer)\s*[:=]\s*[\"']?[A-Za-z0-9_\-]{20,}"),
    re.compile(r"\bsk-[A-Za-z0-9]{20,}\b"),
    re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b"),
    re.compile(r"(?i)-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    re.compile(r"(?i)\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b"),
    re.compile(r"(?<!\d)1[3-9]\d{9}(?!\d)"),
)
BINARY_SUFFIXES = {
    ".png", ".jpg", ".jpeg", ".gif", ".webp", ".wav", ".mp3", ".mp4", ".mov", ".pdf",
    ".zip", ".docx", ".pptx", ".xlsx",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def approved_binaries(root: Path) -> tuple[dict[str, str], list[str]]:
    manifest = root / "examples/manifest.json"
    if not manifest.is_file():
        return {}, []
    try:
        data = json.loads(manifest.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return {}, [f"案例二进制清单无法解析：{exc}"]
    if data.get("public_release_authorized") is not True:
        return {}, ["案例清单未记录公开发布授权"]
    assets = data.get("assets")
    if not isinstance(assets, list):
        return {}, ["案例清单 assets 必须为数组"]
    approved: dict[str, str] = {}
    for index, item in enumerate(assets):
        if not isinstance(item, dict):
            return {}, [f"案例清单 assets[{index}] 必须为对象"]
        path = str(item.get("path", "")).strip()
        expected = str(item.get("sha256", "")).strip().lower()
        if not path or len(expected) != 64:
            return {}, [f"案例清单 assets[{index}] 缺少路径或 SHA-256"]
        approved[path] = expected
    return approved, []


def scan(root: Path, banned: tuple[str, ...], release_root: bool) -> list[str]:
    errors: list[str] = []
    approved, manifest_errors = approved_binaries(root) if release_root else ({}, [])
    errors.extend(manifest_errors)
    for path in sorted(root.rglob("*")):
        if path.is_symlink():
            if release_root:
                errors.append(f"开源包不得包含符号链接：{path.relative_to(root).as_posix()}")
            continue
        if not path.is_file() or ".git" in path.parts:
            continue
        relative = path.relative_to(root).as_posix()
        if release_root and relative.startswith("dist/"):
            continue
        lowered_relative = relative.casefold()
        for term in banned:
            if term.casefold() in lowered_relative:
                errors.append(f"文件名包含禁止标识 {term}：{relative}")
        if path.suffix.casefold() in BINARY_SUFFIXES:
            if release_root:
                expected = approved.get(relative)
                if expected is None:
                    errors.append(f"开源包包含未登记公开授权的二进制文件：{relative}")
                elif sha256(path) != expected:
                    errors.append(f"公开案例文件与清单 SHA-256 不一致：{relative}")
            continue
        try:
            content = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        lowered = content.casefold()
        for term in banned:
            if term.casefold() in lowered:
                errors.append(f"文本包含禁止标识 {term}：{relative}")
        for pattern in SECRET_PATTERNS:
            if pattern.search(content):
                errors.append(f"文本疑似包含密钥或访问令牌：{relative}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="扫描开源 Skill 的个人信息残留")
    parser.add_argument("root", nargs="?", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--project-root", action="append", default=[], help="追加扫描项目目录，可重复使用")
    parser.add_argument("--deny-term", action="append", default=[], help="追加发布者自定义的禁止词，可重复使用")
    parser.add_argument("--deny-file", type=Path, help="包外私人禁止词文件，每行一个；不得复制进 Skill")
    args = parser.parse_args()
    root = args.root.expanduser().resolve()
    if not root.is_dir():
        parser.error(f"Skill 目录不存在：{root}")
    external_terms: list[str] = []
    if args.deny_file:
        deny_file = args.deny_file.expanduser().resolve()
        if not deny_file.is_file():
            parser.error(f"私人禁止词文件不存在：{deny_file}")
        external_terms = [
            line.strip() for line in deny_file.read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.lstrip().startswith("#")
        ]
    banned = (*DEFAULT_BANNED, *(term for term in args.deny_term if term), *external_terms)
    roots = [root, *(Path(item).expanduser().resolve() for item in args.project_root)]
    errors: list[str] = []
    for index, scan_root in enumerate(roots):
        if not scan_root.is_dir():
            parser.error(f"扫描目录不存在：{scan_root}")
        errors.extend(scan(scan_root, banned, release_root=index == 0))
    if errors:
        for error in errors:
            print(f"FAIL {error}")
        return 1
    print("PASS 开源扫描通过：无符号链接、无未审核二进制资产，未发现个人标识、本机路径或密钥")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

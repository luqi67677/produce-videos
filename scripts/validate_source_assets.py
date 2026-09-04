#!/usr/bin/env python3
"""校验用户真实素材盘点，确保风格与镜头工作只使用已展示的来源素材。"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any


SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$", re.IGNORECASE)
VALID_SOURCE_TYPES = {"user-provided", "official", "licensed", "existing-project"}
VALID_PRIVACY_TREATMENTS = {"none", "crop", "opaque-mask", "exclude"}


def nonempty_text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def resolve_path(manifest_path: Path, value: Any) -> Path | None:
    if not nonempty_text(value):
        return None
    candidate = Path(str(value)).expanduser()
    return candidate.resolve() if candidate.is_absolute() else (manifest_path.parent / candidate).resolve()


def validate_file_binding(manifest_path: Path, value: Any, expected_sha: Any, label: str) -> tuple[Path | None, list[str]]:
    target = resolve_path(manifest_path, value)
    if target is None or not target.is_file():
        return target, [f"{label}不存在或不可读取"]
    expected = str(expected_sha or "").strip()
    if not SHA256_PATTERN.fullmatch(expected) or file_sha256(target).casefold() != expected.casefold():
        return target, [f"{label} SHA-256 与实际文件不一致"]
    return target, []


def review_files(path: Path) -> list[Path]:
    files = [path.resolve()]
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return files
    if not isinstance(data, dict):
        return files
    for item in data.get("items", []):
        if isinstance(item, dict):
            target = resolve_path(path, item.get("path"))
            if target is not None:
                files.append(target)
    contact_sheet = resolve_path(path, data.get("contact_sheet_path"))
    if contact_sheet is not None:
        files.append(contact_sheet)
    return list(dict.fromkeys(files))


def validate(path: Path, require_ready: bool = False) -> list[str]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return [f"真实素材清单不存在：{path}"]
    except (OSError, json.JSONDecodeError) as exc:
        return [f"真实素材清单无法解析：{exc}"]
    if not isinstance(data, dict):
        return ["真实素材清单必须为 JSON 对象"]

    errors: list[str] = []
    items = data.get("items")
    if not isinstance(items, list):
        return ["items 必须为数组"]
    if not items and not nonempty_text(data.get("no_real_assets_reason")):
        errors.append("没有真实素材时必须说明 no_real_assets_reason，由用户确认改用生成素材")

    asset_ids: set[str] = set()
    for index, item in enumerate(items):
        label = f"items[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{label} 必须为对象")
            continue
        asset_id = str(item.get("asset_id", "")).strip()
        if not asset_id or asset_id in asset_ids:
            errors.append(f"{label} 缺少唯一 asset_id")
        asset_ids.add(asset_id)
        if item.get("source_type") not in VALID_SOURCE_TYPES:
            errors.append(f"{label}.source_type 必须为 user-provided、official、licensed 或 existing-project")
        for field in ("source", "authorization", "intended_use"):
            if not nonempty_text(item.get(field)):
                errors.append(f"{label} 缺少 {field}")
        target, binding_errors = validate_file_binding(path, item.get("path"), item.get("sha256"), f"{label} 素材")
        errors.extend(binding_errors)
        if target is not None and path.parent.resolve() not in target.parents:
            errors.append(f"{label} 素材必须整理到当前项目内，不能直接绑定外部私人路径")

        privacy = item.get("privacy_review")
        if not isinstance(privacy, dict):
            errors.append(f"{label} 缺少 privacy_review")
            continue
        if not isinstance(privacy.get("contains_personal_information"), bool):
            errors.append(f"{label}.privacy_review.contains_personal_information 必须为布尔值")
        targets = privacy.get("targets")
        if not isinstance(targets, list):
            errors.append(f"{label}.privacy_review.targets 必须为数组")
            targets = []
        treatment = privacy.get("treatment")
        if treatment not in VALID_PRIVACY_TREATMENTS:
            errors.append(f"{label}.privacy_review.treatment 无效")
        if privacy.get("contains_personal_information") is True and not targets:
            errors.append(f"{label} 含个人信息时必须列出精确 privacy targets")
        if privacy.get("contains_personal_information") is True and treatment == "none":
            errors.append(f"{label} 含个人信息时必须裁切、遮挡或排除")

    if items:
        contact_sheet, contact_errors = validate_file_binding(
            path,
            data.get("contact_sheet_path"),
            data.get("contact_sheet_sha256"),
            "真实素材联系表",
        )
        errors.extend(contact_errors)
        if contact_sheet is not None and path.parent.resolve() not in contact_sheet.parents:
            errors.append("真实素材联系表必须位于当前项目内")
    if require_ready:
        if data.get("status") != "ready-for-user-review":
            errors.append("status 必须为 ready-for-user-review")
        if data.get("ready_for_user_review") is not True:
            errors.append("ready_for_user_review 必须为 true")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="校验用户真实素材清单、授权、隐私和联系表")
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--require-ready", action="store_true")
    args = parser.parse_args()
    errors = validate(args.manifest.expanduser().resolve(), args.require_ready)
    if errors:
        for error in errors:
            print(f"FAIL {error}")
        return 1
    print("PASS 用户真实素材已盘点，可提交用户确认")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

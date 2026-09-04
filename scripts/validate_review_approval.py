#!/usr/bin/env python3
"""校验口播、真实素材、镜头素材、静态分镜和动态样片批准状态。"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


VALID_STAGES = {"script", "source-assets", "assets", "storyboard", "motion"}
VALID_MEDIA_TYPES = {"text", "image", "image-gallery", "audio", "audio-gallery", "video"}
NON_APPROVAL_REPLIES = {"嗯", "看看", "再说", "先这样", "不确定"}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate(
    path: Path,
    required_stage: str | None,
    require_approved: bool,
    required_reviewed_files: list[Path] | None = None,
) -> list[str]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return [f"审查批准文件不存在：{path}"]
    except json.JSONDecodeError as exc:
        return [f"审查批准 JSON 无法解析：{exc}"]

    errors: list[str] = []
    schema_version = str(data.get("schema_version", "")).strip()
    if schema_version not in {"1.0", "1.1"}:
        errors.append("schema_version 必须为 1.0 或 1.1")
    stage = data.get("stage")
    if stage not in VALID_STAGES:
        errors.append("stage 必须为 script、source-assets、assets、storyboard 或 motion")
    if required_stage and stage != required_stage:
        errors.append(f"审批阶段不匹配：需要 {required_stage}，实际为 {stage}")
    if require_approved and data.get("approved") is not True:
        errors.append("用户尚未明确确认本阶段审查通过")
    if require_approved and data.get("status") != "approved":
        errors.append("status 必须为 approved")
    if require_approved and not data.get("approved_at"):
        errors.append("缺少 approved_at")
    if require_approved and not str(data.get("approval_message", "")).strip():
        errors.append("缺少用户原始批准语句")
    if require_approved and data.get("approved_by") != "user":
        errors.append("approved_by 必须为 user")

    reviewed_files = data.get("reviewed_files")
    if not isinstance(reviewed_files, list) or not reviewed_files:
        errors.append("reviewed_files 必须包含本阶段全部被审文件")
        return errors

    project_root = path.parent.resolve()
    reviewed_paths: set[Path] = set()
    for index, item in enumerate(reviewed_files):
        if not isinstance(item, dict):
            errors.append(f"reviewed_files[{index}] 必须是对象")
            continue
        raw_path = str(item.get("path", "")).strip()
        expected = str(item.get("sha256", "")).strip().lower()
        if not raw_path:
            errors.append(f"reviewed_files[{index}] 缺少 path")
            continue
        target = Path(raw_path).expanduser()
        if not target.is_absolute():
            target = project_root / target
        target = target.resolve()
        reviewed_paths.add(target)
        if not target.is_file():
            errors.append(f"被审文件不存在：{target}")
            continue
        if len(expected) != 64:
            errors.append(f"被审文件缺少有效 SHA-256：{raw_path}")
            continue
        if sha256(target) != expected:
            errors.append(f"审批后文件发生变化：{raw_path}")

    for required in required_reviewed_files or []:
        required_path = required.expanduser()
        if not required_path.is_absolute():
            required_path = project_root / required_path
        required_path = required_path.resolve()
        if required_path not in reviewed_paths:
            errors.append(f"审批未覆盖本阶段实际使用文件：{required_path}")

    if schema_version == "1.1":
        for field in ("review_prompt", "approval_context", "accepted_response_rule"):
            if not str(data.get(field, "")).strip():
                errors.append(f"V1.1 审批缺少 {field}")
        interpretation = data.get("approval_interpretation")
        if interpretation not in {"explicit", "contextual-stage-response"}:
            errors.append("approval_interpretation 必须为 explicit 或 contextual-stage-response")
        approval_message = str(data.get("approval_message", "")).strip()
        if interpretation == "contextual-stage-response" and approval_message in NON_APPROVAL_REPLIES:
            errors.append("这条短回复不能唯一证明用户批准当前阶段")
        delivery = data.get("review_delivery")
        if not isinstance(delivery, dict):
            errors.append("V1.1 审批缺少 review_delivery")
        else:
            media_type = delivery.get("media_type")
            if media_type not in VALID_MEDIA_TYPES:
                errors.append("review_delivery.media_type 无效")
            if delivery.get("directly_presented") is not True:
                errors.append("审查产物尚未直接展示给用户")
            primary_value = str(delivery.get("primary_path", "")).strip()
            primary_path = (project_root / primary_value).resolve() if primary_value else None
            if primary_path is None or primary_path not in reviewed_paths:
                errors.append("review_delivery.primary_path 必须属于 reviewed_files")
            if stage == "motion":
                if media_type != "video":
                    errors.append("motion 审批的主审查产物必须是视频")
                fallback_value = str(delivery.get("fallback_path", "")).strip()
                fallback_path = (project_root / fallback_value).resolve() if fallback_value else None
                if fallback_path is None or fallback_path not in reviewed_paths:
                    errors.append("motion 审批必须把联系表兜底写入 reviewed_files")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="校验口播、真实素材、镜头素材、静态分镜或动态样片审查批准")
    parser.add_argument("approval", type=Path, help="审批 JSON 路径")
    parser.add_argument("--require-stage", choices=sorted(VALID_STAGES))
    parser.add_argument("--require-approved", action="store_true")
    parser.add_argument(
        "--require-reviewed-file",
        action="append",
        default=[],
        type=Path,
        help="要求 reviewed_files 覆盖的实际文件，可重复提供",
    )
    args = parser.parse_args()

    errors = validate(
        args.approval.expanduser().resolve(),
        args.require_stage,
        args.require_approved,
        args.require_reviewed_file,
    )
    if errors:
        for error in errors:
            print(f"FAIL {error}")
        return 1
    print("PASS 本阶段审查批准有效，被审文件未发生变化")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

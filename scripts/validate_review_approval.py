#!/usr/bin/env python3
"""校验独立审批文件或 V2 审批账本中的阶段批准状态。"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


VALID_STAGES = {"script", "source-assets", "assets", "storyboard", "motion"}
VALID_WORKFLOW_MODES = {"fast", "standard", "high-risk"}
VALID_MEDIA_TYPES = {"text", "image", "image-gallery", "audio", "audio-gallery", "video"}
NON_APPROVAL_REPLIES = {"嗯", "看看", "再说", "先这样", "不确定"}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def approval_path(project_root: Path, stage: str) -> Path:
    """新项目优先使用单一审批账本，旧项目继续读取独立审批文件。"""
    ledger = project_root / "approval-ledger.json"
    return ledger if ledger.is_file() else project_root / f"{stage}-approval.json"


def load_approval(path: Path, required_stage: str | None) -> tuple[dict, str, list[str]]:
    try:
        root = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return {}, "", [f"审查批准文件不存在：{path}"]
    except json.JSONDecodeError as exc:
        return {}, "", [f"审查批准 JSON 无法解析：{exc}"]
    if not isinstance(root, dict):
        return {}, "", ["审查批准 JSON 必须为对象"]

    schema_version = str(root.get("schema_version", "")).strip()
    if schema_version != "2.0":
        return root, schema_version, []
    if root.get("workflow_mode") not in VALID_WORKFLOW_MODES:
        return {}, schema_version, ["V2 审批账本 workflow_mode 必须为 fast、standard 或 high-risk"]
    if not required_stage:
        return {}, schema_version, ["读取 V2 审批账本时必须指定 --require-stage"]
    approvals = root.get("approvals")
    if not isinstance(approvals, dict):
        return {}, schema_version, ["V2 审批账本缺少 approvals"]
    approval = approvals.get(required_stage)
    if not isinstance(approval, dict):
        return {}, schema_version, [f"V2 审批账本缺少 {required_stage} 阶段记录"]
    package = str(approval.get("review_package", "")).strip()
    package_scope = approval.get("package_scope")
    consistency_errors: list[str] = []
    if package and isinstance(package_scope, list):
        for sibling_stage in package_scope:
            if sibling_stage not in VALID_STAGES:
                consistency_errors.append(f"V2 确认包包含无效阶段：{sibling_stage}")
                continue
            sibling = approvals.get(sibling_stage)
            if not isinstance(sibling, dict):
                consistency_errors.append(f"V2 确认包 {package} 缺少 {sibling_stage} 阶段记录")
                continue
            if sibling.get("review_package") != package:
                consistency_errors.append(f"V2 确认包 {package} 的阶段名称不一致：{sibling_stage}")
            if bool(sibling.get("approved")) != bool(approval.get("approved")):
                consistency_errors.append(f"V2 确认包 {package} 不能只批准部分阶段")
            if approval.get("approved") is True:
                for field in ("approval_message", "approved_at", "review_prompt"):
                    if sibling.get(field) != approval.get(field):
                        consistency_errors.append(f"V2 确认包 {package} 的 {field} 必须在各阶段一致")
    data = dict(approval)
    data.setdefault("stage", required_stage)
    return data, schema_version, consistency_errors


def validate(
    path: Path,
    required_stage: str | None,
    require_approved: bool,
    required_reviewed_files: list[Path] | None = None,
) -> list[str]:
    data, schema_version, load_errors = load_approval(path, required_stage)
    if load_errors:
        return load_errors

    errors: list[str] = []
    if schema_version not in {"1.0", "1.1", "2.0"}:
        errors.append("schema_version 必须为 1.0、1.1 或 2.0")
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

    if schema_version in {"1.1", "2.0"}:
        for field in ("review_prompt", "approval_context", "accepted_response_rule"):
            if not str(data.get(field, "")).strip():
                errors.append(f"V1.1/V2 审批缺少 {field}")
        interpretation = data.get("approval_interpretation")
        if interpretation not in {"explicit", "contextual-stage-response"}:
            errors.append("approval_interpretation 必须为 explicit 或 contextual-stage-response")
        approval_message = str(data.get("approval_message", "")).strip()
        if interpretation == "contextual-stage-response" and approval_message in NON_APPROVAL_REPLIES:
            errors.append("这条短回复不能唯一证明用户批准当前阶段")
        delivery = data.get("review_delivery")
        if not isinstance(delivery, dict):
            errors.append("V1.1/V2 审批缺少 review_delivery")
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
    if schema_version == "2.0":
        if not str(data.get("review_package", "")).strip():
            errors.append("V2 阶段记录缺少 review_package")
        package_scope = data.get("package_scope")
        if not isinstance(package_scope, list) or stage not in package_scope:
            errors.append("V2 阶段记录的 package_scope 必须包含当前 stage")
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

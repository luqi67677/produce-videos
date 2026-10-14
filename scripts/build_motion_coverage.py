#!/usr/bin/env python3
"""从真实机器报告准备审片覆盖表；不代填人工检查或用户批准。"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any

from analyze_motion_coverage import load_object, resolve, sha256
from validate_motion_coverage import VALID_WORKFLOW_MODES, is_motion_audit


def build_coverage(
    audit_path: Path,
    output_path: Path,
    *,
    grammars: list[str],
    workflow_mode: str = "standard",
    watermark_required: bool = False,
) -> dict[str, Any]:
    audit_path = audit_path.resolve()
    output_path = output_path.resolve()
    if audit_path == output_path:
        raise ValueError("覆盖表不能覆盖机器报告；两份文件必须分开保存")
    audit = load_object(audit_path)
    if not is_motion_audit(audit) or audit.get("schema_version") not in {"1.0", "1.1"}:
        raise ValueError("输入必须为 analyze_motion_coverage.py 的 V1.0/V1.1 机器报告")
    if workflow_mode not in VALID_WORKFLOW_MODES:
        raise ValueError("workflow_mode 必须为 fast、standard 或 high-risk")
    grammars = list(dict.fromkeys(value.strip() for value in grammars if value.strip()))
    if not grammars:
        raise ValueError("至少填写一条本片实际使用的运动语法；这不代表已审查通过")
    bound: dict[str, Path] = {}
    for path_key, hash_key in (
        ("preview_path", "preview_sha256"),
        ("timeline_path", "timeline_sha256"),
        ("motion_plan_path", "motion_plan_sha256"),
    ):
        value = audit.get(path_key)
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"机器报告缺少 {path_key}")
        target = resolve(audit_path.parent, value)
        if not target.is_file() or sha256(target) != str(audit.get(hash_key, "")):
            raise ValueError(f"机器报告的 {path_key}/{hash_key} 已失效，请先重新审计实际文件")
        bound[path_key] = target

    def relative(target: Path) -> str:
        return os.path.relpath(target, output_path.parent)

    return {
        "artifact_type": "motion-coverage",
        "schema_version": "1.4" if audit["schema_version"] == "1.1" else "1.3",
        "workflow_mode": workflow_mode,
        "review_status": "pending",
        "watermark_required": watermark_required,
        "required_grammars": grammars,
        "samples": [{
            "sample_id": "full-preview-01",
            "path": relative(bound["preview_path"]),
            "proof_kind": "full-preview",
            "representative": False,
            "grammars": grammars,
            "uses_final_audio": False,
            "uses_locked_storyboard": False,
            "single_subtitle_layer": False,
            "watermark_included": watermark_required,
            "visual_coverage_verified": False,
            "character_continuity_verified": False,
            "platform_safe": False,
            "machine_reviewed": False,
            "user_review_required": True,
            "user_reviewed": False,
        }],
        "full_preview_motion_audit": {
            "path": relative(audit_path),
            "schema_version": audit["schema_version"],
            "sha256": sha256(audit_path),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("audit", type=Path, help="独立保存的逐镜机器报告")
    parser.add_argument("output", type=Path, help="新建 motion-coverage.json；不覆写已有审片记录")
    parser.add_argument("--grammar", action="append", required=True, help="实际运动语法，可重复填写")
    parser.add_argument("--workflow-mode", choices=sorted(VALID_WORKFLOW_MODES), default="standard")
    parser.add_argument("--watermark-required", action="store_true")
    args = parser.parse_args()
    try:
        result = build_coverage(
            args.audit.expanduser(), args.output.expanduser(), grammars=args.grammar,
            workflow_mode=args.workflow_mode, watermark_required=args.watermark_required,
        )
        output = args.output.expanduser().resolve()
        output.parent.mkdir(parents=True, exist_ok=True)
        with output.open("x", encoding="utf-8") as handle:
            handle.write(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        parser.error(str(exc))
    print("READY 待审覆盖表已准备；机器结果未改，人工检查与用户审片仍待完成")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

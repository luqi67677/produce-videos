#!/usr/bin/env python3
"""Derive resumable project status from the existing approval ledger."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


STAGES = ("script", "source-assets", "assets", "storyboard", "motion")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_object(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return value if isinstance(value, dict) else {}


def record_for(project: Path, ledger: dict[str, Any], stage: str) -> dict[str, Any]:
    if ledger.get("schema_version") == "2.0":
        approvals = ledger.get("approvals")
        return approvals.get(stage, {}) if isinstance(approvals, dict) else {}
    return load_object(project / f"{stage}-approval.json")


def reviewed_file_state(project: Path, record: dict[str, Any]) -> tuple[list[str], list[str]]:
    missing: list[str] = []
    changed: list[str] = []
    reviewed = record.get("reviewed_files")
    if not isinstance(reviewed, list):
        return ["reviewed_files"], []
    for item in reviewed:
        if not isinstance(item, dict):
            missing.append("invalid-reviewed-file-record")
            continue
        raw = str(item.get("path", "")).strip()
        expected = str(item.get("sha256", "")).strip().lower()
        target = Path(raw).expanduser()
        if not target.is_absolute():
            target = project / target
        if not target.is_file():
            missing.append(raw or "unnamed-file")
        elif len(expected) != 64 or sha256(target) != expected:
            changed.append(raw)
    return missing, changed


def derive(project: Path) -> dict[str, Any]:
    ledger_path = project / "approval-ledger.json"
    ledger = load_object(ledger_path)
    stages: dict[str, Any] = {}
    first_incomplete = ""
    for stage in STAGES:
        record = record_for(project, ledger, stage)
        missing, changed = reviewed_file_state(project, record) if record else ([], [])
        approved = record.get("approved") is True and record.get("status") == "approved"
        valid = approved and not missing and not changed
        stages[stage] = {
            "status": "approved" if valid else "stale" if approved else "pending",
            "approved": approved,
            "missing_files": missing,
            "changed_files": changed,
            "review_package": record.get("review_package", ""),
        }
        if not valid and not first_incomplete:
            first_incomplete = stage

    if not (project / "video-brief.md").is_file():
        next_action = "建立并确认开工信息包"
    elif first_incomplete in {"script", "source-assets"}:
        next_action = "完成内容方向包：口播、真实素材和视觉方向"
    elif not (project / "narration-contract.json").is_file():
        next_action = "按已锁定声音路线完成旁白契约"
    elif first_incomplete in {"assets", "storyboard"}:
        next_action = "完成成片蓝图包：A/B-roll、布局、素材和静态分镜"
    elif first_incomplete == "motion":
        next_action = "生成并确认完整低清预览"
    else:
        final_candidates = sorted((project / "final").glob("*.mp4")) if (project / "final").is_dir() else []
        next_action = "正式成片已存在，运行最终质检并交付" if final_candidates else "运行 full 门禁并导出正式成片"

    completed = [stage for stage in STAGES if stages[stage]["status"] == "approved"]
    return {
        "schema_version": "1.0",
        "derived_from": str(ledger_path if ledger_path.is_file() else project),
        "writes_state": False,
        "workflow_mode": ledger.get("workflow_mode", "legacy-or-unknown"),
        "completed_stages": completed,
        "stages": stages,
        "next_action": next_action,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="从审批账本推导当前进度和下一步，不创建第二套状态")
    parser.add_argument("project", type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    project = args.project.expanduser().resolve()
    if not project.is_dir():
        parser.error(f"项目目录不存在：{project}")
    report = derive(project)
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        for stage in STAGES:
            item = report["stages"][stage]
            print(f"{stage}: {item['status']}")
            for path in item["missing_files"]:
                print(f"  缺失：{path}")
            for path in item["changed_files"]:
                print(f"  审批后变化：{path}")
        print(f"NEXT {report['next_action']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""校验供用户整篇审阅的口播母稿及其全篇逻辑。"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


def nonempty_text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def canonical_segments(data: dict[str, Any]) -> list[tuple[str, str]]:
    result: list[tuple[str, str]] = []
    for item in data.get("segments", []):
        if isinstance(item, dict):
            result.append((str(item.get("scene_id", "")).strip(), str(item.get("display_text", "")).strip()))
    return result


def canonical_text_sha256(data: dict[str, Any]) -> str:
    text = "\n".join(text for _, text in canonical_segments(data))
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def resolve_path(source_path: Path, value: Any) -> Path | None:
    if not isinstance(value, (str, Path)) or not str(value).strip():
        return None
    candidate = Path(value).expanduser()
    return candidate.resolve() if candidate.is_absolute() else (source_path.parent / candidate).resolve()


def validate_contract_binding(contract_path: Path, contract: dict[str, Any], require_approval: bool = True) -> list[str]:
    from validate_review_approval import approval_path
    from validate_review_approval import validate as validate_approval

    errors: list[str] = []
    project = contract_path.parent.resolve()
    master_path = resolve_path(contract_path, contract.get("approved_script_path"))
    if master_path is None or not master_path.is_file() or project not in master_path.parents:
        return ["旁白契约缺少项目内可读取的 approved_script_path"]
    expected_sha = str(contract.get("approved_script_sha256", "")).strip()
    if expected_sha.casefold() != file_sha256(master_path).casefold():
        errors.append("approved_script_sha256 与口播母稿不一致")
    errors.extend(f"口播母稿：{error}" for error in validate(master_path, True))
    if require_approval:
        errors.extend(
            f"口播审批：{error}"
            for error in validate_approval(approval_path(project, "script"), "script", True, [master_path])
        )
    try:
        master = json.loads(master_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [*errors, f"口播母稿无法解析：{exc}"]
    if not isinstance(master, dict):
        return [*errors, "口播母稿必须为 JSON 对象"]
    contract_segments = [
        (str(item.get("scene_id", "")).strip(), str(item.get("display_text", "")).strip())
        for item in contract.get("segments", [])
        if isinstance(item, dict)
    ]
    if contract_segments != canonical_segments(master):
        errors.append("旁白契约的 scene_id/display_text 与用户批准的完整口播不一致")
    return errors


def validate(path: Path, require_ready: bool = False) -> list[str]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return [f"口播母稿不存在：{path}"]
    except (OSError, json.JSONDecodeError) as exc:
        return [f"口播母稿无法解析：{exc}"]
    if not isinstance(data, dict):
        return ["口播母稿必须为 JSON 对象"]

    errors: list[str] = []
    if not nonempty_text(data.get("title")):
        errors.append("口播母稿缺少 title")
    segments = data.get("segments")
    if not isinstance(segments, list) or not segments:
        return [*errors, "segments 必须包含完整口播段落"]
    scene_ids: set[str] = set()
    for index, item in enumerate(segments):
        label = f"segments[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{label} 必须为对象")
            continue
        scene_id = str(item.get("scene_id", "")).strip()
        if not scene_id or scene_id in scene_ids:
            errors.append(f"{label} 缺少唯一 scene_id")
        scene_ids.add(scene_id)
        if not nonempty_text(item.get("display_text")):
            errors.append(f"{label} 缺少 display_text")

    logic = data.get("logic_review")
    if not isinstance(logic, dict):
        errors.append("缺少 logic_review")
    else:
        if logic.get("approved") is not True:
            errors.append("logic_review.approved 必须为 true")
        for field in ("core_claim", "global_flow"):
            if not nonempty_text(logic.get(field)):
                errors.append(f"logic_review 缺少 {field}")
        redundant = logic.get("redundant_segment_ids")
        if not isinstance(redundant, list):
            errors.append("logic_review.redundant_segment_ids 必须为数组")
        elif redundant:
            errors.append("口播仍包含被标记为重复或无贡献的段落")
    if require_ready:
        if data.get("status") != "ready-for-user-review":
            errors.append("status 必须为 ready-for-user-review")
        if data.get("ready_for_user_review") is not True:
            errors.append("ready_for_user_review 必须为 true")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="校验完整口播母稿和全篇逻辑")
    parser.add_argument("master_script", type=Path)
    parser.add_argument("--require-ready", action="store_true")
    args = parser.parse_args()
    errors = validate(args.master_script.expanduser().resolve(), args.require_ready)
    if errors:
        for error in errors:
            print(f"FAIL {error}")
        return 1
    print("PASS 完整口播母稿可提交用户确认")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

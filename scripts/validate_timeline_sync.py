#!/usr/bin/env python3
"""校验逐镜口播、静态分镜和 EDL 使用同一组语义切点。"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any


TOLERANCE_SECONDS = 0.05
VALID_ROLL_TYPES = {"a-roll", "b-roll", "hybrid", "graphic-led"}


def load_object(path: Path, label: str) -> tuple[dict[str, Any] | None, list[str]]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return None, [f"{label}无法读取：{exc}"]
    if not isinstance(value, dict):
        return None, [f"{label}必须为 JSON 对象"]
    return value, []


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def resolve(root: Path, value: Any) -> Path | None:
    if not isinstance(value, str) or not value.strip():
        return None
    path = Path(value).expanduser()
    return path.resolve() if path.is_absolute() else (root / path).resolve()


def close(left: Any, right: Any) -> bool:
    try:
        return abs(float(left) - float(right)) <= TOLERANCE_SECONDS
    except (TypeError, ValueError):
        return False


def number(value: Any) -> float | None:
    try:
        result = float(value)
    except (TypeError, ValueError):
        return None
    return result if math.isfinite(result) else None


def validate(project: Path, narration_path: Path | None = None) -> list[str]:
    project = project.expanduser().resolve()
    shot_path = project / "shot-readiness.json"
    edl_path = project / "edit-decision-list.json"
    narration_path = narration_path or project / "narration-contract.json"

    shot_data, errors = load_object(shot_path, "镜头就绪表")
    edl, load_errors = load_object(edl_path, "EDL")
    errors.extend(load_errors)
    narration, load_errors = load_object(narration_path, "旁白契约")
    errors.extend(load_errors)
    if shot_data is None or edl is None or narration is None:
        return errors
    if str(shot_data.get("schema_version")) != "2.6":
        return errors
    if str(edl.get("schema_version")) != "1.1":
        errors.append("逐镜同步要求 edit-decision-list.json schema_version 为 1.1")

    shots = shot_data.get("shots")
    clips = edl.get("picture_track")
    if not isinstance(shots, list) or not shots or not isinstance(clips, list) or not clips:
        return [*errors, "逐镜同步要求 shots 与 picture_track 都包含完整镜头"]
    shot_ids = [str(item.get("shot_id", "")).strip() for item in shots if isinstance(item, dict)]
    clip_ids = [str(item.get("scene_id", "")).strip() for item in clips if isinstance(item, dict)]
    if shot_ids != clip_ids:
        errors.append("shot-readiness 与 EDL 的镜头 ID 或顺序不一致")
    if len(shots) != len(clips):
        errors.append("shot-readiness 与 EDL 的镜头数量不一致")

    previous_end: float | None = None
    for index, (shot, clip) in enumerate(zip(shots, clips)):
        if not isinstance(shot, dict) or not isinstance(clip, dict):
            errors.append(f"逐镜同步第 {index + 1} 项必须为对象")
            continue
        shot_id = str(shot.get("shot_id", "")).strip() or f"shots[{index}]"
        for shot_field, clip_field in (
            ("timeline_start_seconds", "timeline_start_seconds"),
            ("duration_seconds", "duration_seconds"),
        ):
            if not close(shot.get(shot_field), clip.get(clip_field)):
                errors.append(f"{shot_id} 的 {shot_field} 与 EDL 不一致")
        start = number(clip.get("timeline_start_seconds"))
        clip_duration = number(clip.get("duration_seconds"))
        if start is None or clip_duration is None or start < 0 or clip_duration <= 0:
            errors.append(f"{shot_id} 的 EDL 时间范围无效")
            continue
        expected_end = start + clip_duration
        if not close(shot.get("timeline_end_seconds"), expected_end):
            errors.append(f"{shot_id} 的 timeline_end_seconds 与 EDL 不一致")
        if str(shot.get("narration_excerpt", "")).strip() != str(clip.get("narration_excerpt", "")).strip():
            errors.append(f"{shot_id} 的口播片段与 EDL 不一致")
        if shot.get("roll_type") != clip.get("roll_type") or shot.get("roll_type") not in VALID_ROLL_TYPES:
            errors.append(f"{shot_id} 的 roll_type 与 EDL 不一致")
        if str(shot.get("covers", "")).strip() != str(clip.get("covers", "")).strip():
            errors.append(f"{shot_id} 的 covers 与 EDL 不一致")
        if clip.get("semantic_boundary_verified") is not True:
            errors.append(f"{shot_id} 的 EDL 切点尚未按实际口播听审")
        if previous_end is None and start > TOLERANCE_SECONDS:
            errors.append(f"{shot_id} 没有从 0 秒附近开始")
        if previous_end is not None and abs(start - previous_end) > TOLERANCE_SECONDS:
            errors.append(f"{shot_id} 与上一镜存在时间空洞或重叠")
        previous_end = expected_end

    duration = narration.get("duration_seconds")
    if previous_end is None or not close(previous_end, duration):
        errors.append("EDL 画面轨没有连续覆盖到旁白结束")

    audio_spine = edl.get("audio_spine")
    if not isinstance(audio_spine, dict):
        errors.append("EDL 缺少 audio_spine")
    else:
        audio_path = resolve(project, audio_spine.get("path"))
        narration_audio = resolve(project, narration.get("audio_path"))
        if audio_path is None or not audio_path.is_file() or narration_audio is None or audio_path != narration_audio:
            errors.append("EDL audio_spine 未绑定本次批准的旁白文件")
        elif str(audio_spine.get("sha256", "")).casefold() != sha256(audio_path).casefold():
            errors.append("EDL audio_spine SHA-256 与实际旁白不一致")
        if audio_spine.get("preserve_duration") is not True:
            errors.append("EDL 必须保持批准旁白总时长")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="校验口播、逐镜分镜和 EDL 的语义切点同步")
    parser.add_argument("project", type=Path, help="视频项目目录")
    parser.add_argument("--narration-contract", type=Path)
    args = parser.parse_args()
    narration = args.narration_contract.expanduser().resolve() if args.narration_contract else None
    errors = validate(args.project, narration)
    if errors:
        for error in errors:
            print(f"FAIL {error}")
        return 1
    print("PASS 逐镜声画同步通过：口播片段、静态分镜与 EDL 共用同一组语义切点")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

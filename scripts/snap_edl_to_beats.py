#!/usr/bin/env python3
"""Snap unlocked picture cuts to a beat grid while protecting spoken words."""

from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
from typing import Any


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON 根必须为对象：{path}")
    return value


def inside_word(value: float, words: list[dict[str, Any]]) -> bool:
    return any(
        isinstance(word.get("start"), (int, float))
        and isinstance(word.get("end"), (int, float))
        and float(word["start"]) < value < float(word["end"])
        for word in words
    )


def snap(edl: dict[str, Any], beat_grid: dict[str, Any], words: list[dict[str, Any]], max_shift: float, min_duration: float) -> dict[str, Any]:
    output = copy.deepcopy(edl)
    clips = output.get("picture_track")
    beats = beat_grid.get("beats")
    if not isinstance(clips, list) or len(clips) < 2:
        raise ValueError("picture_track 至少需要两个镜头")
    if not isinstance(beats, list) or not beats:
        raise ValueError("beat-grid 没有 beats")
    numeric_beats = [float(value) for value in beats if isinstance(value, (int, float))]
    boundaries = [float(clips[0].get("timeline_start_seconds", 0))]
    for clip in clips:
        start = float(clip.get("timeline_start_seconds", 0))
        duration = float(clip.get("duration_seconds", 0))
        boundaries.append(start + duration)
    original_end = boundaries[-1]
    changes: list[dict[str, Any]] = []
    for index in range(1, len(boundaries) - 1):
        if clips[index - 1].get("cut_locked") is True:
            continue
        original = boundaries[index]
        candidates = sorted(numeric_beats, key=lambda value: abs(value - original))
        chosen = next((value for value in candidates if abs(value - original) <= max_shift and not inside_word(value, words)), None)
        if chosen is None:
            continue
        if chosen - boundaries[index - 1] < min_duration or boundaries[index + 1] - chosen < min_duration:
            continue
        boundaries[index] = chosen
        changes.append({"after_clip": clips[index - 1].get("clip_id", ""), "from": round(original, 3), "to": round(chosen, 3), "shift_ms": round((chosen - original) * 1000)})
    boundaries[-1] = original_end
    for index, clip in enumerate(clips):
        clip["timeline_start_seconds"] = round(boundaries[index], 3)
        clip["duration_seconds"] = round(boundaries[index + 1] - boundaries[index], 3)
    transitions = output.get("transitions")
    if isinstance(transitions, list):
        for index, transition in enumerate(transitions[: len(clips) - 1]):
            if isinstance(transition, dict):
                transition["at_seconds"] = round(boundaries[index + 1], 3)
    output["beat_quantization"] = {
        "beat_grid_method": beat_grid.get("method", ""),
        "beat_grid_confidence": beat_grid.get("confidence", ""),
        "max_shift_ms": round(max_shift * 1000),
        "protected_word_count": len(words),
        "changes": changes,
    }
    return output


def main() -> int:
    parser = argparse.ArgumentParser(description="把未锁定切点吸附到节拍，避免切进词中")
    parser.add_argument("edl", type=Path)
    parser.add_argument("beat_grid", type=Path)
    parser.add_argument("--transcript", type=Path)
    parser.add_argument("--max-shift-ms", type=int, default=120)
    parser.add_argument("--min-clip-seconds", type=float, default=0.6)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        edl = load(args.edl.expanduser().resolve())
        beat_grid = load(args.beat_grid.expanduser().resolve())
        transcript = load(args.transcript.expanduser().resolve()) if args.transcript else {}
        words = transcript.get("words") if isinstance(transcript.get("words"), list) else []
        output = snap(edl, beat_grid, words, args.max_shift_ms / 1000, args.min_clip_seconds)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"FAIL {exc}")
        return 1
    output_path = args.output.expanduser().resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"PASS 已调整 {len(output['beat_quantization']['changes'])} 个切点：{output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

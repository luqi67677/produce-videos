#!/usr/bin/env python3
"""对完整低清预览做逐镜运动审计，识别静态持图和未分段建立的内容。"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import shutil
import subprocess
from pathlib import Path
from typing import Any


FRAME_WIDTH = 96
FRAME_HEIGHT = 128
FRAME_BYTES = FRAME_WIDTH * FRAME_HEIGHT


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_object(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON 根节点必须为对象：{path}")
    return value


def resolve(root: Path, value: str) -> Path:
    candidate = Path(value).expanduser()
    return candidate.resolve() if candidate.is_absolute() else (root / candidate).resolve()


def finite_number(value: Any, label: str, parser: argparse.ArgumentParser) -> float:
    try:
        result = float(value)
    except (TypeError, ValueError):
        parser.error(f"{label} 必须为有限数字")
    if not math.isfinite(result):
        parser.error(f"{label} 必须为有限数字")
    return result


def extract_frames(video: Path, start: float, duration: float, sample_fps: float) -> list[bytes]:
    ffmpeg = shutil.which("ffmpeg")
    if ffmpeg is None:
        raise RuntimeError("需要 ffmpeg 才能执行逐镜运动审计")
    command = [ffmpeg, "-v", "error"]
    if start > 0:
        command.extend(["-ss", f"{start:.6f}"])
    command.extend(["-i", str(video)])
    if duration > 0:
        command.extend(["-t", f"{duration:.6f}"])
    command.extend([
        "-vf",
        f"fps={sample_fps},scale={FRAME_WIDTH}:{FRAME_HEIGHT}:flags=area,format=gray",
        "-f",
        "rawvideo",
        "-pix_fmt",
        "gray",
        "pipe:1",
    ])
    result = subprocess.run(command, capture_output=True, check=False)
    if result.returncode != 0:
        message = result.stderr.decode("utf-8", errors="replace").strip()
        raise RuntimeError(f"无法读取预览视频：{message}")
    payload = result.stdout
    return [payload[index:index + FRAME_BYTES] for index in range(0, len(payload) - FRAME_BYTES + 1, FRAME_BYTES)]


def frame_difference(previous: bytes, current: bytes, pixel_threshold: int) -> tuple[float, float]:
    absolute_sum = 0
    changed = 0
    for old, new in zip(previous, current):
        delta = abs(old - new)
        absolute_sum += delta
        if delta >= pixel_threshold:
            changed += 1
    return absolute_sum / FRAME_BYTES, changed / FRAME_BYTES


def frame_detail(frame: bytes) -> float:
    if len(frame) != FRAME_BYTES:
        return 0.0
    total = 0
    comparisons = 0
    for row in range(FRAME_HEIGHT):
        offset = row * FRAME_WIDTH
        for column in range(1, FRAME_WIDTH):
            total += abs(frame[offset + column] - frame[offset + column - 1])
            comparisons += 1
    for row in range(1, FRAME_HEIGHT):
        offset = row * FRAME_WIDTH
        previous = offset - FRAME_WIDTH
        for column in range(FRAME_WIDTH):
            total += abs(frame[offset + column] - frame[previous + column])
            comparisons += 1
    return total / comparisons if comparisons else 0.0


def count_events(flags: list[bool], scores: list[float], sample_fps: float) -> int:
    if not flags:
        return 0
    cluster_count = 0
    quiet = 2
    active = False
    for flag in flags:
        if flag and not active:
            cluster_count += 1
            active = True
            quiet = 0
        elif flag:
            quiet = 0
        elif active:
            quiet += 1
            if quiet >= 2:
                active = False

    peak_count = 0
    minimum_gap = max(2, round(sample_fps * 0.25))
    last_peak = -minimum_gap
    for index, score in enumerate(scores):
        if not flags[index] or index - last_peak < minimum_gap:
            continue
        before = scores[index - 1] if index else -1.0
        after = scores[index + 1] if index + 1 < len(scores) else -1.0
        if score >= before and score >= after:
            peak_count += 1
            last_peak = index
    return max(cluster_count, peak_count)


def longest_false_run(flags: list[bool], sample_fps: float) -> float:
    longest = 0
    current = 0
    for flag in flags:
        if flag:
            current = 0
        else:
            current += 1
            longest = max(longest, current)
    return round(longest / sample_fps, 3)


def longest_true_run(flags: list[bool], sample_fps: float) -> float:
    return longest_false_run([not flag for flag in flags], sample_fps)


def blank_visual_failed(
    initial_detail_ratio: float,
    underfilled_hold: float,
    minimum_initial_detail_ratio: float,
    maximum_underfilled_hold: float,
    baseline_visible: bool,
    intentional_blank: bool,
) -> bool:
    return not intentional_blank and (
        (baseline_visible and initial_detail_ratio < minimum_initial_detail_ratio)
        or underfilled_hold > maximum_underfilled_hold
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="逐镜审计完整低清预览的真实运动覆盖")
    parser.add_argument("video", type=Path, help="待审计的完整低清预览")
    parser.add_argument("edl", type=Path, help="edit-decision-list.json")
    parser.add_argument("motion_plan", type=Path, help="包含逐镜 expected_reveal_count 的运动计划")
    parser.add_argument("output", type=Path, help="输出审计 JSON")
    parser.add_argument("--sample-fps", type=float, default=10.0)
    parser.add_argument("--start", type=float, default=0.0)
    parser.add_argument("--timeline-offset", type=float, default=0.0, help="样片首帧对应的 EDL 时间；完整预览保持 0")
    parser.add_argument("--duration", type=float, default=0.0)
    parser.add_argument("--mean-threshold", type=float, default=0.35)
    parser.add_argument("--ratio-threshold", type=float, default=0.006)
    parser.add_argument("--pixel-threshold", type=int, default=10)
    parser.add_argument("--minimum-initial-detail-ratio", type=float, default=0.45)
    parser.add_argument("--minimum-running-detail-ratio", type=float, default=0.25)
    parser.add_argument("--maximum-underfilled-hold", type=float, default=0.2)
    args = parser.parse_args()

    video = args.video.expanduser().resolve()
    edl_path = args.edl.expanduser().resolve()
    plan_path = args.motion_plan.expanduser().resolve()
    output = args.output.expanduser().resolve()
    if args.sample_fps <= 0 or args.start < 0 or args.timeline_offset < 0 or args.duration < 0:
        parser.error("sample-fps 必须大于 0，start/timeline-offset/duration 不能小于 0")
    if not 0 <= args.minimum_initial_detail_ratio <= 1 or not 0 <= args.minimum_running_detail_ratio <= 1:
        parser.error("画面细节比例阈值必须在 0—1 之间")
    if args.maximum_underfilled_hold < 0:
        parser.error("maximum-underfilled-hold 不能小于 0")
    for required in (video, edl_path, plan_path):
        if not required.is_file():
            parser.error(f"文件不存在：{required}")

    edl = load_object(edl_path)
    plan = load_object(plan_path)
    blank_policy = plan.get("blank_policy") if isinstance(plan.get("blank_policy"), dict) else {}
    minimum_initial_detail_ratio = finite_number(
        blank_policy.get("minimum_initial_detail_ratio", args.minimum_initial_detail_ratio),
        "minimum_initial_detail_ratio",
        parser,
    )
    minimum_running_detail_ratio = finite_number(
        blank_policy.get("minimum_running_detail_ratio", args.minimum_running_detail_ratio),
        "minimum_running_detail_ratio",
        parser,
    )
    maximum_underfilled_hold = finite_number(
        blank_policy.get("maximum_underfilled_hold_seconds", args.maximum_underfilled_hold),
        "maximum_underfilled_hold_seconds",
        parser,
    )
    if not 0 <= minimum_initial_detail_ratio <= 1 or not 0 <= minimum_running_detail_ratio <= 1:
        parser.error("运动计划中的画面细节比例阈值必须在 0—1 之间")
    if maximum_underfilled_hold < 0:
        parser.error("运动计划中的 maximum_underfilled_hold_seconds 不能小于 0")
    clips = edl.get("picture_track")
    plan_shots = plan.get("shots")
    if not isinstance(clips, list) or not clips or not isinstance(plan_shots, list) or not plan_shots:
        parser.error("EDL 和运动计划都必须包含完整逐镜列表")
    plan_by_shot = {
        str(item.get("shot_id")): item
        for item in plan_shots
        if isinstance(item, dict) and item.get("shot_id")
    }
    if str(plan.get("schema_version", "")) == "1.3":
        for shot_id, item in plan_by_shot.items():
            if not isinstance(item.get("baseline_visible_from_start"), bool):
                parser.error(f"运动计划 {shot_id} 缺少 baseline_visible_from_start")
            if not isinstance(item.get("intentional_blank_approved"), bool):
                parser.error(f"运动计划 {shot_id} 缺少 intentional_blank_approved")
            if item.get("intentional_blank_approved") is True and not str(item.get("intentional_blank_reason", "")).strip():
                parser.error(f"运动计划 {shot_id} 批准空白时必须说明理由")
    expected_by_shot: dict[str, int] = {}
    for shot_id, item in plan_by_shot.items():
        expected = finite_number(item.get("expected_reveal_count", 1), f"{shot_id}.expected_reveal_count", parser)
        if expected < 1 or not expected.is_integer():
            parser.error(f"{shot_id}.expected_reveal_count 必须为正整数")
        expected_by_shot[shot_id] = int(expected)
    timeline_sync_failures: list[str] = []
    clip_ids = [str(item.get("scene_id", "")).strip() for item in clips if isinstance(item, dict)]
    plan_ids = [str(item.get("shot_id", "")).strip() for item in plan_shots if isinstance(item, dict)]
    if clip_ids != plan_ids:
        timeline_sync_failures.append("EDL 与运动计划的镜头 ID 或顺序不一致")
    for clip in clips:
        if not isinstance(clip, dict):
            continue
        shot_id = str(clip.get("scene_id", "")).strip()
        item = plan_by_shot.get(shot_id)
        if item is None:
            continue
        start = finite_number(clip.get("timeline_start_seconds"), f"{shot_id}.timeline_start_seconds", parser)
        duration = finite_number(clip.get("duration_seconds"), f"{shot_id}.duration_seconds", parser)
        if start < 0 or duration <= 0:
            parser.error(f"{shot_id} 的 EDL 时间范围无效")
        plan_start = finite_number(item.get("timeline_start_seconds"), f"{shot_id}.plan_start", parser)
        plan_duration = finite_number(item.get("duration_seconds"), f"{shot_id}.plan_duration", parser)
        if abs(plan_start - start) > 0.05:
            timeline_sync_failures.append(f"{shot_id} 的运动计划起点与 EDL 不一致")
        if abs(plan_duration - duration) > 0.05:
            timeline_sync_failures.append(f"{shot_id} 的运动计划时长与 EDL 不一致")
        if str(item.get("narration_excerpt", "")).strip() != str(clip.get("narration_excerpt", "")).strip():
            timeline_sync_failures.append(f"{shot_id} 的运动口播线索与 EDL 不一致")
    timeline_end = max(
        finite_number(item.get("timeline_start_seconds"), "EDL timeline_start_seconds", parser)
        + finite_number(item.get("duration_seconds"), "EDL duration_seconds", parser)
        for item in clips if isinstance(item, dict)
    )
    timeline_start = args.timeline_offset + args.start
    audit_end = min(timeline_end, timeline_start + args.duration) if args.duration > 0 else timeline_end
    frames = extract_frames(video, args.start, audit_end - timeline_start, args.sample_fps)
    timestamps = [timeline_start + (index / args.sample_fps) for index in range(len(frames))]

    results: list[dict[str, Any]] = []
    static_shot_ids: list[str] = []
    staged_reveal_failures: list[str] = []
    blank_visual_shot_ids: list[str] = []
    covered_shot_ids: list[str] = []
    for clip in clips:
        if not isinstance(clip, dict):
            continue
        shot_id = str(clip.get("scene_id", "")).strip()
        start = finite_number(clip.get("timeline_start_seconds"), f"{shot_id}.timeline_start_seconds", parser)
        duration = finite_number(clip.get("duration_seconds"), f"{shot_id}.duration_seconds", parser)
        end = start + duration
        if not shot_id or end <= timeline_start or start >= audit_end:
            continue
        indices = [index for index, timestamp in enumerate(timestamps) if start <= timestamp < end]
        if len(indices) < 2:
            continue
        flags: list[bool] = []
        scores: list[float] = []
        for previous_index, current_index in zip(indices, indices[1:]):
            mean_abs, changed_ratio = frame_difference(
                frames[previous_index], frames[current_index], args.pixel_threshold
            )
            meaningful = mean_abs >= args.mean_threshold and changed_ratio >= args.ratio_threshold
            flags.append(meaningful)
            scores.append(mean_abs + (changed_ratio * 10.0))
        updates = count_events(flags, scores, args.sample_fps)
        expected = expected_by_shot.get(shot_id, 1)
        required_updates = min(expected, 3) if expected >= 3 else 1
        if duration > 1.2 and updates < 1:
            static_shot_ids.append(shot_id)
        if expected >= 3 and updates < required_updates:
            staged_reveal_failures.append(shot_id)
        details = [frame_detail(frames[index]) for index in indices]
        peak_detail = max(details, default=0.0)
        detail_ratios = [value / peak_detail if peak_detail > 0 else 0.0 for value in details]
        initial_detail_ratio = detail_ratios[0] if detail_ratios else 0.0
        underfilled_flags = [ratio < minimum_running_detail_ratio for ratio in detail_ratios]
        underfilled_hold = longest_true_run(underfilled_flags, args.sample_fps)
        plan_item = plan_by_shot.get(shot_id, {})
        baseline_visible = plan_item.get("baseline_visible_from_start") is not False
        intentional_blank = plan_item.get("intentional_blank_approved") is True
        blank_failed = blank_visual_failed(
            initial_detail_ratio,
            underfilled_hold,
            minimum_initial_detail_ratio,
            maximum_underfilled_hold,
            baseline_visible,
            intentional_blank,
        )
        if blank_failed:
            blank_visual_shot_ids.append(shot_id)
        covered_shot_ids.append(shot_id)
        results.append({
            "shot_id": shot_id,
            "timeline_start_seconds": start,
            "duration_seconds": duration,
            "expected_reveal_count": expected,
            "meaningful_update_count": updates,
            "required_update_count": required_updates,
            "changed_sample_count": sum(flags),
            "longest_static_run_seconds": longest_false_run(flags, args.sample_fps),
            "initial_detail_ratio": round(initial_detail_ratio, 4),
            "minimum_detail_ratio": round(min(detail_ratios), 4) if detail_ratios else 0.0,
            "underfilled_hold_seconds": underfilled_hold,
            "baseline_visible_from_start": baseline_visible,
            "intentional_blank_approved": intentional_blank,
        })

    all_shot_ids = [str(item.get("scene_id")) for item in clips if isinstance(item, dict)]
    all_shots_covered = timeline_start == 0 and audit_end >= timeline_end - 0.05 and covered_shot_ids == all_shot_ids
    audit = {
        "schema_version": "1.1",
        "preview_path": str(video),
        "preview_sha256": sha256(video),
        "timeline_path": str(edl_path),
        "timeline_sha256": sha256(edl_path),
        "motion_plan_path": str(plan_path),
        "motion_plan_sha256": sha256(plan_path),
        "sample_fps": args.sample_fps,
        "blank_policy": {
            "minimum_initial_detail_ratio": minimum_initial_detail_ratio,
            "minimum_running_detail_ratio": minimum_running_detail_ratio,
            "maximum_underfilled_hold_seconds": maximum_underfilled_hold,
        },
        "audit_start_seconds": timeline_start,
        "audit_end_seconds": audit_end,
        "all_shots_covered": all_shots_covered,
        "covered_shot_ids": covered_shot_ids,
        "static_shot_ids": static_shot_ids,
        "staged_reveal_failures": staged_reveal_failures,
        "blank_visual_shot_ids": blank_visual_shot_ids,
        "timeline_sync_failures": timeline_sync_failures,
        "machine_pass": not static_shot_ids and not staged_reveal_failures and not blank_visual_shot_ids and not timeline_sync_failures,
        "shots": results,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if audit["machine_pass"]:
        print(f"PASS 逐镜运动审计通过：{len(results)} 个镜头")
        return 0
    print(f"FAIL 静态镜头：{', '.join(static_shot_ids) or '无'}")
    print(f"FAIL 分段揭示不足：{', '.join(staged_reveal_failures) or '无'}")
    print(f"FAIL 空白或欠填充镜头：{', '.join(blank_visual_shot_ids) or '无'}")
    print(f"FAIL 时间线同步：{'; '.join(timeline_sync_failures) or '无'}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())

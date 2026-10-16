#!/usr/bin/env python3
"""校验既有逐镜表中的导演计划；EDL 仍是唯一实测时间线。"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any
from urllib.parse import urlparse


def load_object(path: Path, label: str) -> tuple[dict[str, Any] | None, list[str]]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, ValueError) as exc:
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


def text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def number(value: Any) -> float | None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    return float(value) if math.isfinite(value) else None


def compact(value: str) -> str:
    """仅忽略排版空白；不改变标点、大小写或原稿文字。"""
    return "".join(value.split())


def resolve(project: Path, value: Any) -> Path | None:
    if not text(value):
        return None
    path = Path(value).expanduser()
    return path.resolve() if path.is_absolute() else (project / path).resolve()


def require_text(obj: dict, fields: tuple[str, ...], label: str, errors: list[str]) -> None:
    for field in fields:
        if not text(obj.get(field)):
            errors.append(f"{label}.{field} 必须填写具体说明")


def string_list(value: Any, label: str, errors: list[str], *, nonempty: bool = False) -> list[str]:
    if not isinstance(value, list) or any(not text(item) for item in value):
        errors.append(f"{label} 必须为非空文本组成的列表")
        return []
    if nonempty and not value:
        errors.append(f"{label} 至少需要一项")
    if len(value) != len(set(value)):
        errors.append(f"{label} 不得重复")
    return value


def verified_file(project: Path, path_value: Any, hash_value: Any, label: str, errors: list[str]) -> Path | None:
    try:
        path = resolve(project, path_value)
        if path is None or not path.is_file():
            errors.append(f"{label} 文件不存在")
            return None
        if not text(hash_value) or hash_value.casefold() != sha256(path).casefold():
            errors.append(f"{label} SHA-256 与实际文件不一致")
        return path
    except (OSError, ValueError, RuntimeError) as exc:
        errors.append(f"{label} 无法核验：{exc}")
        return None


def https_url(value: Any) -> bool:
    if not text(value):
        return False
    try:
        parsed = urlparse(value)
        return parsed.scheme == "https" and bool(parsed.hostname) and not parsed.username
    except ValueError:
        return False


def validate_rights(project: Path, item: dict, label: str, errors: list[str]) -> None:
    verified_file(project, item.get("path"), item.get("sha256"), label, errors)
    rights = item.get("rights")
    if not isinstance(rights, dict):
        errors.append(f"{label}.rights 缺少逐素材使用依据")
        return
    if rights.get("status") != "reviewed":
        errors.append(f"{label}.rights.status 必须为 reviewed")
    if rights.get("basis") not in ("user-authorization", "licensed", "generated", "self-created"):
        errors.append(f"{label}.rights.basis 不受支持")
    require_text(rights, ("allowed_use", "restrictions_review"), f"{label}.rights", errors)
    if rights.get("basis") == "licensed":
        require_text(rights, ("license_name",), f"{label}.rights", errors)
        for field in ("source_url", "license_url"):
            if not https_url(rights.get(field)):
                errors.append(f"{label}.rights.{field} 必须为有效 HTTPS 网址")
    verified_file(project, rights.get("evidence_path"), rights.get("evidence_sha256"), f"{label} 的许可或授权证据", errors)
    attribution = rights.get("attribution")
    if not isinstance(attribution, dict) or not isinstance(attribution.get("required"), bool):
        errors.append(f"{label}.rights.attribution 必须明确 required 布尔值")
    elif attribution["required"]:
        require_text(attribution, ("text", "placement"), f"{label}.rights.attribution", errors)


def validate_script(project: Path, plan: dict, shots: list, errors: list[str]) -> None:
    binding = plan.get("script_binding")
    if not isinstance(binding, dict):
        errors.append("director_plan.script_binding 缺少原稿绑定")
        return
    path = verified_file(project, binding.get("path"), binding.get("sha256"), "导演计划原稿", errors)
    if path is None:
        return
    if path != (project / "master-script.json").resolve():
        errors.append("导演计划必须绑定项目唯一 master-script.json")
        return
    script, load_errors = load_object(path, "原稿")
    errors.extend(load_errors)
    if script is None:
        return
    segments = script.get("segments")
    if not isinstance(segments, list) or not segments:
        errors.append("master-script.segments 必须包含完整原稿")
        return
    segment_ids: list[str] = []
    segment_text: dict[str, str] = {}
    for index, segment in enumerate(segments):
        label = f"master-script.segments[{index}]"
        if not isinstance(segment, dict):
            errors.append(f"{label} 必须为对象")
            continue
        require_text(segment, ("scene_id", "display_text"), label, errors)
        sid, original = segment.get("scene_id"), segment.get("display_text")
        if text(sid) and text(original):
            if sid in segment_text:
                errors.append(f"原稿段落 ID 重复：{sid}")
            segment_ids.append(sid)
            segment_text[sid] = original
    sequence: list[str] = []
    collected: dict[str, list[str]] = {sid: [] for sid in segment_ids}
    for index, shot in enumerate(shots):
        if not isinstance(shot, dict):
            continue
        sid = shot.get("narration_segment_id")
        excerpt = shot.get("narration_excerpt")
        if not text(sid) or sid not in segment_text:
            errors.append(f"shots[{index}] 的 narration_segment_id 不在原稿中")
            continue
        if not sequence or sequence[-1] != sid:
            sequence.append(sid)
        if text(excerpt):
            collected[sid].append(excerpt)
    if sequence != segment_ids:
        errors.append("逐镜原稿段落存在缺漏、倒序或重复返回；必须保持原稿顺序")
    for sid, original in segment_text.items():
        if compact("".join(collected[sid])) != compact(original):
            errors.append(f"{sid} 的逐镜原文未完整、按顺序覆盖 display_text（不得漏字、改写或重复）")


def validate_direction(shot: dict, label: str, global_event_ids: set[str], errors: list[str]) -> None:
    require_text(shot, ("shot_id", "narration_segment_id", "narration_excerpt", "visual_duty"), label, errors)
    direction = shot.get("direction")
    if not isinstance(direction, dict):
        errors.append(f"{label}.direction 缺少导演分镜")
        return
    require_text(direction, ("audience_takeaway", "visual_form", "composition", "camera", "continuity_anchor", "transition_reason", "subtitle_plan", "music_plan"), f"{label}.direction", errors)
    estimate = number(direction.get("estimated_duration_seconds"))
    if estimate is None or estimate <= 0:
        errors.append(f"{label}.direction.estimated_duration_seconds 必须为正数估时")
    states = direction.get("states")
    if not isinstance(states, dict):
        errors.append(f"{label}.direction.states 缺少开始、动作、结果")
    else:
        require_text(states, ("before", "action", "after"), f"{label}.direction.states", errors)
    requests = direction.get("assets_needed")
    request_ids: set[str] = set()
    if not isinstance(requests, list):
        errors.append(f"{label}.direction.assets_needed 必须为列表；纯程序画面可填空列表")
    else:
        for index, request in enumerate(requests):
            request_label = f"{label}.assets_needed[{index}]"
            if not isinstance(request, dict):
                errors.append(f"{request_label} 必须为对象")
                continue
            require_text(request, ("request_id", "role", "description", "preferred_source", "fallback"), request_label, errors)
            rid = request.get("request_id")
            if text(rid):
                if rid in request_ids:
                    errors.append(f"{request_label} 素材请求 ID 在本镜内重复")
                request_ids.add(rid)
            string_list(request.get("search_queries"), f"{request_label}.search_queries", errors)
            string_list(request.get("acceptance_criteria"), f"{request_label}.acceptance_criteria", errors, nonempty=True)
            string_list(request.get("selected_asset_ids"), f"{request_label}.selected_asset_ids", errors)
    events = direction.get("events")
    if not isinstance(events, list):
        errors.append(f"{label}.direction.events 必须为列表")
        return
    prior_ids: set[str] = set()
    for index, event in enumerate(events):
        event_label = f"{label}.events[{index}]"
        if not isinstance(event, dict):
            errors.append(f"{event_label} 必须为对象")
            continue
        require_text(event, ("event_id", "cue_text", "action", "before", "after"), event_label, errors)
        cue, excerpt = event.get("cue_text"), shot.get("narration_excerpt")
        if text(cue) and text(excerpt) and cue not in excerpt:
            errors.append(f"{event_label}.cue_text 未出现在本镜原文中")
        dependencies = string_list(event.get("depends_on"), f"{event_label}.depends_on", errors)
        for dependency in dependencies:
            if dependency not in prior_ids:
                errors.append(f"{event_label} 依赖 {dependency}，但依赖只能指向本镜先前事件")
        eid = event.get("event_id")
        if text(eid):
            if eid in global_event_ids:
                errors.append(f"事件 ID 全片重复：{eid}")
            global_event_ids.add(eid)
            prior_ids.add(eid)
        sound = event.get("sound")
        if not isinstance(sound, dict) or sound.get("mode") not in ("none", "sfx", "ambience"):
            errors.append(f"{event_label}.sound.mode 必须为 none、sfx 或 ambience")
            continue
        require_text(sound, ("reason",), f"{event_label}.sound", errors)
        if sound["mode"] != "none":
            require_text(sound, ("request_id", "start_trigger", "stop_trigger"), f"{event_label}.sound", errors)
            if not text(sound.get("request_id")) or sound["request_id"] not in request_ids:
                errors.append(f"{event_label}.sound.request_id 必须引用本镜已声明的素材请求")


def frame_range(obj: dict, max_frames: float, label: str, errors: list[str]) -> tuple[int, int] | None:
    start, end = obj.get("start_frame"), obj.get("end_frame")
    if type(start) is not int or type(end) is not int or not (0 <= start < end <= max_frames + 1e-6):
        errors.append(f"{label} 帧范围必须为整数，且满足 0 ≤ start_frame < end_frame ≤ 本镜总帧数")
        return None
    return start, end


def validate_edl(project: Path, shots: list, errors: list[str]) -> None:
    edl, load_errors = load_object(project / "edit-decision-list.json", "实测 EDL")
    errors.extend(load_errors)
    if edl is None:
        return
    if edl.get("schema_version") != "1.1":
        errors.append("导演计划实测定时要求 EDL schema_version 为 1.1")
    fmt = edl.get("format")
    fps = number(fmt.get("fps")) if isinstance(fmt, dict) else None
    if fps is None or fps <= 0:
        errors.append("EDL format.fps 必须为正数")
        return
    clips = edl.get("picture_track")
    if not isinstance(clips, list):
        errors.append("EDL picture_track 必须为列表")
        return
    shot_ids = [shot.get("shot_id") for shot in shots if isinstance(shot, dict)]
    clip_ids = [clip.get("clip_id") for clip in clips if isinstance(clip, dict)]
    if len(clips) != len(shots) or clip_ids != shot_ids:
        errors.append("EDL clip_id 与导演分镜 shot_id 必须一一对应且顺序一致")
    previous_end = 0.0
    for index, (shot, clip) in enumerate(zip(shots, clips)):
        if not isinstance(shot, dict) or not isinstance(clip, dict):
            errors.append(f"EDL 第 {index + 1} 镜必须为对象")
            continue
        label = f"EDL[{index}]"
        if "scene_id" in clip and clip["scene_id"] != shot.get("shot_id"):
            errors.append(f"{label}.scene_id 与 shot_id 不一致")
        if clip.get("narration_excerpt") != shot.get("narration_excerpt"):
            errors.append(f"{label} 口播原文与导演分镜不一致")
        start = number(clip.get("timeline_start_seconds"))
        duration = number(clip.get("duration_seconds"))
        if start is None or start < 0 or duration is None or duration <= 0:
            errors.append(f"{label} 缺少有效实测开始时间或时长")
            continue
        if abs(start - previous_end) > 0.05:
            errors.append(f"{label} 实测画面轨存在时间空洞或重叠")
        previous_end = start + duration
        direction = shot.get("direction")
        planned = direction.get("events") if isinstance(direction, dict) else None
        timed = clip.get("semantic_events")
        if not isinstance(planned, list) or not isinstance(timed, list):
            errors.append(f"{label}.semantic_events 必须为与导演事件对应的列表")
            continue
        expected_ids = [event.get("event_id") for event in planned if isinstance(event, dict)]
        timed_ids = [event.get("event_id") for event in timed if isinstance(event, dict)]
        if len(planned) != len(timed) or expected_ids != timed_ids:
            errors.append(f"{label} 实测事件必须与导演事件一一对应且顺序一致")
        times: dict[str, tuple[int, int]] = {}
        for plan_event, event in zip(planned, timed):
            if not isinstance(plan_event, dict) or not isinstance(event, dict):
                errors.append(f"{label} 事件必须为对象")
                continue
            eid = event.get("event_id")
            event_label = f"{label}.{eid}"
            interval = frame_range(event, duration * fps, event_label, errors)
            dependencies = plan_event.get("depends_on")
            if interval is not None and isinstance(dependencies, list):
                for dependency in dependencies:
                    if isinstance(dependency, str) and dependency in times and times[dependency][1] > interval[0]:
                        errors.append(f"{event_label} 在依赖 {dependency} 完成之前开始")
            if interval is not None and text(eid):
                times[eid] = interval
            sound_plan = plan_event.get("sound")
            sound = event.get("sound")
            if not isinstance(sound_plan, dict):
                continue
            if sound_plan.get("mode") == "none":
                if "sound" in event:
                    errors.append(f"{event_label} 规划为无音效，EDL 不应包含声音事件")
                continue
            if not isinstance(sound, dict):
                errors.append(f"{event_label} 缺少实测声音起止")
                continue
            sound_interval = frame_range(sound, duration * fps, f"{event_label}.sound", errors)
            if (sound_plan.get("mode") == "sfx" and interval is not None
                    and sound_interval is not None and sound_interval[0] < interval[0]):
                errors.append(f"{event_label} 的 SFX 音效不能早于对应语义事件开始")
            gain = number(sound.get("gain_db"))
            if gain is None:
                errors.append(f"{event_label}.sound.gain_db 必须为有限数值")
            fades = [number(sound.get(field)) for field in ("fade_in_ms", "fade_out_ms")]
            if any(value is None or value < 0 for value in fades):
                errors.append(f"{event_label} 声音淡入淡出必须为非负毫秒数")
            elif sound_interval is not None and sum(fades) > (sound_interval[1] - sound_interval[0]) / fps * 1000 + 1e-6:
                errors.append(f"{event_label} 淡入淡出总时长超过声音时长")


def validate_ready_assets(project: Path, shots: list, errors: list[str]) -> None:
    requests: list[tuple[str, dict]] = []
    for shot in shots:
        if not isinstance(shot, dict) or not isinstance(shot.get("direction"), dict):
            continue
        needed = shot["direction"].get("assets_needed")
        if isinstance(needed, list):
            requests.extend((str(shot.get("shot_id", "")), request) for request in needed if isinstance(request, dict))
    if not requests:
        return
    source, load_errors = load_object(project / "source-assets.json", "实际素材清单")
    errors.extend(load_errors)
    if source is None:
        return
    items = source.get("items")
    if not isinstance(items, list):
        errors.append("source-assets.items 必须为列表")
        return
    assets: dict[str, dict] = {}
    for index, item in enumerate(items):
        if not isinstance(item, dict) or not text(item.get("asset_id")):
            errors.append(f"source-assets.items[{index}] 缺少有效 asset_id")
            continue
        aid = item["asset_id"]
        if aid in assets:
            errors.append(f"source-assets 中 asset_id 重复：{aid}")
        assets[aid] = item
    verified: set[str] = set()
    for sid, request in requests:
        selected = request.get("selected_asset_ids")
        label = f"{sid} 的素材请求 {request.get('request_id', '')}"
        if not isinstance(selected, list) or not selected:
            errors.append(f"{label} 尚未解决；ready 阶段必须选择真实素材")
            continue
        for aid in selected:
            if not text(aid) or aid not in assets:
                errors.append(f"{label} 引用的素材未登记到 source-assets.items：{aid}")
            elif aid not in verified:
                validate_rights(project, assets[aid], f"素材 {aid}", errors)
                verified.add(aid)


def validate(project: Path, require_ready: bool = False) -> list[str]:
    project = Path(project).expanduser().resolve()
    data, errors = load_object(project / "shot-readiness.json", "镜头就绪表")
    if data is None:
        return errors
    if "director_plan" not in data:
        return ["缺少 director_plan；合成前必须完成导演分镜"] if require_ready else []
    plan = data["director_plan"]
    if not isinstance(plan, dict):
        return ["director_plan 必须为对象"]
    if data.get("schema_version") != "2.6":
        errors.append("director_plan 扩展要求 shot-readiness schema_version 为 2.6")
    if plan.get("schema_version") != "1.0":
        errors.append("director_plan.schema_version 不受支持")
    stage = plan.get("stage")
    if stage not in ("planning", "ready"):
        errors.append("director_plan.stage 必须为 planning 或 ready")
    if require_ready and stage != "ready":
        errors.append("导演计划尚处于 planning，不能进入合成")
    expected_basis = "measured" if stage == "ready" else "estimated"
    if plan.get("timing_basis") != expected_basis:
        errors.append(f"{stage} 阶段 timing_basis 必须为 {expected_basis}；估时不能冒充实测定时")
    require_text(plan, ("audience", "viewer_outcome", "throughline"), "director_plan", errors)
    shots = data.get("shots")
    if not isinstance(shots, list) or not shots:
        return [*errors, "导演计划 shots 必须包含逐镜分镜"]
    shot_ids: set[str] = set()
    event_ids: set[str] = set()
    for index, shot in enumerate(shots):
        if not isinstance(shot, dict):
            errors.append(f"shots[{index}] 必须为对象")
            continue
        sid = shot.get("shot_id")
        if text(sid):
            if sid in shot_ids:
                errors.append(f"shot_id 重复：{sid}")
            shot_ids.add(sid)
        validate_direction(shot, f"shots[{index}]", event_ids, errors)
    validate_script(project, plan, shots, errors)
    if stage == "ready":
        validate_ready_assets(project, shots, errors)
        validate_edl(project, shots, errors)
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="校验导演分镜、逐镜素材需求与 EDL 因果事件")
    parser.add_argument("project", type=Path, help="视频项目目录")
    parser.add_argument("--require-ready", action="store_true", help="要求素材与实测时间齐备；拒绝仅有规划的项目")
    args = parser.parse_args()
    errors = validate(args.project, args.require_ready)
    if errors:
        for error in errors:
            print(f"未通过：{error}")
        return 1
    print("通过：导演计划结构校验完成；不代表画面、听感或实际成片已验收。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

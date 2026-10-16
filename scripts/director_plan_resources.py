"""导演计划 1.1 的现有动效与本地声音绑定；只检查，不执行实现或渲染。"""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
import shutil
import subprocess
from typing import Any, Callable
from urllib.parse import urlparse
import wave


IMPLEMENTATION_SUFFIXES = {".py", ".js", ".mjs", ".cjs", ".ts", ".tsx", ".jsx", ".css", ".html", ".glsl", ".vert", ".frag", ".wgsl", ".blend"}
TARGETS = ("background", "camera", "foreground", "transition")


def txt(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def num(value: Any) -> float | None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    try:
        return float(value) if math.isfinite(value) else None
    except OverflowError:
        return None


def fields(obj: dict, names: tuple[str, ...], label: str, errors: list[str]) -> None:
    for name in names:
        if not txt(obj.get(name)):
            errors.append(f"{label}.{name} 必须填写具体说明")


def ids(value: Any, label: str, errors: list[str]) -> list[str]:
    if not isinstance(value, list) or any(not txt(item) for item in value):
        errors.append(f"{label} 必须为文本 ID 数组")
        return []
    if len(value) != len(set(value)):
        errors.append(f"{label} 不能重复")
    return value


def read_object(path: Path, label: str, errors: list[str]) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(value, dict):
            return value
    except (OSError, UnicodeError, ValueError) as exc:
        errors.append(f"{label} 无法读取：{exc}")
        return {}
    errors.append(f"{label} 必须为 JSON 对象")
    return {}


def bound_file(project: Path, value: Any, expected: Any, label: str, errors: list[str]) -> Path | None:
    if not txt(value) or "://" in value:
        errors.append(f"{label} 必须引用已有本地文件")
        return None
    try:
        path = Path(value).expanduser()
        path = (path if path.is_absolute() else project / path).resolve()
        if not path.is_file() or path.stat().st_size <= 0:
            errors.append(f"{label} 文件不存在或为空")
            return None
        digest = hashlib.sha256()
        with path.open("rb") as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(chunk)
        if not txt(expected) or digest.hexdigest() != expected.lower():
            errors.append(f"{label} SHA-256 不一致")
            return None
        return path
    except (OSError, ValueError, RuntimeError) as exc:
        errors.append(f"{label} 无法核验：{exc}")
        return None


def media_info(path: Path, kind: str) -> dict | None:
    """读取真实媒体头或探测流；不根据扩展名信任文本伪文件。"""
    if kind == "audio" and path.suffix.lower() == ".wav":
        try:
            with wave.open(str(path), "rb") as stream:
                if stream.getnchannels() > 0 and stream.getframerate() > 0 and stream.getnframes() > 0:
                    frame_count = stream.getnframes()
                    frame_size = stream.getnchannels() * stream.getsampwidth()
                    actual = 0
                    while True:
                        block = stream.readframes(65536)
                        if not block:
                            break
                        actual += len(block)
                    if actual == frame_count * frame_size:
                        return {"duration": frame_count / stream.getframerate()}
        except (OSError, EOFError, wave.Error):
            pass
        return None
    probe = shutil.which("ffprobe")
    if not probe:
        return None
    try:
        run = subprocess.run([probe, "-v", "error", "-show_entries", "stream=codec_type,duration:format=duration", "-of", "json", str(path)], capture_output=True, text=True, timeout=15, check=False)
        data = json.loads(run.stdout)
        if not isinstance(data, dict):
            return None
        streams = data.get("streams", [])
        if not isinstance(streams, list):
            return None
        if run.returncode != 0 or not any(isinstance(stream, dict) and stream.get("codec_type") == kind for stream in streams):
            return None
        fmt = data.get("format")
        values = [fmt.get("duration") if isinstance(fmt, dict) else None] + [stream.get("duration") for stream in streams if isinstance(stream, dict)]
        durations = []
        for value in values:
            try:
                duration = float(value)
                if math.isfinite(duration) and duration > 0:
                    durations.append(duration)
            except (TypeError, ValueError, OverflowError):
                continue
        return {"duration": max(durations)} if durations else ({} if kind == "video" else None)
    except (OSError, ValueError, subprocess.TimeoutExpired):
        return None


def verify_effect(project: Path, effect: dict, errors: list[str]) -> None:
    label = f"动效 {effect.get('effect_id', '')}"
    fields(effect, ("library", "version", "license"), label, errors)
    url = effect.get("source_url")
    if url not in (None, ""):
        try:
            parsed = urlparse(url) if isinstance(url, str) else None
            if parsed is None or parsed.scheme != "https" or not parsed.hostname or parsed.username:
                errors.append(f"{label}.source_url 必须为 HTTPS 来源；本地自产可留空")
        except ValueError:
            errors.append(f"{label}.source_url 无效")
    implementation = effect.get("implementation")
    availability = effect.get("availability")
    if not isinstance(implementation, dict) or not isinstance(availability, dict):
        errors.append(f"{label} 缺少 implementation 或 availability")
        return
    fields(implementation, ("entrypoint",), label + ".implementation", errors)
    path = bound_file(project, implementation.get("path"), implementation.get("sha256"), label + "实现", errors)
    dependencies = implementation.get("dependencies", [])
    if not isinstance(dependencies, list):
        errors.append(f"{label} 实现依赖必须为文件数组")
    else:
        for index, dependency in enumerate(dependencies):
            if not isinstance(dependency, dict):
                errors.append(f"{label} 实现依赖 {index} 必须为文件对象")
                continue
            bound_file(project, dependency.get("path"), dependency.get("sha256"), f"{label} 实现依赖 {index}", errors)
    if path and path.suffix.lower() not in IMPLEMENTATION_SUFFIXES:
        errors.append(f"{label} 必须引用可用实现文件，说明文档不能充当动效实现")
    if availability.get("status") != "verified":
        errors.append(f"{label} 尚未核验可用；不能放入分镜等待实现")
    evidence = bound_file(project, availability.get("evidence_path"), availability.get("evidence_sha256"), label + "可用证明", errors)
    if evidence is None:
        return
    proof = read_object(evidence, label + "可用证明", errors)
    if proof.get("effect_id") != effect.get("effect_id") or proof.get("implementation_sha256") != implementation.get("sha256") or proof.get("status") != "passed":
        errors.append(f"{label} 可用证明未绑定当前实现及通过状态")
    fields(proof, ("details",), label + "可用证明", errors)
    method = proof.get("verification_method")
    if method not in ("execution-test", "existing-render"):
        errors.append(f"{label} 可用证明需要执行测试或既有渲染产物")
    artifact = proof.get("artifact")
    if not isinstance(artifact, dict):
        errors.append(f"{label} 可用证明必须绑定实际日志或既有产物，不能只有状态声明")
        return
    artifact_path = bound_file(project, artifact.get("path"), artifact.get("sha256"), label + "已有测试日志或产物", errors)
    if artifact_path and method == "execution-test":
        fields(proof, ("command",), label + "执行测试", errors)
        try:
            if not artifact_path.read_text(encoding="utf-8").strip():
                errors.append(f"{label} 执行日志为空")
        except (OSError, UnicodeError):
            errors.append(f"{label} 执行日志必须为可读文本")
    if artifact_path and method == "existing-render" and media_info(artifact_path, "video") is None:
        errors.append(f"{label} 既有渲染产物无法识别为图片或视频")


def frame_interval(value: Any, limit: float, label: str, errors: list[str]) -> tuple[int, int] | None:
    if not isinstance(value, dict):
        errors.append(f"{label} 必须为帧范围对象")
        return None
    start, end = value.get("start_frame"), value.get("end_frame")
    if type(start) is not int or type(end) is not int or not 0 <= start < end <= limit + 1e-6:
        errors.append(f"{label} 帧范围超出本镜或不是有效整数区间")
        return None
    return start, end


def validate_resources(project: Path, data: dict, rights_validator: Callable) -> list[str]:
    errors: list[str] = []
    plan = data.get("director_plan", {})
    catalog = plan.get("effect_catalog")
    if not isinstance(catalog, list):
        errors.append("director_plan.effect_catalog 必须为已有动效目录；无动效填空数组")
        catalog = []
    available: dict[str, dict] = {}
    for item in catalog:
        if not isinstance(item, dict) or not txt(item.get("effect_id")):
            errors.append("effect_catalog 项目必须含有效 effect_id")
            continue
        if item["effect_id"] in available:
            errors.append(f"effect_catalog 的 effect_id 重复：{item['effect_id']}")
        available[item["effect_id"]] = item
    source: dict | None = None
    audio_cache: dict[str, dict | None] = {}
    verified_effects: set[str] = set()
    global_instances: set[str] = set()
    shot_details = []

    def local_audio(requests: dict, rid: Any, label: str) -> tuple[str | None, dict | None]:
        nonlocal source
        request = requests.get(rid) if txt(rid) else None
        selected = request.get("selected_asset_ids") if isinstance(request, dict) else None
        if not isinstance(selected, list) or len(selected) != 1 or not txt(selected[0]):
            errors.append(f"{label} 必须选择一个已登记本地音频，不能保留待搜索声音需求")
            return None, None
        aid = selected[0]
        if aid in audio_cache:
            return aid, audio_cache[aid]
        if source is None:
            source = read_object(project / "source-assets.json", "本地音频素材清单", errors)
        items = source.get("items")
        matches = [item for item in items if isinstance(item, dict) and item.get("asset_id") == aid] if isinstance(items, list) else []
        if len(matches) != 1:
            errors.append(f"{label} 引用的本地音频必须在 source-assets 中唯一登记：{aid}")
            audio_cache[aid] = None
            return aid, None
        item = matches[0]
        rights_validator(project, item, f"本地声音 {aid}", errors)
        path = bound_file(project, item.get("path"), item.get("sha256"), f"本地声音 {aid}", errors)
        info = media_info(path, "audio") if path else None
        if info is None:
            errors.append(f"{label} 不是可识别的真实本地音频（非 WAV 格式需可用 ffprobe）")
        audio_cache[aid] = info
        return aid, info

    shots = data.get("shots")
    if not isinstance(shots, list):
        return errors
    for shot_index, shot in enumerate(shots):
        if not isinstance(shot, dict) or not isinstance(shot.get("direction"), dict):
            shot_details.append(None)
            continue
        direction = shot["direction"]
        label = f"{shot.get('shot_id', shot_index)} 的导演安排"
        instances: dict[str, dict] = {}
        effects = direction.get("effects")
        if not isinstance(effects, list):
            errors.append(f"{label}.effects 必须为数组；不使用动效时填空数组")
            effects = []
        for effect in effects:
            if not isinstance(effect, dict):
                errors.append(f"{label}.effects 每项必须为对象")
                continue
            fields(effect, ("instance_id", "effect_id", "purpose", "start_trigger", "stop_trigger"), label + ".effects", errors)
            iid, eid = effect.get("instance_id"), effect.get("effect_id")
            if effect.get("target") not in TARGETS:
                errors.append(f"{label} 动效 target 必须是 background/camera/foreground/transition")
            if not isinstance(effect.get("parameters"), dict):
                errors.append(f"{label} 动效 parameters 必须为对象")
            if txt(iid):
                if iid in global_instances:
                    errors.append(f"动效 instance_id 全片重复：{iid}")
                instances[iid] = effect
                global_instances.add(iid)
            if not txt(eid) or eid not in available:
                errors.append(f"{label} 使用未登记的现有动效：{eid}")
            elif eid not in verified_effects:
                verify_effect(project, available[eid], errors)
                verified_effects.add(eid)
        background = direction.get("background")
        if not isinstance(background, dict):
            errors.append(f"{label}.background 必须明确静止或已有动效")
        else:
            fields(background, ("description", "reason", "continuity"), label + ".background", errors)
            background_ids = ids(background.get("effect_instance_ids"), label + ".background.effect_instance_ids", errors)
            actual = {iid for iid, effect in instances.items() if effect.get("target") == "background"}
            if set(background_ids) != actual:
                errors.append(f"{label} 背景动效引用必须与 background 实例完整对应")
            if background.get("mode") == "static":
                if background_ids or background.get("intensity") != "none":
                    errors.append(f"{label} 静止背景必须无动效，强度为 none")
            elif background.get("mode") == "animated":
                if not background_ids or background.get("intensity") not in ("subtle", "moderate"):
                    errors.append(f"{label} 动态背景需要已有实例及明确强度")
            else:
                errors.append(f"{label}.background.mode 必须为 static 或 animated")
        requests = {item["request_id"]: item for item in direction.get("assets_needed", []) if isinstance(item, dict) and txt(item.get("request_id"))} if isinstance(direction.get("assets_needed"), list) else {}
        source_actions = {}
        effect_events = {}
        sounds = {}
        events = direction.get("events")
        if isinstance(events, list):
            for event in events:
                if not isinstance(event, dict):
                    continue
                selected = ids(event.get("effect_instance_ids"), label + ".events.effect_instance_ids", errors)
                kind = event.get("kind", "effect")
                if kind == "effect":
                    if not selected or any(iid not in instances for iid in selected):
                        errors.append(f"{label} 程序动作事件必须绑定本镜已有动效实例")
                    if "source_request_id" in event:
                        errors.append(f"{label} 程序动效不能同时声明为源素材动作")
                    if txt(event.get("event_id")):
                        effect_events[event["event_id"]] = selected
                elif kind == "source-action":
                    rid = event.get("source_request_id")
                    if selected or not txt(rid) or rid not in requests:
                        errors.append(f"{label} 源素材动作须绑定本镜视觉素材需求，不能附带程序效果实例")
                    elif plan.get("stage") == "ready":
                        selected_assets = requests[rid].get("selected_asset_ids")
                        if not isinstance(selected_assets, list) or len(selected_assets) != 1 or not txt(selected_assets[0]):
                            errors.append(f"{label} 源素材动作须选择一个已经核验的视频")
                        else:
                            if source is None:
                                source = read_object(project / "source-assets.json", "源素材清单", errors)
                            items = source.get("items")
                            matches = [x for x in items if isinstance(x, dict) and x.get("asset_id") == selected_assets[0]] if isinstance(items, list) else []
                            if len(matches) != 1:
                                errors.append(f"{label} 源素材动作引用的视频未唯一登记")
                            else:
                                item = matches[0]
                                rights_validator(project, item, label + "源视频", errors)
                                path = bound_file(project, item.get("path"), item.get("sha256"), label + "源视频", errors)
                                info = media_info(path, "video") if path else None
                                if not info or not info.get("duration"):
                                    errors.append(f"{label} 源素材动作需要真实且有时长的视频，不能使用静态图或文本")
                                elif txt(event.get("event_id")):
                                    source_actions[event["event_id"]] = {"asset_id": item["asset_id"], "sha256": item.get("sha256"), "duration": info["duration"]}
                else:
                    errors.append(f"{label} event.kind 必须为 effect 或 source-action")
                sound = event.get("sound")
                if isinstance(sound, dict) and sound.get("mode") in ("sfx", "ambience"):
                    sound_asset, sound_audio = local_audio(requests, sound.get("request_id"), label + "音效或环境声")
                    continuity = sound.get("continuity", {"from_previous": False, "to_next": False})
                    if not isinstance(continuity, dict) or any(type(continuity.get(key)) is not bool for key in ("from_previous", "to_next")):
                        errors.append(f"{label} 声音 continuity 必须明确两个跨镜布尔值")
                        continuity = {}
                    if txt(event.get("event_id")):
                        sounds[event["event_id"]] = {"asset_id": sound_asset, "audio": sound_audio, "mode": sound["mode"], "continuity": continuity}
        music = direction.get("music")
        aid, audio = None, None
        if not isinstance(music, dict):
            errors.append(f"{label}.music 必须明确 none 或 track")
            music = {}
        fields(music, ("reason",), label + ".music", errors)
        if music.get("mode") == "track":
            fields(music, ("request_id", "start_trigger", "stop_trigger", "ducking"), label + ".music", errors)
            for field in ("gain_db", "fade_in_ms", "fade_out_ms"):
                value = num(music.get(field))
                if value is None or (field != "gain_db" and value < 0):
                    errors.append(f"{label}.music.{field} 无效")
            continuity = music.get("continuity")
            if not isinstance(continuity, dict) or any(type(continuity.get(field)) is not bool for field in ("from_previous", "to_next")):
                errors.append(f"{label}.music.continuity 必须明确 from_previous/to_next 布尔值")
            aid, audio = local_audio(requests, music.get("request_id"), label + "配乐")
        elif music.get("mode") != "none":
            errors.append(f"{label}.music.mode 必须为 none 或 track")
        shot_details.append({"instances": instances, "music": music, "asset_id": aid, "audio": audio, "source_actions": source_actions, "effect_events": effect_events, "sounds": sounds})
    for index, detail in enumerate(shot_details):
        if not detail:
            continue
        for sound in detail["sounds"].values():
            for key, offset, opposite in (("from_previous", -1, "to_next"), ("to_next", 1, "from_previous")):
                if sound["continuity"].get(key) is not True:
                    continue
                adjacent_index = index + offset
                adjacent = shot_details[adjacent_index] if 0 <= adjacent_index < len(shot_details) else None
                matches = [other for other in adjacent["sounds"].values() if sound["asset_id"] and other["asset_id"] == sound["asset_id"] and other["mode"] == sound["mode"] and other["continuity"].get(opposite) is True] if adjacent else []
                if len(matches) != 1:
                    errors.append(f"第 {index + 1} 镜跨镜音效或环境声须与相邻镜同素材同类型且唯一对应")
        music = detail["music"]
        continuity = music.get("continuity")
        if music.get("mode") != "track" or not isinstance(continuity, dict):
            continue
        for key, offset, opposite in (("from_previous", -1, "to_next"), ("to_next", 1, "from_previous")):
            if continuity.get(key) is not True:
                continue
            adjacent_index = index + offset
            adjacent = shot_details[adjacent_index] if 0 <= adjacent_index < len(shot_details) else None
            adjacent_continuity = adjacent["music"].get("continuity") if adjacent else None
            if (not adjacent or adjacent["music"].get("mode") != "track" or not detail["asset_id"] or adjacent["asset_id"] != detail["asset_id"]
                    or not isinstance(adjacent_continuity, dict) or adjacent_continuity.get(opposite) is not True):
                errors.append(f"第 {index + 1} 镜持续配乐必须与相邻镜同一素材并双向声明连续")
            fade = "fade_in_ms" if offset == -1 else "fade_out_ms"
            if music.get(fade) != 0:
                errors.append(f"第 {index + 1} 镜持续配乐的内部边界不能逐镜淡入淡出")
    if plan.get("stage") == "ready":
        validate_resource_cues(project, shot_details, errors)
    return errors


def validate_resource_cues(project: Path, details: list, errors: list[str]) -> None:
    edl = read_object(project / "edit-decision-list.json", "EDL 资源定时", errors)
    fmt = edl.get("format")
    fps = num(fmt.get("fps")) if isinstance(fmt, dict) else None
    clips = edl.get("picture_track")
    if fps is None or fps <= 0 or not isinstance(clips, list):
        return
    music_intervals = []
    sound_cues = []
    for index, detail in enumerate(details):
        sound_cues.append({})
        clip = clips[index] if index < len(clips) else None
        if not detail or not isinstance(clip, dict):
            music_intervals.append(None)
            continue
        duration = num(clip.get("duration_seconds"))
        if duration is None or duration <= 0:
            music_intervals.append(None)
            continue
        label = f"EDL 第 {index + 1} 镜"
        total_frames = duration * fps
        cues = clip.get("effect_cues")
        if not isinstance(cues, list):
            errors.append(f"{label}.effect_cues 必须为与现有动效一一对应的数组")
            cues = []
        cue_ids = [cue.get("instance_id") for cue in cues if isinstance(cue, dict)]
        if len(cue_ids) != len(cues) or cue_ids != list(detail["instances"]):
            errors.append(f"{label}.effect_cues 必须与 effects 实例一一对应并保持顺序")
        effect_intervals = {}
        for cue in cues:
            interval = frame_interval(cue, total_frames, label + "动效", errors)
            if interval and isinstance(cue, dict) and txt(cue.get("instance_id")):
                effect_intervals[cue["instance_id"]] = interval
        semantic = clip.get("semantic_events")
        semantic = semantic if isinstance(semantic, list) else []
        for event in semantic:
            if not isinstance(event, dict):
                continue
            eid = event.get("event_id")
            bound_effects = detail["effect_events"].get(eid, []) if txt(eid) else []
            if bound_effects:
                event_interval = frame_interval(event, total_frames, label + "语义事件", errors)
                for iid in bound_effects:
                    effect_interval = effect_intervals.get(iid)
                    if (event_interval and effect_interval
                            and max(event_interval[0], effect_interval[0]) >= min(event_interval[1], effect_interval[1])):
                        errors.append(f"{label} 事件 {eid} 与绑定动效 {iid} 的帧范围不相交；先行动作须纳入事件跨度")
            sound = detail["sounds"].get(event.get("event_id")) if txt(event.get("event_id")) else None
            timed_sound = event.get("sound")
            if sound and isinstance(timed_sound, dict):
                interval = frame_interval(timed_sound, total_frames, label + "事件声音", errors)
                source_start = timed_sound.get("source_start_frame")
                if timed_sound.get("asset_id") != sound["asset_id"]:
                    errors.append(f"{label} 事件声音素材与分镜选择不一致")
                if type(source_start) is not int or source_start < 0:
                    errors.append(f"{label} 事件声音 source_start_frame 必须为非负整数")
                elif interval and sound["audio"] and source_start + interval[1] - interval[0] > sound["audio"]["duration"] * fps + 1e-6:
                    errors.append(f"{label} 事件声音源区间超出本地音频长度")
                continuity = sound["continuity"]
                if interval:
                    sound_cues[index][event["event_id"]] = {"interval": interval, "cue": timed_sound, "planned": sound}
                    if continuity.get("from_previous") is True and (interval[0] != 0 or timed_sound.get("fade_in_ms") != 0):
                        errors.append(f"{label} 跨镜声音应从本镜首帧延续且不能再次淡入")
                    if continuity.get("to_next") is True and (abs(interval[1] - total_frames) > 1e-6 or timed_sound.get("fade_out_ms") != 0):
                        errors.append(f"{label} 跨镜声音应到本镜末帧且不能提前淡出")
            source_info = detail["source_actions"].get(event.get("event_id")) if txt(event.get("event_id")) else None
            source_action = event.get("source_action")
            if not source_info:
                if source_action is not None:
                    errors.append(f"{label} 未规划源素材动作却存在 source_action")
                continue
            if not isinstance(source_action, dict):
                errors.append(f"{label} 源素材动作须在 EDL 中记录源区间和审阅证据")
                continue
            if source_action.get("asset_id") != source_info["asset_id"]:
                errors.append(f"{label} 源素材动作与已选视频不一致")
            frame_interval({"start_frame": source_action.get("source_start_frame"), "end_frame": source_action.get("source_end_frame")}, source_info["duration"] * fps, label + "源视频", errors)
            proof_path = bound_file(project, source_action.get("evidence_path"), source_action.get("evidence_sha256"), label + "源动作审阅证据", errors)
            if proof_path:
                proof = read_object(proof_path, label + "源动作审阅证据", errors)
                fields(proof, ("reviewer", "details"), label + "源动作审阅证据", errors)
                if proof.get("status") != "reviewed" or proof.get("event_id") != event.get("event_id") or proof.get("asset_sha256") != source_info["sha256"]:
                    errors.append(f"{label} 源动作审阅证据未绑定此事件和素材版本")
        cue = clip.get("music_cue")
        music = detail["music"]
        if music.get("mode") == "none":
            if "music_cue" in clip:
                errors.append(f"{label} 已选择无配乐，不得存在 music_cue")
            music_intervals.append(None)
            continue
        interval = frame_interval(cue, total_frames, label + "配乐", errors)
        music_intervals.append(interval)
        if not isinstance(cue, dict):
            continue
        if cue.get("asset_id") != detail["asset_id"]:
            errors.append(f"{label} 配乐素材与分镜选择不一致")
        for field in ("gain_db", "fade_in_ms", "fade_out_ms"):
            actual = num(cue.get(field))
            if actual is None or actual != num(music.get(field)):
                errors.append(f"{label} 配乐 {field} 必须与分镜一致")
        source_start = cue.get("source_start_frame")
        if type(source_start) is not int or source_start < 0:
            errors.append(f"{label}.music_cue.source_start_frame 必须为非负整数")
        elif interval and detail["audio"] and (source_start + interval[1] - interval[0]) / fps > detail["audio"]["duration"] + 1e-6:
            errors.append(f"{label} 配乐源区间超出已有音频长度")
        fades = [num(cue.get(field)) for field in ("fade_in_ms", "fade_out_ms")]
        if interval and all(value is not None and value >= 0 for value in fades) and sum(fades) > (interval[1] - interval[0]) / fps * 1000 + 1e-6:
            errors.append(f"{label} 配乐淡入淡出总时长超过声音长度")
        continuity = music.get("continuity")
        if interval and isinstance(continuity, dict):
            if continuity.get("from_previous") is True and interval[0] != 0:
                errors.append(f"{label} 持续配乐必须从本镜首帧开始")
            if continuity.get("to_next") is True and abs(interval[1] - total_frames) > 1e-6:
                errors.append(f"{label} 持续配乐必须覆盖到本镜末帧")
    for index in range(1, min(len(details), len(clips))):
        detail = details[index]
        continuity = detail["music"].get("continuity") if detail else None
        if not isinstance(continuity, dict) or continuity.get("from_previous") is not True:
            continue
        previous_interval, interval = music_intervals[index - 1:index + 1]
        previous_clip, clip = clips[index - 1:index + 1]
        if not isinstance(previous_clip, dict) or not isinstance(clip, dict):
            continue
        previous_cue, cue = previous_clip.get("music_cue"), clip.get("music_cue")
        if not previous_interval or not interval or not isinstance(previous_cue, dict) or not isinstance(cue, dict):
            continue
        previous_start, current_start = previous_cue.get("source_start_frame"), cue.get("source_start_frame")
        if type(previous_start) is int and type(current_start) is int and current_start != previous_start + previous_interval[1] - previous_interval[0]:
            errors.append(f"EDL 第 {index + 1} 镜持续配乐源位置不连续，不能每镜从头播放")
        end = num(previous_clip.get("timeline_start_seconds"))
        start = num(clip.get("timeline_start_seconds"))
        if end is not None and start is not None and abs(end + previous_interval[1] / fps - start - interval[0] / fps) > 1e-6:
            errors.append(f"EDL 第 {index + 1} 镜跨镜配乐存在间断或重叠")

    for index in range(1, len(sound_cues)):
        for current in sound_cues[index].values():
            sound = current["planned"]
            if sound["continuity"].get("from_previous") is not True:
                continue
            matches = [previous for previous in sound_cues[index - 1].values() if previous["planned"]["asset_id"] == sound["asset_id"] and previous["planned"]["mode"] == sound["mode"] and previous["planned"]["continuity"].get("to_next") is True]
            if len(matches) != 1:
                continue
            previous = matches[0]
            source_start = current["cue"].get("source_start_frame")
            previous_source = previous["cue"].get("source_start_frame")
            if type(source_start) is int and type(previous_source) is int and source_start != previous_source + previous["interval"][1] - previous["interval"][0]:
                errors.append(f"EDL 第 {index + 1} 镜跨镜声音的源位置不连续")
            end = num(clips[index - 1].get("timeline_start_seconds"))
            start = num(clips[index].get("timeline_start_seconds"))
            if end is not None and start is not None and abs(end + previous["interval"][1] / fps - start - current["interval"][0] / fps) > 1e-6:
                errors.append(f"EDL 第 {index + 1} 镜跨镜声音存在间断或重叠")

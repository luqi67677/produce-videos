#!/usr/bin/env python3
"""Validate story, reusable creator memory, character identity and raw-asset review contracts."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import math
import shutil
import subprocess
from pathlib import Path
from typing import Any


SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$", re.IGNORECASE)
CONTENT_MODES = {"short-social", "tutorial", "promo", "knowledge", "story", "other"}
OPENING_STRATEGIES = {"result", "contrast", "legitimate-conflict", "question", "demonstration"}
THROUGHLINE_TYPES = {"object", "action", "question", "person", "direction", "visual-motif"}
MEMORY_SCOPES = {"project-only", "workspace-opt-in"}
MEMORY_STATUSES = {"candidate", "active", "retired"}
MEMORY_CATEGORIES = {"narrative", "visual", "motion", "platform", "audio", "character", "workflow"}
WORKFLOW_MODES = {"fast", "standard", "high-risk"}
REVIEW_MODES = {"merged-blueprint", "risk-first"}
RISK_FLAGS = {
    "recurring-character",
    "generated-person",
    "brand-identity",
    "privacy",
    "authorization",
    "generated-product-evidence",
}
IDENTITY_RISKS = {"recurring-character", "generated-person", "brand-identity"}
ROLL_USES = {"a-roll", "b-roll", "hybrid", "graphic-led", "cover"}


def nonempty_text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def text_list(value: Any) -> list[str] | None:
    if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
        return None
    return value


def load_object(path: Path) -> tuple[dict[str, Any] | None, list[str]]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None, [f"文件不存在：{path}"]
    except (OSError, json.JSONDecodeError) as exc:
        return None, [f"文件无法解析：{path} ({exc})"]
    if not isinstance(value, dict):
        return None, [f"文件必须是 JSON 对象：{path}"]
    return value, []


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def resolve_path(contract_path: Path, value: Any) -> Path | None:
    if not nonempty_text(value):
        return None
    candidate = Path(str(value)).expanduser()
    return candidate.resolve() if candidate.is_absolute() else (contract_path.parent / candidate).resolve()


def validate_bound_file(contract_path: Path, path_value: Any, sha_value: Any, label: str) -> tuple[Path | None, list[str]]:
    target = resolve_path(contract_path, path_value)
    if target is None or not target.is_file():
        return target, [f"{label}不存在或不可读取"]
    expected = str(sha_value or "").strip()
    if not SHA256_PATTERN.fullmatch(expected) or file_sha256(target).casefold() != expected.casefold():
        return target, [f"{label} SHA-256 与实际文件不一致"]
    return target, []


def validate_story_contract(path: Path) -> list[str]:
    data, errors = load_object(path)
    if data is None:
        return errors
    if data.get("schema_version") != "1.0":
        errors.append("story-contract.schema_version 必须为 1.0")
    mode = data.get("content_mode")
    if mode not in CONTENT_MODES:
        errors.append("story-contract.content_mode 无效")

    opening = data.get("opening")
    if not isinstance(opening, dict):
        errors.append("story-contract 缺少 opening")
    else:
        strategy = opening.get("strategy")
        if strategy not in OPENING_STRATEGIES:
            errors.append("opening.strategy 必须是结果、反差、真实冲突、问题或演示")
        for field in ("promise", "visible_evidence", "truth_basis"):
            if not nonempty_text(opening.get(field)):
                errors.append(f"opening 缺少 {field}")
        latest = opening.get("evidence_by_seconds")
        limit = 2.0 if mode == "short-social" else 3.0
        if not isinstance(latest, (int, float)) or isinstance(latest, bool) or not 0 < float(latest) <= limit:
            errors.append(f"opening.evidence_by_seconds 必须在 0—{limit:g} 秒内")
        if strategy == "legitimate-conflict" and not nonempty_text(opening.get("conflict_source")):
            errors.append("使用冲突开场时必须记录真实 conflict_source")

    tension = data.get("central_tension")
    if not isinstance(tension, dict):
        errors.append("story-contract 缺少 central_tension")
    else:
        for field in ("starting_state", "friction", "key_action", "evidence", "changed_state"):
            if not nonempty_text(tension.get(field)):
                errors.append(f"central_tension 缺少 {field}")
        if tension.get("single_main_tension") is not True:
            errors.append("每条视频必须锁定一条核心张力")
        if tension.get("manufactured_conflict") is not False:
            errors.append("不得制造资料无法支持的假冲突")

    throughline = data.get("throughline")
    if not isinstance(throughline, dict):
        errors.append("story-contract 缺少 throughline")
    else:
        if throughline.get("type") not in THROUGHLINE_TYPES:
            errors.append("throughline.type 无效")
        for field in ("anchor", "setup_scene_id", "payoff_scene_id"):
            if not nonempty_text(throughline.get(field)):
                errors.append(f"throughline 缺少 {field}")
        development = text_list(throughline.get("development_scene_ids"))
        if development is None or not development or any(not item.strip() for item in development):
            errors.append("throughline.development_scene_ids 必须包含中段推进镜头")

    ending = data.get("ending")
    if not isinstance(ending, dict):
        errors.append("story-contract 缺少 ending")
    else:
        if ending.get("resolves_opening") is not True:
            errors.append("结尾必须兑现开头承诺")
        if not nonempty_text(ending.get("result_evidence")):
            errors.append("ending 缺少 result_evidence")
        if ending.get("cta") and ending.get("cta_supports_story") is not True:
            errors.append("行动引导必须与当前故事相关")

    checks = data.get("continuity_checks")
    if not isinstance(checks, dict):
        errors.append("story-contract 缺少 continuity_checks")
    else:
        for field in ("every_scene_advances", "broll_returns_to_axis", "opening_and_ending_match"):
            if checks.get(field) is not True:
                errors.append(f"continuity_checks.{field} 尚未通过")
    return errors


def validate_creator_memory(path: Path, applied_memory_ids: list[str] | None = None) -> list[str]:
    data, errors = load_object(path)
    if data is None:
        return errors
    if data.get("schema_version") != "1.0":
        errors.append("creator-memory.schema_version 必须为 1.0")
    if not nonempty_text(data.get("scope_id")):
        errors.append("creator-memory 缺少 scope_id")
    storage_scope = data.get("storage_scope")
    if storage_scope not in MEMORY_SCOPES:
        errors.append("creator-memory.storage_scope 无效")
    consent = data.get("consent")
    if not isinstance(consent, dict):
        errors.append("creator-memory 缺少 consent")
        consent = {}
    for field in ("reuse_across_projects", "store_relative_asset_references", "store_voice_or_person_identity_references"):
        if not isinstance(consent.get(field), bool):
            errors.append(f"creator-memory.consent.{field} 必须为布尔值")
    if storage_scope == "project-only" and consent.get("reuse_across_projects") is not False:
        errors.append("project-only 记忆不得声称可跨项目复用")
    if storage_scope == "workspace-opt-in" and consent.get("reuse_across_projects") is not True:
        errors.append("跨项目记忆必须获得用户明确授权")

    preferences = data.get("preferences")
    if not isinstance(preferences, list):
        errors.append("creator-memory.preferences 必须为数组")
        preferences = []
    seen: set[str] = set()
    for index, item in enumerate(preferences):
        label = f"preferences[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{label} 必须为对象")
            continue
        memory_id = str(item.get("memory_id", "")).strip()
        if not memory_id or memory_id in seen:
            errors.append(f"{label} 缺少唯一 memory_id")
        seen.add(memory_id)
        if item.get("category") not in MEMORY_CATEGORIES:
            errors.append(f"{label}.category 无效")
        if not nonempty_text(item.get("rule")):
            errors.append(f"{label} 缺少 rule")
        status = item.get("status")
        if status not in MEMORY_STATUSES:
            errors.append(f"{label}.status 无效")
        if status == "active" and item.get("user_confirmed_for_future") is not True:
            errors.append(f"{label} 未获得用户对长期复用的确认")
        evidence = item.get("evidence")
        if not isinstance(evidence, list):
            errors.append(f"{label}.evidence 必须为数组")
            continue
        for evidence_index, record in enumerate(evidence):
            evidence_label = f"{label}.evidence[{evidence_index}]"
            if not isinstance(record, dict):
                errors.append(f"{evidence_label} 必须为对象")
                continue
            for field in ("project_id", "user_feedback"):
                if not nonempty_text(record.get(field)):
                    errors.append(f"{evidence_label} 缺少 {field}")
            if not isinstance(record.get("approved"), bool):
                errors.append(f"{evidence_label}.approved 必须为布尔值")
            digest = str(record.get("artifact_sha256", "")).strip()
            if record.get("approved") is True and not SHA256_PATTERN.fullmatch(digest):
                errors.append(f"{evidence_label} 通过记录缺少有效 artifact_sha256")
        if status == "active" and not any(
            isinstance(record, dict)
            and record.get("approved") is True
            and SHA256_PATTERN.fullmatch(str(record.get("artifact_sha256", "")).strip())
            for record in evidence
        ):
            errors.append(f"{label} 作为长期规则但缺少已批准产物证据")

    retired_ids = text_list(data.get("retired_memory_ids"))
    if retired_ids is None:
        errors.append("creator-memory.retired_memory_ids 必须为字符串数组")
    if not nonempty_text(data.get("updated_at")):
        errors.append("creator-memory 缺少 updated_at")
    if applied_memory_ids is not None:
        active_ids = {
            str(item.get("memory_id", "")).strip()
            for item in preferences
            if isinstance(item, dict) and item.get("status") == "active"
        }
        if len(applied_memory_ids) != len(set(applied_memory_ids)):
            errors.append("memory_binding.applied_memory_ids 不能重复")
        invalid_applied = sorted(set(applied_memory_ids) - active_ids)
        if invalid_applied:
            errors.append(f"只能应用已确认 active 的创作记忆：{', '.join(invalid_applied)}")
    return errors


def is_subtle_presenter(profile: dict[str, Any]) -> bool:
    presentation = profile.get("presentation")
    return isinstance(presentation, dict) and presentation.get("performance_style") == "subtle-presenter"


def validate_presentation_mode(profile: dict[str, Any], label: str) -> list[str]:
    presentation = profile.get("presentation")
    if not isinstance(presentation, dict):
        return []  # 兼容未声明 presentation 的旧人物档案。
    mode = presentation.get("mode")
    errors: list[str] = []
    if mode is not None and mode not in ("generated-performance", "static-presenter", "audio-driven-presenter"):
        errors.append(f"{label}.presentation.mode 无效")
    if is_subtle_presenter(profile) and mode != "generated-performance":
        errors.append(f"{label} 的 subtle-presenter 必须采用 generated-performance")
    return errors


def validate_presenter_motion(
    profile_path: Path,
    profile: dict[str, Any],
    project_root: Path,
    narration_contract_path: Path | None = None,
    label: str = "presenter",
) -> list[str]:
    errors: list[str] = []
    presentation = profile.get("presentation", {})
    subtle = is_subtle_presenter(profile)
    if subtle:
        errors.extend(validate_presentation_mode(profile, label))
        if presentation.get("body_motion") != "subtle":
            errors.append(f"{label}.presentation.body_motion 必须为 subtle")
        regions = text_list(presentation.get("animated_regions"))
        if regions is None or len(regions) != len(set(regions)) or not set(regions).issubset({"head", "hands", "eyes"}) or not set(regions).intersection({"head", "hands"}):
            errors.append(f"{label}.presentation.animated_regions 必须含实际 head 或 hands 动作，不能只动口眼")
        if presentation.get("mouth_behavior") != "non-speaking" or presentation.get("mouth_driver") is not None:
            errors.append(f"{label} 的轻微表演必须 mouth_behavior=non-speaking、mouth_driver=null")
        allowed_regions = set(regions or []).intersection({"head", "hands", "eyes"})
    else:
        if presentation.get("body_motion") != "fixed":
            errors.append(f"{label}.presentation.body_motion 必须为 fixed")
        regions = text_list(presentation.get("animated_regions"))
        if regions is None or len(regions) != 2 or set(regions) != {"mouth", "eyes"}:
            errors.append(f"{label}.presentation.animated_regions 必须且只能为 mouth、eyes")
        allowed_regions = {"mouth", "eyes"}
    driver = presentation.get("mouth_driver")
    if not subtle and driver not in ("amplitude", "phoneme"):
        errors.append(f"{label}.presentation.mouth_driver 必须为 amplitude 或 phoneme")
    if not nonempty_text(presentation.get("animation_authorization")):
        action_kind = "轻微角色动作" if subtle else "动嘴与眨眼"
        errors.append(f"{label}.presentation.animation_authorization 必须记录用户授权{action_kind}的原话")
    motion = presentation.get("motion_review")
    if not isinstance(motion, dict):
        return errors + [f"{label}.presentation.motion_review 必须记录真实动态样段审查，制作授权不能代替审片"]
    if motion.get("mouth_driver") != driver:
        errors.append(f"{label}.motion_review.mouth_driver 与实际驱动模式不一致")
    if subtle:
        required_reviews = ("reviewed", "subtle_motion_verified", "mouth_not_speaking_verified", "identity_preserved_verified", "anatomy_safe_verified")
        if motion.get("status") == "sample-not-created":
            for field in required_reviews + ("lip_sync_verified", "mouth_audio_sync_verified"):
                if motion.get(field) is not False:
                    errors.append(f"{label}.motion_review.{field} 必须为 false，未制作动作短样不得伪填已审")
            return errors + [f"{label}.motion_review 新动作短样待制作：当前仅保存配置与导演安排，不能锁定或通过渲染门"]
        for field in ("lip_sync_verified", "mouth_audio_sync_verified"):
            if motion.get(field) is not False:
                errors.append(f"{label}.motion_review.{field} 必须为 false，轻微表演的嘴不说话")
    else:
        required_reviews = ("reviewed", "body_fixed_verified", "mouth_audio_sync_verified", "blink_verified", "identity_preserved_verified")
    for field in required_reviews:
        if motion.get(field) is not True:
            errors.append(f"{label}.motion_review.{field} 尚未通过真实样段审查")
    if not subtle and driver in ("amplitude", "phoneme") and motion.get("lip_sync_verified") is not (driver == "phoneme"):
        errors.append(f"{label}.motion_review.lip_sync_verified 必须与 mouth_driver 一致；音量开合不得称为音素同步")

    bindings: dict[str, Path | None] = {}
    for field in ("sample", "audio", "character_asset"):
        target = resolve_path(profile_path, motion.get(f"{field}_path"))
        bindings[field] = target
        expected = str(motion.get(f"{field}_sha256", "")).strip()
        if target is None or not target.is_file() or target.stat().st_size == 0:
            errors.append(f"{label}.motion_review.{field}_path 不存在、为空或不可读取")
        elif not SHA256_PATTERN.fullmatch(expected) or file_sha256(target).casefold() != expected.casefold():
            errors.append(f"{label}.motion_review.{field}_sha256 与实际文件不一致")
        if target is not None and project_root not in target.parents:
            errors.append(f"{label}.motion_review.{field}_path 必须位于当前视频项目内")
    references = profile.get("reference_assets")
    anchor_bindings = {
        (resolve_path(profile_path, item.get("path")), str(item.get("sha256", "")).strip().casefold())
        for item in references if isinstance(item, dict) and item.get("role") == "identity-anchor"
    } if isinstance(references, list) else set()
    if (bindings["character_asset"], str(motion.get("character_asset_sha256", "")).strip().casefold()) not in anchor_bindings:
        errors.append(f"{label}.motion_review.character_asset 必须绑定已批准 identity-anchor 的原图及哈希")

    source_refs = motion.get("source_refs")
    source_regions: set[str] = set()
    if not isinstance(source_refs, list) or not source_refs:
        source_kind = "实际头部或手势动作素材" if subtle else "嘴部与眼部局部素材"
        errors.append(f"{label}.motion_review.source_refs 必须绑定{source_kind}")
    else:
        for index, source in enumerate(source_refs):
            source_label = f"{label}.motion_review.source_refs[{index}]"
            if not isinstance(source, dict):
                errors.append(f"{source_label} 必须为对象")
                continue
            region = source.get("region")
            if not isinstance(region, str) or region not in allowed_regions:
                errors.append(f"{source_label}.region 与实际 animated_regions 不一致")
            else:
                source_regions.add(region)
            target = resolve_path(profile_path, source.get("path"))
            expected = str(source.get("sha256", "")).strip()
            if target is None or not target.is_file() or target.stat().st_size == 0:
                errors.append(f"{source_label}.path 不存在、为空或不可读取")
            elif not SHA256_PATTERN.fullmatch(expected) or file_sha256(target).casefold() != expected.casefold():
                errors.append(f"{source_label}.sha256 与实际局部素材不一致")
            if target is not None and project_root not in target.parents:
                errors.append(f"{source_label}.path 必须位于当前视频项目内")
            if subtle and region in ("head", "hands") and (target == bindings["character_asset"] or expected.casefold() == str(motion.get("character_asset_sha256", "")).strip().casefold()):
                errors.append(f"{source_label} 不能用静态身份原图本身代替新头部或手势动作素材")
        if source_regions != allowed_regions:
            errors.append(f"{label}.motion_review.source_refs 必须覆盖实际 animated_regions")
    if subtle:
        def source_bindings(value: Any) -> set[tuple[Any, Any, str]]:
            return {(item.get("region"), resolve_path(profile_path, item.get("path")), str(item.get("sha256", "")).strip().casefold()) for item in value if isinstance(item, dict) and isinstance(item.get("region"), str)} if isinstance(value, list) else set()
        if not source_bindings(source_refs) or source_bindings(source_refs) != source_bindings(presentation.get("source_refs")):
            errors.append(f"{label}.motion_review.source_refs 必须与当前 presentation.source_refs 的实际素材及哈希一致")

    contract_path = narration_contract_path or project_root / "narration-contract.json"
    try:
        narration = json.loads(contract_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"{label}.motion_review 无法读取正式旁白契约：{exc}")
        narration = {}
    if not isinstance(narration, dict):
        narration = {}
    if not isinstance(narration, dict):
        errors.append(f"{label}.motion_review 正式旁白契约必须是 JSON 对象")
        narration = {}
    official_audio = resolve_path(contract_path, narration.get("audio_path"))
    official_sha = str(narration.get("audio_sha256", "")).strip().casefold()
    if bindings["audio"] != official_audio or str(motion.get("audio_sha256", "")).strip().casefold() != official_sha or not SHA256_PATTERN.fullmatch(official_sha):
        errors.append(f"{label}.motion_review.audio 必须绑定正式 narration-contract 的整轨音频路径和哈希")
    duration = narration.get("duration_seconds")
    start = motion.get("audio_start_seconds")
    end = motion.get("audio_end_seconds")
    numeric = lambda value: isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)
    actual_audio_duration: float | None = None
    if official_audio is None or not official_audio.is_file() or official_audio.stat().st_size == 0:
        errors.append(f"{label}.motion_review 正式整轨音频不存在、为空或不可读取")
    else:
        probe = shutil.which("ffprobe")
        if probe is None:
            errors.append(f"{label}.motion_review 无法检查正式整轨音频：未找到 ffprobe")
        else:
            try:
                result = subprocess.run([probe, "-v", "error", "-select_streams", "a", "-show_entries", "stream=codec_type,duration:format=duration", "-of", "json", str(official_audio)], capture_output=True, text=True, timeout=15, check=True)
                audio_data = json.loads(result.stdout)
                audio_streams = [item for item in audio_data.get("streams", []) if isinstance(item, dict) and item.get("codec_type") == "audio"]
                if not audio_streams:
                    errors.append(f"{label}.motion_review 正式整轨文件必须含真实音频声轨")
                else:
                    # 声轨时长优先，避免长视频掩盖其中只有一小段音频。
                    stream_duration = audio_streams[0].get("duration")
                    try:
                        measured_duration = float(stream_duration)
                    except (TypeError, ValueError):
                        measured_duration = float(audio_data.get("format", {}).get("duration", 0))
                    if not math.isfinite(measured_duration) or measured_duration <= 0:
                        errors.append(f"{label}.motion_review 正式整轨声轨没有有效真实时长")
                    else:
                        actual_audio_duration = measured_duration
                        if not numeric(duration) or abs(actual_audio_duration - float(duration)) > 0.25:
                            errors.append(f"{label}.motion_review 正式整轨真实时长与 narration-contract.duration_seconds 不一致")
            except (OSError, subprocess.SubprocessError, ValueError, TypeError) as exc:
                errors.append(f"{label}.motion_review 正式整轨文件无法确认为真实音频：{exc}")
    valid_window = numeric(duration) and float(duration) > 0 and numeric(start) and numeric(end) and actual_audio_duration is not None and 0 <= float(start) < float(end) <= min(float(duration), actual_audio_duration)
    if not valid_window:
        errors.append(f"{label}.motion_review.audio_start_seconds/audio_end_seconds 必须严格位于正式整轨的真实音频时长范围内")

    sample = bindings["sample"]
    if sample is not None and sample.is_file() and sample.stat().st_size > 0:
        probe = shutil.which("ffprobe")
        if probe is None:
            errors.append(f"{label}.motion_review 无法检查真实样段：未找到 ffprobe")
        else:
            try:
                result = subprocess.run([probe, "-v", "error", "-show_entries", "stream=codec_type:format=duration", "-of", "json", str(sample)], capture_output=True, text=True, timeout=15, check=True)
                sample_data = json.loads(result.stdout)
                stream_types = {item.get("codec_type") for item in sample_data.get("streams", []) if isinstance(item, dict)}
                if not {"video", "audio"}.issubset(stream_types):
                    errors.append(f"{label}.motion_review.sample 必须是真实含声音的视频样段")
                sample_duration = float(sample_data.get("format", {}).get("duration", 0))
                if not sample_duration > 0 or (valid_window and abs(sample_duration - (float(end) - float(start))) > 0.25):
                    errors.append(f"{label}.motion_review.sample 时长与正式音频截取范围不一致")
            except (OSError, subprocess.SubprocessError, ValueError, TypeError) as exc:
                errors.append(f"{label}.motion_review.sample 无法确认为真实视频样段：{exc}")
    return errors


def validate_character_profile(path: Path, project_root: Path | None = None) -> list[str]:
    if project_root is not None:
        project_root = project_root.resolve()
    data, errors = load_object(path)
    if data is None:
        return errors
    if data.get("schema_version") != "1.0":
        errors.append(f"{path.name}.schema_version 必须为 1.0")
    if not nonempty_text(data.get("character_id")):
        errors.append(f"{path.name} 缺少 character_id")
    if data.get("status") != "locked":
        errors.append(f"{path.name} 的人物尚未 locked")
    if not nonempty_text(data.get("authorization")):
        errors.append(f"{path.name} 缺少人物授权说明")

    presentation = data.get("presentation")
    errors.extend(validate_presentation_mode(data, path.name))
    static_presenter = isinstance(presentation, dict) and presentation.get("mode") == "static-presenter"
    audio_presenter = isinstance(presentation, dict) and presentation.get("mode") == "audio-driven-presenter"
    fixed_presenter = static_presenter or audio_presenter

    identity = data.get("identity")
    if not isinstance(identity, dict):
        errors.append(f"{path.name} 缺少 identity")
    else:
        for field in ("age_presentation", "face", "hair", "body", "wardrobe", "palette", "visual_style"):
            if not nonempty_text(identity.get(field)):
                errors.append(f"{path.name}.identity 缺少 {field}")
        for field in ("fixed_traits", "allowed_variations", "forbidden_variations"):
            values = text_list(identity.get(field))
            if values is None or not values or any(not item.strip() for item in values):
                errors.append(f"{path.name}.identity.{field} 必须包含明确规则")

    references = data.get("reference_assets")
    if not isinstance(references, list) or not references:
        errors.append(f"{path.name}.reference_assets 必须包含身份锚点")
    else:
        for index, item in enumerate(references):
            label = f"{path.name}.reference_assets[{index}]"
            if not isinstance(item, dict):
                errors.append(f"{label} 必须为对象")
                continue
            target, binding_errors = validate_bound_file(path, item.get("path"), item.get("sha256"), label)
            errors.extend(binding_errors)
            if target is not None and project_root is not None and target != project_root and project_root not in target.parents:
                errors.append(f"{label} 必须整理到当前视频项目内")
            if item.get("role") not in {"identity-anchor", "front", "side", "expression", "wardrobe"}:
                errors.append(f"{label}.role 无效")
            if not nonempty_text(item.get("authorization")):
                errors.append(f"{label} 缺少素材授权")

    if fixed_presenter:
        if not isinstance(references, list) or not any(
            isinstance(item, dict) and item.get("role") == "identity-anchor" for item in references
        ):
            errors.append(f"{path.name} 的静态讲解角色必须复用已批准原图为 identity-anchor")
        not_applicable = presentation.get("review_not_applicable")
        if not isinstance(not_applicable, dict):
            errors.append(f"{path.name}.presentation.review_not_applicable 必须写明动作复核不适用原因")
            not_applicable = {}
        for field in ("representative_actions_reviewed", "action_silhouette_duplicates_checked"):
            if not nonempty_text(not_applicable.get(field)):
                errors.append(f"{path.name}.presentation.review_not_applicable 缺少 {field} 原因")

    continuity = data.get("continuity")
    if not isinstance(continuity, dict):
        errors.append(f"{path.name} 缺少 continuity")
    else:
        if continuity.get("same_identity_across_rolls") is not True:
            errors.append(f"{path.name} 必须在 A-roll 与 B-roll 中保持同一身份")
        applies = text_list(continuity.get("applies_to"))
        if applies is None or not applies or not set(applies).issubset(ROLL_USES):
            errors.append(f"{path.name}.continuity.applies_to 无效")
        required_reviews = ("identity_anchor_reviewed",) if fixed_presenter else ("identity_anchor_reviewed", "representative_actions_reviewed")
        for field in required_reviews:
            if continuity.get(field) is not True:
                errors.append(f"{path.name}.continuity.{field} 尚未通过")
        if fixed_presenter:
            for field in ("representative_actions_reviewed", "action_silhouette_duplicates_checked"):
                if continuity.get(field) is not False:
                    errors.append(f"{path.name}.continuity.{field} 必须为 false，固定站姿人物不得伪填身体动作已审")

    if audio_presenter or is_subtle_presenter(data):
        errors.extend(validate_presenter_motion(path, data, project_root or path.parent.resolve(), label=path.name))

    approval = data.get("approval")
    if not isinstance(approval, dict) or approval.get("approved") is not True:
        errors.append(f"{path.name} 尚未获得用户身份锁定确认")
    else:
        for field in ("approval_message", "approved_at"):
            if not nonempty_text(approval.get(field)):
                errors.append(f"{path.name}.approval 缺少 {field}")
    return errors


def validate_asset_review_plan(path: Path, project_root: Path | None = None) -> list[str]:
    if project_root is not None:
        project_root = project_root.resolve()
    data, errors = load_object(path)
    if data is None:
        return errors
    if data.get("schema_version") != "1.0":
        errors.append("asset-review-plan.schema_version 必须为 1.0")
    if data.get("workflow_mode") not in WORKFLOW_MODES:
        errors.append("asset-review-plan.workflow_mode 无效")
    review_mode = data.get("review_mode")
    if review_mode not in REVIEW_MODES:
        errors.append("asset-review-plan.review_mode 无效")
    risk_flags = text_list(data.get("risk_flags"))
    if risk_flags is None or not set(risk_flags).issubset(RISK_FLAGS):
        errors.append("asset-review-plan.risk_flags 无效")
        risk_set: set[str] = set()
    else:
        risk_set = set(risk_flags)
    if risk_set and not nonempty_text(data.get("risk_reason")):
        errors.append("原始素材存在风险时必须记录 risk_reason")
    if risk_set and review_mode != "risk-first":
        errors.append("人物、品牌、隐私、授权或真实证据风险素材必须先单独审片")

    count = data.get("raw_asset_count")
    if not isinstance(count, int) or isinstance(count, bool) or count < 0:
        errors.append("asset-review-plan.raw_asset_count 必须为非负整数")
        count = 0
    contact = data.get("raw_asset_contact_sheet")
    if not isinstance(contact, dict):
        errors.append("asset-review-plan 缺少 raw_asset_contact_sheet")
    elif count > 0:
        target, binding_errors = validate_bound_file(path, contact.get("path"), contact.get("sha256"), "原始素材联系表")
        errors.extend(binding_errors)
        if target is not None and project_root is not None and target != project_root and project_root not in target.parents:
            errors.append("原始素材联系表必须位于当前项目内")
        if contact.get("machine_checked") is not True:
            errors.append("原始素材联系表尚未完成机器检查")

    identity = data.get("identity_anchor_review")
    identity_required = bool(risk_set & IDENTITY_RISKS)
    if not isinstance(identity, dict):
        errors.append("asset-review-plan 缺少 identity_anchor_review")
    else:
        if identity.get("required") is not identity_required:
            errors.append("identity_anchor_review.required 与人物/品牌风险不一致")
        paths = text_list(identity.get("paths"))
        if paths is None:
            errors.append("identity_anchor_review.paths 必须为数组")
        elif identity_required:
            if not paths:
                errors.append("反复人物或品牌角色必须提供身份锚点样张")
            for value in paths:
                target = resolve_path(path, value)
                if target is None or not target.is_file() or target.stat().st_size == 0:
                    errors.append(f"身份锚点样张不存在或为空：{value}")
            if identity.get("approved") is not True:
                errors.append("身份锚点样张尚未获得用户确认")

    review = data.get("user_review")
    if not isinstance(review, dict):
        errors.append("asset-review-plan 缺少 user_review")
    else:
        must_preapprove = review_mode == "risk-first"
        if review.get("required_before_storyboard") is not must_preapprove:
            errors.append("user_review.required_before_storyboard 与 review_mode 不一致")
        if review.get("approved") is not True:
            errors.append("原始素材尚未在对应确认包中通过")
        if review.get("approval_stage") != "assets":
            errors.append("原始素材确认必须写入 assets 阶段")
    return errors


def validate_platform_profiles(path: Path) -> list[str]:
    data, errors = load_object(path)
    if data is None:
        return errors
    if data.get("schema_version") != "1.0":
        errors.append("platform-overlay-profiles.schema_version 必须为 1.0")
    profiles = data.get("profiles")
    if not isinstance(profiles, dict) or not profiles:
        return [*errors, "platform-overlay-profiles.profiles 不能为空"]
    for required in ("generic-portrait", "douyin-portrait", "generic-landscape"):
        if required not in profiles:
            errors.append(f"缺少必需平台安全区：{required}")
    for profile_id, profile in profiles.items():
        label = f"profiles.{profile_id}"
        if not isinstance(profile, dict):
            errors.append(f"{label} 必须为对象")
            continue
        if profile.get("format") not in {"portrait", "landscape"}:
            errors.append(f"{label}.format 无效")
        safe = profile.get("safe_area_pixels")
        if not isinstance(safe, dict) or any(not isinstance(safe.get(side), int) or safe.get(side) < 0 for side in ("left", "right", "top", "bottom")):
            errors.append(f"{label}.safe_area_pixels 无效")
        ratios = profile.get("occlusion_ratio")
        if not isinstance(ratios, dict):
            errors.append(f"{label}.occlusion_ratio 无效")
        else:
            for side in ("left", "right", "top", "bottom"):
                value = ratios.get(side)
                if not isinstance(value, (int, float)) or isinstance(value, bool) or not 0 <= float(value) <= 0.4:
                    errors.append(f"{label}.occlusion_ratio.{side} 必须在 0—0.4 之间")
        if not isinstance(profile.get("review_overlay_required"), bool):
            errors.append(f"{label}.review_overlay_required 必须为布尔值")
        layers = text_list(profile.get("overlay_layers"))
        if layers is None:
            errors.append(f"{label}.overlay_layers 必须为字符串数组")
        elif profile.get("review_overlay_required") is True and not layers:
            errors.append(f"{label} 需要审查遮挡层但未定义 overlay_layers")
    return errors


def validate_project(project: Path) -> list[str]:
    project = project.resolve()
    shot_path = project / "shot-readiness.json"
    shot, errors = load_object(shot_path)
    if shot is None:
        return errors
    if shot.get("schema_version") not in {"2.5", "2.6"}:
        return []

    errors.extend(validate_story_contract(project / "story-contract.json"))
    errors.extend(validate_asset_review_plan(project / "asset-review-plan.json", project))
    profiles = Path(__file__).resolve().parents[1] / "assets/platform-overlay-profiles.json"
    errors.extend(validate_platform_profiles(profiles))

    memory_binding = shot.get("memory_binding")
    if isinstance(memory_binding, dict) and memory_binding.get("mode") != "disabled":
        memory_path = resolve_path(shot_path, memory_binding.get("path"))
        if memory_path is None:
            errors.append("memory_binding 缺少可读取的创作记忆路径")
        else:
            applied_ids = text_list(memory_binding.get("applied_memory_ids")) or []
            errors.extend(validate_creator_memory(memory_path, applied_ids))
            memory_data, memory_errors = load_object(memory_path)
            if not memory_errors and memory_data is not None and memory_data.get("storage_scope") != memory_binding.get("mode"):
                errors.append("memory_binding.mode 与 creator-memory.storage_scope 不一致")

    registry = shot.get("character_profiles")
    if isinstance(registry, list):
        for item in registry:
            if not isinstance(item, dict):
                continue
            profile_path = resolve_path(shot_path, item.get("path"))
            if profile_path is not None:
                errors.extend(validate_character_profile(profile_path, project))
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="校验叙事、创作记忆、人物一致性与原始素材审片契约")
    parser.add_argument("project", type=Path, help="视频项目目录")
    args = parser.parse_args()
    project = args.project.expanduser().resolve()
    if not project.is_dir():
        parser.error(f"项目目录不存在：{project}")
    errors = validate_project(project)
    if errors:
        for error in errors:
            print(f"FAIL {error}")
        return 1
    print("PASS 叙事、平台安全区、创作记忆、人物一致性与原始素材审片契约通过")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

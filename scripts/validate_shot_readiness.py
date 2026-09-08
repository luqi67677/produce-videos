#!/usr/bin/env python3
"""渲染前检查镜头语义、素材授权、复用、禁用词和安全区。"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import unicodedata
from pathlib import Path
from typing import Any


VALID_FORMATS = {"portrait", "landscape"}
VALID_SOURCE_TYPES = {"real", "official", "generated"}
VALID_MEDIA_TYPES = {"video", "image", "audio"}
VALID_HUMAN_PRESENCE = {"none", "supplied-person", "supplied-character", "generated-scene-illustration"}
VALID_COMPOSITION_SOURCES = {"storyboard", "raw-fullscreen"}
VALID_FOCUS_MARKERS = {"none", "cursor-ring", "underline", "local-highlight", "short-arrow", "hand-drawn-circle"}
VALID_FALLBACK_MODES = {"none", "keyframe", "generated-illustration"}
PERSISTENT_GRAMMARS = {"sequential-list", "continuous-flow", "timeline", "step-ladder"}
ARROW_SYMBOLS = {"arrow", "→", "箭头"}
ABSENCE_WORDS = {"没有", "无", "排除", "不采用", "不存在", "absence", "none"}
VALID_PRIVACY_TREATMENTS = {"crop", "opaque-mask"}
VALID_REVISION_MODES = {"initial", "revision"}
VALID_PREVIEW_KINDS = {"native-frame", "contact-sheet", "motion-sample"}
VALID_ROLL_TYPES = {"a-roll", "b-roll", "hybrid", "graphic-led"}
VALID_VISUAL_SOURCES = {"user-provided", "official", "verified-keyframe", "generated-still", "code-motion", "text-only"}
VISUAL_SOURCE_ORDER = ["user-provided", "official", "verified-keyframe", "generated-still", "code-motion", "text-only"]
VALID_TRANSITIONS = {"none", "hard-cut", "match-cut", "insert-cut", "graphic-bridge"}
VALID_LAYOUT_ADAPTATIONS = {"native-landscape", "portrait-reflow", "custom-verified"}
VALID_MEMORY_MODES = {"disabled", "project-only", "workspace-opt-in"}
VALID_PLATFORM_CALIBRATION_SOURCES = {"bundled-conservative-default", "user-recent-screenshot"}
VALID_SHOT_READINESS_SCHEMAS = {"1.0", "2.0", "2.1", "2.2", "2.3", "2.4", "2.5", "2.6"}
DESIGN_SCHEMAS = {"2.4", "2.5", "2.6"}
FOUNDATION_SCHEMAS = {"2.5", "2.6"}
FINE_SHOT_SCHEMAS = {"2.6"}
VALID_PROOF_CLAIMS = {"none", "quantity", "workflow", "result", "installation", "comparison"}
VALID_EVIDENCE_MODES = {"not-applicable", "real-preview", "verified-result", "illustration", "text-only"}
SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$", re.IGNORECASE)


def nonempty_text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def text_list(value: Any) -> list[str] | None:
    if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
        return None
    return value


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


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def normalize_spoken_text(value: Any) -> str:
    return "".join(
        character.casefold()
        for character in str(value)
        if not character.isspace() and unicodedata.category(character)[0] not in {"P", "Z"}
    )


def validate_fine_shots(
    contract_path: Path,
    shots: Any,
    expected_segments: dict[str, dict[str, Any]],
    contract_duration: float | None,
    character_ids: set[str],
) -> list[str]:
    errors: list[str] = []
    if not isinstance(shots, list) or not shots:
        return ["schema 2.6 的 shots 必须包含逐个剪辑镜头，不能只校验章节级 scenes"]

    project_root = contract_path.parent.resolve()
    seen_shot_ids: set[str] = set()
    previous_end: float | None = None
    excerpts_by_segment: dict[str, list[str]] = {}
    used_segment_ids: set[str] = set()
    seen_action_signatures: dict[str, str] = {}

    for index, shot in enumerate(shots):
        label = f"shots[{index}]"
        if not isinstance(shot, dict):
            errors.append(f"{label} 必须为对象")
            continue

        shot_id = str(shot.get("shot_id", "")).strip()
        if not shot_id or shot_id in seen_shot_ids:
            errors.append(f"{label} 缺少唯一 shot_id")
        else:
            seen_shot_ids.add(shot_id)
            label = shot_id

        segment_id = str(shot.get("narration_segment_id", "")).strip()
        excerpt = str(shot.get("narration_excerpt", "")).strip()
        if not segment_id:
            errors.append(f"{label} 缺少 narration_segment_id")
        else:
            used_segment_ids.add(segment_id)
            excerpts_by_segment.setdefault(segment_id, []).append(excerpt)
            if expected_segments and segment_id not in expected_segments:
                errors.append(f"{label} 绑定了旁白契约中不存在的段：{segment_id}")
        if not excerpt:
            errors.append(f"{label} 缺少 narration_excerpt")
        if not nonempty_text(shot.get("visual_duty")):
            errors.append(f"{label} 缺少与当前口播对应的 visual_duty")
        if shot.get("alignment_verified") is not True:
            errors.append(f"{label} 尚未逐句确认声画对应")

        roll_type = shot.get("roll_type")
        if roll_type not in VALID_ROLL_TYPES:
            errors.append(f"{label}.roll_type 无效")
        if roll_type in {"b-roll", "hybrid"} and not nonempty_text(shot.get("covers")):
            errors.append(f"{label} 的 B-roll 必须填写 covers")

        start = shot.get("timeline_start_seconds")
        end = shot.get("timeline_end_seconds")
        duration = shot.get("duration_seconds")
        if any(not isinstance(value, (int, float)) or isinstance(value, bool) for value in (start, end, duration)):
            errors.append(f"{label} 缺少有效的逐镜时间范围")
        else:
            start_value = float(start)
            end_value = float(end)
            duration_value = float(duration)
            if start_value < 0 or end_value <= start_value or duration_value <= 0:
                errors.append(f"{label} 的逐镜时间范围无效")
            elif abs((end_value - start_value) - duration_value) > 0.05:
                errors.append(f"{label} 的 duration_seconds 与起止时间不一致")
            if previous_end is None and start_value > 0.05:
                errors.append(f"{label} 没有从 0 秒附近开始")
            if previous_end is not None and abs(start_value - previous_end) > 0.05:
                errors.append(f"{label} 与上一镜存在空洞或重叠")
            previous_end = end_value

        boundary = shot.get("semantic_boundary")
        if not isinstance(boundary, dict):
            errors.append(f"{label} 缺少 semantic_boundary")
        else:
            for field in ("starts_on_semantic_boundary", "ends_on_semantic_boundary", "next_visual_after_narration"):
                if boundary.get(field) is not True:
                    errors.append(f"{label}.semantic_boundary.{field} 尚未通过")

        frame_path = resolve_path(contract_path, shot.get("reviewed_frame_path"))
        if frame_path is None or not frame_path.is_file():
            errors.append(f"{label} 缺少可读取的逐镜审查帧")
        elif frame_path != project_root and project_root not in frame_path.parents:
            errors.append(f"{label} 的逐镜审查帧必须位于当前项目内")

        layout_review = shot.get("layout_review")
        if not isinstance(layout_review, dict):
            errors.append(f"{label} 缺少逐镜 layout_review")
        else:
            for field in (
                "alignment_verified",
                "text_overflow_free",
                "orphan_line_free",
                "brand_case_preserved",
                "balanced_density",
            ):
                if layout_review.get(field) is not True:
                    errors.append(f"{label}.layout_review.{field} 尚未通过")

        rendered_text = text_list(shot.get("rendered_text"))
        production_notes = text_list(shot.get("production_notes"))
        if rendered_text is None:
            errors.append(f"{label}.rendered_text 必须为字符串数组")
            rendered_text = []
        if production_notes is None:
            errors.append(f"{label}.production_notes 必须为字符串数组")
            production_notes = []
        visible_normalized = {normalize_spoken_text(item) for item in rendered_text if normalize_spoken_text(item)}
        note_normalized = {normalize_spoken_text(item) for item in production_notes if normalize_spoken_text(item)}
        if visible_normalized & note_normalized:
            errors.append(f"{label} 把制作说明渲染成了观众文案")
        text_review = shot.get("text_boundary_review")
        if not isinstance(text_review, dict):
            errors.append(f"{label} 缺少 text_boundary_review")
        else:
            for field in ("production_notes_excluded", "privacy_treatment_visual_only", "generic_asset_labels_removed"):
                if text_review.get(field) is not True:
                    errors.append(f"{label}.text_boundary_review.{field} 尚未通过")

        proof = shot.get("proof")
        if not isinstance(proof, dict) or proof.get("claim_type") not in VALID_PROOF_CLAIMS:
            errors.append(f"{label}.proof.claim_type 无效")
        else:
            evidence_mode = proof.get("evidence_mode")
            if evidence_mode not in VALID_EVIDENCE_MODES:
                errors.append(f"{label}.proof.evidence_mode 无效")
            evidence_paths = text_list(proof.get("evidence_asset_paths"))
            if evidence_paths is None:
                errors.append(f"{label}.proof.evidence_asset_paths 必须为字符串数组")
                evidence_paths = []
            if proof.get("claim_type") != "none":
                if evidence_mode not in {"real-preview", "verified-result"}:
                    errors.append(f"{label} 的数量、流程或结果主张必须使用真实预览或已验证结果")
                if not evidence_paths:
                    errors.append(f"{label} 的能力主张不能使用空框或文字口号代替证据")
                if proof.get("complete_context_visible") is not True:
                    errors.append(f"{label} 的真实截图或结果没有完整展示有效上下文")
            for value in evidence_paths:
                evidence_path = resolve_path(contract_path, value)
                if evidence_path is None or not evidence_path.is_file():
                    errors.append(f"{label} 的证据文件不存在：{value}")

        shot_character_ids = text_list(shot.get("character_ids"))
        if shot_character_ids is None:
            errors.append(f"{label}.character_ids 必须为字符串数组")
            shot_character_ids = []
        unknown_characters = set(shot_character_ids) - character_ids
        if unknown_characters:
            errors.append(f"{label} 引用了未锁定人物：{', '.join(sorted(unknown_characters))}")
        if shot_character_ids:
            character_review = shot.get("character_review")
            if not isinstance(character_review, dict):
                errors.append(f"{label} 缺少 character_review")
            else:
                for field in ("action", "action_signature"):
                    if not nonempty_text(character_review.get(field)):
                        errors.append(f"{label}.character_review 缺少 {field}")
                for field in ("pose_matches_visual_duty", "styling_matches_context", "identity_verified", "anatomy_safe"):
                    if character_review.get(field) is not True:
                        errors.append(f"{label}.character_review.{field} 尚未通过")
                signature = str(character_review.get("action_signature", "")).strip()
                if signature:
                    previous_shot = seen_action_signatures.get(signature)
                    if previous_shot is not None:
                        approved = character_review.get("reuse_approved") is True
                        if not approved or not nonempty_text(character_review.get("reuse_reason")):
                            errors.append(f"{label} 与 {previous_shot} 重复人物动作，且没有经审查的叙事理由")
                    seen_action_signatures[signature] = label

    if contract_duration is not None and previous_end is not None and abs(previous_end - contract_duration) > 0.05:
        errors.append(f"逐镜时间线结束于 {previous_end:.3f} 秒，与旁白 {contract_duration:.3f} 秒不一致")

    if expected_segments:
        missing = set(expected_segments) - used_segment_ids
        if missing:
            errors.append(f"逐镜表没有覆盖旁白段：{', '.join(sorted(missing))}")
        for segment_id, segment in expected_segments.items():
            expected_text = normalize_spoken_text(segment.get("display_text", ""))
            actual_text = normalize_spoken_text("".join(excerpts_by_segment.get(segment_id, [])))
            if expected_text != actual_text:
                errors.append(f"{segment_id} 的逐镜口播片段未完整、按顺序覆盖批准稿")
    return errors


def validate_scene_design(scene: dict[str, Any], label: str, schema_version: str = "2.4") -> list[str]:
    errors: list[str] = []
    roll = scene.get("roll")
    if not isinstance(roll, dict) or roll.get("type") not in VALID_ROLL_TYPES:
        errors.append(f"{label}.roll.type 必须为 a-roll、b-roll、hybrid 或 graphic-led")
    else:
        for field in ("narrative_role", "entry_reason", "return_strategy"):
            if not nonempty_text(roll.get(field)):
                errors.append(f"{label}.roll 缺少 {field}")
        if roll.get("type") in {"b-roll", "hybrid"} and not nonempty_text(roll.get("covers")):
            errors.append(f"{label} 的 B-roll 必须写明正在解释的口播 covers")

    strategy = scene.get("visual_source_strategy")
    if not isinstance(strategy, dict) or strategy.get("selected") not in VALID_VISUAL_SOURCES:
        errors.append(f"{label}.visual_source_strategy.selected 无效")
    else:
        if strategy.get("source_order_considered") != VISUAL_SOURCE_ORDER:
            errors.append(f"{label} 必须按真实、官方、关键帧、静态补图、代码动画、纯文字顺序考虑素材")
        if strategy.get("video_model_used") is not False:
            errors.append(f"{label} 禁止由本 Skill 调用视频生成模型")
        if strategy.get("selected") in {"generated-still", "code-motion", "text-only"} and not nonempty_text(strategy.get("gap_reason")):
            errors.append(f"{label} 使用补充视觉时必须写明真实素材缺口")
        if strategy.get("selected") == "generated-still" and strategy.get("generated_still_approved") is not True:
            errors.append(f"{label} 生成静态补图尚未获得开工授权")

    transition = scene.get("transition")
    if not isinstance(transition, dict) or transition.get("type") not in VALID_TRANSITIONS:
        errors.append(f"{label}.transition.type 无效")
    else:
        for field in ("previous_end_state", "next_start_state", "continuity_anchor", "reason"):
            if not nonempty_text(transition.get(field)):
                errors.append(f"{label}.transition 缺少 {field}")

    preset = scene.get("layout_preset")
    if not isinstance(preset, dict):
        errors.append(f"{label}.layout_preset 必须为对象")
    else:
        preset_id = str(preset.get("id", "")).strip()
        preset_path = Path(__file__).resolve().parents[1] / "references/frontend-slides-layouts" / preset_id / "layout.md"
        if not preset_id or ".." in Path(preset_id).parts or not preset_path.is_file():
            errors.append(f"{label}.layout_preset.id 不在 88 套布局目录中")
        if preset.get("adaptation") not in VALID_LAYOUT_ADAPTATIONS:
            errors.append(f"{label}.layout_preset.adaptation 无效")
        if not nonempty_text(preset.get("selection_reason")):
            errors.append(f"{label}.layout_preset 缺少 selection_reason")

    budget = scene.get("composition_budget")
    if not isinstance(budget, dict):
        errors.append(f"{label}.composition_budget 必须为对象")
    else:
        numeric_limits = {
            "focal_points": (1, 1),
            "support_groups": (0, 4),
            "decorative_groups": (0, 1),
            "accent_colors": (0, 2),
            "material_systems": (1, 1),
        }
        for field, (minimum, maximum) in numeric_limits.items():
            value = budget.get(field)
            if not isinstance(value, int) or isinstance(value, bool) or not minimum <= value <= maximum:
                errors.append(f"{label}.composition_budget.{field} 必须在 {minimum}—{maximum} 之间")
        occupied = budget.get("occupied_area_ratio")
        if not isinstance(occupied, (int, float)) or isinstance(occupied, bool) or not 0 < occupied <= 1:
            errors.append(f"{label}.composition_budget.occupied_area_ratio 必须在 0—1 之间")
        elif not 0.38 <= occupied <= 0.8 and not nonempty_text(budget.get("density_exception_reason")):
            errors.append(f"{label} 的画面占用率异常，必须解释为何不会过空或过挤")
        empty = budget.get("largest_empty_area_ratio")
        if not isinstance(empty, (int, float)) or isinstance(empty, bool) or not 0 <= empty < 1:
            errors.append(f"{label}.composition_budget.largest_empty_area_ratio 必须在 0—1 之间")
        elif empty > 0.42 and not nonempty_text(budget.get("intentional_whitespace_reason")):
            errors.append(f"{label} 存在大面积空白，但没有说明其构图职责")
    if schema_version in FOUNDATION_SCHEMAS:
        if not nonempty_text(scene.get("narrative_function")):
            errors.append(f"{label} 缺少 narrative_function")
        continuity = scene.get("continuity")
        if not isinstance(continuity, dict):
            errors.append(f"{label}.continuity 必须为对象")
        else:
            for field in ("entering_state", "leaving_state", "anchor"):
                if not nonempty_text(continuity.get(field)):
                    errors.append(f"{label}.continuity 缺少 {field}")
            if continuity.get("advances_story") is not True:
                errors.append(f"{label} 没有证明本镜头推进了叙事")
            if isinstance(roll, dict) and roll.get("type") in {"b-roll", "hybrid"} and continuity.get("returns_to_main_axis") is not True:
                errors.append(f"{label} 的 B-roll 没有回到主叙事轴")
    return errors


def validate_artifact_binding(contract_path: Path, binding: Any, label: str) -> tuple[Path | None, list[str]]:
    errors: list[str] = []
    if not isinstance(binding, dict):
        return None, [f"缺少 {label}"]
    target = resolve_path(contract_path, binding.get("path"))
    if target is None or not target.is_file():
        errors.append(f"{label} 指向的文件不存在或不可读取")
    else:
        project_root = contract_path.parent.resolve()
        if target != project_root and project_root not in target.parents:
            errors.append(f"{label} 必须位于当前视频项目内")
        expected = str(binding.get("sha256", "")).strip()
        if not SHA256_PATTERN.fullmatch(expected) or file_sha256(target).casefold() != expected.casefold():
            errors.append(f"{label} SHA-256 与实际文件不一致")
    if binding.get("approved") is not True:
        errors.append(f"{label} 尚未批准")
    return target, errors


def validate(path: Path, narration_contract_path: Path | None = None) -> list[str]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return [f"镜头就绪表不存在：{path}"]
    except json.JSONDecodeError as exc:
        return [f"镜头就绪表无法解析：{exc}"]

    errors: list[str] = []
    expected_segments: dict[str, dict[str, Any]] = {}
    contract_duration: float | None = None
    if narration_contract_path is not None:
        try:
            narration_contract = json.loads(narration_contract_path.read_text(encoding="utf-8"))
        except (FileNotFoundError, OSError, json.JSONDecodeError) as exc:
            errors.append(f"无法读取旁白契约：{exc}")
            narration_contract = None
        if isinstance(narration_contract, dict):
            raw_segments = narration_contract.get("segments")
            if isinstance(raw_segments, list):
                expected_segments = {
                    str(segment.get("scene_id", "")).strip(): segment
                    for segment in raw_segments
                    if isinstance(segment, dict) and nonempty_text(segment.get("scene_id"))
                }
            raw_duration = narration_contract.get("duration_seconds")
            if isinstance(raw_duration, (int, float)) and not isinstance(raw_duration, bool) and raw_duration > 0:
                contract_duration = float(raw_duration)

            binding = data.get("narration_binding")
            if not isinstance(binding, dict):
                errors.append("缺少 narration_binding，镜头尚未绑定已批准口播")
            else:
                if binding.get("approved") is not True:
                    errors.append("narration_binding.approved 必须为 true")
                expected_sha = str(binding.get("contract_sha256", "")).strip().casefold()
                actual_sha = file_sha256(narration_contract_path)
                if expected_sha != actual_sha:
                    errors.append("镜头绑定的旁白哈希与本次渲染契约不一致")
                if binding.get("segment_count") != len(expected_segments):
                    errors.append("narration_binding.segment_count 与旁白段数不一致")
                locked_duration = binding.get("locked_duration_seconds")
                if contract_duration is None or not isinstance(locked_duration, (int, float)) or isinstance(locked_duration, bool):
                    errors.append("narration_binding 缺少有效的锁定时长")
                elif abs(float(locked_duration) - contract_duration) > 0.05:
                    errors.append("镜头绑定时长与旁白契约总时长不一致")
    if data.get("format") not in VALID_FORMATS:
        errors.append("format 必须为 portrait 或 landscape")
    if not nonempty_text(data.get("theme_id")):
        errors.append("缺少已锁定的 theme_id")
    if data.get("human_presence") not in VALID_HUMAN_PRESENCE:
        errors.append("human_presence 取值无效")

    schema_version = str(data.get("schema_version", "")).strip()
    if schema_version not in VALID_SHOT_READINESS_SCHEMAS:
        errors.append("schema_version 未受支持；禁止用未知版本跳过镜头门禁")
    character_ids: set[str] = set()
    if schema_version in FOUNDATION_SCHEMAS:
        _, binding_errors = validate_artifact_binding(path, data.get("story_binding"), "story_binding")
        errors.extend(binding_errors)
        _, binding_errors = validate_artifact_binding(path, data.get("asset_review_binding"), "asset_review_binding")
        errors.extend(binding_errors)

        memory = data.get("memory_binding")
        if not isinstance(memory, dict) or memory.get("mode") not in VALID_MEMORY_MODES:
            errors.append("memory_binding.mode 必须为 disabled、project-only 或 workspace-opt-in")
        else:
            applied = text_list(memory.get("applied_memory_ids"))
            if applied is None:
                errors.append("memory_binding.applied_memory_ids 必须为字符串数组")
                applied = []
            if memory.get("mode") == "disabled":
                if nonempty_text(memory.get("path")) or nonempty_text(memory.get("sha256")) or applied:
                    errors.append("关闭创作记忆时不得绑定路径、哈希或历史规则")
                if memory.get("reuse_approved") is not False:
                    errors.append("关闭创作记忆时 reuse_approved 必须为 false")
            else:
                memory_path = resolve_path(path, memory.get("path"))
                if memory_path is None or not memory_path.is_file():
                    errors.append("memory_binding 指向的创作记忆不存在")
                else:
                    expected = str(memory.get("sha256", "")).strip()
                    if not SHA256_PATTERN.fullmatch(expected) or file_sha256(memory_path).casefold() != expected.casefold():
                        errors.append("memory_binding SHA-256 与实际记忆不一致")
                    project_root = path.parent.resolve()
                    if memory.get("mode") == "project-only" and memory_path != project_root and project_root not in memory_path.parents:
                        errors.append("project-only 创作记忆必须位于当前视频项目内")
                if memory.get("mode") == "workspace-opt-in" and memory.get("reuse_approved") is not True:
                    errors.append("跨项目创作记忆尚未获得用户授权")

        platform_overlay = data.get("platform_overlay")
        profiles_path = Path(__file__).resolve().parents[1] / "assets/platform-overlay-profiles.json"
        try:
            profiles = json.loads(profiles_path.read_text(encoding="utf-8")).get("profiles", {})
        except (OSError, json.JSONDecodeError):
            profiles = {}
        if not isinstance(platform_overlay, dict):
            errors.append("缺少 platform_overlay 平台遮挡审查")
        else:
            profile_id = str(platform_overlay.get("profile_id", "")).strip()
            profile = profiles.get(profile_id) if isinstance(profiles, dict) else None
            if not isinstance(profile, dict):
                errors.append("platform_overlay.profile_id 不在平台安全区目录中")
            elif profile.get("format") != data.get("format"):
                errors.append("平台安全区与当前画幅不一致")
            calibration_source = platform_overlay.get("calibration_source")
            if calibration_source not in VALID_PLATFORM_CALIBRATION_SOURCES:
                errors.append("platform_overlay.calibration_source 无效")
            screenshot_calibration = calibration_source == "user-recent-screenshot"
            override = platform_overlay.get("occlusion_ratio_override")
            if override is None:
                override = {}
            if not isinstance(override, dict):
                errors.append("platform_overlay.occlusion_ratio_override 必须为对象")
                override = {}
            if screenshot_calibration:
                evidence_path = resolve_path(path, platform_overlay.get("calibration_evidence_path"))
                project_root = path.parent.resolve()
                if evidence_path is None or not evidence_path.is_file() or evidence_path.stat().st_size == 0:
                    errors.append("使用近期平台截图校准时必须绑定真实截图证据")
                elif evidence_path != project_root and project_root not in evidence_path.parents:
                    errors.append("平台校准截图必须整理到当前视频项目内")
                for side in ("left", "right", "top", "bottom"):
                    value = override.get(side)
                    if not isinstance(value, (int, float)) or isinstance(value, bool) or not 0 <= float(value) <= 0.4:
                        errors.append(f"platform_overlay.occlusion_ratio_override.{side} 必须在 0—0.4 之间")
            elif override:
                errors.append("内置保守配置不得静默附加项目覆盖值")
            overlay_required = isinstance(profile, dict) and profile.get("review_overlay_required") is True
            if overlay_required or screenshot_calibration:
                overlay_path = resolve_path(path, platform_overlay.get("review_overlay_path"))
                if overlay_path is None or not overlay_path.is_file() or overlay_path.stat().st_size == 0:
                    errors.append("当前平台必须生成可关闭的 UI 遮挡审查图")
            if platform_overlay.get("review_only") is not True:
                errors.append("平台 UI 遮挡层只能用于审查，不得进入成片")
            if platform_overlay.get("safe_without_overlay") is not True:
                errors.append("关闭平台遮挡层后，成片本身仍未通过安全区检查")

        registry = data.get("character_profiles")
        if not isinstance(registry, list):
            errors.append("character_profiles 必须为数组")
            registry = []
        for index, item in enumerate(registry):
            label = f"character_profiles[{index}]"
            if not isinstance(item, dict):
                errors.append(f"{label} 必须为对象")
                continue
            character_id = str(item.get("character_id", "")).strip()
            if not character_id:
                errors.append(f"{label} 缺少唯一 character_id")
            elif character_id in character_ids:
                errors.append(f"{label} 缺少唯一 character_id")
            else:
                character_ids.add(character_id)
            profile_path = resolve_path(path, item.get("path"))
            if profile_path is None or not profile_path.is_file():
                errors.append(f"{label} 指向的人物档案不存在")
                continue
            if path.parent.resolve() not in profile_path.parents:
                errors.append(f"{label} 必须位于当前视频项目内")
            expected = str(item.get("sha256", "")).strip()
            if not SHA256_PATTERN.fullmatch(expected) or file_sha256(profile_path).casefold() != expected.casefold():
                errors.append(f"{label} SHA-256 与实际档案不一致")
            try:
                profile_data = json.loads(profile_path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                profile_data = {}
            if profile_data.get("character_id") != character_id or profile_data.get("status") != "locked":
                errors.append(f"{label} 的人物 ID 不一致或尚未锁定")
            if schema_version in FINE_SHOT_SCHEMAS:
                identity = profile_data.get("identity")
                if not isinstance(identity, dict):
                    errors.append(f"{label} 缺少人物 identity")
                else:
                    for field in ("wardrobe", "styling_context", "pose_language"):
                        if not nonempty_text(identity.get(field)):
                            errors.append(f"{label}.identity 缺少 {field}")
                continuity = profile_data.get("continuity")
                if not isinstance(continuity, dict):
                    errors.append(f"{label} 缺少人物 continuity")
                else:
                    for field in (
                        "identity_anchor_reviewed",
                        "wardrobe_context_reviewed",
                        "representative_actions_reviewed",
                        "action_silhouette_duplicates_checked",
                    ):
                        if continuity.get(field) is not True:
                            errors.append(f"{label}.continuity.{field} 尚未通过")
        if data.get("human_presence") in {"supplied-character", "generated-scene-illustration"} and not character_ids:
            errors.append("反复使用人物或生成角色时必须锁定 character profile")

    privacy_targets = data.get("privacy_targets")
    privacy_by_id: dict[str, dict[str, Any]] = {}
    if not isinstance(privacy_targets, list):
        errors.append("privacy_targets 必须为数组")
        privacy_targets = []
    for index, target in enumerate(privacy_targets):
        label = f"privacy_targets[{index}]"
        if not isinstance(target, dict):
            errors.append(f"{label} 必须为对象")
            continue
        target_id = str(target.get("target_id", "")).strip()
        if not target_id:
            errors.append(f"{label} 缺少 target_id")
        elif target_id in privacy_by_id:
            errors.append(f"privacy target 重复：{target_id}")
        else:
            privacy_by_id[target_id] = target
        if not nonempty_text(target.get("exact_text_or_region")):
            errors.append(f"{label} 缺少 exact_text_or_region")
        asset_ids = text_list(target.get("asset_ids"))
        if asset_ids is None or not asset_ids or any(not item.strip() for item in asset_ids):
            errors.append(f"{label}.asset_ids 必须包含目标可能出现的素材 ID")
        if target.get("treatment") not in VALID_PRIVACY_TREATMENTS:
            errors.append(f"{label}.treatment 必须为 crop 或 opaque-mask")

    forbidden_terms = text_list(data.get("forbidden_terms"))
    if forbidden_terms is None:
        errors.append("forbidden_terms 必须为字符串数组")
        forbidden_terms = []
    forbidden_terms = [term.strip() for term in forbidden_terms if term.strip()]

    subtitle = data.get("subtitle")
    if not isinstance(subtitle, dict):
        errors.append("subtitle 必须为对象")
    else:
        if subtitle.get("layer_count") != 1:
            errors.append("subtitle.layer_count 必须为 1，禁止双层字幕")
        if not nonempty_text(subtitle.get("renderer")):
            errors.append("subtitle.renderer 必须声明唯一字幕渲染器")

    watermark = data.get("watermark")
    watermark_enabled = isinstance(watermark, dict) and watermark.get("enabled") is True
    if not isinstance(watermark, dict):
        errors.append("watermark 必须为对象")
    elif watermark_enabled:
        if not nonempty_text(watermark.get("asset")):
            errors.append("启用水印时必须提供已授权 asset")
        if watermark.get("position") not in {"top-left", "top-right", "bottom-left", "bottom-right"}:
            errors.append("水印 position 取值无效")

    audio = data.get("audio")
    if not isinstance(audio, dict):
        errors.append("audio 必须为对象")
    else:
        music_gap = audio.get("music_db_below_voice")
        fade_out = audio.get("fade_out_seconds")
        if not isinstance(music_gap, (int, float)) or not 7 <= music_gap <= 18:
            errors.append("music_db_below_voice 应在 7—18 dB 之间")
        if not isinstance(fade_out, (int, float)) or not 3 <= fade_out <= 8:
            errors.append("fade_out_seconds 应在 3—8 秒之间")

    scenes = data.get("scenes")
    if not isinstance(scenes, list) or not scenes:
        errors.append("scenes 必须包含至少一个镜头")
        return errors

    seen_scene_ids: set[str] = set()
    previous_assets: set[str] = set()
    repeated_run_seconds = 0.0
    total_scene_duration = 0.0
    used_segment_ids: set[str] = set()
    seen_visual_signatures: dict[str, tuple[str, str]] = {}
    seen_action_signatures: dict[str, tuple[str, str]] = {}
    scene_records: dict[str, dict[str, Any]] = {}

    for index, scene in enumerate(scenes):
        label = f"scenes[{index}]"
        if not isinstance(scene, dict):
            errors.append(f"{label} 必须为对象")
            continue

        scene_id = str(scene.get("scene_id", "")).strip()
        if not scene_id:
            errors.append(f"{label} 缺少 scene_id")
        elif scene_id in seen_scene_ids:
            errors.append(f"scene_id 重复：{scene_id}")
        else:
            seen_scene_ids.add(scene_id)
            scene_records[scene_id] = scene
        label = scene_id or label

        if schema_version in DESIGN_SCHEMAS:
            errors.extend(validate_scene_design(scene, label, schema_version))

        duration = scene.get("duration_seconds")
        if not isinstance(duration, (int, float)) or duration <= 0:
            errors.append(f"{label} 的 duration_seconds 必须大于 0")
            duration = 0.0
        total_scene_duration += float(duration)

        segment_ids = text_list(scene.get("narration_segment_ids"))
        if segment_ids is None or len(segment_ids) != 1 or not nonempty_text(segment_ids[0]):
            errors.append(f"{label}.narration_segment_ids 必须且只能绑定一个旁白段")
        else:
            segment_id = segment_ids[0].strip()
            if segment_id in used_segment_ids:
                errors.append(f"旁白段被多个镜头重复使用：{segment_id}")
            used_segment_ids.add(segment_id)
            if narration_contract_path is not None:
                expected = expected_segments.get(segment_id)
                if expected is None:
                    errors.append(f"{label} 绑定了旁白契约中不存在的段：{segment_id}")
                elif str(scene.get("narration", "")).strip() != str(expected.get("display_text", "")).strip():
                    errors.append(f"{label} 的旁白与 {segment_id} 的 display_text 不一致")

        for field in ("information_contribution", "visual_signature"):
            if not nonempty_text(scene.get(field)):
                errors.append(f"{label} 缺少 {field}")
        if scene.get("redundant") is not False:
            errors.append(f"{label} 被标记为重复或尚未完成无废镜头检查")

        visual_evidence = scene.get("visual_evidence")
        if not isinstance(visual_evidence, dict):
            errors.append(f"{label}.visual_evidence 必须为对象")
        else:
            for field in ("narration_claim", "on_screen_evidence"):
                if not nonempty_text(visual_evidence.get(field)):
                    errors.append(f"{label}.visual_evidence 缺少 {field}")
            if visual_evidence.get("verified") is not True:
                errors.append(f"{label} 的字幕与画面证据尚未一一核对")

        max_unchanged = scene.get("max_unchanged_seconds")
        if not isinstance(max_unchanged, (int, float)) or isinstance(max_unchanged, bool) or max_unchanged <= 0:
            errors.append(f"{label}.max_unchanged_seconds 必须为正数")
        else:
            if max_unchanged > float(duration) + 0.01:
                errors.append(f"{label}.max_unchanged_seconds 不能超过镜头时长")
            if max_unchanged > 6:
                errors.append(f"{label} 的同一画面连续停留超过 6 秒")
            elif max_unchanged > 4 and not nonempty_text(scene.get("long_hold_reason")):
                errors.append(f"{label} 超过 4 秒没有画面变化，但未说明必要阅读或连续操作理由")

        visual_signature = str(scene.get("visual_signature", "")).strip()
        if visual_signature:
            previous_visual = seen_visual_signatures.get(visual_signature)
            if previous_visual is not None:
                previous_scene_id, previous_end_state = previous_visual
                if scene.get("reuse_advances_state") is not True or not nonempty_text(scene.get("reuse_reason")):
                    errors.append(f"{label} 与 {previous_scene_id} 重复同一视觉，但未证明状态推进")
                if str(scene.get("end_state", "")).strip() == previous_end_state:
                    errors.append(f"{label} 与 {previous_scene_id} 重复同一视觉和结束状态")
            seen_visual_signatures[visual_signature] = (label, str(scene.get("end_state", "")).strip())

        for field in ("semantic_role", "background_token", "motion_grammar", "start_state", "change_state", "end_state", "exit_state"):
            if not nonempty_text(scene.get(field)):
                errors.append(f"{label} 缺少 {field}")

        motion_grammar = str(scene.get("motion_grammar", "")).strip()
        motion_steps = scene.get("motion_steps")
        if not isinstance(motion_steps, list) or not motion_steps:
            errors.append(f"{label} 缺少按旁白线索排列的 motion_steps")
        else:
            for step_index, step in enumerate(motion_steps):
                step_label = f"{label}.motion_steps[{step_index}]"
                if not isinstance(step, dict):
                    errors.append(f"{step_label} 必须为对象")
                    continue
                if not nonempty_text(step.get("cue_text")):
                    errors.append(f"{step_label} 缺少 cue_text")
                if not nonempty_text(step.get("action")):
                    errors.append(f"{step_label} 缺少 action")
                if not isinstance(step.get("persists"), bool):
                    errors.append(f"{step_label}.persists 必须为布尔值")
                elif motion_grammar in PERSISTENT_GRAMMARS and step.get("persists") is not True:
                    errors.append(f"{step_label} 属于连续建立结构，完成状态必须保持")

        audience_text = text_list(scene.get("audience_text"))
        internal_notes = text_list(scene.get("internal_notes"))
        if audience_text is None:
            errors.append(f"{label} 的 audience_text 必须为字符串数组")
            audience_text = []
        if internal_notes is None:
            errors.append(f"{label} 的 internal_notes 必须为字符串数组")
            internal_notes = []

        visible_text = "\n".join([str(scene.get("narration", "")), *audience_text]).casefold()
        for term in forbidden_terms:
            if term.casefold() in visible_text:
                errors.append(f"{label} 的观众可见文字包含禁用词：{term}")
        for note in internal_notes:
            if note.strip() and note.strip().casefold() in visible_text:
                errors.append(f"{label} 把内部制作备注写进了观众可见文字：{note}")

        primary_asset_ids = scene.get("primary_asset_ids")
        if not isinstance(primary_asset_ids, list) or not primary_asset_ids or any(not nonempty_text(item) for item in primary_asset_ids):
            errors.append(f"{label} 缺少有效 primary_asset_ids")
            current_assets: set[str] = set()
        else:
            current_assets = {str(item).strip() for item in primary_asset_ids}

        assets = scene.get("assets")
        if not isinstance(assets, list) or not assets:
            errors.append(f"{label} 缺少 assets")
        else:
            declared_ids: set[str] = set()
            for asset_index, asset in enumerate(assets):
                asset_label = f"{label}.assets[{asset_index}]"
                if not isinstance(asset, dict):
                    errors.append(f"{asset_label} 必须为对象")
                    continue
                asset_id = str(asset.get("asset_id", "")).strip()
                if not asset_id:
                    errors.append(f"{asset_label} 缺少 asset_id")
                else:
                    declared_ids.add(asset_id)
                if asset.get("source_type") not in VALID_SOURCE_TYPES:
                    errors.append(f"{asset_label} 的 source_type 必须为 real、official 或 generated")
                for field in ("path", "purpose", "authorization"):
                    if not nonempty_text(asset.get(field)):
                        errors.append(f"{asset_label} 缺少 {field}")
                asset_path = resolve_path(path, asset.get("path"))
                if asset_path is None or not asset_path.is_file():
                    errors.append(f"{asset_label} 的素材文件不存在或不可读取")
                media_type = asset.get("media_type")
                if media_type not in VALID_MEDIA_TYPES:
                    errors.append(f"{asset_label}.media_type 必须为 video、image 或 audio")
                if media_type == "video":
                    source_window = asset.get("source_window")
                    if not isinstance(source_window, dict):
                        errors.append(f"{asset_label} 是视频但缺少 source_window")
                    else:
                        in_seconds = source_window.get("in_seconds")
                        out_seconds = source_window.get("out_seconds")
                        if not isinstance(in_seconds, (int, float)) or in_seconds < 0:
                            errors.append(f"{asset_label}.source_window.in_seconds 必须大于等于 0")
                        if not isinstance(out_seconds, (int, float)) or not isinstance(in_seconds, (int, float)) or out_seconds <= in_seconds:
                            errors.append(f"{asset_label}.source_window.out_seconds 必须大于入点")
                        if not nonempty_text(source_window.get("action_evidence")):
                            errors.append(f"{asset_label}.source_window 缺少真实操作证据 action_evidence")
            missing_ids = current_assets - declared_ids
            if missing_ids:
                errors.append(f"{label} 的主素材未在 assets 中声明：{', '.join(sorted(missing_ids))}")

        composition_source = scene.get("composition_source")
        if composition_source not in VALID_COMPOSITION_SOURCES:
            errors.append(f"{label}.composition_source 必须为 storyboard 或 raw-fullscreen")
        if not nonempty_text(scene.get("storyboard_frame_path")):
            errors.append(f"{label} 缺少实际消费的 storyboard_frame_path")
        storyboard_frame = resolve_path(path, scene.get("storyboard_frame_path"))
        if storyboard_frame is None or not storyboard_frame.is_file():
            errors.append(f"{label} 的 storyboard_frame_path 不存在或不可读取")
        storyboard_state_ids = text_list(scene.get("storyboard_state_ids"))
        if storyboard_state_ids is None or not {"start", "change", "end"}.issubset(set(storyboard_state_ids)):
            errors.append(f"{label}.storyboard_state_ids 必须包含 start、change、end")

        layout_review = scene.get("layout_review")
        if not isinstance(layout_review, dict):
            errors.append(f"{label}.layout_review 必须为对象")
        else:
            reviewed_frame = resolve_path(path, layout_review.get("reviewed_frame_path"))
            if reviewed_frame is None or not reviewed_frame.is_file():
                errors.append(f"{label}.layout_review 缺少可读取的 reviewed_frame_path")
            for field in (
                "alignment_verified",
                "text_overflow_free",
                "orphan_graphics_free",
                "connections_verified",
                "intentional_whitespace",
            ):
                if layout_review.get(field) is not True:
                    errors.append(f"{label}.layout_review.{field} 尚未通过")
            if schema_version in DESIGN_SCHEMAS:
                for field in (
                    "single_focal_point",
                    "balanced_density",
                    "clean_edges",
                    "single_material_system",
                    "dirty_overlays_free",
                    "crop_remnants_free",
                    "pause_frames_finished",
                ):
                    if layout_review.get(field) is not True:
                        errors.append(f"{label}.layout_review.{field} 尚未通过")
        if scene.get("decorative_outer_frame") is not False:
            if scene.get("decorative_outer_frame") is not True:
                errors.append(f"{label}.decorative_outer_frame 必须为布尔值")
            elif not nonempty_text(scene.get("decorative_outer_frame_reason")):
                errors.append(f"{label} 使用装饰外框但缺少分镜中的叙事理由")

        focus_target = scene.get("focus_target")
        if not isinstance(focus_target, dict) or not isinstance(focus_target.get("required"), bool):
            errors.append(f"{label}.focus_target 必须声明 required")
        elif focus_target.get("required") is True:
            for field in ("label", "cue_text"):
                if not nonempty_text(focus_target.get(field)):
                    errors.append(f"{label}.focus_target 缺少 {field}")
            if focus_target.get("marker") not in VALID_FOCUS_MARKERS - {"none"}:
                errors.append(f"{label}.focus_target.marker 不是允许的局部标注")
            focus_start = focus_target.get("start_seconds")
            focus_end = focus_target.get("end_seconds")
            if not isinstance(focus_start, (int, float)) or not isinstance(focus_end, (int, float)) or not 0 <= focus_start < focus_end <= float(duration):
                errors.append(f"{label}.focus_target 时间必须位于镜头时长内")
            area_ratio = focus_target.get("area_ratio")
            if not isinstance(area_ratio, (int, float)) or not 0 < area_ratio <= 0.2:
                errors.append(f"{label}.focus_target.area_ratio 必须大于 0 且不超过画布 20%")
            if focus_target.get("target_verified") is not True:
                errors.append(f"{label}.focus_target 尚未在原生关键帧验证坐标")
        else:
            if focus_target.get("marker") != "none":
                errors.append(f"{label} 不需要重点标注时 marker 必须为 none")

        fallback_visual = scene.get("fallback_visual")
        if not isinstance(fallback_visual, dict) or fallback_visual.get("mode") not in VALID_FALLBACK_MODES:
            errors.append(f"{label}.fallback_visual.mode 无效")
        elif fallback_visual.get("mode") != "none":
            if not nonempty_text(fallback_visual.get("path")) or not nonempty_text(fallback_visual.get("reason")):
                errors.append(f"{label} 使用关键帧或生成补图时必须写明 path 与 reason")
            fallback_path = resolve_path(path, fallback_visual.get("path"))
            if fallback_path is None or not fallback_path.is_file():
                errors.append(f"{label} 的 fallback_visual 文件不存在或不可读取")

        privacy_review = scene.get("privacy_review")
        scoped_target_ids = {
            target_id
            for target_id, target in privacy_by_id.items()
            if current_assets & set(text_list(target.get("asset_ids")) or [])
        }
        if not isinstance(privacy_review, dict):
            errors.append(f"{label}.privacy_review 必须为对象")
        else:
            checked_ids = text_list(privacy_review.get("checked_target_ids"))
            visible_ids = text_list(privacy_review.get("visible_target_ids"))
            handled_ids = text_list(privacy_review.get("handled_target_ids"))
            if checked_ids is None or set(checked_ids) != scoped_target_ids:
                errors.append(f"{label}.privacy_review.checked_target_ids 未完整覆盖本镜头相关隐私目标")
                checked_ids = []
            if visible_ids is None or not set(visible_ids).issubset(set(checked_ids)):
                errors.append(f"{label}.privacy_review.visible_target_ids 必须属于已检查目标")
                visible_ids = []
            if handled_ids is None or set(handled_ids) != set(visible_ids):
                errors.append(f"{label}.privacy_review.handled_target_ids 必须完整且只处理实际可见目标")
            if privacy_review.get("recording_indicators_checked") is not True:
                errors.append(f"{label} 尚未检查录屏红点、胶囊或计时标记")
            if privacy_review.get("non_target_content_clear") is not True:
                errors.append(f"{label} 尚未确认非隐私教学内容保持清晰")

        overlap = current_assets & previous_assets
        if overlap:
            if scene.get("reuse_advances_state") is not True:
                errors.append(f"{label} 与上一镜头重复主素材但未声明可见状态推进：{', '.join(sorted(overlap))}")
            if not nonempty_text(scene.get("reuse_reason")):
                errors.append(f"{label} 与上一镜头重复主素材但缺少 reuse_reason")
            repeated_run_seconds += float(duration)
            if repeated_run_seconds > 8:
                errors.append(f"{label} 的相邻重复主素材累计超过 8 秒")
        else:
            repeated_run_seconds = 0.0
        previous_assets = current_assets

        if scene.get("subtitle_safe") is not True:
            errors.append(f"{label} 尚未通过字幕安全区检查")
        if watermark_enabled and scene.get("watermark_safe") is not True:
            errors.append(f"{label} 尚未通过水印安全区检查")
        if scene.get("full_frame_motion") is True and not nonempty_text(scene.get("full_frame_motion_reason")):
            errors.append(f"{label} 使用整页运动但缺少语义理由")
        if scene.get("visual_coverage_to_end") is not True:
            errors.append(f"{label} 尚未保证有效视觉覆盖到旁白结束")

        blank_hold = scene.get("blank_hold_seconds")
        if not isinstance(blank_hold, (int, float)) or blank_hold < 0:
            errors.append(f"{label}.blank_hold_seconds 必须为大于等于 0 的数字")
        elif blank_hold > 0.5:
            errors.append(f"{label} 存在 {blank_hold} 秒无职责空白")

        interaction = scene.get("subject_interaction")
        if not isinstance(interaction, dict):
            errors.append(f"{label}.subject_interaction 必须为对象")
        elif interaction.get("required") is True:
            if data.get("human_presence") == "none":
                errors.append(f"{label} 没有人物或角色，不能要求主体交互")
            if any(not nonempty_text(interaction.get(field)) for field in ("target", "action", "action_signature")):
                errors.append(f"{label} 的主体交互缺少 target、action 或 action_signature")
            action_signature = str(interaction.get("action_signature", "")).strip()
            if action_signature:
                previous = seen_action_signatures.get(action_signature)
                semantic_role = str(scene.get("semantic_role", "")).strip()
                if previous is not None and previous[1] != semantic_role:
                    if scene.get("reuse_advances_state") is not True or not nonempty_text(scene.get("reuse_reason")):
                        errors.append(f"{label} 与 {previous[0]} 在不同语义中重复同一人物动作")
                seen_action_signatures[action_signature] = (label, semantic_role)
            for field in ("anatomy_safe", "edge_safe"):
                if interaction.get(field) is not True:
                    errors.append(f"{label} 的主体交互 {field} 未通过")

        if schema_version in FOUNDATION_SCHEMAS:
            scene_character_ids = text_list(scene.get("character_ids"))
            if scene_character_ids is None:
                errors.append(f"{label}.character_ids 必须为字符串数组")
                scene_character_ids = []
            unknown_characters = set(scene_character_ids) - character_ids
            if unknown_characters:
                errors.append(f"{label} 引用了未锁定人物：{', '.join(sorted(unknown_characters))}")
            if isinstance(interaction, dict) and interaction.get("required") is True and data.get("human_presence") in {"supplied-character", "generated-scene-illustration"} and not scene_character_ids:
                errors.append(f"{label} 有人物交互但未绑定 character_id")
            continuity_review = scene.get("character_continuity_review")
            if scene_character_ids:
                if not isinstance(continuity_review, dict):
                    errors.append(f"{label} 缺少 character_continuity_review")
                else:
                    for field in ("identity_verified", "style_consistent"):
                        if continuity_review.get(field) is not True:
                            errors.append(f"{label}.character_continuity_review.{field} 尚未通过")
                    if continuity_review.get("unexplained_changes") is not False:
                        errors.append(f"{label} 的人物存在未解释的换脸、换衣或画风变化")
            if scene.get("platform_safe") is not True:
                errors.append(f"{label} 尚未通过平台 UI 遮挡安全检查")

        symbols = scene.get("semantic_symbols")
        if not isinstance(symbols, list):
            errors.append(f"{label} 的 semantic_symbols 必须为数组")
        else:
            for symbol_index, symbol in enumerate(symbols):
                if not isinstance(symbol, dict) or not nonempty_text(symbol.get("symbol")) or not nonempty_text(symbol.get("meaning")):
                    errors.append(f"{label}.semantic_symbols[{symbol_index}] 必须写明 symbol 与 meaning")
                    continue
                symbol_name = str(symbol["symbol"]).strip().casefold()
                meaning = str(symbol["meaning"]).strip().casefold()
                if symbol_name in ARROW_SYMBOLS and any(word in meaning for word in ABSENCE_WORDS):
                    errors.append(f"{label} 用箭头表达没有或排除，应改用否定符号")

    if schema_version in FINE_SHOT_SCHEMAS:
        errors.extend(validate_fine_shots(path, data.get("shots"), expected_segments, contract_duration, character_ids))

    if narration_contract_path is not None:
        missing_segment_ids = set(expected_segments) - used_segment_ids
        extra_segment_ids = used_segment_ids - set(expected_segments)
        if missing_segment_ids:
            errors.append(f"存在没有对应镜头的旁白段：{', '.join(sorted(missing_segment_ids))}")
        if extra_segment_ids:
            errors.append(f"存在没有对应旁白的镜头绑定：{', '.join(sorted(extra_segment_ids))}")
        if contract_duration is not None and abs(total_scene_duration - contract_duration) > 0.05:
            errors.append(
                f"镜头总时长 {total_scene_duration:.3f} 秒与锁定旁白 {contract_duration:.3f} 秒不一致，禁止静默增减时长"
            )

    revision_scope = data.get("revision_scope")
    if not isinstance(revision_scope, dict):
        errors.append("缺少 revision_scope，无法判断是首版还是既有成片修改")
    else:
        mode = revision_scope.get("mode")
        if mode not in VALID_REVISION_MODES:
            errors.append("revision_scope.mode 必须为 initial 或 revision")
        elif mode == "initial":
            stale_fields = (
                "baseline_shot_readiness",
                "baseline_sha256",
                "affected_scene_ids",
                "preserved_scene_ids",
                "feedback_items",
                "preview_artifacts",
            )
            if any(revision_scope.get(field) not in ("", [], None) for field in stale_fields):
                errors.append("initial 模式不能残留既有成片修改数据")
        else:
            baseline_path = resolve_path(path, revision_scope.get("baseline_shot_readiness"))
            expected_sha = str(revision_scope.get("baseline_sha256", "")).strip()
            baseline_data: dict[str, Any] | None = None
            if baseline_path is None or not baseline_path.is_file() or baseline_path == path.resolve():
                errors.append("revision_scope 缺少独立、可读取的基线镜头表")
            elif not SHA256_PATTERN.fullmatch(expected_sha) or file_sha256(baseline_path).casefold() != expected_sha.casefold():
                errors.append("revision_scope 的基线镜头表 SHA-256 不一致")
            else:
                try:
                    loaded = json.loads(baseline_path.read_text(encoding="utf-8"))
                except (OSError, json.JSONDecodeError) as exc:
                    errors.append(f"revision_scope 的基线镜头表无法解析：{exc}")
                else:
                    if isinstance(loaded, dict):
                        baseline_data = loaded

            affected = text_list(revision_scope.get("affected_scene_ids"))
            preserved = text_list(revision_scope.get("preserved_scene_ids"))
            affected_set = set(affected or [])
            preserved_set = set(preserved or [])
            current_ids = set(scene_records)
            if affected is None or not affected_set:
                errors.append("revision_scope.affected_scene_ids 必须包含本轮修改镜头")
            if preserved is None:
                errors.append("revision_scope.preserved_scene_ids 必须为数组")
            if affected_set & preserved_set:
                errors.append("受影响镜头与保留镜头不能重叠")
            if affected_set | preserved_set != current_ids:
                errors.append("受影响镜头与保留镜头必须完整覆盖当前全片")

            feedback_items = revision_scope.get("feedback_items")
            if not isinstance(feedback_items, list) or not feedback_items:
                errors.append("revision_scope.feedback_items 必须包含用户逐条反馈")
            else:
                feedback_ids: set[str] = set()
                for index, item in enumerate(feedback_items):
                    label = f"revision_scope.feedback_items[{index}]"
                    if not isinstance(item, dict):
                        errors.append(f"{label} 必须为对象")
                        continue
                    feedback_id = str(item.get("feedback_id", "")).strip()
                    if not feedback_id or feedback_id in feedback_ids:
                        errors.append(f"{label} 缺少唯一 feedback_id")
                    feedback_ids.add(feedback_id)
                    for field in ("request", "acceptance_criteria"):
                        if not nonempty_text(item.get(field)):
                            errors.append(f"{label} 缺少 {field}")
                    item_scene_ids = text_list(item.get("scene_ids"))
                    if item_scene_ids is None or not item_scene_ids or not set(item_scene_ids).issubset(affected_set):
                        errors.append(f"{label}.scene_ids 必须属于受影响镜头")
                    if item.get("resolved") is not True:
                        errors.append(f"{label} 尚未解决")

            preview_artifacts = revision_scope.get("preview_artifacts")
            preview_scene_ids: set[str] = set()
            if not isinstance(preview_artifacts, list) or not preview_artifacts:
                errors.append("revision_scope.preview_artifacts 必须包含受影响镜头预览")
            else:
                for index, artifact in enumerate(preview_artifacts):
                    label = f"revision_scope.preview_artifacts[{index}]"
                    if not isinstance(artifact, dict):
                        errors.append(f"{label} 必须为对象")
                        continue
                    if artifact.get("kind") not in VALID_PREVIEW_KINDS:
                        errors.append(f"{label}.kind 无效")
                    artifact_path = resolve_path(path, artifact.get("path"))
                    if artifact_path is None or not artifact_path.is_file() or artifact_path.stat().st_size == 0:
                        errors.append(f"{label} 缺少可读取的真实预览文件")
                    artifact_scene_ids = text_list(artifact.get("scene_ids"))
                    if artifact_scene_ids is None or not artifact_scene_ids or not set(artifact_scene_ids).issubset(affected_set):
                        errors.append(f"{label}.scene_ids 必须属于受影响镜头")
                    else:
                        preview_scene_ids.update(artifact_scene_ids)
                    if artifact.get("verified") is not True:
                        errors.append(f"{label} 尚未完成原尺寸肉眼检查")
            if preview_scene_ids != affected_set:
                errors.append("修改预览没有完整覆盖所有受影响镜头")

            preview_approval = revision_scope.get("preview_approval")
            if not isinstance(preview_approval, dict) or preview_approval.get("approved") is not True:
                errors.append("受影响镜头预览尚未获得用户确认")
            else:
                for field in ("approval_message", "approved_at"):
                    if not nonempty_text(preview_approval.get(field)):
                        errors.append(f"revision_scope.preview_approval 缺少 {field}")

            if baseline_data is not None:
                raw_baseline_scenes = baseline_data.get("scenes")
                baseline_scenes = {
                    str(item.get("scene_id", "")).strip(): item
                    for item in raw_baseline_scenes
                    if isinstance(item, dict) and nonempty_text(item.get("scene_id"))
                } if isinstance(raw_baseline_scenes, list) else {}
                for scene_id in sorted(preserved_set):
                    baseline_scene = baseline_scenes.get(scene_id)
                    current_scene = scene_records.get(scene_id)
                    if baseline_scene is None or current_scene is None:
                        errors.append(f"保留镜头 {scene_id} 在基线或当前镜头表中缺失")
                    elif canonical_json(baseline_scene) != canonical_json(current_scene):
                        errors.append(f"保留镜头 {scene_id} 与基线不一致，必须恢复或列入受影响范围")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="校验动态视频镜头就绪表")
    parser.add_argument("shot_readiness", type=Path, help="shot-readiness.json 路径")
    parser.add_argument("--narration-contract", type=Path, help="用于核对逐段映射、全文哈希和总时长的旁白契约")
    args = parser.parse_args()
    narration_contract = args.narration_contract.expanduser().resolve() if args.narration_contract else None
    errors = validate(args.shot_readiness.expanduser().resolve(), narration_contract)
    if errors:
        for error in errors:
            print(f"FAIL {error}")
        return 1
    print("PASS 镜头就绪表通过：口播映射、总时长、视觉证据、素材复用、字幕和安全区均有效")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

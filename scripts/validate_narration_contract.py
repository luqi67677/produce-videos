#!/usr/bin/env python3
"""校验旁白来源、音频产物、显示文本、单层字幕和连续时间戳。"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from validate_master_script import validate_contract_binding
from validate_voice_selection import validate as validate_voice_selection


VALID_VOICE_SOURCES = {"open-source-model", "other-tts", "user-reference", "external"}
SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$", re.IGNORECASE)


def nonempty_text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def positive_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and value > 0


def load_json(path: Path, label: str) -> tuple[dict[str, Any] | None, list[str]]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None, [f"{label}不存在：{path}"]
    except (OSError, json.JSONDecodeError) as exc:
        return None, [f"{label}无法解析：{exc}"]
    if not isinstance(value, dict):
        return None, [f"{label}必须为 JSON 对象"]
    return value, []


def resolve_path(contract_path: Path, value: Any) -> Path | None:
    if not nonempty_text(value):
        return None
    path = Path(str(value)).expanduser()
    return path.resolve() if path.is_absolute() else (contract_path.parent / path).resolve()


def resolve_resource_path(contract_path: Path, value: Any) -> Path | None:
    path = resolve_path(contract_path, value)
    if path is None or path.exists() or Path(str(value)).expanduser().is_absolute():
        return path
    bundled = Path(__file__).resolve().parents[1] / str(value)
    return bundled.resolve()


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def probe_audio(path: Path) -> tuple[dict[str, Any] | None, str | None]:
    ffprobe = shutil.which("ffprobe")
    if ffprobe is None:
        return None, "需要 ffprobe 才能验证实际音频时长、采样率和声道"
    result = subprocess.run(
        [
            ffprobe,
            "-v",
            "error",
            "-show_entries",
            "format=duration:stream=codec_type,sample_rate,channels",
            "-of",
            "json",
            str(path),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return None, "ffprobe 无法读取旁白音频，请确认文件格式可用"
    try:
        data = json.loads(result.stdout)
        stream = next(item for item in data.get("streams", []) if item.get("codec_type") == "audio")
        return {
            "duration_seconds": float(data.get("format", {}).get("duration", 0)),
            "sample_rate": int(stream.get("sample_rate", 0)),
            "channels": int(stream.get("channels", 0)),
        }, None
    except (StopIteration, TypeError, ValueError, json.JSONDecodeError):
        return None, "旁白音频缺少可读取的音轨信息"


def narration_text_sha256(segments: list[dict[str, Any]]) -> str:
    text = "\n".join(str(segment.get("display_text", "")).strip() for segment in segments)
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def validate(contract_path: Path, require_timestamps: bool, require_audio: bool, require_script_lock: bool = False) -> list[str]:
    contract, errors = load_json(contract_path, "旁白契约")
    if contract is None:
        return errors

    voice_source = contract.get("voice_source")
    if voice_source not in VALID_VOICE_SOURCES:
        errors.append("voice_source 必须为 open-source-model、other-tts、user-reference 或 external；草稿不能直接作为正式契约")
    if voice_source in VALID_VOICE_SOURCES and not nonempty_text(contract.get("voice_profile")):
        errors.append("正式旁白契约缺少 voice_profile")
    if voice_source == "user-reference":
        for field in ("authorization_record", "reference_text", "reference_audio", "reference_audio_sha256"):
            if not nonempty_text(contract.get(field)):
                errors.append(f"用户参考音频缺少 {field}")
        reference_path = resolve_path(contract_path, contract.get("reference_audio"))
        if reference_path is None or not reference_path.is_file():
            errors.append("用户参考音频文件不存在或不可读取")
        elif nonempty_text(contract.get("reference_audio_sha256")):
            if file_sha256(reference_path).casefold() != str(contract["reference_audio_sha256"]).casefold():
                errors.append("用户参考音频 SHA-256 与实际文件不一致")
    if voice_source == "other-tts":
        for field in ("provider", "model_id", "model_url", "runtime", "voice_instruction"):
            if not nonempty_text(contract.get(field)):
                errors.append(f"other-tts 旁白缺少 {field}")
        selection_path = resolve_path(contract_path, contract.get("voice_selection_path"))
        expected_selection_sha = str(contract.get("voice_selection_sha256", "")).strip()
        if selection_path is None or not selection_path.is_file() or contract_path.parent not in selection_path.parents:
            errors.append("other-tts 旁白缺少项目内可读取的 voice_selection_path")
        else:
            if not SHA256_PATTERN.fullmatch(expected_selection_sha) or file_sha256(selection_path).casefold() != expected_selection_sha.casefold():
                errors.append("voice_selection_sha256 与实际声音选择文件不一致")
            for error in validate_voice_selection(selection_path, True):
                errors.append(f"声音选择：{error}")
            selection, selection_errors = load_json(selection_path, "声音选择文件")
            errors.extend(selection_errors)
            if selection is not None:
                if selection.get("engine_type") != "api":
                    errors.append("other-tts 当前必须绑定已通过预检的 API 声音选择")
                for field in ("provider", "model_id"):
                    if str(selection.get(field, "")).strip() != str(contract.get(field, "")).strip():
                        errors.append(f"旁白 {field} 与声音选择不一致")
                if str(selection.get("selected_instruction", "")).strip() != str(contract.get("voice_instruction", "")).strip():
                    errors.append("旁白 voice_instruction 与用户确认的声音选择不一致")
    if voice_source == "open-source-model":
        for field in ("voice_instruction", "model_id", "model_url", "model_path", "runtime"):
            if not nonempty_text(contract.get(field)):
                errors.append(f"开源模型旁白缺少 {field}")
        if contract.get("runtime") != "mlx-audio":
            errors.append("当前 Qwen 执行器的 runtime 必须为 mlx-audio")
        selection_path = resolve_path(contract_path, contract.get("voice_selection_path"))
        expected_selection_sha = str(contract.get("voice_selection_sha256", "")).strip()
        if selection_path is None or not selection_path.is_file() or contract_path.parent not in selection_path.parents:
            errors.append("开源模型旁白缺少项目内可读取的 voice_selection_path")
        else:
            if not SHA256_PATTERN.fullmatch(expected_selection_sha) or file_sha256(selection_path).casefold() != expected_selection_sha.casefold():
                errors.append("voice_selection_sha256 与实际声音选择文件不一致")
            for error in validate_voice_selection(selection_path, True):
                errors.append(f"声音选择：{error}")
            selection, selection_errors = load_json(selection_path, "声音选择文件")
            errors.extend(selection_errors)
            if selection is not None:
                if str(selection.get("selected_instruction", "")).strip() != str(contract.get("voice_instruction", "")).strip():
                    errors.append("旁白 voice_instruction 与用户确认的声音选择不一致")
                if str(selection.get("model_id", "")).strip() != str(contract.get("model_id", "")).strip():
                    errors.append("旁白 model_id 与声音选择不一致")
                selection_model_path = resolve_path(selection_path, selection.get("model_path"))
                contract_model_path = resolve_path(contract_path, contract.get("model_path"))
                if selection_model_path != contract_model_path:
                    errors.append("旁白 model_path 与声音选择不一致")
    if voice_source in {"open-source-model", "other-tts"}:
        parsed = urlparse(str(contract.get("model_url", "")))
        if parsed.scheme != "https" or not parsed.netloc:
            errors.append("模型地址必须是完整的 HTTPS 地址")
    if contract.get("subtitle_layer_count") != 1:
        errors.append("subtitle_layer_count 必须为 1，禁止双层字幕")

    if require_audio:
        audio_path = resolve_path(contract_path, contract.get("audio_path"))
        if audio_path is None or not audio_path.is_file():
            errors.append("正式旁白缺少可读取的 audio_path")
        else:
            actual_sha = file_sha256(audio_path)
            expected_sha = str(contract.get("audio_sha256", "")).strip()
            if not SHA256_PATTERN.fullmatch(expected_sha):
                errors.append("audio_sha256 必须是 64 位十六进制 SHA-256")
            elif actual_sha.casefold() != expected_sha.casefold():
                errors.append("audio_sha256 与实际旁白文件不一致")
            for field in ("duration_seconds", "sample_rate", "channels"):
                if not positive_number(contract.get(field)):
                    errors.append(f"正式旁白缺少有效的 {field}")
            if not nonempty_text(contract.get("audio_format")):
                errors.append("正式旁白缺少 audio_format")
            actual, probe_error = probe_audio(audio_path)
            if probe_error:
                errors.append(probe_error)
            elif actual:
                if abs(float(contract["duration_seconds"]) - actual["duration_seconds"]) > 0.05:
                    errors.append("契约中的 duration_seconds 与实际音频不一致")
                if int(contract["sample_rate"]) != actual["sample_rate"]:
                    errors.append("契约中的 sample_rate 与实际音频不一致")
                if int(contract["channels"]) != actual["channels"]:
                    errors.append("契约中的 channels 与实际音频不一致")

    pronunciation_map = resolve_resource_path(contract_path, contract.get("pronunciation_map"))
    rules: list[dict[str, Any]] = []
    if pronunciation_map is None:
        errors.append("缺少 pronunciation_map")
    else:
        pronunciation, map_errors = load_json(pronunciation_map, "TTS 发音映射")
        errors.extend(map_errors)
        if pronunciation is not None:
            raw_rules = pronunciation.get("rules")
            if not isinstance(raw_rules, list):
                errors.append("TTS 发音映射的 rules 必须为数组")
            else:
                for index, rule in enumerate(raw_rules):
                    if not isinstance(rule, dict) or not nonempty_text(rule.get("pattern")) or not nonempty_text(rule.get("replacement")):
                        errors.append(f"TTS 发音映射 rules[{index}] 缺少 pattern 或 replacement")
                        continue
                    try:
                        re.compile(str(rule["pattern"]))
                    except re.error as exc:
                        errors.append(f"TTS 发音映射 rules[{index}] 的正则无效：{exc}")
                        continue
                    rules.append(rule)

    segments = contract.get("segments")
    if not isinstance(segments, list) or not segments:
        errors.append("segments 必须包含至少一个旁白段")
        return errors

    if require_script_lock:
        errors.extend(f"口播绑定：{error}" for error in validate_contract_binding(contract_path, contract, True))

        script_lock = contract.get("script_lock")
        if not isinstance(script_lock, dict):
            errors.append("缺少 script_lock，完整口播尚未锁定")
        else:
            if script_lock.get("approved") is not True:
                errors.append("script_lock.approved 必须为 true")
            expected_text_sha = str(script_lock.get("approved_text_sha256", "")).strip()
            actual_text_sha = narration_text_sha256(segments)
            if not SHA256_PATTERN.fullmatch(expected_text_sha):
                errors.append("script_lock.approved_text_sha256 必须是 64 位 SHA-256")
            elif expected_text_sha.casefold() != actual_text_sha.casefold():
                errors.append("口播正文已在批准后改动，必须重新通读、确认并锁定")
            locked_duration = script_lock.get("approved_duration_seconds")
            if not positive_number(locked_duration) or not positive_number(contract.get("duration_seconds")):
                errors.append("script_lock 缺少有效的批准时长")
            elif abs(float(locked_duration) - float(contract["duration_seconds"])) > 0.05:
                errors.append("口播总时长已偏离用户批准版本")
            if script_lock.get("segment_count") != len(segments):
                errors.append("script_lock.segment_count 与实际旁白段数不一致")
            if script_lock.get("revision_requires_reapproval") is not True:
                errors.append("script_lock 必须声明改稿后重新审批")

        logic_review = contract.get("logic_review")
        if not isinstance(logic_review, dict):
            errors.append("缺少 logic_review，尚未完成全篇逻辑复核")
        else:
            if logic_review.get("approved") is not True:
                errors.append("logic_review.approved 必须为 true")
            for field in ("core_claim", "global_flow"):
                if not nonempty_text(logic_review.get(field)):
                    errors.append(f"logic_review 缺少 {field}")
            redundant_ids = logic_review.get("redundant_segment_ids")
            if not isinstance(redundant_ids, list):
                errors.append("logic_review.redundant_segment_ids 必须为数组")
            elif redundant_ids:
                errors.append("口播仍包含被标记为重复或无贡献的段落")
            valid_segment_ids = {str(segment.get("scene_id", "")).strip() for segment in segments}
            tool_sections = logic_review.get("tool_sections", [])
            if not isinstance(tool_sections, list):
                errors.append("logic_review.tool_sections 必须为数组")
            else:
                for index, section in enumerate(tool_sections):
                    label = f"logic_review.tool_sections[{index}]"
                    if not isinstance(section, dict):
                        errors.append(f"{label} 必须为对象")
                        continue
                    if not nonempty_text(section.get("tool_name")):
                        errors.append(f"{label} 缺少 tool_name")
                    section_ids = section.get("segment_ids")
                    if not isinstance(section_ids, list) or not section_ids:
                        errors.append(f"{label}.segment_ids 必须包含至少一个旁白段")
                    elif any(str(item).strip() not in valid_segment_ids for item in section_ids):
                        errors.append(f"{label}.segment_ids 包含不存在的旁白段")
                    for field in ("identity_and_purpose_first", "usage_before_result", "duplicate_summary_removed"):
                        if section.get(field) is not True:
                            errors.append(f"{label}.{field} 尚未通过")

    seen_scene_ids: set[str] = set()
    previous_end: float | None = None
    for index, segment in enumerate(segments):
        label = f"segments[{index}]"
        if not isinstance(segment, dict):
            errors.append(f"{label} 必须为对象")
            continue
        scene_id = str(segment.get("scene_id", "")).strip()
        if not scene_id:
            errors.append(f"{label} 缺少 scene_id")
        elif scene_id in seen_scene_ids:
            errors.append(f"scene_id 重复：{scene_id}")
        else:
            seen_scene_ids.add(scene_id)
        label = scene_id or label
        display_text = segment.get("display_text")
        tts_text = segment.get("tts_text")
        if not nonempty_text(display_text):
            errors.append(f"{label} 缺少 display_text")
        if not nonempty_text(tts_text):
            errors.append(f"{label} 缺少 tts_text")
            continue
        for rule in rules:
            if re.search(str(rule["pattern"]), str(tts_text), flags=re.IGNORECASE):
                errors.append(f"{label} 的 tts_text 命中未归一化读法 {rule.get('id', '')}，应改为：{rule['replacement']}")

        if require_timestamps:
            start = segment.get("start_seconds")
            end = segment.get("end_seconds")
            if not isinstance(start, (int, float)) or not isinstance(end, (int, float)):
                errors.append(f"{label} 缺少最终 start_seconds/end_seconds")
                continue
            if start < 0 or end <= start:
                errors.append(f"{label} 的时间范围无效：{start}—{end}")
                continue
            if previous_end is None and start > 0.05:
                errors.append(f"{label} 没有从 0 秒附近开始")
            if previous_end is not None:
                if start < previous_end - 0.01:
                    errors.append(f"{label} 与上一段时间重叠")
                if start - previous_end > 0.05:
                    errors.append(f"{label} 与上一段之间存在未说明的时间空洞")
            previous_end = float(end)

    if require_timestamps and previous_end is not None and positive_number(contract.get("duration_seconds")):
        if abs(previous_end - float(contract["duration_seconds"])) > 0.05:
            errors.append("最后一段时间戳没有覆盖到实际旁白结束位置")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="校验动态视频旁白契约")
    parser.add_argument("narration_contract", type=Path, help="narration-contract.json 路径")
    parser.add_argument("--require-timestamps", action="store_true", help="要求时间戳从 0 秒附近连续覆盖旁白")
    parser.add_argument("--require-audio", action="store_true", help="要求实际音频文件、哈希和媒体参数全部可验证")
    parser.add_argument("--require-script-lock", action="store_true", help="要求完整口播哈希、时长和全篇逻辑已经锁定")
    args = parser.parse_args()
    errors = validate(
        args.narration_contract.expanduser().resolve(),
        args.require_timestamps,
        args.require_audio,
        args.require_script_lock,
    )
    if errors:
        for error in errors:
            print(f"FAIL {error}")
        return 1
    print("PASS 旁白契约通过：来源、产物、授权、TTS 读法、单层字幕和时间戳均有效")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

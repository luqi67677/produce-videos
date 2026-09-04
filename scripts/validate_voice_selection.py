#!/usr/bin/env python3
"""验证模型已就绪且声音由用户明确选择，防止未试听或未确认就生成整条旁白。"""

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

from validate_voice_brief import validate as validate_voice_brief


SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$", re.IGNORECASE)
VALID_SELECTION_MODES = {"direct-description", "audition"}
VALID_ENGINE_TYPES = {"local-model", "api"}
VALID_LOCAL_MODEL_ORIGINS = {"discovered", "downloaded-after-approval", "user-specified"}
VALID_API_CREDENTIAL_STORAGE = {"environment", "secure-store"}
FORBIDDEN_SECRET_KEYS = {
    "api_key", "apikey", "access_token", "refresh_token", "token", "secret",
    "client_secret", "authorization_header", "bearer", "password",
}


def nonempty_text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def persisted_secret_locations(value: Any, prefix: str = "") -> list[str]:
    locations: list[str] = []
    if isinstance(value, dict):
        for key, item in value.items():
            location = f"{prefix}.{key}" if prefix else str(key)
            if str(key).casefold() in FORBIDDEN_SECRET_KEYS and item not in (None, "", False):
                locations.append(location)
            locations.extend(persisted_secret_locations(item, location))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            locations.extend(persisted_secret_locations(item, f"{prefix}[{index}]"))
    return locations


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


def load_object(path: Path, label: str) -> tuple[dict[str, Any] | None, list[str]]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None, [f"{label}不存在：{path}"]
    except (OSError, json.JSONDecodeError) as exc:
        return None, [f"{label}无法解析：{exc}"]
    if not isinstance(value, dict):
        return None, [f"{label}必须为 JSON 对象"]
    return value, []


def verify_bound_report(selection_path: Path, data: dict[str, Any], field: str, label: str) -> tuple[dict[str, Any] | None, list[str]]:
    errors: list[str] = []
    report_path = resolve_path(selection_path, data.get(field))
    expected_sha = str(data.get(f"{field}_sha256", "")).strip()
    if report_path is None or not report_path.is_file():
        return None, [f"{label}缺少可读取文件"]
    if not SHA256_PATTERN.fullmatch(expected_sha) or file_sha256(report_path).casefold() != expected_sha.casefold():
        errors.append(f"{label} SHA-256 与实际文件不一致")
    report, load_errors = load_object(report_path, label)
    errors.extend(load_errors)
    return report, errors


def probe_audio(path: Path) -> str | None:
    ffprobe = shutil.which("ffprobe")
    if ffprobe is None:
        return "需要 ffprobe 才能验证试听音频"
    result = subprocess.run(
        [ffprobe, "-v", "error", "-show_entries", "format=duration:stream=codec_type", "-of", "json", str(path)],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return "试听音频无法读取"
    try:
        value = json.loads(result.stdout)
        duration = float(value.get("format", {}).get("duration", 0))
        has_audio = any(item.get("codec_type") == "audio" for item in value.get("streams", []))
    except (TypeError, ValueError, json.JSONDecodeError):
        return "试听音频媒体信息无效"
    return None if has_audio and duration > 0 else "试听音频缺少有效音轨或时长"


def validate(path: Path, require_approved: bool = True) -> list[str]:
    data, errors = load_object(path, "声音选择文件")
    if data is None:
        return errors
    mode = data.get("selection_mode")
    if mode not in VALID_SELECTION_MODES:
        errors.append("selection_mode 必须为 direct-description 或 audition")
    engine_type = data.get("engine_type")
    if engine_type not in VALID_ENGINE_TYPES:
        errors.append("engine_type 必须为 local-model 或 api")
    origin = data.get("model_origin")
    for field in ("model_id", "model_url", "selected_instruction"):
        if not nonempty_text(data.get(field)):
            errors.append(f"声音选择缺少 {field}")
    parsed_url = urlparse(str(data.get("model_url", "")))
    if parsed_url.scheme != "https" or not parsed_url.netloc:
        errors.append("model_url 必须是完整的 HTTPS 地址")

    if engine_type == "local-model":
        if origin not in VALID_LOCAL_MODEL_ORIGINS:
            errors.append("本地模型的 model_origin 必须为 discovered、downloaded-after-approval 或 user-specified")
        if not nonempty_text(data.get("model_path")):
            errors.append("本地模型声音选择缺少 model_path")
        if origin == "downloaded-after-approval" and not nonempty_text(data.get("download_authorization_record")):
            errors.append("下载模型时必须记录用户的明确授权")

        discovery, discovery_errors = verify_bound_report(path, data, "model_discovery_path", "模型发现报告")
        errors.extend(discovery_errors)
        preflight, preflight_errors = verify_bound_report(path, data, "model_preflight_path", "模型预检报告")
        errors.extend(preflight_errors)
        selected_model_path = resolve_path(path, data.get("model_path"))
        if preflight is not None:
            if preflight.get("status") != "pass":
                errors.append("模型预检尚未通过")
            preflight_model_path = resolve_path(path, preflight.get("model_path"))
            if selected_model_path is None or preflight_model_path != selected_model_path:
                errors.append("声音选择的模型路径与通过预检的模型不一致")
            for field in ("model_id", "model_url"):
                preflight_value = str(preflight.get(field, "")).strip()
                selected_value = str(data.get(field, "")).strip()
                if preflight_value and preflight_value != selected_value:
                    errors.append(f"声音选择的 {field} 与通过预检的记录不一致")
        if discovery is not None and origin == "discovered":
            discovered_candidates = [
                item for item in discovery.get("candidates", [])
                if isinstance(item, dict)
                and item.get("compatible_with_bundled_runner") is True
                and resolve_path(path, item.get("path")) == selected_model_path
            ]
            if not discovered_candidates:
                errors.append("标记为 discovered 的模型不在本次发现报告的兼容候选中")
    elif engine_type == "api":
        if origin != "api":
            errors.append("API 声音选择的 model_origin 必须为 api")
        for field in ("provider", "credential_storage"):
            if not nonempty_text(data.get(field)):
                errors.append(f"API 声音选择缺少 {field}")
        if data.get("credential_storage") not in VALID_API_CREDENTIAL_STORAGE:
            errors.append("API 凭证只能记录为 environment 或 secure-store，不得写入项目文件")
        if secret_locations := persisted_secret_locations(data):
            errors.append("声音选择文件疑似包含密钥字段：" + "、".join(secret_locations))
        api_report, api_errors = verify_bound_report(path, data, "api_preflight_path", "TTS API 预检报告")
        errors.extend(api_errors)
        if api_report is not None:
            if secret_locations := persisted_secret_locations(api_report):
                errors.append("TTS API 预检报告疑似包含密钥字段：" + "、".join(secret_locations))
            if api_report.get("status") != "pass" or api_report.get("engine_type") != "api":
                errors.append("TTS API 预检尚未通过")
            for field in ("provider", "model_id", "model_url", "credential_storage"):
                if str(api_report.get(field, "")).strip() != str(data.get(field, "")).strip():
                    errors.append(f"声音选择的 {field} 与 API 预检记录不一致")
            if api_report.get("secret_values_persisted") is not False:
                errors.append("API 预检报告必须确认没有持久化密钥值")
            if api_report.get("test_request_passed") is not True:
                errors.append("TTS API 最小测试请求尚未通过")
            if api_report.get("voice_listing_or_generation_passed") is not True:
                errors.append("TTS API 尚未证明可以列出声音或生成试听")

    candidates = data.get("candidates")
    if not isinstance(candidates, list):
        errors.append("candidates 必须为数组")
        candidates = []
    if mode == "audition":
        voice_brief_path = resolve_path(path, data.get("voice_brief_path"))
        voice_brief_sha = str(data.get("voice_brief_path_sha256", "")).strip()
        if voice_brief_path is None or not voice_brief_path.is_file():
            errors.append("试听选择缺少可读取的声音需求单")
        else:
            if not SHA256_PATTERN.fullmatch(voice_brief_sha) or file_sha256(voice_brief_path).casefold() != voice_brief_sha.casefold():
                errors.append("声音需求单 SHA-256 与实际文件不一致")
            errors.extend(validate_voice_brief(voice_brief_path, True))
        if not nonempty_text(data.get("audition_text")):
            errors.append("试听选择缺少 audition_text")
        if not 2 <= len(candidates) <= 3:
            errors.append("试听选择必须提供 2—3 个同文案候选")
        candidate_ids: set[str] = set()
        candidate_instructions: set[str] = set()
        candidate_audio_hashes: set[str] = set()
        selected_id = str(data.get("selected_candidate_id", "")).strip()
        selected_instruction = ""
        for index, candidate in enumerate(candidates):
            label = f"candidates[{index}]"
            if not isinstance(candidate, dict):
                errors.append(f"{label} 必须为对象")
                continue
            candidate_id = str(candidate.get("candidate_id", "")).strip()
            instruction = str(candidate.get("instruction", "")).strip()
            if not candidate_id or candidate_id in candidate_ids:
                errors.append(f"{label} 缺少唯一 candidate_id")
            candidate_ids.add(candidate_id)
            if not instruction:
                errors.append(f"{label} 缺少 instruction")
            elif instruction in candidate_instructions:
                errors.append(f"{label} 的 instruction 与其他试听重复")
            candidate_instructions.add(instruction)
            audio_path = resolve_path(path, candidate.get("audio_path"))
            expected_sha = str(candidate.get("audio_sha256", "")).strip()
            if audio_path is None or not audio_path.is_file():
                errors.append(f"{label} 缺少可读取的试听音频")
            else:
                if not SHA256_PATTERN.fullmatch(expected_sha) or file_sha256(audio_path).casefold() != expected_sha.casefold():
                    errors.append(f"{label} 的试听音频 SHA-256 不一致")
                elif expected_sha.casefold() in candidate_audio_hashes:
                    errors.append(f"{label} 的试听音频与其他候选完全相同")
                candidate_audio_hashes.add(expected_sha.casefold())
                probe_error = probe_audio(audio_path)
                if probe_error:
                    errors.append(f"{label}：{probe_error}")
            if candidate_id == selected_id:
                selected_instruction = instruction
        if selected_id not in candidate_ids:
            errors.append("selected_candidate_id 不在试听候选中")
        elif selected_instruction != str(data.get("selected_instruction", "")).strip():
            errors.append("selected_instruction 与用户选中的试听候选不一致")
    elif mode == "direct-description":
        if data.get("direct_description_authorized") is not True:
            errors.append("默认必须提供试听；只有用户明确要求直接描述时才能使用 direct-description")
        if str(data.get("selected_candidate_id", "")).strip():
            errors.append("direct-description 模式不应填写 selected_candidate_id")

    if require_approved:
        if data.get("approved") is not True:
            errors.append("用户尚未明确确认最终声音")
        for field in ("approval_message", "approved_at"):
            if not nonempty_text(data.get(field)):
                errors.append(f"声音选择缺少 {field}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="校验本机模型预检和用户声音选择")
    parser.add_argument("voice_selection", type=Path)
    parser.add_argument("--require-approved", action="store_true")
    args = parser.parse_args()
    errors = validate(args.voice_selection.expanduser().resolve(), args.require_approved)
    if errors:
        for error in errors:
            print(f"FAIL {error}")
        return 1
    print("PASS TTS 引擎已通过预检，声音已由用户明确选择")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

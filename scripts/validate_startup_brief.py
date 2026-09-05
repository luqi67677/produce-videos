#!/usr/bin/env python3
"""Validate that the initial video brief locks content and audio routes once."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


CONTENT_SOURCES = {
    "approved-script",
    "ai-write-from-materials",
    "transcribe-existing-media",
    "no-spoken-narration",
}
AUDIO_SOURCES = {
    "recorded-audio",
    "extract-from-video",
    "tts-api",
    "local-tts-model",
    "qwen-open-source",
    "no-spoken-narration",
}
TTS_SOURCES = {"tts-api", "local-tts-model", "qwen-open-source"}
PENDING = {"", "pending", "待提供", "待确认", "未选择"}


def parse_fields(path: Path) -> dict[str, str]:
    fields: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line.startswith("- ") or "：" not in line:
            continue
        key, value = line[2:].split("：", 1)
        fields[key.strip()] = value.strip()
    return fields


def is_ready(value: str | None) -> bool:
    if value is None:
        return False
    normalized = value.strip()
    if normalized in PENDING:
        return False
    return not any(normalized.startswith(f"{marker} /") for marker in PENDING if marker)


def qwen_model_url() -> str:
    config_path = Path(__file__).resolve().parents[1] / "assets" / "qwen-tts-models.json"
    return json.loads(config_path.read_text(encoding="utf-8"))["recommended"]["model_url"]


def validate(path: Path, require_approved: bool = False) -> list[str]:
    if not path.is_file():
        return [f"开工信息文件不存在：{path}"]
    fields = parse_fields(path)
    errors: list[str] = []

    for key in ("视频模式", "发布平台", "目标时长"):
        if not is_ready(fields.get(key)):
            errors.append(f"开工信息缺少{key}")

    content_source = fields.get("口播内容来源代码", "")
    audio_source = fields.get("最终声音来源代码", "")
    if content_source not in CONTENT_SOURCES:
        errors.append("口播内容来源必须选择已有确定稿、AI 撰写、音视频转写或无口播")
    if audio_source not in AUDIO_SOURCES:
        errors.append("最终声音来源必须选择独立口播、视频内提取、TTS API、本地模型、Qwen 或无旁白")

    if content_source != "no-spoken-narration" and not is_ready(fields.get("口播输入")):
        errors.append("当前口播内容路线缺少真实稿件、材料或待转写音视频")
    if content_source == "no-spoken-narration" and audio_source not in {"", "no-spoken-narration"}:
        errors.append("已选择无口播，最终声音来源也必须为无旁白")

    if audio_source in {"recorded-audio", "extract-from-video"} and not is_ready(fields.get("声音输入")):
        errors.append("当前声音路线缺少独立音频或含目标人声的视频文件")

    tts_status = fields.get("TTS 资源状态", "")
    if audio_source not in TTS_SOURCES and tts_status != "not-required":
        errors.append("非 TTS 路线的 TTS 资源状态必须为 not-required")
    if audio_source in TTS_SOURCES and not is_ready(fields.get("声音方向原话")):
        errors.append("TTS 路线必须在开工时记录用户声音方向或由你判断")

    if audio_source == "tts-api":
        if tts_status != "api-configured":
            errors.append("TTS API 路线必须记录 api-configured")
        if not is_ready(fields.get("TTS 供应方与模型")):
            errors.append("TTS API 路线缺少供应方或模型")
        if fields.get("TTS API 凭证位置") not in {"environment", "secure-store"}:
            errors.append("TTS API 只允许从 environment 或 secure-store 读取凭证")

    if audio_source == "local-tts-model":
        if tts_status != "local-model-known":
            errors.append("本地模型路线必须记录 local-model-known")
        if not is_ready(fields.get("本地模型线索")) or fields.get("本地模型线索") == "not-required":
            errors.append("本地模型路线缺少标准缓存或用户指定目录线索")

    if audio_source == "qwen-open-source":
        if tts_status != "qwen-download-approved":
            errors.append("Qwen 路线必须在开工阶段完成安装与下载授权")
        if fields.get("Qwen 当前 MLX 模型") != f"`{qwen_model_url()}`":
            errors.append("Qwen 路线没有绑定当前配置中的 MLX 模型地址")
        if not is_ready(fields.get("Qwen 目标目录")) or fields.get("Qwen 目标目录") == "not-required":
            errors.append("Qwen 路线缺少 Skill 仓库外的目标目录")
        if fields.get("Qwen 安装与下载授权") != "approved":
            errors.append("Qwen 安装与下载尚未获得用户明确授权")

    if require_approved and fields.get("开工信息确认") not in {"approved", "covered-by-user-message"}:
        errors.append("开工信息尚未获得用户确认")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="校验视频开工信息是否一次锁定口播和声音路线")
    parser.add_argument("brief", type=Path, help="video-brief.md 路径")
    parser.add_argument("--require-approved", action="store_true", help="要求用户已确认开工信息")
    args = parser.parse_args()
    errors = validate(args.brief.expanduser().resolve(), args.require_approved)
    if errors:
        for error in errors:
            print(f"FAIL {error}")
        return 1
    print("PASS 开工信息已一次锁定口播内容、最终声音和 TTS 路线")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

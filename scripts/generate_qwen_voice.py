#!/usr/bin/env python3
"""使用本地 MLX Qwen3-TTS 生成旁白，并可按场景生成连续音频 manifest。"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import tempfile
import wave
from pathlib import Path
from typing import Any

from audio_runtime import relaunch_with_runtime
from validate_master_script import validate_contract_binding as validate_approved_script
from validate_voice_brief import validate as validate_voice_brief
from validate_voice_selection import validate as validate_voice_selection


DEFAULT_TEMPERATURE = 0.66
DEFAULT_TOP_K = 38
DEFAULT_TOP_P = 0.9
DEFAULT_REPETITION_PENALTY = 1.08
DEFAULT_MAX_TOKENS = 1024


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path, label: str) -> dict[str, Any]:
    if not path.is_file():
        raise ValueError(f"{label}不存在：{path}")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"{label}读取失败：{exc}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"{label}必须为 JSON 对象")
    return value


def resolve_project_path(source_path: Path, value: Any) -> Path | None:
    if not isinstance(value, (str, Path)) or not str(value).strip():
        return None
    candidate = Path(value).expanduser()
    return candidate.resolve() if candidate.is_absolute() else (source_path.expanduser().resolve().parent / candidate).resolve()


def safe_name(value: str, fallback: str) -> str:
    name = re.sub(r"[^A-Za-z0-9_-]+", "_", value).strip("_")
    return name or fallback


def wav_info(path: Path) -> dict[str, Any]:
    try:
        with wave.open(str(path), "rb") as handle:
            frame_rate = handle.getframerate()
            frames = handle.getnframes()
            return {
                "sample_rate": frame_rate,
                "channels": handle.getnchannels(),
                "sample_width": handle.getsampwidth(),
                "frames": frames,
                "duration_seconds": frames / frame_rate if frame_rate else 0.0,
            }
    except (OSError, wave.Error) as exc:
        raise ValueError(f"生成的 WAV 无法读取：{path}；请检查 mlx_audio 输出：{exc}") from exc


def merge_wavs(paths: list[Path], output: Path) -> dict[str, Any]:
    if not paths:
        raise ValueError("没有可拼接的分段音频")
    first = wav_info(paths[0])
    output.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(output), "wb") as target:
        target.setnchannels(first["channels"])
        target.setsampwidth(first["sample_width"])
        target.setframerate(first["sample_rate"])
        for path in paths:
            info = wav_info(path)
            keys = ("sample_rate", "channels", "sample_width")
            if any(info[key] != first[key] for key in keys):
                raise ValueError(f"分段音频参数不一致，无法无损拼接：{path}")
            with wave.open(str(path), "rb") as source:
                target.writeframes(source.readframes(source.getnframes()))
    return wav_info(output)


def generate_one(
    model: Any,
    text: str,
    instruction: str | None,
    reference_audio: Path | None,
    reference_text: str | None,
    language: str,
    temperature: float,
    top_k: int,
    top_p: float,
    repetition_penalty: float,
    max_tokens: int,
) -> Any:
    if reference_audio:
        return list(
            model.generate(
                text=text,
                ref_audio=str(reference_audio),
                ref_text=reference_text,
                lang_code=language,
                split_pattern=None,
                temperature=temperature,
                top_k=top_k,
                top_p=top_p,
                repetition_penalty=repetition_penalty,
                max_tokens=max_tokens,
                verbose=True,
            )
        )[0]
    return list(
        model.generate_voice_design(
            text=text,
            instruct=instruction,
            language=language,
            temperature=temperature,
            top_k=top_k,
            top_p=top_p,
            repetition_penalty=repetition_penalty,
            max_tokens=max_tokens,
            verbose=True,
        )
    )[0]


def update_contract(
    contract_path: Path,
    contract: dict[str, Any],
    output: Path,
    manifest: dict[str, Any],
    voice_profile: str,
    voice_source: str,
    model_id: str,
    model_url: str,
    model_path: Path,
    language: str,
    instruction: str,
    reference_audio: Path | None,
    reference_text: str | None,
    reference_sha256: str | None,
) -> None:
    updated = dict(contract)
    relative_audio = Path(os.path.relpath(Path(output).resolve(), contract_path.parent.resolve()))
    updated.update(
        {
            "schema_version": "1.5",
            "voice_profile": voice_profile,
            "voice_source": voice_source,
            "provider": "Alibaba Qwen3-TTS",
            "runtime": "mlx-audio",
            "model_id": model_id,
            "model_url": model_url,
            "model_path": str(model_path),
            "voice_instruction": instruction if voice_source == "open-source-model" else updated.get("voice_instruction", ""),
            "authorization_record": updated.get("authorization_record") or "not-required",
            "audio_path": relative_audio.as_posix(),
            "audio_sha256": manifest["audio_sha256"],
            "duration_seconds": manifest["duration_seconds"],
            "sample_rate": manifest["sample_rate"],
            "channels": manifest["channels"],
            "audio_format": "wav",
            "language": language,
        }
    )
    by_scene = {item["scene_id"]: item for item in manifest["segments"]}
    updated["segments"] = [
        {
            **segment,
            **(
                {
                    "start_seconds": by_scene[str(segment.get("scene_id", ""))]["start_seconds"],
                    "end_seconds": by_scene[str(segment.get("scene_id", ""))]["end_seconds"],
                }
                if str(segment.get("scene_id", "")) in by_scene
                else {}
            ),
        }
        for segment in updated.get("segments", [])
    ]
    if reference_audio:
        updated["reference_audio"] = os.path.relpath(reference_audio.resolve(), contract_path.parent.resolve())
        updated["reference_audio_sha256"] = reference_sha256 or file_sha256(reference_audio)
        updated["reference_text"] = reference_text or ""
    contract_path.parent.mkdir(parents=True, exist_ok=True)
    contract_path.write_text(json.dumps(updated, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="使用本地 Qwen3-TTS 生成 WAV 讲解音频")
    parser.add_argument("--model-path", type=Path, required=True, help="Qwen3-TTS 模型目录")
    parser.add_argument("--runtime-python", type=Path, help="使用模型预检通过的同一 Python 运行环境")
    parser.add_argument("--text-file", type=Path, help="单段 UTF-8 讲稿文本；与 --segments-file 二选一")
    parser.add_argument("--segments-file", type=Path, help="包含 segments 的旁白契约；按场景分段生成")
    parser.add_argument("--output", type=Path, required=True, help="输出 WAV 路径")
    parser.add_argument("--manifest-output", type=Path, help="音频 manifest 路径，默认写在 WAV 旁边")
    parser.add_argument("--contract-output", type=Path, help="生成后写回的旁白契约路径")
    parser.add_argument("--instruction", help="用户确认的声音设计描述；VoiceDesign 路线必填")
    parser.add_argument("--voice-brief", type=Path, help="用户已确认的声音需求单；生成 VoiceDesign 试听时必填")
    parser.add_argument("--voice-selection", type=Path, help="用户已批准的声音选择文件；生成正式 Qwen 旁白时必填")
    parser.add_argument("--reference-config", type=Path, help="当前项目的授权参考音频配置")
    parser.add_argument("--model-id", default="", help="旁白契约中的模型 ID")
    parser.add_argument("--model-url", default="", help="旁白契约中的模型地址")
    parser.add_argument("--language", default="Chinese", help="Qwen 语言代码，默认 Chinese")
    parser.add_argument("--max-segment-chars", type=int, default=800, help="单段最长字符数，超出时必须拆分场景")
    parser.add_argument("--temperature", type=float)
    parser.add_argument("--top-k", type=int)
    parser.add_argument("--top-p", type=float)
    parser.add_argument("--repetition-penalty", type=float)
    parser.add_argument("--max-tokens", type=int)
    args = parser.parse_args()
    try:
        relaunch_with_runtime(args.runtime_python)
    except ValueError as exc:
        parser.error(str(exc))

    if bool(args.text_file) == bool(args.segments_file):
        parser.error("必须且只能提供 --text-file 或 --segments-file")
    if args.max_segment_chars <= 0:
        parser.error("--max-segment-chars 必须大于 0")
    if not args.model_path.is_dir():
        parser.error(f"模型目录不存在：{args.model_path}")
    if args.output.exists():
        parser.error(f"输出已存在，为避免覆盖请换版本路径：{args.output}")

    contract: dict[str, Any] | None = None
    source = "open-source-model"
    voice_profile = "qwen-voice-design"
    segments: list[dict[str, str]] = []
    if args.segments_file:
        contract = load_json(args.segments_file, "旁白契约")
        script_errors = validate_approved_script(args.segments_file.resolve(), contract)
        if script_errors:
            parser.error("完整口播门禁未通过：" + "；".join(script_errors))
        source = str(contract.get("voice_source", "")).strip()
        if source not in {"open-source-model", "user-reference"}:
            parser.error("Qwen 生成器只接受 open-source-model 或 user-reference 旁白契约")
        voice_profile = str(contract.get("voice_profile", voice_profile)).strip() or voice_profile
        raw_segments = contract.get("segments")
        if not isinstance(raw_segments, list) or not raw_segments:
            parser.error("旁白契约的 segments 必须包含至少一个场景")
        for index, raw in enumerate(raw_segments):
            if not isinstance(raw, dict) or not str(raw.get("tts_text", "")).strip():
                parser.error(f"旁白契约 segments[{index}] 缺少 tts_text")
            if len(str(raw["tts_text"]).strip()) > args.max_segment_chars:
                parser.error(f"旁白契约 segments[{index}] 过长，请按场景拆分后再生成")
            segments.append(
                {
                    "scene_id": str(raw.get("scene_id", f"s{index + 1:02d}")),
                    "tts_text": str(raw["tts_text"]).strip(),
                }
            )
    else:
        text_file = args.text_file.expanduser().resolve()
        if not text_file.is_file():
            parser.error(f"讲稿文件不存在：{text_file}")
        text = text_file.read_text(encoding="utf-8").strip()
        if not text:
            parser.error("讲稿文件为空，请先提供可朗读文本")
        if len(text) > args.max_segment_chars:
            parser.error("单段讲稿过长，请使用 --segments-file 按场景拆分后再生成")
        segments = [{"scene_id": "full", "tts_text": text}]

    reference_audio: Path | None = None
    reference_text: str | None = None
    reference_sha256: str | None = None
    voice_brief_path: Path | None = None
    voice_brief_sha256: str | None = None
    try:
        if args.reference_config:
            if source != "user-reference":
                parser.error("只有 user-reference 旁白契约可以使用 --reference-config")
            config = load_json(args.reference_config, "参考音频配置")
            authorization = str(config.get("authorization_record", "")).strip()
            if not authorization:
                parser.error("参考音频配置缺少 authorization_record")
            reference_text = str(config.get("reference_text", "")).strip()
            if not reference_text:
                parser.error("参考音频配置缺少 reference_text")
            reference_audio = Path(str(config.get("reference_audio", ""))).expanduser()
            if not reference_audio.is_absolute():
                reference_audio = args.reference_config.parent / reference_audio
            if not reference_audio.is_file():
                parser.error(f"参考音频不存在：{reference_audio}")
            expected_sha = str(config.get("reference_audio_sha256", "")).strip()
            reference_sha256 = file_sha256(reference_audio)
            if expected_sha and expected_sha != reference_sha256:
                parser.error("参考音频校验失败：文件与项目配置不一致")
            voice_profile = str(config.get("voice_profile", "user-reference")).strip() or "user-reference"
        elif source == "user-reference":
            parser.error("user-reference 旁白契约必须提供 --reference-config")
    except ValueError as exc:
        parser.error(str(exc))

    if args.text_file and not args.reference_config:
        if args.voice_brief is None:
            parser.error("生成 VoiceDesign 试听前必须提供用户已确认的 --voice-brief")
        voice_brief_path = args.voice_brief.expanduser().resolve()
        brief_errors = validate_voice_brief(voice_brief_path, True)
        if brief_errors:
            parser.error("声音需求门禁未通过：" + "；".join(brief_errors))
        voice_brief_sha256 = file_sha256(voice_brief_path)

    instruction = (args.instruction or (contract or {}).get("voice_instruction", "")).strip()
    model_id = args.model_id.strip() or str((contract or {}).get("model_id", "")).strip()
    model_url = args.model_url.strip() or str((contract or {}).get("model_url", "")).strip()
    if contract is not None and source == "open-source-model":
        raw_selection = args.voice_selection or resolve_project_path(
            args.segments_file,
            contract.get("voice_selection_path"),
        )
        if raw_selection is None:
            parser.error("正式 Qwen 旁白必须先提供用户已批准的 --voice-selection")
        selection_path = Path(raw_selection).expanduser().resolve()
        selection_errors = validate_voice_selection(selection_path, True)
        if selection_errors:
            parser.error("声音选择未通过：" + "；".join(selection_errors))
        selection = load_json(selection_path, "声音选择文件")
        selected_instruction = str(selection.get("selected_instruction", "")).strip()
        selected_model_id = str(selection.get("model_id", "")).strip()
        selected_model_url = str(selection.get("model_url", "")).strip()
        selected_model_path = resolve_project_path(selection_path, selection.get("model_path"))
        if selected_model_path != args.model_path.expanduser().resolve():
            parser.error("--model-path 与用户确认声音时通过预检的模型不一致")
        if instruction and instruction != selected_instruction:
            parser.error("--instruction 与用户确认的声音描述不一致")
        if model_id and model_id != selected_model_id:
            parser.error("model_id 与用户确认的声音模型不一致")
        if model_url and model_url != selected_model_url:
            parser.error("model_url 与用户确认的声音模型不一致")
        instruction = selected_instruction
        model_id = selected_model_id
        model_url = selected_model_url
        contract["voice_instruction"] = instruction
        contract["model_id"] = model_id
        contract["model_url"] = model_url
        contract["model_path"] = str(args.model_path.expanduser().resolve())
        contract["voice_selection_path"] = os.path.relpath(selection_path, args.segments_file.parent.resolve())
        contract["voice_selection_sha256"] = file_sha256(selection_path)
    elif not reference_audio and not instruction:
        parser.error("请提供用户确认的声音描述，再使用 --instruction 生成旁白")

    temperature = args.temperature if args.temperature is not None else DEFAULT_TEMPERATURE
    top_k = args.top_k if args.top_k is not None else DEFAULT_TOP_K
    top_p = args.top_p if args.top_p is not None else DEFAULT_TOP_P
    repetition_penalty = args.repetition_penalty if args.repetition_penalty is not None else DEFAULT_REPETITION_PENALTY
    max_tokens = args.max_tokens if args.max_tokens is not None else DEFAULT_MAX_TOKENS
    manifest_output = args.manifest_output or args.output.with_name(f"{args.output.stem}.manifest.json")
    if manifest_output.exists():
        parser.error(f"manifest 已存在，为避免覆盖请换版本路径：{manifest_output}")
    if args.contract_output and args.contract_output.expanduser().resolve() != (args.segments_file or args.contract_output).expanduser().resolve() and args.contract_output.exists():
        parser.error(f"旁白契约已存在，为避免覆盖请换路径：{args.contract_output}")

    try:
        from mlx_audio.audio_io import write as write_audio
        from mlx_audio.tts.utils import load_model
    except ImportError:
        print("当前 Python 未找到 mlx_audio。请使用模型发现报告中的 recommended_runtime_python 重新运行；只有确认没有兼容环境后才安装依赖。", file=sys.stderr)
        return 1

    try:
        model = load_model(args.model_path)
        with tempfile.TemporaryDirectory(prefix="qwen-tts-") as temp_dir:
            temp_root = Path(temp_dir)
            segment_paths: list[Path] = []
            segment_durations: list[float] = []
            for index, segment in enumerate(segments):
                segment_path = temp_root / f"{index:03d}-{safe_name(segment['scene_id'], f'segment-{index + 1:02d}')}.wav"
                result = generate_one(
                    model,
                    segment["tts_text"],
                    instruction if not reference_audio else None,
                    reference_audio,
                    reference_text,
                    args.language,
                    temperature,
                    top_k,
                    top_p,
                    repetition_penalty,
                    max_tokens,
                )
                write_audio(segment_path, result.audio, result.sample_rate)
                segment_paths.append(segment_path)
                segment_durations.append(wav_info(segment_path)["duration_seconds"])
            audio_info = merge_wavs(segment_paths, args.output)

        timestamp = 0.0
        manifest_segments = []
        for segment, duration in zip(segments, segment_durations):
            manifest_segments.append(
                {
                    "scene_id": segment["scene_id"],
                    "start_seconds": round(timestamp, 6),
                    "end_seconds": round(timestamp + duration, 6),
                }
            )
            timestamp += duration
        manifest = {
            "schema_version": "1.0",
            "voice_source": source,
            "voice_profile": voice_profile,
            "provider": "Alibaba Qwen3-TTS",
            "runtime": "mlx-audio",
            "language": args.language,
            "model_id": model_id,
            "model_url": model_url,
            "audio_path": str(args.output.resolve()),
            "audio_sha256": file_sha256(args.output),
            "duration_seconds": round(audio_info["duration_seconds"], 6),
            "sample_rate": audio_info["sample_rate"],
            "channels": audio_info["channels"],
            "audio_format": "wav",
            "segments": manifest_segments,
        }
        if reference_sha256:
            manifest["reference_audio_sha256"] = reference_sha256
        if voice_brief_path and voice_brief_sha256:
            manifest["voice_brief_path"] = str(voice_brief_path)
            manifest["voice_brief_sha256"] = voice_brief_sha256
        manifest_output.parent.mkdir(parents=True, exist_ok=True)
        manifest_output.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        if args.contract_output and contract is not None:
            update_contract(
                args.contract_output.expanduser().resolve(),
                contract,
                args.output,
                manifest,
                voice_profile,
                source,
                model_id,
                model_url,
                args.model_path.expanduser().resolve(),
                args.language,
                instruction,
                reference_audio,
                reference_text,
                reference_sha256,
            )
    except Exception as exc:  # pragma: no cover - requires a real MLX model/runtime
        print(f"声音生成失败：{exc}", file=sys.stderr)
        return 1

    print(f"output={args.output.resolve()}")
    print(f"manifest={manifest_output.resolve()}")
    print(f"sample_rate={manifest['sample_rate']}")
    print(f"audio_duration={manifest['duration_seconds']}")
    print(f"audio_sha256={manifest['audio_sha256']}")
    print(f"voice_profile={voice_profile}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

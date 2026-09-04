#!/usr/bin/env python3
"""把用户已有音频或其他 TTS 产物登记进旁白契约。"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from validate_master_script import validate_contract_binding
from validate_narration_contract import file_sha256, probe_audio
from validate_voice_selection import validate as validate_voice_selection


def main() -> int:
    parser = argparse.ArgumentParser(description="登记实际旁白音频的路径、哈希和媒体参数")
    parser.add_argument("--contract", type=Path, required=True, help="已有旁白契约")
    parser.add_argument("--audio", type=Path, required=True, help="实际旁白音频")
    parser.add_argument("--voice-source", choices=("external", "other-tts", "user-reference"), required=True)
    parser.add_argument("--provider", default="", help="other-tts 的供应方")
    parser.add_argument("--model-id", default="", help="other-tts 的模型标识")
    parser.add_argument("--model-url", default="", help="other-tts 的模型或服务地址")
    parser.add_argument("--runtime", default="", help="other-tts 的运行时")
    parser.add_argument("--voice-selection", type=Path, help="other-tts 必须提供的已批准声音选择文件")
    parser.add_argument("--manifest-output", type=Path, help="输出音频 manifest，默认写在音频旁边")
    args = parser.parse_args()

    contract_path = args.contract.expanduser().resolve()
    audio_path = args.audio.expanduser().resolve()
    if not contract_path.is_file():
        parser.error(f"旁白契约不存在：{contract_path}")
    if not audio_path.is_file():
        parser.error(f"旁白音频不存在：{audio_path}")
    if args.voice_source == "other-tts" and not all((args.provider, args.model_id, args.model_url, args.runtime)):
        parser.error("other-tts 必须同时提供 --provider、--model-id、--model-url 和 --runtime")
    voice_selection_path: Path | None = None
    voice_selection: dict[str, object] | None = None
    if args.voice_source == "other-tts":
        if args.voice_selection is None:
            parser.error("other-tts 必须提供 --voice-selection，先完成 API 预检和用户选声")
        voice_selection_path = args.voice_selection.expanduser().resolve()
        selection_errors = validate_voice_selection(voice_selection_path, True)
        if selection_errors:
            parser.error("声音选择未通过：" + "；".join(selection_errors))
        try:
            loaded_selection = json.loads(voice_selection_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            parser.error(f"声音选择读取失败：{exc}")
        if not isinstance(loaded_selection, dict) or loaded_selection.get("engine_type") != "api":
            parser.error("other-tts 必须绑定 engine_type=api 的声音选择")
        voice_selection = loaded_selection
        if str(voice_selection.get("provider", "")).strip() != args.provider:
            parser.error("--provider 与已批准声音选择不一致")
        if str(voice_selection.get("model_id", "")).strip() != args.model_id:
            parser.error("--model-id 与已批准声音选择不一致")

    try:
        contract = json.loads(contract_path.read_text(encoding="utf-8"))
        if not isinstance(contract, dict):
            raise ValueError("旁白契约必须为 JSON 对象")
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        parser.error(f"旁白契约读取失败：{exc}")
    script_errors = validate_contract_binding(contract_path, contract, True)
    if script_errors:
        parser.error("完整口播门禁未通过：" + "；".join(script_errors))
    if args.voice_source == "user-reference" and not str(contract.get("authorization_record", "")).strip():
        parser.error("user-reference 必须先在旁白契约中记录授权说明")

    audio_info, probe_error = probe_audio(audio_path)
    if probe_error or audio_info is None:
        parser.error(probe_error or "无法读取旁白音频")
    relative_audio = Path(os.path.relpath(audio_path, contract_path.parent))
    contract.update(
        {
            "schema_version": "1.5",
            "voice_source": args.voice_source,
            "voice_profile": str(contract.get("voice_profile", "")).strip() or ("user-recording" if args.voice_source == "external" else "external-tts"),
            "provider": args.provider or ("user-recording" if args.voice_source == "external" else contract.get("provider", "")),
            "model_id": args.model_id or contract.get("model_id", ""),
            "model_url": args.model_url or contract.get("model_url", ""),
            "runtime": args.runtime or ("recorded" if args.voice_source == "external" else contract.get("runtime", "")),
            "voice_instruction": (
                str(voice_selection.get("selected_instruction", "")).strip()
                if voice_selection is not None
                else contract.get("voice_instruction", "")
            ),
            "voice_selection_path": (
                Path(os.path.relpath(voice_selection_path, contract_path.parent)).as_posix()
                if voice_selection_path is not None
                else contract.get("voice_selection_path", "")
            ),
            "voice_selection_sha256": (
                file_sha256(voice_selection_path)
                if voice_selection_path is not None
                else contract.get("voice_selection_sha256", "")
            ),
            "authorization_record": contract.get("authorization_record") or "not-required",
            "audio_path": relative_audio.as_posix(),
            "audio_sha256": file_sha256(audio_path),
            "duration_seconds": round(audio_info["duration_seconds"], 6),
            "sample_rate": audio_info["sample_rate"],
            "channels": audio_info["channels"],
            "audio_format": audio_path.suffix.removeprefix(".").lower() or "unknown",
        }
    )
    contract_path.write_text(json.dumps(contract, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    manifest_output = args.manifest_output or audio_path.with_name(f"{audio_path.stem}.manifest.json")
    if manifest_output.exists():
        parser.error(f"manifest 已存在，为避免覆盖请换版本路径：{manifest_output}")
    manifest_output.parent.mkdir(parents=True, exist_ok=True)
    manifest_output.write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "voice_source": args.voice_source,
                "audio_path": str(audio_path),
                "audio_sha256": contract["audio_sha256"],
                "duration_seconds": contract["duration_seconds"],
                "sample_rate": contract["sample_rate"],
                "channels": contract["channels"],
                "audio_format": contract["audio_format"],
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"PASS 音频已登记：{audio_path}")
    print(f"manifest={manifest_output.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Local-first word-level STT executor with normalized, cacheable output."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from audio_runtime import relaunch_with_runtime


BACKENDS = ("mlx-whisper", "faster-whisper", "openai-whisper")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def normalize_word(value: Any) -> dict[str, Any] | None:
    if isinstance(value, dict):
        text = value.get("word", value.get("text", ""))
        start = value.get("start")
        end = value.get("end")
    else:
        text = getattr(value, "word", getattr(value, "text", ""))
        start = getattr(value, "start", None)
        end = getattr(value, "end", None)
    if not isinstance(text, str) or not text.strip():
        return None
    if not isinstance(start, (int, float)) or not isinstance(end, (int, float)) or end < start:
        return None
    return {"text": text.strip(), "start": round(float(start), 3), "end": round(float(end), 3)}


def normalize_result(payload: dict[str, Any]) -> tuple[str, list[dict[str, Any]], list[dict[str, Any]]]:
    segments: list[dict[str, Any]] = []
    words: list[dict[str, Any]] = []
    for index, raw_segment in enumerate(payload.get("segments") or []):
        if isinstance(raw_segment, dict):
            text = str(raw_segment.get("text", "")).strip()
            start = raw_segment.get("start")
            end = raw_segment.get("end")
            raw_words = raw_segment.get("words") or []
        else:
            text = str(getattr(raw_segment, "text", "")).strip()
            start = getattr(raw_segment, "start", None)
            end = getattr(raw_segment, "end", None)
            raw_words = getattr(raw_segment, "words", None) or []
        normalized_words = [item for item in (normalize_word(word) for word in raw_words) if item]
        words.extend(normalized_words)
        if isinstance(start, (int, float)) and isinstance(end, (int, float)) and end >= start:
            segments.append({
                "id": f"seg-{index + 1:04d}",
                "text": text,
                "start": round(float(start), 3),
                "end": round(float(end), 3),
                "words": normalized_words,
            })
    top_words = payload.get("words") or []
    if not words and isinstance(top_words, list):
        words = [item for item in (normalize_word(word) for word in top_words) if item]
    text = str(payload.get("text", "")).strip() or "".join(segment["text"] for segment in segments)
    return text, segments, words


def local_model(model: str, allow_download: bool) -> str:
    path = Path(model).expanduser()
    if path.exists():
        return str(path.resolve())
    if allow_download:
        return model
    raise ValueError("模型不是本地路径；如确需从模型仓库下载，必须显式添加 --allow-model-download")


def run_backend(source: Path, backend: str, model: str, language: str | None, allow_download: bool) -> dict[str, Any]:
    model_value = local_model(model, allow_download)
    if backend == "mlx-whisper":
        try:
            import mlx_whisper  # type: ignore
        except ImportError as exc:
            raise RuntimeError("未安装 mlx-whisper；先运行 doctor.py，或选择已安装的本地 STT") from exc
        kwargs: dict[str, Any] = {"path_or_hf_repo": model_value, "word_timestamps": True}
        if language:
            kwargs["language"] = language
        return mlx_whisper.transcribe(str(source), **kwargs)
    if backend == "openai-whisper":
        try:
            import whisper  # type: ignore
        except ImportError as exc:
            raise RuntimeError("未安装 openai-whisper；先运行 doctor.py") from exc
        loaded = whisper.load_model(model_value)
        return loaded.transcribe(str(source), language=language, word_timestamps=True)
    if backend == "faster-whisper":
        try:
            from faster_whisper import WhisperModel  # type: ignore
        except ImportError as exc:
            raise RuntimeError("未安装 faster-whisper；先运行 doctor.py") from exc
        loaded = WhisperModel(model_value, device="auto", compute_type="auto")
        iterator, info = loaded.transcribe(str(source), language=language, word_timestamps=True)
        segments = list(iterator)
        return {"text": "".join(segment.text for segment in segments), "segments": segments, "language": info.language}
    raise ValueError(f"不支持的 backend：{backend}")


def build_output(source: Path, backend: str, model: str, language: str, payload: dict[str, Any]) -> dict[str, Any]:
    text, segments, words = normalize_result(payload)
    duration = max((word["end"] for word in words), default=max((segment["end"] for segment in segments), default=0.0))
    return {
        "schema_version": "1.0",
        "source": {"path": str(source), "sha256": sha256(source)},
        "backend": backend,
        "model": model,
        "language": language or str(payload.get("language", "")),
        "duration_seconds": round(float(duration), 3),
        "text": text,
        "segments": segments,
        "words": words,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="使用本地开源 STT 生成统一词级时间戳")
    parser.add_argument("source", type=Path)
    parser.add_argument("--runtime-python", type=Path, help="doctor 检测到的兼容 Python；不复制或重装已有环境")
    parser.add_argument("--backend", choices=BACKENDS, required=True)
    parser.add_argument("--model", required=True, help="本地模型目录；模型仓库 ID 需配合 --allow-model-download")
    parser.add_argument("--language", default="")
    parser.add_argument("--allow-model-download", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        relaunch_with_runtime(args.runtime_python)
    except ValueError as exc:
        parser.error(str(exc))
    source = args.source.expanduser().resolve()
    if not source.is_file():
        parser.error(f"音视频不存在：{source}")
    source_hash = sha256(source)
    output = args.output or source.with_name(f"{source.stem}.{source_hash[:12]}.transcript.json")
    output = output.expanduser().resolve()
    if output.is_file():
        cached = json.loads(output.read_text(encoding="utf-8"))
        if cached.get("source", {}).get("sha256") == source_hash and cached.get("backend") == args.backend and cached.get("model") == args.model:
            print(f"CACHED {output}")
            return 0
    try:
        payload = run_backend(source, args.backend, args.model, args.language or None, args.allow_model_download)
        report = build_output(source, args.backend, args.model, args.language, payload)
    except (RuntimeError, ValueError, OSError) as exc:
        print(f"FAIL {exc}")
        return 1
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"PASS 词级转写已生成：{output}（{len(report['words'])} 词）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

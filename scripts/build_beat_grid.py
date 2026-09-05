#!/usr/bin/env python3
"""Build a deterministic or locally estimated beat grid without network calls."""

from __future__ import annotations

import argparse
import array
import hashlib
import json
import math
import shutil
import statistics
import subprocess
import tempfile
import wave
from pathlib import Path
from typing import Any


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def duration_seconds(source: Path) -> float:
    completed = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", str(source)],
        capture_output=True, text=True, check=True,
    )
    return float(completed.stdout.strip())


def grid(bpm: float, offset: float, duration: float) -> tuple[list[float], list[float]]:
    interval = 60.0 / bpm
    start = offset
    while start > 0:
        start -= interval
    while start < 0:
        start += interval
    beats: list[float] = []
    value = start
    while value <= duration + 1e-6:
        beats.append(round(value, 3))
        value += interval
    downbeats = [value for index, value in enumerate(beats) if index % 4 == 0]
    return beats, downbeats


def estimate(source: Path) -> tuple[float, float, float, str]:
    if not shutil.which("ffmpeg") or not shutil.which("ffprobe"):
        raise RuntimeError("需要 ffmpeg 和 ffprobe")
    with tempfile.TemporaryDirectory() as temp_dir:
        wav_path = Path(temp_dir) / "beat-source.wav"
        subprocess.run(
            ["ffmpeg", "-y", "-v", "error", "-i", str(source), "-vn", "-ac", "1", "-ar", "16000", "-c:a", "pcm_s16le", str(wav_path)],
            check=True,
        )
        with wave.open(str(wav_path), "rb") as handle:
            rate = handle.getframerate()
            width = handle.getsampwidth()
            chunk_frames = max(1, int(rate * 0.05))
            energies: list[float] = []
            while data := handle.readframes(chunk_frames):
                if width != 2:
                    raise RuntimeError("节拍检测只支持 ffmpeg 输出的 16-bit PCM")
                samples = array.array("h", data)
                if samples:
                    energies.append(math.sqrt(sum(sample * sample for sample in samples) / len(samples)))
    if len(energies) < 20 or max(energies, default=0) <= 0:
        raise RuntimeError("音频过短或没有可检测的节拍能量")
    novelties = [0.0]
    for index in range(1, len(energies)):
        baseline = statistics.fmean(energies[max(0, index - 8):index])
        novelties.append(max(0.0, energies[index] - baseline))
    positive = [value for value in novelties if value > 0]
    threshold = sorted(positive)[max(0, int(len(positive) * 0.82) - 1)] if positive else 0
    peaks: list[float] = []
    for index in range(1, len(novelties) - 1):
        time = index * 0.05
        if novelties[index] >= threshold and novelties[index] >= novelties[index - 1] and novelties[index] >= novelties[index + 1]:
            if not peaks or time - peaks[-1] >= 0.25:
                peaks.append(time)
    intervals = [b - a for a, b in zip(peaks, peaks[1:]) if 0.25 <= b - a <= 1.5]
    if len(intervals) < 4:
        raise RuntimeError("没有足够稳定的能量峰；请手动提供 --bpm")
    interval = statistics.median(intervals)
    bpm = 60.0 / interval
    while bpm < 70:
        bpm *= 2
    while bpm > 180:
        bpm /= 2
    offset = peaks[0] % (60.0 / bpm)
    confidence = "medium" if len(intervals) >= 12 else "low"
    return round(bpm, 3), round(offset, 3), duration_seconds(source), confidence


def build_report(source: Path, bpm: float, offset: float, duration: float, method: str, confidence: str) -> dict[str, Any]:
    beats, downbeats = grid(bpm, offset, duration)
    return {
        "schema_version": "1.0",
        "source": {"path": str(source), "sha256": sha256(source)},
        "method": method,
        "confidence": confidence,
        "bpm": bpm,
        "offset_seconds": offset,
        "duration_seconds": round(duration, 3),
        "beats": beats,
        "downbeats": downbeats,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="从音乐建立节拍网格；已知 BPM 优先使用人工值")
    parser.add_argument("source", type=Path)
    parser.add_argument("--bpm", type=float)
    parser.add_argument("--offset-seconds", type=float, default=0.0)
    parser.add_argument("--duration-seconds", type=float)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    source = args.source.expanduser().resolve()
    if not source.is_file():
        parser.error(f"音频不存在：{source}")
    try:
        if args.bpm is not None:
            if not 40 <= args.bpm <= 240:
                raise ValueError("BPM 应在 40—240 之间")
            duration = args.duration_seconds or duration_seconds(source)
            bpm, offset, method, confidence = args.bpm, args.offset_seconds, "manual-bpm", "declared"
        else:
            bpm, offset, duration, confidence = estimate(source)
            method = "local-energy-onset-estimate"
        report = build_report(source, bpm, offset, duration, method, confidence)
    except (RuntimeError, ValueError, OSError, subprocess.CalledProcessError) as exc:
        print(f"FAIL {exc}")
        return 1
    output = args.output.expanduser().resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"PASS beat-grid：{report['bpm']:.3f} BPM，{len(report['beats'])} 个节拍，confidence={report['confidence']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

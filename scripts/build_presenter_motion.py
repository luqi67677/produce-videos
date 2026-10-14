#!/usr/bin/env python3
"""用整数 PCM WAV 生成嘴部活动和眨眼轨迹；不生成口型图片或音素对齐。

例：python3 scripts/build_presenter_motion.py --audio project/audio/narration.wav \
    --output project/audio/presenter-motion.json --fps 30 --seed 0

mouth_openness 和 blink 均为 0..1。blink=1 表示眼睛闭合。
frames[].time 从片段的 0 秒开始；t 是同值别名。加 source_offset_seconds 得到原音频时间。
"""

from __future__ import annotations

import argparse
import array
import hashlib
import json
import math
import random
import sys
import wave
from fractions import Fraction
from pathlib import Path
from typing import Any


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def pcm_rms(data: bytes, sample_width: int) -> float:
    """按所有声道的能量计算 RMS，避免先混合声道产生相位抵消。"""
    if not data:
        return 0.0
    if len(data) % sample_width:
        raise ValueError("PCM 数据没有对齐到整数样本")
    count = len(data) // sample_width
    if sample_width == 1:
        energy = sum((value - 128) ** 2 for value in data)
    elif sample_width in (2, 4):
        values = array.array("h" if sample_width == 2 else "i")
        if values.itemsize != sample_width:
            raise ValueError("当前运行时的整数类型宽度不支持该 PCM 格式")
        values.frombytes(data)
        if sys.byteorder != "little":
            values.byteswap()
        energy = sum(value * value for value in values)
    elif sample_width == 3:
        energy = 0
        for index in range(0, len(data), 3):
            value = data[index] | (data[index + 1] << 8) | (data[index + 2] << 16)
            if value & 0x800000:
                value -= 0x1000000
            energy += value * value
    else:
        raise ValueError("仅支持 8、16、24、32 位整数 PCM WAV")
    full_scale = 1 << (8 * sample_width - 1)
    return math.sqrt(energy / count) / full_scale


def percentile(values: list[float], percent: float) -> float:
    ordered = sorted(values)
    if not ordered:
        return 0.0
    position = (len(ordered) - 1) * percent / 100.0
    lower = math.floor(position)
    upper = math.ceil(position)
    return ordered[lower] + (ordered[upper] - ordered[lower]) * (position - lower)


def blink_schedule(
    source_duration: float,
    seed: int,
    min_interval: float,
    max_interval: float,
    min_duration: float,
    max_duration: float,
) -> list[dict[str, float]]:
    """从原音频 0 秒开始安排眨眼；与语音和词边界无关。"""
    rng = random.Random(seed)
    events: list[dict[str, float]] = []
    start = rng.uniform(min_interval, max_interval)
    while start < source_duration:
        events.append({"source_start_seconds": start, "duration_seconds": rng.uniform(min_duration, max_duration)})
        start += rng.uniform(min_interval, max_interval)
    return events


def blink_value(time: float, event: dict[str, float], fps: float) -> float:
    start, duration = event["source_start_seconds"], event["duration_seconds"]
    phase = (time - start) / duration
    if phase < 0 or phase >= 1:
        return 0.0
    # 在靠近闭眼峰值的一个视频帧上完全闭合；不改身体或头部。
    if abs(time - (start + duration * 0.425)) <= 0.5 / fps:
        return 1.0
    if phase < 0.35:
        return 0.5 * (1.0 - math.cos(math.pi * phase / 0.35))
    if phase < 0.5:
        return 1.0
    return 0.5 * (1.0 + math.cos(math.pi * (phase - 0.5) / 0.5))


def build_motion(
    audio: Path,
    *,
    fps: float = 30.0,
    seed: int = 0,
    start: float = 0.0,
    duration: float | None = None,
    rms_window_ms: float = 40.0,
    silence_rms: float = 0.003,
    open_rms: float = 0.010,
    close_rms: float = 0.006,
    attack_ms: float = 30.0,
    release_ms: float = 80.0,
    close_hold_ms: float = 60.0,
    normalization_percentile: float = 95.0,
    normalization_floor_rms: float = 0.04,
    blink_min_interval: float = 4.0,
    blink_max_interval: float = 7.0,
    blink_min_duration_ms: float = 120.0,
    blink_max_duration_ms: float = 180.0,
) -> dict[str, Any]:
    numbers = [fps, start, rms_window_ms, silence_rms, open_rms, close_rms, attack_ms, release_ms,
               close_hold_ms, normalization_percentile, normalization_floor_rms, blink_min_interval,
               blink_max_interval, blink_min_duration_ms, blink_max_duration_ms]
    if duration is not None:
        numbers.append(duration)
    if not all(math.isfinite(value) for value in numbers):
        raise ValueError("所有时间、阈值和 fps 必须是有限数值")
    if fps <= 0 or start < 0 or (duration is not None and duration <= 0):
        raise ValueError("fps、duration 必须大于 0，start 不能小于 0")
    if not 0 <= silence_rms < close_rms < open_rms <= 1:
        raise ValueError("阈值必须满足 0 <= silence_rms < close_rms < open_rms <= 1")
    if min(rms_window_ms, attack_ms, release_ms, close_hold_ms, normalization_floor_rms) <= 0:
        raise ValueError("RMS 窗口、attack/release、闭嘴等待和归一基准必须大于 0")
    if not 0 < normalization_percentile <= 100:
        raise ValueError("归一百分位必须在 (0, 100] 内")
    if not 0 < blink_min_interval <= blink_max_interval:
        raise ValueError("眨眼间隔必须满足 0 < min <= max")
    if not 0 < blink_min_duration_ms <= blink_max_duration_ms < blink_min_interval * 1000:
        raise ValueError("眨眼时长必须为正，max 不小于 min，且短于最小间隔")

    audio = audio.expanduser().resolve()
    before = audio.stat()
    audio_sha = file_sha256(audio)
    with wave.open(str(audio), "rb") as wav:
        sample_rate, channels = wav.getframerate(), wav.getnchannels()
        sample_width, total_samples = wav.getsampwidth(), wav.getnframes()
        if wav.getcomptype() != "NONE" or sample_width not in (1, 2, 3, 4):
            raise ValueError("仅支持无压缩的 8、16、24、32 位整数 PCM WAV；不支持浮点 WAV")
        if sample_rate <= 0 or channels <= 0 or total_samples <= 0:
            raise ValueError("音频没有可读取的 PCM 样本")
        wav.setpos(total_samples - 1)
        if len(wav.readframes(1)) != channels * sample_width:
            raise ValueError("WAV 实际数据短于文件声明的时长")
        source_duration = total_samples / sample_rate
        start_sample = round(start * sample_rate)
        if start >= source_duration or start_sample >= total_samples:
            raise ValueError("start 必须早于原音频结束位置")
        remaining = total_samples - start_sample
        requested_samples = remaining if duration is None else round(duration * sample_rate)
        selected_samples = min(requested_samples, remaining)
        if selected_samples <= 0:
            raise ValueError("所选片段不足一个 PCM 样本")
        actual_start = start_sample / sample_rate
        actual_duration = selected_samples / sample_rate
        selected_end = start_sample + selected_samples
        fps_fraction = Fraction(str(fps))
        count_numerator = selected_samples * fps_fraction.numerator
        count_denominator = sample_rate * fps_fraction.denominator
        frame_count = (count_numerator + count_denominator - 1) // count_denominator
        window_samples = max(1, round(sample_rate * rms_window_ms / 1000.0))
        rms_values = []
        for index in range(frame_count):
            center = min(selected_end - 1, start_sample + round(index * sample_rate / fps))
            left = max(start_sample, center - window_samples // 2)
            right = min(selected_end, center + (window_samples + 1) // 2)
            wav.setpos(left)
            data = wav.readframes(right - left)
            if len(data) != (right - left) * channels * sample_width:
                raise ValueError("读取 RMS 窗口时发现 PCM 数据不完整")
            rms_values.append(pcm_rms(data, sample_width))
    after = audio.stat()
    if (before.st_size, before.st_mtime_ns) != (after.st_size, after.st_mtime_ns):
        raise ValueError("分析期间原音频发生变化，请重新运行")

    normalization_reference = max(normalization_floor_rms, open_rms * 1.5,
                                  percentile(rms_values, normalization_percentile))
    events = blink_schedule(source_duration, seed, blink_min_interval, blink_max_interval,
                            blink_min_duration_ms / 1000.0, blink_max_duration_ms / 1000.0)
    selected_events = [event for event in events
                       if event["source_start_seconds"] < actual_start + actual_duration
                       and event["source_start_seconds"] + event["duration_seconds"] > actual_start]
    active, envelope, below_close = False, 0.0, 0.0
    step = 1.0 / fps
    frames = []
    event_index = 0
    for index, rms in enumerate(rms_values):
        time = index / fps
        if rms <= silence_rms:
            # 真正静音立即闭嘴；不能用 release 把开口拖进停顿。
            active, envelope, below_close = False, 0.0, 0.0
        else:
            if not active and rms >= open_rms:
                active, below_close = True, 0.0
            elif active and rms < close_rms:
                below_close += step
                if below_close >= close_hold_ms / 1000.0:
                    active = False
            elif active:
                below_close = 0.0
            if not active:
                envelope = 0.0
            else:
                target = max(0.0, min(1.0, (rms - close_rms) / (normalization_reference - close_rms)))
                tau = (attack_ms if target > envelope else release_ms) / 1000.0
                envelope += (target - envelope) * (1.0 - math.exp(-step / tau))
                envelope = max(0.0, min(1.0, envelope))
        source_time = actual_start + time
        while event_index < len(selected_events) and source_time >= (
            selected_events[event_index]["source_start_seconds"] + selected_events[event_index]["duration_seconds"]
        ):
            event_index += 1
        blink = blink_value(source_time, selected_events[event_index], fps) if event_index < len(selected_events) else 0.0
        frames.append({"time": time, "t": time, "mouth_openness": round(envelope, 6), "blink": round(blink, 6)})

    return {
        "schema_version": "1.0",
        "method": "audio_activity_sync",
        "sync_scope": "amplitude-driven; non-phoneme-level lip_sync",
        "phoneme_level_lip_sync": False,
        "body_motion": "fixed",
        "asset_readiness": "not-evaluated",
        "limitations": "这是音频活动轨迹，不识别音素、不验证口型或眼睛素材，也不代表视觉验收完成。",
        "source_audio_path": str(audio),
        "source_audio_sha256": audio_sha,
        "source_audio_duration_seconds": source_duration,
        "source_audio_sample_rate": sample_rate,
        "source_audio_channels": channels,
        "source_audio_sample_width_bytes": sample_width,
        "source_audio_pcm_encoding": "unsigned-integer-8bit" if sample_width == 1 else "signed-integer-little-endian",
        "source_offset_seconds": actual_start,
        "source_offset_samples": start_sample,
        "selected_audio_samples": selected_samples,
        "duration_seconds": actual_duration,
        "frame_count": frame_count,
        "fps": fps,
        "frame_time_basis": "片段本地时间；原音频时间 = source_offset_seconds + frames[].time",
        "frame_coverage": "每帧区间 [time, min(time + 1/fps, duration_seconds))；末帧可能不足一整帧",
        "parameters": {
            "seed": seed, "requested_start_seconds": start, "requested_duration_seconds": duration,
            "duration_clipped_to_source_end": requested_samples > remaining,
            "rms_window_ms": rms_window_ms, "silence_rms": silence_rms, "open_rms": open_rms,
            "close_rms": close_rms, "attack_ms": attack_ms, "release_ms": release_ms,
            "close_hold_ms": close_hold_ms, "normalization_percentile": normalization_percentile,
            "normalization_floor_rms": normalization_floor_rms, "normalization_reference_rms": normalization_reference,
            "normalization_scope": "所选音频片段的 RMS 分布；短样重新归一，整片请生成一次后复用同一轨迹",
            "clip_envelope_initial_state": "closed",
            "blink_min_interval_seconds": blink_min_interval, "blink_max_interval_seconds": blink_max_interval,
            "blink_interval_definition": "相邻眨眼开始时刻的间隔；从原音频 0 秒计时，与语音无关",
            "blink_min_duration_ms": blink_min_duration_ms, "blink_max_duration_ms": blink_max_duration_ms,
            "blink_value_definition": "0 为睁眼，1 为闭眼；快速闭合、短暂闭合、较慢睁开",
        },
        "analysis": {"min_rms": min(rms_values), "max_rms": max(rms_values),
                     "mouth_active_frame_count": sum(frame["mouth_openness"] > 0 for frame in frames),
                     "blink_active_frame_count": sum(frame["blink"] > 0 for frame in frames)},
        "blink_events": selected_events,
        "frames": frames,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="从 PCM WAV 生成嘴部强度与自然眨眼 JSON；audio_activity_sync，非音素级 lip_sync")
    parser.add_argument("--audio", required=True, type=Path, help="源 PCM WAV")
    parser.add_argument("--output", required=True, type=Path, help="轨迹 JSON")
    parser.add_argument("--fps", type=float, default=30.0)
    parser.add_argument("--seed", type=int, default=0, help="眨眼随机种子；相同音频与参数可重复生成")
    parser.add_argument("--start", type=float, default=0.0, help="原音频起点，秒；按样本精度取整")
    parser.add_argument("--duration", type=float, default=None, help="短样时长，秒；超过源结束时截到源结束")
    parser.add_argument("--rms-window-ms", type=float, default=40.0)
    parser.add_argument("--silence-rms", type=float, default=0.003)
    parser.add_argument("--open-rms", type=float, default=0.010)
    parser.add_argument("--close-rms", type=float, default=0.006)
    parser.add_argument("--attack-ms", type=float, default=30.0)
    parser.add_argument("--release-ms", type=float, default=80.0)
    parser.add_argument("--close-hold-ms", type=float, default=60.0)
    parser.add_argument("--normalization-percentile", type=float, default=95.0)
    parser.add_argument("--normalization-floor-rms", type=float, default=0.04)
    parser.add_argument("--blink-min-interval", type=float, default=4.0, help="最短眨眼间隔，秒")
    parser.add_argument("--blink-max-interval", type=float, default=7.0, help="最长眨眼间隔，秒")
    parser.add_argument("--blink-min-duration-ms", type=float, default=120.0)
    parser.add_argument("--blink-max-duration-ms", type=float, default=180.0)
    args = parser.parse_args()
    if args.audio.expanduser().resolve() == args.output.expanduser().resolve():
        parser.error("输出不能覆盖源音频")
    try:
        options = vars(args).copy()
        output = options.pop("output").expanduser()
        audio = options.pop("audio")
        result = build_motion(audio, **options)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    except (OSError, ValueError, wave.Error) as exc:
        parser.error(str(exc))
    print(f"PASS audio_activity_sync：{result['frame_count']} 帧，{result['duration_seconds']:.6f} 秒；不代表口型素材或视觉验收完成")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

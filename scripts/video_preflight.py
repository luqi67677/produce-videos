#!/usr/bin/env python3

import argparse
import hashlib
import json
import math
import re
import shutil
import subprocess
import sys
from pathlib import Path


def run(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, check=False, capture_output=True, text=True)


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def ratio(value: str) -> float:
    numerator, denominator = value.split("/", 1)
    return float(numerator) / float(denominator) if float(denominator) else 0.0


def probe(video: Path) -> dict:
    result = run([
        "ffprobe", "-v", "error", "-show_entries",
        "format=duration:format_tags:stream=index,codec_type,codec_name,width,height,r_frame_rate,sample_rate,channels",
        "-of", "json", str(video),
    ])
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "ffprobe failed")
    return json.loads(result.stdout)


def audio_metrics(video: Path) -> dict:
    result = run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(video), "-filter_complex", "ebur128=peak=true", "-f", "null", "-"])
    integrated = re.findall(r"I:\s+(-?\d+(?:\.\d+)?) LUFS", result.stderr)
    lra = re.findall(r"LRA:\s+(\d+(?:\.\d+)?) LU", result.stderr)
    peak = re.findall(r"Peak:\s+(-?\d+(?:\.\d+)?) dBFS", result.stderr)
    return {
        "integrated_lufs": float(integrated[-1]) if integrated else None,
        "lra_lu": float(lra[-1]) if lra else None,
        "true_peak_dbfs": float(peak[-1]) if peak else None,
    }


def detect_events(video: Path, filter_spec: str, pattern: str, video_only: bool) -> list[str]:
    command = ["ffmpeg", "-hide_banner", "-nostats", "-i", str(video)]
    command.extend(["-vf" if video_only else "-af", filter_spec])
    command.extend(["-an" if video_only else "-vn", "-f", "null", "-"])
    return re.findall(pattern, run(command).stderr)


def create_contact_sheet(video: Path, output: Path, width: int, height: int, duration: float, frames: int) -> None:
    columns = 6
    rows = math.ceil(frames / columns)
    cell_width, cell_height = (320, 180) if width > height else (180, 320)
    fps = frames / max(duration, 0.001)
    vf = (
        f"fps={fps:.8f},"
        f"scale={cell_width}:{cell_height}:force_original_aspect_ratio=decrease,"
        f"pad={cell_width}:{cell_height}:(ow-iw)/2:(oh-ih)/2:color=black,"
        f"tile={columns}x{rows}:nb_frames={frames}"
    )
    result = run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", str(video), "-vf", vf, "-frames:v", "1", "-update", "1", str(output)])
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "contact sheet generation failed")


def loudness_status(value: float) -> str:
    if not -19.0 <= value <= -14.0:
        return "fail"
    return "pass" if abs(value - (-16.5)) <= 1.5 else "warn"


def true_peak_status(value: float) -> str:
    return "pass" if value <= -1.0 else "fail"


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a horizontal or vertical promotional video and create a contact sheet.")
    parser.add_argument("video", type=Path)
    parser.add_argument("--orientation", choices=("auto", "landscape", "portrait"), default="auto")
    parser.add_argument("--expected-duration", type=float)
    parser.add_argument("--duration-tolerance", type=float, default=0.08)
    parser.add_argument("--max-duration", type=float, default=180.0)
    parser.add_argument("--frames", type=int, default=24)
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--narration-contract", type=Path, help="旁白契约，用于校验最终视频使用了确认的音频")
    parser.add_argument("--require-narration-binding", action="store_true", help="旁白绑定缺失或不一致时失败")
    parser.add_argument("--narration-tolerance", type=float, default=0.75, help="旁白与视频时长允许误差，单位秒")
    args = parser.parse_args()

    if not args.video.is_file():
        parser.error(f"video not found: {args.video}")
    if args.frames < 6 or args.frames > 60:
        parser.error("--frames must be between 6 and 60")
    if args.expected_duration is not None and args.expected_duration <= 0:
        parser.error("--expected-duration must be greater than 0")
    if args.max_duration <= 0:
        parser.error("--max-duration must be greater than 0")
    if args.require_narration_binding and not args.narration_contract:
        parser.error("--require-narration-binding 必须同时提供 --narration-contract")
    if args.narration_tolerance < 0:
        parser.error("--narration-tolerance 不能小于 0")
    for binary in ("ffmpeg", "ffprobe"):
        if shutil.which(binary) is None:
            parser.error(f"required binary not found: {binary}")

    data = probe(args.video)
    video_streams = [stream for stream in data.get("streams", []) if stream.get("codec_type") == "video"]
    audio_streams = [stream for stream in data.get("streams", []) if stream.get("codec_type") == "audio"]
    if not video_streams:
        parser.error("video stream missing")
    video_stream = video_streams[0]
    audio_stream = audio_streams[0] if audio_streams else {}
    width = int(video_stream.get("width", 0))
    height = int(video_stream.get("height", 0))
    duration = float(data.get("format", {}).get("duration", 0))
    fps = ratio(video_stream.get("r_frame_rate", "0/1"))
    inferred = "landscape" if width > height else "portrait" if height > width else "square"
    expected_orientation = inferred if args.orientation == "auto" else args.orientation
    expected_ratio = 16 / 9 if expected_orientation == "landscape" else 3 / 4
    actual_ratio = width / height if height else 0
    checks: list[dict] = []

    def add(name: str, status: str, detail: str) -> None:
        checks.append({"name": name, "status": status, "detail": detail})

    add("orientation", "pass" if inferred == expected_orientation else "fail", f"expected={expected_orientation}, actual={inferred}")
    add("aspect_ratio", "pass" if abs(actual_ratio - expected_ratio) <= 0.02 else "fail", f"{width}x{height}, ratio={actual_ratio:.5f}")
    if args.expected_duration is not None:
        add("duration_target", "pass" if abs(duration - args.expected_duration) <= args.duration_tolerance else "fail", f"actual={duration:.3f}s, expected={args.expected_duration:.3f}s")
    add("duration_max", "pass" if duration <= args.max_duration + 0.001 else "fail", f"actual={duration:.3f}s, max={args.max_duration:.3f}s")
    add("video_codec", "pass" if video_stream.get("codec_name") == "h264" else "warn", str(video_stream.get("codec_name")))
    add("frame_rate", "pass" if 24 <= fps <= 60 else "fail", f"{fps:.3f} fps")
    add("audio_stream", "pass" if audio_streams else "fail", "present" if audio_streams else "missing")
    if audio_streams:
        add("audio_codec", "pass" if audio_stream.get("codec_name") == "aac" else "warn", str(audio_stream.get("codec_name")))
        add("sample_rate", "pass" if int(audio_stream.get("sample_rate", 0)) == 48000 else "warn", str(audio_stream.get("sample_rate")))
        add("channels", "pass" if int(audio_stream.get("channels", 0)) == 2 else "warn", str(audio_stream.get("channels")))

    metrics = audio_metrics(args.video) if audio_streams else {}
    loudness = metrics.get("integrated_lufs")
    peak = metrics.get("true_peak_dbfs")
    if loudness is not None:
        add("integrated_loudness", loudness_status(loudness), f"{loudness:.1f} LUFS; target -16.5 LUFS")
    if peak is not None:
        add("true_peak", true_peak_status(peak), f"{peak:.1f} dBFS; target <= -1.0 dBFS")

    black_events = detect_events(args.video, "blackdetect=d=0.35:pix_th=0.025", r"black_start:([^\s]+)", True)
    silence_events = detect_events(args.video, "silencedetect=n=-48dB:d=0.35", r"silence_start:\s*([^\s]+)", False) if audio_streams else []
    add("black_frames", "warn" if black_events else "pass", f"events={black_events}")
    add("mix_silence", "warn" if silence_events else "pass", f"events={silence_events}")

    narration_report: dict = {}
    if args.narration_contract:
        contract_path = args.narration_contract.expanduser().resolve()
        try:
            contract = json.loads(contract_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            parser.error(f"旁白契约无法读取：{contract_path}")
        audio_value = contract.get("audio_path", "") if isinstance(contract, dict) else ""
        source_audio = Path(str(audio_value)).expanduser() if audio_value else None
        if source_audio and not source_audio.is_absolute():
            source_audio = contract_path.parent / source_audio
        source_audio = source_audio.resolve() if source_audio else None
        binding_status = "pass"
        if source_audio is None or not source_audio.is_file():
            binding_status = "fail"
            add("narration_source_audio", "fail", "旁白契约缺少可读取的 audio_path")
        else:
            actual_sha = file_sha256(source_audio)
            expected_sha = str(contract.get("audio_sha256", "")).strip()
            if actual_sha.casefold() != expected_sha.casefold():
                binding_status = "fail"
                add("narration_audio_sha256", "fail", "旁白契约 SHA-256 与音频文件不一致")
            else:
                add("narration_audio_sha256", "pass", actual_sha)
            try:
                source_duration = float(probe(source_audio).get("format", {}).get("duration", 0))
            except (RuntimeError, TypeError, ValueError, json.JSONDecodeError):
                binding_status = "fail"
                add("narration_source_probe", "fail", "无法读取旁白源文件的实际时长")
            else:
                contract_duration = float(contract.get("duration_seconds", 0))
                if abs(source_duration - contract_duration) > 0.05:
                    binding_status = "fail"
                    add("narration_contract_duration", "fail", f"contract={contract_duration:.3f}s, source={source_duration:.3f}s")
                else:
                    add("narration_contract_duration", "pass", f"{source_duration:.3f}s")
                if abs(duration - source_duration) > args.narration_tolerance:
                    binding_status = "fail"
                    add("video_narration_duration", "fail", f"video={duration:.3f}s, narration={source_duration:.3f}s")
                else:
                    add("video_narration_duration", "pass", f"video={duration:.3f}s, narration={source_duration:.3f}s")
            narration_report = {
                "contract": str(contract_path),
                "source_audio": str(source_audio),
                "status": binding_status,
            }

    output_dir = args.output_dir or args.video.parent / f"{args.video.stem}_qa"
    output_dir.mkdir(parents=True, exist_ok=True)
    contact_sheet = output_dir / "contact-sheet.png"
    report_path = output_dir / "preflight.json"
    create_contact_sheet(args.video, contact_sheet, width, height, duration, args.frames)
    report = {
        "video": str(args.video.resolve()),
        "orientation": inferred,
        "technical": {"width": width, "height": height, "fps": fps, "duration_seconds": duration},
        "audio": metrics,
        "narration": narration_report,
        "checks": checks,
        "contact_sheet": str(contact_sheet.resolve()),
        "manual_checks_required": [
            "large unassigned blank areas",
            "old dates and timestamps",
            "private or unauthorized information",
            "unwanted English or legacy UI",
            "cropped subjects, captions, and logos",
            "story continuity and meaningful motion",
        ],
    }
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    for check in checks:
        print(f"[{check['status'].upper()}] {check['name']}: {check['detail']}")
    print(f"contact_sheet={contact_sheet}")
    print(f"report={report_path}")
    return 1 if any(check["status"] == "fail" for check in checks) else 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Read-only environment doctor for Produce Videos."""

from __future__ import annotations

import argparse
import json
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

from discover_audio_models import default_roots, discover


def command_version(name: str, args: list[str]) -> dict[str, Any]:
    path = shutil.which(name)
    if not path:
        return {"available": False, "path": "", "version": ""}
    try:
        completed = subprocess.run([path, *args], capture_output=True, text=True, timeout=8, check=False)
        output = (completed.stdout or completed.stderr).splitlines()
        version = output[0].strip()[:240] if output else "unknown"
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {"available": False, "path": path, "version": "", "error": str(exc)}
    return {"available": completed.returncode == 0, "path": path, "version": version}


def module_available(runtime_python: str, name: str) -> bool:
    try:
        completed = subprocess.run(
            [runtime_python, "-c", "import importlib.util,sys; sys.exit(0 if importlib.util.find_spec(sys.argv[1]) else 1)", name],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
        return completed.returncode == 0
    except (OSError, subprocess.TimeoutExpired):
        return False


def python_runtime() -> dict[str, Any]:
    candidates: list[str] = [sys.executable]
    for name in ("python3.13", "python3.12", "python3.11", "python3.10", "python3"):
        found = shutil.which(name)
        if found and found not in candidates:
            candidates.append(found)
    checked: list[dict[str, Any]] = []
    for path in candidates:
        try:
            completed = subprocess.run(
                [path, "-c", "import json,sys; print(json.dumps(list(sys.version_info[:3])))"],
                capture_output=True, text=True, timeout=5, check=False,
            )
            version_parts = json.loads(completed.stdout.strip()) if completed.returncode == 0 else []
        except (OSError, subprocess.TimeoutExpired, json.JSONDecodeError):
            version_parts = []
        valid = isinstance(version_parts, list) and len(version_parts) == 3
        checked.append({
            "path": path,
            "version": ".".join(str(part) for part in version_parts) if valid else "unknown",
            "compatible": valid and tuple(version_parts) >= (3, 10, 0),
        })
    compatible = next((item for item in checked if item["compatible"]), None)
    return {
        "available": compatible is not None,
        "path": compatible["path"] if compatible else sys.executable,
        "version": compatible["version"] if compatible else platform.python_version(),
        "candidates": checked,
    }


def cjk_fonts() -> list[str]:
    candidates = {
        "PingFang SC": ["/System/Library/Fonts/PingFang.ttc"],
        "Hiragino Sans GB": ["/System/Library/Fonts/Hiragino Sans GB.ttc"],
        "Microsoft YaHei": ["/Library/Fonts/Microsoft Yahei.ttf"],
        "Noto Sans CJK": ["/Library/Fonts/NotoSansCJK-Regular.ttc", "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"],
    }
    return [name for name, paths in candidates.items() if any(Path(path).is_file() for path in paths)]


def build_report(scan_models: bool, search_roots: list[Path]) -> dict[str, Any]:
    python_report = python_runtime()
    python_ok = python_report["available"]
    commands = {
        "ffmpeg": command_version("ffmpeg", ["-version"]),
        "ffprobe": command_version("ffprobe", ["-version"]),
        "node": command_version("node", ["--version"]),
        "npm": command_version("npm", ["--version"]),
        "npx": command_version("npx", ["--version"]),
    }
    fonts = cjk_fonts()
    compatible_pythons = [item["path"] for item in python_report["candidates"] if item["compatible"]]
    stt_modules = {
        "mlx-whisper": "mlx_whisper",
        "faster-whisper": "faster_whisper",
        "openai-whisper": "whisper",
    }
    stt_runtimes = {
        backend: [runtime for runtime in compatible_pythons if module_available(runtime, module)]
        for backend, module in stt_modules.items()
    }
    if shutil.which("whisper") is not None and not stt_runtimes["openai-whisper"]:
        stt_runtimes["openai-whisper"] = [shutil.which("whisper")]
    stt = {backend: bool(runtimes) for backend, runtimes in stt_runtimes.items()}
    tts_api = {
        name: bool(os.environ.get(name, "").strip())
        for name in ("DASHSCOPE_API_KEY", "ELEVENLABS_API_KEY", "OPENAI_API_KEY")
    }
    model_report: dict[str, Any] = {
        "status": "not-scanned",
        "next_action": "run doctor.py without --skip-model-scan or provide --model-root",
    }
    if scan_models:
        roots = search_roots or default_roots()
        model_report = discover(roots, max_depth=6, max_directories=5000)
    core_ready = python_ok and commands["ffmpeg"]["available"] and commands["ffprobe"]["available"]
    remotion_ready = commands["node"]["available"] and commands["npm"]["available"] and commands["npx"]["available"]
    return {
        "schema_version": "1.0",
        "read_only": True,
        "system": {"platform": platform.platform(), "machine": platform.machine()},
        "python": python_report,
        "commands": commands,
        "fonts": {"available": bool(fonts), "detected_cjk_families": fonts},
        "stt": {
            "available_backends": [name for name, available in stt.items() if available],
            "checks": stt,
            "runtime_pythons": stt_runtimes,
        },
        "tts_api": {"configured_names": [name for name, configured in tts_api.items() if configured], "checks": tts_api},
        "local_tts": model_report,
        "capabilities": {
            "core_video_tools": core_ready,
            "remotion_runtime": remotion_ready,
            "local_stt_runtime": any(stt.values()),
            "local_tts_model": model_report.get("status") == "compatible-found",
        },
        "ready_for_core_workflow": core_ready,
        "notes": [
            "缺少可选 STT、TTS 或 Remotion 不等于核心检查失败；只影响对应路线。",
            "doctor 不安装依赖、不下载模型、不打印密钥值。",
        ],
    }


def print_human(report: dict[str, Any]) -> None:
    print("PASS" if report["ready_for_core_workflow"] else "FAIL", "核心视频环境")
    print(f"Python {report['python']['version']}: {'可用' if report['python']['available'] else '需要 3.10+'}")
    for name, item in report["commands"].items():
        print(f"{name}: {'可用' if item['available'] else '缺失'} {item.get('version', '')}")
    print("中文字体:", "、".join(report["fonts"]["detected_cjk_families"]) or "未发现常用中文字体")
    print("本地 STT:", "、".join(report["stt"]["available_backends"]) or "未发现")
    print("TTS API:", "、".join(report["tts_api"]["configured_names"]) or "未配置（只报告变量名，不显示值）")
    local = report["local_tts"]
    print("本地 TTS:", local.get("status", "unknown"))
    if local.get("qwen_recommendation"):
        recommendation = local["qwen_recommendation"]
        print(f"下一步可选 Qwen3-TTS：{recommendation['model_url']}，约 {recommendation['approx_size_gb']} GB；下载前需授权")


def main() -> int:
    parser = argparse.ArgumentParser(description="只读检查 Python、FFmpeg、渲染、字体、STT、TTS API 和本地 Qwen")
    parser.add_argument("--json", action="store_true", help="输出 JSON")
    parser.add_argument("--skip-model-scan", action="store_true", help="跳过有限的本地 TTS 模型扫描")
    parser.add_argument("--model-root", action="append", type=Path, default=[], help="追加允许检查的模型目录")
    args = parser.parse_args()
    report = build_report(not args.skip_model_scan, args.model_root)
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print_human(report)
    return 0 if report["ready_for_core_workflow"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

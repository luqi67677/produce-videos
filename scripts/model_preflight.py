#!/usr/bin/env python3
"""预检 Qwen3-TTS 运行时、设备、模型目录和最小加载。"""

from __future__ import annotations

import argparse
import importlib.metadata
import json
import platform
import shutil
import sys
from pathlib import Path
from urllib.parse import urlparse

from audio_runtime import relaunch_with_runtime


WEIGHT_SUFFIXES = (".safetensors", ".npz", ".bin", ".gguf", ".msgpack")
TOKENIZER_FILES = ("tokenizer.json", "tokenizer_config.json", "vocab.json")


def build_report(args: argparse.Namespace) -> tuple[dict, list[str], list[str]]:
    model_path = args.model_path.expanduser().resolve()
    report = {
        "schema_version": "1.1",
        "runtime": args.runtime,
        "python_executable": sys.executable,
        "python_version": platform.python_version(),
        "platform": platform.system(),
        "machine": platform.machine(),
        "model_path": str(model_path),
        "model_id": args.model_id or "",
        "model_url": args.model_url or "",
        "checks": {},
    }
    errors: list[str] = []
    warnings: list[str] = []

    report["checks"]["platform"] = "pass"
    if args.runtime == "mlx-audio":
        if platform.system() != "Darwin" or platform.machine().casefold() not in {"arm64", "aarch64"}:
            errors.append("当前 MLX 路线只支持 Apple Silicon / arm64；请改用兼容的其他 TTS，或在 Apple Silicon 上运行")
            report["checks"]["platform"] = "fail"

        try:
            import mlx_audio  # noqa: F401
        except ImportError:
            errors.append("当前 Python 未找到 mlx_audio；这不代表电脑上没有兼容环境。请先运行 discover_audio_models.py 查找已有运行环境，仍未找到后再申请安装授权")
            report["checks"]["mlx_audio"] = "fail"
        else:
            report["checks"]["mlx_audio"] = "pass"
            try:
                report["mlx_audio_version"] = importlib.metadata.version("mlx-audio")
            except importlib.metadata.PackageNotFoundError:
                report["mlx_audio_version"] = "unknown"

    if not model_path.is_dir():
        errors.append(f"模型目录不存在：{model_path}")
        report["checks"]["model_directory"] = "fail"
    else:
        report["checks"]["model_directory"] = "pass"
        files = {path.name for path in model_path.iterdir() if path.is_file()}
        has_config = "config.json" in files
        has_weights = any(path.suffix.casefold() in WEIGHT_SUFFIXES for path in model_path.iterdir() if path.is_file())
        has_tokenizer = any(name in files for name in TOKENIZER_FILES)
        report["checks"]["config"] = "pass" if has_config else "fail"
        report["checks"]["weights"] = "pass" if has_weights else "fail"
        report["checks"]["tokenizer"] = "pass" if has_tokenizer else "fail"
        if not has_config:
            errors.append("模型目录缺少 config.json，可能不是完整模型目录")
        if not has_weights:
            errors.append("模型目录未找到权重文件（safetensors、npz、bin、gguf 或 msgpack）")
        if not has_tokenizer:
            errors.append("模型目录缺少 Tokenizer 文件")

        free_gb = shutil.disk_usage(model_path).free / (1024**3)
        report["free_disk_gb"] = round(free_gb, 2)
        if free_gb < args.minimum_free_gb:
            warnings.append(f"模型目录所在磁盘剩余空间约 {free_gb:.2f} GB，低于建议值 {args.minimum_free_gb:.2f} GB")

    if args.model_url:
        parsed = urlparse(args.model_url)
        if parsed.scheme != "https" or not parsed.netloc:
            errors.append("model_url 必须是完整的 HTTPS 地址")
            report["checks"]["model_url"] = "fail"
        else:
            report["checks"]["model_url"] = "pass"

    if args.smoke_test and args.runtime != "mlx-audio":
        errors.append("当前 --smoke-test 只实现 mlx-audio；其他运行时必须由其自身适配器验证")
        report["checks"]["smoke_test"] = "fail"
    elif args.smoke_test and not errors:
        try:
            from mlx_audio.tts.utils import load_model

            load_model(model_path)
        except Exception as exc:  # pragma: no cover - requires a real model/runtime
            errors.append(f"模型最小加载失败：{exc}")
            report["checks"]["smoke_test"] = "fail"
        else:
            report["checks"]["smoke_test"] = "pass"
    elif args.smoke_test:
        report["checks"]["smoke_test"] = "skipped"

    report["status"] = "fail" if errors else "pass"
    report["errors"] = errors
    report["warnings"] = warnings
    return report, errors, warnings


def main() -> int:
    parser = argparse.ArgumentParser(description="预检 Qwen3-TTS 模型与运行时，不执行下载")
    parser.add_argument("--model-path", type=Path, required=True, help="模型目录")
    parser.add_argument("--runtime", choices=("mlx-audio", "qwen-tts", "other"), default="mlx-audio")
    parser.add_argument("--runtime-python", type=Path, help="使用发现报告列出的兼容 Python 运行环境")
    parser.add_argument("--model-id", help="旁白契约中的模型 ID")
    parser.add_argument("--model-url", help="旁白契约中的模型地址")
    parser.add_argument("--minimum-free-gb", type=float, default=5.0)
    parser.add_argument("--smoke-test", action="store_true", help="加载模型做最小运行时测试")
    parser.add_argument("--output", type=Path, help="写入 JSON 预检报告")
    args = parser.parse_args()
    try:
        relaunch_with_runtime(args.runtime_python)
    except ValueError as exc:
        parser.error(str(exc))
    if args.minimum_free_gb < 0:
        parser.error("--minimum-free-gb 不能小于 0")

    report, errors, warnings = build_report(args)
    if args.output:
        output = args.output.expanduser().resolve()
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for warning in warnings:
        print(f"WARN {warning}")
    if errors:
        for error in errors:
            print(f"FAIL {error}", file=sys.stderr)
        return 1
    print("PASS 模型预检通过：设备、运行时、模型目录和必需文件有效")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

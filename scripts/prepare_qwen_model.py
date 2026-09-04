#!/usr/bin/env python3
"""读取 Qwen 单一模型配置；仅在明确授权参数存在时下载。"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path


def load_models() -> dict:
    path = Path(__file__).resolve().parents[1] / "assets" / "qwen-tts-models.json"
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    models = load_models()
    parser = argparse.ArgumentParser(description="准备 Qwen3-TTS 模型；默认只展示地址，不执行下载")
    parser.add_argument("--model-key", choices=("recommended", "smaller_option"), default="recommended")
    parser.add_argument("--model-dir", type=Path, required=True, help="模型下载目录，不得位于 Skill 包内")
    parser.add_argument("--download", action="store_true", help="执行下载；必须同时提供 --download-authorized")
    parser.add_argument("--download-authorized", action="store_true", help="表示用户已明确授权下载")
    args = parser.parse_args()
    if args.download and not args.download_authorized:
        parser.error("下载前必须取得用户明确授权：请同时提供 --download-authorized")
    if args.download_authorized and not args.download:
        parser.error("--download-authorized 只能和 --download 一起使用")

    config = models[args.model_key]
    model_dir = args.model_dir.expanduser().resolve()
    skill_root = Path(__file__).resolve().parents[1]
    if model_dir == skill_root or skill_root in model_dir.parents:
        parser.error("模型不得下载到 Skill 包内，请指定外部模型目录")

    print(f"model_id={config['model_id']}")
    print(f"model_url={config['model_url']}")
    print(f"download_command={config['download_command']}")
    print(f"target={model_dir}")
    if not args.download:
        print("未执行下载：等待用户明确授权")
        return 0

    cli = shutil.which("huggingface-cli")
    if cli is None:
        print(
            "未找到 huggingface-cli，请先执行："
            f" {models['dependency_install_command']}",
            file=sys.stderr,
        )
        return 1

    model_dir.mkdir(parents=True, exist_ok=True)
    command = [cli, "download", config["model_id"], "--local-dir", str(model_dir)]
    completed = subprocess.run(command, check=False)
    if completed.returncode != 0:
        print("Qwen3-TTS 模型下载失败，请检查网络、磁盘空间和 Hugging Face 权限", file=sys.stderr)
        return completed.returncode
    print("PASS Qwen3-TTS 模型下载完成；请继续运行 model_preflight.py --smoke-test")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

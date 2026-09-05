from __future__ import annotations

import json
import os
import stat
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from audio_runtime import absolute_path  # noqa: E402
from discover_audio_models import discover, load_qwen_models  # noqa: E402


class AudioRuntimeDetectionTests(unittest.TestCase):
    def test_qwen_fallback_uses_public_model_config(self) -> None:
        models = load_qwen_models()

        self.assertEqual(models["official_project_url"], "https://github.com/QwenLM/Qwen3-TTS")
        self.assertEqual(
            models["upstream_model"]["model_url"],
            "https://huggingface.co/Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign",
        )
        self.assertEqual(
            models["recommended"]["model_url"],
            "https://huggingface.co/mlx-community/Qwen3-TTS-12Hz-1.7B-VoiceDesign-bf16",
        )
        self.assertEqual(models["recommended"]["approx_size_gb"], 4.52)

    def test_no_local_model_returns_actionable_qwen_recommendation(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            qwen_models = {
                "provider": "Alibaba Qwen3-TTS",
                "runtime": "mlx-audio",
                "supported_platform": "Apple Silicon / arm64",
                "dependency_install_command": "python -m pip install mlx-audio",
                "recommended": {
                    "model_id": "qwen/recommended",
                    "model_url": "https://example.com/qwen-recommended",
                    "approx_size_gb": 4.52,
                },
                "smaller_option": {
                    "model_id": "qwen/smaller",
                    "model_url": "https://example.com/qwen-smaller",
                    "approx_size_gb": 2.5,
                },
            }

            report = discover(
                [Path(temp_dir) / "empty-models"],
                max_depth=3,
                max_directories=100,
                qwen_models=qwen_models,
            )

            self.assertEqual(report["status"], "none-found")
            self.assertEqual(report["next_action"], "recommend-qwen-and-request-download-authorization")
            recommendation = report["qwen_recommendation"]
            self.assertEqual(recommendation["model_url"], "https://example.com/qwen-recommended")
            self.assertEqual(recommendation["approx_size_gb"], 4.52)
            self.assertTrue(recommendation["download_requires_user_authorization"])

    def test_discovers_compatible_runtime_next_to_model_root(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            models = root / "models"
            model = models / "Qwen3-TTS-VoiceDesign"
            model.mkdir(parents=True)
            (model / "config.json").write_text(json.dumps({"model_type": "qwen3_tts"}), encoding="utf-8")
            (model / "tokenizer.json").write_text("{}", encoding="utf-8")
            (model / "weights.safetensors").write_bytes(b"test")

            runtime = root / "qwen-env/bin/python"
            runtime.parent.mkdir(parents=True)
            runtime.write_text(
                "#!/bin/sh\n"
                "printf '%s\\n' '__QWEN_RUNTIME_JSON__{\"python_executable\":\"fake\",\"python_version\":\"3.12.0\",\"mlx_audio_version\":\"0.5.0\"}'\n",
                encoding="utf-8",
            )
            runtime.chmod(runtime.stat().st_mode | stat.S_IXUSR)

            report = discover([models], max_depth=3, max_directories=100)

            self.assertEqual(report["status"], "compatible-found")
            self.assertEqual(report["runtime_status"], "compatible-runtime-found")
            self.assertEqual(report["recommended_runtime_python"], str(runtime))

    def test_runtime_path_keeps_virtualenv_entry_instead_of_resolving_symlink(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            link = Path(temp_dir) / "env/bin/python"
            link.parent.mkdir(parents=True)
            os.symlink(sys.executable, link)

            self.assertEqual(absolute_path(link), link)

    def test_prepare_qwen_dry_run_explains_install_and_authorization(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            target = Path(temp_dir) / "qwen-model"
            completed = subprocess.run(
                [sys.executable, str(SCRIPTS / "prepare_qwen_model.py"), "--model-dir", str(target)],
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(completed.returncode, 0)
            self.assertIn("model_url=https://huggingface.co/mlx-community/Qwen3-TTS", completed.stdout)
            self.assertIn("official_project_url=https://github.com/QwenLM/Qwen3-TTS", completed.stdout)
            self.assertIn("approx_size_gb=4.52", completed.stdout)
            self.assertIn("dependency_install_command=", completed.stdout)
            self.assertIn("download_requires_user_authorization=true", completed.stdout)
            self.assertFalse(target.exists())

    def test_prepare_qwen_blocks_download_without_user_authorization(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            target = Path(temp_dir) / "qwen-model"
            completed = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPTS / "prepare_qwen_model.py"),
                    "--model-dir",
                    str(target),
                    "--download",
                ],
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertNotEqual(completed.returncode, 0)
            self.assertIn("下载前必须取得用户明确授权", completed.stderr)
            self.assertFalse(target.exists())


if __name__ == "__main__":
    unittest.main()

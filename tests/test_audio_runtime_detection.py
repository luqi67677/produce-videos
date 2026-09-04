from __future__ import annotations

import json
import os
import stat
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from audio_runtime import absolute_path  # noqa: E402
from discover_audio_models import discover  # noqa: E402


class AudioRuntimeDetectionTests(unittest.TestCase):
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


if __name__ == "__main__":
    unittest.main()

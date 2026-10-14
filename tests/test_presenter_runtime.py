from __future__ import annotations

import contextlib
import hashlib
import io
import json
import math
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import wave

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import load_local_voice_default as voice_default
from build_presenter_motion import build_motion


def write_pcm(path: Path, width: int, voiced: bool) -> None:
    rate = 24000
    raw = bytearray()
    for i in range(rate * 2):
        t = i / rate
        value = 0.12 * math.sin(2 * math.pi * 220 * t) if voiced and 0.25 <= t < 1.5 else 0.0
        if width == 1:
            raw.append(round(value * 127) + 128)
        else:
            raw.extend(round(value * ((1 << (8 * width - 1)) - 1)).to_bytes(width, "little", signed=True))
    with wave.open(str(path), "wb") as audio:
        audio.setnchannels(1)
        audio.setsampwidth(width)
        audio.setframerate(rate)
        audio.writeframes(raw)


class PresenterRuntimeTests(unittest.TestCase):
    def test_silence_keeps_mouth_closed_for_supported_pcm_widths(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            for width in (1, 2, 3, 4):
                with self.subTest(width=width):
                    audio = Path(tmp) / f"silence-{width}.wav"
                    write_pcm(audio, width, False)
                    track = build_motion(audio, fps=30, seed=12)
                    self.assertEqual(track["frame_count"], 60)
                    self.assertTrue(all(f["mouth_openness"] == 0 for f in track["frames"]))
                    self.assertFalse(track["phoneme_level_lip_sync"])

    def test_voice_opens_mouth_then_pause_closes_it_and_binds_source(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            for width in (1, 2, 3, 4):
                with self.subTest(width=width):
                    audio = Path(tmp) / f"voice-{width}.wav"
                    write_pcm(audio, width, True)
                    track = build_motion(audio, fps=30, seed=12, start=0.25, duration=2)
                    self.assertAlmostEqual(track["source_offset_seconds"], 0.25)
                    self.assertAlmostEqual(track["duration_seconds"], 1.75)
                    self.assertEqual(track["frame_count"], 53)
                    self.assertGreater(max(f["mouth_openness"] for f in track["frames"]), 0.5)
                    self.assertTrue(all(f["mouth_openness"] == 0 for f in track["frames"] if f["time"] > 1.3))
                    self.assertEqual(track["source_audio_sha256"], hashlib.sha256(audio.read_bytes()).hexdigest())
                    self.assertEqual(track["frames"], build_motion(audio, fps=30, seed=12, start=0.25, duration=2)["frames"])

    def test_empty_or_out_of_range_motion_window_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            audio = Path(tmp) / "voice.wav"
            write_pcm(audio, 2, True)
            for options in ({"start": 2.0}, {"start": -1.0}, {"duration": 0.0}, {"fps": float("nan")}):
                with self.subTest(options=options), self.assertRaises(ValueError):
                    build_motion(audio, **options)

    def test_unbound_json_output_is_preserved_even_without_config_hash(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            config = Path(tmp) / "config.json"
            output = Path(tmp) / "record.json"
            config.write_text("{}")
            original = '{"unrelated": true}\n'
            output.write_text(original)
            result = {"status": "not-configured", "config_path": str(config)}
            with patch.object(sys, "argv", ["loader", "--config", str(config), "--output", str(output)]), patch.object(voice_default, "load_default", return_value=result), contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(voice_default.main(), 1)
            self.assertEqual(output.read_text(), original)

    def test_output_cannot_replace_voice_config(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            config = Path(tmp) / "config.json"
            config.write_text("{}")
            result = {"status": "not-configured", "config_path": str(config)}
            with patch.object(sys, "argv", ["loader", "--config", str(config), "--output", str(config)]), patch.object(voice_default, "load_default", return_value=result), contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(voice_default.main(), 1)
            self.assertEqual(config.read_text(), "{}")

    @unittest.skipUnless(shutil.which("node"), "Node is not available")
    def test_renderer_rejects_non_mp4_before_loading_canvas(self) -> None:
        result = subprocess.run([shutil.which("node"), str(ROOT / "scripts/render_presenter_demo.cjs"), "--profile", "missing.json", "--motion", "missing.json", "--output", "demo.mov"], capture_output=True, text=True, timeout=10)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("--output 必须使用 .mp4", result.stderr)


if __name__ == "__main__":
    unittest.main()

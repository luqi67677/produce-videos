from __future__ import annotations

import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from build_beat_grid import grid  # noqa: E402
from export_fcpxml import build_fcpxml  # noqa: E402
from snap_edl_to_beats import snap  # noqa: E402
from transcribe_media import build_output  # noqa: E402


def edl(source: Path) -> dict:
    return {
        "schema_version": "1.0",
        "project": "Test",
        "format": {"width": 1920, "height": 1080, "fps": 30},
        "picture_track": [
            {"clip_id": "c01", "scene_id": "s01", "source_path": str(source), "source_in_seconds": 0, "timeline_start_seconds": 0, "duration_seconds": 1.03, "roll_type": "a-roll", "covers": "hook", "cut_locked": False},
            {"clip_id": "c02", "scene_id": "s02", "source_path": str(source), "source_in_seconds": 1.03, "timeline_start_seconds": 1.03, "duration_seconds": 0.97, "roll_type": "b-roll", "covers": "proof", "cut_locked": False},
        ],
        "transitions": [{"at_seconds": 1.03, "type": "hard-cut", "reason": "proof"}],
    }


class EditingToolsTests(unittest.TestCase):
    def test_manual_grid_is_frame_independent(self) -> None:
        beats, downbeats = grid(120, 0, 2)
        self.assertEqual(beats, [0, 0.5, 1.0, 1.5, 2.0])
        self.assertEqual(downbeats, [0, 2.0])

    def test_snap_moves_cut_without_changing_total_duration(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            source = Path(temp_dir) / "source.mp4"
            source.write_bytes(b"demo")
            result = snap(edl(source), {"beats": [0, 0.5, 1.0, 1.5, 2.0], "method": "manual-bpm", "confidence": "declared"}, [], 0.12, 0.6)
            self.assertEqual(result["picture_track"][0]["duration_seconds"], 1.0)
            self.assertEqual(result["picture_track"][1]["timeline_start_seconds"], 1.0)
            self.assertEqual(result["picture_track"][1]["duration_seconds"], 1.0)

    def test_snap_does_not_cut_inside_word(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            source = Path(temp_dir) / "source.mp4"
            source.write_bytes(b"demo")
            result = snap(edl(source), {"beats": [1.0], "method": "manual-bpm", "confidence": "declared"}, [{"start": 0.95, "end": 1.05}], 0.12, 0.6)
            self.assertEqual(result["picture_track"][0]["duration_seconds"], 1.03)

    def test_transcript_normalizes_word_timestamps(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            source = Path(temp_dir) / "audio.wav"
            source.write_bytes(b"demo")
            result = build_output(source, "mlx-whisper", "local-model", "zh", {"text": "你好", "segments": [{"text": "你好", "start": 0, "end": 0.5, "words": [{"word": "你好", "start": 0.1, "end": 0.4}]}]})
            self.assertEqual(result["words"], [{"text": "你好", "start": 0.1, "end": 0.4}])
            self.assertEqual(result["duration_seconds"], 0.4)

    def test_fcpxml_contains_editable_asset_clips(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            source = Path(temp_dir) / "source.mp4"
            source.write_bytes(b"demo")
            tree = build_fcpxml(edl(source), Path(temp_dir))
            xml = ET.tostring(tree.getroot(), encoding="unicode")
            self.assertIn('version="1.10"', xml)
            self.assertEqual(xml.count("<asset-clip"), 2)
            self.assertIn("b-roll · s02", xml)


if __name__ == "__main__":
    unittest.main()

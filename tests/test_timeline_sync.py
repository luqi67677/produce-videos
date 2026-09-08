from __future__ import annotations

import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from validate_timeline_sync import validate  # noqa: E402


def write_json(path: Path, value: dict) -> None:
    path.write_text(json.dumps(value), encoding="utf-8")


def build_project(root: Path) -> None:
    audio = root / "narration.wav"
    audio.write_bytes(b"audio")
    digest = hashlib.sha256(audio.read_bytes()).hexdigest()
    write_json(root / "narration-contract.json", {"duration_seconds": 2, "audio_path": audio.name})
    write_json(root / "shot-readiness.json", {
        "schema_version": "2.6",
        "shots": [{
            "shot_id": "c01-s01",
            "timeline_start_seconds": 0,
            "timeline_end_seconds": 2,
            "duration_seconds": 2,
            "narration_excerpt": "本地模型",
            "roll_type": "graphic-led",
            "covers": "本地模型",
        }],
    })
    write_json(root / "edit-decision-list.json", {
        "schema_version": "1.1",
        "audio_spine": {"path": audio.name, "sha256": digest, "preserve_duration": True},
        "picture_track": [{
            "scene_id": "c01-s01",
            "timeline_start_seconds": 0,
            "duration_seconds": 2,
            "narration_excerpt": "本地模型",
            "roll_type": "graphic-led",
            "covers": "本地模型",
            "semantic_boundary_verified": True,
        }],
    })


class TimelineSyncTests(unittest.TestCase):
    def test_matching_timeline_passes(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            build_project(root)
            self.assertEqual(validate(root), [])

    def test_unreviewed_boundary_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            build_project(root)
            path = root / "edit-decision-list.json"
            data = json.loads(path.read_text(encoding="utf-8"))
            data["picture_track"][0]["semantic_boundary_verified"] = False
            write_json(path, data)
            self.assertTrue(any("听审" in error for error in validate(root)))

    def test_excerpt_drift_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            build_project(root)
            path = root / "edit-decision-list.json"
            data = json.loads(path.read_text(encoding="utf-8"))
            data["picture_track"][0]["narration_excerpt"] = "下一页"
            write_json(path, data)
            self.assertTrue(any("口播片段" in error for error in validate(root)))

    def test_invalid_time_returns_validation_error(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            build_project(root)
            path = root / "edit-decision-list.json"
            data = json.loads(path.read_text(encoding="utf-8"))
            data["picture_track"][0]["duration_seconds"] = "not-a-number"
            write_json(path, data)
            self.assertTrue(any("时间范围无效" in error for error in validate(root)))


if __name__ == "__main__":
    unittest.main()

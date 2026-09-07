from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from validate_motion_coverage import validate  # noqa: E402


def sample(sample_id: str, proof_kind: str, user_required: bool, user_reviewed: bool) -> dict:
    return {
        "sample_id": sample_id,
        "path": f"{sample_id}.mp4",
        "proof_kind": proof_kind,
        "representative": proof_kind == "micro-sample",
        "grammars": ["continuous-flow"],
        "uses_final_audio": True,
        "uses_locked_storyboard": True,
        "single_subtitle_layer": True,
        "watermark_included": False,
        "visual_coverage_verified": True,
        "character_continuity_verified": True,
        "platform_safe": True,
        "machine_reviewed": True,
        "user_review_required": user_required,
        "user_reviewed": user_reviewed,
    }


def write_contract(root: Path, workflow_mode: str, samples: list[dict]) -> Path:
    for item in samples:
        (root / item["path"]).write_bytes(b"video")
    path = root / "motion-coverage.json"
    path.write_text(json.dumps({
        "schema_version": "1.2",
        "workflow_mode": workflow_mode,
        "watermark_required": False,
        "required_grammars": ["continuous-flow"],
        "samples": samples,
    }), encoding="utf-8")
    return path


class MotionCoveragePolicyTests(unittest.TestCase):
    @patch("validate_motion_coverage.probe_video", return_value=None)
    def test_standard_requires_micro_sample_and_full_preview(self, _probe) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            path = write_contract(root, "standard", [sample("full", "full-preview", True, True)])
            self.assertTrue(any("代表性微样片" in error for error in validate(path)))

    @patch("validate_motion_coverage.probe_video", return_value=None)
    def test_high_risk_micro_sample_requires_user_review(self, _probe) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            path = write_contract(root, "high-risk", [
                sample("micro", "micro-sample", False, False),
                sample("full", "full-preview", True, True),
            ])
            self.assertTrue(any("high-risk" in error for error in validate(path)))

    @patch("validate_motion_coverage.probe_video", return_value=None)
    def test_standard_machine_reviewed_micro_and_user_reviewed_full_pass(self, _probe) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            path = write_contract(root, "standard", [
                sample("micro", "micro-sample", False, False),
                sample("full", "full-preview", True, True),
            ])
            self.assertEqual(validate(path), [])


if __name__ == "__main__":
    unittest.main()

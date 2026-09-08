from __future__ import annotations

import hashlib
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


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_v13_contract(
    root: Path,
    *,
    include_audit: bool = True,
    static_shot_ids: list[str] | None = None,
    staged_reveal_failures: list[str] | None = None,
) -> Path:
    samples = [
        sample("micro", "micro-sample", True, True),
        sample("full", "full-preview", True, True),
    ]
    for item in samples:
        (root / item["path"]).write_bytes(b"video")
    timeline = root / "edit-decision-list.json"
    timeline.write_text(json.dumps({
        "picture_track": [
            {"scene_id": "c01-s01", "timeline_start_seconds": 0, "duration_seconds": 2},
            {"scene_id": "c01-s02", "timeline_start_seconds": 2, "duration_seconds": 2},
        ]
    }), encoding="utf-8")
    plan = root / "motion-plan.json"
    plan.write_text(json.dumps({
        "shots": [
            {"shot_id": "c01-s01", "expected_reveal_count": 1},
            {"shot_id": "c01-s02", "expected_reveal_count": 3},
        ]
    }), encoding="utf-8")
    static_ids = static_shot_ids or []
    reveal_failures = staged_reveal_failures or []
    audit = root / "motion-audit.json"
    audit.write_text(json.dumps({
        "schema_version": "1.0",
        "preview_path": "full.mp4",
        "preview_sha256": digest(root / "full.mp4"),
        "timeline_path": timeline.name,
        "timeline_sha256": digest(timeline),
        "motion_plan_path": plan.name,
        "motion_plan_sha256": digest(plan),
        "all_shots_covered": True,
        "covered_shot_ids": ["c01-s01", "c01-s02"],
        "static_shot_ids": static_ids,
        "staged_reveal_failures": reveal_failures,
        "machine_pass": not static_ids and not reveal_failures,
        "shots": [
            {"shot_id": "c01-s01", "expected_reveal_count": 1, "meaningful_update_count": 1},
            {"shot_id": "c01-s02", "expected_reveal_count": 3, "meaningful_update_count": 3},
        ],
    }), encoding="utf-8")
    contract = {
        "schema_version": "1.3",
        "workflow_mode": "high-risk",
        "watermark_required": False,
        "required_grammars": ["continuous-flow"],
        "samples": samples,
    }
    if include_audit:
        contract["full_preview_motion_audit"] = {"path": audit.name}
    path = root / "motion-coverage.json"
    path.write_text(json.dumps(contract), encoding="utf-8")
    return path


def write_v14_contract(
    root: Path,
    *,
    blank_visual_shot_ids: list[str] | None = None,
    timeline_sync_failures: list[str] | None = None,
) -> Path:
    path = write_v13_contract(root)
    contract = json.loads(path.read_text(encoding="utf-8"))
    contract["schema_version"] = "1.4"
    audit_path = root / contract["full_preview_motion_audit"]["path"]
    audit = json.loads(audit_path.read_text(encoding="utf-8"))
    audit["schema_version"] = "1.1"
    audit["blank_visual_shot_ids"] = blank_visual_shot_ids or []
    audit["timeline_sync_failures"] = timeline_sync_failures or []
    audit["blank_policy"] = {
        "minimum_initial_detail_ratio": 0.2,
        "minimum_running_detail_ratio": 0.12,
        "maximum_underfilled_hold_seconds": 0.2,
    }
    audit["machine_pass"] = not any((
        audit["static_shot_ids"],
        audit["staged_reveal_failures"],
        audit["blank_visual_shot_ids"],
        audit["timeline_sync_failures"],
    ))
    audit_path.write_text(json.dumps(audit), encoding="utf-8")
    path.write_text(json.dumps(contract), encoding="utf-8")
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

    @patch("validate_motion_coverage.probe_video", return_value=None)
    def test_v13_requires_full_preview_motion_audit(self, _probe) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = write_v13_contract(Path(temp_dir), include_audit=False)
            self.assertTrue(any("full_preview_motion_audit" in error for error in validate(path)))

    @patch("validate_motion_coverage.probe_video", return_value=None)
    def test_v13_rejects_static_shot_ids(self, _probe) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = write_v13_contract(Path(temp_dir), static_shot_ids=["c01-s01"])
            self.assertTrue(any("静态持有镜头" in error for error in validate(path)))

    @patch("validate_motion_coverage.probe_video", return_value=None)
    def test_v13_complete_audit_passes(self, _probe) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = write_v13_contract(Path(temp_dir))
            self.assertEqual(validate(path), [])

    @patch("validate_motion_coverage.probe_video", return_value=None)
    def test_v14_complete_audit_passes(self, _probe) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = write_v14_contract(Path(temp_dir))
            self.assertEqual(validate(path), [])

    @patch("validate_motion_coverage.probe_video", return_value=None)
    def test_v14_rejects_blank_visual_shots(self, _probe) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = write_v14_contract(Path(temp_dir), blank_visual_shot_ids=["c01-s01"])
            self.assertTrue(any("空白等待" in error for error in validate(path)))

    @patch("validate_motion_coverage.probe_video", return_value=None)
    def test_v14_rejects_timeline_sync_failures(self, _probe) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = write_v14_contract(Path(temp_dir), timeline_sync_failures=["c01-s01 drift"])
            self.assertTrue(any("EDL" in error for error in validate(path)))


if __name__ == "__main__":
    unittest.main()

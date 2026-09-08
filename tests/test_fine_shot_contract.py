from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from validate_shot_readiness import validate_fine_shots  # noqa: E402


def shot(frame: str) -> dict:
    return {
        "shot_id": "c01-s01",
        "narration_segment_id": "s01",
        "timeline_start_seconds": 0,
        "timeline_end_seconds": 2,
        "duration_seconds": 2,
        "narration_excerpt": "把口播拆成镜头",
        "visual_duty": "展示逐句拆镜结果",
        "roll_type": "graphic-led",
        "covers": "",
        "reviewed_frame_path": frame,
        "alignment_verified": True,
        "semantic_boundary": {
            "starts_on_semantic_boundary": True,
            "ends_on_semantic_boundary": True,
            "next_visual_after_narration": True,
        },
        "rendered_text": ["把口播拆成镜头"],
        "production_notes": ["依次出现三个步骤"],
        "text_boundary_review": {
            "production_notes_excluded": True,
            "privacy_treatment_visual_only": True,
            "generic_asset_labels_removed": True,
        },
        "proof": {
            "claim_type": "none",
            "evidence_mode": "not-applicable",
            "evidence_asset_paths": [],
            "complete_context_visible": True,
        },
        "layout_review": {
            "alignment_verified": True,
            "text_overflow_free": True,
            "orphan_line_free": True,
            "brand_case_preserved": True,
            "balanced_density": True,
        },
        "character_ids": [],
        "character_review": {},
    }


class FineShotContractTests(unittest.TestCase):
    def test_valid_fine_shot_passes(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "frame.png").write_bytes(b"frame")
            errors = validate_fine_shots(
                root / "shot-readiness.json",
                [shot("frame.png")],
                {"s01": {"display_text": "把口播拆成镜头。"}},
                2,
                set(),
            )
            self.assertEqual(errors, [])

    def test_production_note_rendered_as_copy_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "frame.png").write_bytes(b"frame")
            item = shot("frame.png")
            item["rendered_text"].append("依次出现三个步骤")
            errors = validate_fine_shots(root / "shot-readiness.json", [item], {}, 2, set())
            self.assertTrue(any("制作说明" in error for error in errors))

    def test_claim_with_empty_placeholder_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "frame.png").write_bytes(b"frame")
            item = shot("frame.png")
            item["proof"] = {
                "claim_type": "quantity",
                "evidence_mode": "text-only",
                "evidence_asset_paths": [],
                "complete_context_visible": False,
            }
            errors = validate_fine_shots(root / "shot-readiness.json", [item], {}, 2, set())
            self.assertTrue(any("空框" in error for error in errors))

    def test_repeated_character_action_requires_reviewed_reason(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            for name in ("one.png", "two.png"):
                (root / name).write_bytes(b"frame")
            first = shot("one.png")
            first["shot_id"] = "c01-s01"
            first["timeline_end_seconds"] = 1
            first["duration_seconds"] = 1
            first["narration_excerpt"] = "把口播"
            second = shot("two.png")
            second["shot_id"] = "c01-s02"
            second["timeline_start_seconds"] = 1
            second["narration_excerpt"] = "拆成镜头"
            second["timeline_end_seconds"] = 2
            second["duration_seconds"] = 1
            for item in (first, second):
                item["character_ids"] = ["character-001"]
                item["character_review"] = {
                    "action": "抬手指向卡片",
                    "action_signature": "stand-point-right",
                    "pose_matches_visual_duty": True,
                    "styling_matches_context": True,
                    "identity_verified": True,
                    "anatomy_safe": True,
                    "reuse_approved": False,
                    "reuse_reason": "",
                }
            errors = validate_fine_shots(
                root / "shot-readiness.json",
                [first, second],
                {"s01": {"display_text": "把口播拆成镜头"}},
                2,
                {"character-001"},
            )
            self.assertTrue(any("重复人物动作" in error for error in errors))


if __name__ == "__main__":
    unittest.main()

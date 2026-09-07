from __future__ import annotations

import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from validate_creative_foundation import (  # noqa: E402
    validate_asset_review_plan,
    validate_character_profile,
    validate_creator_memory,
    validate_platform_profiles,
    validate_story_contract,
)


def write_json(path: Path, data: dict) -> Path:
    path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    return path


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def valid_story() -> dict:
    return {
        "schema_version": "1.0",
        "content_mode": "short-social",
        "opening": {
            "strategy": "result",
            "promise": "让观众先看到完成结果",
            "visible_evidence": "成片首帧",
            "evidence_by_seconds": 1.5,
            "truth_basis": "用户提供的真实成片",
            "conflict_source": "not-required",
        },
        "central_tension": {
            "starting_state": "只有素材",
            "friction": "不会剪辑",
            "key_action": "使用 Skill",
            "evidence": "逐步生成分镜和预览",
            "changed_state": "得到成片",
            "single_main_tension": True,
            "manufactured_conflict": False,
        },
        "throughline": {
            "type": "object",
            "anchor": "同一个视频项目",
            "setup_scene_id": "s01",
            "development_scene_ids": ["s02"],
            "payoff_scene_id": "s03",
        },
        "ending": {
            "resolves_opening": True,
            "result_evidence": "完整成片预览",
            "cta": "试着制作自己的视频",
            "cta_supports_story": True,
        },
        "continuity_checks": {
            "every_scene_advances": True,
            "broll_returns_to_axis": True,
            "opening_and_ending_match": True,
        },
    }


class CreativeFoundationTests(unittest.TestCase):
    def test_truthful_short_social_story_passes(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = write_json(Path(temp_dir) / "story-contract.json", valid_story())
            self.assertEqual(validate_story_contract(path), [])

    def test_short_social_evidence_after_two_seconds_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            story = valid_story()
            story["opening"]["evidence_by_seconds"] = 2.5
            path = write_json(Path(temp_dir) / "story-contract.json", story)
            self.assertTrue(any("0—2" in error for error in validate_story_contract(path)))

    def test_active_memory_requires_future_reuse_confirmation(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            data = {
                "schema_version": "1.0",
                "scope_id": "project-001",
                "storage_scope": "project-only",
                "consent": {
                    "reuse_across_projects": False,
                    "store_relative_asset_references": False,
                    "store_voice_or_person_identity_references": False,
                },
                "preferences": [{
                    "memory_id": "memory-001",
                    "category": "visual",
                    "rule": "保持单一字幕层",
                    "status": "active",
                    "user_confirmed_for_future": False,
                    "evidence": [],
                }],
                "retired_memory_ids": [],
                "updated_at": "2026-09-06T10:00:00+08:00",
            }
            path = write_json(Path(temp_dir) / "creator-memory.json", data)
            self.assertTrue(any("长期复用" in error for error in validate_creator_memory(path)))

    def test_candidate_memory_cannot_be_applied_as_history(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            data = {
                "schema_version": "1.0",
                "scope_id": "project-001",
                "storage_scope": "project-only",
                "consent": {
                    "reuse_across_projects": False,
                    "store_relative_asset_references": False,
                    "store_voice_or_person_identity_references": False,
                },
                "preferences": [{
                    "memory_id": "memory-001",
                    "category": "narrative",
                    "rule": "开头先给结果",
                    "status": "candidate",
                    "user_confirmed_for_future": False,
                    "evidence": [],
                }],
                "retired_memory_ids": [],
                "updated_at": "2026-09-06T10:00:00+08:00",
            }
            path = write_json(Path(temp_dir) / "creator-memory.json", data)
            errors = validate_creator_memory(path, ["memory-001"])
            self.assertTrue(any("active" in error for error in errors))

    def test_recurring_character_requires_risk_first_asset_review(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            data = {
                "schema_version": "1.0",
                "workflow_mode": "high-risk",
                "review_mode": "merged-blueprint",
                "risk_flags": ["recurring-character"],
                "risk_reason": "同一人物跨镜头反复生成",
                "raw_asset_count": 0,
                "raw_asset_contact_sheet": {"path": "", "sha256": "", "machine_checked": False},
                "identity_anchor_review": {"required": True, "paths": [], "approved": False},
                "user_review": {"required_before_storyboard": False, "approved": False, "approval_stage": "assets"},
            }
            path = write_json(Path(temp_dir) / "asset-review-plan.json", data)
            errors = validate_asset_review_plan(path, Path(temp_dir))
            self.assertTrue(any("先单独审片" in error for error in errors))

    def test_locked_character_profile_passes(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            anchor = root / "identity.png"
            anchor.write_bytes(b"identity-anchor")
            data = {
                "schema_version": "1.0",
                "character_id": "character-001",
                "display_name": "示例人物",
                "status": "locked",
                "authorization": "用户提供并授权当前项目使用",
                "identity": {
                    "age_presentation": "青年",
                    "face": "圆脸",
                    "hair": "黑色短发",
                    "body": "中等身形",
                    "wardrobe": "蓝色上衣",
                    "palette": "蓝白",
                    "visual_style": "干净扁平插画",
                    "fixed_traits": ["圆脸", "黑色短发"],
                    "allowed_variations": ["表情"],
                    "forbidden_variations": ["换脸", "换衣"],
                },
                "reference_assets": [{
                    "path": anchor.name,
                    "sha256": digest(anchor),
                    "role": "identity-anchor",
                    "authorization": "用户授权",
                }],
                "continuity": {
                    "same_identity_across_rolls": True,
                    "applies_to": ["a-roll", "b-roll", "cover"],
                    "identity_anchor_reviewed": True,
                    "representative_actions_reviewed": True,
                },
                "approval": {
                    "approved": True,
                    "approval_message": "人物设定通过",
                    "approved_at": "2026-09-06T10:00:00+08:00",
                },
            }
            path = write_json(root / "character-profile.json", data)
            self.assertEqual(validate_character_profile(path, root), [])

    def test_bundled_platform_profiles_pass(self) -> None:
        self.assertEqual(validate_platform_profiles(ROOT / "assets/platform-overlay-profiles.json"), [])


if __name__ == "__main__":
    unittest.main()

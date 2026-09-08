from __future__ import annotations

import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from validate_cover_contract import validate  # noqa: E402


def write_contract(root: Path) -> Path:
    for name in ("theme.json", "hero.png", "cover.png", "thumb.png"):
        (root / name).write_bytes(name.encode())
    theme_sha = hashlib.sha256((root / "theme.json").read_bytes()).hexdigest()
    data = {
        "schema_version": "1.0",
        "format": {"width": 1080, "height": 1440, "aspect_ratio": "3:4"},
        "theme_binding": {"path": "theme.json", "sha256": theme_sha, "approved": True},
        "main_title": {"text": "不会剪视频也能直接成片", "target_user_or_context_present": True, "pain_or_outcome_present": True},
        "subtitle": {"text": "开源视频制作 Skill", "skill_differentiator_present": True, "duplicates_main_title": False},
        "skill_name": {"text": "Produce Videos", "prominent": True, "original_case_preserved": True},
        "text_hierarchy_review": {"main_title_dominant": True, "subtitle_distinct": True, "orphan_line_free": True, "thumbnail_readable": True},
        "hero_subject": {
            "type": "character",
            "asset_path": "hero.png",
            "authorization_verified": True,
            "action": "站立讲解流程",
            "action_supports_message": True,
            "arbitrary_pose_free": True,
            "styling_matches_context": True,
        },
        "output_cover": "cover.png",
        "output_thumbnail": "thumb.png",
        "review": {"native_size_reviewed": True, "thumbnail_reviewed": True, "approved": True, "approval_message": "封面通过"},
    }
    path = root / "cover-contract.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    return path


class CoverContractTests(unittest.TestCase):
    def test_valid_cover_contract_passes(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            self.assertEqual(validate(write_contract(Path(temp_dir))), [])

    def test_missing_subtitle_hierarchy_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = write_contract(Path(temp_dir))
            data = json.loads(path.read_text(encoding="utf-8"))
            data["subtitle"]["text"] = ""
            data["text_hierarchy_review"]["subtitle_distinct"] = False
            path.write_text(json.dumps(data), encoding="utf-8")
            errors = validate(path)
            self.assertTrue(any("副标题" in error for error in errors))

    def test_arbitrary_character_pose_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = write_contract(Path(temp_dir))
            data = json.loads(path.read_text(encoding="utf-8"))
            data["hero_subject"]["arbitrary_pose_free"] = False
            path.write_text(json.dumps(data), encoding="utf-8")
            self.assertTrue(any("arbitrary_pose_free" in error for error in validate(path)))


if __name__ == "__main__":
    unittest.main()

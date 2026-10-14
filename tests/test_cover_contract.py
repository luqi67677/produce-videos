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
    @staticmethod
    def update(path: Path, **changes: object) -> dict:
        data = json.loads(path.read_text(encoding="utf-8"))
        data.update(changes)
        path.write_text(json.dumps(data), encoding="utf-8")
        return data

    @staticmethod
    def write_data(path: Path, data: dict) -> None:
        path.write_text(json.dumps(data), encoding="utf-8")

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

    def test_general_cover_without_skill_fields_or_subtitle_passes(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = write_contract(Path(temp_dir))
            data = self.update(path, schema_version="1.1", content_mode="general")
            data.pop("skill_name")
            data.pop("subtitle")
            data["text_hierarchy_review"]["subtitle_distinct"] = False
            self.write_data(path, data)
            self.assertEqual(validate(path), [])

    def test_general_cover_optional_subtitle_has_no_skill_requirement(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = write_contract(Path(temp_dir))
            data = self.update(path, schema_version="1.1", content_mode="general")
            data.pop("skill_name")
            data["subtitle"].pop("skill_differentiator_present")
            self.write_data(path, data)
            self.assertEqual(validate(path), [])
            data["subtitle"]["duplicates_main_title"] = True
            self.write_data(path, data)
            self.assertTrue(any("重复主标题" in error for error in validate(path)))
            data["subtitle"]["duplicates_main_title"] = False
            data["text_hierarchy_review"]["subtitle_distinct"] = False
            self.write_data(path, data)
            self.assertTrue(any("subtitle_distinct" in error for error in validate(path)))

    def test_general_blank_subtitle_is_optional(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = write_contract(Path(temp_dir))
            data = self.update(path, schema_version="1.1", content_mode="general")
            data["subtitle"] = {"text": ""}
            data["text_hierarchy_review"].pop("subtitle_distinct")
            self.write_data(path, data)
            self.assertEqual(validate(path), [])

    def test_skill_promotion_retains_skill_specific_requirements(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = write_contract(Path(temp_dir))
            data = self.update(path, schema_version="1.1", content_mode="skill-promotion")
            self.assertEqual(validate(path), [])
            data.pop("skill_name")
            data["subtitle"]["skill_differentiator_present"] = False
            self.write_data(path, data)
            errors = validate(path)
            self.assertTrue(any("Skill 名称" in error for error in errors))
            self.assertTrue(any("差异化能力" in error for error in errors))
            data.pop("subtitle")
            self.write_data(path, data)
            self.assertTrue(any("副标题" in error for error in validate(path)))

    def test_legacy_mode_omission_does_not_bypass_skill_requirements(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = write_contract(Path(temp_dir))
            data = json.loads(path.read_text(encoding="utf-8"))
            data.pop("skill_name")
            data.pop("subtitle")
            self.write_data(path, data)
            errors = validate(path)
            self.assertTrue(any("Skill 名称" in error for error in errors))
            self.assertTrue(any("副标题" in error for error in errors))

    def test_unknown_or_invalid_mode_fails(self) -> None:
        for mode in ("", "other", None, 1, [], {}):
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as temp_dir:
                path = write_contract(Path(temp_dir))
                self.update(path, schema_version="1.1", content_mode=mode)
                self.assertTrue(any("content_mode" in error for error in validate(path)))

    def test_schema_11_requires_explicit_mode(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = write_contract(Path(temp_dir))
            self.update(path, schema_version="1.1")
            self.assertTrue(any("content_mode" in error for error in validate(path)))

    def test_general_keeps_shared_output_theme_authorization_and_review_gates(self) -> None:
        mutations = {
            "main_title": lambda d: d["main_title"].update(text=" "),
            "authorization": lambda d: d["hero_subject"].update(authorization_verified=False),
            "theme_sha": lambda d: d["theme_binding"].update(sha256="0" * 64),
            "theme_approval": lambda d: d["theme_binding"].update(approved=False),
            "cover_missing": lambda d: d.update(output_cover="missing.png"),
            "thumbnail_missing": lambda d: d.update(output_thumbnail="missing.png"),
            "native_review": lambda d: d["review"].update(native_size_reviewed=False),
            "thumbnail_review": lambda d: d["review"].update(thumbnail_reviewed=False),
            "user_approval": lambda d: d["review"].update(approved=False),
            "approval_message": lambda d: d["review"].update(approval_message=""),
        }
        for name, mutate in mutations.items():
            with self.subTest(gate=name), tempfile.TemporaryDirectory() as temp_dir:
                path = write_contract(Path(temp_dir))
                data = self.update(path, schema_version="1.1", content_mode="general")
                mutate(data)
                self.write_data(path, data)
                self.assertTrue(validate(path), name)

    def test_empty_output_and_invalid_subtitle_cannot_pass(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = write_contract(Path(temp_dir))
            self.update(path, schema_version="1.1", content_mode="general")
            (path.parent / "cover.png").write_bytes(b"")
            self.assertTrue(any("output_cover" in error for error in validate(path)))
            data = self.update(path, subtitle={"text": 1})
            self.assertTrue(any("subtitle 必须" in error for error in validate(path)))


if __name__ == "__main__":
    unittest.main()

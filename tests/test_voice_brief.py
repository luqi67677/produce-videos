from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from validate_voice_brief import validate  # noqa: E402


class VoiceBriefTests(unittest.TestCase):
    def write_brief(self, root: Path, **updates: object) -> Path:
        data = {
            "schema_version": "1.0",
            "user_request": "成年女声，温柔自然，不要播音腔",
            "gender_presentation": "女声",
            "age_impression": "成年",
            "tone_keywords": ["温柔", "自然"],
            "energy_level": "中低",
            "pace": "中速",
            "use_case": "品牌宣传",
            "avoid_traits": ["播音腔"],
            "language": "Chinese",
            "approved": True,
            "approval_message": "确认",
            "approved_at": "2026-09-04T23:08:39+08:00",
        }
        data.update(updates)
        path = root / "voice-brief.json"
        path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
        return path

    def test_approved_complete_brief_passes(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            self.assertEqual(validate(self.write_brief(Path(temp_dir)), True), [])

    def test_missing_gender_is_blocked(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            errors = validate(self.write_brief(Path(temp_dir), gender_presentation=""), True)
            self.assertIn("声音需求单缺少 gender_presentation", errors)

    def test_unapproved_brief_is_blocked(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            errors = validate(
                self.write_brief(Path(temp_dir), approved=False, approval_message="", approved_at=""),
                True,
            )
            self.assertIn("用户尚未确认声音需求单", errors)


if __name__ == "__main__":
    unittest.main()

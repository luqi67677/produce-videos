import json
import tempfile
import unittest
from pathlib import Path
import sys


SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from validate_video_theme import validate  # noqa: E402


def valid_theme() -> dict:
    return {
        "schema_version": "1.1",
        "theme_id": "clean-test",
        "name": "干净测试主题",
        "status": "selected",
        "selected_option": "user-specified",
        "selected_at": "2026-09-05 20:00",
        "source_theme": {"user_override": True},
        "source_palette_original": {"background": "#FFFFFF"},
        "palette": {
            "background": "#FFFFFF",
            "surface": "#F5F5F5",
            "text_primary": "#111111",
            "text_inverse": "#FFFFFF",
            "accent_primary": "#333333",
            "accent_secondary": "#777777",
            "highlight": "#BBBBBB",
            "muted_line": "#DDDDDD",
        },
        "semantic_roles": {"background": "背景"},
        "visual_language": {"shadow": "none"},
        "cleanliness_contract": {
            "no_ground_plane": True,
            "no_horizon_line": True,
            "no_cast_shadow": True,
            "no_drop_shadow": True,
            "no_floor_reflection": True,
            "rim_light_mode": "subtle-soft",
            "single_visual_language": True,
            "raw_full_page_as_decoration": False,
            "stacked_background_effects": False,
            "heavy_subtitle_bar": False,
            "exception_policy": "only_when_user_explicitly_requires_real_spatial_context",
        },
        "image_generation": {
            "palette_prompt": "clean neutral palette",
            "negative_palette_prompt": "no dirty color cast",
            "depth_prompt": "subtle soft rim light",
            "negative_composition_prompt": "no floor, no cast shadow",
        },
        "locked": True,
    }


class VideoThemeCleanlinessTests(unittest.TestCase):
    def validate_data(self, data: dict) -> list[str]:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "video-style-theme.json"
            path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
            return validate(path, True)

    def test_clean_theme_passes(self):
        self.assertEqual(self.validate_data(valid_theme()), [])

    def test_ground_or_cast_shadow_fails(self):
        data = valid_theme()
        data["cleanliness_contract"]["no_ground_plane"] = False
        data["cleanliness_contract"]["no_cast_shadow"] = False
        errors = self.validate_data(data)
        self.assertTrue(any("no_ground_plane" in error for error in errors))
        self.assertTrue(any("no_cast_shadow" in error for error in errors))

    def test_missing_cleanliness_contract_fails(self):
        data = valid_theme()
        del data["cleanliness_contract"]
        errors = self.validate_data(data)
        self.assertIn("缺少 cleanliness_contract", errors)

    def test_neon_rim_light_mode_fails(self):
        data = valid_theme()
        data["cleanliness_contract"]["rim_light_mode"] = "neon-halo"
        errors = self.validate_data(data)
        self.assertTrue(any("rim_light_mode" in error for error in errors))


if __name__ == "__main__":
    unittest.main()

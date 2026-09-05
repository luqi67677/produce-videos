import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import sys


SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from validate_style_options import required_quality_fields, validate  # noqa: E402


class StyleOptionsApprovalModeTests(unittest.TestCase):
    def test_v13_requires_cleanliness_review_fields(self):
        fields = required_quality_fields("1.3")
        self.assertIn("no_ground_or_horizon", fields)
        self.assertIn("no_cast_or_drop_shadow", fields)
        self.assertIn("rim_light_separation_appropriate", fields)
        self.assertIn("no_raw_full_page_as_decorative_card", fields)

    def test_candidate_preview_does_not_require_source_user_approval(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            with (
                patch("validate_style_options.validate_catalog", return_value=[]),
                patch("validate_style_options.validate_source_assets", return_value=[]),
                patch("validate_style_options.validate_approval", return_value=[]) as approval,
            ):
                validate(root / "missing-options.json", root / "missing-catalog.json")
            approval.assert_not_called()

    def test_selected_theme_requires_source_user_approval(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            with (
                patch("validate_style_options.validate_catalog", return_value=[]),
                patch("validate_style_options.validate_source_assets", return_value=[]),
                patch("validate_style_options.validate_approval", return_value=[]) as approval,
            ):
                validate(root / "missing-options.json", root / "missing-catalog.json", True)
            approval.assert_called_once()


if __name__ == "__main__":
    unittest.main()

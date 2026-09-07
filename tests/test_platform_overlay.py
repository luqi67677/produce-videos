from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from generate_platform_overlay import build_svg  # noqa: E402


class PlatformOverlayTests(unittest.TestCase):
    def test_douyin_overlay_uses_portrait_canvas_and_review_label(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project = Path(temp_dir)
            shot = project / "shot-readiness.json"
            shot.write_text(json.dumps({
                "format": "portrait",
                "platform_overlay": {
                    "profile_id": "douyin-portrait",
                    "calibration_source": "bundled-conservative-default",
                    "occlusion_ratio_override": {},
                },
            }), encoding="utf-8")
            svg = build_svg(shot)
            self.assertIn('width="1080"', svg)
            self.assertIn('height="1440"', svg)
            self.assertIn("REVIEW ONLY", svg)
            self.assertIn("right-actions", svg)

    def test_custom_ratios_must_include_all_sides(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            shot = Path(temp_dir) / "shot-readiness.json"
            shot.write_text(json.dumps({
                "format": "portrait",
                "platform_overlay": {
                    "profile_id": "douyin-portrait",
                    "calibration_source": "user-recent-screenshot",
                    "occlusion_ratio_override": {"top": 0.1},
                },
            }), encoding="utf-8")
            with self.assertRaises(ValueError):
                build_svg(shot)


if __name__ == "__main__":
    unittest.main()

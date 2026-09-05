from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from validate_shot_readiness import validate_scene_design  # noqa: E402


def valid_scene() -> dict:
    return {
        "roll": {
            "type": "b-roll",
            "narrative_role": "展示当前口播中的产品结果",
            "covers": "安装完成后就可以直接使用",
            "entry_reason": "需要真实结果证据",
            "return_strategy": "证据出现后返回主轴",
        },
        "visual_source_strategy": {
            "selected": "user-provided",
            "source_order_considered": ["user-provided", "official", "verified-keyframe", "generated-still", "code-motion", "text-only"],
            "gap_reason": "",
            "generated_still_approved": False,
            "video_model_used": False,
        },
        "transition": {
            "type": "insert-cut",
            "previous_end_state": "主讲人提出结果",
            "next_start_state": "界面展示完成结果",
            "continuity_anchor": "同一句旁白",
            "reason": "让结论有可见证据",
        },
        "layout_preset": {
            "id": "video/side-reel",
            "adaptation": "native-landscape",
            "selection_reason": "录屏是主证据，说明在左侧",
        },
        "composition_budget": {
            "focal_points": 1,
            "support_groups": 2,
            "decorative_groups": 0,
            "accent_colors": 1,
            "material_systems": 1,
            "occupied_area_ratio": 0.64,
            "largest_empty_area_ratio": 0.24,
            "density_exception_reason": "",
            "intentional_whitespace_reason": "",
        },
    }


class SceneDesignContractTests(unittest.TestCase):
    def test_valid_broll_contract_passes(self) -> None:
        self.assertEqual(validate_scene_design(valid_scene(), "s01"), [])

    def test_broll_without_spoken_coverage_fails(self) -> None:
        scene = valid_scene()
        scene["roll"]["covers"] = ""
        self.assertTrue(any("covers" in error for error in validate_scene_design(scene, "s01")))

    def test_unexplained_large_blank_area_fails(self) -> None:
        scene = valid_scene()
        scene["composition_budget"]["largest_empty_area_ratio"] = 0.6
        self.assertTrue(any("大面积空白" in error for error in validate_scene_design(scene, "s01")))

    def test_video_model_is_blocked(self) -> None:
        scene = valid_scene()
        scene["visual_source_strategy"]["video_model_used"] = True
        self.assertTrue(any("视频生成模型" in error for error in validate_scene_design(scene, "s01")))


if __name__ == "__main__":
    unittest.main()

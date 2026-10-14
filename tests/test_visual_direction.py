from __future__ import annotations

import copy
import math
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from validate_visual_direction import validate


def plan() -> dict:
    return {
        "shots": [
            {"id": "s01", "start": 0.0, "end": 3.0, "subject": "包装", "material": "概念示意", "action": "打开", "result": "露出内容", "covers": "这是什么", "layout_family": "object", "asset_paths": []},
            {"id": "s02", "start": 3.0, "end": 6.0, "subject": "内容", "material": "概念示意", "action": "对照", "result": "看到差异", "covers": "交付了什么", "layout_family": "comparison", "asset_paths": []}
        ],
        "bridges": [{"from": "s01", "to": "s02", "type": "match-cut", "anchor": "包装中心", "reason": "继续看交付物", "audio": "原旁白连续", "duration_seconds": 0.2}]
    }


class VisualDirectionTests(unittest.TestCase):
    def test_valid_plan_does_not_claim_creative_approval(self) -> None:
        result = validate(plan(), ROOT)
        self.assertTrue(result["machine_pass"])
        self.assertEqual(result["creative_quality"], "requires-video-review")

    def test_every_neighbor_needs_a_bridge_and_duplicates_fail(self) -> None:
        data = plan()
        data["bridges"] = []
        self.assertFalse(validate(data, ROOT)["machine_pass"])
        data = plan()
        data["bridges"].append(copy.deepcopy(data["bridges"][0]))
        self.assertFalse(validate(data, ROOT)["machine_pass"])

    def test_missing_real_asset_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            data = plan()
            data["shots"][0]["asset_paths"] = ["actual.png"]
            self.assertFalse(validate(data, Path(tmp))["machine_pass"])
            (Path(tmp) / "actual.png").write_bytes(b"fixture")
            self.assertTrue(validate(data, Path(tmp))["machine_pass"])

    def test_nonfinite_bool_and_discontinuous_times_fail(self) -> None:
        for value in (float("nan"), float("inf"), True, 3.1, 2.9):
            with self.subTest(value=value):
                data = plan()
                data["shots"][1]["start"] = value
                self.assertFalse(validate(data, ROOT)["machine_pass"])

    def test_invalid_bridge_type_is_a_reported_failure(self) -> None:
        for value in ([], {}, None, "random-wipe"):
            with self.subTest(value=value):
                data = plan()
                data["bridges"][0]["type"] = value
                result = validate(data, ROOT)
                self.assertFalse(result["machine_pass"])
                self.assertTrue(any("type 无效" in error for error in result["errors"]))

    def test_cut_has_zero_duration_and_transitions_have_a_limit(self) -> None:
        for kind, duration in (("cut", 0.2), ("match-cut", 0.9), ("match-cut", -0.1), ("match-cut", True)):
            with self.subTest(kind=kind, duration=duration):
                data = plan()
                data["bridges"][0].update(type=kind, duration_seconds=duration)
                self.assertFalse(validate(data, ROOT)["machine_pass"])

    def test_same_layout_warning_does_not_fake_a_creative_failure(self) -> None:
        data = plan()
        data["shots"][1]["layout_family"] = "object"
        third = copy.deepcopy(data["shots"][0])
        third.update(id="s03", start=6.0, end=9.0)
        data["shots"].append(third)
        bridge = copy.deepcopy(data["bridges"][0])
        bridge.update({"from": "s02", "to": "s03"})
        data["bridges"].append(bridge)
        result = validate(data, ROOT)
        self.assertTrue(result["machine_pass"])
        self.assertTrue(any("连续三镜" in item for item in result["warnings"]))


if __name__ == "__main__":
    unittest.main()

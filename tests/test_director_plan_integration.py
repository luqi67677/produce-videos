"""验证导演计划接入合成门禁和节拍工具后，仍保留语义时序。"""

from __future__ import annotations

import contextlib
import copy
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import snap_edl_to_beats  # noqa: E402
import validate_render_gate as gate  # noqa: E402
import test_director_plan as plan_fixtures  # noqa: E402


class DirectorPlanIntegrationTests(unittest.TestCase):
    def test_planning_is_allowed_for_review_but_blocks_sample_and_full_render(self):
        fixture = plan_fixtures.DirectorPlanTests()
        fixture.setUp()
        self.addCleanup(fixture.tearDown)
        fixture.write("video-style-theme.json", {"selected_option": "user-specified"})
        self.assertEqual(gate.validate_director_plan(fixture.project), [])
        plan = fixture.data.pop("director_plan")
        validators = (
            "validate_approval", "validate_master_script", "validate_source_assets",
            "validate_video_theme", "validate_narration_contract", "validate_shot_readiness",
            "validate_timeline_sync", "validate_creative_foundation", "validate_theme_catalog",
            "validate_layout_catalog", "validate_style_options", "validate_motion_coverage",
        )
        # 其他门禁视作已通过，保留真实导演计划校验，确认拒绝来自接线而非缺文件。
        with contextlib.ExitStack() as stack:
            for name in validators:
                stack.enter_context(mock.patch.object(gate, name, return_value=[]))
            for mode in ("sample", "full"):
                with self.subTest(mode=mode):
                    fixture.data.pop("director_plan", None)
                    fixture.save()
                    with mock.patch.object(sys, "argv", ["validate_render_gate.py", str(fixture.project), "--mode", mode]):
                        with contextlib.redirect_stdout(io.StringIO()):
                            self.assertEqual(gate.main(), 0)
                    fixture.data["director_plan"] = plan
                    fixture.save()
                    output = io.StringIO()
                    with mock.patch.object(sys, "argv", ["validate_render_gate.py", str(fixture.project), "--mode", mode]):
                        with contextlib.redirect_stdout(output):
                            self.assertEqual(gate.main(), 1)
                    self.assertIn("director-plan:", output.getvalue())
                    self.assertIn("planning", output.getvalue())
                    self.assertIn(f"STOP 不允许进入 {mode} 渲染", output.getvalue())

    def test_beat_cli_preserves_event_boundaries_and_invalidates_both_moved_sides(self):
        cut = 1.0375
        original = {
            "picture_track": [
                {"clip_id": "s1", "timeline_start_seconds": 0.0, "duration_seconds": cut,
                 "semantic_boundary_verified": True},
                {"clip_id": "s2", "timeline_start_seconds": cut, "duration_seconds": 2.0 - cut,
                 "semantic_boundary_verified": True},
            ],
            "transitions": [{"at_seconds": cut, "type": "cut"}],
        }
        # 高精度切点可发现跳过吸附后仍被统一取整的隐性移动。
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            beats = project / "beat-grid.json"
            beats.write_text(json.dumps({"beats": [1.0], "method": "test"}), encoding="utf-8")
            for protected_side in (0, 1, None):
                with self.subTest(protected_side=protected_side):
                    edl = copy.deepcopy(original)
                    if protected_side is not None:
                        edl["picture_track"][protected_side]["semantic_events"] = [
                            {"event_id": "task-arrived", "start_frame": 3, "end_frame": 20}
                        ]
                    source = project / "edit-decision-list.json"
                    output = project / "snapped.json"
                    source.write_text(json.dumps(edl), encoding="utf-8")
                    source_before = source.read_bytes()
                    run = subprocess.run(
                        [sys.executable, str(Path(snap_edl_to_beats.__file__)), str(source), str(beats), "--output", str(output)],
                        capture_output=True, text=True, check=False,
                    )
                    self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
                    self.assertEqual(source.read_bytes(), source_before)
                    result = json.loads(output.read_text(encoding="utf-8"))
                    if protected_side is not None:
                        self.assertEqual(result["picture_track"], edl["picture_track"])
                        self.assertEqual(result["transitions"], edl["transitions"])
                        self.assertEqual(result["beat_quantization"]["changes"], [])
                    else:
                        left, right = result["picture_track"]
                        self.assertEqual(left["duration_seconds"], 1.0)
                        self.assertEqual(right["timeline_start_seconds"], 1.0)
                        self.assertEqual(right["duration_seconds"], 1.0)
                        self.assertIs(left["semantic_boundary_verified"], False)
                        self.assertIs(right["semantic_boundary_verified"], False)
                        self.assertEqual(result["transitions"][0]["at_seconds"], 1.0)
                        self.assertEqual(len(result["beat_quantization"]["changes"]), 1)


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from analyze_motion_coverage import sha256  # noqa: E402
from build_motion_coverage import build_coverage  # noqa: E402
from validate_motion_coverage import validate  # noqa: E402
from validate_render_gate import motion_review_files  # noqa: E402


def write_json(path: Path, value: dict) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def reviewed_fixture(coverage: dict) -> None:
    """仅测试 fixture；生产 builder 不设置任何这些审查结果。"""
    coverage["review_status"] = "reviewed-test-fixture"
    for sample in coverage["samples"]:
        for key in (
            "uses_final_audio", "uses_locked_storyboard", "single_subtitle_layer",
            "visual_coverage_verified", "character_continuity_verified", "platform_safe",
            "machine_reviewed", "user_reviewed",
        ):
            sample[key] = True


@unittest.skipUnless(shutil.which("ffmpeg") and shutil.which("ffprobe"), "需要本机 FFmpeg/ffprobe")
class MotionProducerConsumerTests(unittest.TestCase):
    def make_real_audit(self, root: Path, *, blank: bool = False, partial: bool = False) -> Path:
        video = root / "preview.mp4"
        source = "color=c=black:s=96x128:r=10:d=2" if blank else "testsrc2=s=96x128:r=10:d=2"
        subprocess.run([
            shutil.which("ffmpeg"), "-v", "error", "-f", "lavfi", "-i", source,
            "-c:v", "libx264", "-threads", "1", "-pix_fmt", "yuv420p", str(video),
        ], check=True, capture_output=True)
        write_json(root / "edit-decision-list.json", {"schema_version": "1.1", "picture_track": [{
            "scene_id": "s01", "timeline_start_seconds": 0, "duration_seconds": 2,
            "narration_excerpt": "测试原句",
        }]})
        write_json(root / "motion-plan.json", {"schema_version": "1.3", "shots": [{
            "shot_id": "s01", "timeline_start_seconds": 0, "duration_seconds": 2,
            "narration_excerpt": "测试原句", "expected_reveal_count": 1,
            "baseline_visible_from_start": True, "intentional_blank_approved": False,
        }]})
        output = root / "motion-audit.json"
        command = [sys.executable, str(ROOT / "scripts/analyze_motion_coverage.py"), str(video),
                   str(root / "edit-decision-list.json"), str(root / "motion-plan.json"), str(output)]
        if partial:
            command += ["--duration", "1"]
        result = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(result.returncode, 1 if blank or partial else 0, result.stdout + result.stderr)
        return output

    def test_real_output_builds_pending_then_reviewed_contract(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            audit = self.make_real_audit(root)
            coverage_path = root / "motion-coverage.json"
            coverage = build_coverage(audit, coverage_path, grammars=["continuous-flow"], workflow_mode="fast")
            original_audit_hash = sha256(audit)
            self.assertFalse(coverage["samples"][0]["user_reviewed"])
            self.assertFalse(coverage["samples"][0]["machine_reviewed"])
            write_json(coverage_path, coverage)
            self.assertTrue(any("用户" in error for error in validate(coverage_path)))
            reviewed_fixture(coverage)
            write_json(coverage_path, coverage)
            self.assertEqual(validate(coverage_path), [])
            self.assertEqual(sha256(audit), original_audit_hash)
            self.assertIn(audit.resolve(), motion_review_files(root))
            # 默认命令不能覆写已存在的审片记录。
            before = coverage_path.read_bytes()
            result = subprocess.run([sys.executable, str(ROOT / "scripts/build_motion_coverage.py"),
                                     str(audit), str(coverage_path), "--grammar", "continuous-flow"],
                                    capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(coverage_path.read_bytes(), before)

    def test_raw_audit_is_rejected_before_approval_errors(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            audit = self.make_real_audit(root)
            coverage_path = root / "motion-coverage.json"
            coverage_path.write_bytes(audit.read_bytes())
            self.assertTrue(any("build_motion_coverage.py" in error for error in validate(coverage_path)))
            result = subprocess.run([sys.executable, str(ROOT / "scripts/validate_render_gate.py"),
                                     str(root), "--mode", "full"], capture_output=True, text=True)
            self.assertEqual(result.returncode, 1)
            self.assertIn("build_motion_coverage.py", result.stdout)
            self.assertNotIn("script:", result.stdout)
            legacy_audit = json.loads(audit.read_text())
            legacy_audit.pop("artifact_type")
            write_json(coverage_path, legacy_audit)
            self.assertTrue(any("build_motion_coverage.py" in error for error in validate(coverage_path)))

    def test_current_file_bindings_and_preview_identity_are_required(self) -> None:
        for target in ("preview.mp4", "edit-decision-list.json", "motion-plan.json", "motion-audit.json", "other-preview"):
            with self.subTest(target=target), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                audit = self.make_real_audit(root)
                coverage_path = root / "motion-coverage.json"
                coverage = build_coverage(audit, coverage_path, grammars=["continuous-flow"], workflow_mode="fast")
                reviewed_fixture(coverage)
                if target == "other-preview":
                    shutil.copy(root / "preview.mp4", root / "other.mp4")
                    coverage["samples"][0]["path"] = "other.mp4"
                else:
                    with (root / target).open("ab") as handle:
                        handle.write(b" ")
                write_json(coverage_path, coverage)
                errors = validate(coverage_path)
                self.assertTrue(errors, target)
                self.assertTrue(any("SHA-256" in error or "未绑定" in error for error in errors), errors)

    def test_real_blank_or_partial_report_cannot_be_approved_into_pass(self) -> None:
        for variant in ("blank", "partial"):
            with self.subTest(variant=variant), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                audit = self.make_real_audit(root, blank=variant == "blank", partial=variant == "partial")
                data = json.loads(audit.read_text())
                self.assertFalse(data["machine_pass"])
                coverage_path = root / "motion-coverage.json"
                coverage = build_coverage(audit, coverage_path, grammars=["continuous-flow"], workflow_mode="fast")
                reviewed_fixture(coverage)
                write_json(coverage_path, coverage)
                self.assertTrue(any("未通过" in error for error in validate(coverage_path)))


if __name__ == "__main__":
    unittest.main()

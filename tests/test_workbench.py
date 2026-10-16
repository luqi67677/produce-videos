from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch


SCRIPT = Path(__file__).absolute().parents[1] / "scripts" / "workbench.py"
SPEC = importlib.util.spec_from_file_location("workbench", SCRIPT)
workbench = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(workbench)


def preview_response(project: Path, url: str | None = "http://127.0.0.1:3027/#project/actual-project-id") -> dict:
    # Hyperframes 0.8.164 的真实 --json 响应有 schemaVersion/operation/result 包装。
    return {"schemaVersion": 1, "operation": "start", "ok": True, "result": {
        "state": "reused", "mode": "background", "projectName": project.name,
        "projectDir": str(project), "host": "127.0.0.1", "port": 3027,
        "pid": 25232, "serverUrl": "http://127.0.0.1:3027", "studioUrl": url, "ready": True,
    }}


class WorkbenchTests(unittest.TestCase):
    def setUp(self) -> None:
        # macOS /var 和 /tmp 可能是系统符号链接；测试使用其真实位置。
        self.temp = tempfile.TemporaryDirectory(dir=os.path.realpath(tempfile.gettempdir()))
        self.root = Path(self.temp.name)
        self.project = self.root / "project"
        self.project.mkdir()
        (self.project / "index.html").write_text('<html><div data-composition-id="main" data-duration="8">画面稿</div></html>', encoding="utf-8")
        (self.project / "hyperframes.json").write_text('{"composition":"index.html"}', encoding="utf-8")
        (self.project / "STORYBOARD.md").write_text("## Frame 1 — 画面\n\n- duration: 8s\n", encoding="utf-8")
        (self.project / "assets").mkdir()
        (self.project / "assets" / "frame.svg").write_text("<svg/>", encoding="utf-8")

    def tearDown(self) -> None:
        self.temp.cleanup()

    def planning(self) -> None:
        (self.project / "shot-readiness.json").write_text(json.dumps({
            "schema_version": "2.6", "shots": [{"shot_id": "s01"}],
            "director_plan": {"stage": "planning", "timing_basis": "estimated"},
        }), encoding="utf-8")

    def test_native_storyboard_has_unverified_production_stage(self) -> None:
        _, report = workbench.validate_project(self.project)
        self.assertEqual(report["storyboard"]["stage"], "storyboard")
        self.assertEqual(report["storyboard"]["timing_basis"], "unverified")
        self.assertFalse(report["production_gate_validated"])

    def test_planning_preview_does_not_require_audio(self) -> None:
        self.planning()
        _, report = workbench.validate_project(self.project)
        self.assertTrue(report["preview_allowed"])
        self.assertFalse(report["audio_required_for_preview"])
        self.assertEqual(report["storyboard"]["timing_basis"], "estimated")
        self.assertFalse((self.project / "narration-contract.json").exists())

    def test_unknown_project_cannot_create_snapshot(self) -> None:
        (self.project / "hyperframes.json").unlink()
        with self.assertRaisesRegex(workbench.WorkbenchError, "未知项目"):
            workbench.snapshot_project(self.project)
        self.assertFalse((self.project / workbench.STATE_DIR).exists())

    def test_unknown_stage_is_rejected_without_writing(self) -> None:
        self.planning()
        path = self.project / "shot-readiness.json"
        data = json.loads(path.read_text())
        data["director_plan"]["stage"] = "mystery"
        path.write_text(json.dumps(data))
        with self.assertRaises(workbench.WorkbenchError):
            workbench.snapshot_project(self.project)
        self.assertFalse((self.project / workbench.STATE_DIR).exists())

    def test_parent_traversal_is_rejected(self) -> None:
        with self.assertRaisesRegex(workbench.WorkbenchError, "路径不能包含"):
            workbench.snapshot_project(self.project / ".." / "project")
        with self.assertRaisesRegex(workbench.WorkbenchError, "越界"):
            workbench.project_file(self.project, "../outside.txt")

    def test_project_symlink_is_rejected(self) -> None:
        alias = self.root / "alias"
        alias.symlink_to(self.project, target_is_directory=True)
        with self.assertRaisesRegex(workbench.WorkbenchError, "符号链接"):
            workbench.snapshot_project(alias)

    def test_managed_file_symlink_is_rejected_before_write(self) -> None:
        secret = self.root / "outside.html"
        secret.write_text("do not read")
        (self.project / "assets" / "linked.html").symlink_to(secret)
        with self.assertRaisesRegex(workbench.WorkbenchError, "符号链接"):
            workbench.snapshot_project(self.project)
        self.assertFalse((self.project / workbench.STATE_DIR).exists())

    def test_state_directory_symlink_never_writes_outside(self) -> None:
        outside = self.root / "outside"
        outside.mkdir()
        (self.project / workbench.STATE_DIR).symlink_to(outside, target_is_directory=True)
        with self.assertRaises((workbench.WorkbenchError, OSError)):
            workbench.snapshot_project(self.project)
        self.assertEqual(list(outside.iterdir()), [])

    def test_baseline_symlink_never_overwrites_target(self) -> None:
        directory = self.project / workbench.STATE_DIR
        directory.mkdir()
        target = self.root / "valuable.json"
        target.write_text("original")
        (directory / workbench.BASELINE_NAME).symlink_to(target)
        with self.assertRaises(workbench.WorkbenchError):
            workbench.snapshot_project(self.project, replace=True)
        self.assertEqual(target.read_text(), "original")

    def test_external_edit_add_delete_are_detected_without_sync(self) -> None:
        workbench.snapshot_project(self.project)
        (self.project / "index.html").write_text('<div data-composition-id="main">edited in Studio</div>')
        (self.project / "assets" / "frame.svg").unlink()
        (self.project / "assets" / "new.css").write_text("body{color:red}")
        result = workbench.check_project(self.project)
        self.assertEqual(result["modified"], ["index.html"])
        self.assertEqual(result["deleted"], ["assets/frame.svg"])
        self.assertEqual(result["added"], ["assets/new.css"])
        self.assertEqual(result["synchronization_status"], "not_performed")
        self.assertFalse(result["baseline_updated"])
        self.assertTrue(workbench.check_project(self.project)["changed"])

    def test_deleted_entry_is_still_reported_by_check(self) -> None:
        workbench.snapshot_project(self.project)
        (self.project / "index.html").unlink()
        self.assertIn("index.html", workbench.check_project(self.project)["deleted"])

    def test_caption_overrides_and_caption_sources_are_managed(self) -> None:
        names = ("caption-overrides.json", "captions.json", "captions.srt", "captions.vtt", "assets/captions.json", "assets/source.txt")
        for name in names:
            (self.project / name).write_text("before", encoding="utf-8")
        workbench.snapshot_project(self.project)
        for name in names:
            (self.project / name).write_text("after", encoding="utf-8")
        result = workbench.check_project(self.project)
        self.assertEqual(result["modified"], sorted(names))

    def test_baseline_requires_explicit_replacement(self) -> None:
        workbench.snapshot_project(self.project)
        with self.assertRaisesRegex(workbench.WorkbenchError, "baseline 已存在"):
            workbench.snapshot_project(self.project)
        workbench.snapshot_project(self.project, replace=True)
        self.assertFalse(workbench.check_project(self.project)["changed"])

    def test_relocated_or_tampered_baseline_is_rejected(self) -> None:
        workbench.snapshot_project(self.project)
        path = self.project / workbench.STATE_DIR / workbench.BASELINE_NAME
        data = json.loads(path.read_text())
        data["project_root"] = str(self.root)
        path.write_text(json.dumps(data))
        with self.assertRaisesRegex(workbench.WorkbenchError, "不属于"):
            workbench.check_project(self.project)

    def test_inspect_returns_current_source_and_truncation(self) -> None:
        report = workbench.inspect_project(self.project, include_source=True, max_chars=10)
        self.assertTrue(report["sources"]["index.html"]["truncated"])
        self.assertEqual(len(report["sources"]["index.html"]["text"]), 10)
        self.assertEqual(report["synchronization_status"], "not_performed")

    def test_open_uses_argv_and_actual_url_without_shell(self) -> None:
        hostile = self.root / "project ; $(touch INJECTED)"
        self.project.rename(hostile)
        self.project = hostile
        cli = self.root / "hyperframes.mjs"
        cli.write_text("// fake executable tested through subprocess mock")
        with patch.object(workbench.shutil, "which", return_value="/usr/bin/node"), patch.object(workbench.subprocess, "run") as run, patch.object(workbench, "verify_runtime_patch", return_value={"verified": True}), patch.object(workbench, "verify_running_patch", return_value={"patch_id": "pv-sync-cut-1"}):
            run.side_effect = [
                subprocess.CompletedProcess([], 0, "0.8.164\n", ""),
                subprocess.CompletedProcess([], 0, json.dumps(preview_response(self.project)), ""),
            ]
            report = workbench.open_project(self.project, cli)
        command = run.call_args_list[1].args[0]
        self.assertEqual(command, ["/usr/bin/node", str(cli), "preview", str(hostile), "--background", "--no-open", "--port", "3027", "--json"])
        self.assertFalse(run.call_args_list[1].kwargs.get("shell", False))
        self.assertEqual(report["studio_url"], "http://127.0.0.1:3027/#project/actual-project-id")
        self.assertFalse(report["browser_opened"])
        self.assertFalse((self.root / "INJECTED").exists())

    def test_version_mismatch_fails_before_preview(self) -> None:
        cli = self.root / "hyperframes.mjs"
        cli.write_text("// fake")
        with patch.object(workbench.shutil, "which", return_value="/usr/bin/node"), patch.object(workbench.subprocess, "run", return_value=subprocess.CompletedProcess([], 0, "0.8.165", "")) as run:
            with self.assertRaisesRegex(workbench.WorkbenchError, "只验证过"):
                workbench.open_project(self.project, cli)
        self.assertEqual(run.call_count, 1)

    def test_cli_path_symlink_and_invalid_port_are_rejected(self) -> None:
        real = self.root / "real.mjs"
        real.write_text("// fake")
        alias = self.root / "alias.mjs"
        alias.symlink_to(real)
        with self.assertRaisesRegex(workbench.WorkbenchError, "符号链接"):
            workbench.cli_environment(alias)
        with self.assertRaisesRegex(workbench.WorkbenchError, "端口"):
            workbench.preview_command(self.project, {"node": "node", "cli": "cli.mjs"}, 0)

    def test_nested_cache_symlink_blocks_external_preview_process(self) -> None:
        cache = self.project / ".hyperframes"
        cache.mkdir()
        target = self.root / "outside.json"
        target.write_text("original")
        (cache / "nested.json").symlink_to(target)
        with patch.object(workbench.subprocess, "run") as run:
            with self.assertRaisesRegex(workbench.WorkbenchError, "符号链接"):
                workbench.open_project(self.project, self.root / "absent.mjs")
        run.assert_not_called()
        self.assertEqual(target.read_text(), "original")

    def test_open_does_not_invent_url_from_requested_port(self) -> None:
        runtime = {"node": "node", "cli": "cli.mjs", "version": "0.8.164"}
        for url in (None, "http://example.com:3027/", "http://127.0.0.1:invalid/"):
            output = preview_response(self.project, url)
            with self.subTest(output=output), patch.object(workbench, "cli_environment", return_value=runtime), patch.object(workbench.subprocess, "run", return_value=subprocess.CompletedProcess([], 0, json.dumps(output), "")):
                with self.assertRaises(workbench.WorkbenchError):
                    workbench.open_project(self.project, "unused.mjs")

    def test_real_cli_envelope_validates_success_ready_and_project(self) -> None:
        runtime = {"node": "node", "cli": "cli.mjs", "version": "0.8.164"}
        actual = preview_response(self.project)
        with patch.object(workbench, "cli_environment", return_value=runtime), patch.object(workbench.subprocess, "run", return_value=subprocess.CompletedProcess([], 0, json.dumps(actual), "")), patch.object(workbench, "verify_running_patch", return_value={"patch_id": "pv-sync-cut-1"}):
            report = workbench.open_project(self.project, "unused.mjs")
        self.assertEqual(report["studio_url"], actual["result"]["studioUrl"])
        self.assertEqual(report["cli_result"]["result"]["state"], "reused")
        for error in ("not_ok", "not_ready", "wrong_project", "unknown_schema"):
            output = preview_response(self.project)
            if error == "not_ok":
                output["ok"] = False
            elif error == "not_ready":
                output["result"]["ready"] = False
            elif error == "wrong_project":
                output["result"]["projectDir"] = str(self.root)
            else:
                output["schemaVersion"] = 99
            with self.subTest(error=error), patch.object(workbench, "cli_environment", return_value=runtime), patch.object(workbench.subprocess, "run", return_value=subprocess.CompletedProcess([], 0, json.dumps(output), "")):
                with self.assertRaises(workbench.WorkbenchError):
                    workbench.open_project(self.project, "unused.mjs")

    def test_reused_old_server_is_rejected(self) -> None:
        runtime = {"node": "node", "cli": "cli.mjs", "version": "0.8.164"}
        with patch.object(workbench, "cli_environment", return_value=runtime), patch.object(workbench.subprocess, "run", return_value=subprocess.CompletedProcess([], 0, json.dumps(preview_response(self.project)), "")), patch.object(workbench, "verify_running_patch", side_effect=workbench.WorkbenchError("旧版本")):
            with self.assertRaisesRegex(workbench.WorkbenchError, "旧版本"):
                workbench.open_project(self.project, "unused.mjs")

    def test_running_patch_requires_local_host_and_exact_capability(self) -> None:
        for url in ("https://example.com/", "http://user@127.0.0.1:3027/"):
            with self.subTest(url=url), patch.object(workbench, "build_opener") as opener:
                with self.assertRaises(workbench.WorkbenchError):
                    workbench.verify_running_patch(url)
                opener.assert_not_called()
        for body in (b'{}', b'{"patch_id":"old","range_cut_preview":true}'):
            with patch.object(workbench, "build_opener") as opener:
                opener.return_value.open.return_value.__enter__.return_value.read.return_value = body
                with self.assertRaisesRegex(workbench.WorkbenchError, "旧版本"):
                    workbench.verify_running_patch("http://127.0.0.1:3027/")

    def test_runtime_patch_required_before_start(self) -> None:
        cli = self.root / "hyperframes.mjs"
        cli.write_text("// fake")
        with patch.object(workbench.shutil, "which", return_value="/usr/bin/node"), patch.object(workbench.subprocess, "run", return_value=subprocess.CompletedProcess([], 0, "0.8.164", "")) as run, patch.object(workbench, "verify_runtime_patch", side_effect=workbench.WorkbenchError("未安装全轨同步补丁")):
            with self.assertRaisesRegex(workbench.WorkbenchError, "全轨同步"):
                workbench.open_project(self.project, cli)
            self.assertEqual(run.call_count, 1)


if __name__ == "__main__":
    unittest.main()

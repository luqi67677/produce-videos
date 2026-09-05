from __future__ import annotations

import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from resume_project import derive  # noqa: E402


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def record(path: Path, stage: str) -> dict:
    return {
        "review_package": "content-direction",
        "status": "approved",
        "approved": True,
        "reviewed_files": [{"path": path.name, "sha256": digest(path)}],
    }


class ProjectResumeTests(unittest.TestCase):
    def test_next_step_is_derived_from_ledger(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project = Path(temp_dir)
            (project / "video-brief.md").write_text("approved", encoding="utf-8")
            script = project / "master-script.json"
            assets = project / "source-assets.json"
            script.write_text("{}", encoding="utf-8")
            assets.write_text("{}", encoding="utf-8")
            approvals = {stage: {"status": "pending", "approved": False, "reviewed_files": []} for stage in ("script", "source-assets", "assets", "storyboard", "motion")}
            approvals["script"] = record(script, "script")
            approvals["source-assets"] = record(assets, "source-assets")
            (project / "approval-ledger.json").write_text(json.dumps({"schema_version": "2.0", "workflow_mode": "standard", "approvals": approvals}), encoding="utf-8")
            result = derive(project)
            self.assertEqual(result["completed_stages"], ["script", "source-assets"])
            self.assertIn("旁白契约", result["next_action"])

    def test_changed_reviewed_file_becomes_stale(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project = Path(temp_dir)
            (project / "video-brief.md").write_text("approved", encoding="utf-8")
            script = project / "master-script.json"
            script.write_text("v1", encoding="utf-8")
            approvals = {stage: {"status": "pending", "approved": False, "reviewed_files": []} for stage in ("script", "source-assets", "assets", "storyboard", "motion")}
            approvals["script"] = record(script, "script")
            (project / "approval-ledger.json").write_text(json.dumps({"schema_version": "2.0", "workflow_mode": "standard", "approvals": approvals}), encoding="utf-8")
            script.write_text("v2", encoding="utf-8")
            result = derive(project)
            self.assertEqual(result["stages"]["script"]["status"], "stale")
            self.assertEqual(result["stages"]["script"]["changed_files"], ["master-script.json"])


if __name__ == "__main__":
    unittest.main()

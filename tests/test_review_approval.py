import hashlib
import json
import tempfile
import unittest
from pathlib import Path
import sys


SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from validate_review_approval import validate  # noqa: E402


class ReviewApprovalTest(unittest.TestCase):
    def write_case(self, message="基本上可以了", fallback=True):
        temporary = tempfile.TemporaryDirectory()
        root = Path(temporary.name)
        video = root / "sample.mp4"
        sheet = root / "contact-sheet.png"
        video.write_bytes(b"video")
        sheet.write_bytes(b"sheet")
        reviewed = [
            {"path": video.name, "sha256": hashlib.sha256(video.read_bytes()).hexdigest()},
            {"path": sheet.name, "sha256": hashlib.sha256(sheet.read_bytes()).hexdigest()},
        ]
        data = {
            "schema_version": "1.1",
            "stage": "motion",
            "status": "approved",
            "approved": True,
            "approved_at": "2026-01-01T00:00:00+08:00",
            "approved_by": "user",
            "approval_message": message,
            "review_prompt": "请确认当前动态样片；通过后进入全片渲染。",
            "approval_context": "上一条只有动态样片一个待确认问题",
            "approval_interpretation": "contextual-stage-response",
            "accepted_response_rule": "该回复紧邻动态样片确认问题",
            "review_delivery": {
                "primary_path": video.name,
                "media_type": "video",
                "directly_presented": True,
                "fallback_path": sheet.name if fallback else "",
            },
            "reviewed_files": reviewed,
        }
        approval = root / "motion-approval.json"
        approval.write_text(json.dumps(data), encoding="utf-8")
        return temporary, approval

    def test_contextual_approval_with_video_fallback_passes(self):
        temporary, approval = self.write_case()
        self.addCleanup(temporary.cleanup)
        self.assertEqual([], validate(approval, "motion", True))

    def test_non_approval_reply_fails(self):
        temporary, approval = self.write_case(message="看看")
        self.addCleanup(temporary.cleanup)
        self.assertTrue(any("不能唯一证明" in item for item in validate(approval, "motion", True)))

    def test_motion_without_contact_sheet_fails(self):
        temporary, approval = self.write_case(fallback=False)
        self.addCleanup(temporary.cleanup)
        self.assertTrue(any("联系表" in item for item in validate(approval, "motion", True)))

    def test_v2_ledger_groups_stages_without_losing_file_hashes(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        root = Path(temporary.name)
        script = root / "master-script.json"
        script.write_text("{}", encoding="utf-8")
        record = {
            "review_package": "content-direction",
            "package_scope": ["script", "source-assets"],
            "status": "approved",
            "approved": True,
            "approved_at": "2026-09-05T00:00:00+08:00",
            "approved_by": "user",
            "approval_message": "内容方向包通过",
            "review_prompt": "请确认口播和真实素材；通过后进入视觉与声音制作。",
            "approval_context": "上一条只有内容方向包一个待确认问题",
            "approval_interpretation": "explicit",
            "accepted_response_rule": "用户明确批准整个内容方向包",
            "review_delivery": {
                "primary_path": script.name,
                "media_type": "text",
                "directly_presented": True,
                "fallback_path": "",
            },
            "reviewed_files": [
                {"path": script.name, "sha256": hashlib.sha256(script.read_bytes()).hexdigest()}
            ],
        }
        ledger = root / "approval-ledger.json"
        ledger.write_text(
            json.dumps(
                {
                    "schema_version": "2.0",
                    "project": "test",
                    "workflow_mode": "fast",
                    "approvals": {"script": record, "source-assets": dict(record)},
                }
            ),
            encoding="utf-8",
        )
        self.assertEqual([], validate(ledger, "script", True, [script]))

    def test_v2_grouped_approval_requires_same_user_message(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        root = Path(temporary.name)
        script = root / "master-script.json"
        script.write_text("{}", encoding="utf-8")
        reviewed = [{"path": script.name, "sha256": hashlib.sha256(script.read_bytes()).hexdigest()}]
        base = {
            "review_package": "content-direction",
            "package_scope": ["script", "source-assets"],
            "status": "approved",
            "approved": True,
            "approved_at": "2026-09-05T00:00:00+08:00",
            "approved_by": "user",
            "approval_message": "内容和素材通过，选 B",
            "review_prompt": "请确认内容方向包。",
            "approval_context": "单一确认包",
            "approval_interpretation": "explicit",
            "accepted_response_rule": "明确批准",
            "review_delivery": {
                "primary_path": script.name,
                "media_type": "text",
                "directly_presented": True,
                "fallback_path": "",
            },
            "reviewed_files": reviewed,
        }
        source = dict(base)
        source["approval_message"] = "另一条回复"
        ledger = root / "approval-ledger.json"
        ledger.write_text(
            json.dumps(
                {
                    "schema_version": "2.0",
                    "project": "test",
                    "workflow_mode": "fast",
                    "approvals": {"script": base, "source-assets": source},
                }
            ),
            encoding="utf-8",
        )
        self.assertTrue(any("approval_message" in item for item in validate(ledger, "script", True)))

    def test_v2_ledger_requires_stage_in_package_scope(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        root = Path(temporary.name)
        script = root / "master-script.json"
        script.write_text("{}", encoding="utf-8")
        ledger = root / "approval-ledger.json"
        ledger.write_text(
            json.dumps(
                {
                    "schema_version": "2.0",
                    "project": "test",
                    "workflow_mode": "standard",
                    "approvals": {
                        "script": {
                            "review_package": "content-direction",
                            "package_scope": ["source-assets"],
                            "status": "approved",
                            "approved": True,
                            "approved_at": "2026-09-05T00:00:00+08:00",
                            "approved_by": "user",
                            "approval_message": "通过",
                            "review_prompt": "请确认内容方向包。",
                            "approval_context": "单一确认包",
                            "approval_interpretation": "explicit",
                            "accepted_response_rule": "明确批准",
                            "review_delivery": {
                                "primary_path": script.name,
                                "media_type": "text",
                                "directly_presented": True,
                                "fallback_path": "",
                            },
                            "reviewed_files": [
                                {"path": script.name, "sha256": hashlib.sha256(script.read_bytes()).hexdigest()}
                            ],
                        }
                    },
                }
            ),
            encoding="utf-8",
        )
        errors = validate(ledger, "script", True)
        self.assertTrue(any("package_scope" in item or "缺少 source-assets" in item for item in errors))


if __name__ == "__main__":
    unittest.main()

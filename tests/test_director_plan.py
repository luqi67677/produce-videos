from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
from validate_director_plan import validate  # noqa: E402
from export_director_board import render_board  # noqa: E402


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def event(eid: str, cue: str, dependencies: list[str] | None = None) -> dict:
    return {"event_id": eid, "cue_text": cue, "action": "沿箭头传递任务", "before": "等待", "after": "收到",
            "depends_on": dependencies or [], "sound": {"mode": "none", "reason": "此处需要听清旁白"}}


def asset_request(rid: str, role: str) -> dict:
    return {"request_id": rid, "role": role, "description": "按本镜说明提供素材", "preferred_source": "合法素材或自制",
            "search_queries": ["工作桌面"], "acceptance_criteria": ["不遮挡人物面部", "允许用于本视频"],
            "fallback": "缺口集中提交，确认改用程序绘图", "selected_asset_ids": []}


def shot(sid: str, segment: str, excerpt: str, events: list) -> dict:
    return {"shot_id": sid, "narration_segment_id": segment, "narration_excerpt": excerpt, "visual_duty": "展示任务发出与结果返回",
            "direction": {"audience_takeaway": "主智能体收到结果后继续判断", "estimated_duration_seconds": 4.2,
                          "visual_form": "人物近景加流程图", "composition": "人物在上，流程居中，字幕在下",
                          "camera": "镜头缓慢推近", "continuity_anchor": "主管节点位置保持一致", "transition_reason": "任务进入下一步",
                          "states": {"before": "主管持有任务", "action": "任务交给资料员", "after": "资料员开始处理"},
                          "assets_needed": [], "events": events, "subtitle_plan": "只显示本镜原文，单层字幕", "music_plan": "本镜无背景音乐"}}


class DirectorPlanTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.project = Path(self.temp.name)
        self.script = {"schema_version": "1.0", "segments": [{"scene_id": "p1", "display_text": "先交任务，再收结果。"}, {"scene_id": "p2", "display_text": "主管继续判断。"}]}
        self.write("master-script.json", self.script)
        self.data = {"schema_version": "2.6", "project": "导演计划测试",
                     "director_plan": {"schema_version": "1.0", "stage": "planning", "audience": "第一次了解智能体的人",
                                       "viewer_outcome": "分清主管与执行者的职责", "throughline": "任务发出、完成、返回",
                                       "script_binding": {"path": "master-script.json", "sha256": digest(self.project / "master-script.json")},
                                       "timing_basis": "estimated"},
                     "shots": [shot("s1", "p1", "先交任务，", [event("send", "交任务")]),
                               shot("s2", "p1", "再收结果。", [event("return", "再收"), event("arrive", "结果", ["return"])]),
                               shot("s3", "p2", "主管继续判断。", [event("judge", "判断")])]}
        direction = self.data["shots"][0]["direction"]
        direction["assets_needed"] = [asset_request("person", "人物图"), asset_request("send-sfx", "音效")]
        direction["events"][0]["sound"] = {"mode": "sfx", "reason": "强调任务已发出", "request_id": "send-sfx",
                                           "start_trigger": "任务卡离开主管", "stop_trigger": "任务卡到达执行者"}
        self.save()

    def tearDown(self) -> None:
        self.temp.cleanup()

    def write(self, name: str, value: dict) -> None:
        (self.project / name).write_text(json.dumps(value, ensure_ascii=False), encoding="utf-8")

    def save(self) -> None:
        self.write("shot-readiness.json", self.data)

    def ready(self) -> None:
        self.data["director_plan"].update(stage="ready", timing_basis="measured")
        assets = []
        for aid, basis in (("portrait", "licensed"), ("whoosh", "self-created")):
            asset = self.project / f"{aid}.bin"
            evidence = self.project / f"{aid}-rights.txt"
            asset.write_bytes(f"测试素材 {aid}".encode())
            evidence.write_text("测试授权证据：允许使用，已核查限制。", encoding="utf-8")
            assets.append({"asset_id": aid, "path": asset.name, "sha256": digest(asset),
                           "rights": {"status": "reviewed", "basis": basis,
                                      "license_name": "CC0" if basis == "licensed" else "",
                                      "source_url": "https://example.org/source" if basis == "licensed" else "",
                                      "license_url": "https://example.org/license" if basis == "licensed" else "",
                                      "evidence_path": evidence.name, "evidence_sha256": digest(evidence),
                                      "allowed_use": "本视频演示", "restrictions_review": "核查后可用于此片",
                                      "attribution": {"required": False, "text": "", "placement": ""}}})
        self.write("source-assets.json", {"items": assets})
        requests = self.data["shots"][0]["direction"]["assets_needed"]
        requests[0]["selected_asset_ids"] = ["portrait"]
        requests[1]["selected_asset_ids"] = ["whoosh"]
        clips = []
        for index, item in enumerate(self.data["shots"]):
            timed_events = []
            for event_index, planned in enumerate(item["direction"]["events"]):
                timed = {"event_id": planned["event_id"], "start_frame": 10 + event_index * 30, "end_frame": 30 + event_index * 30}
                if planned["sound"]["mode"] != "none":
                    timed["sound"] = {"start_frame": 10, "end_frame": 30, "gain_db": -18, "fade_in_ms": 40, "fade_out_ms": 80}
                timed_events.append(timed)
            clips.append({"clip_id": item["shot_id"], "scene_id": item["shot_id"], "timeline_start_seconds": index * 3,
                          "duration_seconds": 3, "narration_excerpt": item["narration_excerpt"], "semantic_events": timed_events})
        self.edl = {"schema_version": "1.1", "format": {"fps": 30}, "picture_track": clips}
        self.write("edit-decision-list.json", self.edl)
        self.save()

    def test_planning_needs_no_media_audio_or_edl(self):
        self.assertEqual(validate(self.project), [])
        self.assertFalse((self.project / "source-assets.json").exists())
        self.assertFalse((self.project / "edit-decision-list.json").exists())
        self.assertTrue(validate(self.project, require_ready=True))

    def test_ready_validates_without_rendering(self):
        self.ready()
        self.assertEqual(validate(self.project, require_ready=True), [])

    def test_legacy_optional_but_explicit_ready_requires_extension(self):
        self.data.pop("director_plan")
        self.save()
        self.assertEqual(validate(self.project), [])
        self.assertTrue(validate(self.project, True))
        with self.assertRaises(ValueError):
            render_board(self.project)

    def test_unknown_extension_version_and_wrong_base_version_rejected(self):
        self.data["director_plan"]["schema_version"] = "99"
        self.save()
        self.assertTrue(validate(self.project))
        self.data["director_plan"]["schema_version"] = "1.0"
        self.data["schema_version"] = "2.7"
        self.save()
        self.assertTrue(validate(self.project))

    def test_approved_text_missing_rewritten_duplicated_or_reordered_rejected(self):
        original = copy.deepcopy(self.data)
        cases = [lambda d: d["shots"].pop(),
                 lambda d: d["shots"][0].update(narration_excerpt="交任务，"),
                 lambda d: d["shots"][0].update(narration_excerpt="先交任务，先交任务，"),
                 lambda d: d["shots"].reverse(),
                 lambda d: d["shots"].insert(2, d["shots"].pop(0))]
        for mutate in cases:
            with self.subTest(mutate=mutate):
                self.data = copy.deepcopy(original)
                mutate(self.data)
                self.save()
                self.assertTrue(validate(self.project))

    def test_script_hash_and_unique_script_path_verified(self):
        self.script["segments"][0]["display_text"] = "改过的稿子。"
        self.write("master-script.json", self.script)
        self.assertTrue(any("SHA-256" in e for e in validate(self.project)))
        self.write("another-script.json", self.script)
        self.data["director_plan"]["script_binding"] = {"path": "another-script.json", "sha256": digest(self.project / "another-script.json")}
        self.save()
        self.assertTrue(any("唯一" in e for e in validate(self.project)))

    def test_estimated_and_measured_cannot_be_confused(self):
        self.data["director_plan"]["timing_basis"] = "measured"
        self.save()
        self.assertTrue(validate(self.project))
        self.ready()
        self.data["director_plan"]["timing_basis"] = "estimated"
        self.save()
        self.assertTrue(validate(self.project))

    def test_cue_global_id_and_local_dependency_checked(self):
        original = copy.deepcopy(self.data)
        cases = [lambda d: d["shots"][0]["direction"]["events"][0].update(cue_text="不存在的词"),
                 lambda d: d["shots"][1]["direction"]["events"][0].update(event_id="send"),
                 lambda d: d["shots"][1]["direction"]["events"][0].update(depends_on=["arrive"]),
                 lambda d: d["shots"][1]["direction"]["events"][0].update(depends_on=["send"])]
        for mutate in cases:
            with self.subTest(mutate=mutate):
                self.data = copy.deepcopy(original)
                mutate(self.data)
                self.save()
                self.assertTrue(validate(self.project))

    def test_sfx_must_reference_a_declared_asset_request(self):
        self.data["shots"][0]["direction"]["events"][0]["sound"]["request_id"] = "missing"
        self.save()
        self.assertTrue(validate(self.project))

    def test_ready_rejects_unresolved_or_unregistered_asset(self):
        self.ready()
        request = self.data["shots"][0]["direction"]["assets_needed"][0]
        for selected in ([], ["missing"]):
            with self.subTest(selected=selected):
                request["selected_asset_ids"] = selected
                self.save()
                self.assertTrue(validate(self.project))

    def test_rights_evidence_file_and_hash_checked_for_self_created(self):
        self.ready()
        evidence = self.project / "whoosh-rights.txt"
        evidence.write_text("证据变化", encoding="utf-8")
        self.assertTrue(any("SHA-256" in e for e in validate(self.project)))
        evidence.unlink()
        self.assertTrue(any("证据" in e and "不存在" in e for e in validate(self.project)))

    def test_media_hash_and_license_urls_checked(self):
        self.ready()
        (self.project / "portrait.bin").write_bytes(b"changed")
        self.assertTrue(any("SHA-256" in e for e in validate(self.project)))
        self.ready()
        source = json.loads((self.project / "source-assets.json").read_text())
        source["items"][0]["rights"]["license_url"] = "http://example.org/license"
        self.write("source-assets.json", source)
        self.assertTrue(any("HTTPS" in e for e in validate(self.project)))

    def test_required_attribution_needs_copy_and_placement(self):
        self.ready()
        source = json.loads((self.project / "source-assets.json").read_text())
        source["items"][0]["rights"]["attribution"]["required"] = True
        self.write("source-assets.json", source)
        self.assertTrue(any("attribution" in e for e in validate(self.project)))

    def test_sfx_cannot_precede_visual_action_but_can_have_a_natural_tail(self):
        self.ready()
        path = self.project / "edit-decision-list.json"
        edl = json.loads(path.read_text(encoding="utf-8"))
        timed = edl["picture_track"][0]["semantic_events"][0]
        timed["sound"]["start_frame"] = timed["start_frame"] - 1
        self.write("edit-decision-list.json", edl)
        self.assertTrue(any("音效不能早于" in error for error in validate(self.project, require_ready=True)))
        timed["sound"].update(start_frame=timed["start_frame"], end_frame=timed["end_frame"] + 10)
        self.write("edit-decision-list.json", edl)
        self.assertEqual(validate(self.project, require_ready=True), [])
        # 环境声有自己的完整事件，先铺声场再出现其他动作，不必借别的动作偷跑。
        self.data["shots"][0]["direction"]["events"][0]["sound"]["mode"] = "ambience"
        timed["start_frame"] = 0
        timed["sound"]["start_frame"] = 0
        self.save()
        self.write("edit-decision-list.json", edl)
        self.assertEqual(validate(self.project, require_ready=True), [])

    def test_event_frame_bounds_dependencies_and_sound_duration_checked(self):
        self.ready()
        original = copy.deepcopy(self.edl)
        cases = [lambda e: e["picture_track"][0]["semantic_events"][0].update(end_frame=91),
                 lambda e: e["picture_track"][1]["semantic_events"][1].update(start_frame=29),
                 lambda e: e["picture_track"][0]["semantic_events"][0]["sound"].update(end_frame=100),
                 lambda e: e["picture_track"][0]["semantic_events"][0]["sound"].update(fade_in_ms=9999),
                 lambda e: e["picture_track"][0]["semantic_events"][0]["sound"].update(gain_db=float("nan")),
                 lambda e: e["picture_track"][0]["semantic_events"][0].update(start_frame=True)]
        for mutate in cases:
            with self.subTest(mutate=mutate):
                changed = copy.deepcopy(original)
                mutate(changed)
                self.write("edit-decision-list.json", changed)
                self.assertTrue(validate(self.project))

    def test_event_mapping_and_silent_events_checked(self):
        self.ready()
        original = copy.deepcopy(self.edl)
        cases = [lambda e: e["picture_track"][1]["semantic_events"].pop(),
                 lambda e: e["picture_track"][1]["semantic_events"].reverse(),
                 lambda e: e["picture_track"][1]["semantic_events"][0].update(sound={}),
                 lambda e: e["picture_track"][0]["semantic_events"][0].pop("sound"),
                 lambda e: e["picture_track"][1].update(clip_id="s1")]
        for mutate in cases:
            with self.subTest(mutate=mutate):
                changed = copy.deepcopy(original)
                mutate(changed)
                self.write("edit-decision-list.json", changed)
                self.assertTrue(validate(self.project))

    def test_malformed_types_report_errors_without_crashing(self):
        original = copy.deepcopy(self.data)
        cases = [lambda d: d["director_plan"].update(stage=[]),
                 lambda d: d["shots"][0]["direction"]["events"][0]["sound"].update(mode=[]),
                 lambda d: d["shots"][0]["direction"].update(estimated_duration_seconds=True),
                 lambda d: d["shots"][0]["direction"]["events"][0].update(depends_on=[{}]),
                 lambda d: d["shots"][0]["direction"]["assets_needed"][0].update(selected_asset_ids=[{}])]
        for mutate in cases:
            with self.subTest(mutate=mutate):
                self.data = copy.deepcopy(original)
                mutate(self.data)
                self.save()
                self.assertTrue(validate(self.project))

    def test_export_planning_shows_estimate_and_every_director_area(self):
        before = (self.project / "shot-readiness.json").read_bytes()
        board = render_board(self.project)
        for value in ("预计 4.2 秒", "画面组合", "构图与元素", "运镜", "连续性锚点", "字幕方案", "音乐方案", "素材需求", "动效与声音事件", "开始：", "停止：", "待解决"):
            self.assertIn(value, board)
        self.assertNotIn("实测 0.000", board)
        self.assertEqual(before, (self.project / "shot-readiness.json").read_bytes())

    def test_export_ready_uses_edl_instead_of_estimates(self):
        self.ready()
        board = render_board(self.project, require_ready=True)
        self.assertIn("实测 0.000–3.000 秒", board)
        self.assertIn("本镜相对帧", board)
        self.assertNotIn("预计 4.2", board)

    def test_cli_exports_md_and_refuses_json_output(self):
        output = self.project / "review" / "board.md"
        result = subprocess.run([sys.executable, str(SCRIPTS / "export_director_board.py"), str(self.project), "--output", str(output)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertTrue(output.is_file())
        original = (self.project / "master-script.json").read_bytes()
        result = subprocess.run([sys.executable, str(SCRIPTS / "export_director_board.py"), str(self.project), "--output", str(self.project / "master-script.json")], capture_output=True, text=True)
        self.assertEqual(result.returncode, 1)
        self.assertEqual(original, (self.project / "master-script.json").read_bytes())


if __name__ == "__main__":
    unittest.main()

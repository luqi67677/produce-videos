"""核验运行时补丁的版本、完整性和失败恢复。"""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

SPEC = importlib.util.spec_from_file_location("runtime_patch", Path(__file__).parents[1] / "scripts/workbench_runtime_patch.py")
runtime_patch = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(runtime_patch)


class RuntimePatchTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name).resolve()
        self.runtime = self.root / "runtime"
        self.assets = self.root / "assets"
        self.runtime.mkdir()
        self.assets.mkdir()
        (self.runtime / "package.json").write_text(json.dumps({"name": "hyperframes", "version": "0.8.164"}))
        (self.runtime / "a.js").write_text("original")
        (self.assets / "extra.js").write_text("module")
        self.manifest = {"patch_id": runtime_patch.PATCH_ID, "version": runtime_patch.VERSION, "files": [
            {"path": "a.js", "before_sha256": runtime_patch.digest(b"original"), "after_sha256": runtime_patch.digest(b"patched"), "replacements": [{"before": "original", "after": "patched"}]},
            {"path": "extra.js", "before_sha256": None, "after_sha256": runtime_patch.digest(b"module"), "payload": "extra.js"},
        ]}
        self.save_manifest()

    def tearDown(self):
        self.temp.cleanup()

    def save_manifest(self):
        (self.assets / "manifest.json").write_text(json.dumps(self.manifest))

    def apply(self, **kwargs):
        return runtime_patch.patch_runtime(self.runtime, assets=self.assets, **kwargs)

    def test_apply_check_and_idempotence(self):
        with self.assertRaises(runtime_patch.PatchError):
            self.apply(check=True)
        self.assertEqual(self.apply()["changed_files"], 2)
        self.assertEqual((self.runtime / "a.js").read_text(), "patched")
        self.assertEqual(self.apply()["changed_files"], 0)
        self.assertEqual(self.apply(check=True)["verified"], True)

    def test_unknown_hash_blocks_all_writes(self):
        (self.runtime / "extra.js").write_text("unrecognized")
        with self.assertRaisesRegex(runtime_patch.PatchError, "未知文件哈希"):
            self.apply()
        self.assertEqual((self.runtime / "a.js").read_text(), "original")

    def test_verified_upgrade_and_unknown_upgrade_are_distinct(self):
        self.manifest["files"][0]["upgrades"] = [{"before_sha256": runtime_patch.digest(b"old-patched"), "replacements": [{"before": "old-patched", "after": "patched"}]}]
        self.save_manifest()
        (self.runtime / "a.js").write_text("old-patched")
        self.assertEqual(self.apply()["changed_files"], 2)
        self.assertEqual((self.runtime / "a.js").read_text(), "patched")

    def test_private_brand_preserved_and_never_copies_profile_fields(self):
        self.manifest["private_brand"] = True
        self.save_manifest()
        path = self.runtime / runtime_patch.BRAND_PATH
        path.parent.mkdir(parents=True)
        self.apply(brand={"name": "示例视频", "mark": "示例", "private_voice": "do-not-copy"})
        self.assertNotIn("do-not-copy", path.read_text())
        self.assertEqual(self.apply()["changed_files"], 0)
        self.assertEqual(runtime_patch.read_installed_brand(path.read_bytes())["name"], "示例视频")
        self.assertTrue(self.apply(check=True)["verified"])
        self.apply(brand={"name": "另一工作台", "mark": "新"})
        self.assertEqual(runtime_patch.read_installed_brand(path.read_bytes())["mark"], "新")

    def test_unknown_brand_script_blocks_all_writes(self):
        self.manifest["private_brand"] = True
        self.save_manifest()
        path = self.runtime / runtime_patch.BRAND_PATH
        path.parent.mkdir(parents=True)
        path.write_text('alert("unexpected")')
        with self.assertRaisesRegex(runtime_patch.PatchError, "有效文件"):
            self.apply()
        self.assertEqual((self.runtime / "a.js").read_text(), "original")

    def test_brand_marks_escape_svg_and_reject_control_characters(self):
        value = {"name": '文字"<测试>', "mark": '<&>'}
        script = runtime_patch.brand_script(value)
        self.assertEqual(runtime_patch.read_installed_brand(script), value)
        self.assertIn(b'&lt;&amp;&gt;', script)
        with self.assertRaises(runtime_patch.PatchError):
            runtime_patch.brand_script({"name": "多\n行", "mark": "字"})

    def test_payload_tamper_blocks_all_writes(self):
        (self.assets / "extra.js").write_text("tampered")
        with self.assertRaisesRegex(runtime_patch.PatchError, "哈希不匹配"):
            self.apply()
        self.assertEqual((self.runtime / "a.js").read_text(), "original")

    def test_write_failure_restores_previous_files(self):
        real_write = runtime_patch.atomic_write
        def fail_second(path, data, mode):
            if path.name == "extra.js":
                raise OSError("simulated write failure")
            real_write(path, data, mode)
        with patch.object(runtime_patch, "atomic_write", side_effect=fail_second):
            with self.assertRaises(OSError):
                self.apply()
        self.assertEqual((self.runtime / "a.js").read_text(), "original")
        self.assertFalse((self.runtime / "extra.js").exists())

    def test_rollback_preserves_concurrent_edits(self):
        real_write = runtime_patch.atomic_write
        def fail_second(path, data, mode):
            if path.name == "extra.js":
                (self.runtime / "a.js").write_text("concurrent edit")
                raise OSError("simulated write failure")
            real_write(path, data, mode)
        with patch.object(runtime_patch, "atomic_write", side_effect=fail_second):
            with self.assertRaisesRegex(runtime_patch.PatchError, "保留当前内容"):
                self.apply()
        self.assertEqual((self.runtime / "a.js").read_text(), "concurrent edit")

    def test_rejects_version_path_escape_and_symlink(self):
        package = self.runtime / "package.json"
        package.write_text('{"name":"hyperframes","version":"0.8.165"}')
        with self.assertRaisesRegex(runtime_patch.PatchError, "仅支持"):
            self.apply()
        package.write_text('{"name":"hyperframes","version":"0.8.164"}')
        self.manifest["files"][0]["path"] = "../outside.js"
        self.save_manifest()
        with self.assertRaisesRegex(runtime_patch.PatchError, "越界"):
            self.apply()
        self.manifest["files"][0]["path"] = "a.js"
        self.save_manifest()
        (self.runtime / "a.js").unlink()
        (self.runtime / "a.js").symlink_to(self.assets / "extra.js")
        with self.assertRaisesRegex(runtime_patch.PatchError, "符号链接"):
            self.apply()


if __name__ == "__main__":
    unittest.main()

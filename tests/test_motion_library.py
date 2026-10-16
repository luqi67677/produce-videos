"""内置动效注册与资源完整性：真实执行、登记后依赖改动、上游协议注释例外。"""
from __future__ import annotations
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from register_motion_library import register
from director_plan_resources import verify_effect
from scan_release import scan, DEFAULT_BANNED


class MotionLibraryTests(unittest.TestCase):
    def test_wrong_implementation_path_or_entrypoint_stops_before_execution(self):
        for field, value in (('path', 'preview.html'),
                             ('entrypoint', 'createMotionPreset:missing')):
            with self.subTest(field=field), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp) / 'skill'; project = Path(tmp) / 'project'; project.mkdir()
                library = root / 'assets/motion-library'; library.mkdir(parents=True)
                manifest = json.loads((ROOT / 'assets/motion-library/library-manifest.json').read_text())
                manifest['effects'][0]['implementation'][field] = value
                (library / 'library-manifest.json').write_text(json.dumps(manifest))
                # 错误路径即使指向真实文件，也不能借固定模块的测试得到证明。
                (library / 'preview.html').write_text('<html>existing</html>')
                with mock.patch('register_motion_library.subprocess.run') as run:
                    with self.assertRaisesRegex(ValueError, '实现路径或入口'):
                        register(project, root)
                    run.assert_not_called()
                self.assertFalse((project / 'motion-library').exists())

    def test_manifest_version_must_match_executed_report(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / 'skill'; project = Path(tmp) / 'project'; project.mkdir()
            shutil.copytree(ROOT / 'assets/motion-library', root / 'assets/motion-library')
            path = root / 'assets/motion-library/library-manifest.json'
            manifest = json.loads(path.read_text())
            executed_version = manifest['version']
            manifest['version'] = executed_version + '-changed'
            path.write_text(json.dumps(manifest))
            report = {'passed': True, 'version': executed_version,
                      'effects': [{'effectId': item['id'], 'passed': True} for item in manifest['effects']]}
            result = subprocess.CompletedProcess([], 0, json.dumps(report), '')
            with mock.patch('register_motion_library.shutil.which', return_value='node'), \
                    mock.patch('register_motion_library.subprocess.run', return_value=result):
                with self.assertRaisesRegex(ValueError, '清单版本与实际执行报告版本不一致'):
                    register(project, root)
            self.assertFalse((project / 'motion-library').exists())

    def test_report_must_explicitly_pass_overall_even_if_effects_pass(self):
        for status in (False, None, 1):
            with self.subTest(status=status), tempfile.TemporaryDirectory() as tmp:
                project = Path(tmp)
                manifest = json.loads((ROOT / 'assets/motion-library/library-manifest.json').read_text())
                report = {'passed': status, 'version': manifest['version'],
                          'effects': [{'effectId': item['id'], 'passed': True} for item in manifest['effects']]}
                result = subprocess.CompletedProcess([], 0, json.dumps(report), '')
                with mock.patch('register_motion_library.shutil.which', return_value='node'), \
                        mock.patch('register_motion_library.subprocess.run', return_value=result):
                    with self.assertRaisesRegex(ValueError, '执行报告未整体通过'):
                        register(project)
                self.assertFalse((project / 'motion-library').exists())

    def test_actual_registration_does_not_edit_plan_and_revalidates_dependencies(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            plan = project / 'shot-readiness.json'
            plan.write_text('{"unchanged":true}')
            target = register(project)
            self.assertEqual(plan.read_text(), '{"unchanged":true}')
            catalog = json.loads(target.read_text())
            self.assertEqual(len(catalog), 8)
            self.assertTrue(all(item['visual_review'] == 'pending' for item in catalog))
            for item in catalog:
                errors = []
                verify_effect(project, item, errors)
                self.assertEqual(errors, [])
            dependency = project / 'changed-dependency.js'
            dependency.write_text('changed')
            item = catalog[0]
            item['implementation']['dependencies'][0]['path'] = str(dependency)
            errors = []
            verify_effect(project, item, errors)
            self.assertTrue(any('SHA-256' in error for error in errors), errors)

    def test_upstream_tamper_stops_before_execution(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / 'skill'; project = Path(tmp) / 'project'; project.mkdir()
            shutil.copytree(ROOT / 'assets/motion-library', root / 'assets/motion-library')
            vendor = root / 'assets/motion-library/vendor/animejs/anime.esm.min.js'
            vendor.write_text(vendor.read_text() + '\n// changed\n')
            with mock.patch('register_motion_library.subprocess.run') as run:
                with self.assertRaisesRegex(ValueError, '上游文件发生变化'):
                    register(project, root)
                run.assert_not_called()
            self.assertFalse((project / 'motion-library').exists())

    def test_protocol_exception_is_pinned_to_original_bytes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            relative = Path('assets/motion-library/vendor/three/three.core.js')
            target = root / relative; target.parent.mkdir(parents=True)
            shutil.copyfile(ROOT / relative, target)
            self.assertEqual(scan(root, DEFAULT_BANNED, True), [])
            target.write_text(target.read_text() + '\n// changed\n')
            self.assertTrue(any('文本包含禁止标识' in error for error in scan(root, DEFAULT_BANNED, True)))


if __name__ == '__main__':
    unittest.main()

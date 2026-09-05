from __future__ import annotations

import sys
import tempfile
import unittest
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from package_workbuddy import build_package, split_frontmatter  # noqa: E402


class AgentCompatibilityTests(unittest.TestCase):
    def test_canonical_frontmatter_stays_portable(self) -> None:
        content = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        frontmatter, _ = split_frontmatter(content)
        keys = {line.split(":", 1)[0] for line in frontmatter.splitlines() if ":" in line}
        self.assertEqual(keys, {"name", "description"})

    def test_readme_has_copyable_install_prompt_and_platform_routes(self) -> None:
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("请帮我安装并验证这个开源视频 Skill", readme)
        self.assertIn("Kimi Code CLI", readme)
        self.assertIn("WorkBuddy", readme)
        self.assertIn("不要假装安装成功", readme)
        self.assertIn("普通 Kimi 聊天网页", readme)

    def test_workbuddy_package_has_required_schema_and_resources(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output = Path(temp_dir) / "produce-videos-workbuddy.zip"
            count = build_package(ROOT, output)
            self.assertGreater(count, 10)

            with zipfile.ZipFile(output) as archive:
                names = set(archive.namelist())
                skill_path = "skills/produce-videos/SKILL.md"
                self.assertIn(skill_path, names)
                self.assertTrue(any(name.startswith("skills/produce-videos/scripts/") for name in names))
                self.assertTrue(any(name.startswith("skills/produce-videos/references/") for name in names))
                self.assertTrue(any(name.startswith("skills/produce-videos/assets/") for name in names))
                self.assertFalse(any("/.git/" in name for name in names))

                content = archive.read(skill_path).decode("utf-8")
                frontmatter, _ = split_frontmatter(content)
                for field in ("description_zh:", "description_en:", "version:", "author:"):
                    self.assertIn(field, frontmatter)


if __name__ == "__main__":
    unittest.main()

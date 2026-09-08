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

    def test_readme_has_agent_first_install_entry_and_platform_routes(self) -> None:
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        install_prompt = (
            "请把这个视频 Skill 安装到你当前使用的 AI，并验证安装成功："
            "https://github.com/luqi67677/produce-videos"
        )
        install_section = readme.split("## 安装", 1)[1].split("## 安装后怎么使用", 1)[0]
        self.assertIn(install_prompt, install_section)
        self.assertLess(install_section.index(install_prompt), install_section.index("npx skills add"))
        self.assertIn("用户不需要打开终端，也不需要选择安装平台", install_section)
        self.assertNotIn("在终端运行 `npx skills add", readme)
        self.assertNotIn("按提示选择本地 Agent", readme)
        self.assertIn("Kimi Code CLI", readme)
        self.assertIn("WorkBuddy", readme)
        self.assertIn("普通 Kimi 聊天网页", readme)
        self.assertIn("GitHub Releases", readme)
        self.assertIn("34 套视觉主题和 88 套结构化布局", readme)
        self.assertIn("scripts/doctor.py", readme)
        self.assertIn("scripts/resume_project.py", readme)
        self.assertIn("Zara Zhang 的 Frontend Slides", readme)

    def test_agent_install_contract_is_noninteractive_and_platform_specific(self) -> None:
        content = (ROOT / "INSTALL_FOR_AGENTS.md").read_text(encoding="utf-8")
        self.assertIn("不要让用户打开终端", content)
        self.assertIn("不要再问用户“安装到哪个平台”", content)
        expected_commands = {
            "codex": "npx skills add luqi67677/produce-videos -g -a codex -y",
            "claude-code": "npx skills add luqi67677/produce-videos -g -a claude-code -y",
            "cursor": "npx skills add luqi67677/produce-videos -g -a cursor -y",
            "kimi-code-cli": "npx skills add luqi67677/produce-videos -g -a kimi-code-cli -y",
        }
        for command in expected_commands.values():
            self.assertEqual(content.count(command), 1)
        self.assertIn("只执行与当前 Agent 对应的一条", content)

    def test_skill_declares_v250_and_fine_shot_contract(self) -> None:
        content = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("V2.5.0", content)
        self.assertIn("每个 B-roll 必须填写 `covers`", content)
        self.assertIn("edit-decision-list.json", content)
        self.assertIn("story-contract.json", content)
        self.assertIn("validate_timeline_sync.py", content)
        self.assertIn("validate_cover_contract.py", content)
        self.assertIn("character-profile.json", content)
        self.assertIn("platform-overlay-profiles.json", content)

    def test_third_party_notices_credit_frontend_slides_sources(self) -> None:
        notices = (ROOT / "THIRD_PARTY_NOTICES.md").read_text(encoding="utf-8")
        self.assertIn("Zara Zhang", notices)
        self.assertIn("zarazhangrui/frontend-slides", notices)
        self.assertIn("dreamid27/frontend-slides", notices)

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
                self.assertIn("skills/produce-videos/examples/README.md", names)
                self.assertTrue(any(name.startswith("skills/produce-videos/examples/thumbnails/") for name in names))
                self.assertFalse(any("examples/videos/" in name for name in names))
                self.assertFalse(any("/.git/" in name for name in names))

                content = archive.read(skill_path).decode("utf-8")
                frontmatter, _ = split_frontmatter(content)
                for field in ("description_zh:", "description_en:", "version:", "author:"):
                    self.assertIn(field, frontmatter)


if __name__ == "__main__":
    unittest.main()

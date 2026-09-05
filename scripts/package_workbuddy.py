#!/usr/bin/env python3
"""Build a WorkBuddy-uploadable ZIP from the canonical Agent Skill source."""

from __future__ import annotations

import argparse
import re
import zipfile
from pathlib import Path


SKIP_PARTS = {".git", "__pycache__", ".pytest_cache"}
SKIP_NAMES = {".DS_Store"}


def split_frontmatter(content: str) -> tuple[str, str]:
    if not content.startswith("---\n"):
        raise ValueError("SKILL.md 缺少 YAML frontmatter")
    end = content.find("\n---\n", 4)
    if end < 0:
        raise ValueError("SKILL.md frontmatter 未正确结束")
    return content[4:end], content[end + 5 :]


def read_version(body: str) -> str:
    match = re.search(r"^版本：V(\d+\.\d+\.\d+)$", body, re.MULTILINE)
    if not match:
        raise ValueError("SKILL.md 正文缺少语义化版本号")
    return match.group(1)


def workbuddy_skill_md(content: str) -> str:
    frontmatter, body = split_frontmatter(content)
    version = read_version(body)
    extra = [
        'display_name: "视频生成与编辑"',
        'display_name_en: "Produce Videos"',
        'description_zh: "把文字和已有素材制作成经过逐步确认与质量检查的视频和独立封面"',
        'description_en: "Turn scripts and source assets into reviewable, quality-gated videos and covers."',
        f'version: "{version}"',
        'author: "produce-videos contributors"',
    ]
    return "---\n" + frontmatter.rstrip() + "\n" + "\n".join(extra) + "\n---\n" + body


def should_skip(path: Path, output: Path) -> bool:
    if path.resolve() == output.resolve():
        return True
    if any(part in SKIP_PARTS for part in path.parts):
        return True
    return path.name in SKIP_NAMES or path.suffix == ".pyc"


def build_package(skill_root: Path, output: Path) -> int:
    skill_root = skill_root.resolve()
    output = output.resolve()
    skill_md = skill_root / "SKILL.md"
    if not skill_md.is_file():
        raise FileNotFoundError(f"未找到 {skill_md}")

    output.parent.mkdir(parents=True, exist_ok=True)
    prefix = Path("skills") / "produce-videos"
    count = 0
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(skill_root.rglob("*")):
            if not path.is_file() or path.is_symlink() or should_skip(path, output):
                continue
            relative = path.relative_to(skill_root)
            arcname = str(prefix / relative)
            if relative == Path("SKILL.md"):
                content = workbuddy_skill_md(path.read_text(encoding="utf-8"))
                archive.writestr(arcname, content)
            else:
                archive.write(path, arcname)
            count += 1
    return count


def main() -> int:
    parser = argparse.ArgumentParser(description="生成可上传到 WorkBuddy 的 produce-videos ZIP")
    parser.add_argument("--output", type=Path, required=True, help="输出 ZIP 路径")
    args = parser.parse_args()
    skill_root = Path(__file__).resolve().parents[1]
    count = build_package(skill_root, args.output)
    print(f"PASS 已生成 WorkBuddy 安装包：{args.output.resolve()}（{count} 个文件）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Validate the bundled style-neutral layout preset catalog."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


EXPECTED_LAYOUTS = 88
VALID_SLOTS = {
    "agenda", "case", "chart", "closing", "comparison", "definition",
    "gallery", "image", "list", "opening", "pricing", "process", "prose",
    "qa", "quote", "risk", "roadmap", "section", "spec", "stats", "team",
    "timeline", "video",
}


def frontmatter_value(content: str, key: str) -> str:
    match = re.search(rf"^{re.escape(key)}:\s*(.+?)\s*$", content, re.MULTILINE)
    return match.group(1).strip().strip('"\'') if match else ""


def validate(root: Path, expected: int = EXPECTED_LAYOUTS) -> list[str]:
    errors: list[str] = []
    if not root.is_dir():
        return [f"布局目录不存在：{root}"]
    readme = root / "README.md"
    license_path = root / "LICENSE"
    source = root / "source.json"
    for path in (readme, license_path, source):
        if not path.is_file():
            errors.append(f"布局库缺少：{path.name}")

    specs = sorted(root.glob("*/*/layout.md"))
    if len(specs) != expected:
        errors.append(f"布局数量应为 {expected}，实际为 {len(specs)}")

    names: set[str] = set()
    ids: set[str] = set()
    readme_text = readme.read_text(encoding="utf-8") if readme.is_file() else ""
    for spec in specs:
        preset_id = spec.parent.relative_to(root).as_posix()
        content = spec.read_text(encoding="utf-8")
        slot = frontmatter_value(content, "slot")
        name = frontmatter_value(content, "name")
        version = frontmatter_value(content, "version")
        if preset_id in ids:
            errors.append(f"布局 ID 重复：{preset_id}")
        ids.add(preset_id)
        if name in names:
            errors.append(f"布局名称重复：{name}")
        names.add(name)
        if not name or not version:
            errors.append(f"{preset_id} 缺少 name 或 version")
        if slot not in VALID_SLOTS or slot != spec.parent.parent.name:
            errors.append(f"{preset_id} 的 slot 与目录不一致")
        preview = spec.with_name("preview.html")
        if not preview.is_file():
            errors.append(f"{preset_id} 缺少 preview.html")
        for heading in ("## Geometry", "## Content constraints (hard limits)", "## Failure modes to avoid"):
            if heading not in content:
                errors.append(f"{preset_id} 缺少章节：{heading}")
        relative = spec.relative_to(root).as_posix()
        if relative not in readme_text:
            errors.append(f"README 索引未登记：{relative}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="校验 88 套结构化版式及预览")
    parser.add_argument(
        "root",
        nargs="?",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "references/frontend-slides-layouts",
    )
    parser.add_argument("--expected", type=int, default=EXPECTED_LAYOUTS)
    args = parser.parse_args()
    errors = validate(args.root.expanduser().resolve(), args.expected)
    if errors:
        for error in errors:
            print(f"FAIL {error}")
        return 1
    print(f"PASS 布局目录完整：{args.expected} 套结构、规格和真实预览一一对应")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

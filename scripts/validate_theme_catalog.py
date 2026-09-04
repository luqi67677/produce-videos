#!/usr/bin/env python3
"""验证 34 套主题索引、目录与中英文设计说明完整可用。"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


EXPECTED_TEMPLATE_COUNT = 34
REQUIRED_FIELDS = {
    "slug",
    "name",
    "tagline",
    "mood",
    "tone",
    "formality",
    "density",
    "scheme",
    "best_for",
    "avoid_for",
    "preview_md",
    "design_md",
}
REQUIRED_PREVIEW_HEADINGS = {
    "## Files",
    "## Selection Metadata",
    "## Visual Snapshot",
    "## Preview Ingredients",
    "## International / CJK Preview Note",
    "## Preview Rules",
}
REQUIRED_DESIGN_HEADINGS = {
    "## Frontend Slides Fixed-Stage Policy",
    "## Overview",
    "## Colors",
    "## Typography",
    "## Layout",
    "## Shapes and Treatment",
    "## Do's and Don'ts",
    "## Responsive Behavior",
    "## CJK & International Content",
    "## Iteration Guide",
    "## Known Gaps",
}


def nonempty(value: Any) -> bool:
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, list):
        return bool(value) and all(isinstance(item, str) and item.strip() for item in value)
    return value is not None


def resolve_catalog_path(index_path: Path, value: str) -> Path:
    candidate = Path(value)
    if candidate.is_absolute():
        return candidate.resolve()
    return (index_path.parent.parent / candidate).resolve()


def headings(content: str, level: str = "##") -> set[str]:
    return {line.strip() for line in content.splitlines() if line.startswith(f"{level} ")}


def validate(index_path: Path) -> list[str]:
    try:
        data = json.loads(index_path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return [f"主题索引不存在：{index_path}"]
    except (OSError, json.JSONDecodeError) as exc:
        return [f"主题索引无法解析：{exc}"]
    if not isinstance(data, dict):
        return ["主题索引必须为 JSON 对象"]
    errors: list[str] = []
    templates = data.get("templates")
    if not isinstance(templates, list):
        return ["templates 必须为数组"]
    if data.get("template_count") != EXPECTED_TEMPLATE_COUNT or len(templates) != EXPECTED_TEMPLATE_COUNT:
        errors.append(f"主题库必须完整包含 {EXPECTED_TEMPLATE_COUNT} 套模板")
    seen: set[str] = set()
    indexed_dirs: set[Path] = set()
    for index, item in enumerate(templates):
        label = f"templates[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{label} 必须为对象")
            continue
        missing = sorted(field for field in REQUIRED_FIELDS if not nonempty(item.get(field)))
        if missing:
            errors.append(f"{label} 缺少字段：{', '.join(missing)}")
        slug = str(item.get("slug", "")).strip()
        if not slug or slug in seen:
            errors.append(f"{label} 缺少唯一 slug")
        seen.add(slug)
        preview = resolve_catalog_path(index_path, str(item.get("preview_md", "")))
        design = resolve_catalog_path(index_path, str(item.get("design_md", "")))
        if preview.parent != design.parent or preview.parent.name != slug:
            errors.append(f"{slug or label} 的索引路径与模板目录不一致")
        indexed_dirs.add(preview.parent)
        for path, kind, minimum, required in (
            (preview, "preview.md", 2500, REQUIRED_PREVIEW_HEADINGS),
            (design, "design.md", 20000, REQUIRED_DESIGN_HEADINGS),
        ):
            if not path.is_file():
                errors.append(f"{slug or label} 缺少 {kind}")
                continue
            content = path.read_text(encoding="utf-8")
            if len(content.encode("utf-8")) < minimum:
                errors.append(f"{slug or label} 的 {kind} 内容过少，不能作为完整主题规范")
            missing_headings = sorted(required - headings(content))
            if missing_headings:
                errors.append(f"{slug or label} 的 {kind} 缺少章节：{', '.join(missing_headings)}")
            if kind == "design.md" and not {"## Depth and Elevation", "## Elevation and Depth"} & headings(content):
                errors.append(f"{slug or label} 的 design.md 缺少层次与景深章节")
    templates_root = index_path.parent / "templates"
    actual_dirs = {path.resolve() for path in templates_root.iterdir() if path.is_dir()} if templates_root.is_dir() else set()
    if actual_dirs != indexed_dirs:
        missing = sorted(path.name for path in actual_dirs - indexed_dirs)
        extra = sorted(path.name for path in indexed_dirs - actual_dirs)
        if missing:
            errors.append(f"存在未进入索引的模板目录：{', '.join(missing)}")
        if extra:
            errors.append(f"索引指向不存在的模板目录：{', '.join(extra)}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="验证 34 套视频主题模板目录")
    parser.add_argument("index", type=Path)
    args = parser.parse_args()
    errors = validate(args.index.expanduser().resolve())
    if errors:
        for error in errors:
            print(f"FAIL {error}")
        return 1
    print("PASS 34 套主题均已入索引，预览与设计规范完整，包含 CJK 和已知限制说明")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

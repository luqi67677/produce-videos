#!/usr/bin/env python3
"""Validate the single source of truth for a video's visual theme."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


HEX_COLOR = re.compile(r"^#[0-9A-Fa-f]{6}$")
PALETTE_KEYS = (
    "background",
    "surface",
    "text_primary",
    "text_inverse",
    "accent_primary",
    "accent_secondary",
    "highlight",
    "muted_line",
)


def parse_color(value: str) -> tuple[float, float, float]:
    channels = [int(value[index : index + 2], 16) / 255 for index in (1, 3, 5)]
    linear = [channel / 12.92 if channel <= 0.04045 else ((channel + 0.055) / 1.055) ** 2.4 for channel in channels]
    return linear[0], linear[1], linear[2]


def luminance(value: str) -> float:
    red, green, blue = parse_color(value)
    return 0.2126 * red + 0.7152 * green + 0.0722 * blue


def contrast(first: str, second: str) -> float:
    high, low = sorted((luminance(first), luminance(second)), reverse=True)
    return (high + 0.05) / (low + 0.05)


def validate(path: Path, require_locked: bool) -> list[str]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return [f"主题文件不存在：{path}"]
    except json.JSONDecodeError as exc:
        return [f"主题 JSON 无法解析：{exc}"]

    errors: list[str] = []
    for key in ("theme_id", "name", "status", "selected_option", "selected_at", "source_theme", "source_palette_original", "palette", "semantic_roles", "image_generation"):
        if not data.get(key):
            errors.append(f"缺少必填字段：{key}")

    if data.get("status") != "selected":
        errors.append("status 必须为 selected")
    if data.get("selected_option") not in {"A", "B", "C", "user-specified"}:
        errors.append("selected_option 必须为 A、B、C 或 user-specified")
    if require_locked and data.get("locked") is not True:
        errors.append("全片视觉主题尚未锁定，不能开始生图或渲染")

    source_theme = data.get("source_theme")
    if isinstance(source_theme, dict):
        if source_theme.get("user_override") is not True:
            for key in ("catalog", "selection_index_sha256", "slug", "preview_md", "design_md"):
                if not source_theme.get(key):
                    errors.append(f"缺少 Frontend Slides 主题来源：source_theme.{key}")
    else:
        errors.append("source_theme 必须是对象")

    palette = data.get("palette")
    if not isinstance(palette, dict):
        errors.append("palette 必须是对象")
        return errors

    for key in PALETTE_KEYS:
        value = palette.get(key)
        if not isinstance(value, str) or not HEX_COLOR.fullmatch(value):
            errors.append(f"palette.{key} 必须是 #RRGGBB 色值")

    if not errors:
        body_ratio = contrast(palette["text_primary"], palette["background"])
        inverse_ratio = contrast(palette["text_inverse"], palette["accent_primary"])
        if body_ratio < 4.5:
            errors.append(f"主文字与背景对比度不足：{body_ratio:.2f}:1，至少需要 4.5:1")
        if inverse_ratio < 3.0:
            errors.append(f"反白文字与主强调色对比度不足：{inverse_ratio:.2f}:1，至少需要 3:1")

    image_generation = data.get("image_generation")
    if isinstance(image_generation, dict):
        if not image_generation.get("palette_prompt"):
            errors.append("缺少 image_generation.palette_prompt")
        if not image_generation.get("negative_palette_prompt"):
            errors.append("缺少 image_generation.negative_palette_prompt")
        if data.get("schema_version") in {"1.1", "1.2"}:
            if not image_generation.get("depth_prompt"):
                errors.append("缺少 image_generation.depth_prompt")
            if not image_generation.get("negative_composition_prompt"):
                errors.append("缺少 image_generation.negative_composition_prompt")

    if data.get("schema_version") in {"1.1", "1.2"}:
        visual_language = data.get("visual_language")
        if not isinstance(visual_language, dict) or visual_language.get("shadow") != "none":
            errors.append("visual_language.shadow 必须为 none")
        cleanliness = data.get("cleanliness_contract")
        if not isinstance(cleanliness, dict):
            errors.append("缺少 cleanliness_contract")
        else:
            for key in (
                "no_ground_plane",
                "no_horizon_line",
                "no_cast_shadow",
                "no_drop_shadow",
                "no_floor_reflection",
                "single_visual_language",
            ):
                if cleanliness.get(key) is not True:
                    errors.append(f"cleanliness_contract.{key} 必须为 true")
            for key in ("raw_full_page_as_decoration", "stacked_background_effects", "heavy_subtitle_bar"):
                if cleanliness.get(key) is not False:
                    errors.append(f"cleanliness_contract.{key} 必须为 false")
            if data.get("schema_version") == "1.2":
                for key in (
                    "global_grime_or_color_cast",
                    "noise_or_dust_texture",
                    "random_particles_or_flares",
                    "generic_ai_cliche_decor",
                    "unassigned_blank_area",
                ):
                    if cleanliness.get(key) is not False:
                        errors.append(f"cleanliness_contract.{key} 必须为 false")
            if cleanliness.get("rim_light_mode") not in {"subtle-soft", "none-when-not-applicable"}:
                errors.append("cleanliness_contract.rim_light_mode 必须为 subtle-soft 或 none-when-not-applicable")
            if cleanliness.get("exception_policy") != "only_when_user_explicitly_requires_real_spatial_context":
                errors.append("cleanliness_contract.exception_policy 只允许用户明确要求真实空间时例外")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="校验视频全片唯一视觉主题")
    parser.add_argument("theme", type=Path, help="video-style-theme.json 路径")
    parser.add_argument("--require-locked", action="store_true", help="要求主题已由用户选定并锁定")
    args = parser.parse_args()

    errors = validate(args.theme.expanduser().resolve(), args.require_locked)
    if errors:
        for error in errors:
            print(f"FAIL {error}")
        return 1
    print("PASS 全片视觉主题有效且可供生图与渲染使用")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

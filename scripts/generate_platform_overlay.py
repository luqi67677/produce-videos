#!/usr/bin/env python3
"""Generate a review-only SVG for platform UI occlusion and safe areas."""

from __future__ import annotations

import argparse
import html
import json
from pathlib import Path
from typing import Any


SIDES = ("left", "right", "top", "bottom")


def load_object(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"无法读取 JSON：{path} ({exc})") from exc
    if not isinstance(data, dict):
        raise ValueError(f"JSON 必须为对象：{path}")
    return data


def validate_ratios(value: Any) -> dict[str, float]:
    if not isinstance(value, dict):
        raise ValueError("平台遮挡比例必须为对象")
    ratios: dict[str, float] = {}
    for side in SIDES:
        raw = value.get(side)
        if not isinstance(raw, (int, float)) or isinstance(raw, bool) or not 0 <= float(raw) <= 0.4:
            raise ValueError(f"平台遮挡比例 {side} 必须在 0—0.4 之间")
        ratios[side] = float(raw)
    return ratios


def build_svg(shot_path: Path) -> str:
    root = Path(__file__).resolve().parents[1]
    shot = load_object(shot_path)
    formats = load_object(root / "assets/format-presets.json")
    profiles = load_object(root / "assets/platform-overlay-profiles.json").get("profiles", {})

    format_id = shot.get("format")
    preset = formats.get(format_id) if isinstance(formats, dict) else None
    overlay = shot.get("platform_overlay")
    if not isinstance(preset, dict) or not isinstance(overlay, dict):
        raise ValueError("shot-readiness 缺少有效 format 或 platform_overlay")

    profile_id = str(overlay.get("profile_id", "")).strip()
    profile = profiles.get(profile_id) if isinstance(profiles, dict) else None
    if not isinstance(profile, dict) or profile.get("format") != format_id:
        raise ValueError("平台安全区配置不存在或与当前画幅不一致")

    width = int(preset["width"])
    height = int(preset["height"])
    calibration_source = overlay.get("calibration_source")
    if calibration_source == "user-recent-screenshot":
        ratios = validate_ratios(overlay.get("occlusion_ratio_override"))
    elif calibration_source == "bundled-conservative-default":
        ratios = validate_ratios(profile.get("occlusion_ratio"))
    else:
        raise ValueError("platform_overlay.calibration_source 无效")

    pixels = profile.get("safe_area_pixels")
    if not isinstance(pixels, dict):
        raise ValueError("平台安全区像素配置无效")
    safe = {
        "left": max(int(pixels["left"]), round(width * ratios["left"])),
        "right": max(int(pixels["right"]), round(width * ratios["right"])),
        "top": max(int(pixels["top"]), round(height * ratios["top"])),
        "bottom": max(int(pixels["bottom"]), round(height * ratios["bottom"])),
    }
    safe_width = width - safe["left"] - safe["right"]
    safe_height = height - safe["top"] - safe["bottom"]
    if safe_width <= 0 or safe_height <= 0:
        raise ValueError("平台遮挡配置没有留下有效安全画面")

    layers = profile.get("overlay_layers", [])
    if not isinstance(layers, list):
        layers = []
    label = html.escape(f"{profile_id} · {calibration_source} · REVIEW ONLY")
    layer_label = html.escape(" / ".join(str(item) for item in layers) or "safe-area-only")
    rects = []
    if safe["top"]:
        rects.append(f'<rect x="0" y="0" width="{width}" height="{safe["top"]}"/>')
    if safe["bottom"]:
        rects.append(f'<rect x="0" y="{height - safe["bottom"]}" width="{width}" height="{safe["bottom"]}"/>')
    if safe["left"]:
        rects.append(f'<rect x="0" y="{safe["top"]}" width="{safe["left"]}" height="{safe_height}"/>')
    if safe["right"]:
        rects.append(f'<rect x="{width - safe["right"]}" y="{safe["top"]}" width="{safe["right"]}" height="{safe_height}"/>')

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
  <g fill="#ff3158" fill-opacity="0.20">{"".join(rects)}</g>
  <rect x="{safe["left"]}" y="{safe["top"]}" width="{safe_width}" height="{safe_height}" fill="none" stroke="#24e0a3" stroke-width="6" stroke-dasharray="18 12"/>
  <rect x="24" y="24" width="{min(width - 48, 940)}" height="92" rx="18" fill="#10131a" fill-opacity="0.88"/>
  <text x="48" y="61" fill="#ffffff" font-size="24" font-family="sans-serif">{label}</text>
  <text x="48" y="94" fill="#c8d0dc" font-size="18" font-family="sans-serif">{layer_label}</text>
</svg>'''


def main() -> int:
    parser = argparse.ArgumentParser(description="生成平台 UI 遮挡与安全区 SVG 审查层")
    parser.add_argument("shot_readiness", type=Path, help="shot-readiness.json 路径")
    parser.add_argument("--output", required=True, type=Path, help="输出 SVG 路径")
    args = parser.parse_args()
    try:
        svg = build_svg(args.shot_readiness.expanduser().resolve())
        output = args.output.expanduser().resolve()
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(svg, encoding="utf-8")
    except ValueError as exc:
        print(f"FAIL {exc}")
        return 1
    print(f"PASS 平台 UI 遮挡审查层已生成：{output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

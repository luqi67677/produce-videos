#!/usr/bin/env python3
"""Export an editable FCPXML 1.10 picture timeline from the project EDL."""

from __future__ import annotations

import argparse
import json
import xml.etree.ElementTree as ET
from fractions import Fraction
from pathlib import Path
from typing import Any


def seconds(value: float, fps: int) -> str:
    frames = round(float(value) * fps)
    fraction = Fraction(frames, fps)
    if fraction.denominator == 1:
        return f"{fraction.numerator}s"
    return f"{fraction.numerator}/{fraction.denominator}s"


def load_edl(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("EDL 根必须为对象")
    return value


def build_fcpxml(edl: dict[str, Any], base: Path) -> ET.ElementTree:
    format_data = edl.get("format")
    clips = edl.get("picture_track")
    if not isinstance(format_data, dict) or not isinstance(clips, list) or not clips:
        raise ValueError("EDL 缺少 format 或 picture_track")
    width = int(format_data.get("width", 0))
    height = int(format_data.get("height", 0))
    fps = int(format_data.get("fps", 0))
    if width <= 0 or height <= 0 or fps <= 0:
        raise ValueError("format 的 width、height、fps 必须为正数")

    root = ET.Element("fcpxml", {"version": "1.10"})
    resources = ET.SubElement(root, "resources")
    ET.SubElement(resources, "format", {
        "id": "r1", "name": f"FFVideoFormat{height}p{fps}", "frameDuration": seconds(1 / fps, fps),
        "width": str(width), "height": str(height), "colorSpace": "1-1-1 (Rec. 709)",
    })
    asset_ids: dict[str, str] = {}
    clip_sources: list[Path] = []
    source_ends: dict[str, float] = {}
    for clip in clips:
        if not isinstance(clip, dict):
            raise ValueError("picture_track 条目必须为对象")
        raw_path = str(clip.get("source_path", "")).strip()
        source = Path(raw_path).expanduser()
        if not source.is_absolute():
            source = (base / source).resolve()
        if not source.is_file():
            raise ValueError(f"源素材不存在：{source}")
        key = str(source)
        clip_sources.append(source)
        source_ends[key] = max(
            source_ends.get(key, 0.0),
            float(clip.get("source_in_seconds", 0)) + float(clip.get("duration_seconds", 0)),
        )
        if key not in asset_ids:
            asset_id = f"r{len(asset_ids) + 2}"
            asset_ids[key] = asset_id
    for key, asset_id in asset_ids.items():
        source = Path(key)
        ET.SubElement(resources, "asset", {
            "id": asset_id, "name": source.name, "src": source.as_uri(), "start": "0s",
            "duration": seconds(source_ends[key], fps), "hasVideo": "1", "format": "r1",
        })

    library = ET.SubElement(root, "library")
    event = ET.SubElement(library, "event", {"name": str(edl.get("project") or "Produce Videos")})
    project = ET.SubElement(event, "project", {"name": str(edl.get("project") or "Produce Videos Timeline")})
    total = max(float(clip.get("timeline_start_seconds", 0)) + float(clip.get("duration_seconds", 0)) for clip in clips)
    sequence = ET.SubElement(project, "sequence", {"format": "r1", "duration": seconds(total, fps), "tcStart": "0s", "tcFormat": "NDF"})
    spine = ET.SubElement(sequence, "spine")
    for clip, source in zip(clips, clip_sources):
        asset_clip = ET.SubElement(spine, "asset-clip", {
            "name": str(clip.get("clip_id") or source.name),
            "ref": asset_ids[str(source)],
            "offset": seconds(float(clip.get("timeline_start_seconds", 0)), fps),
            "start": seconds(float(clip.get("source_in_seconds", 0)), fps),
            "duration": seconds(float(clip.get("duration_seconds", 0)), fps),
        })
        note = str(clip.get("covers", "")).strip()
        ET.SubElement(asset_clip, "marker", {
            "start": seconds(float(clip.get("source_in_seconds", 0)), fps),
            "value": f"{clip.get('roll_type', '')} · {clip.get('scene_id', '')}",
            "note": note,
        })
    return ET.ElementTree(root)


def main() -> int:
    parser = argparse.ArgumentParser(description="从 edit-decision-list.json 导出可继续编辑的 FCPXML")
    parser.add_argument("edl", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    edl_path = args.edl.expanduser().resolve()
    try:
        tree = build_fcpxml(load_edl(edl_path), edl_path.parent)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"FAIL {exc}")
        return 1
    output = args.output.expanduser().resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    ET.indent(tree, space="  ")
    tree.write(output, encoding="utf-8", xml_declaration=True)
    print(f"PASS FCPXML 1.10 已生成：{output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

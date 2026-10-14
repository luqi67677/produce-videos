#!/usr/bin/env python3
"""检查具体画面与相邻镜头计划；不把结构通过当作创意通过。"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path


def validate(data: dict, base: Path) -> dict:
    errors, warnings = [], []
    shots = data.get("shots", [])
    bridges = data.get("bridges", [])
    if not isinstance(shots, list) or not shots:
        return {"machine_pass": False, "errors": ["shots 必须是非空列表"], "warnings": []}
    ids, valid_shots = [], []
    previous_end = None
    for i, shot in enumerate(shots):
        prefix = f"镜头 {i + 1}"
        if not isinstance(shot, dict):
            errors.append(f"{prefix} 必须是对象")
            continue
        sid = shot.get("id")
        if not isinstance(sid, str) or not sid.strip() or sid in ids:
            errors.append(f"{prefix} ID 缺失或重复")
        else:
            ids.append(sid)
        for key in ("subject", "material", "action", "result", "covers", "layout_family"):
            if not isinstance(shot.get(key), str) or not shot[key].strip():
                errors.append(f"{prefix} 缺少 {key}")
        start, end = shot.get("start"), shot.get("end")
        if any(isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v) for v in (start, end)):
            errors.append(f"{prefix} 起止时间必须是有限数字")
            continue
        if start < 0 or end <= start:
            errors.append(f"{prefix} 时间范围无效")
        if previous_end is not None and abs(start - previous_end) > 0.04:
            errors.append(f"{prefix} 与上一镜时间存在空洞或重叠")
        previous_end = end
        paths = shot.get("asset_paths", [])
        if not isinstance(paths, list):
            errors.append(f"{prefix} asset_paths 必须是列表")
            paths = []
        for value in paths:
            if not isinstance(value, str) or not value:
                errors.append(f"{prefix} 素材路径无效")
                continue
            if not (base / value).is_file():
                errors.append(f"{prefix} 素材不存在：{value}")
        if end - start > 8 and not shot.get("hold_reason"):
            warnings.append(f"{prefix} 超过 8 秒，人工检查是否需要拆镜或阅读停留理由")
        valid_shots.append(shot)
    expected = list(zip(ids, ids[1:]))
    seen = []
    if not isinstance(bridges, list):
        errors.append("bridges 必须是列表")
        bridges = []
    types = {"cut", "match-cut", "object-bridge", "camera-bridge", "insert", "occlusion"}
    for i, bridge in enumerate(bridges):
        prefix = f"桥接 {i + 1}"
        if not isinstance(bridge, dict):
            errors.append(f"{prefix} 必须是对象")
            continue
        pair = (bridge.get("from"), bridge.get("to"))
        if pair not in expected or pair in seen:
            errors.append(f"{prefix} 不是唯一的相邻镜头连接")
        seen.append(pair)
        if not isinstance(bridge.get("type"), str) or bridge.get("type") not in types:
            errors.append(f"{prefix} type 无效")
        for key in ("anchor", "reason", "audio"):
            if not isinstance(bridge.get(key), str) or not bridge[key].strip():
                errors.append(f"{prefix} 缺少 {key}")
        duration = bridge.get("duration_seconds")
        if isinstance(duration, bool) or not isinstance(duration, (int, float)) or not math.isfinite(duration) or not 0 <= duration <= 0.8:
            errors.append(f"{prefix} 转场时长须为 0—0.8 秒；特殊设计应单独审片")
        elif bridge.get("type") == "cut" and duration != 0:
            errors.append(f"{prefix} 硬切时长应为 0")
    for pair in expected:
        if pair not in seen:
            errors.append(f"缺少相邻镜头连接：{pair[0]} -> {pair[1]}")
    for i in range(2, len(valid_shots)):
        group = valid_shots[i - 2:i + 1]
        family = group[0].get("layout_family")
        if family and all(s.get("layout_family") == family for s in group):
            warnings.append(f"连续三镜使用 {family}：检查是否重复同构画面")
    return {"machine_pass": not errors, "creative_quality": "requires-video-review", "shot_count": len(shots), "bridge_count": len(bridges), "errors": errors, "warnings": warnings}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("plan", type=Path)
    parser.add_argument("--asset-base", type=Path, help="相对素材路径的基目录，默认计划目录")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        data = json.loads(args.plan.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise ValueError("计划根节点必须是对象")
        result = validate(data, args.asset_base or args.plan.parent)
    except (OSError, ValueError) as exc:
        result = {"machine_pass": False, "errors": [str(exc)], "warnings": []}
    report = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        if args.output.resolve() == args.plan.resolve():
            parser.error("输出文件不能覆盖输入计划")
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(report + "\n", encoding="utf-8")
    print(report)
    return 0 if result["machine_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

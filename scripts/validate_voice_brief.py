#!/usr/bin/env python3
"""验证用户先确认了想要的声音，再允许生成试听。"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def nonempty_text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def text_list(value: Any, allow_empty: bool = False) -> bool:
    return (
        isinstance(value, list)
        and (allow_empty or bool(value))
        and all(nonempty_text(item) for item in value)
    )


def validate(path: Path, require_approved: bool = True) -> list[str]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return [f"声音需求单不存在：{path}"]
    except (OSError, json.JSONDecodeError) as exc:
        return [f"声音需求单无法解析：{exc}"]
    if not isinstance(data, dict):
        return ["声音需求单必须为 JSON 对象"]

    errors: list[str] = []
    for field in (
        "user_request",
        "gender_presentation",
        "age_impression",
        "energy_level",
        "pace",
        "use_case",
        "language",
    ):
        if not nonempty_text(data.get(field)):
            errors.append(f"声音需求单缺少 {field}")
    if not text_list(data.get("tone_keywords")):
        errors.append("tone_keywords 必须包含至少一个用户确认的声音关键词")
    if not text_list(data.get("avoid_traits"), allow_empty=True):
        errors.append("avoid_traits 必须为字符串数组；没有禁忌时使用空数组")
    if require_approved:
        if data.get("approved") is not True:
            errors.append("用户尚未确认声音需求单")
        for field in ("approval_message", "approved_at"):
            if not nonempty_text(data.get(field)):
                errors.append(f"声音需求单缺少 {field}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="验证用户确认的声音需求单")
    parser.add_argument("voice_brief", type=Path)
    parser.add_argument("--require-approved", action="store_true")
    args = parser.parse_args()
    errors = validate(args.voice_brief.expanduser().resolve(), args.require_approved)
    if errors:
        for error in errors:
            print(f"FAIL {error}")
        return 1
    print("PASS 用户声音需求已记录并确认")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""校验独立封面的标题层级、主视觉动作、主题绑定和真实输出。"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


VALID_SUBJECT_TYPES = {"product", "person", "character", "interface", "evidence", "typography"}


def nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def resolve(contract_path: Path, value: Any) -> Path | None:
    if not nonempty(value):
        return None
    path = Path(str(value)).expanduser()
    return path.resolve() if path.is_absolute() else (contract_path.parent / path).resolve()


def validate(path: Path) -> list[str]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"封面契约无法读取：{exc}"]
    if not isinstance(data, dict):
        return ["封面契约必须为 JSON 对象"]

    errors: list[str] = []
    if data.get("schema_version") != "1.0":
        errors.append("封面契约 schema_version 必须为 1.0")
    format_data = data.get("format")
    if not isinstance(format_data, dict) or (
        format_data.get("width"), format_data.get("height"), format_data.get("aspect_ratio")
    ) != (1080, 1440, "3:4"):
        errors.append("独立封面必须为 3:4、1080×1440")

    main_title = data.get("main_title")
    if not isinstance(main_title, dict) or not nonempty(main_title.get("text")):
        errors.append("封面缺少明确主标题")
    else:
        for field in ("target_user_or_context_present", "pain_or_outcome_present"):
            if main_title.get(field) is not True:
                errors.append(f"main_title.{field} 尚未通过")
    subtitle = data.get("subtitle")
    if not isinstance(subtitle, dict) or not nonempty(subtitle.get("text")):
        errors.append("封面缺少与主标题分层的副标题")
    else:
        if subtitle.get("skill_differentiator_present") is not True:
            errors.append("副标题没有说明 Skill 的差异化能力")
        if subtitle.get("duplicates_main_title") is not False:
            errors.append("副标题重复主标题，没有形成信息分工")

    skill_name = data.get("skill_name")
    if not isinstance(skill_name, dict) or not nonempty(skill_name.get("text")):
        errors.append("封面缺少可识别的 Skill 名称")
    else:
        for field in ("prominent", "original_case_preserved"):
            if skill_name.get(field) is not True:
                errors.append(f"skill_name.{field} 尚未通过")

    hierarchy = data.get("text_hierarchy_review")
    if not isinstance(hierarchy, dict):
        errors.append("封面缺少 text_hierarchy_review")
    else:
        for field in ("main_title_dominant", "subtitle_distinct", "orphan_line_free", "thumbnail_readable"):
            if hierarchy.get(field) is not True:
                errors.append(f"text_hierarchy_review.{field} 尚未通过")

    subject = data.get("hero_subject")
    if not isinstance(subject, dict) or subject.get("type") not in VALID_SUBJECT_TYPES:
        errors.append("封面 hero_subject.type 无效")
    elif subject.get("type") != "typography":
        subject_path = resolve(path, subject.get("asset_path"))
        if subject_path is None or not subject_path.is_file():
            errors.append("封面主视觉素材不存在")
        for field in ("authorization_verified", "action_supports_message", "arbitrary_pose_free", "styling_matches_context"):
            if subject.get(field) is not True:
                errors.append(f"hero_subject.{field} 尚未通过")
        if not nonempty(subject.get("action")):
            errors.append("封面人物或主视觉没有说明与标题相关的动作")

    binding = data.get("theme_binding")
    if not isinstance(binding, dict) or binding.get("approved") is not True:
        errors.append("封面没有绑定已批准主题")
    else:
        theme_path = resolve(path, binding.get("path"))
        if theme_path is None or not theme_path.is_file():
            errors.append("封面绑定的主题文件不存在")
        elif str(binding.get("sha256", "")).casefold() != sha256(theme_path).casefold():
            errors.append("封面主题文件 SHA-256 已变化")

    for field in ("output_cover", "output_thumbnail"):
        output = resolve(path, data.get(field))
        if output is None or not output.is_file() or output.stat().st_size == 0:
            errors.append(f"{field} 不存在或为空")
    review = data.get("review")
    if not isinstance(review, dict):
        errors.append("封面缺少 review")
    else:
        for field in ("native_size_reviewed", "thumbnail_reviewed", "approved"):
            if review.get(field) is not True:
                errors.append(f"review.{field} 尚未通过")
        if not nonempty(review.get("approval_message")):
            errors.append("封面缺少用户确认原话")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="校验独立封面契约")
    parser.add_argument("cover_contract", type=Path)
    args = parser.parse_args()
    errors = validate(args.cover_contract.expanduser().resolve())
    if errors:
        for error in errors:
            print(f"FAIL {error}")
        return 1
    print("PASS 独立封面通过：主副标题、Skill 名称、主视觉动作、主题与缩略图均已确认")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""验证三套候选来自完整主题库，并具有真实双画幅样张和逐项质量复核。"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
from pathlib import Path
from typing import Any

from validate_review_approval import validate as validate_approval
from validate_source_assets import review_files as source_asset_review_files
from validate_source_assets import validate as validate_source_assets
from validate_theme_catalog import validate as validate_catalog


EXPECTED_ROLES = {"A": "balanced", "B": "expressive", "C": "unexpected-fit"}
QUALITY_FIELDS = (
    "title_exact",
    "chinese_typography_verified",
    "brand_case_preserved",
    "evidence_readable",
    "safe_area_verified",
    "text_overflow_free",
    "layout_balanced",
    "source_visual_large_enough",
    "no_internal_labels",
    "meaningfully_distinct",
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def nonempty_text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def resolve_path(base_file: Path, value: Any) -> Path | None:
    if not nonempty_text(value):
        return None
    candidate = Path(str(value)).expanduser()
    return candidate.resolve() if candidate.is_absolute() else (base_file.parent / candidate).resolve()


def image_dimensions(path: Path) -> tuple[int, int] | None:
    ffprobe = shutil.which("ffprobe")
    if ffprobe is None:
        return None
    result = subprocess.run(
        [ffprobe, "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height", "-of", "json", str(path)],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return None
    try:
        stream = json.loads(result.stdout)["streams"][0]
        return int(stream["width"]), int(stream["height"])
    except (IndexError, KeyError, TypeError, ValueError, json.JSONDecodeError):
        return None


def validate(options_path: Path, catalog_path: Path, require_selected: bool = False) -> list[str]:
    errors = [f"主题库：{error}" for error in validate_catalog(catalog_path)]
    source_manifest = options_path.parent / "source-assets.json"
    errors.extend(f"用户真实素材：{error}" for error in validate_source_assets(source_manifest, True))
    errors.extend(
        f"用户真实素材审批：{error}"
        for error in validate_approval(
            options_path.parent / "source-assets-approval.json",
            "source-assets",
            True,
            source_asset_review_files(source_manifest),
        )
    )
    try:
        data = json.loads(options_path.read_text(encoding="utf-8"))
        catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        return errors + [f"文件不存在：{exc.filename}"]
    except (OSError, json.JSONDecodeError) as exc:
        return errors + [f"候选或索引无法解析：{exc}"]
    if not isinstance(data, dict) or not isinstance(catalog, dict):
        return errors + ["候选和索引必须为 JSON 对象"]
    format_data = data.get("video_format")
    if not isinstance(format_data, dict) or format_data.get("id") not in {"portrait", "landscape"}:
        errors.append("video_format 必须声明 portrait 或 landscape")
        expected_content = None
    else:
        expected_content = (1080, 1440) if format_data["id"] == "portrait" else (1920, 1080)
        if (format_data.get("width"), format_data.get("height")) != expected_content:
            errors.append("video_format 尺寸与 3:4 / 16:9 规范不一致")
    catalog_info = data.get("theme_catalog")
    if not isinstance(catalog_info, dict):
        errors.append("缺少 theme_catalog")
    else:
        if catalog_info.get("template_count") != 34:
            errors.append("theme_catalog.template_count 必须为 34")
        if str(catalog_info.get("selection_index_sha256", "")).casefold() != sha256(catalog_path).casefold():
            errors.append("主题索引 SHA-256 与本次匹配使用的完整目录不一致")
    catalog_by_slug = {
        str(item.get("slug", "")): item for item in catalog.get("templates", []) if isinstance(item, dict)
    }
    evaluations = data.get("catalog_evaluation")
    shortlisted: set[str] = set()
    evaluated_slugs: set[str] = set()
    if not isinstance(evaluations, list):
        errors.append("catalog_evaluation 必须逐套记录全部 34 个模板")
        evaluations = []
    elif len(evaluations) != 34:
        errors.append("catalog_evaluation 必须逐套记录全部 34 个模板")
    for index, evaluation in enumerate(evaluations):
        label = f"catalog_evaluation[{index}]"
        if not isinstance(evaluation, dict):
            errors.append(f"{label} 必须为对象")
            continue
        slug = str(evaluation.get("theme_slug", "")).strip()
        if not slug or slug in evaluated_slugs:
            errors.append(f"{label} 缺少唯一 theme_slug")
        evaluated_slugs.add(slug)
        score = evaluation.get("score")
        if isinstance(score, bool) or not isinstance(score, int) or not 0 <= score <= 100:
            errors.append(f"{label}.score 必须为 0—100 的整数")
        decision = evaluation.get("decision")
        if decision not in {"shortlisted", "rejected"}:
            errors.append(f"{label}.decision 必须为 shortlisted 或 rejected")
        elif decision == "shortlisted":
            shortlisted.add(slug)
        if not nonempty_text(evaluation.get("reason")):
            errors.append(f"{label}.reason 不能为空")
    catalog_slugs = set(catalog_by_slug)
    if evaluated_slugs != catalog_slugs:
        missing = sorted(catalog_slugs - evaluated_slugs)
        extra = sorted(evaluated_slugs - catalog_slugs)
        if missing:
            errors.append("catalog_evaluation 未覆盖模板：" + ", ".join(missing))
        if extra:
            errors.append("catalog_evaluation 包含目录外模板：" + ", ".join(extra))
    if len(shortlisted) != 3:
        errors.append("catalog_evaluation 必须且只能 shortlist 三套模板")
    options = data.get("options")
    if not isinstance(options, list) or len(options) != 3:
        return errors + ["必须且只能提供三套主题候选"]
    seen_slugs: set[str] = set()
    for index, option in enumerate(options):
        label = f"options[{index}]"
        if not isinstance(option, dict):
            errors.append(f"{label} 必须为对象")
            continue
        option_id = str(option.get("id", "")).strip()
        if EXPECTED_ROLES.get(option_id) != option.get("role"):
            errors.append(f"{label} 的 A/B/C 与候选角色不匹配")
        slug = str(option.get("theme_slug", "")).strip()
        if slug not in catalog_by_slug:
            errors.append(f"{label} 的主题不在 34 套完整目录中")
        elif slug in seen_slugs:
            errors.append("三套候选必须来自三个不同模板")
        seen_slugs.add(slug)
        for field in ("name", "reason", "risk", "content_fit"):
            if not nonempty_text(option.get(field)):
                errors.append(f"{label} 缺少 {field}")
        source = catalog_by_slug.get(slug, {})
        if source and option.get("source_preview") != source.get("preview_md"):
            errors.append(f"{label}.source_preview 与索引不一致")
        if source and option.get("source_design") != source.get("design_md"):
            errors.append(f"{label}.source_design 与索引不一致")
        for field, expected in (
            ("cover_preview", (1080, 1440)),
            ("content_preview", expected_content),
            ("thumbnail_preview", (270, 360)),
        ):
            image_path = resolve_path(options_path, option.get(field))
            if image_path is None or not image_path.is_file() or image_path.stat().st_size == 0:
                errors.append(f"{label} 缺少真实 {field}")
                continue
            dimensions = image_dimensions(image_path)
            if dimensions is None:
                errors.append(f"{label}.{field} 无法读取图片尺寸")
            elif expected is not None and dimensions != expected:
                errors.append(f"{label}.{field} 尺寸应为 {expected[0]}×{expected[1]}，实际为 {dimensions[0]}×{dimensions[1]}")
        review = option.get("quality_review")
        if not isinstance(review, dict):
            errors.append(f"{label} 缺少 quality_review")
        else:
            for field in QUALITY_FIELDS:
                if review.get(field) is not True:
                    errors.append(f"{label}.quality_review.{field} 未通过")
    if shortlisted != seen_slugs:
        errors.append("三套 options 必须与全量 34 套评估中的 shortlisted 完全一致")
    overview_value = data.get("overview_preview")
    overview_path = resolve_path(options_path, overview_value)
    if overview_path is None or not overview_path.is_file() or overview_path.stat().st_size == 0:
        errors.append("缺少可直接展示的三套样张总览图 overview_preview")
    else:
        dimensions = image_dimensions(overview_path)
        if dimensions is None:
            errors.append("overview_preview 无法读取图片尺寸")
        elif dimensions[0] < 810 or dimensions[1] < 360:
            errors.append("overview_preview 尺寸过小，无法完整展示三套候选")
    if str(data.get("schema_version", "")).strip() == "1.2":
        delivery = data.get("review_delivery")
        if not isinstance(delivery, dict):
            errors.append("V1.2 候选缺少 review_delivery")
        else:
            if delivery.get("direct_display") is not True:
                errors.append("三套样张总览尚未作为图片直接展示")
            if delivery.get("html_supplement_only") is not True:
                errors.append("HTML 预览只能作为补充入口")
            if delivery.get("viewport_checked") is not True:
                errors.append("尚未确认总览在当前查看器中完整可见")
            primary = resolve_path(options_path, delivery.get("primary_artifact"))
            if overview_path is not None and primary != overview_path:
                errors.append("review_delivery.primary_artifact 必须与 overview_preview 一致")
            fallback_values = delivery.get("fallback_artifacts")
            if not isinstance(fallback_values, list) or len(fallback_values) < 3:
                errors.append("review_delivery.fallback_artifacts 必须至少包含三个候选缩略图")
            else:
                for value in fallback_values:
                    fallback = resolve_path(options_path, value)
                    if fallback is None or not fallback.is_file() or fallback.stat().st_size == 0:
                        errors.append(f"样张兜底文件不存在：{value}")
    if require_selected:
        selected = data.get("selected_option")
        if data.get("status") != "selected":
            errors.append("用户选择后 status 必须为 selected")
        if selected not in EXPECTED_ROLES:
            errors.append("selected_option 必须为 A、B 或 C")
        approval = data.get("selection_approval")
        if not isinstance(approval, dict):
            errors.append("缺少 selection_approval")
        else:
            if approval.get("approved") is not True:
                errors.append("三套主题尚未获得用户明确选择")
            for field in ("message", "approved_at"):
                if not nonempty_text(approval.get(field)):
                    errors.append(f"selection_approval.{field} 不能为空")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="验证从 34 套主题中匹配出的三套真实样张")
    parser.add_argument("options", type=Path)
    parser.add_argument("--catalog", required=True, type=Path)
    parser.add_argument("--require-selected", action="store_true", help="要求用户已从 A/B/C 中明确选择")
    args = parser.parse_args()
    errors = validate(
        args.options.expanduser().resolve(),
        args.catalog.expanduser().resolve(),
        args.require_selected,
    )
    if errors:
        for error in errors:
            print(f"FAIL {error}")
        return 1
    print("PASS 34 套模板已逐项评估，三套候选的封面、内容帧和缩略图均通过质量复核")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Block sample/full rendering until the required review gates are valid."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from validate_motion_coverage import validate as validate_motion_coverage
from validate_master_script import validate as validate_master_script
from validate_narration_contract import validate as validate_narration_contract
from validate_review_approval import approval_path
from validate_review_approval import validate as validate_approval
from validate_shot_readiness import validate as validate_shot_readiness
from validate_layout_catalog import validate as validate_layout_catalog
from validate_source_assets import review_files as source_asset_review_files
from validate_source_assets import validate as validate_source_assets
from validate_style_options import validate as validate_style_options
from validate_theme_catalog import validate as validate_theme_catalog
from validate_video_theme import validate as validate_video_theme


SAMPLE_STAGES = ("script", "source-assets", "assets", "storyboard")
FULL_STAGES = (*SAMPLE_STAGES, "motion")


def resolve_project_path(project: Path, value: Any) -> Path | None:
    if not isinstance(value, str) or not value.strip():
        return None
    candidate = Path(value).expanduser()
    return candidate.resolve() if candidate.is_absolute() else (project / candidate).resolve()


def load_object(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return value if isinstance(value, dict) else {}


def storyboard_review_files(project: Path) -> list[Path]:
    shot_path = project / "shot-readiness.json"
    required = [shot_path]
    shot_data = load_object(shot_path)
    for scene in shot_data.get("scenes", []):
        if not isinstance(scene, dict):
            continue
        for value in (
            scene.get("storyboard_frame_path"),
            (scene.get("layout_review") or {}).get("reviewed_frame_path")
            if isinstance(scene.get("layout_review"), dict)
            else None,
            (scene.get("fallback_visual") or {}).get("path")
            if isinstance(scene.get("fallback_visual"), dict)
            and scene.get("fallback_visual", {}).get("mode") != "none"
            else None,
        ):
            resolved = resolve_project_path(project, value)
            if resolved is not None:
                required.append(resolved)
    revision_scope = shot_data.get("revision_scope")
    if isinstance(revision_scope, dict) and revision_scope.get("mode") == "revision":
        baseline = resolve_project_path(project, revision_scope.get("baseline_shot_readiness"))
        if baseline is not None:
            required.append(baseline)
        for artifact in revision_scope.get("preview_artifacts", []):
            if not isinstance(artifact, dict):
                continue
            resolved = resolve_project_path(project, artifact.get("path"))
            if resolved is not None:
                required.append(resolved)
    return list(dict.fromkeys(required))


def motion_review_files(project: Path) -> list[Path]:
    coverage_path = project / "motion-coverage.json"
    required = [coverage_path]
    for sample in load_object(coverage_path).get("samples", []):
        if not isinstance(sample, dict):
            continue
        resolved = resolve_project_path(project, sample.get("path"))
        if resolved is not None:
            required.append(resolved)
    return list(dict.fromkeys(required))


def main() -> int:
    parser = argparse.ArgumentParser(description="校验动态样片或正式全片的审批门禁")
    parser.add_argument("project", type=Path, help="视频项目目录")
    parser.add_argument("--mode", choices=("sample", "full"), required=True)
    parser.add_argument(
        "--narration-contract",
        type=Path,
        help="本次渲染实际读取的旁白契约；省略时使用项目根目录 narration-contract.json",
    )
    args = parser.parse_args()

    project = args.project.expanduser().resolve()
    if not project.is_dir():
        parser.error(f"项目目录不存在：{project}")

    narration_contract = (
        args.narration_contract.expanduser().resolve()
        if args.narration_contract
        else project / "narration-contract.json"
    )
    if narration_contract != project and project not in narration_contract.parents:
        parser.error(f"旁白契约必须位于当前项目内：{narration_contract}")

    stages = SAMPLE_STAGES if args.mode == "sample" else FULL_STAGES
    errors: list[str] = []
    required_review_files = {
        "script": [project / "master-script.json"],
        "source-assets": source_asset_review_files(project / "source-assets.json"),
        "assets": [project / "asset-manifest.md"],
        "storyboard": storyboard_review_files(project),
        "motion": motion_review_files(project),
    }
    for stage in stages:
        approval = approval_path(project, stage)
        for error in validate_approval(approval, stage, True, required_review_files[stage]):
            errors.append(f"{stage}: {error}")

    contracts = (
        ("master-script.json", project / "master-script.json", lambda path: validate_master_script(path, True)),
        ("source-assets.json", project / "source-assets.json", lambda path: validate_source_assets(path, True)),
        ("video-style-theme.json", project / "video-style-theme.json", lambda path: validate_video_theme(path, True)),
        (narration_contract.name, narration_contract, lambda path: validate_narration_contract(path, True, True, True)),
        ("shot-readiness.json", project / "shot-readiness.json", lambda path: validate_shot_readiness(path, narration_contract)),
    )
    for name, contract, validator in contracts:
        for error in validator(contract):
            errors.append(f"{name}: {error}")

    skill_root = Path(__file__).resolve().parent.parent
    catalog = skill_root / "references/frontend-slides-themes/bold-template-pack/selection-index.json"
    for error in validate_theme_catalog(catalog):
        errors.append(f"theme-catalog: {error}")
    layout_catalog = skill_root / "references/frontend-slides-layouts"
    for error in validate_layout_catalog(layout_catalog):
        errors.append(f"layout-catalog: {error}")

    theme = load_object(project / "video-style-theme.json")
    selected_option = theme.get("selected_option")
    if selected_option in {"A", "B", "C"}:
        options_path = project / "visual-style-options.json"
        for error in validate_style_options(options_path, catalog, True):
            errors.append(f"visual-style-options.json: {error}")
        options = load_object(options_path).get("options", [])
        selected = next(
            (item for item in options if isinstance(item, dict) and item.get("id") == selected_option),
            None,
        )
        if not isinstance(selected, dict):
            errors.append("visual-style-options.json: 找不到用户选择的候选")
        else:
            source_theme = theme.get("source_theme")
            if not isinstance(source_theme, dict) or source_theme.get("slug") != selected.get("theme_slug"):
                errors.append("visual-style-options.json: 最终 source_theme.slug 与候选不一致")
    elif selected_option != "user-specified":
        errors.append("video-style-theme.json: 主题必须来自 A/B/C 或明确标记 user-specified")

    if args.mode == "full":
        contract = project / "motion-coverage.json"
        for error in validate_motion_coverage(contract):
            errors.append(f"motion-coverage.json: {error}")

    if errors:
        for error in errors:
            print(f"FAIL {error}")
        print(f"STOP 不允许进入 {args.mode} 渲染")
        return 1

    print(f"PASS {args.mode} 渲染门禁通过")
    return 0


if __name__ == "__main__":
    sys.exit(main())

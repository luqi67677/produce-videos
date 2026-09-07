#!/usr/bin/env python3
"""校验动态样片是否覆盖全片运动语法并使用正式声音与视觉骨架。"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from pathlib import Path
from typing import Any


VALID_WORKFLOW_MODES = {"fast", "standard", "high-risk"}
VALID_PROOF_KINDS = {"micro-sample", "full-preview"}


def nonempty_text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def resolve_path(contract_path: Path, value: Any) -> Path | None:
    if not nonempty_text(value):
        return None
    candidate = Path(str(value)).expanduser()
    return candidate.resolve() if candidate.is_absolute() else (contract_path.parent / candidate).resolve()


def probe_video(path: Path) -> str | None:
    ffprobe = shutil.which("ffprobe")
    if ffprobe is None:
        return "需要 ffprobe 才能验证动态样片"
    result = subprocess.run(
        [
            ffprobe,
            "-v",
            "error",
            "-show_entries",
            "format=duration:stream=codec_type",
            "-of",
            "json",
            str(path),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return "动态样片无法读取"
    try:
        data = json.loads(result.stdout)
        duration = float(data.get("format", {}).get("duration", 0))
        has_video = any(stream.get("codec_type") == "video" for stream in data.get("streams", []))
    except (TypeError, ValueError, json.JSONDecodeError):
        return "动态样片媒体信息无效"
    if not has_video or duration <= 0:
        return "动态样片缺少有效视频流或时长"
    return None


def validate(path: Path) -> list[str]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return [f"动态样片覆盖表不存在：{path}"]
    except json.JSONDecodeError as exc:
        return [f"动态样片覆盖表无法解析：{exc}"]

    errors: list[str] = []
    schema_version = data.get("schema_version")
    if schema_version not in {"1.0", "1.1", "1.2"}:
        errors.append("schema_version 必须为 1.0、1.1 或 1.2")
    workflow_mode = data.get("workflow_mode")
    if schema_version == "1.2" and workflow_mode not in VALID_WORKFLOW_MODES:
        errors.append("workflow_mode 必须为 fast、standard 或 high-risk")
    watermark_required = data.get("watermark_required")
    if not isinstance(watermark_required, bool):
        errors.append("watermark_required 必须明确为布尔值")
        watermark_required = False
    required = data.get("required_grammars")
    if not isinstance(required, list) or not required or any(not nonempty_text(item) for item in required):
        errors.append("required_grammars 必须包含全片使用的运动语法")
        required_set: set[str] = set()
    else:
        required_set = {str(item).strip() for item in required}
        if len(required_set) != len(required):
            errors.append("required_grammars 不能重复")

    samples = data.get("samples")
    if not isinstance(samples, list) or not samples:
        errors.append("samples 必须包含至少一个动态样片")
        return errors

    covered: set[str] = set()
    sample_ids: set[str] = set()
    micro_samples: list[dict[str, Any]] = []
    full_previews: list[dict[str, Any]] = []
    for index, sample in enumerate(samples):
        label = f"samples[{index}]"
        if not isinstance(sample, dict):
            errors.append(f"{label} 必须为对象")
            continue
        sample_id = str(sample.get("sample_id", "")).strip()
        if not sample_id:
            errors.append(f"{label} 缺少 sample_id")
        elif sample_id in sample_ids:
            errors.append(f"sample_id 重复：{sample_id}")
        else:
            sample_ids.add(sample_id)
        label = sample_id or label

        if schema_version == "1.2":
            proof_kind = sample.get("proof_kind")
            if proof_kind not in VALID_PROOF_KINDS:
                errors.append(f"{label}.proof_kind 必须为 micro-sample 或 full-preview")
            elif proof_kind == "micro-sample":
                micro_samples.append(sample)
                if sample.get("representative") is not True:
                    errors.append(f"{label} 未标记为代表性动态证明")
            else:
                full_previews.append(sample)

        sample_path = resolve_path(path, sample.get("path"))
        if sample_path is None:
            errors.append(f"{label} 缺少样片路径")
        elif not sample_path.is_file() or sample_path.stat().st_size == 0:
            errors.append(f"{label} 的动态样片文件不存在或为空")
        else:
            probe_error = probe_video(sample_path)
            if probe_error:
                errors.append(f"{label}：{probe_error}")
        grammars = sample.get("grammars")
        if not isinstance(grammars, list) or not grammars or any(not nonempty_text(item) for item in grammars):
            errors.append(f"{label}.grammars 必须包含样片实际证明的运动语法")
        else:
            covered.update(str(item).strip() for item in grammars)
        for field, message in (
            ("uses_final_audio", "未使用已校验的最终旁白与时间轴"),
            ("single_subtitle_layer", "未证明单层字幕"),
            ("visual_coverage_verified", "未检查素材覆盖到旁白结束"),
        ):
            if sample.get(field) is not True:
                errors.append(f"{label}{message}")
        if schema_version == "1.2":
            for field, message in (
                ("uses_locked_storyboard", "未使用已锁定静态分镜"),
                ("character_continuity_verified", "未检查人物身份连续性"),
                ("platform_safe", "未通过平台 UI 遮挡安全检查"),
                ("machine_reviewed", "未完成动态样片机器与 Agent 检查"),
            ):
                if sample.get(field) is not True:
                    errors.append(f"{label}{message}")
            if not isinstance(sample.get("user_review_required"), bool) or not isinstance(sample.get("user_reviewed"), bool):
                errors.append(f"{label} 必须明确记录是否需要用户审核及审核结果")
            elif sample.get("user_review_required") is True and sample.get("user_reviewed") is not True:
                errors.append(f"{label} 需要用户审核但尚未通过")
        if sample.get("watermark_included") is not watermark_required:
            expected = "包含真实水印" if watermark_required else "不包含水印"
            errors.append(f"{label} 的水印状态与项目契约不一致，应{expected}")

    missing = sorted(required_set - covered)
    if missing:
        errors.append(f"以下运动语法没有动态样片覆盖：{', '.join(missing)}")
    if schema_version == "1.2":
        if workflow_mode in {"standard", "high-risk"} and not micro_samples:
            errors.append("standard/high-risk 项目在完整低清预览前必须先做代表性微样片")
        if workflow_mode == "high-risk":
            for sample in micro_samples:
                if sample.get("user_review_required") is not True or sample.get("user_reviewed") is not True:
                    errors.append("high-risk 微样片必须单独给用户审核通过")
        if not full_previews:
            errors.append("正式母版前必须存在完整低清预览证据")
        for sample in full_previews:
            if sample.get("user_review_required") is not True or sample.get("user_reviewed") is not True:
                errors.append("完整低清预览必须经用户确认")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="校验动态样片覆盖表")
    parser.add_argument("motion_coverage", type=Path, help="motion-coverage.json 路径")
    args = parser.parse_args()

    errors = validate(args.motion_coverage.expanduser().resolve())
    if errors:
        for error in errors:
            print(f"FAIL {error}")
        return 1
    print("PASS 动态样片覆盖通过：运动语法、最终旁白、单层字幕、水印状态和末段视觉均已验证")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

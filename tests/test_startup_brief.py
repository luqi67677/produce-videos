from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import sys


SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from validate_startup_brief import validate  # noqa: E402


def write_brief(root: Path, **values: str) -> Path:
    defaults = {
        "视频模式": "portrait",
        "发布平台": "抖音",
        "目标时长": "60 秒以内",
        "口播内容来源代码": "approved-script",
        "口播输入": "本轮用户消息",
        "最终声音来源代码": "recorded-audio",
        "声音输入": "/project/narration.wav",
        "TTS 资源状态": "not-required",
        "静态补图策略": "user-assets-only",
        "静态补图授权": "not-required",
        "TTS 供应方与模型": "not-required",
        "TTS API 凭证位置": "not-required",
        "本地模型线索": "not-required",
        "Qwen 当前 MLX 模型": "`https://huggingface.co/mlx-community/Qwen3-TTS-12Hz-1.7B-VoiceDesign-bf16`",
        "Qwen 目标目录": "not-required",
        "Qwen 安装与下载授权": "not-required",
        "声音方向原话": "not-required",
        "开工信息确认": "approved",
    }
    defaults.update(values)
    path = root / "video-brief.md"
    path.write_text("\n".join(f"- {key}：{value}" for key, value in defaults.items()), encoding="utf-8")
    return path


class StartupBriefTests(unittest.TestCase):
    def test_unfilled_template_options_are_not_treated_as_answers(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            brief = write_brief(Path(temp_dir), **{"视频模式": "未选择 / portrait 竖屏 / landscape 横屏"})
            self.assertTrue(any("视频模式" in error for error in validate(brief, True)))

    def test_recorded_audio_route_passes(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            self.assertEqual(validate(write_brief(Path(temp_dir)), True), [])

    def test_embedded_video_audio_route_passes(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            brief = write_brief(
                Path(temp_dir),
                **{"最终声音来源代码": "extract-from-video", "声音输入": "/project/source.mp4"},
            )
            self.assertEqual(validate(brief, True), [])

    def test_tts_api_requires_provider_and_safe_credentials(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            brief = write_brief(
                Path(temp_dir),
                **{
                    "最终声音来源代码": "tts-api",
                    "声音输入": "not-required",
                    "TTS 资源状态": "api-configured",
                    "TTS 供应方与模型": "待提供",
                    "TTS API 凭证位置": "pending",
                    "声音方向原话": "温柔、青年女声、中速",
                },
            )
            errors = validate(brief, True)
            self.assertTrue(any("供应方" in error for error in errors))
            self.assertTrue(any("凭证" in error for error in errors))

    def test_local_model_route_requires_model_clue(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            brief = write_brief(
                Path(temp_dir),
                **{
                    "最终声音来源代码": "local-tts-model",
                    "声音输入": "not-required",
                    "TTS 资源状态": "local-model-known",
                    "本地模型线索": "待提供",
                    "声音方向原话": "由你判断",
                },
            )
            self.assertTrue(any("本地模型" in error for error in validate(brief, True)))

    def test_qwen_route_requires_upfront_authorization(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            brief = write_brief(
                Path(temp_dir),
                **{
                    "最终声音来源代码": "qwen-open-source",
                    "声音输入": "not-required",
                    "TTS 资源状态": "pending",
                    "Qwen 目标目录": "/project/models/qwen",
                    "Qwen 安装与下载授权": "pending",
                    "声音方向原话": "轻快、儿童女声、中速",
                },
            )
            errors = validate(brief, True)
            self.assertTrue(any("开工阶段" in error for error in errors))
            self.assertTrue(any("明确授权" in error for error in errors))

    def test_qwen_route_passes_after_upfront_authorization(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            brief = write_brief(
                Path(temp_dir),
                **{
                    "最终声音来源代码": "qwen-open-source",
                    "声音输入": "not-required",
                    "TTS 资源状态": "qwen-download-approved",
                    "Qwen 目标目录": "/project/models/qwen",
                    "Qwen 安装与下载授权": "approved",
                    "声音方向原话": "轻快、儿童女声、中速",
                },
            )
            self.assertEqual(validate(brief, True), [])


if __name__ == "__main__":
    unittest.main()

# 第三方 notices

本 Skill 不打包第三方模型权重，只提供用户在授权后自行下载的地址和命令。

- Qwen3-TTS 官方模型页：<https://huggingface.co/Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign>
- 当前 Apple Silicon MLX 转换模型：<https://huggingface.co/mlx-community/Qwen3-TTS-12Hz-1.7B-VoiceDesign-bf16>
- MLX-Audio 使用说明：<https://github.com/Blaizzy/mlx-audio/blob/main/docs/models/tts/qwen3-tts.md>
- 34 套视觉主题来自 Zara Zhang 创建并以 MIT 许可证开源的 [`zarazhangrui/frontend-slides`](https://github.com/zarazhangrui/frontend-slides)，固定来源见 `references/frontend-slides-themes/source.json`，随包许可证见 `references/frontend-slides-themes/LICENSE`。
- 88 套布局来自 [`dreamid27/frontend-slides`](https://github.com/dreamid27/frontend-slides) 对上述项目的扩展版本。该扩展明确保留对 Zara Zhang 原项目的致谢；本仓库固定到的提交哈希见 `references/frontend-slides-layouts/source.json`，随包许可证见 `references/frontend-slides-layouts/LICENSE`。
- Produce Videos 对这些上游资源的本地新增仅包括视频场景选择、3:4 竖屏适配、干净度限制、平台安全区与成片质量门，不声称拥有上游模板或布局的原创权。

模型、运行时和模板的许可证、使用范围及版本以各自上游页面和随附许可证为准。发布者不得把模型权重、访问令牌或用户素材复制进本 Skill。

- IP 讲解导演规则参考 [62656456/ai-film-skills 的 ai-storyboard-director](https://github.com/62656456/ai-film-skills/tree/main/skills/ai-storyboard-director) 的观看顺序、人物调度与取景方法。上游许可证为 [Apache-2.0](https://github.com/62656456/ai-film-skills/blob/main/LICENSE)，许可证副本见 `references/director-source-LICENSE`。本 Skill 的 `ip-presenter-directing.md` 为 2026-10-14 针对静态讲解人和现有项目流程重新组织的规则，未包含上游运行包或执行依赖。

- V2.6.5 的镜头与风格方法独立整理自 HyperFrames、video-shotcraft、brag、OpenMontage 和 Remotion captions 的公开规则及示例；逐项来源链接与取舍见 `references/directing-methods-and-creator-style.md`。此次未打包上述项目的代码、媒体或配方，不改变各上游及其依赖的许可证。

- V2.6.9 的立体机制示意方法参考 [wheresryan22/anatomy](https://github.com/wheresryan22/anatomy) 的 MIT 许可文档，固定来源与采用范围见 [spatial-mechanism-explainers.md](references/spatial-mechanism-explainers.md)。本次独立整理方法，未复制上游代码、模板或媒体，未集成其运行时。

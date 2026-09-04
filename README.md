# Produce Videos：视频生成与编辑 Skill

面向 Codex、Claude Code、Hermes 等 AI Agent 的开源视频制作 Skill。它把讲稿、文档、截图、图片、PPT 或录屏整理为可播放的动态视频和独立封面，覆盖内容核验、真实素材、风格选择、配音、镜头素材、静态分镜、动态样片、全片渲染和质量检查。

An open-source **video production skill for AI agents**. It turns scripts, documents, screenshots, images, slides, and screen recordings into quality-gated videos with explicit user approvals at every expensive production stage.

## 它解决什么问题

- 先生成整条视频，最后才发现口播、素材或风格不对。
- 风格选择只有名称和色块，没有真实样张，也没有完整模板库。
- 没检查已有模型就要求重新安装，或没问声音偏好就随机生成试听。
- 静态分镜是一套，最终视频又变成另一套画面。
- 用户看不到本地预览，却被要求继续确认。
- 输出视频只有文件，没有时长、编码、响度、黑帧和旁白绑定检查。

## 核心流程

1. 确认 `16:9` 横屏或 `3:4` 竖屏。
2. 核验事实并让用户确认完整口播。
3. 盘点、展示并确认用户真实素材。
4. 校验全部 34 套视觉模板，从完整目录匹配三套真实样张。
5. 输出一张校准画面，确认版式后才批量制作。
6. 先确认音频来源，再询问声音需求并生成试听。
7. 确认整批镜头素材和独立封面草图。
8. 确认全量静态分镜。
9. 确认覆盖全部运动语法的动态样片。
10. 通过渲染门禁后输出完整视频、独立封面和质量报告。

每个确认阶段只提出一个问题。图片、音频和视频必须直接展示；HTML 页面只能作为辅助入口。未确认当前阶段时，不提前批量生成下一阶段。

## 声音与 Qwen3-TTS

音频入口支持四种情况：

- 用户已有完整口播音频；
- 用户已有可调用的 TTS API；
- 电脑中已有本地 TTS 模型；
- 当前没有可用音频方案。

选择本地模型后，Skill 只在标准缓存和用户明确指定的目录中有限发现模型，并尝试复用已有 Python 运行环境。只有确认没有可用模型或运行时后，才会说明下载地址、大小和目标目录，并在得到明确授权后准备 Qwen3-TTS。

当前内置 Qwen 执行器面向 Apple Silicon 的 `mlx-audio` 路线。其他设备可以使用用户自己的完整音频或已验证 TTS 服务。仓库不包含模型权重、预设声音、私人参考音频或 API Key。

## 视觉模板

仓库包含 34 套通用视觉模板的设计说明和选择索引。每次推荐都会先检查目录完整性，再依据内容、受众、情绪、密度和平台评估全部模板，从中选择三套不同候选。

候选必须使用相同标题、相同内容和相同主视觉生成：

- 1080×1440 的 3:4 封面样张；
- 与主视频一致画幅的内容样张；
- 270×360 的信息流缩略图；
- 能完整看到三套候选的总览图片。

## 输出规格

- 竖屏：3:4、1080×1440、30fps。
- 横屏：16:9、1920×1080、30fps。
- 独立封面：3:4、1080×1440，同时输出 270×360 缩略图。
- 推荐视频编码：H.264；推荐音频：AAC、48kHz、双声道。
- 综合响度可接受范围：-19 至 -14 LUFS，目标约 -16.5 LUFS。

## 调用示例

```text
使用 $produce-videos，把这份讲稿和产品截图制作成 3:4 竖屏宣传视频。
每一步先让我确认；优先使用真实素材，缺少的部分再生成。
```

```text
使用 $produce-videos，把这段录屏制作成 16:9 教程视频。
先检查隐私信息和口播，再做完整静态分镜和动态样片。
```

## 安装

将整个仓库克隆到目标 Agent 可以读取的 Skill 目录，保持目录结构不变：

```bash
git clone https://github.com/luqi67677/produce-videos.git
```

主要依赖：

- Python 3.10+
- `ffmpeg` 与 `ffprobe`
- 能生成最终画面的浏览器、Remotion、FFmpeg 或其他视频渲染环境
- 本地 Qwen3-TTS 路线可选安装 `mlx-audio`

具体安装位置和调用方式以目标 Agent 的官方说明为准。

## 目录结构

```text
produce-videos/
├── SKILL.md
├── agents/
│   └── openai.yaml
├── assets/
├── references/
│   └── frontend-slides-themes/
├── scripts/
├── tests/
├── evals/
├── THIRD_PARTY_NOTICES.md
└── LICENSE
```

## 隐私边界

- 不包含作者个人形象、私人音色、水印、账号资料、本机路径或用户项目素材。
- 用户提供的素材只属于当前项目，不得写回 Skill 仓库。
- API 凭证只从环境变量或系统安全存储读取，不写入聊天、项目文件或日志。
- 发布前可运行 `python3 scripts/scan_release.py` 检查本机路径、联系方式、密钥、符号链接和未经证明安全的二进制文件。

## 验证

```bash
python3 -m unittest discover -s tests -v
python3 scripts/validate_theme_catalog.py \
  references/frontend-slides-themes/bold-template-pack/selection-index.json
python3 scripts/scan_release.py
```

自动检查不能替代用户对口播、素材、声音、分镜、动态样片和最终成片的实际确认，也不能证明视频已上传、发布或产生真实用户效果。

## 许可证

本项目使用 [MIT License](LICENSE)。第三方组件及模型说明见 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)。

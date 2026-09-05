# Produce Videos：视频生成与编辑 Skill

面向支持目录式 Agent Skills 的 AI Agent。V2.2.0 在开工时一次锁定口播内容来源、最终声音来源和 TTS 准备情况，并提供 Codex、Kimi Code CLI 和 WorkBuddy 的明确安装路径。

An open-source **video production skill for AI agents**. It turns scripts, documents, screenshots, images, slides, and screen recordings into quality-gated videos with risk-based review bundles instead of a rigid approval stop after every internal stage.

## 复制这段话，让 AI 帮你安装

```text
请帮我安装并验证这个开源视频 Skill：
https://github.com/luqi67677/produce-videos

请先判断你当前运行的是 Codex、Kimi Code CLI、WorkBuddy，还是不具备本地文件和终端能力的普通聊天 AI，再按仓库 README 中对应的平台说明安装。不要覆盖已经存在且被修改过的同名目录。

安装后请实际验证：
1. 能读取 produce-videos/SKILL.md；
2. 能看到 scripts、references 和 assets；
3. 运行仓库自带的最小验证；
4. 告诉我真实安装位置、验证结果，以及是否需要重启或重新打开会话。

如果当前平台不能安装目录式 Skill，请明确说明限制和可行的手动导入方式，不要假装安装成功。安装阶段不要下载 TTS 模型，也不要调用任何付费服务。
```

> 这里的 Kimi 指 **Kimi Code CLI**，不是普通 Kimi 聊天网页。纯聊天产品如果不能读取本地文件、执行脚本和生成媒体文件，就无法完整运行这个 Skill。

## 它解决什么问题

- 先生成整条视频，最后才发现口播、素材或风格不对。
- 风格选择只有名称和色块，没有真实样张，也没有完整模板库。
- 没检查已有模型就要求重新安装，或没问声音偏好就随机生成试听。
- 静态分镜是一套，最终视频又变成另一套画面。
- 用户看不到本地预览，却被要求继续确认。
- 画面叠加脏色、重字幕条、整页截图、地面和投射阴影，技术检查通过但仍不具备分享质量。
- 输出视频只有文件，没有时长、编码、响度、黑帧和旁白绑定检查。

## 核心流程

1. 开工信息包：一次补齐画幅、平台、时长、口播内容来源、最终声音来源、现有 API/本地模型和声音方向。
2. 内容方向包：一次审查完整口播、真实素材联系表和三套风格。
3. 声音执行与确认包：需要 TTS 时生成三条同文案试听；已有独立口播或从视频提取口播时跳过试听。
4. 成片蓝图包：在全量静态分镜中一起审查素材用法、隐私和构图。
5. 最终预览包：普通项目直接看完整低清预览，高风险动作才先做 4—8 秒样片；批准后导出母版。

短片且信息完整时通常只需 4 次确认；普通项目为 4—5 次。隐私、授权、模型下载或新运动语法会单独展开。五个内部审批阶段仍写入同一个 `approval-ledger.json` 并校验真实文件哈希。

## 声音与 Qwen3-TTS

最终声音入口支持六种情况：

- 用户已有独立的完整口播音频；
- 用户提供的视频里已经包含可直接提取的口播；
- 用户已有可调用的 TTS API；
- 电脑中已有本地 TTS 模型；
- 当前没有可用音频方案，选择准备免费的 Qwen3-TTS；
- 用户明确选择无旁白。

Skill 会在第一次开工时分别询问“口播内容从哪里来”和“最终声音从哪里来”。选择 TTS 时，会同步问清声音偏好，并优先复用已有 API 或本地模型。没有发现可用本地模型时，会直接推荐免费的 [Qwen3-TTS VoiceDesign bf16](https://huggingface.co/mlx-community/Qwen3-TTS-12Hz-1.7B-VoiceDesign-bf16)（约 4.52 GB）；本机空间或内存紧张时，也可选择约 2.5 GB 的 [5bit 量化版](https://huggingface.co/mlx-community/Qwen3-TTS-12Hz-1.7B-VoiceDesign-5bit)。[阿里 Qwen 官方原始模型](https://huggingface.co/Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign)和[官方项目](https://github.com/QwenLM/Qwen3-TTS)同时保留在配置中，当前 Apple Silicon 执行器使用 MLX 转换版。

Apple Silicon 的明确安装与下载步骤：

```bash
<兼容的 Python 3.10+> -m pip install -U "mlx-audio[tts]" "huggingface_hub[hf_xet]"
<兼容的 Python 3.10+> scripts/prepare_qwen_model.py --model-dir <模型目录>
<兼容的 Python 3.10+> scripts/prepare_qwen_model.py --model-dir <模型目录> \
  --download --download-authorized
```

第一条安装依赖、第三条下载模型，都只能在用户明确同意后执行；第二条只展示地址、预计大小、依赖和目标目录，不会下载模型。Agent 必须先把命令中的两个占位符替换为本机已确认的 Python 运行环境和 Skill 仓库之外的模型目录，再向用户展示命令并申请授权。

当前内置 Qwen 执行器面向 Apple Silicon 的 `mlx-audio` 路线。其他设备可以使用用户自己的完整音频或已验证 TTS 服务。仓库不包含模型权重、预设声音、私人参考音频或 API Key。

## 视觉模板

仓库包含 34 套通用视觉模板的设计说明和选择索引。每次推荐都会先检查目录完整性，再依据内容、受众、情绪、密度和平台评估全部模板，从中选择三套不同候选。全部 34 套保留分数和简短理由，详细解释集中在前三名。

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

## 视觉干净度

- 生成与合成画面默认无地面、无地平线、无投射阴影、无悬浮阴影和地面反射。
- 主体需要与背景分离时，只使用柔和、低饱和、窄范围的轮廓光；不使用霓虹描边或完整光环。
- 不叠加多套背景色偏、渐变和材质，不用重色字幕通栏抢主体，不把整页截图缩小塞进卡片。
- 原尺寸和信息流缩略图都必须通过干净度复核；用户明确要求真实空间时才允许记录例外并重新确认样张。

## 调用示例

```text
使用 $produce-videos，把这份讲稿和产品截图制作成 3:4 竖屏宣传视频。
按风险合并确认；优先使用真实素材，缺少的部分再生成。
```

```text
使用 $produce-videos，把这段录屏制作成 16:9 教程视频。
先检查隐私信息和口播，再做完整静态分镜；新运动语法才先做短样片。
```

## 三个平台怎么安装

| 平台 | 支持方式 | 安装位置或入口 | 调用方式 |
|---|---|---|---|
| Codex | 原生读取标准 `SKILL.md` 目录 | `~/.codex/skills/produce-videos` | `$produce-videos` |
| Kimi Code CLI | 原生读取 Agent Skills | 推荐 `~/.config/agents/skills/produce-videos` | `/skill:produce-videos`，也可由 Agent 自动发现 |
| WorkBuddy | 使用本仓库生成符合其上传结构的 ZIP | 技能市场 → 添加技能 → 上传技能 | 安装后在对话中用自然语言调用 |

### Codex

```bash
git clone https://github.com/luqi67677/produce-videos.git ~/.codex/skills/produce-videos
```

安装完成后重新打开一次会话，再输入 `$produce-videos` 使用。

### Kimi Code CLI

```bash
git clone https://github.com/luqi67677/produce-videos.git ~/.config/agents/skills/produce-videos
```

安装后输入 `/skill:produce-videos`，或直接描述视频任务让 Kimi Code 自动发现。项目内安装也可以放到 `.agents/skills/produce-videos`。

### WorkBuddy

先下载仓库，在仓库目录运行：

```bash
python3 scripts/package_workbuddy.py --output produce-videos-workbuddy.zip
```

然后在 WorkBuddy 的“技能市场 → 添加技能 → 上传技能”中选择生成的 ZIP。打包器会从同一份标准 `SKILL.md` 生成 WorkBuddy 所需的双语描述、版本和作者字段，不会维护第二份视频流程。

以上是三种不同的安装入口，不代表所有聊天 AI 都能安装本地 Skill。其他 Agent 只有在支持 `SKILL.md`、本地文件读写和脚本执行时，才具备完整运行条件。

主要依赖：

- Python 3.10+
- `ffmpeg` 与 `ffprobe`
- 能生成最终画面的浏览器、Remotion、FFmpeg 或其他视频渲染环境
- 本地 Qwen3-TTS 路线可选安装 `mlx-audio`

平台依据：[Codex Skill 规范](https://github.com/openai/codex/blob/main/codex-rs/skills/src/assets/samples/skill-creator/SKILL.md)、[Kimi Code Agent Skills](https://github.com/MoonshotAI/kimi-cli/blob/main/docs/en/customization/skills.md)、[WorkBuddy Skill 文档](https://open.workbuddy.cn/docs/skill)。

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
│   └── package_workbuddy.py
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
python3 scripts/validate_startup_brief.py project/video-brief.md --require-approved
python3 scripts/scan_release.py
python3 scripts/package_workbuddy.py --output /tmp/produce-videos-workbuddy.zip
```

自动检查不能替代用户对确认包和最终预览的实际判断，也不能证明视频已上传、发布或产生真实用户效果。

## 许可证

本项目使用 [MIT License](LICENSE)。第三方组件及模型说明见 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)。

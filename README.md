# Produce Videos：视频生成与编辑 Skill

> 把讲稿、文档、PPT、截图、图片、录屏和已有视频交给 AI Agent，让它协助完成口播、素材、配音、分镜、动画、字幕、预览、质检和成片导出。

Produce Videos 是一个开源的 Agent Skill。它不是独立剪辑软件，也不是视频生成模型，而是一套可以被 Codex、Kimi Code CLI、WorkBuddy 等本地 AI Agent 执行的视频制作流程。

An open-source video production skill for AI agents. It turns scripts and source assets into reviewable videos, covers, storyboards, narration, motion, subtitles, and verified final renders.

## 它是做什么的

当你有一个视频想法、一份稿子或一批素材，却不想自己从头学习剪辑、配音和动画工具时，可以把任务交给支持本地文件与终端操作的 AI Agent，再让 Agent 按这套 Skill 完成制作。

你可以提供：

- 已经确认的口播稿，或用于撰写口播的文档和资料；
- PPT、截图、图片、录屏、已有视频和品牌素材；
- 自己录好的口播、视频中的人声、TTS API 或本地语音模型；
- 发布平台、画幅、时长、目标观众和想要的视觉方向。

它可以协助完成：

- 整理或撰写完整口播；
- 核对真实素材、授权和隐私信息；
- 从 34 套视觉主题中匹配三种真实候选，再按镜头语义从 88 套布局骨架中选结构；
- 复用录音、视频人声、TTS API 或本地模型完成配音；
- 用 A-roll 建立叙事主轴，用 B-roll 补证据、操作演示、静态插画和代码动画；
- 拆分镜头，设计画面、动画、字幕、切换时间和节拍卡点；
- 生成静态分镜、完整低清预览和独立封面；
- 检查时长、编码、音轨、响度、黑帧、画幅和旁白绑定；
- 导出可播放的正式视频、独立 3:4 封面，以及需要时可继续编辑的 FCPXML 时间线。

适合产品介绍、功能演示、教程、知识讲解、品牌宣传、作品展示和已有视频的定点修改。

这套 Skill 不调用视频生成模型来生成整段 AI 视频。它主要组合真实素材、补充图片、代码动画、配音和字幕。需要纯文本生成连续真人镜头或电影级视频时，应另外使用视频生成工具。

## 使用流程

### 1. 把需求和素材交给 Agent

告诉 Agent 想做什么视频，并提供已经有的文字、PPT、截图、图片、录屏、视频或音频。需求还不清楚也可以直接说，让 Agent 一次把缺失信息问完。

### 2. 一次确认开工信息

Agent 会整理平台、画幅、时长、目标观众、口播内容来源、最终声音来源、现有 API 或本地模型、声音方向，以及真实素材不足时是否允许生成静态补图。已经说明的信息不会重复询问。

### 3. 确认口播、真实素材和视觉方向

Agent 先给出完整口播和真实素材联系表。没有指定视觉方向时，它会评估仓库中的 34 套模板，并用相同内容生成三套可直接查看的真实候选。你可以一次回复口播和素材是否通过，并选择 A、B 或 C。

### 4. 确认声音

声音可以来自六种入口：

- 已经录好的独立口播；
- 从已有视频中提取的人声；
- 已有 TTS API；
- 电脑中已有的本地 TTS 模型；
- 经授权后准备免费的 Qwen3-TTS；
- 明确选择无旁白。

选择 TTS 时，Agent 会复用开工阶段已经确认的声音方向，生成三条同文案试听。你选定一个以后，它才生成完整旁白。已有可用口播时会跳过试听。

### 5. 确认完整分镜

素材和声音确定后，Agent 会标记每段是 A-roll、B-roll、混合画面还是纯图形主轴，并从 88 套布局中选择合适骨架。每个 B-roll 都要说明它正在解释哪句话；每个转场都要说明前后状态如何连接。你会看到完整静态分镜，而不只是文字方案。

### 6. 查看整片预览并导出

普通项目直接生成完整低清预览；涉及新动画、敏感录屏或高风险素材时，才会先做最短风险样片。整片预览通过后，Agent 再导出正式视频和独立封面。

短片且信息完整时，通常只需要 4 次确认。普通项目约为 4 至 5 次。隐私、素材授权、依赖安装和模型下载会单独确认。

## 安装

可以直接从 [GitHub Releases](https://github.com/luqi67677/produce-videos/releases/latest) 下载：通用 Agent 使用 `produce-videos.skill` 或 `produce-videos.zip`，WorkBuddy 使用 `produce-videos-workbuddy.zip`。给 Agent 的完整安装契约见 [INSTALL_FOR_AGENTS.md](INSTALL_FOR_AGENTS.md)。

### 最简单的方式：把这段话复制给 AI

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

> 这里的 Kimi 指 **Kimi Code CLI**，不是普通 Kimi 聊天网页。普通聊天产品如果不能读取本地文件、运行脚本和生成媒体文件，就不能完整执行这套 Skill。

### 手动安装

| 平台 | 安装位置或入口 | 安装后调用 |
|---|---|---|
| Codex | `~/.codex/skills/produce-videos` | `$produce-videos` |
| Kimi Code CLI | `~/.config/agents/skills/produce-videos` | `/skill:produce-videos` |
| WorkBuddy | 技能市场中上传仓库生成的 ZIP | 在对话中直接描述视频任务 |

#### Codex

```bash
git clone https://github.com/luqi67677/produce-videos.git ~/.codex/skills/produce-videos
```

安装完成后重新打开会话，再输入 `$produce-videos` 使用。

#### Kimi Code CLI

```bash
git clone https://github.com/luqi67677/produce-videos.git ~/.config/agents/skills/produce-videos
```

重新打开 Kimi Code CLI 后输入 `/skill:produce-videos`。也可以直接描述视频任务，让 Agent 根据 Skill 描述自动发现。项目级安装可以放在 `.agents/skills/produce-videos`。

#### WorkBuddy

先下载仓库，在仓库目录生成上传包：

```bash
python3 scripts/package_workbuddy.py --output produce-videos-workbuddy.zip
```

然后打开“技能市场 → 添加技能 → 上传技能”，选择生成的 ZIP。打包器会把完整的 `SKILL.md`、`scripts`、`references` 和 `assets` 放入 WorkBuddy 要求的目录结构。

#### 其他 Agent

如果 Agent 支持目录式 `SKILL.md`、本地文件读写和命令执行，可以把完整的 `produce-videos` 目录放入它的 Skills 目录。不能只复制 `SKILL.md`，因为声音、模板、校验和渲染流程还依赖同级的 `scripts`、`references` 和 `assets`。

平台依据：[Codex Skill 示例](https://github.com/openai/codex/blob/main/codex-rs/skills/src/assets/samples/skill-creator/SKILL.md)、[Kimi Code CLI Agent Skills](https://github.com/MoonshotAI/kimi-cli/blob/main/docs/en/customization/skills.md)、[WorkBuddy Skill 文档](https://open.workbuddy.cn/docs/skill)。

## 安装后怎么使用

最短调用方式：

```text
使用 $produce-videos，把这份讲稿和产品截图制作成一条 3:4 竖屏宣传视频。
```

Kimi Code CLI 可以这样说：

```text
/skill:produce-videos 把这段录屏制作成一条 16:9 教程视频。
```

信息比较完整时，可以一次提供：

```text
使用 produce-videos 帮我制作一条视频。

发布平台：抖音
画幅：3:4 竖屏
目标时长：60 秒以内
目标观众：第一次了解这个产品的人
想讲的内容：介绍它解决什么问题，以及怎么使用
已有素材：口播稿、产品截图和一段操作录屏
口播内容：使用我提供的稿子
最终声音：从我提供的视频中提取

如果还有缺失信息，请在开工时一次问完。
```

还不知道想做成什么样，也可以说：

```text
使用 produce-videos 帮我做一条视频。我现在只有这些资料，还没有想清楚结构、风格和声音。请先一次问清楚需要的信息，再开始制作。
```

继续昨天或上次中断的项目时：

```bash
python3 scripts/resume_project.py /path/to/video-project
```

它只读取现有审批账本和已审批文件哈希，告诉 Agent 已完成到哪里、哪些文件审批后发生了变化、下一步是什么，不创建第二套项目状态。

## 一次完整演示应该录什么

如果要向别人演示这套 Skill，可以按下面的顺序录屏。每一段都对应用户真正会经历的步骤。

| 录屏段落 | 画面 | 需要说明的重点 |
|---|---|---|
| 1. 找到仓库 | GitHub 首页和 README 第一屏 | 这是一个开源的视频制作 Agent Skill |
| 2. 安装 | 复制“请帮我安装并验证”整段口令到 Codex 或 Kimi Code CLI | 不需要手动研究目录，让 Agent 完成安装和验证 |
| 3. 发起任务 | 输入“使用 produce-videos 帮我做一条视频”，同时展示已有素材 | 文字、PPT、截图、录屏、视频和音频都可以作为输入 |
| 4. 开工信息 | Agent 一次询问平台、画幅、时长、内容和声音 | 先把基础需求说清楚，减少后面返工 |
| 5. 内容方向 | 完整口播、真实素材联系表和三套视觉候选 | 用户确认内容与素材，并从真实样张中选择风格 |
| 6. 声音 | 已有口播直接使用，或展示三条 TTS 试听 | 会先复用现有音频、API 或本地模型，没有时才推荐开源模型 |
| 7. 分镜 | 完整静态分镜联系表 | 每句话对应什么画面、怎么动、何时切换都能看见 |
| 8. 成片 | 完整低清预览、正式视频和独立封面 | 预览确认后才导出最终文件 |

录屏时不需要展示内部脚本和测试代码。观众只需要看见三件事：怎么安装、怎么把素材交给它、最后能得到什么。

## 声音与 Qwen3-TTS

Skill 会优先使用用户已经拥有的音频能力。选择 TTS 时，会先检查已配置的 API、用户明确提供的本地模型目录和标准缓存。没有可用方案时，才会推荐免费的 Qwen3-TTS，并在安装依赖或下载模型前单独取得授权。

- [Qwen3-TTS 官方项目](https://github.com/QwenLM/Qwen3-TTS)
- [Qwen3-TTS VoiceDesign 官方模型](https://huggingface.co/Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign)
- [Apple Silicon 使用的 MLX bf16 转换版](https://huggingface.co/mlx-community/Qwen3-TTS-12Hz-1.7B-VoiceDesign-bf16)，约 4.52 GB
- [较小的 MLX 5bit 转换版](https://huggingface.co/mlx-community/Qwen3-TTS-12Hz-1.7B-VoiceDesign-5bit)，约 2.5 GB

当前内置的 Qwen 执行器面向 Apple Silicon 和 `mlx-audio`。其他设备可以使用自己的完整口播、已验证 TTS API 或兼容的本地模型。仓库不包含模型权重、预设声音、私人参考音频或 API Key。

安装 Skill 本身不会下载 TTS 模型。只有用户在视频任务中选择 Qwen 路线并明确授权后，Agent 才能安装依赖或执行下载。

## 34 套视觉主题 + 88 套布局

仓库包含 34 套视觉主题和 88 套结构化布局。主题决定颜色、字体、材质和动效语气；布局决定标题、截图、人物、图表和辅助信息放在哪里。用户没有指定视觉系统时，Skill 会评估全部 34 套主题并推荐三套真实候选；主题锁定后，每个镜头再按语义选择布局，避免临场乱摆元素。

三套候选必须使用相同标题、相同代表内容、相同主视觉和目标画幅，并直接展示：

- 3:4 封面样张；
- 与主视频一致画幅的内容样张；
- 270×360 信息流缩略图；
- 能完整看到三套候选的总览图。

选中以后，全片的封面、字幕、分镜、动画和成片都会读取同一套视觉主题，不会在后面的制作中自行换风格。

布局还带有硬限制：一个焦点、有限的辅助组与强调色、单一材质、画面占用率和最大空白区。大面积空白必须写清构图职责；脏色、噪点、随机粒子、发光 AI 大脑、漂浮图标、重色字幕条和裁切残留会直接阻止渲染。详细规则见 [视觉干净度系统](references/visual-cleanliness-system.md)。

## A-roll / B-roll 与素材补缺

A-roll 是主叙事画面，B-roll 是在同一声音主轴上切入的证据、操作演示或概念解释。B-roll 不是装饰；如果不能指出它解释的口播，就不应该出现。

素材不足时按这个顺序处理：用户真实素材 → 官方素材 → 已核验关键帧 → 经开工授权生成静态插画/信息图 → 可编辑代码动画 → 保持主画面或纯文字。Skill 不调用视频生成模型，也不使用生成图伪造产品结果、数据和真实背书。详细规则见 [A-roll、B-roll 与镜头桥接](references/roll-and-transition-system.md)。

## 真实案例

仓库提供三个经过授权的压缩预览：Obsidian 软件讲解、不用视频模型的视频 Skill，以及 ICP/网安备案长流程科普。见 [examples/README.md](examples/README.md)。安装包不携带案例视频，避免重复占用空间。

## 运行要求

完整执行需要：

- 能读取和写入本地文件、运行命令并直接展示图片、音频和视频的 AI Agent；
- Python 3.10 或更高版本；
- `ffmpeg` 与 `ffprobe`；
- 浏览器、Remotion、FFmpeg 或其他可完成最终画面渲染的环境。

可选能力：

- 用户自己的 TTS API；
- 已经安装的本地 TTS 模型；
- Apple Silicon 上的 `mlx-audio` 与 Qwen3-TTS。

缺少关键能力时，Agent 必须说明当前能交付到哪一步，不能把“已经读取仓库”当成“已经安装”，也不能把脚本或分镜当成最终视频。

安装后先运行只读体检：

```bash
python3 scripts/doctor.py
```

它会分别报告 Python、FFmpeg、Node/Remotion、中文字体、本地 STT、TTS API 名称和本地 Qwen 模型是否可用；不会安装依赖、下载模型或显示密钥值。

## 输出规格

- 竖屏视频：3:4、1080×1440、30fps；
- 横屏视频：16:9、1920×1080、30fps；
- 独立封面：3:4、1080×1440，同时输出 270×360 缩略图；
- 推荐视频编码：H.264；
- 推荐音频：AAC、48kHz、双声道；
- 综合响度可接受范围：-19 至 -14 LUFS，目标约 -16.5 LUFS。

生成和合成画面默认无地面、无地平线、无投射阴影、无悬浮阴影和地面反射。主体需要与背景分离时，只使用柔和、克制的轮廓光。

## 目录结构

```text
produce-videos/
├── SKILL.md                  # Agent 执行入口
├── agents/openai.yaml        # Codex 界面元数据
├── assets/                   # brief、审批、声音、分镜和主题模板
├── references/               # 制作规则、34 套视觉主题与 88 套布局
├── examples/                 # 三个公开成片案例与哈希清单
├── dist/                     # Release 安装包
├── scripts/                  # 模型发现、校验、质检和打包脚本
├── tests/                    # 自动测试
├── evals/                    # Skill 行为评估用例
├── THIRD_PARTY_NOTICES.md
└── LICENSE
```

`SKILL.md` 是 Agent 的正式执行入口。README 面向第一次接触仓库的人，负责说明能力、流程、安装和使用方式。

## 验证安装

在仓库目录运行：

```bash
python3 -m unittest discover -s tests -v
python3 scripts/validate_theme_catalog.py \
  references/frontend-slides-themes/bold-template-pack/selection-index.json
python3 scripts/validate_layout_catalog.py
python3 scripts/scan_release.py
python3 scripts/package_release.py --output-dir dist
```

验证至少应确认：

- 能读取 `SKILL.md`；
- `scripts`、`references` 和 `assets` 都存在；
- 自动测试通过；
- 34 套视觉主题和 88 套布局完整；
- 开源扫描没有发现个人路径、密钥或未经审核的二进制资产。

自动检查不能替代用户对口播、素材、声音、分镜和最终预览的实际判断，也不能证明视频已经上传、发布或产生真实用户效果。

## 隐私与安全

- 仓库不包含作者个人形象、私人音色、水印、账号资料、本机路径或用户项目素材；
- 用户提供的品牌、人物、声音和素材只属于当前视频项目，不能写回 Skill 仓库；
- API 凭证只从环境变量或系统安全存储读取，不写入聊天、项目文件或日志；
- 安装依赖、下载模型、调用付费服务和上传文件前必须单独取得用户授权；
- 发布前运行 `python3 scripts/scan_release.py` 检查本机路径、联系方式、密钥、符号链接和未经审核的二进制文件。

## 许可证

本项目使用 [MIT License](LICENSE)。第三方组件及模型说明见 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)。

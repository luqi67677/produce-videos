# 视频需求

- 视频模式：未选择 / portrait 竖屏 / landscape 横屏
- 画幅确认回执：待用户确认 / 已回显确认
- 画幅预设：`assets/format-presets.json`
- 最终画幅：portrait = 3:4、1080×1440 / landscape = 16:9、1920×1080
- 项目：
- 品牌或主体：
- 目标观众：
- 发布平台：
- 平台遮挡配置：auto / generic-portrait / douyin-portrait / generic-landscape / 用户自定义
- 平台校准依据：内置保守值 / 用户提供的近期平台截图
- 目标时长：
- 内容模式：账号短视频 / 通用宣传视频 / 用户指定
- 推荐时长：账号短视频 25—75 秒 / 通用宣传视频 90—150 秒 / 用户指定
- 成片硬上限：账号短视频默认 90 秒 / 通用宣传视频 180 秒 / 用户指定
- 一句核心价值：
- 核心问题：
- 开场策略：结果 / 反差 / 真实冲突 / 具体问题 / 操作证据 / 由 Agent 根据资料判断
- 历史参考成片：not-provided / 用户提供的已确认成片路径
- 创作记忆模式：disabled / project-only / workspace-opt-in
- 创作记忆路径：not-required / creator-memory.json / 用户指定的 Skill 外工作区路径
- 跨项目记忆授权：not-required / approved
- 重复人物或角色：none / user-defined / to-define
- 人物定义输入：not-required / 用户描述与授权参考素材
- 必须出现：
- 禁止出现：
- 平台风险词：
- 完整口播母稿：`master-script.json`
- 完整口播确认：待确认 / 已批准
- 口播内容来源代码：pending / approved-script / ai-write-from-materials / transcribe-existing-media / no-spoken-narration
- 口播输入：待提供 / 本轮用户消息 / 已确认稿路径 / 素材路径 / 待转写音视频路径 / not-required
- 用户真实素材清单：`source-assets.json`
- 用户真实素材确认：待确认 / 已批准 / 用户确认无真实素材
- 原始素材审片模式：merged-blueprint / risk-first
- 静态补图策略：pending / user-assets-only / allow-generated-stills
- 静态补图授权：pending / not-required / approved
- 生成素材边界：只补真实素材无法表达的缺口；不调用视频生成模型；不伪造证据
- 最终声音来源代码：pending / recorded-audio / extract-from-video / tts-api / local-tts-model / qwen-open-source / no-spoken-narration
- 声音输入：待提供 / 独立口播音频路径 / 含目标人声的视频路径 / not-required
- TTS 资源状态：pending / not-required / api-configured / local-model-known / qwen-download-approved
- TTS 供应方与模型：待提供 / not-required
- TTS API 凭证位置：pending / not-required / environment / secure-store（只记录位置，不记录密钥）
- 本地模型线索：待提供 / not-required / standard-cache / 用户指定目录
- Qwen 官方来源：`https://huggingface.co/Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign`
- Qwen 当前 MLX 模型：`https://huggingface.co/mlx-community/Qwen3-TTS-12Hz-1.7B-VoiceDesign-bf16`
- Qwen 目标目录：待提供 / not-required / 用户明确指定的 Skill 外目录
- Qwen 安装与下载授权：pending / not-required / approved
- 声音方向原话：待提供 / not-required / 用户原话或“由你判断”
- 开工信息确认：pending / approved / covered-by-user-message
- 旁白来源：pending-user-choice / external / user-reference / other-tts / open-source-model
- TTS API 预检：`tts-api-preflight.json`
- 本机模型发现报告：`model-discovery.json`
- 开源模型状态：未检查 / 缺少模型 / 待用户授权下载 / 已就绪
- 开源模型地址：`assets/qwen-tts-models.json`
- Qwen 声音描述：
- 声音需求单：`voice-brief.json`
- 声音需求确认：待确认 / 已批准
- 声音选择方式：audition（默认 3 个）/ direct-description（仅用户明确要求跳过试听）
- 声音选择文件：`voice-selection.json`
- 用户声音确认：待确认 / 已批准
- TTS 运行时：
- 旁白契约：`narration-contract.json`
- 旁白 manifest：`audio/narration_v1.manifest.json`
- 旁白音频 SHA-256：
- 旁白实际时长 / 采样率 / 声道：
- 全片视觉主题状态：未推荐 / 待用户选择 / 已锁定
- 三套模板样张：
- 用户最终选择：A / B / C / 用户指定模板
- 锁定主题文件：`video-style-theme.json`
- 品牌固有颜色与禁用色：
- 字幕语言与规则：
- 水印：关闭 / 用户提供的已授权资产
- 独立封面：固定 3:4、1080×1440；必须交付
- 封面主视觉：真实产品 / 结果证据 / 用户授权品牌或人物素材
- 运动语法清单：
- 输出文件夹：

> 画幅是第一项决定。未确定 16:9 横屏或 3:4 竖屏时，不开始写稿、生图和渲染。

> 观众可见文案、平台禁用词和内部制作备注分开记录；扫描范围覆盖口播、字幕、画面文字、封面和发布文案。

> 口播内容来源和最终声音来源必须分别回答。用户有口播稿，不等于已有声音；用户有视频内人声，也不等于需要 TTS。

> 缺项必须合并成一次开工问题。已有确定稿、AI 撰写、音视频转写、独立口播、视频内提取、TTS API、本地模型和 Qwen 下载不能拆成后续多轮重复询问。只有依赖安装、模型下载、授权疑点等高风险动作单独取得确认。

> 开工时同时问用户是否有已确认的历史成片、是否要复用项目内或跨项目创作记忆，以及是否会反复使用同一人物。跨项目记忆和人物身份引用必须用户明确授权；不搜索用户全盘，不写回 Skill。

> 平台遮挡配置使用 `assets/platform-overlay-profiles.json`。平台界面会变化，内置数值是保守审查值，用户提供近期截图时应在当前项目建立覆盖，不直接改写全局内置配置。

> 开工时同时确认是否允许在真实/官方素材不足时生成静态插画、信息图或物体图。选 `allow-generated-stills` 后可按镜头缺口自动补图，不再逐镜询问；仍不得调用视频生成模型，也不得用生成图冒充真实证据。

> `pending-user-choice` 只能出现在草稿，正式旁白契约必须在生成或接入音频前改成明确来源。

> 口播确认后先确认用户真实素材；`source-assets-approval.json` 未批准时，不得推荐风格或生成镜头素材。

> 用户选择 TTS 时，开工信息包就要问是否已有 API 或本地模型，并同步收集声音方向。API/模型通过预检后直接制作 3 个同文案试听，不再重复询问声音偏好；`voice-brief.json` 未批准时不能生成试听，`voice-selection.json` 未批准时不能生成整条正式旁白。

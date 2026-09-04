---
name: produce-videos
description: 将讲稿、文档、截图、图片、PPT 或录屏制作成 16:9 横屏或 3:4 竖屏动态视频和独立封面。依次确认完整口播、用户真实素材、整批镜头素材、全量静态分镜和动态样片；音频先确认来源和用户想要的声音，再生成试听，没有可用方案时经授权准备阿里 Qwen3-TTS。开源包不内置发布者个人形象、私人音色、水印或本机路径。
---

# 2026-09-05 视频生成与编辑 V1.9.0

创建日期：2026-09-03

版本：V1.9.0

## 开源边界

- 不内置任何个人形象、私人参考音频、私人水印、账号资料或本机绝对路径。
- 用户提供的品牌、人物、声音和素材只属于当前项目；先确认授权，不得写回 Skill 包。
- 不默认假设品牌色、人物角色、水印或固定音色。
- 内置模板只负责提供视觉系统候选；最终主题由用户选择一次，全片统一读取。

## 交付契约

- 用户要求“制作视频”时，交付可播放成片和一张独立 3:4 封面，不只交付脚本或方案；用户只要求脚本、分镜或审查时不擅自渲染。
- 保留上一个可用版本；修改产生新版本，不覆盖已交付文件。
- 通用宣传视频默认 90—150 秒且不得超过 180 秒；账号短视频默认 25—75 秒，非必要不超过 90 秒。超过上限时压缩主线或拆条，不靠不自然加速声音硬塞。
- 竖屏统一使用 3:4、1080×1440、30fps；横屏使用 16:9、1920×1080、30fps。独立封面始终使用 3:4、1080×1440。
- 只宣传资料可支持的事实；本地输出、上传、草稿、发布和真实用户效果必须分开表述。

## 核心原则

1. 先向用户回显并确认 16:9 横屏或 3:4 竖屏，再进行写稿、生图和排版；不能只把平台或素材尺寸当作画幅确认。
2. 先核验事实与口播，再决定镜头，不让视觉替内容背书。
3. 用户没有视觉方向时，从内置模板库推荐三套真实候选；用户已有视觉系统或明确指定模板时，直接验证并锁定，不强制推荐三套。
4. 三套候选必须使用同一标题、同一代表性镜头和同一目标画幅制作样张，保证可比较。
5. 用户选定后，唯一主题写入 `video-style-theme.json`；封面、插图、字幕、动画和成片共同读取。
6. 完整口播、用户真实素材、整批镜头素材、全量静态分镜和动态样片分别确认；任何一步未确认都不得进入下一步，避免把错误批量复制到下游。
7. 优先使用真实、官方和已授权素材；生成素材只补明确缺口。
8. 字幕只有一个最终渲染层，动画按旁白语义逐步建立。
9. 音频入口必须先明确询问用户有无成品口播、有无可用 TTS API、有无本地模型；只有三者都没有时才提出下载阿里 Qwen3-TTS，禁止静默采用默认模型、默认 API 或默认声音。
10. 正式旁白必须绑定实际音频文件、SHA-256、时长、采样率和声道；最终视频质检要复核这条绑定。
11. Frontend Slides 模板只提供色板、字体角色、材质和标志性动作；必须按中文、真实素材和目标画幅重新构图，不能机械复制演示页。
12. 中文或中英混排标题优先使用中文字体栈；品牌名保持原文大小写，禁止用全大写字体或 `text-transform: uppercase` 把 `Obsidian` 改成 `OBSIDIAN`。
13. 第一张校准画面必须先输出目标原尺寸 PNG 和缩略图，并完成肉眼检查；校准画面未通过，不得批量生成后续版式。
14. 用户确认过的标题是内容事实，必须逐字保留；排版只能调整字号、断行和位置。只有用户明确同意另写封面标题时，才允许使用不同的展示标题。
15. 静态分镜是正式镜头的构图契约，不是只供查看的章节缩略图。成片必须继承分镜中的背景、主视觉窗口、文字层级和信息建立顺序；禁止审核时展示精排分镜，渲染时改成原始录屏全屏轮播。
16. 所有全片渲染入口必须先运行 `scripts/validate_render_gate.py --mode full`；样片入口运行 `--mode sample`。渲染器必须把自己实际读取的旁白契约通过 `--narration-contract` 原样传给门禁，门禁与最终预检必须校验同一份契约；项目存在多个版本时不得退回检查旧的默认文件。门禁还必须校验审批哈希、主题、最终音频、镜头就绪表和动态覆盖表的实际内容，不能只检查文件存在。禁止自写 FFmpeg、Remotion 或浏览器脚本绕过门禁。
17. 录屏隐私检查先建立用户明确点名的 `privacy_targets`，再追踪这些目标在全片的每一次出现。只遮目标实际占用的最小行、字段或区域；目标没有出现在当前裁切中就不加遮挡。不得因为侧边栏里存在一个敏感名称而模糊整栏、整棵文件树或整个素材库。手机状态栏中的录屏红点、录制胶囊或录制计时等系统录制标记一旦被要求隐藏，也必须作为目标覆盖同一素材的全部复用镜头。
18. 口播明确说“第一步、第二步……”时，画面必须持续显示当前步骤、总步骤和流程位置；不能只让观众从声音里猜当前走到哪里。
19. 隐私裁切不得以破坏讲解证据和完整构图为代价。若安全裁切会截掉正在讲解的列表、按钮或结果，改用只命中目标的局部遮挡；账号后台则优先裁掉地址栏、头像和导航，并放大结果区。
20. 每个镜头都要有明确的画面职责。主素材只占一侧时，可在不遮挡证据的负空间加入已授权角色、步骤卡或因果箭头；角色必须完成“对象—动作—结果”链条，例如把文件送入仓库、用手机触发同步、在电脑前沉淀 Skill 或推动闭环。没有可见作用就删除角色；同一姿势不得跨不同语义镜头重复粘贴。
21. 完整口播一经用户确认，立即在独立 `master-script.json` 锁定全文和段落；正式音频生成后再锁定实测总时长。后续任何改字都会使口播、分镜和动态审批失效，必须从头复核全片逻辑与时间轴；补充音频路径等技术信息不得无故使未改字的口播审批失效。
22. 一段口播只绑定一个镜头，一个镜头只承担一个新的信息职责。字幕说到的对象、动作和结果必须在同一时间窗内出现对应画面证据；不能让字幕讲 A、画面展示 B，也不能用无关循环动画填满旁白。
23. 锁定口播后，镜头总时长必须与旁白音频一致。修改画面只能在既有时间轴内重分配；未经用户重新确认口播和时长，不得增加总时长、补写解释句或延长静态停留。
24. 介绍插件、扩展、助手或其他工具时，叙事顺序固定为“准确名称与身份 → 它解决什么问题 → 我如何使用 → 产生什么结果”。同一作用只解释一次，不得先讲操作、后补定义、再重复总结。
25. 每轮修改后必须重跑全片审计：检查非相邻重复画面、开头与结尾撞镜头、已确认画面被误换、字幕与画面错位、最长无变化停留和总时长漂移。用户只要求局部调整时，保留其他已通过内容不变。
26. 门禁必须验证真实产物，不接受只填路径或勾选布尔值：主素材、分镜帧、补图、动态样片和修改预览都必须存在且可读取；动态样片还必须包含可探测的视频流和有效时长。
27. 阶段审批必须覆盖本阶段真正使用的文件：口播审批覆盖独立口播母稿，真实素材审批覆盖清单、实际文件和联系表，镜头素材审批覆盖素材清单，分镜审批覆盖镜头就绪表及全部分镜帧，动态审批覆盖运动覆盖表及全部样片。审批一个无关文件不得放行渲染。
28. 收到成片修改意见后，先在 `shot-readiness.json.revision_scope` 锁定基线、反馈项、受影响镜头和必须保持不变的镜头。受影响镜头先输出原尺寸帧、联系表或短样片并获得确认；未确认前不重新渲染全片，保留镜头与基线不一致时直接停止。
29. 每个镜头在进入渲染前都要记录版式与隐私复核：对齐、文字溢出、孤立线条、箭头终点、空白用途、录屏标记、目标遮挡和非目标内容清晰度。人物或角色参与时还要记录动作签名，避免不同语义镜头重复同一姿势。
30. 用户选择本地模型后，才在标准模型缓存和用户明确提供的目录中发现开源 TTS；同时有限检查当前 Python、活动虚拟环境、PATH 和模型目录同级的虚拟环境，不遍历整块磁盘。默认 Python 无法导入依赖不等于电脑上没有运行环境；发现候选后必须使用报告推荐的同一 Python 完成最小加载和后续生成。
31. TTS API 或本地模型就绪后，必须先询问用户想要的性别呈现、年龄感、气质情绪、能量、语速和明确不想要的特征；把用户原话与归纳结果写入 `voice-brief.json` 并让用户确认。需求未确认不得生成试听。确认后围绕同一声音方向生成 3 个同文案试听，只改变次要维度，不得擅自给用户三个随机音色。选择结果、声音需求、API/模型预检、试听文件和批准记录写入 `voice-selection.json`。未明确选声不得生成整条正式旁白。
32. 每条视频都交付独立 3:4 封面。没有已授权人物时使用真实产品、结果证据或用户品牌素材，不生成发布者个人形象，也不从横屏首帧裁切代替。
33. 用户提供的真实素材必须在推荐风格和生成镜头素材前先单独盘点、展示并审批；整批镜头素材还要在排静态分镜前再次完整展示并审批，包含素材清单、来源授权、联系表、复用矩阵和封面草图。两次审查不能合并，也不能只审批文字清单。
34. 平台风险词和用户禁用词必须同时检查口播、字幕、画面文字、封面和发布文案；内部导演备注不得进入观众画面。
35. 内置主题库必须保持 34 套完整可用。每次匹配先校验完整目录，再从全部 34 套的索引中筛选；入围的三套都必须用同一真实内容输出 3:4 封面帧、目标画幅内容帧和信息流缩略图并逐项质检。低质量候选应修复或替换，不能为了凑三套而展示。
36. 每次只向用户交付一个待确认阶段，说明“现在确认什么、确认后进入哪一步”。图片、音频和视频必须直接作为可查看或可播放的主审查产物；本地 HTML 只能辅助查看，不能成为唯一入口。视频还要同时提供联系表作为无法播放时的兜底。
37. 用户的短回复必须绑定紧邻的单一问题解释。`A/B/C`、编号、`通过`、`继续`、`可以`或“基本上可以”只有在上一条已经明确阶段、候选和确认后果时才可登记；若同一条消息包含修改意见、否定或多个未决问题，不得擅自当作通过。新项目使用 V1.1 审批模板记录审查提示、解释方式和实际展示产物。
38. 最终预检不是建议清单：画幅、时长、音轨、旁白绑定、黑帧和可接受响度中的硬失败必须修复后再交付。综合响度超出 -19 至 -14 LUFS 或真峰值高于 -1.0 dBFS 时，`video_preflight.py` 返回失败；仅在可接受范围内偏离 -16.5 LUFS 时才警告。

## 审查交付规则

进入任一确认节点前读取 `references/review-system.md`。每轮只展示当前阶段完整产物和一个确认问题；先保证用户能直接看到或播放，再等待回复。收到回复后先写审批文件并校验，再开始下一阶段，不能把多个确认合并，也不能一边等待确认一边提前批量生成下游内容。

## 默认流程

### 0. 建立项目与画幅

- 读取 `assets/format-presets.json`。
- 必须先发出一条可见画幅回执，写明“本项目采用横屏 `16:9` / 竖屏 `3:4`”；用户已明确说明时也要回显确认，未说明时只询问这两个选项。
- 在 `video-brief.md` 记录“画幅确认回执”和最终画幅；回执完成前不得生成样张、静态分镜或排版画面。
- 从 `assets/video-brief-template.md` 建立 `video-brief.md`。
- 记录目标平台、受众、时长、禁用词、已授权素材和输出目录。
- 抖音、视频号或其他账号短视频默认记录 25—75 秒目标；通用宣传视频记录 90—150 秒目标。两类都必须记录对应硬上限。

### 1. 核验事实并完成口播

- 从素材中提取主张，写入 `claims-ledger.md`。
- 区分事实、推断、演示数据和待核验项；待核验内容不得写成已证实事实。
- 涉及“官方/第三方”“插件/扩展”“预览/同步/发布”等产品属性时，必须查阅官方帮助、官方仓库或插件目录后再写入口播；不得凭界面印象给工具定性。
- 从 `assets/master-script-template.json` 建立 `master-script.json`，完成可独立朗读的完整口播；音频来源确认后再从这份母稿建立正式 `narration-contract.json`。
- 先从头到尾检查叙事顺序和重复内容，再让用户确认整篇口播。工具类段落按“身份与作用 → 使用方式 → 结果”展开，不在段尾重复总结已经说过的作用。
- 显示字幕使用 `display_text`，TTS 可使用单独的 `tts_text` 做发音归一化。
- 运行 `scripts/validate_master_script.py --require-ready` 后一次性展示整篇口播。用户确认后生成 `script-approval.json`，覆盖 `master-script.json` 的 SHA-256。
- 建立旁白契约时写入 `approved_script_path` 和 `approved_script_sha256`；契约中的每个 `scene_id/display_text` 必须与母稿逐项一致。此后改动任何 `display_text` 都必须重新确认完整口播，并使后续素材、分镜和动态审批失效；只补充音频路径、模型和时长不会改变母稿审批哈希。

### 2. 盘点并确认用户真实素材

- 口播通过后，先请用户提供或指定希望使用的真实录屏、截图、照片、产品界面、Logo、图表和官方资料；此时不生成补图、不做风格样张、不排分镜。
- 从 `assets/source-assets-template.json` 建立 `source-assets.json`。逐项记录实际文件、SHA-256、来源、授权、用途和隐私检查；真实素材必须复制或整理到当前项目中，Skill 包内不保存任何项目素材。
- 若用户没有真实素材，明确回显“本项目没有用户真实素材，将使用官方/授权素材或生成素材补足”，把原因写入 `no_real_assets_reason`，仍需用户确认，不能默认为空。
- 有真实素材时生成一张联系表，让用户逐项确认：素材是不是他要的、人物/产品是否正确、哪些信息要隐藏、哪些素材禁止使用。运行 `scripts/validate_source_assets.py --require-ready` 后，展示联系表。
- 只有收到明确确认，才生成 `source-assets-approval.json`，并覆盖 `source-assets.json`、全部真实素材和联系表的 SHA-256。此前不得推荐风格、生成镜头素材或排静态分镜。
- 后续新增、替换或修改真实素材会使本阶段及其下游审批失效，必须重新展示并确认。

### 3. 从模板库推荐三套方案

读取：

- `references/frontend-slides-themes/bold-template-pack/selection-index.json`
- 候选主题对应的 `preview.md`
- 只有进入候选后才读取对应 `design.md`

先运行 `scripts/validate_theme_catalog.py`，确认索引与 34 个模板目录一一对应且每套设计说明完整；校验失败时停止推荐。

若用户没有提供视觉方向，根据主题、受众、情绪、信息密度、平台、已批准真实素材和已提供品牌限制，选择三个不同的真实模板：

- A `balanced`：信息清楚、阅读稳定、风险最低。
- B `expressive`：更有视觉记忆点，但仍保证可读。
- C `unexpected-fit`：不是最直觉的选择，但能给内容带来合理的新表达。

先在 `visual-style-options.json.catalog_evaluation` 逐套记录全部 34 个模板的适配分数、`shortlisted/rejected` 结论和内容理由；不得只记录最后三个。然后把入围三套的推荐理由、风险、模板 slug、来源路径和样张写入 `options`。三套样张必须：

- 使用相同的已批准真实内容；没有真实素材时使用同一份已确认内容，不用色块或空模板代替；
- 使用最终目标画幅；
- 同时展示封面标题和一个代表性内容镜头；
- 不混合多个模板的设计语言。

三套都要输出 3:4 封面帧、目标画幅内容帧和 270×360 缩略图，并把三套完整合成一张可直接查看的 `overview_preview`；不得只给本地 HTML 链接。通过 `scripts/validate_style_options.py` 后再展示。未通过的候选先修复或从 34 套中替换；三套全部通过后才等待用户选择 A、B 或 C。用户选定后，把原话和时间写入 `selection_approval`，将状态改为 `selected`，再运行带 `--require-selected` 的校验。用户也可以明确指定内置模板；此时记录 `user_override: true`，仍需生成该模板的真实双帧和缩略图确认。

选定后，从 `assets/video-style-theme-template.json` 生成并锁定 `video-style-theme.json`。在用户明确要求重选前，不得静默换主题。

### 3.1 先做一张校准画面

- 读取 `references/layout-system.md` 和 `references/implementation.md`，先把所选主题翻译成当前内容的版式系统。
- 默认逐字使用用户确认的完整标题，只调整字号、语义断行和位置；不得为了套模板擅自删词、改写、换标点或另加一个替代标题。只有用户明确确认独立封面标题时，才记录并使用不同的展示标题。
- 标题允许行数由当前 brief 按标题长度与画幅确定，不预设两行；封面仍只保留一个主视觉和必要辅助信息，不把页码、模板名、日期、镜头号和内部标签塞进画面。
- 有真实截图、产品界面、人物或证据时，选一个作为唯一主视觉；除非用户明确选择纯文字封面，主视觉建议占可用画布约 42%—62%。
- 中英混排标题使用中文优先字体栈，并为品牌词设置保留原始大小写的独立样式。
- 先输出原尺寸 PNG，再输出信息流缩略图；同时检查中文断行、品牌大小写、主视觉大小、空白分配和缩略图可读性。
- 校准画面通过后，才进入音频和整批镜头素材阶段；若未通过，只修这一张，不批量复制错误。

### 4. 确认音频来源并让用户选声

- 开始音频工作前先读取 `references/audio-system.md`，并一次只问清四种互斥情况：①已有可用成品口播；②已有可调用的 TTS API；③电脑上已有本地 TTS 模型；④以上都没有。不得跳过这个问题直接扫描模型或下载。
- 用户选择成品口播时直接登记实际文件；选择 TTS API 时，只通过环境变量或系统安全存储读取凭证，聊天记录、项目文件和 Skill 包都不得保存密钥。完成最小 API 调用和声音能力检查，把不含密钥的结果写入 `tts-api-preflight.json`。
- API 预检通过后，先询问并确认用户的声音需求，写入 `voice-brief.json`；需求单通过 `scripts/validate_voice_brief.py --require-approved` 后，才用同一段 5—12 秒中性文案生成 3 个围绕该方向的试听。用户明确要求跳过试听时，才允许直接确认一条声音描述。把声音需求、API 预检、试听文件、最终声音和用户原始确认写入 `voice-selection.json`，再运行 `scripts/validate_voice_selection.py --require-approved`。
- 用户选择本地模型时，运行 `scripts/discover_audio_models.py --output project/model-discovery.json`；模型只检查标准缓存和用户指定目录，运行环境只有限检查当前 Python、活动虚拟环境、PATH、常见虚拟环境目录和模型目录同级环境。用户已知旧项目使用的 Python 时，用 `--runtime-python` 明确追加。
- 发现兼容的 Qwen3-TTS MLX 模型时，让用户选择使用哪个候选，并优先复用报告中的 `recommended_runtime_python`；使用 `scripts/model_preflight.py --runtime-python <兼容 Python> --smoke-test` 对选中目录做最小加载。只有有限发现和用户已知入口都没有可用环境时，才能把 `mlx-audio` 判定为缺失并申请安装授权；不得把默认 `python3` 的一次导入失败当成电脑缺少依赖。发现其他开源 TTS 时先说明当前 Skill 没有对应适配器，让用户决定提供兼容调用方式、改用其他 TTS，还是准备 Qwen。
- 用户选择“以上都没有”，或选择本地模型但没有兼容候选时，展示 `assets/qwen-tts-models.json` 中阿里 Qwen3-TTS 的精确地址、预计大小和目标目录。只有用户明确授权后才安装依赖或下载；拒绝下载且没有其他音频来源时停止在音频阶段。
- 本地模型通过预检后，先用一个简短问题收集性别呈现、年龄感、气质情绪、能量、语速和禁忌特征；用户可回答“不限”或“由你判断”，但 Agent 不得跳过询问。把用户原话和归纳结果写入 `voice-brief.json`，展示给用户确认并运行 `scripts/validate_voice_brief.py --require-approved`。通过后才用同一段 5—12 秒中性文案生成 3 个围绕该方向的试听；三个候选固定用户确认的核心条件，只在音色明暗、亲密感或节奏等次要维度上拉开差异。把声音需求、模型发现报告、模型预检报告、候选试听、最终描述和用户原始确认写入 `voice-selection.json`，运行 `scripts/validate_voice_selection.py --require-approved`。
- `voice-selection.json` 未通过时，只允许生成短试听，不得生成完整旁白。正式 Qwen 旁白必须把该文件传给 `scripts/generate_qwen_voice.py --voice-selection`，并在 `narration-contract.json` 绑定其 SHA-256。
- 草稿阶段的 `voice_source` 保持为 `pending-user-choice`；用户确认来源后再建立正式旁白契约。
- 用户选择自己的成品口播时，记录为 `external`，并记录音频路径、SHA-256、实际时长、采样率和声道。
- 用户选择授权参考音频时，记录为 `user-reference`，拆分记录参考音频和最终旁白，并记录授权说明、参考文本和两个文件各自的 SHA-256。
- 用户选择 TTS API 时，只使用用户明确指定且通过预检的服务；正式音频必须绑定已批准的 `voice-selection.json`，再使用 `scripts/register_audio_artifact.py --voice-selection` 登记产物。当前 Skill 不擅自替换模型或调用未说明的云端服务。
- 用户选择 Qwen3-TTS 后，模型发现、下载授权、模型预检和声音选择四项缺一不可；不得把“下载完成”直接当成“声音已经选好”。
- 当前 Qwen 执行器是 Apple Silicon 的 `mlx-audio` 路线；非 Apple Silicon 不得把 Qwen 原始模型地址直接交给该执行器，应改用用户明确指定的兼容 TTS 或停止。
- Qwen 模型和声音选择均通过后，使用 `scripts/generate_qwen_voice.py --runtime-python <预检报告中的 python_executable> --segments-file --voice-selection` 按场景分段生成正式旁白；试听和正式旁白必须沿用同一运行环境。不提供或读取 Skill 内置声音预设。
- 使用 `assets/tts-pronunciation-map.json` 处理专有名词读法。
- 生成后读取音频 manifest，把真实时长和场景时间戳回填到 `narration-contract.json`；根据已批准的真实素材清单列生成素材缺口，所有新增素材记录来源、用途和授权状态。
- 对每段真实界面录屏建立隐私区域清单，至少检查地址栏、账号区、侧边栏、仓库/栏目/项目名称、草稿标题、文件树、本地路径和通知。先记录用户明确要求隐藏的精确文字或字段，再逐镜判断它是否实际可见；同一素材复用时重新按当前裁切定位目标，不得机械继承比目标更大的旧遮挡框。
- `privacy_targets` 中每项记录 `target_id`、`exact_text_or_region`、可能出现它的 `asset_ids` 和 `treatment`（`crop` 或 `opaque-mask`）。每个镜头的 `privacy_review` 必须列出已检查、实际可见和已处理的目标；实际可见与已处理集合必须完全一致。
- 教程画面中的非敏感目录、素材标题、正文、插件设置和操作结果属于讲解证据，默认保持清晰可读。只有用户点名、授权清单明确标为敏感，或画面出现账号、密钥、手机号等高风险个人信息时才遮挡；遮挡不能破坏本镜头要证明的操作。

### 5. 生成并确认整批镜头素材

- 在静态分镜前完成全部计划使用的录屏、截图、图片、图表、生成补图和独立封面草图；每项记录 `scene_id`、来源、授权、用途和文件路径。
- 输出全部原始素材联系表与素材复用矩阵。相邻镜头复用同一主素材时，必须说明后一个镜头新增的可见状态或信息。
- 用户逐项检查素材与口播是否对应、人物/产品是否正确、隐私是否处理、是否重复、主题是否一致。根据反馈只修改受影响素材。
- 收到“全部镜头素材通过”的明确确认后，生成 `assets-approval.json`，记录素材清单、全部素材、联系表、复用矩阵和封面草图的 SHA-256；此前不得排完整静态分镜。

### 6. 静态分镜

- 按 `assets/storyboard-template.md` 编写分镜。
- 先按最终旁白段落建立严格的一对一映射：每个 `scene_id` 只能绑定一个旁白段，每个旁白段必须且只能出现一次。镜头中的 `narration` 必须与契约中的 `display_text` 完全一致。
- 先分章节，再把章节拆成可执行镜头；章节只负责叙事归类，不能直接拿一张章节板撑完整段旁白。
- 教程、工作流和录屏类内容必须按真实操作状态拆镜头。默认每 2—4 秒出现一次新的有效视觉职责；连续操作尚未完成时可适当延长，但必须通过界面状态变化、局部重点切换或因果推进保持信息更新，不能用整页晃动代替切镜。
- 口播包含编号步骤时，每个相关镜头都必须显示当前编号和总步骤，章节切换时同步推进；编号不能只在开头闪一次。
- 口播声称“已同步、已进入草稿箱、已发布、已保存”时，镜头必须展示对应动作或结果证据；通用预览页、空白界面和无状态变化的截图不能替代结果证据。
- 口播指向某个按钮、字段、结果或界面区域时，分镜必须写出对应的 `focus_target`、出现时间和退出时间，并用描边框、手绘圈、局部提亮或短箭头中的一种做语义标注；禁止只播放整段录屏，让观众自己寻找重点。
- 分镜必须同时列出章节数、镜头数、平均镜头时长和最长静态停留。90—150 秒教程若只得到个位数镜头，默认判定拆分不足，除非逐镜说明长镜头的连续操作理由。
- 每个镜头写明：旁白、观众可见文字、主素材、开始状态、变化状态、结束状态和退出状态。
- 每个镜头还必须写明新增加的信息、可见证据、视觉签名和最长无变化停留。没有新增信息或没有对应证据的镜头直接删除；同一视觉签名跨不同语义复用必须证明状态确实推进。
- 每个镜头输出可读取的原尺寸分镜帧，并在 `layout_review` 记录对齐、文字溢出、孤立线条、箭头/连线终点和空白用途检查；任何一项未通过都不能进入样片。
- 使用最终画幅输出整套静态分镜；抽检不足以替代全量检查。
- 复用已通过的校准画面骨架；每个镜头仍按自己的语义选择主视觉，不把所有内容套成同一张 PPT 页面。
- 对录屏镜头逐条写明素材入点、出点和这段真实发生的操作；只写“播放某段录屏”不算可执行分镜。录屏必须进入分镜指定的内容窗口，除非分镜明确批准全屏界面演示。
- 分镜中的装饰框只属于被批准的构图层，不能在渲染器里自动给每段素材再套一层彩色外框。语义标注与装饰框必须分开记录。
- 录屏运动本身杂乱、停顿过长或与口播无关时，先截取最能证明结果的关键帧，再按分镜重构静态信息层；有明确素材缺口时才生成补图，不能靠循环、重播、随机裁切填满旁白。
- 用户确认后生成 `storyboard-approval.json`。

### 6.1 修改既有成片

- 先复制当前已通过的 `shot-readiness.json` 作为不可变基线，记录文件路径和 SHA-256；不要直接覆盖后再回忆哪些镜头原本通过。
- 把用户每条反馈写成独立反馈项，包含原话、受影响镜头、验收条件和解决状态；受影响镜头与保留镜头必须完整覆盖全片且不能重叠。
- 只渲染受影响镜头的原尺寸帧、联系表或短样片。用户确认这些预览后，才允许重新渲染全片。
- 保留镜头必须与基线中的完整镜头记录一致；如确需连带修改，把它加入受影响镜头并说明原因。

### 7. 动态样片

- 先列出全片所有运动语法。
- 每种首次出现或高风险运动语法至少制作一个会进入正式成片的最短样片。
- 样片使用已确认的主题、旁白、字幕时间轴、水印设置和真实素材。
- 教程类样片至少验证一次“口播线索出现 → 对应目标被圈出或提亮 → 标注及时退出”的完整同步，不得用随机装饰动画代替语义指示。
- 重点标注必须先在原生分辨率关键帧上确认目标坐标。默认使用光标圈、下划线、局部提亮或短箭头；禁止用覆盖大面积内容的矩形框、整页彩色边框或每镜必出的框线冒充特效。
- 动态样片必须直接消费静态分镜的构图：真实视频只在分镜规定的内容窗口内播放，标题、说明卡和流程节点按口播逐项建立并保持。样片若与分镜看起来是两套东西，直接判定失败。
- 向用户直接展示可播放样片，并同时展示联系表兜底；不能只打开本地播放器页面或只给路径。用户确认后立即生成并校验 `motion-approval.json`，再进入全片。

### 8. 渲染与质检

- 只在五项审批通过后渲染全片：`script`、`source-assets`、`assets`、`storyboard`、`motion`。
- 全片渲染前必须先运行 `python3 scripts/validate_render_gate.py <project> --mode full --narration-contract <project>/narration-contract.json`；返回非零时任何渲染器都必须停止。
- 多步骤流程的片尾回顾必须让全部节点保持可读，当前节点随口播逐项高亮，连线、进度或方向提示同步推进；禁止一开始全部亮起后静止等待整段旁白结束。
- 同一片尾构图连续停留不得超过 6 秒。较长回顾至少拆成两种构图，再用闭环图或行动引导收束；用户要求点赞、收藏或关注时，必须给行动引导独立画面并与口播同步。
- 运行主题、旁白、镜头、运动覆盖和审批校验。
- 渲染门禁必须核对口播全文哈希、旁白段与镜头的一对一映射、镜头总时长与音频总时长、重复视觉签名和最长无变化停留；任何一项漂移都停止渲染。
- 渲染门禁还必须核对真实文件、审批覆盖范围和 `revision_scope`；不能用无关文件审批、空路径、缺失分镜或不存在的样片获得 PASS。
- 使用 `video_preflight.py` 检查画幅、时长、编码、音轨、响度、黑帧、静音和联系表；命令返回非零时必须修复并重新预检，不能带着硬失败交付。
- 人工检查事实、隐私、授权、文字可读性、字幕安全区、遮挡和镜头连续性；隐私检查按素材复用关系覆盖全片，不能只抽一张代表帧。逐镜确认遮挡仅命中 `privacy_targets`，同时确认非敏感教学内容没有被误模糊。

## 标准产物

```text
project/
├── video-brief.md
├── claims-ledger.md
├── master-script.json
├── narration-contract.json
├── source-assets.json
├── tts-api-preflight.json
├── model-discovery.json
├── model-preflight.json
├── voice-brief.json
├── voice-selection.json
├── visual-style-options.json
├── video-style-theme.json
├── asset-manifest.md
├── shot-readiness.json
├── motion-coverage.json
├── script-approval.json
├── source-assets-approval.json
├── assets-approval.json
├── storyboard-approval.json
├── motion-approval.json
├── storyboard/
├── motion-samples/
├── cover/
│   ├── cover-portrait.png
│   └── cover-thumbnail.png
├── audio/
│   └── narration_v1.manifest.json
├── subtitles/
└── final/
```

每条完整视频都必须交付独立 3:4 封面。读取 `assets/cover-brief-template.md`，使用已锁定主题原生重构，不得用横屏首帧裁切代替。

## 校验命令

```bash
python3 scripts/validate_master_script.py project/master-script.json --require-ready
python3 scripts/validate_review_approval.py project/script-approval.json --require-stage script --require-approved
python3 scripts/validate_source_assets.py project/source-assets.json --require-ready
python3 scripts/validate_review_approval.py project/source-assets-approval.json --require-stage source-assets --require-approved
python3 scripts/validate_theme_catalog.py \
  references/frontend-slides-themes/bold-template-pack/selection-index.json
python3 scripts/validate_style_options.py project/visual-style-options.json \
  --catalog references/frontend-slides-themes/bold-template-pack/selection-index.json
python3 scripts/validate_video_theme.py project/video-style-theme.json --require-locked
python3 scripts/validate_layout_preview.py --html project/cover/calibration.html \
  --image project/cover/calibration.png --expected-width 1920 --expected-height 1080 \
  --exact-title "用户确认的完整标题" --exact-token Obsidian \
  --forbid-token OBSIDIAN --max-title-lines 3
python3 scripts/discover_audio_models.py --output project/model-discovery.json
python3 scripts/model_preflight.py --model-path <模型目录> --runtime mlx-audio \
  --runtime-python <model-discovery.json 中的 recommended_runtime_python> \
  --model-id mlx-community/Qwen3-TTS-12Hz-1.7B-VoiceDesign-bf16 \
  --model-url https://huggingface.co/mlx-community/Qwen3-TTS-12Hz-1.7B-VoiceDesign-bf16 \
  --smoke-test --output project/model-preflight.json
python3 scripts/validate_voice_brief.py project/voice-brief.json --require-approved
python3 scripts/validate_voice_selection.py project/voice-selection.json --require-approved
python3 scripts/register_audio_artifact.py --contract project/narration-contract.json \
  --audio project/audio/narration.wav --voice-source other-tts \
  --provider <供应方> --model-id <模型标识> --model-url <HTTPS服务地址> \
  --runtime api --voice-selection project/voice-selection.json
python3 scripts/validate_narration_contract.py project/narration-contract.json --require-timestamps --require-audio --require-script-lock
python3 scripts/validate_shot_readiness.py project/shot-readiness.json \
  --narration-contract project/narration-contract.json
python3 scripts/validate_motion_coverage.py project/motion-coverage.json
python3 scripts/validate_review_approval.py project/assets-approval.json --require-stage assets --require-approved
python3 scripts/validate_review_approval.py project/storyboard-approval.json --require-stage storyboard --require-approved
python3 scripts/validate_review_approval.py project/motion-approval.json --require-stage motion --require-approved
python3 scripts/validate_render_gate.py project --mode full \
  --narration-contract project/narration-contract.json
python3 scripts/video_preflight.py project/final/video.mp4 --orientation portrait --max-duration 180 \
  --narration-contract project/narration-contract.json --require-narration-binding
python3 scripts/scan_release.py
# 发布者个人标识只通过外部文件传入，不把真实姓名写进 Skill：
# python3 scripts/scan_release.py --deny-file /安全位置/private-deny-terms.txt
# 如需同时检查项目产物：追加 --project-root project
```

## 按需读取的参考

- 模板推荐与主题锁定：`references/visual-style-system.md`
- 内容到视频编排：`references/content-to-video-orchestration.md`
- 导演与分镜：`references/director-workflow.md`
- 动画语法：`references/motion-system.md`
- 版式与安全区：`references/layout-system.md`
- 声音系统：`references/audio-system.md`
- 渲染实现：`references/implementation.md`
- 质量门：`references/quality-gates.md`
- 审查交付与短回复：`references/review-system.md`

## 禁止事项

- 不在用户选择前批量生图或渲染全片。
- 不用固定三套模板冒充内容匹配。
- 不把不同模板的字体、颜色和构图规则拼成一套。
- 不把模板演示页的全大写标题、页码、版式密度和装饰信息机械搬进中文视频。
- 不用全大写字体或 CSS 大写转换改变品牌名原始大小写。
- 不以“信息减法”“缩略图可读性”或“模板适配”为理由擅自缩短、改写用户已经确认的标题。
- 不把 PPT 整页直接当视频画面。
- 不把已批准分镜仅当目录，再用原始录屏全屏轮播、重播或随机裁切替代其构图。
- 不自动给全部录屏套彩色外框；不把覆盖大面积界面的矩形框当作重点标注。
- 不用通用预览页冒充“已同步到草稿箱”等结果证据；不让多步骤片尾一开始全部亮起后静止停留。
- 不允许渲染器读取一份旁白契约、门禁却校验另一份旧契约。
- 不把“隐私检查”理解为整栏打码。禁止模糊整个侧边栏、文件树、素材库或 Skill 列表来隐藏其中一两个目标；当前镜头看不到目标时禁止添加无意义毛玻璃。
- 不虚构真实截图、用户数据、产品界面或第三方背书。
- 不把项目中的私人资产复制回 Skill 包。

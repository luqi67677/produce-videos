# IP 讲解人导演规则

适用于用户采用一个已有 IP 形象，配旁白讲解的动画视频。先锁住已批准的口播、声音与主题，再安排人物。人物负责讲述关系，不承担虚构操作或事实证据。 用户选择无人物时，不调用人物配置、出场表与动作分支；已有 IP 形象不等于每片必须出镜。

## 用户选择的人物模式

仅用户选择静态原图讲解人时，采用 `presentation.mode=static-presenter`、`body_motion=fixed`、`animated_regions=[]`、`mouth_behavior=non-speaking`、`mouth_driver=null`。嘴、眼睛和身体都不动；人物按讲解职责静态出现，主画面按题材选真实素材、物件或必要图解，承担主要解释与信息变化。

人物旁可添加独立的小喇叭和轻微声波，提示当前有旁白。图标作为单独的图解资产与图层，不绑定人物嘴部，不变形人物，不冒充口型、眨眼或身体动作；声波也不能替代流程、对比或因果关系的图解运动。

用户当次明确要求覆盖旧长期行为配置。继续复用已批准身份、口播、主题与声音；历史动作或口眼配置不自动恢复。静态模式不要求生成动作或嘴眼素材，也不要求人物动效试样；身份、分镜与整片预览仍按各自门禁审查。

`generated-performance` 只在用户明确选择人物表演时采用；`audio-driven-presenter` 只在用户明确要求嘴动、眨眼时采用。新动作必须来自实际头部或手势素材、分层角色表演或可核验的动作序列。整张静图平移、旋转、漂浮只属于图层运动，不能称为点头、抬手或手势；静态模式入场后保持整个人物固定，不添加这些循环运动。

本机配置优先读取用户已指定的路径或 `PRODUCE_VIDEOS_PRESENTER_CONFIG`。在双 IP 工作区，读取所属 IP 的 `00-账号体系/默认视频讲解人.json`。配置只放在用户工作区，人物图片与私人绝对路径不进入公开 Skill。默认配置有 `identity_authorization`、`animation_authorization`、`identity_anchor`、`source_refs`、`presentation` 和 `motion_effect_approval`；局部口眼参数仅用于旧口眼模式。文件缺失或哈希改变时保留已选身份，指出缺项，不擅自换人或伪造动作素材。

授权和审片分别保存。用户明确要求少量自然动作就是本轮制作授权；原图采用批准不能替代新增动作、分镜或成片批准。默认行为可以是已授权，实际新效果仍为待审。

## 轻微角色表演契约（仅明确选择时）

用户明确选择旁白配少量自然动作时，采用 `presentation.mode=generated-performance`、`performance_style=subtle-presenter`、`body_motion=subtle`、`animated_regions=[head,hands]`、`mouth_behavior=non-speaking`、`mouth_driver=null`。保存本轮制作授权；旧静态或口眼批准不能替新动作背书。新动作短样未制作时 `motion_review.status=sample-not-created`，所有效果复核为 false，用户效果批准保持未批准。

复用 `generated-performance` 原有身份、动作与轮廓检查。已有批准原图作为身份锚点；身体表演的代表动作与轮廓检查不能继续标“不适用”。每镜保留实际 `action/action_signature`、讲解职责和复用理由，并声明 `physical_action=true`、`lip_sync=false`、`mouth_audio_sync=false`。同一动作复用须有经审查的叙事理由，不要求每帧换姿势。`subject_interaction.required` 只在人物实际接触对象时为 true，点头或讲解手势不虚构对象操作。

`presentation.source_refs` 与 `motion_review.source_refs` 绑定实际动作素材的 `region/path/sha256`；`region` 按实际计划填写 head、hands，可选 eyes，不得用原图本身代替新头部或手势素材。`motion_review` 沿用实际 `sample_path/sample_sha256`、正式 `audio_path/audio_sha256`、身份锚点 `character_asset_path/character_asset_sha256` 和整轨 `audio_start_seconds/audio_end_seconds`。

实际短样复核后才填 `reviewed`、`subtle_motion_verified`、`mouth_not_speaking_verified`、`identity_preserved_verified` 和 `anatomy_safe_verified`。`lip_sync_verified=false`、`mouth_audio_sync_verified=false`，`mouth_driver=null`。未制作时 status=sample-not-created、以上各项均为 false；不能拿旧动嘴短样填入。真实视频、音频和时长检查证明媒体与绑定有效，不证明自然程度或用户已批准。

先做 4—8 秒实际短样，沿用正式旁白窗口，展示计划中的小动作与自然停顿。检查头部和手势幅度、动作返回、手指与肢体安全、脸和服装连续性、嘴未讲话以及角色是否挤占图解。未生成动作素材时只交付导演安排，不生成假动作证明。用户确认实际短样后再沿用效果；短样不替代整片预览。

## 出场决策

按现有口播标注引入、概念、机制、对比、转折、建议和收束。每段回答：观众此时需要明白什么？人物出现能帮助哪个理解或情绪转折？只有“好看、填空、保持 IP 曝光”时不安排出场。

- 开场可以建立讲述者，标题或问题仍须在 0—2 秒可读，不先播角色介绍。
- 概念解释可与清楚的对象同框。人物不是流程里的用户、商家或模型节点，除非脚本明确如此。
- 机制、复杂对比、证据、三项以上列表优先用图解全画幅，让人物退场。因果链本身必须成立。
- 转折、提醒和建议可让人物短暂返回。具体清单展开后再让位。
- 收束可返回最后一句；保留必要关系或结论，不增加未经批准的结尾文案。

没有固定出场比例或最低镜数。逐段决定，不每镜贴角色，也不为了变化每几秒切一次。

## 旧口眼模式：固定原图与局部层

原图直接作为身份锚点，绑定授权语句与 SHA-256，不强制生成新身份或两个身体姿势。可以裁成全身、半身或面部，保持比例，不切坏关节或饰品，不镜像或拉长。人物讲话时嘴应足够大，信息流里也能看见开合；全身太小就改用半身。

轻量实现：用 imagegen 在已授权的原图上制作张嘴和闭眼状态，保持身份。嘴部先校准闭嘴与张嘴的唇线，把两张纹理变形到同一中间唇形，再合成不透明嘴部；只在外围皮肤处羽化。不能把位置不同的两套嘴唇直接淡入淡出，否则半开嘴会重影。旧透明叠加仅兼容历史工程；明确选用该口眼模式的新工程采用唇线连续变形，校准后先做短样。眼部单独合成并检查睫毛重影。不要整张切换生成图。局部矩形、素材 SHA 与原图尺寸写入 `presentation.local_composite`，每帧始终使用同一原图作底图。检查编码前区域外像素保持一致，再复核实际编码后的嘴、眼、脸和发丝。

使用 `scripts/build_presenter_motion.py` 读取正式旁白 PCM WAV，产生逐帧音量与眨眼轨迹。音量轨迹做短时平滑与静音阈值：有声音时嘴开合，停顿时闭嘴；不使用固定频率不停开嘴，不使用 BPM 或节拍检测替代配音时间。眨眼默认间隔 4—7 秒、持续 120—180 毫秒，随机种子固定；不跟着每个词眨眼。眼睛不默认左右乱看。

`scripts/render_presenter_demo.cjs` 可把轨迹和局部素材合成实际短样，保留原轨声音；依赖 `@napi-rs/canvas`、FFmpeg 与 FFprobe，模块路径可通过 `--canvas-module` 指定。它只实现音量开合，输出明确 `mouth_driver=amplitude`、`phoneme_level_lip_sync=false`。这足以表达“嘴在讲话”；不宣称逐字音素口型。更精确的音素驱动需要另选真实模型与素材流程，不能只改契约标签。

连续变形参数写入 `presentation.local_composite.mouth_morph`：`method=aligned-lip-grid`，`closed/open` 各包含递增的 7 列 `x` 和 6 行 `rows`，坐标由当前角色局部素材逐一校准。外缘固定到嘴部 ROI，内部唇线不得交叉；`max_opening` 是 0 到 1 之间的正数，控制张口上限。不要复制其他角色的坐标。当前实现只支持这套网格。

嘴部的响应参数写入 `presentation.motion_parameters`，复用到生成轨迹的相应参数。先用小幅开合，检查半开嘴、最大开口和收口过渡；短时平滑过长会拖嘴。最终效果须在带声音的短样中检查，不能把音量驱动描述为音素口型。长期默认配置一起保存网格和运动参数，效果审批单独记录；用户否定旧效果后，不能因技术检查通过继续沿用旧效果。

原图背景不透明时可保留原背景并融入面板；需要透明角色时，在相应授权下抠图并复核发丝、肩线与鞋边。不要为这一步重做身份。讲解人身体不点头、不呼吸漂浮、不挥手；整层淡入淡出或短距离位移仅作进出合成，入场后稳定。独立指示点属于图解，不能说角色真的用手指了对象。

## 构图与注意力接力

每次出场写明第一焦点与退场后的接力对象。人物和图解不要同时强运动。嘴眼运动也不能代替信息变化，不能用“人物嘴一直动”通过语义运动检查。

- 同框时给当句对象足够宽度，先看清对象，再用局部高亮呈现变化。
- 两个比较对象同级、同时可读，放不下就移除人物，不把证据缩成角落。
- 转折保留上个对象或关系，人物返回引入新重点；退场后原对象留到解释结束。
- 竖屏遵守当前平台遮挡配置，脸、重点与字幕互不压盖。不固定全片同一站位；换侧要有观看理由。

段落中途出现或退出时，用实际音频确认触发词。未抽听或转写的词级时间只写 `cue_text`，精确时间为 null，不能均分或按字数猜秒数。完整段落可用已测定边界。旧口眼驱动的轨迹时间源必须是最终正式旁白，样段绑定整轨起止窗口；整片只生成一次轨迹，后续从同一轨迹截取，避免每镜重新归一或随机眨眼。

## 项目出场表与契约

从 `assets/presenter-plan-template.json` 建立 `presenter-plan.json`。逐段记录 `segment_id`、`visible`、触发词、退出词、讲解职责、理由、`focus_handoff`、`asset_id`、景别、位置、图层运动和复用原因。不出现的段落也写理由。它是计划，不是分镜批准或成片证明。

原图与实际镜头素材项必须使用 `role=character`、`character_id`、`asset_id`、`path`、`sha256`。`character_review` 或章节 `character_continuity_review` 的 `asset_id/asset_path` 必须对应实际渲染的人物项和已采用的身份锚点；渲染器不能另从未绑定路径取人物。旧 `audio-driven-presenter` 的局部素材记录在 `presentation.source_refs`，按嘴/眼分别绑定真实文件和 SHA；轻微角色动作按实际 head/hands 等区域绑定动作素材。

两种固定原图模式均写 `physical_action=false`、`explanatory_role` 与 `reuse_reason`；同段连续接力复用另写 `reuse_approved=true`。不填旧的 `action/action_signature/action_evidence` 来宣称身体动作。章节 `subject_interaction.required=false`；图解运动另记录。

- 用户选择 `static-presenter` 时，其 `body_motion=fixed`、`animated_regions=[]`、`mouth_driver=null`、`physical_action=false`、`lip_sync=false`、`mouth_audio_sync=false`；嘴、眼睛和身体完全静止。可用裁切、等比缩放和淡入淡出安排出场，入场后整个人物固定。小喇叭与声波另记为图解资产，不能写成人物动作。
- `audio-driven-presenter` 的 `body_motion=fixed`，`animated_regions=[mouth,eyes]`，`mouth_driver=amplitude` 或实际有效的 `phoneme`。音量模式的 `lip_sync=false`、`mouth_audio_sync=true`；音素模式须有真正模型与音素对应证据，才允许 `lip_sync=true`。
- 固定原图模式的身体代表动作和动作轮廓去重标记为不适用，保留 false 并写原因；身份、场景服装、解剖安全与讲解职责仍要复核。表演模式保持原有动作门。

旧 `audio-driven-presenter` 的 `presentation.motion_review` 绑定实际 `sample_path/sample_sha256`、正式 `audio_path/audio_sha256`、`character_asset_path/character_asset_sha256`、整轨 `audio_start_seconds/audio_end_seconds`、`mouth_driver`。复核后才填写 `reviewed`、`body_fixed_verified`、`mouth_audio_sync_verified`、`blink_verified` 和 `identity_preserved_verified`；音量模式 `lip_sync_verified=false`。FFprobe 证明媒体是真实有声音的视频、正式音频确有声轨、时长和截取窗口有效，不证明人物好看或用户已批准。

## 旧口眼模式的实际短样检查

先做 4—8 秒短样，包含可听见的讲话、自然停顿和至少一次眨眼。需要更多时间才能见到眨眼时选择合适整轨窗口，不人为把眨眼调成每秒一次。

检查实际编码结果：有声时嘴动、停顿时闭嘴，开合幅度明显且不夸张；闭眼干净、睁眼回到原图；身体和衣服不漂移，脸与原图一致；局部层无接缝、双唇重影或不完整眼睑；保留同一段实际旁白。AI/本地技术复核与用户审片分开。新效果直接展示给用户，不拿静态关键帧替动态试样，不拿人物测试片替整片微样片或完整预览。

出场安排复核：去掉人物会损失哪种讲述关系？是否挤占图解？每次返回有新讲解职责吗？关掉声音，图解是否仍显示当句因果或对比？这些问题不能用嘴动回答。

## 方法来源与整合边界

2026-10-14 核对 [ai-storyboard-director](https://github.com/62656456/ai-film-skills/tree/main/skills/ai-storyboard-director) 和 [shot-design-engine](https://github.com/62656456/ai-film-skills/blob/main/skills/ai-storyboard-director/references/shot-design-engine.md)，许可证 Apache-2.0。借鉴先决定观看意义，再决定人物调度、取景与接力的方法；本流程的固定原图、出场契约、局部嘴眼合成和音频活动轨迹由 Produce Videos 新增，未打包或运行完整上游 Skill。Buro director 保留所有权利，不纳入代码、文本或依赖。

核对官方 [LivePortrait](https://github.com/KlingAIResearch/LivePortrait) 的单图眼/嘴比例控制：可用于更复杂的局部变形，但官方管线不等于音频音素驱动，默认人脸检测权重还有单独许可限制。本次轻量实现无需下载该模型。更换实现前检查当时官方许可与实际效果，不为简单嘴动默认增加大模型。

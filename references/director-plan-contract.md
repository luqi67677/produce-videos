# 导演规划字段与唯一时间线

## 一个分镜，两种阶段

沿用 `shot-readiness.json` schema `2.6`。新项目采用 `director_plan` 扩展 `1.1`；已有 `1.0` 项目兼容，不要求为静态、无声项目补造素材。未知版本失败，不能借换版本绕过检查。

`director_plan` 保留 `stage`、`audience`、`viewer_outcome`、`throughline`、`script_binding: {path, sha256}`、`timing_basis`，增加 `effect_catalog`。原稿绑定必须是真实文件与 SHA-256。

- `planning`：`timing_basis=estimated`。允许先交完整分镜、暂缺外部视觉素材、正式旁白和 EDL；逐镜实际时间为空，`direction.estimated_duration_seconds` 只用于估时。**已选动效、音效和配乐必须已经可用**，不能写成“制作时再找/再开发”。缺动效改用现有简单呈现或静态，缺声音用 `none`。已有音色授权不代表已有本片口播音频。
- `ready`：`timing_basis=measured`。全部采用的视觉素材已落实到真实文件和权利证据，EDL 与正式旁白对齐，原有逐镜和合成门禁同时通过。不得填假文件、假审核或假批准。

仅写分镜不要求先通过声音执行或合成门禁。规划通过也不代表可合成。初始空模板供填写，不能当成通过示例。

## 逐镜 direction

原有 `shot_id`、`narration_segment_id`、`narration_excerpt`、`visual_duty` 继续使用。镜头原文按顺序重组须覆盖每段 `display_text`；只忽略空白，不忽略标点和大小写。

| 字段 | 导演或剪辑师必须说明的内容 |
|---|---|
| `audience_takeaway` | 本镜让观众理解的一件事 |
| `estimated_duration_seconds` | 正数，规划估时；不能冒充配音实测长度 |
| `visual_form` | 实景、产品录屏、照片、静态情境图、平面图解或已有可用的立体表达 |
| `composition` | 主体、支持元素、文字与安全区；先看哪里、再看哪里 |
| `camera` | 景别、起止构图；固定理由，或已登记运镜实例的作用。文字不能代替实现引用 |
| `continuity_anchor` | 跨镜保持的对象、方向或问题 |
| `states` | `before/action/after`。静态镜写清阅读停留；真实视频可描述素材内动作；不能在此偷写无实现的动画 |
| `transition_reason` | **本镜怎样接下一镜**、为何在此切、下一镜接住什么；末镜写结束停留。首镜的建立方式写在构图中 |
| `assets_needed` | 视觉素材的具体需求；已采用的音效/环境声/配乐引用。静态程序绘图且无外部素材可为空，在构图中说明 |
| `effects` | 本镜采用的已有动效实例；没有就填 `[]` |
| `background` | 固定或动态、作用、强度与跨镜延续；不能省略背景决定 |
| `events` | 已有动效或真实素材动作的语义事件；只做稳定播放或静态阅读可为 `[]` |
| `subtitle_plan` | 原文如何分组、位置、强调和阅读停留；实际时间取最终旁白 |
| `music` | 结构化的无配乐或已有本地配乐方案 |
| `music_plan` | 保留旧版阅读说明；须与 `music` 一致，不能用自由文字绕过本地素材约束 |

剪辑师使用上述衔接、字幕与声音决定，回填同一份 EDL；不另建一套剪辑时间表。风格、画幅和音色继续引用已有项目契约，不在导演扩展中复制第二套全局偏好。

## 先盘点已有实现，再选动效

用户授权准备新开源库时，可以先独立下载、接入并核验，再将已可用实现加入目录。未完成准备的效果不进入分镜，不能用一个来源 URL 代替本地可用证明。

`director_plan.effect_catalog` 是本项目采用实现的目录。目录为空合法；每个被采用条目必须包含：

- `effect_id`、`library`、`version`、`source_url`、`license`：实现的稳定编号、库名、版本、来源和许可。采用已有开源实现时记录其真实来源与适用许可，不能只填效果名称。schema 兼容已有本地自有实现（来源网址可空），不等于授权本轮新写特效。
- `implementation: {path, sha256, entrypoint}`：本地已有实现文件、实际哈希和入口；说明入口接受的参数。网页链接、文档示意、包名和 TODO 都不是可执行实现。
- `availability: {status: "verified", evidence_path, evidence_sha256}`：只在已有证据确实符合下面条件时写 verified。不得先抄模板值再补证据。

可用证据为真实 JSON 文件，包含同一 `effect_id`、`implementation_sha256`、`status: "passed"`、非空 `details`，以及：

- `verification_method: "execution-test"`：`artifact: {path, sha256}` 指向非空已有执行日志，同时有实际 `command`。
- `verification_method: "existing-render"`：`artifact: {path, sha256}` 指向可识别的已有渲染产物。

证据中的实现哈希必须与目录一致。不能把自填的“测试通过”当执行记录；不能为填证据运行来历不明的代码。仅有源码但无可用证据时，本镜选静态或另一项已验证实现，不承诺稍后开发。这里只检查采用的实现；未采用资源不要求全部登记或核验。

`direction.effects` 每项包含：

`instance_id`、`effect_id`、`target`（background / camera / foreground / transition）、`purpose`、`parameters` 对象、`start_trigger`、`stop_trigger`。

`effect_id` 引用全片目录，`instance_id` 标识本镜使用。参数必须属于该真实入口；导出器不会为不支持的参数补实现。导演描述写“谁在何时发生什么”，实现编号留作追溯。

## 背景与配乐每镜都要决定

`direction.background` 包含 `mode`、`description`、`reason`、`effect_instance_ids`、`intensity`、`continuity`。

- `mode=static`：`effect_instance_ids=[]`，`intensity=none`。写底色或背景素材是什么、固定的理由、是否延续上一镜。
- `mode=animated`：引用本镜 `target=background` 的实例；`intensity` 为 subtle 或 moderate。写对理解有什么作用；不能只写“增加氛围”。没有已验证实现时必须回到 static。

`direction.music`：

- `mode=none`：写 `reason`，例如专注口播、已有文件不合适、未提供配乐。无需声音资产，不能写待搜索曲目。
- `mode=track`：另写 `request_id`、`start_trigger`、`stop_trigger`、`gain_db`、`fade_in_ms`、`fade_out_ms`、`ducking` 说明，以及 `continuity: {from_previous, to_next}`。需求须选中恰好一个本地已存在的音频资产，核查文件、哈希与权利；写清如何避让旁白。

背景、配乐与事件音效各自决定。背景固定不等于无效画面；无配乐不等于无旁白；有动作音效库不等于已有雨声或配乐。

## 素材需求与权利证据

每项 `assets_needed` 写 `request_id`、`role`、`description`、`preferred_source`、`search_queries` 数组、`acceptance_criteria` 数组、`fallback`、`selected_asset_ids` 数组。

外部视觉素材允许在规划时待搜：例如“雨中屋檐滴水，固定近景，无人物与标识，连续可用 4 秒”；写搜索词、接受条件、找不到的静态替代，selected IDs 可空。不得将想找的镜头描述为已看过的画面。

音效、环境声与配乐不同：选用时，`selected_asset_ids` 必须恰好引用一个 `source-assets.json` 中已存在本地音频；`search_queries=[]`，不写待下载/待生成声音。没有合适文件，删除声音需求并把对应 `sound/music.mode` 改成 none。音频路由和正式旁白仍遵守 `audio-system.md`；参考声音不能充作本片成品口播。

素材只引用 `source-assets.json` 的 asset_id，不复制路径与授权形成第二张素材表。`source_type` 可为 user-provided、official、licensed、existing-project、generated、self-created；来源类别不等于已取得使用权。

每份采用素材除文件哈希与隐私检查外，记录：

- `rights.status=reviewed`；`basis` 为 user-authorization / licensed / generated / self-created。
- `license_name`、`source_url`、`license_url`：licensed 必须有许可名和 HTTPS 来源/许可页；其他来源仍核查实际使用条件。
- `evidence_path`、`evidence_sha256`：许可快照、用户授权、生成记录或自制说明的真实文件与哈希。可引用获准读取的项目外私有证据；校验器不自行扫描私人目录，私有内容不进入公开 Skill 包。
- `allowed_use`、`restrictions_review`：说明本片用途及人物、标识、编辑、再分发等限制。
- `attribution: {required, text, placement}`：需署名时，写署谁、文本与成片或发布说明位置。

这是准备与追溯检查，不替代实际权利判断。

## 事件、声音与 EDL

每个事件写 `event_id`、`cue_text`、`before`、`action`、`after`、`depends_on`。cue 是本镜原文中的准确词句；重复词须在制作时确定对应一次。依赖只引用本镜前序事件，避免循环或提前显示完成。1.1 区分两种事件：

- `kind=effect`（默认）：用非空 `effect_instance_ids` 引用本镜已登记的程序动效实例。
- `kind=source-action`：真实素材原生动作，写 `source_request_id` 引用本镜视觉需求，`effect_instance_ids=[]`。planning 可待视觉素材；ready 必须选中恰好一个真实视频及实际动作片段证据。不能把后加运镜、飞入或转场伪装成素材原生动作。

`sound` 至少包含 `mode`（none / sfx / ambience）与 `reason`。有声时写 `request_id`、`start_trigger`、`stop_trigger`；请求只引用本地已有音频。说明尾音、叠加与旁白避让。可选 `continuity: {from_previous, to_next}`，省略为不跨镜；连续时相邻两镜须互相声明、使用相同 mode 与同一已选资产，不能由导出器猜测延长。静态镜不必造一个空事件以挂声音；真实素材动作需要音效时可用 source-action 对齐，已有配乐按 music 记录。

EDL 继续使用 `1.1`，实际帧都写在原 `picture_track` 对应 clip 中：

- `semantic_events`：每项 `event_id/start_frame/end_frame`；1.1 有声音时 `sound` 内写 `asset_id/source_start_frame/start_frame/end_frame/gain_db/fade_in_ms/fade_out_ms`。素材偏移按 EDL fps，须在实际音频长度内；1.0 保持旧字段兼容。
- `source-action` 对应的 `semantic_events[].source_action`：写 `asset_id/source_start_frame/source_end_frame/evidence_path/evidence_sha256`。源帧按 EDL fps，不能超出视频实际长度；证据 JSON 写同一 `event_id`、`asset_sha256`、`status=reviewed`、`reviewer`、`details`，说明哪段实际动作已经看过。校验文件与证据绑定不能自动证明动作含义。
- `effect_cues`：每项 `instance_id/start_frame/end_frame`，与本镜实例一一对应。
- `music_cue`：有配乐时写 `asset_id/start_frame/end_frame/source_start_frame/gain_db/fade_in_ms/fade_out_ms`；无配乐不写 cue。

帧相对本镜，end 是结束边界，不得越过镜头。事件音效不能早于该事件；自然尾音可超过动作完成点但仍在本镜内。跨镜音效/环境声在相邻镜的同类事件内分别记录，素材偏移连续、不重复起播，内部边界淡入淡出为 0。跨镜音乐用相邻片段记录：同一素材、末首相接、source 偏移连续，内部交接不重复淡入淡出；首尾淡化按实际段落执行。

全局时间 = EDL 镜头起点 + 相对帧 / fps。导演分镜只写估时和语义触发，不维护第二张全局时间表。已对齐事件的切点不参与节拍吸附；改变旁白后重对齐受影响事件、字幕和镜头，并使旧审批失效。

## 工具与能力边界

```bash
python3 scripts/validate_director_plan.py project
python3 scripts/export_director_board.py project --output project/director-board.md
python3 scripts/validate_director_plan.py project --require-ready
```

校验器检查原文、依赖、采用资源与时间边界；导出器只把同一合同变成可读分镜。项目渲染器才负责执行已有实现、画图与混音。字段通过不能证明效果好看、混音已执行或许可判断正确，最终检查真实编码产物。

可读分镜先显示估时/实测总长、镜头数与视觉素材缺口，再逐镜显示导演画面、背景、动效、衔接、字幕和声音。编号、路径、哈希等技术信息保留追溯，避免先把它们压给审片用户。更新 JSON 后重导；沿用现有审批账本，不新建批准状态。

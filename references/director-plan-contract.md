# 导演规划字段与唯一时间线

## 一个分镜，两种阶段

沿用 `shot-readiness.json` schema `2.6`，新增 `director_plan` 扩展版本 `1.0`。新项目使用此扩展；旧项目不强制补写。未知版本失败，不能借换版本绕过检查。

```json
{
  "schema_version": "1.0",
  "stage": "planning",
  "audience": "第一次了解这项技术的人",
  "viewer_outcome": "能说明谁负责、资料交给谁、结果由谁采用",
  "throughline": "跟随一份任务单完成交接",
  "script_binding": {"path": "master-script.json", "sha256": "实际原稿文件哈希"},
  "timing_basis": "estimated"
}
```

`planning` 允许没有图片、音频和 EDL。逐镜的实际开始/结束时间保持空值，`direction.estimated_duration_seconds` 给规划估时。它不能进入合成。

`ready` 要求 `timing_basis=measured`；全部素材需求落实到真实文件和许可证据，EDL 与正式旁白已对齐，原有逐镜和合成门禁同时通过。不要为通过校验填假文件或将空需求列表当成没有缺口。

## 逐镜 direction

原有 `shot_id`、`narration_segment_id`、`narration_excerpt`、`visual_duty` 继续使用；原文按镜头顺序重组必须覆盖每段 `display_text`，只忽略空白，不忽略标点和大小写。

| 字段 | 内容 |
|---|---|
| `audience_takeaway` | 本镜观众应理解的一件事 |
| `estimated_duration_seconds` | 正数，规划估时；不替代 EDL 实测时间 |
| `visual_form` | 实景视频、真实产品录屏、照片、静态情境图、平面图解、2.5D 结构等具体选择 |
| `composition` | 主体、支持元素、文字区域、先后关注点；注明实际平台安全区 |
| `camera` | 景别、起止构图和运动方式，或保持静止的理由 |
| `continuity_anchor` | 与前后镜头相接的对象、方向或问题 |
| `states` | `before`、`action`、`after`，明确可见变化或阅读停留 |
| `transition_reason` | 为什么此处切换，接住什么；不只写“转场自然” |
| `assets_needed` | 各画面/声音元素需求；程序直接绘制且无外部素材可为空，并在构图中说明 |
| `events` | 口播触发的语义事件；纯稳定实景可为空，动作在 states 中解释 |
| `subtitle_plan` | 原稿如何分组、位置、关键词强调；实际时间取最终旁白 |
| `music_plan` | 无音乐，或音乐职责、段落与避让旁白方式 |

每项素材需求写 `request_id`、`role`、`description`、`preferred_source`、`search_queries` 数组、`acceptance_criteria` 数组、`fallback` 与 `selected_asset_ids` 数组。例如寻找“雨中屋檐滴水，固定近景，无人物与标识，连续可用 4 秒”，比“找下雨素材”可执行。搜索词可为中文与英文；导出给用户时配中文说明。

规划时 selected IDs 可空；落实后仅引用 `source-assets.json` 的 asset_id，不复制授权信息或文件路径成第二套素材表。该表 source_type 包括 user-provided、official、licensed、existing-project、generated、self-created；来源类别本身不代表已取得权利。

## 素材 rights

每份采用的素材，除原有文件哈希与隐私检查外，写入：

- `status: reviewed`；`basis` 为 user-authorization / licensed / generated / self-created。
- `license_name`、`source_url`、`license_url`：licensed 必须有许可名和 HTTPS 来源/许可页。其余可以不需要网页，仍需核查对应生成工具或自有材料的使用条件。
- `evidence_path`、`evidence_sha256`：许可快照、用户授权记录、生成记录或自制说明的真实文件与哈希。优先随项目保存；也可明确引用获准读取的项目外私有文件。校验器只核对这些明确引用的文件，不搜索私人目录；私有证据不进入公开 Skill 包。
- `allowed_use`、`restrictions_review`：本片实际使用方式，人物、标识、编辑用途、再分发等检查结果；写具体结论。
- `attribution: {required, text, placement}`：必须署名时说明署谁、文本与成片或发布说明中的位置，实际交付也核对。

这是追溯与准备检查，不是法律意见或零风险认证。自制和生成也不能自动消除第三方内容或人物权利问题。

## 事件与音效

每个导演事件记录 `event_id`、`cue_text`、`action`、`before`、`after`、`depends_on`。cue 是该镜原文中的准确词句；同镜重复词要在制作时明确选哪一次。依赖只引用本镜已声明的前序事件，避免出现循环或先更新完成态再行动。

`sound` 至少包括：

- `mode`：none / sfx / ambience；无声也写 `reason`。
- 有声时写 `request_id` 引用本镜的声音素材需求，以及 `start_trigger`、`stop_trigger`。
- 尾音、是否允许叠加及与旁白的避让写进声音理由或停止条件。跨镜环境声在各镜声明其延续范围；不要让导出器猜测无限延长。

EDL 继续为 `1.1`，在对应 picture_track clip 中写 `semantic_events`：

```json
{"event_id":"c01-s01-e01","start_frame":20,"end_frame":44,
 "sound":{"start_frame":30,"end_frame":49,"gain_db":-18,"fade_in_ms":10,"fade_out_ms":80}}
```

帧相对本镜，end 为结束边界；事件/音效不得越过本镜。动作音效可以从动作发生或结果落下时开始，但不能早于该事件；尾音可超过动作完成点，仍须在本镜时段内。背景连续声不绑定一次落点，用 ambience 事件明确完整时段。

全局时间 = EDL 镜头起点 + 相对帧 / fps。不要再手工维护全局事件表。EDL 事件与导演事件逐一对应，依赖事件先结束再推进下一步。已对齐事件的相邻切点不参与节拍吸附；改配音后重新对齐相关事件、字幕和镜头并使旧审批失效。

## 工具与能力边界

```bash
python3 scripts/validate_director_plan.py project
python3 scripts/export_director_board.py project --output project/director-board.md
python3 scripts/validate_director_plan.py project --require-ready
```

校验器检查原文覆盖、结构、依赖、材料证据和时间边界；导出器只把同一合同变成可读分镜，不生成画面或声音。项目渲染器按 EDL 和事件绘图、触发音效；必须验证实际编码结果，字段正确不能证明动作、许可判断或听感正确。

导演分镜导出属于审阅视图；更新 JSON 后重导。使用现有审批账本，不新增独立的批准状态文件。最终 `assets`、`storyboard` 仍绑定真实制作产物与哈希。

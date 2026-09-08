# Produce Videos V2.5.0

V2.5.0 把视频制作的验收单位从“章节大致正确”推进到“每个真实剪辑镜头都可验证”。这次发布集中修复五类会让预览看似完成、实际仍需多轮返工的问题。

## 逐镜声画同步

- `shot-readiness.json` V2.6 逐一登记剪辑镜头，不再只审章节。
- `edit-decision-list.json` V1.1 保存相同的口播片段和语义切点。
- `validate_timeline_sync.py` 阻止上一句旁白跨进下一画幅、时间空洞和切点漂移。
- 未知 schema 不再被当成兼容版本静默放行。

## 动画与画面占用平衡

- `motion-plan.json` V1.3 默认要求首帧已有稳定骨架或主视觉，同时兼容已有 V1.1/V1.2 项目。
- `analyze_motion_coverage.py` 同时检查静态持有、分段揭示、等待元素入场的空白和运动计划漂移。
- `motion-coverage.json` V1.4 把这些结果纳入正式导出门禁。

## 文案、证据与排版边界

- 制作动作、构图意图、隐私处理说明与通用素材标签只保存在 `production_notes`，不得渲染为观众文案。
- 数量、流程、安装和结果主张必须使用完整可辨的真实预览或已验证结果，空框与文字口号不能通过。
- 逐镜复核标题孤行、品牌大小写、溢出、对齐和画面密度。

## 人物不再机械复用

- 人物档案新增场景造型和动作语言。
- 每个含人物镜头登记 `action_signature`，重复姿势必须有经审查的叙事理由。
- 身份一致与场景动作分开检查：角色可以是同一个人，但讲解、操作、递交和片尾不应是同一姿势。

## 独立封面契约

- 新增 `cover-contract.json` 与 `validate_cover_contract.py`。
- 主标题、副标题、Skill 名称各有职责。
- 主视觉动作、服装语境、主题绑定、原尺寸和信息流缩略图必须一起通过。

## 升级说明

旧项目继续兼容原 schema；新项目应从以下模板创建：

- `assets/shot-readiness-template.json`
- `assets/edit-decision-list-template.json`
- `assets/motion-plan-template.json`
- `assets/motion-coverage-template.json`
- `assets/character-profile-template.json`
- `assets/cover-contract-template.json`

V2.6 逐镜表的要求比旧版严格。升级旧项目时，先补齐真实剪辑镜头、审查帧、口播片段和语义切点，再重新运行 sample/full render gate。

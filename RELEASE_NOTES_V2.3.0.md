# Produce Videos V2.3.0

这一版把“能生成视频”继续收紧为“能交付干净、可复核、可继续编辑的视频”。

## 新增

- 34 套视觉主题 + 88 套结构化布局；主题负责视觉语言，布局负责镜头构图。
- A-roll、B-roll、hybrid、graphic-led 镜头职责，以及逐镜 `covers` 和桥接契约。
- 视觉干净度硬门：单一焦点、构图预算、三次停帧检查、无职责空白和脏元素拦截。
- 本地优先词级 STT、EDL 单一剪辑时间、BGM 节拍网格与安全切点吸附。
- FCPXML 1.10 时间线导出；Remotion 项目要求保留可复现源码。
- 只读环境 doctor 与从既有审批账本推导的断点续作入口。
- 三个授权公开案例、GitHub Actions 和正式下载包。

## 下载

- `produce-videos.skill`：通用 Agent Skill 安装包。
- `produce-videos.zip`：通用 ZIP。
- `produce-videos-workbuddy.zip`：WorkBuddy 上传包。
- `SHA256SUMS.txt`：安装包完整性校验。

安装 Skill 本身不会下载 TTS/STT 模型，也不会调用付费服务。需要补充 Qwen3-TTS 或其他依赖时，Agent 必须先说明目标、大小、安装位置和成功标准，再取得用户授权。

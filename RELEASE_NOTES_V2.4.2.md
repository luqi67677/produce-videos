# Produce Videos V2.4.2

这次更新重做了第一次安装体验：用户只需把一句中文安装口令发给当前正在使用的本地 AI Agent，不需要理解终端、目录或平台参数。

## 更新内容

- README 提供统一安装口令，可直接发送给 Codex、Claude Code、Cursor 或 Kimi Code CLI。
- Agent 自动识别自身平台，只执行对应的一条非交互安装命令，不再让用户选择安装目标。
- 安装后必须读回 `SKILL.md`、报告实际路径并运行验证，不能把“看过仓库”当成“安装完成”。
- 当前 Agent 无法运行 `npx` 时，由 Agent 自己使用 Release 包或 Git 克隆兜底。
- 普通网页聊天没有本地文件和命令权限时会明确说明限制；WorkBuddy 继续使用专用 ZIP 上传。

## 用户安装口令

```text
请把这个视频 Skill 安装到你当前使用的 AI，并验证安装成功：https://github.com/luqi67677/produce-videos
```

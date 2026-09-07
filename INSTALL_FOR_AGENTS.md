# 给 AI Agent 的安装说明

目标：安装完整 `produce-videos` 目录并实际验证，不只读取 README，也不覆盖用户已经修改过的同名 Skill。

## 用户只需要发送这一行

```text
请把这个视频 Skill 安装到你当前使用的 AI，并验证安装成功：https://github.com/luqi67677/produce-videos
```

收到这条口令后，由当前 Agent 完成平台判断、安装和验证。不要让用户打开终端，不要再问用户“安装到哪个平台”，也不要把内部命令原样退回给用户执行。

## Agent 自动安装

1. 先根据当前运行环境判断自己是 Codex、Claude Code、Cursor 还是 Kimi Code CLI；不得根据电脑上同时存在的其他 Agent 目录，让用户再次选择平台。
2. 检查目标目录是否已有同名 Skill。不存在时继续；存在时先确认它是未修改的旧版还是用户自己的修改版，不得静默覆盖。
3. 选择并自行执行唯一对应的非交互命令：

   ```bash
   # Codex
   npx skills add luqi67677/produce-videos -g -a codex -y

   # Claude Code
   npx skills add luqi67677/produce-videos -g -a claude-code -y

   # Cursor
   npx skills add luqi67677/produce-videos -g -a cursor -y

   # Kimi Code CLI
   npx skills add luqi67677/produce-videos -g -a kimi-code-cli -y
   ```

   只执行与当前 Agent 对应的一条，不安装到所有 Agent。`-g` 锁定用户级目录，`-a` 锁定当前平台，`-y` 跳过平台和范围选择。
4. 若当前环境没有 Node.js 18 或无法运行 `npx`，但 Agent 仍有本地文件和网络能力，由 Agent 自己从 [最新 Release](https://github.com/luqi67677/produce-videos/releases/latest) 下载通用包，或克隆完整仓库到当前平台目录。不要先要求用户研究终端和目录。
5. WorkBuddy 使用专用上传包：
   - 通用 Agent：`produce-videos.skill` 或 `produce-videos.zip`；
   - WorkBuddy：`produce-videos-workbuddy.zip`。
6. Release 同时提供 `SHA256SUMS.txt` 时，下载后先核对安装包哈希；校验失败不得继续安装。
7. 无法读取本地文件、执行命令或写入 Skill 目录时，明确说明当前平台不能安装，不要假装安装成功。

常见位置：

- Codex：`~/.codex/skills/produce-videos`
- Kimi Code CLI / 通用 Agents：`~/.agents/skills/produce-videos`、`~/.config/agents/skills/produce-videos` 或项目 `.agents/skills/produce-videos`
- Claude Code：`~/.claude/skills/produce-videos`
- Cursor：`~/.cursor/skills/produce-videos`
- WorkBuddy：上传专用 ZIP

## 安装验证

在安装目录运行：

```bash
python3 scripts/doctor.py --skip-model-scan
python3 -m unittest discover -s tests -v
python3 scripts/validate_theme_catalog.py references/frontend-slides-themes/bold-template-pack/selection-index.json
python3 scripts/validate_layout_catalog.py
python3 scripts/scan_release.py
```

然后读回并报告：

- `SKILL.md` 是否存在；
- `scripts`、`references`、`assets` 是否完整，并且包含声音发现、断点续作、平台遮挡、人物一致性和质量门禁所需文件；
- 34 套主题、88 套布局和测试是否通过；
- 开源边界扫描是否通过；
- 实际安装位置；
- 当前能做完整成片、只能做部分阶段，还是缺少 FFmpeg/渲染环境。

安装本 Skill 不等于授权安装依赖、下载 TTS/STT 模型、调用 API 或上传用户素材。需要时在具体视频任务中单独说明成本、目录和成功标准，再取得授权。

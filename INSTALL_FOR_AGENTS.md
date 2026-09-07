# 给 AI Agent 的安装说明

目标：安装完整 `produce-videos` 目录并实际验证，不只读取 README，也不覆盖用户已经修改过的同名 Skill。

## 优先方式

1. 判断当前产品是否能读取本地文件、运行 Python/FFmpeg 并输出媒体文件。普通网页聊天若不具备这些能力，只说明限制，不假装安装成功。
2. 对 Vercel Labs Skills CLI 已支持的本地 Agent，优先运行：

   ```bash
   npx skills add luqi67677/produce-videos -g
   ```

   按提示选择目标 Agent。安装器必须识别出唯一的 `produce-videos`，并安装完整目录；若目标机器没有 Node.js 18 或更高版本，再走下面的 Release 或手动安装路线。
3. WorkBuddy 或无法运行 `npx` 的环境，从 [最新 Release](https://github.com/luqi67677/produce-videos/releases/latest) 下载：
   - 通用 Agent：`produce-videos.skill` 或 `produce-videos.zip`；
   - WorkBuddy：`produce-videos-workbuddy.zip`。
4. Release 同时提供 `SHA256SUMS.txt` 时，下载后先核对安装包哈希；校验失败不得继续安装。
5. 没有 Skills CLI 和 Release 下载能力时，克隆完整仓库。
6. 手动安装时把完整目录放到平台 Skills 目录；不能只复制 `SKILL.md`。

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

# 转写、节拍与可编辑时间线

## 词级转写

已有音视频需要剪口播时，先运行 `scripts/transcribe_media.py`，得到统一的词级时间戳 JSON。优先使用用户电脑中已经安装且已经准备好模型的 `mlx-whisper`、`faster-whisper` 或 `openai-whisper`；脚本不会自动安装依赖，也不会在没有 `--allow-model-download` 时下载模型。

转写是剪辑视图，不是最终文稿。删除、换序或压缩口播后仍需用户确认主叙事，再生成 EDL。切点不得落在词中；发生音频拼接时，默认在边界使用约 30ms 的短淡入淡出避免爆音，不能把它扩成可感知的转场。

## EDL 是剪辑单一真相源

`edit-decision-list.json` 保存声音主轴、画面轨、A/B-roll 类型、素材入点、时间线位置、时长、转场和 `covers`。渲染、节拍吸附和 NLE 导出都读取同一个 EDL，禁止各自维护另一套时间。

模板：`assets/edit-decision-list-template.json`。

## 节拍驱动剪辑

有 BGM 时运行 `scripts/build_beat_grid.py`：

- 已知 BPM 时使用 `--bpm` 和可选 `--offset-seconds` 生成确定节拍；
- 不知道 BPM 时从本地音频能量变化检测候选节拍，并明确标为估算；
- `scripts/snap_edl_to_beats.py` 只在允许的最大位移内调整未锁定切点；
- 有词级转写时，候选切点落在词中会被拒绝；
- 口播语义、动作完成和结果证据优先于卡点，不能为了节拍切断一句话或一个操作。

## 可继续编辑的交付

`scripts/export_fcpxml.py` 从同一 EDL 生成 FCPXML 1.10 时间线，可导入支持 FCPXML 的非线性剪辑软件继续调整。导出保留镜头顺序、源素材入点、时长、A/B-roll 角色和场景标记。代码动画、复杂合成和烧录字幕无法还原为原生特效时，应作为独立 plate 素材进入时间线，并在交付说明中标出扁平化边界。

如果项目本身使用 Remotion 渲染，正式交付还应保留完整源码、锁文件、素材清单和渲染命令；不能只交付 MP4。

## 参考

- [video-use](https://github.com/browser-use/video-use) 的词级转写、EDL 单一真相源、逐切点检查和字幕最后合成方法。
- [video-shotcraft](https://github.com/Vincentwei1021/video-shotcraft) 的节拍卡点和可编辑剪映/FCPXML 交付思路。
- [remotion-ad-video-skill](https://github.com/Alon17-12/remotion-ad-video-skill) 的 BPM 检测与场景量化方法。

# 本机长期默认声音

用户明确要求记住声音后，把模型、参考音频和配置保存在 Skill 外。配置是唯一长期来源；项目保存实际读取的配置哈希与参考副本，不能反向改写默认。

## 开工自动读取

```bash
python3 scripts/load_local_voice_default.py --output project/local-voice-default.json
```

默认配置位置为 `~/Desktop/配音模型/默认配音配置.json`。`--config` 优先于环境变量 `PRODUCE_VIDEOS_VOICE_CONFIG`，环境变量优先于默认位置。只读取这一份文件和它明确指向的文件，不做全盘发现，不联网、不下载。

- `ready`：用户已批准跨项目复用，参考音频 SHA-256 匹配，模型权重完整且运行入口存在。沿用模型和参考音色，不再向用户问声音，不重新生成试听。
- `not-configured`：没有私有默认且用户未指定配置，继续通用声音流程。
- 校验失败：指出具体缺失或损坏的文件，保留声音选择。不得静默换模型、换参考、改用 VoiceDesign 或云端服务。
- 用户当次明确要求换声音、使用自己录好的旁白或无旁白时，当次要求优先。只有另获“以后也用这个”的授权才更新长期默认。

## 每个新项目保留的记录

从配置记录 `voice_profile`、批准原话、配置路径与哈希、参考音频哈希、模型 ID/目录/版本、兼容 Python 和全部生成参数。建立 `voice-brief.json` 与 `voice-selection.json`，使用原始长期授权，记录复用关系；当前项目的模型预检仍须实际通过。参考音频与最终整条旁白是两个文件。

这属于已选参考音色的 `user-reference` 路线。保持参考配置中的 `generator` 参数；传给 `generate_qwen_voice.py --reference-config` 时，参数优先级为用户当次明确指定的命令参数、参考配置、通用默认。Agent 不能因内容主题擅自改参数。不要用描述式声线设计替代 Base 参考音色。

## 配置字段

配置需包含 `approved: true`、`locked_by_user: true`、`applies_to: future-produce-videos`、声音使用与长期保留的授权原话、`voice_profile`、`reference_audio`、`reference_audio_sha256`、`reference_text`、`runtime_python`、`model` 和 `generator`。音频和模型目录可以相对配置文件。`model.integrity` 记录权重大小与已核验 SHA-256；开工检查大小与小文件，迁移或发现漂移时增加 `--verify-model-sha256` 做完整权重校验，随后再实际加载预检。

私人音频、配置和绝对路径不复制到公开 Skill 包、GitHub 或交付下载包。长期默认只读取这份私有文件，不在项目之间保存互相冲突的默认声线。

# 声音系统

## 音频来源先确认

先复用 `video-brief.md` 中用户已经说明的音频路线；只有缺失时才直接询问属于哪一种情况。不扫描、不下载、不调用任何服务。草稿阶段使用 `pending-user-choice`，正式契约不得保留这个值：

1. 用户已经录好的完整口播：`external`，不调用 TTS，直接校验成品音频。
2. 用户已有可调用的 TTS API：`other-tts`，先验证 API，再试听选声；只使用用户提供的服务，不擅自替换。
3. 用户电脑上已有本地 TTS 模型：先做有限范围发现和预检；兼容 Qwen 时使用 `open-source-model`。
4. 以上都没有：向用户说明阿里 Qwen3-TTS 的地址、大小、目标目录和依赖，获得明确授权后才下载。

用户希望使用自己的参考音色时另走 `user-reference`：必须提供参考音频、逐字文本和授权说明，并把参考音频与最终旁白分开记录。

Skill 不携带任何预设声音、试听音频或默认音色。没有成品口播、可用 TTS API 或已准备好的 Qwen 模型时，不能继续生成旁白，也不能静默调用未说明的云端服务。

## 用户已有 TTS API

- 只通过环境变量或系统安全存储读取凭证；不得要求用户把 API Key 粘进公开文件，不得把密钥写入项目、日志、试听清单或 Skill 包。
- 先执行一次最小测试请求，并确认该服务能列出声音或生成短试听。把不含密钥的证据写入 `tts-api-preflight.json`，格式见 `assets/tts-api-preflight-template.json`。
- API 预检必须记录供应方、模型标识、HTTPS 服务地址、凭证存储方式、测试结果和检查时间，并明确 `secret_values_persisted: false`。
- 预检通过后，先询问并确认用户想要的声音，形成 `voice-brief.json`；再用同一段 5—12 秒文案生成 3 个围绕该方向的试听。用户明确选定一个后写入 `voice-selection.json`，声音需求单、API 预检文件及其 SHA-256 都必须与选择记录绑定。
- 只有用户明确要求跳过试听，才允许 `direct-description`，并记录 `direct_description_authorized: true`。否则声音选择校验必须阻断。

## 用户选择本地模型后再发现

运行：

```bash
python3 scripts/discover_audio_models.py \
  --output <项目目录>/model-discovery.json
```

模型默认只检查 Hugging Face 标准缓存和用户目录下常见的 `Models/models` 文件夹，不遍历整块磁盘、不跟随符号链接。运行环境只有限检查当前 Python、活动虚拟环境、PATH、常见虚拟环境目录和模型目录同级环境。用户知道其他模型目录时，用可重复的 `--search-root` 追加；知道旧项目使用的 Python 或虚拟环境入口时，用可重复的 `--runtime-python` 追加。

- 找到唯一兼容的 Qwen3-TTS MLX 模型：记录候选名称、目录和 `runtime_candidates`，直接推荐并使用 `recommended_runtime_python` 运行最小预检；只有存在多个能力、大小或运行成本差异明显的候选时才让用户选择。不能只凭目录名或默认 Python 的结果放行。
- 只找到其他开源 TTS：说明已发现候选，但当前内置执行器不能证明兼容；让用户提供已验证调用方式、改走 `other-tts`，或选择准备 Qwen。
- 没找到完整模型：展示下方 Qwen 地址、大小、目标目录和授权问题；未获授权不安装、不下载。

默认 `python3` 无法导入 `mlx_audio`，只说明当前解释器不兼容，不等于电脑没有运行环境。必须先读取发现报告、检查用户已知的旧项目运行入口，并用候选环境重跑预检；只有这些入口都失败时，才展示依赖名、安装命令和影响，取得用户明确授权后安装，再重新预检。模型存在、运行时确实缺失仍属于不可生成状态。

`model-discovery.json` 属于当前项目，不写回 Skill，也不进入公开发布包。

## Qwen3-TTS 模型地址

当前 `scripts/generate_qwen_voice.py` 只实现 Apple Silicon 的 `mlx-audio` 运行时，优先下载这个 MLX 模型：

- 模型地址：<https://huggingface.co/mlx-community/Qwen3-TTS-12Hz-1.7B-VoiceDesign-bf16>
- 模型 ID：`mlx-community/Qwen3-TTS-12Hz-1.7B-VoiceDesign-bf16`
- 下载命令：

  ```bash
  <兼容的 Python 3.10+> -m pip install -U "mlx-audio[tts]" "huggingface_hub[hf_xet]"
  huggingface-cli download mlx-community/Qwen3-TTS-12Hz-1.7B-VoiceDesign-bf16 \
    --local-dir <模型目录>
  ```

本机内存紧张时可使用较小的量化版本：<https://huggingface.co/mlx-community/Qwen3-TTS-12Hz-1.7B-VoiceDesign-5bit>。阿里 Qwen 官方原始模型页是：<https://huggingface.co/Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign>；当前 `mlx_audio` 脚本必须使用 `mlx-community` 转换版，不能把原始 Transformers 模型目录直接交给 MLX 执行器。

运行时分流：

- Apple Silicon / `arm64`：使用 MLX 转换版和 `mlx-audio`。
- 非 Apple Silicon：当前脚本不承诺可用；只有用户明确提供兼容的其他 TTS，才走 `other-tts`。
- 不得因为网络或设备不匹配，静默切换到云端 TTS、内置音色或另一套模型。

以上地址、模型 ID、下载命令和预计下载量以 `assets/qwen-tts-models.json` 为单一配置来源。模型和依赖不得下载到 Skill 包内，应放在用户指定的模型目录或运行时缓存中。

## 模型缺失时必须停住

只有发现报告列出的候选或用户明确提供的目录，才进入 `scripts/model_preflight.py --model-path <模型目录> --runtime mlx-audio --runtime-python <兼容 Python> --smoke-test`，检查实际 Python、`mlx_audio`、模型目录、权重文件、Tokenizer、目标设备和最小模型加载；预检通过后才允许进入选声。模型缺失时必须把下面的信息给用户：

> 当前没有找到 Qwen3-TTS 开源模型。模型地址：`https://huggingface.co/mlx-community/Qwen3-TTS-12Hz-1.7B-VoiceDesign-bf16`，推荐版约 4.52 GB；较小量化版约 2.5 GB。是否允许我安装 `mlx-audio` 并下载到你指定的模型目录？

只有用户明确同意后，才执行安装或下载；推荐使用 `scripts/prepare_qwen_model.py --download --download-authorized`，避免下载到 Skill 包内。用户拒绝下载、也不提供自己的音频、其他 TTS 或已生成旁白时，音频流程阻断，并说明需要补充哪一种音频来源。

## 生成试听前先确认用户要什么声音

TTS API 或 VoiceDesign 模型通过预检后，不能直接替用户设计三个声音。先复用启动信息中已经收集的声音方向；缺项时才用一条简短问题补齐：

- 性别呈现：男声、女声、儿童声、中性或不限；
- 年龄感：儿童、少年、青年、成年、成熟或不限；
- 气质与情绪：例如轻快、温柔、可靠、松弛、克制、有故事感；
- 能量和语速：低/中/高能量，慢/中/快语速；
- 明确不想要的特征：例如播音腔、幼态、广告腔、机械感、过度煽情；
- 使用场景：品牌宣传、教程、故事旁白等。

用户可以回答“不限”或“由你判断”，但 Agent 不能从视频主题擅自补全未回答的核心条件。把用户原话和归纳结果写入 `voice-brief.json`，格式见 `assets/voice-brief-template.json`。用户原话已完整覆盖必填方向时，该原始回复可以直接作为需求批准；只有 Agent 加入了实质性推断时才展示归纳结果并再次确认。然后运行：

```bash
python3 scripts/validate_voice_brief.py \
  <项目目录>/voice-brief.json --require-approved
```

未通过声音需求门禁时，不得生成试听。确认后生成的三个候选必须固定用户指定的性别、年龄感和核心气质，只在音色明暗、亲密感、节奏或颗粒感等次要维度上形成可比较差异。若用户说三条都不好，记录整轮淘汰并回到声音需求单；先问清要调整的维度，不得继续盲抽三条。

## 模型就绪后由用户选声

Qwen VoiceDesign 不从 Skill 预设中选声音。模型预检和声音需求门禁都通过后，默认再给用户试听：

1. `audition`：声音需求单确认后，使用同一段 5—12 秒中性试听文案生成 3 个围绕已确认方向的试听文件，展示给用户后由用户明确选一个；服务限制时最少可为 2 个。VoiceDesign 试听调用 `generate_qwen_voice.py` 时必须传入 `--voice-brief`。
2. `direct-description`：只有用户明确要求跳过试听时使用，并记录该授权；不能由 Agent 自行选择。

不得用不同文案比较声音，也不得用与需求单冲突的性别或年龄制造差异；不得用内容或音量差异误导选择。把声音需求单及其 SHA-256、发现报告、预检报告、模型来源、候选描述、试听文件 SHA-256、最终声音描述和用户原始批准语句写入 `voice-selection.json`，并运行：

```bash
python3 scripts/validate_voice_selection.py \
  <项目目录>/voice-selection.json --require-approved
```

`voice-selection.json` 未通过时，只能继续调整或生成短试听，不能开始整条正式旁白。

## 使用 Qwen 生成正式旁白

模型准备好后，要求用户确认声音描述，再运行：

```bash
python3 scripts/generate_qwen_voice.py \
  --runtime-python <model-preflight.json 中的 python_executable> \
  --model-path <模型目录> \
  --segments-file <项目目录>/narration-contract.json \
  --output <项目目录>/audio/narration_v1.wav \
  --manifest-output <项目目录>/audio/narration_v1.manifest.json \
  --model-id mlx-community/Qwen3-TTS-12Hz-1.7B-VoiceDesign-bf16 \
  --model-url https://huggingface.co/mlx-community/Qwen3-TTS-12Hz-1.7B-VoiceDesign-bf16 \
  --voice-selection <项目目录>/voice-selection.json \
  --language Chinese \
  --contract-output <项目目录>/narration-contract.json
```

生成器从已批准的 `voice-selection.json` 读取最终声音描述，并核对模型目录、模型 ID 和模型地址；命令行不能临时换声。`--runtime-python` 必须沿用模型预检报告中的 `python_executable`，试听和正式旁白不得退回默认 `python3`。每个分段默认不超过 800 个字符，过长讲稿必须先拆分场景。脚本会输出 narration manifest，包含音频 SHA-256、实际时长和每个场景的连续时间戳；正式旁白生成后，人工抽听开头、中段、结尾和专有名词，再运行旁白契约校验。

## 其他 TTS 和自己的声音

- 用户已经录好完整口播：`voice_source` 使用 `external`，记录文件来源、SHA-256、实际时长、采样率和声道。
- 用户希望用自己的音色由模型生成：要求参考音频、对应逐字文本和授权说明，`voice_source` 使用 `user-reference`；缺少任一项就停止，并另外记录最终旁白文件。
- 用户已有 TTS API：`voice_source` 使用 `other-tts`，记录供应方、模型标识、地址、运行时、API 预检、已批准声音选择和实际生成文件；没有明确可用入口时不能假设存在。

已有音频或其他 TTS 生成文件使用 `scripts/register_audio_artifact.py` 登记。该脚本只读取和记录音频，不替用户选择模型，也不调用未说明的云服务：

```bash
python3 scripts/register_audio_artifact.py \
  --contract <项目目录>/narration-contract.json \
  --audio <项目目录>/audio/narration.wav \
  --voice-source other-tts \
  --provider <供应方> \
  --model-id <模型标识> \
  --model-url <模型或服务地址> \
  --runtime api \
  --voice-selection <项目目录>/voice-selection.json
```

## 旁白契约

每个项目建立 `narration-contract.json`，至少记录：

- `voice_profile`：音频来源标签；Qwen 使用 `qwen-voice-design`，这不是预设声音；草稿为空；
- `voice_source`：`open-source-model`、`other-tts`、`user-reference` 或 `external`；不得使用已删除的 `design-profile`；
- `provider`、`runtime`：TTS 供应方和执行运行时；
- Qwen 开源模型的 `voice_instruction`、`model_id`、`model_url`、`model_path`；
- `voice_selection_path` 与 `voice_selection_sha256`：Qwen 和 TTS API 都必须绑定用户已批准的声音选择文件；
- `authorization_record`：用户参考音频必须填写，其他来源填写 `not-required`；
- `audio_path`、`audio_sha256`、`duration_seconds`、`sample_rate`、`channels`、`audio_format`：正式旁白的实际产物信息；
- 用户参考音频另记录 `reference_audio`、`reference_audio_sha256`、`reference_text`；
- `display_text`：观众看到的字幕；
- `tts_text`：为正确发音做过归一化的朗读文本；
- `start_seconds`、`end_seconds`：由分段生成 manifest 回填，第一段从 0 开始，段间不得有未说明的空洞或重叠。

同一条视频不要拼接不同音色。口播修改后，重新生成受影响的完整连续段，并重新计算字幕与镜头时间轴。

## 旁白连续感

- 按完整语意段生成，每段直接绑定一个场景；停顿放在意思完整处，不强行删掉正常换气。
- 同一条视频固定同一个已批准声音、模型、生成参数族和后处理链，不拼接不同声音。
- 不默认使用强制 `silenceremove`；只有确认不会切掉字头、尾音和换气时才手工裁剪首尾。
- 替换声音或改变口播后，重新生成受影响的完整连续段，并按最终音频重算字幕和镜头时间轴，不沿用估算时间。
- 合成后做一次 ASR 对照并人工抽听开头、中段、结尾，重点核对数字、月份、专有名词、中英相邻词间隔、音色、语速、噪声底和空间感。

## 配乐

- 全片使用同一调性、节拍和乐器族；通过加减鼓组、低频、旋律与音色层推进，不拼接多首无关循环。
- 语音期间配乐默认比旁白低约 9—12 dB，以实际听感与响度检查为准。用户只说“音乐小一点”时优先下调配乐，不改变旁白响度。
- 开场、内容转折、重点结论和收束可以各有一次明确层级变化，但不能每个镜头都换音乐。
- 成片结束前 3—6 秒开始渐弱，让音乐在最后一句或收束后自然落下，不在最终帧硬切。

## 声效

只保留与真实画面事件对应的短声效，例如异常出现、对象入场、信号对齐、位置锁定和结论收束。没有可见事件时不加装饰声，不能用声效掩盖镜头缺少信息变化。

## 字幕与交付响度

- 只保留一个最终字幕渲染层。
- 综合响度目标约 -16.5 LUFS，可接受范围 -19 至 -14 LUFS；真峰值不高于 -1.0 dBFS。
- 默认交付 AAC、48 kHz、双声道、192 kbps 或更高。
- 输出前人工抽听开头、中段、结尾和专有名词，并运行视频预检确认音轨、静音段、响度和峰值。

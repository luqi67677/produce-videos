# 模板推荐与主题锁定

用户没有视觉方向时才推荐三套模板；用户已经提供完整视觉系统或明确指定模板时，直接验证、生成单个真实样张并锁定。

## 模板来源

唯一目录索引：`frontend-slides-themes/bold-template-pack/selection-index.json`。

先读索引缩小候选，再读候选的 `preview.md`；只有最终候选才读取 `design.md`。保留模板包自带的 `LICENSE` 和 `source.json`。

正式匹配前必须运行：

```bash
python3 scripts/validate_theme_catalog.py \
  references/frontend-slides-themes/bold-template-pack/selection-index.json
```

目录必须完整包含 34 个唯一模板；每套都必须有可读取的 `preview.md`、`design.md`、固定舞台、颜色、字体、布局、响应式、CJK 适配和已知限制。缺一套、索引漂移或说明残缺时，停止推荐，不从残缺目录里凑三个候选。

## 主题不等于构图

Frontend Slides 的主题负责提供可复用的设计 token：色板、字体角色、边框、材质、图表语法和标志性动作。演示页的具体标题长度、全大写方式、页码、栏数和信息密度不属于必须照搬的规则。

把主题用于视频时必须重新完成：

1. 按目标横竖画幅建立安全区；
2. 按中文阅读习惯重做字体层级和语义断行；
3. 保留品牌名的原始大小写；
4. 让真实素材成为足够大的主视觉；
5. 删除只为演示模板存在的页码、模板名、日期和装饰元数据。

如果主题的展示字体会把混排标题变成全大写，应保留主题的颜色、材质和结构特征，同时把主标题改为中文优先字体；这属于必要的本地化适配，不算混用主题。

## 匹配维度

- 内容：教程、产品、观点、故事、数据或案例；
- 受众：专业程度与阅读耐心；
- 情绪：克制、温暖、活跃、锋利或叙事；
- 密度：低、中、高；
- 平台：观看距离、节奏和信息流缩略图；
- 限制：品牌色、禁用色、字体和授权素材。

## 三个候选角色

- A `balanced`：最稳妥的结构和阅读体验。
- B `expressive`：更强的节奏或视觉记忆。
- C `unexpected-fit`：非直觉但有明确内容理由的方案。

三者必须来自不同模板 slug。不能预先固定三套，也不能只给三个颜色名称。

匹配时先基于全部 34 套索引的 `best_for`、`avoid_for`、情绪、密度、正式度和明暗方案完成筛选，再读取入围候选的 `preview.md`。在 `visual-style-options.json.catalog_evaluation` 中为 34 套逐项记录 `theme_slug`、0—100 分、`shortlisted/rejected` 和内容理由；入围项必须且只能是最终 A/B/C 的三个 slug。不得只在最近用过或最熟悉的少数模板中循环选择。

## 可比较样张

三套方案使用：

1. 同一封面标题；
2. 同一代表性镜头；
3. 同一画幅和信息量；
4. 各自完整的字体、配色、边框、材质和构图规则。

每套候选都必须分别输出 1080×1440 的 3:4 封面帧、与主视频目标画幅一致的代表性内容帧，以及 270×360 的封面缩略图。封面帧验证标题和主视觉，内容帧验证正文、证据与字幕安全区，缩略图验证信息流识别。三套使用同一标题、同一内容和同一真实主视觉，不能让某套靠更好的素材取胜。另把三套完整候选合成一张实际图片写入 `overview_preview`，将它作为对用户的主交付；HTML 预览只能补充，不能要求用户依靠本地页面完成选择。

样张必须来自实际渲染结果，不能只交付 HTML、JSX、设计说明或未经截图验证的页面。展示给用户前至少检查：

- 标题是否按语义断行、是否超出批准行数；
- 标题是否与用户确认稿逐字一致；若使用不同的封面标题，是否存在用户明确确认记录；
- 品牌词是否逐字保持原稿大小写；
- 主视觉是否足够大，是否因容器或裁切丢失关键信息；
- 原尺寸下是否对齐、清晰、无遮挡；
- 缩略图下是否仍能读出标题并认出主视觉。
- 主总览图是否能一次看到 A/B/C 的完整样张，而不是只露出顶部、需要猜测滚动方式或依赖浏览器缩放；若页面在当前查看器中显示不全，立即改用总览图片和三个缩略图，不让用户排查预览工具。

把检查结果逐套写入 `visual-style-options.json.quality_review`，再运行：


```bash
python3 scripts/validate_style_options.py project/visual-style-options.json \
  --catalog references/frontend-slides-themes/bold-template-pack/selection-index.json
```


任一候选出现溢出、空洞、品牌大小写错误、证据不可读、主视觉过小、内部标签泄漏或与另两套没有实质差异时，先修复；仍不适配则回到 34 套目录换候选。不能为了维持三选一而展示低质量样张。

## 锁定

只有完整目录检查和三套真实样张检查都通过后，才向用户展示 A/B/C。用户选定后，把用户原话与时间写入 `visual-style-options.json.selection_approval`，将 `status` 改为 `selected`，然后运行：

```bash
python3 scripts/validate_style_options.py project/visual-style-options.json \
  --catalog references/frontend-slides-themes/bold-template-pack/selection-index.json \
  --require-selected
```

通过后生成 `video-style-theme.json`：记录模板 slug、索引校验值、来源文件、语义颜色、图像生成提示和选择时间。运行 `validate_video_theme.py --require-locked` 后，生图、封面、字幕、组件和渲染才可继续；样片与正式渲染门禁还会重新校验 34 套目录、三套真实样张、用户选择和最终主题来源是否一致。

单个镜头遇到困难时，先调整构图和信息密度，不静默切换另一模板。只有用户明确要求重选，才生成新版本并记录替代关系。

选定主题后的第一张画面是校准门。只要原图或缩略图中任一项未通过，就只修这一张；校准通过前不得把该结构批量复制到分镜或成片。

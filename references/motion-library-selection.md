# 可落地的动效库与选择规则

适用于 V2.8.0。先把资源准备好，再供导演选用；本页不是已经剪好的样片。

## 已随 Skill 提供的运行资源

| 资源 | 固定版本 | 实际落位 | 用途 |
|---|---|---|---|
| [Anime.js](https://github.com/juliangarnier/anime) | 4.5.0 | `assets/motion-library/vendor/animejs/` | 数值缓动、文字与节点进出、路径推进、镜头取景、转场 |
| [Three.js](https://github.com/mrdoob/three.js) | 0.186.1 | `assets/motion-library/vendor/three/` | 空间坐标、相机和分层投影；本批使用 core 模块，不包含完整 WebGL 产品模型制作工具 |

两个引擎从固定 npm 发行包取文件，下载时核对 SHA-512；原始文件另记 SHA-256。原始 MIT 许可随文件保留。接入预设由本项目编写，并非把网页演示复制成成片。不会联网加载 CDN、监听鼠标、等待滚动或自主播放。

## 第一批 8 项预设

以 `assets/motion-library/library-manifest.json` 的真实参数为准。

| ID | 名称 | 导演怎么选 | 不适合怎么用 |
|---|---|---|---|
| title-reveal | 文字出场 | 章节标题、短关键词进入 | 每句旁白都弹跳；替代字幕本身 |
| stagger-reveal | 分批出场 | 按叙述次序介绍多个角色或步骤 | 同时堆满所有细节 |
| path-progress | 路径推进 | 随讲解画出有方向的联系 | 把装饰线当成实际数据传输 |
| task-transfer | 任务传递 | 沿已定义的路线移动任务或结果 | 随机游走暗示不存在的协作 |
| camera-focus | 镜头聚焦 | 从全局移到讲述中的局部，保留空间连续 | 连续换图抖动；裁掉人物脸 |
| crossfade | 交叉淡化 | 同一叙事空间中的平稳换景 | 两个信息密集画面长时间重叠 |
| background-pulse | 背景呼吸 | 很弱的背景明暗变化，支撑节奏 | 抢字幕、制造假事件、代替机制图变化 |
| layers-explode | 立体分层展开 | 从整体展开不同层，解释结构及归属 | 装饰性旋转；暗示没有依据的层级关系 |

空间展开负责“各层是什么、放在哪里”；任务传递负责“什么从谁到谁”。共享状态更新仍要标明对象、更新前后和读写方向。先给观众稳定的整体，再聚焦或分层；标签跟随对象，声音跟随有意义的事件。参考 Anatomy 的解释方法，不把立体效果当作事实依据。

## 实际使用

需要 Node.js 22 或更新版本。在 Skill 根目录运行：

```bash
python3 scripts/register_motion_library.py <项目目录>
```

工具先校验随包文件，再执行预设验证。通过后只在项目下生成 `motion-library/catalog.json`、执行日志和每项证明，不改导演表，不生成音频，不剪辑。目录里包含本地绝对路径，属于项目资料，不能回传公开 Skill 包。

1. 导演从目录中挑选需要的项放入 `director_plan.effect_catalog`。按每个镜头的讲解目的选择，不能为了把库用完而添加效果。
2. 在 `direction.effects` 给每次使用单独的实例 ID，写对象、参数、起止触发点及理由；背景单独写，明确静态或引用已选实例。
3. 剪辑师把实例绑定到 EDL 的镜头相对帧，通过 `seekFrame(frame, fps)` 定位。真实动作也可来自已经核验的视频素材，无须编造一个代码动效。
4. 实际审查字幕遮挡、人物脸部、相邻镜头衔接和可读性。执行测试通过不代表视觉验收，更不代表用户已批准。
5. 缺少合适效果先记录表达缺口；有授权时独立准备新库，核验后再入目录。不得把尚不存在的动效写成分镜中的已选资源。静态背景合法，但静态机制图不能借此绕过既有动态质量要求。

手动预览：在 Skill 根目录运行 `python3 -m http.server 8788 --bind 127.0.0.1`，打开 `/assets/motion-library/preview.html`，拖动时间查看同一份代码的结果。此页是库测试台，不是用户视频。

## React Bits 以及其他来源如何处理

[React Bits](https://github.com/DavidHDev/react-bits) 本次核对提交 `963f4d21dca65326a470956c42b7b467804f3c14`。[当前许可](https://github.com/DavidHDev/react-bits/blob/963f4d21dca65326a470956c42b7b467804f3c14/LICENSE.md) 为 MIT 加 Commons Clause，并对组件打包、移植再分发有限制，因此没有收入本公开包。它的内容入场、拆字、步骤导航可作为视觉候选；使用具体组件前需单独核验许可、固定提交、接管网页时钟和执行测试。目前不能作为已可用预设选择。

[HyperFrames](https://github.com/heygen-com/hyperframes) 的时间轴和转场方法用于学习；其网页示例的 GSAP 依赖要单独核验许可与本地运行条件，不因为 Skill 文件在本机就宣称引擎已经可用。[Motion](https://github.com/motiondivision/motion) 是后续候选，本轮未打包。没有为了库的数量重复安装同类引擎。

## 声音仍用真实本地资源

此动效目录不携带音效或音乐。音效、环境声、配乐从项目登记的本地文件选择，记录来源许可、哈希、入点、时长、增益、淡入淡出及与旁白的关系。没有合适文件就写无并说明理由，不能虚构雨声、笑声或配乐。调用当前已授权的旁白 TTS 流程不受此条限制。逐镜声音与跨镜连续性仍由导演计划和 EDL 校验。

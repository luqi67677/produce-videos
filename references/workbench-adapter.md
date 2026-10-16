# 工作台接入脚本 V0.3：中文界面、品牌与全轨同步剪切

此文件随 produce-videos V2.9.2 更新；`scripts/workbench.py` 沿用 V2.9.1 的实验入口。完整使用流程见 `editing-workbench.md`；原有成片质量门继续生效。

## 使用范围

- macOS/Linux、Python 3.10+，标准库；基线使用 POSIX 目录描述符，Windows 尚未验证。真实预览需已有 Node.js 22+ 与 Hyperframes 0.8.164。
- 项目需有 `index.html`，其中包含 `data-composition-id`；另有 `hyperframes.json` 或声明 Hyperframes 依赖的 `package.json`。
- 有 `shot-readiness.json` 时检查 `director_plan` 为 `planning/estimated` 或 `ready/measured`，至少一镜。不要求旁白文件存在，也不声称通过完整逐镜校验。
- 尚未绑定 produce-videos 契约的原生工程可使用 `STORYBOARD.md`，至少一个 `## Frame N`。此时报告 `timing_basis=unverified`，不能把它当成实测时间或获批画面。
- 目前只支持 `index.html` 为入口。工程内相对路径和源码不得使用符号链接；请直接指定真实目录。

## 命令

以下变量是本次调用参数；不应将私人路径写入开源 Skill。

首次使用时，将 `RUNTIME_DIR` 设为用户指定的真实工具目录，并使用随包锁文件。运行时安装在 Skill 外。已有未经修改的 Hyperframes 0.8.164 可直接执行补丁脚本。

```bash
RUNTIME_DIR='/用户指定的真实工具目录'
mkdir -p "$RUNTIME_DIR"
# 仅在新建的空运行时目录执行复制；已有未知安装不要覆盖。
cp assets/hyperframes-patches/0.8.164/package.json assets/hyperframes-patches/0.8.164/package-lock.json "$RUNTIME_DIR/"
npm ci --prefix "$RUNTIME_DIR" --ignore-scripts --no-audit --no-fund
python3 scripts/workbench_runtime_patch.py "$RUNTIME_DIR/node_modules/hyperframes"
HF_CLI="$RUNTIME_DIR/node_modules/hyperframes/bin/hyperframes.mjs"
```

补丁先校验版本及全部输入 SHA-256，再修改文件；未知文件拒绝，重复执行不重复修改，写入失败恢复已写文件。补丁改变前后端兼容代码，不捆绑完整第三方运行时。安装后停止旧预览进程并重启；`open` 同时检查磁盘补丁和实际服务的 `pv-sync-cut-1` 标识，不能凭 CLI 的原版本号声称已启用。

确认 `HF_CLI` 后执行：

```bash
PROJECT='/实际的工程目录'
python3 scripts/workbench.py doctor "$PROJECT" --hyperframes-cli "$HF_CLI"
python3 scripts/workbench.py snapshot "$PROJECT"
python3 scripts/workbench.py open "$PROJECT" --hyperframes-cli "$HF_CLI" --port 3027
python3 scripts/workbench.py inspect "$PROJECT" --include-source --max-source-chars 16000
python3 scripts/workbench.py check "$PROJECT"
```

`doctor` 不指定 CLI 时只检查工程并报告运行环境未检查。指定时仅执行版本查询；版本必须恰为 0.8.164，不自动降级或安装依赖。

`open` 通过参数数组执行 `node <cli> preview <project> --background --no-open --port <port> --json`，不用 shell。返回 CLI 实际给出的本机 `studioUrl`，不猜地址、不自动打开浏览器。Hyperframes 可能创建自身缓存并保持后台进程；脚本不自动停止既有服务，也没有验证 UI 是否加载成功。

`inspect` 默认列出受管理文件的哈希和大小。`--include-source` 另返回有长度上限的当前文本，便于 AI 在修改前读取 UI 最新保存的源。文本被截断会明确标记；此输出不适合直接当作完整文件覆盖回去。

`snapshot` 只向工程内 `.produce-videos-workbench/baseline.json` 写哈希基线，文件权限为 0600。默认拒绝覆盖。完成检查并接受当前版本后，才显式运行 `snapshot --replace-baseline`。基线只用于变化检测，不是审批账本或另一套项目进度；含本机项目路径，不进入发布包。

`check` 返回新增、修改、删除列表，不更新基线。不依赖当前 HTML/分镜仍然有效，因此误删入口也能被报告；但已有基线必须属于当前目录。移动工程后，先检查旧基线与源，再在新位置显式重建基线。

## 读取与写入边界

受管理范围为代码中明确列出的根契约，以及 `assets/`、`src/`、`styles/`、`scripts/`、`compositions/` 下受支持的媒体、字体和源码后缀。跳过隐藏文件、依赖目录、未列出的根文件与后缀，不跟随链接，也不读取 HTML 引用的外部路径。最多 2000 个受管理文件；超出即失败，不静默截断清单。

字幕保存范围显式包括根目录 `caption-overrides.json`、`captions.json`、`captions.srt`、`captions.vtt`。Hyperframes 0.8.164 运行时代码实际通过 `fetch("caption-overrides.json")` 加载字幕覆盖；没有据此扫描整个隐藏目录。上述源码目录内的 `.json`、`.txt` 也会跟踪，以覆盖字幕源与文稿。这里只读取用户已授权的可信视频工程；不要把凭证或私人资料放在这些目录中。

这不是全项目安全扫描。外部 URL、未管理路径、未知资源后缀和别处的共享素材不会被哈希跟踪。原生编辑器写入后的完整性与恶意程序同时重命名目录的竞态不在本版保障范围；请在本地可信项目中使用，保存后再检查。

`snapshot` 仅写基线，使用项目目录描述符、拒绝符号链接和原子替换。运行时补丁只修改明确指定的安装目录，工作台编辑通过原生版本校验保存及撤销记录更新工程。`open` 的外部进程会按 Hyperframes 自己的实现写缓存；脚本拒绝已知缓存路径的符号链接，但不承诺控制第三方程序的全部写入行为。

## 明确没有实现

- 没有 HTML → EDL 双向转换、字段映射或三方合并。
- 没有自动更新字幕契约、旁白、素材授权、镜头时间或审批。
- 没有镜头缓存、局部重渲染、最终导出或跨镜转场重建。
- 哈希差异只能证明文件改变，不能判断改了哪个语义字段，也不能证明两条时间线同步。
- `ready` 只表示字段声明。正式合成仍运行原 `validate_director_plan.py --require-ready`、时间线检查、render gate 和实际预览审查。

发现 Studio 改动后，AI 先运行 `check` 与 `inspect --include-source`，根据完整实际文件做逐项核对；未实现转换前不得打印“已同步 EDL”或跳过原质量门。

## 接入验证

运行 `python3 -B -m unittest discover -s tests -p 'test_workbench*.py' -v` 验证接入脚本。另用实际项目验证 CLI、原生编辑保存与重新打开；测试通过不能替代界面与成片验收。尚未完成完整同步前，不批量迁移已有视频工程。

全轨算法的实际运行时集成检查另见 `tests/test-range-cut.mjs`，需指向已打补丁的 0.8.164 包目录。该检查不替代真实浏览器的保存、刷新和撤销验收。


安装后可复跑：

```sh
node tests/test-range-cut.mjs --runtime "$RUNTIME/node_modules/hyperframes"
node assets/hyperframes-patches/0.8.164/test_frontend.mjs "$RUNTIME/node_modules/hyperframes/dist/studio/assets/index-DHqUZqg6.js"
```

第一组使用真实 HTML/GSAP 解析器和时间剪切函数；第二组使用原生保存函数与模拟文件接口。最终仍需浏览器验证保存、刷新与单步撤销。

## 中文界面与品牌配置

V2.9.2 对固定运行时安装静态中文文案补丁，并核验完整模块依赖的缓存版本。旧 `pv-sync-cut-1` 安装可按已知文件哈希升级，未知改动拒绝覆盖。

```bash
python3 scripts/workbench_runtime_patch.py "$RUNTIME_DIR/node_modules/hyperframes" --brand-profile "$PRIVATE_STYLE_PROFILE"
python3 scripts/workbench_runtime_patch.py "$RUNTIME_DIR/node_modules/hyperframes" --check
```

私有 JSON 档案使用 `editing_workbench.brand`，仅接受 `name`（1—32 字）与 `mark`（1—4 字）；未配置时用通用名称。安装器只把这两项写入运行时独立品牌配置，按无缓存路径加载，不打包私人资料。升级保留已安装品牌，未知格式或被改写的脚本会阻止安装。浏览器仍需刷新后读取新界面。

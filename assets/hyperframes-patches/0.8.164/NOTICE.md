# Hyperframes 兼容补丁声明

上游：Hyperframes（HeyGen），https://github.com/heygen-com/hyperframes 。适配版本 0.8.164，包声明许可证 Apache-2.0。协议条款见 LICENSE-Apache-2.0.txt；上游完整许可证：https://github.com/heygen-com/hyperframes/blob/main/LICENSE 。

此目录含 produce-videos 于 2026-10-16 编写的兼容补丁 pv-sync-cut-1，修改了 Studio 删除动作、中文模式按钮、偏好设置，以及后端范围剪切预览接口。上游文件中的版权、许可证和归属声明予以保留。此补丁不是 HeyGen 官方发布。

2026-10-17 增加简体中文操作文案、品牌读取组件、中文面板标题恢复与编辑器提示；移除上游桌面应用推广和反馈问卷的挂载。上游版权、许可证与库名仍保留；界面品牌替换不表示原引擎由本项目原创。

清单修改 Studio 主脚本、后端接口模块、入口 HTML、播放器、媒体处理子模块和默认 favicon。入口、动态导入和子模块反向导入统一加缓存版本，避免循环依赖再执行旧入口。品牌配置通过独立无缓存脚本读取，只携带用户明确配置的名称和文字标志，不包含私人档案全文。

运行时不打包进 Skill。package-lock.json 固定 npm 依赖；manifest.json 记录被修改文件的原始与修改后 SHA-256 和精确替换内容。安装器先核验所有文件，未知版本不修改，失败回滚。后端代码更新后须重启服务；仅前端更新后刷新页面。

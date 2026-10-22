---
name: media-transcribe
description: >
  统一转录抖音、B站、TikTok、微博、知乎、YouTube、视频号、播客、RSS 和本地音频，
  也可在用户已有浏览器登录态中批量同步并转录抖音公开账号作品；
  下载或读取音频后生成统一 Markdown；视频号单条转录只临时下载一个版本并在结束时清理，YouTube 英文内容可用 DeepSeek 翻译成中英对照。
  当用户发送这些平台的音视频链接、视频号分享链接、抖音公开账号 URL、BV 号、RSS 地址、本地音频，或要求“转录/转文字/下载播客/批量转录”时使用。
  不用于账号起号、社交平台发布、总结已有 Markdown、私密/会员内容、学习笔记/闪卡生成或视频剪辑，也不用于导入导出 Cookie 或绕过登录/验证码。
category: media
triggers:
  - 用户发送抖音、B站、TikTok、微博、知乎、YouTube 或视频号分享链接并要求转录
  - 用户发送小宇宙、喜马拉雅、播客直链、RSS 或本地音频并要求转录
  - 用户要求批量转录某个抖音公开账号的公开视频
  - "把这个视频转成文字"
  - "帮我批量转录播客"
version: 2.0.0
tags: [media, audio, video, podcast, transcription, translation, wechat-channels, douyin-account-batch]
---

# Media Transcribe

统一入口覆盖三种转录模式。视频默认使用 SenseVoice-Small，播客和本地音频使用 faster-whisper small；转录稿统一输出 Markdown。支持 macOS、Debian/Ubuntu Linux，以及 Windows 10/11 x64 PowerShell；Windows 抖音账号模式取决于 OpenCLI Browser Bridge 是否可用并已连接。

## 运行入口

- macOS/Linux：`.venv/bin/python scripts/transcribe.py --help`
- Windows PowerShell：`.\.venv\Scripts\python.exe .\scripts\transcribe.py --help`

下表使用 macOS/Linux 写法；Windows 将 Python 入口替换为 `.\.venv\Scripts\python.exe`。

## 无输入调用

用户只调用 Skill、尚未提供输入时，仅回复以下编号列表，不附加权利确认、第三方解析或临时文件说明：

```text
请提供需要转录的内容：

1. 抖音、B站/BV号、TikTok、微博、知乎或 YouTube 视频链接
2. 视频号分享链接
3. 播客页面或直接音频链接
4. RSS 地址
5. 本地音频路径
6. 抖音公开账号主页
```

收到具体视频号链接后，再在实际提交第三方解析前说明并取得本次同意。

## 模式路由

| 输入意图 | CLI 模式 | 代表命令 |
|---|---|---|
| 单个公开视频/音频 URL、视频号分享链接、BVID 或本地音频 | positional `source` | `.venv/bin/python scripts/transcribe.py "<source>" -o ./output`；视频号另需 `--allow-third-party-resolver` |
| RSS 批量下载或转录 | `--rss-url` | `.venv/bin/python scripts/transcribe.py --rss-url "<feed>" --count 10 -o ./output` |
| 抖音公开账号批量同步或转录 | `--account-url` | 先提示账号主页模式需要 OpenCLI Browser Bridge；连接成功后运行 `.venv/bin/python scripts/transcribe.py --account-url "<account-url>" -o ./output` |

当用户提供抖音账号主页并明确要求批量下载、同步或转录时，先运行 `opencli doctor` 检查环境。若 OpenCLI 已安装且 Daemon、Extension 均已连接，直接继续账号模式，不重复展示安装教程；仅在命令缺失或 Browser Bridge 未连接时，说明账号主页模式需要 OpenCLI 复用 Chrome 已有登录上下文来分页读取公开作品列表，并按缺失情况给出以下步骤：

1. CLI 未安装：`npm install -g @jackwener/opencli`
2. 扩展未安装：从 [OpenCLI Releases](https://github.com/jackwener/opencli/releases) 下载 Browser Bridge 扩展。
3. 在 Chrome 打开 `chrome://extensions/`，启用开发者模式，选择“加载已解压的扩展程序”。
4. 保持 Chrome 已登录 `www.douyin.com`，再次运行 `opencli doctor`，确认 Daemon 和 Extension 均为已连接。

不要在单个抖音视频、视频号、RSS、本地音频或其他不需要账号主页枚举的请求中展示上述 OpenCLI 步骤。单个抖音视频链接使用 positional `source`，不需要 OpenCLI。视频号只接受一个 `https://weixin.qq.com/sph/...` 分享链接：Agent 先说明该链接会发送给第三方 `sph.litao.workers.dev`，用户明确同意后才给 CLI 添加 `--allow-third-party-resolver`；直接 CLI 不会询问授权或自行添加参数。CLI 只下载一个可用版本到本次临时目录，并在结束时尽力清理由本次运行创建的临时视频和音频；成功时只把 Markdown 作为最终产物。

线上解析器因凭据、网络、超时或协议错误不可用时，CLI 以错误停止并给出 `--allow-yuanbao-fallback` 重跑提示，不会弹出选择、安装依赖或自动重试。Agent 应先说明失败，再另行询问是否切换隔离腾讯元宝；只有用户明确同意这一降级后，才根据缺失依赖提示运行可选 `wechat-yuanbao` 安装器，并添加 `--allow-yuanbao-fallback` 重跑。该路径打开本次运行专用的临时 Chrome profile，由用户手动登录腾讯元宝；只在元宝页面中同源提交分享链接，不导出 Cookie、不读取或代输密码/OTP/验证码、不修改系统代理，结束后尽力关闭隔离 Chrome 并删除 profile。公共解析成功时不得启动该路径。

不要自动进入 `qiaomu-wx-video` 高权限本地捕获。其根证书、2023 代理接管和异步解密/转码完成状态尚无可依赖的安全恢复契约；不得自动安装后端、信任根证书、启动本地捕获、修改 Shadowrocket 或系统代理。不要自动升级 OpenCLI，也不要导入导出 Cookie、代输凭据或处理验证码。

自动路由不确定时不要猜，要求用户提供可识别输入或显式平台。安装、组件依赖、完整参数和账号目录结构见 [`README.md`](README.md)。

## 边界

支持公开且用户有权处理的媒体、RSS，以及用户当前 Chrome/OpenCLI 会话可见的抖音公开账号作品。视频号在线解析只在用户逐次同意后把单个分享链接发送给第三方，不发送 Cookie、登录态或抓包内容；账号枚举只复用浏览器已有登录上下文，Cookie 和凭据不会被导出、序列化、写入 SQLite/产物或交给视频下载器。

不支持私密/会员内容、自动输入密码/OTP/验证码、Cookie 导入导出、绕过登录或平台访问控制、说话人分离、视频剪辑、账号运营和内容发布。登录过期、验证码、429 或平台限制应作为外部失败如实报告。


## 输出契约

| 模式 | stdout | 主要产物 |
|---|---|---|
| 单项 | 成功时恰好一条最终 Markdown 路径 | 一份转录 Markdown；视频号 CLI 尽力清理由本次运行创建的临时媒体与隔离 profile |
| RSS 转录 | 每个成功生成或复用的稿件一条 Markdown 路径 | 多份 Markdown；`--transcribe-only` 使用已有音频 |
| RSS `--download-only` | 空 | `<output>/audio/*`，不创建 Markdown |
| 抖音账号处理 | 每个本次完成的 transcript 一条路径 | `transcripts/*.md`、`summary.md`、持久队列和失败记录 |
| 抖音账号 `--sync-only` | 空 | `queue.sqlite3`、`account.json`、`summary.md` |

状态、警告和第三方进度只写 stderr。转录类 Markdown 的统一 frontmatter 包含 `title`、`type`、`tags`、`created`、`platform`、`source`、`language`、`translated` 和 `transcriber`。只有播客、RSS 和直接本地音频输出保留时间戳；包括视频号在内的视频输出不保留时间戳，即使内部降级为 faster-whisper，也必须在写入最终 Markdown 前移除时间戳、恢复自然标点并合并语义连续的分段，不能交付“一行一句、无标点”的中间稿。YouTube 翻译成功时同时输出中文和英文原文；SenseVoice 移除音乐、情绪和声音事件表情标记。

## 执行原则

1. 先确认输入公开且用户有权处理；账号模式还需已有 Chrome/OpenCLI 登录上下文。
2. 不要在转录成功前创建最终 Markdown；download-only 和 sync-only 按其非 Markdown 产物验收。
3. 不要把 mock、静态 fixture 或离线测试称为真实宿主路由或平台端到端成功。
4. 用户要求查看下载进度时，CLI 必须在当前前台运行并实时展示从开始到完成的下载状态；除非用户明确要求后台执行，不要把任务放到后台后再转述日志。
5. 首次模型下载和长音频 CPU 转录可能耗时较长，应提前说明。

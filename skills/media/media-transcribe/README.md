# Media Transcribe

![Media Transcribe 分享卡片](assets/share-card.png)

Media Transcribe 是一个统一的音视频转录工具和 Agent Skill。它会识别媒体来源，检查目标能力是否已安装，下载或读取音频，调用对应的语音识别引擎，并输出结构统一的 Markdown。

提供三种运行模式：

| 模式 | 输入 |
|---|---|
| 单项转录 | 单个公开视频/音频 URL、BVID 或本地音频 |
| RSS 批量 | RSS feed，可下载音频、转录或复用已有音频 |
| 抖音账号批量 | 抖音公开账号 URL/sec_uid，使用持久队列同步或顺序转录 |

## 支持范围

- 抖音短链和完整链接
- 抖音公开账号批量枚举、持久队列与断点续跑
- B 站链接和 BV 号
- TikTok、微博、知乎、YouTube 公共链接
- 小宇宙、喜马拉雅等播客页面
- 直接音频 URL 和本地音频文件
- RSS 播客批量下载与转录
- YouTube 英文内容的可选 DeepSeek 中文翻译
- 单个视频号分享链接的逐次授权转录；临时媒体在结束时清理

视频默认使用 SenseVoice-Small；播客、RSS 和本地音频使用 faster-whisper small。两种引擎均按 CPU 模式运行。视频号单条转录会在用户逐次同意后，把分享链接发送给第三方 `sph.litao.workers.dev` 解析；只临时下载一个可用编码版本，转录结束后删除本次视频和音频。

> 仅处理公开且你有权使用的内容。抖音账号模式只复用用户已有 Chrome/OpenCLI 登录态读取浏览器可见的公开作品，不导入或导出 Cookie，也不绕过登录或验证。本项目不支持私密/会员内容、说话人分离、视频剪辑、账号运营或内容发布。平台接口和访问限制可能变化，因此不保证所有公开链接始终可以下载。

## 快速安装

在 Claude Code 或其他能执行本地命令的 AI Agent 中，直接复制下面这句话：

```text
请从 https://github.com/loqz99156/media-transcribe 安装 media-transcribe 到当前项目的 .claude/skills/media-transcribe，然后根据当前系统安装本 Skill 可管理的 Python 依赖，检查 FFmpeg 等系统命令，并运行组件检查和 CLI help 验证安装结果。
```

如果只需要部分能力，也要保留安装来源和目标目录：

```text
请从 https://github.com/loqz99156/media-transcribe 安装 media-transcribe 到当前项目的 .claude/skills/media-transcribe，只安装本地音频转录，并验证安装结果。
请从 https://github.com/loqz99156/media-transcribe 安装 media-transcribe 到当前项目的 .claude/skills/media-transcribe，只安装抖音和 B 站视频转录，并验证安装结果。
请从 https://github.com/loqz99156/media-transcribe 安装 media-transcribe 到当前项目的 .claude/skills/media-transcribe，只安装 RSS 下载和转录，并验证安装结果。
```

AI 会识别当前系统，调用 macOS/Linux 的 `install.sh` 或 Windows 的 `install.ps1`，完成后检查对应组件。缺少 FFmpeg 等系统依赖时，AI 会说明需要执行的安装命令；涉及系统级安装或权限确认时仍需用户批准。

### 手动安装参考

环境要求：

- macOS、Debian/Ubuntu Linux，或 Windows 10/11 x64
- Python 3.9 或更高版本
- Windows 建议使用 PowerShell 7 和 Windows Terminal
- 可访问 Python 包、模型和媒体来源的网络环境

### macOS / Linux

```bash
cd .claude/skills/media-transcribe
bash install.sh
```

### Windows PowerShell

```powershell
cd .claude\skills\media-transcribe
powershell -NoProfile -ExecutionPolicy Bypass -File .\install.ps1 -All
```

Windows 安装器创建 `.venv\Scripts\python.exe`；Bash 安装器创建 `.venv/bin/python`。两者都只修改本 skill 目录，不修改 shell profile 或全局 Python。

在 macOS/Linux 终端中，Bash 安装器会显示组件选择菜单；PowerShell 裸运行 `install.ps1` 时也会提示选择。输入一个或多个组件名，可以安装单个平台、共享能力或全部组件。

```text
1) all            全部能力
2) video          所有视频平台
3) douyin         抖音
4) bilibili       B 站
5) tiktok         TikTok
6) weibo          微博
7) zhihu          知乎
8) youtube        YouTube
9) wechat-channels 视频号单条转录
10) wechat-yuanbao  隔离腾讯元宝降级
11) podcast        远程播客/音频
12) rss            RSS 下载和转录
13) local-audio    本地音频
14) rss-download   仅下载 RSS 音频
```

非交互环境不会等待输入，裸命令默认安装全部组件。macOS/Linux 可以直接使用确定性命令：

```bash
# 安装全部
bash install.sh --all

# 只安装一个组件
bash install.sh --component youtube
bash install.sh --component local-audio

# 一次安装多个组件，共享依赖会自动去重
bash install.sh --component douyin --component podcast
```

Windows PowerShell 对应命令：

```powershell
# 安装全部
powershell -NoProfile -ExecutionPolicy Bypass -File .\install.ps1 -All

# 安装一个或多个组件
powershell -NoProfile -ExecutionPolicy Bypass -File .\install.ps1 -Component youtube
powershell -NoProfile -ExecutionPolicy Bypass -File .\install.ps1 -Component douyin,podcast

# 只检查，不安装
powershell -NoProfile -ExecutionPolicy Bypass -File .\install.ps1 -Check -Component youtube
```

### 组件与依赖

| 组件 | Python 能力 | 系统命令 |
|---|---|---|
| `video` | SenseVoice + yt-dlp | `curl`、`ffmpeg`、`ffprobe` |
| `wechat-channels` | SenseVoice | `ffmpeg`、`ffprobe` |
| `wechat-yuanbao` | websocket-client（只用于可选隔离元宝降级） | Google Chrome 或 Chromium；浏览器由运行时检查，安装器不会安装 |
| `douyin` | SenseVoice | `curl`、`ffmpeg` |
| `bilibili` / `tiktok` / `weibo` / `zhihu` / `youtube` | SenseVoice + yt-dlp | `ffmpeg`、`ffprobe` |
| `podcast` / `rss` | faster-whisper | `curl` |
| `local-audio` | faster-whisper | 无 |
| `rss-download` | 无额外转录包 | `curl` |

如果缺少系统命令，安装器会列出缺失项，并提示对应命令。例如：

```bash
# macOS
brew install ffmpeg curl

# Debian/Ubuntu
sudo apt-get install ffmpeg curl

# Windows 10/11 PowerShell
winget install --id Gyan.FFmpeg --exact
# 当前 Windows 10/11 通常自带 curl.exe；若缺失，请先更新 Windows 或单独安装 curl。
```

安装器只给出提示，不会自动调用 Homebrew 或 APT。

检查全部或指定组件：

```bash
bash install.sh --check
bash install.sh --check --component youtube
bash install.sh --check --component local-audio
```

查看安装器参数和组件列表：

```bash
# macOS/Linux
bash install.sh --help
```

```powershell
# Windows
powershell -NoProfile -ExecutionPolicy Bypass -File .\install.ps1 -Help
```

首次使用某个语音识别引擎时可能需要下载模型；长音频在 CPU 上转录也可能耗时较长。

## 缺失组件提示

CLI 会先识别链接或本地文件，再检查该流程实际需要的依赖。如果组件尚未安装，它会在下载媒体、创建输出目录或加载模型前停止，并给出缺失项和一条可复制的单独安装命令，例如：

```text
error: Missing dependencies for youtube (...). Install this component with: bash '/absolute/path/media-transcribe/install.sh' --component youtube
```

在 macOS/Linux 上，提示会使用 `install.sh` 的绝对路径；在 Windows 上，提示会使用 `install.ps1` 的绝对路径和 PowerShell 安全执行参数。因此从其他工作目录调用 CLI 时也可以直接复制对应命令。安装完成后，重新运行原转录命令即可。

## 环境变量

### `DEEPSEEK_API_KEY`（可选）

为 YouTube 英文转录启用 DeepSeek 中文翻译：

```bash
export DEEPSEEK_API_KEY="your-api-key"
```

未设置时仍会输出英文原文。该变量不是安装前置条件。

### `PYTHON`（可选）

安装时指定 Python 解释器：

```bash
PYTHON=/path/to/python3 bash install.sh --component local-audio
```

## 使用方法

在 Claude Code 或其他能访问本地文件、执行命令的 AI Agent 中，直接提供链接或文件路径，并用自然语言说明目标。无需自己拼接 CLI 命令。

## Agent 入口与直接 CLI 的区别

README 中的自然语言示例描述的是 **Agent Skill 体验**：Agent 负责询问内容处理权和第三方解析授权、根据错误提示询问是否切换隔离元宝，并在获得授权后运行安装器或重试命令。直接运行 `scripts/transcribe.py` 时，CLI 不会弹出选择题、不会自行表示同意、不会安装依赖，也不会静默切换降级路径；它只校验显式参数、执行已授权路径，并在缺少依赖或需要另行授权时以错误和可复制命令退出。

### 单个视频、播客或音频

```text
把这个视频转成文字：https://youtu.be/xxxxx
转录这个 B 站视频：BV1xxxxxxxxx
把这个抖音视频转成 Markdown：https://v.douyin.com/xxxxx/
转录本地文件：/path/to/audio.m4a
转录这个公开视频号；我同意把分享链接发送给第三方解析服务：https://weixin.qq.com/sph/xxxxx
转录这个 YouTube 视频，但不要翻译成中文：https://youtu.be/xxxxx
```

### RSS 批量下载或转录

```text
把这个 RSS 最新 10 集下载并转录：<feed-url>
只下载这个 RSS 的前 10 集音频，不转录：<feed-url>
转录 output 目录里已经下载好的 RSS 音频：<feed-url>
```

### 抖音账号主页批量处理

```text
批量转录这个抖音公开账号的作品：<账号主页 URL>
只同步这个抖音账号的公开作品列表，先不要转录：<账号主页 URL>
先下载并转录这个抖音账号最早的 10 条公开视频：<账号主页 URL>
继续上次中断的账号转录，并重试失败任务：<账号主页 URL>
```

只有收到“抖音账号主页 + 批量下载、同步或转录”请求时，AI 才检查 `opencli doctor`。OpenCLI 已连接就直接执行；未安装或 Browser Bridge 未连接时，AI 会在当次任务中说明并给出对应安装步骤。单个抖音视频、视频号、RSS 和本地音频不需要 OpenCLI。

视频号只接受单个 `https://weixin.qq.com/sph/...` 分享链接。在线解析会把该链接发送给第三方 `sph.litao.workers.dev`，因此 Agent 必须逐次说明并取得用户同意；直接 CLI 用调用方显式传入的 `--allow-third-party-resolver` 表示本次同意，它不会自行询问或添加该参数。公共解析优先选择 H.264，缺失时回退 H.265 或默认流；元宝降级跟随腾讯官方播放器提供的媒体地址。CLI 只临时下载一个版本，验证视频与音轨后提取临时音频，并在结束时尽力清理由本次运行创建的视频、音频和浏览器 profile；成功时只把 Markdown 作为最终产物。

如果线上解析器凭据过期、网络不可用或返回无效协议响应，直接 CLI 会以退出码 `2` 停止，并提示调用方安装可选组件、取得第二次授权后使用 `--allow-yuanbao-fallback` 重跑；它本身不会弹出“是否切换”的交互，也不会自动安装或重试。通过 Agent Skill 使用时，Agent 才会根据该错误另行询问是否切换，并在用户同意后运行对应安装检查与重跑命令。元宝路径打开本次运行专用的临时 Chrome profile，等待用户手动登录，在该页面内同源提交分享链接，再读取腾讯官方播放页的受信媒体地址；它不导出 Cookie、不读取密码或验证码，也不修改系统代理。

视频号获取流程的方法总结与安全边界参考了 [joeseesun/qiaomu-wx-video](https://github.com/joeseesun/qiaomu-wx-video)。本项目为独立实现，不复制或捆绑其可选 `wx_channels_download` 后端；来源与许可证边界见 [`LICENSE`](LICENSE)。该高权限本地捕获后端目前不作为自动降级：它需要根证书和代理接管，而且后端 `done` 状态可能早于异步解密/转码结束，现有包装脚本也没有完成可验证的代理恢复和最终媒体稳定性契约。因此本 Skill 不自动安装该后端、不信任根证书、不启动 2022/2023 服务，也不修改 Shadowrocket 或系统代理。直播生成回放不保证可解析。

如果输入不明确，AI 应先询问来源、处理数量或是否只下载，不要猜平台。只处理公开且用户有权使用的内容；不导入导出 Cookie，不代输密码、OTP 或验证码，也不绕过平台限制。

## CLI 参考（高级用法）

以下 macOS/Linux 命令均在 `.claude/skills/media-transcribe` 目录内执行。Windows PowerShell 使用相同参数，但将 `.venv/bin/python` 替换为 `.\.venv\Scripts\python.exe`，路径分隔符可使用 `\`。

### 单项转录

```bash
# YouTube
.venv/bin/python scripts/transcribe.py "https://youtu.be/xxxxx" -o ./output

# B 站 BV 号
.venv/bin/python scripts/transcribe.py "BV1xxxxxxxxx" -o ./output

# 抖音
.venv/bin/python scripts/transcribe.py "https://v.douyin.com/xxxxx/" -o ./output

# 视频号（逐次同意把分享链接发送给第三方解析服务）
.venv/bin/python scripts/transcribe.py "https://weixin.qq.com/sph/xxxxx" --allow-third-party-resolver -o ./output

# 线上解析失败并退出后，由调用方另行取得授权并重跑隔离元宝路径
# 若缺少可选依赖，先根据 CLI 错误运行：
bash install.sh --component wechat-yuanbao
.venv/bin/python scripts/transcribe.py "https://weixin.qq.com/sph/xxxxx" \
  --allow-third-party-resolver --allow-yuanbao-fallback -o ./output

# 本地音频
.venv/bin/python scripts/transcribe.py "/path/to/audio.m4a" -o ./output
```

程序默认自动识别来源。无法可靠识别时，可以显式指定平台：

```bash
.venv/bin/python scripts/transcribe.py "<source>" --platform podcast -o ./output
```

可选平台值：

```text
auto, douyin, bilibili, tiktok, weibo, zhihu, youtube, wechat-channels, podcast
```

关闭 YouTube 英文翻译：

```bash
.venv/bin/python scripts/transcribe.py "<youtube-url>" --no-translate -o ./output
```

覆盖已有 Markdown：

```bash
.venv/bin/python scripts/transcribe.py "<source>" --overwrite -o ./output
```

### 抖音账号批量转录

> **账号主页模式需要 OpenCLI Browser Bridge。** 当输入一个抖音账号主页并要求批量下载、同步或转录时，程序需要通过 OpenCLI 复用 Chrome 已有登录上下文，分页读取浏览器可见的公开作品列表。OpenCLI 只负责枚举作品，不负责下载或语音识别。**转录单个抖音视频链接不需要 OpenCLI。**

账号模式会先在用户已有登录态的 Chrome/OpenCLI 浏览器上下文中分页冻结公开作品清单，再用 SQLite 队列从旧到新逐个处理。账号枚举请求只在该页面上下文内使用已有凭据；Cookie 和凭据不会被导出、序列化、写入队列/产物或交给视频下载器。它不自动输入密码、OTP 或验证码，也不绕过登录、验证和平台限制。

#### 首次需要账号批量处理时安装并连接 OpenCLI

以下步骤只在实际使用“抖音账号主页批量下载、同步或转录”且 `opencli doctor` 显示未安装或未连接时执行。单视频、RSS、本地音频不需要，也不应重复提示；如果 Daemon 和 Browser Extension 已连接，可直接运行账号模式。

1. 安装 OpenCLI CLI（需要 Node.js 和 npm）：

   ```bash
   npm install -g @jackwener/opencli
   ```

2. 从 [OpenCLI Releases](https://github.com/jackwener/opencli/releases) 下载 Browser Bridge 扩展并解压。
3. 在 Chrome 打开 `chrome://extensions/`，开启“开发者模式”，点击“加载已解压的扩展程序”，选择扩展目录。
4. 保持 Chrome 打开，并确认已经登录 `www.douyin.com`。
5. 检查连接：

   ```bash
   opencli doctor
   ```

只有 Daemon 和 Browser Extension 均显示已连接后，才运行账号模式。安装 CLI 并不等于扩展已经连接；如果看到 `Extension: not connected`，请检查 Chrome 是否运行、扩展是否已启用。不要导入导出 Cookie、代输账号凭据或绕过验证码来建立连接。

macOS/Linux 已按此流程设计；Windows 账号模式仅在 OpenCLI daemon、Chrome Extension 和 Browser Bridge 均支持 Windows且 `opencli doctor` 通过时条件支持。普通单视频、RSS 和本地音频转录不依赖 OpenCLI。

同步账号并开始处理：

```bash
.venv/bin/python scripts/transcribe.py \
  --account-url "https://www.douyin.com/user/<sec_uid>" \
  -o ./outputs/media-transcribe
```

常用选项：

```bash
# 只同步公开作品列表，不转录
.venv/bin/python scripts/transcribe.py --account-url "<url>" --sync-only -o ./outputs/media-transcribe

# 先用 10 条验证流程
.venv/bin/python scripts/transcribe.py --account-url "<url>" --max-videos 10 -o ./outputs/media-transcribe

# 重新入队最终失败的视频
.venv/bin/python scripts/transcribe.py --account-url "<url>" --retry-failed -o ./outputs/media-transcribe

# 从新到旧；默认 oldest
.venv/bin/python scripts/transcribe.py --account-url "<url>" --order newest -o ./outputs/media-transcribe
```

每个账号的输出结构：

```text
outputs/media-transcribe/accounts/<sec_uid>/
├── queue.sqlite3             # 持久队列、状态和错误
├── account.json              # 账号元数据
├── summary.md                # 汇总与逐条状态
├── transcripts/              # 已完成 Markdown
├── failed/failures.jsonl     # 失败记录
└── queue.sqlite3.lock        # 运行时互斥锁，正常退出自动删除
```

队列单线程顺序运行，默认视频间隔 8 秒。单条失败会重试，最终失败不会阻断后续视频；进程中断时，活动任务在下次启动恢复为 pending。当前保证视频级续跑，不保证单条视频内部的下载/转录断点续传。账号分页接口、登录态或平台风控失效时会停止同步，但已冻结的队列和已完成文件不会丢失。

### RSS 批量处理

下载并转录连续 10 集：

```bash
.venv/bin/python scripts/transcribe.py \
  --rss-url "<feed-url>" \
  --start 1 \
  --count 10 \
  -o ./output
```

仅下载音频：

```bash
.venv/bin/python scripts/transcribe.py \
  --rss-url "<feed-url>" \
  --download-only \
  -o ./output
```

仅转录输出目录中已有的音频：

```bash
.venv/bin/python scripts/transcribe.py \
  --rss-url "<feed-url>" \
  --transcribe-only \
  -o ./output
```

`--start` 按 RSS 的 `itunes:episode` 集号选择起点，`--count` 表示从该集号开始的连续集数。批量流程会顺序处理并复用同一个 faster-whisper 模型；已有音频和 Markdown 默认复用，只有使用 `--overwrite` 才覆盖 Markdown。`--transcribe-only` 仍需访问 RSS feed，以读取集数和音频元数据。

查看全部转录参数：

```bash
.venv/bin/python scripts/transcribe.py --help
```

## 运行状态

状态按实际执行阶段写入 `stderr`；成功结果路径单独写入 `stdout`。不同来源的阶段数不同：普通 yt-dlp 视频当前为 8 个阶段，抖音为 10 个，视频号公共解析为 10 个，视频号隔离元宝降级为 13 个。第一个 `Detecting source` 在确定总数前显示为 `[1/?]`。

普通视频的真实状态示例：

```text
[1/?] | Detecting source · 00:00
[2/8] | Checking dependencies · 00:00
[3/8] | Resolving bilibili metadata · 00:06
[4/8] | Downloading and extracting bilibili audio · attempt 1/1 · 00:08
[5/8] | Download complete; preparing transcription · 00:17
[6/8] | Loading SenseVoice-Small · 00:17
[7/8] | Transcribing audio · 00:22
[8/8] | Writing Markdown · 01:43
```

B站、YouTube 等使用 yt-dlp 的路径能够取得下载字节信息时，还会显示真实百分比、大小、速度和 ETA：

```text
14.5% · 1023.0/6.9 MiB · 3.2 MiB/s · ETA 00:01
58.1% · 4.0/6.9 MiB · 4.8 MiB/s · ETA 00:00
100.0% · 6.9/6.9 MiB · 3.7 MiB/s · ETA 00:00
```

视频号公共解析失败并经用户另行授权切换隔离元宝后，当前实际阶段为：

```text
[3/13] | Resolving WeChat Channels share link
[4/13] | Opening isolated Tencent Yuanbao browser
[5/13] | Waiting for Yuanbao same-origin parsing
[6/13] | Reading the official WeChat Channels media URL
[7/13] | Downloading temporary WeChat Channels video
[8/13] | Validating temporary WeChat Channels video
[9/13] | Extracting temporary audio
[10/13] | Download complete; preparing transcription
[11/13] | Loading SenseVoice-Small
[12/13] | Transcribing audio
[13/13] | Writing Markdown
```

等待用户登录时会显示 `Log in to Tencent Yuanbao in the isolated Chrome window; waiting for login`。视频号临时媒体下载当前只能可靠显示阶段，没有下载百分比、速度或 ETA。

ASR 在引擎提供分段信息时显示 `segment i/n`；长时间没有新分段时，每 15 秒输出一次 `still working` 心跳。心跳表示进程仍在运行，不是精确完成百分比：

```text
segment 1/1
Transcription in progress · still working · 00:15
Transcription in progress · still working · 01:15
```

交互终端会在同一行刷新旋转状态；后台任务、管道和重定向环境使用普通逐行日志，不包含 ANSI 或回车控制字符。RSS 会在阶段中显示 `Episode i/n`。首次下载 SenseVoice 模型时，ModelScope 的下载输出也会转发到 `stderr`。

## 输出

| 模式 | stdout | 主要产物 |
|---|---|---|
| 单项转录 | 恰好一条最终 Markdown 路径 | 一份转录 Markdown；视频号 CLI 尽力清理由本次运行创建的临时视频、音频和隔离 profile |
| RSS 转录 / `--transcribe-only` | 每个成功生成或复用的稿件一条路径 | 多份转录 Markdown |
| RSS `--download-only` | 空 | `<output>/audio/*`，不创建 Markdown |
| 抖音账号处理 | 每个本次完成的 transcript 一条路径 | `transcripts/*.md`、`summary.md`、队列和失败记录 |
| 抖音账号 `--sync-only` | 空 | `queue.sqlite3`、`account.json`、`summary.md` |

转录类 Markdown 的 frontmatter 包含：

- `title`、`type`、`tags`、`created`
- `platform`、`source`、`language`
- `translated`、`transcriber`

播客输出保留时间戳；YouTube 翻译成功时同时包含“中文翻译”和“English Original”；SenseVoice 输出不会伪造时间戳，并会移除模型生成的音乐、情绪和声音事件表情标记。

## 项目结构

```text
media-transcribe/
├── SKILL.md                       # Agent Skill 入口与执行规则
├── README.md                      # 项目说明
├── LICENSE                        # MIT License
├── agents/
│   └── interface.yaml             # Agent 宿主接口信息
├── install.sh                     # macOS/Linux 交互式/组件化安装与检查
├── install.ps1                    # Windows PowerShell 组件化安装与检查
├── requirements.txt               # 全部 Python 依赖聚合入口
├── requirements/
│   ├── sensevoice.txt             # 视频转录依赖
│   ├── whisper.txt                # 播客/本地音频转录依赖
│   ├── downloaders.txt            # yt-dlp 下载依赖
│   └── yuanbao.txt                # 隔离元宝 CDP 连接依赖
├── scripts/
│   ├── transcribe.py              # CLI 入口
│   ├── validate_evals.py          # 静态 prompt fixture schema/tag 校验
│   └── media_transcribe/
│       ├── cli.py                 # 参数解析与流程编排
│       ├── account_queue.py       # 抖音账号 SQLite 队列与恢复
│       ├── account_enumerator.py  # OpenCLI 登录浏览器分页枚举
│       ├── account_worker.py      # 顺序转录、重试与汇总
│       ├── dependencies.py        # 来源感知的依赖预检
│       ├── routing.py             # 来源自动识别
│       ├── downloaders.py         # 视频平台下载适配
│       ├── wechat_yuanbao.py      # 隔离元宝同源解析降级
│       ├── podcast.py             # 播客、音频与 RSS 处理
│       ├── engines.py             # SenseVoice 与 faster-whisper
│       ├── translation.py         # 可选 DeepSeek 翻译
│       ├── render.py              # Markdown 渲染
│       └── models.py              # 数据模型
├── tests/                         # 离线单元测试与 fixtures
└── evals/
    └── evals.json                 # 静态触发与边界 prompt fixtures
```

## 本地验证

```bash
# macOS/Linux
bash -n install.sh
bash install.sh --check --all
.venv/bin/python scripts/transcribe.py --help
.venv/bin/python -m unittest discover -s tests -p 'test_*.py'
.venv/bin/python scripts/validate_evals.py
```

```powershell
# Windows PowerShell
powershell -NoProfile -ExecutionPolicy Bypass -File .\install.ps1 -Check -All
.\.venv\Scripts\python.exe .\scripts\transcribe.py --help
.\.venv\Scripts\python.exe -m unittest discover -s tests -p 'test_*.py'
.\.venv\Scripts\python.exe .\scripts\validate_evals.py
```

这些命令验证本地依赖、CLI、离线逻辑和静态 prompt fixture 的 schema/tag 覆盖。`validate_evals.py` 不调用真实宿主路由，因此不能证明 Skill 会被宿主正确选择；这些验证也不等同于真实平台端到端成功。

## License

本项目采用 [MIT License](LICENSE)。

视频号下载方法总结与安全边界参考自：
https://github.com/joeseesun/qiaomu-wx-video

本项目为独立实现，未复制或捆绑该项目的可选 `wx_channels_download` 后端；该后端继续适用其自身许可证与 Commons Clause 限制。

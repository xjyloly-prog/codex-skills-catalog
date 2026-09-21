# Codex 技能总目录 · Codex Skills Catalog

> 中英双语 · 标注来源 · 共 263 个技能 / Bilingual · Attributed · 263 skills

本仓库是一份**目录与说明书**，收录本机可用的全部 Codex 技能（skills）与角色分工（agents），方便按需查找和启用。

**所有技能的版权属于各自的原作者**，本仓库只做索引与说明，不重新分发技能文件本身。每一节都标注了来源仓库与许可证。

## 怎么用 / How to use

1. 告诉 Codex 你要做什么（例如“帮我审这篇数模论文”）。
2. Codex 把对应技能**挂载**到 `~/.codex/skills`。
3. **新开一个对话**，该技能即可用（技能清单在对话开始时读取）。
4. 用完告诉 Codex，技能被**卸载**，不占用上下文。

```powershell
# 只看不装：列出全部可安装技能
.\install.ps1 -List
# 安装需要的技能（从原仓库下载）
.\install.ps1 -Only innovation-proposal,qu-ai-wei
# 不想要了就删掉对应目录
Remove-Item "$env:USERPROFILE\.codex\skills\innovation-proposal" -Recurse
```

> 为什么要按需装卸：技能清单会在**每次对话开始时**注入上下文，装得越多，每轮消耗的 token 越多。只装当下要用的，能省下可观的成本。

## 下载与安装 / Download & install

> 一句话：**想做什么，就下哪一类**。每类都提供打包下载；只有极少数技能因为上游没开放许可，需要单独从原仓库获取，下面会标注清楚。

> ⚠️ **国内网络提示**：GitHub 的 release 下载会跳转到 `objects.githubusercontent.com`，这个域名在部分网络下不可达（表现为「页面能打开、下载没反应」）。每个下载链接都附了**镜像**，直连失败时点镜像即可。

### 按用途挑包 / Pick by what you want to do

| 我想做… | 下载 | 包里有什么 |
|---|---|---|
| 写策划书、商业计划书、申报书 | [pack-proposal.zip](https://github.com/xjyloly-prog/codex-skills-catalog/releases/download/v1.1.0/pack-proposal.zip) · [镜像](https://ghproxy.net/https://github.com/xjyloly-prog/codex-skills-catalog/releases/download/v1.1.0/pack-proposal.zip) · 13.0 MB | 策划书与申报材料：11 个技能 |
| 做路演 / 答辩 / 汇报 PPT | [pack-ppt.zip](https://github.com/xjyloly-prog/codex-skills-catalog/releases/download/v1.1.0/pack-ppt.zip) · [镜像](https://ghproxy.net/https://github.com/xjyloly-prog/codex-skills-catalog/releases/download/v1.1.0/pack-ppt.zip) · 24.1 MB | PPT 与路演：5 个技能 |
| 打数学建模比赛（国赛 / 美赛） | [pack-math.zip](https://github.com/xjyloly-prog/codex-skills-catalog/releases/download/v1.1.0/pack-math.zip) · [镜像](https://ghproxy.net/https://github.com/xjyloly-prog/codex-skills-catalog/releases/download/v1.1.0/pack-math.zip) · 1.1 MB | 数学建模：12 个技能 |
| 给产品建模、出渲染图 | [pack-blender.zip](https://github.com/xjyloly-prog/codex-skills-catalog/releases/download/v1.1.0/pack-blender.zip) · [镜像](https://ghproxy.net/https://github.com/xjyloly-prog/codex-skills-catalog/releases/download/v1.1.0/pack-blender.zip) · 0.1 MB | 三维建模 Blender：27 个技能 |
| 画架构图、流程图、数据图表 | [pack-charts.zip](https://github.com/xjyloly-prog/codex-skills-catalog/releases/download/v1.1.0/pack-charts.zip) · [镜像](https://ghproxy.net/https://github.com/xjyloly-prog/codex-skills-catalog/releases/download/v1.1.0/pack-charts.zip) · 2.0 MB | 图表与可视化：2 个技能 |
| 做网页原型、海报、幻灯片模板 | [pack-design.zip](https://github.com/xjyloly-prog/codex-skills-catalog/releases/download/v1.1.0/pack-design.zip) · [镜像](https://ghproxy.net/https://github.com/xjyloly-prog/codex-skills-catalog/releases/download/v1.1.0/pack-design.zip) · 35.0 MB | 网页与设计原型：122 个技能 |
| 写 Word / PDF / PPT / 表格 | 无需下载（Codex 自带） | Word / PDF / PPT / 表格 / LaTeX |

**想要全部？** 下载 [全量包 codex-skills-pack-v1.0.0.zip](https://github.com/xjyloly-prog/codex-skills-catalog/releases/download/v1.0.0/codex-skills-pack-v1.0.0.zip) · [镜像](https://ghproxy.net/https://github.com/xjyloly-prog/codex-skills-catalog/releases/download/v1.0.0/codex-skills-pack-v1.0.0.zip)（179 个技能，75.3 MB）。

### 分类包一览 / Category packs

| 类别 | 技能数 | 打包下载 | 未收录 | 说明 |
|---|---|---|---|---|
| 策划书与申报材料 / Proposals & applications | 11 | [pack-proposal.zip](https://github.com/xjyloly-prog/codex-skills-catalog/releases/download/v1.1.0/pack-proposal.zip) · [镜像](https://ghproxy.net/https://github.com/xjyloly-prog/codex-skills-catalog/releases/download/v1.1.0/pack-proposal.zip) · 13.0 MB | 4 | 4 个因许可证未收录，需从原仓库获取 |
| PPT 与路演 / Presentations | 5 | [pack-ppt.zip](https://github.com/xjyloly-prog/codex-skills-catalog/releases/download/v1.1.0/pack-ppt.zip) · [镜像](https://ghproxy.net/https://github.com/xjyloly-prog/codex-skills-catalog/releases/download/v1.1.0/pack-ppt.zip) · 24.1 MB | 0 | 全部可下载 |
| 数学建模 / Mathematical modeling | 12 | [pack-math.zip](https://github.com/xjyloly-prog/codex-skills-catalog/releases/download/v1.1.0/pack-math.zip) · [镜像](https://ghproxy.net/https://github.com/xjyloly-prog/codex-skills-catalog/releases/download/v1.1.0/pack-math.zip) · 1.1 MB | 36 | 36 个因许可证未收录，需从原仓库获取 |
| 三维建模 Blender / 3D modeling | 27 | [pack-blender.zip](https://github.com/xjyloly-prog/codex-skills-catalog/releases/download/v1.1.0/pack-blender.zip) · [镜像](https://ghproxy.net/https://github.com/xjyloly-prog/codex-skills-catalog/releases/download/v1.1.0/pack-blender.zip) · 0.1 MB | 0 | 全部可下载 |
| 图表与可视化 / Charts & diagrams | 2 | [pack-charts.zip](https://github.com/xjyloly-prog/codex-skills-catalog/releases/download/v1.1.0/pack-charts.zip) · [镜像](https://ghproxy.net/https://github.com/xjyloly-prog/codex-skills-catalog/releases/download/v1.1.0/pack-charts.zip) · 2.0 MB | 1 | 1 个因许可证未收录，需从原仓库获取 |
| 网页与设计原型 / Web & design prototypes | 122 | [pack-design.zip](https://github.com/xjyloly-prog/codex-skills-catalog/releases/download/v1.1.0/pack-design.zip) · [镜像](https://ghproxy.net/https://github.com/xjyloly-prog/codex-skills-catalog/releases/download/v1.1.0/pack-design.zip) · 35.0 MB | 0 | 全部可下载 |
| 文档与办公 / Documents & office | 0 | 无需下载 | 0 | Codex 自带，装了就有 |

### 未收录的怎么办 / When a skill is not in the pack

三类原因，处理方式不同：

| 情况 | 涉及 | 怎么办 |
|---|---|---|
| 上游**没有许可证文件**（法律默认保留所有权利） | 数学建模类的 `bzd-*`、`math-modeling-skill`、`MathModelAgent`；`pandoc-docx-template`；`doc-coauthoring` 等 3 个 | 用 `install.ps1` 从原仓库安装，或点开对应技能那一行的来源链接自行下载 |
| **非商业许可** | `lieflat-charts`（PolyForm Noncommercial 1.0.0） | 可自用，**禁止商业用途** |
| **Codex 自带 / 专有** | Word、PDF、PPT、表格、LaTeX 等 14 个 | 无需下载，装好 Codex 就有 |

> 数模类尤其要注意：`bzd-math-modeling-skills`（16 个）、`math-modeling-skill`（10 个）、`MathModelAgent`（10 个）都没有许可证，所以分类包 `pack-math.zip` 里只有 MIT 许可的 12 个（`mathodology` 8 个 + `AutoMCM-Pro` 4 个）。要装全套请用脚本：

```powershell
.\install.ps1 -Category math      # 从原仓库安装数模类全部 48 个
```

**方式一：一键安装脚本（推荐，覆盖全部 220 个技能）**

```powershell
# 下载本仓库后，在仓库目录里运行
.\install.ps1 -List                                  # 看看有哪些技能
.\install.ps1                                        # 全部安装
.\install.ps1 -Only innovation-proposal,qu-ai-wei    # 只装这几个
.\install.ps1 -Bundle open-design                    # 只装某一套
.\install.ps1 -Dest D:\CodexSkills -Link            # 装到 D 盘并建立目录联接
```

脚本会**从每个技能的原仓库直接下载**再复制到你本机，本仓库不转发文件；网络不通时自动切换镜像重试。

**方式二：离线压缩包（179 个可再分发技能，约 75 MB）**

- 下载地址：[Releases · Codex Skills Pack](https://github.com/xjyloly-prog/codex-skills-catalog/releases/latest)
- 解压后把 `skills/` 里的目录复制到 `%USERPROFILE%\.codex\skills\`
- 只收录许可证允许再分发的部分（MIT / Apache-2.0），各上游许可证原文在 `_licenses/`

**装完之后**：重启 Codex 或新开一个对话即可生效；不需要的技能直接删掉目录。

## 重点技能详解 / Key skills in detail

下表是最常用的 30 个技能：怎么喊它、会产出什么、需要什么依赖。

| 技能 / Skill | 怎么触发 / Trigger | 产出物 / Output | 依赖 / Needs |
|---|---|---|---|
| [`innovation-proposal`](https://github.com/xwu43361-sys/innovation-proposal) | 「帮我写一份挑战杯创业计划书」 | Word 策划书：章节大纲 + 逐章正文 + 待补充素材清单 | 无 |
| [`qu-ai-wei`](https://github.com/LifelongLazyLearner/qu-ai-wei) | 「这段太像 AI 写的，改自然点」 | 改写后的中文，事实与语气不变 | 无 |
| [`pandoc-docx-template`](https://github.com/Achuan-2/pandoc_docx_template) | 「把这份 Markdown 转成规范的中文 Word」 | .docx（可套标题编号与列表缩进模板） | pandoc |
| [`official-document-drafting`](https://github.com/zhaohui-yang/official-document-drafting) | 「写一份××工作实施方案」 | 规范公文 Markdown，可导出机关版式 Word | 无 |
| [`software-copyright-materials`](https://github.com/Fokkyp/SoftwareCopyright-Skill) | 「用这个项目生成软著申请材料」 | 申请表信息、源代码文档、操作手册（Word/TXT） | 技能内置工具链 |
| [`ppt-agent`](https://github.com/sunbigfly/ppt-agent-skills) | 「把这个项目做成路演 PPT」 | HTML 演示文稿（多风格、可导出） | 浏览器 |
| [`consulting-deck`](https://github.com/zairuilab/consulting-deck) | 「做一份评委视角的路演 PPT」 | 原生可编辑 .pptx，结论先行 + 图表核验 | 无 |
| [`ppt-template-fill`](https://github.com/xiongwenhao112/ppt-template-fill) | 「用这个学校模板做 PPT」 | 套用模板版式的可编辑 .pptx | 你提供 .pptx/.potx 模板 |
| [`academic-pptx`](https://github.com/Gabberflast/academic-pptx-skill) | 「做一份答辩 PPT」 | 学术型幻灯片：论证结构 + 引用规范 | 无 |
| [`math-modeling`](https://github.com/XiaoMaColtAI/math-modeling-skill) | 「帮我做这道数模题」 | 题目分析 + 代码 + 结果 + 论文（三角色分工） | Python；TeX 可选 |
| [`auto-mcm`](https://github.com/RealSeaberry/AutoMCM-Pro) | 「用 AutoMCM 跑这道国赛题」 | 全流程产物 + LaTeX 论文，含代码自证 | Python、Git |
| `mathmodel-1start-mathmodel` | 「启动数模全流程」 | plan.md、todo.md，并串联后续六个阶段 | Python |
| [`bzd-problem-translator`](https://github.com/BZDmathclub/bzd-math-modeling-skills) | 「把题面翻译成建模语言」 | 逐句拆解报告 + 跨问关系流程图 | 无 |
| [`bzd-modeling-ideas`](https://github.com/BZDmathclub/bzd-math-modeling-skills) | 「给我几个建模思路对比」 | 逐问模型对比表 + 推荐路线与理由 | 无 |
| [`bzd-review-paper`](https://github.com/BZDmathclub/bzd-math-modeling-skills) | 「按评委标准给我的论文打分」 | HTML 评审报告：逐项评分 + 获奖区间定位 | 论文与题目原件 |
| [`bzd-paper-format-checker`](https://github.com/BZDmathclub/bzd-math-modeling-skills) | 「检查这篇论文的格式合规性」 | 格式审查清单与问题定位 | PDF 或 Word 论文 |
| [`bzd-paper-aigc-auditor`](https://github.com/BZDmathclub/bzd-math-modeling-skills) | 「查一下这篇论文的 AI 痕迹」 | 分层 HTML 审计报告（语言层 + 事实层） | 论文原件 |
| [`科研可视化工具`](https://github.com/XiaoMaColtAI/math-modeling-skill) | 「把这组数据画成论文级图表」 | 出版级图表（PDF/PNG，可矢量） | Python 绘图库 |
| [`双引擎论文搜索`](https://github.com/XiaoMaColtAI/math-modeling-skill) | 「帮我查这个方向的文献」 | 可追溯的文献元数据列表 | 网络访问 |
| [`archify`](https://github.com/tt-a1i/archify) | 「画一张系统架构图」 | 可交互 HTML，并可导出 PNG/SVG/WebM | 浏览器 |
| [`lieflat-charts`](https://github.com/larashero3-dotcom/lieflat-charts) | 「把这组数据做成图表」 | 单文件 HTML 图表或整页报告 | 浏览器（非商业许可） |
| [`svg-design-system`](https://github.com/VioletScar-Hui/Svg-design-system) | 「画一张流程图 / 矩阵图」 | 信息层级清晰的 SVG（10 套配色） | 无 |
| [`blender-design`](https://github.com/full-aigc-plugins/blender-design-plugin) | 「照策划书给头盔建个概念模型」 | .blend 场景 + 里程碑预览图 | Blender（已装） |
| [`blender-hard-surface`](https://github.com/full-aigc-plugins/blender-design-plugin) | 「做头盔外壳的硬表面建模」 | 可编辑网格、可导出 GLB/FBX | Blender |
| [`blender-render-compositing`](https://github.com/full-aigc-plugins/blender-design-plugin) | 「出一张产品渲染图」 | PNG/EXR 渲染图，含通道与色彩管理 | Blender |
| [`blender-preview`](https://github.com/full-aigc-plugins/blender-design-plugin) | 「给我看看现在的四个角度」 | 相机/正视/侧视/顶视预览图 | Blender |
| [`frontend-design`](https://github.com/anthropics/skills) | 「给我的原型定个视觉方向」 | 字体、配色与排版建议 | 无 |
| [`web-artifacts-builder`](https://github.com/anthropics/skills) | 「做一个可交互的演示原型页」 | React/Tailwind 多组件原型 | Node.js |
| [`doc-coauthoring`](https://github.com/anthropics/skills) | 「陪我把这份方案写出来」 | 分节打磨的文档 + 读者盲测反馈 | 无 |
| `latex:latex-compile` | 「编译这份 LaTeX」 | PDF（简单项目走内置 Tectonic，复杂项目走 MiKTeX） | Tectonic / MiKTeX |

## 目录 / Contents

1. [竞赛策划与申报 / Competition proposals](#1-竞赛策划与申报--competition-proposals) — 15 个
2. [演示与路演 / Presentations](#2-演示与路演--presentations) — 5 个
3. [数学建模 / Mathematical modeling](#3-数学建模--mathematical-modeling) — 48 个
4. [三维建模 / 3D modeling (Blender)](#4-三维建模--3d-modeling-blender) — 60 个
5. [图表与可视化 / Charts & diagrams](#5-图表与可视化--charts--diagrams) — 3 个
6. [网页与设计原型 / Web & design prototypes](#6-网页与设计原型--web--design-prototypes) — 122 个
7. [文档与办公 / Documents & office](#7-文档与办公--documents--office) — 10 个

另外包含：[Agents 角色分工](#agents-角色分工--agent-roles) · [依赖清单](#依赖清单--dependencies) · [来源与许可](#来源与许可--sources--licenses) · [免责声明](#免责声明--disclaimer)

## 1. 竞赛策划与申报 / Competition proposals

写策划书、商业计划书、申报书、软著材料，以及配套的 Word 排版与网页原型。

**📦 打包下载：[pack-proposal.zip](https://github.com/xjyloly-prog/codex-skills-catalog/releases/download/v1.1.0/pack-proposal.zip) · [镜像](https://ghproxy.net/https://github.com/xjyloly-prog/codex-skills-catalog/releases/download/v1.1.0/pack-proposal.zip)**（13.0 MB，含 11 个技能；另有 4 个因许可证未收录，见表格来源链接）

> 按需启用：默认**不挂载**，需要时挂上并新开对话。

| 技能 / Skill | 中文说明 | English | 来源 / Source |
|---|---|---|---|
| `doc-coauthoring` | 长文档协作写作流程：收集上下文 → 逐节打磨 → 用无上下文读者盲测。 | Guide users through a structured workflow for co-authoring documentation. | [anthropics/skills](https://github.com/anthropics/skills) · 见仓库 |
| `frontend-design` | 界面视觉方向指导：字体、排版与审美取向，避免模板化的默认样式。 | Guidance for distinctive, intentional visual design when building new UI or reshaping an existing one. | [anthropics/skills](https://github.com/anthropics/skills) · Apache-2.0 |
| `innovation-proposal` | 创新创业大赛策划书写作：内置 2026 互联网+ 官方评审规则、16 章大纲、逐章写法与质量清单。 | 为各类大学生/青年创新创业大赛撰写符合评审标准的项目策划书、商业计划书、项目计划书或申报书。内置中国国际大学生创新大赛（原"互联网+"）2026官方评审规则全文，并适配"挑战杯"创业计划竞赛、"创青春"、三创赛、服务外包、大创计划（国创）、iCAN及各类省赛校赛。当用户提到大创赛、互联网+、挑战杯… | [xwu43361-sys/innovation-proposal](https://github.com/xwu43361-sys/innovation-proposal) · MIT |
| `doc-type-routing` | 公文文种判定：按行文方向、目的、是否需回应三个维度选对文种。 | 在起草前判定「该用哪个文种、什么行文方向」。Use when 不确定该写通知/报告/请示/函/通报/意见/决定…，或需要判断上行/下行/平行/公开、要不要对方回复。按「行文方向＋目的＋是否需回应」三维收敛到正确文种，再交给「公文写作」起草。是流程第一步的判定脚手架，不生成正文。 | [zhaohui-yang/official-document-drafting](https://github.com/zhaohui-yang/official-document-drafting) · MIT |
| `document-qa` | 公文成稿质检：章节完整性、标题层级、篇幅匹配度、文种与结尾用语是否规范。 | 对已成稿的中文公文做结构与质量校验。Use when the user wants to check/review/lint a 公文 draft——校验章节是否齐全、标题层级是否跳级或混编、篇幅与标题深度是否匹配、一是/二是 是否被误用为正式标题、文种是否用对、结尾用语是否匹配、有无未经提供的事… | [zhaohui-yang/official-document-drafting](https://github.com/zhaohui-yang/official-document-drafting) · MIT |
| `docx-export` | 公文 Markdown 导出为机关版式 Word：字体、字号、页边距、行距、页码、附件排版。 | 把中文公文 Markdown 成稿导出为符合机关版式的 .docx。Use when the user wants to export/convert a 公文 Markdown draft to Word/.docx, adjust 字体、字号、页边距、行距、页码、标题断行, embed loc… | [zhaohui-yang/official-document-drafting](https://github.com/zhaohui-yang/official-document-drafting) · MIT |
| `ministry-news-daily` | 部委动态日报：采集中央部委官网最新动态，核实后按《报告》文种成稿。 | 浏览中央国家部委官网的最新动态，汇总成一份每日《报告》，用于快速了解国家大事与各部委政策要求。Use when the user wants 部委/政府每日动态、政务新闻日报、了解国家大事、各部委最新政策与要求的汇总报告。采集→核实→按「报告」文种成稿，可导出 Word。文体固定为报告。 | [zhaohui-yang/official-document-drafting](https://github.com/zhaohui-yang/official-document-drafting) · MIT |
| `official-document-drafting` | 中文公文起草与改写：决议、通知、报告、请示、纪要等文种，含结构规范与 Word 导出。 | 起草、改写、润色、扩写、压缩、规范并导出中文公文与行政正式文本。Use when the user asks to write, revise, summarize, standardize, or convert 公文、决议、决定、命令、公告、公报、通告、意见、通知、通报、报告、请示、批复、议案… | [zhaohui-yang/official-document-drafting](https://github.com/zhaohui-yang/official-document-drafting) · MIT |
| `offline-prompt-packager` | 把技能打包成断网可用的离线提示词包，适配离线 WebUI。 | 把基于 prompts/ 主源的 skill 打包成断网单机可用的离线提示词包。Use when the user wants to export/package offline prompts for disconnected hosts (WebUI、Qwen、AnythingLLM、Clau… | [zhaohui-yang/official-document-drafting](https://github.com/zhaohui-yang/official-document-drafting) · MIT |
| `policy-keyword-tracker` | 政策专题跟踪：围绕关键词汇总各部委政策口径，按《情况专报》成稿。 | 围绕一个关键词/主题（如「创新药」「低空经济」「数据要素」）检索各中央国家部委的相关政策、措施与动态，汇总成一份《情况专报》。Use when 用户想跟踪某一主题在各部委的政策口径、做专题政策梳理与研判。采集→核实→按「情况专报」文种成稿，可导出 Word。文体固定为情况专报。 | [zhaohui-yang/official-document-drafting](https://github.com/zhaohui-yang/official-document-drafting) · MIT |
| `skill-build` | 公文技能包的自构建流程：从单一提示词源生成并校验 SKILL.md 产物。 | 从 prompts/ 单一主源生成并校验本项目的 skill 产物。Use when working on 构建/重新生成 SKILL.md、agent 接口、dist 副本、assets/templates/ 模板或离线提示词，校验产物是否与 prompts/ 主源同步（--check / 防漂… | [zhaohui-yang/official-document-drafting](https://github.com/zhaohui-yang/official-document-drafting) · MIT |
| `pandoc-docx-template` | Markdown 转规范中文 Word：内置多种标题编号、列表缩进与论文模板，可反向转回 Markdown。 | Use this skill when converting Markdown to Word DOCX or DOCX back to Markdown with Pandoc, especially when the output should use the bundled Chinese… | [Achuan-2/pandoc_docx_template](https://github.com/Achuan-2/pandoc_docx_template) · 见仓库 |
| `qu-ai-wei` | 中文去 AI 味：在保持事实与语气的前提下重写，降低 AIGC 检测特征。 | Rewrite and humanize Simplified Chinese while preserving facts, meaning, evidence strength, register, and authorial voice. | [LifelongLazyLearner/qu-ai-wei](https://github.com/LifelongLazyLearner/qu-ai-wei) · MIT |
| `software-copyright-materials` | 软著申请材料生成：从真实项目代码产出申请表、源代码文档、操作手册与 Word/TXT。 | Generate guided Chinese software copyright application materials from a real project. | [Fokkyp/SoftwareCopyright-Skill](https://github.com/Fokkyp/SoftwareCopyright-Skill) · 见仓库 |
| `web-artifacts-builder` | 复杂可交互网页原型构建：React、Tailwind、shadcn/ui 多组件工程。 | Suite of tools for creating elaborate, multi-component claude.ai HTML artifacts using modern frontend web technologies (React, Tailwind CSS, shadcn/u… | [anthropics/skills](https://github.com/anthropics/skills) · Apache-2.0 |

## 2. 演示与路演 / Presentations

路演、答辩、汇报用的 PPT：HTML 演示、可编辑 PPTX、模板套用。

**📦 打包下载：[pack-ppt.zip](https://github.com/xjyloly-prog/codex-skills-catalog/releases/download/v1.1.0/pack-ppt.zip) · [镜像](https://ghproxy.net/https://github.com/xjyloly-prog/codex-skills-catalog/releases/download/v1.1.0/pack-ppt.zip)**（24.1 MB，含 5 个技能）

> 按需启用：默认**不挂载**，需要时挂上并新开对话。

| 技能 / Skill | 中文说明 | English | 来源 / Source |
|---|---|---|---|
| `academic-pptx` | 学术型演示：答辩、研讨会、开题与结题的论证结构与引用规范。 | Use this skill whenever the user wants to create or improve a presentation for an academic context — | [Gabberflast/academic-pptx-skill](https://github.com/Gabberflast/academic-pptx-skill) · MIT |
| `consulting-deck` | 咨询风格路演 PPT：结论先行、图表带数据核验、逐页质检，输出原生可编辑 PPTX。 | Create, revise, and audit executive-ready strategy-consulting presentations as native, editable PowerPoint files. | [zairuilab/consulting-deck](https://github.com/zairuilab/consulting-deck) · Apache-2.0 |
| `ppt-agent-alt` | PPT 全流程生成（Akxan 版，因与 sunbigfly 版重名而改名）。 | 专业 PPT 演示文稿全流程 AI 生成助手。模拟顶级 PPT 设计公司的完整工作流（需求调研 -> 资料搜集 -> 大纲策划 -> 策划稿 -> 设计稿），输出高质量 HTML 格式演示文稿。当用户提到制作 PPT、做演示文稿、做 slides、做幻灯片、做汇报材料、做培训课件、做路演 deck… | [Akxan/ppt-agent-skill](https://github.com/Akxan/ppt-agent-skill) · MIT |
| `ppt-agent` | PPT 全流程生成：需求调研 → 资料搜集 → 大纲 → 策划稿 → 设计稿，输出 HTML 演示文稿。 | 专业 PPT 演示文稿全流程 AI 生成助手。模拟顶级 PPT 设计公司的完整工作流（需求调研到资料搜集到大纲策划到策划稿到设计稿），输出高质量 HTML 格式演示文稿。当用户提到制作 PPT、做演示文稿、做 slides、做幻灯片、做汇报材料、做培训课件、做路演 deck、做产品介绍页面时触发此… | [sunbigfly/ppt-agent-skills](https://github.com/sunbigfly/ppt-agent-skills) · MIT |
| `ppt-template-fill` | 按指定 PPT 模板填充内容，完整保留原版式、字体与配色，输出可编辑 PPTX。 | 基于用户提供的 PPT 模板制作演示文稿时使用。解析任意 .pptx/.potx 模板(含无占位符的自由文本框模板)每页的可填充槽位，克隆模板页并在完整保留原版式、字体、配色的前提下填入新内容，输出与模板视觉一致的原生可编辑 PPTX。触发语如：用这个模板做 PPT、按公司模板生成、套模板写 PP… | [xiongwenhao112/ppt-template-fill](https://github.com/xiongwenhao112/ppt-template-fill) · MIT |

## 3. 数学建模 / Mathematical modeling

从读题、建模、编程、作图到论文撰写与模拟评审的完整链条。

**📦 打包下载：[pack-math.zip](https://github.com/xjyloly-prog/codex-skills-catalog/releases/download/v1.1.0/pack-math.zip) · [镜像](https://ghproxy.net/https://github.com/xjyloly-prog/codex-skills-catalog/releases/download/v1.1.0/pack-math.zip)**（1.1 MB，含 12 个技能；另有 36 个因许可证未收录，见表格来源链接）

> 按需启用：默认**不挂载**，需要时挂上并新开对话。

| 技能 / Skill | 中文说明 | English | 来源 / Source |
|---|---|---|---|
| `auto-mcm` | AutoMCM-Pro 全流程：AI 主导或人工主导双模式，强制 GitOps 检查点与代码自证。 | AutoMCM-Pro industrial-grade math modeling agent (Codex CLI binding). | [RealSeaberry/AutoMCM-Pro](https://github.com/RealSeaberry/AutoMCM-Pro) · MIT |
| `cumcm-master` | AutoMCM 国赛专用全自动建模智能体。 | Full-stack autonomous math modeling agent for CUMCM (全国大学生数学建模竞赛). | [RealSeaberry/AutoMCM-Pro](https://github.com/RealSeaberry/AutoMCM-Pro) · MIT |
| `draw-image` | 用图像模型生成示意图、流程图与概念插画。 | Generate diagrams, flowcharts, and conceptual illustrations using OpenAI gpt-image-2 (default) or gpt-image-1. | [RealSeaberry/AutoMCM-Pro](https://github.com/RealSeaberry/AutoMCM-Pro) · MIT |
| `mcm-master` | AutoMCM 美赛（MCM/ICM）专用全自动建模智能体。 | Full-stack autonomous math modeling agent for MCM/ICM (美国大学生数学建模竞赛). | [RealSeaberry/AutoMCM-Pro](https://github.com/RealSeaberry/AutoMCM-Pro) · MIT |
| `1start-mathmodel` | MathModelAgent 六阶段流水线入口：生成计划与待办，串联后续各阶段技能。 | 数学建模竞赛工作流入口。用于启动完整建模流程：询问用户偏好，生成 plan.md 和 todo.md，并按阶段调用赛题分析、建模、代码与图表、流程图、论文撰写、验证验收等 skills。 | [jihe520/MathModelAgent](https://github.com/jihe520/MathModelAgent) · 见仓库 |
| `2analysis-modeling` | 赛题分析与建模设计：子问题拆解、假设预检、变量与公式、求解策略。 | 数学建模赛题分析与建模设计合并阶段。用于读取题面和附件，完成子问题拆解、数据理解、假设预检、变量定义、模型公式、目标函数、约束条件、求解策略和可交给代码实现的建模报告。 | [jihe520/MathModelAgent](https://github.com/jihe520/MathModelAgent) · 见仓库 |
| `3coding-visual` | 编程实现与图表生成：可复现代码、约束验证、结果报告与论文可用图表。 | 数学建模编程实现与数据图表生成阶段。根据 ANALYSIS_MODELING_REPORT.md 编写可复现代码、运行求解、验证约束、输出 RESULTS_REPORT.md 并生成论文可用的数据驱动图表 PDF。 | [jihe520/MathModelAgent](https://github.com/jihe520/MathModelAgent) · 见仓库 |
| `4drawio` | 非数据型图示绘制：技术路线图、求解流程图、模型结构图，导出论文可引用 PDF。 | 数学建模非数据型图示绘制阶段。根据 ANALYSIS_MODELING_REPORT.md、RESULTS_REPORT.md 和已有 figures/ 生成技术路线图、子问题求解流程图、模型结构图、数据处理流程图等 DrawIO 图，并导出论文可引用 PDF。 | [jihe520/MathModelAgent](https://github.com/jihe520/MathModelAgent) · 见仓库 |
| `5writing` | 论文撰写：支持 Typst 与 LaTeX 双引擎，按比赛模板组织章节并插入图表。 | 数学建模竞赛论文撰写阶段，支持 Typst 和 LaTeX 双引擎。根据 ANALYSIS_MODELING_REPORT.md、RESULTS_REPORT.md 和 figures/*.pdf 选择比赛模板、排版引擎、组织章节，并在论文正文中按章节直接插入图表。 | [jihe520/MathModelAgent](https://github.com/jihe520/MathModelAgent) · 见仓库 |
| `6verity` | 论文终检：章节顺序、图表引用、数值一致性、占位符、参考文献与编译就绪度。 | 数学建模竞赛最终验证和验收阶段，支持 Typst 和 LaTeX 双引擎。用于论文写完后检查章节数量、标题顺序、图表引用、数值一致性、占位符、内部文件泄露、参考文献、代码可复现性、编译和提交就绪状态。 | [jihe520/MathModelAgent](https://github.com/jihe520/MathModelAgent) · 见仓库 |
| `_references` | 数模共享知识库：写作规范、题型防错速查与图表规范的参考文档。 | 共享规范知识库。包含数学建模竞赛的写作规范、题型防错速查、图表规范等参考内容。其他 skills 在执行过程中按需读取，无需单独触发。 | [jihe520/MathModelAgent](https://github.com/jihe520/MathModelAgent) · 见仓库 |
| `doctor` | 数模环境体检：检查工作流所需的全部依赖，给出并执行安装命令。 | 环境检查与安装向导。检查数学建模工作流所需的全部依赖是否已安装，对缺失项提供安装命令，并在用户确认后执行安装。手动触发。 | [jihe520/MathModelAgent](https://github.com/jihe520/MathModelAgent) · 见仓库 |
| `mathmodel-figure-templates` | 科研绘图模板库：SHAP 蜂群图、ROC、泰勒图、热图、和弦图等可直接运行的脚本。 | Use this skill in the MathModel LaTeX sandbox when the user asks to reproduce built-in scientific visualization templates, especially prompts from th… | [jihe520/MathModelAgent](https://github.com/jihe520/MathModelAgent) · 见仓库 |
| `typst-author` | Typst 排版：语法、模板、调试与文档工程。 | Generate idiomatic Typst (.typ) code, edit and troubleshoot Typst documents and projects, and answer Typst syntax/reference questions. | [jihe520/MathModelAgent](https://github.com/jihe520/MathModelAgent) · 见仓库 |
| `bzd-abstract-checker` | 检查中文摘要：写作缺陷诊断与修改优先级。 | Review a user-provided Chinese mathematical-modeling abstract without requiring the problem statement or full paper, identify concrete writing defect… | [BZDmathclub/bzd-math-modeling-skills](https://github.com/BZDmathclub/bzd-math-modeling-skills) · 见仓库 |
| `bzd-ai-usage-disclosure` | 生成或核查 AI 工具使用声明与匿名版使用详情 PDF。 | Generate or review mathematical-modeling competition AI tool usage statements and the anonymous AI工具使用详情.pdf. | [BZDmathclub/bzd-math-modeling-skills](https://github.com/BZDmathclub/bzd-math-modeling-skills) · 见仓库 |
| `bzd-cumcm-school-awards` | 查询国赛学校获奖数据（2021-2025）与 2026 预测，评估冲奖距离。 | Query 2021-2025 CUMCM school awards and 2026 forecasts, or assess a student's preparation distance from provincial and national awards using school h… | [BZDmathclub/bzd-math-modeling-skills](https://github.com/BZDmathclub/bzd-math-modeling-skills) · 见仓库 |
| `bzd-model-assumption-checker` | 检查「模型假设」：是否必要、有依据、与题目相容、可被后续模型使用。 | Review a mathematical-modeling paper's model-assumption section against the complete problem statement. | [BZDmathclub/bzd-math-modeling-skills](https://github.com/BZDmathclub/bzd-math-modeling-skills) · 见仓库 |
| `bzd-model-dictionary` | 模型词典查询：适用条件、输入输出、局限与验证方式，并判断是否适配当前题目。 | Query the bundled BZD mathematical-modeling dictionary for a user-selected model, explain its assumptions, inputs, outputs, limitations and validatio… | [BZDmathclub/bzd-math-modeling-skills](https://github.com/BZDmathclub/bzd-math-modeling-skills) · 见仓库 |
| `bzd-model-solution-checker` | 检查「模型建立与求解」：数值解、结果分析、验证与灵敏度。 | Review the model establishment, numerical solution, result analysis, model validation, and sensitivity or robustness sections of a mathematical-model… | [BZDmathclub/bzd-math-modeling-skills](https://github.com/BZDmathclub/bzd-math-modeling-skills) · 见仓库 |
| `bzd-modeling-ideas` | 整篇建模思路：逐问对比可行模型、给出选型理由与创新点。 | Generate a coherent, whole-paper mathematical modeling solution framework from a complete contest problem. | [BZDmathclub/bzd-math-modeling-skills](https://github.com/BZDmathclub/bzd-math-modeling-skills) · 见仓库 |
| `bzd-modeling-workflow` | BZD 数模总控：在读懂题、出思路、选模型、写论文、自查、评审之间编排下一步。 | Orchestrate the BZD mathematical-modeling Skills across problem reading, idea generation, model selection, paper drafting, section checks, final form… | [BZDmathclub/bzd-math-modeling-skills](https://github.com/BZDmathclub/bzd-math-modeling-skills) · 见仓库 |
| `bzd-paper-aigc-auditor` | 论文 AI 痕迹两层审计：语言层九维检测 + 模型合理性深度审查，输出分层 HTML 报告。 | 对数学建模竞赛论文进行两层AI痕迹审计——第一层9维检测(语言层面60%：连接词/排比/拔高词/被动句/段落规律/文本复杂度；事实层面40%：引文验证/数值一致性/术语一致性)，第二层模型合理性深度审查。严格判分+一票否决+问题标红。输出分层HTML报告。 | [BZDmathclub/bzd-math-modeling-skills](https://github.com/BZDmathclub/bzd-math-modeling-skills) · 见仓库 |
| `bzd-paper-format-checker` | 整篇格式合规审查：摘要可读性、页面结构、排版、图表、公式与匿名性。 | Review a complete mathematical-modeling competition paper with an atomic checklist covering abstract readability, page structure, typography, heading… | [BZDmathclub/bzd-math-modeling-skills](https://github.com/BZDmathclub/bzd-math-modeling-skills) · 见仓库 |
| `bzd-problem-analysis-checker` | 检查「问题分析」章节：任务分类、数据推理、跨问关联与建模框架。 | Review a Chinese mathematical-modeling problem-analysis section against the original problem, checking task classification, data reasoning, cross-pro… | [BZDmathclub/bzd-math-modeling-skills](https://github.com/BZDmathclub/bzd-math-modeling-skills) · 见仓库 |
| `bzd-problem-restatement` | 生成合规的「问题重述」章节，或按原题检查已写内容。 | Generate a compliant Chinese mathematical-modeling problem-restatement chapter from a complete problem statement, or review a user's restatement agai… | [BZDmathclub/bzd-math-modeling-skills](https://github.com/BZDmathclub/bzd-math-modeling-skills) · 见仓库 |
| `bzd-problem-translator` | 赛题逐句翻译成建模语言：暴露隐藏约束、画跨问流程图、查漏补缺。 | Translate a complete mathematical modeling contest problem sentence by sentence into precise modeling language, preserve every substantive condition… | [BZDmathclub/bzd-math-modeling-skills](https://github.com/BZDmathclub/bzd-math-modeling-skills) · 见仓库 |
| `bzd-reference-appendix-checker` | 检查「参考文献与附录」：引用、篇幅、代码、可复现性与匿名性。 | Check a mathematical-modeling paper's in-text citations, bibliography, appendix length and content, code, supporting files, reproducibility, consiste… | [BZDmathclub/bzd-math-modeling-skills](https://github.com/BZDmathclub/bzd-math-modeling-skills) · 见仓库 |
| `bzd-review-paper` | 模拟评委打分：逐项评分、低分保护、按题型与赛区做获奖定位，输出中文 HTML 评审报告。 | Review mathematical modeling competition papers from a complete problem and paper, with an optional strict bzd-paper-format-checker audit, itemized p… | [BZDmathclub/bzd-math-modeling-skills](https://github.com/BZDmathclub/bzd-math-modeling-skills) · 见仓库 |
| `bzd-symbol-notation-checker` | 检查「符号说明」：覆盖率、单位、重载、大小写与下标一致性。 | Review the symbol-notation section of a mathematical-modeling paper against the full paper. | [BZDmathclub/bzd-math-modeling-skills](https://github.com/BZDmathclub/bzd-math-modeling-skills) · 见仓库 |
| `DOCX工具` | 数学建模 Word 工具：论文模板、原生公式、三线表，也可把完整 LaTeX 论文转成 DOCX。 | 创建、编辑、校验和转换 Word DOCX，支持把完整 LaTeX 论文转换为 DOCX，以及数学建模论文模板、原生公式、三线表、修订和批注。 | [XiaoMaColtAI/math-modeling-skill](https://github.com/XiaoMaColtAI/math-modeling-skill) · 见仓库 |
| `Excel工具` | 数学建模 Excel 工具：读取、创建、修改与验证表格，支持保留模板与公式重算。 | 读取、创建、修改和验证 XLSX，支持模板保留、公式重算和错误检查。 | [XiaoMaColtAI/math-modeling-skill](https://github.com/XiaoMaColtAI/math-modeling-skill) · 见仓库 |
| `LaTeX工具` | 数学建模 LaTeX 工具：按官方或内置模板创建、编译与校验论文工程。 | 从官方或内置模板创建、编译和校验数学建模 LaTeX 论文项目，并可配合 DOCX 工具把完整 LaTeX 论文转换为 Word。 | [XiaoMaColtAI/math-modeling-skill](https://github.com/XiaoMaColtAI/math-modeling-skill) · 见仓库 |
| `math-modeling` | 数模总入口：三阶段流程（建模分析 → 编程求解 → 论文撰写），含建模手/编程手/论文手角色分工。 | 当用户要求数学建模、建模竞赛、建模分析、代码求解、结果可视化或生成数学建模论文时使用。支持完整三阶段流程、单独执行任一角色，以及在关键节点使用独立 Subagent 进行阶段内质检；默认只启用质检 Subagent，用户可明确选择额外协作。 | [XiaoMaColtAI/math-modeling-skill](https://github.com/XiaoMaColtAI/math-modeling-skill) · 见仓库 |
| `pdf` | PDF 全能处理：文本与表格提取、合并拆分、水印、表单填写、加密解密与 OCR。 | Use this skill whenever the user wants to do anything with PDF files. | [XiaoMaColtAI/math-modeling-skill](https://github.com/XiaoMaColtAI/math-modeling-skill) · 见仓库 |
| `双引擎论文搜索` | 文献检索：OpenAlex 与 AnySearch 双源并行搜索并输出可追溯元数据。 | 使用 OpenAlex 与 AnySearch 两个真实数据源并行搜索、交叉匹配和输出可追溯论文元数据。 | [XiaoMaColtAI/math-modeling-skill](https://github.com/XiaoMaColtAI/math-modeling-skill) · 见仓库 |
| `建模手` | 数模角色：题目理解、模型选择与算法设计，输出题目分析报告。 | 数学建模的题目理解、模型选择和算法设计阶段。输出题目分析报告与术语表格。 | [XiaoMaColtAI/math-modeling-skill](https://github.com/XiaoMaColtAI/math-modeling-skill) · 见仓库 |
| `科研可视化工具` | 出版级科研配图全流程：数据剖析、选图决策、绘制自检与多格式导出。 | 从数据剖析到出版级成图的完整可视化工具。先做数据剖析（列类型/样本量/分布/异常值/分组结构/相关性）， 再结合论证目标推荐图型，主动拦截科研画图经典错误，产出 Nature / Science / IEEE / Elsevier / PNAS / 中文核心期刊级别的成图。覆盖数据 EDA、图表契… | [XiaoMaColtAI/math-modeling-skill](https://github.com/XiaoMaColtAI/math-modeling-skill) · 见仓库 |
| `编程手` | 数模角色：Python 或 MATLAB 实现、求解、表格与可视化输出、结果复现。 | 数学建模的 Python 或 MATLAB 实现、运行、表格输出、可视化和复现阶段。 | [XiaoMaColtAI/math-modeling-skill](https://github.com/XiaoMaColtAI/math-modeling-skill) · 见仓库 |
| `论文手` | 数模角色：依据题目与真实代码结果撰写完整 Word 论文，可选 LaTeX。 | 根据题目、建模分析和真实代码结果生成完整 Word 数学建模论文，用户显式要求时同时生成 LaTeX 论文。 | [XiaoMaColtAI/math-modeling-skill](https://github.com/XiaoMaColtAI/math-modeling-skill) · 见仓库 |
| `mathodology-agent-pipeline` | 规划建模方案、决定下一步动作或向专家角色交办。 | Use when planning a modeling solution, selecting the next useful step or briefing a specialist. | [sweetcornna/mathodology](https://github.com/sweetcornna/mathodology) · MIT |
| `mathodology-award-gates` | 评审数学有效性、证据、可复现性、图表与投稿草稿。 | Use when reviewing mathematical validity, evidence, reproducibility, figures or a submission draft. | [sweetcornna/mathodology](https://github.com/sweetcornna/mathodology) · MIT |
| `mathodology-dev-test-release` | 检查技能元数据、引用与仓库边界，或准备发布。 | Use when checking skill metadata, references or repository boundaries, or preparing an explicitly requested skills release. | [sweetcornna/mathodology](https://github.com/sweetcornna/mathodology) · MIT |
| `mathodology-evidence-search` | 查找文献、数据集、领域事实、引用信息与可授权图表。 | Use when finding literature, datasets, domain facts, citation details or licensed figure references. | [sweetcornna/mathodology](https://github.com/sweetcornna/mathodology) · MIT |
| `mathodology-figure-presets` | 科研配图选型、设计与评审；含复杂建模图表与插画。 | Use when selecting, designing, generating or reviewing scientific figures, complex modeling charts, paper illustrations or image2-assisted visuals. | [sweetcornna/mathodology](https://github.com/sweetcornna/mathodology) · MIT |
| `mathodology-project-orientation` | 维护纯技能仓库，判断某项改动是否属于本仓库。 | Use when maintaining the skills-only repository or checking whether a change belongs here. | [sweetcornna/mathodology](https://github.com/sweetcornna/mathodology) · MIT |
| `mathodology-skill-authoring` | 新增、修改或评审技能、角色提示词与元数据。 | Use when adding, editing or reviewing skills, role prompts or skill metadata. | [sweetcornna/mathodology](https://github.com/sweetcornna/mathodology) · MIT |
| `mathodology-whole-project` | 数模项目起点：安装、备份与维护整套技能包。 | Use when starting a modeling task or installing, backing up or maintaining the skills pack. | [sweetcornna/mathodology](https://github.com/sweetcornna/mathodology) · MIT |

## 4. 三维建模 / 3D modeling (Blender)

产品外观建模、材质渲染、动画与导出。需要时启用，用完关掉。

**说明**：下表包含两套内容重叠的版本——`blender-design` 是**插件版（33 个，当前使用）**，`blender-skills` 是**独立技能包（27 个，备用）**。实际写进目录的是插件版，独立包作为离线备份保留。

**📦 打包下载：[pack-blender.zip](https://github.com/xjyloly-prog/codex-skills-catalog/releases/download/v1.1.0/pack-blender.zip) · [镜像](https://ghproxy.net/https://github.com/xjyloly-prog/codex-skills-catalog/releases/download/v1.1.0/pack-blender.zip)**（0.1 MB，含 27 个技能）

> Blender 相关：默认**已关闭**，要做三维建模时再启用。

| 技能 / Skill | 中文说明 | English | 来源 / Source |
|---|---|---|---|
| `blender-asset-library` | 从 PolyHaven 等 CC0 资产库取材：搜索资产、下载 HDRI 环境与 PBR 材质。 | 从 PolyHaven 等 CC0 资产库为 Blender 场景取材：搜索资产、按体积纪律经 asset.fetch_url 下载、应用 HDRI 环境与 PBR 材质；用户要 HDRI、环境贴图、贴图材质、低模道具或提到 PolyHaven 时使用。 | [full-aigc-plugins/blender-design-plugin](https://github.com/full-aigc-plugins/blender-design-plugin) · Apache-2.0 |
| `blender-background-jobs` | 后台任务：批量渲染、帧序列导出、视频合成与仿真烘焙，不阻塞前台。 | Run snapshot-isolated Blender exports, durable animation frame sequences, explicit frame recovery, verified video composition, still renders, and sim… | [full-aigc-plugins/blender-design-plugin](https://github.com/full-aigc-plugins/blender-design-plugin) · Apache-2.0 |
| `blender-character-animation` | 角色动画：时间控制、IK、约束与动作连续性校验。 | Animate a registered Blender character rig and a single interactive prop with editable timing, IK controls, constraints, and continuity checks. | [full-aigc-plugins/blender-design-plugin](https://github.com/full-aigc-plugins/blender-design-plugin) · Apache-2.0 |
| `blender-character-rigging` | 骨骼绑定：骨架、蒙皮权重、IK 控制与关节限制。 | Build and inspect editable Blender armatures, skin weights, IK controls, pole targets, joint limits, and prop constraints for character work. | [full-aigc-plugins/blender-design-plugin](https://github.com/full-aigc-plugins/blender-design-plugin) · Apache-2.0 |
| `blender-cinematography` | 摄影机设计：镜头、朝向、路径运动、对焦与构图。 | Design and validate Blender cameras, lenses, subject aiming, path motion, focus, framing, and controlled handheld response. | [full-aigc-plugins/blender-design-plugin](https://github.com/full-aigc-plugins/blender-design-plugin) · Apache-2.0 |
| `blender-connector` | 连接已打开的 Blender 窗口（Connector 模式）。 | Connect Codex to an already-open Blender window through the pinned PartMe Blender MCP Add-on. | [full-aigc-plugins/blender-design-plugin](https://github.com/full-aigc-plugins/blender-design-plugin) · Apache-2.0 |
| `blender-curves` | 曲线建模：路径、剖面、线缆与轨道等曲线驱动道具。 | Build editable Blender paths, profiles, cables, rails, or curve-driven props using registered curve commands. | [full-aigc-plugins/blender-design-plugin](https://github.com/full-aigc-plugins/blender-design-plugin) · Apache-2.0 |
| `blender-design` | 设计总入口：从一句想法到场景，含建模、材质、灯光、相机与动画。 | Turn a user's idea into a Blender scene through milestone-based modeling, materials, lighting, camera, and animation commands. | [full-aigc-plugins/blender-design-plugin](https://github.com/full-aigc-plugins/blender-design-plugin) · Apache-2.0 |
| `blender-export` | 导出并验证：模型、图片、视频、EXR、USD、Alembic 多格式产物。 | Export an approved Blender snapshot to verified model, image, video, EXR, USD, or Alembic artifacts using compatible receipt contracts. | [full-aigc-plugins/blender-design-plugin](https://github.com/full-aigc-plugins/blender-design-plugin) · Apache-2.0 |
| `blender-grease-pencil` | 蜡笔工具：2D 图层、材质、逐帧绘制与 2D/3D 混排。 | Create editable Blender Grease Pencil layers, materials, frame drawings, and mixed 2D/3D scenes with structured stroke data. | [full-aigc-plugins/blender-design-plugin](https://github.com/full-aigc-plugins/blender-design-plugin) · Apache-2.0 |
| `blender-hair` | 头发曲线：按表面点生成与检查发丝。 | Create and inspect native Blender Hair Curves from explicit surface-local strand points, radii, and bound source surfaces. | [full-aigc-plugins/blender-design-plugin](https://github.com/full-aigc-plugins/blender-design-plugin) · Apache-2.0 |
| `blender-hard-surface` | 硬表面建模：产品、机械与道具外形，配合修改器保持可编辑。 | Create editable hard-surface, product, mechanical, or prop geometry with registered Blender mesh, modifier, collection, and recipe commands. | [full-aigc-plugins/blender-design-plugin](https://github.com/full-aigc-plugins/blender-design-plugin) · Apache-2.0 |
| `blender-harness` | Harness 会话与 JSON 命令通道：所有 Blender 操作的唯一入口。 | Launch a managed Blender harness session and dispatch structured JSON commands through harness_cli.py. | [full-aigc-plugins/blender-design-plugin](https://github.com/full-aigc-plugins/blender-design-plugin) · Apache-2.0 |
| `blender-harness-driving` | 从命令行驱动 Harness：启动会话、派发命令、核验回执与导出产物。 | Drive the Blender Design Harness from a shell client: launch a session, dispatch the closed request contract, keep the sceneRevision chain coherent,… | [full-aigc-plugins/blender-design-plugin](https://github.com/full-aigc-plugins/blender-design-plugin) · Apache-2.0 |
| `blender-inspect` | 只读检查当前场景，动工前先看清现状。 | Inspect an active Blender scene read-only before Codex designs, modifies, previews, or exports it. | [full-aigc-plugins/blender-design-plugin](https://github.com/full-aigc-plugins/blender-design-plugin) · Apache-2.0 |
| `blender-managed` | 托管模式：由 Codex 直接启动 Blender，无需安装插件。 | Start a non-invasive Blender design session from Codex without installing a Blender Add-on. | [full-aigc-plugins/blender-design-plugin](https://github.com/full-aigc-plugins/blender-design-plugin) · Apache-2.0 |
| `blender-mcp-setup` | 连接排查：Blender 未安装、插件未启用、服务未启动或端口不通。 | Set up or diagnose the plugin-owned Blender MCP connection when Blender is missing, the Add-on is disabled, Start MCP Server has not been clicked, or… | [full-aigc-plugins/blender-design-plugin](https://github.com/full-aigc-plugins/blender-design-plugin) · Apache-2.0 |
| `blender-preview` | 预览截图：相机、正视、侧视与顶视四个角度。 | Capture fresh camera, front, side, and top Blender previews for milestone review or visual diagnosis. | [full-aigc-plugins/blender-design-plugin](https://github.com/full-aigc-plugins/blender-design-plugin) · Apache-2.0 |
| `blender-previs` | 预演：把故事或分镜变成色块白模预演视频。 | Use when turning a story or shot list into a color-coded white-model previs video in Blender, producing placeholder blocking, exact cut timing, and a… | [full-aigc-plugins/blender-design-plugin](https://github.com/full-aigc-plugins/blender-design-plugin) · Apache-2.0 |
| `blender-procedural-modeling` | 程序化建模：Geometry Nodes 系统与参数化环境。 | Build or update reusable Blender Geometry Nodes systems and parameterized environments with version-probed node and socket semantics. | [full-aigc-plugins/blender-design-plugin](https://github.com/full-aigc-plugins/blender-design-plugin) · Apache-2.0 |
| `blender-quality-validation` | 质量验收：按阈值核验几何、动画、碰撞、运动与镜头。 | Measure Blender geometry, character, prop, collision, motion, and camera acceptance criteria against explicit objects, frames, proxies, and tolerance… | [full-aigc-plugins/blender-design-plugin](https://github.com/full-aigc-plugins/blender-design-plugin) · Apache-2.0 |
| `blender-recover` | 失败恢复：回滚到上一个检查点继续，不重放未提交命令。 | Rollback a failed Blender milestone or resume from the latest confirmed checkpoint without replaying uncommitted commands. | [full-aigc-plugins/blender-design-plugin](https://github.com/full-aigc-plugins/blender-design-plugin) · Apache-2.0 |
| `blender-render-compositing` | 渲染合成：Eevee/Cycles、渲染通道、色彩管理、材质烘焙与合成节点。 | Configure Blender Eevee or Cycles, render passes, color management, material baking, dependency packing, compositor nodes, and verified extended expo… | [full-aigc-plugins/blender-design-plugin](https://github.com/full-aigc-plugins/blender-design-plugin) · Apache-2.0 |
| `blender-retopology` | 重拓扑：投影与数据层传递，得到可编辑的布面。 | Set up, project, transfer data layers for, and validate editable retopology surfaces against source meshes using registered retopo commands. | [full-aigc-plugins/blender-design-plugin](https://github.com/full-aigc-plugins/blender-design-plugin) · Apache-2.0 |
| `blender-scene-assembly` | 场景组织：集合、对象命名、变换、可见性与资产溯源。 | Organize Blender scenes, collections, object identity, transforms, visibility, and authorized reusable assets without losing editability or provenanc… | [full-aigc-plugins/blender-design-plugin](https://github.com/full-aigc-plugins/blender-design-plugin) · Apache-2.0 |
| `blender-sculpt-surface` | 雕刻：遮罩、置换、笔刷、体素重网格与细节清理。 | Create and refine Blender surface detail with topology-bound masks, displacement, foreground sculpt strokes, voxel remesh, Multires, and cleanup modi… | [full-aigc-plugins/blender-design-plugin](https://github.com/full-aigc-plugins/blender-design-plugin) · Apache-2.0 |
| `blender-seedance-pipeline` | 把 Blender 预演接入 Dreamina / Seedance 渲染流水线。 | Drive a Blender preview through the validated Dreamina 3D pipeline. | [full-aigc-plugins/blender-design-plugin](https://github.com/full-aigc-plugins/blender-design-plugin) · Apache-2.0 |
| `blender-sequence-editing` | 序列剪辑：VSE 时间线、转场、变速、音频淡化与输出。 | Assemble editable Blender VSE timelines from images, image sequences, scenes, movies, text, and sound, including timing, speed, transitions, audio fa… | [full-aigc-plugins/blender-design-plugin](https://github.com/full-aigc-plugins/blender-design-plugin) · Apache-2.0 |
| `blender-simulation` | 仿真：刚体、碰撞、布料、软体、烟雾、点缓存与流体。 | Configure and validate Blender rigid-body, collision, cloth, soft-body, smoke, point-cache, and fluid-cache workflows. | [full-aigc-plugins/blender-design-plugin](https://github.com/full-aigc-plugins/blender-design-plugin) · Apache-2.0 |
| `blender-to-dreamina` | 用即梦上传器把本地视频生成网页交付链接。 | Use an already enabled official Jimeng Blender uploader to render or select a local video and create a Jimeng Web handoff link. | [full-aigc-plugins/blender-design-plugin](https://github.com/full-aigc-plugins/blender-design-plugin) · Apache-2.0 |
| `blender-tracking` | 摄像机反求：标记点、解算与重投影误差校验。 | Load approved footage, create normalized Blender tracking markers, solve a foreground camera, set up the scene, and validate reprojection error. | [full-aigc-plugins/blender-design-plugin](https://github.com/full-aigc-plugins/blender-design-plugin) · Apache-2.0 |
| `blender-use` | 任务路由：判断该走托管模式还是 Connector 模式。 | Route requests to managed or Connector Blender workflows when a user wants Codex to create, modify, review, save, or export a Blender design. | [full-aigc-plugins/blender-design-plugin](https://github.com/full-aigc-plugins/blender-design-plugin) · Apache-2.0 |
| `blender-uv-material` | UV 与 PBR 材质：贴图色彩空间与法线贴图语义。 | Prepare UVs and physically based Blender materials for editable product or character assets, including texture color-space and normal-map semantics. | [full-aigc-plugins/blender-design-plugin](https://github.com/full-aigc-plugins/blender-design-plugin) · Apache-2.0 |
| `blender-background-jobs` | 后台任务：批量渲染、帧序列导出、视频合成与仿真烘焙，不阻塞前台。 | Run snapshot-isolated Blender exports, durable animation frame sequences, explicit frame recovery, verified video composition, still renders, and sim… | [full-aigc-skills/blender-skills](https://github.com/full-aigc-skills/blender-skills) · Apache-2.0 |
| `blender-character-animation` | 角色动画：时间控制、IK、约束与动作连续性校验。 | Animate a registered Blender character rig and a single interactive prop with editable timing, IK controls, constraints, and continuity checks. | [full-aigc-skills/blender-skills](https://github.com/full-aigc-skills/blender-skills) · Apache-2.0 |
| `blender-character-rigging` | 骨骼绑定：骨架、蒙皮权重、IK 控制与关节限制。 | Build and inspect editable Blender armatures, skin weights, IK controls, pole targets, joint limits, and prop constraints for character work. | [full-aigc-skills/blender-skills](https://github.com/full-aigc-skills/blender-skills) · Apache-2.0 |
| `blender-cinematography` | 摄影机设计：镜头、朝向、路径运动、对焦与构图。 | Design and validate Blender cameras, lenses, subject aiming, path motion, focus, framing, and controlled handheld response. | [full-aigc-skills/blender-skills](https://github.com/full-aigc-skills/blender-skills) · Apache-2.0 |
| `blender-curves` | 曲线建模：路径、剖面、线缆与轨道等曲线驱动道具。 | Build editable Blender paths, profiles, cables, rails, or curve-driven props using registered curve commands. | [full-aigc-skills/blender-skills](https://github.com/full-aigc-skills/blender-skills) · Apache-2.0 |
| `blender-design` | 设计总入口：从一句想法到场景，含建模、材质、灯光、相机与动画。 | Turn a user's idea into a Blender scene through milestone-based modeling, materials, lighting, camera, and animation commands. | [full-aigc-skills/blender-skills](https://github.com/full-aigc-skills/blender-skills) · Apache-2.0 |
| `blender-export` | 导出并验证：模型、图片、视频、EXR、USD、Alembic 多格式产物。 | Export an approved Blender snapshot to verified model, image, video, EXR, USD, or Alembic artifacts using compatible receipt contracts. | [full-aigc-skills/blender-skills](https://github.com/full-aigc-skills/blender-skills) · Apache-2.0 |
| `blender-grease-pencil` | 蜡笔工具：2D 图层、材质、逐帧绘制与 2D/3D 混排。 | Create editable Blender Grease Pencil layers, materials, frame drawings, and mixed 2D/3D scenes with structured stroke data. | [full-aigc-skills/blender-skills](https://github.com/full-aigc-skills/blender-skills) · Apache-2.0 |
| `blender-hair` | 头发曲线：按表面点生成与检查发丝。 | Create and inspect native Blender Hair Curves from explicit surface-local strand points, radii, and bound source surfaces. | [full-aigc-skills/blender-skills](https://github.com/full-aigc-skills/blender-skills) · Apache-2.0 |
| `blender-hard-surface` | 硬表面建模：产品、机械与道具外形，配合修改器保持可编辑。 | Create editable hard-surface, product, mechanical, or prop geometry with registered Blender mesh, modifier, collection, and recipe commands. | [full-aigc-skills/blender-skills](https://github.com/full-aigc-skills/blender-skills) · Apache-2.0 |
| `blender-inspect` | 只读检查当前场景，动工前先看清现状。 | Inspect an active Blender scene read-only before Codex designs, modifies, previews, or exports it. | [full-aigc-skills/blender-skills](https://github.com/full-aigc-skills/blender-skills) · Apache-2.0 |
| `blender-mcp-setup` | 连接排查：Blender 未安装、插件未启用、服务未启动或端口不通。 | Set up or diagnose the plugin-owned Blender MCP connection when Blender is missing, the Add-on is disabled, Start MCP Server has not been clicked, or… | [full-aigc-skills/blender-skills](https://github.com/full-aigc-skills/blender-skills) · Apache-2.0 |
| `blender-preview` | 预览截图：相机、正视、侧视与顶视四个角度。 | Capture fresh camera, front, side, and top Blender previews for milestone review or visual diagnosis. | [full-aigc-skills/blender-skills](https://github.com/full-aigc-skills/blender-skills) · Apache-2.0 |
| `blender-procedural-modeling` | 程序化建模：Geometry Nodes 系统与参数化环境。 | Build or update reusable Blender Geometry Nodes systems and parameterized environments with version-probed node and socket semantics. | [full-aigc-skills/blender-skills](https://github.com/full-aigc-skills/blender-skills) · Apache-2.0 |
| `blender-quality-validation` | 质量验收：按阈值核验几何、动画、碰撞、运动与镜头。 | Measure Blender geometry, character, prop, collision, motion, and camera acceptance criteria against explicit objects, frames, proxies, and tolerance… | [full-aigc-skills/blender-skills](https://github.com/full-aigc-skills/blender-skills) · Apache-2.0 |
| `blender-render-compositing` | 渲染合成：Eevee/Cycles、渲染通道、色彩管理、材质烘焙与合成节点。 | Configure Blender Eevee or Cycles, render passes, color management, material baking, dependency packing, compositor nodes, and verified extended expo… | [full-aigc-skills/blender-skills](https://github.com/full-aigc-skills/blender-skills) · Apache-2.0 |
| `blender-retopology` | 重拓扑：投影与数据层传递，得到可编辑的布面。 | Set up, project, transfer data layers for, and validate editable retopology surfaces against source meshes using registered retopo commands. | [full-aigc-skills/blender-skills](https://github.com/full-aigc-skills/blender-skills) · Apache-2.0 |
| `blender-scene-assembly` | 场景组织：集合、对象命名、变换、可见性与资产溯源。 | Organize Blender scenes, collections, object identity, transforms, visibility, and authorized reusable assets without losing editability or provenanc… | [full-aigc-skills/blender-skills](https://github.com/full-aigc-skills/blender-skills) · Apache-2.0 |
| `blender-sculpt-surface` | 雕刻：遮罩、置换、笔刷、体素重网格与细节清理。 | Create and refine Blender surface detail with topology-bound masks, displacement, foreground sculpt strokes, voxel remesh, Multires, and cleanup modi… | [full-aigc-skills/blender-skills](https://github.com/full-aigc-skills/blender-skills) · Apache-2.0 |
| `blender-sequence-editing` | 序列剪辑：VSE 时间线、转场、变速、音频淡化与输出。 | Assemble editable Blender VSE timelines from images, image sequences, scenes, movies, text, and sound, including timing, speed, transitions, audio fa… | [full-aigc-skills/blender-skills](https://github.com/full-aigc-skills/blender-skills) · Apache-2.0 |
| `blender-simulation` | 仿真：刚体、碰撞、布料、软体、烟雾、点缓存与流体。 | Configure and validate Blender rigid-body, collision, cloth, soft-body, smoke, point-cache, and fluid-cache workflows. | [full-aigc-skills/blender-skills](https://github.com/full-aigc-skills/blender-skills) · Apache-2.0 |
| `blender-tracking` | 摄像机反求：标记点、解算与重投影误差校验。 | Load approved footage, create normalized Blender tracking markers, solve a foreground camera, set up the scene, and validate reprojection error. | [full-aigc-skills/blender-skills](https://github.com/full-aigc-skills/blender-skills) · Apache-2.0 |
| `blender-uv-material` | UV 与 PBR 材质：贴图色彩空间与法线贴图语义。 | Prepare UVs and physically based Blender materials for editable product or character assets, including texture color-space and normal-map semantics. | [full-aigc-skills/blender-skills](https://github.com/full-aigc-skills/blender-skills) · Apache-2.0 |
| `openspec-apply-change` | 执行 OpenSpec 变更中的待办任务。 | Implement tasks from an OpenSpec change. | [full-aigc-skills/blender-skills](https://github.com/full-aigc-skills/blender-skills) · Apache-2.0 |
| `openspec-archive-change` | 归档已完成的变更。 | Archive a completed change in the experimental workflow. | [full-aigc-skills/blender-skills](https://github.com/full-aigc-skills/blender-skills) · Apache-2.0 |
| `openspec-explore` | 进入探索模式，作为思考伙伴一起梳理想法。 | Enter explore mode - | [full-aigc-skills/blender-skills](https://github.com/full-aigc-skills/blender-skills) · Apache-2.0 |
| `openspec-propose` | 一步生成新的变更提案及其全部产物。 | Propose a new change with all artifacts generated in one step. | [full-aigc-skills/blender-skills](https://github.com/full-aigc-skills/blender-skills) · Apache-2.0 |

## 5. 图表与可视化 / Charts & diagrams

架构图、流程图、数据图表与 SVG 设计系统。

**📦 打包下载：[pack-charts.zip](https://github.com/xjyloly-prog/codex-skills-catalog/releases/download/v1.1.0/pack-charts.zip) · [镜像](https://ghproxy.net/https://github.com/xjyloly-prog/codex-skills-catalog/releases/download/v1.1.0/pack-charts.zip)**（2.0 MB，含 2 个技能；另有 1 个因许可证未收录，见表格来源链接）

> 按需启用：默认**不挂载**，需要时挂上并新开对话。

| 技能 / Skill | 中文说明 | English | 来源 / Source |
|---|---|---|---|
| `archify` | 架构与流程可视化：架构图、时序图、数据流、状态机，输出可交互 HTML 并可导出多格式。 | Create polished, validated architecture, workflow, sequence, data-flow, and lifecycle/state diagrams as explorable standalone HTML with inline SVG, d… | [tt-a1i/archify](https://github.com/tt-a1i/archify) · MIT |
| `lieflat-charts` | 数据可视化与报告：模板驱动生成精致 HTML 图表，或整页可发布报告。 | 一套模板驱动的数据可视化与报告生成 skill，既能严格从 Lupi、Basics、Glance、Maps 与 Interactive gallery 的真实实现生成 HTML 图表，也能从 12 套中英文整页报告模板生成可发布的 HTML 报告；以 Mono 为保底，能按数据语义自动选择内置彩色… | [larashero3-dotcom/lieflat-charts](https://github.com/larashero3-dotcom/lieflat-charts) · 见仓库 |
| `svg-design-system` | SVG 图表设计系统：流程图、矩阵图、架构图、时间轴、关系图、循环图与对比图。 | A reusable visual design system for drawing SVG diagrams that look professional AND carry real information hierarchy. | [VioletScar-Hui/Svg-design-system](https://github.com/VioletScar-Hui/Svg-design-system) · 见仓库 |

## 6. 网页与设计原型 / Web & design prototypes

122 个网页 / 幻灯片 / 海报模板（来自 open-design），按需启用。

**📦 打包下载：[pack-design.zip](https://github.com/xjyloly-prog/codex-skills-catalog/releases/download/v1.1.0/pack-design.zip) · [镜像](https://ghproxy.net/https://github.com/xjyloly-prog/codex-skills-catalog/releases/download/v1.1.0/pack-design.zip)**（35.0 MB，含 122 个技能）

> 按需启用：默认**不挂载**，需要时挂上并新开对话。

| 技能 / Skill | 中文说明 | English | 来源 / Source |
|---|---|---|---|
| `8-bit-orbit-video-template` | 复古像素风动态视频模板（HyperFrames）。 | Hyperframes-based video template for retro pixel deck motion design. | [dunzic/open-design](https://github.com/dunzic/open-design) · 见仓库 |
| `after-hours-editorial-template` | 奢华暗色杂志风三页故事板模板。 | Luxury dark-editorial HyperFrames template for three-page cinematic storyboards, inspired by haute couture title cards and magazine chapter spreads. | [dunzic/open-design](https://github.com/dunzic/open-design) · 见仓库 |
| `audio-jingle` | 音频生成：片头音、背景乐、旁白与音效。 | Audio generation skill — | [dunzic/open-design](https://github.com/dunzic/open-design) · 见仓库 |
| `blog-post` | 长文 / 博客页面：刊头、主图占位、正文配图与脚注。 | A long-form article / blog post — | [dunzic/open-design](https://github.com/dunzic/open-design) · 见仓库 |
| `clinical-case-report` | 结构化医学病例汇报页面。 | Structured medical case presentation for clinical rounds, conferences, and documentation. | [dunzic/open-design](https://github.com/dunzic/open-design) · 见仓库 |
| `critique` | 对任意 HTML 作品做五维专家设计评审。 | Run a 5-dimension expert design review on any HTML artifact in the project — | [dunzic/open-design](https://github.com/dunzic/open-design) · 见仓库 |
| `dashboard` | 单文件管理 / 分析看板：侧边栏、顶栏、图表区。 | Admin / analytics dashboard in a single HTML file. | [dunzic/open-design](https://github.com/dunzic/open-design) · 见仓库 |
| `dating-web` | 消费级社交配对产品界面原型。 | A consumer-feeling dating / matchmaking dashboard — | [dunzic/open-design](https://github.com/dunzic/open-design) · 见仓库 |
| `dcf-valuation` | 上市公司 DCF 估值与内在价值分析。 | Discounted cash flow valuation and intrinsic value analysis for public companies. | [dunzic/open-design](https://github.com/dunzic/open-design) · 见仓库 |
| `design-brief` | 把 I-Lang 格式的设计概要解析成具体设计规格。 | Parse a structured design brief written in I-Lang protocol format into a concrete design spec. | [dunzic/open-design](https://github.com/dunzic/open-design) · 见仓库 |
| `digital-eguide` | 两跨页电子导览预览（封面 + 内页）。 | A two-spread digital e-guide preview — | [dunzic/open-design](https://github.com/dunzic/open-design) · 见仓库 |
| `digits-fintech-swiss-template` | 瑞士网格金融科技演示模板（黑 / 暖纸 / 荧光绿）。 | Swiss-grid fintech deck template in black / warm paper / neon-lime contrast. | [dunzic/open-design](https://github.com/dunzic/open-design) · 见仓库 |
| `docs-page` | 文档站页面：左侧导航、正文、右侧目录。 | A documentation page — | [dunzic/open-design](https://github.com/dunzic/open-design) · 见仓库 |
| `editorial-burgundy-principles-template` | 酒红 + 裸粉 + 哑金杂志风演示模板。 | Editorial studio deck template in burgundy / blush / muted-gold palette. | [dunzic/open-design](https://github.com/dunzic/open-design) · 见仓库 |
| `email-marketing` | 品牌产品发布邮件模板。 | A brand product-launch email — | [dunzic/open-design](https://github.com/dunzic/open-design) · 见仓库 |
| `eng-runbook` | 工程运维手册页面：服务概览、告警表、常用流程。 | An engineering runbook — | [dunzic/open-design](https://github.com/dunzic/open-design) · 见仓库 |
| `field-notes-editorial-template` | “野外笔记”报告模板，柔和纸感。 | Editorial "Field Notes" report template with soft paper background, serif hero typography, rounded pastel insight cards, and a retention chart panel. | [dunzic/open-design](https://github.com/dunzic/open-design) · 见仓库 |
| `finance-report` | 季度 / 月度财务报告：KPI、收入与烧钱曲线、损益摘要。 | Quarterly / monthly financial report — | [dunzic/open-design](https://github.com/dunzic/open-design) · 见仓库 |
| `flowai-live-dashboard-template` | FlowAI 风格团队管理看板（三标签页）。 | Team-management dashboard skill in the FlowAI aesthetic — | [dunzic/open-design](https://github.com/dunzic/open-design) · 见仓库 |
| `gamified-app` | 游戏化移动应用多帧原型。 | A multi-frame gamified mobile-app prototype — | [dunzic/open-design](https://github.com/dunzic/open-design) · 见仓库 |
| `github-dashboard` | GitHub 仓库分析看板：星标、Fork、贡献者、议题与 PR。 | GitHub repository analytics dashboard — | [dunzic/open-design](https://github.com/dunzic/open-design) · 见仓库 |
| `hatch-pet` | 生成 / 修复 / 校验 / 打包 Codex 动态宠物精灵图。 | Create, repair, validate, preview, and package Codex-compatible animated pet spritesheets from character art, screenshots, generated images, or visua… | [dunzic/open-design](https://github.com/dunzic/open-design) · 见仓库 |
| `hr-onboarding` | 新员工入职计划单页。 | A new-hire onboarding plan as a single page — | [dunzic/open-design](https://github.com/dunzic/open-design) · 见仓库 |
| `html-ppt` | HTML PPT 工作室：多风格静态网页演示创作。 | HTML PPT Studio — | [dunzic/open-design](https://github.com/dunzic/open-design) · 见仓库 |
| `html-ppt-course-module` | 在线课程 / 工作坊模块演示（暖纸 + 衬线）。 | Online-course / workshop module deck — | [dunzic/open-design](https://github.com/dunzic/open-design) · 见仓库 |
| `html-ppt-dir-key-nav-minimal` | 极简 8 页 keynote，方向键导航。 | 8 页极简方向键 keynote — | [dunzic/open-design](https://github.com/dunzic/open-design) · 见仓库 |
| `html-ppt-graphify-dark-graph` | 暗色知识图谱风演示。 | 暗底知识图谱 deck — | [dunzic/open-design](https://github.com/dunzic/open-design) · 见仓库 |
| `html-ppt-hermes-cyber-terminal` | 终端 / CRT 复古风评审演示。 | 暗终端 honest-review deck — | [dunzic/open-design](https://github.com/dunzic/open-design) · 见仓库 |
| `html-ppt-knowledge-arch-blueprint` | 蓝图风知识架构演示。 | 奶油蓝图架构 deck — | [dunzic/open-design](https://github.com/dunzic/open-design) · 见仓库 |
| `html-ppt-obsidian-claude-gradient` | Obsidian 渐变风演示。 | GitHub 暗紫渐变 deck — | [dunzic/open-design](https://github.com/dunzic/open-design) · 见仓库 |
| `html-ppt-pitch-deck` | 投资人视角 10 页路演演示。 | Investor-ready 10-slide HTML pitch deck — | [dunzic/open-design](https://github.com/dunzic/open-design) · 见仓库 |
| `html-ppt-presenter-mode` | 带演讲者模式的演示（备注 + 计时）。 | 演讲者模式专用 deck — | [dunzic/open-design](https://github.com/dunzic/open-design) · 见仓库 |
| `html-ppt-product-launch` | 产品发布主题演讲演示。 | Launch keynote deck — | [dunzic/open-design](https://github.com/dunzic/open-design) · 见仓库 |
| `html-ppt-retro-quarterly-review` | 复古蓝橙风季度复盘演示。 | Retro Quarterly Review presentation template in a bold blue + orange editorial language. | [dunzic/open-design](https://github.com/dunzic/open-design) · 见仓库 |
| `html-ppt-taste-brutalist` | 战术终端 / 野蛮主义风格 16:9 演示。 | 16:9 HTML deck in tactical-telemetry / CRT-terminal taste. | [dunzic/open-design](https://github.com/dunzic/open-design) · 见仓库 |
| `html-ppt-taste-editorial` | 杂志极简风 16:9 演示。 | 16:9 HTML deck in editorial-minimalist taste. | [dunzic/open-design](https://github.com/dunzic/open-design) · 见仓库 |
| `html-ppt-tech-sharing` | 技术分享 / 会议演示（GitHub 暗色 + 终端代码块）。 | Conference / internal tech-talk deck — | [dunzic/open-design](https://github.com/dunzic/open-design) · 见仓库 |
| `html-ppt-testing-safety-alert` | 测试预警风演示（风险分级与告警框）。 | 红琥珀警示 deck — | [dunzic/open-design](https://github.com/dunzic/open-design) · 见仓库 |
| `html-ppt-weekly-report` | 团队周报演示（KPI 网格 + 进展列表）。 | Team weekly / status-update deck — | [dunzic/open-design](https://github.com/dunzic/open-design) · 见仓库 |
| `html-ppt-xhs-pastel-card` | 小红书淡彩卡片风演示。 | 柔和马卡龙慢生活 deck — | [dunzic/open-design](https://github.com/dunzic/open-design) · 见仓库 |
| `html-ppt-xhs-post` | 小红书 / Instagram 9 页图文模板（810×1080）。 | 小红书 / Instagram 风 9 页 3:4 竖版图文（810×1080）— 暖色 pastel、虚线 sticker 卡片、底部页码点点。用于发小红书图文、Instagram carousel、品牌种草内容。 | [dunzic/open-design](https://github.com/dunzic/open-design) · 见仓库 |
| `html-ppt-xhs-white-editorial` | 白底杂志风演示。 | 白底杂志风 deck — | [dunzic/open-design](https://github.com/dunzic/open-design) · 见仓库 |
| `html-ppt-zhangzara-8-bit-orbit` | 配色风格：8-bit 像素霓虹街机。 | 8-Bit Orbit — | [dunzic/open-design](https://github.com/dunzic/open-design) · 见仓库 |
| `html-ppt-zhangzara-biennale-yellow` | 配色风格：暖羊皮纸 + 太阳能黄 + 深靛衬线。 | Biennale Yellow — | [dunzic/open-design](https://github.com/dunzic/open-design) · 见仓库 |
| `html-ppt-zhangzara-block-frame` | 配色风格：新野蛮主义色块 + 粗黑边框。 | BlockFrame — | [dunzic/open-design](https://github.com/dunzic/open-design) · 见仓库 |
| `html-ppt-zhangzara-blue-professional` | 配色风格：奶油纸底 + 钴蓝，现代专业。 | Blue Professional — | [dunzic/open-design](https://github.com/dunzic/open-design) · 见仓库 |
| `html-ppt-zhangzara-bold-poster` | 配色风格：海报式超大字标题。 | Bold Poster — | [dunzic/open-design](https://github.com/dunzic/open-design) · 见仓库 |
| `html-ppt-zhangzara-broadside` | 配色风格：暗色编辑风 + 单一橙色重点。 | Broadside — | [dunzic/open-design](https://github.com/dunzic/open-design) · 见仓库 |
| `html-ppt-zhangzara-capsule` | 配色风格：胶囊卡片 + 粉彩配色。 | Capsule — | [dunzic/open-design](https://github.com/dunzic/open-design) · 见仓库 |
| `html-ppt-zhangzara-cartesian` | 配色风格：暖中性色 + 古典衬线。 | Cartesian — | [dunzic/open-design](https://github.com/dunzic/open-design) · 见仓库 |
| `html-ppt-zhangzara-cobalt-grid` | 配色风格：钴蓝斜体衬线 + 方格纸底。 | Cobalt Grid — | [dunzic/open-design](https://github.com/dunzic/open-design) · 见仓库 |
| `html-ppt-zhangzara-coral` | 配色风格：近黑底 + 珊瑚色超大标题。 | Coral — | [dunzic/open-design](https://github.com/dunzic/open-design) · 见仓库 |
| `html-ppt-zhangzara-creative-mode` | 配色风格：奶油纸 + 多色活泼。 | Creative Mode — | [dunzic/open-design](https://github.com/dunzic/open-design) · 见仓库 |
| `html-ppt-zhangzara-daisy-days` | 配色风格：手绘雏菊、星星与彩虹，活泼。 | Daisy Days — | [dunzic/open-design](https://github.com/dunzic/open-design) · 见仓库 |
| `html-ppt-zhangzara-editorial-tri-tone` | 配色风格：三色编辑系统（灰粉 / 芥末 / 酒红）。 | Editorial Tri-Tone — | [dunzic/open-design](https://github.com/dunzic/open-design) · 见仓库 |
| `html-ppt-zhangzara-grove` | 配色风格：森林绿 + 奶油字 + 铁锈点缀。 | Grove — | [dunzic/open-design](https://github.com/dunzic/open-design) · 见仓库 |
| `html-ppt-zhangzara-long-table` | 配色风格：暖奶油 + 铁锈红晚餐会风。 | Long Table — | [dunzic/open-design](https://github.com/dunzic/open-design) · 见仓库 |
| `html-ppt-zhangzara-mat` | 配色风格：暗鼠尾草绿 + 骨白 + 焦橙。 | Mat — | [dunzic/open-design](https://github.com/dunzic/open-design) · 见仓库 |
| `html-ppt-zhangzara-monochrome` | 配色风格：象牙账本纸 + 全黑字体。 | Monochrome — | [dunzic/open-design](https://github.com/dunzic/open-design) · 见仓库 |
| `html-ppt-zhangzara-neo-grid-bold` | 配色风格：编辑新野蛮主义 + 荧光黄。 | Neo-Grid Bold — | [dunzic/open-design](https://github.com/dunzic/open-design) · 见仓库 |
| `html-ppt-zhangzara-peoples-platform` | 配色风格：蓝橙红海报能量（行动主义）。 | People's Platform (Block & Bold) — | [dunzic/open-design](https://github.com/dunzic/open-design) · 见仓库 |
| `html-ppt-zhangzara-pin-and-paper` | 配色风格：黄纸 + 别针插画 + 手写体。 | Pin & Paper — | [dunzic/open-design](https://github.com/dunzic/open-design) · 见仓库 |
| `html-ppt-zhangzara-pink-script` | 配色风格：黑底 + 亮粉 + 珍珠纸。 | Pink Script — | [dunzic/open-design](https://github.com/dunzic/open-design) · 见仓库 |
| `html-ppt-zhangzara-playful` | 配色风格：暖桃色 + 独立品牌活泼感。 | Playful — | [dunzic/open-design](https://github.com/dunzic/open-design) · 见仓库 |
| `html-ppt-zhangzara-raw-grid` | 配色风格：粗边框 + 错位阴影新野蛮主义。 | Raw Grid — | [dunzic/open-design](https://github.com/dunzic/open-design) · 见仓库 |
| `html-ppt-zhangzara-retro-windows` | 配色风格：Windows 95 界面复刻。 | Retro Windows — | [dunzic/open-design](https://github.com/dunzic/open-design) · 见仓库 |
| `html-ppt-zhangzara-retro-zine` | 配色风格：米色纸 + 绿色点缀的 riso 杂志。 | Retro Zine — | [dunzic/open-design](https://github.com/dunzic/open-design) · 见仓库 |
| `html-ppt-zhangzara-sakura-chroma` | 配色风格：复古日式卡带包装。 | Sakura Chroma — | [dunzic/open-design](https://github.com/dunzic/open-design) · 见仓库 |
| `html-ppt-zhangzara-scatterbrain` | 配色风格：便利贴 + 手写体拼贴。 | Scatterbrain — | [dunzic/open-design](https://github.com/dunzic/open-design) · 见仓库 |
| `html-ppt-zhangzara-signal` | 配色风格：深藏青 + 骨白 + 哑金，机构感。 | Signal — | [dunzic/open-design](https://github.com/dunzic/open-design) · 见仓库 |
| `html-ppt-zhangzara-soft-editorial` | 配色风格：暖纸 + 鼠尾草绿 / 腮红 / 柠檬。 | Soft Editorial — | [dunzic/open-design](https://github.com/dunzic/open-design) · 见仓库 |
| `html-ppt-zhangzara-stencil-tablet` | 配色风格：骨白纸 + 镂空标题 + 大地六色。 | Stencil & Tablet — | [dunzic/open-design](https://github.com/dunzic/open-design) · 见仓库 |
| `html-ppt-zhangzara-studio` | 配色风格：黑底 + 电光黄，设计工作室感。 | Studio — | [dunzic/open-design](https://github.com/dunzic/open-design) · 见仓库 |
| `html-ppt-zhangzara-vellum` | 配色风格：深藏青 + 暖黄斜体衬线。 | Vellum — | [dunzic/open-design](https://github.com/dunzic/open-design) · 见仓库 |
| `hyperframes` | 视频合成：动画、标题卡、字幕、配音与音频反应。 | Create video compositions, animations, title cards, overlays, captions, voiceovers, audio-reactive visuals, and scene transitions in HyperFrames HTML. | [dunzic/open-design](https://github.com/dunzic/open-design) · 见仓库 |
| `ib-pitch-book` | 投行风格并购 / 战略方案书（可比公司、先例交易）。 | Investment-banking pitch book for strategic alternatives — | [dunzic/open-design](https://github.com/dunzic/open-design) · 见仓库 |
| `image-poster` | 单图生成：海报、主视觉与编辑插画。 | Single-image generation skill for posters, key art, and editorial illustrations. | [dunzic/open-design](https://github.com/dunzic/open-design) · 见仓库 |
| `invoice` | 可打印发票页面（明细、税额、合计）。 | A printable invoice page — | [dunzic/open-design](https://github.com/dunzic/open-design) · 见仓库 |
| `kami-deck` | 印刷级 kami（纸）设计系统幻灯片。 | Produce a print-grade slide deck in the kami (紙 / 纸) design system — | [dunzic/open-design](https://github.com/dunzic/open-design) · 见仓库 |
| `kami-landing` | 印刷级 kami 单页文档。 | Produce a print-grade single-page kami (紙 / 纸) document — | [dunzic/open-design](https://github.com/dunzic/open-design) · 见仓库 |
| `kanban-board` | 看板 / 任务板（待办、进行中、评审、完成）。 | Kanban / task board with columns (To do / In progress / In review / Done), draggable-looking cards, assignee avatars, swimlanes, and a top filter bar. | [dunzic/open-design](https://github.com/dunzic/open-design) · 见仓库 |
| `last30days` | 近 30 天社区与社交趋势调研。 | Recent community and social trend research over the last 30 days. | [dunzic/open-design](https://github.com/dunzic/open-design) · 见仓库 |
| `live-artifact` | 可刷新、可审计的数据驱动页面（连接器或本地数据）。 | Create refreshable, auditable Open Design artifacts backed by connector or local data. | [dunzic/open-design](https://github.com/dunzic/open-design) · 见仓库 |
| `live-dashboard` | Notion 风格团队看板（Live Artifact）。 | Notion-style team dashboard rendered as a Live Artifact. | [dunzic/open-design](https://github.com/dunzic/open-design) · 见仓库 |
| `magazine-poster` | 编辑风海报：新闻纸、日期栏、超大衬线标题。 | An editorial-style poster — | [dunzic/open-design](https://github.com/dunzic/open-design) · 见仓库 |
| `magazine-web-ppt` | 中文“杂志风 · 泼墨”网页版 PPT，含 WebGL 流体背景。 | 生成"电子杂志 × 电子墨水"风格的横向翻页网页 PPT（单 HTML 文件），含 WebGL 流体背景、衬线标题 + 非衬线正文、章节幕封、数据大字报、图片网格等模板。当用户需要制作分享 / 演讲 / 发布会风格的网页 PPT，或提到"杂志风 PPT"、"horizontal swipe dec… | [dunzic/open-design](https://github.com/dunzic/open-design) · 见仓库 |
| `meeting-notes` | 会议纪要页：参会人、议程、决议、行动项。 | Meeting notes page — | [dunzic/open-design](https://github.com/dunzic/open-design) · 见仓库 |
| `mobile-app` | 手机应用界面（iPhone 15 Pro 精确边框）。 | A mobile-app screen rendered inside a pixel-accurate iPhone 15 Pro frame on the page. | [dunzic/open-design](https://github.com/dunzic/open-design) · 见仓库 |
| `mobile-onboarding` | 多屏移动端引导流程（三帧并排）。 | A multi-screen mobile onboarding flow rendered as three phone frames side by side — | [dunzic/open-design](https://github.com/dunzic/open-design) · 见仓库 |
| `motion-frames` | 单帧动效构图（循环 CSS 动画）。 | A single-frame motion-design composition with looping CSS animations — | [dunzic/open-design](https://github.com/dunzic/open-design) · 见仓库 |
| `open-design-landing` | Atelier Zero 风格单页编辑型落地页。 | Produce a world-class single-page editorial landing site in the Atelier Zero visual language (Monocle / Apartamento / Études editorial collage) — | [dunzic/open-design](https://github.com/dunzic/open-design) · 见仓库 |
| `open-design-landing-deck` | Atelier Zero 风格单文件幻灯片。 | Produce a single-file slide deck in the Atelier Zero visual language (warm-paper background, italic-serif emphasis spans, coral terminating dots, sur… | [dunzic/open-design](https://github.com/dunzic/open-design) · 见仓库 |
| `orbit-general` | 多连接器场景的简报技能（Orbit 流水线）。 | Open Orbit briefing skill — | [dunzic/open-design](https://github.com/dunzic/open-design) · 见仓库 |
| `orbit-github` | 仅连接 GitHub 时的简报技能。 | Open Orbit briefing skill — | [dunzic/open-design](https://github.com/dunzic/open-design) · 见仓库 |
| `orbit-gmail` | 仅连接 Gmail 时的简报技能。 | Open Orbit briefing skill — | [dunzic/open-design](https://github.com/dunzic/open-design) · 见仓库 |
| `orbit-linear` | 仅连接 Linear 时的简报技能。 | Open Orbit briefing skill — | [dunzic/open-design](https://github.com/dunzic/open-design) · 见仓库 |
| `orbit-notion` | 仅连接 Notion 时的简报技能。 | Open Orbit briefing skill — | [dunzic/open-design](https://github.com/dunzic/open-design) · 见仓库 |
| `pm-spec` | 产品需求文档单页（问题、指标、范围、用户故事）。 | Product spec / PRD as a single page — | [dunzic/open-design](https://github.com/dunzic/open-design) · 见仓库 |
| `pptx-html-fidelity-audit` | 审查 python-pptx 导出与源 HTML 幻灯片的版式偏差。 | Audit a python-pptx export against its source HTML deck, identify layout/content drift (footer overflow, cropped content, missing italic/em, lost sty… | [dunzic/open-design](https://github.com/dunzic/open-design) · 见仓库 |
| `pricing-page` | 独立定价页（套餐、功能对比表、FAQ）。 | A standalone pricing page — | [dunzic/open-design](https://github.com/dunzic/open-design) · 见仓库 |
| `release-notes-one-pager` | 发布说明单页（亮点、新增、修复、破坏性变更）。 | Release notes one-page HTML with highlights, Added, Fixed, Breaking changes, Known issues, and Upgrade note. | [dunzic/open-design](https://github.com/dunzic/open-design) · 见仓库 |
| `replit-deck` | Replit 风格单文件横滑演示。 | Single-file horizontal-swipe HTML deck in the style of Replit Slides's landing-page template gallery. | [dunzic/open-design](https://github.com/dunzic/open-design) · 见仓库 |
| `saas-landing` | 单页 SaaS 落地页（主视觉、功能、社会证明、定价）。 | Single-page SaaS landing with hero, features, social proof, pricing, and CTA. | [dunzic/open-design](https://github.com/dunzic/open-design) · 见仓库 |
| `simple-deck` | 通用单文件横滑演示，基于种子模板克隆。 | Single-file horizontal-swipe HTML deck. | [dunzic/open-design](https://github.com/dunzic/open-design) · 见仓库 |
| `social-carousel` | 三卡社交媒体轮播图（1080×1080）。 | A three-card social-media carousel laid out as 1080×1080 squares — | [dunzic/open-design](https://github.com/dunzic/open-design) · 见仓库 |
| `social-media-dashboard` | 创作者社媒数据分析看板。 | Creator-facing social media analytics dashboard in a single HTML file. | [dunzic/open-design](https://github.com/dunzic/open-design) · 见仓库 |
| `social-media-matrix-tracker-template` | 社媒矩阵追踪看板模板（电影感、数据密集）。 | 社媒矩阵数据追踪面板模板（Social Media Matrix Tracker）。 Use when users ask for a cinematic, data-dense social media analytics dashboard with multi-platform metric… | [dunzic/open-design](https://github.com/dunzic/open-design) · 见仓库 |
| `sprite-animation` | 像素 / 精灵风动画讲解页。 | A pixel / sprite-style animated explainer slide — | [dunzic/open-design](https://github.com/dunzic/open-design) · 见仓库 |
| `swiss-creative-mode-template` | 瑞士风创意模式演示模板。 | Swiss-inspired creative-mode presentation template skill with bold editorial typography, high-contrast geometric cards, interactive slide navigation,… | [dunzic/open-design](https://github.com/dunzic/open-design) · 见仓库 |
| `swiss-user-research-video-template` | 瑞士风用户研究叙事模板。 | Swiss-style user-research narrative template in warm-paper editorial aesthetics. | [dunzic/open-design](https://github.com/dunzic/open-design) · 见仓库 |
| `team-okrs` | OKR 追踪页（季度横幅 + 进度条）。 | OKR tracker page — | [dunzic/open-design](https://github.com/dunzic/open-design) · 见仓库 |
| `trading-analysis-dashboard-template` | 交易分析看板模板（明暗主题切换）。 | Professional trading analysis dashboard template (single-file HTML) with light/dark theme switch, dense market panels, chart interactions, demo/live… | [dunzic/open-design](https://github.com/dunzic/open-design) · 见仓库 |
| `tweaks` | 给任意 HTML 作品加实时参数控制面板。 | Wrap any HTML artifact with a side panel of live, parameterized controls — | [dunzic/open-design](https://github.com/dunzic/open-design) · 见仓库 |
| `video-shortform` | 短视频生成（3-10 秒产品短片 / 动效预告）。 | Short-form video generation skill — | [dunzic/open-design](https://github.com/dunzic/open-design) · 见仓库 |
| `waitlist-page` | 极简预热落地页（邮箱收集）。 | Minimal pre-launch landing with email capture, brand logo, and optional decorative layer. | [dunzic/open-design](https://github.com/dunzic/open-design) · 见仓库 |
| `web-prototype` | 通用桌面网页原型（单文件 HTML）。 | General-purpose desktop web prototype. | [dunzic/open-design](https://github.com/dunzic/open-design) · 见仓库 |
| `web-prototype-taste-brutalist` | 瑞士工业印刷风网页原型。 | Swiss industrial-print web prototype. | [dunzic/open-design](https://github.com/dunzic/open-design) · 见仓库 |
| `web-prototype-taste-editorial` | 编辑极简风网页原型。 | Editorial-minimalist web prototype. | [dunzic/open-design](https://github.com/dunzic/open-design) · 见仓库 |
| `web-prototype-taste-soft` | 苹果级柔和风网页原型。 | Apple-tier soft web prototype. | [dunzic/open-design](https://github.com/dunzic/open-design) · 见仓库 |
| `weekly-update` | 团队周报单文件横滑演示。 | Single-file horizontal-swipe slide deck for a weekly team update — | [dunzic/open-design](https://github.com/dunzic/open-design) · 见仓库 |
| `wireframe-sketch` | 手绘线框探索图。 | A hand-drawn wireframe exploration — | [dunzic/open-design](https://github.com/dunzic/open-design) · 见仓库 |
| `x-research` | X / Twitter 舆情调研。 | X/Twitter public sentiment research for recent market, company, product, or community discourse. | [dunzic/open-design](https://github.com/dunzic/open-design) · 见仓库 |

## 7. 文档与办公 / Documents & office

Codex 自带能力：Word / PDF / PPT / 表格 / 可视化 / LaTeX 编译。

**📦 无需下载**：这些是 Codex 自带能力，装好就有。

> 这些是 Codex 自带或插件能力，通常**常驻可用**。

| 技能 / Skill | 中文说明 | English | 来源 / Source |
|---|---|---|---|
| `imagegen` | 生成或编辑位图图像：照片、插画、贴图、原型图与透明底素材。 | Generate or edit raster images when the task benefits from AI-created bitmap visuals such as photos, illustrations, textures, sprites, mockups, or tr… | [OpenAI Codex 内置](https://openai.com/) · Proprietary |
| `openai-docs` | 查询 OpenAI / Codex 官方文档：模型、定价、设置、排障与 API 用法。 | Use for Codex models/pricing, scheduled tasks, skills, settings, setup, troubleshooting, customization, automations, and self-knowledge—including 'yo… | [OpenAI Codex 内置](https://openai.com/) · Proprietary |
| `plugin-creator` | 创建或更新 Codex 插件目录结构与市场条目。 | Create and scaffold plugin directories for Codex with a required `.codex-plugin/plugin.json`, optional plugin folders/files, valid manifest defaults,… | [OpenAI Codex 内置](https://openai.com/) · Proprietary |
| `review-agent` | 对指定代码改动做只读、缺陷优先的审查。 | Perform a read-only, defect-first review of a specified code change and return every actionable finding. | [OpenAI Codex 内置](https://openai.com/) · Proprietary |
| `skill-creator` | 创建或更新 Codex 技能及其配套资源。 | Create or update a Codex skill with appropriately scoped instructions and any needed supporting resources. | [OpenAI Codex 内置](https://openai.com/) · Proprietary |
| `skill-installer` | 从精选列表或 GitHub 仓库安装技能。 | Install Codex skills into $CODEX_HOME/skills from a curated list or a GitHub repo path. | [OpenAI Codex 内置](https://openai.com/) · Proprietary |
| `latex-compile` | 编译 TeX 项目：简单项目用内置 Tectonic，复杂项目回退到 TeX Live。 | Compile a TeX project from Codex, trying bundled Tectonic for simple projects and falling back to detected TeX Live or MacTeX when needed. | [OpenAI Codex 内置插件](https://openai.com/) · Proprietary |
| `latex-doctor` | 检测 LaTeX 工具链可用性，并做小规模编译冒烟测试。 | Detect bundled Tectonic plus TeX Live or MacTeX availability, report missing LaTeX tools, and run small compile smoke tests when possible. | [OpenAI Codex 内置插件](https://openai.com/) · Proprietary |
| `texlive-runtime-installer` | 在本机没有 TeX Live 时，安装由 Codex 管理的完整运行时。 | Detect existing TeX Live or MacTeX first, then optionally install a Codex-managed full TeX Live runtime only when no existing TeX Live installation i… | [OpenAI Codex 内置插件](https://openai.com/) · Proprietary |
| `visualize` | 在对话里直接创建可视化与交互工具，用于讲解、对比与探索。 | Create visualizations and interactive tools directly in conversation. | [OpenAI Codex 内置插件](https://openai.com/) · Proprietary |

## Agents 角色分工 / Agent roles

Codex 里的“agent”有三层含义，用法不同：

| 类型 | 说明 | 怎么触发 |
|---|---|---|
| 主 Agent | 就是你正在对话的 Codex 本身，负责读写文件、执行命令、生成文档 | 直接说需求 |
| 技能内置角色 | 数模的**建模手 / 编程手 / 论文手**，各自有独立的产出与自检标准；Blender 的 harness 工作流角色 | 说“用建模手分析这道题” |
| 多 Agent 并行 | 把任务拆成几路同时做（查资料 / 写代码 / 审校） | 说“用多个 agent 并行做这件事” |

数模三阶段角色（来自 `math-modeling`）：

1. **建模手** — 题目理解、模型选择与算法设计。
2. **编程手** — Python / MATLAB 实现、求解、图表与结果复现。
3. **论文手** — 依据真实代码结果撰写论文。

## 依赖清单 / Dependencies

| 工具 | 用途 | 安装位置 |
|---|---|---|
| pandoc 3.11 | Markdown ↔ Word 转换 | `D:\CodexSkills\_tools\pandoc` |
| Typst 0.15.1 | 论文排版（Typst 引擎） | `D:\CodexSkills\_tools\typst` |
| MiKTeX | LaTeX 编译（xelatex / pdflatex，中文宏包） | `D:\CodexSkills\_tools\miktex` |
| Blender 5.2.2 LTS | 三维建模与渲染 | `D:\CodexSkills\_tools\blender` |
| drawio | 流程图 / 路线图导出 | `D:\CodexSkills\_tools\drawio` |
| ffmpeg | 视频合成与转码 | `D:\CodexSkills\_tools\ffmpeg` |
| Python 科学计算库 | numpy / pandas / matplotlib / scipy / scikit-learn 等 | 系统 Python 用户目录 |

## 来源与许可 / Sources & licenses

| 来源仓库 / Source | 收录技能数 | 许可证 |
|---|---|---|
| [dunzic/open-design](https://github.com/dunzic/open-design) | 122 | 见仓库 |
| [full-aigc-plugins/blender-design-plugin](https://github.com/full-aigc-plugins/blender-design-plugin) | 33 | Apache-2.0 |
| [full-aigc-skills/blender-skills](https://github.com/full-aigc-skills/blender-skills) | 27 | Apache-2.0 |
| [BZDmathclub/bzd-math-modeling-skills](https://github.com/BZDmathclub/bzd-math-modeling-skills) | 16 | 见仓库 |
| [XiaoMaColtAI/math-modeling-skill](https://github.com/XiaoMaColtAI/math-modeling-skill) | 10 | 见仓库 |
| [jihe520/MathModelAgent](https://github.com/jihe520/MathModelAgent) | 10 | 见仓库 |
| [sweetcornna/mathodology](https://github.com/sweetcornna/mathodology) | 8 | MIT |
| [zhaohui-yang/official-document-drafting](https://github.com/zhaohui-yang/official-document-drafting) | 8 | MIT |
| [OpenAI Codex 内置](https://openai.com/) | 6 | Proprietary |
| [RealSeaberry/AutoMCM-Pro](https://github.com/RealSeaberry/AutoMCM-Pro) | 4 | MIT |
| [OpenAI Codex 内置插件](https://openai.com/) | 4 | Proprietary |
| [anthropics/skills](https://github.com/anthropics/skills) | 2 | Apache-2.0 |
| [Gabberflast/academic-pptx-skill](https://github.com/Gabberflast/academic-pptx-skill) | 1 | MIT |
| [tt-a1i/archify](https://github.com/tt-a1i/archify) | 1 | MIT |
| [zairuilab/consulting-deck](https://github.com/zairuilab/consulting-deck) | 1 | Apache-2.0 |
| [anthropics/skills](https://github.com/anthropics/skills) | 1 | 见仓库 |
| [xwu43361-sys/innovation-proposal](https://github.com/xwu43361-sys/innovation-proposal) | 1 | MIT |
| [larashero3-dotcom/lieflat-charts](https://github.com/larashero3-dotcom/lieflat-charts) | 1 | 见仓库 |
| [Achuan-2/pandoc_docx_template](https://github.com/Achuan-2/pandoc_docx_template) | 1 | 见仓库 |
| [Akxan/ppt-agent-skill](https://github.com/Akxan/ppt-agent-skill) | 1 | MIT |
| [sunbigfly/ppt-agent-skills](https://github.com/sunbigfly/ppt-agent-skills) | 1 | MIT |
| [xiongwenhao112/ppt-template-fill](https://github.com/xiongwenhao112/ppt-template-fill) | 1 | MIT |
| [LifelongLazyLearner/qu-ai-wei](https://github.com/LifelongLazyLearner/qu-ai-wei) | 1 | MIT |
| [Fokkyp/SoftwareCopyright-Skill](https://github.com/Fokkyp/SoftwareCopyright-Skill) | 1 | 见仓库 |
| [VioletScar-Hui/Svg-design-system](https://github.com/VioletScar-Hui/Svg-design-system) | 1 | 见仓库 |

本项目对这些技能的收录方式是：**只写说明与出处，不复制技能文件**（Blender 等个别条目除外，均已注明）。若原作者希望调整署名或移除条目，提出即可。

## 免责声明 / Disclaimer

本仓库为个人学习与备赛用途的索引文档，与上述任何原作者、机构无隶属关系。技能的实际功能、适用性与授权范围以原仓库为准。

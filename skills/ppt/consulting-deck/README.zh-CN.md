<div align="center">

# Consulting Deck

### 把复杂材料，做成能交给管理层的麦肯锡风格 PowerPoint

结论先行 · 图表驱动 · 证据可追溯 · 原生可编辑 · 逐页质检

[English](README.md) · [下载真实 Demo](#真实成品不是概念图) · [查看工作流](#完整工作流) · [项目官网](https://www.zhizhuzairui.com/works/consulting-deck)

</div>

<p align="center">
  <a href="examples/ai-value-realization/ai-value-realization-demo.pptx?raw=1">
    <img src="examples/ai-value-realization/renders/slide-03.png" width="100%" alt="Consulting Deck 麦肯锡风格原生可编辑图表页">
  </a>
</p>

<p align="center"><sub>真实生成页面。点击图片可下载原生可编辑 PPTX；示例数据均为模拟数据。</sub></p>

> 咨询风不等于白底、深蓝和细线。真正有用的咨询 PPT，每一页都有明确结论，每张图表都回答一个问题，每个关键数字都能回到来源。

Consulting Deck 是一套用于创建、修改和审计麦肯锡风格咨询 PPT 的 Agent Skill。它先梳理受众、决策问题、证据和故事线，再决定图表与版式，最终交付可以继续修改的 `.pptx`，而不是一组看起来像 PPT 的图片。

## 一眼看懂

| | Consulting Deck |
|---|---|
| 输入 | PDF、Word、Markdown、表格、CSV、网页、研究主题或已有 PPTX |
| 分析 | Evidence Ledger、金字塔结构、SCQA、结论标题、图表规格 |
| 生产 | PowerPoint 原生文字、图表、表格、形状和演讲备注 |
| 修改 | 保留项目真源，只重做受影响页面，不必推翻整套文稿 |
| 验收 | 证据、逻辑、数据、可编辑性和逐页渲染检查 |
| 输出 | 可编辑 `.pptx`、完整项目工作区和交付说明 |

## v0.3：不只生成图表，还核验图表

| 新能力 | 对用户的价值 |
|---|---|
| 8 类分析页面，6 种原生图表组件 | 趋势、排名、对比、构成、调研分布、双图与小多图，都有明确的数据和排版规则 |
| 导出后的真实数据核验 | 对照项目数据，检查 PPTX 中的分类顺序、系列名称、数值和内嵌 Excel 数据，发现不一致就阻止交付 |
| 文案只维护一份 | 标题与关键解释可集中保存；换版式不换结论，也不产生多份互相矛盾的文案 |
| 难页先试，再定稿 | 根据图表数量、数据量和文案长度筛选可用版式，用同一份内容生成少量真实候选，不靠缩小字号硬塞 |
| 修改后的重新核验 | 源数据或 PPTX 改动后，旧检查记录失效，必须重新检查 |

这些能力用于支持的原生组件页面；其他页面仍由宿主 Agent 的演示工具制作和检查。具体规则与调用方法见 [原生图表组件指南](references/native-exhibits.md)。

## 30 秒开始

先检查仓库内容和安全边界，再把它复制或链接到 Agent 使用的 Skill 目录：

```bash
git clone https://github.com/zairuilab/consulting-deck.git
```

常见目录：

```text
~/.agents/skills/consulting-deck
~/.codex/skills/consulting-deck
~/.claude/skills/consulting-deck
```

然后直接交付材料和任务：

```text
使用 Consulting Deck，把这份行业报告做成 12 页、阅读型的麦肯锡风格咨询 PPT。
先提炼整套核心结论，再重建影响判断的关键图表。
所有重要图表保持 PowerPoint 原生可编辑，并在备注中保留来源和页码。
生成后逐页渲染，修复溢出、遮挡、错误换行和兼容性问题。
```

## 真实成品，不是概念图

<table>
  <tr>
    <td width="50%">
      <a href="examples/ai-value-realization/ai-value-realization-demo.pptx?raw=1">
        <img src="examples/ai-value-realization/renders/slide-05.png" alt="AI Value Realization 咨询 PPT 示例">
      </a>
    </td>
    <td width="50%">
      <a href="examples/retail-banking-growth/retail-banking-growth-demo.pptx?raw=1">
        <img src="examples/retail-banking-growth/renders/slide-05.png" alt="Retail Banking Growth 咨询 PPT 示例">
      </a>
    </td>
  </tr>
  <tr>
    <td valign="top">
      <strong>AI Value Realization</strong><br>
      围绕“AI 价值并不平均分布”建立证据链，把组合取舍、规模化障碍和 90 天行动方案连成一条管理层故事线。<br><br>
      <a href="examples/ai-value-realization/ai-value-realization-demo.pptx?raw=1">下载可编辑 PPTX</a> ·
      <a href="examples/ai-value-realization/montage.png">查看全部 6 页</a>
    </td>
    <td valign="top">
      <strong>Retail Banking Growth</strong><br>
      围绕“主要关系比获客规模更能解释增长差距”展开分析，依次呈现客户经济性、旅程流失、客群优先级和增长动作。<br><br>
      <a href="examples/retail-banking-growth/retail-banking-growth-demo.pptx?raw=1">下载可编辑 PPTX</a> ·
      <a href="examples/retail-banking-growth/montage.png">查看全部 6 页</a>
    </td>
  </tr>
</table>

两套示例均使用模拟数据，不代表真实行业基准或预测。仓库保留最终 PPTX、逐页渲染图、整套预览和可复现的生成源码。

| 已验证项目 | AI 示例 | 银行示例 |
|---|---:|---:|
| 页面 | 6 | 6 |
| PowerPoint 原生图表 | 4 | 4 |
| 带演讲备注的页面 | 6 | 6 |
| 图片化整页 | 0 | 0 |
| 结构与溢出检查 | 通过 | 通过 |

[查看机器可读的验收记录](examples/qa-summary.json)

### 图表画廊

下面是现有公开 Demo 的真实页面，不是效果概念图。点击即可下载对应 PPTX，查看图表和文字的可编辑对象。

<table>
  <tr>
    <td width="50%"><a href="examples/ai-value-realization/ai-value-realization-demo.pptx?raw=1"><img src="examples/ai-value-realization/renders/slide-03.png" alt="AI 分析图表页"></a></td>
    <td width="50%"><a href="examples/ai-value-realization/ai-value-realization-demo.pptx?raw=1"><img src="examples/ai-value-realization/renders/slide-04.png" alt="AI 规模化分析页"></a></td>
  </tr>
  <tr>
    <td width="50%"><a href="examples/retail-banking-growth/retail-banking-growth-demo.pptx?raw=1"><img src="examples/retail-banking-growth/renders/slide-03.png" alt="银行增长分析图表页"></a></td>
    <td width="50%"><a href="examples/retail-banking-growth/retail-banking-growth-demo.pptx?raw=1"><img src="examples/retail-banking-growth/renders/slide-04.png" alt="银行客群分析页"></a></td>
  </tr>
</table>

公开 Demo 保留已验收的设计版本。v0.3 的新组件另用银行业与 AI 调研数据完成回归验证；未将用户提供的报告或私人验收文件收入公开仓库。

[查看 v0.3 验证范围：24 项测试、14 页、19 张原生图表](examples/v0.3-verification.json)

## 它和普通 AI PPT 工具有何不同

| | 常见 AI PPT 工具 | Consulting Deck |
|---|---|---|
| 起点 | 根据主题套页面 | 从受众、决策问题和证据出发 |
| 标题 | 描述这一页讲什么 | 直接写出这一页的结论 |
| 图表 | 先选样式，再填数据 | 先明确分析问题，再选择图表并标注结论 |
| 证据 | 来源容易丢失 | 关键结论保留来源、页码和证据类型 |
| 交付 | 图片、HTML 或难以修改的页面 | 文字、图表、表格和简单框架尽可能原生可编辑 |
| 修改 | 经常整套重新生成 | 修改项目真源，只重做受影响的页面 |
| 验收 | 文件能打开就结束 | 逐页渲染，检查逻辑、数据、版式和兼容性 |

## 六个核心机制

### 1. 先搭论证，再画页面

先确定整套文稿的核心结论，再安排每一页承担的沟通任务。系统同时检查页面之间的横向逻辑，以及单页内部“结论—证据—含义”的纵向逻辑。

### 2. 把图表作为分析语言

根据比较、趋势、构成、变化、分布和关系等业务问题选择图表。每张重要图表先形成独立规格，明确数据、结论、标注和来源，再进入 PowerPoint 制作。

图表方法参考公开咨询研究和麦肯锡开源的 [Vizro](https://github.com/mckinsey/vizro) 可视化词汇，最终交付以清晰、克制和原生可编辑为准。

### 3. 让重要结论回到原始材料

事实、计算、来源解读和假设分开管理。关键结论能够指向原始文件、具体页码或数据表，避免出现“页面看起来像咨询报告，但数字不知道从哪来”的情况。

### 4. 交付可以继续修改的 PPTX

文字保留为文字，表格保留为表格，常用图表优先使用 PowerPoint 原生图表，矩阵、流程和时间线尽可能使用原生形状。用户可以改标题、更新数据、调整配色，而不是面对一整页截图。

### 5. 保留可复用的项目工作区

证据、假设、故事线、图表数据、页面蓝图和检查记录都留在项目工作区。修改某一页时，系统修改对应真源、重新生成受影响页面并复查整套一致性。

### 6. 交付前逐页检查

生成文件不等于完成。交付前检查来源、结论标题、图表问题、对象可编辑性、字体和版式，并逐页渲染发现溢出、遮挡、错误换行和兼容性问题。

## 完整工作流

```text
明确受众、决策问题和页数
  → 整理证据，必要时建立可证伪的假设
  → 搭建整套故事线和结论标题
  → 为重要图表编写数据、标注和来源规格
  → 确定视觉方向和页面蓝图
  → 通过合适的运行时生成原生可编辑 PPTX
  → 逐页渲染并检查整套一致性
  → 交付文件并说明仍需人工确认的内容
```

完整项目工作区会保留：

```text
brief.json          受众、决策问题、页数和交付约束
evidence.json       来源、页码、事实、计算与假设
storyline.json      整套核心结论和页面顺序
charts.json         图表问题、数据、标注和来源
slides.json         页面蓝图与对象规格
content.json        可选：集中维护标题和关键解释
design-system.json  字体、色彩、栅格和密度
qa/                 结构检查、逐页检查和交付记录
```

## 三种呈现方向

| 方向 | 适合场景 | 特征 |
|---|---|---|
| Research Analytical | 行业研究、白皮书、正式业务复盘 | 高信息密度，强调证据、图表和脚注 |
| Executive Story | 管理层决策、战略方案、客户提案 | 结论集中，页面围绕决策推进 |
| Editorial Keynote | 演讲、发布会、观点表达 | 页面更少，节奏和视觉张力更强 |

每种方向都可以选择阅读型或演讲型密度，也可以接入用户自己的品牌规范和合法持有的 PPTX 模板。

## 支持的任务

- 创建：把 PDF、Word、Markdown、表格、CSV、网页或研究主题做成新演示文稿。
- 修改：基于保存的项目工作区修改指定页面，并重新检查受影响内容。
- 套模板：接入用户自己的品牌规范或合法持有的 PPTX 模板。
- 审计：不改原文件，只检查故事线、证据、图表、可编辑性、版式和渲染质量。

## PowerPoint 运行时

Consulting Deck 把咨询逻辑和 PPTX 生产分开：Skill 负责证据、故事线、图表规格、页面蓝图和质量标准；运行时负责把这些真源转成 PowerPoint 对象。

默认优先使用宿主 Agent 的原生演示能力。需要更深的母版、原生模板填充或 DrawingML 能力时，可以接入经过独立安全审计的 PPT Master 运行时。它是可选适配器，不是捆绑依赖，也不能改写已经确认的证据和故事线。具体边界见 [`references/runtime-adapters.md`](references/runtime-adapters.md)。

### 已验证的环境与边界

| 部分 | 要求与验证范围 |
|---|---|
| 数据编译、版式筛选、PPTX 数据核验 | Python 3.10+，只使用标准库；核验器不依赖生成 PPTX 的工具 |
| 新原生图表组件 | 需要宿主已提供的 Artifact Tool；已验证生成、内嵌工作簿、重新导入与逐页渲染 |
| 其他 PPTX 工具 | 可接入，但须独立适配和验证，不承诺直接运行新组件 |
| PowerPoint / WPS | 保留原生对象；本轮未进行 Office 或 WPS 内的手动编辑测试 |

这不是在线 PPT 编辑器，也不是一条命令就能跨所有 Agent 生成成品的独立应用。图表数据核验不能代替原文核对、分析判断或视觉验收。

开发者可运行本地回归测试：

```bash
python3 -B -m unittest discover -s tests -p 'test_*.py'
node --test tests/test_native_exhibits.mjs
```

## 品牌边界

默认输出采用麦肯锡风格咨询视觉，但品牌层保持中性，不会出现“智珠在睿”标识。只有用户明确选择时，才会启用 Peng 品牌预设。其他用户无需修改核心 Skill，就能换成自己的 Logo、字体、配色或 PPTX 模板。

Consulting Deck 由 **Peng · 智珠在睿** 创建。

## 独立项目声明

Consulting Deck 是独立开源项目，与麦肯锡、BCG、贝恩或其他咨询公司不存在官方关联或背书。它借鉴公开咨询研究中的分析表达方法，不复制咨询公司的 Logo、专有模板或受保护品牌资产。

## 安全与许可

Consulting Deck 不会自动下载依赖、联网搜索或安装第三方运行时。内置脚本只处理本地项目文件和 PPTX 包，不包含遥测、凭据采集、持久化 Hook 或自动网络请求。安全边界见 [SECURITY.md](SECURITY.md)。

本项目采用 [Apache License 2.0](LICENSE)。

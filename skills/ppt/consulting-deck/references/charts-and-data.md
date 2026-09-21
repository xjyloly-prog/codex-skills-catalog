# Charts and data

Read `chart-system.md` first. That file defines the chart-selection taxonomy,
annotation grammar, Vizro integration, and chart QA score. This file focuses on data
fidelity and reconciliation.

## Data contract

For every quantitative slide, keep:

- raw source or extracted table;
- transformation or calculation;
- unit, currency, time range, and denominator;
- source locator;
- chart-ready data;
- reconciliation note;
- intended conclusion.

Do not type chart values directly into slide code when a structured data file can be
used.

## Reconstruct source exhibits

When the supplied PDF, spreadsheet, or deck already contains analytical exhibits:

1. inventory every material exhibit;
2. extract the complete visible data, not only the headline number;
3. preserve category order when it encodes a process or survey response scale;
4. preserve sample size, field dates, unit, denominator, and rounding note;
5. record unavailable or visually estimated values explicitly;
6. use the source chart's analytical question, then improve hierarchy, labeling, and
   editability.

Do not:

- replace a stacked survey chart with one percentage when the response distribution
  matters;
- replace a multi-period comparison with a before/after card when the trend matters;
- omit comparison groups that prove the source's conclusion;
- invent intermediate time-series values from a plotted line;
- reproduce a consultancy logo, footer, or proprietary page chrome.

If exact values cannot be recovered, either use only verified endpoints, reproduce
the source figure as a cited image, or omit the chart. Never present estimated values
as exact.

## Select the chart by question

Use the nine question families in `chart-system.md`: deviation, correlation, ranking,
distribution, magnitude, time, part-to-whole, flow, and spatial. Use matrix charts
for multi-dimensional combinations.

Avoid pie or donut charts for more than five categories. Avoid dual axes unless the
relationship cannot be shown more clearly in two aligned charts. Do not select a
chart merely because the renderer supports it.

## Write the conclusion before styling

Require a one-sentence conclusion for each chart. Then:

- highlight the series, period, or category that proves it;
- mute nonessential context;
- annotate the inflection or gap directly;
- remove legends when direct labels are clearer;
- keep gridlines subtle;
- start a bar axis at zero unless a different baseline is analytically justified and
  clearly disclosed.

## Maintain editability

Use native PowerPoint charts when users may need to:

- inspect values;
- update data;
- recolor series;
- change labels;
- reuse the chart.

Use a native table for exact values. Use an image only when the source visualization
is itself evidence or when the chart type cannot be reproduced faithfully. Never
flatten a routine bar, line, waterfall, or scatter chart.

## Formatting

- Use locale-aware number separators.
- Keep one unit per visual.
- Use `k`, `m`, `bn`, or Chinese units consistently.
- State whether percentages are share, growth, margin, or percentage-point change.
- Use tabular figures for aligned values.
- Round only to the precision required by the decision.
- Show sample size for survey results.
- State forecast, estimate, or actual status.

## Color

Use one focal color and neutral comparison colors. Reserve semantic red and green for
actual risk/negative and positive states. Do not encode meaning by color alone; add
labels, position, pattern, or annotation.

## Reconciliation checks

Before delivery:

- confirm components sum to totals within disclosed rounding;
- confirm start plus bridge drivers equals end;
- confirm percentage shares are coherent;
- confirm chart labels match visible numbers and slide copy;
- confirm the title's claim is supported by the chart;
- confirm the source date and scope are visible or in notes;
- confirm no outdated source is presented as current.
- confirm every chart-ready data file reconciles to the visible source exhibit;
- confirm Research Analytical decks meet the native chart/table threshold in
  `presentation-modes.md`.
- confirm every material exhibit has a matching `charts.json` record;
- confirm category order in the rendered chart matches labels and source order;
- score every material chart using the 14-point chart QA rubric in
  `chart-system.md`.

## Survey data

Include:

- field dates;
- sample size;
- respondent definition;
- geography or sector coverage;
- question wording when interpretation depends on it;
- rounding note when totals do not equal 100%.

Do not compare samples with materially different definitions without disclosure.

## Sources in notes

Add a source block to speaker notes for every non-trivial chart:

```text
[Sources]
- <source title>, <publisher>, <publication date>, <page/figure>, <URL or local file>
- Calculation: <brief transformation>
[/Sources]
```

Adapt the exact syntax to the host presentation capability, but preserve the same
information.

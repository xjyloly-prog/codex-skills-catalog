# Executable native exhibits

Use this reference when a quantitative page can use the first executable subset:
C14, C15, C16, C38, C39, C40, C42, or C43. The other semantic layouts remain valid;
use the host's native authoring route instead of forcing them into this subset.

## What is implemented

- `assets/layouts/native-exhibits.json`: machine-readable type, panel, series,
  category and copy capacity; wide/annotation-rail candidates where appropriate.
- `scripts/exhibit_contracts.py`: local JSON/explicitly mapped CSV data validation,
  source hashes, bound content resolution and common scales for small multiples.
- `scripts/compile_deck.py`: compile canonical inputs into a disposable render plan.
- `scripts/query_native_layouts.py`: capacity-compatible candidates, deduplicated
  by actual geometry. A semantic ID change alone is not a different composition.
- `scripts/native_exhibits.mjs`: original Artifact Tool native chart components;
  the host supplies an already available presentation object and verified font.
- `scripts/verify_chart_data.py`: exported chart categories, series names, values,
  number formats and embedded workbook ranges compared with the source contract.

The Python checks need only Python 3.10+ standard library. The component renderer
has been tested with the OpenAI host's Artifact Tool. It is not a bundled renderer
or an automatic package installer. Other hosts may render the same data contract
with their existing native PPTX runtime and then use the portable data reconciler.
Do not claim untested runtimes, browsers or Office applications are supported.

## Bind business copy once

Create `content.json`:

```json
{"schema_version":1,"items":[
  {"content_id":"T01","text":"The value gap is concentrated in three functions","evidence_ids":["E01"]},
  {"content_id":"I01","text":"Test a focused portfolio before expanding deployment.","evidence_ids":["E01"]}
]}
```

In a slide record use `content_bindings` rather than duplicating the same literal:

```json
{"slide_id":"S01","display_order":1,"layout_id":"C15","selected_variant":"wide",
 "content_bindings":{"action_title":"T01","implication":"I01"},"chart_ids":["CH01"]}
```

Bindings and literals for the same field are mutually exclusive. Evidence remains
in `evidence.json`; numeric data remains in the chart's `data_path`. Renderer plans
and previews are caches, not new business sources. Recompile after any input edit.

## Explicit chart data

```json
{"categories":["IT","Knowledge","Operations"],"unit":"%","value_scale":"percent-points",
 "series":[{"id":"high","name":"High performers","values":[33,31,25]},
           {"id":"other","name":"Other companies","values":[8,7,6]}]}
```

Add `component_type` to its `charts.json` record:

```json
{"chart_id":"CH01","slide_id":"S01","component_type":"comparison",
 "data_path":"data/chart-01.json","unit":"%","display_title":"Scaled deployment",
 "source_locator":"Report, Figure 12, p.12","decimals":0}
```

Supported primitives: `line`, `ranking`, `comparison`, `column`, `stacked`, `survey`.
All retain native PowerPoint data charts and an embedded workbook. Negative ranking
values are allowed; negative stacks require another explicitly designed component.
Missing/non-finite values fail instead of becoming zero. The initial component
route does not support incomplete/gapped series; use a suitable native host chart.

Percent datasets must explicitly choose `percent-points` (33) or `fraction` (0.33).
The renderer applies percentage formatting to fractions. It never normalizes
rounded survey rows. Declare a justified `sum_tolerance` in percentage points,
and keep the rounding caveat visible. The default is 1.1; this first implementation
allows up to 2. A source requiring a larger tolerance needs explicit review or an
alternative host-native route, not silent loosening of the data check.

CSV requires `csv_mapping.category` and `csv_mapping.series` entries containing
`id`, `name`, and `column`; declare `unit` and `value_scale` in the chart spec. Only
workspace-relative data paths are accepted. Symlink and parent-directory escapes
are rejected. Do not use these sample values as factual research.

## Production and review

1. For an all-component deck, set `brief.json.native_component_contract` to `1`.
2. Run `python scripts/query_native_layouts.py PROJECT S03 --seed PROJECT_ID`.
3. Shortlist genuinely different compositions for only the two or three hardest
   pages. Render real PPTX candidates from the same evidence/data/theme. Do not
   default to four variants for every page.
4. Save the chosen `selected_variant` in `slides.json`. Do not store candidate
   copy/data duplicates. If nothing fits, split/rewrite/change the layout rather
   than reducing fonts or dropping required rows.
5. Run `python scripts/compile_deck.py PROJECT --output PROJECT/qa/native-plan.json`.
6. In the host authoring module call `addExhibitSlide(presentation, plan.slides[i],
   {fontFamily, pageNumber:i+1})`. Store each returned `contract`, plus the plan's
   `source_hashes`, in `qa/pptx-contract.json` with a `slides` array.
7. The host must export real native charts with workbook ranges. For newly authored
   complete literal data, its supported workbook snapshot route is appropriate;
   do not replace an existing workbook's formulas or provenance automatically.
8. Run `python scripts/verify_chart_data.py PROJECT/output/deck.pptx --workspace
   PROJECT --contract PROJECT/qa/pptx-contract.json --output
   PROJECT/qa/chart-validation.json` after exporting the final file.
9. Run project validation, structural inspection, host geometry/font checks, and
   full-size visual review on every page. A capacity estimate is not rendered-fit
   proof. Save manual review and compatibility limitations before the final gate.

The delivery gate requires actual chart reconciliation for component decks and
rejects stale input/PPTX hashes. For mixed decks, apply the portable checker to a
complete contract of the supported native charts, document unsupported exhibits,
and retain host-native validation; do not set the all-component flag prematurely.

## Editing and compatibility boundaries

Natural-language changes update canonical content/data, then recompile and rerender
affected pages. Re-run data checks for affected charts and inspect the assembled
deck for coherence. This release does not include a browser WYSIWYG editor or
automatic Office editing; do not imply that it does.

The reconciler supports ordinary native bar/line charts and bounded one-dimensional
A1 ranges in embedded XLSX files. Unsupported chart types, external references,
missing caches or broken ranges are blocked, never labeled verified. It verifies
data preservation, not source extraction, causal interpretation, legibility, or
successful editing in PowerPoint. If application testing is unavailable, say so.

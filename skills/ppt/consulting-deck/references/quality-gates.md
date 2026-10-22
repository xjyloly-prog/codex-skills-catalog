# Quality gates

Read `harness-system.md` first. Machine checks and expert review are complementary:
scripts may block delivery, but scripts alone cannot approve semantic or visual
quality.

Classify findings as:

- **blocker** — do not deliver;
- **warning** — deliver only with explicit disclosure;
- **advisory** — improve when it materially raises quality.

Do not auto-fix a semantic problem with a mechanical layout patch.

## Gate 1 — Evidence

Block delivery when:

- a material number or external claim has no source;
- the source locator cannot be found;
- a hypothesis is presented as fact;
- old data is presented as current;
- a chart calculation does not reconcile;
- the slide contradicts the source.

Check source title, publisher, date, page or figure, sample definition, and any
calculation.

For component decks, run `verify_chart_data.py` against the final PPTX and the
source-bound contract. It compares ordered categories, series names, numeric caches,
percent formats and embedded XLSX ranges; absent/unsupported references fail.
The final gate requires this report and current input/PPTX hashes. Do not substitute
`reconciliation: passed`, object counts, or the mere presence of XLSX files for proof.

## Gate 2 — Storyline

Block delivery when:

- the governing thought is missing;
- the Executive Summary lists topics instead of conclusions;
- slide titles do not form a coherent argument;
- recommendations do not follow from the diagnosis;
- multiple slides repeat the same takeaway;
- the final decision or action is unclear.

Read slide titles alone as an executive memo. Then read each slide vertically to
confirm its evidence proves its title.

## Gate 3 — Slide content

Block delivery when:

- a slide has more than one primary communication job;
- visible copy contains internal planning language;
- the selected layout cannot carry the content;
- a chart's visual emphasis contradicts its conclusion;
- body text is reduced below the production engine's minimum;
- an essential label, unit, date, or denominator is missing.

Prefer shortening, splitting, or changing layout over shrinking.

## Gate 3A — Chart craft

Block delivery when:

- a material exhibit has no `charts.json` record;
- the selected chart family does not match the analytical question;
- category order, labels, units, or annotations do not match the data;
- a multi-dimensional relationship required by the conclusion was removed;
- a default Office chart remains visually unedited;
- chart marks are colorful but analytically undifferentiated;
- a legend forces unnecessary eye movement when direct labels are feasible;
- the source, sample, period, unit, or rounding note is missing;
- a Vizro or Plotly preview was flattened into the final PPTX without explicit
  approval.

Score every material chart using `chart-system.md`. Require at least 12/14 for
internal delivery and 13/14 for public examples.

## Gate 4 — Structural PowerPoint

Block delivery when:

- the PPTX package is corrupt or triggers a repair warning;
- required slides or notes are missing;
- text-heavy slides are flattened as images;
- editable charts or tables were unnecessarily rasterized;
- a template master or layout hierarchy was broken;
- a font substitution makes key text overflow or disappear.

Run `scripts/inspect_pptx.py` as a portable structural check. Use the host's stronger
inspection tools when available.

For Research Analytical mode, compare the delivered package with the planned
exhibit inventory. A 10–12 slide deck must include at least six evidence-led pages
and at least five pages with native charts or tables. Block delivery when a
material multi-dimensional source exhibit was replaced by a hero number or generic
cards without an explicit analytical reason.

## Gate 5 — Visual rendering

Render every slide. Inspect every page individually at full size and use a contact
sheet only for deck-level rhythm.

Block delivery for:

- overlap, clipping, or off-canvas content;
- unintended title wrapping;
- unreadable chart labels or source notes;
- blurred or distorted images;
- broken glyphs or missing characters;
- inconsistent margins, footer, or page numbering;
- connectors crossing labels or shapes;
- an empty region caused by a failed asset or layout.
- category labels visually aligned to the wrong horizontal bars or segments.

Inspect at the final aspect ratio and with the fonts available on the target system.

## Gate 6 — Deck coherence

Check:

- at least five distinct semantic layouts in a 7–9 slide deck;
- at least seven distinct semantic layouts in a 10–15 slide deck;
- no three consecutive slides with the same silhouette;
- consistent title, source, annotation, and page-number bands;
- intentional alternation between proof and synthesis;
- a controlled number of signature/metaphor pages;
- one coherent visual system rather than a collage of styles.

For Research Analytical mode, also check:

- 60–80% of content pages are exhibit-led;
- analytical pages use a conclusion title, dominant exhibit, annotation,
  implication, and source band;
- covers, dividers, and synthesis pages do not overwhelm the report grammar;
- source dimensions, units, periods, and rounding notes remain visible.

## Gate 7 — Deliverability

Confirm:

- final filename and path;
- page count and aspect ratio;
- language;
- editability;
- source-note coverage;
- speaker notes where requested;
- known font substitutions;
- compatibility target actually tested;
- project workspace retained for future revisions.

Deliver only the final deck and a concise summary by default. Keep scratch renders,
preview variants, and QA ledgers inside the project workspace.

## Final machine-readable decision

Before delivery:

1. save `scripts/validate_project.py` output to `qa/project-validation.json`;
2. save `scripts/inspect_pptx.py` output to `qa/pptx-inspection.json`;
3. complete every boolean in `qa/manual-review.json`;
4. run `scripts/finalize_gate.py`;
5. read `qa/final-gate.json`.

Only `"passed": true` authorizes delivery. A missing file, non-boolean manual review
field, failed structural check, or project blocker must produce `"passed": false`.
Warnings may pass only when they are explicitly listed in `warnings_accepted`.

## Acceptance rubric

Score each dimension from 1 to 5:

| Dimension | 1 | 3 | 5 |
| --- | --- | --- | --- |
| Decision clarity | Topic dump | Main point visible | Clear decision and implications |
| Storyline | Disconnected | Mostly coherent | Titles read as a persuasive memo |
| Evidence | Unsupported | Mostly sourced | Traceable, reconciled, appropriately qualified |
| Visual hierarchy | Crowded or empty | Readable | Immediate focal point and disciplined hierarchy |
| Consulting craft | Generic template | Some semantic layouts | Layout and chart choices encode the argument |
| Editability | Flattened | Mixed | Core objects natively editable |
| Consistency | Mixed styles | Mostly consistent | One coherent system with deliberate rhythm |
| Revision readiness | Final file only | Partial source | Saved project with stable slide and evidence IDs |

Require:

- no blockers;
- no dimension below 4;
- average score at least 4.3 for public examples.

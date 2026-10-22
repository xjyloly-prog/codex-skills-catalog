# Consulting deck workflow

Follow the stage and gate contract in `harness-system.md`. The numbered workflow
below expands those stages; it does not authorize skipping their saved outputs.

## 1. Frame the communication job

Capture:

- target audience and their prior knowledge;
- decision or action expected after reading;
- presentation mode: research-analytical, executive-story, or editorial-keynote;
- speaker-led or reading-first mode;
- source boundary and freshness requirement;
- analysis route: source-synthesis or problem-solving;
- language, page count, aspect ratio, deadline, and compatibility target;
- brand or template constraints.

Ask only for information that changes the result. Infer low-risk defaults and record
them in `brief.json`.

For a problem-solving route, read `problem-solving-system.md`, define the problem
boundary, build the issue tree, and create `hypotheses.json` before broad research.
For source-synthesis, start from the supplied source's exhibit and argument structure.

## 2. Extract and classify evidence

Inspect every supplied file. For PDFs and existing decks, review both extracted text
and every rendered page that contains a potentially useful exhibit.

Create an exhibit inventory before writing the storyline:

- source page and figure number;
- source conclusion;
- chart or table type;
- categories, periods, units, sample, and denominator;
- chart-ready values and any extraction uncertainty;
- whether to reproduce, combine, move to appendix, or omit;
- reason for omission when the exhibit is material.

Create `charts.json` for selected exhibits using `chart-system.md`. Separate:

- analytical question and conclusion;
- chart family and subtype;
- data path and source locator;
- encoding and focal marks;
- annotation plan;
- renderer and editability target;
- reconciliation status.

Use Vizro's Visual Vocabulary to expand the candidate set for complex analytical
questions. Do not make Vizro a mandatory runtime dependency and do not flatten its
output into PowerPoint by default.

For a data-rich source, do not treat representative page review as sufficient. Review
all exhibit pages and select the presentation mode using `presentation-modes.md`.

Create an evidence ledger with:

- `evidence_id`;
- claim or data point;
- source file or URL;
- page, table, figure, or section locator;
- publication date;
- evidence type: fact, data, quotation, interpretation, or hypothesis;
- freshness status;
- intended slide IDs.

Keep old source data when the user asks for a faithful summary, but label the source
date clearly. Research newer evidence only when the user requests a current view or
when the communication job requires current facts.

## 3. Build the governing thought

Write one sentence that combines:

- situation;
- decisive insight;
- implication;
- recommended response.

Test whether an executive could understand the deck's position from this sentence
alone. If not, sharpen it before planning slides.

## 4. Design the storyline

Use `storyline-system.md`.

Create:

- the audience question;
- the governing thought;
- 3–5 supporting arguments;
- a slide sequence;
- an evidence mapping;
- an appendix plan.

For each slide, also record `generation_phase`, `requires_slide_ids`, and
`display_order`. Validate the dependency graph before production. Generate in
dependency-safe order even when the Executive Summary appears near the beginning of
the delivered deck.

In Research Analytical mode, map at least one source exhibit to every evidence-led
slide before creating conceptual frameworks.

Write every slide title as an answer, not a topic label. Mark any title that remains a
hypothesis.

## 5. Choose visual direction

If the user has not locked a visual direction, create three representative mini-sets:

- cover;
- analytical/data page;
- framework/action page.

Use authentic content from the source. Present the three sets as rendered images or
slides outside the final deck. After selection, record design tokens and the chosen
signature device in `design-system.json`.

## 6. Map content to semantic layouts

For every planned slide, record:

- slide ID;
- action title;
- communication job;
- selected layout ID;
- evidence IDs;
- chart or diagram type;
- exhibit type and chart-data path;
- whether a native chart or table is expected;
- visual asset needs;
- speaker-note purpose;
- overflow risk.
- generation phase, display order, and cross-slide prerequisites.

For every chart slide, link exactly one or more `chart_id` values from `charts.json`.

Use the capacity limits in `layout-library.md`. Split a slide when the content exceeds
the chosen layout's capacity.

## 7. Produce a method sample

Create the cover, Executive Summary, three representative exhibits, and one
framework/action slide first. Render them and check:

- hierarchy;
- title treatment;
- chart and label readability;
- information density;
- source treatment;
- visual consistency;
- editability.

For Research Analytical mode, the three exhibit samples must include:

- one routine native chart;
- one dense multi-series chart;
- one complex chart or matrix when the source requires it.

A hero metric does not satisfy an exhibit sample.

Fix system-level problems before producing the rest of the deck.

## 8. Produce the full deck

Create the remaining slides using the approved design system. Keep:

- content source files;
- chart data;
- generated code or structured slide spec;
- visual assets;
- notes;
- rendered pages;
- QA reports.

Do not place planning comments or internal workflow labels on audience-facing slides.

## 9. Run quality gates

Apply `quality-gates.md` in order:

1. evidence;
2. storyline;
3. slide-level content;
4. structural PPTX;
5. visual rendering;
6. deck-level coherence.

Fix all blocking issues. Do not merely list them.

Save the machine results as:

- `qa/project-validation.json`;
- `qa/pptx-inspection.json`;
- `qa/final-gate.json`.

Complete `qa/manual-review.json` before running the final gate. Never treat a
conversation-level assessment as a substitute for these artifacts.

## 10. Deliver and revise

Deliver the final PPTX and retain the project workspace. For later edits, update the
saved project source, regenerate affected slides, and re-run affected and final gates.
Record repeatable production lessons in `qa/experience-log.md`; ordinary use must not
mutate the installed Skill.

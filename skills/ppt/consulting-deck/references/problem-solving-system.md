# Problem-solving system

Use this system when the input is a topic, an open business problem, a strategic
choice, or a request that requires original research. Do not force it onto a faithful
summary of supplied source material; use the source's own analytical structure there.

## 1. Select the analysis route

- **source-synthesis** — reconstruct and synthesize supplied evidence without
  inventing a hypothesis tree first;
- **problem-solving** — define a decision problem, decompose it, form falsifiable
  hypotheses, and research to confirm, reject, or qualify them.

Record the route in `brief.json`.

## 2. Define the problem boundary

Write:

- one decision question;
- the decision owner and decision date;
- in-scope and out-of-scope boundaries;
- key definitions and units;
- constraints and non-negotiables;
- success criteria;
- known unknowns.

Avoid vague prompts such as “analyze the market.” Convert them into a decision:
“Should the company enter segment X in market Y within period Z, and under what
conditions?”

## 3. Build the issue tree

Decompose the decision question into mutually distinct branches that are collectively
sufficient for the decision. Prefer two or three levels.

Test each branch:

1. Does answering it change the decision?
2. Can it be answered with evidence?
3. Does it overlap materially with another branch?
4. Is a major decision factor missing?

MECE is a quality test, not a decorative tree. Do not add branches merely to make the
diagram symmetrical.

## 4. Maintain falsifiable hypotheses

Create `hypotheses.json`. Every hypothesis must state what would confirm, reject, or
qualify it.

Required fields:

- `hypothesis_id`;
- `issue`;
- `statement`;
- `rationale`;
- `validation_plan`;
- `confirming_evidence_ids`;
- `contrary_evidence_ids`;
- `status`: pending, supported, rejected, mixed, or untestable;
- `implication`;
- `slide_ids`.

Search for disconfirming evidence deliberately. Do not turn an early hunch into a
slide title until its status and qualification are clear.

## 5. Design analytical pages before production

For every intended analytical page, define:

- question answered;
- working conclusion or hypothesis;
- evidence required;
- chart or table form;
- source plan;
- dependency on other slides or artifacts;
- decision implication.

This is the functional value of a dummy page. Store it in structured workspace files
instead of a large free-form Markdown plan.

## 6. Model slide dependencies

Use stable slide IDs and record:

- `generation_phase`: independent, dependent, synthesis, or appendix;
- `requires_slide_ids`: true prerequisites only;
- `display_order`: audience-facing order.

Examples:

- an Executive Summary is normally `synthesis` and depends on the decisive analysis
  pages even when displayed near the beginning;
- a market-share page may depend on a market-sizing page if it reuses the same
  denominator;
- a section divider has no analytical dependency merely because it appears before a
  section.

The project validator must reject unknown dependencies, self-dependencies, and
cycles. Use the validator's `recommended_generation_order` for production, then
assemble slides by `display_order`.

## 7. Control research

Research by hypothesis and evidence gap, not by page count. For each search:

- state the question;
- prefer primary and authoritative sources;
- record complete source locators;
- capture both supporting and contrary findings;
- stop when additional evidence is unlikely to change the decision.

Do not promise a fixed number of searches per slide. Research depth follows decision
risk and evidence quality.

## 8. Convert findings into the story

After evidence review:

1. update hypothesis statuses;
2. write the governing thought;
3. convert supported or qualified findings into action titles;
4. move rejected hypotheses out of the core story or use them as explicit
   counterarguments;
5. show remaining uncertainty and the decision condition it affects.

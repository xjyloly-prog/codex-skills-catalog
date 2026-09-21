# Workspace schema

Create one saved workspace per deck:

```text
deck-project/
├── brief.json
├── hypotheses.json
├── evidence.json
├── charts.json
├── content.json          # Optional bound business copy for native components
├── storyline.json
├── design-system.json
├── slides.json
├── project-state.json
├── notes/
├── sources/
├── data/
├── assets/
├── src/
├── renders/
├── qa/
│   ├── manual-review.json
│   ├── project-validation.json
│   ├── pptx-inspection.json
│   ├── final-gate.json
│   └── experience-log.md
└── output/
```

Use `scripts/init_project.py` to create the structure.

## brief.json

```json
{
  "project_id": "stable-kebab-case-id",
  "title": "",
  "audience": "",
  "decision": "",
  "analysis_route": "source-synthesis|problem-solving",
  "problem_statement": "",
  "in_scope": [],
  "out_of_scope": [],
  "context": "board|client|workshop|conference|async",
  "deck_mode": "research-analytical|executive-story|editorial-keynote",
  "density": "speaker-led|reading-first",
  "language": "zh-CN",
  "aspect_ratio": "16:9",
  "target_slide_count": 10,
  "source_boundary": "",
  "freshness_requirement": "",
  "brand_profile": "neutral",
  "visual_direction": "executive-classic",
  "production_runtime": "auto|host-native|ppt-master-adapter|pptxgenjs",
  "compatibility_target": "Microsoft PowerPoint"
}
```

`auto` selects an already available runtime that satisfies the contract. It never
authorizes installing a package, enabling network access, or invoking an unaudited
external Skill. When `ppt-master-adapter` is selected, read
[`ppt-master-adapter.md`](ppt-master-adapter.md) and create
`qa/runtime-handoff.json` before execution.

## hypotheses.json

Use this ledger for a problem-solving route. Keep an empty array for a
source-synthesis route:

```json
[
  {
    "hypothesis_id": "H01",
    "issue": "",
    "statement": "",
    "rationale": "",
    "validation_plan": "",
    "confirming_evidence_ids": [],
    "contrary_evidence_ids": [],
    "status": "pending|supported|rejected|mixed|untestable",
    "implication": "",
    "slide_ids": []
  }
]
```

## evidence.json

Use an array of evidence records:

```json
[
  {
    "evidence_id": "E001",
    "claim": "",
    "value": null,
    "unit": "",
    "source": "",
    "locator": "",
    "publication_date": "",
    "type": "fact|data|quotation|interpretation|hypothesis",
    "freshness": "current|source-faithful|stale|unknown",
    "slide_ids": []
  }
]
```

## storyline.json

```json
{
  "audience_question": "",
  "governing_thought": "",
  "narrative_spine": "SCQA",
  "supporting_arguments": [],
  "decision_or_action": "",
  "appendix_plan": []
}
```

## charts.json

Use one declarative record per material chart:

```json
[
  {
    "chart_id": "CH01",
    "slide_id": "S03",
    "question": "",
    "conclusion": "",
    "family": "deviation|correlation|ranking|distribution|magnitude|time|part-to-whole|flow|spatial|matrix",
    "subtype": "",
    "data_path": "data/chart-01.json",
    "source_locator": "",
    "unit": "",
    "period": "",
    "sample": "",
    "encoding": {},
    "focal_marks": [],
    "annotations": [],
    "renderer": "native-pptx|native-shapes|vizro-preview|source-image|svg-fallback",
    "editability": "native-chart|native-shapes|image",
    "reconciliation": "pending|passed|failed"
  }
]
```

Use `vizro-preview` only as an intermediate renderer. Record the final renderer and
editability before delivery.

For executable exhibits, add `component_type`, `display_title`, optional
`sum_tolerance` and `decimals`. Use the explicit dataset schema and `content.json`
bindings in [`native-exhibits.md`](native-exhibits.md). An all-component workspace
sets `brief.json.native_component_contract` to `1`; a mixed/legacy deck does not.
`selected_variant` and `content_bindings` are optional slide fields. Do not store
an `action_title` literal alongside its binding. Keep exact data only in data files.

## design-system.json

Record:

- selected direction and theme asset;
- color tokens;
- fonts and fallbacks;
- grid and margin rules;
- type scale;
- signature device;
- image treatment;
- chart treatment;
- footer and source style;
- approved preview paths.

## slides.json

Use stable slide IDs:

```json
[
  {
    "slide_id": "S01",
    "display_order": 1,
    "generation_phase": "independent|dependent|synthesis|appendix",
    "requires_slide_ids": [],
    "page_role": "orient",
    "action_title": "",
    "communication_job": "",
    "layout_id": "C01",
    "evidence_ids": [],
    "visual_type": "none",
    "exhibit_type": "none|chart|table|chart-table|source-figure",
    "native_chart_expected": false,
    "chart_ids": [],
    "chart_data_path": "",
    "asset_paths": [],
    "speaker_note_goal": "",
    "status": "planned"
  }
]
```

Do not renumber slide IDs merely because pages are inserted or removed. Store display
order separately. `requires_slide_ids` must contain only true production
prerequisites, not every earlier slide in the narrative.

## qa/

Keep:

- structural inspection;
- evidence reconciliation;
- chart-spec validation and chart QA scores;
- storyline review;
- slide-level visual findings;
- deck-level rubric;
- compatibility notes.

Component workspaces additionally keep `native-plan.json`, `pptx-contract.json`,
and `chart-validation.json`. These are disposable/derived checks, not canonical
business content. Rebuild them whenever source hashes change.

Use plain text or JSON for generated intermediates unless the host requires another
format.

## project-state.json

```json
{
  "stage": "S1-contract",
  "completed_stages": [],
  "gate_files": {
    "project_validation": "qa/project-validation.json",
    "pptx_inspection": "qa/pptx-inspection.json",
    "final_gate": "qa/final-gate.json"
  },
  "last_updated": ""
}
```

Update this file after a stage is genuinely complete. When inputs change, move the
stage back to the earliest invalidated point.

## qa/manual-review.json

```json
{
  "evidence_reviewed": false,
  "storyline_reviewed": false,
  "charts_reviewed": false,
  "visual_reviewed": false,
  "coherence_reviewed": false,
  "compatibility_reviewed": false,
  "reviewer": "",
  "reviewed_at": "",
  "warnings_accepted": [],
  "notes": []
}
```

Booleans must reflect completed review, not intent. Keep warnings as explicit,
human-readable strings.

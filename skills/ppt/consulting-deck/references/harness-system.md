# Staged production harness

Use this harness to prevent premature rendering, unverifiable self-approval, and
loss of revision state. The workspace is the source of truth; the final `.pptx` is
one compiled artifact.

## Non-negotiable rules

1. Complete stages in order unless the request is an Audit route.
2. Do not render the full deck before the method sample is approved or explicitly
   waived.
3. Run deterministic checks as scripts and save their JSON outputs.
4. A machine gate checks only what its code can observe. Human review remains
   mandatory for evidence, narrative, chart meaning, and rendered visual quality.
5. Never reinterpret a failing machine gate as passed in prose.
6. Do not create a host-specific dependency unless the user selects that runtime.
   `production_runtime: auto` permits selection among already available runtimes; it
   does not permit installation, updating, bridging, network access, or use of an
   unaudited external runtime.
7. Record stage and gate paths in `project-state.json` so work can resume safely.

## Six stages

| Stage | Purpose | Required outputs | Gate |
| --- | --- | --- | --- |
| S1 Contract | Define decision problem, analysis route, audience, mode, density, scope, and compatibility | `brief.json`, source inventory | Required fields complete |
| S2 Evidence | Extract source evidence or test structured hypotheses, then reconcile exhibits and data | `hypotheses.json`, `evidence.json`, `charts.json`, `data/` | Material claims traceable and chart data reconciled |
| S3 Argument | Build governing thought, storyline, action titles, layouts, exhibit mapping, and dependency graph | `storyline.json`, `slides.json` | `validate_project.py` returns no blockers or cycles |
| S4 Method sample | Prove the visual and analytical system before scaling | approved cover, 3 exhibits, 1 action/framework page, `design-system.json` | Expert review recorded |
| S5 Production | Build the full editable deck and render every slide | `src/`, `.pptx`, `renders/` | Structural inspection returns no blockers |
| S6 Assurance | Review evidence, chart craft, visual quality, coherence, compatibility, and revision readiness | `qa/manual-review.json`, `qa/final-gate.json` | `finalize_gate.py` returns `"passed": true` |

## Machine gates

### Project validation

Run after S3 and whenever evidence, charts, storyline, or slide plans change:

```bash
python scripts/validate_project.py "/path/to/deck-project" \
  --json --output "/path/to/deck-project/qa/project-validation.json"
```

The deck cannot enter full production when `blockers` is non-empty. Warnings require
review and either correction or explicit disclosure.

### Structural inspection

Run after every PPTX build:

```bash
python scripts/inspect_pptx.py "/path/to/deck.pptx" \
  --json --output "/path/to/deck-project/qa/pptx-inspection.json"
```

This detects package and editability signals. It does not replace rendered-page
inspection.

### Final gate

Complete `qa/manual-review.json`, then run:

```bash
python scripts/finalize_gate.py "/path/to/deck-project"
```

Delivery is allowed only when `qa/final-gate.json` exists and contains
`"passed": true`.

## Manual review boundary

The required manual checks are:

- `evidence_reviewed` — claims, locators, dates, calculations, and qualifications;
- `storyline_reviewed` — governing thought and title-only memo coherence;
- `charts_reviewed` — question fit, encoding, labels, annotations, sources, and score;
- `visual_reviewed` — every rendered slide inspected at full size;
- `coherence_reviewed` — deck rhythm, repeated silhouettes, density, and consistency;
- `compatibility_reviewed` — opened or validated against the declared target.

Each field must be a boolean. Add `reviewer`, `reviewed_at`, `warnings_accepted`, and
`notes` for traceability.

## Fast track

For a deck of five slides or fewer with no quantitative exhibit, S2 may use a minimal
evidence ledger and S4 may use one representative content slide. S3, structural
inspection, rendered visual review, and the final gate remain mandatory.

## Resume protocol

On resume:

1. Read `project-state.json`.
2. Verify the listed output and gate files exist.
3. Recompute the earliest invalidated stage from changed source or plan files.
4. Continue from that stage; do not trust conversation memory over workspace state.

## Experience loop

Write only repeatable failures to `qa/experience-log.md`:

- problem and observed artifact;
- root cause;
- correction;
- preventive rule;
- affected stage or gate;
- whether it should become a future Skill update.

One-off content edits do not belong in the experience log.

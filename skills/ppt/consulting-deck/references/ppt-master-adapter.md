# PPT Master runtime adapter

## Purpose

Use an independently installed PPT Master runtime only when the approved deck
contract needs native PowerPoint depth that the host presentation runtime cannot
reliably provide. Typical triggers are native slide-master and layout structure,
direct filling of an existing PPTX template, or DrawingML export from a constrained
SVG authoring route.

PPT Master is an external open-source project, not bundled code and not a second
strategy authority. Consulting Deck owns the evidence, reasoning, storyline, chart
intent, slide order, action titles, source notes, and delivery standard. The adapter
owns only the declared PowerPoint production operation.

## Activation gate

Do not install, download, update, execute, or bridge PPT Master automatically.
Activate this adapter only when all conditions are true:

1. The user has selected or approved the `ppt-master-adapter` runtime.
2. The exact external version or commit has been staged and audited under the
   user's Skill security policy.
3. The audit conclusion is `approved`, its directory hash is registered, and all
   residual risks and allowed domains are recorded.
4. The official attribution, license, sponsor files, and integrity guard remain
   intact. Never patch around or disable the external project's integrity checks.
5. The runtime can operate on the current project without sending source material
   to an unapproved model, image, search, speech, or relay provider.

If any condition is missing, leave `production_runtime` as `auto` or select another
available runtime. Do not degrade to screenshots, HTML, or PDF.

## Input contract

Run `scripts/validate_project.py` before handoff. The adapter may read only the
current deck project's approved production sources:

- `brief.json`
- `evidence.json`
- `charts.json` and referenced local chart data
- `storyline.json`
- `slides.json`
- `design-system.json`
- approved local assets, source extracts, and template files

Treat the following fields as locked:

- slide IDs and display order;
- governing thought and action titles;
- factual claims, values, units, periods, and source locators;
- chart questions, conclusions, and reconciled data;
- brand selection and compatibility target.

The runtime may resolve typography, shape geometry, object grouping, supported
chart implementation, and package mechanics. It may not add unsupported facts,
replace the storyline, silently drop a required exhibit, or convert an editable
object requirement into a flattened image.

## Route mapping

| Consulting Deck job | PPT Master route | Adapter boundary |
|---|---|---|
| Create a new deck | Quick Generate | Skip the external Strategist and confirmation flow. Produce pages from the locked Consulting Deck slide contract. |
| Fill a raw user-owned PPTX template | Fill Native PPTX | Use the template as a native slide library. Consulting Deck still owns page purpose, order, copy, data, and evidence. |
| Apply a reusable Master/Layout workspace | Generate with the approved template workspace | Preserve the declared Master/Layout structure while following the locked slide contract. |
| Add notes, transitions, or narration to a finished deck | Enhance Native PPTX | Run only when the user explicitly requests the enhancement and approves any provider calls. |

Do not use the external default Strategist to create a second storyline after S3.
Do not use its topic-research, web-image search, AI-image generation, TTS, narration,
video, or update scripts unless the user separately requests that capability and its
network and data boundary has been approved.

## Handoff record

Before execution, record the following in `qa/runtime-handoff.json`:

```json
{
  "schema": "consulting_deck_runtime_handoff.v1",
  "runtime": "ppt-master-adapter",
  "external_version": "pinned-version-or-commit",
  "security_decision": "approved",
  "security_record": "/absolute/path/to/audit-decision",
  "route": "quick-generate|fill-native-pptx|template-workspace|native-enhance",
  "locked_files": [
    "brief.json",
    "evidence.json",
    "charts.json",
    "storyline.json",
    "slides.json",
    "design-system.json"
  ],
  "network_enabled": false,
  "allowed_domains": [],
  "status": "ready"
}
```

Use absolute paths only inside the local handoff file. Do not publish local paths,
credentials, provider keys, or private source names in the public repository.

## Output and quality gate

Return the generated PPTX to the Consulting Deck project's `output/` directory and
keep external intermediate artifacts in a runtime-specific subdirectory under
`src/` or `qa/`.

Then:

1. Run `scripts/inspect_pptx.py` and save `qa/pptx-inspection.json`.
2. Confirm the expected native charts, tables, notes, masters, and layouts exist.
3. Render every exported slide from the final PPTX, not only from an intermediate
   SVG or browser preview.
4. Reconcile displayed chart values against `charts.json` and the source data.
5. Complete manual visual and compatibility review.
6. Run `scripts/finalize_gate.py` and deliver only when it reports `passed`.

If the external runtime changes locked content or skips an unsupported object,
repair the adapter input or choose another supported PowerPoint construction. Never
reinterpret a successful file save as a passed delivery gate.

# Runtime adapters

## Purpose

Select a production engine without weakening the delivery contract. The final output
must remain an editable PowerPoint and must be renderable for visual QA.

## Selection order

1. Use a user-supplied native PPTX template through the host's template-following
   workflow.
2. Otherwise use the host's current native presentation capability.
3. When the host cannot provide required native Master/Layout structure, direct
   PPTX template filling, or adequate DrawingML depth, use an independently installed
   and security-approved PPT Master adapter. Read
   [`ppt-master-adapter.md`](ppt-master-adapter.md) before selection or execution.
4. For complex charts, optionally use Vizro and the Vizro Visual Vocabulary as a
   local selection or prototype layer, then rebuild the approved exhibit as editable
   PowerPoint objects.
5. Use PptxGenJS only as a portable fallback.
6. Stop and explain the missing capability if none of the above can create and render
   an editable `.pptx`.

Never substitute HTML, PDF, or full-slide images for a requested PowerPoint.
Never flatten a Vizro preview into the final deck when native charts or editable
PowerPoint shapes can preserve the analytical structure.

Record the selected engine in `brief.json` as `production_runtime` with one of:
`auto`, `host-native`, `ppt-master-adapter`, or `pptxgenjs`. `auto` means choose the
first available runtime that satisfies the deck contract. It does not authorize an
installation or network call.

## PPT Master adapter

PPT Master is optional and external. Consulting Deck does not bundle, fork, install,
update, or execute it automatically.

- Use it only after a separate pinned-version security audit returns `approved`.
- Keep its official license, attribution, sponsor files, and integrity gate intact.
- Use the external Quick Generate route for a new deck so it does not replace the
  already approved Consulting Deck strategy and storyline.
- Use the Fill Native PPTX route only for a user-owned or licensed source template.
- Disable external research, image search, image generation, TTS, narration, video,
  and update operations unless the user explicitly requests and approves them.
- Run Consulting Deck's PPTX inspection, final-PPTX rendering, chart reconciliation,
  manual review, and final gate after export.

Read [`ppt-master-adapter.md`](ppt-master-adapter.md) for the complete handoff
contract and failure policy.

## Vizro adapter

Vizro is an optional chart-prototyping route, not a mandatory runtime dependency.

- Use its visual vocabulary to select a chart family from the analytical question.
- Use declarative chart specifications in `charts.json` as the shared contract.
- Use `vizro.plotly.express` or Plotly graph objects only when a complex exhibit
  benefits from interactive prototyping or faster comparison of alternatives.
- Record the prototype as `renderer: "vizro-preview"` while it is provisional.
- Before delivery, convert it to `native-pptx` or `native-shapes`, reconcile every
  displayed value, and update the renderer and editability fields.
- Do not install Vizro automatically. A runtime installation requires a pinned
  version, isolated environment, security review, and user approval.

## Codex

- Load the installed `Presentations` skill and obey its current hard requirements.
- Use its supported PowerPoint engine, template-following route, rendering helpers,
  overflow checks, and notes/source conventions.
- Treat this Skill as the consulting narrative, visual, semantic-layout, and QA
  layer. Do not override lower-level file-format safety rules.

## Claude Code

- Load the current native `pptx` capability when available.
- Require editable objects, notes, template preservation, page rendering, and visual
  inspection.
- Keep the same project workspace and evidence model described here.

## Generic coding agent

Use PptxGenJS only when Node.js and the package are already available, or after the
user approves installation.

Require:

- a wide 16:9 presentation unless the user specifies otherwise;
- a shared theme and slide masters where supported;
- editable text, shapes, tables, and charts;
- deterministic source files kept with the project;
- a render route using LibreOffice or another available PowerPoint renderer;
- structural inspection of the resulting OOXML package.

Do not download packages or execute remote scripts without user approval.

## Compatibility

Treat Microsoft PowerPoint as the primary validation target. When practical, open or
render a sample in Keynote, WPS, or LibreOffice, but do not claim compatibility that
was not tested. Avoid rare effects, unsupported fonts, or animations when portability
matters.

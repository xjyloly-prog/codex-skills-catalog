# Brand system

## Separation of identities

Keep three identities separate:

1. **Skill identity** — `Consulting Deck by Peng`, created by `Peng · 智珠在睿`.
2. **Deck owner identity** — the user, team, or client presenting the deck.
3. **Source identity** — organizations whose research or assets are cited.

Never place the Skill author's mark in another user's generated deck by default.
Never treat a source publisher's logo as the deck owner's brand.

## Default behavior

Use `assets/brands/neutral.json`. Show no logo or author watermark. Use the selected
visual direction from `assets/themes/`.

## Peng preset

Use `assets/brands/peng.json` only when the user explicitly requests:

- Peng branding;
- 智珠在睿 branding;
- the Peng preset.

The preset may add a small author line or text mark, but it must not overpower the
deck's subject.

## User brand profile

Create a project-level `brand.json` from supplied assets and rules. Record:

- display name;
- logo paths and permitted variants;
- primary, secondary, accent, background, and semantic colors;
- heading, body, and data fonts;
- footer and page-number rules;
- confidentiality labels;
- clear-space and minimum-size constraints;
- forbidden treatments;
- source or license for every asset.

Do not guess logo proportions, recolor a logo without permission, or use unavailable
fonts without recording a fallback.

## Native PowerPoint templates

When a user supplies a `.pptx` template:

1. Inspect every master, layout, placeholder, theme color, and font.
2. Map semantic content to native layouts and placeholders.
3. Preserve the master-layout-slide hierarchy.
4. Avoid overlaying new text boxes on decorative sample slides.
5. Duplicate and edit inherited elements only when the template requires it.
6. Render representative descendants after any master or layout change.

## Brand precedence

Apply rules in this order:

1. user-supplied licensed PPTX template;
2. user-supplied brand profile;
3. explicitly selected Peng preset;
4. neutral default.

Source-report styling may inform a citation or comparison, but it does not override
the deck owner's brand.

# Task-scoped dense slide quality

This extends the existing SVG → native DrawingML → `verify_deck.py` path.
It does not register a template, replace a company Master, bypass selection or
storyline gates, or activate a plugin runtime.

## Authoring

Keep each uploaded company original and recovery copy private. Use the existing
native template owner for PPTX preservation, and the existing CUSTOM review
owner for photographs/sketches. Unreadable values remain marked unknown.
Capture purpose, count, family, role sizes, edit regions and protected regions
together in the current brief; never promote one company's sizes to defaults.

Use actual font files and record their hashes. Do not silently substitute a
missing face. `SamsungOneKorean` now maps both Latin and East Asian slots to the
requested family; this mapping is not font installation or license verification.
Fonts remain unembedded unless a separately verified owner embeds them.

For dense tables, work in this order:

1. Preserve required text, values, merged anchors and protected content.
2. Allocate column widths by content; short identifiers need less width than
   long Korean instructions. Reword only with the user's permission.
3. Calculate row height from wrapped text, paragraph spacing and top/bottom
   padding. Check actual glyph metrics, not character counts alone.
4. Specify all four margins, vertical alignment, thin borders and locked colors.
5. Use `style.line_spacing`, `paragraph_before`, `paragraph_after` in SVG pixels;
   cells may override each value. Omission preserves previous export behavior.
6. Keep compact diagrams inside their assigned region. Four directional native
   connectors around a low rectangle provide a readable editable cycle.

For a task explicitly requesting 14/12/11/9pt, use 18.6667/16/14.6667/12 SVG
pixels. That conversion is task input, not an authoring-wide style policy.

## Final native checks

Place `dense_layout_contract.json` in the private project. `verify_deck.py`
automatically invokes `dense_pptx_quality.py` when that file exists, and saves
`dense_quality_report.json`. Without the contract, older projects keep their
existing validation behavior. Direct-PPTX owners can call the same checker
without adopting SVG planning gates.

```json
{
  "font_family": "SamsungOneKorean",
  "font_files": {
    "SamsungOneKorean": {
      "regular": {"path": "fonts/regular.ttf", "sha256": "verified-file-hash"},
      "bold": {"path": "fonts/bold.ttf", "sha256": "verified-file-hash"}
    }
  },
  "slide_size_pt": [960, 540],
  "slides": [{
    "slide": 1,
    "region_pt": [24, 24, 432, 480],
    "objects": {
      "process-table": {
        "kind": "table", "header_rows": 1,
        "header_pt": 12, "header_max_pt": 12,
        "body_pt": 11, "max_font_pt": 12
      },
      "heading": {
        "kind": "text", "text_equals": "Exact required heading", "font_pt": 14
      }
    },
    "required_diagram_labels": ["Exact label"],
    "minimum_arrow_ends": 4
  }]
}
```

Replace example hashes with real SHA-256 values. Font paths resolve relative
to the contract; keep the fonts private and use host-approved file transport.
Use a unique native shape name or unique exact-text match. Specify every object
that must be checked. Optional table `column_widths_pt`, `row_heights_pt`,
`padding_pt` (left/right/top/bottom), `header_color` and `body_color` bind exact
geometry and colors. Text objects support `color` and `align`.

```bash
python .claude/skills/ppt-master/scripts/dense_pptx_quality.py \
  projects/private/exports/output.pptx \
  --contract projects/private/dense_layout_contract.json \
  --output projects/private/dense_quality_report.json
```

The checker reads final PPTX table grids, merges, margins, point sizes, font
families, autofit, explicit point/percent line spacing, bounds and overlap.
It rejects missing/changed actual font bytes and absent native diagram labels.
Arrow ends with `type="none"` do not count. Design preferences (contrast, line
weight, unspecified line spacing) are separate from mechanical failures.

## Precise spacing, image and layout contracts

Paragraphs support task-required `line_spacing_pt` or `line_spacing_multiple`
(mutually exclusive), `paragraph_before_pt` and `paragraph_after_pt`.
Tables accept these prefixed with `header_`/`body_`, plus `header_align`/
`body_align`. They check actual exported values; they do not change user sizes.
All objects can bind `box_pt: [x,y,width,height]`. `kind: "shape"` checks a native
box; `kind: "image"` checks an embedded editable picture, visible-source aspect
ratio, crop and optional effective `min_dpi`. Set `allow_crop: false` for diagrams
or screenshots whose full content must survive. For other images, a normalized
`protected_source_rect: [x,y,width,height]` can preserve a declared important
source area. Do not invent a safe area for unreadable photo text or faces.

Page-level constraints use exact native object names:

```json
{
  "alignment": [{"objects": ["image-left", "image-right"], "axis": "top", "tolerance_pt": 0.5}],
  "spacing": [{"objects": ["image-left", "image-right"], "axis": "x", "min_gap_pt": 12, "max_gap_pt": 16}]
}
```

Alignment supports left/right/top/bottom/center_x/center_y. Gap objects are ordered
left→right for x and top→bottom for y; omitting max_gap_pt leaves the upper bound
open. Keep background frames out of non-overlap target pairs; these checks do not
understand intentional layering. Rotated/grouped objects, vector images and masks
still need separate review. Image checks do not recognize subject matter or OCR.
An aspect pass is not proof that all important content is visible through a mask.

If font rights are unresolved, `text_metrics: "structure_only"` permits checks
of literal font/size/spacing, grids, margins, geometry and image layout without
reading or installing font files. It reports no actual text width/height result
and explicitly leaves wrapping/clipping unverified. The standalone inspector can
pass those limited checks; **verify_deck.py rejects this mode for final acceptance**.
Default actual-font behavior is unchanged. Do not silently turn on this mode to
avoid a missing font or publish its pass as a final company deck certificate.

## Final application review

For the supplied runtime's Windows native exit problem, reuse the process-checked
CPU review helper and opt-in `verify_deck.py --review-*` path documented in
[renderer continuation](RENDERER_CONTINUATION_20261013.md). It never installs
dependencies/fonts and cannot substitute an unapproved profile or certify a
failed child process. Renderer completion and manual visual review are separate.

Reopen the exported PPTX in the supported renderer with the verified font files.
Inspect all pages at full size, including small cells, Korean wrapping,
alignment, arrows, protected regions and editability. Compare identical source
content before/after; record code-only versus layout changes separately.
Where available, inspect an additional copy in real PowerPoint and verify an
editable table cell, text box and shape can be changed, saved and reopened.
Record this separately from renderer inspection and source compilation.

A geometric pass is an estimate, not PowerPoint certification: inherited theme
fonts/colors, grouped/rotated text, bullets/tabs, shaping, glyph coverage and
unsupported OOXML remain unverified. Only listed targets are inspected. Check
source-package preservation separately through the native owner. The reports
explicitly leave rendered/PowerPoint review false; an operator records actual
application evidence without rewriting these fields as a fabricated success.

Cloud generation can use project-local font bytes and the existing converter
plus supplied renderer. Real Windows PowerPoint requires a Windows host.
An instruction-only GPT plugin still needs an authenticated attachment/model
dispatcher, confirmation callback and private download delivery. A local
function or loopback UI is not evidence of that cloud round trip. No secrets,
private file URLs or company artifacts belong in public source history.

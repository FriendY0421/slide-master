# Measured Korean text and final-render synthetic fixture

This is an explicitly synthetic two-page engineering fixture, not a company
presentation, image reconstruction or registered template. Its task brief has
two total pages and explicit body21pt; the entry-regression brief is a separate
one-page fixture. Nothing silently changes a user's requested count or pt size.

- [Exact fit contract](fit-contract.json) / [task brief](task-brief.json)
- [Actual glyph premeasurement](measured-fit.json)
- [Final editable PPTX](review/korean-fit.pptx)
- [Final long text render](review/slide-1.png)
- [Final long center name / native table render](review/slide-2.png)
- [Regression, source/render hashes, native content and finalization checks](validation-summary.json)
- [Korean operating contract and verified source research](../../../../../../docs/ppt-project/KOREAN_TEXT_FIT_EVIDENCE.md)

The existing `template_preview_pptx.py --visual-only` converter authored manually
written source SVGs. This compatibility preview uses ordinary DrawingML and one
native table; it does not certify a reusable Master/Layout package. The shared
Presentations runtime finalized candidate bytes unchanged and rendered both
pages with registered bundled OFL Pretendard Regular/Bold. Every final image was
individually inspected. There was no observed tofu/clipping/unintended overlap.
Actual ink bounds stayed within declared source margins. There are no media
parts/full-slide raster overlays.

The native table preserves four paragraphs (one synthetic long center name and
three body paragraphs), two mixed runs with bold `2026Q3`, exact copy, body21pt
and16px padding. Table paragraph spacing uses existing native defaults; this is
not a new table-spacing engine. The plain-text page carries explicit line/
paragraph baseline spacing and0.3pt tracking as native text.

Negative prechecks cover height, oversized Korean words, margins, line overlap,
paragraph before/after spacing, missing glyph, unapproved pt reduction, mixed
English/% units and explicit negative tracking. Source tokens are retained.
Overflow asks for user summary/split/spacing-box decisions; no automatic font
shrink, content removal or slide addition occurs.

Pillow actual glyph measurements remain a precheck. Mixed-run fit needs final
rendering; decomposed jamo plus tracking needs shaping review. Actual PowerPoint
opening/Edit Data, arbitrary renderer font support and real company/photo
reproduction remain unverified. No new engine, package install or font install.

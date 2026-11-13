# PPT quality resource review — 2026-11-07

FAH integration is deferred at the user's request. This is primary-source
research, not an engine replacement, installation, benchmark run or release.
Continues PR #14 and the [earlier precision review](PPT_PRECISION_RESEARCH_20261013.md).
Official repository READMEs, relevant source, licenses and model/dataset cards
were read. Upstream branches/cards can change; pin commits/model revisions and
transitive licenses before implementing or measuring any candidate.

## Ranked findings

### 1. PPTAgent / DeepPresenter — borrow artifact-based revision

- [Official repository](https://github.com/icip-cas/PPTAgent),
  [current skill documentation](https://github.com/icip-cas/PPTAgent/blob/master/skills/pptagent/README.md),
  [MIT code license](https://github.com/icip-cas/PPTAgent/blob/master/LICENSE).
- Current skill describes editable PPTX/HTML sources, rendered-page inspection,
  revision and exported-deck review. This closely matches the existing host
  authoring/finalizer route. Useful extension: record region-specific findings
  and verify that each repair actually resolves its finding without modifying
  protected content. A new competing skill/engine is not necessary to try this.
- The repository explicitly separates current development from PPTAgent research
  v0.2.0 and DeepPresenter research v1.1.38. Do not attribute paper scores to the
  newest skill or assume its converters preserve company masters exactly.
- Current skill requires Linux/WSL or macOS, Python, uv, npm and LibreOffice;
  optional external visual-model configurations require separate credentials.
  These are additional dependencies, not capabilities silently supplied by our
  current plugin. Do not run installers or change host model providers.
- [DeepPresenter-9B model card](https://huggingface.co/Forceless/DeepPresenter-9B)
  lists a 9B language model and MIT tag; the card reports no deployed HF inference
  provider. Model weights are not a turnkey converter/private-download service.
  No dense Korean 9/11pt advantage was established here. Defer model hosting.

### 2. AutoPresent / SlidesBench — adapt reference comparison, fix blind spots

- [Official project](https://github.com/para-lost/AutoPresent),
  [MIT code license](https://github.com/para-lost/AutoPresent/blob/main/LICENSE),
  [reference evaluation source](https://github.com/para-lost/AutoPresent/blob/main/evaluate/page_eval.py).
- Provides reference-based text/color/position comparison and reference-free
  assessment. Useful for protecting the untouched/right-hand area and detecting
  changed wording, values, box positions and palette after a repair.
- Important source-level limitation: `parse_blocks` handles text-frame shapes
  and pictures, skipping other shapes. It does not recursively evaluate groups
  or traverse native table cells. `viz_scores` represents an empty metric list
  as N/A while storing 100. Such output must not become an all-clear for our
  complex tables, groups, merges or charts. This was code inspection, not a run.
- Adapt the comparison concept into the existing native inspector; explicitly
  report coverage/unsupported objects and keep unknown distinct from passed.
  Exact protected XML and region visual checks complement approximate scores.
- Full generation setup documents OpenAI API credentials and unoconv. No such
  setup is needed merely to study/adapt the comparison method.

### 3. PaddleOCR / PP-StructureV3 — photo text and coordinate candidates

- [Official toolkit](https://github.com/PaddlePaddle/PaddleOCR) is Apache-2.0.
  Its README describes PP-StructureV3 outputs with text/table-cell coordinates.
  [Official HF collection](https://huggingface.co/collections/PaddlePaddle/pp-structurev3).
- [Korean line recognizer](https://huggingface.co/PaddlePaddle/korean_PP-OCRv5_mobile_rec)
  has an Apache-2.0 card and an explicitly Korean recognition target. This is a
  line-recognition component, not a complete photograph-to-editable-slide system;
  detection, table structure, geometry reconstruction and output review remain.
- Use as an independent transcription/coordinate cross-check, especially for
  decimal points, commas, units and long Korean text. Conflicting or unreadable
  values must be marked for user review rather than guessed or overwritten.
- Published accuracy is on the author's dataset, not our material. Installing
  Paddle dependencies/downloading weights requires a concrete approval bundle
  under the user's current constraints. No company files were sent to HF Spaces.

### 4. PptxGenJS / python-pptx documentation — detailed layout reference

- [PptxGenJS table API](https://gitbrent.github.io/PptxGenJS/docs/api-tables.html)
  documents per-column widths, per-row heights and per-cell formatting.
  [MIT license](https://github.com/gitbrent/PptxGenJS/blob/master/LICENSE).
  This was already reviewed on October 13; it is not a newly implemented feature.
- [python-pptx fit-text analysis](https://python-pptx.readthedocs.io/en/latest/dev/analysis/txt-fit-text.html)
  explains fitting text through font-size adjustment. That behavior must not
  override this task's fixed 14/12/11/9pt policy. Prefer dimensions, margins and
  reviewed reflow; do not automatically shrink fonts or add table pages.
- Treat these as export/layout references. No evidence was collected that an
  engine swap improves Samsung wrapping or preserves arbitrary company masters.

### 5. Zenodo10K — diverse evaluation inputs, per-file rights

- [Dataset card/viewer](https://huggingface.co/datasets/Forceless/Zenodo10K)
  lists about 10.4k PPTX records, with original URLs, checksums and individual
  license fields. The viewer shows many license values; it is not uniformly MIT.
- Useful for selecting a small rights-cleared test corpus covering real tables,
  groups, charts and crowded layouts. Reuse terms, attribution and included
  asset/font rights require file-specific checks before redistribution.
- Do not bulk-import decks into the company's template catalog or treat diverse
  academic slides as evidence of dense Korean corporate-layout quality.

## Lower priority / excluded from direct adoption

- [Microsoft Table Transformer](https://github.com/microsoft/table-transformer)
  provides table-structure research and GriTS evaluation. The upstream repository
  is archived (September 21, 2026). Keep as a comparison reference rather than
  making it a new production dependency without a maintenance decision. OCR,
  Korean font rendering and native PPTX authoring are separate responsibilities.
- [Microsoft MarkItDown](https://github.com/microsoft/markitdown) extracts content
  into Markdown. It can help inventory wording, but text extraction does not
  preserve a company slide master or certify rendering/editability. It is not
  an appropriate replacement for the current editable authoring route.

## Recommended next experiment, not yet performed

1. Preserve the existing owner, quality contracts, approved outlines and fonts.
2. Use a single nonsensitive, rights-cleared mixed fixture: long Korean, 9pt
   notes, 11pt table body, 12pt headers, decimals/units, merged cells, groups,
   images and directional arrows. Preserve an exact baseline and protected area.
3. Add findings/repair correspondence and reference-region/coverage reporting
   to the existing inspector before adding new inference models. Missing checks
   must remain unverified. Numeric strings and protected content must match.
4. Compare identical baseline/changed PPTX exports, reopened renders, native
   objects and actual target-app behavior. Report actual-font vs temporary-font
   results separately. Judge gains on the same fixture rather than demo scores.
5. Only if photo transcription remains a measured bottleneck, prepare an isolated
   PaddleOCR trial with exact versions, model downloads, resource/cost and data
   retention impacts, and rollback (remove trial artifacts, no production swap).

The immediate recommendations above are engineering judgments based on inspected
sources. No downloaded model, public demo upload, third-party installation,
API call, generated PPTX benchmark, font usage, FAH integration, plugin update,
deployment, PR merge or new spending occurred in this research task. Existing
company/Samsung rights and real-user attachment acceptance remain unresolved.

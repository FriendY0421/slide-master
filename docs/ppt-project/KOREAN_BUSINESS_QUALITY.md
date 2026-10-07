# Opt-in Korean business quality profile

This adds explicit evidence checks and a small synthetic comparison to existing
Slide Master font, geometry, visual review and OfficeCLI conventions. It does not
replace the converter, introduce a second production engine, migrate the library,
or change the template/preset/storyline approval sequence.

## Contract and use

The example profile lives at
`.claude/skills/ppt-master/examples/korean_business/profile.json`. It is a
contributor example, not an ACTIVE template or a selectable catalog item. Ordinary
PPT requests still require the existing user selection and approved storyline.
The user explicitly authorized this engineering comparison with synthetic data.

The profile defines page-purpose capacity and role-specific typography. In this
read-close example, titles use 44px, body 28px, table/axis labels 22px, and footnotes
16px. These are example-specific limits. They do not impose 14pt/12pt everywhere
or override a user's company form. For another purpose, create an explicit profile
consistent with the approved spec, rather than reducing its thresholds after an
overflow failure. Reflow, rewrite or split content first.

`required_disclosure` is profile-specific: this fixture requires a synthetic-data
label on every page. A future profile for genuine supplied company material must
use its actual disclosure requirement, never label genuine facts as synthetic.

Each text element declares `data-business-role` and `data-business-width` in
explicit slide coordinates. Each root declares `data-business-page-type`.
`business_quality.py` uses the existing `text_fit` heuristic, and rejects missing
roles, insufficient size, excessive capacity, missing titles/disclosures,
out-of-zone text and canvas overflow. The narrow profile currently rejects
transformed text rather than pretending to measure it. It does not implement
actual-font glyph measurement or automatic collision proof; existing geometry
checks and full rendered review remain necessary.

Exported PPTX checks require the declared native Chart/Table owners, embedded
chart workbooks, exact chart categories/cache values and exact table cells from
source metadata. The shared runtime finalizer separately verifies relationships,
native-table fit, chart caches/formulas against embedded workbook cells, and
first-party import. The example keeps ordinary diagrams as editable DrawingML
shapes. These checks strengthen the evidence boundary of existing capabilities.

This first profile compares category-chart series and unmerged rectangular text
tables. Extend the contract explicitly before applying it to combos, chartEx or
merged/rich-text tables; the broader existing converter remains unchanged.

`--native-charts-and-tables` is now an alias for the fork's existing
`--native-objects`. Both preserve its opt-in behavior and `_native_charts` naming.
Neither guesses data from arbitrary bars, lines or text. Existing markers and
complete metadata are still required. Upstream's whole CLI/template contract is
not imported.

## Reproduce the comparison without installing dependencies

Run from repository root. The example's two workspaces retain full SVG page
sources and explicit Master/Layout/title-placeholder metadata. Baseline files
mechanically fill the unchanged `0578dba` Consulting Clarity content prototype;
the improved workspace hand-authors six different evidence compositions from the
same synthetic facts in `content.json`. This is a targeted comparison, not a
statistical benchmark or a claim that all old templates have been repaired.

```bash
python3 .claude/skills/ppt-master/scripts/svg_quality_checker.py \
  .claude/skills/ppt-master/examples/korean_business/improved/templates --template-mode
python3 .claude/skills/ppt-master/scripts/template_preview_pptx.py \
  .claude/skills/ppt-master/examples/korean_business/baseline \
  -o projects/_smoke_business/exports/baseline.pptx
python3 .claude/skills/ppt-master/scripts/template_preview_pptx.py \
  .claude/skills/ppt-master/examples/korean_business/improved \
  -o projects/_smoke_business/exports/improved.pptx
```

Use a new output filename on each revision. Do not overwrite baseline evidence.
Production decks use `svg_to_pptx.py`, not this template-preview contributor path.

For rendering, read the shared Presentations skill and resolve its supplied
`RUNTIME_NODE`, `RUNTIME_NODE_MODULES`, `RUNTIME_BIN_DIR`, and `RUNTIME_PYTHON`
environment variables exactly as its implementation guide specifies. Run its
artifact-operation marker once before sample creation. Never substitute global
or newly installed packages when this runtime is missing.

The example's `finalize_review.mjs` calls that skill's packaged finalizer on
existing converter output, preserving candidate bytes and writing a distinct
final file. `render_review.mjs` uses the same supported `importPptx`/PNG export API
as the packaged renderer, first registering existing bundled Pretendard
Regular/Bold via artifact-tool's bundled Skia font registry. It writes image and
font hashes. Fonts are SIL OFL 1.1; their existing license remains in
`assets/fonts/Pretendard/LICENSE.txt`. No OS font installation, downloads or
PyMuPDF redistribution is needed. PPTX fonts remain unembedded.

```bash
"$RUNTIME_NODE" .claude/skills/ppt-master/examples/korean_business/finalize_review.mjs \
  projects/_smoke_business projects/_smoke_business/exports/improved.pptx \
  projects/_smoke_business/deliverables/improved.pptx improved "$SHARED_PRESENTATIONS_SKILL_DIR"
"$RUNTIME_NODE" .claude/skills/ppt-master/examples/korean_business/render_review.mjs \
  projects/_smoke_business/deliverables/improved.pptx \
  projects/_smoke_business/improved-render \
  .claude/skills/ppt-master/examples/korean_business/profile.json "$SHARED_PRESENTATIONS_SKILL_DIR"
```

Pass the actual shared skill directory as `SHARED_PRESENTATIONS_SKILL_DIR`.
Repeat with the baseline candidate and `baseline` kind. Rendering does not prove
PowerPoint application compatibility; retain the independent OfficeCLI/PowerPoint
acceptance when available.

## Explicit review and invalidation

Inspect **every final PNG individually** for titles, clipping, overlaps, table
rows, Korean glyphs, axis baselines and facts. A contact sheet checks only sequence
and rhythm. Only then record the actual reviewer, including agent identity when
the agent performed the review. The record is an attestation, not an automated
claim that images were seen or a replacement for user acceptance.

```bash
python3 .claude/skills/ppt-master/scripts/business_quality.py \
  .claude/skills/ppt-master/examples/korean_business/improved/templates \
  --profile .claude/skills/ppt-master/examples/korean_business/profile.json \
  --pptx projects/_smoke_business/deliverables/improved.pptx \
  --render-manifest projects/_smoke_business/improved-render/render-manifest.json \
  --record-review projects/_smoke_business/improved.review.json --reviewer agent:Codex
```

Replace `--record-review ... --reviewer ...` with `--review-record ...` to verify
the receipt. Content, source SVG, source CSS/JSON/Markdown, project design/spec
locks, declared shared inputs, font bytes, final PPTX bytes, manifest or any PNG
change invalidates it. Review all slides again after shared design changes.
Missing/incomplete renders and mismatched font registration fail closed when
review is requested. The non-review command reports `visual_review: false` and
never claims delivery readiness.

For a normal generated project, final `verify_deck.py` now accepts opt-in
`--business-profile`, `--business-review` and `--business-render-manifest`.
It verifies the newest native export against `svg_output/` and requires all three
evidence inputs. Record that receipt from the project's exact `svg_output/`
directory. Existing main-pipeline checks still run. The example's standalone
preview checks do not manufacture normal production gate approvals.

## Reference decisions and remaining boundaries

- [Presenton Template V2](https://github.com/presenton/presenton/blob/main/docs/template-v2.md): page-type content schema and safe text capacity informed the profile. No app, vision calls or source code was imported.
- [PPTAgent task contract](https://github.com/icip-cas/PPTAgent/blob/main/skills/pptagent/references/task-contract.md): shared changes invalidating complete visual review informed byte-bound evidence. No second engine was integrated.
- [Upstream template guide](https://github.com/hugohe3/ppt-master/blob/main/docs/templates-guide.md): preserve the fork's existing native structure rather than attempting unsupported in-place migration.
- [OfficeCLI Korean README](https://github.com/iOfficeAI/OfficeCLI/blob/main/README_ko.md): OfficeCLI remains an independent validation path. It was absent in this cloud; no installation or PowerPoint execution is claimed.

Renderer/PowerPoint differences remain possible. The initial unfilled six-layout
prototype had a title present in source/XML but absent in one runtime image. All
six titles are visible in this filled before/after comparison with registered
fonts, but this does not prove that unrelated unfilled previews or every existing
template have been fixed. Keep the issue scoped and retain a real OfficeCLI or
PowerPoint acceptance before claiming universal compatibility.

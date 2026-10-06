# Template-first follow-up, 2026-10-06

User feedback redirected priority from a three-slide visual redesign to fidelity
with per-task company PPTX/sample/font/point-size/writing rules, two intake modes,
and cloud-first execution portable to another checkout root. No actual company
files were supplied. No final visual style or permanent company default is set.

## Implemented

- `presentation_brief.py` and `schemas/presentation_brief.v1.json`: builtin/custom
  mode, task-only scope, input completeness, grouped missing-only questions,
  explicit confirmation, rule precedence, and optional environment/font probes
  reusing existing preparation helpers. Intake never grants generation approval.
- Guard/router/native-fill instructions now describe the two modes, keeping
  builtin selection/preset/storyline and custom fill-plan approval distinct.
- Opt-in native `template_fidelity` locks source SHA256, editable slots/cells,
  original transitions, fixed text, geometry, paragraph/run styles, dynamic
  fields, retained Master/Layout/theme/media/fonts and slide size. Native XML is
  cloned; original slide content is never flattened into a full-slide image.
- `paragraph_run_texts` edits exact existing run topology, including table cells.
  Analyzer provides the text scaffold and directly assigned font/pt properties;
  inherited values remain explicit unknowns. Strict mode copies original notes
  bytes and retargets only their new slide relationship.
- Separate six-slide **synthetic** fixture and before/after renders are committed
  under `examples/template_fidelity`. Real material stays private; no external
  AI upload or public source-file sharing is authorized.

## Verification

Eighteen positive/rejection cases passed; subsequent final-code rerun preserved
all previously verified PPTX ZIP-part bytes. Invalid point sizes and unconfirmed
input were also rejected. Supported shared Presentations finalizer passed the
six-slide output with native chart/workbook checks and import validation. Source
and output were rendered with the exact existing OFL Pretendard Regular/Bold
bytes; twelve PNGs were individually inspected. Titles preserve 33pt/24pt mixed
formatting; the changed owner cell preserves table style; unchanged slides
2/3/4/6 are pixel-identical. No tofu, overflow or unintended overlap observed.

Fresh Linux checkout-root reproduction, with canonical repo-relative structure,
produced identical native ZIP part bytes. An initial flattened scripts-only copy
failed an existing repo-root helper's depth assumption; this is not a supported
distribution. The successful rerun retained the actual folder structure. The
recipe, brief and committed report contain no machine-specific root paths.
Runtime-contract alignment, generated-stub check, compile and diff check pass.

## Limits / next input

Company PPTX, best sample(s), confirmed font/point-size and writing rules are
still required for company acceptance. Specified styles differing from the
original are intake only: v1 does not silently override them. Strict mode
preserves charts unchanged and rejects data/style edits; existing general fill
supports category/value edits but its stronger chart-style fidelity contract is
not implemented. Image replacement, SmartArt edits, arbitrary inherited font
resolution and duplicated chart editing independence remain outside this narrow
contract. Unusual private theme overrides may fail closed. No broad arbitrary
company template compatibility is claimed.

OfficeCLI/PowerPoint application opening and Edit Data are unverified; no fonts
are embedded. Windows/macOS were not executed. No installs, accounts, servers,
paid APIs, upstream merges, deployments or Actions runs occurred. Library upload
was not retried. Existing four original sample artifacts and PR #6 remain intact.

## Visual research retained

Actual Presenton Momentum/Executive gallery images and official upstream Apple
review/EV strategy thumbnails were inspected. `korean_business/visual_revision_02`
retains the six-slide critique, original reference links/image blob hashes and
one unfinished strategy SVG study. It is explicitly not a three-slide finished
deck, approved company style or registered template. Source logos/facts/code
were not reused. Design research is separate from template fidelity acceptance.

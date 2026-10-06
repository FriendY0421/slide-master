# Generation quality audit and selective improvement plan

Date: 2026-10-06 UTC
Scope: `FriendY0421/slide-master` only. Initial investigation and implementation design.

## Implementation follow-up — 2026-10-06

The subsequent user instruction authorized a minimal profile, synthetic six-page
before/after comparison, local smoke checks and a new draft PR. This follow-up
supersedes the initial report's implementation-pending status below.

Draft PR: https://github.com/FriendY0421/slide-master/pull/10
Branch: `feat/korean-business-quality-20261006`
Implementation commit: `aba622a2a8b2165851f049f1c2f4cbae2909f727`
The PR remains Draft for the explicitly documented desktop acceptance boundary.

- Added an opt-in `business_quality.py` profile/coverage/review check and optional
  evidence arguments on `verify_deck.py`. Existing gates/default behavior remain.
- Added `--native-charts-and-tables` as an alias to the existing fork option;
  retained `--native-objects`, opt-in behavior and output naming.
- Added separate example sources/profile, without modifying library templates
  or registering an ACTIVE deck. Improved layout has explicit roles/capacity,
  shared native Master/Layout/title placeholders, charts on slides 2/3 and
  tables on 5/6. The same synthetic facts are used in the six-page baseline.
- Existing SVG template quality: improved 6/6 PASS, zero errors/warnings.
  Eleven positive/rejection smoke cases PASS, plus source-value/table-cell edit
  propagation to real chart caches, workbooks and tables.
- Shared Presentations runtime: bundled Pretendard registered directly into its
  bundled renderer, no font/dependency installation. Every before/after page
  inspected individually; every filled title visible. KPI axis corrected to an
  explicit zero baseline / 100% maximum after visual inspection.
- Shared finalizer: both decks pass package/layout/import checks; improved native
  chart caches/formulas match embedded Excel cells. Final bytes are unchanged.
  No PowerPoint/OfficeCLI application verification is claimed.
- Review artifacts and hashes:
  `.claude/skills/ppt-master/examples/korean_business/review/`.
  Runbook: `docs/ppt-project/KOREAN_BUSINESS_QUALITY.md`.
- Original unfilled-preview title-loss and stale stable gallery remain scoped
  findings; this small change does not claim to fix every existing preview.
  Existing Draft PR #6 remains untouched. No deployment/Actions/upstream merge.

Research handoff received: current official upstream and OfficeCLI activity,
Presenton page schemas/text capacities, and PPTAgent full-review invalidation
informed selective design. No app integration or third-party implementation was
copied. Source links and the compatibility boundary are recorded in the runbook.

## Baseline and preservation boundary

- Remote fetch and branch enumeration completed. `main`, `origin/main`, and the clean local `work` checkout resolve to `0578dba7ddf56cf5d7024cf574063c4db7332a3e` (2026-08-30, Finalize Slide Design System V3 authority).
- Draft PR #6 remains open on `feat/apps-sdk-template-picker-20260827`, head `142346b10d375c4c9bfd0a2b92a3fb49c1756529`. Its outstanding real-host UI acceptance and its history are separate from generation quality: https://github.com/FriendY0421/slide-master/pull/6.
- Preserve the fork's template/preset/storyline gates, Korean Pretendard preference, company-template lifecycle, registered IDs, native routes, OfficeCLI verification, generated Codex stubs, and MIT notice (Hugo He). Do not merge upstream wholesale or rewrite the picker branch.
- No other workspace repository was read for implementation or modified. No Actions, paid API, new login, app permissions, deployment, dependency installation, or upstream integration was performed.
- No actual company source deck was supplied. Existing templates contain demonstration numbers and unresolved template tokens; these are not company facts. Future comparison content must explicitly identify all numbers as synthetic.

## Current production and review flow

`PPT_REQUEST_GUARD.md` and routing choose the owner. New SVG decks use explicit template/preset evidence, research, an approved storyline snapshot, initialization, design/spec locks, SVG authoring and checks, then DrawingML export. The converter already supports structured Master/Layout/placeholder output and native-object markers. Raw template-fill and finished-PPTX enhancement remain separate OOXML routes.

`verify_deck.py` runs specification, SVG and composition checks, then optionally validates/renders the exported PPTX through OfficeCLI. SVG text and geometry become editable DrawingML shapes. PowerPoint data objects are a distinct capability, enabled by `--native-objects` and explicit `data-pptx-native` metadata; that flag alone cannot infer a data model from arbitrary bars and text.

## Concrete quality causes and evidence

| Finding | Evidence | Consequence and first change |
|---|---|---|
| Design defaults and template geometry have drifted | V3 documents body defaults of 28/34/40px. Consulting Clarity `03_content.svg` still has BODY_2 at 16px and BODY_3–5 at 15px, with a 32px page title. | Improve selected business prototypes and their content budgets together; enlarge text through reflow rather than multiplying every coordinate. Keep source-faithful and explicitly dense report exceptions. |
| Editable shapes do not provide editable chart data | Four inspected business decks have zero native chart/table markers. The exported Consulting Clarity prototype has 0 chart XML parts and 0 `a:tbl` elements, despite preview exporter using `native_objects=True`. | Add semantic native chart/table examples with literal data, dimensions, labels and units, and enforce requested data-object coverage in the resulting package. |
| Existing previews favor repeated panels and weak data semantics | Rendered comparison/content/data pages reuse boxed regions; data chart has decorative trend lines without meaningful axes/units. Data KPI prototype shows `87%`, `92%`, `-5%`; the difference between percentages needs a percentage-point label when used as a difference. | Use a dominant evidence region and contextual annotation; separate example data from reusable carriers and test arithmetic/units. |
| Current structural checks do not establish visual quality | Consulting Clarity and Data Insight Pro each pass 6/6 SVG template checks with zero warnings, while retaining small text and shape-only charts. Template mode intentionally omits a generated project's typography lock. | Add a business-purpose profile to QA with role-aware type checks and requested native object requirements; do not apply body floors to footers and axis labels indiscriminately. |
| Final verification can succeed without rendered evidence | `officecli_checks()` returns no failure/warning when OfficeCLI is absent. Screenshot failure is non-blocking. Composition warnings are not propagated through the nested checker exit code unless it runs in strict mode. | Introduce explicit rendering/review status and a delivery requirement distinct from structural PASS. Retain iteration `--no-render`; final delivery must not claim visual validation without evidence. |
| Approximate fit can miss font and transform effects | `text_fit.py` uses fixed CJK/Latin character-width factors; `design_quality_gate.py` reads local attributes and approximate boxes without full inherited styles/transforms. | Use actual available-font measurement where supported, keep conservative heuristic fallback visibly identified, and check post-export rendering. |
| Font lock is not font availability | Bundled Pretendard OTFs exist, but the cloud's `fc-match Pretendard` resolves to OpenAI Sans and reports unwritable font caches. The PPTX has named Pretendard runs but no embedded font guarantee. | Configure a writable task-local font/cache path from existing bundled fonts for controlled rendering; do not silently substitute a new family. Verify the receiving machine separately. |
| Stable visual gallery is stale | Existing tracked gallery check fails on ten newer deck IDs and their preview links. A fresh gallery generated to `/tmp` passes the same checker. | Regenerate the gallery from the live catalog with its normal tooling after the quality changes; preserve IDs. This is a discovery artifact defect, not evidence that catalog files are absent. |

Across six SVG prototypes per inspected deck, text elements below 24px are: Consulting Clarity 61/74; Executive Boardroom 64/77; Strategy Roadmap 70/81; Data Insight Pro 60/74. These counts include intentionally small chrome and labels and are diagnostic, not a claim that every counted element violates a body rule.

## Baseline checks and supported visual inspection

- `check_runtime_contracts.py`: PASS.
- `template_recommendation_audit.py --source local --template deck:strategy_roadmap --prompt '삼성전자서비스 미래 대응 전략'`: PASS, rank 1.
- `svg_quality_checker.py <consulting_clarity/templates> --template-mode`: 6/6 PASS, zero errors/warnings.
- Same check on Data Insight Pro: 6/6 PASS, zero errors/warnings.
- Existing `template_gallery_markdown.py --source local --check`: FAIL, stale registered previews. Temporary regenerated gallery and subsequent `--check`: PASS.
- No tracked PPTX sample was present. Existing preview exporter generated `/tmp/slide-master-baseline-consulting.pptx`: 6 slides, 1 Master, 4 Layouts; structural export check PASS.
- Shared runtime skill was read at `/opt/codex/skills/builtins/presentations/SKILL.md`, with implementation and finalization guidance. Its supported `container_tools/render_presentation.mjs`, using the supplied runtime environment variables, rendered all six slides to `/tmp/slide-master-baseline-render/slide-1.png` through `slide-6.png`. Every image was inspected individually.
- Visual inspection confirms small supporting type, repeated boxes and decorative evidence. Slide 5's title is absent in the runtime-rendered image although it exists in both SVG and exported slide XML. Treat this as an unresolved rendering/export compatibility issue; do not attribute it to PowerPoint without OfficeCLI/PowerPoint or another supported independent render.
- These are prototype reviews with unresolved tokens, not completed Korean synthetic-content or improvement comparisons. No PowerPoint application inspection was performed.

## Upstream compatibility findings

Official upstream README now documents `--native-charts-and-tables` and a separate native-data output, while this fork implements `--native-objects` and its own output naming. Preserve the existing option contract; any alias/backport must be explicit and regression tested, rather than copying the upstream CLI.

Official upstream template guide now separates Brand/Style/Layout/Deck contributions. It rejects certain legacy packages and states that creating a new workspace does not upgrade the old package in place. This differs from the fork's legacy-flat compatibility and registered-template selection policy. Adopt useful architecture ideas selectively, without replacing the fork's catalog, migration rules, or user approval flow.

Sources checked on 2026-10-06:
- https://github.com/hugohe3/ppt-master/blob/main/README.md
- https://github.com/hugohe3/ppt-master/blob/main/docs/templates-guide.md

Fresh popularity/activity/license comparison from the separate researcher is still pending. Existing V3 star counts are historical checkpoints, not current ranking evidence. No third-party implementation is selected yet.

## Prioritized reusable improvements

1. **P0: make quality evidence honest.** Report structured export, actual native data-object coverage, requested fonts, rendering success and visual inspection as separate results. Missing required evidence blocks final delivery, while contributor diagnostics and iteration remain usable.
2. **P1: Korean business layout recipes.** Improve a small compatible set of business prototypes for executive decisions, quarterly performance, variance analysis, strategic priorities and owner/date/action reports. Favor whitespace, typographic hierarchy and useful evidence over decorative panels. Preserve registered IDs and Master/Layout/placeholder ownership.
3. **P1: native evidence contract.** Reuse the fork's existing marker converter for editable tables and charts, with explicit series/categories/units and package-level coverage validation. Protect literal data and reject missing requested native objects; avoid a new generator engine.
4. **P1: Korean content-fit profile.** Test long Korean titles, mixed Korean/English product names, negatives, large numbers and dense tables. Recommend split/rewrite/reflow before smaller type. A specific one-page 14pt/12pt company report remains an explicit form exception, never a global default.
5. **P2: catalog and reference freshness.** Regenerate real previews/gallery and attach generation-quality metadata only after measured acceptance. Use recent project research to choose targeted tests and layout ideas, with license attribution for any copied code/assets.

## Minimum before/after acceptance plan

Use the same clearly labelled synthetic Korean material for both current-main and improved output; freeze baseline SHA, content, canvas, template/preset and font assets. Create six test pages: executive decision; quarterly performance chart; actual/target variance; strategic roadmap with editable diagram; action report with editable table; long-title/dense-table stress page. Cover and section templates can be reviewed separately. Do not replace baseline evidence with a later exporter output.

| Layer | Minimum acceptance |
|---|---|
| Compatibility | Existing template/preset/storyline gate regressions pass, including rejection paths and legacy resume. Existing registered IDs and structured Master/Layout counts remain valid. Old `--native-objects` remains supported. |
| Content/data | Synthetic disclosure visible; labels, units, actual/target gaps and table arithmetic match frozen inputs. No unresolved production tokens. |
| Editability | Expected chart slide contains a native Chart and its source data; expected table slide contains `a:tbl`; diagram labels/shapes remain editable. Test changing a value and inspect updated evidence. |
| Typography/layout | Role-aware minimums match the chosen delivery purpose and specific form exceptions. Required Pretendard assets resolve; long titles, negative values and table rows fit. No unintended clipping or collisions. |
| Rendering | Render baseline and improved PPTX through the shared supported runtime, inspect every slide at full size and the deck sequence. Resolve the observed title loss through independent supported rendering. Retain rendered images and renderer/version/font evidence. |
| Human comparison | Side-by-side review of message hierarchy, whitespace, legibility, meaningful visual prominence and variation; successful XML checks alone are insufficient. |

## Execution constraints and next handoff

Source-level changes and local checks are authorized. This initial report does not claim that improvements are implemented or accepted. The next implementation should remain small and additive, beginning with validation/evidence and selected templates after researcher recommendations arrive.

OfficeCLI is absent in this cloud, so its actual validation and PowerPoint rendering cannot be claimed. The shared renderer works, but its font fidelity and the missing title need resolution before a reliable visual A/B acceptance. Existing bundled fonts permit a task-local setup without downloading or installing a new dependency. If OfficeCLI installation or an engine replacement becomes necessary, propose it first as requested.

No changes to production engines, canonical skills, picker branch, dependency manifests or repository history were made during this initial audit. Only this report is added to the repository; baseline/export/render logs remain temporary local review artifacts.

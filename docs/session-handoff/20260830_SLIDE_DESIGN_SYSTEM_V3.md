# Slide Master handoff — Design System V3

Updated: 2026-08-30 KST
Status: DESIGN V3 CURRENT ON MAIN

## Resume authority
Repository: `FriendY0421/slide-master`
Workflow/content branch: `main`
Base before this change: `df5af974fa4ddba3846653ae8539a0a89affce88`

Read first on future PPT design/quality work:
1. `docs/ppt-project/DESIGN_SYSTEM_V3.md`
2. `docs/session-handoff/20260830_STORYLINE_LAYOUT_READABILITY_V2.md`
3. this handoff
4. `PPT_REQUEST_GUARD.md`

## What was fixed
The failed real 20-slide test proved two separate issues: Picker host wording could still authorize immediate generation, and technically valid pages could still be visually weak. Design V3 adds a professional composition/readability authority plus machine heuristics, while the Picker runtime is being corrected separately on its Apps SDK feature branch.

Do not solve future density problems by restoring small body text or by increasing card count. Reflow, split, simplify, or increase slide count first.
## Current V3 rules
- body: text 28px / balanced 34px / presentation 40px;
- body line-height: 1.35–1.50x;
- card padding: 28–36px horizontal / 20–30px vertical;
- normal page: 1–3 primary regions;
- text+visual: meaningful visual roughly 35–60% when relevant;
- prefer 60:40 / 65:35 asymmetry except true comparisons;
- 5+ peer cards = warning/restructure; 6+ large rounded cards = error;
- three repeated dense layout signatures = warning;
- cramped multiline body-like text <1.20x = error;
- slide preview and explicit approval remain mandatory before generation.

## External-source policy
GitHub references must normally be >=1,000 stars, actively maintained, and presentation-relevant. Current accepted engineering references: reveal.js, Slidev, Marp, PptxGenJS. Human-readable design authority prioritizes Microsoft, Duarte, Presentation Zen, and established presentation educators such as Presentation Process.

## Validation
- Python compile: PASS.
- `git diff --check`: PASS.
- design-quality good fixture: PASS.
- design-quality card-wall/cramped fixture: expected FAIL.
- GitHub Actions: unused.

## Next acceptance
The next real ChatGPT test must prove both layers together:
`Picker -> template+preset -> WAIT_STORYLINE_PREVIEW -> full editable slide plan -> user edits/approval -> generation -> Design V3 QA -> PPTX`.

Implementation commit: `c23328ebe065edc2854148c72f2b2e5d09759cb1`

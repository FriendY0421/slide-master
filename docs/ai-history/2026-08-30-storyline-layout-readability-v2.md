# 2026-08-30 — Storyline Review + Layout Readability V2

## Trigger
User reviewed `maeumsokai_intro.pptx` and requested larger text, more natural text/image/card placement, better line spacing and inner padding, less cramped card text, less unexplained outer whitespace, and the ability to request 20–30+ slides. User also reported that the previously expected slide-by-slide content preview was being skipped.

## Decision
The fix is not a font-only scale-up. New FriendY decks now use a combined typography + spacing + content-density + storyline-approval contract.

## Typography V2
- Standard PPT recommendations: `text=28px`, `balanced=34px`, `presentation=40px`.
- 24px remains an emergency hard floor for normal non-mirror body text, not the normal recommendation.
- Production presets seed the actual body baseline: business/report presets 34px, Executive Brief/Product Showcase 40px.
- Mirror/source-faithful templates retain their explicit source typography contract.

## Natural layout contract
- Body-bearing card padding: 24–32px horizontal, 18–28px vertical.
- Heading-to-body gap: 14–22px; paragraph/group gap: 10–18px.
- Body line-height: 1.35–1.5×; lead/subtitle: 1.25–1.4×.
- Normal content-page meaningful occupancy target: roughly 72–88% of usable content area.
- Text+visual pages generally give meaningful visuals 35–55% of content area.
- Prefer 1–3 strong regions; do not default to many small equal cards.
- If locked type/spacing does not fit, redistribute/split/add pages before shrinking type.

## User-editable storyline gate
Before initialization/authoring, show every proposed slide with: number, title, core message, 2–5 content points, visual plan, and layout plan. User may add/delete/merge/split/reorder/retitle/rewrite slides or request a different count.

`storyline_gate.py` records the exact approved snapshot with SHA-256. `new_deck_init.py` now requires `--storyline-approval-result` in addition to template/preset evidence. `svg_to_pptx.py` blocks current gate-v3 new-deck export without storyline approval. `validate_spec.py` checks slide count/title/core-message alignment against the approved snapshot.

If the preview is revised after approval, the old approval is stale: show the revised preview and obtain approval again.

## 20/30+ slide policy
Explicit user counts such as 20 or 30 slides are supported. Expand through real topic decomposition, evidence, examples, comparisons, process phases, FAQ, implementation, or appendix material. Do not add repetitive/filler pages; if evidence cannot support the requested count, surface that during preview.

## Acceptance evidence
- 20-slide storyline approval: PASS.
- New-deck init without storyline approval argument: blocked (exit 2).
- Approved 20-slide init: PASS; both gate files written.
- Approved title changed after approval: alignment block PASS.
- 30-slide storyline approval: PASS.
- Gate-v3 export without `storyline_approval.json`: `[storyline-gate] EXPORT BLOCKED` (exit 1).
- JSON/JS/Python parse and `git diff --check`: PASS.
- Production preset picker smoke shows business body 34px and presentation body 40px.
- GitHub Actions not used.

## GitHub implementation
- Implementation commit: `fabf6b60afe99de9114ab8eecb718a4bdfe01438`
- Branch retained: `fix/ppt-layout-spacing-20260830`
- Implementation was fast-forwarded to `main` after confirming remote main had not moved.
- GitHub Actions were not used.

# 2026-08-30 — Slide Design System V3

## Trigger
The real 20-slide `samsung_service_future_strategy_20slides.pptx` test skipped the required slide-by-slide review and produced visually weak slides: small supporting text, repeated card-grid structures, cramped internal text rhythm, and inconsistent use of empty outer space.

## Root-cause split
1. Workflow: the Apps SDK Picker still told ChatGPT to “continue PPT production” immediately after template+preset confirmation, contradicting the newer storyline-approval gate on `main`.
2. Design: existing rules improved typography but did not automatically fail visually valid-yet-weak pages such as card walls, cramped multiline text, tiny decorative imagery, or repeated layouts.

## Authority filter for research
External evidence was deliberately narrowed to mature, widely recognized sources:
- official Microsoft PowerPoint guidance;
- Duarte professional presentation practice;
- Presentation Zen / Garr Reynolds;
- Presentation Process verified YouTube channel;
- GitHub references only when presentation-relevant, actively maintained, and normally >=1,000 stars.

Accepted GitHub engineering references at this checkpoint: reveal.js, Slidev, Marp, and PptxGenJS. Small personal AI-PPT repositories were excluded.
## V3 design formula
- One slide = one assertion + one focal visual + supporting evidence.
- Default body ramp remains 28/34/40px for text/balanced/presentation; 24px is an emergency floor, not a target.
- Body line-height 1.35–1.50x; text-card padding 28–36px horizontal / 20–30px vertical.
- Prefer 1–3 primary regions and asymmetric 60:40 or 65:35 text/visual weight when appropriate.
- 5+ equal rounded cards are a redesign signal; 6+ large rounded cards are a machine-gate error.
- Tiny decorative imagery, a dense center island with unused outer space, and three consecutive repeated dense layout signatures are flagged.
- 20/30+ slide requests are valid when supported by real ideas/evidence; filler remains forbidden.

## Machine enforcement
Added `.claude/skills/ppt-master/scripts/design_quality_gate.py` and wired it into `verify_deck.py` after the existing SVG quality sweep.

Fixture validation:
- readable 2-region / 34px body / 48px line spacing page: PASS;
- 6-card wall with 34px body and 28px line step (0.82x): FAIL with both cramped-spacing and card-wall errors.

`PPT_REQUEST_GUARD.md` and GPTS canonical instructions now treat Picker handoff values `NEXT_STATE=WAIT_STORYLINE_PREVIEW` and `GENERATION_ALLOWED=false` as a hard host-level stop before generation.

GitHub Actions were not used.

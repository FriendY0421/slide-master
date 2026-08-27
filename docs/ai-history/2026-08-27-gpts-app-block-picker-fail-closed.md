# 2026-08-27 — GPTS App Block picker fail-closed authority

## Problem confirmed
A real GPTS request (`삼성전자서비스 천안센터 문제점 PPT`) returned a prose list of template ids instead of the user-approved in-conversation interactive picker.

Root cause was authority drift:
- `PPT_REQUEST_GUARD.md` / `AGENTS.md` prioritized the stable GitHub visual catalog.
- `AI_CONTEXT.md` / `template-selection.md` prioritized inline interactive HTML.
- Selection records did not prove which picker surface had actually rendered.

## Resolution
- ChatGPT/GPTS primary surface is conversation-native App Block / GenUI when available.
- `template_gallery_chat_manifest_v2.py` remains the live picker data contract.
- Self-contained inline HTML and GitHub visual catalog are fallbacks, not primary.
- Lower-priority surfaces require a concrete fallback reason.
- New `picker_surface_gate.py` records visible picker evidence.
- `record_template_choice_v2.py` gate v2 requires picker evidence for recommendation flows.
- Direct user-specified registered templates use `--direct-template`.
- `template_gate.py` preserves legacy v1 records while enforcing v2 evidence for new records.
- The accepted FAH execution contract v1.0 is intentionally unchanged.
- No GitHub Actions were used.

## Expected user-visible flow
`PPT request → FAH → live catalog → App Block/GenUI → card/detail navigation → production preset → final user id → picker evidence → template evidence → generation/QA/PPTX`

Implementation commit: `b0234dd281dd733a5bdbc05a3106e4ddf74df4eb`

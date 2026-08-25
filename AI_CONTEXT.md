# AI Context

This repository participates in FriendY Automation Hub (FAH) control-plane continuity.

- Project ID: `SLIDE_MASTER`
- Repository: `FriendY0421/slide-master`
- FAH capabilities: `GITHUB_MONITOR, DURABLE_AUTHORITY, EXECUTION_CONTRACT`
- Technical source of truth remains this repository.
- `AI_STATE.json` is the machine-readable durable authority used by FAH monitoring.
- Project execution contract: `.fah/execution-contract.json`
- Before meaningful execution, clients must evaluate the declared execution contract through FAH when available, or read the same GitHub contract as fallback.
- A decision other than `ALLOW` or `EXEMPT` must not proceed.
- Existing project-local fail-closed guards remain mandatory as the final enforcement layer.
- GitHub Actions are not implied or enabled by FAH onboarding or contract enforcement.

## Global PPT request entry rule

Whenever FriendY asks to create a new PPT/presentation/slides deck, even without mentioning Slide Master or FAH explicitly, the execution entrypoint is always project `SLIDE_MASTER` in canonical repository `FriendY0421/slide-master`.

Do not begin from upstream `byungjunjang/slide-master`, a generic presentation repository, a host-native slide generator, or an artifact-generation shortcut. Those must not precede or bypass the FriendY FAH Execution Contract.

Required order:

`PPT request → canonical SLIDE_MASTER repository lock → FAH Execution Contract evaluation → scalable two-stage TEMPLATE_SELECTION → final user confirmation → content research/generation → local fail-closed validation → PPTX`

For a new deck, template selection is a blocking user-interaction gate. The **primary selection UI on ChatGPT is the internal card-style gallery in the current conversation**; external HTML/GUI is auxiliary fallback only. Missing selection evidence means execution must stop at `WAIT_USER_ACTION`/blocked state.

### Canonical V2 selection behavior

- Discovery is index-driven through `template_catalog.py`; do not hard-code current template ids/counts.
- Registered Decks and Layouts are both valid selection candidates.
- On ChatGPT, use `template_gallery_chat_manifest_v2.py` semantics.
- When 10+ registered templates exist, Stage 1 must visibly show 10 real registered candidates; Free Design is separate.
- A Stage-1 choice is tentative only.
- Stage 2 must show up to 6 real examples from the tentative template before final confirmation.
- Only after final confirmation may `record_template_choice_v2.py --confirmed` create selection evidence.
- When true clickable cards/buttons are required, use `template_gallery_unified.py` HTML/GUI; do not represent a static image as clickable UI.
- Broken Korean glyphs are never acceptable. If a headless raster host cannot verify Korean font support, use safe English sample tokens inside previews and Korean labels outside the image.
- Legacy Deck-only gallery/V1 manifest remain compatibility/rollback paths only, not FriendY new-PPT execution authority.

Only the documented existing-PPT beautification/direct-PPTX routes may use their contract exemptions.

Read `PPT_REQUEST_GUARD.md` before any presentation research or generation work.

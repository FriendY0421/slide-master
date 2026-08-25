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

A host-required `artifact_handoff` / presentation-preparation call may occur first, but it is **preparation only**. It never authorizes PPT generation and never replaces the FAH `TEMPLATE_SELECTION` gate.

Required order:

`PPT request → host preparation if required → canonical SLIDE_MASTER lock → FAH TEMPLATE_SELECTION → inline interactive HTML gallery → user final selection → template_selection.json → research/generation → local fail-closed validation → PPTX`

## Canonical ChatGPT template-selection UI

The **primary selection UI on ChatGPT is the self-contained interactive HTML gallery rendered inside the current conversation**, matching the user-approved `preview(1).html` behavior.

Production gallery generation uses:

`template_gallery_inline_html.py --source github --purpose "<actual purpose>" --page-size 12 --output <gallery.html>`

Rules:

- Every new PPT request rebuilds the gallery from the latest GitHub `main` Deck/Layout indexes.
- Discovery is index-driven through `template_catalog.py`; never hard-code current template ids/counts.
- Registered Decks and Layouts are both valid candidates and future registered templates appear automatically.
- The HTML is self-contained: registered SVG previews and package-local assets are embedded as data URIs.
- Recommended templates are shown separately but never auto-selected.
- The complete current template library remains accessible.
- The gallery provides search, Deck/Layout filters, and automatic pagination when the library grows; default is 12 cards/page.
- Card click opens an in-page dialog with up to 6 real examples from the exact workspace.
- `이 템플릿 선택` is the final UI confirmation; the selected id is displayed in the HTML and returned to chat by the user.
- Only after the selected id returns in chat may `record_template_choice_v2.py --confirmed` create evidence.
- Missing selection evidence is `WAIT_USER_ACTION`; no research/generation may start.
- External/local browser HTML (`template_gallery_unified.py`) is auxiliary fallback only, not the normal first-choice path.
- Conversation-native static image galleries are secondary fallback only when inline interactive HTML cannot render.
- Markdown `<img>` lists and static PNGs are not valid substitutes for the approved interactive gallery.
- Broken Korean glyphs are never acceptable.

Only the documented existing-PPT beautification/direct-PPTX routes may use their contract exemptions.

Read `PPT_REQUEST_GUARD.md` before any presentation research or generation work.

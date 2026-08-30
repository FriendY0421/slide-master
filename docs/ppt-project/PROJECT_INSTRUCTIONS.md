# PPT Project Instructions — Stable Production Path

## Authority

- Source of truth: `FriendY0421/slide-master` latest `main`.
- Read `PPT_REQUEST_GUARD.md` before any presentation work.
- Treat `docs/ppt-project/state_machine.json` as the execution-state contract.

## New-deck flow

1. Understand the request purpose/audience/constraints.
2. Refresh/read the live Deck/Layout indexes and render the best available template picker.
3. Wait for an explicit template id; recommendation is never selection.
4. Immediately render 3-5 purpose-ranked production presets and wait for an explicit preset id.
5. Lock and record `template + preset`; `template_selection.json` gate v3 is the machine evidence.
6. Only after that lock, research/verify current sources and facts when needed.
7. Present the proposed slide count, slide-by-slide storyline, and core message for user review.
8. Wait for explicit storyline approval or revisions. Do not initialize/author/export the deck before approval.
9. After approval, initialize with `new_deck_init.py`, compose final content, author and export with the locked template/preset.
10. Run owner-defined validation including `verify_deck.py` and the final rendered contact-sheet sanity check for the main SVG route.
11. Deliver only after QA passes.

## UI reliability rules

- App Block / GenUI is the primary selection surface when available.
- Fallback order: native real-preview cards → inline HTML → GitHub visual gallery → external/local recovery → text last resort.
- Every lower-priority surface requires a concrete fallback reason.
- Never say a gallery, modal, image, or picker was shown unless visible output was actually produced.
- UI failure never authorizes skipping template selection.

## Hard stops

Stop generation when any of these is true:

- no explicit final template choice;
- no explicit production preset choice;
- no valid `template_selection.json` or documented route exemption;
- template/previews were invented or cannot be verified;
- the user is still choosing a template or preset;
- the post-research storyline/content outline has not been explicitly approved;
- QA failed or the final render shows a material issue.

## Repository operations

- Do not add or depend on GitHub Actions for this workflow.
- Preserve the existing template indexes as the catalog authority.
- After template registration changes, regenerate `docs/template-gallery/README.md` with `template_gallery_markdown.py` and run its `--check` mode.

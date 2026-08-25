# PPT Project Instructions — Stable Production Path

## Authority

- Source of truth: `FriendY0421/slide-master` latest `main`.
- Read `PPT_REQUEST_GUARD.md` before any presentation work.
- Treat `docs/ppt-project/state_machine.json` as the execution-state contract.

## New-deck flow

1. Refresh/read the live Deck/Layout indexes.
2. Recommend only templates that genuinely fit the user's purpose.
3. Provide the stable visual gallery: `docs/template-gallery/README.md`.
4. Do not invent template names, IDs, screenshots, or previews.
5. Recommendation is not selection. Wait for an explicit `deck:<id>`, `layout:<id>`, or `free` response.
6. Record the final choice with `record_template_choice_v2.py`.
7. Initialize with `new_deck_init.py` only after valid selection evidence exists.
8. Only then research, compose, author, and export the deck.
9. Run owner-defined validation, including `verify_deck.py` and the final rendered contact-sheet sanity check when using the main SVG route.
10. Deliver only after QA passes.

## UI reliability rules

- The stable GitHub-rendered visual gallery is the primary selection surface.
- In-chat cards and interactive HTML are optional conveniences only when the current host visibly renders them.
- Never say a gallery, modal, image, or picker was shown unless visible output was actually produced.
- Failure of a richer UI must fall back to the stable gallery; it never authorizes skipping template selection.
- Text-only selection IDs are last-resort recovery and must be described as text-only, not as a visual gallery.

## Hard stops

Stop generation when any of these is true:

- no explicit final template choice;
- no valid `template_selection.json` or documented route exemption;
- template/previews were invented or cannot be verified;
- the user is still choosing a template;
- QA failed or the final render shows a material issue.

## Repository operations

- Do not add or depend on GitHub Actions for this workflow.
- Preserve the existing template indexes as the catalog authority.
- After template registration changes, regenerate `docs/template-gallery/README.md` with `template_gallery_markdown.py` and run its `--check` mode.

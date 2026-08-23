---
description: Mandatory template-selection gate for new Slide Master deck generation
---

# Template Selection Gate

This repository requires an explicit template choice before any **new deck generation** begins.
The goal is simple: users must see what is actually available, inspect a representative preview,
and choose the visual system themselves instead of silently falling into free design.

## Scope

Apply this gate to:
- topic-only decks that will enter `topic-research` and then the main SVG pipeline;
- decks generated from PDF, DOCX, URL, Markdown, spreadsheet, conversation text, or other source material;
- PPTX used as re-architectable source material when slide count/order may change.

Do **not** apply this gate to:
- `ppt-template-fill` (the supplied PPTX is already the template);
- strict 1:1 `beautify-pptx` (the source deck is the visual reference);
- `native-enhance-pptx` (content/layout remain stable);
- resume/continue operations for a project that already has a confirmed template decision.

## Mandatory behavior

1. Read `templates/decks/decks_index.json` live. Never use a hard-coded catalog.
2. List **every currently registered deck template** plus `Free Design`.
3. Mark up to three content-relevant templates as `Recommended`; recommendations never auto-select.
4. Show each deck's display id/name, one-line summary, and workspace path.
5. When a visual picker is available, show the existing SVG card preview from
   `/api/template_preview/<deck_id>` before confirmation.
6. Hard stop until the user chooses one option.
7. A valid deck id/workspace path already named in the user's request counts as the user's selection;
   acknowledge it and continue without asking the same question again.
8. After a deck id is selected, resolve it to the exact registered workspace path and hand that
   user-confirmed path to main Step 3. This must not trigger a second template-choice prompt.
9. `Free Design` is allowed only when the user explicitly chooses it.

## Preview contract for newly registered templates

A library deck is not selection-ready until:
- it is present in `decks_index.json`;
- `<workspace>/templates/design_spec.md` exists and declares `kind: deck`;
- `<workspace>/templates/` contains at least one SVG;
- the lexicographically first SVG is a representative, self-contained preview shell (normally
  `01_title.svg` or `01_cover.svg`) with normal `{{TOKEN}}` placeholders where sample text is needed.

The Confirm UI already renders this first SVG with localized sample copy. Therefore a newly
registered template automatically appears with a preview when it satisfies this contract; no
separate PNG/JPEG thumbnail is required.

## Chat fallback

If the visual Confirm UI cannot be opened, present the same catalog in chat and wait for the user's
choice. Do not skip the gate because previews are unavailable. Mention that the visual preview is
available in the local Confirm UI when the host supports it.

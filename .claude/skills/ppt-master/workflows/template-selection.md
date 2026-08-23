---
description: Mandatory template-selection gate for new Slide Master deck generation
---

# Template Selection Gate

This repository requires an explicit template choice before any **new deck generation** begins.
The user must see what is actually registered, inspect representative previews, and choose the
visual system before research, project initialization, SVG authoring, or PPTX generation continues.

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

## Mandatory HTML gallery behavior

1. If the user already named a valid registered deck id/workspace path, treat that as the explicit
   choice and continue without opening the gallery or asking the same question again.
2. Otherwise, launch the standalone HTML picker **before the main generation pipeline**:

```bash
python .claude/skills/ppt-master/scripts/template_gallery.py \
  --source auto \
  --lang <ko|en> \
  --purpose "<short deck purpose>" \
  --recommend <deck1,deck2,deck3>
```

   On Windows, use `python` when `python3` is unavailable.
3. `template_gallery.py` refreshes `origin/main` without checking it out or modifying the working
   tree. The gallery therefore reflects the latest GitHub-registered `decks_index.json` and template
   SVGs. When GitHub is unavailable, `--source auto` falls back to the local checkout and labels the
   fallback visibly.
4. Show **every selection-ready registered deck** plus `Free Design` as 16:9 cards. Mark up to three
   content-relevant decks as `Recommended`; recommendations never auto-select. The UI must clearly
   distinguish **registered template count** from each template's internal **layout count**.
5. Each card uses the deck's first representative SVG for fast scanning. Clicking a card opens a
   large detail gallery with up to **6 representative layout types** automatically selected from
   the registered SVG roster (cover/title, agenda/section, content, data/KPI, comparison/visual,
   closing, with remaining slots filled by other distinct layouts). The user confirms only after
   inspecting these layouts.
6. Hard stop until the picker returns `TEMPLATE_SELECTED=...`. Do not continue because the browser
   was merely opened, and never silently default to Free Design. **The caller must keep the current
   agent task/turn alive while the gallery is open.** If the command host returns control while the
   gallery child process is still running, immediately wait on that process or poll the result file;
   do not end the assistant response with a message telling the user to select and come back later.
7. As soon as `TEMPLATE_SELECTED=...` is returned, **resume the same PPT request immediately in the
   same task/turn**: consume the returned workspace, enter main Step 3, and continue research/design/
   generation without requiring another user message. Only a true timeout, gallery failure, or host
   limitation may break this automatic handshake.
8. After a deck id is selected, resolve its returned `workspace` to the exact registered workspace
   path and hand that user-confirmed path to main Step 3. This must not trigger a second template
   question.
9. `Free Design` is allowed only when the user explicitly chooses it.

## Catalog and user-added templates

The catalog is **not hard-coded**. `decks_index.json` is the discovery source of truth. Therefore a
future user/company template automatically joins the same HTML gallery after it is registered in
GitHub and satisfies the preview contract below. No picker-code modification is required for each
new template.

## Preview contract for newly registered templates

A library deck is not selection-ready until:
- it is present in `decks_index.json`;
- `<workspace>/templates/design_spec.md` exists and declares `kind: deck`;
- `<workspace>/templates/` contains at least one SVG;
- the lexicographically first SVG is a representative, self-contained preview shell (normally
  `01_title.svg` or `01_cover.svg`) with normal `{{TOKEN}}` placeholders where sample text is needed.

The gallery uses the first SVG as the summary-card thumbnail and automatically selects up to six
representative SVGs for the detail view. Selection is semantic by filename and falls back to other
available SVGs, so newly registered company/user templates automatically gain the same multi-layout
preview without picker-code changes. Referenced workspace assets are served through the read-only
asset endpoint. No separate PNG/JPEG thumbnail is required.

## Fast validation / diagnostics

Before release or while diagnosing catalog problems, run:

```bash
python .claude/skills/ppt-master/scripts/template_gallery.py --source local --list
```

This lists only templates that have a usable representative SVG and does not open a browser.

## Chat fallback

If the HTML gallery cannot start or the host is truly headless, present the same live registered
catalog in chat and wait for the user's choice. Do not skip the gate merely because visual previews
are unavailable.

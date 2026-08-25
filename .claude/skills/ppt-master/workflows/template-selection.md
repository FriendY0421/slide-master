---
description: Mandatory template-selection gate for new Slide Master deck generation
---

# Template Selection Gate

This repository requires an explicit template choice before any **new deck generation** begins.
The user must see what is actually registered, inspect representative previews, and choose the
visual system before research, project initialization, SVG authoring, or PPTX generation continues.
[`../../../..//PPT_REQUEST_GUARD.md`](../../../../PPT_REQUEST_GUARD.md) is the short fail-closed
authority for this rule; this workflow owns the detailed picker behavior.

## Scope

Apply this gate to:
- topic-only decks that will enter `topic-research` and then the main SVG pipeline;
- decks generated from PDF, DOCX, URL, Markdown, spreadsheet, conversation text, or other source material;
- PPTX used as re-architectable source material when slide count/order may change.

Do **not** apply the HTML picker to:
- `ppt-template-fill` (the supplied PPTX is already the template);
- strict 1:1 `beautify-pptx` (the source deck is the visual reference);
- `native-enhance-pptx` (content/layout remain stable);
- resume/continue operations for a project that already has a confirmed template decision.

Those exempt routes must still write a documented `template_selection.json` exemption when they
enter any shared generated-deck export path. The purpose is auditability and fail-closed enforcement,
not to force an irrelevant template choice onto a direct-PPTX workflow.

## Mandatory context-aware HTML gallery behavior

1. If the user already named a valid registered deck id/workspace path, treat that as the explicit
   choice and continue without opening the gallery or asking the same question again. Record it with
   `record_template_choice.py` so the project can carry machine-readable selection evidence.
2. Otherwise, launch the standalone context-aware HTML picker **before research or project init**:

```bash
python .claude/skills/ppt-master/scripts/template_gallery_context.py \
  --source auto \
  --lang <ko|en> \
  --purpose "<the user's actual deck purpose/context>"
```

   On Windows, use `python` when `python3` is unavailable. For Korean or other non-ASCII purpose text on Windows, prefer a UTF-8 purpose file and `--purpose-file <path>` instead of embedding the purpose in the shell command. `--recommend` is optional and may add
   already-known registered ids, but automatic context ranking is the default and total recommended
   items remain capped at 10.
3. The picker refreshes `origin/main` through the existing gallery core without checking it out or
   modifying the working tree. The gallery therefore reflects the latest GitHub-registered
   `decks_index.json` and template SVGs. When GitHub is unavailable, `--source auto` falls back to the
   local checkout and labels the fallback visibly.
4. The gallery interprets the user's purpose text and groups the complete catalog by use category,
   including at least: **보고용**, **학습·교육용**, **공지·안내용**, **발표용**,
   **제안·기획용**, **데이터·실적용**, **브랜드·스토리용**, and
   **제품·서비스 소개용**. Future categories may be added through catalog metadata.
5. Show **every selection-ready registered deck** plus `Free Design`. The maintained catalog should normally contain **at least 10** selection-ready registered decks; never hide a smaller catalog behind an invented text-only list. Mark only templates with genuine
   contextual relevance as `Recommended`, up to **10**. This is a ceiling, not a quota: one strong
   match may yield one recommendation; four relevant matches may yield four. Recommendations never
   auto-select. The user still chooses the final visual system.
6. Each card uses a real representative SVG. Clicking a template opens a detail gallery with up to
   **6 representative layout types** selected from the registered SVG roster (cover/title,
   agenda/section, content, data/KPI, comparison/visual, closing, with remaining slots filled by
   other distinct layouts). The user confirms only after inspecting the layouts.
7. Hard stop until the picker returns `TEMPLATE_SELECTED=...`. Do not continue because the browser
   was merely opened, and never silently default to Free Design. **The caller must keep the current
   agent task/turn alive while the gallery is open.** If the command host returns control while the
   gallery child process is still running, immediately wait on that process or poll the result file;
   do not end the assistant response with a message telling the user to select and come back later.
8. As soon as `TEMPLATE_SELECTED=...` is returned, **resume the same PPT request immediately in the
   same task/turn**. Initialize a new main-SVG deck with:

```bash
python .claude/skills/ppt-master/scripts/new_deck_init.py <project_name> \
  --format <format> \
  --template-selection-result <result.json>
```

   Do not use a bare `project_manager.py init` for a new deck. The resulting project must contain
   `template_selection.json` before downstream work begins.
9. After a registered deck id is selected, resolve its returned `workspace` to the exact registered
   workspace path and hand that user-confirmed path to main Step 3. This must not trigger a second
   template question.
10. `Free Design` is allowed only when the user explicitly chooses it. The result is recorded exactly
    like a registered selection, with `template: free` and no workspace.

## Catalog taxonomy and context matching

The catalog is **not hard-coded**. `templates/decks/decks_index.json` is the discovery source of truth.
Every selection-ready deck should declare:

- `primary_category`: its main gallery section;
- `categories`: additional valid use categories;
- `keywords`: user-language terms that identify suitable requests;
- normal display fields such as `display_name`, `summary`, `primary_color`, and `page_count`.

Current stable category ids are `report`, `education`, `notice`, `presentation`, `proposal`, `data`,
`brand_story`, `product`, and `general`. Newly registered templates automatically participate in
context ranking and categorized display when these fields are present. Do not edit picker code for
each new template.

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

Before release or while diagnosing catalog problems, run context examples without opening a browser:

```bash
python .claude/skills/ppt-master/scripts/template_gallery_context.py \
  --source local --purpose "경영진 개선 보고" --list

python .claude/skills/ppt-master/scripts/template_gallery_context.py \
  --source local --purpose "신입사원 AI 교육" --list

python .claude/skills/ppt-master/scripts/template_gallery_context.py \
  --source local --purpose "전 직원 안전 공지" --list
```

Also validate the fail-closed evidence independently:

```bash
python .claude/skills/ppt-master/scripts/template_gate.py validate <project_path>
```

## Chat fallback

If the HTML gallery cannot start or the host is truly headless, present the same live registered
catalog grouped by the same categories in chat and wait for the user's explicit choice. Record that
choice with `record_template_choice.py` before `new_deck_init.py`. Do not skip the gate merely because
visual previews are unavailable, and do not replace a working GUI/HTML picker with a text list for
convenience.

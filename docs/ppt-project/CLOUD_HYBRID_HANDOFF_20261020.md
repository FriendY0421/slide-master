# Notebook-independent Slide Master preparation

Status: local candidate and bounded cloud QA, 2026-10-20. No main merge, plugin
release, server deployment, credentials, access change or new paid resource.
The existing private main plugin remains 0.4.3. Its exact source readback returned
22 files, including the existing four inspector/renderer helpers.

## Architecture and existing owners

- Aro's supplied cloud runtime performs actual pixel analysis, native authoring
  where already routed, finalization and exact-file QA.
- GitHub stores approved public code, public template design assets and sanitized
  evidence. Company source files, photos, fonts, private links and account IDs
  stay out of public commits.
- Existing owner-only Drive stores private originals, outputs and recovery
  copies. A local path or assistant-side download does not prove recipient access.
- Existing main SVG projects retain `svg_to_pptx.py` and `verify_deck.py`.
  Existing native/template-fill projects retain their own owners and gates.
  Approved image-reference reconstruction uses the existing host Presentations
  authoring/finalizer path described in plugin 0.4.3. This candidate introduces
  no new converter, model API, identity provider or dispatcher.
- FAH receives only a proposed review contract. The supplemental contract is
  explicitly disabled and is not a provider registration or runtime release.
  Updating an ordinary project does not authorize persistent credentials or
  automatic self-updating of unsafe providers.

## Template choice without a laptop

The existing approved repository already supports a conversation-native visual
fallback. `picker_surface_gate.py` includes `conversation_native_visual` and
requires a concrete fallback reason for any non-primary surface.
`workflows/template-selection.md` documents the fallback hierarchy and keeps
template, preset and current storyline approval mandatory.

Use the native interactive Picker first when it is actually available and
trusted on the current host. Its old PC-hosted endpoint and tunnel are not
evidence of a migrated cloud service. Do not start a new server merely to keep
the same dropdown UI.

When a PC-independent interactive surface is unavailable:

1. Read the current approved `main` Deck/Layout indices through existing
   authorized repository access.
2. Reuse `template_catalog.py` scoring/selection helpers and the registered
   SVG previews. Never hard-code template IDs/counts into production logic.
3. Show real candidate images in the conversation, then up to six actual
   layouts for the user's tentative choice. A prepared local HTML file does
   not establish that the user saw it.
4. Record the actual visible surface and reason with `picker_surface_gate.py`.
   This records a UI event, not user approval.
5. Obtain the exact template and production-preset choice in the conversation,
   then call the existing `record_template_choice_v2.py`. Do not fabricate a
   user message, callback, actor, selected ID or evidence receipt.
6. Show the current content outline and obtain its approval before authoring.
   If source, outline or requested design changes, prior approval is stale.

For photo reconstruction or source-preserving edits, the source itself is the
design reference. Do not replace it with an unrelated registered template.
Keep the plugin's purpose menu, source/CUSTOM confirmation and route-specific
approval requirements. Original replication does not authorize ACTIVE template
registration or public upload.

Current preparation read `main` commit
`0578dba7ddf56cf5d7024cf574063c4db7332a3e`: 14 deck entries and 7 layout entries,
all currently ACTIVE. A purpose-ranked six-template preview was prepared from
40 actual registered SVGs, with six detail previews per shortlisted template.
These are a dated snapshot, not fixed future IDs/counts. No user selection or
generation approval was recorded, and no new business deck was generated.

## New photo analysis and quality gates

`PHOTO_ANALYSIS_REVIEW_SCHEMA.json` describes the review record, not an
authorization token. It always retains `generation_allowed: false`.

After an actual new input arrives:

1. Use its real host/Drive provenance and actual bytes/hash. Do not call a
   public reference or a local path an authenticated user attachment.
2. The current host model inspects the pixels. Explain font candidates and
   estimated sizes, image/crop positions, colors, spacing, alignment, tables
   and proposed editable objects. Mark unreadable text rather than guessing.
3. Separate observed facts from estimates. A photo-only font estimate cannot
   claim exact identification. Request the original PPTX/PDF, licensed font
   files or original images only when they materially affect fidelity.
4. Keep original wording and numbers. Do not invent company strategy, logos,
   statistics or missing text. Do not flatten the whole slide and call it
   editable. Do not silently substitute, install or embed fonts.
5. Present the source analysis, unresolved differences and current outline
   for real user confirmation.
6. Author with the existing approved owner. Preserve the source and earlier
   outputs. Width/height/padding/spacing fixes precede arbitrary font shrinking.
7. Reopen the exact final PPTX, inspect editable text/table/group/chart
   structure, render every slide and visually compare every page with source.
   Check text clipping, font and size, alignment, crop, resolution, numerical
   content and intended protected areas. Repair through the original owner.
8. Deliver privately and read permission metadata. Check the actual downloaded
   bytes/hash. Ask for recipient opening only when an output exists. Report
   native PowerPoint verification separately from artifact rendering.

## Local executable QA adapter

`scripts/cloud_review_existing.py` links existing checks to a single exact-file
cloud QA invocation. It:

- requires the expected PPTX SHA256 and actual font-file SHA256 values;
- uses only supplied Node/Python/Artifact Tool paths, without installing tools;
- calls existing host package/layout validators, optional existing dense QA,
  and the same reviewed 0.4.3 process-checked renderer;
- rejects a structure-only dense contract for final QA;
- binds each dense face role to actual OpenType weight/style/width metadata and
  its exact SHA256, then requires the renderer profile to contain the same
  unique role-to-file mapping. A SHA set alone cannot detect swapped roles;
- probes the supplied Skia renderer's supported `FontLibrary.use` API and checks
  its per-file weight/style/width/path/hash registration result against the
  same roles. Aggregate family metadata is not used as face proof;
- checks actual dense and renderer receipt paths/hashes against those bindings;
  a registration preflight is not per-run or per-glyph rendering evidence;
- stops on child failure, preserves old receipts, rechecks source bytes and
  writes a new private receipt directory;
- never claims visual review, recipient opening or production approval from
  process success. Those require separate actual evidence.

It is a local source candidate. It is not added to the installed plugin and
does not change the original engine. Font metadata is read using the already
available host fontTools; no dependency or font is downloaded or installed.
The self-test uses small generated two-face font fixtures and isolated inputs,
never calls a real renderer and never records real user approval.

This adapter's dense-font scope is intentionally narrow: static, single-face,
normal-width upright Regular 400 / Bold 700 with consistent style flags.
Variable/collection/indexed, italic/oblique, condensed and ambiguous duplicate
faces fail closed. Package-wide italic declarations and `b="true"` run encoding
are rejected because the unchanged dense checker does not measure them.
Measured table/placeholder runs need an explicit bold flag. Plain text with an
omitted bold flag is accepted only when no body/presentation/master-other-style
bold default applies; inherited bold cannot silently measure as Regular.
These are local QA-candidate restrictions, not changes to the installed engine.

## Current exact-file proof and limits

The previous grouped public-reference v1 remained owner-only in Drive. Its
downloaded PPTX is 20,662 bytes with SHA256:
`49ecb31bedac25b90084a63e30eedc8588504dc0be8a529e718d12f82ba5855c`.

Actual current Aro cloud checks:

- original source hash matches the 2026-10-15 result;
- native structure has two groups with five and three child rectangles,
  one 3-row/2-column table, one note, zero pictures, zero external relationships
  and no embedded font parts;
- package integrity and layout checks pass with zero findings/warnings;
- seven dense text/cell measurements pass with zero mechanical errors and
  zero design warnings, using the repository's licensed OFL Pretendard only;
- the exact file imports and all one page renders with process exit 0;
- current model compared the original PNG and full-page render: words,
  12,345.67, colors, layout and whitespace remain visible without obvious
  clipping. Minor rasterization/edge differences remain.

The candidate adapter's final replay and forty-five isolated safety tests passed.
One initial layout invocation mixed mutually exclusive font-policy options and
was rejected before checking. The corrected source-font-policy invocation
passed; the failed attempt remains in private evidence.

Independent review found two successive P2 gaps: family-only matching permitted
unequal font versions, and SHA-set matching still permitted Regular/Bold roles
to be crossed. The corrected candidate checks actual face metadata and binds
role-specific bytes to the same renderer's per-file registration result.
Both different-version and swapped-role regressions reject before review
processes start, including a negative test using the actual reference fonts.
Identical bytes at another path and misleading filenames remain compatible
when their actual face metadata is correct. Adjacent unsupported italic and
inherited-bold cases now fail closed as documented above. The subsequent
measurement and rendering receipts are checked again against exact paths/hashes.
The existing correct reference was not invalidated: its actual Pretendard role
mapping already matched. The final replay's PNG is byte-identical to the
previously visually reviewed image. No installed inspector/renderer source was
changed. `per_glyph_font_verified` and the renderer's `text_font_verified` remain
false: a registered face mapping does not prove every rendered glyph selection.

This proves current cloud readback/review/recovery of the existing result. It
does not prove a fresh user-photo flow, real current template choice, new
generation, all registered templates, a laptop-off Picker endurance test,
Samsung/company-template fidelity, PowerPoint editing/save/reopen or recipient
opening. New legitimate choices and source approval cannot be simulated to
close those gates. No new photo or current deck-production request was supplied
for this engineering preparation.

## Minimum remaining gates

1. When the user starts a real deck: purpose/source choice and actual input.
2. Actual visible template/reference confirmation plus preset where applicable.
3. Actual current analysis/outline approval.
4. Existing-owner production and all-page final-file visual QA.
5. Owner-private delivery/readback and the recipient's own opening.

The next useful user input is a real deck request with its reference, not a
laptop connection or a new service account. Do not prompt for it prematurely
during this preparation task.

## Historical evidence

- [Cloud reference production and private transfer](https://github.com/FriendY0421/slide-master/pull/14#issuecomment-6194142732)
- [Exact grouped cloud result](https://github.com/FriendY0421/slide-master/pull/14#issuecomment-6194264924)
- [Approved main selection workflow](https://github.com/FriendY0421/slide-master/blob/main/.claude/skills/ppt-master/workflows/template-selection.md)
- [Approved main surface gate](https://github.com/FriendY0421/slide-master/blob/main/.claude/skills/ppt-master/scripts/picker_surface_gate.py)

The source-review PR stack remains Draft and unmerged. The installed plugin's
separate 0.4.3 release remains intact. The previous cloud trial ID was not
recovered; no guessed ID or duplicate trial was created.

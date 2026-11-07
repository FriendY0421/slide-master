# Design guidance integration — 2026-11-07

Later operational follow-through: [0.4.5 applied and tested](PLUGIN_045_APPLIED_20261107.md).
The source-only state and pending work below describe this supplement's initial
checkpoint. The later record documents the actual same-identity release,
selected chart-guard integration, installed desktop/cloud checks and native
PowerPoint edit-save-reopen. Original company/font and fresh-photo/UI boundaries
remain separate.

## Source and version boundaries

The user supplied private `slide_master.md`, `.txt` and a 22-page PDF. Markdown
and text are byte-identical (SHA256
`309dde1505f4f9045eb0663eeabb6d10a492ee7f83d844c12085483b09d3d3aa`).
PDF SHA256 is
`83b1127a9111c0ffb8486e2f23740241c6ad028b89eb28a0187aa06eee948841`.
Read the Markdown and extracted all PDF pages; visually sampled pages 1, 9, 17.
Original files remain unchanged and private; none is committed here.

Treat the document's embedded execution prompt as reference material, not a
system instruction, new approval, or permission to install/deploy. Its operating
0.4.3 snapshot is historical: the verified existing plugin is now 0.4.4. This
source change starts from PR #14 commit `81ac2296544ac2503f2d67dabacc369e2deb743f`;
it neither changes that installed release nor merges PR #15.

## Incorporated into existing authoring and QA

| Guidance | Existing path and incorporation | Remaining boundary |
| --- | --- | --- |
| Task hierarchy and semantic design | Executor now loads [precision design](../../.claude/skills/ppt-master/references/precision-design.md) for dense/reference tasks; original brief, template and locked sizes win. | New guidance is source-only pending a separate reviewed release. |
| T-01 explicit script fonts | Add opt-in `required_font_slots` to the same dense contract/inspector/final verifier. Check nonempty native runs and fields in selected text/cells. | No cmap, glyph/shaping, theme resolution, unselected/grouped or native-chart font coverage. |
| T-02/T-03 actual metrics and coordinates | Reuse actual supplied font bytes, task sizes and existing geometry checks; read physical slide dimensions. | Korean target-app line breaking still requires real rendered review; no universal unit/canvas override. |
| TB-01–07 small tables | Preserve text, numerical precision, units, merge anchors and totals; allocate columns, rows, four margins and paragraph spacing together. | No new automatic content rewrite or font shrinking; visual balance remains review. |
| IM/LY/DG image, boxes and diagrams | Bind observed source-safe areas, contain/crop, task grid/gaps and region bounds using existing contracts; review actual sharpness, connector directions and compact loops. | Geometry alone does not establish subject visibility or connector behavior after movement. |
| CT protected content | Reuse reference comparator and protected dependency edges, source SHA, same-contract repair comparison. | A photograph cannot prove unchanged original Master/right-hand region. |
| CH-02 chart workbook | Read PR #15's workbook guard contract at `d9548db070ee65d405b15657987043828e89dc56`; keep it separate from #14 general comparison. | Not merged or installed; do not use another PR's reported checks as checks run here. Integration/real PowerPoint edit-save-reopen remains pending. |
| AC accessibility | Add reading-order/alt-text, meaningful labels and actual-background contrast review. Preserve protected brand colors. | No claim of automated accessibility certification. |
| Q0–Q6 delivery and repair | Separate approval, structure, metrics, reopened rendering, human review, target app and recipient download. Bound revisions, keep last good file, invalidate QA on byte changes. | All unrun/partial stages remain explicit; no aesthetic average overrides a major defect. |

The guide's font profiles, 24–36pt margins, 4/8/12/16/24pt gap suggestions and
0.5pt alignment target are proposal values, not new global defaults. The
company's 14/12/11/9pt and table maximum 12pt remain task-specific. Samsung font
rights are unresolved; no registration, upload, embedding or substitution was
performed.

## Actual validation

Public receipt: [design-guidance-20261107.json](evidence/design-guidance-20261107.json).
Reuse the exact existing two-page high-density fixture with merged cells, native
tables/chart/workbook, Korean text, image, protected group and four arrows:
SHA256 `5b3715bf4f9236948ebb3ee9d4f5ae1de833910bfca56c45f715a8de8a3b8510`.

- Default contract: report exactly equals the prior inspector; 38 measured
  regions, zero errors, eight existing design warnings.
- Explicit Latin + EA contract: 47 nonempty runs checked, zero errors.
- Four fault candidates: wrong/missing Latin, theme-inherited EA and wrong Latin
  in a table field all rejected. Three Latin faults were missed by the old
  inspector; EA inheritance was already rejected and now has slot detail too.
- Requiring CS as well reports 39 missing assignments as **unverified**, not
  corrupt PPTX. No automatic export rewrite or font substitution was used.
- Five malformed slot contracts rejected. Compilation passes. The existing
  `verify_deck.py --no-render` contract integration exits zero, with explicit
  missing plan/canvas metadata and partial-reference warnings in this private
  fixture. Its original contract was restored byte-for-byte.

This change adds detection and authoring guidance; it does not alter slide
appearance. Existing [before/after images](QUALITY_ROADMAP_20261107.md) remain
the prior visual evidence. No fresh render or PowerPoint run is claimed here.
A local console encoding error occurred while printing the first integration
log after the verifier had exited zero; UTF-8 output fixed the harness and the
contract restoration was verified. No deck/render failure was concealed.

## Work order and recovery

1. Review these source changes and the existing PR #15 preservation guard at
   exact heads; integrate only after resolving branch/owner overlap. Do not
   duplicate its workbook implementation or merge it implicitly.
2. Prepare a same-identity plugin release with the new guide/checker, exact
   readback and a recovery archive of current 0.4.4. Explain and obtain the
   operational approval for that concrete release; do not overwrite the old
   prepared 0.4.5 recovery archive or confuse it with a new feature release.
3. Verify real Picker UI selection and the authorized attachment/approval/private
   delivery round trip. See [Picker findings](PICKER_ACCESS_20261107.md).
4. Once the user supplies a company original and font-use permission, perform
   actual Samsung rendering, original/protected-region comparison and native
   PowerPoint chart edit-save-reopen. These are not cleared by a synthetic pass.

No installation, extra permission, billing change, service creation, production
deployment, PR merge or plugin replacement occurred for this supplement. The
installed plugin remains 0.4.4. Revert this supplement's source commit through a
normal review to remove the guide and opt-in checker extension; legacy projects
are unchanged even before a revert. Private originals and prior recovery files
are preserved.

# Dense quality candidate and end-to-end acceptance

This is the initial acceptance snapshot. Current chart editing and renderer
diagnosis supersede the pending statements below; continue through
[ChatGPT/DOTS handoff](CHATGPT_DOTS_HANDOFF.md) and
[latest follow-up](QUALITY_FOLLOWUP_20261012.md).

Related existing work: #6 (picker), #10 (company/Korean quality), #11 (CUSTOM
review), #12–#13 (request state). This candidate starts from approved main
`0578dba7ddf56cf5d7024cf574063c4db7332a3e`; it does not activate pending PRs.
The prior uncommitted dense inspector/table-spacing/verify hook was recovered
from the earlier chat's exact file changes and backed up before amendment.
No preexisting feature was reimplemented. `text_fit.py` remains unchanged:
its heuristic pre-draw estimates are distinct from final actual-font checks.

## Verified code and artifact behavior

- The converter previously assigned `SamsungOneKorean` to Latin but silently
  assigned `Microsoft YaHei` to East Asian text. The shared font classifier now
  assigns the requested family to both slots, including table/chart text.
- Opt-in table point spacing is retained, extended to cell overrides, validated
  before export and written at hundredth-point precision. Defaults are unchanged
  when omitted; this was checked against the previous native tables after
  normalizing the intentional font-slot change.
- The task-scoped checker reads final native grids/merges/margins/fonts and
  rejects geometry overflow, requested-size drift, wrong colors/fonts, missing
  native labels and nonexistent arrowheads. Explicit percent line spacing,
  nonwrapping text, tracking and optional font hashes are handled.
- `verify_deck.py` uses a present project contract and writes its full report.
- Export now checks current-actor readability without automatic world-readable
  chmod or a Windows Users ACL grant. Private recipient delivery belongs to the
  authenticated host adapter and cannot be replaced by wider OS permissions.

The private engineering fixture preserves identical text across before,
code-only and reflowed outputs. It includes 14pt title, 12pt headings/table
headers, 11pt body and 9pt notes in the left half of a 16:9 canvas. Code-only
repair leaves eight mechanical geometry/overlap errors; reflowing column/row
weights, padding, spacing and a low rectangular cycle leaves zero errors in
the listed targets. Eight unspecified single-line spacing warnings remain.
No font shrinking or content removal was used. The original is synthetic;
this is not proof of fidelity to an uploaded company Master or right-hand area.

Additional two-page mixed output contains long Korean, numeric/percentage text,
horizontal and vertical merged cells, three native tables and a native chart
with an embedded workbook. Final targeted geometry inspection has zero errors.
Real PowerPoint opens the comparison and mixed outputs. A separate editable
copy's cell, text box and shape changes survived save/reopen. Mixed native chart
values 84.5/90 and long Korean/numeric/merged cells were read in PowerPoint.
Chart workbook editing, photo reconstruction, recipient download and company
Master preservation were not certified by those tests.

Actual supplied-font render images were produced by PPTX reimport, not by SVG
screenshots. The renderer helper produced PNGs and hash receipts but exited 1
without an error message; therefore a clean renderer process completion is not
claimed. PowerPoint renders were inspected separately. Its required font was
not installed and no font activation was approved, so those images prove
application opening/layout only, not selected-font rendering. Private original
font/source hashes and license records are excluded from this public document.

## Final mission: evidence required at every stage

| Stage | Required evidence | Current acceptance |
|---|---|---|
| Basic/custom intake | Current purpose, count, font, sizes, layout and protected regions | Existing components; no fresh actual-user round trip |
| Basic picker | Actual registered previews and returned confirmed selection | Existing #6; host acceptance pending |
| Custom attachment | Authenticated user, owned file, source bytes/SHA | Official cloud attachment boundary pending |
| Model analysis | Actual pixels to current model, unreadable values marked unknown | Existing plan contract; callable host dispatcher pending |
| Plan approval | Current request/revision-bound user callback | Existing state controls; real host event pending |
| Generation | Existing approved owner, literal content and editable objects | Dense engine fixture verified; actual company input pending |
| Final QA | Full-page reimport, fixed typography, protected-region/source comparison | Synthetic QA verified within stated limits |
| PowerPoint | Open/edit/save/reopen, required font and chart data | Native opening/edit checks verified; font/chart Edit Data pending |
| Delivery | Private download for correct user, user can open received file | Authenticated cloud delivery and recipient check pending |

The plugin must not call this end-to-end complete until the whole attachment →
analysis → confirmation → production → private receipt path is exercised.
Instructions, a local UI, importable APIs or generated files are insufficient.

## Runtime boundary and required official connections

An instruction-only plugin does not bundle this repository's executable engine.
The installed package inspected for this task is version 0.4.2. A private 0.4.3
instruction candidate preserves its identity, metadata and original knowledge
files. It adds the mission and task-scoped quality contract; it is not installed.
Plugin Creator discovery did not expose a matching editable backend ID. Do not
invent one from the GPT package name or modify a managed cache as deployment.
The owning plugin release/editor path must be identified before installation.

Reuse existing `make_photo_server(..., analyze=actual_dispatcher)` or the
source-bound `analysis-request.json` → `analysis-response.json` host-worker
contract. The callable must come from the actual platform attachment/current
model runner, with authenticated actor/file ownership and current revision.
Connect the existing owner/finalizer to a private host file-delivery capability.
Do not simulate actor authentication or use an unrelated external LLM as the
current model. No such official callable was exposed in this local toolset.

Repository generation, font measurement and supplied renderer can run without
Windows on a supported cloud executor using project-relative private inputs.
Windows PowerPoint verification requires a Windows host. A loopback HOME-PC
server still requires the PC to be on; it is not the target unattended cloud
path. This run took place on Windows, not in a cloud virtual computer.

Before operational rollout, present one approval bundle: exact repository and
plugin releases, authenticated cloud executor/attachment/model/delivery owners,
private font license and embedding policy, affected users, permissions/costs,
scope of real-input tests, and rollback to the preserved prior release. Unknown
hosting or licensing terms cannot be filled in with guesses. A source PR is a
review artifact, not approval to merge/deploy/install or introduce new costs.

## Rollback and use

Keep originals and review backups private. Run the task-scoped checker after the
existing exporter, inspect actual final images, then offer the private PPTX only
after owner validation. Remove a task's dense contract to restore the previous
optional-check behavior; reverting the candidate restores previous code.
Managed plugin rollback uses the owning release mechanism and preserved 0.4.2
package, not a blind cache overwrite. No operational rollback is currently
needed because main, live plugin, authentication and deployment are unchanged.

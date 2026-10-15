# Overnight checkpoint — source/review work, not operational acceptance

Recorded just after midnight on 2026-10-14 KST. Draft #14 is the review branch;
main and installed 0.4.2 are unchanged. The overnight allowance ends at 07:00 KST.

## New defects reproduced and corrected

| Defect | Before | After / evidence |
|---|---|---|
| Page coverage | Duplicate/misnumbered/reordered page receipts accepted | Four faulty cases rejected, valid case and fresh actual two-page geometry render passed; [receipt](evidence/page-coverage-validation-20261013.json) |
| Early Korean line overflow | 180.625pt first line in a 100pt non-wrapping box missed if last line was short | Both early/last-line overflow detected; fitting and wrapping cases pass; [receipt](evidence/early-line-validation-20261013.json) |
| Table-wide size ceiling | Header setting could bypass table maximum | Header 14pt/table maximum 12pt rejected; 12/12 and another template's 14/14 pass; [receipt](evidence/table-cap-validation-20261013.json) |

Source commits: `e1eff54`, `b6c3450`, `23e7d0d`. The renderer CPU workaround and
its actual local final-verifier integration remain documented in
[renderer continuation](RENDERER_CONTINUATION_20261013.md). Code acceptance is
separate from all-page visual, Samsung, company-source and recipient acceptance.

After the latest inspector changes, the existing two-page complex fixture still
passes 38 limited structure regions, with zero errors and zero font files read.
This new regression is **structure-only**: Korean wrapping/glyph clipping is not
certified. Existing PowerPoint table/text/shape editing and chart data
84.5→85.75 save/reopen evidence is preserved, not counted as a new test.

## Private review files prepared

A local private review archive contains three editable synthetic PPTX copies,
temporary Pretendard preview, prior PowerPoint chart preview, intermediate
before/code/after image, test records, scope README and hashes. No font binaries
or company originals are included. Its SHA256 is
`81365888a7a01aeea90d56c6ddddcb007f6282ced5814d48e9571cd0cb7be61e`.
The archive is not published on GitHub or claimed delivered to a cloud recipient.
The exact receiving user's download/open remains unverified.

Intermediate images produced before the native exit workaround are explicitly
labelled PARTIAL and cannot certify successful renderer completion. The actual
PowerPoint chart image is labelled font-unverified. The temporary Pretendard
preview is not substituted for SamsungOneKorean acceptance. Original/recovery
files remain in the existing private review storage and were not overwritten.

## Remaining boundaries and minimum actions

The [completed Cloud Work trial](CLOUD_TRIAL_RESULT_20261013.md) confirmed the
main plugin's editable 0.4.2 USER/PRIVATE skills-only record and independent
Linux rendering. It did not complete Picker selection (one HTTP 429), saved
connection scope, authenticated attachment/current confirmation/private delivery,
retention/cost or recipient download/open. Do not repeat its failed call.

- For the cloud round trip: upload the existing nonsensitive synthetic PNG into
  the already-created trial, then confirm the current displayed outline/design.
  Public-source download is not an actor-bound upload.
- For company preservation: provide the actual original PPTX and changed/protected
  regions. Prior generated results cannot serve as the company original.
- For Samsung: supply local usage conditions and temporary-session approval,
  separately cloud installation, server rendering and output-embedding rights.
  No font registration/upload/embedding proceeds from file possession alone.
- For release: present exact source/plugin/transport target, affected users,
  permissions/cost, test impact and rollback together before operational changes.

Continue only independent work with a specific untested concern. Repeated failed
discovery or unchanged successful checks are not progress. Source rollback is a
reviewed revert; private bundle removal does not remove original evidence. Stop
the local heartbeat in Codex automation controls; it otherwise expires at 07:00.
No new server/service was deployed, and the weather project is outside scope.

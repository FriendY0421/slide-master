# Chart/workbook preservation in the existing dense gate

The standalone preservation helper is reused from PR #15 head
`d9548db070ee65d405b15657987043828e89dc56`, upstream SHA256
`b75d394bf0378191e7806dfc554849204a549e5fce59fa078f50a23e5714e2a5`.
Only its example-document link is changed; preservation logic is reused intact.
This is a reviewed file-level reuse, not a PR #15 merge. Its cloud adapter,
Samsung-font code, FAH configuration, network changes and selftests are not
imported. No new dependencies are required.

## Existing contract and execution order

For a post-import native edit, keep the actual pre-edit source and hash. Add to
the private `dense_layout_contract.json` used by the existing inspector/verifier:

```json
{
  "chart_workbook_preservation": {
    "path": "actual-pre-edit-original.pptx",
    "sha256": "actual-source-SHA256",
    "mode": "edit"
  }
}
```

Keep the normal font/slide/object fields too. Paths resolve from the contract.
Candidate SHA is calculated from the actual input file; the helper reads only
those exact source/candidate bytes. Missing or invalid source/hash raises an
error. No guessed originals, manifest provenance or user confirmation is accepted.

The same `dense_pptx_quality.py` now invokes preservation **before** font metric
or object checks. A lost chart/workbook/linkage, altered series/range/type or
lost source workbook formula returns errors, zero measurements and
`stopped_before_dense_checks=true`. Existing `verify_deck.py` stops its later
review-render stage on that failure. A standalone caller must likewise stop;
do not use an old render to approve the rejected bytes.

On success, ordinary dense checks and optional reference comparison continue.
Source/candidate hashes are rechecked before the report is accepted. Baseline
repair tracking uses the same geometry/font contract without rerunning the
post-edit guard against a different comparison baseline. Without this opt-in
contract, the previous report remains identical.

The guard resolves logical slide/chart/workbook relationship edges, handles
physical package renumbering, compares series/ranges/formulas, and does not
fetch external targets. Unsupported external targets in the chart chain block.
New XLSX external-link parts block; existing external dependencies are not
certified safe. Review external-data, macros and other unsupported workbook
features separately. An unchanged unsupported feature is not acceptance.

## Deliberate limits

A guard pass is not content approval or delivery permission:
`candidate_deliverable` remains false in its narrow result. Numeric edits can
preserve the relationship/formula contract; validate the explicitly approved
values, chart cache and embedded workbook with the existing authoring owner.
Protected chart bytes in a reference contract must not be removed merely to
make an unauthorized edit pass. A legitimate series/formula/owner change needs
its own reviewed contract; this guard intentionally does not infer it.

`mode: "regenerate"` additionally requires `authoring_manifest`, a real retained
source-code/data manifest bound to the pre-edit SHA and in-directory file hashes.
The helper never executes it or repairs the external rendering engine. A manifest
cannot override an invalid candidate. Never manufacture a replacement source or
flatten a chart and report it editable.

## This integration's actual checks

Same high-density two-page fixture: 38 regions, 47 Latin/EA runs, zero errors.
Four injected cases (missing workbook, missing externalData, external workbook
target and changed series range) stop before metrics even with unavailable font
paths. Repacking identical parts passes. Regeneration without retained sources
blocks. These are newly run integration checks, not PR #15's historical suite.

The current exact fixture was also edited in actual Windows PowerPoint on a
separate copy: B2 84.5 -> 85.75, chart/workbook persistence after save/reopen,
native PNG export. The first COM attempt lost its reopened chart handle; a fresh
application/chart/data handle fixed the validation harness. Both attempts remain
private. No original, company file, installed font or external linked data was
modified. Samsung appearance and original-company preservation remain unverified.

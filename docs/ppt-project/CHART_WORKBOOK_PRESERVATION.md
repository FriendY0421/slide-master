# Chart/workbook preservation before delivery

A supplied-runtime import → native edit → export round trip lost an embedded
chart workbook in the isolated fixture. The resulting draft was correctly
rejected by the native finalizer. This source change adds a separate read-only
preservation barrier to the existing cloud QA adapter. It does not patch the
external engine, install a component, or enable an installed-plugin release.

## Required edit flow

1. Preserve the exact pre-edit PPTX and SHA256 before importing. Retain the existing
   authoring code/data and their hashes when those original sources are available.
2. Export edits to a separate candidate. Never overwrite the source or an earlier
   failed draft.
3. For every post-import edit, invoke `cloud_review_existing.py --operation edit`
   with `--edit-source` and `--edit-source-sha256`, plus the existing exact candidate
   SHA/profile/runtime/review arguments. A missing source/hash is an error. Plain
   `--operation review` is not post-edit preservation evidence; passing edit-source
   fields to review mode is rejected.
4. The new `chart-workbook-preservation` stage executes before any child QA or
   rendering. It resolves logical slides, chart relationships, chart externalData
   and actual embedded XLSX packages. It compares logical chart owners/counts,
   chart types, series counts, source-range references and workbook linkage.
   Retained workbook formulas must remain unchanged. New external workbook links
   are unsupported. Renumbered physical parts are resolved through relationships.
5. A broken candidate stops the pipeline with `qa_processes_passed: false`.
   Neither a retained authoring manifest nor successful earlier render evidence
   can override that failure. Do not deliver, upload or label that candidate final.
6. Only when real retained authoring code **and** source data verify against their
   recorded hashes may the existing original authoring owner regenerate explicit
   edits into a different candidate. Use `--operation regenerate` and supply the
   manifest. That mode requires the manifest and still checks the regenerated
   PPTX against the original chart/workbook preservation contract. It then runs
   ordinary font, package, layout, dense and rendering QA again.
7. Without verified original authoring sources, stop with an undeliverable failed
   draft. Do not invent source code/data, remove workbook references, create an
   unrelated workbook snapshot, claim source-formula preservation, or mark an
   engine repair complete. An unsupported legitimate change of chart ownership,
   series/range topology or workbook formulas requires a separate reviewed source
   contract; this conservative gate does not infer such authorization.

The adapter defaults to legacy read-only review for compatibility. Callers must
select edit/regenerate for the corresponding workflow; the receipt exposes
`review_operation` and the preservation result. This Draft has not changed any
installed caller or runtime. The standalone preservation CLI defaults to edit and
is useful before invoking the full adapter:

```bash
python3 .claude/skills/ppt-master/scripts/chart_workbook_preservation.py \
  SOURCE.pptx CANDIDATE.pptx --source-sha256 SOURCE_SHA \
  --candidate-sha256 CANDIDATE_SHA --mode edit
```

It writes JSON only to stdout. A pass removes this specific preservation block;
it never grants delivery, generation or deployment approval. In particular,
`candidate_deliverable` stays false in this narrow report. Ordinary data/content,
rendering and owner delivery checks are still required.

## Retained authoring contract

`--authoring-manifest` points to a task-private JSON file. Example structure:

```json
{
  "source_pptx_sha256": "exact_pre_edit_PPTX_SHA256",
  "files": [
    {"role": "authoring_code", "path": "build/original-builder.mjs", "sha256": "recorded_original_hash"},
    {"role": "source_data", "path": "build/original-data.json", "sha256": "recorded_original_hash"}
  ]
}
```

Paths must stay relative to the manifest directory. Missing/changed files, an
incorrect original PPTX hash, root escapes, or missing code/data roles block
regeneration. The helper never executes commands from a manifest or automatically
regenerates anything. Hash agreement proves file identity, not author permission,
license rights or historical source provenance: use the actual retained records,
not a manifest manufactured from an arbitrary new approximation.

For the real fixture below, original builder/data hashes were checked against the
previously retained handoff manifest before the regeneration review was enabled.
Existing originals, failed drafts and earlier manifests remain unchanged.

## Current verification

- 20 new stdlib-only synthetic regressions pass: retained relationships, missing
  workbook/relationship/externalData/chart, external targets, formula/series/range
  loss, permitted numeric edits, bound input hashes, manifest roles/root boundary,
  changed authoring bytes, source preservation, missing-source regeneration block,
  and a manifest's inability to override a broken candidate.
- Eight focused adapter checks pass, including missing source/hash rejection,
  preservation failure before **any** child process, explicit operation enforcement,
  and existing success/failure/source-change/font-map behavior. The previously
  completed full suite was not blindly rerun.
- Actual malformed import/edit/export fixture SHA256:
  `95b9b806d65ee03c486b2bc0f1c8d1b4d2c8cd4e0785ec12aa73d06990221f44`.
  The new adapter stops after its first preservation stage, even with verified
  retained authoring files. No later renderer process runs for that failed draft.
- Actual separately regenerated specimen SHA256:
  `829e17821a63bed2921199a13bb8e3e85b524c37d58ea316d39748b8f89cac08`.
  Preservation plus all six existing QA stages pass. Its new render is byte-identical
  to the previously full-page inspected PNG. The native table/chart/workbook values
  remain 13/18/31. A second actual check with no authoring manifest blocks regenerate
  mode, even though this specimen otherwise has valid chart/workbook structure.

These are synthetic data and existing repository OFL Pretendard checks. They do
not certify Samsung bytes, company source fidelity or PowerPoint open/edit/save/
reopen. The external engine defect remains. Safe original-source regeneration and
failed-candidate blocking are verified separately from an engine fix.

The parent has confirmed that the blocked storage hostname is already in the
latest approved 42-host policy, while this executor is an older runtime. No more
font downloads or network changes are attempted here. A formal latest-environment
handoff is parent-coordinated and independent of this source preservation fix.

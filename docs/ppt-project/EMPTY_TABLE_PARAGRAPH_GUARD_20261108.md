# Empty table paragraph typography: source guard and production boundary

The actual approved private photo job exposed a native PowerPoint issue:
otherwise blank cells could inherit larger paragraph-mark typography and expand
rows. The existing native preparation step corrected paragraph ends, and actual
PowerPoint rerender confirmed the delivered job. That correction was **per job**;
it was not a globally patched Artifact Tool or installed plugin exporter.

The existing dense inspector previously checked nonempty runs but could miss
that risk. Its new table-level opt-in `require_empty_cell_paragraph_style`
checks explicit end-paragraph size/typeface for every blank paragraph, including
merged continuation cells, using the actual task's font and header/body roles.
No font is loaded for the new structural check, substituted or installed. No
content/geometry/package is changed. Legacy contracts omit the flag and retain
their prior complete report. The existing `verify_deck.py` dense-contract path
reaches this same inspector, with no second renderer or generator introduced.

## Evidence

| Verification | Actual result and scope |
| --- | --- |
| Complete old/new inspector report, same existing public synthetic deck and contract without new flag | Equal, not just matching error counts. |
| Existing synthetic fixture plus one blank paragraph, correct explicit 11pt/Latin/EA | No new guard errors. |
| Missing mark; 18pt mark; wrong EA family; missing EA slot | Each rejected by the opt-in guard; omission of the flag retains prior behavior. Structural fault probes, not native renders. |
| Exact existing private pre-correction PPTX | 25 blank paragraph marks inspected, 25 new guard errors. This file already had actual PowerPoint expansion evidence. |
| Exact existing private corrected delivery PPTX | Same 25 blank paragraphs, zero new guard errors; input SHA unchanged. This file already had successful native rerender evidence. |
| New native rerender | Not repeated: unchanged previously inspected artifacts were reused to connect the new guard to the established defect. |

The first probe attempt failed because its test contract omitted required
`slide_size_pt`; correcting the probe contract resolved it. That was not a
production PPT failure. No original or delivered file was overwritten.

Public [fault probe](evidence/empty-table-paragraph-20261108/probe.py) uses only
the already public nonsensitive fixture and a caller-supplied separate output
directory; exclusive ZIP creation refuses overwrites. Run with existing Python:

```text
python docs/ppt-project/evidence/empty-table-paragraph-20261108/probe.py <new-output-directory>
```

The [synthetic report](evidence/empty-table-paragraph-20261108/synthetic-result.json)
and [sanitized summary](evidence/empty-table-paragraph-20261108/summary.json)
contain no company text, values, assets, font files, private paths or links.
Private native-app screenshots/source files remain private.

## Applied / unapplied and recovery

Applied to source in existing PR #14: existing inspector plus opt-in contract
documentation and a reproducible structural fault probe. This guard is an
additional check, not a claim of automatic layout correction or complete font
inheritance resolution. Defaults and unselected objects are unchanged.

**Not applied to installed plugin0.4.6:** no release, deployment, merge,
installation, permission or fee change occurred. Before any rollout, package
the actual current official plugin source with the updated checker/instructions,
retain exact source/recovery, and group version/impact/cost/recovery for approval
if needed under the current user authorization. Do not patch managed caches.

Source recovery is an ordinary revert of the eventual guard commit, with original
PPTX/copies retained. Existing contract users need no rollback. A required task
must not remove its check merely to hide a known failure. This progress does
not close recipient opening, Samsung rights or Aro/PC-off hosting acceptance,
and does not start FAH operational integration.

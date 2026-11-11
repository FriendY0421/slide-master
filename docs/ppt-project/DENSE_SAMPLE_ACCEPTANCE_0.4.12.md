# Slide Master 0.4.12 dense-sample acceptance

Reused the two-slide synthetic fixture from the [0.4.10 PowerPoint review](COMPOSITION_RELEASE_20261111.md).
Applied the saved 0.4.12 authoring guidance in the local preservation workflow.
The comparison tests those design decisions on fixed content. It does not
exercise a new ChatGPT mobile request through the installed plugin.

| Evidence | Before, reviewed 0.4.10 fixture | After, 0.4.12 guidance |
|---|---|---|
| Main table columns in points | 45 / 139.5 / 193.5 / 48 | 51 / 163.5 / 160.5 / 51 |
| Main table body rows in points | 49.5 / 49.5 / 51 | 45 / 45 / 46.5 |
| Image size in points | 259.2 × 129.6 | 315 × 157.5, aligned with the table top and the protected panel edges |
| Dense inspector | 38 measured regions, 0 errors, 8 warnings | 38 measured regions, 0 errors, same 8 warnings |

The image remains an editable picture object with the full 2:1 source
preserved. The shorter main table let the comparison table, loop and note move
up together by 13.5 pt. Page count, wording, data, type sizes and merge topology
match the baseline. The dense inspection uses the existing fixture's 14/12/11/9
pt contract, table maximum of 12 pt and the approved Pretendard font files
for measurement. The eight warnings are for implicit line spacing in existing
objects. The reference inspector reports partial coverage for the native chart.

PowerPoint 16.0 opened both exact files and exported both slides at 1600×900.
The Korean lines, small notes, tables and arrow directions were reviewed in
the renders. The protected box on slide 1 and all of slide 2 are pixel-identical.
Only slide 1 XML changed in the package. Chart XML, embedded workbook and image
bytes are identical. In a separate copy, edits to text, a table cell, picture
position and an embedded workbook value all survived save and reopen. Both the
workbook and PowerPoint chart reported the edited value. The delivery file
remained unchanged. The actual PowerPoint glyph font was not certified.
SamsungOneKorean was outside this synthetic check.

The 40,338-byte delivery file is a native PPTX in private My Drive. The connector
reported owner-only permissions. An authenticated download matched the local
file byte for byte. The recipient confirmed downloading the file on their
phone without using the PC and opening both slides successfully in PowerPoint.
This confirms phone receipt and opening of the delivered PPTX. New PPTX
production initiated from the phone remains a separate acceptance run.

- Baseline SHA-256 `63d15081a4ab6a7351b548384ddb4826d1d6a0c9e1eb9396178ab2da25e3607d`.
- Delivery SHA-256 `ab7dfa61dfbce37d7486b0587e89490628eba7244b2cca37d59abc743c096afa`.
- The comparison PNG and inspection logs were retained with the local review
  files. The private Drive link and editability test copy are excluded from Git.

# Korean business quality comparison

Contributor example, not an ACTIVE registered template. Every value, organization
and date is synthetic. The user authorized this implementation/validation sample;
normal presentation requests still follow all existing selection/storyline gates.

- [Before PPTX](review/baseline.pptx) / [Improved PPTX](review/improved.pptx)
- [KPI before/after](review/kpi-before-after.png)
- [Improved six-page overview](review/improved-contact-sheet.png)
- [Full-size comparison gallery](review/comparison.html) — open locally with its adjacent PNGs
- [Validation summary](review/validation-summary.json)
- [Profile and runbook](../../../../../docs/ppt-project/KOREAN_BUSINESS_QUALITY.md)

The baseline repeats the unchanged Consulting Clarity content prototype from
`0578dba` with the same synthetic facts. The improved example changes layout and
evidence form: strategy summary, KPI chart, cause chart, editable execution
roadmap, action table and risk table. This isolates visible improvements in a
small fixture; it is not an automatic migration or a statistical quality score.

| Check | Before | Improved |
| --- | --- | --- |
| Titles | 32px | 44px |
| Supporting prose | 15–16px | 28px body / 22px evidence labels |
| Native Charts / Tables | 0 / 0 | 2 / 2 |
| Embedded chart workbooks | 0 | 2 |
| Structured Master / Layout | 1 / 1 | 1 / 1 |
| Individual supported-runtime PNG inspection | 6 pages | 6 pages |

Pretendard Regular/Bold were registered from the existing OFL 1.1 font bundle into
the shared Presentations runtime's renderer. Both final PPTX files passed that
runtime's finalizer without byte changes. Improved chart caches/formulas and
embedded Excel cells were checked. The source-value edit smoke updated 84 to 86
in both chart cache and workbook, and updated a native table's owner cell.

Eleven positive/rejection smoke cases passed. All six improved SVG pages passed
the existing template-mode quality checker with zero errors/warnings. Exact
sources/profile/fonts/PPTX/render bytes are bound to an explicit `agent:Codex`
review receipt in the local scratch project, rather than fabricated user approval.
Committed artifact hashes are in the validation summary; receipts with local
absolute paths are regenerated on the inspecting machine.

**Remaining acceptance:** OfficeCLI/PowerPoint application opening and Edit Data
interaction were unavailable in this cloud. No fonts are embedded in the deck.
The initial unfilled template-preview title-loss issue is not claimed universally
fixed; every filled title is visible in this controlled comparison. Existing
library templates, draft picker PR #6, dependencies and production deployment
remain unchanged. No third-party implementation or new engine was bundled.

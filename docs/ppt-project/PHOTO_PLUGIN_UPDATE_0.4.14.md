# Photo reconstruction update 0.4.14

The private plugin baseline was 0.4.12 with 29 files. The update
updates the photo reconstruction guide, the two existing dense/reference
checker files and the versions in both manifests. The photo guide directs
authors to show observed typography and layout, identify unreadable regions,
propose editable reconstruction and obtain approval of the current plan.
The optional photo text contract checks approved text in named editable regions
of the resulting PPTX.

The scripts in the candidate match the repository implementation. Running the
packaged code on a synthetic fixture accepted an editable unreadable marker,
rejected a guessed replacement and a mismatched source hash, and preserved
the legacy result of 38 measured regions with zero errors.
The packaged checker also followed actual presentation order in a reordered
deck and rejected text declared on the wrong slide and a missing native object.

| Private overlay | SHA-256 |
| --- | --- |
| `slide-master-0.4.14-photo-review.zip` | `32cdf934de2977be4781df718676279a7ae1f396be6b4aeccfc0b272b1fb06f2` |
| `slide-master-0.4.15-restore-0.4.12.zip` | `7dc150725302640be1fe9e398d35df1b0f81635b274b8d8f7993521a9fde68db` |

The earlier 0.4.13 restore for 0.4.10 is retained. The 0.4.15 overlay restores
the three overwritten files from 0.4.12 and bumps the two manifests. Apply
with a fresh current release guard to the same private plugin and verify all
retained paths. Verify the installed package separately after official loading.

The user approved the update and Plugin Creator saved 0.4.14 on the same
personal private plugin using the 0.4.12 release guard. Official readback
matched all 29 expected files exactly, including five updated paths and 24
retained paths. The Picker and Drive declarations were preserved. The first
local check showed 0.4.12. Opening the installed plugin detail in Codex
subsequently showed 0.4.14, with both Picker and Google Drive connected. The
managed 0.4.14 package matched all 29 official paths. Of those, 27 matched
exactly and two unchanged Markdown files matched after text normalization.
The installed checker passed the editable unreadable marker and existing
38-region fixture, rejected the guessed text, and rejected the wrong source
hash. No new dependencies, connections, permissions or paid service were
required for the release.
Company photo comparison and exact font or visual fidelity are outside the
synthetic fixture. Mobile testing remains paused in this workstream.

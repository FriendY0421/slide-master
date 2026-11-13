# Photo reconstruction update candidate 0.4.14

The current private plugin was read back as 0.4.12 with 29 files. The candidate
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

| Private overlay | SHA-256 |
| --- | --- |
| `slide-master-0.4.14-photo-review.zip` | `32cdf934de2977be4781df718676279a7ae1f396be6b4aeccfc0b272b1fb06f2` |
| `slide-master-0.4.15-restore-0.4.12.zip` | `7dc150725302640be1fe9e398d35df1b0f81635b274b8d8f7993521a9fde68db` |

The earlier 0.4.13 restore for 0.4.10 is retained. The 0.4.15 overlay restores
the three overwritten files from 0.4.12 and bumps the two manifests. Apply
with a fresh current release guard to the same private plugin and verify all
retained paths. Verify the installed package separately after official loading.

Release pending operational approval. The candidate requires no new
installation, dependencies, connections, permissions or paid service.
Company photo comparison and exact font or visual fidelity are outside the
synthetic fixture. Mobile testing remains paused in this workstream.

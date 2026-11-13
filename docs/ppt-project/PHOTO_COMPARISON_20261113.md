# Photo reconstruction comparison and quality follow-up

The user approved a two-slide portrait reconstruction from one private photo.
Two authored layouts used the same source crops, reviewed transcription,
temporary Pretendard and export library. Both exact PPTX files were reopened
and rendered in desktop PowerPoint 16.0. The same assistant authored both
arms. This is a controlled comparison of two implementations for one source.

| Review | General authoring | Slide Master workflow |
| --- | --- | --- |
| Visual match | The cover used a rounded rectangular title panel. The two section headers and small number label used a simplified treatment. | The cover recreated the cloud contour. The body retained the two colored accents and a separate tinted number label. |
| Remaining visual differences | Simplified art, rectangular crop edges and a rectangular caption band. | Simplified art, rectangular crop edges and a rectangular caption band. |
| Editable objects | 31 text objects and seven separate images. Five PowerPoint edit/save/reopen checks passed. | 31 text objects and seven separate images. The same five checks passed. |
| Approved text | All 24 declared regions passed under the corrected inspector. | All 24 declared regions passed under the corrected inspector. |
| Revisions | Zero layout revision rounds after the first successful export. | Zero layout revision rounds after the first successful export. A verifier fix was required. |

The 24-region contract was assembled from the photo transcription used for
both exports. It establishes output consistency for declared text, including
two unreadable markers. Independent transcription review remains open. The
source typography and photographed color were estimated. Exact PowerPoint
glyph fidelity was not certified. The five edit checks were heading text,
body text, checklist text, checkbox geometry and picture position on copies.
The original source and delivered decks were preserved. All company assets,
output decks, render comparison and text contracts remain outside Git.

## Defect found in the installed verifier

Version 0.4.14 stopped on the real exports because the exporter emitted blank
names on unrelated picture objects. The approved region lookup now resolves
only declared native paths. Ambiguous names within a requested path still
fail. The corrected source checked both actual files and a native table cell.
A deliberately duplicated requested name failed. The existing PPTX-to-PPTX
preservation inventory retains its stricter naming rule.

## Quality work informed by public references

| Priority | Improvement | Evidence and application |
| --- | --- | --- |
| Photo fidelity | Align a photographed page using reviewed corners, then compare the exact final render with the aligned page. Review title boxes, figure crops, margins and color by region. | The reusable overlay tool ran on both pages of both PowerPoint exports. [OpenCV homography](https://github.com/opencv/opencv/blob/4.x/doc/tutorials/features2d/homography/homography.markdown) |
| Consistent visual review | Tie the review to the exact export and repeat the affected page checks after an edit. Review both full-slide hierarchy and small text at reading scale. | Reuse the existing hash-checked rendering and compare photos and exact output before delivery. [PPTAgent evidence model](https://github.com/icip-cas/PPTAgent/blob/main/skills/pptagent/references/task-contract.md) |
| Layout for report decks | Plan chart and label space with the text grid. Check slide-to-slide title and caption consistency and verify logical reading order where required. | The geometry check and human review remain separate. Reading order and alt text are suitable follow-up checks, particularly for decks distributed broadly. [OpenAI slide automation](https://github.com/openai/plugins/blob/main/plugins/build-web-data-visualization/skills/reports-pdfs-and-slide-automation/references/powerpoint-and-google-slides.md), [Microsoft reading order](https://support.microsoft.com/en-us/powerpoint/make-slides-easier-to-read-by-using-the-reading-order-pane) |

## Aligned review and release preparation

The same manually estimated corner coordinates were applied to both arms for
each page. The left and right outer corners were partly cropped. Each run
produced an aligned photo, a 50/50 blend and a two-color boundary map. The
Slide Master render followed the cover's cloud contour and the section title
bands more closely in this comparison. Illustration crop seams and differences
in caption position and shape remained visible. Lighting, texture and the
estimated corners limit interpretation of isolated edge differences.

The tool passed identity and angled geometry checks, rejected crossed and
out-of-bounds corners, and distinguished source, render and shared edges.
The packaged tool reproduced the reviewed page 2 hashes. The packaged
transcription checker passed all 24 declared regions in both actual decks.
The input decks and photographs stayed in the private job directory.

The 0.4.16 candidate combines the overlay script, the named-region verifier
fix, the photo workflow guide and both version manifests. It uses existing
Pillow. No new dependencies, connections, permissions or costs are required.
The user approved deployment and the existing personal private plugin was
updated to 0.4.16 using the current 0.4.14 release guard. All 30 server files
matched the expected package exactly, including 25 retained files. Codex
showed 0.4.16 with Google Drive and the Template Picker connected. The
local package appeared after refreshing the Codex plugin catalog. Of its
30 files, 28 matched the server exactly and two retained Markdown files
matched after text normalization.

The installed 0.4.16 scripts processed the same guidebook photo and the
four existing PowerPoint slide renders. All twelve generated PNGs matched
the previously reviewed image hashes. Each PPTX passed all 24 declared
transcription regions. An ambiguous requested object name was rejected.
No rollback was triggered.

| Private overlay | SHA-256 |
| --- | --- |
| `slide-master-0.4.16-photo-overlay.zip` | `eb81d246fef81be4eb52c3d6f6f3f7ac6832d5e92128c31953cba03616d06cdd` |
| `slide-master-0.4.17-restore-0.4.14.zip` | `7409e77032bd179000414ce67ac54f8eb9d6b3f5862dd8caf17606c3f4dd348b` |

For recovery use the current official release guard on the same private plugin.
The 0.4.17
restore overlays the prior guide and verifier and requires one explicit
deletion, `skills/instructions/scripts/review_photo_overlay.py`. Verify the
restored inventory and local loading separately.

## Illustration and caption revision

The follow-up used the same private source photo, two slides, approved text
and temporary Pretendard. Four cover illustrations now use separate PNG
objects with manually traced transparent masks. The caption is a native
diagonal shape over the lower-left photo with two separate editable text
objects. The shape starts at the left photo edge and reaches the lower
margin. Its geometry and blue fill are approximations of the photographed
design. A thin backing strip closes the existing bottom gap.

PowerPoint 16 reopened the revised PPTX and rendered both pages. The
installed 0.4.16 overlay tool used the previous corner coordinates to compare
the same photo with the before and after renders. The rectangular borders
around the four illustrations are absent in the new render. The diagonal
caption follows the photographed composition more closely. Some local mask
edges, the color and the background texture still differ from the photo.

Both revisions contain 31 text objects and seven picture objects. The revised
file passed all 24 declared transcription checks. On a copy, six edits
survived saving and reopening in PowerPoint. They covered the cover title,
two caption text objects, one checklist item, the diagonal caption shape
width and a masked illustration's position. The delivered file hash was
unchanged by the edit test. The source photo, editable PPTX and comparison
images remain in the private job directory.

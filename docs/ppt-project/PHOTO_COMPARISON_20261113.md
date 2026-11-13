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
| Photo fidelity | Align a photographed page using confirmed corners, then compare the exact final render with the aligned page. Review title boxes, figure crops, margins and color by region. | Manual three-way render comparison completed for this job. A reusable alignment/overlay tool remains a candidate. [OpenCV homography](https://github.com/opencv/opencv/blob/4.x/doc/tutorials/features2d/homography/homography.markdown) |
| Consistent visual review | Tie the review to the exact export and repeat the affected page checks after an edit. Review both full-slide hierarchy and small text at reading scale. | Reuse the existing hash-checked rendering and compare photos and exact output before delivery. [PPTAgent evidence model](https://github.com/icip-cas/PPTAgent/blob/main/skills/pptagent/references/task-contract.md) |
| Layout for report decks | Plan chart and label space with the text grid. Check slide-to-slide title and caption consistency and verify logical reading order where required. | The geometry check and human review remain separate. Reading order and alt text are suitable follow-up checks, particularly for decks distributed broadly. [OpenAI slide automation](https://github.com/openai/plugins/blob/main/plugins/build-web-data-visualization/skills/reports-pdfs-and-slide-automation/references/powerpoint-and-google-slides.md), [Microsoft reading order](https://support.microsoft.com/en-us/powerpoint/make-slides-easier-to-read-by-using-the-reading-order-pane) |

The verifier correction is a repository change. The installed private plugin
remains 0.4.14. No new dependencies, permissions or costs were introduced.

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

## Final visual pass

The same source and perspective coordinates were used for the final
comparison against the prior PowerPoint render. The cover now has an
editable continuous cloud outline, subtle blue gradient and separate
decorative shapes placed from the photo. The inside page follows the
reference's rounded banners and angled checklist header. Both office
pictures reach the bottom edge; the previous artificial backing strip is
gone. The left picture is masked along the diagonal so the original photo
caption does not show through the editable overlay. The caption, its
detail, and the small Tip label are separate native text objects.

PowerPoint 16 reopened and rendered both slides. The two final renders
were visually compared with the same aligned photo and the prior renders.
All 24 approved transcription checks passed, including both unreadable
markers. The deck contains 32 native text objects, seven independent picture
objects (five with transparency), and 13 native freeforms. On a copy, nine
changes to text, shape geometry and picture positions survived a save and
reopen. The final deck and previous revision hashes remained unchanged
during the edit test. The source, earlier revision, final deck, render and
overlay images are preserved privately.

Pretendard remains the temporary typeface. The exact original font, print
texture and small original illustration details cannot be verified against
the photo alone. This was a document revision; it did not alter the
installed 0.4.16 plugin, deployment or permissions.

## Reusable illustration and caption workflow

Candidate 0.4.18 extends the existing photo/CUSTOM guide after the plan approval
and perspective review. `prepare_photo_layers.py` uses a reviewed polygon to
remove the rectangular background from an illustration. It previews the edge
on light and dark backgrounds. For a descending caption, it masks the printed
caption from the picture and emits the matching native freeform coordinates.
The current authoring tool builds that shape and keeps title, detail and badge
text editable. A new photo needs its own crop and reviewed outline. The
triangular caption helper covers the slope used in this guidebook. Other
caption shapes stay in the manual native authoring path.

### Guidebook verification

The isolated candidate archive produced four illustration PNGs and one
caption-masked photo from the same guidebook. Its outputs matched the
repository tool byte for byte. The tool rejected an out-of-page diagonal and
an attempt to overwrite an existing review directory. All five images were
embedded in the candidate PPTX. The deck contains seven picture objects and
32 native text objects. Its caption is a native freeform. The existing
verifier passed 24 of 24 approved transcription checks.

PowerPoint 16 reopened and rendered both pages. Compared with the previous
final render, page 2 was pixel-identical. Page 1 differences stayed within
the illustration area. Inspection against the aligned source and light/dark
previews found no rectangular crop frames. Narrow handles and similar-color
edges still depend on the precision of the reviewed outline. In a copy,
picture movement, caption resize, caption detail and Tip text survived saving
and reopening. The candidate PPTX was unchanged during this edit test.
All guidebook inputs, derived images and decks are private. The current
operating plugin is 0.4.16. The candidate workflow was exercised locally
with the packaged code and existing runtime. Mobile and cloud execution of
this candidate have not been verified.

### Apply and restore

The personal private 0.4.16 source inventory reported 30 files. Both manifests
and the existing photo guide matched the archived base byte for byte.
Candidate and restore archives are partial updates for the same plugin.

| Private archive | SHA-256 |
| --- | --- |
| `slide-master-0.4.18-photo-layers.zip` | `67cbe5cfa482932044c2f8febd6834f5cc578c2217fb5bad87d6efc70f4cf9e2` |
| `slide-master-0.4.19-restore-0.4.16.zip` | `057f9f5f47fddbe6af6715edc506788ac22de5fb3ef16e6ed8a42a909a98ec4a` |

1. When applying, read back the exact existing private plugin and its current
   release ID. Use that ID as the update guard. If the base has changed,
   reconcile its source with the archive before sending an update.
2. Apply the 0.4.18 archive. It replaces two version manifests and the photo
   guide and adds one helper. The expected inventory is 31 files. Read back
   the version and affected bytes, confirm Google Drive and Template Picker
   declarations, refresh the host, and run the packaged workflow on the same
   guidebook. This package uses the existing Pillow dependency. It requires
   no new connection, permission or paid service.
3. To restore after a 0.4.18 deployment, read the current release ID and
   apply the 0.4.19 archive with explicit deletion of
   `skills/instructions/scripts/prepare_photo_layers.py`. If the host cannot
   request the deletion, stop the update until it can. Verify the restored
   30-file inventory, the original photo guide and both connections. The
   archive simulation restored the changed content byte for byte apart from
   the recovery version. The earlier 0.4.17 recovery archive remains preserved
   for its original 0.4.14 target.

### Additional quality improvements

| Order | Improvement | Decision |
| --- | --- | --- |
| 1 | Inspect masked images on dark and light backgrounds and compare the exact exported slide. Keep the approved outline separate from the photo. [Pillow polygon rendering](https://pillow.readthedocs.io/en/stable/reference/ImageDraw.html#PIL.ImageDraw.ImageDraw.polygon) | Included in the candidate. Useful for spotting crop edges and pale halos before delivery. |
| 2 | Keep freeform caption geometry independent of text and photos. Use the existing PowerPoint authoring tool to preserve native objects. [PptxGenJS custom geometry example](https://github.com/gitbrent/PptxGenJS/blob/master/demos/modules/demo_shape.mjs) | Included as a geometry handoff. No new authoring library. |
| 3 | Review the whole slide for hierarchy, then revisit changed areas at reading size. For shared decks, verify the reading order and meaningful image descriptions in PowerPoint. [PPTAgent](https://github.com/icip-cas/PPTAgent), [Microsoft reading order](https://support.microsoft.com/en-us/powerpoint/make-slides-easier-to-read-by-using-the-reading-order-pane) | Documented for production review. Add a reading-order check only after a representative shared deck is available. |
| 4 | Trial local foreground segmentation on difficult photos, with manual boundary correction. [OpenCV GrabCut](https://docs.opencv.org/4.x/d8/d83/tutorial_py_grabcut.html) | Deferred. The existing host does not have OpenCV, and segmentation may remove narrow details. Compare results on authorized samples before adding a dependency. |

# Photo-based company slides: analyze before authoring

This refines the existing CUSTOM/source-reconstruction path, not a new OCR
service or converter. User direction: company PPTs are often provided as
authorized photographs because the editable source is DRM-protected. Accept
the supplied image without requiring the unavailable original PPTX. Reconstruct
what is visible; do not claim to have extracted its original master or hidden
objects. Preserve each company's own appearance, with no automatic public
registration. Optional reusable registration keeps its existing separate gate.

## First visible response: analysis summary v1

Before slide authoring, inspect actual image pixels, then show a concise Korean
summary. Use one row per slide and one row per ambiguous region as needed:

| Item | Required observation / user-review field |
| --- | --- |
| Source and scope | Actual attached/private file, page/image number, readable area, requested slide count, preserved regions and requested changes. Record real source SHA privately when bytes are available. |
| Canvas | Observed slide boundary, aspect ratio, crop/rotation/perspective, blur, glare and missing edges. Distinguish a camera photograph from a clean screenshot. Preserve the source image; rectified views are separate derivatives. |
| Content | Title, headings, exact text, numbers, decimal points, units, dates and notes by region. Mark illegible text/numbers `[판독 불가: 위치]`; list ambiguous alternatives without selecting one as fact. |
| Layout | Relative region bounds, alignments, margins, spacing, box proportions, image crops and protected/right-hand areas. Separate the slide's geometry from the camera frame. |
| Color | Dominant background/text/accent/border colors and their evidence. Camera tint/glare makes exact brand RGB uncertain; prefer a supplied company palette when confirmed. |
| Typography | Family candidates, weight, alignment, line breaks, line/paragraph spacing and size hierarchy. Label each family/size as user-confirmed, observed estimate or unknown. OCR text recognition does not identify a font. |
| Tables and diagrams | Row/column boundaries, merges, headers/body/notes, cell padding, lines, arrow direction, box order and layers. Distinguish visible chart labels from unavailable underlying series/workbook data. |
| Editable plan | Native text, tables, simple shapes and connectors; separate photo/logo/complex-art assets. Declare object-level raster editability separately from editable internal geometry. Do not use one full-slide screenshot as the final editable slide. |
| Questions and production plan | Collect only missing consequential information together: font name/size, palette, unclear values, allowed crop, slide ratio or an editable chart's actual data. Show proposed reconstruction and wait for real approval of its current version. |

Example Korean response structure (fill with actual observations, never example
values presented as image-derived facts):

> 사진 분석 v1: 원문·수치 / 배치·색상 / 글꼴·크기(확정·추정·미확인) /
> 표·도식·이미지 / 읽기 어려운 부분 / 편집형 재구성안 / 추가 확인 사항.

Do not re-ask supplied information. User corrections become analysis/brief v2;
retain the source and approved snapshot. If layout/content changes after approval,
the existing current-revision approval rule applies again. A recovered synthetic
fixture is not a substitute for the user's absent photo or approval.

## Scale, fonts and preservation

Pixel glyph height is not a directly observed PowerPoint point size. Record the
assumed target slide dimensions and relative positions before estimating sizes;
do not apply an arbitrary 96-DPI conversion as an exact source-font finding.
Retain uncertainty if the slide boundaries or physical dimensions are unknown.

For this user's explicitly requested company jobs, record SamsungOneKorean and
14/12/11/9pt roles plus the table maximum 12pt. If those constraints conflict with
the photographed hierarchy, explain the conflict in the analysis and obtain the
current task decision. They are not global template defaults. No silent font
substitution; Samsung installation/rendering/embedding still requires its
separately established rights. Temporary approved Pretendard remains temporary.

Photo matching is a visual comparison, not source-PPTX XML/master preservation.
For protected areas, compare aligned source-image and exact exported-slide
regions; retain unknowns caused by image quality. Preserve all visible content
unless a real user edit allows a change. Do not invent hidden chart data or an
embedded workbook from photographed labels. Obtain data if native-data editing
is required, otherwise state the actual editable representation.

## Existing production and final QA

After current analysis/design approval, use the existing CUSTOM host-production
owner / route-selected presentation finalizer, not an unrelated installed skill.
Record genuine file/actor/approval evidence and any route exemption; this policy
does not bypass the request guard. Reuse the dense inspector and reference
contracts for supported elements; report unsupported photo semantics separately.

Reopen the exported exact PPTX, render all slides and compare against the source
and approved analysis. Check wording/numbers, Korean line breaks, actual fonts,
row/column sizes, padding, line spacing, merges, image crops, borders and arrows.
Inspect native editability independently of visual similarity. Keep actual
PowerPoint checks distinct from other renderers. Deliver privately and preserve
source, approved analysis, final bytes, QA and recovery in the authorized stores.

## Application boundary

Linked from repository canonical instructions and project instructions. Existing
plugin 0.4.5 already includes photo/CUSTOM analysis, real approval and native
production guidance; this more detailed supplement is **source guidance**, not
a new plugin release or a newly validated photo-to-download round trip. No new
company photo is present in this turn, so no photo-specific analysis, production
or font/layout similarity pass is asserted. See
[source research and adoption decisions](PHOTO_RECONSTRUCTION_RESEARCH_20261108.md).

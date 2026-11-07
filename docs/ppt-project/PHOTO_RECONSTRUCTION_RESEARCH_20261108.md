# Photograph-to-editable-PPT research and adoption decisions

Continues [the earlier resource review](PPT_RESOURCE_REVIEW_20261107.md) for the
user's frequent company-photo input. Primary READMEs, relevant implementation
and license documents were inspected. No repository/model was installed, no
external OCR API called, and no company image sent to a third party. These are
engineering references, not established design authorities or measured Korean
company-photo benchmarks. Small project demos do not establish production quality.

## Findings

| Source | Useful evidence / limitation | Decision for existing Slide Master |
| --- | --- | --- |
| [PaddleOCR PP-StructureV3](https://github.com/PaddlePaddle/PaddleOCR/blob/main/docs/version3.x/pipeline_usage/PP-StructureV3.en.md), [Korean recognizer card](https://huggingface.co/PaddlePaddle/korean_PP-OCRv5_mobile_rec), [code license](https://github.com/PaddlePaddle/PaddleOCR/blob/main/LICENSE) | Structured text/layout/table coordinates; optional document preprocessing and table recognition. Korean text-line model has an Apache-2.0 card. Neither identifies the actual font nor recreates an editable company master. Model pipeline/dependency size and Korean merged-table performance need measurement. | Best optional independent transcription/bbox cross-check after a concrete install/model/storage approval; not installed now. Keep text disagreements and unreadable values visible in user review. Prioritize current supplied-model analysis to avoid new dependencies/cost. |
| [NoahYUYE/image-to-editable-ppt](https://github.com/NoahYUYE/image-to-editable-ppt), [reconstruction playbook](https://github.com/NoahYUYE/image-to-editable-ppt/blob/main/references/reconstruction-playbook.md), [MIT license](https://github.com/NoahYUYE/image-to-editable-ppt/blob/main/LICENSE) | Workflow explicitly needs a separate PPT authoring/rendering owner. Separates native text/geometry from image layers; requires aspect-ratio/layer/crop review. Near-white transparency may remove object details. It is not a standalone automatic converter. | Reinforce the existing CUSTOM owner with an element/editability plan and final-byte image comparison. No new competing skill; do not flatten text/tables into a background or mask away white details. |
| [BRCOO/image2pptx](https://github.com/BRCOO/image2pptx), [actual COM conversion script](https://github.com/BRCOO/image2pptx/blob/main/scripts/svg-to-editable-ppt.ps1) | Converts reconstructed semantic SVG through desktop PowerPoint's SVGEdit command and ungrouping. Source inserts SVG as a picture first and requires Office/interactive COM for editable conversion. The inspected root did not establish a LICENSE (`main/LICENSE` returned 404). | Read-only engineering reference. Do not copy/install its code or replace existing native DrawingML export. Semantic reconstruction already fits our owner; shape counts or SVG ungrouping do not prove editable Korean text/native tables. It does not solve PC-off execution. |
| [Daniel-Siae/image2pptx](https://github.com/Daniel-Siae/image2pptx), [MIT license](https://github.com/Daniel-Siae/image2pptx/blob/main/LICENSE) | OCR JSON plus original-image bbox crops become text/table/image objects. README explicitly acknowledges inaccurate font sizes, line spacing, wrapping and complex merged cells. Its OCR path uses an AI Studio token/remote Jobs API; server source directory could not be retrieved through the web tool in this pass. | Borrow only the inspected diagnostic idea, not uninspected code. Keep bbox overlays/intermediate review separate from a fidelity pass. Do not add token, API, external company-file processing or depend on its service. |
| [guohuan-xie/image2PPT](https://github.com/guohuan-xie/image2PPT), [actual dependencies](https://github.com/guohuan-xie/image2PPT/blob/main/pyproject.toml) | Flat-infographic pipeline with OCR, simple shapes/freeforms and raster fallback. Requires OpenCV, rapidocr-onnxruntime, vtracer and Ultralytics/SAM; README says missing SAM weights may auto-download on first use. No license was established from the inspected root/pyproject. | Do not install/copy or allow first-run model downloads. Practical element-level editability reporting is relevant, but not evidence of camera-photo/Korean/table fidelity. |

The useful common pattern is explicit scene/region analysis followed by native
authoring and inspection of the final exported file. None of these inspected
sources establishes exact family/point-size recovery from arbitrary photographs,
perfect merged-cell fidelity or automatic private delivery under our current
connections. No scores from their demos are attributed to Slide Master.

## Applied now, and work still needed

1. Linked [photo analysis first](PHOTO_CUSTOM_RECONSTRUCTION.md) from existing
   canonical/project instructions: source pixels, uncertainty, typography and
   user-supplied corrections precede current-revision approval and production.
2. Clarified that per-job CUSTOM company use does not require public registration
   or an unavailable original PPTX. Preserve visible text/numbers/layout; retain
   separate editable vs image-only region declarations and current font rights.
3. Retained existing authoring/finalizer/inspector rather than introducing another
   converter, generic OCR install or cloud service. No upstream code copied.
4. Next actual-photo acceptance needs an authorized attached photo and its real
   analysis/current approval. Compare the exact exported slide to that photo,
   retain uncertain fields, check native text/table/shape editability and provide
   verified private bytes. Existing synthetic results do not establish this pass.

This supplement is repository guidance, not an installed plugin release or a
new OCR integration. Current main plugin remains 0.4.5. Any later operational
package update must preserve its identity/dependencies/recovery and receive the
required concrete scope/impact/recovery review. Optional OCR approval, if ever
needed, must name exact versions/weights/host/download size/storage/outbound
processing/cost and uninstall or file-cleanup recovery; do not seek a blanket
approval for unknown installation requirements.

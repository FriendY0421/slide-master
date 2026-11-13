# Precision work without a company source PPTX

Continues #14 and the [ChatGPT/DOTS handoff](CHATGPT_DOTS_HANDOFF.md).
Date: 2026-10-13, Asia/Seoul. This is implementation and engineering validation;
it does not close company-source, font-rights or authenticated-delivery acceptance.

## Primary open-source references inspected

| Source | Useful capability | Decision for this repository |
|---|---|---|
| [PptxGenJS](https://github.com/gitbrent/PptxGenJS), [image sizing](https://gitbrent.github.io/PptxGenJS/docs/api-images.html), [table API](https://gitbrent.github.io/PptxGenJS/docs/api-tables.html) | Separate contain/cover/crop intent; explicit columns, margins and table paging | Keep the existing converter; bind image intent and table geometry in the final contract |
| [python-pptx](https://github.com/scanny/python-pptx), [picture API](https://python-pptx.readthedocs.io/en/latest/api/shapes.html), [paragraph API](https://python-pptx.readthedocs.io/en/latest/api/text.html) | Native editable objects and explicit paragraph spacing; supplying both picture dimensions can stretch it | Inspect the final visible-source aspect ratio and the exported spacing values |
| [Microsoft Open XML SDK](https://github.com/dotnet/Open-XML-SDK), [validator](https://learn.microsoft.com/en-us/dotnet/api/documentformat.openxml.validation.openxmlvalidator) | Package/schema checks and chart/workbook operations | Potential optional structural layer; no SDK installed or new dependency added |

These tools are relevant references, not a guarantee of elegant layout or Korean
line breaking. Schema validity is separate from visual quality. No third-party
source was vendored, no new service was connected and no package was installed.
The repository already had editable contain/slice picture conversion: it was
reused, not rewritten. Automatic table paging would change the approved slide
count, so it is not silently applied to the user's company material.

## Implemented refinement

The existing dense final-PPTX inspector now verifies exact paragraph line spacing
or multiples, paragraph before/after spacing, header/body-specific table spacing
and alignment, requested object positions, shared anchors and object gaps.

Native embedded raster pictures are checked for aspect distortion, effective
resolution after cropping, forbidden crop and removal of a declared important
source rectangle. An unreadable picture is unverified. Rotated/grouped layouts,
vector formats, clipping masks and subject recognition need separate review.

The new provisional `text_metrics: structure_only` mode checks explicit fonts,
sizes, spacing, margins and layout without reading fonts. It does not estimate
text height/width and does not certify wrapping/clipping. `verify_deck.py` rejects
this mode for final acceptance, even if the limited inspector checks pass.
The default remains actual-font measurement; no typography profile was forced
on other templates. See [contract recipe](DENSE_PPTX_QUALITY.md).

The executor reference now instructs authoring to bind these constraints, revise
the existing source geometry on failures and re-export. This reaches the existing
SVG→DrawingML→dense verifier path; it is not installed into the live plugin.

## Evidence

An original synthetic raster source was generated with simple colored geometry;
no external photos or font files were used in the inspector. The existing
`create_pptx_with_native_svg` exported two editable pictures and a native table
with header 12pt, body 11pt and note 9pt plus explicit 14pt table line spacing.
The narrow identifier column and wide Korean-description column were retained.

- Limited inspector: zero errors, nine checked image/text/cell targets.
- Eleven negative copies/contracts were rejected: distortion, inadequate DPI,
  protected crop, wrong alignment/gap, changed line spacing, undersized body,
  changed margin, missing spacing object, wrong object kind and nonfinite geometry.
- The previous dense output still passes structural regression without font loads.
- The final verifier explicitly rejects the provisional mode as its only failed
  check in the isolated fixture. A planning-artifact warning remains; this test
  does not create an approved production storyline or certify a company deck.
- PowerPoint 16.0 opens two native pictures and one editable table. Picture frame
  positions and crop are read back; export preview was inspected and source hash
  stayed unchanged. Requested-font rendering remains false.
- Python compilation and whitespace checks pass. Public sanitized evidence is
  [precision-validation-20261013.json](evidence/precision-validation-20261013.json).

The fixture is not a finished company deck. The native-renderer shutdown failure,
SamsungOneKorean permissions/actual wrapping, company preservation, plugin editor
and stored connection identification, cloud execution and private user receipt
remain open. No replacement plugin, merge, deployment, install, font registration,
embedding, new authentication or paid resource was activated.
## Early-line overflow follow-up

The actual-font inspector previously compared only the last line's width when
`wrap=none`. A long first line followed by a short line could measure 180.625pt
inside a 100pt box without a `TEXT_WIDTH` error. It now checks the maximum line
width within each paragraph, including all explicit line breaks. Text, font
sizes, wrapping settings and exported content are not automatically changed.

Actual bundled OFL Pretendard 11pt probes: first-line and last-line overflow both
reject; short two-line text and normal wrapping pass. The existing temporary
native PPTX still has zero errors over nine target regions (one design warning).
This checks font metrics, not Samsung rendering or actual PowerPoint behaviour.
See [limited evidence](evidence/early-line-validation-20261013.json).

# Brand deck composition references — 2026-11-11

Follow-up to [PR #14](https://github.com/FriendY0421/slide-master/pull/14) and
the [previous resource review](PPT_RESOURCE_REVIEW_20261107.md).

## Public presentations reviewed

| Source | Evidence | Transfer to Slide Master |
|---|---|---|
| [Microsoft Financial pitch deck](https://powerpoint.cloud.microsoft/create/en/pitch-deck-templates/) | Official editable PPTX, selected pages rendered in PowerPoint. Page 10 aligns comparisons and page 12 uses dated growth stages. | Align comparable figures and give milestones a consistent reading direction. |
| [Microsoft Retail pitch deck](https://powerpoint.cloud.microsoft/create/en/pitch-deck-templates/) | Official editable PPTX, selected pages rendered in PowerPoint. Pages 7 and 9 use a section transition and separate text/metric and image zones. | Use the subject and available space to choose a split layout. Preserve approved information density. |
| [Apple WWDC19 — Modernizing Your UI for iOS 13](https://developer.apple.com/videos/play/wwdc2019/224/) | The official slide PDF was rendered locally. Page 8 pairs a short principle with a separate full-height phone UI. | Give a product or screen room to be read, with its explanation beside it. |
| [Netflix Culture](https://www.slideshare.net/slideshow/culture-1798664/1798664) | Historical original linked from the [Netflix culture memo announcement](https://about.netflix.com/en/news/sharing-our-latest-culture-memo). Pages 3–7 move from principle to concrete behaviors, and pages 19 and 40 reprise the outline. | Use principle, example and action in training. Reorient the audience at major section changes in a long deck. |
| [NVIDIA October 2023 Investor Presentation](https://investor.nvidia.com/files/doc_presentations/2023/Oct/NVIDIA-Oct-2023-Investor-Presentation.pdf) | Official PDF text inspected. The deck uses common periods in a comparison and describes a cycle connecting users, developers and ecosystem growth. | Keep periods explicit. Use a directional loop only when the content has a return path. |

Apply structure and reading order. Use the approved template, palette, type and
authorized project assets. Brand artwork, screenshots and template files are
excluded from the changes.

## Figma Community follow-up

The [user-supplied Community presentations gallery](https://www.figma.com/ko-kr/community/presentations?resource_type=files)
could not be loaded by the research browser. Figma's own public examples and
documentation support the following additions. Individual Community previews,
rankings, and usage counts remain unverified.

| Source | Evidence and application |
|---|---|
| [Figma's template examples](https://www.figma.com/resource-library/what-is-a-slide-deck/) | Project Review separates objectives, results and takeaways. Product Roadmap presents strategy, timeline and metrics. Use a dedicated decision zone in reviews and a shared time axis in roadmaps. |
| [Figma's Redesigning Finance](https://static.figma.com/uploads/6ed58f992ed1fa443b27259144770d48803bbf82.pdf) | The “Apps Then → Apps Now” example uses real interface comparisons to support a chronology. Align comparable screens and place editable callouts outside the image. |
| [Figma's slide template guide](https://help.figma.com/hc/en-us/articles/26621828788631-Find-and-use-slide-deck-templates) | Choose layouts by page purpose while reusing type and color styles. Apply the layout principle inside Slide Master's approved visual system. |

The catalog is a reference source. Existing template IDs and the editable
PowerPoint production route continue to own export. If a later task calls for
reusing a Community asset, check its individual terms and attribution first.
[Figma Community publishing guide](https://help.figma.com/hc/en-us/articles/25923960876567-Publish-slide-deck-templates-to-the-Figma-Community)

## GitHub features reviewed

Star counts from the GitHub API on 2026-11-11. Capabilities are based on project
documentation.

| Project | Stars | Relevant feature and production consideration |
|---|---:|---|
| [reveal.js](https://github.com/hakimel/reveal.js) | 72,554 | Themes, overview and nested pages in an HTML deck. The overview is a useful reference for reviewing deck pacing and hierarchy. |
| [Slidev](https://github.com/slidevjs/slidev) | 49,434 | Reusable layouts and components. Standard PPTX export uses slide images. The editable option can rasterize unsupported elements or fall back to a slide image. [Export guide](https://sli.dev/guide/exporting) |
| [Presenton](https://github.com/presenton/presenton) | 11,855 | Template previews and an editor. The preview pattern supports showing a meaningful layout before the user chooses. |
| [PptxGenJS](https://github.com/gitbrent/PptxGenJS) | 6,370 | Slide masters and native PowerPoint text, charts, tables and shapes. These are useful criteria when comparing any future export route. |
| [PPTAgent](https://github.com/icip-cas/PPTAgent) | 5,239 | Reference-slide analysis by functional role, outlining and revision. Apply the reference-role idea inside the existing composition planning step. |
| [Marp CLI](https://github.com/marp-team/marp-cli) | 3,913 | Predictable visual preview. Standard PPTX uses slide images and the editable export is experimental. |

## Change and verification

- The existing [composition planning reference](../../.claude/skills/ppt-master/references/composition-planning.md)
  now maps page purpose to composition. Strategist and Executor already load it.
- The private 0.4.12 candidate carries the same patterns in the precision design
  reference and preserves the existing mobile and font delivery guidance. The
  previous candidate and the 0.4.13 recovery package are retained.
- No dependency, renderer or app connection changed. The private plugin release
  and actual PPTX/mobile output review remain pending.

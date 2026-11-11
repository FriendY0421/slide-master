# Composition Planning Reference Manual

Apply content-led composition and subject-aware image placement during Strategist planning and Executor authoring.

## 1. Scope and precedence

**Hard rule**: Preserve the selected route, source facts/numbers, protected regions,
confirmed template/preset, typography, colors, image sources and current storyline
approval. Design refinement never grants permission to rewrite, split, reorder,
change a fixed page count, acquire images or switch fonts. Preserve native tables,
charts/workbooks and editable text; never flatten a slide for visual polish.

| Route / constraint | Apply |
|---|---|
| New SVG deck / approved re-architecture | Plan composition in existing §IX, within the locked template and content approval. |
| Strict template or mirror | Use allowed slots and exact preservation rules; omit incompatible alternatives. |
| Beautify | Apply only within its confirmed visual-redesign scope; preserve every source page and word. |
| Native template-fill / native enhancement | Retain that owner's geometry and QA; do not import this SVG authoring process. |
| Dense company/photo reconstruction | Preserve task-specific sizes, source text/numbers and protected geometry; never apply generic whitespace/type defaults over them. |

**Hard rule**: An unavailable source image, font or rendering tool stays explicitly
unverified. Do not manufacture previews, source details, subject detection or QA.

---

## 2. Content-led composition selection

**Default — choose by the message (may override for the confirmed template)**:

| Content relationship | Composition to consider | Preserve |
|---|---|---|
| Equal alternatives / before-after | Matched side-by-side panels with aligned comparison rows | Comparable scale and equal evidence weight. |
| Sequence / procedure | Editable steps or timeline following reading order | Every step, direction and dependency. |
| Main result + supporting evidence | One focal number/chart with a smaller evidence zone | Units, time period, source and uncertainty. |
| Product / place / person | Subject-led hero image with a separate text zone | Subject, relevant context and image rights. |
| Explanation + evidence photo | Asymmetric text/photo split; image size follows its evidentiary role | Caption and details needed to interpret the evidence. |
| Dense report / table | Aligned table plus compact takeaway within the approved geometry | Values, labels, merge structure and fixed type. |

**Default — compare design directions inside the existing confirmation**: When
visual direction is undecided, attach a concrete composition description to the
existing safe/shifted/bold style candidates. Keep source content identical across
candidates. Describe focal point, text/image arrangement and expected density;
recommend the best content fit. Do not add another mandatory confirmation stage,
a new style enum or an automatic template/preset switch. If direction is already
confirmed, use it and skip the repeated choice.

**Hard rule**: Label descriptions as proposals. Call a preview rendered only when
an actual visible output exists. Use actual registered previews at the template
stage; do not generate slide SVGs/PPTX as a shortcut around storyline approval.

**Per-page planning**: In the existing §IX visual/layout treatment, record the
composition, focal object, reading order and image intent. Reuse §VIII image rows
for filename/source/status. Use prose within existing fields; add no required
schema keys and do not invalidate legacy projects lacking these details.

```text
Visual/layout: result-led composition; editable chart is the focus on the left;
key takeaway and source on the right; matched baselines and locked typography.
Image intent (when used): product photo in the right zone; preserve the whole
product and label; contain if a subject-safe crop cannot be achieved.
```

---

## 3. Subject-aware image placement

**Mandatory**: Inspect the actual available image before deciding its crop.
Identify the meaningful subject and any indispensable labels, hands, equipment,
chart axes or evidence context. Mark uncertain details as unknown; inspection is
not an automatic face/object detection service.

| Condition | Placement action |
|---|---|
| Formula, screenshot, document, chart image, `no-crop` or evidence context required | Use contain/meet and adapt the surrounding layout; preserve all meaningful content. |
| Decorative/photo asset permits cropping | Try cover/slice; check the actual visible source region before accepting it. |
| Important subject would be cut | Move the frame or use supported SVG image alignment, change the frame ratio, or use contain; never stretch the picture. |
| Text would obscure the subject | Move text to negative space or a separate panel; use only locked overlay colors and confirm rendered legibility. |
| Low-resolution image | Reduce display area or request an authorized better source; do not claim recovered detail. |
| Acquisition failed / image missing | Follow existing image-owner failure handling; a placeholder is not a completed production image. |

**Reference — centered crop arithmetic**: For source `Ws × Hs` and frame
`Wf × Hf`, cover scale is `s = max(Wf/Ws, Hf/Hs)`. The visible source window
is `(Wf/s) × (Hf/s)`, with centered origin
`((Ws-Wf/s)/2, (Hs-Hf/s)/2)`. Compare the observed subject against this window.
A 1600×900 photo in a 600×600 frame retains only the central 900×900 source
region (`x=350..1250`); a label outside that region requires another placement.
Use existing supported image alignment/contain/slice conversion; invent no crop
metadata. Preserve original image bytes and record any derived asset separately.

---

## 4. Execution and review

**Mandatory**: Read §IX for the current page along with the existing spec lock.
Resolve zones from locked type and actual image dimensions before drawing; use
existing text-fit and geometry checks. If an approved layout cannot accommodate
protected content, report the conflict rather than silently changing the outline.

| Review | Action |
|---|---|
| Hierarchy | Check that the message/focal visual is apparent and supporting material remains readable. |
| Alignment and spacing | Use shared baselines, consistent margins/gutters and locked role sizes. |
| Deck rhythm | Review adjacent pages for unjustified identical layouts; vary within approved content/template limits. Repeated comparison/report layouts may be intentional. |
| Image treatment | Check subject visibility, aspect ratio, crop, caption, attribution, resolution and text contrast in actual final renders. |
| Preservation | Compare protected content/regions and native chart/table/workbook structures using existing task contracts. |

**Hard rule**: Taste judgments are review recommendations, not new mechanical
failure rules or numerical beauty scores. Fix objective clipping, overlap, missing
content and broken editability through the existing owners. Do not add forced
layout quotas, decorative filler pages, automatic copy shortening or font shrinking.

**Validation**: Run the existing route's required quality/export/reopen/render
checks on exact final bytes. Fold this review into its existing final rendered
scan; do not auto-enter optional per-page visual-review or verify-pptx-export.
Report which checks actually ran and which remain unverified. A structural pass
alone does not certify aesthetics, exact fonts or recipient acceptance.

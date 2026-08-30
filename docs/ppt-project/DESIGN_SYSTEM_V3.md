# Slide Design System V3 — Professional Readability & Composition

Updated: 2026-08-30 KST
Status: CURRENT for new Slide Master PPTs on `main`

## 1. Authority and evidence policy

This design system uses only widely validated references. External GitHub projects are eligible only when they are actively maintained, presentation-relevant, and have at least 1,000 GitHub stars. One-off demo repos and small personal AI-PPT experiments are excluded from design authority.

Accepted reference set at this checkpoint:
- Microsoft PowerPoint Support — official readability/accessibility guidance.
- Duarte — long-running professional presentation design and storytelling practice; one-idea-per-slide and Glance Test principles.
- Presentation Zen / Garr Reynolds — simplicity, rule of thirds, Contrast/Repetition/Alignment/Proximity.
- Presentation Process — verified YouTube channel, 25+ years practitioner experience, 1,000+ videos / 40M+ views, global corporate-training use.
- `hakimel/reveal.js` — 72k+ stars, mature presentation framework.
- `slidevjs/slidev` — 46k+ stars, actively maintained presentation ecosystem.
- `marp-team/marp` — 11k+ stars, verified presentation ecosystem.
- `gitbrent/PptxGenJS` — 6k+ stars, mature programmatic PPTX generator.

GitHub references inform engineering stability, layout/theming architecture, and reusable-slide structure. They do **not** override Microsoft/Duarte/Presentation Zen on human readability or visual communication.

## 2. Core communication formula

Every content slide must pass this equation:

`ONE SLIDE = ONE ASSERTION + ONE FOCAL VISUAL + SUPPORTING EVIDENCE`

- If a slide has two independent assertions, split it.
- Content-slide titles should state the so-what whenever possible; label-only titles are reserved for navigation/section roles.
- A viewer should understand the slide's direction from the title + dominant visual before reading detail copy.
- Decorative elements that do not support the assertion are removed.
## 3. Typography formula

For a 1280×720 PPT canvas, the normal new-deck defaults are:

| Purpose | Body | PowerPoint equivalent | Typical use |
|---|---:|---:|---|
| `text` | 28px | 21pt | read-close leave-behind |
| `balanced` | 34px | 25.5pt | business review / mixed use |
| `presentation` | 40px | 30pt | room projection / keynote |

- 24px / 18pt is a hard emergency floor for non-mirror PPT body text, not the normal target.
- Page title: about `1.55–1.8 × body`; subtitle/lead: `1.15–1.35 × body`.
- Body line height: `1.35–1.50 × font size`; title line height: `1.08–1.18 ×`.
- Card title → body gap: 16–24px. Related paragraph/bullet groups: 12–20px.
- For projected slides, treat Microsoft's “font below 30pt may be difficult” guidance as a strong reason to prefer the `presentation` profile rather than shrinking copy.
- The accessibility “6×7” convention is an upper-density warning, not a target: avoid more than ~6–7 meaningful text lines on a projected slide unless the page is explicitly a read-close/table page.

## 4. Composition formula

Use a 12-column mental grid and the rule of thirds as guides, not rigid templates.

Normal content-page geometry:
- Outer safe margin: 56–72px horizontal, 40–56px vertical.
- Primary block gap: 24–36px.
- Text card padding: 28–36px horizontal, 20–30px vertical.
- Prefer asymmetric weight such as 60:40 or 65:35 for text+visual pages. Use 50:50 only for true comparisons.
- A meaningful image/chart should usually occupy about 35–60% of the usable content area. Tiny decorative thumbnails are discouraged.
- Normal `dense`/business pages should visually use about 68–88% of the safe content zone. `breathing` pages may intentionally use less when the whitespace amplifies one focal idea.

## 5. Card and hierarchy formula

- Prefer 1–3 primary content regions per slide.
- 4 peer cards are allowed only when the four-way comparison itself is the message.
- 5+ equal rounded cards on a normal slide are a redesign signal: regroup, convert to process/table/diagram, or split the slide.
- A card is not a default wrapper for every sentence. Use naked text, dividers, bands, diagrams, imagery, and whitespace to vary rhythm.
- Use one dominant color role, one accent, and neutral support colors. Not every label should be accented.
- Use contrast, repetition, alignment, and proximity consistently: related items sit closer; unrelated groups get visibly larger separation; aligned edges form deliberate reading paths.
## 6. Rhythm and long-deck formula

A professional 20–30 slide deck should not look like one layout duplicated many times.

- Do not repeat the same card-grid signature for 3 consecutive content slides without a content-driven reason.
- Across a long deck, alternate evidence modes: hero statement, text+visual, comparison, process, data/chart, diagram, case/example, summary.
- `page_rhythm` remains narrative-driven: `anchor`, `dense`, and `breathing` are selected by the story, not by a fixed quota.
- User-requested 20/30+ slide counts are valid. Expand by splitting genuine ideas, evidence, examples, phases, cases, FAQs, and appendices — never by filler or repeated wording.
- If evidence cannot support the requested count, disclose that in the slide-by-slide preview before generation.

## 7. Mandatory pre-generation preview

After template + production preset lock and any needed research, show the full slide plan in chat **before authoring/export**.

Each row must contain:
`slide number | title | core message | key content | visual/layout plan`

The user may modify, delete, add, reorder, or change the requested slide count. After any modification, show the updated full plan again. Only the explicitly approved current version may generate `storyline_approval.json` and permit PPT production.

## 8. QA acceptance

The final deck must pass both machine and visual checks:
- typography/spec-lock consistency;
- text fit and overlap checks;
- design-quality heuristics for card overload, cramped line spacing, dead-space imbalance, and repeated layouts;
- PPTX contact-sheet scan for converted-pixel reality;
- no silent reduction below approved typography to solve overflow.

When a visual defect remains, fix the owning layout/content source rather than cosmetically shrinking everything.

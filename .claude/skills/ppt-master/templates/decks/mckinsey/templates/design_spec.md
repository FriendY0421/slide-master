---
deck_id: mckinsey
kind: deck
category: scenario
summary: McKinsey consulting-style strategy decks — 전략 보고서, 시장/산업 분석, 경영진 브리핑, 실행 로드맵
keywords: [consulting, strategy, executive-summary, evidence-led, data-dense]
primary_color: "#0F2A4A"
theme_mode: mixed
canvas_format: ppt169
canvas_width: 1280
canvas_height: 720
canvas_viewbox: "0 0 1280 720"
source_canvas_width: 1280
source_canvas_height: 720
source_viewbox: "0 0 1280 720"
replication_mode: fidelity
native_structure_mode: structured
page_count: 10
---

# McKinsey Consulting Style Deck — Design Specification

> Style homage benchmarked from the MIT-licensed `seulee26/mckinsey-pptx` generator. This is not an official McKinsey identity and contains no trademark assets. Colors are third-party approximations; typography follows this repository's install-local Pretendard lock.

## I. Template Overview

- **Use cases**: 전략 보고, 시장·산업 분석, 경영진 브리핑, 실행 로드맵, 투자 검토, 조직 진단.
- **Tone**: restrained, hypothesis-driven, evidence-first.
- **Theme**: white evidence pages with dark-navy chapter and ending pages.
- **Recognition test**: action titles argue; bodies prove. Reading only the action titles must reconstruct the storyline.
- **Anti-mood**: marketing keynote, gradient SaaS dashboard, decorative infographic, rounded-card gallery.

The content chrome is fixed to a 44px safe margin, a title rule at y=112, a content zone at x=44 / y=136 / w=1192 / h=524, and a footer rule at y=676. Dark structural pages use wide negative space rather than dense evidence.

## II. Color Scheme

| Role | HEX | Application |
| --- | --- | --- |
| Background | `#FFFFFF` | Evidence pages |
| Primary navy | `#0F2A4A` | Structure, primary series, key numbers |
| Deep navy | `#0A1F3D` | Chapter and ending backgrounds |
| Accent | `#2E9BD6` | One focus entity, series, number, or pointer per page |
| Blue mid | `#1F6FA8` | Secondary chart series |
| Blue light | `#4FB2E5` | Tertiary series and dark-page secondary text |
| Text | `#1A1A1A` | Primary text |
| Secondary text | `#888888` | Labels, support, sources |
| Title rule | `#999999` | Content-page title rule |
| Grid | `#D0D0D0` | Chart grids and footer rule |
| Border | `#E8E8E8` | Quiet dividers |
| Surface | `#F2F2F2` | Table banding and neutral comparison shapes |

- Navy carries hierarchy; cyan identifies exactly one analytical focus.
- The same focus may repeat across exhibits, but unrelated items must not compete for accent.
- Charts use the navy ladder; all remaining hierarchy is weight, banding, and hairlines.
- Gradients, shadows, glow, 3D, and decorative traffic-light colors are outside this deck identity.

## III. Signature Design Elements

### Action-title chrome

Content pages use an optional 13.3px uppercase kicker, a declarative 32px action title, the y=112 title rule, a 12px source line, and a right-aligned page number. Label-only and question-form evidence titles are not part of this template.

### Executive-summary choices

- **Keyword stack**: choose for 3–5 independent findings or when quantitative evidence is thin. Each row uses a 4px navy bar, a classification kicker, one finding sentence, one support line, and a hairline. This list-led pattern remains a first-class option.
- **Thesis chain**: choose only when one conclusion follows from 2–4 connected drivers. Use one full-width thesis band, an integrated outcome comparison, one left-to-right causal chain, and one watchpoint. Do not turn it into a row of unrelated mini charts.

### Visual-evidence family

- The action title owns the primary takeaway. The body contains exhibits, chart labels, table labels, and at most one compact bottom `INSIGHT` strip—never a prose findings rail.
- **Evidence matrix**: four exhibits must jointly prove one thesis; avoid four unrelated dashboard widgets.
- **Trend + small multiples**: use one shared time-axis story above and four diagnostic views below.
- **Primary + supporting exhibit**: limit the body to two major zones. The right zone contains one integrated supporting visualization and never another nested mini-grid.
- `INSIGHT` is the label for analytical synthesis. `VERDICT` is reserved for genuine option selection, approval, or recommendation pages.

### Metric and density discipline

- Every emphasized number carries subject, metric, time, and unit in the same visual group. Place deltas beside their compared values; detached `+X`, `%`, or `%p` callouts are not allowed.
- Dense exhibits use 12px microtext instead of shrinking below the ramp. When content does not fit, shorten copy or change layout.
- **Font scale policy**: `fixed-no-upscale`. Empty space never triggers automatic type enlargement.
- Same pattern may appear at most twice in succession; preserve the generic content shell for compositions outside the five authored variants.

## IV. Typography System

Install-local Pretendard is the deck typeface. Weight cuts are authored as installed family names; `Malgun Gothic` is the Korean fallback.

| Role | Size px | Weight | Use |
| --- | ---: | ---: | --- |
| Hero number | 64 | 700 | Single data hook only |
| Display | 48 | 700 | Cover, chapter, ending |
| Display small | 40 | 700 | Chapter marker, large comparison value |
| Action title | 32 | 700 | Declarative content-page headline |
| Compact KPI | 29 | 700 | Dense but prominent KPI |
| Subtitle / block title | 18.7 | 600 | Summary and exhibit blocks |
| Finding title | 16.5 | 600 | Compact finding or insight lead |
| Body / insight | 16 | 400/600 | Body copy, table cells, insight sentence |
| Exhibit title | 15 | 600 | A/B/C/D exhibit headers |
| Annotation / label | 13.3 | 500/600 | Kicker, axis label, category, support |
| Dense chart microtext | 12 | 400/600 | Dense axes, legends, data labels |
| Dense table header | 12 | 600 | Compact table headers |
| Footer | 12 | 400 | Source line and page number |

`Action title 32 / Body 16 / Subtitle 18.7 / Annotation 13.3` is the default locked candidate when this deck is selected. Delivery purpose changes page density and rhythm, not this size ramp, unless the user explicitly overrides typography.

## V. Page Roster

All pages use Master `mckinsey-master`. Existing five prototypes remain unchanged; the five content variants are newly authored fidelity-mode layouts.

| File | Role | Layout key | PowerPoint picker | Intended content and slot topology |
| --- | --- | --- | --- | --- |
| `01_cover.svg` | cover | `01_cover` | Cover | Asymmetric consulting cover |
| `02_toc.svg` | toc | `02_toc` | Agenda | Four ruled agenda rows |
| `02_chapter.svg` | chapter | `02_chapter` | Chapter | Dark-navy section reset |
| `03_content.svg` | content | `03_content` | Content | Generic action-title shell; Executor composes the body |
| `03a_content_keyword_stack.svg` | content | `03a_content_keyword_stack` | Executive Summary — Keyword Stack | One composite findings zone supporting 3–5 rows |
| `03b_content_thesis_chain.svg` | content | `03b_content_thesis_chain` | Executive Summary — Thesis Chain | Thesis band, causal chain, watchpoint proxy zones |
| `03c_content_evidence_matrix.svg` | content | `03c_content_evidence_matrix` | Evidence Matrix | Four exhibit proxy zones plus one INSIGHT zone |
| `03d_content_trend_multiples.svg` | content | `03d_content_trend_multiples` | Trend + Small Multiples | One trend, four diagnostic proxy zones, one INSIGHT zone |
| `03e_content_exhibit_split.svg` | content | `03e_content_exhibit_split` | Primary + Supporting Exhibit | One 65% primary exhibit, one 35% supporting exhibit, one INSIGHT zone |
| `04_ending.svg` | ending | `04_ending` | Ending | Dark-navy centered closing |

The composite zones intentionally use `object` proxy bindings because each contains several visible chart or text atoms. Their differing counts and bounds are the authored Layout contracts; they must not be collapsed into identical generic content Layouts.

# 합성 기본 모드 전체 경로 - Design Spec

Synthetic engineering fixture only. No actual user/company approval. Source: sources/facts.md from the unchanged public builtin-brief.json. UI, native app and production acceptance remain separate.

## I. Project Information
| Item | Value |
| --- | --- |
| Project Name | builtin_full_path |
| Canvas Format | PPT 16:9 (1280x720) |
| Page Count | 1 |
| Design Style | briefing + swiss-minimal |
| Target Audience | 합성 임원보고 검증 |
| Use Case | 기존 기본 SVG 생성 경로의 engineering test |
| Delivery Purpose | presentation |
| Content Strategy | 기존 합성 KPI만 사용; 파생 격차 명시 |
| Template Adherence | adaptive |
| Created Date | 2026-10-07 |

## II. Canvas Specification
| Property | Value |
| --- | --- |
| Format | PPT 16:9 |
| Dimensions | 1280x720 |
| viewBox | `0 0 1280 720` |
| Margins | left 76, right 76, top 56, bottom 50 |
| Content Area | 1128x500 |

## III. Visual Theme
Mode: briefing. Visual style: swiss-minimal. Existing Executive Boardroom palette. No gradients.
| Role | HEX | Purpose |
| --- | --- | --- |
| Background | `#F7F2E8` | Source template field |
| Primary | `#17352B` | Text and band |
| Accent | `#B38B3F` | Current series and rules |
| Secondary accent | `#315E52` | Target series |
| Body text | `#17352B` | Body |
| Secondary text | `#706A5F` | Captions |
| Surface | `#FFFDF8` | Inverse lead text |

## IV. Typography System
Typography direction: OFL Pretendard Regular/Bold. Requires Pretendard on receiving machines; no embedding or font installation. Shared rendering will register the bundled exact faces only.
| Role | Chinese | English | Fallback tail |
| --- | --- | --- | --- |
| Title | Pretendard | Pretendard | Malgun Gothic, Arial, sans-serif |
| Body | Pretendard | Pretendard | Malgun Gothic, Arial, sans-serif |
| Emphasis | Pretendard | Pretendard | Malgun Gothic, Arial, sans-serif |
| Code | Pretendard | Pretendard | Malgun Gothic, Arial, sans-serif |
Per-role font stacks:
- Title: `Pretendard, 'Malgun Gothic', Arial, sans-serif`
- Body: `Pretendard, 'Malgun Gothic', Arial, sans-serif`
- Emphasis: `Pretendard, 'Malgun Gothic', Arial, sans-serif`
- Code: `Pretendard, 'Malgun Gothic', Arial, sans-serif`
| Role | Size | Weight |
| --- | --- | --- |
| title | 64 | 700 |
| body | 40 | 400 |
| lead | 48 | 700 |
| annotation | 28 | 400 |
| footnote | 20 | 400 |

## V. Layout Principles
Inherited full 03_content scaffold: header, title slot, rule, message band, three factual columns, three short divider lines, footer/page-number. Reflow font sizes, keep every visible prototype element. Add a small editable comparison chart below the factual columns. Adaptive output adds reusable footer/page-number slots and framing; retains source Master identity. No images, no outside facts.
Spacing: outer inset 76, body band padding 30, columns gap 50. Single focal KPI comparison; no extra slides or filler.

## VI. Icon Usage Specification
No icons required; inventory empty. No generic company logos.

## VII. Visualization Reference List
Catalog read: 76 templates
| Page | Template | Path | Summary-quote | Usage |
| --- | --- | --- | --- | --- |
| P01 | grouped_bar_chart | `templates/charts/grouped_bar_chart.svg` | Pick for 2-4 series side-by-side across the same categories (e.g. YoY/QoQ). Skip if showing composition within each category (use stacked_bar_chart). | Two series current 84 and target 90 for one synthetic KPI; 0-100 percent axis. |
Runners-up considered:
- column_chart rejected for P01: catalog targets 3-8 categories; this fixture has two states of one KPI.

## VIII. Image Resource List
No image rows. No AI/web/private assets. Formula policy text-only: simple percentages remain editable.

## IX. Content Outline
### Part 1: 합성 KPI
#### Slide 01 - 합성 KPI 점검
- **Cover impact**: Data hook: current 84 versus target 90; complete boardroom scaffold with editable chart.
- **Layout**: `03_content` input; adaptive output `kpi-content-chart` adds footer/page-number slots and chart under inherited three factual columns.
- **Title**: 합성 KPI 점검
- **Core message**: 현재 84%, 목표 90%
- **Visualization**: grouped_bar_chart
- **Content**:
  - 합성자료
  - 격차 -6%p
- **Visual treatment**: Native chart

## X. Speaker Notes Requirements
None requested

---
deck_id: visual_story
kind: deck
display_name: "Visual Story"
version: "1.0"
status: ACTIVE
visibility: public
source_type: native
fidelity: native
native_structure_mode: structured
primary_category: brand_story
categories: ["brand_story", "presentation", "product"]
keywords: ["스토리", "비전", "브랜드", "메시지", "키노트", "발표", "storytelling"]
audience: ["고객", "직원", "대중", "경영진"]
purpose: ["비전 발표", "브랜드 스토리", "핵심 메시지", "제품 스토리"]
aliases: ["비주얼 스토리", "키노트", "visual story"]
document_types: ["brand_story", "keynote", "vision_deck"]
tone: ["visual", "minimal", "emotional"]
avoid_for: ["상세 KPI", "감사보고", "밀집 데이터"]
quality_score: 93
summary: "한 장 한 메시지, 큰 숫자와 강한 문장으로 전달하는 스토리텔링·비전 발표 템플릿입니다."
primary_color: "#D14D32"
canvas_format: ppt169
canvas_width: 1280
canvas_height: 720
page_count: 6
page_types: [cover, toc, content, data_chart, comparison, ending]
---

# Visual Story — Design Specification

## I. Template Overview
- **Use cases**: 비전 발표, 브랜드 스토리, 핵심 메시지, 제품 스토리.
- **Audience**: 고객, 직원, 대중, 경영진.
- **Tone**: visual, minimal, emotional.
- **Recommendation rule**: purpose/audience/keywords must match the request; this template is not globally preferred only because its quality score is high.
- **Negative fit**: 상세 KPI, 감사보고, 밀집 데이터.

This template is an original Slide Master design. It is informed by recurring professional presentation patterns—clear narrative, action titles, reusable business layouts, data storytelling, and strong hierarchy—without copying third-party template assets, logos, or proprietary slide files.

## II. Color System
| Role | HEX |
| --- | --- |
| Background | `#F7F7F5` |
| Primary text | `#171717` |
| Accent | `#D14D32` |
| Secondary accent | `#2F6B62` |
| Surface | `#FFFFFF` |
| Structural dark | `#171717` |

## III. Typography
Pretendard is the primary Korean/Latin family with Malgun Gothic fallback. Cover titles use 50–58px, content titles 32px, body 13–21px, and micro labels 10–13px. Keep message hierarchy stronger than decorative styling.

## IV. Page Roster
| File | Role |
| --- | --- |
| `01_cover.svg` | Cover / title |
| `02_toc.svg` | Agenda / section map |
| `03_content.svg` | Core message / structured content |
| `03_data_chart.svg` | KPI / data storytelling |
| `03_comparison.svg` | Current vs next / option comparison |
| `04_ending.svg` | Closing / next move |

## V. Production Rules
- Preserve 16:9 geometry and safe margins.
- Use one dominant message per slide.
- Keep real charts/tables editable when converting to PPTX where possible.
- Do not force this template when `avoid_for` matches the user's request.
- ACTIVE status requires picker discovery, six-preview rendering, recommendation audit, and MCP smoke validation.

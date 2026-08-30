---
deck_id: training_playbook
kind: deck
display_name: "Training Playbook"
version: "1.0"
status: ACTIVE
visibility: public
source_type: native
fidelity: native
native_structure_mode: structured
primary_category: education
categories: ["education", "presentation", "notice"]
keywords: ["교육", "매뉴얼", "가이드", "사용법", "워크숍", "프로세스", "training"]
audience: ["직원", "신입", "교육생", "현장인력"]
purpose: ["교육 자료", "사용법 안내", "업무 매뉴얼", "워크숍"]
aliases: ["교육 플레이북", "매뉴얼", "training playbook"]
document_types: ["training_deck", "manual", "how_to_guide"]
tone: ["friendly", "structured", "instructional"]
avoid_for: ["투자 IR", "재무 보고", "감사보고"]
quality_score: 93
summary: "교육·매뉴얼·사용법·워크숍에 적합한 단계형 학습 플레이북 템플릿입니다."
primary_color: "#F4B942"
canvas_format: ppt169
canvas_width: 1280
canvas_height: 720
page_count: 6
page_types: [cover, toc, content, data_chart, comparison, ending]
---

# Training Playbook — Design Specification

## I. Template Overview
- **Use cases**: 교육 자료, 사용법 안내, 업무 매뉴얼, 워크숍.
- **Audience**: 직원, 신입, 교육생, 현장인력.
- **Tone**: friendly, structured, instructional.
- **Recommendation rule**: purpose/audience/keywords must match the request; this template is not globally preferred only because its quality score is high.
- **Negative fit**: 투자 IR, 재무 보고, 감사보고.

This template is an original Slide Master design. It is informed by recurring professional presentation patterns—clear narrative, action titles, reusable business layouts, data storytelling, and strong hierarchy—without copying third-party template assets, logos, or proprietary slide files.

## II. Color System
| Role | HEX |
| --- | --- |
| Background | `#FFF9ED` |
| Primary text | `#243447` |
| Accent | `#F4B942` |
| Secondary accent | `#2D6A8A` |
| Surface | `#FFFFFF` |
| Structural dark | `#23445A` |

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

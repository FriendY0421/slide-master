---
deck_id: executive_boardroom
kind: deck
display_name: "Executive Boardroom"
version: "1.0"
status: ACTIVE
visibility: public
source_type: native
fidelity: native
native_structure_mode: structured
primary_category: report
categories: ["report", "presentation", "proposal"]
keywords: ["임원", "경영진", "이사회", "의사결정", "경영현안", "boardroom"]
audience: ["임원", "경영진", "이사회"]
purpose: ["임원 보고", "경영 현안", "의사결정", "중장기 전략"]
aliases: ["보드룸", "임원보고", "executive boardroom"]
document_types: ["executive_brief", "board_report", "decision_memo"]
tone: ["premium", "formal", "restrained"]
avoid_for: ["어린이", "캐주얼", "게임"]
quality_score: 95
summary: "임원회의·경영현안·의사결정 보고에 적합한 절제된 보드룸 스타일입니다."
primary_color: "#B38B3F"
canvas_format: ppt169
canvas_width: 1280
canvas_height: 720
page_count: 6
page_types: [cover, toc, content, data_chart, comparison, ending]
---

# Executive Boardroom — Design Specification

## I. Template Overview
- **Use cases**: 임원 보고, 경영 현안, 의사결정, 중장기 전략.
- **Audience**: 임원, 경영진, 이사회.
- **Tone**: premium, formal, restrained.
- **Recommendation rule**: purpose/audience/keywords must match the request; this template is not globally preferred only because its quality score is high.
- **Negative fit**: 어린이, 캐주얼, 게임.

This template is an original Slide Master design. It is informed by recurring professional presentation patterns—clear narrative, action titles, reusable business layouts, data storytelling, and strong hierarchy—without copying third-party template assets, logos, or proprietary slide files.

## II. Color System
| Role | HEX |
| --- | --- |
| Background | `#F7F2E8` |
| Primary text | `#17352B` |
| Accent | `#B38B3F` |
| Secondary accent | `#315E52` |
| Surface | `#FFFDF8` |
| Structural dark | `#17352B` |

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

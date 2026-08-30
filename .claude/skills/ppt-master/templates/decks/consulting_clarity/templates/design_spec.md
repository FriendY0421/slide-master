---
deck_id: consulting_clarity
kind: deck
display_name: "Consulting Clarity"
version: "1.0"
status: ACTIVE
visibility: public
source_type: native
fidelity: native
native_structure_mode: structured
primary_category: report
categories: ["report", "proposal", "data"]
keywords: ["컨설팅", "전략", "경영보고", "문제분석", "개선안", "executive", "consulting"]
audience: ["임원", "관리자", "의사결정자"]
purpose: ["전략 보고", "문제점 분석", "개선 제안", "경영진 브리핑"]
aliases: ["컨설팅 클린", "전략 보고서", "consulting clarity"]
document_types: ["strategy_report", "improvement_proposal", "executive_brief"]
tone: ["formal", "concise", "evidence-led"]
avoid_for: ["어린이", "축하", "웨딩"]
quality_score: 96
summary: "메시지 중심의 컨설팅·전략 보고용. 액션 타이틀, 근거, 비교와 로드맵을 빠르게 읽히게 구성합니다."
primary_color: "#1E4D8F"
canvas_format: ppt169
canvas_width: 1280
canvas_height: 720
page_count: 6
page_types: [cover, toc, content, data_chart, comparison, ending]
---

# Consulting Clarity — Design Specification

## I. Template Overview
- **Use cases**: 전략 보고, 문제점 분석, 개선 제안, 경영진 브리핑.
- **Audience**: 임원, 관리자, 의사결정자.
- **Tone**: formal, concise, evidence-led.
- **Recommendation rule**: purpose/audience/keywords must match the request; this template is not globally preferred only because its quality score is high.
- **Negative fit**: 어린이, 축하, 웨딩.

This template is an original Slide Master design. It is informed by recurring professional presentation patterns—clear narrative, action titles, reusable business layouts, data storytelling, and strong hierarchy—without copying third-party template assets, logos, or proprietary slide files.

## II. Color System
| Role | HEX |
| --- | --- |
| Background | `#FFFFFF` |
| Primary text | `#172033` |
| Accent | `#1E4D8F` |
| Secondary accent | `#22A6B3` |
| Surface | `#F4F6F8` |
| Structural dark | `#102A43` |

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

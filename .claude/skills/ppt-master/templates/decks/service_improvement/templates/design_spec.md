---
deck_id: service_improvement
kind: deck
display_name: "Service Improvement"
version: "1.0"
status: ACTIVE
visibility: public
source_type: native
fidelity: native
native_structure_mode: structured
primary_category: report
categories: ["report", "proposal", "data"]
keywords: ["VOC", "센터", "품질", "문제점", "원인", "개선", "재서비스", "고객불만"]
audience: ["센터장", "관리자", "기술리더", "임원"]
purpose: ["서비스 개선", "문제점 분석", "VOC 개선", "품질 개선", "센터 보고"]
aliases: ["서비스 개선", "문제점 개선", "service improvement"]
document_types: ["service_review", "root_cause_report", "improvement_plan"]
tone: ["practical", "evidence-led", "action-oriented"]
avoid_for: ["투자 피치", "웨딩", "예술 포트폴리오"]
quality_score: 97
summary: "서비스 품질·VOC·재서비스·센터 문제점과 개선대책을 진단→원인→실행으로 연결하는 실무형 템플릿입니다."
primary_color: "#1D70B7"
canvas_format: ppt169
canvas_width: 1280
canvas_height: 720
page_count: 6
page_types: [cover, toc, content, data_chart, comparison, ending]
---

# Service Improvement — Design Specification

## I. Template Overview
- **Use cases**: 서비스 개선, 문제점 분석, VOC 개선, 품질 개선, 센터 보고.
- **Audience**: 센터장, 관리자, 기술리더, 임원.
- **Tone**: practical, evidence-led, action-oriented.
- **Recommendation rule**: purpose/audience/keywords must match the request; this template is not globally preferred only because its quality score is high.
- **Negative fit**: 투자 피치, 웨딩, 예술 포트폴리오.

This template is an original Slide Master design. It is informed by recurring professional presentation patterns—clear narrative, action titles, reusable business layouts, data storytelling, and strong hierarchy—without copying third-party template assets, logos, or proprietary slide files.

## II. Color System
| Role | HEX |
| --- | --- |
| Background | `#FFFFFF` |
| Primary text | `#172B4D` |
| Accent | `#1D70B7` |
| Secondary accent | `#F59E0B` |
| Surface | `#F4F7FA` |
| Structural dark | `#12375B` |

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

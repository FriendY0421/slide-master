---
deck_id: modern_corporate_blue
kind: deck
display_name: "Modern Corporate Blue"
version: "1.0"
status: ACTIVE
visibility: public
source_type: native
fidelity: native
native_structure_mode: structured
primary_category: report
categories: ["report", "presentation", "notice", "proposal"]
keywords: ["회사", "기업", "업무보고", "회의", "현황", "소개", "corporate"]
audience: ["직원", "관리자", "고객", "임원"]
purpose: ["업무 보고", "현황 공유", "회사 소개", "회의 자료"]
aliases: ["코퍼레이트 블루", "회사 보고", "modern corporate"]
document_types: ["business_report", "company_profile", "meeting_deck"]
tone: ["clean", "professional", "balanced"]
avoid_for: ["아트 포트폴리오", "웨딩"]
quality_score: 95
summary: "범용 회사 보고·회의·소개 자료에 쓰기 쉬운 깔끔한 블루 코퍼레이트 템플릿입니다."
primary_color: "#146FE8"
canvas_format: ppt169
canvas_width: 1280
canvas_height: 720
page_count: 6
page_types: [cover, toc, content, data_chart, comparison, ending]
---

# Modern Corporate Blue — Design Specification

## I. Template Overview
- **Use cases**: 업무 보고, 현황 공유, 회사 소개, 회의 자료.
- **Audience**: 직원, 관리자, 고객, 임원.
- **Tone**: clean, professional, balanced.
- **Recommendation rule**: purpose/audience/keywords must match the request; this template is not globally preferred only because its quality score is high.
- **Negative fit**: 아트 포트폴리오, 웨딩.

This template is an original Slide Master design. It is informed by recurring professional presentation patterns—clear narrative, action titles, reusable business layouts, data storytelling, and strong hierarchy—without copying third-party template assets, logos, or proprietary slide files.

## II. Color System
| Role | HEX |
| --- | --- |
| Background | `#F6F9FC` |
| Primary text | `#172B4D` |
| Accent | `#146FE8` |
| Secondary accent | `#00A3BF` |
| Surface | `#FFFFFF` |
| Structural dark | `#0B3A73` |

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

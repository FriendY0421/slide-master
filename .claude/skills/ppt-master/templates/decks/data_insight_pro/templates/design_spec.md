---
deck_id: data_insight_pro
kind: deck
display_name: "Data Insight Pro"
version: "1.0"
status: ACTIVE
visibility: public
source_type: native
fidelity: native
native_structure_mode: structured
primary_category: data
categories: ["data", "report", "presentation"]
keywords: ["데이터", "KPI", "실적", "VOC", "추이", "통계", "분석", "dashboard"]
audience: ["관리자", "분석가", "임원"]
purpose: ["데이터 분석", "실적 보고", "KPI 리뷰", "VOC 분석"]
aliases: ["데이터 인사이트", "KPI 대시보드", "data insight"]
document_types: ["data_report", "kpi_review", "performance_report"]
tone: ["analytical", "modern", "data-heavy"]
avoid_for: ["사진앨범", "축하", "웨딩"]
quality_score: 96
summary: "KPI·실적·VOC·트렌드 분석을 위한 데이터 스토리텔링 중심의 다크 대시보드형 템플릿입니다."
primary_color: "#22D3EE"
canvas_format: ppt169
canvas_width: 1280
canvas_height: 720
page_count: 6
page_types: [cover, toc, content, data_chart, comparison, ending]
---

# Data Insight Pro — Design Specification

## I. Template Overview
- **Use cases**: 데이터 분석, 실적 보고, KPI 리뷰, VOC 분석.
- **Audience**: 관리자, 분석가, 임원.
- **Tone**: analytical, modern, data-heavy.
- **Recommendation rule**: purpose/audience/keywords must match the request; this template is not globally preferred only because its quality score is high.
- **Negative fit**: 사진앨범, 축하, 웨딩.

This template is an original Slide Master design. It is informed by recurring professional presentation patterns—clear narrative, action titles, reusable business layouts, data storytelling, and strong hierarchy—without copying third-party template assets, logos, or proprietary slide files.

## II. Color System
| Role | HEX |
| --- | --- |
| Background | `#0B1220` |
| Primary text | `#EAF2FF` |
| Accent | `#22D3EE` |
| Secondary accent | `#60A5FA` |
| Surface | `#111C2F` |
| Structural dark | `#07101F` |

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

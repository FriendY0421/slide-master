# Popular Professional Template Pack — 2026-08-30

## Purpose
This pack adds 10 original, reusable professional deck templates to Slide Master. The goal is not to copy third-party commercial templates, but to capture presentation patterns repeatedly recommended by consultants and professional PowerPoint users: clear storylines, reusable slide libraries, action-oriented titles, executive readability, data storytelling, and purpose-specific layouts.

## Research basis
External references used only as design-pattern research:
- SlideScience, “500+ Free and Downloadable Consulting Presentations (2026)” — emphasizes studying real consulting decks and reading action titles as the storyline: https://slidescience.co/consulting-presentations/
- SlideScience, “How To Write The Perfect Action Titles For Your Slides” — action titles state the takeaway rather than merely labeling a topic: https://slidescience.co/action-titles/
- Reddit r/powerpoint, “How to Create Professional Consulting-Style PowerPoint Slides?” — experienced consultants emphasize message/story and Pyramid-Principle-style clarity over decoration: https://www.reddit.com/r/powerpoint/comments/1qxhv2l/how_to_create_professional_consultingstyle/
- Reddit r/consulting, “Do you have a standard library of frequently used PowerPoint slides in Consulting?” — repeated support for reusable/editable slide libraries: https://www.reddit.com/r/consulting/comments/p7la3f/
- Reddit r/consulting, “Any good slide template sites?” — users distinguish professional reusable templates from cosmetic recolors: https://www.reddit.com/r/consulting/comments/1fpyzb0/any_good_slide_template_sites/

No third-party PPTX, logo, proprietary layout file, or copyrighted template asset was copied into this repository.

## Added templates
1. `consulting_clarity` — Consulting Clarity: strategy, executive reporting, problem analysis, improvement proposals.
2. `executive_boardroom` — Executive Boardroom: board/executive decisions, management issues, formal leadership briefings.
3. `data_insight_pro` — Data Insight Pro: KPI, VOC, performance, trends, analytical reporting.
4. `startup_pitch_bold` — Startup Pitch Bold: startup, new business, investment and product pitches.
5. `modern_corporate_blue` — Modern Corporate Blue: general corporate reporting, meetings, company profiles and status sharing.
6. `strategy_roadmap` — Strategy Roadmap: roadmaps, project plans, transformation and execution sequencing.
7. `service_improvement` — Service Improvement: service quality, VOC, center issues, root causes and corrective actions.
8. `training_playbook` — Training Playbook: training, manuals, how-to guides and workshops.
9. `visual_story` — Visual Story: brand stories, vision, keynote-style messages and visual narratives.
10. `future_tech` — Future Tech: AI, semiconductor, IT, future strategy and technical presentations.

## Common production contract
Every template contains six representative SVG prototypes:
- Cover
- Agenda / TOC
- Structured content
- Data / KPI
- Comparison
- Ending

Each template declares `native_structure_mode: structured`, a dedicated PowerPoint Master, reusable Layout identities, explicit placeholder boundaries, purpose/audience metadata, positive recommendation keywords, `quality_score`, and `avoid_for` negative-fit signals.

The three analytical variants (`03_content`, `03_data_chart`, `03_comparison`) intentionally reuse one PowerPoint `03_content` Layout contract while keeping different slide-local visual compositions. This avoids duplicate Layout definitions while preserving distinct usable examples.

## Recommendation behavior
Recommendation is contextual rather than globally preferring a new/high-quality template. Examples verified on 2026-08-30:
- `삼성전자서비스 미래에 대한 PPT` → `future_tech` is the only recommendation badge and ranks first.
- `삼성전자서비스 센터 문제점 및 개선방안 PPT` → `service_improvement` ranks first.
- `AI 반도체 미래 기술 전략 PPT` → `future_tech` ranks first.
- `직원 교육 매뉴얼 PPT` → `training_playbook` ranks first.
- `KPI 실적 데이터 분석 PPT` → `data_insight_pro` ranks first.
- `스타트업 투자 피치덱` → `startup_pitch_bold` ranks first.
## Validation record
Validation was performed locally on HOME-PC without GitHub Actions.

- Registration: 10/10 templates registered in `decks_index.json`.
- Catalog: 14 Deck templates total after addition; combined Picker catalog becomes 21 selectable Deck/Layout templates.
- SVG XML parse: 60/60 SVG files valid.
- `svg_quality_checker.py --template-mode`: all 10 templates pass 6/6; warnings 0; errors 0.
- Recommendation audit: 10/10 positive-fit and negative-fit audits pass; unrelated prompts do not receive inappropriate recommendation badges.
- Structured PPTX preview export: 10/10 templates pass, each 6 slides, 1 PowerPoint Master, 4 reusable Layouts, failed slides 0.
- Native DrawingML conversion: editable shapes enabled; no conversion failures.
- Microsoft PowerPoint COM render: all 10 generated preview decks export to PNG successfully; visual review of covers and KPI/data pages found no visible clipping or overlap.
- Picker payload local benchmark after expansion: approximately 472 ms for a six-card request, far below the server’s 30-second generation timeout.

## Maintenance rule
When modifying any template in this pack:
1. Re-register the template.
2. Run the template-mode SVG quality checker.
3. Run positive and negative recommendation audits.
4. Export the structured preview PPTX.
5. Render or visually inspect representative pages.
6. Verify the live Picker discovers it from GitHub `main`.

A template must not remain `ACTIVE` if any required validation fails.

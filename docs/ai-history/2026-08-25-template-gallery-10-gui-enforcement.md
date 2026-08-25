# Slide Master GUI Template Gallery 10-template enforcement — 2026-08-25

## Why this change was required
A ChatGPT PPT request incorrectly returned three text template choices instead of executing the registered HTML/GUI gallery. The repository already required a GUI picker, but the actual catalog contained only four registered templates and the central contract did not encode enough launcher behavior to prevent a conversational shortcut.

## Corrected execution path
`FAH → latest GitHub authority → Execution Contract → template_gallery_context.py → HTML/GUI gallery → user preview/selection → TEMPLATE_SELECTED evidence → new_deck_init.py → PPT generation`.

## Catalog result
- Registered selection-ready templates increased from 4 to 10.
- Existing: Apple Monochrome, JangPM Editorial, McKinsey Strategy, NAVER IR.
- Added: Executive Teal, Strategy Burgundy, Learning Coral, Data Cobalt, Premium Sand, Corporate Slate.
- Free Design remains an explicit user-only choice.
- Each registered card uses real SVG previews and may expose up to 6 representative layouts.

---
name: native-enhance-pptx
description: >
  Enhance a finished PPTX while keeping visible content and layout stable. Use
  for adding or replacing speaker notes, narration audio, auto-advance timing,
  or slide transitions through direct OOXML. Do not use for redesign, raw
  template filling, SVG-generated project narration, or changing slide content.
---

# Native PPTX Enhance

Use this standalone direct-PPTX route only after
[`../ppt-master/workflows/routing.md`](../ppt-master/workflows/routing.md)
selects native enhancement.

## Runtime Procedure

1. Read
   [`../ppt-master/workflows/native-enhance-pptx.md`](../ppt-master/workflows/native-enhance-pptx.md)
   in full.
2. Execute that workflow step by step, including its enhancement-plan
   confirmation, any separate voice/settings confirmation, apply, and read-back
   gates.
3. Keep slide count, order, visible wording, and layout stable unless the user
   changes the request and routing selects a different route.

Shared scripts do not imply main-pipeline inheritance. Do not load or execute
the main SVG `ppt-master` skill, Strategist/Executor references,
`finalize_svg.py`, `svg_to_pptx.py`, or `verify_deck.py` for this route unless
the native-enhancement workflow explicitly hands off to one of them.

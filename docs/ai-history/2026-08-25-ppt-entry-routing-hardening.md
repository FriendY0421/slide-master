# PPT entry routing hardening — 2026-08-25

## Reason

A ChatGPT PPT request was incorrectly routed through the upstream `byungjunjang/slide-master` repository and presentation generation began before the FriendY FAH/Slide Master template-selection gate was evaluated.

The existing FAH runtime @45 Execution Contract and Slide Master local fail-closed guards were healthy; the failure occurred earlier, at repository/project entry routing.

## Durable correction

For every new presentation request, including generic phrases such as `PPT 만들어줘`, `ppt로 만들어줘`, `프레젠테이션 만들어줘`, `슬라이드 만들어줘`, or a request to turn a URL/document/topic into a deck:

1. Bind the task to project `SLIDE_MASTER` and canonical repository `FriendY0421/slide-master` before any presentation research, SVG generation, project initialization, or PPTX export.
2. Do not use upstream `byungjunjang/slide-master` as the execution authority for FriendY presentation requests.
3. Evaluate the FAH Execution Contract first when available; otherwise read `.fah/execution-contract.json` directly as the durable fallback.
4. `CREATE_PRESENTATION` must pass the mandatory `TEMPLATE_SELECTION` user-interaction gate.
5. If there is no valid template-selection evidence, the only correct state is `WAIT_USER_ACTION`/blocked execution: launch the real HTML/GUI template gallery and wait for the user's explicit selection.
6. Only after a valid user selection may content research, project initialization, SVG authoring, or PPTX generation continue.
7. Existing local guards (`template_gate.py`, `new_deck_init.py`, guarded `svg_to_pptx.py`) remain the final fail-closed enforcement layer.
8. `BEAUTIFY_PRESENTATION` retains its documented exemption only for an existing PPTX beautification route.

## Safety decision

The `.fah/execution-contract.json` contract itself was not changed. It is already accepted by FAH runtime @45 and monitored as `CONTRACT_CURRENT`; changing it only to fix entry routing would unnecessarily create contract SHA drift.

## Expected user-visible flow

`PPT request → FriendY0421/slide-master lock → FAH contract evaluation → live template gallery → relevant template recommendations → user explicit selection → content analysis/research → deck generation → quality verification → PPTX handoff`

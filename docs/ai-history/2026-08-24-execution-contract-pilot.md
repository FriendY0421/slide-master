# Slide Master Execution Contract Pilot

Updated: 2026-08-24 22:08 KST

## Purpose

Make presentation workflow safety independent of model memory by adding a FAH-managed project execution contract while preserving Slide Master local fail-closed guards.

## Contract

- path: `.fah/execution-contract.json`
- contract version: `1.0`
- contract blob SHA: `d8c24c26460cded0fe947df75b2e278488fd7641`
- capability: `EXECUTION_CONTRACT`
- auto deploy: `N` unchanged

## Actions

- `CREATE_PRESENTATION` requires `TEMPLATE_SELECTION`.
- Missing user selection returns `WAIT_USER_ACTION` centrally.
- Invalid selection evidence returns `BLOCK`.
- Valid selection evidence permits `ALLOW`.
- `BEAUTIFY_PRESENTATION` is `EXEMPT` with `beautify-pptx` semantics.

## Local guard preserved

`template_gate.py`, `new_deck_init.py`, and guarded `svg_to_pptx.py` remain mandatory. Missing `template_selection.json` blocks generated-deck export even if a conversational or central check was skipped.

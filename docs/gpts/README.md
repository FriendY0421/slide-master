# PPT GPTS integration

This directory contains the GPTS-facing contract for Slide Master presentation creation.

## Canonical files

- `PPT_GPTS_CANONICAL_INSTRUCTIONS.md` — compact GPT Builder instruction source.
- `INTERACTIVE_PICKER_CONTRACT.md` — App Block / GenUI picker behavior and fallback rules.
- `ACCEPTANCE_TESTS.md` — required regression tests before changing the picker or template gate.
- `COMPANY_TEMPLATE_REGISTRATION.md` — company/user PPT/PDF/image/photo onboarding and security policy.
- `PRODUCTION_PRESETS.json` — reusable content-production presets shown after template choice.
- `TEMPLATE_METADATA_SCHEMA.json` — status/version/source/fidelity metadata contract.

## Runtime authority

The technical source of truth remains `FriendY0421/slide-master`.
`PPT_REQUEST_GUARD.md` is the first-read new-deck guard and `.fah/execution-contract.json` remains the FAH execution contract.

GPTS documentation must not hard-code the current template count or template ids. Runtime discovery comes from the live Deck/Layout indexes through `template_catalog.py`.

GitHub Actions are not required for this flow and remain default-off unless the user explicitly requests them.

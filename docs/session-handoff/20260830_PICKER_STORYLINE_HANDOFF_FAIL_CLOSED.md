# Picker handoff — Storyline Preview Fail-Closed

Updated: 2026-08-30 KST
Status: CURRENT ON FEATURE BRANCH

Branch: `feat/apps-sdk-template-picker-20260827`
Base before fix: `2efa7c6338137ed0c788e6abe803e3ca1a6bb167`

## Mandatory resume rule
Do not restore the old final Picker action that says to continue PPT production. Template+preset validation is not generation permission.

After final selection, the required host state is:
`WAIT_STORYLINE_PREVIEW`
with `GENERATION_ALLOWED=false`.

The next visible ChatGPT output must be a complete editable slide plan, not a PPTX. Each slide shows number, title, core message, key content, and visual/layout plan. User edits and explicit approval come before generation.

## Validation evidence
Temporary server on 3001 returned:
`WORKFLOW WAIT_STORYLINE_PREVIEW false true 34`
while tools, UI resource, CSP, and final selection validation all passed.
## Runtime safety
Do not kill the current user-approved foreground runtime merely to activate the server-side contract. TCP 3000 Picker and TCP 8080 Secure Tunnel remain running/minimized during use. The rebuilt app bundle is available to new resource loads; structured server changes activate on the next normal restart.

Do not redo CSP/template/port/startup-order/maxBuffer diagnosis unless fresh evidence points there.

## Next real acceptance
Run exactly one normal ChatGPT Picker request after the updated UI is loaded. Expected flow:
`template cards -> template choice -> preset choice -> final selection -> full editable slide-by-slide preview -> user revision/approval -> generation`.

Failure condition: any PPT/PPTX generation begins before the slide preview is visible and explicitly approved.

GitHub Actions remain unused. PR #6 stays Draft until host-side selection return and full workflow acceptance are proven.

Implementation commit: `fc62c951dc4b1300b5279552e416c5461efa5692`

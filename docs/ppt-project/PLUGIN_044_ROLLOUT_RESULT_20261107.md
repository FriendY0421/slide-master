# 0.4.4 rollout result — approved update blocked by package validation

Later status: the user separately approved mandatory declarations and limited
recovery; the [subsequent 0.4.4 update succeeded](PLUGIN_044_APPLIED_20261107.md).
The blocked attempts below are retained as historical evidence.

The user explicitly approved the prepared rollout, verification and conditional
recovery. **No 0.4.4 release was saved. The existing USER/PRIVATE plugin remains
0.4.3.** This report supersedes the pending-approval state in the
[preparation bundle](PLUGIN_044_ROLLOUT_APPROVAL_20261107.md).

## Actual execution, not a new preparation claim

1. Official metadata reconfirmed the same 0.4.3 current release before upload.
   Approved 24-file ZIP/hash matched the preparation receipt exactly.
2. Submitted that archive with the exact existing plugin ID and current-release
   guard. The API returned INVALID_ARGUMENT / HTTP 400:
   `apps.google-drive` must not set `required` to `false` or `optional` to `true`.
3. Re-read current metadata: version/release still 0.4.3. Prepared an official
   partial overlay containing only the 11 approved changed/new files; all uploaded
   file bytes matched the original approved archive. Existing App declarations
   were omitted to preserve them, not edited or removed. No semantic scope change.
4. The guarded partial-overlay request received the same validation rejection.
   This establishes that omitting the unchanged file does not avoid the effective
   package constraint. Do not repeat either rejected path without new evidence.
5. Read current source again. Inventory remains 22 files, same release/version,
   original `.app.json` with both `optional: true` declarations, and old manifests.
   No 0.4.4 helper/reference was saved. No installed-0.4.4 or cloud-0.4.4 test was
   run or claimed; executing another pre-release sample would not prove rollout.

Full approved archive SHA256:
`363c19284684710b2b079859b10c6a1f7c93a418d80d7d45e8618d785073dd0f`.
Approved-content partial overlay SHA256:
`34d0057fda8d5f1deed248b5a220c86d51215da7e2e6da3a7db75b847704c140`.
Both were rejected before a new saved release; originals/archives remain private.

This is an actual package-validation rejection, **not** a user authorization
denial, an automatic approval-review rejection, a font failure or a PPTX defect.
Local JSON/YAML/Python checks from preparation did not test this backend rule.
No new auth, permission, connection, install, fee, main merge or deployment occurred.

## Official references and remaining uncertainty

[Account plugin packaging](https://developers.openai.com/plugins/build/plugins)
describes App declarations, and the
[official error reference](https://developers.openai.com/plugins/deploy/submission-errors)
lists optional/required fields as boolean when provided. These pages do not
establish that the observed account-save API accepts optional dependencies.
The actual API rejection governs this target; do not infer that an earlier
successful release can be reuploaded unchanged today.

## Recovery impact discovered before mutation

There was no saved update to roll back, so the original 0.4.3 is already intact.
The prepared recovery ZIP remains a valid **content backup**, but it contains
the same optional App declaration and cannot now be promised to publish through
this API unchanged. Its earlier overlay-content validation was not a server
acceptance test. Never claim that exact restoration is guaranteed under this rule.

## Concrete alternatives and approval boundary

| Alternative | Effect, cost and recovery |
| --- | --- |
| Keep live 0.4.3 (recommended while connection policy is unresolved) | No mutation or new cost; PR quality improvements/source and candidate remain available. Resume only after an official optional-preserving update path is established. |
| Explicitly require both existing Drive and Picker mappings in 0.4.4 | Same App IDs and no new OAuth scopes are proposed, but selection becomes a required dependency declaration. Missing/unavailable apps may block use or require connection; host enforcement and PC-free Picker behavior are not verified. Requires separate explicit approval because the approved bundle promised unchanged optional declarations. |
| Remove App mappings/create a replacement/local-cache patch | Not an equivalent preservation fix; not proposed or attempted. Do not silently drop existing integration or create a substitute plugin. |

For review only, prepared a private alternative candidate that changes only
`.app.json` relative to the approved archive: remove `optional: true` and set
`required: true` for the two existing entries. No App IDs or other content changes.
It has **not been submitted**, so successful API acceptance is not claimed.

Alternative candidate SHA256:
`c66ada82ecf24d53f4d78b18ce5274d47ae2e1d17389b17ec3e57b1fdddb57c5`.

The corresponding alternative recovery restores 0.4.3 **code/instructions** as
0.4.5 and removes the two new files, but keeps both required declarations.
It therefore cannot restore the original optional-connection behavior. This is
the material recovery limitation to approve before any dependency migration.
No new installation/auth/payment is included; if prompted, stop and report the
exact scope rather than accept it. Do not use the earlier rollout approval as
permission for this dependency-policy change.

The minimum user decision is whether to retain 0.4.3 while resolving platform
support, or explicitly accept both required mappings **and** the limited rollback.
There is no need to send credentials, install another plugin or pay for a server.
The planned PDF has not been received; no PDF rule is applied or published.

[Sanitized actual rollout receipt](evidence/plugin-044-rollout-20261107.json).
Existing sample/code validation remains separate in
[the quality roadmap](QUALITY_ROADMAP_20261107.md).

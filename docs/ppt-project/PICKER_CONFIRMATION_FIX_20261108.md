# Original Picker confirmation safety: actual local runtime fix

## Problem and resulting behavior

The original Picker frontend treated any resolved validation response as
`server_validated`, including MCP `isError`, invalid/missing structured content
and a token for a different selection. It also converted all thrown errors into
payload-backed confirmation. That allowed a rejected selection to update model
context and send a final-selection message.

The existing confirmation function now requires valid=true, matching template,
preset and token, and the WAIT_STORYLINE_PREVIEW/generation_allowed=false
contract. It checks that the selected entries and payload remain current before
and after awaiting validation. Rejection, malformed response, stale selection or
an unclassified exception shows a retry notice and sends neither model context
nor confirmation message. Recognized temporary transport failures (502/503/504,
network/reset/timeout) retain the original payload-backed fallback and its
`local_payload` label. Valid choices still lead to storyline review, not PPTX
generation. Existing host-message failure/manual-copy behavior is preserved.

## Actual owning source and application

This is the **original existing Picker runtime**, not a new App or a disconnected
replacement added to PR #14. Owning base is [PR #6](https://github.com/FriendY0421/slide-master/pull/6),
commit `142346b10d375c4c9bfd0a2b92a3fb49c1756529`:

- Local checkout: `C:\Users\User\Tools\slide-master-picker-runtime`.
- Changed source: `apps/slide-master-picker/web/src/app.js`.
- Rebuilt existing `web/dist/app.js` using already installed esbuild/SDK.
- Preserved the pre-existing `src/server.js` modification byte-for-byte.
- Existing App/plugin identity, required connections, tunnel profile/keys, normal
  ports, dependency versions and installed main plugin 0.4.5 are unchanged.

PR #14 does not own a duplicate full Picker checkout. The exact
[runtime patch](evidence/picker-confirmation-20261108/picker-confirmation.patch)
is stored here with evidence and its PR #6 base. `git apply --check` passed
against the actual runtime before application. No PR was merged, no runtime Git
branch committed/pushed, and no new plugin release or App replacement occurred.

Source SHA256 after application:
`5de3a6fbd4ce752cdeb86852df143345050526ce1ce64af1861d0a6f01a16f69`.
Bundle SHA256:
`91b0b4d2b6513455d75f172ab5fdb088e5d2dd410e621f7aac4ae4f6d53f9425`.

## Evidence and scope

| Check | Actual result |
| --- | --- |
| Original confirmation-function execution in an isolated VM context | [Before](evidence/picker-confirmation-20261108/baseline.json): 13 incorrect outcomes across 16 cases. Uses the actual original function with a mocked host bridge, not actual user selection. |
| Same isolated cases after runtime application | [After](evidence/picker-confirmation-20261108/applied.json): all 16 pass, including valid selection, 502/503 fallback, explicit server rejection, wrong IDs/token, permissive/missing workflow contract, undefined result, stale payload and removed entries. No rejected case updates context or sends a message. |
| Syntax and bundle | Node syntax checks and existing esbuild compile pass without installation. |
| Existing real MCP server on temporary loopback port 39045 | [Protocol receipt](evidence/picker-confirmation-20261108/protocol.json): actual valid response and actual invalid-template isError; served resource contains the changed code, 604,878 bytes. |
| Protocol catalog scope | Explicitly process-local `PICKER_SOURCE=local`, 11 entries in the older PR #6 checkout, used only for bounded protocol/resource inspection. Does **not** verify current live 21-entry catalog. Normal server default remains GitHub. |
| Cleanup | Owned temporary server stopped; no port 39045 listener remains. Normal server/tunnel were not started or reconfigured. |
| Actual intended host iframe/card/detail/preset callback | **Not run in this change**. Mocked bridge results and a served resource are not host acceptance. |

Private probes and full pre-change source/bundle remain in the project sibling
`review/picker-confirmation-20261108/`. No company input, Samsung font, credentials
or private Drive URL was used or published. The change adds no fee, permission,
authentication, dependency, hosted service or persistent process.

## Stop and recovery

The modified local runtime will provide the new bundle on its next normal
startup. This does not make the Picker always-on or PC-independent. Already
rendered host frames may retain their earlier resource until reopened.

If a regression appears, stop only this Picker's owned process and restore
`app.before.js` to its `web/src/app.js` and `bundle.before.js` to
`web/dist/app.js` from the private directory above. Do not reset the runtime Git
checkout or overwrite the pre-existing server modification. Check hashes and
reopen the original Picker resource before claiming recovery.

Original source SHA256:
`0f8d9c8184d118d38c34b142c95524e4740df8b542061fe7df2c7ec46dfaf176`.
Original bundle SHA256:
`b0efc47a050681484f5aa8fee804811529ffc0ec6641037c837c3e74ebdd6e8b`.
No live rollback was necessary. Main plugin recovery archives remain unchanged.

## Related Aro handoff evidence

Aro reported a separate **HOME-PC** download/inspection/render, not Dot VM or
PC-off execution, in [the existing PR comment](https://github.com/FriendY0421/slide-master/pull/14#issuecomment-6709155985).
This task independently read its saved quality report (errors empty) and hashed
the saved PPTX: `5b3715bf4f9236948ebb3ee9d4f5ae1de833910bfca56c45f715a8de8a3b8510`.
That corroborates local handoff of the synthetic fixture; it does not close
actual new input, host selection, recipient opening, Samsung or company-source
acceptance. It is not counted as another project's delivery or a new render here.

Remaining full-flow and cloud requirements stay in
[the active scope](ACTIVE_GOAL_SCOPE_20261107.md) and
[host assessment](DOTS_PICKER_HOST_ASSESSMENT.md). This safety fix is concrete
progress, not overall completion.

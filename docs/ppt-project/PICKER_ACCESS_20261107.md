# Picker access and PC dependency — 2026-11-07

Later main-plugin quality update: [0.4.5](PLUGIN_045_APPLIED_20261107.md). It does
not change the separate Picker or move its loopback upstream. A subsequent
browser observation was stopped by Computer Use because the current URL could
not be verified confidently. No browser inputs, authentication or safety bypass
followed. Actual gallery selection remains unverified; do not repeat that path
without an external state/capability change. This is a UI-verification limit,
not evidence that the Picker's payload or endpoint is defective.

## Exact target and existing runtime

Main Slide Master remains the already verified private 0.4.4 plugin. The
separate existing private Template Picker App remains 1.0.0; neither was
replaced. Read current official package metadata, the existing local launcher,
runtime helpers and the original operating/selection contract at PR #6 head
`142346b10d375c4c9bfd0a2b92a3fb49c1756529` rather than its stale root pointer.

The actual failing host route's identifier matches the existing Windows tunnel
profile, whose upstream is loopback port 3000. The current desktop hostname
matches the connected HOME-PC device. This independently connects the runtime
configuration to the observed tool route; the management API still does not
expose a complete saved transport/target readback. Tunnel identifiers, keys,
device IDs and raw configuration remain private.

## Observed sequence

| Stage | Actual result | Meaning |
| --- | --- | --- |
| Initial local runtime | No listeners on ports 3000/8080; tunnel process absent. | Existing runtime was stopped. |
| Initial actual desktop and existing cloud calls | Each returned MCP SSE probe 429; no repeated unchanged attempt. | Transport unavailable then; 429's control-plane root cause remains undiagnosed. |
| Temporary existing runtime | Ran existing Node server directly with its existing source setting, then existing tunnel executable/profile. MCP_READY passes; `/readyz` returns 200. | No npm install/build, file/config/key change or new tunnel/service. |
| Actual host call after readiness | Success: ACTIVE 21 templates, six recommendations, five presets, GitHub/main catalog. | Real tool access and current catalog payload confirmed. |
| Existing local protocol smoke | UI resource served (592685 bytes), module present; validation returns WAIT_STORYLINE_PREVIEW and generation_allowed=false. | Protocol/payload validation only; test choice is not actual user selection or approval. |
| Existing cloud chat, one post-readiness call | Same catalog response succeeds. | Cloud tool access works while the existing PC runtime is running. |
| Host-visible UI | `host_ui_rendered=null`, `pending_app_signal`; desktop accessibility inspection found no displayed Picker controls. CUA bootstrap failed; no blind clicks. | Actual preview/card/detail/preset interaction and host selection-message return remain NOT_RUN. |
| Cleanup | Stopped only the server/tunnel sessions started for this trial; ports 3000/8080 have no listeners again. | Restored the originally stopped runtime state. No PC shutdown performed. |

Cloud record: [post-ready actual trial](https://github.com/FriendY0421/slide-master/pull/14#issuecomment-6707879217).
The new ready state justified one follow-up invocation after the initial error;
it does not prove that starting the server explains every 429.

## PC-off boundary and minimum remaining action

**The configured Picker is PC-dependent.** Its matching tunnel targets the PC's
loopback server. Calling the tool from cloud does not move that upstream into
cloud. No physical power-off trial was performed, and no PC-off success is
claimed. Reopened cloud PPTX rendering/private Drive transport previously
verified in [0.4.4 results](PLUGIN_044_APPLIED_20261107.md) are separate capabilities;
they do not prove the mandatory Picker's availability with the PC off.

For current operation use the existing desktop launcher and keep the PC/server/
tunnel running, then open the Picker in the intended ChatGPT host. The remaining
human-visible test is: observe real previews, inspect a candidate's detail,
choose template and production preset, confirm and verify the returned pair
enters WAIT_STORYLINE_PREVIEW. Do not fake this evidence or allow generation
before the actual storyline/content approval.

A PC-independent Picker requires an approved persistent upstream and an official
mapping to the **same** App, with UI/file/access boundaries, cost and rollback
specified first. No cloud host, new credentials, permissions, expense, background
service, plugin replacement or source deployment was authorized/performed here.
Do not enable a different similarly named App as a substitute.

To resume use the existing launcher; to stop the foreground runtime use its
normal console termination. No persistent configuration was modified, so no
configuration rollback is required. Existing plugin/source recovery artifacts
remain unchanged.

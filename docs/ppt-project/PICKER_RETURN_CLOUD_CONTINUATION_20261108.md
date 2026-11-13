# Picker return repair and actual Cloud Work 0.4.6 verification

**Later actual result:** matching original-App model-context and selection
message arrived in the intended chat after the prior assistant final. See
[PICKER_AUTOMATIC_RETURN_ACCEPTANCE_20261108.md](PICKER_AUTOMATIC_RETURN_ACCEPTANCE_20261108.md).
The intermediate missing-receipt observation below is historical and superseded.


This continues existing PR #14 with the same original Picker and main plugin.
No company input, font, private download URL or credential is included here.
The user explicitly approved messaging the existing cloud trial for this check.

## Original Picker: concrete bounded repair

The actual source awaited `updateModelContext` inside the same try block as
`sendMessage`. If supplementary context rejected/timed out, the validated
selection message was never attempted. It also rechecked selection freshness
before, but not after, the context RPC; rapid confirmation could send twice.
These are reproduced code defects, **not an established explanation of the
user's previous missing host message**.

The original runtime now:

- Keeps existing server validation, matching token/workflow checks and known
  transient transport fallback. No rejected selection is permitted to send.
- Gives supplementary context a 4-second SDK request timeout; a context failure
  still permits the one self-contained selection message. That message includes
  the complete validated pair and explicit no-generation/storyline-review gate.
- Checks freshness again after the context await; guards in-flight duplicate
  confirmation; sends once with a 15-second SDK timeout. No ambiguous send is
  automatically retried through another bridge.
- Reports request acknowledgement separately from observed transcript receipt;
  preserves manual copy if automatic delivery is unavailable. Company-specific
  font/size/layout instructions now take precedence over default new-deck style
  language in the handoff message.

The actual existing runtime source and rebuilt bundle were applied. No plugin
identity/version, server source, tunnel profile/key, connection, port, installed
main package, dependency or persistent service was changed. Full pre-change
source/bundle/server copies are preserved privately. The exact
[patch and receipts](evidence/picker-return-20261108/receipt.json) are public-safe.
The patch layers on the prior confirmation-safety and Korean-UI patches. It is
a zero-context patch; use `git apply --unidiff-zero --check` against the exact
backed-up runtime before any application.

Eight new actual-function isolated cases with a **mocked host bridge** pass,
including failed context, stale selection during context, double click, message
rejection and ambiguous timeout. Before the fix four behavior cases fail;
the normal case additionally lacks the newly required explicit request timeout.
All 16 existing validation-safety cases still pass. These are not real host
message receipts. Source syntax and existing esbuild compile pass.

Actual existing server resource readback includes the new code and unchanged
Korean/copy behavior. Initial literal timeout inspection failed on esbuild
whitespace; corrected whitespace-aware inspection passes without code mutation.
Actual original connected tool returns the live GitHub/main 21-entry catalog.
The original Picker was reopened for a real user click, **without manufacturing
a choice or generating a PPTX**. The user then explicitly reported pressing
confirmation. The current chat and existing trial-parent recent-turn readback
contain no automatic selected pair. Thus click observation is real, automatic
return is **not passed**. The user then supplied the final screen: both context and message show request
acceptance, yet no automatic pair arrived. See the
[minimal host-delivery reproduction](PICKER_HOST_DELIVERY_REPRO_20261108.md). The
quoted diagnostic pair is manual, test-only and not production approval. No
repeat selection is requested. Exact owned foreground sessions were stopped
after the click test; ports3000/8080 have no remaining listeners.

Recovery: stop this test's owned processes; restore only `app.before.js` and
`bundle.before.js` from the private picker-return job to the original runtime
source/bundle. Preserve `src/server.js` and the earlier safety/Korean fixes.
Reopen to avoid cached UI. No main-plugin rollback is needed.

## Cloud Work: new target-side actual evidence

The previously approved existing Cloud Work trial ran actual installed 0.4.6.
Its command/output and private-delivery evidence is recorded in
[the trial's PR comment](https://github.com/FriendY0421/slide-master/pull/14#issuecomment-6715471949).
This local task also read the completed trial's actual command summaries,
exit codes, image-review events and Drive upload/readback/raw-hash events.

| Check | Actual result and boundary |
| --- | --- |
| Executor | Cloud Work, Linux 6.18.57 x86_64. No proof it is Aro/Dot. |
| Version | Installed cache manifest 0.4.6 and loaded 0.4.6 guidance separately read; installed scripts actually executed. |
| Write/read/delete | Existing task workspace and /tmp: each exclusive-create unique 1KB probe, reread/hash, delete only own file; errno0. No mount/permission change. |
| Installed dense checker | Existing nonsensitive fixture: exit0, errors0, 44 regions, 14 line-spacing warnings; reference comparison partial/one unverified object retained. |
| Missing-workbook negative | Exit1, one preservation error, measured regions0; not rendered or delivered. |
| Exact file reimport/render | Both slides rendered and visually inspected by the cloud model; OS exit0, text_font_verified=false. |
| Private Office delivery | Existing Drive, owner-only metadata readback, actual 40,449-byte raw download SHA equals unchanged synthetic fixture. |

No PC tools, Picker call, new install/permission/auth/fee/host/server/tunnel or
deployment was used in that cloud trial. It validates a PC-tool-independent
inspection/render/private-delivery path for the existing synthetic fixture;
it is not fresh-photo creation, recipient opening, actual PowerPoint, or proof
that Aro's separate reported read-only paths are now writable. Do not restart
identical checks instead of addressing those remaining conditions.

## Remaining full mission and FAH follow-on

The latest user direction is to finish the whole Slide Master mission, then
add its capabilities to FAH for PPT delivery. This supersedes indefinite FAH
deferral **as a future sequence**, not as an immediate deployment/merge approval.
Use the [standing full scope](ACTIVE_GOAL_SCOPE_20261107.md). The user's runtime
Goal was cleared; repository scope remains valid without claiming a Goal active.

The bounded real Picker automatic receipt is now evidenced. Remaining evidence:
recipient opening of the delivered actual photo PPTX; actual Aro writable
path/errno where that environment is used; Samsung rights only for subsequent
Samsung-specific acceptance. Existing local photo production is not undone.

After Slide Master acceptance, inspect the actual FAH owner/version/dispatcher
and existing file/auth/delivery contracts read-only. Prepare a reversible adapter
that reuses analysis/current-plan approval/native production/private delivery.
Do not copy secrets/fonts/company material, replace the plugin or invent user
ownership. Present exact target/change/impact/cost/recovery before any additional
permission, installation, hosting or operational rollout. No FAH code/service
was changed in this continuation.

# Slide Master 0.4.18 mobile photo reconstruction trial

The trial uses a [synthetic reference PNG](evidence/synthetic-mobile-photo-layers-0418.png)
drawn for this test. It contains a fictional tool illustration in a visible
rectangular crop and a diagonal caption on an abstract background.
Reference SHA-256:
`e8f08c66387f3d3411c017cb9bf01f5727b3335c30e2d7c3d5f594399a927584`.

## Phone trial

1. Save the PNG to the phone. With the PC off, invoke the existing private
   Slide Master in mobile ChatGPT and attach the PNG. Request a single editable
   16:9 slide through the existing photo reconstruction workflow. Ask for a
   layout proposal first and approve the current proposal in the phone chat.
   If the PC-hosted Picker is unavailable, use the documented mobile fallback
   and keep any required selections and plan approval.
2. Confirm the mobile host exposes the 0.4.18 skill or executable package.
   Report the observed version and the source of the helper. If the installed
   helper is unavailable and repository source is used for diagnostics, record
   that as source execution. Record whether the cloud can write files, render
   the actual exported deck and attach it privately in the same chat.
3. Preserve the visible English words and numbers. Trace the tool silhouette
   to remove the beige rectangle and keep the tool as a separate picture.
   Keep the diagonal blue shape, its caption and the TIP label editable.
   On the synthetic 960 by 540 reference, the diagonal runs from about
   (405,335) to (825,488). The existing helper can mask the left crop to the
   edge of the caption. Place the right crop separately. Compare the exported
   render against the attached PNG and verify the actual PPTX object types.
4. Download the private PPTX from that chat and open it in PowerPoint on the
   phone. Record the observed PC power state during generation and download,
   whether the file opened, and the first failing step if applicable. Keep
   chat links, file bytes and account details out of GitHub.

## Evidence as of November 14

The synthetic input is ready. The historical Cloud Work task could not be
queried through its durable host. The saved Codex Cloud environment reported
ready, which establishes configuration availability only. It does not establish
access to the existing private mobile ChatGPT plugin or phone download.
The local 0.4.18 installation and guidebook test remain verified separately.
The PC-off mobile invocation, actual cloud export/render, private mobile
download and phone open are pending a physical-phone trial.

## Regular ChatGPT Chat trial readback

The trial conversation recorded one image attachment, the one-slide proposal,
and the user's approval of that proposal. The Chat reply reported HTTP 429
during the Picker preview. After approval, the reply reported no available
execution route for verifying the loaded 0.4.18 version and producing and
attaching the PPTX. Chat history confirms the reported failure and approval.
It does not expose the raw Picker response or establish the reason for the
429. There was no PPTX attachment in the trial history. Cloud production,
rendering, private download and phone opening therefore remain unverified.
The PC power state is not independently established by the chat readback.

Reuse the approved one-slide specification when an execution route becomes
available in the same Chat. Confirm the loaded plugin version separately
from Picker availability. Then require a rendered PPTX attached to the Chat
and a recipient download and open result before closing the mobile trial.

## Mobile Work trial readback

The Work conversation recorded a synthetic image attachment, a one-slide
proposal, and the user's explicit approval. The first Work reply reported
reading the 0.4.18 package instructions directly. This is evidence reported
by the Work conversation, which does not expose a separate executable
package or runtime receipt. After approval, the reply reported two attempts
to reach the cloud execution environment, both unavailable. This trial
reached plan approval with reported instruction loading and stopped before
PPTX authoring. No output PPTX was attached. Cloud authoring and rendering,
private delivery and the phone download and open remain unverified. The
history does not independently confirm the PC power state.

When the Work execution environment becomes available, continue from the
already approved proposal in that conversation. Capture actual generation
and render results before asking for the recipient's phone download and
open result. A ready saved Codex Cloud configuration does not establish
execution or delivery in this mobile Work conversation.

## Same Work conversation execution preflight

One follow-up in the same Work conversation used the existing approval and
attachment. It requested a read-only cloud startup probe before the PC-off
production trial. The Work reply reported that the previous two attempts
returned `No usable execution environment is available` before command
startup. The new probe returned an execution session and `pwd` completed
in the cloud workspace with exit code 0. The Work reply also reported that
a private file delivery tool was available. The conversation readback
exposes these results as reported by Work, without the underlying tool
trace. The error does not establish why the earlier executor was
unavailable. The public OpenAI status check listed ChatGPT Work as
operational at the time of the follow-up.

The next production turn should start from the phone after the user turns
off the PC. Reuse the existing image and approved one-slide plan. The probe
did not create a PPTX or test the attachment tool. Production, rendered
review, delivery, and opening the downloaded file on the phone are still
pending. No new environment, permission or paid resource was used.

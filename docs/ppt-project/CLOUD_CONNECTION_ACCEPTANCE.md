# Official cloud connection acceptance

This records the missing connections after #14, reusing #6 and #10–#13.
Documentation is not a deployed service or an authorization grant.

## Official interfaces found

- [Plugin file APIs](https://developers.openai.com/plugins/reference): file inputs
  declare `_meta["openai/fileParams"]`. The file schema declares `download_url`,
  `file_id`, optional `mime_type` and `file_name`, with only the first two
  required. Feature-detect optional widget upload/select/download helpers in
  the actual host. Use private output file references, not public buckets or
  machine-local paths represented as cloud downloads.
- [Authentication](https://developers.openai.com/plugins/build/auth): use the
  supported authorization flow and server-side token validation. Bind the
  verified actor, source bytes/hash and job. Client-supplied actor IDs and local
  session flags are not platform identity or file ownership evidence.
- [MCP server](https://developers.openai.com/plugins/build/mcp-server): tools run
  on infrastructure the operator provides. A HOME-PC endpoint remains dependent
  on that PC; a cloud endpoint still needs authentication, licensed fonts,
  model invocation and private delivery.
- [Sign in with ChatGPT](https://developers.openai.com/cookbook/articles/sign-in-with-chatgpt)
  and [inference](https://developers.openai.com/siwc/token-sharing-open-source/models-and-inference):
  eligible applications may request separate identity and plan-usage permissions.
  Identity does not grant model use; neither permission grants access to existing
  ChatGPT conversations. This is a separately approved alternative, not a
  discovered endpoint for the current conversation's model. Eligibility,
  permission and hosting costs remain unverified; no registration was attempted.

## Reuse and evidence

| Existing component | Missing actual binding | Required evidence |
|---|---|---|
| Picker | Registered preview and confirmation return | Visible UI and current selection |
| CUSTOM intake | Supported file input | Verified actor and privately retrieved bytes |
| Photo plan | Host dispatcher or separately approved inference | Real pixels/model receipt; unknown values preserved |
| Request state | Current user confirmation | Request/revision/source/plan binding |
| Native build/finalizer | Approved cloud executor and fonts | Native readback and all-page reimport render |
| Delivery | Private output file reference | Correct user receives and opens exact PPTX |

Do not replace these seams with fabricated local authentication flags. The
installed instruction-only plugin does not expose the production tools. The
available picker accepts purpose/recommendation input, not photo-analysis or
file-delivery input. Discovery did not resolve its managed GPT-derived package
to an editable backend ID; identify the owning release path instead of editing
a different plugin or a managed cache.

## Approval and minimum input

First identify the existing plugin editor/release identity and approved cloud
executor/endpoint. Then present one approval bundle with exact revisions,
changed tools, authorization/model scopes, private retention, eligible account,
hosting/inference costs and limits, font license/embedding policy, affected
users and rollback. Never request blanket approval for unknown costs/scopes.

The user supplied the previous picker handoff instead of an unverified editor
link. Compare that record with the existing owner-visible management screen;
do not ask for the same unavailable link again. The existing picker identity
and developer were matched. Its development connection currently reports no
authentication. The screen does not expose the saved transport target or prove
workspace membership. This picker is distinct from the instruction-only main
plugin. Neither PRIVATE visibility nor a matching running tunnel proves the
registered transport or actor/file ownership. Do not create a replacement.

Font permission remains the minimum external policy input. Obtain separate
answers for server installation, server rendering and output embedding.
Until those are documented, do not upload the font to a new cloud environment,
redistribute it or embed it. A permitted alternate-font structural probe must
be labelled temporary and cannot certify SamsungOneKorean wrapping.

After binding the official host path, use a nonsensitive real attachment
to exercise upload → analysis → plan → user confirmation → production → review
→ private download, then have the user open that editable file. Company
references remain task-specific uploads. No new sign-in, API key, deployment,
font embedding, paid resource or cloud access was activated here.

## PC-independent execution candidate

[Cloud Work](https://learn.chatgpt.com/docs/enterprise/chatgpt-work-overview)
can run supported steps on OpenAI-managed infrastructure. It does not inherit
the local files, applications or browser session and cannot switch a running
local turn into cloud execution. Account/workspace availability and the
existing plugin's cloud tools must be inspected before calling this a usable
production path. This is an alternative to a separately operated server, not
evidence that the current picker is cloud-hosted.

[Local computer access](https://learn.chatgpt.com/docs/enterprise/cloud-local-access)
still requires the computer online for local steps. A PC-hosted picker tunnel
and Windows PowerPoint therefore remain PC-dependent. Do not enable local
access, change the transport, register an inference client or incur hosting
costs merely to discover availability. Preserve the recorded loopback-only
change and existing uncommitted work in the operating checkout.

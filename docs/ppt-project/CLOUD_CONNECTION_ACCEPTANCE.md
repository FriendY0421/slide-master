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

The smallest user input currently needed is the existing plugin's owning
editor/release link and evidence for the selected font's intended private cloud
use. After binding the official host path, use a nonsensitive real attachment
to exercise upload → analysis → plan → user confirmation → production → review
→ private download, then have the user open that editable file. Company
references remain task-specific uploads. No new sign-in, API key, deployment,
font embedding, paid resource or cloud access was activated here.

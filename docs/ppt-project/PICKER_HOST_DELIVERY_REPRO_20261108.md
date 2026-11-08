# Original Picker: acknowledged UI requests without intended-chat receipt

## Observed actual user test

The user operated the original registered Picker, then reported pressing
confirmation. The assistant did not select for the user. The user subsequently
provided the exact final screen text as a diagnostic response:

- Selection: `deck:modern_corporate_blue | preset:data_insight`.
- Screen: selection delivery request completed.
- Message status: host request accepted.
- Context status: request accepted.
- Screen explicitly says actual chat receipt must be checked separately.

No automatic pair appears in the intended local Codex chat's actual recent-turn
readback or in the inspected existing cloud-trial parent chat's recent turns.
The pair above was obtained **manually in a diagnostic reply**, not an automatic
callback, a fresh production approval or a replacement for the earlier photo
proposal's approval. Do not generate a new deck from this test selection.

This confirms the corrected resource was shown (new context-status wording),
and narrows the remaining seam beyond validation/UI confirmation. It does not
prove which platform component lost/routed/delayed the message or rule out an
uninspected destination. No host-level routing logs or delivery-receipt query
are exposed in the tools available to this task. Do not claim an established
OpenAI defect or solve it with invented transcript messages/actor IDs.

## Minimal non-sensitive reproduction for a platform investigation

1. In the intended host conversation, invoke the original Picker tool.
2. In its real frame choose a registered template and preset, then confirm once.
3. Check the resulting screen status separately from the actual conversation
   transcript/model input; do not paste the token until the distinction is made.

Relevant actual-source sequence, after fail-closed server validation:

```javascript
try {
  await app.updateModelContext(
    { content: [{ type: "text", text: contextText }] },
    { timeout: 4000 },
  );
} catch (_) {
  contextStatus = "unavailable";
}
if (!selectionIsCurrent()) return blockSelection();
const result = await app.sendMessage(
  { role: "user", content: [{ type: "text", text: message }] },
  { timeout: 15000 },
);
if (result?.isError) throw new Error("host rejected selection message");
```

Actual installed `@modelcontextprotocol/ext-apps` 1.7.5 implementation delegates
these calls to `ui/update-model-context` and `ui/message` respectively. Its
`strict:false` concerns lifecycle handler/initialization warnings, not a route
to write arbitrary chat records. No legacy send or raw browser automation was
used. The self-contained message already includes the full pair and review gate.

Official [OpenAI UI guidance](https://developers.openai.com/plugins/build/chatgpt-ui)
maps follow-up messages to `ui/message`; the
[component reference](https://developers.openai.com/plugins/reference) lists the
ChatGPT compatibility alias. These establish supported interfaces, not proof of
successful routing in this account. Do not blindly call both interfaces or
retry an acknowledged/ambiguous send: doing so can duplicate user messages.

## Current safe behavior and next boundary

Keep the existing copy-to-chat fallback so the real user can still select and
continue the approval/production workflow. It is a manual fallback, not the
requested automatic return. Existing read-only source/resource checks and
24 isolated cases passed, but they cannot certify host receipt.

The test's exact owned foreground server/tunnel sessions were stopped after the
user click, with no remaining listeners on ports3000/8080. Existing plugin,
runtime backups, server source, keys, auth and permissions remain intact.

For an automatic-return closure, the intended host must supply a working
`ui/message` delivery path or a verifiable host diagnostic showing the actual
destination/rejection. This report is prepared on the user's existing PR; no
external support message/issue, new App, account permission, hosting or payment
was created. Do not repeat the same test without a changed host condition or
new routing evidence. Cloud Work's separate write/render/private-download pass
and the private photo PPTX remain valid within their own scopes.

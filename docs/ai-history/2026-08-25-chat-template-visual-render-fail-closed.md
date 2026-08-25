# Chat Template Visual Render Fail-Closed

Updated: 2026-08-25 10:56 KST

The prior chat-first template-selection correction was incomplete because it changed the preferred surface but did not make actual visual rendering a completion criterion. A conversational host could still list template names/numbers and incorrectly treat the selection prompt as displayed.

## Final rule

On ChatGPT and other conversational hosts capable of rendering visuals, template selection is incomplete unless at least one exact registered Slide Master preview is visibly rendered for every registered template offered for selection.

Names/numbers only, prose-only descriptions, external-gallery redirection while inline rendering is available, approximated thumbnails, or asking for a number before actual previews appear are explicit failures.

On an unexpected inline render failure, retry once using the exact registered SVG source. Only after that may the external HTML/GUI fallback be used when the host is genuinely unable to render visuals.

The FAH contract itself remains unchanged at v1.0 / blob SHA d8c24c26460cded0fe947df75b2e278488fd7641. No GitHub Actions or FAH runtime deployment were used.

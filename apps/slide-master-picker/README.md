# Slide Master Template Picker — ChatGPT MCP App

This app turns the Slide Master template-selection gate into a real interactive UI inside ChatGPT.

## What it does

- exposes one read-only MCP tool: `open_slide_master_template_picker`;
- refreshes the current Slide Master Deck/Layout catalog;
- shows 5–10 recommended templates (default 6) plus the complete ACTIVE library;
- renders real registered SVG previews, with up to 6 detail examples;
- provides Free Design and production-preset selection;
- sends the final `deck:<id> | preset:<id>` selection back into the ChatGPT conversation using MCP Apps UI messaging;
- keeps PPT generation blocked until the normal Slide Master selection-evidence gate is satisfied.

## Install / run

```text
cd apps/slide-master-picker
npm install
npm start
```

Environment variables:

- `PORT` — default `3000`.
- `PICKER_SOURCE` — `github` (production default) or `local` (local smoke tests).
- `PYTHON` — Python executable name/path; default `python`.

Health endpoint: `GET /health`
MCP endpoint: `POST/GET /mcp`

## ChatGPT connection

ChatGPT does not connect directly to a localhost MCP server. For development, expose the `/mcp` endpoint through OpenAI Secure MCP Tunnel or another trusted HTTPS deployment, then create/enable the custom app in ChatGPT Developer Mode and run **Scan Tools**.

The GPTS instructions must treat `open_slide_master_template_picker` as mandatory for new PPT requests unless the user already named a valid registered template.

## Security

The picker tool is read-only. It does not write files, register templates, or generate PPTX. Company/private template catalogs must only be added after server-side authorization is in place; do not expose confidential source assets through a public unauthenticated endpoint.

## Local validation

Run:

```text
npm run build
npm run check
```

Then use an MCP client/Inspector against `http://localhost:3000/mcp`. Validate that the tool is discoverable, returns shortlist metadata, and the UI resource MIME is `text/html;profile=mcp-app`.

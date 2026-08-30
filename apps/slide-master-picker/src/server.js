import express from "express";
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import path from "node:path";
import { spawnSync } from "node:child_process";
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StreamableHTTPServerTransport } from "@modelcontextprotocol/sdk/server/streamableHttp.js";
import { registerAppResource, registerAppTool, RESOURCE_MIME_TYPE } from "@modelcontextprotocol/ext-apps/server";
import { z } from "zod/v3";

const HERE = path.dirname(fileURLToPath(import.meta.url));
const APP_ROOT = path.resolve(HERE, "..");
const REPO_ROOT = path.resolve(APP_ROOT, "../..");
const PICKER_SCRIPT = path.join(REPO_ROOT, ".claude", "skills", "ppt-master", "scripts", "template_picker_payload.py");
const BUNDLE_PATH = path.join(APP_ROOT, "web", "dist", "app.js");
const TEMPLATE_URI = "ui://slide-master/template-picker-v1.html";
const PYTHON = process.env.PYTHON || "python";
const SOURCE_VALUES = new Set(["auto", "github", "local"]);
const RAW_SOURCE = String(process.env.PICKER_SOURCE ?? "github");
const SOURCE = RAW_SOURCE.trim().toLowerCase();
if (!SOURCE_VALUES.has(SOURCE)) {
  throw new Error(`Invalid PICKER_SOURCE=${JSON.stringify(RAW_SOURCE)}. Allowed: auto, github, local.`);
}
const PORT = Number(process.env.PORT || 3000);

function loadPayload(purpose, limit) {
  const proc = spawnSync(PYTHON, [PICKER_SCRIPT, "--source", SOURCE, "--purpose", purpose, "--limit", String(limit)], {
    cwd: REPO_ROOT, encoding: "utf8", timeout: 30000, maxBuffer: 16 * 1024 * 1024,
  });
  if (proc.status !== 0) throw new Error((proc.stderr || proc.stdout || "picker payload failed").trim());
  return JSON.parse(proc.stdout);
}

function validateSelection(payload, templateId, presetId) {
  const template = templateId === "free"
    ? { id: "free", name: "Free Design" }
    : payload.all_templates.find((item) => item.id === templateId);
  if (!template) throw new Error(`Unknown or inactive template: ${templateId}`);
  const preset = payload.presets.find((item) => item.id === presetId);
  if (!preset) throw new Error(`Unknown production preset: ${presetId}`);
  const deliveryPurpose = preset.delivery_purpose || "balanced";
  const bodyPx = Number(preset.body_px || (deliveryPurpose === "presentation" ? 40 : deliveryPurpose === "text" ? 28 : 34));
  return {
    template_id: template.id,
    template_name: template.name || template.display_name,
    preset_id: preset.id,
    preset_name: preset.display_name,
    selection_token: `${template.id} | preset:${preset.id}`,
    production_profile: {
      delivery_purpose: deliveryPurpose,
      body_px: bodyPx,
      typography_profile: preset.typography_profile || "modern_readable",
      content_density: preset.content_density || "balanced",
      visual_ratio: preset.visual_ratio || null,
    },
    workflow_contract: {
      next_state: "WAIT_STORYLINE_PREVIEW",
      generation_allowed: false,
      storyline_preview_required: true,
      user_revision_supported: true,
      explicit_storyline_approval_required: true,
      required_preview_fields: ["slide_number", "title", "core_message", "key_content", "visual_layout_plan"],
      rule: "Do not create or export PPTX yet. Research/verify as needed, then show the complete slide-by-slide preview in chat, let the user revise any slide, and wait for explicit approval before generation.",
    },
  };
}

function createMcpServer() {
  const server = new McpServer(
    { name: "slide-master-template-picker", version: "1.0.0" },
    {
      instructions: "For a new PPT request without a directly specified registered template, call open_slide_master_template_picker before giving template recommendations. A successful tool result confirms only that picker data was prepared; it does NOT prove the host rendered the interactive UI. Never tell the user that the gallery is visible until the app view reports SLIDE_MASTER_PICKER_UI_RENDERED. Do not replace the picker with a prose list when the interactive UI is available. After the app validates the final template+preset selection, DO NOT generate or export PPTX. The next required state is WAIT_STORYLINE_PREVIEW: research/verify as needed, then present the complete slide-by-slide preview (slide number, title, core message, key content, visual/layout plan), allow user edits/reordering/count changes, and wait for explicit approval. Only that approval permits PPT generation.",
      capabilities: { tools: {}, resources: {} },
    },
  );

  registerAppResource(server, "slide-master-picker", TEMPLATE_URI, { mimeType: RESOURCE_MIME_TYPE }, async () => {
    const bundle = readFileSync(BUNDLE_PATH, "utf8");
    return {
      contents: [{
        uri: TEMPLATE_URI,
        mimeType: RESOURCE_MIME_TYPE,
        text: `<div id="root"></div><script type="module">${bundle}</script>`,
        _meta: {
          ui: {
            prefersBorder: false,
            csp: { connectDomains: [], resourceDomains: ["data:"] },
          },
          "openai/widgetCSP": { connect_domains: [], resource_domains: ["data:"] },
          "openai/widgetPrefersBorder": false,
        },
      }],
    };
  });

  registerAppTool(
    server,
    "open_slide_master_template_picker",
    {
      title: "Open Slide Master template picker",
      description: "Use this FIRST for every new PPT request when the user did not directly specify a registered template. It renders real Slide Master previews and production presets. Do not answer with a prose-only recommendation list instead.",
      inputSchema: {
        purpose: z.string().min(1).describe("The user's actual presentation purpose/topic."),
        recommendation_limit: z.number().int().min(5).max(10).optional().default(6),
      },
      annotations: { readOnlyHint: true, destructiveHint: false, openWorldHint: false },
      _meta: {
        ui: { resourceUri: TEMPLATE_URI, visibility: ["model", "app"] },
        "openai/outputTemplate": TEMPLATE_URI,
        "openai/widgetAccessible": true,
      },
    },
    async ({ purpose, recommendation_limit = 6 }) => {
      const payload = loadPayload(purpose, recommendation_limit);
      return {
        structuredContent: {
          schema_version: payload.schema_version,
          purpose: payload.purpose,
          source: payload.source,
          payload_ready: true,
          host_ui_rendered: false,
          selectable_total: payload.selectable_total,
          recommended_keys: payload.recommended_keys,
          shortlist: payload.shortlist.map((item) => ({
            id: item.id,
            key: item.key,
            name: item.name,
            reason: item.reason,
          })),
          presets: payload.presets.map((item) => ({
            id: item.id,
            display_name: item.display_name,
            summary: item.summary,
            recommended_rank: item.recommended_rank,
          })),
        },
        content: [{ type: "text", text: `Slide Master picker payload prepared: ${payload.selectable_total} ACTIVE templates. Host UI rendering is NOT confirmed by this result. Do not tell the user the gallery is visible unless the app view reports SLIDE_MASTER_PICKER_UI_RENDERED.` }],
        _meta: { pickerPayload: payload },
      };
    },
  );

  registerAppTool(
    server,
    "validate_slide_master_selection",
    {
      title: "Validate Slide Master selection",
      description: "App-only final validation for a selected template and production preset. Returns a fail-closed workflow contract: selection validation never authorizes PPT generation; the next required step is a user-editable slide-by-slide storyline preview and explicit approval.",
      inputSchema: {
        purpose: z.string().min(1),
        template_id: z.string().min(1),
        preset_id: z.string().min(1),
      },
      annotations: { readOnlyHint: true, destructiveHint: false, openWorldHint: false },
      _meta: { ui: { visibility: ["app"] } },
    },
    async ({ purpose, template_id, preset_id }) => {
      const payload = loadPayload(purpose, 10);
      const selection = validateSelection(payload, template_id, preset_id);
      return {
        structuredContent: { valid: true, ...selection },
        content: [{ type: "text", text: `${selection.selection_token}\nNEXT_STATE=${selection.workflow_contract.next_state}\nGENERATION_ALLOWED=false\nDo not create PPTX yet. Show the complete slide-by-slide preview in chat and wait for explicit user approval after revisions.` }],
      };
    },
  );

  return server;
}

const app = express();
app.use(express.json({ limit: "2mb" }));
app.get("/health", (_req, res) => res.json({ ok: true, source: SOURCE }));
app.all("/mcp", async (req, res) => {
  const server = createMcpServer();
  const transport = new StreamableHTTPServerTransport({ sessionIdGenerator: undefined });
  res.on("close", () => {
    transport.close().catch(() => {});
    server.close().catch(() => {});
  });
  try {
    await server.connect(transport);
    await transport.handleRequest(req, res, req.body);
  } catch (error) {
    if (!res.headersSent) res.status(500).json({ error: String(error?.message || error) });
  }
});

app.listen(PORT, "0.0.0.0", () => {
  console.log(`Slide Master Template Picker MCP listening on http://localhost:${PORT}/mcp`);
  if (RAW_SOURCE !== SOURCE) console.log(`Normalized PICKER_SOURCE ${JSON.stringify(RAW_SOURCE)} -> ${SOURCE}`);
});

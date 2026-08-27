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
const SOURCE = process.env.PICKER_SOURCE || "github";
const PORT = Number(process.env.PORT || 3000);

function loadPayload(purpose, limit) {
  const proc = spawnSync(PYTHON, [PICKER_SCRIPT, "--source", SOURCE, "--purpose", purpose, "--limit", String(limit)], {
    cwd: REPO_ROOT, encoding: "utf8", timeout: 30000,
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
  return {
    template_id: template.id,
    template_name: template.name || template.display_name,
    preset_id: preset.id,
    preset_name: preset.display_name,
    selection_token: `${template.id} | preset:${preset.id}`,
  };
}

function createMcpServer() {
  const server = new McpServer(
    { name: "slide-master-template-picker", version: "1.0.0" },
    {
      instructions: "For a new PPT request without a directly specified registered template, call open_slide_master_template_picker before giving template recommendations. Do not replace it with a prose list when the interactive UI is available.",
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
        _meta: { ui: { prefersBorder: false } },
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
      _meta: { ui: { resourceUri: TEMPLATE_URI, visibility: ["model", "app"] } },
    },
    async ({ purpose, recommendation_limit = 6 }) => {
      const payload = loadPayload(purpose, recommendation_limit);
      const light = (items) => items.map((t) => ({
        id: t.id, name: t.name, template_kind: t.template_kind, summary: t.summary,
        reason: t.reason, recommended: Boolean(t.rec), preview_count: t.previews?.length || 0,
      }));
      return {
        structuredContent: {
          purpose: payload.purpose, source: payload.source,
          registered_total: payload.registered_total, selectable_total: payload.selectable_total,
          shortlist: light(payload.shortlist), presets: payload.presets, free_design: payload.free_design,
        },
        content: [{ type: "text", text: `Slide Master 템플릿 ${payload.shortlist.length}개를 인터랙티브 선택 화면에 표시했습니다.` }],
        _meta: { pickerPayload: payload },
      };
    },
  );

  registerAppTool(
    server,
    "validate_slide_master_selection",
    {
      title: "Validate Slide Master selection",
      description: "Validate a template/preset selection from the interactive picker before it is sent back to chat.",
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
        structuredContent: selection,
        content: [{ type: "text", text: selection.selection_token }],
      };
    },
  );

  return server;
}

const app = express();
app.use(express.json({ limit: "12mb" }));
app.get("/health", (_req, res) => res.json({ ok: true, app: "slide-master-template-picker", source: SOURCE }));
app.all("/mcp", async (req, res) => {
  const server = createMcpServer();
  const transport = new StreamableHTTPServerTransport({ sessionIdGenerator: undefined });
  res.on("close", () => {
    void transport.close().catch(() => {});
    void server.close().catch(() => {});
  });
  try {
    await server.connect(transport);
    await transport.handleRequest(req, res, req.body);
  } catch (error) {
    console.error(error);
    if (!res.headersSent) res.status(500).json({ error: "MCP request failed" });
  }
});

app.listen(PORT, "0.0.0.0", () => {
  console.log(`Slide Master Template Picker MCP listening on http://localhost:${PORT}/mcp`);
});

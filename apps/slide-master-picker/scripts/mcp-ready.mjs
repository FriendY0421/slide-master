import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StreamableHTTPClientTransport } from "@modelcontextprotocol/sdk/client/streamableHttp.js";

const mcpUrl = process.env.MCP_URL || "http://127.0.0.1:3000/mcp";
const client = new Client({ name: "slide-master-picker-startup-readiness", version: "1.0.0" });
const transport = new StreamableHTTPClientTransport(new URL(mcpUrl));

try {
  await client.connect(transport);
  const tools = await client.listTools();
  const names = new Set(tools.tools.map((tool) => tool.name));
  if (!names.has("open_slide_master_template_picker") || !names.has("validate_slide_master_selection")) {
    throw new Error("required Picker MCP tools are missing");
  }
  console.log("MCP_READY PASS");
} finally {
  await client.close().catch(() => {});
}

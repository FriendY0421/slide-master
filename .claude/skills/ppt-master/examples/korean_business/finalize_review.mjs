// Validate existing-converter output with the shared Presentations finalizer.
// No slide authoring, re-export or replacement engine is introduced here.
import fs from "node:fs/promises";
import path from "node:path";
import { pathToFileURL } from "node:url";

const [workspaceArg, inputArg, finalArg, kind, skillDir] = process.argv.slice(2);
if (![workspaceArg, inputArg, finalArg, kind, skillDir].every(Boolean)
    || !["baseline", "improved"].includes(kind)) {
  throw new Error("Usage: finalize_review.mjs WORKSPACE INPUT FINAL baseline|improved SHARED_SKILL_DIR");
}
const workspaceDir = path.resolve(workspaceArg);
const finalPath = path.resolve(finalArg);
await fs.mkdir(path.dirname(finalPath), { recursive: true });
const { finalizePresentation } = await import(pathToFileURL(
  path.join(skillDir, "container_tools/artifact_tool_utils.mjs"),
).href);
const tableOwners = kind === "improved" ? [5, 6] : [];
const result = await finalizePresentation({
  workspaceDir, candidatePath: path.resolve(inputArg), finalPath,
  pythonExecutable: process.env.RUNTIME_PYTHON,
  integrityValidatorPath: path.join(skillDir, "container_tools/inspect_presentation_package_integrity.py"),
  layoutValidatorPath: path.join(skillDir, "container_tools/inspect_presentation_layout_geometry.py"),
  explicitTotalSlideCount: 6,
  requiredNativeChartOwnerSlides: kind === "improved" ? [2, 3] : [],
  requiredNativeTableOwnerSlides: tableOwners,
  layoutArgs: ["--expected-slide-size-emu", "12192000,6858000", "--validate-heading-fit",
    ...tableOwners.flatMap(n => ["--require-native-table-slide", String(n)])],
  fontPolicy: { basis: "design", families: ["Pretendard"] },
  verifyArtifactToolImport: true,
  receiptPath: path.join(workspaceDir, `${kind}.finalization.json`),
});
console.log(JSON.stringify({ finalPath, status: result?.status ?? "completed" }));

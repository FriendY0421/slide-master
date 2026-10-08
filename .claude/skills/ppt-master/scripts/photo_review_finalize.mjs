// Finalization only: authoring remains in the existing structured SVG compiler.
import fs from "node:fs/promises";
import path from "node:path";
import { pathToFileURL } from "node:url";

const [workspace, candidate, final, profilePath, skillDir, sizeEmu] = process.argv.slice(2);
if (![workspace, candidate, final, profilePath, skillDir, sizeEmu].every(Boolean)) {
  throw new Error("Usage: photo_review_finalize.mjs WORKSPACE CANDIDATE FINAL PROFILE SHARED_SKILL SIZE_EMU");
}
if (!path.isAbsolute(process.env.RUNTIME_PYTHON ?? "")) {
  throw new Error("Supplied RUNTIME_PYTHON required");
}
const profile = JSON.parse(await fs.readFile(profilePath, "utf8"));
const { finalizePresentation } = await import(pathToFileURL(
  path.join(skillDir, "container_tools/artifact_tool_utils.mjs"),
).href);
const result = await finalizePresentation({
  workspaceDir: workspace, candidatePath: candidate, finalPath: final,
  pythonExecutable: process.env.RUNTIME_PYTHON,
  integrityValidatorPath: path.join(skillDir, "container_tools/inspect_presentation_package_integrity.py"),
  layoutValidatorPath: path.join(skillDir, "container_tools/inspect_presentation_layout_geometry.py"),
  layoutArgs: ["--expected-slide-size-emu", sizeEmu, "--validate-bullet-geometry", "--validate-heading-fit"],
  explicitTotalSlideCount: profile.slide_count,
  requiredNativeTableOwnerSlides: [], requiredNativeChartOwnerSlides: [],
  requiredEmbeddedWorkbookChartOwnerSlides: [],
  fontPolicy: { basis: "design", families: [profile.font_family] },
  verifyArtifactToolImport: true,
  receiptPath: path.join(workspace, "analysis/shared-finalization-receipt.json"),
});
console.log(JSON.stringify(result, null, 2));

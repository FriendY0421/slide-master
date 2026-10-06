// Three-page contributor comparison, validated by shared Presentations runtime.
// Existing repository converter authors the candidate; this only checks/copies it.
import path from "node:path";
import fs from "node:fs/promises";
import { pathToFileURL } from "node:url";
const [workspace, candidate, final, skillDir] = process.argv.slice(2);
if (![workspace, candidate, final, skillDir].every(Boolean)) throw new Error("Usage: WORKSPACE CANDIDATE FINAL SHARED_SKILL_DIR");
await fs.mkdir(path.dirname(path.resolve(final)), {recursive:true});
const { finalizePresentation } = await import(pathToFileURL(path.join(skillDir,"container_tools/artifact_tool_utils.mjs")).href);
const result = await finalizePresentation({
  workspaceDir:path.resolve(workspace), candidatePath:path.resolve(candidate), finalPath:path.resolve(final),
  pythonExecutable:process.env.RUNTIME_PYTHON,
  integrityValidatorPath:path.join(skillDir,"container_tools/inspect_presentation_package_integrity.py"),
  layoutValidatorPath:path.join(skillDir,"container_tools/inspect_presentation_layout_geometry.py"),
  explicitTotalSlideCount:3, requiredNativeChartOwnerSlides:[2], requiredNativeTableOwnerSlides:[],
  requiredEmbeddedWorkbookChartOwnerSlides:[2],
  layoutArgs:["--expected-slide-size-emu","12192000,6858000","--validate-heading-fit"],
  fontPolicy:{basis:"design",families:["Pretendard"]}, verifyArtifactToolImport:true,
  receiptPath:path.resolve(workspace,path.basename(final)+".finalization.json"),
});
console.log(JSON.stringify({final,status:result?.status??"completed"}));

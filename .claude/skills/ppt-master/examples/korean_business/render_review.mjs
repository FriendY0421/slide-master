// Review helper using the shared Presentations runtime API. No authoring engine.
// RUNTIME_* must point to the supplied runtime; no packages are installed here.
import fs from "node:fs/promises";
import path from "node:path";
import { createHash } from "node:crypto";
import { pathToFileURL } from "node:url";
import { createRequire } from "node:module";

const [input, output, profilePath, skillDir] = process.argv.slice(2);
if (![input, output, profilePath, skillDir].every(Boolean)) {
  throw new Error("Usage: render_review.mjs INPUT OUTPUT_DIR PROFILE SHARED_PRESENTATIONS_SKILL_DIR");
}
const { importRuntimeModule } = await import(pathToFileURL(
  path.join(skillDir, "container_tools/runtime_helpers.mjs"),
).href);
const hash = bytes => createHash("sha256").update(bytes).digest("hex");
const profile = JSON.parse(await fs.readFile(profilePath, "utf8"));
const fontPaths = profile.font_files.map(p => path.resolve(path.dirname(profilePath), p));
// Use artifact-tool's bundled renderer dependency, rather than a global canvas.
if (!path.isAbsolute(process.env.RUNTIME_NODE_MODULES ?? "")) {
  throw new Error("RUNTIME_NODE_MODULES must name the supplied runtime modules directory");
}
const runtimeRequire = createRequire(path.join(
  process.env.RUNTIME_NODE_MODULES, "@oai/artifact-tool/package.json",
));
const { FontLibrary } = runtimeRequire("skia-canvas");
FontLibrary.use(profile.font_family, fontPaths);
if (!FontLibrary.families.includes(profile.font_family)) {
  throw new Error(`Bundled ${profile.font_family} font registration failed`);
}
const registeredFonts = {};
for (const font of fontPaths) registeredFonts[font] = hash(await fs.readFile(font));
const { FileBlob, PresentationFile } = await importRuntimeModule("@oai/artifact-tool");
const presentation = await PresentationFile.importPptx(await FileBlob.load(input));
const slides = presentation.slides.items;
if (slides.length !== profile.slide_count) throw new Error("Unexpected slide count");
await fs.mkdir(output, { recursive: true });
const images = [];
for (let i = 0; i < slides.length; i++) {
  const blob = await presentation.export({ slide: slides[i], format: "png", scale: 1 });
  const bytes = Buffer.from(await blob.arrayBuffer());
  const name = `slide-${i + 1}.png`;
  await fs.writeFile(path.join(output, name), bytes);
  images.push({ slide: i + 1, path: name, sha256: hash(bytes) });
}
await fs.writeFile(path.join(output, "render-manifest.json"), JSON.stringify({
  renderer: "shared Presentations runtime / artifact-tool importPptx + export png",
  artifact_tool_version: runtimeRequire("./package.json").version,
  node_version: process.version,
  pptx_sha256: hash(await fs.readFile(input)), registered_fonts: registeredFonts, images,
}, null, 2) + "\n");
console.log(JSON.stringify({ output, slides: images.length, registeredFonts }, null, 2));

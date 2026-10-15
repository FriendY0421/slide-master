// Review existing PPTX using the supplied runtime; never installs or authors.
import fs from 'node:fs/promises';
import path from 'node:path';
import {createHash} from 'node:crypto';
import {createRequire} from 'node:module';
import {pathToFileURL} from 'node:url';

const [input, output, runtimeRoot, profilePath] = process.argv.slice(2);
if (![input, output, runtimeRoot, profilePath].every(Boolean)) {
  throw new Error('Invoke through render_pptx_review.py with explicit runtime and profile/mode');
}
const req=createRequire(path.join(path.resolve(runtimeRoot),'@oai/artifact-tool/package.json'));
const skia=req('skia-canvas');
let cpuCanvasCount=0;
// Reuse the existing operating review helper's supported property setter.
// A constructor gpu:false option did not prevent native teardown failures here.
if(process.platform==='win32') {
  const NativeCanvas=skia.Canvas;
  skia.Canvas=class WindowsCpuCanvas extends NativeCanvas {
    constructor(...args) {
      super(...args);
      this.gpu=false;
      if(this.gpu) throw new Error('Windows CPU renderer selection failed');
      cpuCanvasCount++;
    }
  };
}
const hash=bytes=>createHash('sha256').update(bytes).digest('hex');
const profile=profilePath==='geometry-only'?null:JSON.parse(await fs.readFile(profilePath,'utf8'));
const fontHashes={};
if(profile) {
  if(!profile.font_family || !Array.isArray(profile.font_files) || !profile.font_files.length) {
    throw new Error('Explicit family and actual font files required; no automatic fallback');
  }
  const fonts=[];
  for(const entry of profile.font_files) {
    if(!entry.path || !/^[a-f0-9]{64}$/.test(entry.sha256??'')) throw new Error('Font profile requires verified hashes');
    const file=path.resolve(path.dirname(profilePath),entry.path);
    const actual=hash(await fs.readFile(file));
    if(actual!==entry.sha256) throw new Error('Font source differs from profile');
    fonts.push(file);fontHashes[file]=actual;
  }
  skia.FontLibrary.use(profile.font_family,fonts);
  if(!skia.FontLibrary.families.includes(profile.font_family)) throw new Error('Requested font registration failed');
}
// Patch only this child process before loading Artifact Tool's Canvas binding.
const {FileBlob,PresentationFile}=await import(pathToFileURL(path.join(path.resolve(runtimeRoot),
  '@oai/artifact-tool/dist/artifact_tool.mjs')).href);
const deck=await PresentationFile.importPptx(await FileBlob.load(input));
if(!deck.slides.items.length) throw new Error('No slides imported');
if(profile?.slide_count && deck.slides.items.length!==profile.slide_count) throw new Error('Unexpected slide count');
await fs.mkdir(output,{recursive:true});
const images=[];
for(let i=0;i<deck.slides.items.length;i++) {
  const blob=await deck.export({slide:deck.slides.items[i],format:'png',scale:1});
  const bytes=Buffer.from(await blob.arrayBuffer());
  const name=`slide-${i+1}.png`;
  await fs.writeFile(path.join(output,name),bytes);
  images.push({slide:i+1,path:name,sha256:hash(bytes)});
}
await fs.writeFile(path.join(output,'render-manifest.json'),JSON.stringify({
  renderer:'artifact-tool importPptx/export PNG; existing Windows CPU property-setter workaround',
  node_version:process.version,cpu_canvas_count:cpuCanvasCount,
  pptx_sha256:hash(await fs.readFile(input)),images,registered_fonts:fontHashes,
  font_profile_registered:Boolean(profile),text_font_verified:false,geometry_only:!profile,powerpoint:false,
  process_completed:false,license_verified:false
},null,2)+'\n');
console.log(JSON.stringify({slides:images.length,cpuCanvasCount,geometryOnly:!profile}));

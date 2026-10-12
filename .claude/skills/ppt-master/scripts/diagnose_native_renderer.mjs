// Read-only, font-independent isolation. No PPT, installation or forced success.
import {spawnSync} from 'node:child_process';
import {createRequire} from 'node:module';
import path from 'node:path';
import fs from 'node:fs';

const [runtimeRoot, output] = process.argv.slice(2);
if (!runtimeRoot || !output) throw new Error('Usage: node diagnose_native_renderer.mjs <node_modules> <report.json>');
const req = createRequire(path.join(path.resolve(runtimeRoot), '@oai/artifact-tool/package.json'));
const skia = req.resolve('skia-canvas');
const results=[];
for (const mode of ['node-only','module-only','cpu','gpu']) {
  const code = `
    const stage=s=>console.log(JSON.stringify(s));
    process.on('exit',code=>stage({stage:'js-exit',code}));
    stage({stage:'start'});
    ${mode==='node-only' ? '' : `const {Canvas}=require(${JSON.stringify(skia)});stage({stage:'module-loaded'});`}
    ${['cpu','gpu'].includes(mode) ? `const canvas=new Canvas(300,100,{gpu:${mode==='gpu'}});
      canvas.getContext('2d').fillRect(0,0,20,20);
      stage({stage:'engine',engine:canvas.engine});
      canvas.toBuffer('png').then(bytes=>stage({stage:'render-complete',bytes:bytes.length}));` : ''}
  `;
  const child=spawnSync(process.execPath,['-e',code],{encoding:'utf8',timeout:30000,windowsHide:true});
  results.push({mode,status:child.status,windowsStatusHex:child.status===null?null:
    '0x'+(child.status>>>0).toString(16),signal:child.signal,error:child.error?.message??null,
    stdout:child.stdout,stderr:child.stderr});
}
const report={nodeVersion:process.version,platform:process.platform,
  skiaVersion:JSON.parse(fs.readFileSync(path.join(path.dirname(skia),'../package.json'),'utf8')).version,results,
  passed:results.every(item=>item.status===0)};
fs.writeFileSync(output,JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify(report,null,2));
if(!report.passed)process.exitCode=1;

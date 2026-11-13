const fs = require('node:fs');
const vm = require('node:vm');
const source = fs.readFileSync(process.argv[2], 'utf8');
const start = source.indexOf('async function confirmSelection()');
const end = source.indexOf('\nfunction renderFinal()', start);
if (start < 0 || end < 0) throw Error('Original confirmation function not found');
const fn = source.slice(start, end);
const expected = {
  valid: true, template_id: 'deck:fixture', preset_id: 'fixture',
  selection_token: 'deck:fixture | preset:fixture',
  workflow_contract: {next_state: 'WAIT_STORYLINE_PREVIEW', generation_allowed: false},
};
const cases = [
  ['valid', {structuredContent: expected}, true],
  ['server_is_error', {isError:true, content:[{type:'text',text:'Unknown or inactive template'}]}, false],
  ['server_invalid', {structuredContent:{...expected,valid:false}}, false],
  ['wrong_template', {structuredContent:{...expected,template_id:'deck:other'}}, false],
  ['wrong_preset', {structuredContent:{...expected,preset_id:'other'}}, false],
  ['wrong_token', {structuredContent:{...expected,selection_token:'deck:other | preset:fixture'}}, false],
  ['generation_allowed', {structuredContent:{...expected,workflow_contract:{...expected.workflow_contract,generation_allowed:true}}}, false],
  ['missing_contract', {structuredContent:{...expected,workflow_contract:null}}, false],
  ['missing_result', undefined, false],
  ['transport_502', Error('HTTP 502 Bad Gateway'), true],
  ['thrown_rejection', Error('Unknown or inactive template: deck:fixture'), false],
  ['transport_503', Error('HTTP 503 Service Unavailable'), true],
  ['unknown_exception', Error('Unexpected parser failure'), false],
  ['stale_payload', {structuredContent:expected}, false],
  ['removed_template', {structuredContent:expected}, false],
  ['removed_preset', {structuredContent:expected}, false],
];
(async () => {
 const results = [];
 for (const [name,result,shouldSend] of cases) {
   const calls = [];
   const root = {innerHTML:'',querySelectorAll:()=>[]};
   const sandbox = {
    selectedTemplate:{id:'deck:fixture'}, selectedPreset:{id:'fixture'},
    payload:{purpose:'Synthetic 1 slides',all_templates:[{id:'deck:fixture'}],presets:[{id:'fixture'}]},
    confirmationInFlight:false,root, console:{warn:()=>{}}, navigator:{},
    esc:(s)=>String(s??''), bind:()=>{}, renderGallery:()=>{}, renderFinal:()=>{},
    localToken:()=> 'deck:fixture | preset:fixture',
    app:{callServerTool:async()=>{if(name==='stale_payload')sandbox.payload={...sandbox.payload};if(result instanceof Error)throw result;return result},
      updateModelContext:async(v)=>{calls.push(['context',v]);},
      sendMessage:async(v)=>{calls.push(['message',v]);return{};}}
   };
   if(name==='removed_template')sandbox.payload.all_templates=[];
   if(name==='removed_preset')sandbox.payload.presets=[];
   await vm.runInNewContext(fn+'\nconfirmSelection()',sandbox);
   const sent=calls.some(x=>x[0]==='message');
   const contextUpdated=calls.some(x=>x[0]==='context');
   const resultRow={name,shouldSend,sent,contextUpdated,pass:sent===shouldSend && (shouldSend||!contextUpdated)};
   results.push(resultRow);
 }
 console.log(JSON.stringify({scope:'isolated original confirmation-function execution; mocked bridge, not host/user acceptance',results,failures:results.filter(x=>!x.pass).length},null,2));
 if (results.some(x=>!x.pass)) process.exitCode=1;
})();

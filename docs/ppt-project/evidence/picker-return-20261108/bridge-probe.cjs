const fs=require('node:fs'),vm=require('node:vm');
const source=fs.readFileSync(process.argv[2],'utf8');const start=source.indexOf('async function confirmSelection()');const end=source.indexOf('\nfunction renderFinal()',start);if(start<0||end<0)throw Error('Missing actual confirmation function');
const expected={valid:true,template_id:'deck:fixture',preset_id:'fixture',selection_token:'deck:fixture | preset:fixture',workflow_contract:{next_state:'WAIT_STORYLINE_PREVIEW',generation_allowed:false}};
(async()=>{const results=[];for(const name of ['normal','context_rejection','context_timeout','context_stale','double_click','message_rejection','message_timeout','invalid_validation']){
 const calls=[];const root={innerHTML:'',querySelectorAll:()=>[]};const options={};
 const sandbox={confirmationInFlight:false,selectedTemplate:{id:'deck:fixture'},selectedPreset:{id:'fixture'},payload:{purpose:'Synthetic 1 slides',all_templates:[{id:'deck:fixture'}],presets:[{id:'fixture'}]},root,console:{warn:()=>{}},navigator:{},esc:v=>String(v??''),bind:()=>{},renderGallery:()=>{},renderFinal:()=>{},localToken:()=>expected.selection_token,
 app:{callServerTool:async()=>({structuredContent:{...expected,valid:name!=='invalid_validation'}}),updateModelContext:async(v,o)=>{calls.push('context');options.context=o;if(name==='context_stale')sandbox.payload={...sandbox.payload};if(name==='context_rejection'||name==='context_timeout')throw Error(name);return{};},sendMessage:async(v,o)=>{calls.push('message');options.message=o;if(!v.content[0].text.includes('GENERATION_ALLOWED=false')||!v.content[0].text.includes(expected.selection_token))throw Error('Incomplete message');if(name==='message_rejection')return{isError:true};if(name==='message_timeout')throw Error('Request timed out');return{};}}};
 vm.createContext(sandbox);vm.runInContext(source.slice(start,end)+'\nglobalThis.invoke=confirmSelection;',sandbox);await Promise.all(name==='double_click'?[sandbox.invoke(),sandbox.invoke()]:[sandbox.invoke()]);
 const expectedMessages=['context_stale','invalid_validation'].includes(name)?0:1;const messageCount=calls.filter(x=>x==='message').length;let pass=messageCount===expectedMessages;
 if(name==='message_rejection'||name==='message_timeout')pass=pass&&root.innerHTML.includes('자동 채팅 전달이 제한');
 if(name==='context_timeout')pass=pass&&options.context?.timeout===4000;
 if(name==='normal')pass=pass&&options.message?.timeout===15000;
 results.push({name,messageCount,expectedMessages,pass});
 }
 const report={scope:'actual confirmation-function isolated execution; mocked MCP host, not actual user or transcript acceptance',results,failures:results.filter(r=>!r.pass).length};console.log(JSON.stringify(report,null,2));if(report.failures)process.exitCode=1;
})().catch(e=>{console.error(e);process.exitCode=1});

# 클라우드 재현 실행 안내 (Draft PR 검토용)

2026-10-07: 기능 기준은 `58a25cede9ebbaf44cd76a216ae522cdc2caf7fb`다. 별도 검토자의 67 PASS는 부모 작업에서 전달받은 결과이며 여기서 재실행한 수치가 아니다. 이번 변경은 문서와 합성 검증 기록만 추가한다. main 병합, 플러그인 업데이트, 운영 활성화는 하지 않았다.

## 실제 확인과 남은 경계

동일한 공급 Linux 런타임에서 저장소 작업 경로와 별도 tracked checkout의 경로를 바꾸어 검사했다. 각 19개 입력/환경/승인/생성 검사, 각 기본 2장과 사용자정의 6장의 공유 Presentations finalization 및 렌더를 수행했다. 8쌍은 픽셀 일치하며 기존 공개 검토 이미지와도 모두 일치한다. 폰트는 저장소의 OFL Pretendard Regular/Bold 실파일과 해시/버전을 검증했다.

기본 경로는 intake → 실제 main 카탈로그 → 직접 지정 기록 → 구성 승인 fixture → init → **기존 템플릿 검토 exporter** 범위다. 전체 main SVG 제작/verify_deck/실사용 전달의 완료 증거가 아니다. 사용자정의 경로는 표준 project init/import → 별도 작업 brief → count/SHA 결합 계획 → apply → exact readback → 공유 finalization/render 범위다. OfficeCLI가 없어 해당 owner의 native 앱 gate는 미완료다.

두 PC, 실제 PowerPoint/Edit Data, 같은 계정의 새 대화 자동 적용, 실제 선택 UI 표시, 비공개 전달, 실제 회사자료·사진·사설 폰트는 확인하지 않았다. 임시 파일은 새 세션에서 사라질 수 있으므로 아래 코드를 문서에서 다시 저장한다. 이전 `/tmp` 파일을 실행 전제에 넣지 않는다.

[검증 기록](../../.claude/skills/ppt-master/examples/cloud_entry/cloud_portability/README.md)에 정확한 버전·해시·단계·실패해야 하는 사례를 남겼다. 생성 ZIP 전체 해시는 시각 메타데이터 때문에 매 실행 달라질 수 있다. 내부 파트, 승인 결합, readback 및 렌더를 함께 비교한다.

## 실행 담당자 시작 절차

1. 대상은 `FriendY0421/slide-master`만 사용한다. 기존 credentials, `.aws`, 환경 파일, private cache, 다른 프로젝트를 복사하지 않는다. 실제 작업은 최신 승인 main과 guard/router/선택 owner를 먼저 확인한다. 아래 exact SHA는 **PR의 합성 재현 검토용**이다.
2. `AGENTS.md`, `CLAUDE.md`, `PPT_REQUEST_GUARD.md`와 선택 owner skill을 읽는다. 실제 PPTX 검토 전 호스트가 제공한 공유 Presentations `SKILL.md`와 finalization/render 지원 경로를 읽는다. 없으면 제작·검수 한계를 보고하고 런타임을 임의 설치하거나 대체하지 않는다.
3. 공급된 `CODEX_PRIMARY_RUNTIME`, `CODEX_PRIMARY_RUNTIME_PYTHON`, `CODEX_PRIMARY_RUNTIME_NODE`, `CODEX_PRIMARY_RUNTIME_NODE_MODULES`를 확인한다. 내부 helper용 `RUNTIME_*`는 그 값 그대로 연결한다. PC의 PATH나 예전 세션 절대경로를 재사용하지 않는다. 누락 시 existing environment gate가 중단해야 한다.
4. 기본 모드는 최신 카탈로그의 실제 source commit/미리보기/선택을 기록한다. 사용자정의는 원본과 내용부터 받는다. font/pt/count/writing rules 중 빠진 것만 묻고, 이미 확인한 입력을 반복해서 묻지 않는다. 14/12pt를 모든 슬라이드에 강제하지 않는다.
5. 실사용 승인 기록은 실제 사용자 확인에서 만든다. 합성 실행의 `confirmed`, `approved_by: user` 구조는 테스트 fixture일 뿐이다. 아래 실행을 사용자의 승인이나 실제 UI 표시 증거로 재사용하지 않는다.
6. 작업 자료/폰트는 작업별 상대 경로로 해석하고 실파일·라이선스·해시·버전을 확인한다. custom plan에는 별도 complete confirmed v2 brief, 양의 정수 requested_slide_count, 정확한 brief byte SHA가 필수다. 생성/재개/force 모두 동일 gate를 따른다.
7. 후보/최종 파일은 별도 경로에 두고 validation/deliverables 폴더를 먼저 만든다. 지원 finalizer의 구조/레이아웃/폰트/native chart/table gate 후 모든 페이지를 렌더해 검수한다. owner 요구 OfficeCLI와 실제 앱 검증, 전달 검증은 각각 따로 기록한다.

## 고정 기준의 합성 재현

운영용 설치 안내가 아니라, 준비된 클라우드 환경에서 실행한 검토 절차다. 추가 의존성 설치/유료 API/로그인이 필요하면 중단하고 제안한다. 새 빈 작업 디렉터리에서 시작한다. 기존 scratch가 있으면 보존하거나 다른 checkout을 사용한다. 아래 Python은 해당 checkout의 `projects/_smoke_cloud_portability`만 초기화하므로 실제 작업을 그 이름으로 넣지 않는다.

```bash
# TASK_DIR는 새 빈 검토 경로. 실제 자료/credential을 복사하지 않는다.
TASK_DIR=/tmp/slide-master-review-20261007
mkdir "$TASK_DIR"
git clone https://github.com/FriendY0421/slide-master.git "$TASK_DIR/repo"
git -C "$TASK_DIR/repo" checkout --detach 58a25cede9ebbaf44cd76a216ae522cdc2caf7fb
export RUNTIME_PYTHON="${CODEX_PRIMARY_RUNTIME_PYTHON:?supplied Python required}"
export RUNTIME_NODE="${CODEX_PRIMARY_RUNTIME_NODE:?supplied Node required}"
export RUNTIME_NODE_MODULES="${CODEX_PRIMARY_RUNTIME_NODE_MODULES:?supplied modules required}"
export RUNTIME_ROOT="${CODEX_PRIMARY_RUNTIME:?supplied runtime required}"
# PRESENTATIONS_SKILL는 현재 호스트가 제공한 공유 skill 디렉터리로 지정한다.
PRESENTATIONS_SKILL=/opt/codex/skills/builtins/presentations
cat "$PRESENTATIONS_SKILL/SKILL.md"
"$RUNTIME_PYTHON" -c 'import sys,importlib.metadata as m; print(sys.version); print({p:m.version(p) for p in ["python-pptx","Pillow","fonttools","lxml","jsonschema"]})'
"$RUNTIME_NODE" --version
```

다음 Python 코드 블록을 `$TASK_DIR/audit.py`로 저장한다. `--visual-only`는 기존 공개 2장 fixture의 검토 exporter이며 production QA 우회용으로 사용하지 않는다. 네트워크 읽기는 main 카탈로그에만 사용한다. 현재 main이 바뀌면 실제 카탈로그 SHA와 source previews를 새로 기록한다.

```python
import copy,hashlib,importlib.metadata,json,os,shutil,subprocess,sys,zipfile
from xml.etree import ElementTree as ET
from pathlib import Path
BASE='58a25cede9ebbaf44cd76a216ae522cdc2caf7fb'
root=Path(sys.argv[1]).resolve(); work=root/'projects/_smoke_cloud_portability'; shutil.rmtree(work,ignore_errors=True);work.mkdir(parents=True,exist_ok=True); inp=work/'input';inp.mkdir(exist_ok=True);scripts=root/'.claude/skills/ppt-master/scripts';sys.path.insert(0,str(scripts))
from presentation_brief import validate_brief,check_environment
from storyline_gate import make_approval
from project_manager import ProjectManager
from private_font_cache import font_availability
checks=[];cmds=[]
def check(name,value):
 if not value:raise RuntimeError(name)
 checks.append({'name':name,'passed':True})
def cli(name,args,ok=True):
 cmd=[sys.executable,str(scripts/name),*map(str,args)];r=subprocess.run(cmd,cwd=root,capture_output=True,text=True)
 if (r.returncode==0)!=ok:raise RuntimeError(name+': '+r.stdout+r.stderr)
 cmds.append({'script':name,'exit_code':r.returncode,'expected_success':ok});return r
check('exact reviewed source commit',subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip()==BASE)
for package in ['python-pptx','Pillow','fonttools','lxml','jsonschema']:importlib.metadata.version(package)
versions={p:importlib.metadata.version(p) for p in ['python-pptx','Pillow','fonttools','lxml','jsonschema']}
fontdir=root/'.claude/skills/ppt-master/assets/fonts/Pretendard';original=root/'.claude/skills/ppt-master/examples/cloud_entry/korean_fit';brief=json.loads((original/'task-brief.json').read_text())
def relocate(brief,base,sourcebase):
 for key in ['font_files','content_files','template_files','sample_files']:
  if key in brief:brief[key]=[os.path.relpath((sourcebase/p).resolve(),base) for p in brief[key]]
 if 'font_license_review' in brief:
  p=brief['font_license_review']['evidence_file'];brief['font_license_review']['evidence_file']=os.path.relpath((sourcebase/p).resolve(),base)
 return brief
brief=relocate(brief,inp,original);brief['authorization']='Synthetic portability audit only; not an actual user deck or approval';(inp/'builtin.json').write_text(json.dumps(brief,ensure_ascii=False,indent=2)+'\n')
r=validate_brief(brief,inp);check('complete builtin keeps font/pt/count/rules, asks nothing twice',r['ready_for_plan'] and r['question'] is None and not r['ready_for_generation'])
empty=copy.deepcopy(brief);empty.pop('mode');check('mode stage asks only supported mode choice',validate_brief(empty,inp)['stage']=='mode')
empty=copy.deepcopy(brief);empty.pop('template_id');check('builtin template before missing settings',validate_brief(empty,inp)['stage']=='template')
empty=copy.deepcopy(brief)
for key in ['font_policy','font_size_policy','slide_count','writing_rules']:empty.pop(key)
check('missing four settings bundled',len(validate_brief(empty,inp)['missing_required'])==4)
check('no UI rendering invented',r['mode_menu_contract']['actually_rendered'] is False)
env=check_environment(brief,inp);check('supplied runtime and exact licensed font available',env['ok'])
actual=font_availability(brief,inp);check('both exact OFL font faces verified',len({f['sha256'] for f in actual['verified_faces']})==2)
missing=copy.deepcopy(brief);missing['font_policy']['values']['body']='SyntheticMissingFamily';check('effective font has no silent fallback',not font_availability(missing,inp)['ok'])
partial_env=os.environ.copy()
for key in ['CODEX_PRIMARY_RUNTIME_NODE','CODEX_PRIMARY_RUNTIME_NODE_MODULES','CODEX_PRIMARY_RUNTIME','CODEX_PRIMARY_RUNTIME_PYTHON']:partial_env.pop(key,None)
noenv=subprocess.run([sys.executable,str(scripts/'presentation_brief.py'),str(inp/'builtin.json'),'--check-environment'],cwd=root,env=partial_env,capture_output=True,text=True);check('missing supplied runtime is blocked without install/fallback',noenv.returncode!=0)
cli('template_gallery_chat_manifest_v2.py',['--source','github','--purpose','합성 클라우드 시작 검증','--output',inp/'manifest.json'])
manifest=json.loads((inp/'manifest.json').read_text());mainsha=manifest['source_commit'];check('live main snapshot is immutable',len(mainsha)==40)
preview=[]
for item in manifest['shortlist']:
 for source in item['previews']:
  raw=subprocess.check_output(['git','show',mainsha+':'+source['path']],cwd=root);preview.append({'path':source['path'],'sha256':hashlib.sha256(raw).hexdigest()})
check('real registered source previews resolve at pinned main',bool(preview))
cli('record_template_choice_v2.py',['deck:executive_boardroom','--source','github','--expected-source-commit',mainsha,'--preset','executive_brief','--confirmed','--direct-template','--purpose','SYNTHETIC registered selection audit, not real approval','--output',inp/'registered-selection.json'])
cli('record_template_choice_v2.py',['free','--source','github','--expected-source-commit',mainsha,'--preset','balanced_report','--confirmed','--direct-template','--purpose','SYNTHETIC existing free two-page fixture only','--output',inp/'selection.json'])
cli('record_template_choice_v2.py',['free','--source','github','--expected-source-commit','0'*40,'--preset','balanced_report','--confirmed','--direct-template','--output',inp/'must-not-record.json'],False)
outline={'slides':[{'title':'한글 장문·간격 검증','core_message':'합성 장문과 간격의 재현 검증','content_points':['기존 합성자료만 사용'],'visual_treatment':'Existing editable text fixture'},{'title':'긴 센터명·장문 표 검증','core_message':'합성 장문 native 표 재현 검증','content_points':['기존 합성자료만 사용'],'visual_treatment':'Existing native table fixture'}]}
approval=make_approval(outline,'SYNTHETIC fixture only; not actual user/storyline approval');(inp/'approval.json').write_text(json.dumps(approval,ensure_ascii=False,indent=2)+'\n')
cli('new_deck_init.py',['builtin_portable','--dir',work/'builtin','--template-selection-result',inp/'selection.json','--storyline-approval-result',inp/'approval.json','--design-brief',inp/'builtin.json'])
builtin=next((work/'builtin').glob('*builtin_portable*'));check('entry project records approved synthetic count2',json.loads((builtin/'storyline_approval.json').read_text())['requested_slide_count']==2)
shutil.copytree(original/'templates',builtin/'templates',dirs_exist_ok=True)
cli('template_preview_pptx.py',[builtin,'--visual-only','-o',builtin/'exports/candidate.pptx'])
# This is the explicit existing-template review exporter, not main production QA.
with zipfile.ZipFile(builtin/'exports/candidate.pptx') as a,zipfile.ZipFile(original/'review/korean-fit.pptx') as b:
 delta=[n for n in set(a.namelist())|set(b.namelist()) if n not in a.namelist() or n not in b.namelist() or a.read(n)!=b.read(n)]
check('builtin slide/design/table parts preserved; only creation timestamps vary',set(delta)<= {'docProps/core.xml'})
with zipfile.ZipFile(builtin/'exports/candidate.pptx') as a,zipfile.ZipFile(original/'review/korean-fit.pptx') as b:
 def stable_core(raw):
  tree=ET.fromstring(raw)
  for e in tree:
   if e.tag in ['{http://purl.org/dc/terms/}created','{http://purl.org/dc/terms/}modified']:e.text='<generation-time>'
  return ET.tostring(tree)
 check('builtin metadata differences limited to created/modified times',stable_core(a.read('docProps/core.xml'))==stable_core(b.read('docProps/core.xml')))
# Native custom path: standard workspace, copied input, separate current approval.
custom=Path(ProjectManager().init_project('custom_portable','ppt169',base_dir=str(work/'custom')))
fixture=root/'.claude/skills/ppt-master/examples/template_fidelity';cli('project_manager.py',['import-sources',custom,fixture/'sources/template-source.pptx','--copy'])
custombrief=copy.deepcopy(brief);custombrief.update(mode='custom',slide_count=6,font_policy={'basis':'source'},font_size_policy={'basis':'source'},writing_rules_policy='source');custombrief.pop('template_id');custombrief.pop('production_preset_id');custombrief.pop('writing_rules');custombrief['template_files']=['../sources/template-source.pptx'];custombrief=relocate(custombrief,custom/'analysis',inp)
# template path is a new project-relative input rather than the old root's value.
custombrief['template_files']=['../sources/template-source.pptx'];custombrief['content_text']='합성 6장 기존 native 원형/편집 검증';bp=custom/'analysis/design_brief.json';bp.write_text(json.dumps(custombrief,ensure_ascii=False,indent=2)+'\n')
cli('presentation_brief.py',[bp,'--check-environment','--planned-slide-count','6','--output',custom/'validation/intake.json'])
check('complete custom asks no builtin selection or duplicate inputs',json.loads((custom/'validation/intake.json').read_text())['question'] is None)
plan=json.loads((fixture/'fill_plan.json').read_text());plan.update(requested_slide_count=6,task_brief_sha256=hashlib.sha256(bp.read_bytes()).hexdigest());pp=custom/'analysis/fill_plan.json';pp.write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n')
lib=next((custom/'analysis').glob('*.slide_library.json'));cli('template_fill_pptx.py',['check-plan',lib,pp,'-o',custom/'validation/plan-check.json'])
cli('template_fill_pptx.py',['apply',custom/'sources/template-source.pptx',pp,'--design-brief',bp,'--transition','keep','-o',custom/'exports/candidate_20261007_000000.pptx'])
cli('template_fill_pptx.py',['validate',custom,'--design-brief',bp]);validated=json.loads((custom/'validation/validate_report.json').read_text());check('native exact readback and external approval binding pass',validated['summary']['error']==0 and validated['task_binding']['requested_slide_count']==6)
with zipfile.ZipFile(custom/'exports/candidate_20261007_000000.pptx') as a,zipfile.ZipFile(fixture/'review/filled.pptx') as b:
 delta=[n for n in set(a.namelist())|set(b.namelist()) if n not in a.namelist() or n not in b.namelist() or a.read(n)!=b.read(n)]
check('custom native reviewed ZIP parts preserved',not delta)
bad=copy.deepcopy(plan);bad.pop('task_brief_sha256');badpp=inp/'missing-hash-plan.json';badpp.write_text(json.dumps(bad));cli('template_fill_pptx.py',['apply',custom/'sources/template-source.pptx',badpp,'--design-brief',bp,'--transition','keep','-o',work/'must-not-create.pptx'],False)
bad=copy.deepcopy(plan);bad['requested_slide_count']=5;badpp=inp/'wrong-count-plan.json';badpp.write_text(json.dumps(bad));cli('template_fill_pptx.py',['apply',custom/'sources/template-source.pptx',badpp,'--design-brief',bp,'--transition','keep','-o',work/'must-not-create.pptx'],False)
check('sources and public font paths stay inside this checkout',all((inp/p).resolve().is_relative_to(root) for p in brief['font_files']))
result={'reviewed_head':BASE,'synthetic_only':True,'actual_user_approval':False,'actual_picker_rendered':False,'independent_67_pass':'reported by parent, not rerun here','checks':checks,'commands':cmds,'versions':versions,'python_version':sys.version.split()[0],'runtime_available':env['supplied_runtime'],'font_faces':actual['verified_faces'],'source_main_sha':mainsha,'registered_source_preview_count':len(preview),'preview_sources':preview,'builtin_project':str(builtin.relative_to(root)),'custom_project':str(custom.relative_to(root)),'limits':['Two checkout paths in one supplied Linux environment, not two real PCs','Builtin intake/selection/init plus existing review exporter, not full main SVG production workflow','OfficeCLI/PowerPoint unavailable; native application gate not certified','Actual host UI/private delivery/real company/private fonts not exercised']}
(work/'audit.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'root':str(root),'checks_passed':len(checks),'builtin':str(builtin.relative_to(root)),'custom':str(custom.relative_to(root))},ensure_ascii=False))
```

```bash
"$RUNTIME_NODE" "$PRESENTATIONS_SKILL/container_tools/mark_artifact_operation_started.mjs" --operation-kind edit --expected-output-count 2 --output-format pptx
"$RUNTIME_PYTHON" "$TASK_DIR/audit.py" "$TASK_DIR/repo"
```

다음 JavaScript를 `$TASK_DIR/finalize.mjs`로 저장한다. finalizer는 후보의 정확한 bytes를 다른 최종 경로에 복사하고 receipt를 쓴다. 공유 runtime 성공은 OfficeCLI/PowerPoint 검증 완료를 대신하지 않는다.

```javascript
import fs from 'node:fs/promises';
import path from 'node:path';
import crypto from 'node:crypto';
import {pathToFileURL} from 'node:url';
import {spawnSync} from 'node:child_process';
const [root,skill]=process.argv.slice(2);
const work=path.join(root,'projects/_smoke_cloud_portability');
const audit=JSON.parse(await fs.readFile(path.join(work,'audit.json'),'utf8'));
const {finalizePresentation}=await import(pathToFileURL(path.join(skill,'container_tools/artifact_tool_utils.mjs')).href);
const hash=async p=>crypto.createHash('sha256').update(await fs.readFile(p)).digest('hex');
const records=[];
for(const mode of ['builtin','custom']){
 const project=path.join(root,audit[`${mode}_project`]);
 const count=mode==='builtin'?2:6,charts=mode==='builtin'?[]:[2,3],tables=mode==='builtin'?[2]:[5,6];
 const candidate=path.join(project,'exports',mode==='builtin'?'candidate.pptx':'candidate_20261007_000000.pptx');
 const final=path.join(project,'deliverables/review-final.pptx');await fs.mkdir(path.dirname(final),{recursive:true});
 const fontPolicy=mode==='builtin'?{basis:'design',families:['Pretendard']}:{basis:'reference',families:['Pretendard'],referencePath:path.join(project,'sources/template-source.pptx'),referenceSha256:await hash(path.join(project,'sources/template-source.pptx'))};
 const receiptPath=path.join(project,'validation/shared-finalization.json');await fs.mkdir(path.dirname(receiptPath),{recursive:true});
 await finalizePresentation({workspaceDir:project,candidatePath:candidate,finalPath:final,pythonExecutable:process.env.RUNTIME_PYTHON,
 integrityValidatorPath:path.join(skill,'container_tools/inspect_presentation_package_integrity.py'),layoutValidatorPath:path.join(skill,'container_tools/inspect_presentation_layout_geometry.py'),
 explicitTotalSlideCount:count,requiredNativeChartOwnerSlides:charts,requiredNativeTableOwnerSlides:tables,requiredEmbeddedWorkbookChartOwnerSlides:charts,
 layoutArgs:['--expected-slide-size-emu','12192000,6858000','--validate-heading-fit',...tables.flatMap(i=>['--require-native-table-slide',String(i)])],fontPolicy,verifyArtifactToolImport:true,receiptPath});
 const profile=path.join(project,'validation/render-profile.json');
 await fs.writeFile(profile,JSON.stringify({slide_count:count,font_family:'Pretendard',font_files:['Regular','Bold'].map(s=>path.relative(path.dirname(profile),path.join(root,'.claude/skills/ppt-master/assets/fonts/Pretendard',`Pretendard-${s}.otf`)))},null,2));
 const render=path.join(project,'validation/shared-render');
 const proc=spawnSync(process.env.RUNTIME_NODE,[path.join(root,'.claude/skills/ppt-master/examples/korean_business/render_review.mjs'),final,render,profile,skill],{encoding:'utf8',env:process.env});
 if(proc.status!==0)throw new Error(proc.stderr||proc.stdout);
 records.push({mode,slide_count:count,final_sha256:await hash(final),candidate_bytes_preserved:(await hash(candidate))===(await hash(final)),finalization:JSON.parse(await fs.readFile(receiptPath,'utf8')),render_manifest:JSON.parse(await fs.readFile(path.join(render,'render-manifest.json'),'utf8'))});
}
await fs.writeFile(path.join(work,'shared-review.json'),JSON.stringify(records,null,2)+'\n');console.log(JSON.stringify({root,finalized_and_rendered:records.map(r=>({mode:r.mode,count:r.slide_count,sha256:r.final_sha256}))}));
```

```bash
"$RUNTIME_NODE" "$TASK_DIR/finalize.mjs" "$TASK_DIR/repo" "$PRESENTATIONS_SKILL"
```

출력은 `projects/_smoke_cloud_portability/audit.json`, `shared-review.json` 및 두 날짜 접두어 프로젝트의 validation/shared-render와 deliverables/review-final.pptx다. init 반환 경로를 사용한다. 날짜 접두어를 제거한 프로젝트 경로를 가정하지 않는다.

경로 이동 검토는 **다른 빈 checkout**에도 동일한 두 스크립트와 공급 runtime을 사용한다. 폰트/라이선스 경로는 코드가 각 brief 기준으로 다시 계산한다. audit.json의 checks 19개, exact readback, receipt의 fontSelection/package/layout/chart 통과, candidate bytes 보존, 전체 8개 렌더의 픽셀을 비교한다. 생성 시간이 다른 기본 PPTX는 docProps/core.xml의 created/modified만 달라질 수 있다. 이 외 차이는 원인을 확인한다.

단일 체크아웃에서 명령이 통과한 것과 다른 PC 검증은 구분한다. 운영 승인/사용자 확인/실제 native 앱 gate 없이 샘플 성공을 배포 승인으로 읽지 않는다. 다음 별도 리뷰 대상은 이 문서의 재현 명령과 검증 기록의 범위·비밀정보 미포함이며, 기능 기준 58a25ce의 재개발은 포함하지 않는다.

## 2026-10-07 후속 기본 SVG 정상 경로 검증

별도 [합성 1장 전체 경로 검증](../../.claude/skills/ppt-master/examples/cloud_entry/builtin_full_path/README.md)은 source 07c781d에서 design_spec/spec_lock, strict planning, 손작성 SVG page/full QA, 정상 svg_to_pptx, verify_deck와 지원 공유 finalization/render까지 실행했다. 위 2장 review exporter 근거와 구분한다. Planning 누락 경고는 없었다. live preview 실패, verify 내부 cached skip과 OfficeCLI/실제 사용자 UI·PowerPoint 미실행은 별도 기록했다. 기능/운영 변경을 의미하지 않는다.

### 기존 합성 프로젝트 미리보기 환경 후속 확인

[Flask 격리 환경 후속 근거](../../.claude/skills/ppt-master/examples/cloud_entry/builtin_full_path/preview_followup/README.md)는 source b832fe9에서 기존 선언 Flask를 공식 PyPI로 작업 전용 venv에 준비하고 post-export plain preview의 시작·브라우저 1장 표시·UI 종료를 확인했다. 공급 runtime 라이브러리를 읽고 global 환경은 수정하지 않았다. 당시 전체 생성 실행의 실패 기록은 유지하며 전체 생성/실제 승인/PowerPoint 검증 성공으로 확대하지 않는다.

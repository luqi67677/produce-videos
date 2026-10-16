// 核验调用契约、模式偏好、单次保存与拒绝冲突；不调用浏览器或真实项目写接口。
import assert from 'node:assert/strict';
import {execFileSync} from 'node:child_process';
import {readFileSync} from 'node:fs';
import vm from 'node:vm';
import {dirname} from 'node:path';
import {fileURLToPath} from 'node:url';

const scriptDir = dirname(fileURLToPath(import.meta.url));
const bundlePath = process.argv[2];
if (!bundlePath) throw new Error('用法：node test_frontend.mjs /absolute/path/to/index-DHqUZqg6.js');
const helper = execFileSync(process.env.PYTHON || 'python3', ['-c', 'import sys;sys.path.insert(0,sys.argv[1]);from frontend_patch import SYNC_HELPER;print(SYNC_HELPER)', scriptDir], {encoding:'utf8'});
const bundle = readFileSync(bundlePath,'utf8');
function nativeChunk(start,end) {
  const first = bundle.indexOf(start);
  const last = bundle.indexOf(end, first);
  assert(first >= 0 && last > first, '原生保存函数的版本不匹配');
  return bundle.slice(first,last);
}
const nativeSave = nativeChunk('async function yq(', 'const ROt=');

function harness(options={}) {
  const selected = options.selected ?? [{domId:'s02',sourceFile:'index.html',start:5,duration:5,track:0,compositionScope:'main'}];
  const elements = options.elements ?? [...selected,{domId:'caption',sourceFile:'index.html',start:0,duration:15,track:2,hidden:true},{domId:'audio',sourceFile:'index.html',start:0,duration:15,track:3,audioGroupHidden:true,volume:0}];
  const calls={requests:[],writes:[],edits:[],toasts:[],reload:0};
  let disk='BEFORE';
  const state={currentTime:12,duration:15,setSelectedElementId(value){this.selection=value;},setSelectedElementIds(value){this.selections=value;},setDuration(value){this.duration=value;},setCurrentTime(value){this.currentTime=value;}};
  const context={console,Set,Math,Number,JSON,Error,AggregateError,
    he:{getState:()=>state,setState:value=>Object.assign(state,value)},
    $I:(a,b)=>(a.sourceFile??'')===(b.sourceFile??'')&&(a.compositionScope??'')===(b.compositionScope??''),
    Va:(element,time)=>Math.max(0,time-(element.parentCompositionStart??0)),
    xa:element=>element.domId?{id:element.domId}:null,
    dMt:(path,target)=>path+'#'+target.id,NPe:element=>element.track,
    pMt:async()=> 'v1', Tn:(project,path)=>'/api/projects/'+project+path,
    Dt:async(url,init)=>{calls.requests.push({url,...JSON.parse(init.body)});return {ok:!options.error,status:options.error?409:200,json:async()=>options.error?{ok:false,error:options.error}:{ok:true,patch_id:options.patchId??'pv-sync-cut-1',path:'index.html',before:options.before??'BEFORE',after:'AFTER',duration:options.duration??10,stats:{}}};},
    Pd:async(write,paths,callback)=>callback(),r2:async()=>disk,
  };
  vm.createContext(context);
  vm.runInContext(nativeSave+helper,context);
  const pv={projectId:'fixture',activeCompPath:'index.html',selected,elements,
    writeProjectFile:async(path,after,expected)=>{assert.equal(expected,disk,'原生保存必须校核前文');calls.writes.push({path,after,expected});disk=after;},
    recordEdit:async(edit)=>{if(options.historyError)throw Error('history failure');calls.edits.push(edit);},
    showToast:(...values)=>calls.toasts.push(values),forceReloadSdkSession:()=>{},reloadPreview:()=>{calls.reload++;}
  };
  return {run:()=>context.pvSyncDelete1(pv),calls,state,get disk(){return disk;}};
}

const normal=harness();await normal.run();
assert.equal(normal.calls.writes.length,1);
assert.equal(normal.calls.edits.length,1);
assert.equal(normal.calls.edits[0].label,'全轨同步剪切');
assert.equal(normal.calls.edits[0].files['index.html'].before,'BEFORE');
assert.equal(normal.calls.edits[0].files['index.html'].after,'AFTER');
assert.equal(normal.calls.requests[0].targets.length,3,'隐藏与静音轨也必须提交');
assert.equal(normal.calls.reload,1);assert.equal(normal.state.duration,10);assert.equal(normal.state.currentTime,7);

const overlaps=harness({selected:[{domId:'a',sourceFile:'index.html',start:5,duration:5,track:0},{domId:'b',sourceFile:'index.html',start:8,duration:4,track:2}],duration:8});
await overlaps.run();assert.equal(JSON.stringify(overlaps.calls.requests[0].intervals),'[{"start":5,"end":12}]');

for(const options of [{before:'CONCURRENT CHANGE'},{patchId:'wrong-patch'},{error:'locked clip'},{duration:NaN}]) {
  const fixture=harness(options);await assert.rejects(fixture.run());assert.equal(fixture.calls.writes.length,0);assert.equal(fixture.calls.edits.length,0);assert.equal(fixture.calls.reload,0);
}
const across=harness({selected:[{domId:'a',sourceFile:'index.html',start:0,duration:5},{domId:'b',sourceFile:'child.html',start:5,duration:5}]});
await assert.rejects(across.run());assert.equal(across.calls.requests.length,0);assert.equal(across.calls.writes.length,0);

const rollback=harness({historyError:true});await assert.rejects(rollback.run());assert.equal(rollback.disk,'BEFORE');assert.equal(rollback.calls.writes.length,2);assert.equal(rollback.calls.reload,0);

console.log(JSON.stringify({ok:true,checks:['原生yq/bq单次写入和单条history','隐藏及静音轨入参','重叠时间区间合并','内容版本冲突拒绝写入','错误patch拒绝写入','后端拒绝时零写入','无效总时长拒绝写入','跨文件选择整单拒绝','history失败原生回滚'],count:9},null,2));

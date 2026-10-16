// 针对独立审查发现的解析遗漏，确认计算函数整单拒绝，且不修改输入快照。
// 用法：node test_backend_guards.mjs /absolute/path/to/backend-module.mjs
import assert from 'node:assert/strict';
import {pathToFileURL} from 'node:url';
import {resolve} from 'node:path';

if (!process.argv[2]) throw new Error('请传入导出 pvRangeCutPreviewHtml 的模块路径');
const {pvRangeCutPreviewHtml: fold} = await import(pathToFileURL(resolve(process.argv[2])).href);
assert.equal(typeof fold, 'function');
const common = 'const tl=gsap.timeline({paused:true});';
const end = 'window.__timelines={main:tl};';
const cases = [
  ['动态选择器', common+'tl.fromTo(window.selector,{x:0},{x:100,duration:10,ease:"none"},0);'+end, '', /动态|选择器/],
  ['延迟动画', common+'tl.fromTo("#a",{x:0},{x:100,duration:10,ease:"none",delay:2},0);'+end, '', /延迟/],
  ['第二条动画时间线', common+'const other=gsap.timeline({paused:true});other.fromTo("#a",{x:0},{x:100,duration:10,ease:"none"},0);'+end, '', /多条/],
  ['作用于合成祖先的动画', common+'tl.fromTo("#root",{x:0},{x:100,duration:10,ease:"none"},0);'+end, '', /祖先|父级|选择器|容器/],
  ['源播放速率非法', '', 'data-playback-rate="invalid"', /速率/],
  ['源媒体偏移非法', '', 'data-media-start="invalid"', /偏移|起点/],
];
const checks=[];
for (const [name,script,attributes,message] of cases) {
  const before=`<!doctype html><html><body><div id="root" data-composition-id="main" data-duration="15"><audio id="a" data-start="0" data-duration="15" ${attributes}></audio></div>${script?`<script>${script}</script>`:''}</body></html>`;
  const input={intervals:[{start:4,end:7}],targets:[{target:{id:'a'},originalId:'a',elementStart:0,elementDuration:15}]};
  const snapshot=JSON.stringify(input);
  await assert.rejects(()=>fold(before,input),message,name);
  assert.equal(JSON.stringify(input),snapshot,name+'不能修改输入');
  checks.push(name);
}
console.log(JSON.stringify({ok:true,count:checks.length,checks},null,2));

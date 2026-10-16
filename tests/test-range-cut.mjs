#!/usr/bin/env node
/**
 * 全轨范围删除的独立集成测试。
 * 用法：node test-range-cut.mjs --runtime <node_modules/hyperframes>
 *      [--module <含 pvRangeCutPreviewHtml 导出的临时模块>] [--report <结果.json>]
 * 只生成内存 HTML；不读取用户项目、素材，也不修改运行时或演示工程。
 * 使用 Hyperframes 的真实解析器和补丁函数。浏览器点击、持久化和 Undo 不由纯函数测试替代。
 */
import assert from 'node:assert/strict';
import { readFile, writeFile } from 'node:fs/promises';
import path from 'node:path';
import { pathToFileURL } from 'node:url';
import { createRequire } from 'node:module';
import { runInNewContext } from 'node:vm';

const options = {};
for (let i = 2; i < process.argv.length; i += 2) {
  const key = process.argv[i];
  if (!['--runtime', '--module', '--report'].includes(key) || !process.argv[i + 1]) {
    throw new Error('用法：node test-range-cut.mjs --runtime <目录> [--module <文件>] [--report <文件>]');
  }
  options[key.slice(2)] = path.resolve(process.argv[i + 1]);
}
assert.ok(options.runtime, '必须用 --runtime 指定 Hyperframes 包目录');
const runtime = options.runtime;
const packageInfo = JSON.parse(await readFile(path.join(runtime, 'package.json'), 'utf8'));
assert.equal(packageInfo.name, 'hyperframes');
assert.equal(packageInfo.version, '0.8.164', '该测试针对已核验的 0.8.164');
const load = (file) => import(pathToFileURL(path.join(runtime, 'dist', file)).href);
const [{ parseSourceDocument }, { parseGsapScriptAcorn }, patched] = await Promise.all([
  load('chunk-D5PUMG2P.js'),
  load('chunk-5CS4T6C6.js'),
  import(pathToFileURL(options.module ?? path.join(runtime, 'dist', 'chunk-CXVBPW5F.js')).href),
]);
const fold = patched.pvRangeCutPreviewHtml;
assert.equal(typeof fold, 'function', '模块必须导出 pvRangeCutPreviewHtml；未安装补丁时可用 --module 指定临时测试模块');
const requireRuntime = createRequire(path.join(runtime, 'package.json'));
const { gsap } = requireRuntime('gsap');

const cases = [];
const test = (name, run) => cases.push({ name, run });
const epsilon = 1e-6;
function near(actual, expected, message = '') {
  assert.ok(Number.isFinite(actual) && Math.abs(actual - expected) <= epsilon,
    `${message}: 期望 ${expected}，实际 ${actual}`);
}
function escapeAttr(value) {
  return String(value).replaceAll('&', '&amp;').replaceAll('"', '&quot;').replaceAll('<', '&lt;');
}
function fixture(clips, { duration = 15, script = '', rootExtra = '', extra = '' } = {}) {
  const html = clips.map((clip) => {
    const { id, start, duration: length, tag = 'div', track = 0, offset, rate, attrs = {}, text = id } = clip;
    const values = {
      id, 'data-test-group': id, 'data-start': start, 'data-duration': length,
      'data-track-index': track, ...attrs,
    };
    if (offset !== undefined) values[clip.offsetAttr ?? (tag === 'div' ? 'data-playback-start' : 'data-media-start')] = offset;
    if (rate !== undefined) values['data-playback-rate'] = rate;
    // 路径仅是未加载的测试标记，不包含真实素材。
    if (tag === 'audio' || tag === 'video') values.src = `fixture-${id}.wav`;
    const attributes = Object.entries(values).map(([key, value]) => `${key}="${escapeAttr(value)}"`).join(' ');
    return `<${tag} ${attributes}>${text}</${tag}>`;
  }).join('\n');
  const before = `<!doctype html><html><head><style>#visual{color:red}</style></head><body><div id="root" data-composition-id="main" data-width="1920" data-height="1080" data-duration="${duration}" ${rootExtra}>${html}${extra}</div>${script ? `<script>${script}</script>` : ''}</body></html>`;
  const targets = clips.map((clip) => ({
    target: { id: clip.id }, originalId: clip.id, elementStart: Number(clip.start),
    elementDuration: clip.duration, track: clip.track ?? 0,
    ...(clip.offset === undefined ? {} : { playbackStart: clip.offset }),
    ...(clip.rate === undefined ? {} : { playbackRate: clip.rate }),
  }));
  return { before, targets, duration };
}
async function cut(source, intervals, overrides = {}) {
  const result = await fold(source.before, {
    intervals, targets: source.targets, rootTarget: { id: 'root' }, ...overrides,
  }, 'acorn');
  assert.equal(typeof result.after, 'string');
  assert.deepEqual(result.skippedSelectors ?? [], [], '成功必须没有静默跳过的动画');
  return { ...result, document: parseSourceDocument(result.after).document };
}
function pieces(result, id) {
  return [...result.document.querySelectorAll(`[data-test-group="${id}"]`)].map((element) => ({
    id: element.id,
    start: Number(element.getAttribute('data-start')),
    duration: Number(element.getAttribute('data-duration')),
    offset: Number(element.getAttribute('data-playback-start') ?? element.getAttribute('data-media-start') ?? 0),
    rate: Number(element.getAttribute('data-playback-rate') ?? 1),
    track: Number(element.getAttribute('data-track-index')),
    element,
  })).sort((a, b) => a.start - b.start || a.offset - b.offset);
}
function expectPieces(result, id, expected) {
  const actual = pieces(result, id);
  assert.equal(actual.length, expected.length, `${id} 保留段数`);
  for (let i = 0; i < expected.length; i++) {
    for (const property of ['start', 'duration', 'offset', 'rate', 'track']) {
      if (expected[i][property] !== undefined) near(actual[i][property], expected[i][property], `${id}[${i}].${property}`);
    }
    assert.ok(actual[i].duration > 0, '不得保留零长或负长片段');
  }
  return actual;
}
function expectDuration(result, expected) {
  near(result.duration, expected, '返回的总时长');
  near(Number(result.document.getElementById('root').getAttribute('data-duration')), expected, '根总时长');
}
function expectUniqueIds(result) {
  for (const attribute of ['id', 'data-hf-id']) {
    const values = [...result.document.querySelectorAll(`[${attribute}]`)].map((el) => el.getAttribute(attribute));
    assert.equal(new Set(values).size, values.length, `${attribute} 不可重复`);
  }
}
async function expectRejected(source, intervals, overrides = {}, pattern = /./) {
  const saved = source.before;
  await assert.rejects(() => cut(source, intervals, overrides), pattern);
  assert.equal(source.before, saved, '失败不能改变输入快照');
}
function scripts(result) {
  return [...result.document.querySelectorAll('script')].map((node) => node.textContent).join('\n');
}
function sampleGsap(result, group, time, property = 'x') {
  // 将选择器映射到普通对象，由实际安装的 GSAP 求值，免去 DOM/CSS 插件。
  const states = new Map([...result.document.querySelectorAll('[id]')].map((element) => [element.id, { x: 0, y: 0, opacity: 1 }]));
  const timelines = [];
  const resolveTargets = (selector) => typeof selector === 'string'
    ? [...result.document.querySelectorAll(selector)].map((element) => states.get(element.id)) : selector;
  const api = { ...gsap,
    set: (selector, vars) => gsap.set(resolveTargets(selector), vars),
    timeline: (options) => {
      const timeline = gsap.timeline(options);
      for (const method of ['to', 'from', 'fromTo', 'set']) {
        const original = timeline[method].bind(timeline);
        timeline[method] = (selector, ...args) => original(resolveTargets(selector), ...args);
      }
      timelines.push(timeline);
      return timeline;
    },
  };
  try {
    runInNewContext(scripts(result), { gsap: api, window: {} }, { timeout: 1000 });
    assert.equal(timelines.length, 1, '测试 fixture 应只有一条 GSAP 时间线');
    timelines[0].seek(time, true);
    const visible = pieces(result, group).filter((piece) => time >= piece.start && time < piece.start + piece.duration);
    assert.equal(visible.length, 1, `${group} 在 ${time} 应只显示一个保留段`);
    return Number(states.get(visible[0].id)[property]);
  } finally {
    for (const timeline of timelines) timeline.kill();
    gsap.ticker.sleep();
  }
}

test('半开区间：完全在前、完全在后、完全覆盖、左相交、右相交、跨区间', async () => {
  const source = fixture([
    { id: 'before', start: 0, duration: 4 },
    { id: 'after', tag: 'audio', start: 7, duration: 4, offset: 3, track: 1 },
    { id: 'exact', start: 4, duration: 3 },
    { id: 'inside', start: 5, duration: 1 },
    { id: 'left', start: 2, duration: 3 },
    { id: 'right', tag: 'audio', start: 5, duration: 4, offset: 10, rate: 2, track: 2 },
    { id: 'span', tag: 'video', start: 2, duration: 10, offset: 10, rate: 2, track: 3 },
  ]);
  const result = await cut(source, [{ start: 4, end: 7 }]);
  expectPieces(result, 'before', [{ start: 0, duration: 4 }]);
  expectPieces(result, 'after', [{ start: 4, duration: 4, offset: 3, track: 1 }]);
  expectPieces(result, 'exact', []);
  expectPieces(result, 'inside', []);
  expectPieces(result, 'left', [{ start: 2, duration: 2 }]);
  expectPieces(result, 'right', [{ start: 4, duration: 2, offset: 14, rate: 2, track: 2 }]);
  expectPieces(result, 'span', [
    { start: 2, duration: 2, offset: 10, rate: 2 },
    { start: 4, duration: 5, offset: 20, rate: 2 },
  ]);
  expectDuration(result, 12);
  expectUniqueIds(result);
});

test('画面、字幕、旁白、音效、BGM 五轨同步，静音轨仍裁切', async () => {
  const clips = [
    { id: 'visual', tag: 'video', start: 0, duration: 15, track: 0 },
    { id: 'caption', start: 3, duration: 6, track: 1, text: '保留确认过的字幕。' },
    { id: 'voice', tag: 'audio', start: 3, duration: 6, offset: 8, track: 2 },
    { id: 'sfx', tag: 'audio', start: 5, duration: 1, track: 3 },
    { id: 'bgm', tag: 'audio', start: 0, duration: 15, track: 4, attrs: { muted: '', 'data-volume': '0' } },
  ];
  const result = await cut(fixture(clips), [{ start: 4, end: 7 }]);
  expectPieces(result, 'visual', [{ start: 0, duration: 4, offset: 0 }, { start: 4, duration: 8, offset: 7 }]);
  expectPieces(result, 'caption', [{ start: 3, duration: 1 }, { start: 4, duration: 2 }]);
  expectPieces(result, 'voice', [{ start: 3, duration: 1, offset: 8 }, { start: 4, duration: 2, offset: 12 }]);
  expectPieces(result, 'sfx', []);
  const bgm = expectPieces(result, 'bgm', [{ start: 0, duration: 4, offset: 0 }, { start: 4, duration: 8, offset: 7 }]);
  for (const part of bgm) assert.equal(part.element.getAttribute('data-volume'), '0');
  for (const part of pieces(result, 'caption')) assert.equal(part.element.textContent, '保留确认过的字幕。');
  expectDuration(result, 12);
});

test('未排序、重叠、相邻的删除区间先求并集，不能重复减时长', async () => {
  const source = fixture([{ id: 'bgm', tag: 'audio', start: 0, duration: 15 }]);
  const result = await cut(source, [{ start: 8, end: 10 }, { start: 4, end: 7 }, { start: 6, end: 9 }, { start: 10, end: 11 }]);
  expectPieces(result, 'bgm', [{ start: 0, duration: 4, offset: 0 }, { start: 4, duration: 4, offset: 11 }]);
  expectDuration(result, 8);
  near(result.stats.removedDuration, 7);
  assert.equal(result.stats.intervalCount, 1);
});

test('不相邻区间按原始时坐标处理，跨 BGM 拆三段且累计前移', async () => {
  const result = await cut(fixture([{ id: 'bgm', tag: 'audio', start: 0, duration: 15 }]), [{ start: 7, end: 9 }, { start: 2, end: 4 }]);
  expectPieces(result, 'bgm', [
    { start: 0, duration: 2, offset: 0 },
    { start: 2, duration: 3, offset: 4 },
    { start: 5, duration: 6, offset: 9 },
  ]);
  expectDuration(result, 11);
});

test('2 倍速跨多个区间：每个新段的素材偏移乘以速率', async () => {
  const result = await cut(fixture([{ id: 'voice', tag: 'audio', start: 0, duration: 15, offset: 5, rate: 2 }]), [{ start: 2, end: 4 }, { start: 7, end: 9 }]);
  expectPieces(result, 'voice', [
    { start: 0, duration: 2, offset: 5, rate: 2 },
    { start: 2, duration: 3, offset: 13, rate: 2 },
    { start: 5, duration: 6, offset: 23, rate: 2 },
  ]);
});

test('data-playback-start 优先且子合成沿用该字段', async () => {
  const source = fixture([{ id: 'scene', start: 2, duration: 10, offset: 3, rate: 2,
    attrs: { 'data-composition-src': 'fixture-scene.html', 'data-media-start': '100' } }]);
  const result = await cut(source, [{ start: 4, end: 7 }]);
  const parts = expectPieces(result, 'scene', [{ start: 2, duration: 2, offset: 3 }, { start: 4, duration: 5, offset: 13 }]);
  for (const part of parts) {
    assert.equal(part.element.getAttribute('data-composition-src'), 'fixture-scene.html');
    assert.ok(part.element.hasAttribute('data-playback-start'));
  }
});

test('同一子合成的多个实例只修改实例时间和偏移，素材引用不变', async () => {
  const source = fixture([
    { id: 'first', start: 0, duration: 8, offset: 1, attrs: { 'data-composition-src': 'shared-scene.html' } },
    { id: 'second', start: 8, duration: 7, offset: 3, track: 1, attrs: { 'data-composition-src': 'shared-scene.html' } },
  ]);
  const result = await cut(source, [{ start: 4, end: 7 }]);
  const all = [...expectPieces(result, 'first', [{ start: 0, duration: 4, offset: 1 }, { start: 4, duration: 1, offset: 8 }]),
    ...expectPieces(result, 'second', [{ start: 5, duration: 7, offset: 3 }])];
  for (const part of all) assert.equal(part.element.getAttribute('data-composition-src'), 'shared-scene.html');
});

test('头部与尾部裁切、恰好在边界上的片段不产生零长节点', async () => {
  const result = await cut(fixture([
    { id: 'head', tag: 'audio', start: 0, duration: 5, offset: 10 },
    { id: 'middle', start: 5, duration: 5 },
    { id: 'tail', tag: 'video', start: 10, duration: 5 },
  ]), [{ start: 0, end: 2 }, { start: 12, end: 15 }]);
  expectPieces(result, 'head', [{ start: 0, duration: 3, offset: 12 }]);
  expectPieces(result, 'middle', [{ start: 3, duration: 5 }]);
  expectPieces(result, 'tail', [{ start: 8, duration: 2 }]);
  expectDuration(result, 10);
});

test('保留原有尾部空白：根时长减删除长度，不按最后片段求最大值', async () => {
  const result = await cut(fixture([{ id: 'last', start: 7, duration: 6 }]), [{ start: 4, end: 7 }]);
  expectPieces(result, 'last', [{ start: 4, duration: 6 }]);
  expectDuration(result, 12);
});

test('毫秒边界无反向片段或累计漂移', async () => {
  const result = await cut(fixture([{ id: 'voice', tag: 'audio', start: 0, duration: 1.001 }], { duration: 1.001 }), [{ start: 0.1, end: 0.2 }, { start: 0.333, end: 0.667 }]);
  expectPieces(result, 'voice', [
    { start: 0, duration: 0.1, offset: 0 },
    { start: 0.1, duration: 0.133, offset: 0.2 },
    { start: 0.233, duration: 0.334, offset: 0.667 },
  ]);
  expectDuration(result, 0.567);
});

test('已链接音画的左右段分组分离，右段组仍一致', async () => {
  const attrs = { 'data-link': 'linked', 'data-sync-origin': 'origin' };
  const result = await cut(fixture([
    { id: 'visual', tag: 'video', start: 0, duration: 15, attrs },
    { id: 'voice', tag: 'audio', start: 0, duration: 15, track: 1, attrs },
  ]), [{ start: 4, end: 7 }]);
  const video = pieces(result, 'visual');
  const audio = pieces(result, 'voice');
  assert.equal(video.length, 2); assert.equal(audio.length, 2);
  const link = (part) => part.element.getAttribute('data-link');
  assert.ok(link(video[0]) && link(video[1]));
  assert.notEqual(link(video[0]), link(video[1]), '不能把右段继续链接在左段组');
  assert.equal(link(video[0]), link(audio[0]));
  assert.equal(link(video[1]), link(audio[1]));
  expectUniqueIds(result);
});

test('失败是事务边界：第二个目标缺失时没有部分成功结果', async () => {
  const source = fixture([{ id: 'good', start: 0, duration: 15 }]);
  await expectRejected(source, [{ start: 4, end: 7 }], { targets: [...source.targets,
    { target: { id: 'missing' }, originalId: 'missing', elementStart: 0, elementDuration: 15, track: 1 }] });
});

for (const [label, intervals] of [
  ['空列表', []], ['反向', [{ start: 7, end: 4 }]], ['零长', [{ start: 4, end: 4 }]],
  ['负起点', [{ start: -1, end: 4 }]], ['越过片尾', [{ start: 14, end: 16 }]],
  ['非有限数', [{ start: 4, end: Number.NaN }]], ['整片删除', [{ start: 0, end: 15 }]],
]) {
  test(`明确拒绝无效区间：${label}`, () => expectRejected(fixture([{ id: 'clip', start: 0, duration: 15 }]), intervals));
}

test('函数不改变输入快照和目标列表，历史层可保存完整 before/after', async () => {
  const source = fixture([{ id: 'bgm', tag: 'audio', start: 0, duration: 15 }]);
  const before = source.before;
  const input = structuredClone(source.targets);
  const result = await cut(source, [{ start: 4, end: 7 }]);
  assert.equal(source.before, before);
  assert.deepEqual(source.targets, input);
  assert.notEqual(result.after, before);
  // 纯函数没有历史栈。真实单步 Undo、CAS 和失败回滚由端点/UI 集成另验。
});

test('GSAP：删除区间之后的简单动画同步前移', async () => {
  const source = fixture([{ id: 'visual', start: 8, duration: 4 }], {
    script: `const tl = gsap.timeline({paused:true});\ntl.fromTo("#visual", {x:0}, {x:100,duration:2,ease:"none"}, 8);\nwindow.__timelines = {main:tl};`,
  });
  const result = await cut(source, [{ start: 4, end: 7 }]);
  expectPieces(result, 'visual', [{ start: 5, duration: 4 }]);
  const parsed = parseGsapScriptAcorn(scripts(result));
  assert.ok(parsed.animations.length > 0, '保留可解析的动画');
  // 同时检查真实解析器产物与脚本，避免只改 HTML 时间而遗漏动画。
  const positions = parsed.animations.map((animation) => animation.position ?? animation.start ?? animation.startTime);
  assert.ok(positions.some((position) => Number(position) === 5) || /,\s*5\s*\)/.test(scripts(result)),
    `动画需从 8 秒移到 5 秒：${JSON.stringify(parsed.animations)}`);
});

test('GSAP：跨删除区间拆分不允许静默跳过选择器', async () => {
  const source = fixture([{ id: 'visual', start: 0, duration: 15 }], {
    script: `const tl = gsap.timeline({paused:true});\ntl.fromTo("#visual", {x:0}, {x:150,duration:15,ease:"none"}, 0);\nwindow.__timelines = {main:tl};`,
  });
  const result = await cut(source, [{ start: 4, end: 7 }]);
  const parts = expectPieces(result, 'visual', [{ start: 0, duration: 4 }, { start: 4, duration: 8 }]);
  assert.ok(scripts(result).includes(`#${parts[1].id}`), '右段必须有自己的动画选择器');
  assert.deepEqual(result.skippedSelectors, []);
  for (const [time, expected] of [[2, 20], [4.001, 70.01], [8, 110], [11.5, 145]]) {
    near(sampleGsap(result, 'visual', time), expected, `GSAP 在新时间 ${time} 的 x`);
  }
});

test('GSAP：多个删除区间后的实际动画取值等于原时间的取值', async () => {
  const source = fixture([{ id: 'visual', start: 0, duration: 15 }], {
    script: `const tl = gsap.timeline({paused:true});\ntl.fromTo("#visual", {x:0}, {x:150,duration:15,ease:"none"}, 0);\nwindow.__timelines = {main:tl};`,
  });
  const result = await cut(source, [{ start: 2, end: 4 }, { start: 7, end: 9 }]);
  for (const [time, expected] of [[1, 10], [2.5, 45], [5.5, 95], [10.5, 145]]) {
    near(sampleGsap(result, 'visual', time), expected, `多区间 GSAP 在 ${time} 的 x`);
  }
});

test('源码中的隐藏或静音轨未出现在请求列表时仍自动同步', async () => {
  const source = fixture([
    { id: 'visual', start: 0, duration: 15 },
    { id: 'hidden', tag: 'audio', start: 0, duration: 15, track: 2, attrs: { muted: '', hidden: '', 'data-volume': 0 } },
  ]);
  const result = await cut(source, [{ start: 4, end: 7 }], { targets: [source.targets[0]] });
  expectPieces(result, 'hidden', [{ start: 0, duration: 4, offset: 0 }, { start: 4, duration: 8, offset: 7 }]);
});

test('受影响的锁定轨阻止整次修改，包括值为空的锁定属性', async () => {
  const source = fixture([
    { id: 'visual', start: 0, duration: 15 },
    { id: 'locked', tag: 'audio', start: 0, duration: 15, track: 2, attrs: { 'data-timeline-locked': '' } },
  ]);
  await expectRejected(source, [{ start: 4, end: 7 }]);
});

test('请求的时间与源码不一致时拒绝过期编辑', async () => {
  const source = fixture([{ id: 'visual', start: 0, duration: 15 }]);
  await expectRejected(source, [{ start: 4, end: 7 }], { targets: [{ ...source.targets[0], elementStart: 1 }] });
});

test('嵌套的定时父子节点拒绝同时位移，防止重复扣除', async () => {
  const source = fixture([{ id: 'parent', start: 0, duration: 15,
    text: '<div id="child" data-test-group="child" data-start="8" data-duration="4" data-track-index="1">Child</div>' }]);
  source.targets.push({ target: { id: 'child' }, originalId: 'child', elementStart: 8, elementDuration: 4, track: 1 });
  await expectRejected(source, [{ start: 4, end: 7 }]);
});

test('跨切口的裸 to 动画没有已知起始值时拒绝', async () => {
  const source = fixture([{ id: 'visual', start: 0, duration: 15 }], {
    script: `const tl = gsap.timeline({paused:true});\ntl.to("#visual", {opacity:0,duration:15,ease:"none"}, 0);\nwindow.__timelines = {main:tl};`,
  });
  await expectRejected(source, [{ start: 4, end: 7 }]);
});

test('GSAP：无法可靠切分的 repeat 动画明确拒绝', async () => {
  const source = fixture([{ id: 'visual', start: 0, duration: 15 }], {
    script: `const tl = gsap.timeline({paused:true});\ntl.to("#visual", {x:100,duration:2,repeat:-1}, 0);\nwindow.__timelines = {main:tl};`,
  });
  await expectRejected(source, [{ start: 4, end: 7 }]);
});

test('GSAP：跨切口的非线性 easing 不能按线性插值静默保存', async () => {
  const source = fixture([{ id: 'visual', start: 0, duration: 15 }], {
    script: `const tl = gsap.timeline({paused:true});\ntl.fromTo("#visual", {x:0}, {x:150,duration:15,ease:"power2.inOut"}, 0);\nwindow.__timelines = {main:tl};`,
  });
  await expectRejected(source, [{ start: 4, end: 7 }]);
});

test('GSAP：子元素选择器不能只复制父片段而遗漏子动画', async () => {
  const source = fixture([{ id: 'visual', start: 0, duration: 15, text: '<span class="child">Caption</span>' }], {
    script: `const tl = gsap.timeline({paused:true});\ntl.fromTo("#visual .child", {x:0}, {x:150,duration:15,ease:"none"}, 0);\nwindow.__timelines = {main:tl};`,
  });
  await expectRejected(source, [{ start: 4, end: 7 }]);
});

test('原生解析器为匿名漏轨补 hf-id 后仍纳入全轨裁切', async () => {
  const source = fixture([{ id: 'visual', start: 0, duration: 15 }], {
    extra: '<audio data-test-group="anonymous" data-start="0" data-duration="15" data-track-index="2" src="fixture-anonymous.wav"></audio>',
  });
  const result = await cut(source, [{ start: 4, end: 7 }]);
  const parts = expectPieces(result, 'anonymous', [{ start: 0, duration: 4, offset: 0 }, { start: 4, duration: 8, offset: 7 }]);
  for (const part of parts) assert.ok(part.element.getAttribute('data-hf-id'), '保留段需持久稳定标识');
  expectUniqueIds(result);
});

test('源码 duration 不是有限数字时拒绝客户端的旧时间覆盖', async () => {
  const source = fixture([{ id: 'visual', start: 0, duration: 15, attrs: { 'data-duration': 'unresolved' } }]);
  await expectRejected(source, [{ start: 4, end: 7 }]);
});

test('变速自动化无法按固定速率推导源偏移时明确拒绝', async () => {
  const source = fixture([{ id: 'voice', tag: 'audio', start: 0, duration: 15,
    attrs: { 'data-automation': '{"playbackRate":[{"time":0,"value":1},{"time":10,"value":2}]}' } }]);
  await expectRejected(source, [{ start: 4, end: 7 }]);
});

test('未经解析的相对 start 引用不可按 parseFloat 静默计算', async () => {
  const source = fixture([{ id: 'anchor', start: 0, duration: 3 }, { id: 'ref', start: 'anchor + 1', duration: 5 }]);
  // UI fallback 是已解析的 4；源表达式若本轮不支持，必须拒绝，而非把它写成 0。
  source.targets[1].elementStart = 4;
  await expectRejected(source, [{ start: 5, end: 7 }]);
});

for (const [label, script] of [
  ['动态选择器', 'const tl=gsap.timeline({paused:true});tl.fromTo(window.selector,{x:0},{x:100,duration:10,ease:"none"},0);window.__timelines={main:tl};'],
  ['延迟', 'const tl=gsap.timeline({paused:true});tl.fromTo("#visual",{x:0},{x:100,duration:10,delay:2,ease:"none"},0);window.__timelines={main:tl};'],
  ['多条时间线', 'const tl=gsap.timeline({paused:true});const other=gsap.timeline({paused:true});other.fromTo("#visual",{x:0},{x:100,duration:10,ease:"none"},0);window.__timelines={main:tl};'],
  ['根节点动画', 'const tl=gsap.timeline({paused:true});tl.fromTo("#root",{x:0},{x:100,duration:10,ease:"none"},0);window.__timelines={main:tl};'],
]) {
  test(`GSAP：${label}不会静默遗漏`, async () => {
    const source = fixture([{ id: 'visual', start: 0, duration: 15 }], { script });
    await expectRejected(source, [{ start: 4, end: 7 }]);
  });
}
for (const [attr, value] of [['data-fade-in', '2'], ['data-fade-out', '2'], ['loop', ''], ['data-loop', 'true'], ['data-fx-chain', '{}']]) {
  test(`音频跨边界时拒绝无法保留的 ${attr}`, async () => {
    const source = fixture([{ id: 'voice', tag: 'audio', start: 0, duration: 15, attrs: { [attr]: value } }]);
    await expectRejected(source, [{ start: 4, end: 7 }]);
  });
}
test('音频整片移动保留淡入淡出和循环属性', async () => {
  const source = fixture([{ id: 'voice', tag: 'audio', start: 8, duration: 4,
    attrs: { 'data-fade-in': 1, 'data-fade-out': 1, loop: '' } }]);
  const result = await cut(source, [{ start: 4, end: 7 }]);
  const [part] = expectPieces(result, 'voice', [{ start: 5, duration: 4 }]);
  assert.equal(part.element.getAttribute('data-fade-in'), '1');
  assert.equal(part.element.getAttribute('data-fade-out'), '1');
  assert.equal(part.element.hasAttribute('loop'), true);
});
for (const attr of ['data-playback-rate', 'data-media-start']) {
  test(`源 ${attr} 非法时拒绝客户端默认值`, async () => {
    const source = fixture([{ id: 'voice', tag: 'audio', start: 0, duration: 15, attrs: { [attr]: 'unresolved' } }]);
    await expectRejected(source, [{ start: 4, end: 7 }]);
  });
}

const results = [];
for (const item of cases) {
  const started = performance.now();
  try {
    await item.run();
    results.push({ name: item.name, passed: true, durationMs: Math.round(performance.now() - started) });
    console.log(`PASS ${item.name}`);
  } catch (error) {
    results.push({ name: item.name, passed: false, durationMs: Math.round(performance.now() - started), error: error.stack ?? String(error) });
    console.error(`FAIL ${item.name}\n${error.stack ?? error}`);
  }
}
const report = {
  runtimeVersion: packageInfo.version,
  scope: '真实 Hyperframes HTML/GSAP 解析器与范围删除函数集成；不包含浏览器操作、文件并发或历史栈',
  passed: results.filter((item) => item.passed).length,
  failed: results.filter((item) => !item.passed).length,
  total: results.length,
  results,
};
if (options.report) await writeFile(options.report, JSON.stringify(report, null, 2) + '\n');
console.log(`\n${report.passed}/${report.total} 通过，${report.failed} 失败。`);
process.exitCode = report.failed ? 1 : 0;

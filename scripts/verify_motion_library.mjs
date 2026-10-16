#!/usr/bin/env node
/** 数值、端点和乱序取帧验证；不渲染用户视频，不作为视觉或听感验收。 */
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {createMotionPreset, PRESET_DEFINITIONS, ENGINE_VERSIONS, LIBRARY_VERSION} from '../assets/motion-library/motion-presets.mjs';

const manifest = JSON.parse(await readFile(new URL('../assets/motion-library/library-manifest.json', import.meta.url), 'utf8'));
const close = (actual, expected) => assert.ok(Math.abs(actual - expected) < 1e-6, `${actual} 与 ${expected} 不一致`);
function finiteTree(value, path = 'snapshot') {
  if (typeof value === 'number') assert.ok(Number.isFinite(value), `${path} 含非有限值`);
  else if (Array.isArray(value)) value.forEach((item, i) => finiteTree(item, `${path}[${i}]`));
  else if (value && typeof value === 'object') for (const [key, item] of Object.entries(value)) finiteTree(item, `${path}.${key}`);
}
function readableLayers(start, middle, end) {
  const bounds = layer => ({
    minX: Math.min(...layer.polygon.map(point => point.x)), maxX: Math.max(...layer.polygon.map(point => point.x)),
    minY: Math.min(...layer.polygon.map(point => point.y)), maxY: Math.max(...layer.polygon.map(point => point.y)),
  });
  const rows = end.layers.map(bounds);
  assert.equal(start.layers.filter(layer => layer.labelOpacity > 0).length, 1, '收拢时只能显示顶层标签，避免文字重叠');
  assert.ok(end.layers.every(layer => layer.labelOpacity === 1), '完全展开后每层标签应可见');
  assert.ok(middle.layers.every(layer => layer.labelOpacity === 1), '中间帧应可辨认每层标签');
  for (let i = 1; i < rows.length; i += 1) {
    assert.ok(rows[i].minY - rows[i - 1].maxY > 0.025, '终点各层之间必须留出可见间隔');
    assert.ok(middle.layers[i].center.y - middle.layers[i - 1].center.y > 0.075, '中点相邻标签应有可读间距');
  }
  const occupiedWidth = Math.max(...rows.map(row => row.maxX)) - Math.min(...rows.map(row => row.minX));
  const occupiedHeight = Math.max(...rows.map(row => row.maxY)) - Math.min(...rows.map(row => row.minY));
  assert.ok(occupiedWidth > 0.48 && occupiedHeight > 0.48, '结构太小，未充分利用画幅');
}
function endpointChecks(id, start, middle, end) {
  if (id === 'title-reveal') { close(start.opacity, 0); close(end.opacity, 1); close(end.y, 0); assert.ok(middle.opacity > 0 && middle.opacity < 1); }
  else if (id === 'stagger-reveal') {
    assert.ok(start.items.every(item => item.opacity === 0));
    assert.ok(end.items.every(item => item.opacity === 1));
    assert.ok(middle.items[0].opacity > middle.items.at(-1).opacity);
  } else if (id === 'path-progress') { close(start.pathProgress, 0); close(end.pathProgress, 1); assert.deepEqual(start.position, start.path[0]); assert.deepEqual(end.position, end.path.at(-1)); }
  else if (id === 'task-transfer') { close(start.x, 0.16); close(end.x, 0.84); assert.ok(middle.y < start.y); }
  else if (id === 'camera-focus') {
    close(start.scale, 1); assert.ok(end.scale > start.scale); assert.ok(middle.scale > start.scale && middle.scale < end.scale);
    // 预览主体占 x=10%..90%、y=15%..85%；默认推近全程保留至少 4% 边距。
    for (const sample of [start, middle, end]) for (const x of [0.1, 0.9]) for (const y of [0.15, 0.85]) {
      const visibleX = (x - sample.anchorX) * sample.scale + sample.anchorX + sample.x;
      const visibleY = (y - sample.anchorY) * sample.scale + sample.anchorY + sample.y;
      assert.ok(visibleX >= 0.04 && visibleX <= 0.96 && visibleY >= 0.04 && visibleY <= 0.96, '默认聚焦裁切了预览主体安全区');
    }
  }
  else if (id === 'crossfade') { close(start.incoming, 0); close(end.incoming, 1); for (const sample of [start, middle, end]) close(sample.incoming + sample.outgoing, 1); }
  else if (id === 'background-pulse') { close(start.opacity, end.opacity); close(start.scale, end.scale); assert.ok(middle.opacity > start.opacity); assert.ok(middle.scale > start.scale); }
  else if (id === 'layers-explode') {
    close(start.spread, 0); close(end.spread, 1);
    const distance = sample => Math.hypot(sample.layers[0].center.x - sample.layers.at(-1).center.x, sample.layers[0].center.y - sample.layers.at(-1).center.y);
    assert.ok(distance(end) > distance(start));
    assert.equal(new Set(end.drawOrder).size, end.layers.length);
    readableLayers(start, middle, end);
    for (const sample of [start, middle, end]) for (const layer of sample.layers) for (const point of layer.polygon) assert.ok(point.x > 0 && point.x < 1 && point.y > 0 && point.y < 1, '结构投影超出归一化画幅');
  }
}

const results = [];
for (const definition of PRESET_DEFINITIONS) {
  const id = definition.id;
  let preset;
  try {
    const listed = manifest.effects.find(effect => effect.id === id);
    assert.ok(listed, 'manifest 缺少预设');
    for (const key of ['name', 'engine', 'version', 'default_duration_ms', 'parameters']) assert.deepEqual(listed[key], definition[key], `manifest ${key} 与实现不一致`);
    preset = createMotionPreset(id);
    const duration = preset.durationMs;
    const times = [0, duration * 0.25, duration * 0.5, duration * 0.75, duration];
    const expected = times.map(time => {
      const fresh = createMotionPreset(id);
      try { return fresh.seek(time); } finally { fresh.dispose(); }
    });
    // 回到相同时间，必须得到相同结果；不能依赖先前帧或播放方向。
    const order = [4, 0, 2, 1, 4, 3, 0, 2, 4, 0];
    for (const index of order) {
      const sample = preset.seek(times[index]);
      finiteTree(sample);
      assert.deepEqual(sample, expected[index], `乱序取样 ${times[index]}ms 与全新实例不一致`);
      assert.equal(preset.paused, true, '取样后不得开始自主播放');
    }
    endpointChecks(id, expected[0], expected[2], expected[4]);
    if (id === 'layers-explode') {
      for (const aspect of [0.75, 16 / 9]) {
        const variant = createMotionPreset(id, {parameters: {aspect}});
        try {
          const sample = variant.seek(variant.durationMs);
          close(sample.aspectRatio, aspect);
          finiteTree(sample);
          readableLayers(variant.seek(0), variant.seek(variant.durationMs / 2), sample);
          for (const layer of sample.layers) for (const point of layer.polygon) assert.ok(point.x > 0 && point.x < 1 && point.y > 0 && point.y < 1, '3:4 或 16:9 投影超出画幅');
          if (aspect > 1) {
            // 横幅相机距离相同：宽高比改变只改变横向投影比例，不能硬拉几何。
            for (let i = 0; i < sample.layers.length; i += 1) for (let j = 0; j < 4; j += 1) {
              close((sample.layers[i].polygon[j].x - 0.5) * aspect, (expected[4].layers[i].polygon[j].x - 0.5) * 1.6);
              close(sample.layers[i].polygon[j].y, expected[4].layers[i].polygon[j].y);
            }
          }
        } finally { variant.dispose(); }
      }
    }
    assert.deepEqual(preset.seekFrame(15, 30), preset.seek(500));
    assert.deepEqual(preset.seek(-1), expected[0]);
    assert.deepEqual(preset.seek(duration + 1), expected[4]);
    for (const value of [NaN, Infinity, -Infinity, '0', null]) assert.throws(() => preset.seek(value));
    assert.throws(() => preset.seekFrame(0, 0));
    assert.throws(() => preset.seekFrame(1.5, 30));
    assert.throws(() => createMotionPreset(id, {durationMs: Infinity}));
    assert.throws(() => createMotionPreset(id, {parameters: {unknown: 1}}));
    // 覆盖参数范围边界，避免默认值通过而合法输入产生坏坐标。
    for (const [key, spec] of Object.entries(definition.parameters)) {
      for (const value of [spec.min, spec.max]) {
        let parameters = {[key]: value};
        if (id === 'background-pulse' && key === 'minOpacity') parameters.maxOpacity = Math.max(value, definition.parameters.maxOpacity.default);
        if (id === 'background-pulse' && key === 'maxOpacity') parameters.minOpacity = Math.min(value, definition.parameters.minOpacity.default);
        const variant = createMotionPreset(id, {parameters});
        try { for (const time of [variant.durationMs, 0, variant.durationMs / 2]) finiteTree(variant.seek(time)); } finally { variant.dispose(); }
      }
      assert.throws(() => createMotionPreset(id, {parameters: {[key]: NaN}}));
    }
    preset.dispose();
    assert.throws(() => preset.seek(0));
    results.push({effectId: id, passed: true, details: '真实引擎运行；端点/中点、10 次乱序回取、逐帧入口、参数边界、非有限输入与暂停状态通过。未执行成片或视觉验收。'});
  } catch (error) {
    results.push({effectId: id, passed: false, details: error.message});
  } finally { preset?.dispose(); }
}
const globalChecks = [];
try {
  assert.equal(manifest.schema_version, '1.0');
  assert.equal(manifest.effects.length, PRESET_DEFINITIONS.length);
  assert.equal(new Set(manifest.effects.map(effect => effect.id)).size, PRESET_DEFINITIONS.length);
  assert.throws(() => createMotionPreset('missing'));
  assert.throws(() => createMotionPreset('title-reveal', null));
  globalChecks.push({name: 'manifest 与非法入口', passed: true});
} catch (error) { globalChecks.push({name: 'manifest 与非法入口', passed: false, details: error.message}); }

const passed = results.every(item => item.passed) && globalChecks.every(item => item.passed);
process.stdout.write(`${JSON.stringify({schema_version: '1.0', version: LIBRARY_VERSION, engineVersions: ENGINE_VERSIONS, passed, effects: results, checks: globalChecks, scope: '本地数值实现验证；不包含用户成片、浏览器视觉或声音验收。'}, null, 2)}\n`);
process.exitCode = passed ? 0 : 1;

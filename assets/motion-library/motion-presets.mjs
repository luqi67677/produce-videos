/** 本地数值动效。只接受外部时间；不创建自主播放或第二条时间线。 */
import {animate, stagger} from './vendor/animejs/anime.esm.js';
import {Matrix4, PerspectiveCamera, Vector3, REVISION} from './vendor/three/three.core.js';

export const LIBRARY_VERSION = '1.0.0';
export const ENGINE_VERSIONS = Object.freeze({animejs: '4.5.0', three: '0.186.1', threeRevision: REVISION});

const number = (description, value, min, max, integer = false) => ({
  type: integer ? 'integer' : 'number', default: value, min, max, description,
});

export const PRESET_DEFINITIONS = Object.freeze([
  {
    id: 'title-reveal', name: '标题显现', engine: 'animejs', version: '4.5.0',
    purpose: '新章节或核心结论进入时，短距离上移并显现。', default_duration_ms: 650,
    parameters: {offsetY: number('起始纵向偏移，占画面高度的比例。', 0.06, 0, 0.15), startScale: number('起始缩放。', 0.98, 0.9, 1)},
    limits: ['只控制整体字块，不拆汉字、不改原文。', '字号、换行和安全区由排版层核验；不保证长标题自动适配。'],
  },
  {
    id: 'stagger-reveal', name: '逐项显现', engine: 'animejs', version: '4.5.0',
    purpose: '按讲解顺序展示清单、成员或处理步骤。', default_duration_ms: 1200,
    parameters: {count: number('元素数。', 4, 1, 8, true), offsetY: number('起始纵向偏移。', 0.06, 0, 0.15), staggerFraction: number('首项与末项的启动间隔占总时长的比例。', 0.4, 0, 0.8)},
    limits: ['元素顺序由导演计划给定。', '只控制可见性和位移；不表示任务依赖已完成。'],
  },
  {
    id: 'path-progress', name: '路径推进', engine: 'animejs', version: '4.5.0',
    purpose: '沿折线路径呈现数据或任务的流动方向。', default_duration_ms: 1000,
    parameters: {startX: number('路径起点横坐标。', 0.12, 0.05, 0.3), endX: number('路径终点横坐标。', 0.88, 0.7, 0.95)},
    limits: ['输出归一化路径、路径比例和当前位置，须由画面绘制。', '同一段推进不自动代表授权、同步或完成。'],
  },
  {
    id: 'task-transfer', name: '任务传递', engine: 'animejs', version: '4.5.0',
    purpose: '把同一个任务标记从发送者移动到接收者。', default_duration_ms: 1000,
    parameters: {arcHeight: number('弧线最大抬升。', 0.14, 0, 0.25)},
    limits: ['只表达一个标记的转移，接收关系需配节点名称。', '控制权移交与子任务派发必须使用不同文案和状态。'],
  },
  {
    id: 'camera-focus', name: '镜头聚焦', engine: 'animejs', version: '4.5.0',
    purpose: '轻推近并平移到当前讲解对象，保留连续镜头。', default_duration_ms: 1600,
    parameters: {zoom: number('结束缩放。', 1.1, 1, 1.25), panX: number('结束横向平移。', -0.015, -0.1, 0.1), panY: number('结束纵向平移。', 0, -0.1, 0.1)},
    limits: ['以画面中心缩放，输出的是数值变换。', '不能自动识别人脸或补齐画外内容；使用者须核验主体安全区。'],
  },
  {
    id: 'crossfade', name: '叠化转场', engine: 'animejs', version: '4.5.0',
    purpose: '在几何位置固定的两个图层之间柔和交接。', default_duration_ms: 450,
    parameters: {},
    limits: ['输出互补权重，合成器须按权重混合两幅完整画面。', '不能修复不同人物位置或构图造成的视觉跳动；应先对齐构图。'],
  },
  {
    id: 'background-pulse', name: '背景轻呼吸', engine: 'animejs', version: '4.5.0',
    purpose: '背景强调区缓慢明暗一次，辅助当前信息显现。', default_duration_ms: 2400,
    parameters: {minOpacity: number('最低不透明度。', 0.04, 0, 0.12), maxOpacity: number('最高不透明度。', 0.1, 0.01, 0.2), maxScale: number('最大缩放。', 1.025, 1, 1.05)},
    limits: ['只执行一次呼吸，不自动循环。', '避免闪烁、抢字幕、遮挡人物；无表达需要时用静态背景。'],
  },
  {
    id: 'layers-explode', name: '分层立体展开', engine: 'animejs+three', version: '4.5.0+0.186.1',
    purpose: '把叠在一起的结构层拉开，解释层与层之间的关系。', default_duration_ms: 1500,
    parameters: {count: number('结构层数。', 3, 2, 6, true), gap: number('展开后的纵向层间距，世界坐标单位。', 1.05, 0.8, 1.4), tiltX: number('水平轴倾角，弧度。', 0.3, 0.15, 0.5), tiltY: number('纵轴倾角，弧度。', -0.28, -0.5, -0.12), aspect: number('目标画幅宽高比；3:4 为 0.75，16:9 为 16/9。', 1.6, 0.5, 2.4)},
    limits: ['Three.js 相机和矩阵生成二维投影，可交给 Canvas 或 SVG 绘制；绘图区宽高比必须等于 aspect。', '属于分层图解，不是完整 WebGL 产品建模、光照、材质或交互系统。', '层的语义由文案负责，不能把概念分层宣称为实际存储架构。'],
  },
]);

function finite(value, name) {
  if (typeof value !== 'number' || !Number.isFinite(value)) throw new TypeError(`${name} 必须是有限数值`);
  return value;
}

function validateParameters(definition, supplied) {
  if (!supplied || typeof supplied !== 'object' || Array.isArray(supplied)) throw new TypeError('parameters 必须是对象');
  for (const key of Object.keys(supplied)) {
    if (!Object.hasOwn(definition.parameters, key)) throw new TypeError(`不支持参数：${key}`);
  }
  const result = {};
  for (const [key, spec] of Object.entries(definition.parameters)) {
    const value = finite(supplied[key] ?? spec.default, key);
    if (value < spec.min || value > spec.max || (spec.type === 'integer' && !Number.isInteger(value))) {
      throw new RangeError(`${key} 必须为 ${spec.min} 到 ${spec.max} 之间的${spec.type === 'integer' ? '整数' : '数值'}`);
    }
    result[key] = value;
  }
  if (definition.id === 'background-pulse' && result.maxOpacity < result.minOpacity) throw new RangeError('最高不透明度不能低于最低不透明度');
  return result;
}

function samplePolyline(points, progress) {
  const lengths = points.slice(1).map((p, i) => Math.hypot(p.x - points[i].x, p.y - points[i].y));
  const total = lengths.reduce((a, b) => a + b, 0);
  let distance = progress * total;
  for (let i = 0; i < lengths.length; i += 1) {
    if (distance <= lengths[i] || i === lengths.length - 1) {
      const t = Math.max(0, Math.min(1, distance / lengths[i]));
      return {x: points[i].x + (points[i + 1].x - points[i].x) * t, y: points[i].y + (points[i + 1].y - points[i].y) * t};
    }
    distance -= lengths[i];
  }
}

/** 建立暂停状态的预设；seek 的时间来自主 EDL，不会自行计时。 */
export function createMotionPreset(effectId, options = {}) {
  const definition = PRESET_DEFINITIONS.find(item => item.id === effectId);
  if (!definition) throw new RangeError(`未知动效：${String(effectId)}`);
  if (!options || typeof options !== 'object' || Array.isArray(options)) throw new TypeError('options 必须是对象');
  for (const key of Object.keys(options)) if (!['durationMs', 'parameters'].includes(key)) throw new TypeError(`不支持选项：${key}`);
  const durationMs = finite(options.durationMs ?? definition.default_duration_ms, 'durationMs');
  if (durationMs < 1 || durationMs > 600000) throw new RangeError('durationMs 必须在 1 到 600000 之间');
  const p = validateParameters(definition, options.parameters ?? {});
  let animation;
  let getValues;
  let disposed = false;
  const tween = (target, values, settings = {}) => animate(target, {
    ...values, duration: durationMs, ease: 'outCubic', ...settings, autoplay: false, composition: 'none',
  });

  if (effectId === 'title-reveal') {
    const value = {opacity: 0, y: p.offsetY, scale: p.startScale};
    animation = tween(value, {opacity: [0, 1], y: [p.offsetY, 0], scale: [p.startScale, 1]});
    getValues = () => ({opacity: value.opacity, y: value.y, scale: value.scale});
  } else if (effectId === 'stagger-reveal') {
    const items = Array.from({length: p.count}, () => ({opacity: 0, y: p.offsetY}));
    const spread = p.count === 1 ? 0 : durationMs * p.staggerFraction;
    animation = tween(items, {opacity: [0, 1], y: [p.offsetY, 0]}, {
      duration: durationMs - spread, delay: stagger(p.count === 1 ? 0 : spread / (p.count - 1)),
    });
    getValues = () => ({items: items.map((item, index) => ({index, opacity: item.opacity, y: item.y}))});
  } else if (effectId === 'path-progress') {
    const value = {pathProgress: 0};
    const path = [{x: p.startX, y: 0.68}, {x: 0.45, y: 0.68}, {x: 0.45, y: 0.32}, {x: p.endX, y: 0.32}];
    animation = tween(value, {pathProgress: [0, 1]}, {ease: 'linear'});
    getValues = () => ({pathProgress: value.pathProgress, dashOffset: 1 - value.pathProgress, path: path.map(point => ({...point})), position: samplePolyline(path, value.pathProgress)});
  } else if (effectId === 'task-transfer') {
    const value = {transferProgress: 0};
    animation = tween(value, {transferProgress: [0, 1]}, {ease: 'inOutCubic'});
    getValues = () => ({transferProgress: value.transferProgress, x: 0.16 + 0.68 * value.transferProgress, y: 0.54 - 4 * p.arcHeight * value.transferProgress * (1 - value.transferProgress)});
  } else if (effectId === 'camera-focus') {
    const value = {x: 0, y: 0, scale: 1};
    animation = tween(value, {x: [0, p.panX], y: [0, p.panY], scale: [1, p.zoom]}, {ease: 'inOutSine'});
    getValues = () => ({x: value.x, y: value.y, scale: value.scale, anchorX: 0.5, anchorY: 0.5});
  } else if (effectId === 'crossfade') {
    const value = {outgoing: 1, incoming: 0};
    animation = tween(value, {outgoing: [1, 0], incoming: [0, 1]}, {ease: 'linear'});
    getValues = () => ({outgoing: value.outgoing, incoming: value.incoming});
  } else if (effectId === 'background-pulse') {
    // Anime 只驱动一个绝对相位，避免多段属性竞争在倒放时留下前一帧的值。
    const value = {phase: 0};
    animation = tween(value, {phase: [0, 1]}, {ease: 'linear'});
    getValues = () => {
      const strength = Math.sin(Math.PI * value.phase) ** 2;
      return {opacity: p.minOpacity + (p.maxOpacity - p.minOpacity) * strength, scale: 1 + (p.maxScale - 1) * strength};
    };
  } else if (effectId === 'layers-explode') {
    const value = {spread: 0};
    animation = tween(value, {spread: [0, 1]}, {ease: 'inOutSine'});
    const rotation = new Matrix4().makeRotationY(p.tiltY).multiply(new Matrix4().makeRotationX(p.tiltX));
    const corners = [[-1.7, -0.36], [1.7, -0.36], [1.7, 0.36], [-1.7, 0.36]];
    const middle = (p.count - 1) / 2;
    const matrixAt = (index, spread) => new Matrix4().makeTranslation(
      0, (middle - index) * p.gap * spread, (index - middle) * 0.07,
    ).multiply(rotation);
    // 根据终点完整结构固定取景；展开途中不缩放相机，也不按画幅拉伸几何。
    const fullPoints = Array.from({length: p.count}, (_, index) => corners.map(([x, y]) => new Vector3(x, y, 0).applyMatrix4(matrixAt(index, 1)))).flat();
    const maxX = Math.max(...fullPoints.map(point => Math.abs(point.x)));
    const maxY = Math.max(...fullPoints.map(point => Math.abs(point.y)));
    const maxZ = Math.max(...fullPoints.map(point => point.z));
    const field = Math.tan(45 * Math.PI / 360);
    const distance = maxZ + Math.max(maxY / field, maxX / (field * p.aspect)) / 0.84;
    const camera = new PerspectiveCamera(45, p.aspect, 0.1, 50);
    camera.position.set(0, 0, distance);
    camera.lookAt(0, 0, 0);
    camera.updateMatrixWorld(true);
    camera.updateProjectionMatrix();
    getValues = () => {
      const layers = Array.from({length: p.count}, (_, index) => {
        const matrix = matrixAt(index, value.spread);
        const centerWorld = new Vector3(0, 0, 0).applyMatrix4(matrix);
        const project = vector => {
          const projected = vector.project(camera);
          return {x: (projected.x + 1) / 2, y: (1 - projected.y) / 2};
        };
        return {index, depth: centerWorld.z, labelOpacity: index === p.count - 1 ? 1 : Math.max(0, Math.min(1, (value.spread - 0.15) / 0.3)), center: project(centerWorld.clone()), polygon: corners.map(([x, y]) => project(new Vector3(x, y, 0).applyMatrix4(matrix)))};
      });
      return {spread: value.spread, aspectRatio: p.aspect, layers, drawOrder: [...layers].sort((a, b) => a.depth - b.depth).map(layer => layer.index)};
    };
  }

  const seek = timeMs => {
    if (disposed) throw new Error('动效已释放，不能继续取帧');
    const clamped = Math.max(0, Math.min(durationMs, finite(timeMs, 'timeMs')));
    animation.seek(clamped, true);
    return {effectId, timeMs: clamped, progress: clamped / durationMs, ...getValues()};
  };
  return Object.freeze({
    id: effectId, durationMs, parameters: Object.freeze({...p}),
    get paused() { return animation.paused; },
    seek,
    seekFrame(frame, fps = 30) {
      finite(frame, 'frame'); finite(fps, 'fps');
      if (!Number.isInteger(frame) || frame < 0) throw new RangeError('frame 必须是非负整数');
      if (fps <= 0 || fps > 1000) throw new RangeError('fps 必须大于 0 且不超过 1000');
      return seek(frame / fps * 1000);
    },
    dispose() { if (!disposed) animation.cancel(); disposed = true; },
  });
}

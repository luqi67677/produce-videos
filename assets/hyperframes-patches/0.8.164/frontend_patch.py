"""Hyperframes 0.8.164 前端补丁转换器；仅返回新源码，不修改安装包。"""

from __future__ import annotations

import argparse
from pathlib import Path

PATCH_ID = "pv-sync-cut-1"

# 复用 Studio 原生 yq：每次动作只保存一次、只记录一条撤销。
SYNC_HELPER = r'''
/* pv-sync-cut-1: 全轨同步剪切 */
async function pvSyncDelete1(pv) {
  const state = he.getState();
  const activePath = pv.activeCompPath || "index.html";
  const selected = pv.selected;
  if (!selected.length) return;
  const fileOf = element => element.sourceFile || activePath;
  const path = fileOf(selected[0]);
  if (selected.some(element => fileOf(element) !== path || !$I(element, selected[0]))) {
    throw new Error("全轨同步剪切需要在同一个场景时间线内选择片段；本次未保存任何修改。");
  }
  if (path !== activePath) {
    throw new Error("请先进入该子场景的时间线，再执行全轨同步剪切；本次未保存任何修改。");
  }
  const rawIntervals = selected.map(element => ({
    start: Va(element, element.start),
    end: Va(element, element.start) + element.duration
  }));
  if (rawIntervals.some(range => !Number.isFinite(range.start) || !Number.isFinite(range.end) || range.end <= range.start)) {
    throw new Error("选中片段的时间无效，本次未保存任何修改。");
  }
  rawIntervals.sort((a, b) => a.start - b.start || a.end - b.end);
  const intervals = [];
  for (const range of rawIntervals) {
    const previous = intervals[intervals.length - 1];
    if (previous && range.start <= previous.end + 1e-7) previous.end = Math.max(previous.end, range.end);
    else intervals.push({start: range.start, end: range.end});
  }
  const seen = new Set();
  const targets = [];
  for (const element of pv.elements.filter(element => fileOf(element) === path)) {
    if (!Number.isFinite(element.start) || !Number.isFinite(element.duration) || element.duration <= 0) continue;
    const target = xa(element);
    if (!target) throw new Error("当前时间线存在无法安全修改的片段，本次未保存任何修改。");
    const key = dMt(path, target);
    if (seen.has(key)) continue;
    seen.add(key);
    targets.push({
      target,
      ...(element.domId ? {originalId: element.domId} : {}),
      elementStart: Va(element, element.start),
      elementDuration: element.duration,
      ...(element.playbackStart != null ? {playbackStart: element.playbackStart} : {}),
      ...(element.playbackRate != null ? {playbackRate: element.playbackRate} : {}),
      track: NPe(element),
      timelineLocked: !!element.timelineLocked
    });
  }
  if (!targets.length) throw new Error("当前场景没有可剪切的轨道，本次未保存任何修改。");
  let preview;
  const changed = await yq({
    projectId: pv.projectId,
    path,
    label: "全轨同步剪切",
    writeFile: pv.writeProjectFile,
    recordEdit: pv.recordEdit,
    rewrite: async before => {
      const expectedVersion = await pMt(pv.projectId, path);
      const response = await Dt(Tn(pv.projectId, "/file-mutations/range-cut-preview"), {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({path, expectedVersion, intervals, targets})
      });
      const result = await response.json().catch(() => null);
      if (!response.ok || result?.ok !== true) {
        throw new Error(result?.error || `全轨同步剪切计算失败（${response.status}），本次未保存任何修改。`);
      }
      if (result.patch_id !== "pv-sync-cut-1" || result.path !== path || result.before !== before || typeof result.after !== "string") {
        throw new Error("工作台版本或文件内容已变化，本次未保存任何修改。刷新后重试。");
      }
      if (!Number.isFinite(result.duration) || result.duration < 0) {
        throw new Error("剪切后的总时长无效，本次未保存任何修改。");
      }
      preview = result;
      return {disk: before, after: result.after};
    }
  });
  if (!changed || preview.after === preview.before) {
    pv.showToast("所选时间段没有可剪切的内容。", "info");
    return;
  }
  const nextState = he.getState();
  nextState.setSelectedElementId(null);
  nextState.setSelectedElementIds(new Set());
  he.setState({rangeSelection: null, isPlaying: false});
  nextState.setDuration(preview.duration);
  const previousTime = state.currentTime;
  const removedBeforePlayhead = intervals.reduce((sum, range) => sum + Math.max(0, Math.min(previousTime, range.end) - range.start), 0);
  nextState.setCurrentTime(Math.max(0, Math.min(preview.duration, previousTime - removedBeforePlayhead)));
  try {
    pv.forceReloadSdkSession?.();
    pv.reloadPreview();
  } catch {
    pv.showToast("全轨剪切已保存，预览刷新失败。请刷新页面；Cmd+Z 可撤销。", "info");
    return;
  }
  pv.showToast("已同步剪切画面、字幕和声音，并收拢后续时间。Cmd+Z 可一次撤销。", "info");
}
'''


def _once(source: str, before: str, after: str, name: str) -> str:
    count = source.count(before)
    if count != 1:
        raise ValueError(f"{name}: 预期 1 个匹配，实际 {count} 个；拒绝修改不匹配版本")
    return source.replace(before, after, 1)


def patch(source: str) -> str:
    """只适配已核验的 0.8.164 bundle；任何锚点不符都整次失败。"""
    if "/* pv-sync-cut-1:" in source:
        raise ValueError("前端已包含 pv-sync-cut-1；请由安装器处理幂等检查")

    source = _once(
        source,
        'typeof r.rippleEditEnabled=="boolean"&&(i.rippleEditEnabled=r.rippleEditEnabled),',
        'typeof r.rippleEditEnabled=="boolean"&&(i.rippleEditEnabled=r.rippleEditEnabled),typeof r.pvSyncCutEnabled=="boolean"&&(i.pvSyncCutEnabled=r.pvSyncCutEnabled),',
        "新增独立模式偏好",
    )
    source = _once(
        source,
        'rippleEditEnabled:ua().rippleEditEnabled??!0,setRippleEditEnabled:n=>{Na({rippleEditEnabled:n}),e({rippleEditEnabled:n})}',
        'rippleEditEnabled:ua().pvSyncCutEnabled??!0,setRippleEditEnabled:n=>{Na({pvSyncCutEnabled:n}),e({rippleEditEnabled:n})}',
        "全轨同步默认开启",
    )
    source = _once(source, "function UMt(", SYNC_HELPER + "\nfunction UMt(", "注入同步剪切保存函数")
    source = _once(
        source,
        'try{const E=aC("main-track-ripple-delete"),k="Delete timeline clip";',
        'try{if(he.getState().rippleEditEnabled){await pvSyncDelete1({projectId:b,activeCompPath:t,elements:n,selected:g,writeProjectFile:i,recordEdit:s,reloadPreview:o,forceReloadSdkSession:l,showToast:r});return}const E=aC("main-track-ripple-delete"),k="Delete timeline clip";',
        "删除动作全轨分支",
    )
    source = _once(
        source,
        'N=Uwt(M,C,he.getState().rippleEditEnabled),',
        'N=null,',
        "关闭旧主轨单独收拢",
    )
    source = _once(
        source,
        'y.jsx(Tr,{label:h?"Ripple on: keeps the main track gapless":"Ripple off: deleting a main-track clip leaves a gap",children:y.jsx("button",{type:"button",onClick:()=>p(!h),"aria-label":"Toggle ripple edit","aria-pressed":h,className:h?k8:ih,children:y.jsx(q1n,{size:16})})})',
        'y.jsx(Tr,{label:h?"全轨同步：删除所选时间段，画面、字幕和声音一起收拢":"仅删所选：删除选中片段，保留其他轨道时间",children:y.jsxs("button",{type:"button",onClick:()=>p(!h),"aria-label":h?"全轨同步":"仅删所选","aria-pressed":h,"data-pv-sync-cut":"pv-sync-cut-1",className:h?k8:ih,style:{width:"auto",padding:"0 8px",gap:"4px",flexShrink:0},children:[y.jsx(q1n,{size:16}),y.jsx("span",{style:{fontSize:"11px",whiteSpace:"nowrap"},children:h?"全轨同步":"仅删所选"})]})})',
        "可见中文模式切换",
    )
    return source


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    if args.source.resolve() == args.output.resolve():
        parser.error("拒绝覆盖输入文件；请输出到独立文件交由安装器验证")
    result = patch(args.source.read_text())
    args.output.write_text(result)
    print(f"{PATCH_ID}: 已写入独立补丁产物 {args.output}")

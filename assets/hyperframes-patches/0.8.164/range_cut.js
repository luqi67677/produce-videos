// pv-sync-cut-1: pure range edit; persistence is owned by Studio CAS/history.
var PV_SYNC_CUT_PATCH_ID = "pv-sync-cut-1";
var PV_RANGE_EPS = 1e-6;
var pvRangeRound = (value) => Math.round(value * 1e6) / 1e6;
function pvRangeFail(message) {
  throw new Error(`全轨同步未保存：${message}`);
}
function pvRangeIntervals(intervals, duration) {
  if (!Array.isArray(intervals) || !intervals.length) pvRangeFail("没有有效删除区间");
  const sorted = intervals.map((range) => {
    if (!range || !Number.isFinite(range.start) || !Number.isFinite(range.end) || range.start < -PV_RANGE_EPS || range.end > duration + PV_RANGE_EPS || range.end - range.start <= PV_RANGE_EPS)
      pvRangeFail("删除区间超出当前合成或长度无效");
    return { start: Math.max(0, range.start), end: Math.min(duration, range.end) };
  }).sort((a, b) => a.start - b.start || a.end - b.end);
  const merged = [];
  for (const range of sorted) {
    const previous = merged.at(-1);
    if (previous && range.start <= previous.end + PV_RANGE_EPS) previous.end = Math.max(previous.end, range.end);
    else merged.push({ ...range });
  }
  return merged;
}
function pvRangeIdentity(el) {
  const hfId = el.getAttribute("data-hf-id");
  const id = el.getAttribute("id");
  if (!hfId && !id) pvRangeFail("片段缺少稳定标识，请重新加载预览");
  return { ...hfId ? { hfId } : {}, ...id ? { id } : {} };
}
function pvRangeTimed(el) {
  if (el.hasAttribute("data-start") || el.hasAttribute("data-duration") || el.matches("[data-composition-src], [data-composition-id]")) return el;
  return el.querySelector("video[data-start], audio[data-start]") ?? el;
}
function pvRangeAttrNumber(el, name) {
  const raw = el.getAttribute(name);
  if (raw === null || raw.trim() === "") return null;
  const value = Number(raw);
  return Number.isFinite(value) ? value : null;
}
function pvRangeAffected(start, end, ranges) {
  return ranges.some((range) => end > range.start + PV_RANGE_EPS);
}
function pvRangeCheckGsap(html, clipPlans) {
  const block = extractGsapScriptBlock(html);
  if (!block) return;
  const parsed = parseGsapScriptAcornForWrite(block.scriptText);
  if (!parsed) pvRangeFail("当前 GSAP 脚本无法安全解析");
  let timelineCount = 0;
  const inspect = (node) => {
    if (!node || typeof node !== "object") return;
    if (node.type === "CallExpression" && node.callee?.type === "MemberExpression" &&
      (node.callee.computed ? node.callee.property?.value : node.callee.property?.name) === "timeline") timelineCount++;
    for (const value of Object.values(node)) {
      if (Array.isArray(value)) value.forEach(inspect);
      else if (value && typeof value === "object") inspect(value);
    }
  };
  inspect(parsed.ast);
  if (timelineCount > 1 && clipPlans.some((plan) => plan.affected))
    pvRangeFail("当前脚本包含多条动画时间线，暂不支持同步剪切");
  for (const entry of parsed.located) {
    const animation = entry.animation;
    if (clipPlans.some((plan) => plan.affected) && (animation.hasUnresolvedSelector || animation.hasPartialSelector))
      pvRangeFail("动画使用动态或部分可解析选择器，暂不支持同步剪切");
    if (animation.global && animation.method === "set") continue;
    const selector = animation.targetSelector;
    if (typeof selector !== "string" || !selector) continue;
    let matches;
    try { matches = Array.from(clipPlans[0].el.ownerDocument.querySelectorAll(selector)); }
    catch { pvRangeFail(`无法解析动画选择器 ${selector}`); }
    const touched = clipPlans.filter((plan) => plan.affected && matches.some((node) => node === plan.el || plan.el.contains(node) || node.contains(plan.el)));
    if (!touched.length) continue;
    // Splitting a selector shared by multiple nodes, descendants, or hfIds would
    // leave the cloned animation attached to the original node. Fail atomically.
    if (touched.some((plan) => !plan.originalId || selector !== `#${plan.originalId}`))
      pvRangeFail(`动画选择器 ${selector} 暂不支持同步剪切`);
    if (typeof animation.position !== "number" || !Number.isFinite(animation.position))
      pvRangeFail(`动画 ${selector} 的时间不是可解析的绝对时间`);
    if (animation.hasUnresolvedKeyframes)
      pvRangeFail(`动画 ${selector} 的关键帧无法安全解析`);
    if (animation.extras && ["repeat", "repeatDelay", "yoyo", "stagger", "delay"].some((key) => animation.extras[key] !== undefined && animation.extras[key] !== 0 && animation.extras[key] !== false))
      pvRangeFail(`动画 ${selector} 含延迟、重复或错峰设置，暂不支持同步剪切`);
    if (animation.inspectionTiming && (["repeat", "repeatDelay", "delay"].some((key) => animation.inspectionTiming[key] !== 0) ||
      !animation.inspectionTiming.stagger || Object.values(animation.inspectionTiming.stagger).some((value) => value !== 0)))
      pvRangeFail(`动画 ${selector} 含延迟、重复或错峰设置，暂不支持同步剪切`);
    if (animation.implicitPosition || animation.durationUnresolved)
      pvRangeFail(`动画 ${selector} 的时间依赖无法安全移动`);
    const crossing = touched.flatMap((plan) => plan.cuts).filter((time) => time > animation.position + PV_RANGE_EPS && time < animation.position + (animation.duration ?? 0) - PV_RANGE_EPS);
    if (crossing.length && !authorsKeyframes(animation)) {
      // The native splitter interpolates numbers linearly. Applying it to an
      // eased tween or an unknown CSS baseline changes the rendered motion.
      if (!['none', 'linear'].includes(animation.ease || ''))
        pvRangeFail(`动画 ${selector} 的缓动暂不支持跨边界剪切`);
      if (animation.method === 'from') pvRangeFail(`动画 ${selector} 缺少可确定的结束状态`);
      const matching = parsed.located.map((item) => item.animation).filter((item) => item.targetSelector === selector);
      const index = matching.indexOf(animation);
      for (const time of crossing) {
        const baseline = animation.fromProperties ?? computeForwardBaselines(matching, time).before[index] ?? {};
        if (Object.entries(animation.properties).some(([key, value]) => typeof value !== 'number' || !Number.isFinite(value) || typeof baseline[key] !== 'number' || !Number.isFinite(baseline[key])))
          pvRangeFail(`动画 ${selector} 缺少可确定的数值起始状态`);
      }
    }
  }
}
async function pvRangeCutPreviewHtml(before, input, writer = "acorn") {
  if (typeof before !== "string" || !input || !Array.isArray(input.targets) || !input.targets.length)
    pvRangeFail("缺少当前合成的片段列表");
  const { document: originalDocument } = parseSourceDocument(before);
  const root = input.rootTarget ? findTargetElement(originalDocument, input.rootTarget) : originalDocument.querySelector("[data-composition-id]");
  const rootDuration = root && pvRangeAttrNumber(root, "data-duration");
  if (!root || rootDuration === null || rootDuration <= 0) pvRangeFail("当前合成缺少有效时长");
  const rootIdentity = pvRangeIdentity(root);
  const ranges = pvRangeIntervals(input.intervals, rootDuration);
  const removedDuration = pvRangeRound(ranges.reduce((sum, range) => sum + range.end - range.start, 0));
  if (rootDuration - removedDuration <= PV_RANGE_EPS) pvRangeFail("不能删除整个合成，请至少保留一个片段");
  const requests = [...input.targets];
  const requestedElements = input.targets.map((request) => request?.target && findTargetElement(originalDocument, request.target)).filter(Boolean);
  for (const el of root.querySelectorAll("[data-start], [data-duration], [data-end]")) {
    if (requestedElements.some((target) => target === el || target !== root && target.contains(el))) continue;
    // Source is authoritative: hidden/muted clips absent from the visible UI
    // still participate when their authored timing can be resolved safely.
    const start = el.hasAttribute("data-start") ? pvRangeAttrNumber(el, "data-start") : 0;
    const duration = pvRangeAttrNumber(el, "data-duration") ?? (pvRangeAttrNumber(el, "data-end") !== null && start !== null ? pvRangeAttrNumber(el, "data-end") - start : null);
    if (start === null || duration === null || duration <= 0) pvRangeFail("原文件中有无法解析时间的片段");
    if (requests.some((request) => { const target = request.target && findTargetElement(originalDocument, request.target); return target && target !== root && target.contains(el); })) continue;
    requests.push({ target: pvRangeIdentity(el), originalId: el.getAttribute("id") || undefined, elementStart: start, elementDuration: duration,
      playbackStart: readMediaOffsetSeconds((name) => el.getAttribute(name)), playbackRate: pvRangeAttrNumber(el, "data-playback-rate") ?? 1,
      track: pvRangeAttrNumber(el, "data-track-index") ?? pvRangeAttrNumber(el, "data-layer") ?? 0 });
  }
  const seen = new Set();
  const plans = [];
  for (const request of requests) {
    if (!request?.target || !Number.isFinite(request.elementStart) || !Number.isFinite(request.elementDuration) || request.elementStart < -PV_RANGE_EPS || request.elementDuration <= 0)
      pvRangeFail("片段时间无效，请重新加载时间线");
    const el = findTargetElement(originalDocument, request.target);
    if (!el || !isHTMLElement(el)) pvRangeFail("有片段无法在原文件中定位");
    if (el === root) continue;
    if (seen.has(el)) continue;
    seen.add(el);
    const timed = pvRangeTimed(el);
    const authoredStart = pvRangeAttrNumber(timed, "data-start");
    const authoredDuration = pvRangeAttrNumber(timed, "data-duration");
    if (timed.hasAttribute("data-start") && authoredStart === null) pvRangeFail("片段使用未解析的相对起始时间，暂不支持同步剪切");
    if (timed.hasAttribute("data-duration") && (authoredDuration === null || authoredDuration <= 0)) pvRangeFail("原文件中的片段时长无效");
    if (authoredStart !== null && Math.abs(authoredStart - request.elementStart) > 0.002 || authoredDuration !== null && Math.abs(authoredDuration - request.elementDuration) > 0.002)
      pvRangeFail("片段时间与原文件不一致，请重新加载时间线");
    const start = authoredStart ?? request.elementStart;
    const end = start + (authoredDuration ?? request.elementDuration);
    const affected = pvRangeAffected(start, end, ranges);
    if (affected && (request.timelineLocked === true || timed.hasAttribute("data-timeline-locked") || el.hasAttribute("data-timeline-locked")))
      pvRangeFail("受影响轨道含锁定片段，请先解锁");
    if (affected && timed.hasAttribute("data-automation")) pvRangeFail("变速自动化片段暂不支持同步剪切");
    const rate = pvRangeAttrNumber(timed, "data-playback-rate") ?? request.playbackRate ?? 1;
    if (timed.hasAttribute("data-playback-rate") && pvRangeAttrNumber(timed, "data-playback-rate") === null)
      pvRangeFail("原文件中的播放速率无效");
    if (!Number.isFinite(rate) || rate <= 0) pvRangeFail("片段播放速率无效");
    for (const attr of ["data-media-start", "data-playback-start"]) {
      if (timed.hasAttribute(attr) && (pvRangeAttrNumber(timed, attr) === null || pvRangeAttrNumber(timed, attr) < 0))
        pvRangeFail("原文件中的媒体起点无效");
    }
    const cuts = [...new Set(ranges.flatMap((range) => [range.start, range.end]).filter((time) => time > start + PV_RANGE_EPS && time < end - PV_RANGE_EPS))].sort((a, b) => b - a);
    if (cuts.length && [el, timed, ...el.querySelectorAll("audio, video")].some((node) =>
      ["data-fade-in", "data-fade-out"].some((attr) => parseFloat(node.getAttribute(attr) || "0") > 0) ||
      node.hasAttribute("loop") || node.getAttribute("data-loop") === "true" || node.hasAttribute("data-fx-chain")))
      pvRangeFail("带淡入淡出、循环或音频效果的片段暂不支持跨边界剪切");
    if (cuts.length && Array.from(el.querySelectorAll("[id]")).some((child) => child !== timed))
      pvRangeFail("片段包含带 ID 的子元素，暂不支持安全复制");
    plans.push({ request: { ...request, playbackRate: rate }, el, start, end, cuts, affected, target: pvRangeIdentity(el), originalId: el.getAttribute("id") || request.originalId || null });
  }
  if (!plans.length) pvRangeFail("没有可编辑片段");
  for (const plan of plans) {
    if (plans.some((other) => other !== plan && other.el.contains(plan.el)))
      pvRangeFail("当前选择混合了父子时间线，请进入同一合成后操作");
  }
  // All authored timeline children in this scope must participate. This prevents
  // a stale or filtered client list from silently leaving an audio track behind.
  for (const el of root.querySelectorAll("[data-start], [data-duration], [data-end]")) {
    if (plans.some((plan) => plan.el === el || plan.el.contains(el))) continue;
    const start = el.hasAttribute("data-start") ? pvRangeAttrNumber(el, "data-start") : 0;
    const duration = pvRangeAttrNumber(el, "data-duration");
    if (start !== null && duration !== null && duration > 0 && pvRangeAffected(start, start + duration, ranges))
      pvRangeFail("当前片段列表不完整，请重新加载时间线");
  }
  pvRangeCheckGsap(before, plans);
  let after = before;
  const segments = [];
  const rightHalfIds = [];
  const stats = { splitCount: 0, removedCount: 0, shiftedCount: 0, intervalCount: ranges.length, removedDuration };
  const respond = (data) => pvRangeFail(data.error || "动画编辑失败");
  for (const plan of plans) {
    let leftEnd = plan.end;
    for (const time of plan.cuts) {
      const split = splitElementInHtml(after, plan.target, time, `${plan.originalId || "clip"}-split`, {
        start: plan.start, duration: leftEnd - plan.start,
        playbackStart: plan.request.playbackStart, playbackRate: plan.request.playbackRate, track: plan.request.track
      });
      if (!split.matched || !split.newId) pvRangeFail("片段边界无法安全分割");
      after = split.html;
      stats.splitCount++;
      rightHalfIds.push(split.newId);
      segments.push({ target: { id: split.newId }, id: split.newId, start: time, end: leftEnd });
      if (plan.originalId) {
        const block = extractGsapScriptBlock(after);
        if (block) {
          const result = await executeGsapMutation({ type: "split-animations", originalId: plan.originalId, newId: split.newId, splitTime: time, elementStart: plan.start, elementDuration: leftEnd - plan.start }, block, respond, writer);
          // The native splitter reports previously-created '#x-split' siblings
          // because its conservative check uses String.includes(originalId).
          // Those exact sibling selectors belong to already separated windows.
          const unsupported = typeof result === "string" ? [] : (result.skippedSelectors ?? []).filter((selector) => !rightHalfIds.some((id) => selector === `#${id}`));
          if (unsupported.length)
            pvRangeFail(`以下动画暂不支持同步剪切：${unsupported.join("、")}`);
          const script = typeof result === "string" ? result : result.script;
          if (script !== block.scriptText) after = block.replaceScript(writer === "acorn" ? syncPositionHoldsBeforeKeyframes(script, block.scriptText) : (await loadGsapParser()).syncPositionHoldsBeforeKeyframes(script, block.scriptText));
        }
      }
      leftEnd = time;
    }
    segments.push({ target: plan.target, id: plan.originalId, start: plan.start, end: leftEnd });
  }
  after = relinkSplitHalvesInHtml(after, rightHalfIds);
  const removed = segments.filter((segment) => ranges.some((range) => segment.start >= range.start - PV_RANGE_EPS && segment.end <= range.end + PV_RANGE_EPS));
  stats.removedCount = removed.length;
  if (removed.length) after = removeElementsFromHtml(after, removed.map((segment) => segment.target));
  const retained = segments.filter((segment) => !removed.includes(segment));
  const shifts = [];
  const { document: finalDocument, wrappedFragment } = parseSourceDocument(after);
  for (const segment of retained) {
    const el = findTargetElement(finalDocument, segment.target);
    if (!el) pvRangeFail("分割后片段丢失，已取消全部修改");
    const timed = pvRangeTimed(el);
    const shift = ranges.filter((range) => range.end <= segment.start + PV_RANGE_EPS).reduce((sum, range) => sum + range.end - range.start, 0);
    const nextStart = pvRangeRound(segment.start - shift);
    timed.setAttribute("data-start", String(nextStart));
    timed.setAttribute("data-duration", String(pvRangeRound(segment.end - segment.start)));
    timed.removeAttribute("data-end");
    if (shift > PV_RANGE_EPS) {
      stats.shiftedCount++;
      if (segment.id) shifts.push({ targetSelector: `#${segment.id}`, delta: -shift });
    }
  }
  const finalRoot = findTargetElement(finalDocument, rootIdentity);
  if (!finalRoot) pvRangeFail("合成根节点丢失");
  const duration = pvRangeRound(rootDuration - removedDuration);
  finalRoot.setAttribute("data-duration", String(duration));
  finalRoot.removeAttribute("data-end");
  after = wrappedFragment ? finalDocument.body.innerHTML || "" : finalDocument.toString();
  if (shifts.length) {
    const block = extractGsapScriptBlock(after);
    if (block) {
      const result = await executeGsapMutation({ type: "shift-positions-batch", shifts }, block, respond, writer);
      if (typeof result !== "string" && result.skippedSelectors?.length) pvRangeFail("有动画无法同步移动");
      after = block.replaceScript(typeof result === "string" ? result : result.script);
    }
  }
  return { patch_id: PV_SYNC_CUT_PATCH_ID, after: ensureHfIds(after), duration, stats, skippedSelectors: [] };
}

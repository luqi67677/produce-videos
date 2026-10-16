#!/usr/bin/env python3
"""从唯一 shot-readiness.json 导出可审阅分镜，不生成媒体。"""

from __future__ import annotations

import argparse
import html
import json
from pathlib import Path

from validate_director_plan import validate


def cell(value: object) -> str:
    return html.escape(str(value), quote=False).replace("\\", "\\\\").replace("|", "\\|").replace("\n", "<br>")


def listed(values: list) -> str:
    return "；".join(cell(value) for value in values) or "无"


def render_board(project: Path, require_ready: bool = False) -> str:
    project = Path(project).expanduser().resolve()
    errors = validate(project, require_ready)
    if errors:
        raise ValueError("\n".join(errors))
    data = json.loads((project / "shot-readiness.json").read_text(encoding="utf-8"))
    plan = data.get("director_plan")
    if not isinstance(plan, dict):
        raise ValueError("旧项目未包含 director_plan；兼容校验不等于已有可导出的导演分镜")
    ready = plan["stage"] == "ready"
    shots = data["shots"]
    edl = json.loads((project / "edit-decision-list.json").read_text(encoding="utf-8")) if ready else None
    clips = {clip["clip_id"]: clip for clip in edl["picture_track"]} if ready else {}
    title = data.get("project") or "导演分镜"
    unresolved = sum(not request["selected_asset_ids"] for shot in shots for request in shot["direction"]["assets_needed"])
    if ready:
        total_seconds = max(clip["timeline_start_seconds"] + clip["duration_seconds"] for clip in clips.values())
        total_label = f"实测总长：{total_seconds:.3f} 秒"
    else:
        total_seconds = sum(shot["direction"]["estimated_duration_seconds"] for shot in shots)
        total_label = f"预计总时长：{total_seconds:g} 秒（导演估时）"
    lines = [f"# {cell(title)} · 导演分镜", "",
             f"- 阶段：{'素材与实测定时已落实' if ready else '规划；尚未进入合成'}",
             f"- {total_label}", f"- 镜头：{len(shots)} 个",
             f"- 待解决素材需求：{unresolved} 项（按镜头逐项计数）",
             f"- 目标观众：{cell(plan['audience'])}", f"- 看完所得：{cell(plan['viewer_outcome'])}",
             f"- 叙事主线：{cell(plan['throughline'])}", ""]
    if ready:
        lines += ["下表使用已测量的正式时间；总长取实际画面时间线的结束位置。", ""]
    else:
        lines += ["以下全部为导演估时。正式时间须等旁白测量后确定，估时不能用于声画对齐验收。", ""]
    lines += ["| 镜头 | 口播原文 | 观众所得 | 时间 |", "| --- | --- | --- | --- |"]
    for shot in shots:
        direction = shot["direction"]
        if ready:
            clip = clips[shot["shot_id"]]
            start, duration = clip["timeline_start_seconds"], clip["duration_seconds"]
            timing = f"实测 {start:.3f}–{start + duration:.3f} 秒（{duration:.3f} 秒）"
        else:
            timing = f"预计 {direction['estimated_duration_seconds']:g} 秒"
        lines.append(f"| {cell(shot['shot_id'])} | {cell(shot['narration_excerpt'])} | {cell(direction['audience_takeaway'])} | {timing} |")
    for shot in shots:
        direction = shot["direction"]
        lines += ["", f"## {cell(shot['shot_id'])}", "",
                  f"- 原稿段落：{cell(shot['narration_segment_id'])}",
                  f"- 口播原文：{cell(shot['narration_excerpt'])}",
                  f"- 观众所得：{cell(direction['audience_takeaway'])}",
                  f"- 本镜负责讲清：{cell(shot['visual_duty'])}",
                  f"- 画面组合：{cell(direction['visual_form'])}",
                  f"- 构图与元素：{cell(direction['composition'])}",
                  f"- 运镜：{cell(direction['camera'])}",
                  f"- 连续性锚点：{cell(direction['continuity_anchor'])}",
                  f"- 切换理由：{cell(direction['transition_reason'])}",
                  f"- 开始状态：{cell(direction['states']['before'])}",
                  f"- 可见动作：{cell(direction['states']['action'])}",
                  f"- 结果状态：{cell(direction['states']['after'])}",
                  f"- 字幕方案：{cell(direction['subtitle_plan'])}",
                  f"- 音乐方案：{cell(direction['music_plan'])}", "", "### 素材需求", ""]
        requests = direction["assets_needed"]
        if not requests:
            lines += ["无外部素材需求；按本镜已声明的画面与元素实现。"]
        else:
            for request in requests:
                lines += [f"**{cell(request['role'])}**", "",
                          f"- 需要什么：{cell(request['description'])}",
                          f"- 获取路线：{cell(request['preferred_source'])}",
                          f"- 检索词：{listed(request['search_queries'])}",
                          f"- 验收条件：{listed(request['acceptance_criteria'])}",
                          f"- 缺口替代：{cell(request['fallback'])}",
                          f"- 已选素材：{listed(request['selected_asset_ids']) if request['selected_asset_ids'] else '待解决'}",
                          f"- 请求编号：{cell(request['request_id'])}", ""]
        lines += ["", "### 动效与声音事件", ""]
        events = direction["events"]
        if not events:
            lines += ["本镜未安排独立事件；按本镜状态、运镜及音乐方案执行。"]
        else:
            for event in events:
                sound = event["sound"]
                mode = {"none": "不加音效", "sfx": "动作音效", "ambience": "环境声"}[sound["mode"]]
                lines += [f"**口播到“{cell(event['cue_text'])}”时**", "",
                          f"- 动作前：{cell(event['before'])}",
                          f"- 画面动作：{cell(event['action'])}",
                          f"- 动作后：{cell(event['after'])}",
                          f"- 先决事件：{listed(event['depends_on'])}",
                          f"- 声音：{mode}。{cell(sound['reason'])}"]
                if sound["mode"] != "none":
                    lines += [f"- 声音开始：{cell(sound['start_trigger'])}",
                              f"- 声音停止：{cell(sound['stop_trigger'])}",
                              f"- 声音素材请求：{cell(sound['request_id'])}"]
                lines += [f"- 事件编号：{cell(event['event_id'])}", ""]
        if ready:
            lines += ["", "### EDL 实测事件（本镜相对帧，结束帧不包含在区间内）", "",
                      f"帧率：{edl['format']['fps']:g} 帧/秒。", ""]
            for event in clips[shot["shot_id"]]["semantic_events"]:
                sound = event.get("sound")
                if sound:
                    sound_range = f"{sound['start_frame']}–{sound['end_frame']}"
                    settings = f"{sound['gain_db']:g} dB / {sound['fade_in_ms']:g}、{sound['fade_out_ms']:g} 毫秒"
                else:
                    sound_range, settings = "无", "无"
                lines += [f"**{cell(event['event_id'])}**", "",
                          f"- 画面帧范围：{event['start_frame']}–{event['end_frame']}",
                          f"- 声音帧范围：{sound_range}",
                          f"- 声音增益 / 淡入淡出：{settings}", ""]
    lines += ["", "## 追溯信息", "",
              "此表由 shot-readiness.json 导出；修改源契约后重新导出。", "",
              f"- 原稿：{cell(plan['script_binding']['path'])}",
              f"- 原稿 SHA-256：{cell(plan['script_binding']['sha256'])}"]
    if ready:
        lines += ["- 实测时间来源：edit-decision-list.json；本表不建立第二条时间线。"]
    lines += ["", "本表和校验结果只证明计划与时间引用一致；成片画面、因果表达和声音是否合适仍需实际审片。", ""]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="把同一份导演计划导出为可审阅 Markdown 分镜，不渲染视频")
    parser.add_argument("project", type=Path, help="视频项目目录")
    parser.add_argument("--output", type=Path, help="Markdown 输出路径；省略时输出到终端")
    parser.add_argument("--require-ready", action="store_true", help="仅导出素材与实测定时已落实的分镜")
    args = parser.parse_args()
    try:
        board = render_board(args.project, args.require_ready)
        if args.output:
            output = args.output.expanduser().resolve()
            if output.suffix.lower() != ".md":
                raise ValueError("输出必须为 .md，防止覆盖 JSON 源契约")
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(board, encoding="utf-8")
            print(f"已导出导演分镜：{output}")
        else:
            print(board, end="")
    except (ValueError, OSError) as exc:
        print(f"无法导出：{exc}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

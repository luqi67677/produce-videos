#!/usr/bin/env python3
"""Validate deterministic layout facts before manual visual review."""

from __future__ import annotations

import argparse
import re
import struct
from html.parser import HTMLParser
from pathlib import Path


class VisibleHTML(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.hidden_depth = 0
        self.text: list[str] = []
        self.in_title = False
        self.title_text: list[str] = []
        self.title_breaks = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in {"script", "style"}:
            self.hidden_depth += 1
        if tag == "h1":
            self.in_title = True
        elif tag == "br" and self.in_title:
            self.title_breaks += 1

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style"} and self.hidden_depth:
            self.hidden_depth -= 1
        if tag == "h1":
            self.in_title = False

    def handle_data(self, data: str) -> None:
        if not self.hidden_depth:
            self.text.append(data)
            if self.in_title:
                self.title_text.append(data)


def png_size(path: Path) -> tuple[int, int]:
    with path.open("rb") as handle:
        if handle.read(8) != b"\x89PNG\r\n\x1a\n":
            raise ValueError(f"不是 PNG 文件: {path}")
        length = struct.unpack(">I", handle.read(4))[0]
        chunk = handle.read(4)
        if chunk != b"IHDR" or length < 8:
            raise ValueError(f"PNG 缺少有效 IHDR: {path}")
        return struct.unpack(">II", handle.read(8))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--html", type=Path, required=True)
    parser.add_argument("--image", type=Path, required=True)
    parser.add_argument("--expected-width", type=int, required=True)
    parser.add_argument("--expected-height", type=int, required=True)
    parser.add_argument("--exact-title")
    parser.add_argument("--exact-token", action="append", default=[])
    parser.add_argument("--forbid-token", action="append", default=[])
    parser.add_argument("--max-title-lines", type=int, default=2)
    args = parser.parse_args()

    errors: list[str] = []
    html = args.html.read_text(encoding="utf-8")
    visible = VisibleHTML()
    visible.feed(html)
    text = re.sub(r"\s+", " ", " ".join(visible.text)).strip()
    title_text = re.sub(r"\s+", "", "".join(visible.title_text))

    if args.exact_title:
        expected_title = re.sub(r"\s+", "", args.exact_title)
        if title_text != expected_title:
            errors.append(f"主标题与用户确认稿不一致: {title_text}")

    for token in args.exact_token:
        if token not in text:
            errors.append(f"缺少精确品牌词: {token}")
    for token in args.forbid_token:
        if token in text:
            errors.append(f"出现禁用文字: {token}")

    title_lines = visible.title_breaks + 1
    if title_lines > args.max_title_lines:
        errors.append(f"主标题 {title_lines} 行，超过限制 {args.max_title_lines} 行")

    if re.search(r"text-transform\s*:\s*uppercase", html, re.IGNORECASE):
        errors.append("检测到 text-transform: uppercase")

    leaked = [
        label
        for label in ("Option A", "Option B", "Option C", "template slug", "镜头编号")
        if label.casefold() in text.casefold()
    ]
    if leaked:
        errors.append("画面泄漏内部标签: " + ", ".join(leaked))

    width, height = png_size(args.image)
    if (width, height) != (args.expected_width, args.expected_height):
        errors.append(
            f"图片尺寸为 {width}×{height}，应为 {args.expected_width}×{args.expected_height}"
        )

    if errors:
        print("版式预检失败：")
        for error in errors:
            print(f"- {error}")
        return 1

    print(
        f"版式预检通过：{args.image}，{width}×{height}，主标题 {title_lines} 行"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

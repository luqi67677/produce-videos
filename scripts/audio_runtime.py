#!/usr/bin/env python3
"""为音频脚本切换到用户已有的兼容 Python 运行环境。"""

from __future__ import annotations

import os
import sys
from pathlib import Path


def absolute_path(path: Path) -> Path:
    """保留虚拟环境入口路径，不能 resolve 到基础解释器。"""
    expanded = path.expanduser()
    return expanded if expanded.is_absolute() else Path.cwd() / expanded


def _without_runtime_argument(argv: list[str]) -> list[str]:
    filtered: list[str] = []
    index = 0
    while index < len(argv):
        value = argv[index]
        if value == "--runtime-python":
            index += 2
            continue
        if value.startswith("--runtime-python="):
            index += 1
            continue
        filtered.append(value)
        index += 1
    return filtered


def relaunch_with_runtime(runtime_python: Path | None) -> None:
    """如用户指定了另一解释器，用它重启当前脚本并保留原退出状态。"""
    if runtime_python is None:
        return
    target = absolute_path(runtime_python)
    if not target.is_file() or not os.access(target, os.X_OK):
        raise ValueError(f"指定的声音运行环境不可执行：{target}")
    current = absolute_path(Path(sys.executable))
    if target == current:
        return
    argv = [str(target), str(Path(sys.argv[0]).absolute()), *_without_runtime_argument(sys.argv[1:])]
    os.execv(str(target), argv)

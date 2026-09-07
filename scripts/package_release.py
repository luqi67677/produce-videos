#!/usr/bin/env python3
"""Build generic, .skill, and WorkBuddy release artifacts."""

from __future__ import annotations

import argparse
import hashlib
import zipfile
from pathlib import Path

from package_workbuddy import build_package as build_workbuddy


SKIP_PARTS = {".git", "dist", "__pycache__", ".pytest_cache"}
SKIP_NAMES = {".DS_Store"}


def included_files(root: Path) -> list[Path]:
    return [
        path for path in sorted(root.rglob("*"))
        if path.is_file() and not path.is_symlink()
        and not any(part in SKIP_PARTS for part in path.relative_to(root).parts)
        and path.relative_to(root).parts[:2] != ("examples", "videos")
        and path.name not in SKIP_NAMES and path.suffix != ".pyc"
    ]


def build_generic(root: Path, output: Path) -> int:
    output.parent.mkdir(parents=True, exist_ok=True)
    files = included_files(root)
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in files:
            archive.write(path, Path("produce-videos") / path.relative_to(root))
    return len(files)


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def build_all(root: Path, output_dir: Path) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    generic = output_dir / "produce-videos.zip"
    skill = output_dir / "produce-videos.skill"
    workbuddy = output_dir / "produce-videos-workbuddy.zip"
    build_generic(root, generic)
    build_generic(root, skill)
    build_workbuddy(root, workbuddy)
    artifacts = [generic, skill, workbuddy]
    checksums = output_dir / "SHA256SUMS.txt"
    checksums.write_text("".join(f"{digest(path)}  {path.name}\n" for path in artifacts), encoding="utf-8")
    return [*artifacts, checksums]


def main() -> int:
    parser = argparse.ArgumentParser(description="生成 GitHub Release 可直接下载的 Skill 安装包")
    parser.add_argument("--output-dir", type=Path, default=Path(__file__).resolve().parents[1] / "dist")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    artifacts = build_all(root, args.output_dir.expanduser().resolve())
    for artifact in artifacts:
        print(f"PASS {artifact} ({artifact.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

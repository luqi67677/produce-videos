#!/usr/bin/env python3
"""打开已有 Hyperframes 工程并检查源文件变化；不转换 EDL，不批准成片。"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
from html.parser import HTMLParser
import json
import os
from pathlib import Path
import re
import shutil
import stat
import subprocess
import sys
import uuid
from urllib.parse import urlparse
from urllib.request import ProxyHandler, HTTPRedirectHandler, Request, build_opener
from urllib.error import URLError


COMPATIBLE_VERSION = "0.8.164"
REQUIRED_PATCH_ID = "pv-sync-cut-1"
STATE_DIR = ".produce-videos-workbench"
BASELINE_NAME = "baseline.json"
ROOT_FILES = (
    "index.html", "STORYBOARD.md", "hyperframes.json", "package.json",
    "shot-readiness.json", "edit-decision-list.json", "motion-plan.json",
    "video-style-theme.json", "master-script.json", "narration-contract.json",
    "caption-overrides.json", "captions.json", "captions.srt", "captions.vtt",
)
SOURCE_DIRS = ("assets", "src", "styles", "scripts", "compositions")
SOURCE_EXTENSIONS = {
    ".html", ".css", ".js", ".mjs", ".cjs", ".ts", ".tsx", ".jsx",
    ".svg", ".png", ".jpg", ".jpeg", ".webp", ".gif", ".mp4", ".mov",
    ".webm", ".wav", ".mp3", ".m4a", ".aac", ".ogg", ".woff", ".woff2",
    ".ttf", ".otf", ".srt", ".vtt", ".json", ".txt",
}
TEXT_EXTENSIONS = {".html", ".css", ".js", ".mjs", ".cjs", ".ts", ".tsx", ".jsx", ".md", ".json", ".srt", ".vtt", ".txt"}
MAX_FILES = 2000
MAX_JSON_BYTES = 8 * 1024 * 1024


class WorkbenchError(ValueError):
    """可向用户直接说明的失败。"""


def protected_path(raw: str | Path, *, must_exist: bool = True) -> Path:
    path = Path(raw).expanduser()
    if ".." in path.parts:
        raise WorkbenchError("路径不能包含 ..；请提供明确的项目路径")
    if not path.is_absolute():
        path = Path.cwd() / path
    current = Path(path.anchor)
    for part in path.parts[1:]:
        current = current / part
        try:
            info = current.lstat()
        except FileNotFoundError:
            if must_exist:
                raise WorkbenchError(f"路径不存在：{current}") from None
            continue
        if stat.S_ISLNK(info.st_mode):
            raise WorkbenchError(f"不接受符号链接：{current}")
    return path


def project_file(project: Path, relative: str) -> Path:
    fragment = Path(relative)
    if fragment.is_absolute() or ".." in fragment.parts:
        raise WorkbenchError(f"项目路径越界：{relative}")
    path = protected_path(project / fragment)
    if not path.is_relative_to(project) or not path.is_file():
        raise WorkbenchError(f"不是项目内普通文件：{relative}")
    return path


def read_bytes(path: Path, limit: int | None = None) -> bytes:
    descriptor = os.open(path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
    with os.fdopen(descriptor, "rb") as handle:
        before = os.fstat(handle.fileno())
        if not stat.S_ISREG(before.st_mode):
            raise WorkbenchError(f"不是普通文件：{path.name}")
        if limit is not None and before.st_size > limit:
            raise WorkbenchError(f"文件超出读取上限：{path.name}")
        value = handle.read()
        after = os.fstat(handle.fileno())
        if (before.st_size, before.st_mtime_ns) != (after.st_size, after.st_mtime_ns):
            raise WorkbenchError(f"文件正在变化，请保存后重试：{path.name}")
        return value


def read_json(path: Path) -> dict:
    try:
        value = json.loads(read_bytes(path, MAX_JSON_BYTES))
    except (UnicodeError, json.JSONDecodeError) as error:
        raise WorkbenchError(f"JSON 无法解析：{path.name}：{error}") from error
    if not isinstance(value, dict):
        raise WorkbenchError(f"JSON 根必须是对象：{path.name}")
    return value


class CompositionParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.compositions: list[dict] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        data = dict(attrs)
        if data.get("data-composition-id"):
            self.compositions.append({key: value for key, value in data.items() if key.startswith("data-")})


def storyboard_state(project: Path) -> dict:
    readiness = project / "shot-readiness.json"
    if readiness.exists() or readiness.is_symlink():
        document = read_json(project_file(project, "shot-readiness.json"))
        director = document.get("director_plan")
        if not isinstance(director, dict):
            raise WorkbenchError("shot-readiness.json 缺少 director_plan；请先迁移旧分镜契约")
        stage = director.get("stage")
        timing = director.get("timing_basis")
        if (stage, timing) not in {("planning", "estimated"), ("ready", "measured")}:
            raise WorkbenchError("director_plan 只接受 planning/estimated 或 ready/measured")
        shots = document.get("shots")
        if not isinstance(shots, list) or not shots:
            raise WorkbenchError("shot-readiness.json 必须包含至少一个镜头")
        return {"source": "shot-readiness.json", "stage": stage, "timing_basis": timing,
                "shot_count": len(shots), "production_gate_validated": False}
    native = project_file(project, "STORYBOARD.md")
    content = read_bytes(native, MAX_JSON_BYTES).decode("utf-8")
    frames = re.findall(r"^##\s+Frame\s+\d+\b", content, re.MULTILINE | re.IGNORECASE)
    if not frames:
        raise WorkbenchError("STORYBOARD.md 至少需要一个 ## Frame N 分镜")
    return {"source": "STORYBOARD.md", "stage": "storyboard", "timing_basis": "unverified",
            "shot_count": len(frames), "production_gate_validated": False,
            "note": "原生画面稿可预览；尚未绑定 produce-videos 的 planning/ready 契约"}


def validate_project(raw: str | Path) -> tuple[Path, dict]:
    project = protected_path(raw)
    if not project.is_dir():
        raise WorkbenchError("项目路径必须是目录")
    index = project_file(project, "index.html")
    parser = CompositionParser()
    parser.feed(read_bytes(index, MAX_JSON_BYTES).decode("utf-8"))
    if not parser.compositions:
        raise WorkbenchError("index.html 缺少 data-composition-id，不能识别为 Hyperframes 工程")
    identified = False
    config_path = project / "hyperframes.json"
    if config_path.exists() or config_path.is_symlink():
        config = read_json(project_file(project, "hyperframes.json"))
        if config.get("composition", "index.html") != "index.html":
            raise WorkbenchError("本接入版只支持 composition=index.html")
        identified = True
    package_path = project / "package.json"
    if package_path.exists() or package_path.is_symlink():
        package = read_json(project_file(project, "package.json"))
        for name in ("dependencies", "devDependencies"):
            dependencies = package.get(name, {})
            if isinstance(dependencies, dict) and "hyperframes" in dependencies:
                identified = True
    if not identified:
        raise WorkbenchError("未知项目：需要 hyperframes.json 或声明 hyperframes 的 package.json")
    return project, {"project": str(project), "entry": "index.html", "preview_allowed": True,
                     "storyboard": storyboard_state(project), "compositions": parser.compositions,
                     "audio_required_for_preview": False, "production_gate_validated": False,
                     "synchronization_status": "not_performed"}


def managed_files(project: Path) -> list[Path]:
    files = []
    for name in ROOT_FILES:
        path = project / name
        if path.exists() or path.is_symlink():
            files.append(project_file(project, name))
    for name in SOURCE_DIRS:
        directory = project / name
        if not directory.exists() and not directory.is_symlink():
            continue
        protected_path(directory)
        if not directory.is_dir():
            raise WorkbenchError(f"源码目录不是目录：{name}")
        for current, directories, names in os.walk(directory, followlinks=False):
            directories[:] = sorted(item for item in directories if not item.startswith(".") and item != "node_modules")
            for item in directories:
                protected_path(Path(current) / item)
            for item in sorted(names):
                path = Path(current) / item
                if item.startswith(".") or path.suffix.lower() not in SOURCE_EXTENSIONS:
                    continue
                files.append(project_file(project, path.relative_to(project).as_posix()))
                if len(files) > MAX_FILES:
                    raise WorkbenchError(f"受管理文件超过 {MAX_FILES} 个，请缩小项目范围")
    return sorted(set(files))


def hash_file(path: Path) -> dict:
    descriptor = os.open(path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
    with os.fdopen(descriptor, "rb") as handle:
        before = os.fstat(handle.fileno())
        if not stat.S_ISREG(before.st_mode):
            raise WorkbenchError(f"不是普通文件：{path.name}")
        digest = hashlib.sha256()
        while chunk := handle.read(1024 * 1024):
            digest.update(chunk)
        after = os.fstat(handle.fileno())
    if (before.st_size, before.st_mtime_ns) != (after.st_size, after.st_mtime_ns):
        raise WorkbenchError(f"文件正在变化，请保存后重试：{path.name}")
    return {"sha256": digest.hexdigest(), "size_bytes": before.st_size}


def manifest(project: Path) -> dict:
    return {path.relative_to(project).as_posix(): hash_file(path) for path in managed_files(project)}


def inspect_project(raw: str | Path, *, include_source: bool = False, max_chars: int = 16000) -> dict:
    project, report = validate_project(raw)
    report["managed_files"] = manifest(project)
    report["scope"] = {"root_files": list(ROOT_FILES), "source_directories": list(SOURCE_DIRS),
                       "external_assets_and_other_paths": "not_inspected"}
    if include_source:
        sources = {}
        for name, record in report["managed_files"].items():
            path = project_file(project, name)
            if path.suffix.lower() not in TEXT_EXTENSIONS:
                continue
            if record["size_bytes"] > MAX_JSON_BYTES:
                sources[name] = {"skipped": "source_too_large"}
                continue
            content = read_bytes(path, MAX_JSON_BYTES).decode("utf-8", errors="replace")
            if hashlib.sha256(content.encode("utf-8")).hexdigest() != record["sha256"]:
                raise WorkbenchError(f"源文件编码无效或检查时已变化：{name}")
            sources[name] = {"text": content[:max_chars], "truncated": len(content) > max_chars}
        report["sources"] = sources
    return report


def snapshot_project(raw: str | Path, *, replace: bool = False) -> dict:
    project, report = validate_project(raw)
    files = manifest(project)
    baseline = {"schema_version": "1.0", "project_root": str(project), "files": files,
                "purpose": "source-change-detection-only"}
    root_fd = os.open(project, os.O_RDONLY | os.O_DIRECTORY | getattr(os, "O_NOFOLLOW", 0))
    try:
        try:
            os.mkdir(STATE_DIR, mode=0o700, dir_fd=root_fd)
        except FileExistsError:
            pass
        state_fd = os.open(STATE_DIR, os.O_RDONLY | os.O_DIRECTORY | getattr(os, "O_NOFOLLOW", 0), dir_fd=root_fd)
        try:
            try:
                existing = os.stat(BASELINE_NAME, dir_fd=state_fd, follow_symlinks=False)
            except FileNotFoundError:
                existing = None
            if existing is not None:
                if not stat.S_ISREG(existing.st_mode):
                    raise WorkbenchError("已有 baseline 不是普通文件，拒绝写入")
                if not replace:
                    raise WorkbenchError("baseline 已存在；先运行 check，确认后显式使用 --replace-baseline")
            temporary = f"baseline-{uuid.uuid4().hex}.tmp"
            descriptor = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0), 0o600, dir_fd=state_fd)
            try:
                with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
                    json.dump(baseline, handle, ensure_ascii=False, indent=2)
                    handle.write("\n")
                    handle.flush()
                    os.fsync(handle.fileno())
                os.replace(temporary, BASELINE_NAME, src_dir_fd=state_fd, dst_dir_fd=state_fd)
            finally:
                try:
                    os.unlink(temporary, dir_fd=state_fd)
                except FileNotFoundError:
                    pass
        finally:
            os.close(state_fd)
    finally:
        os.close(root_fd)
    report.update({"baseline": f"{STATE_DIR}/{BASELINE_NAME}", "managed_file_count": len(files), "baseline_written": True})
    return report


def check_project(raw: str | Path) -> dict:
    # 即使用户删除了 index 或改坏分镜，仍能检测；基线负责识别已登记项目。
    project = protected_path(raw)
    baseline = read_json(project_file(project, f"{STATE_DIR}/{BASELINE_NAME}"))
    if baseline.get("schema_version") != "1.0" or baseline.get("project_root") != str(project):
        raise WorkbenchError("baseline 不属于当前项目或版本未知")
    original = baseline.get("files")
    if not isinstance(original, dict) or "index.html" not in original:
        raise WorkbenchError("baseline 缺少已登记的 index.html")
    for name, value in original.items():
        if not isinstance(name, str) or Path(name).is_absolute() or ".." in Path(name).parts:
            raise WorkbenchError("baseline 含越界路径")
        if not isinstance(value, dict) or not re.fullmatch(r"[0-9a-f]{64}", str(value.get("sha256", ""))):
            raise WorkbenchError("baseline 文件记录无效")
    current = manifest(project)
    added = sorted(set(current) - set(original))
    deleted = sorted(set(original) - set(current))
    modified = sorted(name for name in set(current) & set(original) if current[name]["sha256"] != original[name]["sha256"])
    return {"project": str(project), "changed": bool(added or deleted or modified), "added": added,
            "deleted": deleted, "modified": modified, "files": current,
            "synchronization_status": "not_performed", "baseline_updated": False,
            "note": "仅发现文件变化；没有将 HTML 转换为 EDL，也没有更新审批"}


def verify_runtime_patch(cli: Path) -> dict:
    patch_script = Path(__file__).with_name("workbench_runtime_patch.py")
    spec = importlib.util.spec_from_file_location("produce_videos_runtime_patch", patch_script)
    if spec is None or spec.loader is None:
        raise WorkbenchError("缺少全轨同步补丁检查器")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    try:
        return module.patch_runtime(cli.parent.parent, check=True)
    except (ValueError, OSError, KeyError) as error:
        raise WorkbenchError(f"全轨同步运行时检查失败：{error}") from error


def verify_running_patch(url: str) -> dict:
    parsed = urlparse(url)
    if parsed.scheme != "http" or parsed.hostname not in {"127.0.0.1", "localhost", "::1"} or parsed.username or parsed.password:
        raise WorkbenchError("补丁服务核验只接受本机 HTTP 地址")

    class NoRedirect(HTTPRedirectHandler):
        def redirect_request(self, req, fp, code, msg, headers, newurl):
            return None

    endpoint = f"{parsed.scheme}://{parsed.netloc}/api/pv-workbench/capabilities"
    try:
        opener = build_opener(ProxyHandler({}), NoRedirect())
        with opener.open(Request(endpoint, headers={"Accept": "application/json"}), timeout=5) as response:
            capabilities = json.loads(response.read(65536))
    except (URLError, OSError, ValueError) as error:
        raise WorkbenchError("正在运行的服务未通过全轨同步核验；请停止旧预览进程，再用已打补丁的 CLI 启动") from error
    if not isinstance(capabilities, dict) or capabilities.get("patch_id") != REQUIRED_PATCH_ID or capabilities.get("range_cut_preview") is not True:
        raise WorkbenchError("预览端口仍在运行旧版本；重启后才能使用全轨同步剪切")
    return capabilities


def cli_environment(raw: str | Path, *, node: str = "node") -> dict:
    cli = protected_path(raw)
    if not cli.is_file() or cli.suffix not in {".js", ".mjs", ".cjs"}:
        raise WorkbenchError("--hyperframes-cli 必须指向真实的 CLI JavaScript 文件")
    executable = shutil.which(node)
    if executable is None:
        raise WorkbenchError(f"找不到 Node.js 可执行文件：{node}")
    result = subprocess.run([executable, str(cli), "--version"], check=False, capture_output=True, text=True, timeout=30)
    if result.returncode != 0:
        raise WorkbenchError(f"Hyperframes 版本检查失败：{result.stderr.strip()[:500]}")
    versions = re.findall(r"(?<![\d.])\d+\.\d+\.\d+(?![\d.])", result.stdout)
    if versions != [COMPATIBLE_VERSION]:
        raise WorkbenchError(f"只验证过 Hyperframes {COMPATIBLE_VERSION}；实际版本输出：{result.stdout.strip()[:200]}")
    patch = verify_runtime_patch(cli)
    return {"node": executable, "cli": str(cli), "version": COMPATIBLE_VERSION, "patch": patch}


def preview_command(project: Path, runtime: dict, port: int) -> list[str]:
    if not 1024 <= port <= 65535:
        raise WorkbenchError("端口必须在 1024 到 65535 之间")
    return [runtime["node"], runtime["cli"], "preview", str(project), "--background", "--no-open", "--port", str(port), "--json"]


def check_cache_paths(project: Path) -> None:
    for name in (".hyperframes", ".thumbnails", ".waveform-cache", STATE_DIR):
        directory = protected_path(project / name, must_exist=False)
        if not directory.exists():
            continue
        if not directory.is_dir():
            raise WorkbenchError(f"缓存位置不是目录：{name}")
        for current, directories, files in os.walk(directory, followlinks=False):
            for item in directories + files:
                protected_path(Path(current) / item)


def open_project(raw: str | Path, cli: str | Path, *, port: int = 3027, node: str = "node") -> dict:
    project, report = validate_project(raw)
    # 启动器会产生缓存，先拒绝已知源码和缓存位置中的符号链接。
    managed_files(project)
    check_cache_paths(project)
    runtime = cli_environment(cli, node=node)
    command = preview_command(project, runtime, port)
    result = subprocess.run(command, cwd=project, check=False, capture_output=True, text=True, timeout=60)
    if result.returncode != 0:
        raise WorkbenchError(f"Hyperframes preview 启动失败：{result.stderr.strip()[:1000]}")
    try:
        actual = json.loads(result.stdout)
    except json.JSONDecodeError as error:
        raise WorkbenchError("CLI 没有返回可解析 JSON，不能确认预览地址") from error
    if not isinstance(actual, dict):
        raise WorkbenchError("CLI 返回值不是对象，不能确认预览地址")
    if actual.get("schemaVersion") != 1 or actual.get("operation") != "start":
        raise WorkbenchError("CLI 返回了未知的预览启动响应格式")
    if actual.get("ok") is not True:
        raise WorkbenchError("CLI 报告预览启动未成功")
    preview = actual.get("result")
    if not isinstance(preview, dict) or preview.get("ready") is not True:
        raise WorkbenchError("CLI 未确认预览服务已就绪")
    returned_project = preview.get("projectDir")
    if not isinstance(returned_project, str) or not Path(returned_project).is_absolute():
        raise WorkbenchError("CLI 未返回明确的工程绝对路径")
    if protected_path(returned_project) != project:
        raise WorkbenchError("CLI 返回的工程路径与请求不一致")
    url = preview.get("studioUrl")
    parsed = urlparse(url if isinstance(url, str) else "")
    try:
        returned_port = parsed.port
    except ValueError as error:
        raise WorkbenchError("CLI 返回的 studioUrl 端口无效") from error
    if parsed.scheme != "http" or parsed.hostname not in {"127.0.0.1", "localhost", "::1"} or returned_port != port:
        raise WorkbenchError("CLI 未返回请求端口上的本机 studioUrl，不能确认预览地址")
    capabilities = verify_running_patch(url)
    report.update({"runtime": runtime, "studio_url": url, "cli_result": actual,
                   "workbench_capabilities": capabilities,
                   "started_or_reused": True, "browser_opened": False,
                   "note": "地址来自 CLI 实际返回；未验证浏览器审片、编辑回写、EDL 同步或最终导出"})
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("doctor", "open", "inspect", "snapshot", "check"):
        command = commands.add_parser(name)
        command.add_argument("project", type=Path)
        if name in {"doctor", "open"}:
            command.add_argument("--hyperframes-cli", type=Path, required=name == "open")
            command.add_argument("--node", default="node")
        if name == "open":
            command.add_argument("--port", type=int, default=3027)
        if name == "inspect":
            command.add_argument("--include-source", action="store_true")
            command.add_argument("--max-source-chars", type=int, default=16000)
        if name == "snapshot":
            command.add_argument("--replace-baseline", action="store_true")
    args = parser.parse_args(argv)
    try:
        if args.command == "doctor":
            _, report = validate_project(args.project)
            report["runtime"] = cli_environment(args.hyperframes_cli, node=args.node) if args.hyperframes_cli else {"status": "not_checked", "required_version": COMPATIBLE_VERSION}
            report["read_only"] = True
        elif args.command == "open":
            report = open_project(args.project, args.hyperframes_cli, port=args.port, node=args.node)
        elif args.command == "inspect":
            if not 1 <= args.max_source_chars <= 100000:
                raise WorkbenchError("--max-source-chars 必须在 1 到 100000 之间")
            report = inspect_project(args.project, include_source=args.include_source, max_chars=args.max_source_chars)
        elif args.command == "snapshot":
            report = snapshot_project(args.project, replace=args.replace_baseline)
        else:
            report = check_project(args.project)
        print(json.dumps({"ok": True, **report}, ensure_ascii=False, indent=2))
        return 0
    except (WorkbenchError, OSError, UnicodeError, subprocess.TimeoutExpired) as error:
        print(json.dumps({"ok": False, "error": str(error), "synchronization_status": "not_performed"}, ensure_ascii=False), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""在有限的常见目录中发现本地开源 TTS 模型，不遍历整块磁盘。"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any


WEIGHT_SUFFIXES = (".safetensors", ".npz", ".bin", ".gguf", ".msgpack")
TOKENIZER_FILES = ("tokenizer.json", "tokenizer_config.json", "tokenizer.model", "vocab.json")
TTS_MARKERS = ("tts", "text-to-speech", "text_to_speech", "voice", "cosyvoice", "fish-speech", "fishspeech", "xtts", "bark")
RUNTIME_COMMANDS = ("python", "python3", "python3.10", "python3.11", "python3.12", "python3.13")
RUNTIME_PROBE_MARKER = "__QWEN_RUNTIME_JSON__"
MAX_RUNTIME_CANDIDATES = 40


def load_qwen_models() -> dict[str, Any]:
    path = Path(__file__).resolve().parents[1] / "assets" / "qwen-tts-models.json"
    return json.loads(path.read_text(encoding="utf-8"))


def qwen_recommendation(models: dict[str, Any]) -> dict[str, Any]:
    recommended = models["recommended"]
    smaller = models["smaller_option"]
    return {
        "provider": models["provider"],
        "runtime": models["runtime"],
        "supported_platform": models["supported_platform"],
        "model_id": recommended["model_id"],
        "model_url": recommended["model_url"],
        "approx_size_gb": recommended["approx_size_gb"],
        "smaller_model_id": smaller["model_id"],
        "smaller_model_url": smaller["model_url"],
        "smaller_approx_size_gb": smaller["approx_size_gb"],
        "dependency_install_command": models["dependency_install_command"],
        "download_requires_user_authorization": True,
        "next_step": (
            "先向用户展示模型地址、预计下载量、依赖和目标目录；"
            "只有用户明确同意后，才运行 prepare_qwen_model.py --download --download-authorized"
        ),
    }


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def default_roots() -> list[Path]:
    home = Path.home()
    values: list[Path] = []
    hf_home = os.environ.get("HF_HOME", "").strip()
    if hf_home:
        values.append(Path(hf_home).expanduser())
    values.extend(
        [
            home / ".cache/huggingface/hub",
            home / "Library/Caches/huggingface/hub",
            home / "Models",
            home / "models",
            home / "Documents/models",
            home / "Documents/AI/models",
            home / "Documents/Codex/models",
        ]
    )
    return list(dict.fromkeys(path.resolve() for path in values))


def lexical_absolute(path: Path) -> Path:
    """保留虚拟环境的入口路径；解析符号链接会丢失其 site-packages。"""
    expanded = path.expanduser()
    return expanded if expanded.is_absolute() else Path.cwd() / expanded


def runtime_paths(model_roots: list[Path], explicit: list[Path]) -> list[tuple[Path, str]]:
    candidates: dict[str, tuple[Path, str]] = {}

    def add(path: Path | None, source: str) -> None:
        if path is None or len(candidates) >= MAX_RUNTIME_CANDIDATES:
            return
        candidate = lexical_absolute(path)
        candidates.setdefault(str(candidate), (candidate, source))

    add(Path(sys.executable), "current-python")
    virtual_env = os.environ.get("VIRTUAL_ENV", "").strip()
    if virtual_env:
        add(Path(virtual_env) / "bin/python", "active-virtualenv")
    for name in RUNTIME_COMMANDS:
        found = shutil.which(name)
        if found:
            add(Path(found), f"path:{name}")
    for path in explicit:
        add(path, "explicit")

    home = Path.home()
    environment_roots = [home / ".venvs", home / ".virtualenvs", home / "venvs"]
    environment_roots.extend(root.expanduser().absolute().parent for root in model_roots)
    for root in dict.fromkeys(environment_roots):
        if not root.is_dir():
            continue
        for path in sorted(root.glob("*/bin/python")):
            add(path, "near-model-or-standard-env")
    return list(candidates.values())


def probe_runtime(path: Path, source: str) -> dict[str, Any]:
    result: dict[str, Any] = {
        "path": str(path),
        "source": source,
        "compatible": False,
    }
    if not path.is_file() or not os.access(path, os.X_OK):
        result["error"] = "Python 入口不存在或不可执行"
        return result
    probe_code = """
import importlib.metadata
import json
import sys
import mlx_audio
try:
    package_version = importlib.metadata.version("mlx-audio")
except importlib.metadata.PackageNotFoundError:
    package_version = "unknown"
print("__QWEN_RUNTIME_JSON__" + json.dumps({
    "python_executable": sys.executable,
    "python_version": platform_version if (platform_version := sys.version.split()[0]) else "unknown",
    "mlx_audio_version": package_version,
}))
""".strip()
    try:
        completed = subprocess.run(
            [str(path), "-c", probe_code],
            capture_output=True,
            text=True,
            check=False,
            timeout=10,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        result["error"] = f"运行环境检查失败：{exc}"
        return result
    marker_lines = [line for line in completed.stdout.splitlines() if line.startswith(RUNTIME_PROBE_MARKER)]
    if completed.returncode == 0 and marker_lines:
        try:
            details = json.loads(marker_lines[-1][len(RUNTIME_PROBE_MARKER):])
        except json.JSONDecodeError:
            result["error"] = "运行环境返回了无效检查结果"
        else:
            result.update(details)
            result["compatible"] = True
            return result
    error_text = completed.stderr.strip().splitlines()
    result["error"] = (error_text[-1] if error_text else "当前环境无法导入 mlx_audio")[:300]
    return result


def guess_model_id(path: Path) -> str:
    for parent in (path, *path.parents):
        if parent.name.startswith("models--"):
            return parent.name.removeprefix("models--").replace("--", "/", 1)
    return path.name


def read_identity(path: Path) -> str:
    config_path = path / "config.json"
    values: list[str] = [str(path), guess_model_id(path)]
    try:
        config = json.loads(config_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return " ".join(values).casefold()
    if isinstance(config, dict):
        for key in ("model_type", "architectures", "task", "pipeline_tag"):
            value: Any = config.get(key)
            if isinstance(value, list):
                values.extend(str(item) for item in value)
            elif value is not None:
                values.append(str(value))
    return " ".join(values).casefold()


def inspect_candidate(path: Path, names: set[str]) -> dict[str, Any] | None:
    if "config.json" not in names:
        return None
    has_weights = any(Path(name).suffix.casefold() in WEIGHT_SUFFIXES for name in names)
    has_tokenizer = any(name in names for name in TOKENIZER_FILES)
    if not has_weights or not has_tokenizer:
        return None
    identity = read_identity(path)
    if not any(marker in identity for marker in TTS_MARKERS):
        return None
    is_qwen_tts = "qwen3" in identity and "tts" in identity
    is_mlx = "mlx" in identity
    return {
        "path": str(path.resolve()),
        "model_id_guess": guess_model_id(path),
        "kind": "qwen3-tts-candidate" if is_qwen_tts else "other-open-source-tts",
        "runtime_hint": "mlx-audio-preflight-required" if is_qwen_tts else "requires-user-confirmed-adapter",
        "compatible_with_bundled_runner": is_qwen_tts,
        "mlx_marker_present": is_mlx,
        "config_sha256": sha256(path / "config.json"),
        "required_files_present": True,
    }


def discover(
    roots: list[Path],
    max_depth: int,
    max_directories: int,
    runtime_pythons: list[Path] | None = None,
    qwen_models: dict[str, Any] | None = None,
) -> dict[str, Any]:
    candidates: list[dict[str, Any]] = []
    scanned_directories = 0
    scanned_roots: list[str] = []
    warnings: list[str] = []
    for root in roots:
        root = root.expanduser().resolve()
        if not root.is_dir():
            continue
        scanned_roots.append(str(root))
        for current, dirs, files in os.walk(root, followlinks=False):
            current_path = Path(current)
            depth = len(current_path.relative_to(root).parts)
            dirs[:] = [name for name in dirs if name not in {".git", "node_modules", "__pycache__"}]
            if depth >= max_depth:
                dirs[:] = []
            scanned_directories += 1
            candidate = inspect_candidate(current_path, set(files))
            if candidate is not None:
                candidates.append(candidate)
                dirs[:] = []
            if scanned_directories >= max_directories:
                warnings.append(f"达到目录扫描上限 {max_directories}，如模型在其他位置请显式提供 --search-root")
                break
        if scanned_directories >= max_directories:
            break
    candidates.sort(key=lambda item: (not item["compatible_with_bundled_runner"], item["path"]))
    compatible = [item for item in candidates if item["compatible_with_bundled_runner"]]
    runtime_candidates = [probe_runtime(path, source) for path, source in runtime_paths(roots, runtime_pythons or [])]
    compatible_runtimes = [item for item in runtime_candidates if item["compatible"]]
    if compatible and not compatible_runtimes:
        warnings.append("发现兼容模型，但在有限范围内未发现可导入 mlx_audio 的 Python 运行环境")
    status = "compatible-found" if compatible else "other-found" if candidates else "none-found"
    report = {
        "schema_version": "1.1",
        "status": status,
        "runtime_status": "compatible-runtime-found" if compatible_runtimes else "none-found",
        "recommended_runtime_python": compatible_runtimes[0]["path"] if compatible_runtimes else "",
        "scope": "standard-caches-and-explicit-roots-only",
        "scanned_roots": scanned_roots,
        "scanned_directories": scanned_directories,
        "candidates": candidates,
        "runtime_candidates": runtime_candidates,
        "warnings": warnings,
    }
    if not compatible:
        report["next_action"] = "recommend-qwen-and-request-download-authorization"
        report["qwen_recommendation"] = qwen_recommendation(qwen_models or load_qwen_models())
    elif not compatible_runtimes:
        report["next_action"] = "locate-compatible-runtime-before-installing"
    else:
        report["next_action"] = "preflight-existing-model"
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="发现本机已有的开源 TTS 模型，不执行下载或模型加载")
    parser.add_argument("--search-root", action="append", default=[], type=Path, help="追加或指定模型目录，可重复使用")
    parser.add_argument("--runtime-python", action="append", default=[], type=Path, help="追加已知 Python/虚拟环境入口，可重复使用")
    parser.add_argument("--max-depth", type=int, default=6)
    parser.add_argument("--max-directories", type=int, default=10000)
    parser.add_argument("--output", type=Path, help="模型发现报告 JSON")
    args = parser.parse_args()
    if args.max_depth < 1 or args.max_directories < 1:
        parser.error("扫描深度和目录上限必须大于 0")
    roots = args.search_root or default_roots()
    report = discover(roots, args.max_depth, args.max_directories, args.runtime_python)
    if args.output:
        output = args.output.expanduser().resolve()
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for candidate in report["candidates"]:
        state = "COMPATIBLE" if candidate["compatible_with_bundled_runner"] else "OTHER"
        print(f"{state} {candidate['model_id_guess']} {candidate['path']}")
    for runtime in report["runtime_candidates"]:
        if runtime["compatible"]:
            print(f"RUNTIME {runtime['python_version']} mlx-audio={runtime['mlx_audio_version']} {runtime['path']}")
    if report["status"] == "none-found":
        print("NOT_FOUND 未在标准缓存和指定目录中发现完整开源 TTS 模型")
    elif report["status"] == "other-found":
        print("FOUND_OTHER 发现其他开源 TTS 模型；使用前需要用户确认兼容运行时或适配器")
    else:
        print("PASS 发现可由当前执行器预检的 Qwen3-TTS MLX 模型")
    if report["runtime_status"] == "none-found":
        print("RUNTIME_NOT_FOUND 有模型不等于缺少依赖；请先追加已知 --runtime-python，确认仍无兼容环境后再申请安装")
    recommendation = report.get("qwen_recommendation")
    if recommendation:
        print(
            "QWEN_RECOMMENDED "
            f"{recommendation['model_url']} "
            f"约 {recommendation['approx_size_gb']} GB"
        )
        print(f"QWEN_SMALLER {recommendation['smaller_model_url']} 约 {recommendation['smaller_approx_size_gb']} GB")
        print(f"INSTALL {recommendation['dependency_install_command']}")
        print("AUTHORIZATION_REQUIRED 下载前必须向用户说明目标目录并取得明确同意")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

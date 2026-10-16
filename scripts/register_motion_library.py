#!/usr/bin/env python3
"""核验内置动效并输出项目可用目录；不修改导演计划，不剪辑或生成视频。"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import uuid

ROOT = Path(__file__).resolve().parents[1]


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def local_file(base: Path, name: str) -> Path:
    path = (base / name).resolve()
    if not path.is_relative_to(base.resolve()) or not path.is_file() or path.stat().st_size == 0:
        raise ValueError(f'库文件无效：{name}')
    return path


def register(project: Path, root: Path = ROOT) -> Path:
    project = project.resolve()
    if not project.is_dir():
        raise ValueError('项目目录不存在；请先建立内容制作工程')
    library = root / 'assets/motion-library'
    manifest = json.loads((library / 'library-manifest.json').read_text())
    effects = manifest['effects']
    if not effects or len({item['id'] for item in effects}) != len(effects):
        raise ValueError('动效目录为空或 ID 重复')
    version = manifest.get('version')
    if not isinstance(version, str) or not version.strip():
        raise ValueError('动效清单缺少有效版本')
    # 验证脚本只执行这个模块与工厂；不能给清单中其他文件或入口签发证明。
    for effect in effects:
        implementation = effect.get('implementation')
        if (not isinstance(implementation, dict)
                or implementation.get('path') != 'motion-presets.mjs'
                or implementation.get('entrypoint') != f'createMotionPreset:{effect["id"]}'):
            raise ValueError(f'动效 {effect["id"]} 的实现路径或入口与固定验证脚本不一致')
    dependencies = []
    # 先检查原始发行包摘取文件，再执行本项目固定验证脚本；不运行下载的安装脚本。
    for engine in ('animejs', 'three'):
        vendor = library / 'vendor' / engine
        files = json.loads((vendor / 'files.json').read_text())
        if not files:
            raise ValueError(f'{engine} 缺少原始文件记录')
        for item in files:
            path = local_file(vendor, item['path'])
            if digest(path) != item['sha256']:
                raise ValueError(f'上游文件发生变化：{engine}/{item["path"]}')
            dependencies.append({'path': str(path), 'sha256': digest(path)})
    node = shutil.which('node')
    if not node:
        raise ValueError('需要本地 Node.js 22 或更新版本；当前没有运行验证，不能登记可用')
    command = [node, str(root / 'scripts/verify_motion_library.mjs')]
    result = subprocess.run(command, cwd=root, text=True, capture_output=True, timeout=60)
    if result.returncode:
        raise ValueError('内置动效执行测试失败：' + result.stderr[-2000:] + result.stdout[-2000:])
    report = json.loads(result.stdout)
    if not isinstance(report, dict) or report.get('passed') is not True:
        raise ValueError('内置动效执行报告未整体通过，不登记目录')
    if report.get('version') != version:
        raise ValueError('动效清单版本与实际执行报告版本不一致，不登记目录')
    checked = {item['effectId']: item for item in report['effects']}
    if any(checked.get(item['id'], {}).get('passed') is not True for item in effects):
        raise ValueError('部分动效未通过执行验证，不登记目录')
    output = project / 'motion-library'
    run = output / 'verification' / uuid.uuid4().hex
    log = run / 'execution.json'
    write_json(log, report)
    catalog = []
    for effect in effects:
        implementation = local_file(library, effect['implementation']['path'])
        sha = digest(implementation)
        proof = run / (effect['id'] + '.json')
        write_json(proof, {
            'effect_id': effect['id'], 'implementation_sha256': sha,
            'status': 'passed', 'verification_method': 'execution-test',
            'command': 'node scripts/verify_motion_library.mjs',
            'details': '固定版本运行测试通过；检查端点、中点、乱序定位及数值有效性。未代替实际镜头审片。' + str(checked[effect['id']]['details']),
            'artifact': {'path': str(log), 'sha256': digest(log)},
            'visual_review': 'pending',
        })
        catalog.append({
            'effect_id': effect['id'], 'name': effect['name'],
            'library': 'produce-videos motion presets / ' + effect['engine'],
            'version': manifest['version'] + ' / ' + effect['version'],
            'source_url': 'https://github.com/luqi67677/produce-videos/tree/main/assets/motion-library',
            'license': 'MIT; 上游声明见随包 vendor 许可证',
            'implementation': {'path': str(implementation), 'sha256': sha,
                'entrypoint': effect['implementation']['entrypoint'], 'dependencies': dependencies},
            'availability': {'status': 'verified', 'evidence_path': str(proof), 'evidence_sha256': digest(proof)},
            'purpose': effect['purpose'], 'parameters': effect['parameters'], 'limits': effect['limits'],
            'visual_review': 'pending',
        })
    target = output / 'catalog.json'
    write_json(target, catalog)
    return target


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('project', type=Path)
    args = parser.parse_args()
    try:
        target = register(args.project.expanduser())
    except (OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError) as exc:
        print(f'FAIL {exc}')
        return 1
    print(f'PASS 已生成可用动效目录：{target}')
    print('挑选需要的条目放入 director_plan.effect_catalog；已执行验证，实际镜头审片仍待完成。')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

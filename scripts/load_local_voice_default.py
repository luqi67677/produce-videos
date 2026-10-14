#!/usr/bin/env python3
"""只读用户批准的私有声音配置；不扫描目录，不加载模型，不联网。"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import sys
import wave


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def resolve_path(root: Path, raw: str) -> Path:
    if not isinstance(raw, str) or not raw.strip():
        raise ValueError('配置中的文件路径为空')
    path = Path(raw).expanduser()
    return path if path.is_absolute() else root / path


def load_default(config_path: Path, verify_model_hash: bool = False) -> dict:
    config = json.loads(config_path.read_text(encoding='utf-8'))
    if not isinstance(config, dict):
        raise ValueError('默认声音配置必须是 JSON 对象')
    if config.get('approved') is not True or config.get('locked_by_user') is not True:
        raise ValueError('默认声音未由用户批准')
    if config.get('applies_to') != 'future-produce-videos':
        raise ValueError('默认声音没有跨项目复用授权')
    for key in ('voice_profile', 'authorization_record', 'retention_authorization_record', 'reference_text'):
        if not isinstance(config.get(key), str) or not config[key].strip():
            raise ValueError(f'默认声音缺少 {key}')
    if config.get('skip_voice_auditions') is not True:
        raise ValueError('默认配置未批准直接复用，不能跳过选声')
    root = config_path.parent
    reference = resolve_path(root, config.get('reference_audio', ''))
    if not reference.is_file():
        raise ValueError(f'参考音频不存在：{reference}')
    actual_hash = sha256(reference)
    if actual_hash != config.get('reference_audio_sha256'):
        raise ValueError('参考音频与已批准的 SHA-256 不一致')
    with wave.open(str(reference), 'rb') as audio:
        audio_info = {'duration_seconds': audio.getnframes() / audio.getframerate(),
                      'sample_rate': audio.getframerate(), 'channels': audio.getnchannels()}
    if audio_info['duration_seconds'] <= 0:
        raise ValueError('参考音频为空')
    model = config.get('model')
    generator = config.get('generator')
    if not isinstance(model, dict) or not isinstance(generator, dict):
        raise ValueError('配置缺少 model 或 generator 对象')
    if generator.get('model_type') != 'base':
        raise ValueError('参考音色必须沿用 Base 模型')
    required_params = ('temperature', 'top_k', 'top_p', 'repetition_penalty', 'max_tokens')
    if any(isinstance(generator.get(key), bool) or not isinstance(generator.get(key), (int, float))
           or not math.isfinite(generator[key]) for key in required_params):
        raise ValueError('配置中的生成参数必须是有限数值')
    model_path = resolve_path(root, model.get('path', ''))
    for item in ('config.json', 'tokenizer_config.json', 'speech_tokenizer/config.json'):
        if not (model_path / item).is_file():
            raise ValueError(f'本地模型缺少：{model_path / item}')
    integrity = model.get('integrity', [])
    if not integrity:
        raise ValueError('本地模型缺少已核验的权重清单')
    checked = []
    for item in integrity:
        relative = Path(item['file'])
        if relative.is_absolute() or '..' in relative.parts:
            raise ValueError('模型清单路径必须在模型目录内')
        weight = model_path / relative
        if not weight.is_file() or weight.stat().st_size != item['size']:
            raise ValueError(f'本地模型权重缺失或大小不一致：{weight}')
        if verify_model_hash and sha256(weight) != item['sha256']:
            raise ValueError(f'本地模型权重 SHA-256 不一致：{weight}')
        checked.append({'file': str(relative), 'size': weight.stat().st_size,
                        'sha256_rechecked': verify_model_hash})
    runtime = resolve_path(root, config.get('runtime_python', ''))
    if not runtime.is_file() or not os.access(runtime, os.X_OK):
        raise ValueError(f'已确认的运行环境不存在或无法执行：{runtime}')
    return {'status': 'ready', 'source': 'user-reference', 'voice_profile': config['voice_profile'],
            'approved': True, 'skip_voice_auditions': True,
            'config_path': str(config_path), 'config_sha256': sha256(config_path),
            'authorization_record': config['authorization_record'],
            'retention_authorization_record': config['retention_authorization_record'],
            'reference_audio': str(reference), 'reference_audio_sha256': actual_hash,
            'reference_text': config['reference_text'], 'reference_info': audio_info,
            'reference_config': str(config_path), 'model_id': model['id'],
            'model_url': model.get('url', ''), 'model_path': str(model_path),
            'model_revision': model.get('revision', ''), 'runtime_python': str(runtime),
            'generation_settings': {key: generator[key] for key in required_params},
            'model_files_checked': checked, 'model_load_preflight_required': True,
            'allow_cloud_fallback': False}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', type=Path)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--verify-model-sha256', action='store_true')
    args = parser.parse_args()
    environment = os.environ.get('PRODUCE_VIDEOS_VOICE_CONFIG')
    config_path = args.config or (Path(environment) if environment else None)
    if config_path is None:
        config_path = Path('~/Desktop/配音模型/默认配音配置.json')
    config_path = config_path.expanduser().absolute()
    try:
        if not config_path.exists():
            if args.config or environment:
                raise ValueError(f'指定的默认声音配置不存在：{config_path}')
            result = {'status': 'not-configured', 'config_path': str(config_path)}
        else:
            result = load_default(config_path, args.verify_model_sha256)
        if args.output:
            if args.output.resolve() == config_path.resolve():
                raise ValueError('输出记录不能覆盖默认声音配置')
            if args.output.exists():
                existing = json.loads(args.output.read_text(encoding='utf-8'))
                if (not isinstance(existing, dict)
                        or existing.get('status') != result.get('status')
                        or existing.get('config_path') != result.get('config_path')
                        or existing.get('config_sha256') != result.get('config_sha256')):
                    raise ValueError('项目已有另一份声音记录，请使用新版本路径')
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (OSError, ValueError, KeyError, TypeError, wave.Error) as error:
        print(json.dumps({'status': 'blocked', 'error': str(error)}, ensure_ascii=False), file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())

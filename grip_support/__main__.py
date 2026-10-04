import argparse
import importlib
import json
import subprocess
import sys
from pathlib import Path
from .runtime import ROOT, RunContext, load_config, seed_process


def main():
    parser = argparse.ArgumentParser(description='Gripping/lifting support tools; python -m grip_support COMMAND --help')
    sub = parser.add_subparsers(dest='command', required=True)
    sub.add_parser('setup-check', help='Check installed dependencies and imports')
    sub.add_parser('sim-check', help='Reset/render/step upstream PickCube; not the learner task')
    for name in ('train', 'resume', 'evaluate'):
        p = sub.add_parser(name, help='Run learner core (fails until implemented)')
        p.add_argument('--config', default=str(ROOT / 'configs/grip.json'))
        p.add_argument('--check-only', action='store_true', help='Validate config and report missing core; never train')
        if name != 'train':
            p.add_argument('--checkpoint', required=True, type=Path)
    args = parser.parse_args()
    if args.command == 'setup-check':
        result = subprocess.run(['uv', 'pip', 'check', '--python', sys.executable])
        if result.returncode:
            return result.returncode
        for name in ('torch', 'numpy', 'gymnasium', 'mani_skill.envs', 'sapien'):
            importlib.import_module(name)
            print(f'IMPORT OK: {name}')
        print(f'SETUP OK: {sys.executable}')
        return 0
    if args.command == 'sim-check':
        return subprocess.run([sys.executable, str(ROOT / 'scripts/check_environment.py'), '--output-dir', str(ROOT / 'runs/checks/grip-smoke')], cwd=ROOT).returncode
    config = load_config(args.config)
    core = importlib.import_module(config['core_module'])
    missing = core.missing(config, args.command)
    if missing:
        print('CORE INCOMPLETE: ' + args.command, file=sys.stderr)
        for item in missing:
            print('  - ' + item, file=sys.stderr)
        return 2
    checkpoint = None
    if args.command != 'train':
        checkpoint = RunContext.load(args.checkpoint, config)
    if args.check_only:
        print('READINESS OK (core self-report only; no rollout or training executed)')
        return 0
    seed_process(config['seed'])
    context = RunContext(config, args.command, getattr(args, 'checkpoint', None))
    print(f'RUN: {context.directory}', flush=True)
    context.log('started', mode=args.command)
    try:
        core.run(args.command, config, context, checkpoint)
    except Exception as error:
        context.log('failed', error=repr(error))
        raise
    context.log('completed')
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except Exception as error:
        print(f'ERROR: {type(error).__name__}: {error}', file=sys.stderr)
        sys.exit(1)

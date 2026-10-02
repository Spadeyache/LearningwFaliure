"""Run artifacts and atomic checkpoint I/O, independent of PPO implementation."""
import hashlib
import json
import os
from pathlib import Path
import platform
import random
import subprocess
import sys
from datetime import datetime, timezone
from importlib.metadata import version

ROOT = Path(__file__).resolve().parents[1]


def digest(config):
    return hashlib.sha256(json.dumps(config, sort_keys=True).encode()).hexdigest()


def load_config(path):
    config = json.loads(Path(path).read_text())
    required = {"seed", "run_root", "core_module", "framework", "task", "ppo", "estimator", "evaluation"}
    if not isinstance(config, dict) or set(config) != required:
        raise ValueError(f"Config must contain exactly {sorted(required)}")
    if type(config['seed']) is not int or config['seed'] < 0:
        raise ValueError('seed must be a nonnegative integer')
    for key in ('task', 'ppo', 'estimator', 'evaluation'):
        if not isinstance(config[key], dict):
            raise ValueError(f'{key} must be an object')
    for key in ('run_root', 'core_module'):
        if not isinstance(config[key], str) or not config[key]:
            raise ValueError(f'{key} must be a nonempty string')
    if config['framework'] is not None and not isinstance(config['framework'], str):
        raise ValueError('framework must be null or a string')
    return config


def seed_process(seed):
    import numpy as np
    import torch
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


class RunContext:
    def __init__(self, config, mode, source=None):
        root = Path(config['run_root'])
        if not root.is_absolute():
            root = ROOT / root
        root.mkdir(parents=True, exist_ok=True)
        import tempfile
        self.directory = Path(tempfile.mkdtemp(prefix=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ-') + mode + '-', dir=root))
        self.config = config
        self.log_path = self.directory / 'events.jsonl'
        (self.directory / 'checkpoints').mkdir()
        (self.directory / 'config.json').write_text(json.dumps(config, indent=2) + '\n')
        git = subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=ROOT, capture_output=True, text=True)
        diff = subprocess.run(['git', 'diff', 'HEAD'], cwd=ROOT, capture_output=True, text=True)
        status = subprocess.run(['git', 'status', '--porcelain'], cwd=ROOT, capture_output=True, text=True)
        (self.directory / 'tracked-changes.patch').write_text(diff.stdout)
        metadata = {'mode': mode, 'source_checkpoint': str(source) if source else None,
                    'python': sys.version, 'platform': platform.platform(), 'command': sys.argv,
                    'git_commit': git.stdout.strip(), 'git_status': status.stdout,
                    'packages': {p: version(p) for p in ('torch', 'numpy', 'gymnasium', 'mani-skill', 'sapien')},
                    'environment': {k: os.environ.get(k) for k in ('VK_ICD_FILENAMES', 'MS_ASSET_DIR', 'OMP_NUM_THREADS')}}
        (self.directory / 'metadata.json').write_text(json.dumps(metadata, indent=2) + '\n')

    def log(self, event, **fields):
        with self.log_path.open('a') as stream:
            stream.write(json.dumps({'time': datetime.now(timezone.utc).isoformat(), 'event': event, **fields}, allow_nan=False) + '\n')

    def save(self, name, state):
        """Caller supplies complete serializable learning/estimator/RNG state."""
        import torch
        if Path(name).name != name or not name.endswith('.pt'):
            raise ValueError('Checkpoint name must be a simple .pt filename')
        target = self.directory / 'checkpoints' / name
        import tempfile
        fd, temporary = tempfile.mkstemp(dir=target.parent, suffix='.tmp')
        os.close(fd)
        try:
            torch.save({'schema': 1, 'config_digest': digest(self.config), 'state': state}, temporary)
            os.replace(temporary, target)
        finally:
            Path(temporary).unlink(missing_ok=True)
        self.log('checkpoint_saved', path=str(target))
        return target

    @staticmethod
    def load(path, config):
        import torch
        payload = torch.load(path, map_location='cpu', weights_only=True)
        if payload.get('schema') != 1 or payload.get('config_digest') != digest(config):
            raise ValueError('Checkpoint schema/config mismatch; use original config.json')
        if 'state' not in payload:
            raise ValueError('Checkpoint has no state')
        return payload

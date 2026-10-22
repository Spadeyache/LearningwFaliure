"""Plan/run a reproducible CREST analysis; default invocation only prints a plan."""
from __future__ import annotations

import argparse
from dataclasses import asdict
from datetime import datetime, timezone
import hashlib
from importlib.metadata import version
import json
import os
from pathlib import Path
import platform
import shutil

import numpy as np

from .config import ROOT, describe_plan, load_config
from .core import Evaluation, run_crest
from .optimization import REPSOptimizer
from robot_adaptation.collection.provenance import source_paths as collection_source_paths


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, allow_nan=False).encode()).hexdigest()


def write_json(path, value):
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n")
    temporary.replace(path)


class RolloutBudgetExceeded(RuntimeError):
    pass


class CachedTask:
    """Append-only evaluations, strict resume validation and a physical-run cap."""
    def __init__(self, task, parameters, path, max_rollouts):
        self.task, self.parameters = task, parameters
        self.path, self.max_rollouts = Path(path), max_rollouts
        self.cache = {}
        if self.path.exists():
            # A torn final JSONL write is an error, never silently discarded.
            for line in self.path.read_text().splitlines():
                row = json.loads(line)
                key = digest(row["request"])
                if row["key"] != key or key in self.cache:
                    raise ValueError("Evaluation journal has a bad hash or duplicate request")
                self.cache[key] = Evaluation(**row["result"])

    def validate_context(self, context):
        self.task.validate_context(context)

    def initial_parameters(self, context, seed):
        return self.task.initial_parameters(context, seed)

    def evaluate(self, context, theta, seed):
        request = dict(context=context, theta=self.parameters.validate(theta).tolist(), seed=int(seed))
        key = digest(request)
        if key not in self.cache:
            if len(self.cache) >= self.max_rollouts:
                raise RolloutBudgetExceeded(f"Reached {self.max_rollouts} physical rollouts; journal is resumable")
            result = self.task.evaluate(context, theta, seed)
            with self.path.open("a") as stream:
                stream.write(json.dumps(dict(key=key, request=request, result=asdict(result)),
                                        sort_keys=True, allow_nan=False) + "\n")
                stream.flush()
                os.fsync(stream.fileno())
            self.cache[key] = result
        return self.cache[key]


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=ROOT / "configs/crest_lift.json")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--plan-only", action="store_true")
    mode.add_argument("--run", action="store_true", help="Actually optimize controllers and run simulations")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--only", help="Comma-separated factors to intervene on; others stay nominal")
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--max-rollouts", type=int, help="May be increased when resuming")
    args = parser.parse_args(argv)
    config, contexts, parameters = load_config(args.config, only=args.only.split(",") if args.only else None)
    if args.max_rollouts is not None:
        if args.max_rollouts < 1:
            parser.error("--max-rollouts must be positive")
        config["max_rollouts"] = args.max_rollouts
    print(json.dumps(describe_plan(config, contexts, parameters), indent=2), flush=True)
    if not args.run:
        if args.resume:
            parser.error("--resume requires --run")
        return 0
    if args.output is None:
        parser.error("--run requires --output; choose a fresh run directory")

    # Only actual runs import/initialize the simulator; planning needs no GPU/assets.
    import torch
    from .lifting import LiftingTask
    torch.set_num_threads(1)
    task = LiftingTask(contexts, parameters, **config["task"])
    task.validate_context(contexts.nominal)
    # Snapshot the live implementation and shared simulation dependencies.
    source_paths = {
        p for folder in (ROOT / "experiments/crest", ROOT / "robot_adaptation/simulation",
                         ROOT / "robot_adaptation/collection")
        for p in folder.glob("*.py")
    }
    source_paths.update(p for p in (
        ROOT / "experiments/__init__.py", ROOT / "robot_adaptation/__init__.py",
        ROOT / "robot_adaptation/paths.py") if p.is_file())
    source_paths.update(collection_source_paths())
    sources = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
               for p in sorted(source_paths)}
    runtime = dict(python=platform.python_version(), platform=platform.platform(),
                   versions={name: version(name) for name in ("numpy", "scipy", "torch", "sapien", "mani-skill")},
                   sim_backend="physx_cpu", torch_num_threads=1,
                   asset_dir=os.environ.get("MS_ASSET_DIR"), vulkan_icd=os.environ.get("VK_ICD_FILENAMES"))
    # Raising a cap does not change existing observations or search decisions.
    scientific_config = {k: v for k, v in config.items() if k != "max_rollouts"}
    identity = digest(dict(config=scientific_config, sources=sources, runtime=runtime,
                           context_order=list(contexts.names), parameter_order=list(parameters.names)))
    output = args.output.resolve()
    if output.exists() and not args.resume:
        raise FileExistsError("Output exists; use a fresh directory or --resume")
    if args.resume and not output.exists():
        raise FileNotFoundError("Cannot resume a missing run")
    output.mkdir(parents=True, exist_ok=True)
    # Held descriptor lock survives exceptions and automatically releases on exit.
    import fcntl
    lock = (output / ".run.lock").open("a")
    try:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        manifest_path = output / "manifest.json"
        if args.resume:
            manifest = json.loads(manifest_path.read_text())
            if manifest["identity"] != identity:
                raise ValueError("Resume requires identical scientific settings, sources and runtime")
        else:
            manifest = dict(identity=identity, created_at=datetime.now(timezone.utc).isoformat(),
                            sources=sources, runtime=runtime, status="prepared",
                            paper="https://arxiv.org/abs/2103.16772", config=config)
            for name in sources:
                target = output / "source" / name
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(ROOT / name, target)
        write_json(output / "config.json", config)
        manifest.update(status="running", max_rollouts=config["max_rollouts"])
        write_json(manifest_path, manifest)
        cached = CachedTask(task, parameters, output / "evaluations.jsonl", config["max_rollouts"])

        def progress(record):
            with (output / "events.jsonl").open("a") as stream:
                stream.write(json.dumps(record, sort_keys=True, allow_nan=False) + "\n")
            print(f"{record['kind']} {record.get('factor', record.get('anchor'))}: {record['status']} "
                  f"({len(cached.cache)} rollouts)", flush=True)

        try:
            report = run_crest(task=cached, contexts=contexts, parameters=parameters,
                               optimizer=REPSOptimizer(parameters, **config["optimizer"]),
                               on_record=progress, **config["experiment"])
            report["identity"] = identity
            report["physical_rollouts"] = len(cached.cache)
            write_json(output / "report.json", report)
            write_json(output / "training_examples.json", report["training_examples"])
            write_json(output / "policy_inputs.json", {k: report[k] for k in (
                "context_names", "feature_names", "parameter_names", "solved_anchors",
                "selected_context", "conservative_parents", "reduced_feature_indices",
                "partitioned_feature_indices", "interpretation")})
            manifest["status"] = "complete" if report["solved_anchors"] else "no_solved_anchors"
        except RolloutBudgetExceeded as error:
            manifest.update(status="budget_exhausted", reason=str(error))
            print(str(error), flush=True)
            return 2
        except BaseException as error:
            manifest.update(status="interrupted", reason=f"{type(error).__name__}: {error}")
            raise
        finally:
            manifest["physical_rollouts"] = len(cached.cache)
            write_json(manifest_path, manifest)
        return 0 if manifest["status"] == "complete" else 3
    finally:
        task.close()
        lock.close()


if __name__ == "__main__":
    raise SystemExit(main())

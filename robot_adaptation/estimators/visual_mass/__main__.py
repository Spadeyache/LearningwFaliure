"""Generate initial images, train a mass predictor, and save the results."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import sys

from robot_adaptation.paths import ROOT


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=None,
                        help="New run directory (default: runs/visual_mass/<UTC time>)")
    parser.add_argument("--objects", type=int, default=96)
    parser.add_argument("--views", type=int, default=4)
    parser.add_argument("--image-size", type=int, default=96)
    parser.add_argument("--epochs", type=int, default=80)
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--threads", type=int, default=4)
    parser.add_argument("--device", choices=("auto", "cpu", "cuda"), default="auto")
    args = parser.parse_args()
    if args.objects < 16 or args.objects % 8:
        parser.error("--objects must be at least 16 and divisible by 8")
    if min(args.views, args.epochs, args.batch_size, args.threads) < 1:
        parser.error("--views, --epochs, --batch-size, and --threads must be positive")
    if not 32 <= args.image_size <= 1024:
        parser.error("--image-size must be between 32 and 1024")
    if not 0 <= args.seed < 2**31:
        parser.error("--seed must be in [0, 2**31)")

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S_%f")
    output = (args.output or ROOT / "runs" / "visual_mass" / timestamp).expanduser().resolve()
    output.mkdir(parents=True, exist_ok=False)
    run = {"status": "running", "stage": "generation", "output": str(output),
           "config": {key: value for key, value in vars(args).items() if key != "output"}}

    def save_status() -> None:
        temporary = output / ".run.json.tmp"
        temporary.write_text(json.dumps(run, indent=2) + "\n")
        temporary.replace(output / "run.json")

    save_status()
    # Launching fresh processes keeps simulator resources separate from training.
    # Use the same interpreter and an explicit module path, with no shell parsing.
    project = ROOT
    try:
        subprocess.run([
            sys.executable, "-m", "robot_adaptation.estimators.visual_mass.generate",
            "--output", str(output / "dataset"),
            "--objects", str(args.objects), "--views", str(args.views),
            "--image-size", str(args.image_size), "--seed", str(args.seed),
        ], cwd=project, check=True)
        run["stage"] = "training"
        save_status()
        subprocess.run([
            sys.executable, "-m", "robot_adaptation.estimators.visual_mass.train",
            "--dataset", str(output / "dataset"), "--output", str(output / "model"),
            "--epochs", str(args.epochs), "--batch-size", str(args.batch_size),
            "--seed", str(args.seed), "--threads", str(args.threads),
            "--device", args.device,
        ], cwd=project, check=True)
        run.update(status="complete", stage="complete")
        print(f"Run complete: {output}", flush=True)
    except BaseException as error:
        run.update(status="incomplete", error=str(error))
        raise
    finally:
        save_status()


if __name__ == "__main__":
    main()

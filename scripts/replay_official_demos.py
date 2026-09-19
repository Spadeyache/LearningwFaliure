"""Run the official replay CLI with an explicit CPU renderer in its input metadata."""
import argparse
import json
from pathlib import Path
import subprocess
import sys


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--count", type=int, default=3)
    args = parser.parse_args()
    source = Path("demos/PickCube-v1/motionplanning/trajectory.h5").resolve()
    scratch = Path("checks/replay_input")
    scratch.mkdir(parents=True, exist_ok=True)
    link = scratch / "trajectory.h5"
    if not link.exists():
        link.symlink_to(source)
    elif link.resolve() != source:
        raise FileExistsError(f"{link} points to a different dataset")
    metadata = json.loads(source.with_suffix(".json").read_text())
    # The official CLI exposes sim_backend but not render_backend.
    # Change only a local metadata copy; preserve the official download.
    metadata["env_info"]["env_kwargs"]["render_backend"] = "cpu"
    link.with_suffix(".json").write_text(json.dumps(metadata, indent=2) + "\n")
    subprocess.run([
        sys.executable, "-m", "mani_skill.trajectory.replay_trajectory",
        "--traj-path", str(link), "--use-first-env-state",
        "-b", "physx_cpu", "-o", "rgb", "--shader", "minimal",
        "--count", str(args.count), "--num-envs", "1",
        "--reward-mode", "normalized_dense", "--record-rewards", "--save-traj",
    ], check=True)


if __name__ == "__main__":
    main()

"""Inspect a clean episode without enabling NumPy pickle loading."""
import argparse
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("episode", nargs="?", type=Path,
                        default=Path("data/pickcube/episode_000.npz"))
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    output = args.output or Path("checks") / f"cube_z_{args.episode.stem}.png"
    with np.load(args.episode, allow_pickle=False) as episode:
        for key in sorted(episode.files):
            value = episode[key]
            print(f"{key:48s} shape={str(value.shape):18s} dtype={value.dtype}")
        steps = len(episode["action"])
        for key in ("rgb", "qpos", "qvel", "ee_pose", "cube_pose", "goal_pos"):
            if len(episode[key]) != steps + 1:
                raise ValueError(f"{key} must have T+1 observations")
        for key in ("reward", "success", "terminated", "truncated"):
            if episode[key].shape != (steps,):
                raise ValueError(f"{key} must have T transitions")
        if steps == 0 or not episode["success"][-1]:
            raise ValueError("Episode does not end in success")
        rgb = episode["rgb"]
        if rgb.dtype != np.uint8 or rgb.ndim != 4 or rgb.shape[-1] != 3:
            raise ValueError("Expected RGB uint8 [T+1, H, W, 3]")
        cube_z = episode["cube_pose"][:, 2]
        if not np.isfinite(cube_z).all():
            raise ValueError("Non-finite cube positions")
        lift = float(cube_z.max() - cube_z[0])
        print(f"Transitions: {steps}; final success: {bool(episode['success'][-1])}")
        print(f"Cube z: initial={cube_z[0]:.5f} m, peak={cube_z.max():.5f} m, "
              f"final={cube_z[-1]:.5f} m; peak lift={lift:.5f} m")
        print(f"Lift exceeds 1 cm: {lift > 0.01}")
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.plot(np.arange(steps + 1), cube_z, label="Cube center z")
        ax.axhline(cube_z[0], color="gray", linestyle="--", label="Initial height")
        ax.plot(np.arange(steps + 1), episode["goal_pos"][:, 2],
                linestyle=":", label="Goal z")
        ax.set(xlabel="Control timestep (0 = initial state)",
               ylabel="World z (m)", title=args.episode.stem)
        ax.grid(alpha=0.25)
        ax.legend()
        fig.tight_layout()
        output.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(output, dpi=160)
        plt.close(fig)
        print(f"Saved {output}")


if __name__ == "__main__":
    main()

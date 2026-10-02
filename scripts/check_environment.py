"""Render and step the installed PickCube-v1 environment once."""
import argparse
import json
from pathlib import Path

import gymnasium as gym
import numpy as np
from PIL import Image
import torch
import mani_skill.envs  # Registers PickCube-v1.


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--render-backend", default="cpu")
    parser.add_argument("--output-dir", type=Path, default=Path("checks"))
    args = parser.parse_args()
    env = gym.make(
        "PickCube-v1", num_envs=1, obs_mode="rgb",
        control_mode="pd_joint_pos", sim_backend="physx_cpu",
        render_backend=args.render_backend,
        sensor_configs={"shader_pack": "minimal"},
        human_render_camera_configs={"shader_pack": "minimal"},
    )
    try:
        obs, info = env.reset(seed=0)
        rgb = obs["sensor_data"]["base_camera"]["rgb"][0].cpu().numpy()
        assert rgb.dtype == np.uint8 and rgb.ndim == 3 and rgb.shape[-1] == 3
        assert rgb.max() > rgb.min(), "Camera frame is constant"
        args.output_dir.mkdir(parents=True, exist_ok=True)
        Image.fromarray(rgb).save(args.output_dir / "first_frame.png")
        env.action_space.seed(0)
        _, reward, terminated, truncated, info = env.step(env.action_space.sample())
        print(json.dumps({
            "rgb_shape": list(rgb.shape), "rgb_dtype": str(rgb.dtype),
            "torch": torch.__version__, "cuda_available": torch.cuda.is_available(),
            "sim_backend": env.unwrapped.backend.sim_backend,
            "render_backend": env.unwrapped.backend.render_backend,
            "reward": float(reward.item()), "success": bool(info["success"].item()),
            "sim_freq": env.unwrapped.sim_freq,
            "control_freq": env.unwrapped.control_freq,
        }, indent=2))
    finally:
        env.close()


if __name__ == "__main__":
    main()

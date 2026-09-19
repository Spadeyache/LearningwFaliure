"""Verify an NPZ can reproduce its recorded states with no perturbations."""
import argparse
import json
from pathlib import Path

import gymnasium as gym
import numpy as np
import torch
import mani_skill.envs


def tensor_tree(tree):
    if isinstance(tree, dict):
        return {key: tensor_tree(value) for key, value in tree.items()}
    return torch.as_tensor(tree, dtype=torch.float32)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("episode", nargs="?", type=Path,
                        default=Path("data/pickcube/episode_000.npz"))
    args = parser.parse_args()
    with np.load(args.episode, allow_pickle=False) as data:
        kwargs = json.loads(str(data["env_kwargs_json"]))
        env = gym.make(str(data["env_id"]), **kwargs)
        try:
            env.reset(**json.loads(str(data["reset_kwargs_json"])))
            state = {}
            for key in data.files:
                if key.startswith("reset_state/"):
                    node = state
                    parts = key.split("/")[1:]
                    for part in parts[:-1]:
                        node = node.setdefault(part, {})
                    node[parts[-1]] = torch.from_numpy(data[key].copy())
            base = env.unwrapped
            base.set_state_dict(state)
            base.agent.set_controller_state(
                tensor_tree(json.loads(str(data["initial_controller_json"]))))
            max_error = {key: 0.0 for key in ("qpos", "qvel", "ee_pose", "cube_pose", "goal_pos")}
            rgb_equal = True
            for t in range(len(data["action"]) + 1):
                if t == 0:
                    obs = base.get_obs()
                else:
                    obs, reward, terminated, truncated, info = env.step(data["action"][t - 1])
                    np.testing.assert_allclose(float(reward.item()), data["reward"][t - 1], atol=1e-6)
                    assert bool(info["success"].item()) == bool(data["success"][t - 1])
                    assert bool(terminated.item()) == bool(data["terminated"][t - 1])
                    assert bool(truncated.item()) == bool(data["truncated"][t - 1])
                current = {
                    "qpos": base.agent.robot.get_qpos()[0],
                    "qvel": base.agent.robot.get_qvel()[0],
                    "ee_pose": base.agent.tcp.pose.raw_pose[0],
                    "cube_pose": base.cube.pose.raw_pose[0],
                    "goal_pos": base.goal_site.pose.p[0],
                }
                for key, value in current.items():
                    value = value.cpu().numpy()
                    max_error[key] = max(max_error[key], float(np.max(np.abs(value - data[key][t]))))
                    np.testing.assert_allclose(value, data[key][t], rtol=0, atol=1e-6, err_msg=f"{key} at {t}")
                rgb = obs["sensor_data"]["base_camera"]["rgb"][0].cpu().numpy()
                rgb_equal = rgb_equal and np.array_equal(rgb, data["rgb"][t])
            print(json.dumps({"episode": str(args.episode), "transitions": len(data["action"]),
                              "max_absolute_error": max_error, "rgb_bitwise_equal": rgb_equal,
                              "final_success": bool(info["success"].item())}, indent=2))
        finally:
            env.close()


if __name__ == "__main__":
    main()

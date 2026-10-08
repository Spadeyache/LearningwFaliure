"""Inspect the official example checkpoint, with two cameras and raw data.

This uses upstream PickCube, state observations and the upstream Agent.
It does not import the custom lift task or custom PPO implementation.
"""
from datetime import datetime, timezone
import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace
import sys
import uuid

import gymnasium as gym
import numpy as np
from PIL import Image, ImageDraw
import torch
from mani_skill.envs.tasks.tabletop.pick_cube import PickCubeEnv
from mani_skill.sensors.camera import CameraConfig
from mani_skill.utils import sapien_utils

ROOT = Path(__file__).resolve().parents[3]
RUN_ROOT = ROOT / "runs" / "maniskill_example" / "pick_cube"
SETTINGS = {"checkpoint": None, "episodes": 5, "seed": 1000}
VIEWS = {"front_right_top": "render_camera", "front_left_top": "front_left_top"}


class ViewingTask(PickCubeEnv):
    @property
    def _default_human_render_camera_configs(self):
        original = super()._default_human_render_camera_configs
        eye = list(self.human_cam_eye_pos)
        eye[1] = -eye[1]
        other = CameraConfig("front_left_top", sapien_utils.look_at(eye=eye, target=self.human_cam_target_pos),
                             512, 512, 1, 0.01, 100)
        return [original, other]


def values(tensor):
    return tensor.detach().cpu().reshape(-1).tolist()


def state(task, observation, info):
    return {
        "policy_observation": values(observation),
        "tcp_pose_world_m_wxyz": values(task.agent.tcp_pose.raw_pose),
        "cube_pose_world_m_wxyz": values(task.cube.pose.raw_pose),
        "finger_positions_m": values(task.agent.robot.get_qpos()[:, -2:]),
        "left_contact_force_world_n": values(task.scene.get_pairwise_contact_forces(task.agent.finger1_link, task.cube)),
        "right_contact_force_world_n": values(task.scene.get_pairwise_contact_forces(task.agent.finger2_link, task.cube)),
        "is_grasped": bool(info["is_grasped"].item()),
        "is_obj_placed": bool(info["is_obj_placed"].item()),
        "success": bool(info["success"].item()),
    }


def picture(task, camera, step, snapshot, reward):
    array = task.render_rgb_array(camera_name=camera)[0].cpu().numpy().astype(np.uint8)
    image = Image.fromarray(array)
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, image.width, 45), fill="black")
    draw.multiline_text((5, 5), f"OFFICIAL MANISKILL EXAMPLE | step {step} | reward {reward:.3f}\n"
                        f"Grasp {snapshot['is_grasped']} | at goal {snapshot['is_obj_placed']} | success {snapshot['success']}",
                        fill="white")
    return image


def main(settings=None):
    settings = {**SETTINGS, **(settings or {})}
    checkpoint = settings["checkpoint"]
    if checkpoint is None:
        candidates = [path for path in RUN_ROOT.glob("*/final_ckpt.pt") if (path.parent / "manifest.json").is_file()]
        if not candidates:
            raise FileNotFoundError("Run train_example.py first, or set checkpoint to an example checkpoint")
        checkpoint = max(candidates, key=lambda path: path.stat().st_mtime_ns)
    checkpoint = Path(checkpoint).resolve()
    manifest = json.loads((checkpoint.parent / "manifest.json").read_text())
    if manifest["artifact_origin"] != "official_maniskill_example":
        raise ValueError("This inspector requires an official example checkpoint")
    settings_overrides = manifest["settings_overrides"]
    spec = importlib.util.spec_from_file_location("maniskill_example_upstream", Path(__file__).with_name("ppo_upstream.py"))
    upstream = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = upstream
    spec.loader.exec_module(upstream)
    torch.set_num_threads(4)
    task = ViewingTask(num_envs=1, obs_mode="state", control_mode=settings_overrides["control_mode"],
                       sim_backend="physx_cpu", render_backend="cpu",
                       sensor_configs={"shader_pack": "minimal"}, human_render_camera_configs={"shader_pack": "minimal"})
    # The upstream task uses a 50-step time limit. Keep that same horizon here.
    env = gym.wrappers.TimeLimit(task, max_episode_steps=50)
    spaces = SimpleNamespace(single_observation_space=task.observation_space, single_action_space=task.action_space)
    agent = upstream.Agent(spaces)
    agent.load_state_dict(torch.load(checkpoint, map_location="cpu", weights_only=True))
    agent.eval()
    output = checkpoint.parent / "inspect" / (datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S") + "-" + uuid.uuid4().hex[:8])
    output.mkdir(parents=True, exist_ok=False)
    outcomes = []
    try:
        for episode in range(settings["episodes"]):
            observation, info = env.reset(seed=settings["seed"] + episode)
            initial = state(task, observation, info)
            frames = {view: [picture(task, camera, 0, initial, 0.)] for view, camera in VIEWS.items()}
            for view in VIEWS:
                frames[view][0].save(output / f"episode_{episode + 1:02d}_initial_{view}.png")
            total_reward, success_once = 0., False
            with (output / f"episode_{episode + 1:02d}_steps.jsonl").open("w") as log:
                log.write(json.dumps({"step": 0, "state": initial}) + "\n")
                for step in range(1, 51):
                    before = state(task, observation, info)
                    with torch.no_grad():
                        raw_action = agent.get_action(observation, deterministic=True)
                    action = raw_action.clamp(torch.as_tensor(task.action_space.low), torch.as_tensor(task.action_space.high))
                    observation, reward, terminated, truncated, info = env.step(action)
                    after = state(task, observation, info)
                    reward_value = float(reward.item())
                    total_reward += reward_value
                    success_once |= after["success"]
                    log.write(json.dumps({"step": step, "before": before, "raw_policy_action": values(raw_action),
                                          "applied_action": values(action), "after": after, "reward": reward_value,
                                          "terminated": bool(terminated), "truncated": bool(truncated)}, allow_nan=False) + "\n")
                    for view, camera in VIEWS.items():
                        frames[view].append(picture(task, camera, step, after, reward_value))
                    # Upstream evaluation ignores success termination and runs to horizon.
                    if bool(truncated):
                        break
            for view, images in frames.items():
                images[0].save(output / f"episode_{episode + 1:02d}_{view}.gif", save_all=True,
                               append_images=images[1:], duration=round(1000 / task.control_freq), loop=0)
                images[-1].save(output / f"episode_{episode + 1:02d}_final_{view}.png")
            outcomes.append({"episode": episode + 1, "seed": settings["seed"] + episode, "steps": step,
                             "return": total_reward, "success_once": success_once, "success_at_end": after["success"]})
            print("Example episode:", outcomes[-1], flush=True)
        summary = {"artifact_origin": "official_maniskill_example", "checkpoint": str(checkpoint),
                   "source_commit": manifest["source_commit"], "episodes": outcomes,
                   "success_once_rate": sum(x["success_once"] for x in outcomes) / len(outcomes),
                   "success_at_end_rate": sum(x["success_at_end"] for x in outcomes) / len(outcomes),
                   "inspection_adjustments": ["one CPU environment", "two viewing cameras", "bounded applied actions"],
                   "note": "Small diagnostic sample; task success means holding the cube at the target and being static."}
        (output / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    finally:
        env.close()
    print("Official example inspection:", output)
    return output


if __name__ == "__main__":
    main()

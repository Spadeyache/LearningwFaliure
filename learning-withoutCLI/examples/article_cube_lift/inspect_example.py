"""Watch a saved article-inspired policy without changing its weights.

Each attempt produces two camera GIFs/PNGs, named raw measurements/actions,
reward components, a plot and a summary. Edit SETTINGS and run this file.
"""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from types import SimpleNamespace
import uuid

import gymnasium as gym
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image, ImageDraw
import torch

from lift_env import HORIZON, ORIGIN, ViewingTask
from model import Agent

HERE = Path(__file__).resolve().parent
RUN_ROOT = HERE.parents[2] / "runs" / "article_inspired" / "cube_lift"
SETTINGS = {"checkpoint": None, "episodes": 3, "seed": 1000}
VIEWS = {"front_right_top": "render_camera", "front_left_top": "front_left_top"}


def values(tensor):
    return tensor.detach().cpu().reshape(-1).tolist()


def snapshot(task, observation, info):
    measurements = task.get_obs(info=info, unflattened=True)["extra"]
    components = {key: float(info[key].item()) for key in
                  ("reach_score", "grasp_score", "lift_score", "success_bonus", "task_score")}
    return dict(policy_observation=values(observation),
                measurements={name: values(value) for name, value in measurements.items()},
                distance_m=float(info["distance_m"].item()), clearance_m=float(info["clearance_m"].item()),
                is_grasped=bool(info["is_grasped"].item()), success=bool(info["success"].item()),
                reward_components=components)


def picture(task, camera, step, state, reward):
    pixels = task.render_rgb_array(camera_name=camera)[0].cpu().numpy().astype(np.uint8)
    image = Image.fromarray(pixels)
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, image.width, 57), fill="black")
    draw.multiline_text((5, 5), f"ARTICLE-INSPIRED CUBE LIFT | step {step} | reward {reward:.3f}\n"
                        f"Grasp {state['is_grasped']} | clearance {state['clearance_m']:.3f} m | success {state['success']}\n"
                        f"Finger width {state['measurements']['finger_width_m'][0]:.3f} m", fill="white")
    return image


def plot(states, path, control_freq):
    time = np.arange(len(states)) / control_freq
    figure, axes = plt.subplots(2, 2, figsize=(10, 7), sharex=True)
    axes[0, 0].plot(time, [s["distance_m"] for s in states], label="TCP to cube")
    axes[0, 0].plot(time, [s["clearance_m"] for s in states], label="Cube bottom clearance")
    axes[0, 0].axhline(.08, color="gray", linestyle="--", label="Lift threshold")
    axes[0, 0].set_ylabel("Metres")
    axes[0, 1].plot(time, [s["measurements"]["finger_width_m"][0] for s in states], label="Measured finger width")
    axes[0, 1].set_ylabel("Metres")
    for finger in ("left", "right"):
        axes[1, 0].plot(time, [np.linalg.norm(s["measurements"][finger + "_contact_force_world_n"]) for s in states], label=finger)
    axes[1, 0].set_ylabel("Contact force magnitude (N)")
    for component in ("reach_score", "grasp_score", "lift_score", "success_bonus"):
        axes[1, 1].plot(time, [s["reward_components"][component] for s in states], label=component)
    axes[1, 1].set_ylabel("Reward contribution")
    for axis in axes.flat:
        axis.legend(fontsize=8)
        axis.grid(alpha=.2)
    axes[1, 0].set_xlabel("Seconds")
    axes[1, 1].set_xlabel("Seconds")
    figure.suptitle("ARTICLE-INSPIRED CUBE LIFT — saved policy, no learning")
    figure.tight_layout()
    figure.savefig(path, dpi=150)
    plt.close(figure)


def main(settings=None):
    settings = {**SETTINGS, **(settings or {})}
    if not isinstance(settings["episodes"], int) or settings["episodes"] <= 0:
        raise ValueError("episodes must be a positive integer")
    checkpoint = settings["checkpoint"]
    if checkpoint is None:
        candidates = [p for p in RUN_ROOT.glob("*/final_ckpt.pt") if (p.parent / "manifest.json").is_file()]
        if not candidates:
            raise FileNotFoundError("Run this example's train.py first, or set checkpoint")
        checkpoint = max(candidates, key=lambda p: p.stat().st_mtime_ns)
    checkpoint = Path(checkpoint).resolve()
    manifest = json.loads((checkpoint.parent / "manifest.json").read_text())
    if manifest["artifact_origin"] != ORIGIN:
        raise ValueError("Select an article-inspired cube lift checkpoint")
    for file, key in (("lift_env.py", "task_sha256"), ("model.py", "model_sha256")):
        if hashlib.sha256((HERE / file).read_bytes()).hexdigest() != manifest[key]:
            raise ValueError("Task/model source changed since training; use the saved source or train fresh")
    torch.set_num_threads(4)
    output = checkpoint.parent / "inspect" / (datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S") + "-" + uuid.uuid4().hex[:8])
    output.mkdir(parents=True, exist_ok=False)
    outcomes = []
    for episode in range(settings["episodes"]):
        mass = manifest["masses_kg"][episode % len(manifest["masses_kg"])]
        task = ViewingTask(num_envs=1, masses_kg=(mass,), obs_mode="state",
                           sim_backend="physx_cpu", render_backend="cpu",
                           sensor_configs={"shader_pack": "minimal"}, human_render_camera_configs={"shader_pack": "minimal"})
        env = gym.wrappers.TimeLimit(task, max_episode_steps=HORIZON)
        try:
            spaces = SimpleNamespace(single_observation_space=task.single_observation_space, single_action_space=task.single_action_space)
            agent = Agent(spaces)
            agent.load_state_dict(torch.load(checkpoint, map_location="cpu", weights_only=True))
            agent.eval()
            observation, info = env.reset(seed=settings["seed"] + episode)
            states = [snapshot(task, observation, info)]
            frames = {view: [picture(task, camera, 0, states[0], 0.)] for view, camera in VIEWS.items()}
            prefix = f"episode_{episode + 1:02d}"
            total_reward, success_once = 0., False
            with (output / (prefix + "_steps.jsonl")).open("w") as log:
                log.write(json.dumps(dict(step=0, state=states[0]), allow_nan=False) + "\n")
                for step in range(1, HORIZON + 1):
                    with torch.no_grad():
                        raw_action = agent.get_action(observation, deterministic=True)
                    action = raw_action.clamp(-1, 1)
                    observation, reward, terminated, truncated, info = env.step(action)
                    after = snapshot(task, observation, info)
                    reward_value = float(reward.item())
                    total_reward += reward_value
                    success_once |= after["success"]
                    log.write(json.dumps(dict(step=step, before=states[-1], raw_policy_action=values(raw_action),
                                              applied_action=values(action), after=after, reward=reward_value,
                                              terminated=bool(terminated), truncated=bool(truncated)), allow_nan=False) + "\n")
                    states.append(after)
                    for view, camera in VIEWS.items():
                        frames[view].append(picture(task, camera, step, after, reward_value))
                    # Same fixed-horizon inspection as training; record success at every step.
                    if bool(truncated):
                        break
            for view, images in frames.items():
                images[0].save(output / f"{prefix}_initial_{view}.png")
                images[-1].save(output / f"{prefix}_final_{view}.png")
                images[0].save(output / f"{prefix}_{view}.gif", save_all=True,
                               append_images=images[1:], duration=round(1000 / task.control_freq), loop=0)
            plot(states, output / (prefix + "_measurements.png"), task.control_freq)
            outcome = dict(episode=episode + 1, seed=settings["seed"] + episode, mass_kg=mass,
                           steps=step, episode_return=total_reward, success_once=success_once,
                           success_at_end=states[-1]["success"], grasp_steps=sum(s["is_grasped"] for s in states[1:]),
                           max_clearance_m=max(s["clearance_m"] for s in states))
            outcomes.append(outcome)
            print("Article-inspired episode:", outcome, flush=True)
        finally:
            env.close()
    summary = dict(artifact_origin=ORIGIN, checkpoint=str(checkpoint), article_url=manifest["article_url"],
                   training_settings=manifest["settings"], episodes=outcomes,
                   success_once_rate=sum(s["success_once"] for s in outcomes) / len(outcomes),
                   success_at_end_rate=sum(s["success_at_end"] for s in outcomes) / len(outcomes),
                   inspection_adjustments=["one CPU environment", "two viewing cameras", "deterministic bounded actions"],
                   note="Small diagnostic sample of an adaptation, not the article's trained sorting model.")
    (output / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print("Article-inspired inspection:", output, flush=True)
    return output


if __name__ == "__main__":
    main()

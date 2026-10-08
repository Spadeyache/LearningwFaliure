"""Run a published, already-trained ManiSkill PPO policy. No training here.

First test the model on its original PickCube task, then on our LiftTask.
Edit SETTINGS. The policy keeps its original 42 inputs and native controller;
the added weight feature is discarded when running this original checkpoint.
"""
from datetime import datetime, timezone
from importlib.metadata import version
import hashlib
import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace
import sys
import urllib.request
import uuid

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image, ImageDraw
import torch
from mani_skill.utils.common import flatten_state_dict
from mani_skill.utils.geometry.rotation_conversions import quaternion_to_matrix
from mani_skill.sensors.camera import CameraConfig
from mani_skill.utils import sapien_utils

from inspect_example import ViewingTask, values

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE.parents[1]))
from weighted_lift_v1 import LiftTask

DATASET = "haosulab/ManiSkill_Demonstrations"
REVISION = "d674485bbffdd533914e52d272fdda34c0515608"
MODEL_HASHES = {
    "pd_ee_delta_pos": "0b17b5ed9690ccf83111d0f09af8d1599f69ee7ba0077e1aac48814ac78ce99c",
    "pd_joint_delta_pos": "78959417279892d73e4ed5930a6d8de8626a24eee0ec553dfc6af61391b0b356",
}
SETTINGS = {
    "control_mode": "pd_ee_delta_pos",  # Four actions: XYZ plus finger opening.
    "tasks": ["official_pick_cube", "custom_lift"],
    "episodes": 20,                   # New randomized reset for each attempt.
    "record_episodes": 3,             # Two camera GIFs/PNGs and plots for these.
    "seed": 1000,
    "custom_episode_steps": 100,      # Continue after success to inspect holding.
    "masses_kg": [0.040, 0.064, 0.100],
    "gif_playback_speed": 0.5,        # Half-speed playback; physics is unchanged.
}
VIEWS = {"front_right_top": "render_camera", "front_left_top": "front_left_top"}


class ViewingLift(LiftTask):
    @property
    def _default_human_render_camera_configs(self):
        original = super()._default_human_render_camera_configs
        eye = list(self.human_cam_eye_pos)
        eye[1] = -eye[1]
        return [original, CameraConfig("front_left_top", sapien_utils.look_at(eye=eye, target=self.human_cam_target_pos),
                                       512, 512, 1, 0.01, 100)]


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def download_model(control):
    """Cache the pinned 1.2 MB model; verify its published SHA256 every time."""
    folder = ROOT / "runs" / "maniskill_pretrained" / "pick_cube" / "models" / REVISION
    folder.mkdir(parents=True, exist_ok=True)
    filename = "ppo_" + control + "_ckpt.pt"
    model = folder / filename
    base = "https://huggingface.co/datasets/" + DATASET + "/resolve/" + REVISION + "/demos/PickCube-v1/rl/"
    if not model.exists():
        data = urllib.request.urlopen(base + filename, timeout=60).read()
        if hashlib.sha256(data).hexdigest() != MODEL_HASHES[control]:
            raise ValueError("Downloaded model does not match its published hash")
        temporary = model.with_suffix(".tmp")
        temporary.write_bytes(data)
        temporary.replace(model)
    if sha256(model) != MODEL_HASHES[control]:
        raise ValueError("Cached checkpoint hash mismatch")
    metadata_path = folder / ("trajectory_" + control + ".json")
    if not metadata_path.exists():
        data = urllib.request.urlopen(base + "trajectory.none." + control + ".physx_cuda.json", timeout=60).read()
        metadata_path.write_bytes(data)
    metadata = json.loads(metadata_path.read_text())
    if metadata["env_info"]["env_id"] != "PickCube-v1" or metadata["env_info"]["env_kwargs"]["control_mode"] != control:
        raise ValueError("Published model/environment metadata mismatch")
    return model, metadata, base + filename


def load_agent(task, model):
    spec = importlib.util.spec_from_file_location("pretrained_maniskill_ppo", HERE / "ppo_upstream.py")
    upstream = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = upstream
    spec.loader.exec_module(upstream)
    spaces = SimpleNamespace(single_observation_space=SimpleNamespace(shape=(42,)), single_action_space=task.single_action_space)
    agent = upstream.Agent(spaces)
    agent.load_state_dict(torch.load(model, map_location="cpu", weights_only=True))
    agent.eval()
    return agent


def vector(observation):
    # LiftTask returns a named dictionary. Flatten its INHERITED PickCube fields
    # in their original order, discarding the current task's appended weight feature for this original model.
    result = flatten_state_dict(observation, use_torch=True, device="cpu") if isinstance(observation, dict) else observation
    # The current weighted task appends one feature; this original model ignores it.
    if result.shape == (1, 43):
        result = result[:, :42]
    if result.shape != (1, 42) or not torch.isfinite(result).all():
        raise ValueError("Published checkpoint requires the original 42 finite PickCube state inputs")
    return result


def snapshot(task, observation, info):
    rotation = quaternion_to_matrix(task.cube.pose.q)
    clearance = float((task.cube.pose.p[:, 2] - task.cube_half_size * rotation[:, 2].abs().sum(-1)).item())
    grasp = bool(info["is_grasped"].item())
    scores = {name: float(info[name].item()) for name in ("reach_score", "grasp_score", "lift_score", "task_score") if name in info}
    return dict(policy_observation=values(vector(observation)),
                tcp_pose_world_m_wxyz=values(task.agent.tcp_pose.raw_pose), cube_pose_world_m_wxyz=values(task.cube.pose.raw_pose),
                goal_position_m=values(task.goal_site.pose.p), cube_mass_kg=float(task.cube.mass.item()),
                finger_width_m=float(task.agent.robot.get_qpos()[:, -2:].sum().item()),
                left_contact_force_world_n=values(task.scene.get_pairwise_contact_forces(task.agent.finger1_link, task.cube)),
                right_contact_force_world_n=values(task.scene.get_pairwise_contact_forces(task.agent.finger2_link, task.cube)),
                distance_m=float((task.cube.pose.p - task.agent.tcp_pose.p).norm().item()), clearance_m=clearance,
                is_grasped=grasp, grasped_lift_8cm=grasp and clearance >= .08,
                task_success=bool(info["success"].item()), reward_components=scores)


def picture(task, camera, name, step, state, playback_speed):
    pixels = task.render_rgb_array(camera_name=camera)[0].cpu().numpy().astype(np.uint8)
    image = Image.fromarray(pixels)
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, image.width, 58), fill="black")
    draw.multiline_text((5, 5), f"OFFICIAL PRETRAINED PPO | {name} | step {step}\n"
                        f"Grasp {state['is_grasped']} | clearance {state['clearance_m']:.3f} m | success {state['task_success']}\n"
                        f"Mass {state['cube_mass_kg']:.3f} kg | GIF playback {playback_speed:g}x", fill="white")
    return image


def plot(states, output, frequency):
    time = np.arange(len(states)) / frequency
    fig, axes = plt.subplots(2, 2, figsize=(10, 7), sharex=True)
    axes[0, 0].plot(time, [s["distance_m"] for s in states], label="TCP distance to cube")
    axes[0, 0].plot(time, [s["clearance_m"] for s in states], label="Cube bottom clearance")
    axes[0, 0].axhline(.08, color="gray", linestyle="--", label="8 cm lift")
    axes[0, 0].set_ylabel("Metres")
    axes[0, 1].plot(time, [s["finger_width_m"] for s in states], label="Finger width")
    axes[0, 1].set_ylabel("Metres")
    for side in ("left", "right"):
        axes[1, 0].plot(time, [np.linalg.norm(s[side + "_contact_force_world_n"]) for s in states], label=side)
    axes[1, 0].set_ylabel("Contact force magnitude (N)")
    for name in ("is_grasped", "grasped_lift_8cm", "task_success"):
        axes[1, 1].plot(time, [float(s[name]) for s in states], label=name)
    axes[1, 1].set_ylabel("Condition met")
    for axis in axes.flat:
        axis.legend(fontsize=8)
        axis.grid(alpha=.2)
    for axis in axes[1]:
        axis.set_xlabel("Simulation seconds")
    fig.suptitle("OFFICIAL PRETRAINED PPO — inference only")
    fig.tight_layout()
    fig.savefig(output, dpi=150)
    plt.close(fig)


def main(settings=None):
    settings = {**SETTINGS, **(settings or {})}
    control = settings["control_mode"]
    if control not in MODEL_HASHES:
        raise ValueError("Choose pd_ee_delta_pos or pd_joint_delta_pos with its matching model")
    for key in ("episodes", "custom_episode_steps"):
        if not isinstance(settings[key], int) or settings[key] <= 0:
            raise ValueError(f"{key} must be a positive integer")
    if not isinstance(settings["record_episodes"], int) or settings["record_episodes"] < 0:
        raise ValueError("record_episodes must be a nonnegative integer")
    if not np.isfinite(settings["gif_playback_speed"]) or settings["gif_playback_speed"] <= 0:
        raise ValueError("gif_playback_speed must be positive and finite")
    if not settings["tasks"] or any(task not in ("official_pick_cube", "custom_lift") for task in settings["tasks"]):
        raise ValueError("Choose official_pick_cube and/or custom_lift")
    if not settings["masses_kg"] or any(not np.isfinite(m) or m <= 0 for m in settings["masses_kg"]):
        raise ValueError("masses_kg must contain positive finite masses")
    torch.set_num_threads(4)
    model, metadata, url = download_model(control)
    output = ROOT / "runs" / "maniskill_pretrained" / "pick_cube" / (datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S") + "-" + uuid.uuid4().hex[:8])
    output.mkdir(parents=True, exist_ok=False)
    # Preserve the exact runner alongside the checkpoint/environment provenance.
    runner_source = Path(__file__).read_bytes()
    (output / "runner.py").write_bytes(runner_source)
    manifest = dict(artifact_origin="official_maniskill_pretrained_ppo", checkpoint=str(model), checkpoint_url=url,
                    checkpoint_sha256=sha256(model), dataset_revision=REVISION, published_metadata=metadata,
                    settings=settings, simulator_backend="physx_cpu", policy_inputs=42,
                    runner_sha256=hashlib.sha256(runner_source).hexdigest(),
                    ppo_source_sha256=sha256(HERE / "ppo_upstream.py"), lift_task_sha256=sha256(HERE / "weighted_lift_v1.py"),
                    versions={package: version(package) for package in ("torch", "mani_skill", "sapien")},
                    adaptations=["CPU simulation/rendering", "two inspection cameras", "preserved v1 floating-goal task with standard reward and varied masses; original model ignores weight", "continue after success to inspect holding"],
                    status="running")
    manifest_path = output / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
    results = {}
    try:
        for name in settings["tasks"]:
            folder = output / name
            folder.mkdir()
            task = ViewingTask(num_envs=1, obs_mode="state", control_mode=control, sim_backend="physx_cpu", render_backend="cpu",
                               sensor_configs={"shader_pack": "minimal"}, human_render_camera_configs={"shader_pack": "minimal"}) if name == "official_pick_cube" else ViewingLift(control_mode=control)
            outcomes = []
            try:
                agent = load_agent(task, model)
                horizon = metadata["env_info"]["max_episode_steps"] if name == "official_pick_cube" else settings["custom_episode_steps"]
                for episode in range(settings["episodes"]):
                    options = {} if name == "official_pick_cube" else {"mass_kg": settings["masses_kg"][episode % len(settings["masses_kg"]) ]}
                    observation, info = task.reset(seed=settings["seed"] + episode, options={**options, "reconfigure": True})
                    states = [snapshot(task, observation, info)]
                    record = episode < settings["record_episodes"]
                    frames = {view: [picture(task, camera, name, 0, states[0], settings['gif_playback_speed'])] for view, camera in VIEWS.items()} if record else {}
                    total_reward = 0.
                    prefix = f"episode_{episode + 1:02d}"
                    with (folder / (prefix + "_steps.jsonl")).open("w") as log:
                        log.write(json.dumps(dict(step=0, state=states[0]), allow_nan=False) + "\n")
                        for step in range(1, horizon + 1):
                            with torch.no_grad():
                                raw_action = agent.get_action(vector(observation), deterministic=True)
                            action = raw_action.clamp(-1, 1)
                            observation, reward, terminated, truncated, info = task.step(action)
                            after = snapshot(task, observation, info)
                            total_reward += float(reward.item())
                            log.write(json.dumps(dict(step=step, before=states[-1], raw_policy_action=values(raw_action), applied_action=values(action),
                                                      after=after, reward=float(reward.item()), environment_terminated=bool(terminated),
                                                      evaluation_time_limit=step == horizon), allow_nan=False) + "\n")
                            states.append(after)
                            if record:
                                for view, camera in VIEWS.items():
                                    frames[view].append(picture(task, camera, name, step, after, settings['gif_playback_speed']))
                    if record:
                        # Save a still of the highest confirmed grasp, even if
                        # the policy later releases or drops the cube.
                        peak_step = max(range(len(states)), key=lambda i: states[i]['clearance_m'] if states[i]['is_grasped'] else -float('inf'))
                        for view, images in frames.items():
                            images[0].save(folder / f"{prefix}_initial_{view}.png")
                            images[-1].save(folder / f"{prefix}_final_{view}.png")
                            images[peak_step].save(folder / f"{prefix}_peak_grasp_{view}.png")
                            images[0].save(folder / f"{prefix}_{view}.gif", save_all=True, append_images=images[1:],
                                           duration=round(1000 / task.control_freq / settings["gif_playback_speed"]), loop=0)
                        plot(states, folder / (prefix + "_measurements.png"), task.control_freq)
                    outcome = dict(episode=episode + 1, seed=settings["seed"] + episode, mass_kg=states[0]["cube_mass_kg"],
                                   steps=horizon, episode_return=total_reward, success_once=any(s["task_success"] for s in states[1:]),
                                   success_at_end=states[-1]["task_success"], grasp_once=any(s["is_grasped"] for s in states[1:]),
                                   grasp_at_end=states[-1]["is_grasped"], final_clearance_m=states[-1]["clearance_m"],
                                   grasped_lift_8cm_once=any(s["grasped_lift_8cm"] for s in states[1:]),
                                   grasped_lift_8cm_at_end=states[-1]["grasped_lift_8cm"], max_clearance_m=max(s["clearance_m"] for s in states),
                                   grasp_steps=sum(s["is_grasped"] for s in states[1:]))
                    outcomes.append(outcome)
                    print(name, outcome, flush=True)
                summary = dict(episodes=outcomes, **{key + "_rate": sum(s[key] for s in outcomes) / len(outcomes)
                                                   for key in ("success_once", "success_at_end", "grasp_once", "grasp_at_end", "grasped_lift_8cm_once", "grasped_lift_8cm_at_end")})
                (folder / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
                results[name] = summary
            finally:
                task.close()
        (output / "summary.json").write_text(json.dumps(dict(artifact_origin=manifest["artifact_origin"], checkpoint=str(model), tasks=results), indent=2) + "\n")
        manifest["status"] = "complete"
    except BaseException:
        manifest["status"] = "interrupted_or_failed"
        raise
    finally:
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
    print("Official pretrained evaluation:", output, flush=True)
    return output


if __name__ == "__main__":
    main()

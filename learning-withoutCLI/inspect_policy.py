"""Watch a saved policy and compare its measurements with the lift reward.

Run this file directly. Change SETTINGS below; no command-line arguments needed.
This uses the policy without training it or changing its checkpoint.
"""

from datetime import datetime, timezone
import json
from pathlib import Path
import uuid

import numpy as np
from PIL import Image, ImageDraw
import torch
from mani_skill.sensors.camera import CameraConfig
from mani_skill.utils import sapien_utils

from lift_task import LiftTask, controller_action, normal_forces, read_inputs
from train_ppo import load_checkpoint


ROOT = Path(__file__).resolve().parent.parent
SETTINGS = {
    "checkpoint": None,  # None selects the newest completed training run's final.pt.
    "seed": 0,
    "mass_kg": 0.064,
    "episode_steps": None,  # None uses the checkpoint's episode limit.
    "deterministic": True,  # Use the mean action; False samples as training does.
    "output_root": ROOT / "runs" / "inspect",
}


class InspectionTask(LiftTask):
    """Same physics and reward, with two cameras for viewing the same attempt."""

    @property
    def _default_human_render_camera_configs(self):
        original = super()._default_human_render_camera_configs
        # Mirror the existing elevated camera across the table's centre line.
        eye = list(self.human_cam_eye_pos)
        eye[1] = -eye[1]
        other = CameraConfig(
            "front_left_top", sapien_utils.look_at(eye=eye, target=self.human_cam_target_pos),
            512, 512, 1, 0.01, 100,
        )
        return [original, other]


VIEWS = {"front_right_top": "render_camera", "front_left_top": "front_left_top"}


def numbers(value):
    """Convert a tensor snapshot to ordinary numbers for the saved log."""
    return value.detach().cpu().reshape(-1).tolist()


def snapshot(env, inputs, vector, info):
    # All these measurements describe the SAME state, before another action.
    return {
        "inputs": {name: numbers(value) for name, value in inputs.items()},
        "input_vector": numbers(vector),
        "normal_forces_n": numbers(normal_forces(env, inputs)),
        **{name: float(info[name].item()) for name in (
            "distance_m", "clearance_m", "reach_score", "grasp_score",
            "lift_score", "task_score",
        )},
        "is_grasped": bool(info["is_grasped"].item()),
        "success": bool(info["success"].item()),
    }


def frame(env, state, step, mass, camera_name):
    # Rendering is for us; images are never passed into the policy.
    rgb = env.render_rgb_array(camera_name=camera_name)[0].cpu().numpy().astype(np.uint8)
    image = Image.fromarray(rgb).convert("RGB")
    draw = ImageDraw.Draw(image)
    text = (
        f"Step {step} | mass {mass:.3f} kg | grasp {state['is_grasped']} | success {state['success']}\n"
        f"Distance {state['distance_m']:.3f} m | clearance {state['clearance_m']:.3f} m\n"
        f"Reward: reach {state['reach_score']:.3f} + grasp {state['grasp_score']:.3f}"
        f" + lift {state['lift_score']:.3f} = {state['task_score']:.3f}\n"
        f"Finger normal forces: {state['normal_forces_n'][0]:.2f}, {state['normal_forces_n'][1]:.2f} N"
    )
    draw.rectangle((0, 0, image.width, 65), fill="black")
    draw.multiline_text((5, 5), text, fill="white", spacing=2)
    return image


def main(settings=None):
    settings = {**SETTINGS, **(settings or {})}
    checkpoint = settings["checkpoint"]
    if checkpoint is None:
        candidates = list((ROOT / "runs" / "learning").glob("*/final.pt"))
        if not candidates:
            raise FileNotFoundError("Train first, or set checkpoint to an existing saved .pt file")
        checkpoint = max(candidates, key=lambda path: path.stat().st_mtime_ns) # max find the most recent modified file.
    checkpoint = Path(checkpoint).resolve()
    agent, saved = load_checkpoint(checkpoint)
    limit = settings["episode_steps"] or saved["settings"]["episode_steps"]
    if not isinstance(limit, int) or limit <= 0:
        raise ValueError("episode_steps must be a positive integer")
    mass = float(settings["mass_kg"])
    if not np.isfinite(mass) or mass <= 0:
        raise ValueError("mass_kg must be positive and finite")
    torch.set_num_threads(4)
    torch.manual_seed(settings["seed"])
    run_name = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S") + "-" + uuid.uuid4().hex[:8]
    output = Path(settings["output_root"]) / run_name
    output.mkdir(parents=True, exist_ok=False)
    frames = {view: [] for view in VIEWS}
    env = InspectionTask(settings=saved["reward_settings"], control_mode="pd_ee_pose")
    try:
        observation, info = env.reset(seed=settings["seed"], options={"mass_kg": mass})
        inputs, vector = read_inputs(env, observation)
        initial = snapshot(env, inputs, vector, info)
        for view, camera in VIEWS.items():
            frames[view].append(frame(env, initial, 0, mass, camera))
            frames[view][0].save(output / f"initial_{view}.png")
        total_reward = 0.0
        max_clearance = initial["clearance_m"]
        grasp_steps = 0
        with (output / "steps.jsonl").open("w") as log:
            log.write(json.dumps({"kind": "reset", "step": 0, "state": initial}) + "\n")
            for step in range(1, limit + 1):
                before = snapshot(env, inputs, vector, info)
                # Use the saved network. There is no optimizer or learning call.
                with torch.no_grad():
                    action = agent.get_action(vector, deterministic=settings["deterministic"])
                command, targets = controller_action(env, inputs, action, saved["settings"])
                observation, reward, terminated, truncated, info = env.step(command)
                inputs, vector = read_inputs(env, observation)
                after = snapshot(env, inputs, vector, info)
                reward_value = float(reward.item())
                if not np.isclose(reward_value, after["task_score"]) or not np.isclose(
                    reward_value, sum(after[name] for name in ("reach_score", "grasp_score", "lift_score"))
                ):
                    raise AssertionError("Returned reward does not match its recorded components")
                timed_out = bool(truncated.item()) or step >= limit
                record = {
                    "kind": "transition", "step": step,
                    "before": before, "policy_action": numbers(action),
                    "controller_targets": {name: numbers(value) for name, value in targets.items()},
                    "simulator_command": numbers(command), "after": after,
                    "reward": reward_value, "terminated": bool(terminated.item()),
                    "truncated": timed_out,
                }
                log.write(json.dumps(record, allow_nan=False) + "\n")
                for view, camera in VIEWS.items():
                    frames[view].append(frame(env, after, step, mass, camera))
                total_reward += reward_value
                max_clearance = max(max_clearance, after["clearance_m"])
                grasp_steps += int(after["is_grasped"])
                if bool(terminated.item()) or timed_out:
                    break
        # Animated GIF works with existing Pillow; no video encoder install needed.
        duration_ms = round(1000 / env.control_freq)
        for view, images in frames.items():
            images[0].save(output / f"attempt_{view}.gif", save_all=True,
                           append_images=images[1:], duration=duration_ms, loop=0)
            images[-1].save(output / f"final_{view}.png")
        summary = {
            "checkpoint": str(checkpoint), "seed": settings["seed"], "mass_kg": mass,
            "deterministic": settings["deterministic"], "steps": step,
            "episode_return": total_reward, "success": after["success"],
            "terminated": bool(terminated.item()), "truncated": timed_out,
            "grasp_steps": grasp_steps, "max_clearance_m": max_clearance,
            "frame_duration_ms": duration_ms,
            "views": list(VIEWS),
            "note": "One diagnostic attempt, not an estimate of success rate. Reset frame is frame 0; transition step N ends at frame N.",
        }
        (output / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
        print("Checkpoint:", checkpoint)
        print("Inspection:", output)
        print(f"Steps={step} success={after['success']} grasp_steps={grasp_steps} "
              f"max_clearance={max_clearance:.4f} m")
    finally:
        env.close()
    return output


if __name__ == "__main__":
    main()

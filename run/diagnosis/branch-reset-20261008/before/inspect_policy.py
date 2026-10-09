"""INSPECTION AND WEIGHT TEST: run after training; no weights are changed.

Use identical reset seeds for every mass and input condition. Compare the actual
weight input against the same policy given a fixed 40 g estimate, while the
physical cube mass varies across the training range. Edit SETTINGS for other
masses. Force traces and cube motion relative to the fingers help inspect grip. GIFs, plots,
raw measurements and paired summaries are saved under runs/inspect/.
"""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import uuid
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image, ImageDraw
import torch
from mani_skill.sensors.camera import CameraConfig
from mani_skill.utils import sapien_utils
from lift_task import ENV_SETTINGS, HORIZON, LiftTask, ORIGIN, normal_forces, read_inputs, WEIGHT_INPUT_INDEX
from train_ppo import load_checkpoint, latest_checkpoint

ROOT = Path(__file__).resolve().parent.parent
SETTINGS = {
    "checkpoint": None,          # Newest completed 45-input/five-action grip-aware model.
    "seed": 1000,
    "masses_kg": ENV_SETTINGS["masses_kg"],  # Match the fine-tuning range; edit for heavier stress tests.
    "episodes_per_mass": 10,      # Ten matched starts at each physical mass.
    "weight_inputs": ["true", "nominal"],
    "nominal_mass_kg": 0.040,     # Tell the policy 40 g in the nominal condition.
    "episode_steps": HORIZON,     # Whole attempts; increase to 100 to watch holding longer.
    "record_episodes_per_mass": 1,
    "record_weight_inputs": ["true", "nominal"],  # Record both sides of the comparison.
    "gif_playback_speed": 0.5,
    "output_root": str(ROOT / "runs" / "inspect"),
}
VIEWS = {"front_right_top": "render_camera", "front_left_top": "front_left_top"}


class InspectionTask(LiftTask):
    @property
    def _default_human_render_camera_configs(self):
        original = super()._default_human_render_camera_configs
        eye = list(self.human_cam_eye_pos)
        eye[1] = -eye[1]
        return [original, CameraConfig("front_left_top", sapien_utils.look_at(eye=eye, target=self.human_cam_target_pos),
                                       512, 512, 1, .01, 100)]


def numbers(value):
    return value.detach().cpu().reshape(-1).tolist()


def policy_inputs(vector, mode, gravity, nominal_mass):
    result = vector.clone()
    if mode == "nominal":
        result[:, WEIGHT_INPUT_INDEX] = nominal_mass * gravity
    elif mode != "true":
        raise ValueError("Choose true or nominal weight input")
    return result


def snapshot(env, obs, info):
    inputs, vector = read_inputs(env, obs)
    return dict(cube_in_tcp_position_m=numbers((env.agent.tcp_pose.inv() * env.cube.pose).p), inputs={name: numbers(value) for name, value in inputs.items()}, input_vector=numbers(vector),
                normal_forces_n=numbers(normal_forces(env)), mass_kg=float(env.cube.mass.item()),
                finger_width_m=float(env.agent.robot.get_qpos()[:, -2:].sum().item()),
                cube_pose= numbers(env.cube.pose.raw_pose), goal_position_m=numbers(env.goal_site.pose.p),
                **{key: float(info[key].item()) for key in ("distance_m", "goal_distance_m", "clearance_m",
                    "reach_score", "grasp_score", "goal_score", "static_score", "success_bonus", "task_score",
                    "grip_force_cost", "reward_total", "grip_limit_n")},
                is_grasped=bool(info["is_grasped"].item()), success=bool(info["success"].item()),
                held_goal_success=bool(info["held_goal_success"].item()))


def frame(env, state, step, camera, mode, reported_mass):
    image = Image.fromarray(env.render_rgb_array(camera_name=camera)[0].cpu().numpy().astype(np.uint8))
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, image.width, 90), fill="black")
    draw.multiline_text((5, 5), f"WEIGHTED MANISKILL PPO | step {step} | mass {state['mass_kg']:.3f} kg\n"
                        f"Input {mode} | reported mass {reported_mass:.3f} kg\n"
                        f"Motor limit {state['grip_limit_n']:.2f} N/finger\n"
                        f"Grasp {state['is_grasped']} | held goal {state['held_goal_success']}\n"
                        f"Goal distance {state['goal_distance_m']:.3f} m | clearance {state['clearance_m']:.3f} m", fill="white")
    return image


def plot(states, folder, frequency, mode, reported_mass):
    time = np.arange(len(states)) / frequency
    fig, axes = plt.subplots(3, 2, figsize=(10, 10), sharex=True)
    axes[0, 0].plot(time, [s["goal_distance_m"] for s in states], label="Cube to floating goal")
    axes[0, 0].plot(time, [s["distance_m"] for s in states], label="TCP to cube")
    axes[0, 0].axhline(.025, color="gray", linestyle="--", label="Goal tolerance")
    axes[0, 0].set_ylabel("Metres")
    for key in ("reach_score", "grasp_score", "goal_score", "static_score", "success_bonus", "task_score", "grip_force_cost", "reward_total"):
        axes[0, 1].plot(time, [s[key] for s in states], label=key)
    axes[0, 1].set_ylabel("Normalized reward")
    forces = np.asarray([s["normal_forces_n"] for s in states])
    for index, side in enumerate(("left", "right")):
        axes[1, 0].plot(time, forces[:, index], label=side)
    axes[1, 0].set_ylabel("Finger compression (N)")
    for key in ("is_grasped", "success", "held_goal_success"):
        axes[1, 1].plot(time, [float(s[key]) for s in states], label=key)
    axes[1, 1].set_ylabel("Condition met")
    axes[2, 0].plot(time, [s["grip_limit_n"] for s in states], label="Requested motor limit")
    axes[2, 0].plot(time, forces.mean(-1), label="Mean measured compression")
    axes[2, 0].set_ylabel("Newtons")
    relative = np.asarray([s["cube_in_tcp_position_m"] for s in states])
    for i, direction in enumerate(("X", "Y", "Z")):
        axes[2, 1].plot(time, relative[:, i], label=f"Cube in finger frame: {direction}")
    axes[2, 1].set_ylabel("Relative position (m)")
    for axis in axes.flat:
        axis.grid(alpha=.2)
        axis.legend(fontsize=7)
    for axis in axes[2]:
        axis.set_xlabel("Simulation seconds")
    fig.suptitle(f"Actual {states[0]['mass_kg']*1000:.0f} g | reported {reported_mass*1000:.0f} g ({mode}) — inference only")
    fig.tight_layout()
    fig.savefig(folder / "measurements.png", dpi=150)
    plt.close(fig)



def plot_success_rates(groups, settings, output):
    """Compare final grasped-at-goal success across physical mass and input conditions."""
    masses = settings["masses_kg"]
    modes = settings["weight_inputs"]
    x = np.arange(len(masses))
    width = .8 / len(modes)
    fig, axis = plt.subplots(figsize=(9, 5))
    for index, mode in enumerate(modes):
        rows = [next(g for g in groups if g["mass_kg"] == mass and g["weight_input"] == mode)
                for mass in masses]
        positions = x + (index - (len(modes)-1)/2) * width
        rates = [100 * g["held_goal_at_end_rate"] for g in rows]
        label = "Correct weight" if mode == "true" else f'Reported {settings["nominal_mass_kg"]*1000:.0f} g'
        bars = axis.bar(positions, rates, width, label=label)
        for bar, row in zip(bars, rows):
            successes = round(row["held_goal_at_end_rate"] * row["episodes"])
            axis.text(bar.get_x()+bar.get_width()/2, bar.get_height()+2,
                      f'{successes}/{row["episodes"]}', ha="center", fontsize=10)
    axis.set_xticks(x, [f"{mass*1000:.0f} g" for mass in masses])
    axis.set_xlabel("Actual physical cube mass")
    axis.set_ylabel("Held at floating goal at end (%)")
    axis.set_ylim(0, 115)
    axis.set_yticks([0, 20, 40, 60, 80, 100])
    axis.grid(axis="y", alpha=.2)
    axis.set_axisbelow(True)
    axis.legend()
    fig.suptitle("Weight mismatch stress test — same trained policy and matched starts")
    trained = settings["_training_masses_kg"]
    fig.text(.5, .015, "Training masses: " + ", ".join(f"{m*1000:.0f} g" for m in trained)
             + "; masses outside this list test performance beyond training.", ha="center", fontsize=9)
    fig.tight_layout(rect=(0, .05, 1, .96))
    fig.savefig(output / "success_rates.png", dpi=150)
    plt.close(fig)


def plot_grip_strength(groups, settings, output):
    """Measured contact force and requested limit are different quantities."""
    fig, axes = plt.subplots(1, 2, figsize=(11, 4), sharex=True)
    for mode in settings["weight_inputs"]:
        rows = [g for g in groups if g["weight_input"] == mode]
        label = "Correct weight" if mode == "true" else f'Reported {settings["nominal_mass_kg"]*1000:.0f} g'
        for axis, key in zip(axes, ("mean_finger_force_n_while_lifted", "mean_strength_limit_n_while_lifted")):
            axis.plot([g["mass_kg"]*1000 for g in rows],
                      [g[key] if g[key] is not None else np.nan for g in rows], "o-", label=label)
            axis.set_xlabel("Actual cube mass (g)")
            axis.set_ylabel("Newtons per finger")
            axis.grid(alpha=.2)
            axis.legend()
    axes[0].set_title("Measured compression during lifted contact")
    axes[1].set_title("Requested motor limit during lifted contact")
    fig.suptitle("Grip-aware policy: force usage alongside success")
    fig.text(.5, .01, "Each point averages qualifying episodes; missing points mean no lifted contact. Compare success rates too.",
             ha="center", fontsize=8)
    fig.tight_layout(rect=(0,.05,1,.92))
    fig.savefig(output / "grip_strength_by_mass.png", dpi=150)
    plt.close(fig)


def main(settings=None):
    settings = {**SETTINGS, **(settings or {})}
    for key in ("episodes_per_mass", "episode_steps"):
        if not isinstance(settings[key], int) or settings[key] <= 0:
            raise ValueError(f"{key} must be a positive integer")
    if not isinstance(settings["record_episodes_per_mass"], int) or settings["record_episodes_per_mass"] < 0:
        raise ValueError("record_episodes_per_mass must be nonnegative")
    if not settings["masses_kg"] or any(not np.isfinite(m) or m <= 0 for m in settings["masses_kg"]):
        raise ValueError("Choose positive finite masses")
    if not settings["weight_inputs"] or any(mode not in ("true", "nominal") for mode in settings["weight_inputs"]):
        raise ValueError("Choose true and/or nominal input conditions")
    if any(mode not in ("true", "nominal") for mode in settings["record_weight_inputs"]):
        raise ValueError("Record true and/or nominal input conditions")
    if not np.isfinite(settings["gif_playback_speed"]) or settings["gif_playback_speed"] <= 0:
        raise ValueError("Choose a positive finite playback speed")
    if not np.isfinite(settings["nominal_mass_kg"]) or settings["nominal_mass_kg"] <= 0:
        raise ValueError("nominal_mass_kg must be positive and finite")
    checkpoint = settings["checkpoint"]
    if checkpoint is None:
        checkpoint = latest_checkpoint()
    checkpoint = Path(checkpoint).resolve()
    torch.set_num_threads(4)
    agent, saved = load_checkpoint(checkpoint)
    output = Path(settings["output_root"]) / (datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S") + "-" + uuid.uuid4().hex[:8])
    output.mkdir(parents=True, exist_ok=False)
    outcomes, paired_starts = [], {}
    manifest = dict(artifact_origin=ORIGIN + "_inspection", checkpoint=str(checkpoint),
                    checkpoint_sha256=hashlib.sha256(checkpoint.read_bytes()).hexdigest(), settings=settings,
                    training_manifest=saved, status="running")
    manifest_path = output / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2)+"\n")
    try:
        for mass in settings["masses_kg"]:
            env = InspectionTask(masses_kg=saved["settings"]["masses_kg"], goal_clearance_m=saved["settings"]["goal_clearance_m"],
                                 grip_force_limits_n=saved["settings"]["grip_force_limits_n"],
                                 grip_force_cost=saved["settings"]["grip_force_cost"])
            gravity = float(torch.as_tensor(env.scene.px.get_config().gravity).norm())
            try:
                for mode in settings["weight_inputs"]:
                    reported_mass = mass if mode == "true" else settings["nominal_mass_kg"]
                    for episode in range(settings["episodes_per_mass"]):
                        seed = settings["seed"] + episode
                        torch.manual_seed(seed)
                        obs, info = env.reset(seed=seed, options={"mass_kg": mass, "reconfigure": True})
                        initial = snapshot(env, obs, info)
                        # Match all 42 original inputs across conditions and masses.
                        reset_hash = hashlib.sha256(np.asarray(initial["input_vector"][:42], dtype=np.float32).tobytes()).hexdigest()
                        if seed in paired_starts and paired_starts[seed] != reset_hash:
                            raise AssertionError("Reset states differ; weight comparison would not be controlled")
                        paired_starts[seed] = reset_hash
                        folder = output / f"mass_{mass:.3f}" / mode / f"episode_{episode+1:02d}"
                        folder.mkdir(parents=True)
                        record = mode in settings["record_weight_inputs"] and episode < settings["record_episodes_per_mass"]
                        states = [initial]
                        frames = {view: [frame(env, initial, 0, cam, mode, reported_mass)] for view, cam in VIEWS.items()} if record else {}
                        total = 0.
                        with (folder / "steps.jsonl").open("w") as log:
                            log.write(json.dumps(dict(step=0, state=initial, reset_hash=reset_hash, reported_mass_kg=reported_mass), allow_nan=False)+"\n")
                            for step in range(1, settings["episode_steps"]+1):
                                _, vector = read_inputs(env, obs)
                                fed = policy_inputs(vector, mode, gravity, settings["nominal_mass_kg"])
                                with torch.no_grad():
                                    raw = agent.get_action(fed, deterministic=True)
                                action = raw.clamp(-1, 1)
                                obs, reward, terminated, truncated, info = env.step(action)
                                state = snapshot(env, obs, info)
                                if not np.isclose(float(reward.item()), state["reward_total"], atol=1e-6):
                                    raise AssertionError("Reward components do not match simulator reward")
                                total += float(reward.item())
                                log.write(json.dumps(dict(step=step, reported_mass_kg=reported_mass, policy_inputs=numbers(fed), raw_action=numbers(raw),
                                                          action=numbers(action), reward=float(reward.item()), state=state,
                                                          environment_terminated=bool(terminated.item()), evaluation_time_limit=step==settings["episode_steps"]), allow_nan=False)+"\n")
                                states.append(state)
                                if record:
                                    for view, cam in VIEWS.items():
                                        frames[view].append(frame(env, state, step, cam, mode, reported_mass))
                        if record:
                            peak = min(range(len(states)), key=lambda i: states[i]["goal_distance_m"] if states[i]["is_grasped"] else float("inf"))
                            for view, images in frames.items():
                                images[0].save(folder / f"initial_{view}.png")
                                images[-1].save(folder / f"final_{view}.png")
                                images[peak].save(folder / f"closest_held_goal_{view}.png")
                                images[0].save(folder / f"attempt_{view}.gif", save_all=True, append_images=images[1:],
                                               duration=round(1000/env.control_freq/settings["gif_playback_speed"]), loop=0)
                            plot(states, folder, env.control_freq, mode, reported_mass)
                        held_states = [s for s in states[1:] if s["is_grasped"] and s["clearance_m"] > .03]
                        mean_force = float(np.mean([np.mean(s["normal_forces_n"]) for s in held_states])) if held_states else None
                        mean_limit = float(np.mean([s["grip_limit_n"] for s in held_states])) if held_states else None
                        grasp_loss = any(a["is_grasped"] and a["clearance_m"] > .03 and not b["is_grasped"]
                                         for a,b in zip(states[1:], states[2:]))
                        outcome = dict(mean_finger_force_n_while_lifted=mean_force,
                                       mean_strength_limit_n_while_lifted=mean_limit, lifted_contact_steps=len(held_states),
                                       grasp_loss_after_lift=grasp_loss,mass_kg=mass, reported_mass_kg=reported_mass, weight_input=mode, seed=seed, reset_hash=reset_hash,
                                       mass_seen_in_training=any(np.isclose(mass,m) for m in saved["settings"]["masses_kg"]),
                                       episode_return=total, success_once=any(s["success"] for s in states[1:]),
                                       success_at_end=states[-1]["success"], held_goal_once=any(s["held_goal_success"] for s in states[1:]),
                                       held_goal_at_end=states[-1]["held_goal_success"], grasp_at_end=states[-1]["is_grasped"],
                                       final_goal_distance_m=states[-1]["goal_distance_m"], final_clearance_m=states[-1]["clearance_m"])
                        outcomes.append(outcome)
                        print(outcome, flush=True)
            finally:
                env.close()
        groups = []
        for mass in settings["masses_kg"]:
            for mode in settings["weight_inputs"]:
                rows = [r for r in outcomes if r["mass_kg"] == mass and r["weight_input"] == mode]
                groups.append(dict(mass_kg=mass, reported_mass_kg=mass if mode == "true" else settings["nominal_mass_kg"], weight_input=mode, episodes=len(rows),
                                   **{key+"_rate": sum(r[key] for r in rows)/len(rows) for key in
                                      ("success_once","success_at_end","held_goal_once","held_goal_at_end","grasp_at_end")}))
        for group in groups:
            rows = [r for r in outcomes if r["mass_kg"] == group["mass_kg"] and r["weight_input"] == group["weight_input"]]
            group["grasp_loss_after_lift_rate"] = sum(r["grasp_loss_after_lift"] for r in rows)/len(rows)
            for key in ("mean_finger_force_n_while_lifted", "mean_strength_limit_n_while_lifted"):
                valid = [r[key] for r in rows if r[key] is not None]
                group[key] = float(np.mean(valid)) if valid else None
            group["episodes_with_lifted_contact"] = sum(r["lifted_contact_steps"] > 0 for r in rows)
        plot_grip_strength(groups, settings, output)
        (output / "summary.json").write_text(json.dumps(dict(episodes=outcomes, grouped_rates=groups,
            interpretation="Compare paired true vs nominal weight inputs. A higher true-input rate supports use of weight information; equality does not prove adaptation. Force statistics are conditional on lifted contact, not proof of adaptation. Grasp loss can include opening or dropping, not confirmed slipping. No memory or weight estimation is implemented."), indent=2)+"\n")
        plot_success_rates(groups, {**settings, "_training_masses_kg": saved["settings"]["masses_kg"]}, output)
        manifest["status"] = "complete"
    except BaseException:
        manifest["status"] = "interrupted_or_failed"
        raise
    finally:
        manifest_path.write_text(json.dumps(manifest, indent=2)+"\n")
    print("Weighted inspection and paired weight test:", output, flush=True)
    return output


if __name__ == "__main__":
    main()

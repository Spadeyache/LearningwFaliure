"""Deploy an initial-image mass estimate through a saved policy in simulation.

One raw initial RGB image determines the mass estimate. That estimate is held
fixed for the episode; no optimizer, failure update or second reset is involved.
Actual object properties define the simulated scene and separate evaluation logs.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
from importlib.metadata import version
import json
import math
from pathlib import Path
import platform
import shutil
import time

import numpy as np
from PIL import Image
import torch

from robot_adaptation.paths import ROOT
from robot_adaptation.estimators.visual_mass.generate import (
    CAMERA_EYE, CAMERA_TARGET, CAMERA_FOV_RAD, SIDE_RANGE_M,
)
from robot_adaptation.estimators.visual_mass.model import (
    image_to_tensor, load_estimator, predict_mass,
)
from .environment import VisualPolicyEnv
from .policy import load_policy, policy_grip_limits, inject_mass_estimate, WEIGHT_INPUT_INDEX


DEFAULT_CONFIG = ROOT / "configs/visual_mass_deployment.json"
CONFIG_KEYS = {
    "estimator_checkpoint", "policy_checkpoint", "cube_sizes_m", "density_kg_m3",
    "object_xy_m", "object_yaw_rad", "static_friction", "dynamic_friction",
    "finger_friction", "table_friction", "goal_clearance_m", "episode_steps",
    "start_seed", "threads", "video_stride",
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _write_json(path: Path, value: dict) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n")
    temporary.replace(path)


def _checkpoint_path(value: str | Path) -> Path:
    path = Path(value).expanduser()
    return (path if path.is_absolute() else ROOT / path).resolve()


def validate_config(config: dict) -> dict:
    if not isinstance(config, dict):
        raise ValueError("Deployment config must be a JSON object")
    if set(config) != CONFIG_KEYS:
        raise ValueError(f"Config keys must be {sorted(CONFIG_KEYS)}")
    if not isinstance(config["estimator_checkpoint"], str) or not config["estimator_checkpoint"]:
        raise ValueError("estimator_checkpoint must name a saved estimator")
    if config["policy_checkpoint"] is not None and (
        not isinstance(config["policy_checkpoint"], str) or not config["policy_checkpoint"]
    ):
        raise ValueError("policy_checkpoint must be a path, 'latest', or null")
    sizes = config["cube_sizes_m"]
    if not isinstance(sizes, list) or not sizes:
        raise ValueError("cube_sizes_m must be a nonempty list")
    numeric = ["density_kg_m3", "object_yaw_rad", "static_friction", "dynamic_friction",
               "finger_friction", "table_friction", "goal_clearance_m"]
    for value in [*(config[key] for key in numeric), *sizes]:
        if isinstance(value, bool) or not isinstance(value, (float, int)) or not math.isfinite(value):
            raise ValueError("Physical settings must be finite numbers")
    if config["density_kg_m3"] <= 0 or not 0.025 < config["goal_clearance_m"] <= 0.4:
        raise ValueError("Use positive density and goal_clearance_m in (0.025, 0.4]")
    if any(not SIDE_RANGE_M[0] <= side <= SIDE_RANGE_M[1] for side in sizes):
        raise ValueError("Cube sizes must stay in the estimator's 0.025–0.075 m visual range")
    for key in ("static_friction", "dynamic_friction", "finger_friction", "table_friction"):
        if config[key] < 0:
            raise ValueError(f"{key} must be nonnegative")
    if config["dynamic_friction"] > config["static_friction"]:
        raise ValueError("dynamic_friction must not exceed static_friction")
    xy = config["object_xy_m"]
    if (not isinstance(xy, list) or len(xy) != 2 or
            any(isinstance(v, bool) or not isinstance(v, (float, int)) or
                not math.isfinite(v) or abs(v) > 0.01 for v in xy)):
        raise ValueError("object_xy_m must contain two values within the trained ±0.01 m range")
    for key in ("episode_steps", "threads", "video_stride", "start_seed"):
        if type(config[key]) is not int or config[key] < (0 if key == "start_seed" else 1):
            raise ValueError(f"Invalid {key}")
    if config["start_seed"] >= 2**31:
        raise ValueError("start_seed must fit a nonnegative 31-bit seed")
    return config


def load_config(path: str | Path = DEFAULT_CONFIG) -> dict:
    return validate_config(json.loads(Path(path).expanduser().read_text()))


def _source_snapshot(output: Path) -> dict:
    package = ROOT / "robot_adaptation"
    sources = {package / "__init__.py", package / "paths.py",
               package / "estimators/__init__.py"}
    for folder in (package / "runtime", package / "simulation", package / "policy",
                   package / "estimators/visual_mass"):
        sources.update(folder.rglob("*.py"))
        sources.update(folder.rglob("*LICENSE*"))
    hashes = {}
    for source in sorted(sources):
        relative = source.relative_to(ROOT)
        target = output / "source" / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        hashes[relative.as_posix()] = _sha256(source)
    return hashes


def _row(tensor) -> np.ndarray:
    return tensor.detach().cpu().numpy()[0].copy()


def _bool(value) -> bool:
    return bool(value.item()) if hasattr(value, "item") else bool(value)


def _assert_weight(observation: torch.Tensor, mass: float, gravity: float) -> None:
    expected = torch.tensor(mass, dtype=torch.float32) * torch.tensor(gravity, dtype=torch.float32)
    if observation.shape != (1, 45) or not torch.isfinite(observation).all():
        raise RuntimeError("Expected one finite 45-value policy observation")
    actual = observation[0, WEIGHT_INPUT_INDEX].detach().cpu()
    if not torch.isclose(actual, expected, atol=1e-7, rtol=1e-6):
        raise RuntimeError("Policy weight input no longer matches the visual estimate")


@torch.inference_mode()
def _run_episode(folder: Path, *, index: int, side: float, seed: int, config: dict,
                 estimator, estimator_metadata: dict, policy, grip_limits: tuple,
                 record_video: bool, stop_on_success: bool) -> dict:
    started = time.perf_counter()
    folder.mkdir()
    report = {"status": "running", "episode": index, "seed": seed,
              "estimate_source": "initial raw RGB only", "estimate_updates": 0}
    _write_json(folder / "episode.json", report)
    env = None
    try:
        yaw = config["object_yaw_rad"]
        properties = {
            "shape": "cube", "size_xyz_m": [side] * 3,
            "mass_kg": config["density_kg_m3"] * side**3,
            "static_friction": config["static_friction"],
            "dynamic_friction": config["dynamic_friction"],
            "finger_friction": config["finger_friction"],
            "table_friction": config["table_friction"],
            "initial_pose_world": [*config["object_xy_m"], side / 2,
                                   math.cos(yaw / 2), 0.0, 0.0, math.sin(yaw / 2)],
        }
        # The initial placeholder is independent of actual mass. It is replaced
        # before the first policy call; it is never used to select an action.
        env = VisualPolicyEnv(properties, reported_mass_kg=0.04,
                              goal_clearance_m=config["goal_clearance_m"],
                              grip_force_limits_n=grip_limits,
                              image_size=estimator_metadata["image_size"])
        observation, info = env.reset(seed=seed, options={"reconfigure": True})
        rgb = env.capture_initial_rgb()
        image_path = folder / "initial.png"
        Image.fromarray(rgb).save(image_path)
        pixels = image_to_tensor(image_path, estimator_metadata["image_size"]).unsqueeze(0)
        mass = float(predict_mass(
            estimator, pixels, log_mass_mean=estimator_metadata["log_mass_mean"],
            log_mass_std=estimator_metadata["log_mass_std"],
        ).cpu().item())
        env.set_mass_estimate(mass)
        gravity = env.gravity_m_s2
        observation = inject_mass_estimate(observation, mass, gravity)
        _assert_weight(observation, mass, gravity)
        # Ground truth is read for reporting only, after prediction/injection.
        actual = env.physics_readback()
        input_weight = float(observation[0, WEIGHT_INPUT_INDEX].item())
        report.update(predicted_mass_kg=mass, supplied_weight_n=input_weight,
                      gravity_m_s2=gravity, image_sha256=_sha256(image_path),
                      actual_physics=actual,
                      mass_absolute_error_g=abs(mass - float(actual["mass_kg"])) * 1000)
        _write_json(folder / "episode.json", report)

        observations = [_row(observation)]
        object_poses = [_row(env.cube.pose.raw_pose)]
        tcp_poses = [_row(env.agent.tcp_pose.raw_pose)]
        states = [_row(env.agent.robot.get_qpos())]
        raw_actions, applied_actions, rewards, terminated_flags, truncated_flags = [], [], [], [], []
        successes, grasped, motor_limits = [], [], []
        frames = []
        if record_video:
            frames.append(Image.fromarray(_row(env.render_rgb_array()).astype(np.uint8)))
        # No reset takes place here: the image and policy act on the same scene.
        for step in range(config["episode_steps"]):
            _assert_weight(observation, mass, gravity)
            raw = policy.get_action(observation, deterministic=True)
            if raw.shape != (1, 5) or not torch.isfinite(raw).all():
                raise RuntimeError("Policy must produce five finite actions")
            applied = raw.clamp(-1, 1)
            observation, reward, terminated, truncated, info = env.step(applied)
            _assert_weight(observation, mass, gravity)
            raw_actions.append(_row(raw))
            applied_actions.append(_row(applied))
            rewards.append(float(reward.item()))
            terminated_flags.append(_bool(terminated))
            truncated_flags.append(_bool(truncated))
            successes.append(_bool(info["success"]))
            grasped.append(_bool(info["is_grasped"]))
            observations.append(_row(observation))
            object_poses.append(_row(env.cube.pose.raw_pose))
            tcp_poses.append(_row(env.agent.tcp_pose.raw_pose))
            states.append(_row(env.agent.robot.get_qpos()))
            motor_limits.append(float(env.agent.controller.controllers["gripper"].force_limit_n.item()))
            # Native task success sets terminated=True. As in collection.rollout,
            # continue that success signal to the configured evaluation horizon
            # unless the caller explicitly requested a short first-success clip.
            should_stop = truncated_flags[-1] or (
                terminated_flags[-1] and (stop_on_success or not successes[-1]))
            if record_video and ((step + 1) % config["video_stride"] == 0
                                 or should_stop
                                 or step + 1 == config["episode_steps"]):
                frames.append(Image.fromarray(_row(env.render_rgb_array()).astype(np.uint8)))
            if should_stop:
                break
        vectors = np.asarray(observations, dtype=np.float32)
        np.savez_compressed(
            folder / "trajectory.npz", policy_observations=vectors,
            estimated_weight_input_n=vectors[:, WEIGHT_INPUT_INDEX],
            actions_raw=np.asarray(raw_actions), actions_applied=np.asarray(applied_actions),
            rewards=np.asarray(rewards), terminated=np.asarray(terminated_flags),
            truncated=np.asarray(truncated_flags), success=np.asarray(successes),
            is_grasped=np.asarray(grasped), motor_limit_n=np.asarray(motor_limits),
            actual_object_pose_world_m_wxyz=np.asarray(object_poses),
            tcp_pose_world_m_wxyz=np.asarray(tcp_poses), joint_position_rad_m=np.asarray(states),
        )
        if frames:
            frames[-1].save(folder / "final.png")
            frames[0].save(folder / "rollout.gif", save_all=True, append_images=frames[1:],
                           duration=max(1, round(1000 * config["video_stride"] / env.control_freq)), loop=0)
        final_error = float(torch.linalg.norm(env.cube.pose.p - env.goal_site.pose.p).item())
        terminal_success_steps = 0
        for success in reversed(successes):
            if not success:
                break
            terminal_success_steps += 1
        terminal_grasp_steps = 0
        for grasp in reversed(grasped):
            if not grasp:
                break
            terminal_grasp_steps += 1
        report.update(
            status="complete", steps=len(raw_actions),
            success_final=successes[-1], success_any=any(successes),
            grasped_final=grasped[-1], final_goal_error_m=final_error,
            final_clearance_m=float((env.cube.pose.p[:, 2] - env.support_height()).item()),
            peak_finger_compression_n=float(vectors[:, 43:45].max()),
            max_motor_limit_per_finger_n=max(motor_limits),
            simulated_seconds=len(raw_actions) / env.control_freq,
            full_horizon_completed=len(raw_actions) == config["episode_steps"],
            first_success_step=next((i + 1 for i, success in enumerate(successes) if success), None),
            terminal_success_steps=terminal_success_steps,
            terminal_success_seconds=terminal_success_steps / env.control_freq,
            terminal_grasp_steps=terminal_grasp_steps,
            terminal_grasp_seconds=terminal_grasp_steps / env.control_freq,
            ended_by=("step_budget" if len(raw_actions) == config["episode_steps"] else
                      "truncated" if truncated_flags[-1] else "terminated"),
            wall_time_seconds=time.perf_counter() - started,
            initial_state_sha256=hashlib.sha256(
                np.concatenate([object_poses[0], tcp_poses[0], states[0]]).tobytes()).hexdigest(),
        )
        _write_json(folder / "episode.json", report)
        return report
    except BaseException as error:
        report.update(status="incomplete", error=f"{type(error).__name__}: {error}")
        _write_json(folder / "episode.json", report)
        raise
    finally:
        if env is not None:
            env.close()


def run_deployment(config: dict, *, output: str | Path | None = None,
                   episodes: int | None = None, record_video: bool = False,
                   stop_on_success: bool = False) -> dict:
    """Run independent episodes using frozen initial estimates and frozen policies."""
    started = time.perf_counter()
    # Validate programmatic callers through the same configuration contract.
    config = validate_config(config)
    count = len(config["cube_sizes_m"]) if episodes is None else episodes
    if type(count) is not int or count < 1 or config["start_seed"] + count > 2**31:
        raise ValueError("episodes must be positive with seeds within 31 bits")
    torch.set_num_threads(config["threads"])
    estimator_path = _checkpoint_path(config["estimator_checkpoint"])
    estimator, estimator_metadata, _ = load_estimator(estimator_path, device="cpu")
    estimator.requires_grad_(False)
    selection = config["policy_checkpoint"]
    policy, policy_metadata, policy_path = load_policy(
        None if selection in (None, "latest") else _checkpoint_path(selection))
    limits = policy_grip_limits(policy_metadata)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S_%f")
    destination = (_checkpoint_path(output) if output is not None
                   else ROOT / "runs/deployment" / timestamp)
    destination.mkdir(parents=True, exist_ok=False)
    manifest = {
        "schema_version": "visual_mass_deployment_v1", "status": "running",
        "config": config, "episodes_requested": count, "record_video": record_video,
        "stop_on_success": stop_on_success,
        "rollout_rule": "continue task success to step budget; stop on truncation or nonsuccess termination"
                        if not stop_on_success else "stop at first termination/truncation",
        "estimator_checkpoint": str(estimator_path), "estimator_sha256": _sha256(estimator_path),
        "policy_checkpoint": str(policy_path), "policy_sha256": _sha256(policy_path),
        "policy_architecture": policy_metadata["policy_architecture"],
        "policy_training_settings": policy_metadata["settings"],
        "estimated_weight_observation_index": WEIGHT_INPUT_INDEX,
        "estimator_input": "one raw initial RGB image only",
        "estimate_update_rule": "fixed during episode; recompute for each reset",
        "actual_properties_usage": "scene construction and evaluation logs only",
        "camera": {"eye_m": CAMERA_EYE, "target_m": CAMERA_TARGET,
                   "fov_rad": CAMERA_FOV_RAD, "image_size": estimator_metadata["image_size"]},
        "runtime": {"python": platform.python_version(), "sim_backend": "physx_cpu",
                    "versions": {name: version(name) for name in
                                 ("torch", "numpy", "pillow", "mani-skill", "sapien")}},
        "interpretation": "integration demo; not a controlled comparison of policy improvement",
        "episodes": [],
    }
    try:
        manifest["source_sha256"] = _source_snapshot(destination)
        _write_json(destination / "config.json", config)
        _write_json(destination / "manifest.json", manifest)
        print(f"Deployment output: {destination}", flush=True)
        for index in range(count):
            side = config["cube_sizes_m"][index % len(config["cube_sizes_m"])]
            report = _run_episode(
                destination / f"episode_{index:03d}", index=index, side=side,
                seed=config["start_seed"] + index, config=config, estimator=estimator,
                estimator_metadata=estimator_metadata, policy=policy, grip_limits=limits,
                record_video=record_video, stop_on_success=stop_on_success,
            )
            manifest["episodes"].append(report)
            _write_json(destination / "manifest.json", manifest)
            print(f"Episode {index + 1}/{count}: predicted {report['predicted_mass_kg'] * 1000:.2f} g; "
                  f"final success={report['success_final']}", flush=True)
        rows = manifest["episodes"]
        summary = {"episodes": len(rows), "successes_final": sum(r["success_final"] for r in rows),
                   "successes_any": sum(r["success_any"] for r in rows),
                   "mass_mae_g": float(np.mean([r["mass_absolute_error_g"] for r in rows])),
                   "elapsed_seconds": time.perf_counter() - started,
                   "interpretation": manifest["interpretation"]}
        _write_json(destination / "summary.json", summary)
        manifest.update(status="complete", summary=summary)
        print(f"Saved deployment run: {destination}", flush=True)
    except BaseException as error:
        manifest.update(status="incomplete", error=f"{type(error).__name__}: {error}")
        raise
    finally:
        _write_json(destination / "manifest.json", manifest)
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--output", type=Path, help="Fresh output folder (default: runs/deployment/<UTC time>)")
    parser.add_argument("--estimator-checkpoint", type=Path)
    parser.add_argument("--policy-checkpoint", help="Saved compatible policy path, or latest")
    parser.add_argument("--episodes", type=int, help="Default: one episode per configured cube size")
    parser.add_argument("--record-video", action="store_true", help="Also save a GIF per episode")
    parser.add_argument("--stop-on-success", action="store_true",
                        help="Stop at first task success (default: finish the step budget to observe holding)")
    args = parser.parse_args()
    try:
        config = load_config(args.config)
        if args.estimator_checkpoint is not None:
            config["estimator_checkpoint"] = str(args.estimator_checkpoint)
        if args.policy_checkpoint is not None:
            config["policy_checkpoint"] = args.policy_checkpoint
        run_deployment(config, output=args.output, episodes=args.episodes,
                       record_video=args.record_video, stop_on_success=args.stop_on_success)
    except (ValueError, FileNotFoundError, FileExistsError) as error:
        parser.error(str(error))


if __name__ == "__main__":
    main()

"""Shared episode runner for the current fixed-weight collection.

The command-line entry point is failure_collection.varied.
"""
from dataclasses import asdict
import hashlib
from importlib.metadata import version
import json
import os
from pathlib import Path
import platform
import subprocess
import numpy as np
import torch
from . import SCHEMA_VERSION
from .recording import EpisodeRecorder, first
from .schema import validate_episode

ROOT = Path(__file__).resolve().parents[1]


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, allow_nan=False).encode()).hexdigest()


def write_json(path, value):
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n")
    temporary.replace(path)


def rollout(env, policy, seed, config, *, video_path=None):
    env.physics_step_callback = None
    # Teleport-only resets can retain PhysX contact solver history despite an
    # identical visible state. Rebuild each scene before every matched attempt.
    observation, info = env.reset(seed=seed, options={"reconfigure": True})
    recorder = EpisodeRecorder(env, config["contact_threshold_n"])
    recorder.snapshot(observation, info, initial=True)
    def serializable(value):
        if isinstance(value, dict):
            return {key: serializable(v) for key, v in value.items()}
        return value.detach().cpu().numpy().tolist() if hasattr(value, "detach") else np.asarray(value).tolist()
    reset_state = serializable(env.get_state_dict())
    frames = []
    if video_path is not None:
        from PIL import Image
        frames.append(Image.fromarray(first(env.render_rgb_array()).astype(np.uint8)))
    initial_pose = first(env.cube.pose.raw_pose)
    goal = first(env.goal_site.pose.p)
    env.physics_step_callback = recorder.physics_step
    try:
        active_controller_config = {name: asdict(controller.config)
                                    for name, controller in env.agent.controller.controllers.items()}
        for step in range(config["episode_steps"]):
            raw = policy(observation)
            applied = raw.clamp(-1, 1).clone()
            recorder.begin_action()
            observation, reward, terminated, truncated, info = env.step(applied)
            recorder.end_action(raw, applied, reward, terminated, truncated)
            recorder.snapshot(observation, info)
            if video_path is not None and (step + 1) % 2 == 0:
                frames.append(Image.fromarray(first(env.render_rgb_array()).astype(np.uint8)))
        data, outcome = recorder.finish()
    finally:
        env.physics_step_callback = None
    physical = env.physics_readback()
    for name in ("shape", "size_xyz_m", "mass_kg", "weight_n", "com_offset_m", "com_pose_object_m_wxyz",
                 "inertia_principal_kg_m2", "gravity_world_m_s2", "linear_damping", "angular_damping", "inertia_model"):
        data["label__" + name] = np.asarray(physical[name])
    for material_name in ("static_friction", "dynamic_friction", "restitution"):
        data["label__object_" + material_name] = np.asarray(physical["object_materials"][0][material_name])
        data["label__finger_" + material_name] = np.asarray([v[0][material_name] for v in physical["finger_materials"]])
        data["label__table_" + material_name] = np.asarray(physical["table_materials"][0][material_name])
    data.update({
        "label__initial_object_pose_world_m_wxyz": initial_pose,
        "label__goal_position_world_m": goal,
        "input__goal_position_world_m": goal.copy(),
        "label__seed": np.asarray(seed, dtype=np.int64),
        "label__reset_state_json": np.asarray(json.dumps(reset_state, sort_keys=True)),
        "label__reset_state_hash": np.asarray(digest(reset_state)),
        "meta__physics_readback_json": np.asarray(json.dumps(physical, sort_keys=True)),
        "meta__schema_version": np.asarray(getattr(env, "episode_schema_version", SCHEMA_VERSION)),
        "meta__simulation_frequency_hz": np.asarray(env.sim_freq),
        "meta__control_frequency_hz": np.asarray(env.control_freq),
        "meta__contact_threshold_n": np.asarray(config["contact_threshold_n"]),
        "meta__lift_threshold_m": np.asarray(0.02),
        "meta__ideal_sensor_proxies": np.asarray(True),
        "meta__continue_after_success": np.asarray(True),
        "meta__fresh_scene_reset": np.asarray(True),
        "meta__environment": np.asarray(getattr(env, "collection_description", "CollectionEnv(PickCube-v1), stock success")),
        "meta__controller_config_json": np.asarray(json.dumps(active_controller_config, default=str, sort_keys=True)),
        "meta__recovery_capability_json": np.asarray(json.dumps({"supported": True, "reason": "no_correction"}, sort_keys=True)),
        "meta__simulation_config_json": np.asarray(json.dumps(asdict(env.sim_config), default=str, sort_keys=True)),
    })
    from .events import episode_events
    if hasattr(env, "reported_mass_kg"):
        data["input__reported_mass_kg"] = np.asarray(env.reported_mass_kg)
    data.update(episode_events(data))
    if video_path is not None:
        Path(video_path).parent.mkdir(parents=True, exist_ok=True)
        frames[0].save(video_path, save_all=True, append_images=frames[1:],
                       duration=round(2000 / env.control_freq), loop=0)
    validate_episode(data)
    return data, outcome


def runtime_metadata():
    source = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(Path(__file__).parent.glob("*.py"))}
    git = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True)
    return {"versions": {name: version(name) for name in ("mani-skill", "sapien", "torch", "numpy", "scipy")},
            "python": platform.python_version(), "platform": platform.platform(),
            "sim_backend": "physx_cpu", "render_backend": "cpu", "num_envs": 1,
            "source_sha256": source, "git_commit": git.stdout.strip(),
            "torch_num_threads": torch.get_num_threads(),
            "vulkan_icd": os.environ.get("VK_ICD_FILENAMES"),
            "asset_dir": os.environ.get("MS_ASSET_DIR")}

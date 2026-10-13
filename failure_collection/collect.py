"""Run with python -m failure_collection.collect --help."""
import argparse
from dataclasses import asdict
from collections import Counter
from datetime import datetime, timezone
import hashlib
from importlib.metadata import version
import itertools
import json
import os
from pathlib import Path
import platform
import subprocess

import numpy as np
import torch

from . import SCHEMA_VERSION
from .environment import CollectionEnv, normalized_properties
from .policy import load_policy
from .recording import EpisodeRecorder, first
from .schema import describe, save_episode, validate_episode

ROOT = Path(__file__).resolve().parents[1]


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, allow_nan=False).encode()).hexdigest()


def write_json(path, value):
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n")
    temporary.replace(path)


def load_config(path):
    config = json.loads(Path(path).read_text())
    allowed = {"base_properties", "axes", "seeds", "seed_count", "start_seed", "episode_steps",
               "contact_threshold_n", "experiment", "recovery"}
    if set(config) - allowed:
        raise ValueError(f"Unknown config keys: {set(config) - allowed}")
    config.setdefault("base_properties", {})
    config.setdefault("axes", {})
    config.setdefault("episode_steps", 100)
    config.setdefault("contact_threshold_n", 0.05)
    if "seed_count" in config:
        if "seeds" in config:
            raise ValueError("Use seed_count or seeds, not both")
        count, start = config["seed_count"], config.get("start_seed", 1000)
        if type(count) is not int or count < 1 or type(start) is not int or start < 0 or start + count > 2**31:
            raise ValueError("seed_count must be positive and start_seed must define valid 31-bit seeds")
        config["seeds"] = list(range(start, start + count))
    seeds = config.get("seeds", [])
    if not seeds or any(type(s) is not int or s < 0 or s >= 2**31 for s in seeds) or len(seeds) != len(set(seeds)):
        raise ValueError("seeds must be distinct nonnegative 31-bit integers")
    if type(config["episode_steps"]) is not int or config["episode_steps"] < 1:
        raise ValueError("episode_steps must be a positive integer")
    if not np.isfinite(config["contact_threshold_n"]) or config["contact_threshold_n"] <= 0:
        raise ValueError("contact_threshold_n must be positive and finite")
    if config.get("experiment") == "matched_mass_friction":
        if config["axes"]:
            raise ValueError("Matched mass/friction experiments cannot also have Cartesian axes")
        from .paired import matched_conditions
        from .recovery import normalize_recovery
        config["recovery"] = normalize_recovery(config.get("recovery"))
        return config, matched_conditions(config["base_properties"])
    if config.get("experiment") is not None:
        raise ValueError("Unknown experiment")
    if config.get("recovery"):
        raise ValueError("Recovery requires a matched_mass_friction experiment")
    axes = config["axes"]
    if not isinstance(axes, dict):
        raise ValueError("axes must map axis names to lists of property overrides")
    seen = set()
    for name, levels in axes.items():
        if not isinstance(levels, list) or not levels or any(not isinstance(p, dict) or not p for p in levels):
            raise ValueError(f"Axis {name} must have nonempty property mappings")
        keys = set(levels[0])
        if any(set(p) != keys for p in levels) or keys & seen:
            raise ValueError(f"Axis {name} has inconsistent or overlapping property keys")
        seen |= keys
    conditions = []
    for levels in itertools.product(*axes.values()):
        props = dict(config["base_properties"])
        for level in levels:
            props.update(level)
        properties = normalized_properties(props)
        conditions.append({"condition_index": len(conditions), "condition_id": digest(properties)[:16],
                           "axis_levels": dict(zip(axes, levels)), "properties": properties})
    if len({c["condition_id"] for c in conditions}) != len(conditions):
        raise ValueError("Duplicate property conditions in sweep")
    return config, conditions


def rollout(env, policy, seed, config, *, correction=None, video_path=None):
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
    from .recovery import correction_context, apply_correction
    try:
        with correction_context(env, correction) as capability:
            active_controller_config = {name: asdict(controller.config)
                                        for name, controller in env.agent.controller.controllers.items()}
            for step in range(config["episode_steps"]):
                raw = policy(observation)
                applied = apply_correction(raw.clamp(-1, 1), env, correction)
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
        "meta__recovery_capability_json": np.asarray(json.dumps(capability, sort_keys=True)),
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


def check_replay(env, policy, seed, config, reference):
    repeated, _ = rollout(env, policy, seed, config)
    keys = [key for key in reference if key.startswith(("input__", "sim__", "label__"))]
    point_keys = [key for key in keys if key.startswith("sim__contact_") and key != "sim__contact_point_offsets"]

    def contact_order(data):
        offsets = data["sim__contact_point_offsets"]
        columns = np.column_stack([data[key].reshape(len(data[key]), -1) for key in point_keys]) if offsets[-1] else np.empty((0, 1))
        order = []
        for start, end in zip(offsets[:-1], offsets[1:]):
            values = columns[start:end]
            order.extend(start + np.lexsort(values.T[::-1]))
        return np.asarray(order, dtype=int)

    left_order, right_order = contact_order(reference), contact_order(repeated)
    differences = []
    for key in keys:
        left, right = reference[key], repeated[key]
        if key in point_keys:
            left, right = left[left_order], right[right_order]
        equal = (np.array_equal(left, right, equal_nan=True) if left.dtype.kind in "fc"
                 else np.array_equal(left, right))
        if not equal:
            differences.append(key)
    return {"seed": seed, "arrays_compared": len(keys), "bitwise_equal": not differences,
            "differing_arrays": differences,
            "contact_points_canonicalized_within_physics_sample": True,
            "scope": "Repeated full rollout after fresh-scene same-seed reset; contact enumeration canonicalized, other arrays compared bitwise; same CPU process, no cross-hardware guarantee"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=ROOT / "configs/failure_collection_matched.json")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--checkpoint", type=Path)
    parser.add_argument("--max-episodes", type=int, help="Collect a prefix of the planned sweep; same plan can later resume")
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--check-determinism", action="store_true", help="Repeat first newly collected episode and compare every input/sim/label array")
    parser.add_argument("--dry-run", action="store_true", help="Validate config/model and print plan without simulating")
    parser.add_argument("--seed-count", type=int, help="Override matched experiment seed_count (10 pilot, 50 atlas)")
    parser.add_argument("--record-seeds", type=int, default=0, help="Save GIFs for this many first seeds in each condition")
    args = parser.parse_args()
    torch.set_num_threads(1)
    config, conditions = load_config(args.config)
    if args.seed_count is not None:
        if "seed_count" not in config or args.seed_count < 1:
            parser.error("--seed-count requires a seed_count config and a positive count")
        start = config.get("start_seed", 1000)
        if start + args.seed_count > 2**31:
            parser.error("Seed range exceeds 31-bit integers")
        config["seed_count"] = args.seed_count
        config["seeds"] = list(range(start, start + args.seed_count))
    if args.record_seeds < 0:
        parser.error("--record-seeds must be nonnegative")
    policy, policy_info = load_policy(args.checkpoint)
    total = len(conditions) * len(config["seeds"])
    if args.max_episodes is not None and args.max_episodes < 1:
        parser.error("--max-episodes must be positive")
    limit = min(total, args.max_episodes or total)
    if args.dry_run:
        print(json.dumps({"conditions": len(conditions), "seeds_per_condition": len(config["seeds"]),
                          "planned_episodes": total, "selected_episodes": limit, "episode_steps": config["episode_steps"],
                          "policy": policy_info}, indent=2))
        return
    if config.get("experiment") == "matched_mass_friction":
        from .paired import collect_matched
        collect_matched(args, config, conditions, policy, policy_info)
        return
    output = args.output or ROOT / "runs/failure_collection" / datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ")
    output = output.resolve()
    runtime = runtime_metadata()
    contract = {"schema_version": SCHEMA_VERSION, "config": config, "policy": policy_info, "runtime": runtime}
    fingerprint = digest(contract)
    if args.resume:
        manifest = json.loads((output / "manifest.json").read_text())
        if manifest["run_fingerprint"] != fingerprint:
            raise ValueError("Resume refused: config, policy, source, or runtime differs from saved run")
        # An interrupted atomic write never counts as a complete episode.
        for partial in output.glob("episode_*.npz.tmp"):
            partial.unlink()
    else:
        output.mkdir(parents=True, exist_ok=False)
        manifest = {**contract, "run_fingerprint": fingerprint, "planned_episodes": total,
                    "conditions": conditions, "created_utc": datetime.now(timezone.utc).isoformat(),
                    "status": "collecting", "proposed_schema_assumption": "Ideal pose and force proxies; descriptive outcome labels"}
        write_json(output / "manifest.json", manifest)
    print(f"Output: {output}\nPlan: {len(conditions)} conditions x {len(config['seeds'])} matched seeds = {total} episodes", flush=True)
    checked = False
    rows = []
    try:
        for condition in conditions:
            env = None
            try:
                for seed_index, seed in enumerate(config["seeds"]):
                    index = condition["condition_index"] * len(config["seeds"]) + seed_index
                    if index >= limit:
                        break
                    path = output / f"episode_{index:06d}.npz"
                    if path.exists():
                        with np.load(path, allow_pickle=False) as saved:
                            validate_episode(saved)
                            if str(saved["meta__run_fingerprint"]) != fingerprint or int(saved["label__seed"]) != seed or str(saved["meta__condition_id"]) != condition["condition_id"]:
                                raise ValueError(f"Existing episode has mismatched identity: {path}")
                            outcome = {key.removeprefix("label__"): saved[key].item() for key in ("label__success_final", "label__success_any", "label__failure_mode")}
                    else:
                        if env is None:
                            env = CollectionEnv(condition["properties"])
                        data, outcome = rollout(env, policy, seed, config)
                        if args.check_determinism and not checked:
                            check = check_replay(env, policy, seed, config, data)
                            write_json(output / "determinism.json", check)
                            checked = True
                            print(f"Same-seed replay bitwise equal: {check['bitwise_equal']}", flush=True)
                        data.update({"meta__run_fingerprint": np.asarray(fingerprint),
                                     "meta__condition_id": np.asarray(condition["condition_id"]),
                                     "meta__episode_index": np.asarray(index),
                                     "meta__properties_requested_json": np.asarray(json.dumps(condition["properties"], sort_keys=True)),
                                     "meta__policy_provenance_json": np.asarray(json.dumps(policy_info, sort_keys=True)),
                                     "meta__runtime_json": np.asarray(json.dumps(runtime, sort_keys=True))})
                        save_episode(path, data)
                        if not (output / "schema.json").exists():
                            write_json(output / "schema.json", describe(data))
                    rows.append({"episode_index": index, "condition_id": condition["condition_id"], "seed": seed, **outcome})
                    print(f"[{index + 1}/{limit}] seed={seed} condition={condition['condition_id']} {outcome['failure_mode']}", flush=True)
            finally:
                if env is not None:
                    env.close()
            if len(rows) >= limit:
                break
        summary = {"episodes": len(rows), "planned_episodes": total,
                   "success_final": sum(r["success_final"] for r in rows),
                   "success_any": sum(r["success_any"] for r in rows),
                   "outcome_counts": dict(Counter(r["failure_mode"] for r in rows)), "episodes_detail": rows}
        write_json(output / "summary.json", summary)
        manifest.update(status="complete" if len(rows) == total else "partial", completed_episodes=len(rows))
        write_json(output / "manifest.json", manifest)
        print(json.dumps({k: v for k, v in summary.items() if k != "episodes_detail"}, indent=2), flush=True)
    except BaseException as exc:
        manifest.update(status="interrupted", error=f"{type(exc).__name__}: {exc}")
        write_json(output / "manifest.json", manifest)
        raise


if __name__ == "__main__":
    main()

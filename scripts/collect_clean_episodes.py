"""Replay official PickCube demos through ManiSkill and save successful NPZ episodes."""
import argparse
import copy
import hashlib
import importlib.metadata
import json
from pathlib import Path

import gymnasium as gym
import h5py
import numpy as np
import torch
import mani_skill.envs
from mani_skill.trajectory.replay_trajectory import Args, replay_cpu_sim
from mani_skill.trajectory.utils import index_dict
from mani_skill.utils.wrappers.record import RecordEpisode


def numpy_copy(value):
    if isinstance(value, torch.Tensor):
        value = value.detach().cpu().numpy()
    return np.array(value, copy=True)


def json_default(value):
    if isinstance(value, (torch.Tensor, np.ndarray)):
        return numpy_copy(value).tolist()
    if isinstance(value, np.generic):
        return value.item()
    raise TypeError(f"Cannot serialize {type(value)}")


def json_array(value):
    return np.asarray(json.dumps(value, default=json_default, sort_keys=True))


def flatten_state(tree, prefix="initial_state"):
    result = {}
    for key, value in tree.items():
        name = f"{prefix}/{key}"
        if isinstance(value, dict):
            result.update(flatten_state(value, name))
        else:
            result[name] = numpy_copy(value)
    return result


class CaptureEpisode(gym.Wrapper):
    """Observe the official replayer's resets and steps; do not drive the replay."""

    def reset(self, **kwargs):
        result = self.env.reset(**kwargs)
        self.samples = []
        self.actions = []
        self.rewards = []
        self.successes = []
        self.terminated = []
        self.truncated = []
        self.initial = {}
        return result

    def snapshot(self, obs):
        base = self.unwrapped
        return {
            "rgb": numpy_copy(obs["sensor_data"]["base_camera"]["rgb"][0]),
            "qpos": numpy_copy(base.agent.robot.get_qpos()[0]),
            "qvel": numpy_copy(base.agent.robot.get_qvel()[0]),
            "ee_pose": numpy_copy(base.agent.tcp.pose.raw_pose[0]),
            "cube_pose": numpy_copy(base.cube.pose.raw_pose[0]),
            "goal_pos": numpy_copy(base.goal_site.pose.p[0]),
        }

    def step(self, action):
        # The official replayer restores the demo state AFTER reset. Capture here
        # so sample 0 and initial_state refer to that restored state.
        if not self.actions:
            base = self.unwrapped
            state = base.get_state_dict()
            state.pop("controller", None)  # Saved separately, including empty dicts.
            self.initial = flatten_state(state)
            self.initial["initial_controller_json"] = json_array(
                base.agent.get_controller_state()
            )
            self.samples.append(self.snapshot(base.get_obs()))
        result = self.env.step(action)
        obs, reward, terminated, truncated, info = result
        self.samples.append(self.snapshot(obs))
        self.actions.append(numpy_copy(action).reshape(-1))
        self.rewards.append(float(reward.item()))
        self.successes.append(bool(info["success"].item()))
        self.terminated.append(bool(terminated.item()))
        self.truncated.append(bool(truncated.item()))
        return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--traj-path", type=Path, default=Path(
        "demos/PickCube-v1/motionplanning/trajectory.h5"))
    parser.add_argument("--num-episodes", "-n", type=int, default=20,
                        help="Number of source episodes to attempt, not successful episodes to target")
    parser.add_argument("--output-dir", type=Path, default=Path("data/pickcube"))
    parser.add_argument("--render-backend", default="cpu")
    args = parser.parse_args()
    if args.num_episodes < 1:
        parser.error("--num-episodes must be positive")
    if list(args.output_dir.glob("episode_*.npz")):
        raise FileExistsError(f"{args.output_dir} already contains episodes; choose a new output directory")
    metadata_path = args.traj_path.with_suffix(".json")
    metadata = json.loads(metadata_path.read_text())
    if metadata["env_info"]["env_id"] != "PickCube-v1":
        raise ValueError("Only PickCube-v1 is supported")
    episodes = copy.deepcopy(metadata["episodes"][:args.num_episodes])
    if len(episodes) != args.num_episodes:
        raise ValueError(f"Requested {args.num_episodes}, but found only {len(episodes)} episodes")
    modes = {episode["control_mode"] for episode in episodes}
    if len(modes) != 1:
        raise ValueError(f"Mixed control modes are not supported: {modes}")
    control_mode = modes.pop()
    if control_mode != "pd_joint_pos":
        raise ValueError("Use the official pd_joint_pos motionplanning demos for this pipeline")
    kwargs = copy.deepcopy(metadata["env_info"]["env_kwargs"])
    kwargs.pop("shader_dir", None)  # Legacy value would override the explicit sensor shader.
    kwargs.update(
        num_envs=1, obs_mode="rgb", control_mode=control_mode,
        reconfiguration_freq=1,  # Rebuild the scene so episodes replay independently.
        reward_mode="normalized_dense", sim_backend="physx_cpu",
        render_backend=args.render_backend,
        sensor_configs={"shader_pack": "minimal"},
        human_render_camera_configs={"shader_pack": "minimal"},
    )
    kwargs["max_episode_steps"] = metadata["env_info"]["max_episode_steps"]
    args.output_dir.mkdir(parents=True, exist_ok=True)
    versions = {name: importlib.metadata.version(name)
                for name in ("mani_skill", "sapien", "torch", "numpy", "gymnasium")}
    source_hash = hashlib.sha256(args.traj_path.read_bytes()).hexdigest()
    capture = CaptureEpisode(gym.make("PickCube-v1", **kwargs))
    env = RecordEpisode(capture, output_dir="checks/replay_capture",
                        save_trajectory=False, save_video=False, save_on_reset=False)
    replay_args = Args(traj_path=str(args.traj_path), use_first_env_state=True,
                       sim_backend="physx_cpu", max_retry=0)
    kept = 0
    report = {"attempted": 0, "kept": 0, "discarded": 0, "episodes": []}
    try:
        with h5py.File(args.traj_path, "r") as demos:
            for episode in episodes:
                source_id = episode["episode_id"]
                if f"traj_{source_id}" not in demos:
                    raise KeyError(f"Missing source trajectory traj_{source_id}")
                result = replay_cpu_sim(replay_args, env, None, None, [episode], demos)
                success = bool(capture.successes and capture.successes[-1])
                if result.successful_replays != int(success):
                    raise RuntimeError("Official replay result disagrees with captured final success")
                report["attempted"] += 1
                entry = {"source_episode_id": source_id, "success": success,
                         "length": len(capture.actions)}
                report["episodes"].append(entry)
                if not success:
                    report["discarded"] += 1
                    print(f"DISCARD source={source_id}: final success=False", flush=True)
                    continue
                arrays = {key: np.stack([sample[key] for sample in capture.samples])
                          for key in capture.samples[0]}
                arrays.update(
                    action=np.stack(capture.actions).astype(np.float32),
                    reward=np.asarray(capture.rewards, dtype=np.float32),
                    success=np.asarray(capture.successes, dtype=np.bool_),
                    terminated=np.asarray(capture.terminated, dtype=np.bool_),
                    truncated=np.asarray(capture.truncated, dtype=np.bool_),
                )
                if arrays["rgb"].dtype != np.uint8:
                    raise TypeError("Camera returned non-uint8 RGB")
                for key, value in arrays.items():
                    if not np.isfinite(value).all():
                        raise ValueError(f"Non-finite values in {key}")
                base = env.unwrapped
                arrays.update(capture.initial)
                # Preserve the exact input to set_state_dict; reading it back can
                # introduce tiny root-pose round-trip differences in PhysX.
                arrays.update(flatten_state(index_dict(
                    demos[f"traj_{source_id}"]["env_states"], 0), "reset_state"))
                arrays.update(
                    seed=np.asarray(episode["episode_seed"], dtype=np.int64),
                    control_mode=np.asarray(control_mode),
                    sim_freq=np.asarray(base.sim_freq, dtype=np.int64),
                    control_freq=np.asarray(base.control_freq, dtype=np.int64),
                    env_id=np.asarray("PickCube-v1"),
                    sim_backend=np.asarray(base.backend.sim_backend),
                    render_backend=np.asarray(base.backend.render_backend),
                    camera_name=np.asarray("base_camera"),
                    joint_names=np.asarray([joint.name for joint in base.agent.robot.get_active_joints()]),
                    env_kwargs_json=json_array(kwargs),
                    reset_kwargs_json=json_array(episode["reset_kwargs"]),
                    versions_json=json_array(versions),
                    source_episode_json=json_array(episode),
                    source_episode_id=np.asarray(source_id, dtype=np.int64),
                    source_sha256=np.asarray(source_hash),
                    schema_version=np.asarray(2, dtype=np.int64),
                )
                path = args.output_dir / f"episode_{kept:03d}.npz"
                with path.with_suffix(".npz.tmp").open("xb") as output:
                    np.savez_compressed(output, **arrays)
                path.with_suffix(".npz.tmp").rename(path)
                entry["file"] = str(path)
                entry["peak_lift_m"] = float(arrays["cube_pose"][:, 2].max() - arrays["cube_pose"][0, 2])
                kept += 1
                report["kept"] = kept
                print(f"KEEP source={source_id} -> {path}, T={len(capture.actions)}, "
                      f"peak lift={entry['peak_lift_m']:.4f} m", flush=True)
    finally:
        env.close()
        (args.output_dir / "collection_summary.json").write_text(json.dumps(report, indent=2) + "\n")
    print(f"Attempted {report['attempted']}; kept {kept}; discarded {report['discarded']}", flush=True)
    if kept == 0:
        raise RuntimeError("No successful episodes were collected")


if __name__ == "__main__":
    main()

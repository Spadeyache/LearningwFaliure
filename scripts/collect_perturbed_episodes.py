"""Replay only held-out demo identities with predefined simulator interventions."""
import argparse
import copy
import json
from pathlib import Path

import gymnasium as gym
import h5py
import numpy as np
import torch
import mani_skill.envs
from mani_skill.trajectory.replay_trajectory import Args, replay_cpu_sim
from mani_skill.utils.structs.pose import Pose
from mani_skill.utils.wrappers.record import RecordEpisode
from collect_clean_episodes import CaptureEpisode, numpy_copy, json_array
from pose_model import file_hash, split_paths

CONDITIONS = ("clean", "cube_shift", "gripper_open", "arm_hold")
SAMPLE_KEYS = ("rgb", "qpos", "qvel", "ee_pose", "cube_pose", "goal_pos")


class PerturbedCapture(CaptureEpisode):
    def __init__(self, env, condition, length):
        super().__init__(env)
        self.condition = condition
        self.injection_step = (-1 if condition == "clean" else
                               max(1, int(length*(.35 if condition=="cube_shift" else .55))))

    def reset(self, **kwargs):
        result = super().reset(**kwargs)
        self.applied_actions = []
        self.fault_active = []
        self.hold_target = None
        return result

    def step(self, action):
        intended = numpy_copy(action).reshape(-1)
        applied = intended.copy()
        step = len(self.actions)
        base = self.unwrapped
        active = False
        if self.condition == "cube_shift" and step == self.injection_step:
            offset = torch.tensor([[.08, 0., 0.]], device=base.device)
            base.cube.set_pose(Pose.create_from_pq(
                p=base.cube.pose.p+offset, q=base.cube.pose.q))
            active = True
        elif self.condition == "gripper_open" and step >= self.injection_step:
            applied[-1] = 1.
            active = True
        elif self.condition == "arm_hold" and self.injection_step <= step < self.injection_step+10:
            if self.hold_target is None:
                self.hold_target = numpy_copy(base.agent.robot.get_qpos()[0, :7])
            applied[:7] = self.hold_target
            active = True
        result = super().step(applied)
        # Model input is the command issued, not the actuator's faulty command.
        self.actions[-1] = intended
        self.applied_actions.append(applied)
        self.fault_active.append(active)
        return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=Path("results/splits.json"))
    parser.add_argument("--traj-path", type=Path, default=Path("demos/PickCube-v1/motionplanning/trajectory.h5"))
    parser.add_argument("--output-dir", type=Path, default=Path("data/perturbed"))
    parser.add_argument("--limit", type=int, default=None, help="Optional smoke-test limit on held-out source episodes")
    args = parser.parse_args()
    if list(args.output_dir.glob("*.npz")):
        raise FileExistsError("Choose an empty output directory; existing replays are preserved")
    sources = split_paths(args.manifest, "test")
    if args.limit is not None:
        if args.limit < 1:
            raise ValueError("--limit must be positive")
        sources = sources[:args.limit]
    args.output_dir.mkdir(parents=True, exist_ok=True)
    report = {"manifest_sha256": file_hash(args.manifest), "cases": [],
              "conditions": list(CONDITIONS)}
    demo_hash = file_hash(args.traj_path)
    with h5py.File(args.traj_path, "r") as demos:
        for source in sources:
            with np.load(source, allow_pickle=False) as archive:
                original = {key: archive[key].copy() for key in archive.files}
            if str(original["source_sha256"]) != demo_hash:
                raise ValueError("Official demo HDF5 changed since clean collection")
            metadata = json.loads(str(original["source_episode_json"]))
            source_id = int(original["source_episode_id"])
            if not np.array_equal(demos[f"traj_{source_id}/actions"][:], original["action"]):
                raise ValueError("Source demo actions differ from the saved clean episode")
            length = len(original["action"])
            for condition in CONDITIONS:
                kwargs = json.loads(str(original["env_kwargs_json"]))
                capture = PerturbedCapture(gym.make("PickCube-v1", **kwargs), condition, length)
                env = RecordEpisode(capture, output_dir="checks/perturb_capture",
                                    save_trajectory=False, save_video=False, save_on_reset=False)
                try:
                    # allow_failure keeps the replay workflow running; labels come
                    # from real step info, never ReplayResult.successful_replays.
                    replay_cpu_sim(Args(traj_path=str(args.traj_path), use_first_env_state=True,
                                        allow_failure=True, max_retry=0),
                                   env, None, None, [copy.deepcopy(metadata)], demos)
                    arrays = original.copy()
                    arrays.update({key: np.stack([sample[key] for sample in capture.samples])
                                   for key in SAMPLE_KEYS})
                    arrays.update(
                        action=np.stack(capture.actions).astype(np.float32),
                        applied_action=np.stack(capture.applied_actions).astype(np.float32),
                        reward=np.asarray(capture.rewards, dtype=np.float32),
                        success=np.asarray(capture.successes, dtype=np.bool_),
                        terminated=np.asarray(capture.terminated, dtype=np.bool_),
                        truncated=np.asarray(capture.truncated, dtype=np.bool_),
                        fault_active=np.asarray(capture.fault_active, dtype=np.bool_),
                        condition=np.asarray(condition),
                        injection_step=np.asarray(capture.injection_step, dtype=np.int64),
                        clean_episode_sha256=np.asarray(file_hash(source)),
                    )
                    arrays.update(capture.initial)
                    prefix = length+1 if condition=="clean" else capture.injection_step+1
                    for key in SAMPLE_KEYS:
                        if not np.array_equal(arrays[key][:prefix], original[key][:prefix]):
                            raise AssertionError(f"{source.name}/{condition}: clean prefix changed in {key}")
                    if condition=="clean" and not bool(arrays["success"][-1]):
                        raise AssertionError("Unperturbed control failed")
                    if not np.array_equal(arrays["action"], original["action"]):
                        raise AssertionError("Intended commands changed")
                    spec = {"condition": condition, "injection_step": capture.injection_step,
                            "cube_shift_world_m": [.08,0,0] if condition=="cube_shift" else None,
                            "arm_hold_steps": 10 if condition=="arm_hold" else None,
                            "gripper_override": 1. if condition=="gripper_open" else None,
                            "source_file": str(source), "manifest_sha256": report["manifest_sha256"],
                            "timing": "before action injection_step; observation injection_step remains pre-fault"}
                    arrays["perturbation_json"] = json_array(spec)
                    path = args.output_dir/f"{source.stem}__{condition}.npz"
                    with path.with_suffix(".npz.tmp").open("xb") as output:
                        np.savez_compressed(output, **arrays)
                    path.with_suffix(".npz.tmp").rename(path)
                    entry = {"file": str(path), "sha256": file_hash(path), "source_file": str(source),
                             "source_episode_id": source_id, "condition": condition,
                             "injection_step": capture.injection_step, "length": length,
                             "final_success": bool(arrays["success"][-1]), "clean_prefix_equal": True}
                    report["cases"].append(entry)
                    (args.output_dir/"replay_summary.json").write_text(json.dumps(report, indent=2)+"\n")
                    print(f"{path.name}: final_success={entry['final_success']}, clean_prefix_equal=True", flush=True)
                finally:
                    env.close()
    print(f"Saved {len(report['cases'])} trials, including all failures", flush=True)


if __name__ == "__main__":
    main()

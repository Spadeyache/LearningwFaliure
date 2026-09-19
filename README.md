# PickCube failure-detection research pipeline

ManiSkill3 PickCube-v1 with the Panda and official motion-planning demonstrations.
The clean-collection stage stores one compressed, pickle-free NPZ per successful
episode. Load with `np.load(path, allow_pickle=False)`.

## Completed stages

1. Clean data collection and exact replay (documented below).
2. [Clean-success pose prediction](docs/STEP2.md): trained GRU checkpoint and baseline comparisons.
3. [Clean-only calibration and perturbed replay](docs/STEP3.md): locked thresholds and 60 held-out trials.
4. [Held-out evaluation and failure analysis](RESULTS.md): measured alarms, prediction errors, and limitations.

The research scope is in [docs/RESEARCH_PLAN.md](docs/RESEARCH_PLAN.md).
This is a working state-based prototype; the evaluation shows missed failures and
alarms on recoveries. Read RESULTS.md before interpreting an alarm as task failure.
Code, the small trained checkpoint, manifests, reports and figures are committed.
Large datasets and per-step evaluation traces remain on disk and are Git-ignored.

After the environment setup below, score a saved episode with:

    python scripts/score_episode.py data/perturbed/episode_041__cube_shift.npz --output runs/my_scores.npz

The remaining sections document the original clean-data stage.

## Machine and setup

Tested in Ubuntu 24.04.2 / WSL2, Python 3.10.18; NVIDIA RTX 3050 Laptop GPU,
4 GiB VRAM; CUDA available in PyTorch; 838 GiB disk free before installation.
**This run uses CPU physics and CPU Vulkan rendering (Mesa lavapipe).**
CUDA access does not provide the missing native NVIDIA Vulkan driver in WSL.

Versions: ManiSkill 3.0.1, SAPIEN 3.0.3, PyTorch 2.14.0+cu130, NumPy 2.2.6.
All 103 dependencies are pinned in requirements-lock.txt; the environment uses 6.2 GiB.
No system drivers were changed. From Windows, select the correct distribution:

```powershell
wsl -d Ubuntu --cd /home/ubuntu/faliure
```

For a fresh Python environment, run in the Linux project directory:

```bash
uv venv --python 3.10 .venv
uv pip install --python .venv/bin/python -r requirements-lock.txt
```

For each new shell, activate it and select this machine's existing Mesa driver:

```bash
source .venv/bin/activate
export VK_ICD_FILENAMES=/usr/share/vulkan/icd.d/lvp_icd.x86_64.json
export MS_ASSET_DIR=/home/ubuntu/faliure/.maniskill/assets
export MS_SKIP_ASSET_DOWNLOAD_PROMPT=1
export OMP_NUM_THREADS=4
```

## Reproduce steps 2-5

```bash
# 2: built-in environment reset/step; checks/first_frame.png
python scripts/check_environment.py

# 3: official download and official CLI replay of three demos
python -m mani_skill.utils.download_demo PickCube-v1 -o demos
python scripts/replay_official_demos.py --count 3

# 4: attempt 20 source episodes; keep only final successes
python scripts/collect_clean_episodes.py

# 5: print shapes/dtypes; checks/cube_z_episode_000.png
python scripts/inspect_episode.py data/pickcube/episode_000.npz

# Restore the saved episode without any perturbation and compare every step
python scripts/verify_saved_replay.py data/pickcube/episode_000.npz
```

The collector refuses to overwrite existing episodes. For another run use
`--output-dir data/pickcube_rerun`; `--num-episodes N` changes the number
attempted (default 20), not the number of successes targeted.
Files are numbered contiguously; stdout and collection_summary.json record
kept/discarded counts and original source IDs. No failed replay is retried.

The replay launcher links the original HDF5 and writes a scratch metadata copy
with `render_backend="cpu"` in checks/replay_input. It then runs the unmodified CLI:

```bash
python -m mani_skill.trajectory.replay_trajectory \
  --traj-path checks/replay_input/trajectory.h5 \
  --use-first-env-state -b physx_cpu -o rgb --shader minimal \
  --count 3 --num-envs 1 --reward-mode normalized_dense --record-rewards --save-traj
```

The original download is unchanged. The collector uses the same installed
`replay_cpu_sim` function, with a small Gym wrapper that captures outputs.
Only the initial state is restored; subsequent states come from action-driven
physics. It retains the original pd_joint_pos controller and uses
`reconfiguration_freq=1` to rebuild the scene at each reset.

## NPZ keys (schema 2)

T = number of actions. State/image arrays have T+1 entries, starting with the initial
observation. Action t takes state t to state t+1; reward/success/terminal flags
at t describe the resulting state. Per-step arrays have no singleton environment axis.

All Cartesian poses use **world coordinates, metres, z up** (tabletop z=0).
Pose layout is **[x,y,z,qw,qx,qy,qz]**, with dimensionless, scalar-first quaternions.
Joint values are coordinates about/along each robot joint's own axis.

| Key | Shape | dtype | Meaning / units / frame |
|---|---|---|---|
| rgb | (T+1,128,128,3) | uint8 | Default base_camera, RGB pixels 0-255, minimal shader |
| qpos | (T+1,9) | float32 | Seven arm angles in rad, then two finger displacements in m |
| qvel | (T+1,9) | float32 | Same order, arm rad/s and fingers m/s |
| ee_pose | (T+1,7) | float32 | World pose of panda_hand_tcp (tool center) |
| cube_pose | (T+1,7) | float32 | World pose of cube center |
| goal_pos | (T+1,3) | float32 | Target cube-center world position, m |
| action | (T,8) | float32 | Seven absolute target arm angles (rad), normalized gripper command [-1,1] |
| reward | (T,) | float32 | ManiSkill normalized dense reward, dimensionless |
| success | (T,) | bool | Task success after each action; final value must be True |
| terminated, truncated | (T,) each | bool | Gym termination and time-limit flags, independent of success |
| seed | () | int64 | Environment reset seed |
| sim_freq, control_freq | () each | int64 | Physics 100 Hz, control/image sampling 20 Hz |
| control_mode | () | Unicode | pd_joint_pos |
| env_id | () | Unicode | PickCube-v1 |
| sim_backend, render_backend | () each | Unicode | physx_cpu and sapien_cpu |
| camera_name | () | Unicode | base_camera |
| joint_names | (9,) | Unicode | Seven Panda arm joints followed by two finger joints |
| reset_state/actors/cube | (13,) | float32 | Exact original reset input for cube; layout below |
| reset_state/actors/goal_site | (13,) | float32 | Exact original reset input for goal |
| reset_state/actors/table-workspace | (13,) | float32 | Exact original reset input for registered table actor |
| reset_state/articulations/panda | (31,) | float32 | Exact original robot reset input |
| initial_state/actors/cube | (1,13) | float32 | Observed simulator state after restoration |
| initial_state/actors/goal_site | (1,13) | float32 | Observed initial goal state |
| initial_state/actors/table-workspace | (1,13) | float32 | Observed initial registered table state |
| initial_state/articulations/panda | (1,31) | float32 | Observed initial robot state |
| initial_controller_json | () | Unicode JSON | Controller state before action 0; empty object for pd_joint_pos |
| env_kwargs_json | () | Unicode JSON | Construction overrides, renderer, shader, scene-reset settings, time limit |
| reset_kwargs_json | () | Unicode JSON | Reset seed and options |
| versions_json | () | Unicode JSON | ManiSkill, SAPIEN, PyTorch, NumPy, Gymnasium versions |
| source_episode_json | () | Unicode JSON | Source metadata, with reset seed normalized by official replay |
| source_episode_id | () | int64 | Original HDF5 traj_ID |
| source_sha256 | () | Unicode | SHA-256 of official source HDF5 |
| schema_version | () | int64 | 2 |

Actor state layout: position (3, world m), quaternion (4), linear velocity
(3, world m/s), angular velocity (3, world rad/s).
Robot state: those 13 root-link quantities, then 9 qpos and 9 qvel.
The gripper command maps [-1,1] to target finger positions [-0.01,0.04] m;
negative targets provide closing force. The two observed fingers remain separate.

**Restore reset_state, not initial_state.** Rebuild the nested dictionary from
slash-separated keys, call reset with reset_kwargs, then set_state_dict and
agent.set_controller_state. The verifier provides executable restoration code.
The exact input and read-back state are both saved because float round trips
through PhysX can change the robot root position slightly.

## Results and gotchas

The official CLI check succeeded on **3/3** demos. Final collection: **20 attempted,
20 kept, 0 discarded** (100%); **1,493 actions**, lengths **49-88** (mean 74.65),
**45.51 MiB** compressed. Counts and lengths are recorded in
data/pickcube/collection_summary.json and checks/dataset_summary.json.
Episode 000 has 74 actions: RGB (75,128,128,3), joints (75,9), poses (75,7);
its cube rises from 0.0200 m to 0.2862 m (26.62 cm).
**All 20 NPZs independently replayed with zero state error, matching rewards and
success/terminal flags, and bitwise-identical RGB frames.** Comparisons are saved
in checks/replay_verification.json.

- **19/20** final episodes have truncated=True; source trajectories can exceed the nominal 50-step limit. Finish all saved
  actions, as the official replayer does; do not stop at the first terminated or
  truncated flag. Final success is the collection criterion.
- Peak lifts range from **0.00096 to 0.29209 m**. A low goal can succeed with very little lift. Success is the task's placement
  and robot-static criterion, not a minimum-lift or continued-grasp criterion.
- Ground-truth poses/labels and 20 selected motion-planning episodes are a useful
  starting dataset, not evidence of failure-detection performance.
- Exact replay is checked on this installed CPU stack, not guaranteed across
  software versions, hardware, physics backends, or changed simulation settings.

Resolved setup/reproducibility errors (original logs retained in checks):
1. The command runner chose the wrong WSL distribution and lacked bwrap in that
   distribution. Commands explicitly targeted Ubuntu, which contains the project.
2. Default Vulkan selection failed with
   "RuntimeError: vk::createInstanceUnique: ErrorIncompatibleDriver".
   Selecting the existing lavapipe ICD fixed rendering.
3. The official CLI requested CUDA rendering and failed with
   'RuntimeError: Failed to find a supported physical device "cuda:0"'.
   Its CLI has no renderer flag; the launcher changes only a scratch metadata copy.
4. Reapplying the read-back initial state introduced a 1.49e-8 m root-position
   change and a later 8.41e-6 velocity mismatch at step 36.
   Preserving the exact reset input removed this error for episode 000.
5. Reusing the scene still caused episode 001 to differ when replayed independently
   (velocity difference 1.07e-5 at step 41). Scene reconfiguration at reset addresses
   dependence on the previous episode; the strict 1e-6 comparison is retained.
6. SAPIEN warns about missing NVIDIA glvnd ICD. CPU Vulkan headless rendering
   works despite this warning. No warning was suppressed.
7. The installed official CPU HDF5 recorder appears to replace its initial saved
   state with demo state 1 under use_first_env_state. Its HDF5 is only a smoke
   artifact here; NPZ captures the live initial observation and exact reset input.

## API references

Installed package source was checked against these official documentation/source pages:

- [Installation and Vulkan](https://maniskill.readthedocs.io/en/latest/user_guide/getting_started/installation.html).
- [Official demo setup](https://maniskill.readthedocs.io/en/latest/user_guide/learning_from_demos/setup.html)
  and [download_demo.py](https://github.com/mani-skill/ManiSkill/blob/main/mani_skill/utils/download_demo.py): download module/output directory.
- [Replay guide](https://maniskill.readthedocs.io/en/latest/user_guide/datasets/replay.html)
  and [replay_trajectory.py](https://github.com/mani-skill/ManiSkill/blob/main/mani_skill/trajectory/replay_trajectory.py): Args, replay_cpu_sim, initial restoration, final-success filtering.
- [record.py](https://github.com/mani-skill/ManiSkill/blob/main/mani_skill/utils/wrappers/record.py)
  and [trajectory utilities](https://github.com/mani-skill/ManiSkill/blob/main/mani_skill/trajectory/utils/__init__.py): RecordEpisode, HDF5/JSON layout, index_dict.
- [sapien_env.py](https://github.com/mani-skill/ManiSkill/blob/main/mani_skill/envs/sapien_env.py)
  and [backend.py](https://github.com/mani-skill/ManiSkill/blob/main/mani_skill/envs/utils/system/backend.py): gym.make arguments, reset/step/get_obs, state get/set, frequencies, scene reconfiguration and CPU rendering.
- [pick_cube.py](https://github.com/mani-skill/ManiSkill/blob/main/mani_skill/envs/tasks/tabletop/pick_cube.py): default camera, cube/goal poses, success and rewards.
- [panda.py](https://github.com/mani-skill/ManiSkill/blob/main/mani_skill/agents/robots/panda/panda.py)
  and [base_agent.py](https://github.com/mani-skill/ManiSkill/blob/main/mani_skill/agents/base_agent.py): TCP, joint/action order and units, controller state.
- [actor.py](https://github.com/mani-skill/ManiSkill/blob/main/mani_skill/utils/structs/actor.py),
  [articulation.py](https://github.com/mani-skill/ManiSkill/blob/main/mani_skill/utils/structs/articulation.py),
  [pose.py](https://github.com/mani-skill/ManiSkill/blob/main/mani_skill/utils/structs/pose.py): packed state, qpos/qvel, active joints and scalar-first poses.

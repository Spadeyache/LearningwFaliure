# Gripping and lifting PPO learning workspace

Start with plain Python scripts as you learn robotic gripping and lifting.
There is now a small runnable PyTorch PPO baseline in `learning/`.
**It has passed integration checks, not demonstrated learned lifting.**
The existing simulator is ManiSkill 3.0.1 / SAPIEN 3.0.3 with Gymnasium and
PyTorch. No weight estimator is implemented. The separate optional CLI scaffolding
is still incomplete; its `framework: null` setting is not used by these scripts.

The previous failure-detection pipeline, demonstrations, datasets, predictor
checkpoints, reports, figures, tests and archived documentation have been deleted
at your request. The simulator smoke check and installed dependencies are retained.

## Start here: plain Python

Run these commands in Bash using the existing environment:

```bash
cd /home/ubuntu/faliure
source scripts/activate_grip.sh
python learning/simulator_starter.py
```

Open [learning/simulator_starter.py](learning/simulator_starter.py) and read it
from top to bottom. It creates the installed **PickCube** simulation, resets it,
saves a camera image, takes one random action and closes the simulator. Settings
are directly in the file. There is no `argparse`, configuration file or
`grip_support` import. The activation script only prepares Python and simulator
environment settings; you do not need to learn CLI helpers to use this path.

Expected output includes image shape `(128, 128, 3)`, a reward and a success flag.
Open `checks/learning/first_frame.png` to see the scene immediately after reset;
rerunning the script replaces this image. It does not open a live viewer.
`Success: False` is normal after one random action. This is a simulator starter,
not a trained policy or your future custom gripping task.

Put your next plain `.py` files in `learning/` and run them the same way:
`python learning/your_file.py` (replace `your_file.py` with your filename).
For a first small change, edit `seed`, rerun and compare the saved image.
You can build up your own code one step at a time without changing the CLI core.

### Inspect the lift reward

With the same environment activated, run `python learning/check_reward.py`.
It checks six synthetic conditions, then prints named reward components from an
actual reset and one random action. The synthetic lifts are formula checks, not
physically achieved or learned behaviour. The original `simulator_starter.py`
still uses upstream PickCube's reward; this separate check uses `LiftTask`.

The editable provisional settings are near the top of `learning/lift_task.py`:
`proximity = exp(-distance / 0.10)` using TCP-to-cube-centre distance in metres;
`reach = 1` when grasped, otherwise `proximity`; `grasp` is 0 or 1; and
`lift = grasp * clamp(cube_bottom_clearance / 0.08, 0, 1)`.
The single task score is **0.2 × reach + 0.3 × grasp + 0.5 × lift**, bounded
between 0 and 1. Confirmed grasp completes reaching. Grasp on the table earns
0.5; grasp with 4 cm clearance earns 0.75; grasp with at least 8 cm earns 1 and
ends the episode successfully. The cube's orientation is accounted for when
finding its lowest point. Raising an empty gripper earns no grasp/lift credit.

Grasp uses ManiSkill Panda's existing two-finger contact test (at least 0.5 N
per finger and force direction within 85 degrees of its opening axis). There is
no hold-duration requirement, force penalty or slip penalty yet. Excessive-force
tuning is deferred. The inherited random goal is not part of this reward or
success condition. The reward check uses a random joint-position action;
the training script below uses the pose/force adapter with the same reward.

### Run and read the PPO baseline

```bash
cd /home/ubuntu/faliure
source scripts/activate_grip.sh
python learning/train_ppo.py
```

Edit `SETTINGS` at the top of `train_ppo.py`. The provisional CPU defaults are
**8 updates × 128 steps = 1,024 steps**, at most 100 steps per episode, cycling
actual cube masses **0.040, 0.064, 0.100 kg** at reset. Inertia scales with mass;
shape and friction stay fixed. These are small engineering starting settings,
not a validated learning budget or a tuned mass study. No new packages are needed.

Read the code first, using the official docs alongside it:

1. `lift_task.py`: 21 inputs, physical mass, agreed reward, pose/force adapter.
2. `ppo.py`, `Agent`: separate actor and critic, each with two 64-unit tanh layers.
3. `train_ppo.py`, `main`: collect transitions and reset episodes with new masses.
4. `ppo.py`, `generalized_advantages` and `update_ppo`: advantages and Adam updates.
5. `train_ppo.py`, `save_checkpoint` and `load_checkpoint`: saving and restoring.

The actor and critic see only TCP pose (7), cube pose (7), true weight in newtons
(1), and separate world finger–cube force vectors (3 + 3), collected at one
simulation state. Fixed scaling divides positions by 0.3 m, weight by 1 N, forces
by 10 N, and leaves `wxyz` quaternions unchanged. No RGB, joint positions, gripper
width or hidden goal is added. Velocities/history are also absent, so this small
feed-forward policy has only a partial view of the dynamics.

The bounded seven-value action requests world TCP position/rotation increments
(up to 1.5 cm and 0.1 rad per axis) and **0–8 N normal contact force per finger**.
The adapter creates an absolute target TCP pose, clips its position to the visible
workspace bounds, transforms it to the Panda root frame, and uses ManiSkill's
absolute pose/IK controller. Targets may not be fully reached within one step.
A feedback servo integrates force error into a bounded finger-position target;
it closes with no contact and releases near zero demand. It uses the larger of
the two projected normal forces to protect the more loaded finger. This is
approximate force regulation, not an actuator-force-limit command or a guarantee
of equal force on both fingers. Physical robot transfer has not been tested.

Each run has its own `runs/learning/<run>/` folder with settings, episode/update
metrics, checkpoints **every 2 updates (256 steps)**, and `final.pt`.
Ctrl+C saves `interrupted.pt`. Checkpoints include actor, critic, Adam state,
counters, fixed scaling, feature/action/reward metadata and the PyTorch RNG state.
To continue, set `resume_from` to a checkpoint path and raise `updates` above its
completed count; all other dynamics/model/optimizer settings must match. Resume
creates a new run and fresh episode, discarding the old partial episode/rollout.
An interrupted optimizer update may be partial; continuation is not exact replay.
`load_checkpoint(path)` also returns a model for
`model.get_action(inputs, deterministic=True)`.

The implementation adapts the [official ManiSkill v3.0.1 PPO source](https://github.com/mani-skill/ManiSkill/blob/a4a4f9272ad64b1564035874b605ceb687b63ed8/examples/baselines/ppo/ppo.py)
(commit `a4a4f9272ad64b1564035874b605ceb687b63ed8`), with its Apache-2.0 license
preserved in `learning/MANISKILL_LICENSE`. See the [official baseline guide](https://maniskill.readthedocs.io/en/latest/user_guide/reinforcement_learning/baselines.html).
Local changes reduce the network and CPU budget, use tanh-transformed Gaussian
actions with corrected log probabilities, and separate terminal and time-limit
bootstrapping. The CLI, GPU wrappers and external logging dependencies are omitted.

`python learning/check_training.py` runs targeted GAE/action/controller/mass tests,
a scripted contact test, 32 PPO steps and a 16-step resume, including checkpoint
action equivalence. Validation found finite parameter updates across all three
masses. A scripted 2 N request produced about 1.67 N per finger, 6 N produced
about 5.97 N, and release returned contact force to zero. This verifies controller
response and training plumbing; it is not evidence of a learned grasp, lift,
mass adaptation or generalization. Force-efficiency penalties remain inactive.

## Folder purposes

| Path | Purpose |
|---|---|
| `learning/` | Your standalone Python learning scripts; start here. |
| `checks/learning/` | Images generated by the starter, ignored by Git. |
| `scripts/` | Existing environment activation and optional simulator check helpers. |
| `grip_support/` | Optional CLI scaffolding for later; separate from the learning scripts. |
| `configs/` | Configuration for the optional CLI scaffolding. |
| `checks/`, `runs/` | Generated check output, learning checkpoints and optional CLI runs. |
| `.venv/`, `.maniskill/`, `.cache/` | Installed Python environment, simulator assets and caches. |
| `requirements-lock.txt` | Existing dependency versions for recreating the environment. |

## Optional CLI helpers (later)

Everything below documents the existing helpers. You can defer this section
while working in `learning/`. Both `grip_support` and
`scripts/check_environment.py` are preserved; neither is called by the starter.

Run these commands in Bash:

```bash
cd /home/ubuntu/faliure
source scripts/activate_grip.sh
python -m grip_support --help
python -m grip_support setup-check
python -m grip_support sim-check
python -m grip_support train --config configs/grip.json --check-only
```

`setup-check` should print `All installed packages are compatible`, five
`IMPORT OK` lines and `SETUP OK` with this workspace's Python path (exit 0).
`sim-check` starts upstream **PickCube**, resets, renders and takes one sampled
action. Expected output includes RGB shape `[128,128,3]`, `physx_cpu`, and
`sapien_cpu` (exit 0). The image goes to `checks/grip-smoke/first_frame.png`.
A false success flag is normal for a one-step check. This does not validate your
future gripping environment or train/evaluate a policy.

`train --check-only` currently prints `CORE INCOMPLETE: train`, lists missing
implementations, and exits **2**. This is expected. `train`, `resume` and
`evaluate` refuse to run until the learner core reports readiness. Invalid JSON,
missing imports/files, runtime failures or checkpoint incompatibility exit **1**.
`--check-only` checks configuration/core readiness; it never performs a rollout.

### Recreate the Python environment

The existing `.venv` is usable; do not reinstall just to run checks. For a fresh
checkout, with `uv` available:

```bash
cd /home/ubuntu/faliure
export UV_CACHE_DIR="$PWD/.cache/uv"
uv venv --python 3.10 .venv
uv pip install --python .venv/bin/python -r requirements-lock.txt
source scripts/activate_grip.sh
python -m grip_support setup-check
```

The lock file captures the existing 103-package stack, including CUDA dependencies;
installation can be large and needs network access. `uv pip` operates on the
explicit Python without requiring a pip module inside the environment. Keep
this lock to reproduce the installed dependency stack. After choosing an RL framework, record
its exact compatible dependencies before updating the lock. No new dependency
was needed for these support tools.

Activation selects the venv and writable uv/Matplotlib caches, project-local
ManiSkill assets and (when present) Mesa lavapipe Vulkan for CPU rendering.
It preserves an explicitly set `VK_ICD_FILENAMES`. Run the module commands from
the project root so Python can find `grip_support`; no package installation is
needed. `.venv` is the **Python environment**, while a ManiSkill/Gymnasium
**simulation environment** is a separate object created by your task code.

## Optional CLI integration boundary

If you later choose to connect your code to the CLI, start with
[grip_support/core.py](grip_support/core.py). `missing(config, mode)`
returns remaining work for a requested command. Make it mode-specific as needed;
remove a blocker only after implementing and checking it. `run(mode, config,
context, checkpoint)` is your integration entry point.

You own the simulation dynamics/task, observation and action definitions, reward,
termination, PPO settings/experiments, estimator, metrics and evaluation protocol.
The intended input information is true object weight, object pose, gripper pose,
gripper width and contact force during training; deployment substitutes estimated
weight. You define layout, units, coordinate frames, scaling and extraction.
You also define how slip/lift outcomes update estimates, object identity and when
estimates persist or reset. No estimator update formula or persistence policy is
provided here.

`configs/grip.json` contains only supporting settings plus empty dictionaries
for your decisions. `seed` seeds Python, NumPy and PyTorch at run startup; your
core must seed simulator resets, spaces, workers and other generators. `run_root`
is resolved relative to the project root. `core_module` selects the importable
learner implementation. The loader rejects malformed top-level keys/types. It
does not validate task or PPO parameters; add that validation in your core.

## Commands and run artifacts

After implementing the core, the command flow is:

```bash
python -m grip_support train --config configs/grip.json --check-only
python -m grip_support train --config configs/grip.json
# Substitute an actual run directory and checkpoint produced by your core:
python -m grip_support resume --config runs/grip/RUN/config.json --checkpoint runs/grip/RUN/checkpoints/latest.pt
python -m grip_support evaluate --config runs/grip/RUN/config.json --checkpoint runs/grip/RUN/checkpoints/latest.pt
```

`RUN` is a placeholder: use the directory printed as `RUN: ...`. Each execution
gets a unique UTC-prefixed directory under `runs/grip`, including resumed and
evaluation executions. A readiness failure creates no run. The directory contains:

- `config.json`: exact parsed configuration.
- `metadata.json`: command, source checkpoint, Python/package versions, platform,
  Git commit/status and relevant environment variables.
- `tracked-changes.patch`: tracked working-tree changes at startup.
- `events.jsonl`: timestamped start/completion/failure and checkpoint events.
- `checkpoints/`: files saved by your core using `context.save('latest.pt', state)`.

Call `context.log('your_event', field=value)` for your chosen diagnostics; values
must be finite JSON-serializable data. Support logs define no performance metrics.
The support layer never saves a model automatically. `context.save()` writes a
schema/config-tagged PyTorch checkpoint through a temporary file and atomic rename;
reusing a name replaces that checkpoint. Choose your own checkpoint cadence and
retention. Provide tensors/primitives/containers compatible with
`torch.load(weights_only=True)`; load on CPU and move states to your selected device.
Do not put arbitrary custom Python objects in checkpoints.

## Small checks before long training

First run setup and upstream simulator checks above. Then implement and run your
own small task check: reset, validate finite observations against your space and
units, apply valid actions, inspect contacts/lift and verify your reward and
termination. Do this before enabling the trainer. The upstream sim check cannot
catch errors in custom observations, actions or task logic.

Create a separate configuration for a short run **after you select its parameters**:

```bash
cp configs/grip.json configs/grip-small.json
# Edit grip-small.json with your chosen task/PPO settings and small-run limits.
python -m grip_support train --config configs/grip-small.json --check-only
python -m grip_support train --config configs/grip-small.json
```

Implement the chosen limit in your core; no step-count field or default PPO
hyperparameters have been imposed. Check that real rollouts/updates occur and
that you can save/load/resume a checkpoint before launching a long job. Readiness
is your core's self-report, not evidence that rollouts or PPO are correct.

## Isolate problems

| Symptom | Next check |
|---|---|
| Missing package or incompatible dependencies | Activate, check `which python`, run `setup-check`; use `uv pip check --python .venv/bin/python`. |
| Simulator fails before task code | Run `sim-check`; inspect Vulkan ICD, assets and full error. GPU CUDA availability does not imply Vulkan rendering works. |
| Upstream simulator works, custom task fails | Check task registration/reset and your simulator construction independently of PPO. |
| Invalid observations/actions | Check shapes, dtypes, finite values, spaces, units, frames and normalization at reset and every step; compare training/deployment weight substitution. |
| Training crashes or produces invalid updates | Keep task checks passing, inspect run failure events and invoke your core directly for a full traceback; check your PPO tensors/optimizer/checkpoint restoration. |
| Training runs but behavior is poor | Use your chosen evaluation protocol; inspect real trajectories, task/reward signals, exploration and estimator behavior. Setup success cannot diagnose policy quality. |

For a full traceback of CLI runtime errors:

```bash
python -c 'from grip_support.__main__ import main; raise SystemExit(main())' train --config configs/grip-small.json
```

## Reproduce and resume

Use a run's saved `config.json`, same dependency lock, Git commit **and** local
changes, same simulator assets/backend and environment variables. Preserve your
new source/config files explicitly: metadata lists untracked files but the patch
does not capture their contents. Save them in version control or a separate copy.
The package versions are recorded, but the whole environment/assets are not bundled.
A seed alone does not guarantee determinism across hardware, physics or versions.

Resume loads the supplied checkpoint only after readiness checks, verifies its
schema and exact config digest, and passes the payload to your core. Restore
`checkpoint['state']` yourself; loading does not automatically restore the model.
Save/restore policy, optimizer, learning counters/schedules, normalization,
Python/NumPy/PyTorch RNG states and your chosen estimator/object state as required.
If exact continuation needs simulator state, buffers or worker RNGs, you must
capture those too. Define whether resume continues mid-episode or resets; document
any approximation. The startup seed is applied before your core restores RNG state.
Checkpoint writes are atomic on the filesystem but are not power-loss durability
or backup guarantees. Changed configuration is rejected; define an explicit,
reviewable migration if you need to change it rather than silently bypassing this.

## What simulator checks establish

A successful PickCube reset/render/step confirms that this installed simulator
can run with the selected backends. CUDA availability depends on the machine and
session; it is separate from the starter's CPU simulation and rendering settings.
Support checkpoint/log/config checks are independent of task learning. Neither
the starter nor the CLI checks establish training or policy performance.

# Weighted floating-goal PickCube

Run from the project directory:

```bash
cd /home/ubuntu/faliure
source scripts/activate_grip.sh
python learning-withoutCLI/train_ppo.py
python learning-withoutCLI/inspect_policy.py
```

Training saves under `runs/learning/<run>/`. Inspection selects the newest
completed compatible weighted run and saves under `runs/inspect/<inspection>/`.
It does not select old 21-input checkpoints or integration-check runs. Edit the
SETTINGS dictionary at the top of each script. No command-line flags are needed.

## What the three files mean

- `lift_task.py`: the simulator task, actual mass/inertia, observations and floating target.
- `ppo.py`: the actor and critic, using the original ManiSkill network.
- `train_ppo.py`: coordinates training using the pinned ManiSkill PPO loop.

The loop and architecture come from ManiSkill v3.0.1 commit
`a4a4f9272ad64b1564035874b605ceb687b63ed8`. The source remains unchanged in
`examples/maniskill_pick_cube/ppo_upstream.py`, with its Apache license. Each run
freezes the task, model, upstream source and runtime beside a provenance manifest.

## What stays aligned with the working example

Same Panda, cube/table scene, randomized cube placement, native
`pd_ee_delta_pos` controller, 50-step attempts, normalized dense PickCube reward
and success condition. The actor and critic each have three 256-unit tanh layers.
The original Gaussian exploration, PPO clipping, finite-horizon learning targets
and episode-ending value handling are retained.

Success means the **cube**, not the empty arm, is within 2.5 cm of the goal and
the arm is nearly stationary. Inspection also requires confirmed grasp for its
separate `held_goal` metric. Continuing inspection to the full attempt checks
holding after an initial success.

## The requested differences

1. The target retains random XY coordinates, but always floats above the table.
   SETTINGS `goal_clearance_m=[0.10,0.30]` chooses the goal centre so an upright
   cube would have 10–30 cm bottom clearance. The old fixed 8 cm threshold is gone.
   The existing green sphere is the target marker.
2. Physical mass is 0.040, 0.064 or 0.100 kg. Inertia scales with mass; shape and
   friction remain standard. True gravitational **weight in newtons** is appended
   to the original 42 inputs. This makes **43 inputs**.
3. Training uses a smaller balanced GPU batch for this machine: 63 robots, 21
   at each mass; nine evaluation robots, three at each mass. Each GPU environment
   retains its assigned mass across resets. Across the shared policy's experience,
   all three masses are present equally. CPU single-robot checks cycle mass at reset.
4. By default training initializes from the published working PPO policy.
   Its original weights are copied into the new network. The added weight-input
   column starts at zero, preserving the original behavior. Training must learn
   to use that feature; initialization alone is not adaptation. Set
   `initialize_from_pretrained=False` to train from random weights instead.

The pretrained source is
[haosulab/ManiSkill_Demonstrations](https://huggingface.co/datasets/haosulab/ManiSkill_Demonstrations),
revision `d674485bbffdd533914e52d272fdda34c0515608`,
`ppo_pd_ee_delta_pos_ckpt.pt`. Its published SHA256 is verified on every use.
Its exact training parameter overrides are not known; our settings follow the
pinned PPO reference rather than claiming an exact reconstruction of that run.

## Measurements and commands

| Input group | Count |
|---|---:|
| Joint positions, including fingers | 9 |
| Joint velocities | 9 |
| Grasp flag | 1 |
| TCP position/orientation | 7 |
| Floating goal position | 3 |
| Cube position/orientation | 7 |
| TCP-to-cube displacement | 3 |
| Cube-to-goal displacement | 3 |
| True object weight, N | 1 |
| Total | 43 |

The four normalized action numbers request XYZ position increments and finger
opening (-1 closed, +1 open). Orientation is maintained by the native controller.
Raw contact forces are logged for inspection; they are not extra model inputs.
Images remain viewing artifacts, not model inputs.

## Training settings and checkpoints

Default budget is **10,001,250 interactions**: 3,175 rollouts of 63 × 50 = 3,150.
Each rollout is split into seven minibatches of 450, with four learning epochs.
This is a full training budget, substantially longer than the old 25,600 steps.

Reference choices: Adam learning rate 0.0003, gamma 0.8, GAE lambda 0.9, PPO clip
0.2, critic coefficient 0.5, gradient limit 0.5, entropy coefficient 0, policy
change stopping threshold 0.1. The GPU batch size is our hardware adjustment.
The training reward is the original reach + grasp + move-to-goal + stillness
reward, with a success boost and division by five.

`ckpt_<iteration>.pt` is saved at evaluation points; `final_ckpt.pt` is saved
on completion. These are original-style **network weights**, with settings and
source metadata in the neighboring manifest. Setting `checkpoint` starts from
saved compatible weights with a fresh Adam optimizer and simulator; it is not
an exact optimizer-state resume. Old custom 21-input/seven-output checkpoints
cannot be used. The original 42-input pretrained model requires the explicit
initialization conversion.

For CPU training choose `sim_backend="physx_cpu"`, `num_envs=1`,
`num_eval_envs=1`, and whole 50-step rollouts. GPU training is the default.
CPU scenes rebuild at reset to clear stale contact flags.

## Test whether weight information helps

Inspection uses the actual masses selected in SETTINGS. You can also test unseen
intermediate masses such as 0.050 and 0.080 kg. It uses the same reset seeds for
both input conditions at every actual mass:

- `true`: supply the actual object's weight.
- `nominal`: supply the weight of a 0.040 kg cube while physical mass stays unchanged.

The current default compares actual 0.100, 0.500 and 1.000 kg cubes, with ten matched
starts per mass using the correct weight and ten using the 0.040 kg estimate.
The 0.500 and 1.000 kg cubes are heavier than any training cube. Their correct
weight inputs are also outside the training range, so failures in both conditions
do not establish that an incorrect estimate was responsible. A run-level
`success_rates.png` compares final grasped-at-goal success for both conditions. Only the last
model input changes between conditions. Both conditions save two camera views
for their first attempt. Change `masses_kg` and `nominal_mass_kg` in the inspection
settings to try other actual masses or estimates; this does not retrain the model.

Each attempt rebuilds the CPU scene so contacts from the previous attempt cannot
carry over. The original 42 starting measurements must match across conditions
and masses. Both input conditions record their first attempt with elevated camera
views, initial/final/closest-held-goal PNGs, GIFs and plots. All attempts log actual measurements,
the exact inputs fed to the model, actions, reward and success. GIFs default to
half speed; plot axes use simulation seconds.

`summary.json` groups goal success and grasped goal success by mass and input
condition, measuring both success at least once and success at the end. A higher
correct-weight result supports a benefit from knowing weight. Equal results mean
these trials do not demonstrate that benefit. A small sample is not proof of
general robustness. Compare enough matched starts and repeat independent training
seeds before claiming an improvement.

This is a feed-forward weight-conditioned policy. It does not estimate unknown
weight, remember previous attempts, or update from success/failure during
inspection. Those would be separate experiments.

## Verification performed

The reward check confirms equivalence with the installed original task's reward,
floating targets and actual weight. The training check verifies mass/inertia,
matching reset states, native opening endpoints, preservation of the published
policy at initialization, finite PPO updates, learning in the new input column
and checkpoint reload.

```bash
python learning-withoutCLI/checks/check_reward.py
python learning-withoutCLI/checks/check_training.py
```

These checks validate implementation, not learned adaptation. A short 6,300-step
GPU run verified the actual 63-robot configuration; its artifacts are separated
under `runs/checks/alignment/`. The full default run has not been started.

The matched inspection check used four masses (including unseen 0.050 kg), one
reset seed and two input conditions: all eight attempts reached the goal while
grasped. Success was identical with true and nominal weight inputs, so this small
check does not establish a weight-information advantage. Two-camera artifacts
and verified logs are under
`runs/checks/alignment/inspection/20261007T220434-15b51dde/`.

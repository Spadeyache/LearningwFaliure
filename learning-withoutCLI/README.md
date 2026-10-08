# Grip-aware PPO: current setup

Run the same plain scripts:

```bash
cd /home/ubuntu/faliure
source scripts/activate_grip.sh
python learning-withoutCLI/train_ppo.py
python learning-withoutCLI/inspect_policy.py
```

Edit SETTINGS at the top of each script. Training saves under
`runs/learning/<run>/`; inspection saves under `runs/inspect/<run>/`.
Check artifacts stay under `runs/checks/`.

## What the files do

- `lift_task.py`: cube mass/inertia, floating goal, measurements and reward.
- `grip_controller.py`: native Panda finger opening plus a chosen motor force limit.
- `ppo.py`: actor/critic and conversion of existing models into the larger network.
- `train_ppo.py`: warm-start the latest model and run the pinned ManiSkill PPO loop.
- `inspect_policy.py`: run without learning, log signals and compare weight estimates.
- `checks/`: optional checks of controllers, rewards, PPO updates and loading.
- `examples/`: simulator starter, original ManiSkill references and earlier experiments.

## Inputs: retain the previous 43 and append two forces

| Measurement | Numbers |
|---|---:|
| Joint positions | 9 |
| Joint velocities | 9 |
| Grasp contact flag | 1 |
| Hand pose | 7 |
| Floating goal position | 3 |
| Cube pose | 7 |
| Hand-to-cube displacement | 3 |
| Cube-to-goal displacement | 3 |
| True object weight, newtons | 1 |
| Measured left finger compression, newtons | 1 |
| Measured right finger compression, newtons | 1 |
| Total | 45 |

Object weight remains at index 42. The new forces are at indices 43 and 44.
Force observations are measured contact forces projected along each finger's
opening direction, with negative compression clamped to zero. They are neither
requested motor limits nor the grasp detector's binary flags.

## Actions: retain the previous four and append strength

The five normalized actions are XYZ hand movement, finger opening, and
per-finger motor force limit. The arm settings and native opening mapping stay
unchanged. Opening maps from -1 closed to +1 open. Strength maps from -1 to
0.25 N and +1 to 40 N **per finger**, controlled by `grip_force_limits_n`.

Strength caps how much the native position-drive motors may push. It does not
ask the simulator to fabricate an exact contact force. Measured forces can also
contain collision impacts. Both fingers use the same requested limit, and each
parallel robot can choose its own limit. The cap applies to both closing and
opening effort; a higher limit also lets the fingers open more firmly. Native implicit position-drive
integration is retained on CPU and GPU.

The real Franka gripper also exposes width and grasp force, but its API and
force convention are not identical to our simulated per-finger motor cap.
The custom action is a project extension, not ManiSkill's original baseline.

## Objective: carry and hold with only the force needed

The green target is a floating point for the **cube centre**, at 10–30 cm
upright bottom clearance, retaining the original randomized XY.
The task keeps PickCube's reaching, grasping, carrying and stillness terms.
Success additionally requires finger contact while at the target with a still arm.

Each step subtracts:

```text
grip_force_cost × clamp(mean measured finger compression / maximum motor limit, 0, 1)
```

The default coefficient is 0.05. Thus the cost is at most 0.05 per step;
successful holding remains the dominant reward. This encourages lower measured
squeezing while still holding. It does not prescribe a force from a weight formula
or guarantee that the learned policy will use weight. All reward parts and the
total are logged, including after success.

Training now continues through a complete 50-step attempt after reaching the
goal. That gives the policy experience holding the cube, rather than immediately
resetting on the first success. Each attempt is 2.5 simulated seconds.

## Fine-tuning the latest trained policy

By default `checkpoint="latest"` chooses the newest completed main training
checkpoint compatible with either the previous weighted policy or this extension.
Checks never participate in automatic selection. A specific path pins a model.
If no compatible model exists, selection stops with an explanation.
To start from the published model instead, set `checkpoint=None` and leave
`initialize_from_pretrained=True`. Set both to None/False for random initialization.

A previous 43-input/four-action model is converted by copying every learned
existing weight, zeroing the two added input columns, and preserving the first
four action outputs and critic predictions. The added strength output initially
requests the maximum allowed strength, with exploration. It must learn during PPO.
The new motor cap and reward change physical behavior, even if copied actions match.

The official 42-input/four-action model is also convertible; its added weight
and force columns start at zero. Existing 45-input/five-action models load directly.
Old custom 21-input/seven-action policies are incompatible.

Continuation loads model weights but restarts Adam and simulation. It is
fine-tuning, not exact optimizer-state resumption. Runs freeze the controller,
task, model, launcher, pinned PPO source and license and record the initialization
checkpoint/hash plus source settings. Earlier files and artifacts remain intact.

## Starting training settings

The mass range is 0.040, 0.064, 0.100, 0.250 and 0.500 kg. Shape and friction
remain unchanged; physical inertia scales with mass. Sixty GPU environments
provide twelve robots per mass, with ten evaluation robots (two per mass).
GPU masses remain assigned across resets. CPU one-robot checks cycle masses.

One rollout contains 60 × 50 = 3,000 interactions.
The default fine-tuning budget is 1,002,000 interactions: 334 collect/learn cycles.
Each cycle has up to four PPO epochs, ten minibatches per pass, and target-KL
early stopping. The terminal's Epoch counter means collect/learn cycles.
Learning rate is 0.0001; other PPO loss/advantage settings retain the reference.
These are starting choices, not tuned or proven settings.

PPO remains the pinned ManiSkill baseline at commit
`a4a4f9272ad64b1564035874b605ceb687b63ed8`: three 256-unit tanh layers per network,
learned Gaussian exploration, clipping actions before physics, and finite-horizon
GAE. The source baseline is preserved unchanged; the runtime replaces the model
and task integration. Published checkpoint metadata does not establish the exact
original training seed, budget or hyperparameter overrides.

## Inspect whether grip strength changes with weight

Inspection runs ten matched starts per actual mass with both true and fixed
40 g reported-weight inputs. Only index 42 changes in the nominal condition;
measured finger-force feedback stays available. The model weights are unchanged.

Outputs include:

- `summary.json`: success, grasp loss after lifting, average measured compression
  and requested strength during lifted contact.
- `success_rates.png`: success rates by physical mass and reported weight.
- `grip_strength_by_mass.png`: measured force and requested limit by mass.
- `steps.jsonl`: all actual measurements, fed inputs, actions and reward parts.
- Two camera GIFs and initial/final/closest-held-goal PNGs for the first attempt
  in **both** conditions at each mass.
- Per-attempt plots of rewards, forces, requested limits and cube position relative
  to the fingers.

Force averages include only grasped steps with cube bottom clearance above 3 cm.
Missing averages mean no qualifying contact; compare success rates alongside
force plots. Loss of a grasp flag can mean opening or dropping, not confirmed
slipping. Relative cube motion and recordings help diagnose it.
Friction is still the original setting; no slipping or failure is artificially forced.

A successful experiment should demonstrate secure holds across masses, lower
force usage for light cubes where feasible, and repeatable comparisons against
fixed strength/incorrect weight. True-weight versus nominal input alone does not
prove adaptation from past failures. The policy is feedforward, receives true
weight during training and has no learned weight estimator or persistent memory.

The original pretrained runner uses the preserved v1 weighted task in
`examples/maniskill_pick_cube/weighted_lift_v1.py`, with its original controller
and reward. It is a separate reference, not an evaluation of this new controller.

## Verification of this extension

CPU reward/controller checks and a 150-step PPO run passed. A 6,000-step GPU
run with 60 robots passed, including independent limits and partial-reset isolation.
Both added force columns and the strength output changed during PPO updates,
and the final model reloaded exactly. Six inspection attempts exercised raw logs,
new force plots, rewards, and both cameras. These are integration checks; the
long fine-tuning budget has not been run and learned adaptation is unproven.

A separate fixed-position hold diagnostic used one matched starting seed.
At a 1 N per-finger motor limit, a 40 g cube stayed lifted while a 500 g cube
dropped. At 5 N, both stayed lifted. This establishes a physical force/weight
tradeoff without changing friction, rather than proving that PPO learned it.
The inherited grasp detector requires 0.5 N contact on both fingers; very gentle
physically stable holds can fall below that binary detector threshold.

Artifacts: `runs/checks/grip_extension/calibration/20261008T031936-anchored/`,
`runs/checks/grip_extension/gpu_training/20261008T031725-a918879c/`, and
`runs/checks/grip_extension/inspection/20261008T031931-9f92e11a/`.

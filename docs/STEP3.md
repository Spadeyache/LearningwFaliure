# Step 3: clean-only calibration and perturbation replay

The trained model and split manifest are locked before perturbation evaluation.
Thresholds for the learned model, persistence, and constant velocity are stored
separately in results/calibration.json. No failure examples set these thresholds.

## Calibration

For each control transition, compute four errors:
TCP position norm (m), TCP shortest rotation angle (rad), cube position norm (m),
and cube shortest rotation angle (rad). Divide each by its validation-set 95th
percentile, floored at 1 mm for position and 0.01 rad for orientation.
The scalar score is the maximum of these four normalized errors.

For each of the 15 clean calibration episodes, take its maximum score. The alarm
threshold is the largest of those episode maxima; an alarm requires a strictly
greater score. This is a conservative empirical rule. With only 15 calibration
episodes, it does not establish a certified 95% clean-episode coverage rate.
Validation chooses scales; calibration chooses thresholds; test does neither.

Thresholds in this run: learned 1.844924, persistence 1.371084, constant velocity
2.090219. Their different scales mean raw thresholds are not directly comparable.

## Simulator interventions

Only the 15 test identities are replayed. Each has these four conditions:

| Condition | Intervention | Timing |
|---|---|---|
| clean | None | Full original action sequence |
| cube_shift | Move cube center +0.08 m along world x, preserve orientation/velocity | Before action floor(0.35*T) |
| gripper_open | Replace the gripper's applied command with +1 (fully open) | Before action floor(0.55*T), through episode end |
| arm_hold | Hold the seven arm targets at their current qpos; gripper command unchanged | 10 actions beginning at floor(0.55*T) |

These are controlled simulation faults, not claims of realistic physical noise.
The displacement uses ManiSkill's Actor.set_pose/Pose.create_from_pq APIs.
Action interventions model differences between issued commands and actuator behavior.
The official replay_cpu_sim function still drives the action sequence.
The original source demo and initial-state arrays are never overwritten.

The test generator checks every state and RGB pixel against the clean source up to
the injection point. Unperturbed controls must match the entire episode and succeed.
Later states always come from physics. Failed and recovered trials are both saved.

## Additional NPZ keys

The clean schema is retained, including T+1 observations and T transition values.
These files are a separate evaluation dataset; never feed them into training.

| Key | Shape / dtype | Meaning |
|---|---|---|
| action | (T,8), float32 | Original intended commands; model conditioning input |
| applied_action | (T,8), float32 | Commands actually passed to the simulated controller |
| fault_active | (T,), bool | Whether an intervention was directly applied at that transition; not a failure label |
| condition | (), Unicode | clean, cube_shift, gripper_open, or arm_hold |
| injection_step | (), int64 | Zero-based action index; -1 for clean |
| clean_episode_sha256 | (), Unicode | Hash of the matched clean NPZ |
| perturbation_json | (), Unicode JSON | Exact parameters, timing, source path, and split-manifest hash |

Observation injection_step remains pre-fault. Observation injection_step+1 is the
first post-intervention observation. Final success is the simulator's real task
evaluation, not the mere presence of an intervention.

## Commands

After activating the existing environment and Vulkan exports:

```bash
python scripts/calibrate_detector.py
python scripts/collect_perturbed_episodes.py
python -m unittest discover -s tests -v
```

Outputs are results/calibration.json and data/perturbed/*.npz.
A replay_summary.json lists file hashes, conditions, injection times and outcomes.
For a four-trial smoke test, use --limit 1 --output-dir checks/perturb_smoke.
Existing outputs are preserved; choose new paths to repeat experiments.

Sources:
[ManiSkill replay](https://github.com/mani-skill/ManiSkill/blob/main/mani_skill/trajectory/replay_trajectory.py),
[Actor state/pose APIs](https://github.com/mani-skill/ManiSkill/blob/main/mani_skill/utils/structs/actor.py),
[Pose constructors](https://github.com/mani-skill/ManiSkill/blob/main/mani_skill/utils/structs/pose.py),
[Panda controller units](https://github.com/mani-skill/ManiSkill/blob/main/mani_skill/agents/robots/panda/panda.py).

## Observed replay outcomes

All 60 trials passed clean-prefix checks. All 15 clean controls reproduced
states, pixels, rewards and flags exactly.

| Condition | Trials | Successes | Failures |
|---|---:|---:|---:|
| clean | 15 | 15 | 0 |
| cube_shift | 15 | 0 | 15 |
| gripper_open | 15 | 1 | 14 |
| arm_hold | 15 | 14 | 1 |

These are simulator task outcomes, not detector performance measurements.

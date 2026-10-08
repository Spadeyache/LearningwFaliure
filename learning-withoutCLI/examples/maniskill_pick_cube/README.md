# Official ManiSkill PickCube PPO example

The main training setup has since been aligned with this example: see
[the weighted setup](../../README.md). The pretrained runner still runs its
original 42-input weights; when testing the current custom task it discards the
added weight input and uses the current floating-goal task. The 8 cm custom-task
results below are historical measurements from the earlier task version.

## Watch a published trained policy first

```bash
cd /home/ubuntu/faliure
source scripts/activate_grip.sh
python learning-withoutCLI/examples/maniskill_pick_cube/run_pretrained.py
```

`run_pretrained.py` downloads a small official PPO checkpoint, verifies its
published SHA256, and runs it without changing its weights. It first evaluates
20 randomized attempts in original PickCube, then 20 in your existing LiftTask
with masses 0.040, 0.064 and 0.100 kg. Edit SETTINGS at the top. No new packages
or training are needed. This runs a neural network, not a scripted grasp.

The selected checkpoint comes from the
[official demonstration dataset](https://huggingface.co/datasets/haosulab/ManiSkill_Demonstrations/tree/d674485bbffdd533914e52d272fdda34c0515608/demos/PickCube-v1/rl),
pinned to revision `d674485bbffdd533914e52d272fdda34c0515608`:
`ppo_pd_ee_delta_pos_ckpt.pt`, SHA256
`0b17b5ed9690ccf83111d0f09af8d1599f69ee7ba0077e1aac48814ac78ce99c`.
Its metadata identifies a dense-reward PPO policy trained on PickCube-v1 with
state observations and the native `pd_ee_delta_pos` controller. The dataset
declares Apache-2.0 licensing; the upstream code license is retained here.

This checkpoint needs its original **42 state inputs**, including joint
positions/velocities, gripper pose, cube pose and goal information. For the
current weighted task the runner discards the appended weight measurement.
Its **four outputs** command XYZ movement and finger opening through the native
controller. The actor and critic each have three 256-unit layers.

Contact forces and physical mass are logged, but are not additional inputs to
this original checkpoint. The main training script explicitly converts it to a
43-input policy before learning with weight. Old 21-input/seven-output models
are incompatible.

Original PickCube success means reaching its random goal and becoming nearly
static. The current custom task uses a floating goal and varied masses with
the same reward/success rules. The older custom task required a grasped 8 cm
lift; the historical results below refer to that older version. The published
runner reports its task success plus an independent grasped 8 cm measurement,
both at least once and at the end. It continues after success for 50 steps in
original PickCube and 100 in the current custom task. CPU results can differ
from the published GPU setup.

All generated files live under
`runs/maniskill_pretrained/pick_cube/<run>/`, labelled
**OFFICIAL PRETRAINED PPO**. Models are cached in the sibling `models/` folder.
Each evaluation has a provenance manifest, a combined summary, separate task
summaries, and raw state/action/reward/contact logs for every attempt. The first
three attempts per task also save front-right/top and front-left/top GIFs,
initial/final/peak-grasp PNGs and measurement plots. GIFs play at half speed by
default; plots use real simulation seconds. This runner never selects one of
our untrained or locally trained checkpoints by modification time.

## Evidence behind the choice

These are reported results from the linked authors, with different setups;
they do not guarantee the same rate for the downloaded checkpoint here.

| Source | Reported successful behavior | Relevance |
|---|---|---|
| [ManiSkill3 paper, section IV-C](https://arxiv.org/html/2410.00425v2) | State-based PPO approaches 100% PickCube success on an RTX 4090. | Same simulator and task family; state policy. |
| [Official demo gallery](https://maniskill.readthedocs.io/en/latest/user_guide/demos/gallery.html) | Real robot picks the cube and returns to rest in 18/20 trials. | Separate vision policy and Koch robot; evidence of actual grasp/lift behavior, not these Panda weights. |
| [Independent PickCube PPO reproduction](https://github.com/ymt200120/maniskill-pickcube-ppo) | Three seeds report 100%, 100%, 95% final success in 20 evaluations each: 59/60. | Independent state-PPO reproduction; its weights are not the ones used here. |
| [RLinf ManiSkill benchmark](https://rlinf.readthedocs.io/en/latest/rst_source/examples/embodied/maniskill.html) | PPO-OpenVLA-OFT reports 97.66% on the training-distribution put-on-plate task. | A placement example, but a different vision-language model requiring much more hardware. |

PickCube carries and holds the cube at a target. It does not train a full
place-and-release sequence. Your requested grasp-and-lift task is the one
implemented and measured here.

## Results verified in this workspace

Evaluation `runs/maniskill_pretrained/pick_cube/20261007T160411-c3dd5f0f/`
used the four-action official checkpoint, deterministic actions, CPU physics,
and reset seeds 1000–1019. The same weights ran in both tasks without training.

| Measured condition | Original PickCube, 50 steps | Your LiftTask, 100 steps |
|---|---:|---:|
| Grasped at least once | 20/20 | 19/20 |
| Task success at least once | 19/20 | 14/20 |
| Still grasping at the end | 19/20 | 18/20 |
| Task success at the end | 19/20 | 2/20 |

The task success definitions differ, so those rates are not directly comparable.
Your mass-specific 8 cm successes were 6/7 at 0.040 kg, 5/7 at 0.064 kg, and
3/6 at 0.100 kg. This small sample couples masses to different reset seeds;
it is not a controlled mass comparison or a demonstration of adaptation.

The pretrained policy visibly grasps and lifts in your simulator. Continued
evaluation reveals a mismatch: your marker puts the cube centre exactly at the
8 cm clearance boundary. Many held cubes settle slightly below that height,
so your stricter success predicate becomes false even though grasp remains
true. One attempt lifts then drops; another never grasps. These outcomes are
retained in the raw logs and summaries. No reward/threshold was changed to
inflate success. This is a working published-policy baseline, not evidence
that our custom 21-input policy has learned or that placement/release works.

All 3,000 transitions were checked for 42 finite state inputs and four actions;
custom reward-component sums match returned rewards. Six pairs of camera GIFs
have the expected 51/101 frames, 100 ms playback and distinct views. The model's
published hash still matches after evaluation. See `verification.json`,
`manifest.json` and `summary.json` in that run.

## Train the upstream example yourself

This is the ManiSkill v3.0.1 PPO baseline at commit
`a4a4f9272ad64b1564035874b605ceb687b63ed8`. The original source is
`ppo_upstream.py`, preserved unchanged with its Apache license.

This separate launcher uses the stock goal distribution, 42 inputs and eight
joint-delta/finger-opening actions. The current main setup uses 43 inputs, four
native XYZ/finger-opening actions, varied mass and floating goals. Both retain
the original PickCube reward, stationary-arm goal success and network widths.

From the project folder:

```bash
source scripts/activate_grip.sh
python learning-withoutCLI/examples/maniskill_pick_cube/train_example.py
python learning-withoutCLI/examples/maniskill_pick_cube/inspect_example.py
```

Edit SETTINGS at the top of the launchers. Training defaults to 256,000 steps,
64 GPU environments and the upstream PPO defaults, with minibatch count adjusted
for the smaller batch. This is a starting experiment, not the published benchmark
budget or a guaranteed successful policy. Rendering uses the existing CPU renderer.
The launcher supplies the WSL CUDA library path and limits CPU threads; all
adjustments and the source hash are recorded in each run's manifest.

Artifacts live only in `runs/maniskill_example/pick_cube/<run>/`: upstream model
checkpoints, TensorBoard metrics, console.log, manifest.json and a reproducible
runtime copy. Run inspection after training: it defaults to the newest example
final checkpoint and writes two-angle GIFs, initial/final PNGs, raw state/action/
reward logs and success summaries under that run's inspect folder. Images are
labelled OFFICIAL MANISKILL EXAMPLE. It never selects custom lift checkpoints.

TensorBoard was added to the existing project virtual environment to run upstream
logging. Inspection uses the original network on one CPU simulator and runs five
50-step episodes without training. That is a diagnostic sample, not a benchmark.

## Grip-aware main setup

The main scripts now have 45 observations and five actions, including a motor
strength limit and measured-force reward cost. This pretrained reference keeps
its original four-action controller and uses the preserved weighted v1 task in
`weighted_lift_v1.py` for custom comparisons. It does not evaluate the new grip
controller. Main training can convert its checkpoint into the larger network.

# Article-inspired cube lift in ManiSkill

This experiment adapts [Keith Chester's PPO project](https://hlfshell.ai/posts/ppo-pick-and-place/)
to **our goal: grasp one cube and raise its lowest point at least 8 cm above
the table**. It is not a copy of the author's sorting environment or a pretrained
model. Learning still starts from fresh network weights.

Grasping/lifting is the first physical stage of pick-and-place, but the article
does not train that stage separately. Its reported policy often slides objects
into bins; the author lists adding grasp/lift rewards as future work. Thus its
reported results do not establish that this cube-lift adaptation will succeed.

## Comparison with our existing implementation

| Part | Existing `learning-withoutCLI` implementation | Article / linked repository | This adaptation |
| --- | --- | --- | --- |
| Simulator | ManiSkill / SAPIEN; one CPU environment | panda-gym / PyBullet | ManiSkill; parallel GPU environments |
| Goal | Grasped cube with 8 cm bottom clearance | Sort varied shapes into bins | Same cube-lift condition as ours |
| Actions | XYZ, wrist rotation, finger opening: 7 | Default end-effector mode: XYZ and gripper: 4 | Native `pd_ee_delta_pos`: XYZ and finger opening, 4 |
| Inputs | 21: TCP/cube poses, weight, two force vectors | Per object: pose, velocities, type, dimensions; TCP pose/velocities and finger width | 38: article-style single-cube state, plus both force vectors and actual weight |
| Reward | Repeated reaching/grasping/lifting score, 0–1 | Step −1; floor −50; wrong/correct bin +200/+500 | Reach + grasp + lift, plus success bonus; normalized 0–1 |
| Ending | Success ends the attempt; otherwise 400-step limit | All objects removed, or trainer limit | 100-step limit; successful lifts can keep earning maximum reward |
| Networks | Separate actor/critic, each two 64-unit tanh layers | Actor 1024/512/256/128/64/32; critic 128/64/32; LeakyReLU | Article widths and activations |
| Exploration | Learned Gaussian spread, tanh-bounded actions | Fixed diagonal Gaussian variance 0.5 | Fixed variance 0.5; applied commands clipped to [−1,1] |
| PPO data use | GAE; shuffled minibatches; four epochs | Whole-episode discounted returns; full-batch updates; five cycles | ManiSkill GAE/minibatches; five epochs |
| Training size | Current settings: 25,600 steps, rollout 128 | Post reports 20–35 million steps and final rollout size 200,000 | Starting budget 1,024,000 steps; rollout 6,400 |
| Evaluation | Separate single-attempt inspection | Training reward plots and playback | Periodic separate evaluation, then three inspection attempts |
| Masses / adaptation | Three physical masses; true weight input; no history | Size/shape variation changes physical properties | Same three masses; true weight; no history |
| Checkpoints | Model, optimizer, counters, schema, RNG | Model weights and trainer bookkeeping, fresh optimizers after load | ManiSkill model state, manifest, frozen task/model source; no optimizer resume |

The author's repository entry point currently configures **3 objects, 5,000
steps per batch, 750 steps per episode and 200 million requested steps**. Those
are not the post's final reported settings. We inspected commit
`e13011177332b481eba9df9acfa3b4151cef29f5`:
[task](https://github.com/hlfshell/rbe595-rl-project/blob/e13011177332b481eba9df9acfa3b4151cef29f5/project/envs/sorter.py),
[models](https://github.com/hlfshell/rbe595-rl-project/blob/e13011177332b481eba9df9acfa3b4151cef29f5/project/ppo/model.py),
[trainer](https://github.com/hlfshell/rbe595-rl-project/blob/e13011177332b481eba9df9acfa3b4151cef29f5/project/ppo/pose_trainer.py),
[entry point](https://github.com/hlfshell/rbe595-rl-project/blob/e13011177332b481eba9df9acfa3b4151cef29f5/train_arm.py).
The task's `is_success` reports all objects removed, including floor/wrong-bin
outcomes; it is not a reliable measure of correct sorting. Our success measures
the physical grasp and cube clearance instead.

## How to run

From `/home/ubuntu/faliure`:

```bash
source scripts/activate_grip.sh
python learning-withoutCLI/examples/article_cube_lift/train.py
python learning-withoutCLI/examples/article_cube_lift/inspect_example.py
```

`train.py` has SETTINGS at the top. With the defaults, each rollout collects
64 robots × 100 steps = 6,400 interactions. PPO splits those into eight
minibatches of 800 and revisits the data for up to five epochs. The run collects
160 rollouts = 1,024,000 interactions. This is a starting experiment, not a tuned
budget or a guarantee of lifting. Increase `total_timesteps` in multiples of
6,400 for longer training. Changing `num_steps` changes data collected before
learning; the task's attempt length is `HORIZON` in `lift_env.py`.

`lift_env.py` defines observations, real cube mass/inertia, success and reward.
`model.py` defines the actor and critic. The launcher uses the existing pinned
ManiSkill PPO source beside `maniskill_pick_cube`, with an explicit runtime
replacement of its environment and Agent. The original source stays intact.
The article's network design is implemented independently here; its trainer
and PyBullet code are not copied into this project. ManiSkill's Apache license
is retained in `MANISKILL_LICENSE`.

The finger command is −1 closed, +1 open. Zero means partly open, so this change
does not force the policy to keep its fingers open during approach. Native
ManiSkill XYZ actions request up to 0.1 m per axis in the robot root frame;
the root is aligned with this table's world axes. Orientation is not an action.
It is maintained approximately by the position/IK controller. This is different
from our custom 0.015 m pose adapter and from PyBullet's controller dynamics.

The 31 article-style input values are cube position/Euler rotation/linear and
angular velocity (12), cube type and half sizes (6), TCP position/Euler rotation/
linear and angular velocity (12), and measured finger width (1). We append the
two measured force vectors (6) and true weight (1): total 38. Fixed scaling is
our addition. Cameras are for inspection and never enter the policy.

Each GPU environment gets one of 0.040, 0.064, 0.100 kg before physics starts;
it keeps that mass across resets. Cube position/yaw and robot initial pose vary.
There is no estimator, recurrent memory, or learning from past failures during
inspection. Responding to the true weight is different from inferring it from
experience.

## Reward and results

Before success the unnormalized reward is
`1 - tanh(5 * TCP_distance) + grasped + grasped * clamp(clearance/0.08, 0, 1)`.
Once grasped with 8 cm bottom clearance it becomes 5; normalized reward divides
by 5. The plot logs each contribution, including the success bonus. This is
our lift shaping using ManiSkill's reaching formula, not the article's sorting
reward. Keeping successful attempts running avoids cutting off future rewards
at success, which could favour delayed completion in our old training setup.
There is no additional floor penalty or early-closing penalty.

Output is always in `runs/article_inspired/cube_lift/<run>/`. A manifest records
the origin, article and ManiSkill commits, settings, source hashes and all
adaptations. Checkpoints and TensorBoard events are beside the exact task/model
and runtime source. The original custom and official-example runs have separate
folders and are never selected by this inspector.

Inspection defaults to the newest final checkpoint in this experiment's folder.
It runs three 100-step attempts, one at each mass, without learning. Each saves
two labelled camera GIFs, initial/final PNGs, raw named state/action/reward logs,
a measurement plot and a summary with grasping, clearance and success. It uses
one CPU simulator; training uses GPU physics, so this is a diagnostic check
across backends rather than a benchmark. Periodic training evaluation uses the
same GPU backend as training. Inspect the final checkpoint after training;
the last periodic evaluation may have occurred before the final update.

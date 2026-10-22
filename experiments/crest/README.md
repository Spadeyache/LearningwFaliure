# CREST for picking, lifting and holding

This package adapts **Sections III–IV of [Lee et al., CREST](https://arxiv.org/abs/2103.16772)**
to the existing Panda/ManiSkill physics environment. It implements both context
selection and context-to-controller mappings. It is not an implementation of a
failure classifier or an environmental estimator.

## Start here

```bash
cd /home/ubuntu/faliure
source scripts/activate_grip.sh

# Prints inputs, dimensions and a conservative cost estimate. No simulation/files.
python -m experiments.crest --plan-only

# Start a small intervention subset in a NEW output folder.
python -m experiments.crest --run --only mass,object_friction,goal_height,object_color_r \
  --max-rollouts 300 --output runs/crest/first_subset

# Resume the same scientific experiment; raising the rollout cap is allowed.
python -m experiments.crest --run --only mass,object_friction,goal_height,object_color_r \
  --resume --max-rollouts 600 --output runs/crest/first_subset

# All 21 candidates; this can require many CPU simulations.
python -m experiments.crest --run --output runs/crest/all_factors
```

Without `--run`, the CLI only prints a plan. The default configuration is
[configs/crest_lift.json](../../configs/crest_lift.json). It reads all 18 existing
factors from [failure_collection_varied.json](../../configs/failure_collection_varied.json)
and adds three RGB appearance controls. Change the CREST configuration or use a
copy to change search budgets and ranges. Do not change the preserved collection
configuration simply to start a smaller CREST experiment. `--only` holds all
other factors at their declared nominal values.

The default budget is **3,000 actual rollouts**, not a promise the full search
fits in that budget. The plan gives a deliberately pessimistic upper bound;
successful early stopping and caching reduce it. A budget-limited run exits with
code 2 and keeps its evaluation journal. Resume to continue it. It does not
publish a completed selection from a truncated experiment.

## Modules

| File | Responsibility |
| --- | --- |
| `spaces.py` | Named factors, numerical ranges, category encoding, single-factor interventions, bounded controller vectors. |
| `optimization.py` | Per-context REPS optimization with a bounded Gaussian search distribution. |
| `core.py` | Simulator-independent CREST: screen contexts, re-solve, breadth-first minimum-support search. |
| `lifting.py` | Existing physics adapter plus a fixed waypoint/strength skill. |
| `policies.py` | Full, reduced and partitioned upper-policy MLP architectures. |
| `config.py` | Separate experiment settings and side-effect-free planning. |
| `__main__.py` | Journaling, deterministic caching, provenance, resume and run budget. |

To add another task, implement `validate_context`, `initial_parameters`, and
`evaluate` from the `Task` protocol. The two search stages need no simulator
changes. To add a lifting factor, give it a domain and implement its actual
physical/appearance intervention in `scene_arguments`; adding a JSON name alone
is deliberately rejected by the adapter.

## What happens in one anchor

1. Sample a context and fix its reset seed. The first anchor is nominal by
   default; the remaining anchors sample enabled numerical factors uniformly
   and categories uniformly. Set `nominal_first=false` for all-uniform anchors.
2. Solve that specific task by optimizing a controller vector. An unsolved
   baseline supplies no relevance evidence.
3. Change exactly one **declared context factor**, keeping all controller
   parameters and the reset seed fixed. A failure is sensitivity evidence for
   that factor under this controller and context.
4. Warm-start optimization from the baseline controller in the changed context.
   A failed search is unresolved: the task might be infeasible, the controller
   inadequate, or the optimizer insufficient. It is not proof of irrelevance.
5. For a successful repair, try subsets of its parameter changes in increasing
   cardinality. The first successful subset is the smallest subset of **that
   discovered repair**, as in the paper's search. It need not be unique or
   globally minimal across all possible controller solutions.
6. Union the discovered context-to-parameter dependencies across tested anchors.

The paper uses a parameterized lower skill and an upper policy that predicts
its parameters. Here theta contains seven values:

| Controller parameter | Meaning |
| --- | --- |
| `grasp_x_m`, `grasp_y_m`, `grasp_z_m` | Fixed world-frame grasp waypoint. |
| `lift_target_z_m` | Fixed final TCP height. |
| `lift_speed_m_s` | Rate at which the vertical waypoint increases. |
| `close_duration_s` | Closing wait before lifting. |
| `grip_limit_n` | Motor force cap per finger, **not a measured contact-force target**. |

The skill approaches, descends, closes, lifts, then holds. It uses measured TCP
pose to track fixed targets; it does not secretly read an intervened object's
pose/physics/goal to correct its plan. The initial search guess uses the original
object pose and task goal, with a fixed 10 N grip cap; subsequent re-solves start
from the original theta. No PPO checkpoint is required or modified.

Success requires the object to be held within the existing 2.5 cm vertical goal
tolerance, arm joint speeds to meet the existing static threshold, and at least
2 cm bottom clearance for every sample in the final configured hold window.
Shaped approach/grasp/lift/goal scores guide unsuccessful searches, but only
the success criterion determines relevance and repair acceptance.

## Variables: existing task versus paper

The paper does **not** recommend a universal list of environmental parameters.
Its task contexts include block positions, orientation, height and RGB color;
crate contexts also include grasp geometry and desired opening angle. Distractor
objects supply irrelevant pose/color inputs. Physical parameters below are
task-specific extensions using the paper's intervention method, not a claim
that its block-stacking experiment selected mass or friction.

| Our candidates | Coverage and interpretation |
| --- | --- |
| `spawn_x`, `spawn_y`, `spawn_yaw` | Existing pose factors; analogous to paper position/orientation contexts. |
| `size`, `shape` | Existing geometry; size is uniform full extent/diameter, shape is cube or sphere. The paper varies block height, not every geometry type. |
| `goal_height` | Existing desired task outcome; analogous to paper goal/target geometry. |
| `mass` | Existing mass, with derived inertia; relevant to lifting physics, not assumed relevant in advance. |
| `object_friction`, `dynamic_friction_ratio` | Existing static friction and sliding/static ratio. |
| `finger_friction`, `table_friction` | Existing interacting surfaces, independently controllable. |
| `com_x`, `com_y`, `com_z` | Existing COM offsets; keep the configured physical-validity limits. |
| `inertia_scale` | Existing synthetic independent multiplier relative to primitive inertia. |
| `restitution`, `linear_damping`, `angular_damping` | Existing contact/dynamics factors. |
| `object_color_r`, `object_color_g`, `object_color_b` | Added visual appearance controls, analogous to the paper's RGB distractors. They change visual geometry color without changing materials or mass. |

There are **21 semantic factors and 22 encoded features** because shape is
one-hot encoded. No arbitrary numerical ordering is assigned to shape.

Useful extensions, **not yet implemented**, are independent box dimensions,
grasp orientation, independent horizontal goal position, distractor-object
position/color, and explicit robot/control calibration or sensor error models.
Visual lighting belongs in perception experiments if a visual policy is used;
this state/waypoint skill cannot assess visual-estimation relevance.

Important coordinate and intervention details:

- For CREST, object pose is explicit: `spawn_x/y` offset a fixed upright origin,
  and yaw offsets zero yaw. The old collection offsets a *random seeded* pose.
  This intentional difference prevents the same encoded context from hiding
  different starting object positions. Reset seeds still vary robot starts.
- The vertical goal follows object spawn XY. A spawn intervention consequently
  changes the target XY too, as in the existing lifting task. This is a semantic
  pose intervention, not an isolated test of independently specified target XY.
- Mass/size derive inertia; object friction derives dynamic friction using the
  ratio. These are documented descendants of the intervened semantic factor.
  COM/inertia are synthetic physical settings, not inferred density fields.
- The gripper has no commanded yaw in `pd_ee_delta_pos`. Any yaw conclusion is
  conditional on this fixed-orientation skill, not a statement about all grasps.
- All true context values are privileged simulation inputs during analysis.
  This does not make them available to a future real-world estimator.
- A color can be physically irrelevant to this controller and still be a useful
  visual **predictor** of material or mass. Do not interpret a CREST context mask
  as instructions to remove predictive appearance cues from your visual model.

## Results and upper-policy use

Each run saves the effective configuration, dependency versions and source
hashes plus a source snapshot. Resume rejects changed code/settings/runtime;
only the rollout cap may change. A per-run file lock prevents concurrent writers.
Every candidate reconfigures and resets its scene, using the same reset seed
for its baseline and intervention. Completed evaluations are reused on resume.

| Output | Contents |
| --- | --- |
| `evaluations.jsonl` | Exact context, theta, seed, physical readback, metrics and outcome for each actual rollout. |
| `events.jsonl` | Anchor/intervention decisions; replay on resume may append repeated logical events. |
| `report.json` | Per-factor counts, observed/recovered relevance, sparse dependencies, unresolved cases and examples. Written after search completes. |
| `policy_inputs.json` | Feature indices for full/reduced/partitioned policy construction; unresolved factors are retained conservatively. |
| `training_examples.json` | Successful context/theta pairs for later upper-policy initialization. |
| `manifest.json` | Identity, provenance, status, rollout count and any failure reason. |

`not_detected` means no effect was detected **over the tested contexts, ranges,
controller and success definition**. It is not a universal causal claim. A
generous fixed grip cap may make all tested masses succeed and therefore hide
mass relevance under a success-only criterion. Finite samples can also miss
interaction effects; varying anchors helps but provides no completeness proof.

`FullMLP`, `ReducedMLP` and `PartitionedMLP` are untrained upper-policy modules:
pass normalized/one-hot `ContextSpace.encode(context)` features, obtain a
normalized theta vector and use `ParameterSpace.denormalize` before executing.
The supplied examples are optional supervised warm-start data, not learned
weights. PPO pretraining and target-domain fine-tuning from the paper's Section V
are a later stage; this package does not claim to reproduce the paper's complete
sim-to-real experiments. Never reuse a changed input dimension with an old PPO
checkpoint without retraining.

## Validation

```bash
python -m unittest discover -s tests -p 'test_crest.py' -v
RUN_CREST_INTEGRATION=1 python -m unittest discover -s tests -p 'test_crest_lifting.py' -v
```

Core tests use known causal systems to verify single-factor interventions,
frozen controllers, minimum-cardinality repair, unknown outcomes, REPS search,
encoding, architecture masks and budget/resume behavior. The small CPU test
checks an actual held lift, unchanged physics under a color intervention, and
a fixed-goal failure repaired by changing only the lift-height parameter.

## Package location and saved runs

The canonical package is `experiments.crest`; `crest.*` imports and `python -m crest`
remain compatibility entry points. Shared physical environments and controller
interfaces live under `robot_adaptation.simulation` and collection factor design
under `robot_adaptation.collection`. New manifests snapshot those live shared
dependencies. Historical runs and their frozen source snapshots remain unchanged;
a changed source layout starts a new run rather than rewriting an old identity.

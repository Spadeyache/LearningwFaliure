# Failure-attribution data collection

This collector runs a frozen, cached ManiSkill PickCube policy over explicit
physical-property conditions and writes one `.npz` per episode. It preserves a
separate set of deployment-sensor proxies, simulator evidence, and outcome
labels. It does not train a classifier or infer causal explanations from a
failed attempt.

## Matched mass/friction experiment and gap atlas

The new default is `configs/failure_collection_matched.json`. Set **`seed_count`
to 10 for the pilot or 50 for the atlas**. Each seed runs one normal condition,
mass ×0.5/×2/×4, and object friction ×0.5/×2/×4: **70 or 350 primary attempts**.
Both object friction coefficients scale together; finger/table friction stays
fixed. Mass changes density and therefore scales the primitive's inertia too.
Shape, size, COM, policy, goal and initial robot/object state stay matched.
The earlier Cartesian configs and 72-episode dataset are preserved.
Each episode now rebuilds the PhysX scene. A same-seed teleport reset alone
retained hidden contact-solver history in a regression case, even though the
saved visible initial state matched exactly. Fresh-scene replay is tested with
another seed interleaved between repeats.

```bash
source scripts/activate_grip.sh
uv pip install -r requirements-atlas.txt
python -m failure_collection.collect --config configs/failure_collection_matched.json --output runs/failure_collection/matched_pilot --record-seeds 1 --check-determinism
python -m failure_collection.atlas runs/failure_collection/matched_pilot
# After checking labels, force_verification.json, residuals and preview GIFs:
python -m failure_collection.collect --config configs/failure_collection_matched.json --seed-count 50 --output runs/failure_collection/matched_atlas_50
python -m failure_collection.atlas runs/failure_collection/matched_atlas_50
```

`--seed-count` overrides the same single setting without editing the JSON.
Use a fresh output name for new experiments; compatible interrupted runs support
`--resume`. `--checkpoint PATH` selects a relocated copy of the same pinned
official policy. In a worktree without its own `.venv`, assets or checkpoint,
use the original workspace's interpreter, set `MS_ASSET_DIR` to its assets, and
pass the original cached checkpoint explicitly. Outputs still go to the current
checkout. `requirements-atlas.txt` adds scikit-learn/joblib/threadpoolctl to the
existing simulation environment; plotting already uses matplotlib.

Every primary NPZ includes `meta__episode_id`, `meta__run_role`,
`label__shifted_variable`, `label__shift_magnitude`, seed, actual physical values,
and a full simulator reset-state JSON plus its hash. Continuous distances are
`input__object_tcp_distance_m` and per-finger `input__finger_object_distance_m`;
these measure distance to the object's tracked origin, **not surface clearance**.
All existing pose, width, action, response and physics-rate force traces remain.
Exact object-pair force also has per-action means/peaks under `sim__` on every
run, including normal and retry episodes.

Each shifted archive adds:

| Field | Meaning |
|---|---|
| `residual` | T×19 differences aligned at the end of each action; reset force placeholders excluded. |
| `residual_channels` | Relative position (3), relative rotation (3), world position (3), world rotation (3), width (1), left/right object-contact force XYZ (6), with units in each name. |
| `residual_time_s` | Physical simulation seconds after reset. |
| `residual_source_valid_mask` | T×2 booleans: shifted, normal. Shorter run repeats its last sample but padding is false. |
| `residual_valid_mask` | Intersection: both sources are observed and valid. |
| `matched_normal_run_id` | Exact episode ID of the same-seed normal reference. |

Position/width/force residuals are shifted minus normal. Orientation uses the
shortest rotation vector `log(R_shifted @ inverse(R_normal))` in radians, so
equivalent quaternion signs cannot create fake gaps. Force uses the mean across
all physics substeps in that action. Matching checks initial object/TCP/joint
state, goal, seed and frequencies before saving. The normal run may itself fail;
`label__matched_normal_success` makes this visible. No outcome/property labels
are part of the residual feature vector.

**The atlas is a simulation diagnostic.** Its exact gripper–object force channels
require simulator body attribution. Net finger forces remain the deployment
sensor proxy in `input__`; a real robot would need appropriate sensing and
object attribution to reproduce the atlas channels. Mass/friction labels do not
establish a unique cause for individual failures.

`atlas.py` ignores normals and retries, resamples all residuals onto the same
physical-time window, and excludes padded samples. It standardizes flattened
trajectories for PCA. Logistic regression uses five folds **grouped by seed**;
all six shifts sharing a baseline stay together, and the scaler fits only the
training fold. Full trajectories answer the offline signature question, not
early-warning accuracy. Magnitudes are pooled in the mean curves (±1 SD).
The script saves `atlas_pca.png`, `atlas_mean_residuals.png`,
`atlas_confusion_matrix.png` and `separability.json` inside the run's `atlas/`.
The JSON records counts, folds, predictions, time window and the confusion
matrix (rows true, columns predicted). Chance/majority accuracy is 50% for a
complete balanced experiment. A PCA overlap alone is not a separability test.

## Failure events and controlled recovery tests

The original descriptive `label__failure_mode` remains. Additional heuristic
`label__failure_type` distinguishes slip, drop and miss when observed.
`label__failure_time_s` is unknown (NaN) for a miss or timeout; the separate
`label__failure_detection_time_s` records when a decision could be made.
Slip/drop masks and first event times remain even if the episode later succeeds.
`events.py` stores rule thresholds and version in each archive. Relative motion
can also mean rolling/reseating, and a drop-like event can include commanded
release, so these labels describe evidence rather than proving intent or cause.

Set `recovery.enabled` to `true` to run extra full-episode retries after failed
shifted attempts. They **start over from the same initial state**, with the same
physical properties and frozen policy. They are additional to the 70/350 primary
attempts and are excluded from atlas scoring.

- `slow_lift` factors 0.75 and 0.5 scale the bounded upward Z command while
  grasping. Other action axes and descent remain as commanded. Actual ascent
  speed is measured separately; this is not a guarantee of a specific speed.
- `grip_limit` requests ×1.5 and ×2 caps, checks available headroom and actual
  controller readback, then restores the cap. The stock 100 N limit already
  reaches the default 100 N ceiling, so those corrections are reported as
  skipped. A higher cap only counts as a force correction when force increases.
- Lower grasp-point retries require an explicit approach-stage controller and
  are not implemented by adding a blind position offset.

Each retry records its parent, correction and magnitude, measured force/speed
changes, whether the correction took effect, and success. `summary.json` reports
the smallest **tested** successful correction per direction; it does not claim
an untested minimum or a unique physical cause. Retry identity and reset state
are verified again on resume.

Schema `pick_failure_v2` adds these fields. The input loader still reads original
v1 archives and excludes all sim-only labels, recovery outcomes and residuals.

## Verified matched runs (October 12)

| Run under `runs/failure_collection/` | Primary attempts | Final successes | Shifted runs for atlas | 5-fold accuracy |
|---|---:|---:|---:|---:|
| `matched_pilot/` | 70 | 51 | 60 | 70.0% |
| `matched_atlas_50/` | 350 | 283 | 300 | 60.3% |

The 50-seed confusion matrix is `[[73,77],[42,108]]`, with mass then friction
on both axes. The signatures overlap substantially under this experiment;
60.3% is modest discrimination compared with the balanced 50% baseline.
All 326 full-run episodes that established a grasp had bilateral nonzero
contact force during grasp. Every seed had one identical visible reset state
across its seven conditions, and the 70 overlapping pilot/full trajectories and
force traces matched bitwise. Preview GIFs were inspected. All **64 tests**
passed, including the fresh-scene, interleaved-seed regression and CPU force
checks. Full-run source hashes match its saved source snapshot.

`recovery_check/` separately tested seed 1004: seven primary failures and 12
slower-lift retries, with no recovery. Eight retries changed the upward command;
four never reached an eligible grasp. Twelve stronger-cap requests were skipped
because the stock cap had no headroom. This checks the recovery harness, not a
general conclusion that slower lifting cannot help. Resume was also exercised.

## What the installed environment exposes

The workspace has ManiSkill **3.0.1**, SAPIEN **3.0.3**, and two different pick
interfaces. The distinction matters when selecting a checkpoint.

| Environment | Observation/action interface | Task and success |
|---|---|---|
| Installed `PickCube-v1` | 42 state values, four actions | Move a red cube within 0.025 m of the target; every arm joint must have absolute velocity at most 0.2 rad/s. Success does **not** separately require a grasp. |
| Workspace `GripWeightedPickCube-v2` in `learning-withoutCLI/lift_task.py` | 45 values, five actions | Carry to a floating goal with 0.10–0.30 m upright bottom clearance. Adds a true-weight input, two finger compression inputs, a motor-strength action, and a grasp requirement for success. |
| Workspace `GripWeightedHoldCube-v1` | Same 45/five interface | Places the object between the fingers and physically settles the grasp before the episode. The policy controls strength while the arm/opening commands are fixed. This is a hold exercise. |
| Collector `CollectionEnv` | Stock 42/four interface | Preserves upstream PickCube success and control while exposing independent physical-property construction. |

The hand is a Panda parallel two-finger gripper on a seven-joint arm. There are
nine position and nine velocity values: seven rotary arm joints and two linear
finger joints. Finger opening is the sum of the finger positions, nominally
0–0.08 m. Poses use `[x, y, z, qw, qx, qy, qz]`, metres and unit quaternions.

Stock Panda PickCube uses a 0.04 m cube, random XY in `[-0.1, 0.1]` m, random
yaw, and an upright initial placement on the table. Goal XY has the same range;
goal Z is sampled between the cube half-height and half-height plus 0.3 m. Arm
initialization adds joint noise with standard deviation 0.02 rad. The registered
horizon is 50 control steps; defaults are 20 Hz control and 100 Hz physics.

Native PickCube has no mass/COM/shape/friction reset-option interface. The custom
weighted task adds CPU `reset(options={"mass_kg": ...})` and constructor-level
mass/friction controls. Its default friction deliberately changes with mass;
its CPU reset also cycles masses unless a mass is supplied. Reusing only a seed
there would not fix all physical properties.

The collector rebuilds the CPU scene at every seeded reset and reads applied
physical values back from PhysX. It supports boxes and spheres as well as cubes. These variants and
nondefault physics are distribution shifts for the pretrained policy.

## Policy availability and privilege

An official PPO state-policy checkpoint is already cached under
`runs/maniskill_pretrained/pick_cube/models/`. `policy.py` verifies its complete
SHA256 and loads its 42-input/four-action network strictly. The frozen policy
uses its deterministic actor mean; raw and clipped commands are both logged.
The loader neither trains nor downloads a model.

The artifact is pinned to
[the official ManiSkill demonstrations dataset](https://huggingface.co/datasets/haosulab/ManiSkill_Demonstrations/tree/d674485bbffdd533914e52d272fdda34c0515608/demos/PickCube-v1/rl).
The workspace's learned 45-input/five-action strength models cannot be exchanged
with this checkpoint. The official policy uses exact simulator object pose and
simulator grasp status. Its observation vector is logged as **sim-only**; its
availability does not imply that its inputs are all deployable sensors.

The four normalized actions are root-frame XYZ position increments and finger
opening. XYZ maps to ±0.1 m relative to the current TCP. Opening maps to a
position target between −0.01 and 0.04 m **per finger**; the negative closed
target supplies compression against an object. The stock drive limit is 100 N
per finger. This limit is a motor setting, not a measured contact force or an
extra strength action. The controller requests a TCP target and joint targets;
it does not emit a distinct grip point or requested surface-contact positions.

## Proposed additions and their purpose

The schema includes the requested trajectories and physical labels plus the
following quantities. The checked-in definitions and every run's generated
`schema.json` keep the choices reviewable and versioned.

| Addition | Why it helps |
|---|---|
| Joint positions/velocities, finger opening velocity, commanded joint/TCP targets | Distinguish poor actuator tracking or incomplete closure from object motion inside a closed hand. |
| Full XYZ finger forces, local finger forces, interval means/peaks and left/right compression imbalance | Retain tangential loading, short collisions and one-sided contact that two scalar forces can hide. |
| World and TCP-relative object translation/rotation response, finite-difference velocities | Separate whole-arm motion from translational or rotational slip. The derivatives use the pose proxy rather than privileged simulator velocities. |
| Physics-step samples and explicit timestamps/action alignment | Preserve events between policy commands and compare force peaks with the command that caused them. |
| Precontact samples plus contact-onward masks | Retain attempts that never contact the object and allow later selection of the contact-onward segment. |
| Exact contact locations, impulses, normals and separation as sim evidence | Support later analysis of where contact occurred; they remain outside the deployment feature set. |
| Inertia, separate finger/table/object materials, restitution, gravity and damping | Capture physical factors beyond mass and one nominal friction number, and distinguish applied settings from requested settings. |
| Initial robot/object/goal state, policy identity, timing, environment versions and outcome-rule version | Make episodes interpretable and reproducible within the recorded software and physics configuration. |

The commanded goal is also available as `input__goal_position_world_m`: it is
known to the task controller. Controller gains/limits and the full simulation
configuration are saved as JSON metadata in every episode.

Object poses in `input__` are **ideal simulated tracking measurements**, TCP and
finger poses are **ideal forward-kinematics measurements**, and net finger forces
are **ideal force-sensor proxies**. A real deployment needs the corresponding
tracker, encoders/calibration and force or tactile instrumentation. No camera
tracker, occlusion model, noise, sensor latency, tactile reconstruction, or motor
current sensor is implemented here. The point of the split is to expose that
provenance rather than treat every simulator getter as a real measurement.

Total finger force sums contacts with every body, as a finger-mounted sensor
would. Exact **finger–object** force and precise contact positions require oracle
object attribution and are stored under `sim__`. The raw policy observation,
simulator object velocities, oracle grasp flag and task-success signal are also
excluded from the feature whitelist. Object mass, COM, materials and shape are
labels, even when a deployed vision system might eventually estimate some of
them.

The absent explicit grip point is represented by a NaN placeholder and a false
availability flag. Use the available commanded TCP target and actual finger
poses; neither should be relabeled as a measured surface-contact point.

## Physical-property configuration

`normalized_properties()` accepts the following construction-time values.

| Key | Meaning / default |
|---|---|
| `shape` | `cube` (default), `box`, or `sphere` |
| `size_xyz_m` | Full geometric extents; default `[0.04, 0.04, 0.04]`. Cube/sphere dimensions must be equal; a sphere uses the diameter. |
| `mass_kg` | Positive mass, default `0.064`; weight in newtons is also recorded using actual gravity. |
| `com_offset_m` | COM in the geometric object frame, default `[0, 0, 0]`; must lie inside the geometry. |
| `static_friction`, `dynamic_friction` | Independently specified object coefficients, defaults `0.3`; require `0 <= dynamic <= static`. |
| `finger_friction`, `table_friction` | Separate static/dynamic coefficients for those surfaces, defaults `2.0` and `0.3`. They are not the same as a combined contact coefficient. |
| `restitution` | Object restitution in `[0,1]`, default `0`; finger and table restitution are fixed to zero and recorded. |
| `inertia_principal_kg_m2` | Optional three positive principal moments about the supplied COM, aligned with object axes. |
| `initial_pose_world` | Optional full `[xyz,wxyz]` initial pose; otherwise seeded native XY/yaw with orientation-aware bottom support height. Initial table penetration is rejected. |
| `goal_position_world` | Optional explicit target `[x,y,z]`; otherwise native seeded target. |

By default, inertia uses the uniform primitive's principal-moment formula and is
assigned about the specified COM. With a nonzero COM offset this is a synthetic
independent mass-property intervention, not a reconstructed density distribution.
The actual COM frame and moments, plus that modeling choice, are logged.

The sweep takes a Cartesian product of named axes and all seeds. Each axis item
is a property-override dictionary. Keep independent mass and friction axes when
investigating attribution; a deliberately coupled intervention can be a single
axis item containing both properties. For example:

```json
{
  "base_properties": {"shape": "cube", "size_xyz_m": [0.04, 0.04, 0.04]},
  "axes": {
    "mass": [{"mass_kg": 0.04}, {"mass_kg": 0.25}],
    "friction": [
      {"static_friction": 0.3, "dynamic_friction": 0.3},
      {"static_friction": 0.8, "dynamic_friction": 0.8}
    ]
  },
  "seeds": [0, 1, 2],
  "episode_steps": 50,
  "contact_threshold_n": 0.05
}
```

This example requests 12 episodes. For shape/size variation, put each valid
shape-and-dimension combination together in one axis item. Group train/test
splits by condition or held-out physical combinations as well as seed to avoid
evaluating only near-duplicate interventions.

The supplied `configs/failure_collection.json` instead contains **81 conditions
× 5 seeds = 405 episodes**, spanning three masses, three object-friction levels,
three geometries and three COM offsets. It uses 100 control steps (5 seconds)
and finger friction 0.6 as an explicit collection intervention. Those settings
differ from the published policy's 50-step task and native finger friction 2.0;
both are recorded. This is a collection sweep, not a claim of benchmark parity.

## Run

From the workspace root in Bash:

```bash
source scripts/activate_grip.sh
python -m failure_collection.collect --config configs/failure_collection.json --dry-run
python -m failure_collection.collect --config configs/failure_collection_pilot.json --output runs/failure_collection/new_pilot --check-determinism
```

The separate pilot configuration covers **36 conditions × 2 seeds = 72
episodes**: three masses, two friction levels, three geometries and two COM
offsets, with fixed finger friction 0.2. Inspect its manifest/schema before a
larger sweep. Resume an interrupted compatible run with:

```bash
python -m failure_collection.collect --config configs/failure_collection_pilot.json --output runs/failure_collection/new_pilot --resume
```

Choose another output directory for a changed configuration. `--max-episodes`
bounds the prefix of the plan, including already completed episodes; omit it to
run the configured sweep. A short prefix may cover only some axes. Use a small
explicit sweep configuration to test all desired shape/property families.
The collector runs the configured horizon so that a transient success followed
by loss remains visible. Per-step termination is evidence, not a silent reset
into the next episode.

## Array layout and safe loading

Every `.npz` is loadable with `allow_pickle=False`. JSON/string metadata and
numeric arrays avoid Python-object serialization. The full generated schema in
each run specifies field names, units, frames, provenance and time alignment.

| Prefix | Use |
|---|---|
| `input__` | Candidate sensor proxies and issued commands; consult availability and provenance. |
| `sim__` | Privileged physics/task evidence, exact object-contact attribution and policy state. |
| `label__` | Applied physical properties and descriptive episode outcomes. |
| `meta__` | Source/configuration identifiers, timestamps, validity and alignment metadata. The reset seed is `label__seed`. |

For `T` actions and `K = sim_freq/control_freq` physics steps per action:

- State trajectories have **T+1** rows, including the reset state.
- Commands, control-interval summaries and responses have **T** rows. Action
  `t` acts between state `t` and state `t+1`.
- Physics trajectories have **T×K** rows at the ends of the physics steps.
  `meta__physics_action_index` maps each row to its issued action.
- Contact points use flat numeric arrays and `sim__contact_point_offsets` of
  length **T×K+1**. Points for physics row `j` occupy
  `offsets[j]:offsets[j+1]`; no-contact rows have equal offsets.
- Reset force values are placeholders, with `meta__force_valid_state[0]`
  and `input__finger_force_valid[0]` false. PhysX retains old contact data after
  a teleport until a fresh step.
- `sim__from_contact_state_mask` and `sim__from_contact_physics_mask` retain
  everything from the first threshold-crossing contact onward. They are oracle
  alignment aids, not deployment input features. No-contact episodes retain
  their full trajectories and all-false masks.

Forces are expressed **on the finger**. Dividing each PhysX-step impulse by its
physics duration yields that substep's mean force in newtons; the interval mean
uses all substeps. A force queried only after `env.step()` describes the last
substep and would miss intermediate peaks. World relative position subtraction
alone is not a TCP-frame pose: the logger uses the full `TCP.inverse() * object`
transform, including orientation.

Use the whitelist loader for classifier inputs rather than selecting every
numeric field in an archive:

```python
from pathlib import Path
import numpy as np
from failure_collection.schema import load_inputs

episode = next(Path("runs/failure_collection/pilot_v1").rglob("*.npz"))
features = load_inputs(episode)
with np.load(episode, allow_pickle=False) as data:
    object_in_hand = data["input__object_pose_tcp_m_wxyz"]
    from_contact = data["sim__from_contact_state_mask"]
    contact_segment = object_in_hand[from_contact]
    print(data["label__failure_mode"].item())
```

Do not concatenate T, T+1 and T×K arrays without aligning them. Select the
features available on the intended robot and use the documented missing-value
flags. Oracle contact masks may select a training segment, but the deployed
system will need a measurable contact-onset rule of its own.
The loader also supports `include_pose=False` and `include_force=False` to
exclude sensor families. Use only history available at the chosen prediction
time; a full recorded episode includes future responses and outcomes.

## Outcome labels and determinism

`label__success_final` uses the task's final sampled success flag;
`label__success_any` separately captures an earlier success.
`label__held_goal_success_final` adds the final oracle grasp requirement. The
failure-mode rules distinguish `never_contacted`, `contact_without_grasp`,
`grasped_no_lift`, `lifted_then_lost_grasp`, and
`goal_not_reached_or_not_static`, plus `success`. Lift requires a sampled grasp
and at least 0.02 m geometric bottom clearance. Grasp uses the stock bilateral
contact-force/direction test, not a rigid attachment.

These are descriptive, sampled outcomes. They do not establish that high mass,
low friction or COM offset caused the failure; `failure_cause` remains
`unknown`. Grasp/lift outcomes use the control-rate state timeline, while the
contact detector examines physics-rate forces. An event shorter than a control
interval can therefore escape a grasp/lift outcome rule while still appearing
in the raw physics evidence.

Explicit reset seeds determine initialization with fixed properties and a
fixed environment/backend. The collector uses CPU simulation and ManiSkill's
enhanced reset determinism plus fresh scene reconstruction. A reset does not
perform a settling step. Reusing
an integer seed does not promise identical trajectories across CPU/GPU,
hardware, physics/solver settings or package versions. `--check-determinism`
provides a local replay check; its recorded result and manifest define the scope
of any reproducibility claim.

Within one physics sample, PhysX can enumerate identical contact points in a
different order after rebuilding the scene. Treat each offsets-delimited group
as an unordered set; point row numbers are not stable contact identities.

## Verified pilot

This section describes the original v1 Cartesian pilot. Its checks did not test
episode-order independence; use the fresh-scene matched experiment for the gap
atlas and controlled retry comparisons.

`runs/failure_collection/pilot_v1/` contains 72 complete episode archives,
7,200 control transitions and 36,000 physics samples. The observed final
outcomes were 40 successes, 19 grasped without lifting, 11 contacted without
grasping, and two lifted then lost the grasp. These counts describe this pilot,
not balanced class coverage or estimates of causal effects. No episode in this
pilot produced the `never_contacted` or `goal_not_reached_or_not_static` class.

The run includes `manifest.json`, `schema.json`, `summary.json`, a same-scene
replay result in `determinism.json`, and `verification.json` with archive hashes
and checks. The applied configuration and exact collection Python sources were
also copied into this pilot's `config.json` and `source_snapshot/`.

The 26 automated checks include all outcome rules, feature whitelist and archive
safety, sweep independence, and actual CPU simulation for cube/box/sphere:

```bash
source scripts/activate_grip.sh
RUN_MANISKILL_INTEGRATION=1 python -m unittest discover -s tests -p 'test_collection*.py' -v
```

The integration check verifies force signs against ManiSkill's own APIs,
relative-pose frames, contact impulses, action/response alignment, physical
readback, and fresh-scene seeded replay. Same-scene replay of the pilot's first
full episode was bitwise identical; fresh-scene contact sets are compared without
assuming their enumeration order.

The installed sources are authoritative for this workspace. Relevant upstream
references explain [contact-force queries](https://maniskill.readthedocs.io/en/latest/user_guide/tutorials/custom_tasks/advanced.html)
and [seeded initialization](https://maniskill.readthedocs.io/en/latest/user_guide/concepts/rng.html).

## Broad collection with the trained weight-aware policy

Use the new collector for raw data before later clustering:

```bash
bash /home/ubuntu/faliure/scripts/collect_varied.sh
```

The launcher pins the completed trained policy from October 9 (45 observations,
5 actions), runs deterministic inference, and never trains it. Its reported mass
is always **40 g** (converted to newtons for the policy's weight input). Actual
mass remains a separate simulator label. It retains the trained strength
controller and motor bounds. The vertical goal is directly above the object's
spawn, making this a pick-and-lift task. Success requires the object held within
2.5 cm of that goal and each arm joint speed at most 0.2 rad/s. Both final and
any-time success are saved; the horizon is 100 control steps (5 seconds).

`configs/failure_collection_varied.json` is the experiment definition. Its single
`seed_count` value defaults to 10: **60 unique conditions × 10 seeds = 600
episodes**. Each seed provides a random starting object position/orientation and
robot reset; the same seeds are reused across physical conditions. A fresh
physics scene is rebuilt for every episode. Positions and distances are both
retained. Size changes necessarily change the tabletop spawn height and inertia;
these derived changes are recorded as actual physical properties.

The baseline is a 100 g, 4 cm cube, object friction 0.4, finger friction 0.2,
table friction 0.3, centered COM, and 20 cm vertical lift. Factors include:

- Actual mass: 40, 100, 500 g; object friction: 0.1, 0.4, 1.0.
- Size: 3, 4, 5 cm; shape: cube or sphere; COM X offset: −5, 0, +5 mm.
- Goal lift: 10, 20, 30 cm; finger friction: 0.1, 0.2, 0.5; table friction: 0.1, 0.3, 0.8.

The design includes baseline and single-factor controls, ordered same-direction
and opposite-direction pairings (mass with object friction, size, and goal
height), the complete mass/friction grid, and 32 seeded mixed combinations.
Repeated combinations are run once and retain all design-family memberships.
“Together/opposite” means ordered co-variation, not equal numeric increments.
Object static and dynamic friction are varied together. The training environment's
automatic mass/friction coupling is disabled: only the declared factors vary.
The reward does not train or adapt the frozen policy during collection.

Output defaults to `runs/failure_collection/varied_fixed40g/` in **your original project folder**.
Each episode NPZ contains continuous poses, TCP–object and object–goal distances,
finger width, forces at control and physics rates, all five actions and actual
motor caps, property labels, reset state, seed, changed-property list, design
memberships, and success/failure/event labels. The policy-observation recording
contains the actual fixed-weight vector fed to the policy; it remains excluded
from deployment-feature loading because some other policy inputs are privileged.
The primary data remain NPZ; `episodes.json` is a per-episode index and
`summary.json` contains counts. `manifest.json`, source snapshots and `schema.json`
record experiment provenance. V3 adds five-action validation; old V1/V2 files
remain readable. Force and pose signals remain ideal simulator sensor proxies;
event labels describe sampled motion rather than proving a failure's cause.

Useful commands:

```bash
# Print planned counts, without running simulation or creating output:
bash /home/ubuntu/faliure/scripts/collect_varied.sh --plan-only
# A smaller collection (all 60 conditions, one starting seed each):
bash /home/ubuntu/faliure/scripts/collect_varied.sh --seed-count 1 --output /tmp/varied-small
# Resume an interrupted default collection, requiring identical code/config/policy:
bash /home/ubuntu/faliure/scripts/collect_varied.sh --resume
```

The launcher accepts `--config`, `--checkpoint`, `--output`, and `--seed-count`.
Its local Python, asset and checkpoint defaults match this machine; use
`COLLECTION_PYTHON`, `MS_ASSET_DIR`, and `COLLECTION_CHECKPOINT` if relocating.
No atlas, clustering, or recovery retries run in this collection.

Validation: 67 tests completed (65 passed; 2 optional simulator tests skipped); a separate
2-episode real-physics smoke check verified matched initial states, constant
reported weight, nonzero bilateral object contact forces, distance formulas,
and action-derived motor caps. Resume also revalidated the saved archives.
The full 600 episodes have not been run.

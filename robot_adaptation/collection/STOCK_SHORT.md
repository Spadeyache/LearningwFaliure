# Short collection with the official policy

Use the published ManiSkill PickCube policy, unchanged. It has **42 inputs and
four actions**, with no added weight estimate or grip-strength action. The task
keeps its original independent random XYZ goal, reward, geometric success rule,
and 50-step horizon. PickCube carries to a goal point; it is not a place-and-release task.

```bash
cd /home/ubuntu/faliure
bash scripts/collect_stock_short.sh
```

**Short budget:** 76 unique settings × 10 seeds = **760 attempts**. Five evenly
spaced numeric levels plus the nominal value where it falls between levels.
Single-variable changes only; no pair combinations. The 18 factors are listed in
[the config](../../configs/failure_collection_stock_short.json). Their nominal values
come from the installed native Panda PickCube task: 64 g cube, 40 mm width,
object/table friction 0.3, finger friction 2.0, and random goal-height range up to
0.3 m above the cube's initial center height.

## The baseline gate

The first ten attempts use the native, unmodified scene. The default screening
threshold is **90% final success**. If that fails, the script saves the baseline
and stops before collecting any shifted conditions. Ten starts are a screening
check, not a precise reliability estimate. The threshold is in the config; do
not lower it merely to claim a reliable policy.

**Current result:** 7/10 final successes on CPU simulation, also 7/10 any-time
successes. The gate rejected this baseline. `runs/failure_collection/stock_short/`
contains **only ten baseline episodes**, not the planned 760-episode sweep.

The published checkpoint metadata specifies GPU simulation. This collector uses
CPU simulation for exact per-contact logging, so it preserves task/controller
settings but does not claim to reproduce the original GPU runtime. The next
baseline investigation must separate checkpoint quality, runtime differences,
and installation/version differences before spending another batch on sweeps.

## Preview and adjust

```bash
bash scripts/collect_stock_short.sh --plan-only
bash scripts/collect_stock_short.sh --levels 11 --plan-only
bash scripts/collect_stock_short.sh --baseline-only --output runs/collection/stock_baseline_new
```

The finer 11-level option remains single-variable only. `--seed-count` changes
starting-state repeats. A new experiment requires a new `--output` folder.
`--resume` requires identical settings, code, runtime and checkpoint. It does not
bypass a failed baseline gate. The saved config and plan record the exact budget.

## What stays fixed and what changes

Object mass, friction, size, shape, COM X/Y/Z, restitution, damping, inertia,
starting X/Y/yaw, finger/table friction, sliding/static friction ratio, and native
maximum goal-height range can be swept one at a time. Numeric factors vary above
and below nominal where physically possible; zero damping/restitution cannot go
negative, and the sliding/static ratio cannot exceed one. Shape is categorical.
Mass and size derive inertia; independent inertia shifts are synthetic.

Starting offsets do not move the independently sampled native goal. The goal
height factor changes the maximum random height range, not a custom fixed lift.
The native scene is preserved exactly for the baseline. Non-geometry shifts
patch only the relevant native property; geometry shifts rebuild the primitive.

## Saved results

One `.npz` per attempt, using the existing recorder and sensor/ground-truth split:
poses, distances, finger opening, forces at every physics step, actions,
physical readbacks, reset state, seed and outcomes. Exact policy observations
remain under `sim__` and never become deployment features automatically.
The official policy itself includes simulator state such as `is_grasped`; this
experiment is not yet a real-robot sensor implementation.

- `baseline_check.json`: gate result.
- `episodes.json`, `summary.json`, `manifest.json`: completed attempts and provenance.
- `config.json`, `plan.md`, `source/`, `schema.json`: reproducible experiment definition.

The existing frozen weighted-policy dataset and training scripts remain available.
No policy training occurs here. Do not feed this four-action dataset into the
current five-action failure-discovery pilot without adapting its action features.

## Plot after a complete sweep

```bash
.venv/bin/python -m robot_adaptation.analysis.plots.plot --dataset runs/failure_collection/stock_short
```

The existing plotter generates 18 isolated views after a complete sweep. It refuses
to present a rejected baseline as if all planned conditions had been tested.

New collections default to a fresh `runs/collection/stock_<timestamp>/` folder.
The historical rejected baseline remains at the path described above.

For the new **short official-policy experiment**, see [STOCK_SHORT.md](STOCK_SHORT.md). It is separate from the weighted-policy collection described below.

# Current data collection

The collector runs a fixed trained pick-and-lift policy, keeps its reported mass
at **40 g**, and saves one NPZ per attempt. Actual physical properties vary.

## Next collection: dense singles and pairs

```bash
cd /home/ubuntu/faliure
bash scripts/collect_varied.sh
```

Defaults: **2,983 settings × 10 starting seeds = 29,830 episodes**, saved to a fresh
`runs/collection/varied_<timestamp>/` folder by default. The completed historical
dataset remains in `runs/failure_collection/dense_single_pair_fixed40g/`.

No condition deliberately changes more than **two declared factors**. All
single-factor comparisons are included. Every numeric pair is swept in both
same and opposite directions. Shape is categorical and crossed with every
numeric factor. These are pair-direction sweeps, not a full 2D factorial grid.

The 18 controllable factors are:

- Actual mass; object friction; sliding/static-friction ratio.
- Finger friction; table friction; uniform object size; cube/sphere shape.
- COM X, Y and Z offsets.
- Required lift height; restitution (bounciness).
- Linear and angular damping; independent inertia scale.
- Spawn X, Y and yaw offsets from the seeded starting state.

Numeric factors have 11 evenly spaced values over each configured range, plus
the nominal value if it is not already on that grid. For example, the mass sweep
uses 40, 86, **100 nominal**, 132, 178, 224, 270, 316, 362, 408, 454 and 500 g.
Pair sweeps use 11 synchronized range positions in each direction. Duplicate
settings are collected once, retaining every applicable design-family label.

Edit `configs/failure_collection_varied.json`:

- `levels_per_factor`: numeric resolution (default 11).
- `seed_count`: number of starting setups repeated per setting (default 10).
- Each factor's `min`, `nominal`, `max`, or categorical `values`.
- Set a factor's `enabled` to `false` to hold it nominal and reduce the workload.

Preview counts and save a readable plan without running episodes:

```bash
bash scripts/collect_varied.sh --plan-only --write-plan configs/failure_collection_plan.md
```

For a smaller new collection or a different output folder:

```bash
bash scripts/collect_varied.sh --seed-count 2 --output runs/collection/dense_two_seeds
```

Resume an interrupted run using its exact original command plus `--resume`.
Config, policy and code fingerprints must match. Every episode starts with a
fresh physics scene and uses the same seed set across conditions.

## What is recorded

Continuous object/gripper poses, relative motion, object–gripper and object–goal
distances, finger width, contact forces, all five actions, and motor caps.
Simulator labels record mass, friction, geometry, COM, inertia, damping, initial
pose, seed, outcome and heuristic failure events. Each new episode also records
`changed_factors`, the full `factor_values_json`, pair direction, and spawn offsets.

Success requires holding the object within 2.5 cm of its vertical goal with
arm joint speeds at most 0.2 rad/s at the end of the five-second attempt.
The policy receives 45 observations and produces five actions. Its local
inference architecture/controller are pinned to the saved October 9 checkpoint.

Factor counts refer to independent experiment controls: mass/size naturally
change derived inertia; object friction and its ratio determine static/sliding
coefficients; spawn offsets move the vertical goal's XY too. Inertia scaling is
an explicitly synthetic independent inertia intervention. The policy's weight
estimate and learned weights remain fixed.

## Existing data and plotting

The earlier 600 episodes in `runs/failure_collection/varied_fixed40g/` remain
unchanged (202 successes, 398 failures). Their saved config/source describe their
older coarse experiment; do not resume them with this new design.

`robot_adaptation/analysis/plots/plots.md` currently describes that 600-episode dataset. A new dataset
needs its own condition/plot list; it must not reuse the old condition IDs.
See `configs/failure_collection_plan.md` for the full new range/family inventory.

## Code

- `design.py`: ranges, dense conditions, all pair directions and two-factor guard.
- `varied.py`: collection CLI using the explicitly versioned frozen v1 policy.
- `../simulation/environment.py`: physical construction and property readbacks.
- `../simulation/collection_lift.py`: supplied-weight observation/task interface.
- `../policy/frozen_v1.py`: pinned inference architecture and checkpoint loader.
- `collect.py`, `recording.py`: resets, continuous logging and archive metadata.
- `outcomes.py`, `events.py`, `schema.py`: labels, validation and saving.

## Source provenance after the layout migration

New source snapshots preserve package-relative paths and include the shared
simulator, controller, and frozen policy implementation. Existing saved sources
and datasets stay at their historical locations. The migration changes code
fingerprints; resuming a pre-migration run requires its original saved code.

# Current data collection

This folder contains only the fixed-40-gram-estimate collector. It runs the
trained 45-input / 5-action policy without training it, varying actual physical
properties and recording one compressed NPZ per episode.

## Existing dataset

`/home/ubuntu/faliure/runs/failure_collection/varied_fixed40g/` contains 600 episodes:
60 physical conditions × 10 starting seeds, with 202 final successes and 398 failures.
The dataset and its original source snapshots are preserved unchanged. Source
snapshots document the version that produced those results; they are not active
collection entry points.

Each episode records continuous object/gripper poses, relative pose, object–gripper
and object–goal distances, finger width, forces, all five commanded actions,
actual motor caps, actual physical properties, initial state, seed, varied-property
labels, and success/failure. No residuals, clustering, or recovery retries are
produced. Motion-event labels such as miss and drop are heuristic descriptions.
Measurable signals are ideal simulator sensor proxies; simulator truth is kept
separate from deployment-model inputs.

The policy always receives a 40 g mass estimate, converted to newtons. Actual
mass, object/finger/table friction, size, shape, COM offset, and lift height vary.
The design includes single-variable controls, same-direction and opposite-direction
pairs, a mass/friction grid, and mixed conditions. Seeds are reused across
conditions and physics is rebuilt for every episode. Attempts last 5 seconds;
final success requires holding the object within 2.5 cm of the vertical goal
with each arm joint speed at most 0.2 rad/s.

## Run a new collection

The existing default output is complete. Choose a new output directory:

```bash
cd /home/ubuntu/faliure
bash scripts/collect_varied.sh --seed-count 50 --output runs/failure_collection/varied_3000
```

This collects 3,000 episodes. Change `--seed-count` or `seed_count` in
`configs/failure_collection_varied.json`; total episodes = 60 × seed count.
Use `--plan-only` to print counts without running physics. For a newly started
collection, repeat its exact command with `--resume` after an interruption.
Resume requires identical code, policy and configuration. The preserved 600-run
collection predates this code cleanup, so it must not be resumed with the changed
source fingerprint. Read/analyze those NPZs directly; they remain fully supported.

## Active files

- `varied.py`: experiment design, fixed-weight policy interface and collection CLI.
- `collect.py`: shared episode runner, reset/provenance recording and utilities.
- `environment.py`: physical object construction, properties and contact sampling hook.
- `recording.py`: continuous movement, forces, commands and distances.
- `outcomes.py` and `events.py`: outcome and sampled failure-event labels.
- `schema.py`: validation, atomic NPZ saving and deployment-input-only loading.
- `inference.py` and `grip_controller.py`: pinned inference-only policy interface and strength controller.
- `__init__.py`: package schema definitions.

The collector pins its inference architecture and strength controller locally so
changes to training code cannot silently change this experiment. It uses the saved
October 9 checkpoint. Training code and other policy-evaluation tools remain separate
and unchanged in `learning-withoutCLI/`.

## Checks

```bash
cd /home/ubuntu/faliure
.venv/bin/python -m unittest discover -s tests -p 'test_collection_*.py' -q
MS_ASSET_DIR=/home/ubuntu/faliure/.maniskill/assets MS_SKIP_ASSET_DOWNLOAD_PROMPT=1 \
VK_ICD_FILENAMES=/usr/share/vulkan/icd.d/lvp_icd.x86_64.json \
RUN_MANISKILL_INTEGRATION=1 .venv/bin/python -m unittest discover -s tests -p 'test_collection_simulation.py' -v
```

The opt-in integration check compares two fresh trajectories with the preserved
600-episode dataset, including commands, sensor signals, contact forces and outcomes.

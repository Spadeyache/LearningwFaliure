# Architecture and development

## Code layout

```text
robot_adaptation/
  simulation/                  environments, controllers, task variants
  policy/                      model, training, inspection, frozen v1 inference
  estimators/visual_mass/       image generation, model, training, prediction
  collection/                  physical sweeps, recorder, schemas, source provenance
  analysis/failure_discovery/   grouping and intervention-response reports
  analysis/plots/               plot plans and report generation
  runtime/                     initial image to estimator to policy rollout
experiments/crest/              CREST-specific search, repair and experiment driver
configs/                       experiment settings
runs/                          generated outputs and source snapshots
docs/                          project-level explanations and experiment index
```

A model's training and inference belong together. Shared simulation code is
independent of collection commands. Analysis consumes saved records. Experiment
drivers compose reusable components and own their experimental choices.

The image generator is local to the visual-mass baseline because its fixed-density
scene is part of that estimator experiment. General robot episode collection lives
in `collection/`.

## Dependencies and interfaces

- `policy/model.py` defines the current v2 learner. `policy/frozen_v1.py` defines
  the older inference interface and strict checkpoint loader for collection.
  Matching input/output counts alone does not make these architectures interchangeable.
- `simulation/training_lift.py` and `simulation/collection_lift.py` remain
  separate task variants. Training's mass/friction relationship differs from
  independent-physics collection; moving code does not merge those assumptions.
- `simulation/grip_controller.py` is the shared controller implementation.
- Estimator training and prediction receive RGB pixels. Actual simulator masses
  are supervised labels, not prediction inputs. The initial visual baseline
  needs size correlated with mass and does not establish arbitrary-density inference.
- Estimator outputs are kilograms. The current policy's supplied-weight input
  is in newtons. The runtime uses simulator gravity for that conversion, preserves the observation
  ordering and architecture version, and checks the supplied weight each step.
- Episode schemas and input/label separation are owned by `collection/`.
  Simulator-only labels do not automatically become deployment observations.

Use the existing `.venv`, `scripts/activate_grip.sh`, and root
`requirements-lock.txt`. Analysis and estimator code share that environment;
there are no separate, conflicting environments for individual experiments.

## Adding an experiment

1. State the question and comparison in [the experiment index](experiments.md).
2. Put reusable changes in the relevant component; keep experimental choices in
   a driver under `experiments/` or the component's existing command.
3. Save the configuration, seed, input dataset/checkpoint, and relevant source
   identity with a new run under `runs/<experiment>/<run>/`.
4. Record the result and its scope in the index, linking the generated artifacts.

Policy and estimator architectures are explicit in saved manifests/checkpoints.
Keep that identity meaningful when introducing a new model. Checkpoint shapes
and old source snapshots retain their original interpretation.

## Compatibility and historical artifacts

Old top-level Python entrypoints are small forwards to canonical modules.
Canonical commands are listed in the root README. Update active code only in
`robot_adaptation/` and `experiments/`.

Historical `runs/`, analysis results, plots, and code archives were not moved.
New policy outputs use `runs/policy/`; latest-checkpoint lookup also searches
historical `runs/learning/`. New collection, plotting, and discovery outputs use
fresh run directories by default.

New collection and CREST snapshots include the shared implementations, with
package-relative source paths. New PPO preparation keeps its standalone frozen
runtime source format. Pre-migration source fingerprints differ from the new
layout, so continuing an old collection requires its original saved code; the
migration does not rewrite old experiment identities.

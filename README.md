# Robot adaptation research

Policy learning, physical-property estimation, failure discovery, and adaptation
experiments share one codebase and one Python environment.

## Where to work

| Component | Active location | Responsibility |
| --- | --- | --- |
| Policy | [robot_adaptation/policy/](robot_adaptation/policy/README.md) | Model, PPO training, checkpoint loading, inspection, reference examples. |
| Estimators | [robot_adaptation/estimators/visual_mass/](robot_adaptation/estimators/visual_mass/README.md) | Initial-image mass prediction, image generation, supervised training, inference. |
| Simulation | [robot_adaptation/simulation/](robot_adaptation/simulation/README.md) | Shared physics, sensors, controllers, explicitly different task variants. |
| Collection | [robot_adaptation/collection/](robot_adaptation/collection/README.md) | Physical sweeps, recording, episode schemas and provenance. |
| Failure discovery | [robot_adaptation/analysis/failure_discovery/](robot_adaptation/analysis/failure_discovery/README.md) | Motion grouping and responses to matched physical interventions. |
| Plots | [robot_adaptation/analysis/plots/](robot_adaptation/analysis/plots/README.md) | Editable plot plans, individual plots and combined reports. |
| Runtime | [robot_adaptation/runtime/](robot_adaptation/runtime/README.md) | Initial RGB to estimated mass to policy actions in simulation. |
| CREST | [experiments/crest/](experiments/crest/README.md) | Research experiment using the shared simulator and collection design. |

Edit the active locations above. Old top-level code folders contain compatibility
entrypoints and pointers to the active guides. Historical reports, plots, source
archives, datasets and checkpoints remain at their existing paths.

[Experiment index](docs/experiments.md) · [Architecture and development](docs/development.md)

## Commands

Start from the repository root:

```bash
cd /home/ubuntu/faliure
source scripts/activate_grip.sh
```

| Action | Command |
| --- | --- |
| Train policy | `python -m robot_adaptation.policy.train` |
| Inspect saved policy | `python -m robot_adaptation.policy.inspect` |
| Generate images and train mass estimator | `python -m robot_adaptation.estimators.visual_mass` |
| Deploy estimator with policy in simulation | `python -m robot_adaptation.runtime --record-video` |
| Preview dense collection | `bash scripts/collect_varied.sh --plan-only` |
| Collect dense physical sweeps | `bash scripts/collect_varied.sh` |
| Preview official-policy collection | `bash scripts/collect_stock_short.sh --plan-only` |
| Compare saved failure responses | `python -m robot_adaptation.analysis.failure_discovery.response_groups` |
| Generate planned plots | `python -m robot_adaptation.analysis.plots.plot` |
| Inspect the plot list | `python -m robot_adaptation.analysis.plots.plot --check` |
| Preview CREST experiment | `python -m experiments.crest --plan-only` |

Each command supports its existing options; consult its guide or `--help`.
Training commands learn weights. Collection and inspection use saved policies.
New outputs go under `runs/`; an explicit output path can select a fresh location.

## Current research state

- **Policy:** the active learner uses the independent movement/strength v2
  architecture. Collection deliberately loads the frozen v1 interface used by
  the historical datasets. Their manifest checks keep these versions explicit.
- **Collected episodes:** [29,830 attempts](runs/failure_collection/dense_single_pair_fixed40g/)
  across 2,983 physical settings and ten starts, with the policy receiving a
  fixed 40 g estimate. The [earlier 600 episodes](runs/failure_collection/varied_fixed40g/)
  are also kept. Records contain motion, forces, actions, actual physics and outcomes.
- **Failure discovery:** [90 matched saved attempts](failure_discovery/results/response_mass_friction/index.html)
  produced seven observed response profiles. These profiles describe responses
  to tested mass/friction changes; deployment recognition remains future work.
- **Visual estimator:** [completed CPU baseline](runs/visual_mass/initial_rgb_mass/model/metrics.json)
  using 384 RGB images, with **2.76 g test MAE** across 12 held-out sizes
  (48 images), versus 106.37 g for a constant training-mean prediction. Cubes have
  constant density and fixed friction, so size predicts mass by construction.
  A combined simulation runner is available; policy improvement has not yet been evaluated.
- **Official-policy baseline:** ten CPU attempts achieved 7/10 successes; its
  quality gate stopped the planned sweep. See the [collection guide](robot_adaptation/collection/STOCK_SHORT.md).

## Settings, dependencies, and saved work

- `configs/`: collection and experiment settings. Policy settings currently live
  in `robot_adaptation/policy/train.py` and are recorded with each run.
- `requirements-lock.txt`: shared pinned environment, including analysis dependencies.
- `scripts/`: environment activation and convenience launchers.
- `runs/`: new datasets, checkpoints, metrics, figures and source snapshots.
- `docs/`: project architecture and experiment summaries.

Legacy commands such as `python learning-withoutCLI/train_ppo.py`,
`python -m visual_mass_estimator`, `python -m failure_collection.varied`,
`python failure_discovery/response_groups.py`, `python data_check/plot.py`, and
`python -m crest` forward to the active implementations. The older `grip_support/`
setup tools remain separate; their unfinished training interface is not the
active learner.

Existing `failure_discovery/results/`, `data_check/plots/`,
`data_check/plots_archive/`, and `data_check/code_archive/` are historical artifacts.
The [historical plot report](data_check/plots/index.html) remains available.

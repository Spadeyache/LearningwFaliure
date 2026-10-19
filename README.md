# Robot picking: training, data, and plots

## Main folders

| Folder | What it does |
|---|---|
| [learning-withoutCLI/](learning-withoutCLI/README.md) | Trains the policy and runs policy inspections. |
| [failure_collection/](failure_collection/README.md) | Runs the trained policy under varied physical settings and saves one `.npz` per attempt. |
| [failure_discovery/](failure_discovery/README.md) | Reuses saved episodes to group failures by responses to controlled physical changes. |
| [data_check/](data_check/README.md) | Reads the collected data and generates individual plots plus a combined view. |
| [runs/](runs/) | Saved checkpoints, episode data, and inspection recordings. Plot outputs are in `data_check/plots/`. |
| [configs/](configs/) | Collection settings and older support-tool settings. |
| [scripts/](scripts/) | Environment activation, the collection launcher, and simulator checks. |
| [grip_support/](grip_support/) | Older optional setup/check tools; its training interface is unfinished. Use `learning-withoutCLI/` for training. |

**Current dataset:** [29,830 episodes](runs/failure_collection/dense_single_pair_fixed40g/) = 2,983 settings × 10 starts. The [original 600 episodes](runs/failure_collection/varied_fixed40g/) are also kept. The robot always receives a **40 g estimate** while actual properties vary. Each episode includes movement, forces, actions, physical settings, and success/failure.

## Commands

Start in Bash:

```bash
cd /home/ubuntu/faliure
source scripts/activate_grip.sh
```

| What you want | Command |
|---|---|
| Start policy training | `python learning-withoutCLI/train_ppo.py` |
| Inspect a trained policy | `python learning-withoutCLI/inspect_policy.py` |
| Preview short official-policy collection (760 attempts; gated) | `bash scripts/collect_stock_short.sh --plan-only` |
| Run short official-policy collection | `bash scripts/collect_stock_short.sh` |
| Collect dense singles/pairs (29,830 attempts by default) | `bash scripts/collect_varied.sh` |
| Preview the next collection without running it | `bash scripts/collect_varied.sh --plan-only` |
| Compare failure responses (90 saved attempts; choose new output) | `python failure_discovery/response_groups.py --output failure_discovery/results/NEW_RESPONSE_TEST` |
| Generate every listed plot | `python data_check/plot.py` |
| Generate only the friction plot | `python data_check/plot.py --only object_friction_only` |
| Check the plot list without rendering | `python data_check/plot.py --check` |

Training starts learning; inspection and collection run saved policies without learning. Choose a new output folder for a new collection.

## Settings and results

- **Short official-policy collection:** [guide](failure_collection/STOCK_SHORT.md). Current baseline: 7/10 successes; the quality gate stopped the sweep.
- **Collection settings:** [configs/failure_collection_varied.json](configs/failure_collection_varied.json): 18 factors, finer numeric levels, at most two changed factors. [Full new plan](configs/failure_collection_plan.md).
- **Failure discovery:** [guide](failure_discovery/README.md) and [current response experiment](failure_discovery/results/response_mass_friction/index.html). 90 saved attempts; seven observed response profiles. No new robot trials.
- **Plot list:** [data_check/plots_dense.md](data_check/plots_dense.md). One Markdown row = one plot; 307 isolated comparisons cover all 2,983 settings.
- **[Open plot results](data_check/plots/index.html).** Each run gets its own folder. Individual plots appear first; the combined view is built automatically at the end.
- **Training settings:** `SETTINGS` inside the training script; see the [training guide](learning-withoutCLI/README.md).

Earlier analysis code and plots are kept in `data_check/code_archive/` and `data_check/plots_archive/`.

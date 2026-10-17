# Robot picking: training, data, and plots

## Main folders

| Folder | What it does |
|---|---|
| [learning-withoutCLI/](learning-withoutCLI/README.md) | Trains the policy and runs policy inspections. |
| [failure_collection/](failure_collection/README.md) | Runs the trained policy under varied physical settings and saves one `.npz` per attempt. |
| [data_check/](data_check/README.md) | Reads the collected data and generates individual plots plus a combined view. |
| [runs/](runs/) | Saved checkpoints, episode data, and inspection recordings. Plot outputs are in `data_check/plots/`. |
| [configs/](configs/) | Collection settings and older support-tool settings. |
| [scripts/](scripts/) | Environment activation, the collection launcher, and simulator checks. |
| [grip_support/](grip_support/) | Older optional setup/check tools; its training interface is unfinished. Use `learning-withoutCLI/` for training. |

**Current dataset:** [600 episodes](runs/failure_collection/varied_fixed40g/) = 60 settings × 10 starts. The robot always receives a **40 g estimate** while actual properties vary. Each episode includes movement, forces, actions, physical settings, and success/failure.

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
| Collect 3,000 attempts into a new folder | `bash scripts/collect_varied.sh --seed-count 50 --output runs/failure_collection/varied_3000` |
| Generate every listed plot | `python data_check/plot.py` |
| Generate only the friction plot | `python data_check/plot.py --only object_friction_only` |
| Check the plot list without rendering | `python data_check/plot.py --check` |

Training starts learning; inspection and collection run saved policies without learning. Choose a new output folder for a new collection.

## Settings and results

- **Collection settings:** [configs/failure_collection_varied.json](configs/failure_collection_varied.json).
- **Plot list:** [data_check/plots.md](data_check/plots.md). One Markdown row = one plot; currently 46 rows covering all 60 settings.
- **[Open plot results](data_check/plots/index.html).** Each run gets its own folder. Individual plots appear first; the combined view is built automatically at the end.
- **Training settings:** `SETTINGS` inside the training script; see the [training guide](learning-withoutCLI/README.md).

Earlier analysis code and plots are kept in `data_check/code_archive/` and `data_check/plots_archive/`.

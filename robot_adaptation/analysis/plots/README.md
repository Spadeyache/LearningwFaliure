# Episode plots

Read the saved collection and plot the actual parameter values, with **green
circles for success** and **red crosses for failure**. No new robot trials.

```bash
cd /home/ubuntu/faliure
.venv/bin/python -m robot_adaptation.analysis.plots.plot
```

The default is the completed **29,830-episode** dense collection. The editable
[plots_dense.md](plots_dense.md) defines **307 comparison plots** covering all
2,983 settings:

- 18 single-variable views.
- 136 same-direction and 136 opposite-direction numeric-pair views.
- 17 shape × numeric-variable views.

Every comparison includes the same nominal reference attempts; these are shared
references, not additional experiments. Only factors listed in the row may vary.
Derived quantities can change with a factor (for example inertia with mass/size,
or dynamic friction with static friction and its ratio).

Each execution creates a folder under `runs/plots/`. Plots appear as they
finish, followed by **one combined scrolling view**, one comparison underneath
another. Large combined views use several full-resolution PNG sheets so the
browser can display them without shrinking the text.

**[Open historical plot runs](../../../data_check/plots/index.html)** or **[open the complete dense run](../../../data_check/plots/dense_single_pair_all/index.html)**.

## Axis and selection

Dense plots show only the selected attempts in collection order. X-axis ticks
retain their original episode numbers; unrelated episodes are omitted so a
100-attempt comparison is readable within a 29,830-attempt dataset. The Y axis
shows the actual setting and units. Use `--x-axis original` for a common full
1–29,830 axis with unrelated attempts left blank.

Starting-position/yaw factors are commanded offsets from each seed's reset pose;
the complete initial pose is retained in the source data. Shape is categorical.
Same/opposite directions describe sweep ordering, not an exact proportional law.

## Run just one plot

```bash
.venv/bin/python -m robot_adaptation.analysis.plots.plot --only object_friction_only
.venv/bin/python -m robot_adaptation.analysis.plots.plot --only mass_object_friction_together
```

Use `--output runs/plots/YOUR_RUN_FOLDER` to place results in a chosen run.
With `--only`, unaffected unchanged plot rows in that run are retained. To combine
existing PNGs again without recomputing the plots:

```bash
.venv/bin/python -m robot_adaptation.analysis.plots.combine_plots data_check/plots/dense_single_pair_all
```

The combined view defaults to one column; `--columns 3` is also supported.

## Edit the Markdown plan

Each row under **Plots** defines one PNG: plot name, variable panels, condition
IDs, whether to include nominal references, and title. Names identify saved
conditions, not arbitrary combinations. The plotter rejects hidden extra changes
and a plan fingerprint belonging to a different dataset.

```bash
.venv/bin/python -m robot_adaptation.analysis.plots.plot --check
```

`--make-plan` regenerates the dense Markdown from the saved experiment families;
it overwrites edits to that plan. Normal runs preserve your Markdown edits.

## Original 600-episode plots

The original plan and outputs remain available. To regenerate them:

```bash
.venv/bin/python -m robot_adaptation.analysis.plots.plot --dataset runs/failure_collection/varied_fixed40g --plan robot_adaptation/analysis/plots/plots.md
```

That plan contains 46 rows covering the old 60 settings. Earlier analyses remain
in `data_check/code_archive/` and `data_check/plots_archive/`.

## Files saved per run

- Individual PNGs and `index.html`, updated as each plot finishes.
- `combined.html`, combined PNG(s), and their tile layout.
- `selections.json`: exact episodes included in each comparison.
- `episodes.csv`: episode order, outcomes and all plotted factor values.
- `manifest.json`: data/code fingerprints and verification that raw files stayed unchanged.

Uses the existing NumPy, Matplotlib and Pillow dependencies. This workflow does
not run failure discovery, classifiers, or policy training.

## Code and historical results

The canonical modules are under `robot_adaptation.analysis.plots`; editable Markdown
plans live alongside them. Existing `data_check/*.py` entry points still work.
The historical `data_check/plots/`, `plots_archive/` and `code_archive/` folders
remain in place. New runs and their gallery are written under `runs/plots/`.

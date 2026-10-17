# Simple, modular episode plots

Edit **[plots.md](plots.md)**, then run one command:

```bash
cd /home/ubuntu/faliure
.venv/bin/python data_check/plot.py
```

The default is **every row** in the Markdown: currently 46 plots covering all
60 physical settings and 600 attempts.

Each run creates a new folder inside `data_check/plots/`. Individual plots are
saved immediately and appear in that folder's `index.html` as they finish.
The page refreshes while rendering. At the end, the script combines the saved
plots into one image and a zoomable viewer.

**[Open the run list](plots/index.html)** to choose an individual or combined view.

## The two code modules

- **[plot.py](plot.py)** reads the Markdown, validates the isolation rules, draws
  individual plots, and calls the combiner at the end.
- **[combine_plots.py](combine_plots.py)** assembles saved PNGs into `combined.png`
  and `combined.html`. It never re-runs the individual plot calculations.

The combined viewer has a zoom slider, Fit width, Full resolution, and scrolling.
Click any tile to open its original full-size plot. The image contains all plots
in the same order as their Markdown rows.

## Generate just one plot

```bash
.venv/bin/python data_check/plot.py --only object_friction_only
```

This makes a new run with just that row and its combined view. To rebuild one
plot inside an existing run while preserving its other unchanged plots:

```bash
.venv/bin/python data_check/plot.py --only object_friction_only --output data_check/plots/YOUR_RUN_FOLDER
```

The combined view is rebuilt from the available individual PNGs afterward.
You can list several names after `--only`.

To recombine an existing run without recalculating any individual plots:

```bash
.venv/bin/python data_check/combine_plots.py data_check/plots/YOUR_RUN_FOLDER
```

The combiner defaults to one vertical column and 1500 pixels per plot. The nominal
reference stays inside each comparison; there is no standalone nominal row. Optional
`--columns` and `--tile-width` let you change the combined layout.

## Edit the plot list

Each row under `## Plots` in **[plots.md](plots.md)** defines one PNG. For example:

```markdown
| custom_friction | object_friction | C04,C05 | yes | Object friction only |
```

- `Variables` lists the panels to draw.
- `Conditions` selects exact collected settings from the Markdown catalog.
- `Reference=yes` adds the nominal C01 attempts.
- The script rejects hidden changes to variables not listed in the row.

To validate edits without drawing anything:

```bash
.venv/bin/python data_check/plot.py --check
```

The default rows include eight single-variable plots,
six same/opposite-direction pair plots, and 32 separate mixed settings. Nominal
references are reused in comparisons; they are not additional collected trials.

## What is shown and saved

The X axis retains original episode numbers 1–600. Each Y axis shows the listed
parameter value. Successes are green circles; failures are red crosses. Unrelated
episodes are blank. Each generated run contains:

- Individual PNGs and an immediately usable `index.html`.
- One `combined.png` and zoomable `combined.html`.
- `selections.json`: exact episodes used for each Markdown row.
- `episodes.csv`: the original episode-number lookup.
- `manifest.json`: source/code hashes and the combined image layout dimensions.

Only NumPy, Matplotlib and Pillow from the existing project environment are
needed. The original 600 episode files remain unchanged. No new robot trials,
policy training, classifiers or PCA calculations are run by these scripts.

Earlier analysis is preserved in `plots_archive/` and `code_archive/`.
`plots/run_initial_markdown/` preserves the first flat Markdown-driven output.

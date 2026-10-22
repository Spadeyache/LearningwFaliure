# Failure discovery

## Current method: group by response to controlled changes

[Open the completed mass/friction response experiment](../../../failure_discovery/results/response_mass_friction/index.html).
The algorithm compares matched trials with the same starting seed and reset state.
It groups failed cases by which tested physical changes turn failure into success;
no motion-based failure names are required.

The complete 3 × 3 grid uses **40, 100, 500 g** and object friction
**0.1, 0.4, 1.0**, across ten starts: **90 saved attempts, 51 failures**.
It finds seven exact response profiles. Of the failures, 25 have a successful
mass-only change, 10 a friction-only change, 11 either, and five only a joint
change among these tested levels. All other deliberate factors stay nominal.
Mass changes also change derived inertia; object friction changes both static
and sliding friction.

```bash
cd /home/ubuntu/faliure
.venv/bin/python -m robot_adaptation.analysis.failure_discovery.response_groups --output runs/failure_discovery/NEW_RESPONSE_TEST
.venv/bin/python -m unittest discover -s failure_discovery -p test_response_groups.py
```

Choose a fresh output folder. The script checks complete matching, recorded
outcomes, and unchanged source files. It saves a viewing page, two plots, JSON
scores, seven group definitions, all per-failure response vectors, and the
recorded evidence for every comparison. Missing matches cause an error.

These are **observed response groups**, not proven distinct physical mechanisms.
Several failures share the same seed and comparison targets, so their counts
are not independent repetitions. This experiment uses the frozen custom policy
with its supplied weight estimate fixed at 40 g. It does not learn grip-force
adjustments or change estimator inputs. No new simulator runs are needed.

## Earlier exploratory method: motion clustering

Reuse saved episodes to find recurring failure patterns, without defining names
such as “slip” or “drop” first. No new robot trials or policy training.

```bash
cd /home/ubuntu/faliure
.venv/bin/python -m robot_adaptation.analysis.failure_discovery.analyze
```

The default pilot samples **120 episodes** from the completed 600-episode dataset,
balanced across starting seeds. Each execution creates a fresh folder under
`runs/failure_discovery/`. [Open the pilot results](../../../failure_discovery/results/index.html).

## Earlier motion identification test

[Open the mass/friction test](../../../failure_discovery/results/mass_friction_discovery/index.html).
It uses **230 attempts (154 failures)** from the completed 29,830-episode dataset:
only nominal, isolated mass changes, and isolated object-friction changes.
Two broad candidate behavior groups recur across seed splits; they are not yet
verified, mutually exclusive physical failure mechanisms.

```bash
cd /home/ubuntu/faliure
.venv/bin/python -m robot_adaptation.analysis.failure_discovery.analyze --dataset runs/failure_collection/dense_single_pair_fixed40g --single-factors mass object_friction --max-episodes 1000 --output runs/failure_discovery/NEW_TEST
.venv/bin/python -m robot_adaptation.analysis.failure_discovery.check_groups runs/failure_discovery/NEW_TEST
```

`check_groups.py` validates all five pairs of held-out seeds, saves a frozen
pickle-free `candidate_model.npz`, summarizes actual object motion, and reveals
physical settings afterward in `controlled_group_rates.png` and CSV. The
frequency denominator is all ten starts, including successes. ARI is grouping
agreement, **not classification accuracy**. Reference assignments overlap with
some fold-training data, so the check measures consistency rather than semantic
correctness. Groups may contain more than one failure mechanism.

Optional recorded-pose GIFs use the simulator renderer without new policy or
physics runs. Source the project environment first:

```bash
source scripts/activate_grip.sh
python -m robot_adaptation.analysis.failure_discovery.view_examples runs/failure_discovery/NEW_TEST
python -m robot_adaptation.analysis.failure_discovery.check_groups runs/failure_discovery/NEW_TEST
```

The second check command adds completed GIFs to the viewing page. The current
results already include one held-out example per group. These are reconstructions
of saved poses, not newly simulated attempts. `--per-group 2` gives more examples.

## What it does

1. Measures target error, relative object motion during bilateral finger-force
   signals, and steady-hold duration. Original success flags remain unchanged.
2. Groups original failures from movement, rotation, finger width, forces and
   actions. Mass, friction, physical settings, policy observations and existing
   failure names are excluded. Two entire starting seeds are held out.
3. Reveals physical settings afterward, saving counts per condition and group.
   These are associations, not proof of causes.

**Next requested stage:** identify which robot-measurable or robot-estimated
signals predict failure and distinguish the discovered groups. A fully commented, disabled implementation sketch is included under
`STEP 3` in `analyze.py`; it does not run. It compares per-group recognition
with and without each measurement family. This feature-selection stage is not
enabled or validated yet. It must use held-out starting states,
compare predictions with and without each signal, and evaluate information
available *before* the failure if the goal is early warning. A useful predictive
measurement is not necessarily a physical cause.

## Stable-success proxy

The object must remain within **25 mm** of the goal through an interval ending
at the final sample. During that interval both fingers' net-force magnitudes
must exceed **0.05 N**, relative translation must stay within **3 mm** of its
interval-start pose, and relative rotation within **5 degrees**. A final interval
of at least **0.5 seconds** counts as the new stability proxy. The longest steady
interval anywhere in the episode is also reported.

These are provisional thresholds, not thresholds validated against real grasp
quality. Net finger forces can include other contacts; they do not prove a grasp.
Poses are ideal simulator sensor proxies, sampled at 20 Hz. Real deployment
needs pose estimation and appropriate sensors. Relative path length is left
unknown when no sustained bilateral-force interval exists.

## Outputs in each run

- `index.html`: plots and explanation.
- `episode_metrics.csv`: continuous measures, original success, new proxy, group.
- `groups.png` and `group_traces.png`: unnamed groups and their measured behavior.
- `scores.json`: held-out separation, grouping agreement, assumptions and thresholds.
- `representative_episodes.csv`: three example recordings per group to inspect.
- `physical_settings_revealed_after_grouping.csv` and `condition_group_counts.csv`.
- `manifest.json`: exact input files, their hashes, and analysis-code hash.

Scaling/PCA/group fitting and group-count selection use training seeds only.
Candidate group counts 2–6 are compared using training silhouette. Eight fits
using subsets of training seeds are compared on the same held-out starting
states using adjusted Rand index (ARI). One means matching groups; zero means
chance-level agreement. A high silhouette can still isolate a few outliers;
collapsed held-out groups and group sizes are reported explicitly. The model
forces at least two groups: this alone cannot establish distinct failure types.

Different starts are held out, not different physical conditions. Reset-aligned,
normalized-duration traces may group geometry, timing, or task phases rather
than physical mechanisms. Videos and controlled repeats are still needed to
interpret candidates. No automatic “slip/drop” names are assigned.

## Other saved datasets or a larger sample

```bash
.venv/bin/python -m robot_adaptation.analysis.failure_discovery.analyze --dataset runs/failure_collection/dense_single_pair_fixed40g --max-episodes 600
```

Use after enough conditions and at least five seeds have finished. Partial
collections are accepted, but their order can bias the available conditions.
The script reads a snapshot of completed NPZ files; it does not watch for new ones.
Use `--max-episodes 600` on the default dataset to analyze all original episodes.

Analysis uses the shared project environment and root dependency lock:

```bash
uv pip install --python .venv/bin/python --no-deps -r requirements-lock.txt
.venv/bin/python -m unittest discover -s failure_discovery -p test_analyze.py
```

## Code and historical results

The canonical modules are under `robot_adaptation.analysis.failure_discovery`.
Existing script commands under `failure_discovery/` remain compatibility entry points.
Saved historical reports and GIFs stay in `failure_discovery/results/`; new analyses
create fresh folders under `runs/failure_discovery/`.

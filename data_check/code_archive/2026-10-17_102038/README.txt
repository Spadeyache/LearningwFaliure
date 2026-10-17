PICK-AND-LIFT DATA CHECK
======================

Start here: plots/index.html (browsable figure gallery).
The input is ../runs/failure_collection/varied_fixed40g: 600 episodes,
60 physical conditions, 10 seeds, 202 final successes and 398 failures.
No new robot trials are run. No original NPZ files are edited.

REGENERATE EVERYTHING
  cd /home/ubuntu/faliure
  bash data_check/run.sh

Optional output directory / input dataset:
  bash data_check/run.sh --output /tmp/pick-plots
  bash data_check/run.sh --dataset /path/to/compatible/dataset
The current design expects the retained 60-condition, 5-second experiment.

TEST
  cd /home/ubuntu/faliure/data_check
  ../.venv/bin/python -m unittest test_analysis -v

FILES
  data.py          Input validation, channel extraction and matched nominal gaps.
  models.py        Seed-grouped evaluation, per-fold channel ranking, PCA and
                   multi-label single-to-combination transfer diagnostics.
  plots.py         All A-H plots, including each condition's detailed traces.
  run.py / run.sh  Reproducible analysis entry point; gallery and score export.
  test_analysis.py Focused geometry, alignment, fold-leakage and dataset checks.
  requirements.txt Analysis extras, installed separately in .deps/.
  plots/           29 overview PNGs plus 60 per-condition PNGs and HTML gallery.
  plots/scores.json Numeric scores, fold memberships and limitations.
  plots/conditions.csv Plot IDs C01-C60 mapped to the actual physical settings.
  plots/episodes.csv Each file, seed, outcome, active variables and lift timing.
  plots/predictions.csv Selected-channel held-out predictions for isolated shifts.
  plots/analysis_manifest.json Source hashes, code hashes and library versions.
  derived/gaps.npz  Derived gaps for all 600 episodes, channel names, units,
                   matched nominal IDs, reset/lift alignment and validity masks.

EXPERIMENT LABELS ARE NOT PROVEN FAILURE CAUSES
The analysis predicts which factor was deliberately changed. It does not identify
which factor actually caused an individual failure. All isolated-shift episodes,
including successes, enter the primary classification. C3 is explicitly failure-
only; scores.json also records a failure-only mass/friction diagnostic.
This is a CREST-inspired exploratory measurement-selection workflow, not a claim
that a particular published causal algorithm was implemented or validated.

GAPS AND TIME
For each episode, subtract the nominal run with the SAME seed at the SAME elapsed
time. Position/width/force gaps use subtraction. Orientations use the rotation
vector of R_shift * inverse(R_nominal); quaternion signs do not create fake gaps.
There are 20 measurement/command channels. Compression is the all-contact finger
sensor proxy; object-attributed oracle forces are not classifier features.

For lift-aligned figures, BOTH members of the pair use the nominal run's first
held lift (bottom clearance >= 2 cm) as their common zero. A shifted run that never
lifts can still be plotted. The nominal run for seed 2000 never lifts, so this seed
has no lift-aligned curve. It remains in reset-aligned coverage/classification.
No missing onset or out-of-range sample is silently replaced or extrapolated.
Mean bands are +/- ONE STANDARD DEVIATION, not confidence intervals. Valid counts
can decrease at window edges. All sources currently have equal-length timelines.

The nominal condition is not a guaranteed successful demonstration (4/10 final
successes). Its actual mass is 100 g; the policy's reported mass stays 40 g.
Geometry changes support height and goal position; goal-height interventions
change task demand. The corresponding gaps include these known starting/task
changes. Read nominal_reset_match in the derived archive before treating a gap
as a matched-state physics-only comparison.

MAGNITUDES
The requested 0.5x / 2x / 4x mass/friction series is NOT present. Actual mass levels
are 0.4x and 5x nominal; object friction is 0.25x and 2.5x. COM uses signed mm,
shape is categorical, and all other exact values are in conditions.csv.
The atlas markers distinguish lower/negative and higher/positive shifts; the
condition table provides the exact magnitude for each variable.

MODELS AND LEAKAGE
Five outer folds group all same-seed episodes together. Scalers fit only on each
training fold. Channel ranking uses only that fold's training labels. Logistic
regression uses fixed C=1 and balanced class weights; the main selected-channel
model uses five channels. No held-out label selects a channel. Accuracy versus
channel count is exploratory: picking a winner from that curve needs another
independent test. Scores and all fold memberships are saved.

The PCA scaler and basis fit only isolated shifts; mixed episodes are projected
without refitting. PCA is descriptive and not cross-validated. Its axes need not
separate intervention labels even if a classifier can discriminate them.

Single-to-combination testing uses eight binary membership classifiers, trained
on isolated shifts + nominal, with a fixed 0.5 threshold. Combinations are evaluated
on unseen seeds and scored as multiple labels (exact match, micro/macro F1), not
forced into one supposedly correct cause. Geometry-transfer strata can overlap
and remain confounded by other mixed factors; class counts are shown explicitly.

The gaps use a second, matched nominal trajectory, and lift timing is privileged
simulator information. These scores are OFFLINE DIAGNOSTICS, not evidence that a
real robot can achieve the same result from a single episode or noisy sensors.

GRIPPER AND DIVERGENCE
There is no commanded contact-force target or logged actuator-effort trace.
The command specifies a per-finger motor cap. G1 therefore plots cap versus
measured compression and requested command-ceiling use; it cannot establish true
motor saturation. Collision contact forces can exceed drive limits.

G2 separates detected slip/drop onset from cases with unknown physical onset.
For unknown onset, the horizon/detection sample is shown separately and labeled.
Relative Z velocity is measured in a moving gripper frame, not an inertial frame.

Divergence is a descriptive threshold crossing sustained for 3 samples with at
least 3 contributing runs. Thresholds: position/distance 5 mm, rotation 0.1 rad,
width 2 mm, force/cap 1 N, relative speed 0.02 m/s, TCP height 5 mm. These are
analysis choices, not calibrated alarms or significance tests. Pooled low/high
shifts can cancel; inspect individual-condition pages as well.

DEPENDENCIES
Uses the project's existing NumPy/SciPy/Matplotlib/Pillow. Extra libraries are
isolated from the training environment. To reinstall those extras:
  /home/ubuntu/.local/bin/uv pip install --python ../.venv/bin/python \
      --target .deps --no-deps -r requirements.txt

EPISODE-NUMBER VIEWS
  plots/I01_parameters_vs_episode.png: all 8 varied inputs over episodes 1-600.
  plots/I02_pairs/: all 28 pairs, vertical axis lists the two values jointly.
  plots/I03_complete_combinations_vs_episode.png: all 60 complete settings.
  plots/episode_parameter_values.csv: actual collection-order numbering lookup.
Green circles = success; red crosses = failure. Pair views show joint settings,
not multiplication of unlike units. These include mixed conditions; comparisons
that isolate one variable remain in B1/B2. Full regeneration includes these views.
To regenerate only these episode views, without fitting statistical models:
  cd /home/ubuntu/faliure
  MPLCONFIGDIR=/tmp/failure-data-check-mpl .venv/bin/python data_check/episode_parameters.py

ISOLATED SITUATIONS (START HERE FOR PARAMETER EFFECTS)
  plots/J01_single_variable_overview.png: one filtered row per variable.
  plots/J01_single/: eight individual single-variable plots.
  plots/J02_pairs/: mass+friction, mass+size, mass+lift height; each has
      same-direction, opposite-direction, and all-tested-with-others-fixed views.
  plots/J03_combinations/: one dedicated page per exact set of changed factors.
  plots/isolated_selections.json: the precise original episode numbers used.
These retain global episode positions 1-600 and the original green/red style.
Excluded episodes are blank. The nominal ten-reference block is included in each
comparison; every other displayed point satisfies its specific isolation filter.
The earlier I-series views pool across conditions and remain useful as an overview.
The J-series pages are the designated isolated views.
The normal regeneration commands automatically include these additions.

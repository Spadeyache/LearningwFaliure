# Experiment index

| Question | Active command / config | Data or checkpoint | Current result / next step |
| --- | --- | --- | --- |
| Can the policy learn movement and independent grip strength? | `python -m robot_adaptation.policy.train`; `SETTINGS` in `policy/train.py` | New runs: `runs/policy/`; historical: `runs/learning/` | Learner uses v2; inspection command loads a selected saved run. |
| How do physical changes affect a fixed supplied estimate? | `bash scripts/collect_varied.sh`; `configs/failure_collection_varied.json` | [29,830 attempts](../runs/failure_collection/dense_single_pair_fixed40g/), [earlier 600](../runs/failure_collection/varied_fixed40g/) | Recorded movement, forces, physics and outcomes with the policy receiving 40 g. |
| Can movement-based grouping recover useful failure distinctions? | `python -m robot_adaptation.analysis.failure_discovery.analyze` | Existing saved episodes | Numeric groups did not consistently capture the intended underlying causes. See the component guide for the exploratory results. |
| Do failures respond differently to matched physical interventions? | `python -m robot_adaptation.analysis.failure_discovery.response_groups` | Mass/friction grid from dense collection | [90 attempts, seven observed response profiles](../failure_discovery/results/response_mass_friction/index.html). Deployment recognition remains open. |
| Can appearance supply an initial physical estimate? | `python -m robot_adaptation.estimators.visual_mass` | [Fixed-density cube images and trained estimator](../runs/visual_mass/initial_rgb_mass/) | 2.76 g test MAE on 48 images / 12 held-out sizes; 106.37 g constant baseline. Grasping benefit remains to be evaluated. |
| Which environmental inputs matter to a repairable lift skill? | `python -m experiments.crest --plan-only`; `configs/crest_lift.json` | Explicit run output chosen with `--run --output` | CREST experiment implementation is separate from the visual estimator. |
| Is the published policy reliable in the current CPU setup? | `bash scripts/collect_stock_short.sh --plan-only`; `configs/failure_collection_stock_short.json` | [Ten baseline attempts](../runs/failure_collection/stock_short/) | 7/10 success; quality gate rejected the sweep. |

## Combined simulation runner

`python -m robot_adaptation.runtime --record-video` connects the initial RGB
prediction to a completed saved policy. Settings are in
`configs/visual_mass_deployment.json`, and outputs go to `runs/deployment/`.
[Full-horizon recorded episode](../runs/deployment/20261021_235109_413496/summary.json):
predicted mass 62.319 g for an actual 64.000 g cube. The estimate was supplied
through all 50 actions / 51 observations. The cube rose 105.5 mm and met the
goal-and-grasp condition for the final 42 samples (about 2.1 simulated seconds).
Final goal error was 7.85 mm. Reported runner time was 3.98 seconds, excluding
Python/import startup.
[Full rollout GIF](../runs/deployment/20261021_235109_413496/episode_000/rollout.gif).

The earlier nine-step clips stopped on first success and were insufficient to
evaluate continued holding. The runner now completes the configured horizon by
default, following the collection procedure, with `--stop-on-success` available
for short clips. The task success criterion itself is unchanged.
Controlled policy-benefit comparisons remain to be run.

### Full configured rollout: three cube sizes

[Run summary](../runs/deployment/20261022_014201_067220/summary.json): all three
configured cases completed 50 actions with final goal success and grasp. The
predicted-weight input stayed fixed throughout every trajectory. Recorded runner
time was 10.10 seconds, excluding Python/import startup.

| Cube side | Actual mass | Predicted mass | Final success | Final continuous success |
| --- | ---: | ---: | --- | ---: |
| 4 cm | 64.0 g | 62.32 g | Yes | 2.10 s |
| 5 cm | 125.0 g | 121.24 g | Yes | 2.10 s |
| 6 cm | 216.0 g | 212.45 g | Yes | 2.05 s |

Mean absolute mass error across these three cases was 3.00 g. These are three
configured trials, one starting seed per size, not a broad reliability estimate.
Recordings are in each episode folder in the linked run.


## Current research question

Does an explicit physical estimate help the robot adapt better than predicting
useful control settings directly?

The current visual baseline establishes that a small image-only model can learn
a controlled size-to-mass prior. The next comparison needs the same held-out
conditions and policy evaluation; estimator accuracy alone does not answer the
adaptation question. Updating estimates from interaction is a later research stage.

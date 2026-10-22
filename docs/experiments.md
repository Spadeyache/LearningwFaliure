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

## Current research question

Does an explicit physical estimate help the robot adapt better than predicting
useful control settings directly?

The current visual baseline establishes that a small image-only model can learn
a controlled size-to-mass prior. The next comparison needs the same held-out
conditions and policy evaluation; estimator accuracy alone does not answer the
adaptation question. Updating estimates from interaction is a later research stage.

# Visual mass estimator moved

The active code and guide are in
[robot_adaptation/estimators/visual_mass](../robot_adaptation/estimators/visual_mass/README.md).

Run `python -m robot_adaptation.estimators.visual_mass --help`. The legacy
`python -m visual_mass_estimator` entrypoints still delegate to this package.
Existing datasets and checkpoints remain in `runs/visual_mass/`.

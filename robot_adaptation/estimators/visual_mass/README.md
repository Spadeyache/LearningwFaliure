# Initial-image mass estimator

A standalone first experiment: render an object before contact, predict its mass
from RGB, and compare the prediction with the simulator's actual mass.

## Run everything

From the repository root, using the existing environment and simulator assets:

```bash
source scripts/activate_grip.sh
python -m robot_adaptation.estimators.visual_mass
```

This generates 384 images of 96 different cube sizes, trains a small CNN for up to
80 epochs, and saves a fresh directory under `runs/visual_mass/`. No pretrained
weights are downloaded. CPU software rendering and CPU training are supported;
training chooses CUDA when available. Existing output directories are refused.

To choose a destination and change the run size:

```bash
python -m robot_adaptation.estimators.visual_mass --output runs/visual_mass/my_run \
  --objects 96 --views 4 --epochs 80 --device cpu
```

Object count must be at least 16 and divisible by eight. A tiny smoke run is not
enough to establish prediction quality.

## What this experiment assumes

- All objects are cubes of one material at density 1000 kg/m³. Side length varies
  from 25 to 75 mm, giving masses from about 15.6 to 421.9 g.
- Friction, camera calibration, material appearance, and the background are fixed.
  Position and orientation vary independently of mass.
- Visible size supplies a genuine cue: mass equals density times volume. Color,
  filenames, and simulator metadata are never model inputs.
- Each image is captured immediately after reset, before contact or an action.
  Its label is the actual mass read back from the physics engine.

This is a **controlled visual size-to-mass prior**, not general mass inference.
Identical-looking objects can have different densities and masses. The earlier
failure collection varied mass independently of appearance and has no initial
images, so rendering that data alone would not make mass visually identifiable.

## Training and evaluation

The CNN predicts standardized log mass. Normalization uses only training labels;
the output is converted back to kilograms. All views of an object stay in one
split. In each group of eight neighboring sizes, six objects go to training, one
to validation, and one to test. Held-out sizes measure interpolation under this
controlled setup, not generalization to unseen materials or camera setups.

Validation selects the checkpoint; the test split is evaluated only after that
selection. Results include mass error and a constant training-mean baseline.
The run saves:

- `run.json`: configuration and stage status.
- `dataset/dataset.json`: scene assumptions, splits, actual mass labels, images.
- `model/best.pt`: predictor weights and training normalization.
- `model/metrics.json`: held-out metrics and baseline.
- `model/predictions.csv`: individual predictions.
- `model/training_curve.png` and `model/predictions.png`: result plots.

Train again using a generated dataset, with a fresh output directory:

```bash
python -m robot_adaptation.estimators.visual_mass.train \
  --dataset runs/visual_mass/my_run/dataset \
  --output runs/visual_mass/retrain --epochs 80 --device cpu
```

Predict from an image:

```bash
python -m robot_adaptation.estimators.visual_mass.predict \
  --checkpoint runs/visual_mass/my_run/model/best.pt \
  --image runs/visual_mass/my_run/dataset/images/cube_0000_view_000.png
```

Prediction reports mass in kilograms and gravitational weight in newtons. The
existing policy's estimated-weight input uses newtons, so a later integration
must convert predicted mass with the simulator's gravitational acceleration.

## What comes next

First connect the prediction to a policy that uses the estimated property, then
compare true mass, predicted mass, and a fixed estimate on the same held-out
objects. Prediction accuracy alone does not demonstrate improved grasping.

Holding friction fixed is sufficient for this first experiment. Grip also depends
on friction and contact geometry: mass alone does not determine a universal grip
force. Vary friction later to examine where a mass-only assumption breaks down.
Learning to revise estimates from interaction remains a separate next stage.

## Completed baseline run

`runs/visual_mass/initial_rgb_mass` completed on CPU with the defaults above.
The model was selected at epoch 64 by validation loss, out of 80 training epochs.

| Split | Objects | Images | Mean absolute error |
| --- | ---: | ---: | ---: |
| Training | 72 | 288 | 1.42 g |
| Validation | 12 | 48 | 2.51 g |
| Test | 12 | 48 | 2.76 g |

The constant training-mean predictor had test MAE **106.37 g**. Test RMSE for the
CNN was **4.43 g**. This single controlled run demonstrates learning the visual
size-to-mass relationship under the stated assumptions. It does not establish
general mass estimation or improved policy performance.

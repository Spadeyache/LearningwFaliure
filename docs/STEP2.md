# Step 2: clean-success next-pose prediction

The committed model is artifacts/predictor.pt (about 120 KiB). It was trained on
60 clean episodes / 4,601 transitions, with 10 episodes / 785 transitions used
only for checkpoint selection. Calibration and test episodes were not used.
The fixed manifest is results/splits.json; files are checked by SHA-256.

## Reproduce

Use the Python environment and Vulkan exports from the root README.

```bash
python scripts/collect_clean_episodes.py -n 100 --output-dir data/pickcube100
python scripts/make_splits.py --output results/splits.json
python scripts/train_predictor.py --manifest results/splits.json --output-dir runs/predictor
python -m unittest discover -s tests -v
```

Existing datasets, manifests, and checkpoints are preserved. On this completed
workspace, the first two commands are already done. To retrain using the locked
manifest, use a new training output directory. If regenerating data differs from
the recorded hashes, create a separate manifest/run rather than changing this one.

## Method

At each 20 Hz control step, a single-layer, 64-hidden-unit, unidirectional GRU
observes 62 features: qpos (9), qvel (9), TCP/cube position and rotation-matrix
features (18), goal-minus-cube (3), intended action (8), previous observed pose
increments (12), and cube-minus-TCP position (3). Rotations are sign invariant.

The target is a 12-vector of next-step world translation/rotation-vector increments:
TCP translation/rotation then cube translation/rotation. The network predicts a
correction to the previous increment (constant velocity). Its initial zero output
is exactly that baseline. Predictions convert back to two 7D world poses.

Inputs and target residuals are scaled using training statistics only. Padding is
masked out of the loss. GRU state starts fresh for each episode. Optimization uses
AdamW, learning rate 0.001, weight decay 0.0001, batches of 16 episodes, gradient
norm clipping at 1, and deterministic PyTorch operations. Seed: 7.
Best validation checkpoint: epoch 132; early stopping ended at epoch 167.
The selected checkpoint is never changed in response to test or perturbation results.

| Validation mean error | Learned | Constant velocity | Persistence |
|---|---:|---:|---:|
| TCP position (mm) | 0.2040 | 0.7476 | 4.8857 |
| TCP rotation (mrad) | 0.3553 | 0.8911 | 5.5271 |
| Cube position (mm) | 0.1134 | 0.3546 | 2.6943 |
| Cube rotation (mrad) | 0.2855 | 0.2281 | 0.2322 |

Full metrics and loss history are in results/training.json.
These are teacher-forced, one-step forecasts, not free-running long-horizon rollouts.
Success flags and rewards are not model inputs or targets. Training on successful
transitions is self-supervised; it uses no failure labels.

Tests cover causal dependence, rotation/translation round trips, quaternion sign
equivalence, and the zero-initialized constant-velocity prior.

Sources: [PyTorch GRU](https://docs.pytorch.org/docs/2.14/generated/torch.nn.GRU.html),
[AdamW](https://docs.pytorch.org/docs/2.14/generated/torch.optim.AdamW.html), and
[ManiSkill rotation utilities](https://github.com/mani-skill/ManiSkill/blob/main/mani_skill/utils/geometry/rotation_conversions.py).

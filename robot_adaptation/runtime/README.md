# Estimator-to-policy simulation runtime

Run the saved visual-mass estimator and a saved picking policy together:

```bash
cd /home/ubuntu/faliure
source scripts/activate_grip.sh
python -m robot_adaptation.runtime --record-video
```

This creates a fresh `runs/deployment/<timestamp>/` directory. By default it runs
three independent episodes with 4, 5, and 6 cm cubes at constant density
1000 kg/m³ (64, 125, and 216 g). Object/table friction is 0.3, finger friction is
2.0, and yaw is zero. Both models use CPU inference with frozen weights.

## Per-episode flow

1. Construct the physical scene and reset it.
2. Capture one raw initial RGB image using the exact camera configuration from
   visual-estimator training. No action advances physics before this image.
3. Predict mass from RGB pixels using the saved CNN.
4. Set the environment's reported mass and replace observation slot 42 with
   predicted mass × actual gravity magnitude, in newtons, before the first action.
5. Run the deterministic policy for the configured 50-step horizon, continuing
   after an initial success signal to observe holding. Subsequent observations
   keep the same estimate. No reset separates the image from the actions.
6. Save the trajectory, actual physics for evaluation, and final task outcome.

Use `--stop-on-success` only for a short first-success clip. By default, the
runner continues task-success termination signals to the step budget, matching
the existing collection procedure. Truncation or nonsuccess termination still
stops the run. The success criterion itself is unchanged.

The scene's true mass is used for physics and separate evaluation logs. It does
not enter the visual predictor or the policy's supplied-weight slot. The policy
still receives its usual simulator state observations, including positions and
finger forces; this is a simulation integration, not a real-robot sensor stack.

## Models and settings

[configs/visual_mass_deployment.json](../../configs/visual_mass_deployment.json)
contains the scene, episode budget and model paths. Paths inside the config are
relative to the repository root. The default estimator checkpoint is the completed
`runs/visual_mass/initial_rgb_mass/model/best.pt` baseline. A null policy path
selects the latest usable completed model across `runs/policy/` and historical
`runs/learning/`.

Supported policies must have a completed manifest, the exact 45-input/five-action
schema, the native controller, and either the frozen v1 or independent v2
architecture. Incomplete models and older 43-input policies are excluded.
A model's recorded grip-force limits are used by the runtime environment.

Override paths or choose a smaller run:

```bash
python -m robot_adaptation.runtime --episodes 1 --record-video   --output runs/deployment/my_first_episode

python -m robot_adaptation.runtime   --estimator-checkpoint runs/visual_mass/initial_rgb_mass/model/best.pt   --policy-checkpoint runs/learning/20261009T045047-c852bfc9/final_ckpt.pt
```

Existing output directories are refused. The runner has no training loop or model
download step. Changing `density_kg_m3` introduces an appearance/physical-mass
mismatch against the estimator's fixed-density prior; prediction cannot see that
hidden change directly.

## Saved artifacts

- `config.json`, `manifest.json`: resolved model paths, checkpoint/source hashes,
  policy architecture/training settings, camera, software versions and run status.
- `summary.json`: final/any-time successes and mass prediction MAE for this run.
- `source/`: the runtime, estimator, policy and simulator source used.
- `episode_000/initial.png`: the unannotated RGB input to the estimator.
- `episode_000/episode.json`: predicted mass, supplied weight, actual physics,
  seed, image/state hashes, final goal error, clearance and grasp/success status.
- `episode_000/trajectory.npz`: actual policy observations, raw/clipped actions,
  weight input at every step, rewards, poses, joint states and motor limits.
- `episode_000/rollout.gif` and `final.png`: optional human-view recording and
  final frame with `--record-video`. The final frame is saved even on early success.

A failed/interrupted episode is recorded as incomplete. Final success uses the
shared collection task's held-at-goal rule, including the grasp requirement;
reaching the goal earlier is recorded separately as any-time success.

## Scope

This runner establishes the connection between the two saved models. Estimates
are recomputed at each episode's initial image and stay fixed within that episode.
Learning updates from failures and retaining experience across attempts remain
future work.

The estimator assumes constant-density cubes. The policy was trained on 4 cm
cubes and a different hidden friction profile; larger cubes and the chosen
materials can change grasp performance. A successful launch alone does not show
that estimated mass improves adaptation. That requires matched comparisons with
fixed estimates, true mass, and eventually directly predicted control settings.

## Recorded integration example

The full-horizon run in `runs/deployment/20261021_235109_413496/` completed
50 actions and 51 observations for one 4 cm cube. The estimator predicted
62.319 g for a 64.000 g body (1.681 g error), and all observations carried
the same 0.611352 N predicted-weight input. The cube rose 105.5 mm; success
and grasp stayed true from step 9 through step 50 (42 final samples, about
2.1 simulated seconds). Final goal error was 7.85 mm. The GIF includes all
50 steps and the final state. Reported runner time was 3.98 seconds, excluding
Python/import startup.

Earlier runs in `20261021_234802_550312` and `20261021_234906_513736` ended
at first success after nine steps. Their reports remain preserved, but do not
establish sustained holding. The runner now defaults to the full configured
horizon; `--stop-on-success` reproduces the shorter stopping behavior.


## Full default set recorded

`runs/deployment/20261022_014201_067220/` contains the full three-size default
set. All three episodes completed 50 steps and ended grasped at the goal. Actual
masses 64/125/216 g were predicted as 62.32/121.24/212.45 g, respectively. The
estimated weight input remained constant in each trajectory. The final
continuous-success periods were 2.10/2.10/2.05 seconds; runner time was 10.10
seconds excluding Python/import startup. Each episode has an 11-frame GIF with
its final state. This is one seed per configured size.

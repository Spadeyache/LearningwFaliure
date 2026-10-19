# Official policy: short single-variable collection

76 settings × 10 seeds = 760 attempts.
Baseline gate: at least 90% FINAL success in the nominal attempts.
If the gate fails, save the baseline and stop before physical sweeps.
Original 42 inputs / 4 actions; no weight input, grip-strength branch, or custom vertical-lift goal.
Original 50-step horizon and geometric success; final and any-time flags both saved.
Native task on CPU is not a claim of identical behavior to the published GPU runtime.

| Factor | Nominal | Short sweep |
| --- | --- | --- |
| mass | 0.064 | 0.016, 0.064, 0.076, 0.136, 0.196, 0.256 |
| object_friction | 0.3 | 0.075, 0.3, 0.35625, 0.6375, 0.91875, 1.2 |
| dynamic_friction_ratio | 1.0 | 0.25, 0.4375, 0.625, 0.8125, 1.0 |
| finger_friction | 2.0 | 0.5, 2.0, 2.375, 4.25, 6.125, 8.0 |
| table_friction | 0.3 | 0.075, 0.3, 0.35625, 0.6375, 0.91875, 1.2 |
| size | 0.04 | 0.03, 0.035, 0.04, 0.045, 0.05 |
| shape | cube | cube, sphere |
| com_x | 0.0 | -0.005, -0.0025, 0.0, 0.0025, 0.005 |
| com_y | 0.0 | -0.005, -0.0025, 0.0, 0.0025, 0.005 |
| com_z | 0.0 | -0.005, -0.0025, 0.0, 0.0025, 0.005 |
| goal_height | 0.3 | 0.2, 0.25, 0.3, 0.35, 0.4 |
| restitution | 0.0 | 0.0, 0.125, 0.25, 0.375, 0.5 |
| linear_damping | 0.0 | 0.0, 0.25, 0.5, 0.75, 1.0 |
| angular_damping | 0.05 | 0.0, 0.0375, 0.05, 0.075, 0.1125, 0.15 |
| spawn_x | 0.0 | -0.04, -0.02, 0.0, 0.02, 0.04 |
| spawn_y | 0.0 | -0.04, -0.02, 0.0, 0.02, 0.04 |
| spawn_yaw | 0.0 | -0.523598775598, -0.261799387799, 0.0, 0.261799387799, 0.523598775598 |
| inertia_scale | 1.0 | 0.5, 0.875, 1.0, 1.25, 1.625, 2.0 |

Goal height denotes the maximum of the native random height range, not a fixed vertical lift.
Restitution and linear damping start at zero and cannot vary below zero. Sliding/static ratio cannot exceed one.
Mass/size shifts also change derived inertia. Inertia-scale shifts are explicitly synthetic.
The default gate uses only ten starts and is a screening check, not a precise reliability estimate.

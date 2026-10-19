# Next collection: dense single and pair sweeps

2,983 unique settings × 10 seeds = 29,830 episodes.
At most two declared factors change per setting. Fixed policy mass estimate: 40 g. No new data has been collected by writing this plan.

| Factor | Nominal | Numeric levels / categories | Unit | Enabled |
| --- | --- | --- | --- | --- |
| mass | 0.1 | 0.04, 0.086, 0.1, 0.132, 0.178, 0.224, 0.27, 0.316, 0.362, 0.408, 0.454, 0.5 | kg | True |
| object_friction | 0.4 | 0.1, 0.19, 0.28, 0.37, 0.4, 0.46, 0.55, 0.64, 0.73, 0.82, 0.91, 1 | coefficient | True |
| dynamic_friction_ratio | 1.0 | 0.25, 0.325, 0.4, 0.475, 0.55, 0.625, 0.7, 0.775, 0.85, 0.925, 1 | sliding/static ratio | True |
| finger_friction | 0.2 | 0.1, 0.14, 0.18, 0.2, 0.22, 0.26, 0.3, 0.34, 0.38, 0.42, 0.46, 0.5 | coefficient | True |
| table_friction | 0.3 | 0.1, 0.17, 0.24, 0.3, 0.31, 0.38, 0.45, 0.52, 0.59, 0.66, 0.73, 0.8 | coefficient | True |
| size | 0.04 | 0.03, 0.032, 0.034, 0.036, 0.038, 0.04, 0.042, 0.044, 0.046, 0.048, 0.05 | m; uniform side or diameter | True |
| shape | cube | cube, sphere | category | True |
| com_x | 0.0 | -0.005, -0.004, -0.003, -0.002, -0.001, 0, 0.001, 0.002, 0.003, 0.004, 0.005 | m | True |
| com_y | 0.0 | -0.005, -0.004, -0.003, -0.002, -0.001, 0, 0.001, 0.002, 0.003, 0.004, 0.005 | m | True |
| com_z | 0.0 | -0.005, -0.004, -0.003, -0.002, -0.001, 0, 0.001, 0.002, 0.003, 0.004, 0.005 | m | True |
| goal_height | 0.2 | 0.1, 0.12, 0.14, 0.16, 0.18, 0.2, 0.22, 0.24, 0.26, 0.28, 0.3 | m | True |
| restitution | 0.0 | 0, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5 | coefficient | True |
| linear_damping | 0.0 | 0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1 | simulator coefficient | True |
| angular_damping | 0.05 | 0, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5 | simulator coefficient | True |
| spawn_x | 0.0 | -0.04, -0.032, -0.024, -0.016, -0.008, 0, 0.008, 0.016, 0.024, 0.032, 0.04 | m offset from seeded spawn | True |
| spawn_y | 0.0 | -0.04, -0.032, -0.024, -0.016, -0.008, 0, 0.008, 0.016, 0.024, 0.032, 0.04 | m offset from seeded spawn | True |
| spawn_yaw | 0.0 | -0.523599, -0.418879, -0.314159, -0.20944, -0.10472, 0, 0.10472, 0.20944, 0.314159, 0.418879, 0.523599 | rad offset from seeded yaw | True |
| inertia_scale | 1.0 | 0.5, 0.65, 0.8, 0.95, 1, 1.1, 1.25, 1.4, 1.55, 1.7, 1.85, 2 | multiplier; synthetic independent inertia | True |

## Pair designs

Every enabled numeric pair is sampled in both same-direction and opposite-direction sweeps. These use evenly spaced physical values from low to high; categorical shape pairs use all collected level combinations.
The nominal value is additionally retained for every single-factor comparison. Duplicate settings are run once and retain all applicable design-family labels.
These are diagonal pair sweeps, not the complete two-dimensional factorial grid. Reused starting seeds vary initial states but do not count as extra property interventions.
Mass changes derive inertia from mass and size. Inertia-scale interventions are explicitly synthetic independent inertia changes. Dynamic-friction ratio changes sliding friction while holding static friction fixed.
Spawn X/Y/yaw are offsets from the same seeded reset. The vertical goal follows the spawn; changing spawn also moves the target XY by design.

## Actual family coverage

| Family | Unique settings (references may overlap) |
| --- | --- |
| baseline | 1 |
| categorical_cross:dynamic_friction_ratio+shape | 22 |
| categorical_cross:finger_friction+shape | 24 |
| categorical_cross:mass+shape | 24 |
| categorical_cross:object_friction+shape | 24 |
| categorical_cross:shape+angular_damping | 22 |
| categorical_cross:shape+com_x | 22 |
| categorical_cross:shape+com_y | 22 |
| categorical_cross:shape+com_z | 22 |
| categorical_cross:shape+goal_height | 22 |
| categorical_cross:shape+inertia_scale | 24 |
| categorical_cross:shape+linear_damping | 22 |
| categorical_cross:shape+restitution | 22 |
| categorical_cross:shape+spawn_x | 22 |
| categorical_cross:shape+spawn_y | 22 |
| categorical_cross:shape+spawn_yaw | 22 |
| categorical_cross:size+shape | 22 |
| categorical_cross:table_friction+shape | 24 |
| opposite:angular_damping+inertia_scale | 11 |
| opposite:angular_damping+spawn_x | 11 |
| opposite:angular_damping+spawn_y | 11 |
| opposite:angular_damping+spawn_yaw | 11 |
| opposite:com_x+angular_damping | 11 |
| opposite:com_x+com_y | 11 |
| opposite:com_x+com_z | 11 |
| opposite:com_x+goal_height | 11 |
| opposite:com_x+inertia_scale | 11 |
| opposite:com_x+linear_damping | 11 |
| opposite:com_x+restitution | 11 |
| opposite:com_x+spawn_x | 11 |
| opposite:com_x+spawn_y | 11 |
| opposite:com_x+spawn_yaw | 11 |
| opposite:com_y+angular_damping | 11 |
| opposite:com_y+com_z | 11 |
| opposite:com_y+goal_height | 11 |
| opposite:com_y+inertia_scale | 11 |
| opposite:com_y+linear_damping | 11 |
| opposite:com_y+restitution | 11 |
| opposite:com_y+spawn_x | 11 |
| opposite:com_y+spawn_y | 11 |
| opposite:com_y+spawn_yaw | 11 |
| opposite:com_z+angular_damping | 11 |
| opposite:com_z+goal_height | 11 |
| opposite:com_z+inertia_scale | 11 |
| opposite:com_z+linear_damping | 11 |
| opposite:com_z+restitution | 11 |
| opposite:com_z+spawn_x | 11 |
| opposite:com_z+spawn_y | 11 |
| opposite:com_z+spawn_yaw | 11 |
| opposite:dynamic_friction_ratio+angular_damping | 11 |
| opposite:dynamic_friction_ratio+com_x | 11 |
| opposite:dynamic_friction_ratio+com_y | 11 |
| opposite:dynamic_friction_ratio+com_z | 11 |
| opposite:dynamic_friction_ratio+finger_friction | 11 |
| opposite:dynamic_friction_ratio+goal_height | 11 |
| opposite:dynamic_friction_ratio+inertia_scale | 11 |
| opposite:dynamic_friction_ratio+linear_damping | 11 |
| opposite:dynamic_friction_ratio+restitution | 11 |
| opposite:dynamic_friction_ratio+size | 11 |
| opposite:dynamic_friction_ratio+spawn_x | 11 |
| opposite:dynamic_friction_ratio+spawn_y | 11 |
| opposite:dynamic_friction_ratio+spawn_yaw | 11 |
| opposite:dynamic_friction_ratio+table_friction | 11 |
| opposite:finger_friction+angular_damping | 11 |
| opposite:finger_friction+com_x | 11 |
| opposite:finger_friction+com_y | 11 |
| opposite:finger_friction+com_z | 11 |
| opposite:finger_friction+goal_height | 11 |
| opposite:finger_friction+inertia_scale | 11 |
| opposite:finger_friction+linear_damping | 11 |
| opposite:finger_friction+restitution | 11 |
| opposite:finger_friction+size | 11 |
| opposite:finger_friction+spawn_x | 11 |
| opposite:finger_friction+spawn_y | 11 |
| opposite:finger_friction+spawn_yaw | 11 |
| opposite:finger_friction+table_friction | 11 |
| opposite:goal_height+angular_damping | 11 |
| opposite:goal_height+inertia_scale | 11 |
| opposite:goal_height+linear_damping | 11 |
| opposite:goal_height+restitution | 11 |
| opposite:goal_height+spawn_x | 11 |
| opposite:goal_height+spawn_y | 11 |
| opposite:goal_height+spawn_yaw | 11 |
| opposite:linear_damping+angular_damping | 11 |
| opposite:linear_damping+inertia_scale | 11 |
| opposite:linear_damping+spawn_x | 11 |
| opposite:linear_damping+spawn_y | 11 |
| opposite:linear_damping+spawn_yaw | 11 |
| opposite:mass+angular_damping | 11 |
| opposite:mass+com_x | 11 |
| opposite:mass+com_y | 11 |
| opposite:mass+com_z | 11 |
| opposite:mass+dynamic_friction_ratio | 11 |
| opposite:mass+finger_friction | 11 |
| opposite:mass+goal_height | 11 |
| opposite:mass+inertia_scale | 11 |
| opposite:mass+linear_damping | 11 |
| opposite:mass+object_friction | 11 |
| opposite:mass+restitution | 11 |
| opposite:mass+size | 11 |
| opposite:mass+spawn_x | 11 |
| opposite:mass+spawn_y | 11 |
| opposite:mass+spawn_yaw | 11 |
| opposite:mass+table_friction | 11 |
| opposite:object_friction+angular_damping | 11 |
| opposite:object_friction+com_x | 11 |
| opposite:object_friction+com_y | 11 |
| opposite:object_friction+com_z | 11 |
| opposite:object_friction+dynamic_friction_ratio | 11 |
| opposite:object_friction+finger_friction | 11 |
| opposite:object_friction+goal_height | 11 |
| opposite:object_friction+inertia_scale | 11 |
| opposite:object_friction+linear_damping | 11 |
| opposite:object_friction+restitution | 11 |
| opposite:object_friction+size | 11 |
| opposite:object_friction+spawn_x | 11 |
| opposite:object_friction+spawn_y | 11 |
| opposite:object_friction+spawn_yaw | 11 |
| opposite:object_friction+table_friction | 11 |
| opposite:restitution+angular_damping | 11 |
| opposite:restitution+inertia_scale | 11 |
| opposite:restitution+linear_damping | 11 |
| opposite:restitution+spawn_x | 11 |
| opposite:restitution+spawn_y | 11 |
| opposite:restitution+spawn_yaw | 11 |
| opposite:size+angular_damping | 11 |
| opposite:size+com_x | 11 |
| opposite:size+com_y | 11 |
| opposite:size+com_z | 11 |
| opposite:size+goal_height | 11 |
| opposite:size+inertia_scale | 11 |
| opposite:size+linear_damping | 11 |
| opposite:size+restitution | 11 |
| opposite:size+spawn_x | 11 |
| opposite:size+spawn_y | 11 |
| opposite:size+spawn_yaw | 11 |
| opposite:spawn_x+inertia_scale | 11 |
| opposite:spawn_x+spawn_y | 11 |
| opposite:spawn_x+spawn_yaw | 11 |
| opposite:spawn_y+inertia_scale | 11 |
| opposite:spawn_y+spawn_yaw | 11 |
| opposite:spawn_yaw+inertia_scale | 11 |
| opposite:table_friction+angular_damping | 11 |
| opposite:table_friction+com_x | 11 |
| opposite:table_friction+com_y | 11 |
| opposite:table_friction+com_z | 11 |
| opposite:table_friction+goal_height | 11 |
| opposite:table_friction+inertia_scale | 11 |
| opposite:table_friction+linear_damping | 11 |
| opposite:table_friction+restitution | 11 |
| opposite:table_friction+size | 11 |
| opposite:table_friction+spawn_x | 11 |
| opposite:table_friction+spawn_y | 11 |
| opposite:table_friction+spawn_yaw | 11 |
| single:angular_damping | 11 |
| single:com_x | 11 |
| single:com_y | 11 |
| single:com_z | 11 |
| single:dynamic_friction_ratio | 11 |
| single:finger_friction | 12 |
| single:goal_height | 11 |
| single:inertia_scale | 12 |
| single:linear_damping | 11 |
| single:mass | 12 |
| single:object_friction | 12 |
| single:restitution | 11 |
| single:shape | 2 |
| single:size | 11 |
| single:spawn_x | 11 |
| single:spawn_y | 11 |
| single:spawn_yaw | 11 |
| single:table_friction | 12 |
| together:angular_damping+inertia_scale | 11 |
| together:angular_damping+spawn_x | 11 |
| together:angular_damping+spawn_y | 11 |
| together:angular_damping+spawn_yaw | 11 |
| together:com_x+angular_damping | 11 |
| together:com_x+com_y | 11 |
| together:com_x+com_z | 11 |
| together:com_x+goal_height | 11 |
| together:com_x+inertia_scale | 11 |
| together:com_x+linear_damping | 11 |
| together:com_x+restitution | 11 |
| together:com_x+spawn_x | 11 |
| together:com_x+spawn_y | 11 |
| together:com_x+spawn_yaw | 11 |
| together:com_y+angular_damping | 11 |
| together:com_y+com_z | 11 |
| together:com_y+goal_height | 11 |
| together:com_y+inertia_scale | 11 |
| together:com_y+linear_damping | 11 |
| together:com_y+restitution | 11 |
| together:com_y+spawn_x | 11 |
| together:com_y+spawn_y | 11 |
| together:com_y+spawn_yaw | 11 |
| together:com_z+angular_damping | 11 |
| together:com_z+goal_height | 11 |
| together:com_z+inertia_scale | 11 |
| together:com_z+linear_damping | 11 |
| together:com_z+restitution | 11 |
| together:com_z+spawn_x | 11 |
| together:com_z+spawn_y | 11 |
| together:com_z+spawn_yaw | 11 |
| together:dynamic_friction_ratio+angular_damping | 11 |
| together:dynamic_friction_ratio+com_x | 11 |
| together:dynamic_friction_ratio+com_y | 11 |
| together:dynamic_friction_ratio+com_z | 11 |
| together:dynamic_friction_ratio+finger_friction | 11 |
| together:dynamic_friction_ratio+goal_height | 11 |
| together:dynamic_friction_ratio+inertia_scale | 11 |
| together:dynamic_friction_ratio+linear_damping | 11 |
| together:dynamic_friction_ratio+restitution | 11 |
| together:dynamic_friction_ratio+size | 11 |
| together:dynamic_friction_ratio+spawn_x | 11 |
| together:dynamic_friction_ratio+spawn_y | 11 |
| together:dynamic_friction_ratio+spawn_yaw | 11 |
| together:dynamic_friction_ratio+table_friction | 11 |
| together:finger_friction+angular_damping | 11 |
| together:finger_friction+com_x | 11 |
| together:finger_friction+com_y | 11 |
| together:finger_friction+com_z | 11 |
| together:finger_friction+goal_height | 11 |
| together:finger_friction+inertia_scale | 11 |
| together:finger_friction+linear_damping | 11 |
| together:finger_friction+restitution | 11 |
| together:finger_friction+size | 11 |
| together:finger_friction+spawn_x | 11 |
| together:finger_friction+spawn_y | 11 |
| together:finger_friction+spawn_yaw | 11 |
| together:finger_friction+table_friction | 11 |
| together:goal_height+angular_damping | 11 |
| together:goal_height+inertia_scale | 11 |
| together:goal_height+linear_damping | 11 |
| together:goal_height+restitution | 11 |
| together:goal_height+spawn_x | 11 |
| together:goal_height+spawn_y | 11 |
| together:goal_height+spawn_yaw | 11 |
| together:linear_damping+angular_damping | 11 |
| together:linear_damping+inertia_scale | 11 |
| together:linear_damping+spawn_x | 11 |
| together:linear_damping+spawn_y | 11 |
| together:linear_damping+spawn_yaw | 11 |
| together:mass+angular_damping | 11 |
| together:mass+com_x | 11 |
| together:mass+com_y | 11 |
| together:mass+com_z | 11 |
| together:mass+dynamic_friction_ratio | 11 |
| together:mass+finger_friction | 11 |
| together:mass+goal_height | 11 |
| together:mass+inertia_scale | 11 |
| together:mass+linear_damping | 11 |
| together:mass+object_friction | 11 |
| together:mass+restitution | 11 |
| together:mass+size | 11 |
| together:mass+spawn_x | 11 |
| together:mass+spawn_y | 11 |
| together:mass+spawn_yaw | 11 |
| together:mass+table_friction | 11 |
| together:object_friction+angular_damping | 11 |
| together:object_friction+com_x | 11 |
| together:object_friction+com_y | 11 |
| together:object_friction+com_z | 11 |
| together:object_friction+dynamic_friction_ratio | 11 |
| together:object_friction+finger_friction | 11 |
| together:object_friction+goal_height | 11 |
| together:object_friction+inertia_scale | 11 |
| together:object_friction+linear_damping | 11 |
| together:object_friction+restitution | 11 |
| together:object_friction+size | 11 |
| together:object_friction+spawn_x | 11 |
| together:object_friction+spawn_y | 11 |
| together:object_friction+spawn_yaw | 11 |
| together:object_friction+table_friction | 11 |
| together:restitution+angular_damping | 11 |
| together:restitution+inertia_scale | 11 |
| together:restitution+linear_damping | 11 |
| together:restitution+spawn_x | 11 |
| together:restitution+spawn_y | 11 |
| together:restitution+spawn_yaw | 11 |
| together:size+angular_damping | 11 |
| together:size+com_x | 11 |
| together:size+com_y | 11 |
| together:size+com_z | 11 |
| together:size+goal_height | 11 |
| together:size+inertia_scale | 11 |
| together:size+linear_damping | 11 |
| together:size+restitution | 11 |
| together:size+spawn_x | 11 |
| together:size+spawn_y | 11 |
| together:size+spawn_yaw | 11 |
| together:spawn_x+inertia_scale | 11 |
| together:spawn_x+spawn_y | 11 |
| together:spawn_x+spawn_yaw | 11 |
| together:spawn_y+inertia_scale | 11 |
| together:spawn_y+spawn_yaw | 11 |
| together:spawn_yaw+inertia_scale | 11 |
| together:table_friction+angular_damping | 11 |
| together:table_friction+com_x | 11 |
| together:table_friction+com_y | 11 |
| together:table_friction+com_z | 11 |
| together:table_friction+goal_height | 11 |
| together:table_friction+inertia_scale | 11 |
| together:table_friction+linear_damping | 11 |
| together:table_friction+restitution | 11 |
| together:table_friction+size | 11 |
| together:table_friction+spawn_x | 11 |
| together:table_friction+spawn_y | 11 |
| together:table_friction+spawn_yaw | 11 |

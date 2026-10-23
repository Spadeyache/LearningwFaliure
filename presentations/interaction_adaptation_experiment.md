# Refining a mass estimate through interaction

**Status: proposed experiment; not implemented or evaluated.**

## Question and hypothesis

Can a robot improve its initial mass estimate through a short interaction, and does that improvement help an existing weight-conditioned policy complete a pick-and-lift task?

Start with one object type: cubes with identical dimensions and appearance but different densities. An initial image cannot distinguish their masses. The hypothesis is that informative interaction can improve the estimate, and that the improved estimate helps control when the policy is sensitive to its supplied weight.

## What is shared, and what changes

Use one learned update function shared across objects. Its inputs are the initial visual mass prior and the history of permitted observations and applied actions. Its output is an updated mass belief, ideally including uncertainty. The belief belongs to the current object encounter and resets for an unrelated new object; the update function's learned weights remain frozen during deployment.

The policy also stays frozen. It receives the belief's point estimate converted to weight, `estimated_mass × gravity`, through its existing weight input. Updating the belief from new evidence is the first experiment. Updating shared model weights across deployments is a separate, later lifelong-learning experiment.

## 1. Check that the controller can benefit before training an updater

Pin one policy checkpoint, controller, and simulator configuration. Fix cube geometry, friction, center of mass, damping, camera, and starting-state distribution. Vary only physical mass by changing density. In particular, disable any mass-dependent friction schedule for this experiment.

Begin with representative masses in the policy's supported range, such as 40, 100, 250, and 500 g, subject to qualification below. Use ten matched starting seeds per mass for an initial screening; this is a pilot, not a powered final evaluation.

Check both:

- At the same observation, does changing only supplied weight change the policy's movement or motor-limit outputs?
- Across matched rollouts, does true weight improve success, retention, or force use relative to an incorrect fixed estimate?

Retain conditions in which the true-weight policy can complete the task. If the policy ignores weight or true weight provides no useful advantage, do not start expensive updater training: establish a useful conditioned controller first, or report that this controller does not require better mass estimates for the selected task.

## 2. Establish whether the available interaction reveals mass

Use the same predefined probe for every condition: close the gripper, command a small lift, and briefly hold. Specify its opening, motor limits, movement, duration, and timing before collecting data. Keep the probe and total interaction budget identical across experimental conditions. If a probe drops the cube, retain that outcome in the data.

The current policy observations contain joint positions and velocities, hand and cube poses, goal/displacement information, a grasp flag, supplied weight, and two finger-compression measurements. Applied actions contain XYZ hand movement, gripper opening, and the per-finger motor force limit. A history makes object movement and tracking response available to an updater even though the current policy is feedforward.

**The two finger-force measurements are normal compression, not vertical object load.** A steady hold does not uniquely determine mass from these readings. Slip or binary failure alone generally provides a constraint involving mass, friction, and the action; it does not uniquely identify mass.

Inspect matched probe trajectories and test whether a small history-based predictor can distinguish masses on held-out starts above sensor noise and a constant-prior baseline. Check prediction on intermediate masses as well, after confirming the controller covers them. Prevent a constant per-mass environment index, trace ordering, filename, or seed assignment from identifying the label.

If the current signals are insufficient, revise the probe or add an informative measurement such as wrist force/torque. Reassess observability before training a more complex updater. Any added measurement must be available to the deployed updater and documented as a change to the sensing setup.

## 3. Collect the smallest useful updater dataset

Collect offline probe histories with:

- Initial image and visual prior; timestamped permitted observations and applied actions.
- Probe phase, contact/grasp events, and subsequent task outcomes.
- True mass as a supervised training label and separate evaluation reference.

Keep training, validation, and final test encounters separate. Hold out starts and noise realizations; include held-out mass values within the controller's verified operating range. Report that this tests inference across masses for one object type, rather than generalization to arbitrary objects or physical mechanisms.

Begin with a simple shared history-to-mass update function. Train it offline and freeze its weights before test deployment. Compare prior and posterior error and uncertainty calibration. Do not require it to infer an exact mass if the available evidence only supports a range.

## 4. Run three matched deployment conditions

For each test mass and starting seed, run:

| Condition | Weight input before the probe ends | Weight input during the remaining task |
|---|---|---|
| Fixed estimate | Initial visual estimate | Same initial estimate |
| Updated estimate | Initial visual estimate | Estimate revised from probe history |
| Oracle reference | Initial visual estimate | True weight |

All conditions execute exactly the same probe. Introduce the updated or oracle weight at the same time so the comparison isolates the estimate used for the remaining task. The oracle is an empirical reference for this frozen controller, not a guarantee of perfect performance. An additional true-weight-from-start run may qualify controller coverage but should be reported separately from this matched comparison.

For the first version, update once after the probe; repeated updates can follow after this comparison works. Reset the per-object belief between independent encounters. Use identical controller weights, probe, episode duration, noise settings, and evaluation criteria in all three conditions.

## Leakage boundary

True mass and other hidden simulator physics may supply training labels and evaluation reports. They must not enter the deployed updater, initial visual prior, probe selection, or policy observation, except in the explicitly labeled oracle condition. Replacing the supplied-weight observation must not change the object's actual physical mass.

The current controller uses simulator-provided object state, including cube pose. Keep that observation access consistent across conditions and state it explicitly; this experiment is not evidence for fully visual control. Do not expose additional physical readbacks to the updater under a generic label such as "state."

## Measurements and interpretation

Report mass error before and after the probe, task success, grasp loss/drop rate, measured finger compression during held contact, and requested motor limits. Use paired differences across the matched seeds and include variability. A requested motor limit is not the same quantity as measured contact force.

Evidence for the hypothesis requires both an improvement in the mass estimate and a useful control effect relative to the fixed-estimate condition. Better mass prediction without better task behavior is still an inference result, but it does not establish a benefit to this controller. A small fixed-to-oracle gap leaves little room for an updater to improve task performance.

The first decision is therefore: **does the policy benefit from accurate weight, and can the permitted probe observations reveal mass?** Only after both checks should updater training become the main investment.

## Relevant current implementation

- `robot_adaptation/runtime/deploy.py`: one initial RGB image, frozen estimator and policy, estimated weight supplied to the policy, currently fixed throughout an episode.
- `robot_adaptation/runtime/environment.py`: capture initial RGB and set the reported mass without changing physical mass.
- `robot_adaptation/runtime/policy.py`: frozen policy loading and estimated-weight observation injection.
- `robot_adaptation/simulation/collection_lift.py`: measured finger-compression observations.
- `robot_adaptation/policy/README.md`: observation/action definitions and limitations of current conditioning evidence.

No implementation, training run, or presentation change is part of this proposal.

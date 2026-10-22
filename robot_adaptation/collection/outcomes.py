"""Observable episode outcomes; these rules do not infer a failure's cause."""

from __future__ import annotations

import numpy as np


def classify_outcome(
    contact_any,
    grasped,
    clearance_m,
    success,
    lift_threshold_m: float = 0.02,
) -> dict:
    """Classify equally sized state timelines, including the initial state.

    ``clearance_m`` is the object's bottom-to-support clearance, not its
    center height. A lift requires a simultaneous grasp and clearance greater
    than or equal to ``lift_threshold_m``. Indices refer to the supplied state
    timeline, and are -1 if the corresponding event was never observed.

    Only the final success flag determines the ``success`` outcome. Earlier
    successful states remain available as ``success_any``. Failure modes are
    descriptive outcomes, never mass/friction/center-of-mass causal labels.
    """
    timelines = {
        "contact_any": np.asarray(contact_any, dtype=bool),
        "grasped": np.asarray(grasped, dtype=bool),
        "clearance_m": np.asarray(clearance_m, dtype=float),
        "success": np.asarray(success, dtype=bool),
    }
    for name, values in timelines.items():
        if values.ndim != 1:
            raise ValueError(f"{name} must be a one-dimensional state timeline")
        if values.size == 0:
            raise ValueError(f"{name} must contain at least one state")
    if len({values.shape for values in timelines.values()}) != 1:
        raise ValueError("all state timelines must have the same shape")
    if not np.isfinite(timelines["clearance_m"]).all():
        raise ValueError("clearance_m must contain only finite values")
    if not np.isfinite(lift_threshold_m) or lift_threshold_m <= 0:
        raise ValueError("lift_threshold_m must be a positive finite number")

    contact = timelines["contact_any"]
    grasp = timelines["grasped"]
    lift = grasp & (timelines["clearance_m"] >= lift_threshold_m)
    successful = timelines["success"]
    success_final = bool(successful[-1])

    if success_final:
        mode = "success"
    elif not contact.any():
        mode = "never_contacted"
    elif not grasp.any():
        mode = "contact_without_grasp"
    elif not lift.any():
        mode = "grasped_no_lift"
    elif not grasp[-1]:
        mode = "lifted_then_lost_grasp"
    else:
        mode = "goal_not_reached_or_not_static"

    def first_index(values: np.ndarray) -> int:
        indices = np.flatnonzero(values)
        return int(indices[0]) if indices.size else -1

    return {
        "success_final": success_final,
        "success_any": bool(successful.any()),
        "failure_mode": mode,
        "first_contact_state_index": first_index(contact),
        "first_grasp_state_index": first_index(grasp),
        "first_lift_state_index": first_index(lift),
        "failure_mode_source": "outcome_rules_v1",
        "failure_cause": "unknown",
    }

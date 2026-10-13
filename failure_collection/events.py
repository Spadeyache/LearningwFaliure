"""Sampled event descriptions, independent of the final task outcome.

These conservative rules describe motion; they do not identify its cause.
In particular, relative motion may be rolling/reseating, and a drop-like event
may include a deliberate release. Miss is decided at the collection horizon;
its physical onset is unknown and is therefore never assigned a fake time.
"""
from __future__ import annotations

import numpy as np
from scipy.spatial.transform import Rotation


def episode_events(data, *, slip_translation_m=0.005, slip_rotation_rad=0.15,
                   lift_threshold_m=0.02, drop_lost_states=3,
                   drop_descent_m=0.001):
    """Return scalar labels and state-aligned heuristic slip/drop event masks.

    Slip requires relative translation or rotation between two consecutive
    grasped samples after a grasped lift. Drop requires at least three lost
    grasp samples following lift, plus downward object motion from the last
    grasped sample. Drop onset and detection are recorded separately. All
    thresholds and the rule version accompany the labels in the NPZ.
    """
    if type(drop_lost_states) is not int or drop_lost_states < 2:
        raise ValueError("drop_lost_states must be an integer >= 2")
    thresholds = [slip_translation_m, slip_rotation_rad, lift_threshold_m, drop_descent_m]
    if not np.isfinite(thresholds).all() or np.any(np.asarray(thresholds) <= 0):
        raise ValueError("event thresholds must be positive and finite")
    times = np.asarray(data["meta__state_time_s"], dtype=float)
    grasp = np.asarray(data["sim__is_grasped"], dtype=bool)
    clearance = np.asarray(data["sim__object_clearance_m"], dtype=float)
    relative = np.asarray(data["input__object_pose_tcp_m_wxyz"], dtype=float)
    world = np.asarray(data["input__object_pose_world_m_wxyz"], dtype=float)
    count = len(times)
    if count == 0 or times.ndim != 1 or grasp.shape != (count,) or clearance.shape != (count,):
        raise ValueError("event state timelines must be nonempty and aligned")
    if relative.shape != (count, 7) or world.shape != (count, 7):
        raise ValueError("event pose timelines must have shape (state_count, 7)")
    if not all(np.isfinite(a).all() for a in (times, clearance, relative, world)) or np.any(np.diff(times) <= 0):
        raise ValueError("event observations must be finite with increasing timestamps")
    lifted = grasp & (clearance >= lift_threshold_m)
    ever_lifted = np.maximum.accumulate(lifted)
    translation = np.zeros(count)
    rotation = np.zeros(count)
    translation[1:] = np.linalg.norm(np.diff(relative[:, :3], axis=0), axis=-1)
    attitudes = Rotation.from_quat(relative[:, 3:], scalar_first=True)
    rotation[1:] = (attitudes[1:] * attitudes[:-1].inv()).magnitude()
    slip = np.zeros(count, dtype=bool)
    slip[1:] = (ever_lifted[1:] & grasp[1:] & grasp[:-1]
                & ((translation[1:] >= slip_translation_m) | (rotation[1:] >= slip_rotation_rad)))
    drop = np.zeros(count, dtype=bool)
    lost_start, last_grasp, first_drop_onset = None, None, None
    for index in range(count):
        if grasp[index]:
            last_grasp, lost_start = index, None
            continue
        if not ever_lifted[index] or last_grasp is None:
            continue
        if lost_start is None:
            lost_start = index
        descended = world[last_grasp, 2] - world[index, 2] >= drop_descent_m
        if index - lost_start + 1 >= drop_lost_states and descended:
            drop[index] = True
            if first_drop_onset is None:
                first_drop_onset = lost_start

    def first_time(mask):
        indices = np.flatnonzero(mask)
        return float(times[indices[0]]) if indices.size else float("nan")

    slip_time, drop_detection = first_time(slip), first_time(drop)
    drop_time = float(times[first_drop_onset]) if first_drop_onset is not None else float("nan")
    success = bool(np.asarray(data["label__success_final"]).item())
    if success:
        failure_type, failure_time, detection = "none", float("nan"), float("nan")
    elif drop.any():
        failure_type, failure_time, detection = "drop", drop_time, drop_detection
    elif slip.any():
        failure_type, failure_time, detection = "slip", slip_time, slip_time
    elif not grasp.any():
        failure_type, failure_time, detection = "miss", float("nan"), float(times[-1])
    else:
        failure_type = str(np.asarray(data["label__failure_mode"]).item())
        failure_time, detection = float("nan"), float(times[-1])
    values = {
        "sim__slip_event_mask": slip,
        "sim__drop_event_mask": drop,
        "label__slip_observed": bool(slip.any()),
        "label__drop_observed": bool(drop.any()),
        "label__first_slip_time_s": slip_time,
        "label__first_drop_time_s": drop_time,
        "label__drop_detection_time_s": drop_detection,
        "label__failure_type": failure_type,
        "label__failure_time_s": failure_time,
        "label__failure_detection_time_s": detection,
        "label__event_rule_version": "sampled_motion_events_v1",
        "label__event_rule_scope": "heuristic_motion_not_cause_or_intent",
        "label__slip_translation_threshold_m": slip_translation_m,
        "label__slip_rotation_threshold_rad": slip_rotation_rad,
        "label__event_lift_threshold_m": lift_threshold_m,
        "label__drop_lost_states": drop_lost_states,
        "label__drop_descent_threshold_m": drop_descent_m,
    }
    return {key: np.asarray(value) for key, value in values.items()}

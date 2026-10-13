"""NPZ validation, schema descriptors, and a strict input-only loader."""
import json
from pathlib import Path

import numpy as np

from . import SCHEMA_VERSION


INPUT_LAYOUTS = {}
for _timeline, _specs in {
    "state": {
        "object_pose_world_m_wxyz": (7,), "object_pose_tcp_m_wxyz": (7,),
        "tcp_pose_world_m_wxyz": (7,), "finger_pose_world_m_wxyz": (2, 7),
        "joint_position_rad_m": (9,), "joint_velocity_rad_m_s": (9,),
        "finger_width_m": (), "finger_width_velocity_m_s": (),
        "finger_net_force_world_n": (2, 3), "finger_force_valid": (),
        "object_tcp_distance_m": (), "finger_object_distance_m": (2,),
        "object_goal_distance_m": (),
    },
    "transition": {
        "action_raw": (4,), "action_applied": (4,), "tcp_target_pose_world_m_wxyz": (7,),
        "joint_target_rad_m": (9,), "finger_joint_target_m": (2,), "grip_motor_limit_n": (2,),
        "finger_force_mean_world_n": (2, 3), "finger_force_peak_norm_n": (2,),
        "finger_compression_mean_n": (2,), "finger_force_imbalance_n": (),
        "object_translation_response_world_m": (3,), "object_rotation_response_world_rotvec_rad": (3,),
        "relative_translation_response_tcp_m": (3,), "relative_rotation_response_tcp_rotvec_rad": (3,),
        "tcp_translation_response_world_m": (3,), "explicit_grip_point_world_m": (3,),
        "object_velocity_from_pose_world_m_s": (3,), "object_angular_velocity_from_pose_world_rad_s": (3,),
    },
    "physics": {
        "physics_finger_net_force_world_n": (2, 3), "physics_finger_net_force_local_n": (2, 3),
        "physics_object_pose_tcp_m_wxyz": (7,), "physics_object_pose_world_m_wxyz": (7,),
        "physics_tcp_pose_world_m_wxyz": (7,), "physics_finger_width_m": (),
    },
    "constant": {"goal_position_world_m": (3,), "reported_mass_kg": ()},
}.items():
    INPUT_LAYOUTS.update({"input__" + name: (_timeline, shape) for name, shape in _specs.items()})


def validate_episode(data):
    version = str(data["meta__schema_version"])
    if version not in (SCHEMA_VERSION, "pick_failure_v1", "pick_failure_v3"):
        raise ValueError("Unsupported episode schema")
    for key, value in data.items():
        value = np.asarray(value)
        if value.dtype.hasobject:
            raise ValueError(f"Pickle/object array forbidden: {key}")
        if key.startswith("input__") and key != "input__explicit_grip_point_world_m":
            if not np.isfinite(value).all():
                raise ValueError(f"Nonfinite sensor/command field: {key}")
    t = len(data["input__action_applied"])
    s = len(data["meta__physics_time_s"])
    unknown = {key for key in data if key.startswith("input__")} - set(INPUT_LAYOUTS)
    if unknown:
        raise ValueError(f"Unapproved classifier inputs: {sorted(unknown)}")
    lengths = {"state": (t + 1,), "transition": (t,), "physics": (s,), "constant": ()}
    for key, (timeline, shape) in INPUT_LAYOUTS.items():
        if version != "pick_failure_v3" and key in {"input__object_goal_distance_m", "input__reported_mass_kg"} and key not in data:
            continue
        if version == "pick_failure_v3" and key in {"input__action_raw", "input__action_applied"}:
            shape = (5,)
        if version == "pick_failure_v1" and key in {"input__object_tcp_distance_m", "input__finger_object_distance_m"}:
            continue
        if key not in data or data[key].shape != lengths[timeline] + shape:
            raise ValueError(f"Invalid or missing {timeline} field: {key}")
    action_count = 5 if version == "pick_failure_v3" else 4
    if data["input__action_applied"].shape != (t, action_count) or t < 1:
        raise ValueError("Invalid action count for episode schema")
    if np.abs(data["input__action_applied"]).max() > 1:
        raise ValueError("Actions outside normalized controller bounds")
    for key in ("input__object_pose_world_m_wxyz", "input__object_pose_tcp_m_wxyz", "input__tcp_pose_world_m_wxyz"):
        if data[key].shape != (t + 1, 7) or not np.allclose(np.linalg.norm(data[key][:, 3:], axis=1), 1, atol=1e-4):
            raise ValueError(f"Invalid state pose: {key}")
    offsets = data["sim__contact_point_offsets"]
    if offsets.shape != (s + 1,) or offsets[0] != 0 or (np.diff(offsets) < 0).any():
        raise ValueError("Invalid ragged contact offsets")
    if offsets[-1] != len(data["sim__contact_position_world_m"]):
        raise ValueError("Contact count disagrees with offsets")
    if bool(data["label__success_final"]) != bool(data["sim__task_success"][-1]):
        raise ValueError("Final success label disagrees with timeline")
    if "residual" in data:
        values = data["residual"]
        n = len(values)
        if values.ndim != 2 or not np.isfinite(values).all() or data["residual_channels"].shape != (values.shape[1],):
            raise ValueError("Invalid residual values/channels")
        if data["residual_valid_mask"].shape != (n,) or data["residual_source_valid_mask"].shape != (n, 2):
            raise ValueError("Invalid residual padding masks")
        if not np.array_equal(data["residual_valid_mask"], data["residual_source_valid_mask"].all(axis=1)):
            raise ValueError("Residual mask must exclude either padded source")
        if data["residual_time_s"].shape != (n,) or not np.all(np.diff(data["residual_time_s"]) > 0):
            raise ValueError("Invalid residual time alignment")
        if not str(data["matched_normal_run_id"]):
            raise ValueError("Residual needs matched normal identity")


def save_episode(path, data):
    """Compressed, pickle-free write, atomic rename, refuse completed overwrite."""
    validate_episode(data)
    path = Path(path)
    if path.exists():
        raise FileExistsError(path)
    temporary = path.with_suffix(".npz.tmp")
    try:
        with temporary.open("xb") as stream:
            np.savez_compressed(stream, **data)
        temporary.replace(path)
    finally:
        if temporary.exists():
            temporary.unlink()


def load_inputs(path, *, include_pose=True, include_force=True):
    """Return only available sensor/command candidates; never oracle metadata.

    These are IDEAL sensor proxies. Sensor suitability, filtering/noise and
    causal history windows must be chosen before training a deployed model.
    Disable pose or force families when the real robot lacks those sensors.
    Kinematic robot poses still require calibration and encoder forward kinematics.
    """
    with np.load(path, allow_pickle=False) as data:
        if str(data["meta__schema_version"]) not in (SCHEMA_VERSION, "pick_failure_v1", "pick_failure_v3"):
            raise ValueError("Unsupported episode schema")
        return {key: data[key].copy() for key in data.files
                if key in INPUT_LAYOUTS and "explicit_grip_point" not in key
                and (include_pose or ("object_" not in key and "relative_" not in key))
                and (include_force or ("force" not in key and "compression" not in key and "imbalance" not in key))}


def describe(data):
    """Machine-readable inventory; exact shapes are from the first episode."""
    fields = {}
    for key, value in sorted(data.items()):
        value = np.asarray(value)
        fields[key] = {"dtype": str(value.dtype), "example_shape": list(value.shape),
                       "group": key.split("__", 1)[0]}
        if key in INPUT_LAYOUTS:
            fields[key]["timeline"] = INPUT_LAYOUTS[key][0]
    return {
        "schema_version": str(data["meta__schema_version"]),
        "layout": {"state": "T+1 rows at t=0..T/control_hz", "action_response": "T rows: action[t] causes state[t+1]-state[t]",
                   "physics": "T*K rows at dt..T/control_hz; K=sim_hz/control_hz",
                   "contacts": "ragged points: offsets[j]:offsets[j+1] belongs to physics sample j"},
        "units": "SI: metres, seconds, kilograms, newtons, N*s, radians; quaternions [w,x,y,z]; joint arrays first 7 rad, final 2 m",
        "frames": "world and TCP (panda_hand_tcp); relative object pose = inverse(T_world_tcp) @ T_world_object",
        "input_provenance": "Ideal zero-noise simulator pose/force sensor proxies, encoder states and known commands; no perception/tactile estimator is implemented",
        "force_semantics": "Total force ON each finger (left,right) from ALL contacts. World or finger-link frame. Physics force=impulse/dt; interval mean averages K samples, peak is max sample norm; compression projects finger-local +/-y, not a surface-normal oracle",
        "relative_response_semantics": "Difference of object coordinates in successive moving TCP frames; useful slip proxy, not an inertial velocity",
        "residual_semantics": "Post-action shifted minus matched normal; shortest relative rotation vectors replace quaternion subtraction. Last-value padding has false source/intersection masks. Exact object-pair force channels are sim-attributed, excluded from load_inputs. Channel names specify units; residuals.py defines transforms.",
        "rotation_response_semantics": "Shortest rotation vector for R_next @ inverse(R_previous), in the indicated coordinate representation",
        "missing": "Explicit grip point is NaN and availability false: policy has no such output. First-contact time is NaN if never contacted. Reset forces zero with validity false",
        "success": "Stock PickCube: geometric origin within .025m goal and all arm |qvel|<=.2rad/s. Final and any-time success distinct; held-goal flag separately available",
        "classifier_rule": "Use load_inputs only; sim__, label__, meta__ and privileged policy observation excluded. Contact masks depend on oracle object attribution; do not use them as deployment features",
        "fields": fields,
    }

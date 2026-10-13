"""Matched-run gap signatures, aligned by control timestep after each action.

Translations, widths and forces are ``shifted - normal`` in SI units. Orientation
gaps use the shortest rotation vector ``log(R_shifted @ inverse(R_normal))`` in
radians, rather than subtracting quaternion components. The result is invariant
to quaternion sign; as with any shortest rotation vector, the axis is ambiguous
at exactly pi. Relative pose coordinates are expressed in each run's TCP frame.

Force channels are the mean force ON each finger from the object during that
action, averaged over its physics samples. These exact pair forces use simulator
body attribution: the atlas is a simulation diagnostic, not automatically a
deployment feature set. No physical-property or outcome labels enter its values.
Reset poses are used to verify matching, but reset samples (whose force is not
valid) do not enter the residual. Short trajectories repeat their final sample;
the corresponding source and intersection masks are false for padded rows.
"""

import numpy as np
from scipy.spatial.transform import Rotation


RESIDUAL_CHANNELS = np.asarray(
    [f"object_relative_position_tcp_{axis}_m" for axis in "xyz"]
    + [f"object_relative_rotation_tcp_{axis}_rad" for axis in "xyz"]
    + [f"object_position_world_{axis}_m" for axis in "xyz"]
    + [f"object_rotation_world_{axis}_rad" for axis in "xyz"]
    + ["gripper_width_m"]
    + [f"{finger}_contact_force_world_{axis}_n" for finger in ("left", "right") for axis in "xyz"]
)


def _scalar(data, key):
    value = np.asarray(data[key])
    if value.shape != ():
        raise ValueError(f"Expected scalar {key}")
    return value.item()


def _finite(data, key, shape):
    value = np.asarray(data[key], dtype=np.float64)
    if value.shape != shape or not np.isfinite(value).all():
        raise ValueError(f"Invalid residual source field: {key}; expected finite {shape}")
    return value


def _pose(data, key, count):
    value = _finite(data, key, (count, 7))
    if not np.allclose(np.linalg.norm(value[:, 3:], axis=1), 1, atol=1e-4, rtol=0):
        raise ValueError(f"Invalid quaternion in {key}")
    return value


def _same_pose(left, right, key):
    left, right = np.asarray(left), np.asarray(right)
    rotations = Rotation.from_quat(np.stack((left[3:], right[3:])), scalar_first=True)
    angle = (rotations[0] * rotations[1].inv()).magnitude()
    if not np.allclose(left[:3], right[:3], atol=1e-6, rtol=0) or angle > 1e-6:
        raise ValueError(f"Matched runs have different initial {key}")


def _trajectory(data):
    """Validate control/physics alignment and return only the feature channels."""
    control_hz = float(_scalar(data, "meta__control_frequency_hz"))
    simulation_hz = float(_scalar(data, "meta__simulation_frequency_hz"))
    if not np.isfinite([control_hz, simulation_hz]).all() or min(control_hz, simulation_hz) <= 0:
        raise ValueError("Residual frequencies must be positive and finite")
    ratio = simulation_hz / control_hz
    if not np.isclose(ratio, round(ratio), rtol=0, atol=1e-9) or ratio < 1:
        raise ValueError("Simulation frequency must be a multiple of control frequency")
    count = len(data["input__action_applied"])
    if count < 1:
        raise ValueError("Residual requires at least one completed action per run")
    state_time = _finite(data, "meta__state_time_s", (count + 1,))
    if not np.allclose(state_time, np.arange(count + 1) / control_hz, rtol=0, atol=1e-9):
        raise ValueError("State times must align with the control timestep from reset")
    physical_count = count * int(round(ratio))
    indices = np.asarray(data["meta__physics_action_index"])
    expected_indices = np.repeat(np.arange(count), int(round(ratio)))
    if indices.dtype.kind not in "iu" or not np.array_equal(indices, expected_indices):
        raise ValueError("Physics samples must cover each action in timestep order")
    physical_time = _finite(data, "meta__physics_time_s", (physical_count,))
    if not np.allclose(physical_time, np.arange(1, physical_count + 1) / simulation_hz, rtol=0, atol=1e-9):
        raise ValueError("Physics times must align with the simulation timestep")
    pair_force = _finite(data, "sim__physics_object_pair_force_world_n", (physical_count, 2, 3))
    mean_force = pair_force.reshape(count, int(round(ratio)), 2, 3).mean(axis=1)
    force_valid = np.asarray(data["input__finger_force_valid"])
    if force_valid.shape != (count + 1,) or force_valid.dtype.kind != "b":
        raise ValueError("Expected a boolean state force validity mask")
    return {
        "count": count,
        "control_hz": control_hz,
        "simulation_hz": simulation_hz,
        "relative_pose": _pose(data, "input__object_pose_tcp_m_wxyz", count + 1),
        "world_pose": _pose(data, "input__object_pose_world_m_wxyz", count + 1),
        "tcp_pose": _pose(data, "input__tcp_pose_world_m_wxyz", count + 1),
        "joint_position": _finite(data, "input__joint_position_rad_m", (count + 1, 9)),
        "joint_velocity": _finite(data, "input__joint_velocity_rad_m_s", (count + 1, 9)),
        "width": _finite(data, "input__finger_width_m", (count + 1,))[1:],
        "force": mean_force.reshape(count, 6),
        "valid": force_valid[1:],
    }


def _validate_match(shifted, normal, shifted_trajectory, normal_trajectory):
    if _scalar(shifted, "label__seed") != _scalar(normal, "label__seed"):
        raise ValueError("Matched runs must have the same seed")
    for key in ("control_hz", "simulation_hz"):
        if shifted_trajectory[key] != normal_trajectory[key]:
            raise ValueError(f"Matched runs must have the same {key}")
    for key in ("world_pose", "relative_pose", "tcp_pose"):
        _same_pose(shifted_trajectory[key][0], normal_trajectory[key][0], key)
    for key in ("joint_position", "joint_velocity"):
        if not np.allclose(shifted_trajectory[key][0], normal_trajectory[key][0], atol=1e-6, rtol=0):
            raise ValueError(f"Matched runs have different initial {key}")
    shifted_goal = _finite(shifted, "input__goal_position_world_m", (3,))
    normal_goal = _finite(normal, "input__goal_position_world_m", (3,))
    if not np.allclose(shifted_goal, normal_goal, atol=1e-6, rtol=0):
        raise ValueError("Matched runs must have the same goal")
    # These values only guard matching; none are appended to the feature vector.
    for data, trajectory in ((shifted, shifted_trajectory), (normal, normal_trajectory)):
        initial_pose = _finite(data, "label__initial_object_pose_world_m_wxyz", (7,))
        _same_pose(initial_pose, trajectory["world_pose"][0], "recorded object reset pose")


def _pad_last(values, count):
    return np.concatenate((values, np.repeat(values[-1:], count - len(values), axis=0)), axis=0)


def _pose_gap(shifted, normal):
    shifted_rotation = Rotation.from_quat(shifted[:, 3:], scalar_first=True)
    normal_rotation = Rotation.from_quat(normal[:, 3:], scalar_first=True)
    rotation_gap = (shifted_rotation * normal_rotation.inv()).as_rotvec()
    return np.concatenate((shifted[:, :3] - normal[:, :3], rotation_gap), axis=1)


def build_residual(shifted, normal):
    """Return pickle-free NPZ fields for a shifted run and its matched baseline.

    Inputs are episode dictionaries or open ``np.load(..., allow_pickle=False)``
    archives. ``normal['meta__episode_id']`` identifies the exact reference run.
    ``residual_source_valid_mask[:, 0]`` corresponds to shifted, column 1 to
    normal. Consumers must exclude false rows of ``residual_valid_mask`` when
    fitting or plotting; padded values are stored only to keep arrays aligned.
    """
    reference_id = _scalar(normal, "meta__episode_id")
    if not isinstance(reference_id, str) or not reference_id.strip():
        raise ValueError("Matched normal run must have a nonempty meta__episode_id")
    shifted_trajectory, normal_trajectory = _trajectory(shifted), _trajectory(normal)
    _validate_match(shifted, normal, shifted_trajectory, normal_trajectory)
    count = max(shifted_trajectory["count"], normal_trajectory["count"])
    padded = []
    source_valid = np.zeros((count, 2), dtype=bool)
    for column, trajectory in enumerate((shifted_trajectory, normal_trajectory)):
        padded.append({
            "relative_pose": _pad_last(trajectory["relative_pose"][1:], count),
            "world_pose": _pad_last(trajectory["world_pose"][1:], count),
            "width": _pad_last(trajectory["width"], count),
            "force": _pad_last(trajectory["force"], count),
        })
        source_valid[:trajectory["count"], column] = trajectory["valid"]
    shifted_features, normal_features = padded
    residual = np.column_stack((
        _pose_gap(shifted_features["relative_pose"], normal_features["relative_pose"]),
        _pose_gap(shifted_features["world_pose"], normal_features["world_pose"]),
        shifted_features["width"] - normal_features["width"],
        shifted_features["force"] - normal_features["force"],
    )).astype(np.float32)
    return {
        "residual": residual,
        "residual_channels": RESIDUAL_CHANNELS.copy(),
        "residual_time_s": np.arange(1, count + 1, dtype=np.float64) / shifted_trajectory["control_hz"],
        "residual_source_valid_mask": source_valid,
        "residual_valid_mask": source_valid.all(axis=1),
        "matched_normal_run_id": np.asarray(reference_id),
    }

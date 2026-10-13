"""Controlled full-episode retries from the same reset, not online rescue.

A higher drive-force limit is only a changed actuator constraint. Measured
contact force must actually increase before calling it a force intervention.
"""
from __future__ import annotations

from contextlib import contextmanager
from copy import deepcopy
import json

import numpy as np


def _numpy(value):
    if hasattr(value, "detach"):
        value = value.detach().cpu().numpy()
    return np.asarray(value)


def normalize_recovery(config=None):
    """Validate a recovery mapping; disabled by default, retries cost extra.

    Accepted corrections are ``{kind: slow_lift, factor: .75/.5}`` and
    ``{kind: grip_limit, factor: 1.5/2}``. Arbitrary grasp offsets are rejected
    because they require an explicit approach-stage policy interface.
    """
    config = deepcopy({} if config is None else config)
    if not isinstance(config, dict) or set(config) - {"enabled", "corrections", "max_grip_limit_n"}:
        raise ValueError("recovery accepts enabled, corrections, max_grip_limit_n")
    config.setdefault("enabled", False)
    config.setdefault("max_grip_limit_n", 100.0)
    config.setdefault("corrections", [
        {"kind": "slow_lift", "factor": .75},
        {"kind": "slow_lift", "factor": .5},
        {"kind": "grip_limit", "factor": 1.5},
        {"kind": "grip_limit", "factor": 2.0},
    ])
    if type(config["enabled"]) is not bool:
        raise ValueError("recovery.enabled must be a boolean")
    maximum = float(config["max_grip_limit_n"])
    if not np.isfinite(maximum) or maximum <= 0:
        raise ValueError("recovery.max_grip_limit_n must be positive and finite")
    config["max_grip_limit_n"] = maximum
    corrections = config["corrections"]
    if not isinstance(corrections, list):
        raise ValueError("recovery.corrections must be a list")
    seen = set()
    for correction in corrections:
        if not isinstance(correction, dict) or set(correction) - {"kind", "factor", "max_grip_limit_n"}:
            raise ValueError("each correction requires kind and factor")
        kind, factor = correction.get("kind"), float(correction.get("factor", np.nan))
        if not np.isfinite(factor) or not ((kind == "slow_lift" and 0 < factor < 1)
                                         or (kind == "grip_limit" and factor > 1)):
            raise ValueError("slow_lift requires 0 < factor < 1; grip_limit requires factor > 1")
        if (kind, factor) in seen:
            raise ValueError("duplicate recovery correction")
        seen.add((kind, factor))
        correction["factor"] = factor
        correction["max_grip_limit_n"] = maximum
    return config


def recovery_capability(env, spec):
    """Read capabilities/headroom without changing the environment."""
    if spec["kind"] == "slow_lift":
        arm = env.agent.controller.controllers["arm"]
        supported = bool(getattr(arm.config, "use_delta", False)) and hasattr(env.agent, "is_grasping")
        return {"supported": supported, "reason": "supported" if supported else "requires_delta_position_and_grasp_query"}
    if spec["kind"] != "grip_limit":
        return {"supported": False, "reason": "unsupported_correction"}
    gripper = env.agent.controller.controllers["gripper"]
    limits = _numpy(gripper.config.force_limit).astype(float)
    if limits.size == 0 or not np.isfinite(limits).all() or not np.allclose(limits, limits.flat[0]):
        return {"supported": False, "reason": "requires_uniform_finite_finger_limits"}
    baseline = float(limits.flat[0])
    target = min(baseline * float(spec["factor"]), float(spec.get("max_grip_limit_n", 100.0)))
    result = {"baseline_limit_n": baseline, "requested_limit_n": baseline * float(spec["factor"]),
              "applied_limit_n": target}
    if target <= baseline + 1e-8:
        return {**result, "supported": False, "reason": "no_motor_limit_headroom"}
    supported = (hasattr(gripper, "set_drive_property") and bool(getattr(gripper, "joints", []))
                 and all(hasattr(joint, "get_force_limit") for joint in gripper.joints)
                 and not hasattr(gripper, "force_limit_n"))
    return {**result, "supported": supported,
            "reason": "supported" if supported else "requires_static_limit_controller_and_readback"}


@contextmanager
def correction_context(env, spec):
    """Apply a supported actuator correction and restore its original limit.

    Wrap the whole reset/rollout in this context. A controller reset retains its
    configured drive limit. The gripper readback is checked before yielding.
    """
    if spec is None:
        yield {"supported": True, "reason": "no_correction"}
        return
    capability = recovery_capability(env, spec)
    if not capability["supported"]:
        raise ValueError(f"Unsupported recovery: {capability['reason']}")
    if spec["kind"] == "slow_lift":
        yield capability
        return
    gripper = env.agent.controller.controllers["gripper"]
    original = deepcopy(gripper.config.force_limit)
    try:
        gripper.config.force_limit = capability["applied_limit_n"]
        gripper.set_drive_property()
        for joint in gripper.joints:
            if not np.allclose(_numpy(joint.get_force_limit()), capability["applied_limit_n"]):
                raise RuntimeError("Gripper drive-limit readback disagrees with requested correction")
        yield capability
    finally:
        gripper.config.force_limit = original
        gripper.set_drive_property()


def apply_correction(raw, env, spec):
    """Copy the policy command; scale upward Z only while currently grasping.

    Keep raw and applied commands separately in the recorder. This changes the
    ascent command, not the policy weights or descent/opening commands.
    """
    action = raw.clone() if hasattr(raw, "clone") else np.array(raw, copy=True)
    if spec is None or spec["kind"] == "grip_limit":
        return action
    if spec["kind"] != "slow_lift" or action.shape[-1] != 4:
        raise ValueError("slow_lift requires the four-action delta-position pick controller")
    # A reset teleports bodies without refreshing PhysX's contact cache.
    grasping = (not getattr(env, "_contacts_stale", False)
                and bool(_numpy(env.agent.is_grasping(env.cube)).item()))
    if grasping and float(_numpy(action[..., 2]).item()) > 0:
        action[..., 2] *= float(spec["factor"])
    return action


def _contact_force_mean(data):
    for key in ("sim__object_pair_force_mean_world_n", "sim__physics_object_pair_force_world_n"):
        if key in data:
            forces = np.linalg.norm(np.asarray(data[key], dtype=float), axis=-1).sum(axis=-1)
            contact = forces > float(np.asarray(data.get("meta__contact_threshold_n", .05)))
            return float(forces[contact].mean()) if contact.any() else 0.0
    return float("nan")


def _ascent_speed(data):
    pose = np.asarray(data["input__tcp_pose_world_m_wxyz"], dtype=float)
    times = np.asarray(data["meta__state_time_s"], dtype=float)
    speed = np.diff(pose[:, 2]) / np.diff(times)
    grasp = np.asarray(data["sim__is_grasped"], dtype=bool)
    ascent = (speed > 0) & grasp[:-1]
    return float(speed[ascent].mean()) if ascent.any() else 0.0


def recovery_result(parent, retry, spec):
    """Measured matched-retry result; a tested correction is not a cause label.

    Collector must first validate same seed/reset/properties and record the
    parent episode ID. This result deliberately does not infer an untested
    minimum correction or count a higher cap alone as higher contact force.
    """
    parent_force, retry_force = _contact_force_mean(parent), _contact_force_mean(retry)
    parent_speed, retry_speed = _ascent_speed(parent), _ascent_speed(retry)
    force_delta = retry_force - parent_force
    if spec["kind"] == "grip_limit":
        effect = bool(np.isfinite(force_delta) and force_delta > max(.05, .05 * parent_force))
    else:
        actions = np.asarray(retry["input__action_applied"])
        raw = np.clip(np.asarray(retry["input__action_raw"]), -1, 1)
        effect = bool(np.any((raw[:, 2] > 0) & (actions[:, 2] < raw[:, 2] - 1e-7)))
    parent_success = bool(np.asarray(parent["label__success_final"]).item())
    retry_success = bool(np.asarray(retry["label__success_final"]).item())
    result = {
        "meta__recovery_protocol": "full_episode_matched_reset_retry",
        "meta__recovery_correction_json": json.dumps(spec, sort_keys=True),
        "label__recovery_kind": spec["kind"],
        "label__recovery_factor": float(spec["factor"]),
        "label__recovery_parent_success": parent_success,
        "label__recovery_retry_success": retry_success,
        "label__recovery_effect_observed": effect,
        "label__recovery_recovered": not parent_success and retry_success and effect,
        "label__recovery_parent_contact_force_mean_n": parent_force,
        "label__recovery_retry_contact_force_mean_n": retry_force,
        "label__recovery_contact_force_delta_n": force_delta,
        "label__recovery_parent_ascent_speed_m_s": parent_speed,
        "label__recovery_retry_ascent_speed_m_s": retry_speed,
        "label__recovery_ascent_speed_delta_m_s": retry_speed - parent_speed,
        "label__recovery_causal_interpretation": "matched_retry_association_not_unique_cause",
    }
    return {key: np.asarray(value) for key, value in result.items()}

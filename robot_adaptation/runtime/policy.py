"""Frozen CPU policy loading and estimated-mass observation injection.

This adapter accepts only completed 45-input, five-action v1/v2 checkpoints.
It never converts older architectures, downloads weights, or starts training.
"""
from __future__ import annotations

import json
import math
from numbers import Real
from pathlib import Path
import pickle
from typing import Any

import torch
from torch import nn

from robot_adaptation.paths import ROOT
from robot_adaptation.simulation.training_lift import (
    ACTION_DESCRIPTION,
    INPUT_FIELDS,
    INPUT_SIZES,
    ORIGIN,
    WEIGHT_INPUT_INDEX as _TASK_WEIGHT_INDEX,
)


WEIGHT_INPUT_INDEX = 42
V1_ARCHITECTURE = "frozen_movement_independent_strength_v1"
V2_ARCHITECTURE = "independent_movement_strength_v2"
SUPPORTED_ARCHITECTURES = (V1_ARCHITECTURE, V2_ARCHITECTURE)

if (
    _TASK_WEIGHT_INDEX != WEIGHT_INPUT_INDEX
    or sum(INPUT_SIZES) != 45
    or sum(INPUT_SIZES[:INPUT_FIELDS.index("object_weight_n")]) != WEIGHT_INPUT_INDEX
):
    raise RuntimeError("The supplied-weight policy input layout changed; update the runtime adapter.")


def _positive_scalar(value: Any, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, Real):
        raise ValueError(f"{name} must be a finite positive scalar.")
    value = float(value)
    if not math.isfinite(value) or value <= 0:
        raise ValueError(f"{name} must be a finite positive scalar.")
    return value


def policy_grip_limits(manifest: dict[str, Any]) -> tuple[float, float]:
    """Read validated per-finger force limits in newtons from policy settings."""
    settings = manifest.get("settings")
    if not isinstance(settings, dict):
        raise ValueError("The policy manifest must include its settings object.")
    limits = settings.get("grip_force_limits_n")
    if not isinstance(limits, (list, tuple)) or len(limits) != 2:
        raise ValueError("Policy settings must specify two grip_force_limits_n values.")
    low = _positive_scalar(limits[0], "minimum grip force")
    high = _positive_scalar(limits[1], "maximum grip force")
    if low >= high:
        raise ValueError("Policy grip force limits must be ordered: 0 < minimum < maximum.")
    return low, high


def validate_policy_manifest(manifest: Any) -> dict[str, Any]:
    """Reject incomplete, unsupported, or ambiguous policy interfaces."""
    if not isinstance(manifest, dict):
        raise ValueError("The policy manifest must be a JSON object.")
    if manifest.get("status") != "complete":
        raise ValueError("Runtime requires a fully completed policy run.")
    if type(manifest.get("observations")) is not int or manifest["observations"] != 45:
        raise ValueError("Runtime requires exactly 45 policy observations.")
    if type(manifest.get("actions")) is not int or manifest["actions"] != 5:
        raise ValueError("Runtime requires exactly five policy actions.")
    architecture = manifest.get("policy_architecture")
    if architecture not in SUPPORTED_ARCHITECTURES:
        raise ValueError("Only exact independent-strength v1 and v2 policies are supported.")
    if manifest.get("artifact_origin") != ORIGIN:
        raise ValueError("Unsupported policy artifact origin.")
    if manifest.get("input_fields") != INPUT_FIELDS or manifest.get("input_sizes") != INPUT_SIZES:
        raise ValueError("The policy manifest does not match the expected 45-input observation schema.")
    if manifest.get("action_description") != ACTION_DESCRIPTION:
        raise ValueError("The policy uses an unsupported action layout.")
    if architecture == V2_ARCHITECTURE and manifest.get("optimization_mode") not in ("joint", "strength_only"):
        raise ValueError("A v2 policy must specify its joint or strength_only optimization mode.")
    policy_grip_limits(manifest)
    if manifest["settings"].get("control_mode") != "pd_ee_delta_pos":
        raise ValueError("Runtime requires the policy's native pd_ee_delta_pos controller.")
    return manifest


def _load_one(checkpoint: Path) -> tuple[nn.Module, dict[str, Any], Path]:
    checkpoint = checkpoint.expanduser().resolve()
    if not checkpoint.is_file():
        raise FileNotFoundError(f"Policy checkpoint does not exist: {checkpoint}")
    with checkpoint.with_name("manifest.json").open(encoding="utf-8") as handle:
        manifest = validate_policy_manifest(json.load(handle))
    if manifest["policy_architecture"] == V1_ARCHITECTURE:
        from robot_adaptation.policy.frozen_v1 import load_agent

        agent, loaded_manifest = load_agent(checkpoint)
    else:
        from robot_adaptation.policy.model import POLICY_ARCHITECTURE
        from robot_adaptation.policy.train import load_checkpoint

        if POLICY_ARCHITECTURE != V2_ARCHITECTURE:
            raise ValueError("The installed current-policy implementation no longer matches runtime v2.")
        agent, loaded_manifest = load_checkpoint(checkpoint)
        # The training loader supports warm-start conversion. Runtime inference
        # forbids that conversion: every tensor must already match this model.
        state = torch.load(checkpoint, map_location="cpu", weights_only=True)
        if not isinstance(state, dict) or not all(isinstance(value, torch.Tensor) for value in state.values()):
            raise ValueError("Runtime policy checkpoints must contain model tensors only.")
        agent.load_state_dict(state, strict=True)
    if loaded_manifest != manifest:
        raise ValueError("The policy manifest changed while the checkpoint was being loaded.")
    agent.to(device="cpu", dtype=torch.float32).eval().requires_grad_(False)
    if any(not torch.isfinite(parameter).all().item() for parameter in agent.parameters()):
        raise ValueError("The policy checkpoint contains nonfinite model parameters.")
    return agent, manifest, checkpoint


def load_policy(
    checkpoint: str | Path | None = None,
) -> tuple[nn.Module, dict[str, Any], Path]:
    """Load a specified policy, or the latest usable completed main-policy run.

    Default lookup checks final_ckpt.pt in both the new runs/policy directory
    and historical runs/learning. Incomplete, legacy 43-input, malformed, and
    incompatible candidates are skipped; explicit paths fail with their error.
    """
    if checkpoint is not None:
        return _load_one(Path(checkpoint))
    candidates = [
        path
        for folder in (ROOT / "runs" / "policy", ROOT / "runs" / "learning")
        for path in folder.glob("*/final_ckpt.pt")
        if path.is_file()
    ]
    candidates.sort(key=lambda path: path.stat().st_mtime_ns, reverse=True)
    skipped = 0
    for path in candidates:
        try:
            return _load_one(path)
        except (OSError, ValueError, RuntimeError, TypeError, KeyError, EOFError, pickle.UnpicklingError):
            skipped += 1
    raise FileNotFoundError(
        "No usable completed 45-input/five-action v1 or v2 policy found in "
        f"runs/policy or runs/learning ({skipped} incompatible candidates skipped). "
        "Provide an explicit completed policy checkpoint."
    )


def inject_mass_estimate(
    observation: torch.Tensor,
    mass_kg: float,
    gravity_m_s2: float,
) -> torch.Tensor:
    """Clone one observation and replace only its supplied weight (newtons).

    Mass and gravity are positive scalar magnitudes. The returned observation
    uses float32 on the input device; the original observation is untouched.
    """
    if not isinstance(observation, torch.Tensor) or tuple(observation.shape) != (1, 45):
        raise ValueError("Mass injection expects a torch observation with shape (1, 45).")
    if not observation.is_floating_point():
        raise ValueError("Policy observations must contain floating-point values.")
    mass = _positive_scalar(mass_kg, "estimated mass_kg")
    gravity = _positive_scalar(gravity_m_s2, "gravity_m_s2 magnitude")
    weight = mass * gravity
    if not math.isfinite(weight) or weight > torch.finfo(torch.float32).max:
        raise ValueError("Estimated weight must be finite and representable as float32.")
    supplied = observation.detach().to(dtype=torch.float32).clone()
    if not torch.isfinite(supplied).all().item():
        raise ValueError("Policy observations must contain finite values.")
    # Match the environment's float32 multiply exactly, including the first
    # action; converting a double-precision product can differ by one ULP.
    supplied[0, WEIGHT_INPUT_INDEX] = (
        torch.as_tensor(mass, dtype=torch.float32, device=supplied.device)
        * torch.as_tensor(gravity, dtype=torch.float32, device=supplied.device)
    )
    if supplied[0, WEIGHT_INPUT_INDEX].item() <= 0:
        raise ValueError("Estimated weight is too small to remain positive in float32.")
    return supplied

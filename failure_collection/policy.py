"""Frozen, hash-verified official ManiSkill PickCube state policy.

This loader does not train, download, or change a checkpoint.  Its state input
contains simulator object pose and goal information; that policy input is not
the classifier's deployment-measurable feature vector.
"""
from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

import torch
from torch import nn


DATASET = "haosulab/ManiSkill_Demonstrations"
REVISION = "d674485bbffdd533914e52d272fdda34c0515608"
CONTROL_MODE = "pd_ee_delta_pos"
CHECKPOINT_NAME = "ppo_pd_ee_delta_pos_ckpt.pt"
CHECKPOINT_SHA256 = "0b17b5ed9690ccf83111d0f09af8d1599f69ee7ba0077e1aac48814ac78ce99c"
CHECKPOINT_URL = (
    f"https://huggingface.co/datasets/{DATASET}/resolve/{REVISION}/"
    f"demos/PickCube-v1/rl/{CHECKPOINT_NAME}"
)
DEFAULT_CHECKPOINT = (
    Path(__file__).resolve().parents[1]
    / "runs" / "maniskill_pretrained" / "pick_cube" / "models"
    / REVISION / CHECKPOINT_NAME
)


def _network(outputs: int) -> nn.Sequential:
    return nn.Sequential(
        nn.Linear(42, 256), nn.Tanh(),
        nn.Linear(256, 256), nn.Tanh(),
        nn.Linear(256, 256), nn.Tanh(),
        nn.Linear(256, outputs),
    )


class PickPolicy(nn.Module):
    """Exact 42-input, four-action architecture of the published PPO model.

    Calling the model returns the deterministic, *unclipped* actor mean.
    Log it and apply ``raw_action.clamp(-1, 1)`` to the native controller.
    The critic and exploration parameter are retained so strict checkpoint
    loading verifies the complete saved architecture; inference uses neither.
    """

    def __init__(self) -> None:
        super().__init__()
        self.critic = _network(1)
        self.actor_mean = _network(4)
        self.actor_logstd = nn.Parameter(torch.zeros(1, 4))

    @torch.no_grad()
    def forward(self, observation: torch.Tensor) -> torch.Tensor:
        if not isinstance(observation, torch.Tensor):
            raise TypeError("Policy observation must be a torch Tensor")
        if observation.ndim != 2 or observation.shape[1] != 42:
            raise ValueError("Official PickCube policy requires a batch of 42 state inputs")
        if not torch.isfinite(observation).all():
            raise ValueError("Policy observation contains a nonfinite value")
        result = self.actor_mean(observation.to(device="cpu", dtype=torch.float32))
        if not torch.isfinite(result).all():
            raise ValueError("Policy produced a nonfinite action")
        return result


def load_policy(path: str | Path | None = None) -> tuple[PickPolicy, dict[str, Any]]:
    """Load the cached official policy, checking its bytes and full state dict.

    ``path`` permits a relocated copy of the same published checkpoint.  Other
    models (including the workspace's 45-input/five-action learned strength
    models) are intentionally rejected, so collection always has one fixed
    policy and control mapping.  No network request is made.
    """
    checkpoint = (DEFAULT_CHECKPOINT if path is None else Path(path)).expanduser().resolve()
    if not checkpoint.is_file():
        raise FileNotFoundError(
            f"Official PickCube checkpoint is absent: {checkpoint}. "
            f"Provide a cached copy of {CHECKPOINT_NAME} with SHA256 {CHECKPOINT_SHA256}."
        )
    digest = hashlib.sha256(checkpoint.read_bytes()).hexdigest()
    if digest != CHECKPOINT_SHA256:
        raise ValueError(
            "Checkpoint SHA256 mismatch: this collector requires the pinned "
            f"official 42-input/four-action PickCube policy; got {digest}"
        )
    state = torch.load(checkpoint, map_location="cpu", weights_only=True)
    if not isinstance(state, dict) or any(
        not isinstance(value, torch.Tensor) or not torch.isfinite(value).all()
        for value in state.values()
    ):
        raise ValueError("Checkpoint must contain only finite model-weight tensors")
    model = PickPolicy()
    model.load_state_dict(state, strict=True)
    model.eval()
    model.requires_grad_(False)
    metadata: dict[str, Any] = {
        "checkpoint_path": str(checkpoint),
        "checkpoint_sha256": digest,
        "checkpoint_url": CHECKPOINT_URL,
        "artifact_origin": "official_maniskill_pretrained_ppo",
        "dataset": DATASET,
        "dataset_revision": REVISION,
        "training_environment": "PickCube-v1",
        "training_sim_backend": "physx_cuda",
        "training_observation_mode": "state",
        "training_observation_privilege": (
            "42 simulator-state values include exact cube pose, TCP pose, "
            "joint positions/velocities, goal and relative positions, and "
            "simulator-derived grasp status; do not use this vector as a "
            "deployment-measurable classifier input."
        ),
        "control_mode": CONTROL_MODE,
        "observation_size": 42,
        "action_size": 4,
        "action_description": ["delta_x", "delta_y", "delta_z", "finger_opening"],
        "action_application": "Deterministic actor mean clipped elementwise to [-1, 1]",
        "published_episode_horizon": 50,
        "inference_device": "cpu",
        "deterministic": True,
        "weights_frozen": True,
    }
    return model, metadata

"""Small causal pose predictor and shared, sign-invariant pose calculations."""
import hashlib
import json
from pathlib import Path

import numpy as np
import torch
from torch import nn
from torch.nn import functional as F
from mani_skill.utils.geometry.rotation_conversions import (
    axis_angle_to_quaternion, quaternion_invert, quaternion_multiply,
    quaternion_to_axis_angle, quaternion_to_matrix,
)

STATE_KEYS = ("qpos", "qvel", "ee_pose", "cube_pose", "goal_pos", "action")
INPUT_DIM = 62


def file_hash(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load_episode(path, require_success=True):
    with np.load(path, allow_pickle=False) as archive:
        data = {key: archive[key].copy() for key in STATE_KEYS}
        data["success"] = archive["success"].copy()
        data["control_freq"] = int(archive["control_freq"])
    T = len(data["action"])
    shapes = {"qpos": (T+1, 9), "qvel": (T+1, 9), "ee_pose": (T+1, 7),
              "cube_pose": (T+1, 7), "goal_pos": (T+1, 3), "action": (T, 8)}
    for key, shape in shapes.items():
        if data[key].shape != shape or not np.isfinite(data[key]).all():
            raise ValueError(f"Invalid {key} in {path}: {data[key].shape}")
    if T < 1 or (require_success and not bool(data["success"][-1])):
        raise ValueError(f"Training/calibration requires a successful nonempty episode: {path}")
    return data


def pose_delta(current, following):
    """World translation and shortest world rotation vectors, for two 7D poses."""
    blocks = []
    for offset in (0, 7):
        q0 = F.normalize(current[..., offset+3:offset+7], dim=-1)
        q1 = F.normalize(following[..., offset+3:offset+7], dim=-1)
        dq = quaternion_multiply(q1, quaternion_invert(q0))
        blocks.extend((following[..., offset:offset+3] - current[..., offset:offset+3],
                       quaternion_to_axis_angle(dq)))
    return torch.cat(blocks, dim=-1)


def apply_delta(current, delta):
    blocks = []
    for pose_offset, delta_offset in ((0, 0), (7, 6)):
        q = F.normalize(current[..., pose_offset+3:pose_offset+7], dim=-1)
        dq = axis_angle_to_quaternion(delta[..., delta_offset+3:delta_offset+6])
        blocks.extend((current[..., pose_offset:pose_offset+3] + delta[..., delta_offset:delta_offset+3],
                       F.normalize(quaternion_multiply(dq, q), dim=-1)))
    return torch.cat(blocks, dim=-1)


def prepare_episode(data):
    """Only current/past observations and the current intended action enter x."""
    tensors = {key: torch.as_tensor(data[key], dtype=torch.float32) for key in STATE_KEYS}
    poses = torch.cat((tensors["ee_pose"], tensors["cube_pose"]), dim=-1)
    current, following = poses[:-1], poses[1:]
    previous = torch.cat((poses[:1], poses[:-2]), dim=0)
    velocity_delta = pose_delta(previous, current)
    geometry = []
    for offset in (0, 7):
        q = F.normalize(current[:, offset+3:offset+7], dim=-1)
        rotation = quaternion_to_matrix(q)[:, :, :2].reshape(-1, 6)
        geometry.extend((current[:, offset:offset+3], rotation))
    features = torch.cat((
        tensors["qpos"][:-1], tensors["qvel"][:-1], *geometry,
        tensors["goal_pos"][:-1] - current[:, 7:10],
        tensors["action"], velocity_delta, current[:, 7:10] - current[:, :3],
    ), dim=-1)
    assert features.shape[-1] == INPUT_DIM
    target = pose_delta(current, following)
    return {"x": features, "target": target, "base": velocity_delta,
            "current": current, "following": following}


class PosePredictor(nn.Module):
    """Learn a correction to constant velocity; one unidirectional GRU layer."""
    def __init__(self, hidden_size=64):
        super().__init__()
        self.register_buffer("input_mean", torch.zeros(INPUT_DIM))
        self.register_buffer("input_scale", torch.ones(INPUT_DIM))
        self.register_buffer("target_scale", torch.ones(12))
        self.gru = nn.GRU(INPUT_DIM, hidden_size, batch_first=True)
        self.head = nn.Sequential(nn.Linear(hidden_size, hidden_size), nn.SiLU(),
                                  nn.Linear(hidden_size, 12))
        nn.init.zeros_(self.head[-1].weight)
        nn.init.zeros_(self.head[-1].bias)

    def forward(self, features, hidden=None):
        values, hidden = self.gru((features-self.input_mean)/self.input_scale, hidden)
        return self.head(values), hidden


def pose_errors(predicted, actual):
    """Four interpretable errors: TCP m, TCP rad, cube m, cube rad."""
    delta = pose_delta(predicted, actual)
    return torch.stack([torch.linalg.vector_norm(delta[..., i:i+3], dim=-1)
                        for i in (0, 3, 6, 9)], dim=-1)


@torch.no_grad()
def predict(model, episode, baseline=None):
    device = next(model.parameters()).device
    if baseline == "persistence":
        delta = torch.zeros_like(episode["target"])
    elif baseline == "constant_velocity":
        delta = episode["base"]
    else:
        output, _ = model(episode["x"].to(device)[None])
        delta = episode["base"] + output[0].cpu()*model.target_scale.cpu()
    predicted = apply_delta(episode["current"], delta)
    return predicted, pose_errors(predicted, episode["following"])


def load_model(path, device="cpu"):
    checkpoint = torch.load(path, map_location=device, weights_only=True)
    model = PosePredictor(checkpoint["hidden_size"]).to(device)
    model.load_state_dict(checkpoint["model_state"])
    model.eval()
    return model, checkpoint


def split_paths(manifest_path, split):
    manifest = json.loads(Path(manifest_path).read_text())
    root = Path(manifest["data_dir"])
    paths = []
    for record in manifest["splits"][split]:
        path = root / record["file"]
        if file_hash(path) != record["sha256"]:
            raise ValueError(f"Dataset changed since splitting: {path}")
        paths.append(path)
    return paths

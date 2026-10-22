"""Small, offline image-only mass estimator and safe inference helpers."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image
import torch
from torch import nn


MODEL_VERSION = 1
STANDARD_GRAVITY = 9.81


class MassRegressor(nn.Module):
    """Predict standardized log mass from normalized RGB pixels only.

    Spatial pooling preserves apparent size, unlike global average pooling.
    This network starts from random weights and never downloads pretrained data.
    """

    def __init__(self) -> None:
        super().__init__()
        layers: list[nn.Module] = []
        previous = 3
        for channels in (16, 24, 32, 48):
            layers.extend(
                [
                    nn.Conv2d(previous, channels, kernel_size=3, stride=2, padding=1),
                    nn.GroupNorm(4, channels),
                    nn.SiLU(),
                ]
            )
            previous = channels
        self.features = nn.Sequential(*layers, nn.AdaptiveAvgPool2d((4, 4)))
        self.regressor = nn.Sequential(
            nn.Flatten(), nn.Linear(48 * 4 * 4, 96), nn.SiLU(), nn.Linear(96, 1)
        )

    def forward(self, images: torch.Tensor) -> torch.Tensor:
        return self.regressor(self.features(images)).squeeze(-1)


def image_to_tensor(path: str | Path, image_size: int) -> torch.Tensor:
    """Load RGB pixels using exactly the same preprocessing for every split."""
    with Image.open(Path(path).expanduser()) as source:
        if source.mode != "RGB":
            raise ValueError(f"Expected an RGB image, got {source.mode!r}: {path}")
        resized = source.resize((image_size, image_size), Image.Resampling.BILINEAR)
        pixels = np.asarray(resized, dtype=np.float32).copy() / 255.0
    return torch.from_numpy(pixels).permute(2, 0, 1).contiguous().mul(2).sub(1)


def resolve_device(requested: str) -> torch.device:
    if requested == "auto":
        return torch.device("cuda" if torch.cuda.is_available() else "cpu")
    device = torch.device(requested)
    if device.type not in {"cpu", "cuda", "mps"}:
        raise ValueError("Device must be auto, cpu, cuda, cuda:N, or mps.")
    if device.type == "cuda" and not torch.cuda.is_available():
        raise ValueError("CUDA was requested, but this PyTorch runtime has no available CUDA device.")
    if device.type == "mps" and not torch.backends.mps.is_available():
        raise ValueError("MPS was requested, but it is unavailable in this runtime.")
    return device


def load_estimator(
    checkpoint_path: str | Path, device: str = "cpu"
) -> tuple[MassRegressor, dict[str, Any], torch.device]:
    """Load only tensor/primitive checkpoint data, without arbitrary unpickling."""
    selected = resolve_device(device)
    checkpoint = torch.load(Path(checkpoint_path).expanduser(), map_location="cpu", weights_only=True)
    if not isinstance(checkpoint, dict) or checkpoint.get("model_version") != MODEL_VERSION:
        raise ValueError("Unsupported or invalid visual mass checkpoint.")
    if checkpoint.get("architecture") != "small_spatial_cnn":
        raise ValueError("Unsupported estimator architecture.")
    image_size = checkpoint.get("image_size")
    mean = checkpoint.get("log_mass_mean")
    std = checkpoint.get("log_mass_std")
    if not isinstance(image_size, int) or not 32 <= image_size <= 1024:
        raise ValueError("Checkpoint has an invalid image size.")
    if not isinstance(mean, (int, float)) or not np.isfinite(mean):
        raise ValueError("Checkpoint has an invalid log-mass mean.")
    if not isinstance(std, (int, float)) or not np.isfinite(std) or std <= 0:
        raise ValueError("Checkpoint has an invalid log-mass scale.")
    model = MassRegressor()
    model.load_state_dict(checkpoint["model_state_dict"], strict=True)
    model.to(selected).eval()
    return model, checkpoint, selected


@torch.inference_mode()
def predict_mass(
    model: MassRegressor,
    images: torch.Tensor,
    *,
    log_mass_mean: float,
    log_mass_std: float,
) -> torch.Tensor:
    """Return kilograms; callers pass RGB images, never physical-property labels."""
    log_mass = model(images) * log_mass_std + log_mass_mean
    return torch.exp(log_mass)

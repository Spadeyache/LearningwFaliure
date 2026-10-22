"""Run the trained image-only mass estimator on one RGB image."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

from .model import STANDARD_GRAVITY, image_to_tensor, load_estimator, predict_mass


def predict_image(checkpoint: str | Path, image: str | Path, *, device: str = "cpu") -> dict[str, float | str]:
    model, metadata, selected = load_estimator(checkpoint, device=device)
    pixels = image_to_tensor(image, metadata["image_size"]).unsqueeze(0).to(selected)
    mass = float(predict_mass(
        model, pixels, log_mass_mean=metadata["log_mass_mean"], log_mass_std=metadata["log_mass_std"]
    ).cpu().item())
    if not math.isfinite(mass) or mass <= 0:
        raise ValueError("The estimator produced an invalid mass.")
    return {
        "image": str(Path(image).expanduser().resolve()),
        "mass_kg": mass, "mass_g": mass * 1000, "weight_n": mass * STANDARD_GRAVITY,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--checkpoint", required=True, type=Path)
    parser.add_argument("--image", required=True, type=Path)
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--output", type=Path, help="Optional prediction JSON path")
    parser.add_argument("--overwrite", action="store_true", help="Explicitly allow replacing the output JSON")
    args = parser.parse_args()
    try:
        if args.output is not None and args.output.exists() and not args.overwrite:
            raise FileExistsError(f"Output already exists: {args.output}. Use --overwrite to replace it.")
        result = predict_image(args.checkpoint, args.image, device=args.device)
        serialized = json.dumps(result, indent=2, allow_nan=False) + "\n"
        if args.output is not None:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(serialized, encoding="utf-8")
        print(serialized, end="")
    except (ValueError, FileNotFoundError, FileExistsError) as error:
        parser.error(str(error))


if __name__ == "__main__":
    main()

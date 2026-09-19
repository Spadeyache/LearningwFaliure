"""Set residual scales/thresholds from clean validation and calibration only."""
import argparse
import json
from pathlib import Path
import numpy as np
import torch
from pose_model import file_hash, load_episode, load_model, predict, prepare_episode, split_paths

METHODS = ("learned", "persistence", "constant_velocity")


def residual_score(errors, scales):
    errors = np.asarray(errors)
    scales = np.asarray(scales)
    if errors.ndim != 2 or errors.shape[1] != 4 or scales.shape != (4,) or np.any(scales <= 0):
        raise ValueError("Expected four pose-error groups and positive scales")
    return np.max(errors/scales, axis=1)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=Path("results/splits.json"))
    parser.add_argument("--model", type=Path, default=Path("artifacts/predictor.pt"))
    parser.add_argument("--output", type=Path, default=Path("results/calibration.json"))
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError("Preserve the existing calibration; choose a new output path")
    torch.set_num_threads(4)
    model, checkpoint = load_model(args.model)
    manifest_hash = file_hash(args.manifest)
    if checkpoint["manifest_sha256"] != manifest_hash:
        raise ValueError("Checkpoint and split manifest disagree")
    validation = [prepare_episode(load_episode(p)) for p in split_paths(args.manifest, "validation")]
    calibration_paths = split_paths(args.manifest, "calibration")
    calibration = [prepare_episode(load_episode(p)) for p in calibration_paths]
    result = {"schema_version": 1, "model_sha256": file_hash(args.model),
              "manifest_sha256": manifest_hash, "calibration_episodes": len(calibration),
              "error_order": ["tcp_position_m", "tcp_rotation_rad", "cube_position_m", "cube_rotation_rad"],
              "rule": "strict score > maximum clean calibration episode score; empirical, not a 95% guarantee",
              "methods": {}}
    for method in METHODS:
        baseline = None if method == "learned" else method
        validation_errors = torch.cat([predict(model, ep, baseline)[1] for ep in validation])
        scales = torch.maximum(torch.quantile(validation_errors, .95, dim=0),
                               torch.tensor([.001, .01, .001, .01])).numpy()
        maxima = []
        for path, episode in zip(calibration_paths, calibration):
            errors = predict(model, episode, baseline)[1].numpy()
            maxima.append({"file": path.name, "max_score": float(residual_score(errors, scales).max())})
        threshold = max(entry["max_score"] for entry in maxima)
        result["methods"][method] = {"scales": scales.tolist(), "threshold": threshold,
                                     "calibration_episode_maxima": maxima}
        print(f"{method}: threshold={threshold:.6f}, scales={scales.tolist()}", flush=True)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2)+"\n")


if __name__ == "__main__":
    main()

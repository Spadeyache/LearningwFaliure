"""Train an image-only regressor on a generated dataset.json manifest."""

from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path
import random
import time
from typing import Any

import numpy as np
import torch
from torch import nn
from torch.utils.data import DataLoader, TensorDataset

from .model import MODEL_VERSION, MassRegressor, image_to_tensor, resolve_device


SPLITS = ("train", "val", "test")
OUTPUT_FILES = (
    "best.pt", "metrics.json", "predictions.csv", "training_curve.png", "predictions.png"
)


def read_manifest(dataset: str | Path) -> tuple[Path, dict[str, Any], list[dict[str, Any]]]:
    """Validate grouping, targets, and image paths before fitting anything."""
    supplied = Path(dataset).expanduser().resolve()
    manifest_path = supplied / "dataset.json" if supplied.is_dir() else supplied
    root = manifest_path.parent
    with manifest_path.open(encoding="utf-8") as handle:
        manifest = json.load(handle)
    if manifest.get("schema_version") != 1:
        raise ValueError("Expected dataset schema_version 1.")
    if manifest.get("status") != "complete":
        raise ValueError("Dataset generation must have status 'complete' before training.")
    image_size = manifest.get("image_size")
    if not isinstance(image_size, int) or not 32 <= image_size <= 1024:
        raise ValueError("Manifest image_size must be an integer between 32 and 1024.")
    records = manifest.get("records")
    if not isinstance(records, list) or not records:
        raise ValueError("The dataset must contain a nonempty records list.")
    object_splits: dict[str, str] = {}
    seen_paths: set[Path] = set()
    split_counts = {split: 0 for split in SPLITS}
    checked: list[dict[str, Any]] = []
    for index, record in enumerate(records):
        if not isinstance(record, dict):
            raise ValueError(f"Record {index} must be an object.")
        split, object_id = record.get("split"), record.get("object_id")
        if split not in SPLITS or not isinstance(object_id, str) or not object_id:
            raise ValueError(f"Record {index} has an invalid split or object_id.")
        if object_id in object_splits and object_splits[object_id] != split:
            raise ValueError(f"Object {object_id!r} appears in multiple splits.")
        object_splits[object_id] = split
        mass = record.get("mass_kg")
        if isinstance(mass, bool) or not isinstance(mass, (int, float)) or not math.isfinite(mass) or mass <= 0:
            raise ValueError(f"Record {index} must have a finite positive mass_kg.")
        size = record.get("size_m")
        if isinstance(size, bool) or not isinstance(size, (int, float)) or not math.isfinite(size) or size <= 0:
            raise ValueError(f"Record {index} must have a finite positive size_m.")
        relative = record.get("image")
        if not isinstance(relative, str) or not relative or Path(relative).is_absolute():
            raise ValueError(f"Record {index} must have a relative image path.")
        image_path = (root / relative).resolve()
        if not image_path.is_relative_to(root):
            raise ValueError(f"Record {index} image escapes the dataset directory.")
        if not image_path.is_file():
            raise ValueError(f"Missing image in record {index}: {relative}")
        if image_path in seen_paths:
            raise ValueError(f"Image {relative!r} appears more than once in the dataset.")
        seen_paths.add(image_path)
        split_counts[split] += 1
        checked.append(dict(record, _image_path=image_path))
    if any(count == 0 for count in split_counts.values()):
        raise ValueError(f"Every split must contain images; found {split_counts}.")
    if len({float(row["mass_kg"]) for row in checked if row["split"] == "train"}) < 2:
        raise ValueError("Training requires at least two distinct training masses.")
    return manifest_path, manifest, checked


def _batches(
    records: list[dict[str, Any]], image_size: int, mean: float, std: float,
    batch_size: int, seed: int, shuffle: bool,
) -> DataLoader:
    images = torch.stack([image_to_tensor(row["_image_path"], image_size) for row in records])
    labels = torch.tensor(
        [(math.log(float(row["mass_kg"])) - mean) / std for row in records],
        dtype=torch.float32,
    )
    return DataLoader(
        TensorDataset(images, labels), batch_size=batch_size, shuffle=shuffle,
        num_workers=0, generator=torch.Generator().manual_seed(seed),
    )


@torch.inference_mode()
def _evaluate(
    model: MassRegressor, loader: DataLoader, device: torch.device, mean: float, std: float
) -> tuple[float, np.ndarray]:
    model.eval()
    total_squared_error = 0.0
    predictions = []
    for images, targets in loader:
        outputs = model(images.to(device))
        total_squared_error += float(torch.sum((outputs - targets.to(device)) ** 2).cpu())
        mass = torch.exp(outputs * std + mean)
        predictions.append(mass.cpu().numpy().astype(np.float64))
    values = np.concatenate(predictions)
    if not np.isfinite(values).all():
        raise ValueError("The estimator produced nonfinite masses; reduce the learning rate.")
    return total_squared_error / len(loader.dataset), values


def _metrics(actual: np.ndarray, predicted: np.ndarray, baseline_kg: float) -> dict[str, float]:
    error_g = (predicted - actual) * 1000.0
    baseline_error_g = (baseline_kg - actual) * 1000.0
    return {
        "mae_g": float(np.mean(np.abs(error_g))),
        "rmse_g": float(np.sqrt(np.mean(error_g ** 2))),
        "baseline_mae_g": float(np.mean(np.abs(baseline_error_g))),
        "baseline_rmse_g": float(np.sqrt(np.mean(baseline_error_g ** 2))),
    }


def _plots(output: Path, history: list[dict[str, float]], final: dict[str, Any]) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    plt.rcParams.update({"font.size": 10, "axes.spines.top": False, "axes.spines.right": False})
    figure, axis = plt.subplots(figsize=(7, 4.2))
    axis.plot([row["epoch"] for row in history], [row["train_mse"] for row in history], label="Train")
    axis.plot([row["epoch"] for row in history], [row["val_mse"] for row in history], label="Validation")
    axis.set(xlabel="Epoch", ylabel="Standardized log-mass MSE", title="Training and validation loss")
    axis.legend()
    axis.grid(alpha=0.2)
    figure.tight_layout()
    figure.savefig(output / "training_curve.png", dpi=160)
    plt.close(figure)

    figure, axes = plt.subplots(1, 3, figsize=(12, 3.8), sharex=True, sharey=True)
    all_actual = np.concatenate([final[split]["actual"] for split in SPLITS]) * 1000
    all_pred = np.concatenate([final[split]["predicted"] for split in SPLITS]) * 1000
    low = max(0.0, min(float(all_actual.min()), float(all_pred.min())) * 0.9)
    high = max(float(all_actual.max()), float(all_pred.max())) * 1.08
    for axis, split in zip(axes, SPLITS):
        values = final[split]
        axis.scatter(values["actual"] * 1000, values["predicted"] * 1000, s=15, alpha=0.65)
        axis.plot([low, high], [low, high], color="black", linestyle="--", linewidth=1)
        axis.set(title=split.capitalize(), xlabel="True mass (g)", xlim=(low, high), ylim=(low, high))
        axis.grid(alpha=0.2)
    axes[0].set_ylabel("Predicted mass (g)")
    figure.suptitle("Image-only predictions; objects are disjoint across splits")
    figure.tight_layout()
    figure.savefig(output / "predictions.png", dpi=160)
    plt.close(figure)


def train_model(
    dataset: str | Path, output: str | Path, *, epochs: int = 80, batch_size: int = 32,
    seed: int = 42, device: str = "auto", threads: int = 4,
    learning_rate: float = 0.001, patience: int = 20, overwrite: bool = False,
) -> dict[str, Any]:
    """Fit using train labels, select with validation, evaluate test exactly once."""
    if epochs < 1 or batch_size < 1 or threads < 1 or patience < 1:
        raise ValueError("epochs, batch_size, threads, and patience must be positive.")
    if not math.isfinite(learning_rate) or learning_rate <= 0:
        raise ValueError("learning_rate must be finite and positive.")
    destination = Path(output).expanduser().resolve()
    if destination.exists() and not overwrite:
        raise FileExistsError(f"Output already exists: {destination}. Use --overwrite explicitly to replace outputs.")
    if destination.exists() and not destination.is_dir():
        raise ValueError("Output must be a directory.")
    manifest_path, manifest, records = read_manifest(dataset)
    if destination == manifest_path.parent:
        raise ValueError("Choose an output directory different from the dataset directory.")
    selected_device = resolve_device(device)
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
    torch.set_num_threads(threads)
    torch.use_deterministic_algorithms(True, warn_only=True)
    torch.backends.cudnn.benchmark = False
    torch.backends.cudnn.deterministic = True
    by_split = {split: [row for row in records if row["split"] == split] for split in SPLITS}
    training_masses = np.array([row["mass_kg"] for row in by_split["train"]], dtype=np.float64)
    log_mass_mean = float(np.log(training_masses).mean())
    log_mass_std = max(float(np.log(training_masses).std()), 1e-6)
    baseline_mass = float(training_masses.mean())
    image_size = int(manifest["image_size"])
    loaders = {
        split: _batches(by_split[split], image_size, log_mass_mean, log_mass_std, batch_size, seed, False)
        for split in SPLITS
    }
    training_loader = DataLoader(
        loaders["train"].dataset, batch_size=batch_size, shuffle=True, num_workers=0,
        generator=torch.Generator().manual_seed(seed),
    )
    destination.mkdir(parents=True, exist_ok=True)
    model = MassRegressor().to(selected_device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=learning_rate, weight_decay=0.0001)
    loss_function = nn.MSELoss()
    history: list[dict[str, float]] = []
    best_loss, best_epoch, stale_epochs = math.inf, 0, 0
    best_state = None
    start = time.perf_counter()
    print(f"Device: {selected_device}; images: " + ", ".join(f"{split}={len(by_split[split])}" for split in SPLITS), flush=True)
    print("Inputs are RGB pixels only. Target scaling and constant baseline use training labels only.", flush=True)
    for epoch in range(1, epochs + 1):
        model.train()
        training_error = 0.0
        for images, targets in training_loader:
            images, targets = images.to(selected_device), targets.to(selected_device)
            optimizer.zero_grad(set_to_none=True)
            loss = loss_function(model(images), targets)
            if not torch.isfinite(loss):
                raise ValueError("Nonfinite training loss; reduce the learning rate.")
            loss.backward()
            nn.utils.clip_grad_norm_(model.parameters(), 5.0)
            optimizer.step()
            training_error += float(loss.detach().cpu()) * len(images)
        train_mse = training_error / len(training_loader.dataset)
        val_mse, val_predictions = _evaluate(model, loaders["val"], selected_device, log_mass_mean, log_mass_std)
        val_actual = np.array([row["mass_kg"] for row in by_split["val"]], dtype=np.float64)
        val_mae = float(np.mean(np.abs(val_predictions - val_actual)) * 1000)
        history.append({"epoch": epoch, "train_mse": train_mse, "val_mse": val_mse, "val_mae_g": val_mae})
        if val_mse < best_loss:
            best_loss, best_epoch, stale_epochs = val_mse, epoch, 0
            best_state = {key: value.detach().cpu().clone() for key, value in model.state_dict().items()}
        else:
            stale_epochs += 1
        print(f"Epoch {epoch:03d}/{epochs}: train MSE={train_mse:.5f}; val MSE={val_mse:.5f}; val MAE={val_mae:.2f} g", flush=True)
        if stale_epochs >= patience:
            print(f"Early stop after {patience} epochs without validation improvement.", flush=True)
            break
    if best_state is None:
        raise RuntimeError("No valid estimator checkpoint was produced.")
    model.load_state_dict(best_state)
    checkpoint = {
        "model_version": MODEL_VERSION, "architecture": "small_spatial_cnn",
        "model_state_dict": best_state, "image_size": image_size,
        "log_mass_mean": log_mass_mean, "log_mass_std": log_mass_std,
        "best_epoch": best_epoch, "best_val_mse": best_loss,
        "seed": seed, "training_manifest": str(manifest_path),
        "input": "RGB pixels normalized to [-1, 1]", "target": "mass_kg",
    }
    torch.save(checkpoint, destination / "best.pt")
    final: dict[str, Any] = {}
    metrics: dict[str, Any] = {
        "schema_version": 1, "model": "small_spatial_cnn", "seed": seed,
        "device": str(selected_device), "best_epoch": best_epoch,
        "epochs_completed": len(history), "requested_epochs": epochs,
        "elapsed_seconds": time.perf_counter() - start,
        "checkpoint_selection": "minimum validation standardized log-mass MSE; test not used for selection",
        "baseline": {"type": "constant training-set arithmetic mean mass", "mass_kg": baseline_mass},
        "target_scaling": {"log_mass_mean": log_mass_mean, "log_mass_std": log_mass_std, "source": "train only"},
        "splits": {}, "history": history,
    }
    for split in SPLITS:
        normalized_mse, predicted = _evaluate(model, loaders[split], selected_device, log_mass_mean, log_mass_std)
        actual = np.array([row["mass_kg"] for row in by_split[split]], dtype=np.float64)
        final[split] = {"actual": actual, "predicted": predicted}
        metrics["splits"][split] = {
            "images": len(actual), "objects": len({row["object_id"] for row in by_split[split]}),
            "log_mass_mse_standardized": normalized_mse, **_metrics(actual, predicted, baseline_mass),
        }
    with (destination / "predictions.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["split", "object_id", "image", "true_mass_kg", "predicted_mass_kg", "absolute_error_g", "baseline_mass_kg"])
        for split in SPLITS:
            for row, actual, predicted in zip(by_split[split], final[split]["actual"], final[split]["predicted"]):
                writer.writerow([split, row["object_id"], row["image"], actual, predicted, abs(predicted - actual) * 1000, baseline_mass])
    _plots(destination, history, final)
    (destination / "metrics.json").write_text(json.dumps(metrics, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    result = metrics["splits"]["test"]
    print(f"Best epoch: {best_epoch}; held-out test MAE={result['mae_g']:.2f} g; constant baseline MAE={result['baseline_mae_g']:.2f} g", flush=True)
    print(f"Saved checkpoint, predictions, metrics, and figures to {destination}", flush=True)
    return metrics


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", required=True, type=Path, help="Dataset directory or dataset.json")
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--epochs", type=int, default=80)
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--device", default="auto")
    parser.add_argument("--threads", type=int, default=4)
    parser.add_argument("--learning-rate", type=float, default=0.001)
    parser.add_argument("--patience", type=int, default=20)
    parser.add_argument("--overwrite", action="store_true", help="Explicitly allow replacing the named training outputs")
    args = parser.parse_args()
    try:
        train_model(**vars(args))
    except (ValueError, FileNotFoundError, FileExistsError) as error:
        parser.error(str(error))


if __name__ == "__main__":
    main()

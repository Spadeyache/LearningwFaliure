"""Plot matched-run residuals and measure held-out-seed separability.

Run with ``python -m failure_collection.atlas RUN_DIRECTORY``. The PCA is an
exploratory view fitted to all included runs; reported accuracy comes from a
separate five-fold, seed-grouped classifier with training-fold-only scaling.
Only observed samples in the shared physical-time window enter either model.
"""

import argparse
from dataclasses import dataclass
import json
from pathlib import Path

import numpy as np


VARIABLES = ("mass", "friction")
MAGNITUDES = (0.5, 2.0, 4.0)
COLORS = {"mass": "#2368bd", "friction": "#da7230"}
MARKERS = {0.5: "o", 2.0: "s", 4.0: "^"}


@dataclass(frozen=True)
class ResidualRun:
    path: Path
    run_id: str
    normal_run_id: str
    variable: str
    magnitude: float
    seed: int
    channels: tuple
    residual: np.ndarray
    time_s: np.ndarray
    valid: np.ndarray


def _scalar(data, key):
    if key not in data or data[key].shape != ():
        raise ValueError(f"Missing or nonscalar field: {key}")
    return data[key].item()


def load_residual_runs(directory):
    """Load shifted episodes only, rejecting ambiguous pairs and bad masks.

    Normal runs and recovery retries never contribute classifier samples.
    Legacy archives without a run role or residual are not atlas inputs.
    """
    directory = Path(directory)
    if not directory.is_dir():
        raise ValueError(f"Episode directory does not exist: {directory}")
    runs = []
    seen_conditions = set()
    seen_ids = set()
    baseline_seeds = {}
    for path in sorted(directory.rglob("*.npz")):
        try:
            with np.load(path, allow_pickle=False) as data:
                if "meta__run_role" not in data:
                    continue
                if _scalar(data, "meta__run_role") != "shifted":
                    continue
                variable = str(_scalar(data, "label__shifted_variable"))
                magnitude = float(_scalar(data, "label__shift_magnitude"))
                seed = _scalar(data, "label__seed")
                normal_id = str(_scalar(data, "matched_normal_run_id"))
                id_key = next((key for key in ("meta__run_id", "meta__episode_id") if key in data), None)
                run_id = str(_scalar(data, id_key)) if id_key else str(path.relative_to(directory))
                if variable not in VARIABLES or magnitude not in MAGNITUDES:
                    raise ValueError("Expected mass/friction shift with magnitude 0.5, 2 or 4")
                if isinstance(seed, bool) or not isinstance(seed, int) or not normal_id or not run_id:
                    raise ValueError("Expected integer seed and nonempty run/baseline IDs")
                channels_array = data["residual_channels"]
                if channels_array.ndim != 1 or channels_array.dtype.kind not in "US":
                    raise ValueError("residual_channels must be a one-dimensional string array")
                channels = tuple(str(value) for value in channels_array)
                if not channels or len(set(channels)) != len(channels):
                    raise ValueError("Residual channel names must be nonempty and unique")
                residual = np.asarray(data["residual"], dtype=np.float64)
                time_s = np.asarray(data["residual_time_s"], dtype=np.float64)
                valid = data["residual_valid_mask"].copy()
                if residual.ndim != 2 or residual.shape[1] != len(channels):
                    raise ValueError("Residual dimensions do not match channel names")
                if time_s.shape != (len(residual),) or valid.shape != time_s.shape or valid.dtype.kind != "b":
                    raise ValueError("Expected aligned time vector and boolean residual_valid_mask")
                if not np.isfinite(time_s).all() or not np.all(np.diff(time_s) > 0):
                    raise ValueError("Residual times must be finite and strictly increasing")
                indexes = np.flatnonzero(valid)
                if len(indexes) < 2 or not np.all(np.diff(indexes) == 1):
                    raise ValueError("Need at least two contiguous observed residual samples; cannot interpolate mask gaps")
                if not np.isfinite(residual[valid]).all():
                    raise ValueError("Observed residual samples must be finite")
                condition = (seed, variable, magnitude)
                if condition in seen_conditions or run_id in seen_ids:
                    raise ValueError("Duplicate shifted episode; use one experiment directory")
                if normal_id in baseline_seeds and baseline_seeds[normal_id] != seed:
                    raise ValueError("A shared normal run cannot belong to multiple seed groups")
                if runs and channels != runs[0].channels:
                    raise ValueError("Residual channel names/order differ between episodes")
                seen_conditions.add(condition)
                seen_ids.add(run_id)
                baseline_seeds[normal_id] = seed
                runs.append(ResidualRun(path, run_id, normal_id, variable, magnitude, seed,
                                        channels, residual.copy(), time_s.copy(), valid))
        except (KeyError, TypeError, ValueError) as error:
            raise ValueError(f"{path}: {error}") from error
    if not runs:
        raise ValueError("No shifted episodes with matched residuals found")
    return runs


def build_features(runs, time_points=100):
    """Return flattened features, resampled trajectories and shared times.

    Every run uses the SAME physical seconds. We never stretch each episode to
    its own duration, append a length feature, use padding, or interpolate over
    a missing interior sample. Ending early changes only the common window.
    """
    if isinstance(time_points, bool) or not isinstance(time_points, int) or time_points < 2:
        raise ValueError("time_points must be an integer >= 2")
    if not runs:
        raise ValueError("No residual runs supplied")
    starts = [run.time_s[run.valid][0] for run in runs]
    ends = [run.time_s[run.valid][-1] for run in runs]
    start, end = max(starts), min(ends)
    if end <= start:
        raise ValueError("Episodes have no shared observed physical-time interval")
    grid = np.linspace(start, end, time_points)
    trajectories = []
    for run in runs:
        times = run.time_s[run.valid]
        values = run.residual[run.valid]
        trajectories.append(np.column_stack([
            np.interp(grid, times, values[:, channel]) for channel in range(values.shape[1])
        ]))
    trajectories = np.stack(trajectories)
    return trajectories.reshape(len(runs), -1), trajectories, grid


def make_seed_folds(labels, seeds):
    """Five disjoint seed groups, with both classes represented in every fold."""
    from sklearn.model_selection import GroupKFold

    labels, seeds = np.asarray(labels), np.asarray(seeds)
    if set(labels) != set(VARIABLES):
        raise ValueError("Both mass and friction shifted runs are required")
    for variable in VARIABLES:
        if len(np.unique(seeds[labels == variable])) < 5:
            raise ValueError("Five-fold evaluation requires at least five distinct seeds for EACH variable")
    folds = list(GroupKFold(n_splits=5).split(np.zeros(len(labels)), labels, seeds))
    for train, test in folds:
        if set(labels[train]) != set(VARIABLES) or set(labels[test]) != set(VARIABLES):
            raise ValueError("Every fold needs both variables; collect mass and friction for each seed")
        if set(seeds[train]) & set(seeds[test]):
            raise ValueError("Seed leakage between training and evaluation")
    return folds


def evaluate_separability(features, labels, seeds):
    """Fit scaling and logistic regression anew on each training fold."""
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import accuracy_score, confusion_matrix
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler

    features = np.asarray(features)
    labels, seeds = np.asarray(labels), np.asarray(seeds)
    folds = make_seed_folds(labels, seeds)
    predicted = np.empty_like(labels)
    fold_scores = []
    for index, (train, test) in enumerate(folds):
        model = make_pipeline(StandardScaler(), LogisticRegression(C=1.0, max_iter=2000, random_state=0))
        model.fit(features[train], labels[train])
        predicted[test] = model.predict(features[test])
        fold_scores.append({
            "fold": index + 1,
            "accuracy": float(accuracy_score(labels[test], predicted[test])),
            "train_seeds": sorted(int(value) for value in np.unique(seeds[train])),
            "test_seeds": sorted(int(value) for value in np.unique(seeds[test])),
            "train_runs": len(train), "test_runs": len(test),
        })
    counts = [int(np.sum(labels == variable)) for variable in VARIABLES]
    return {
        "accuracy": float(accuracy_score(labels, predicted)),
        "mean_fold_accuracy": float(np.mean([fold["accuracy"] for fold in fold_scores])),
        "std_fold_accuracy": float(np.std([fold["accuracy"] for fold in fold_scores])),
        "majority_class_accuracy": max(counts) / len(labels),
        "class_labels": list(VARIABLES),
        "confusion_matrix": confusion_matrix(labels, predicted, labels=list(VARIABLES)).tolist(),
        "confusion_matrix_axes": {"rows": "true variable", "columns": "predicted variable"},
        "cv": {"fold_count": 5, "splitter": "GroupKFold", "group_by": "label__seed",
               "preprocessing": "StandardScaler fitted separately on each training fold",
               "classifier": {"type": "LogisticRegression", "C": 1.0, "max_iter": 2000, "random_state": 0},
               "folds": fold_scores},
        "predictions": predicted.tolist(),
    }


def _plot_atlas(runs, features, trajectories, times, scores, output):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D
    from sklearn.decomposition import PCA
    from sklearn.preprocessing import StandardScaler

    scaled = StandardScaler().fit_transform(features)
    pca = PCA(n_components=2, svd_solver="full")
    if np.any(np.var(scaled, axis=0) > 0):
        points = pca.fit_transform(scaled)
        variance = np.nan_to_num(pca.explained_variance_ratio_).tolist()
    else:
        points = np.zeros((len(runs), 2))
        variance = [0.0, 0.0]
    fig, axis = plt.subplots(figsize=(8, 6), layout="constrained")
    for variable in VARIABLES:
        for magnitude in MAGNITUDES:
            selection = np.array([run.variable == variable and run.magnitude == magnitude for run in runs])
            if selection.any():
                axis.scatter(points[selection, 0], points[selection, 1], color=COLORS[variable],
                             marker=MARKERS[magnitude], alpha=0.8, s=48, edgecolors="white", linewidths=0.4)
    legend = [Line2D([], [], color=COLORS[variable], marker="o", linestyle="", label=variable)
              for variable in VARIABLES]
    legend += [Line2D([], [], color="#444444", marker=MARKERS[magnitude], linestyle="", label=f"×{magnitude:g}")
               for magnitude in MAGNITUDES]
    axis.legend(handles=legend, title="Variable / magnitude")
    axis.set(xlabel=f"PC1 ({variance[0]:.1%} variance)", ylabel=f"PC2 ({variance[1]:.1%} variance)",
             title="Matched gap signatures — exploratory PCA")
    axis.grid(alpha=0.15)
    fig.savefig(output / "atlas_pca.png", dpi=170)
    plt.close(fig)

    channels = runs[0].channels
    columns = min(3, len(channels))
    rows = (len(channels) + columns - 1) // columns
    fig, axes = plt.subplots(rows, columns, figsize=(6 * columns, 2.6 * rows),
                             squeeze=False, sharex=True, layout="constrained")
    for channel, axis in enumerate(axes.flat):
        if channel >= len(channels):
            axis.set_visible(False)
            continue
        for variable in VARIABLES:
            selection = np.array([run.variable == variable for run in runs])
            samples = trajectories[selection, :, channel]
            mean, spread = samples.mean(axis=0), samples.std(axis=0)
            axis.plot(times, mean, color=COLORS[variable], label=variable)
            axis.fill_between(times, mean - spread, mean + spread, color=COLORS[variable], alpha=0.15)
        axis.set_title(channels[channel], fontsize=9, wrap=True)
        axis.set_xlabel("Time since reset (s)")
        axis.axhline(0, color="#777777", linewidth=0.6)
        axis.grid(alpha=0.15)
    axes.flat[0].legend()
    fig.suptitle("Mean shifted − normal residual (shading: ±1 SD across runs; magnitudes pooled)")
    fig.savefig(output / "atlas_mean_residuals.png", dpi=150)
    plt.close(fig)

    matrix = np.asarray(scores["confusion_matrix"])
    fig, axis = plt.subplots(figsize=(6, 5), layout="constrained")
    display = axis.imshow(matrix, cmap="Blues", vmin=0)
    for (row, column), value in np.ndenumerate(matrix):
        axis.text(column, row, str(value), ha="center", va="center", fontsize=16,
                  color="white" if value > matrix.max() / 2 else "black")
    axis.set(xticks=np.arange(2), yticks=np.arange(2), xticklabels=VARIABLES, yticklabels=VARIABLES,
             xlabel="Predicted variable", ylabel="True variable",
             title=f"Held-out-seed confusion matrix\n5-fold accuracy: {scores['accuracy']:.1%}")
    fig.colorbar(display, ax=axis, label="Runs")
    fig.savefig(output / "atlas_confusion_matrix.png", dpi=170)
    plt.close(fig)
    return variance


def build_atlas(directory, output=None, time_points=100):
    """Write three PNGs and separability.json; return the JSON-compatible scores."""
    try:
        import sklearn  # noqa: F401
        import matplotlib  # noqa: F401
    except ImportError as error:
        raise RuntimeError("Atlas requires scikit-learn and matplotlib; install the project's analysis dependencies") from error
    directory = Path(directory)
    runs = load_residual_runs(directory)
    features, trajectories, times = build_features(runs, time_points=time_points)
    labels = [run.variable for run in runs]
    seeds = [run.seed for run in runs]
    scores = evaluate_separability(features, labels, seeds)
    output = Path(output) if output is not None else directory / "atlas"
    output.mkdir(parents=True, exist_ok=True)
    variance = _plot_atlas(runs, features, trajectories, times, scores, output)
    scores.update({
        "schema_version": "gap_atlas_v1", "run_count": len(runs), "seed_count": len(set(seeds)),
        "condition_counts": {variable: {str(magnitude): sum(run.variable == variable and run.magnitude == magnitude for run in runs)
                                        for magnitude in MAGNITUDES} for variable in VARIABLES},
        "residual_channels": list(runs[0].channels),
        "feature_shape": [len(runs), features.shape[1]], "time_points": time_points,
        "time_window_s": [float(times[0]), float(times[-1])],
        "resampling": "Linear interpolation at shared physical times; padded samples excluded; flatten in time-major order",
        "excluded_run_roles": ["normal", "retry"],
        "pca_explained_variance_ratio": variance,
        "pca_scope": "Exploratory fit on all included runs; not used by the cross-validated classifier",
        "interpretation": "Held-out-seed accuracy measures distinguishability in this experiment, not causal proof or deployment performance",
        "runs": [{"run_id": run.run_id, "matched_normal_run_id": run.normal_run_id,
                  "seed": run.seed, "variable": run.variable, "magnitude": run.magnitude,
                  "prediction": prediction} for run, prediction in zip(runs, scores.pop("predictions"))],
        "figures": ["atlas_pca.png", "atlas_mean_residuals.png", "atlas_confusion_matrix.png"],
    })
    (output / "separability.json").write_text(json.dumps(scores, indent=2, allow_nan=False) + "\n")
    return scores


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path, help="Directory containing one matched collection experiment")
    parser.add_argument("--output", type=Path, help="Output directory (default: RUN_DIRECTORY/atlas)")
    parser.add_argument("--time-points", type=int, default=100, help="Common physical-time samples per residual trajectory")
    args = parser.parse_args(argv)
    try:
        scores = build_atlas(args.directory, args.output, args.time_points)
    except (ValueError, RuntimeError) as error:
        parser.error(str(error))
    print(f"{scores['run_count']} shifted runs, {scores['seed_count']} seeds; 5-fold held-out-seed accuracy: {scores['accuracy']:.1%}")
    print(f"Saved atlas PNGs and separability.json to {args.output or args.directory / 'atlas'}")


if __name__ == "__main__":
    main()

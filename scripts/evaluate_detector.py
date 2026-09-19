"""Evaluate locked models/thresholds on all held-out clean and perturbed trials."""
import argparse
import json
from pathlib import Path
import numpy as np
import torch
from calibrate_detector import METHODS, residual_score
from collect_perturbed_episodes import CONDITIONS
from pose_model import file_hash, load_episode, load_model, predict, prepare_episode, split_paths


def alarm_timing(alarms, injection_step, control_freq):
    indices = np.flatnonzero(alarms)
    first = int(indices[0]) if len(indices) else None
    post = indices[indices >= injection_step] if injection_step >= 0 else np.array([], dtype=int)
    first_post = int(post[0]) if len(post) else None
    # Injection is before step t; its first observation arrives one interval later.
    delay = ((first_post-injection_step+1)/control_freq if first_post is not None else None)
    return {"alarm": first is not None, "first_alarm_action": first,
            "first_post_injection_alarm_action": first_post, "delay_seconds": delay,
            "premature_alarm": bool(injection_step >= 0 and np.any(alarms[:injection_step]))}


def summarize(rows):
    def rate(n, d):
        return n/d if d else None
    failed = [r for r in rows if not r["final_success"]]
    succeeded = [r for r in rows if r["final_success"]]
    clean = [r for r in rows if r["condition"]=="clean"]
    disturbed = [r for r in rows if r["condition"]!="clean"]
    recovered = [r for r in disturbed if r["final_success"]]
    tp = sum(r["alarm"] for r in failed)
    fp = sum(r["alarm"] for r in succeeded)
    post_failed = [r for r in failed if r["first_post_injection_alarm_action"] is not None]
    delay = [r["delay_seconds"] for r in post_failed]
    return {
        "trials": len(rows), "task_failures": len(failed), "task_successes": len(succeeded),
        "true_positive": tp, "false_negative": len(failed)-tp,
        "false_positive": fp, "true_negative": len(succeeded)-fp,
        "task_failure_recall": rate(tp,len(failed)),
        "task_failure_precision": rate(tp,tp+fp),
        "successful_trial_alarm_rate": rate(fp,len(succeeded)),
        "clean_controls": len(clean), "clean_control_alarms": sum(r["alarm"] for r in clean),
        "clean_episode_false_alarm_rate": rate(sum(r["alarm"] for r in clean),len(clean)),
        "clean_step_false_alarm_rate": rate(sum(r["alarm_steps_count"] for r in clean),
                                            sum(r["length"] for r in clean)),
        "perturbed_trials": len(disturbed),
        "post_injection_detection_rate": rate(sum(r["first_post_injection_alarm_action"] is not None for r in disturbed),len(disturbed)),
        "failed_trials_detected_after_injection": len(post_failed),
        "post_injection_failure_recall": rate(len(post_failed),len(failed)),
        "recovered_trials": len(recovered), "recovered_trial_alarms": sum(r["alarm"] for r in recovered),
        "premature_alarm_trials": sum(r["premature_alarm"] for r in disturbed),
        "median_detected_failure_delay_seconds": float(np.median(delay)) if delay else None,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=Path("results/splits.json"))
    parser.add_argument("--model", type=Path, default=Path("artifacts/predictor.pt"))
    parser.add_argument("--calibration", type=Path, default=Path("results/calibration.json"))
    parser.add_argument("--replays", type=Path, default=Path("data/perturbed/replay_summary.json"))
    parser.add_argument("--output", type=Path, default=Path("results/evaluation.json"))
    parser.add_argument("--trace-dir", type=Path, default=Path("runs/evaluation"))
    args = parser.parse_args()
    if args.output.exists() or list(args.trace_dir.glob("*.npz")):
        raise FileExistsError("Choose new output and trace paths; previous evaluations are preserved")
    torch.set_num_threads(4)
    model, checkpoint = load_model(args.model)
    calibration = json.loads(args.calibration.read_text())
    replays = json.loads(args.replays.read_text())
    manifest_hash = file_hash(args.manifest)
    if any(value != manifest_hash for value in (
        checkpoint["manifest_sha256"], calibration["manifest_sha256"], replays["manifest_sha256"])):
        raise ValueError("Manifest provenance mismatch")
    if calibration["model_sha256"] != file_hash(args.model):
        raise ValueError("Model changed after threshold calibration")
    tests = split_paths(args.manifest, "test")
    expected = {(str(path), condition) for path in tests for condition in CONDITIONS}
    actual = {(row["source_file"], row["condition"]) for row in replays["cases"]}
    if actual != expected or len(replays["cases"]) != len(expected):
        raise ValueError("Replay set must contain exactly one of each condition for every test identity")
    args.trace_dir.mkdir(parents=True, exist_ok=True)
    rows = []
    clean_errors = {name: [] for name in METHODS}
    for replay in replays["cases"]:
        path = Path(replay["file"])
        if file_hash(path) != replay["sha256"]:
            raise ValueError(f"Replay file changed: {path}")
        data = load_episode(path, require_success=False)
        episode = prepare_episode(data)
        if bool(data["success"][-1]) != replay["final_success"]:
            raise ValueError("Replay metadata and actual task success disagree")
        for method in METHODS:
            predicted, errors = predict(model, episode, None if method=="learned" else method)
            errors = errors.numpy()
            config = calibration["methods"][method]
            scores = residual_score(errors, config["scales"])
            alarms = scores > config["threshold"]
            row = {"file": str(path), "method": method, "condition": replay["condition"],
                   "source_episode_id": replay["source_episode_id"], "length": len(scores),
                   "injection_step": replay["injection_step"], "final_success": replay["final_success"],
                   "max_score": float(scores.max()), "threshold": config["threshold"],
                   "alarm_steps_count": int(alarms.sum()),
                   **alarm_timing(alarms, replay["injection_step"], data["control_freq"])}
            rows.append(row)
            if replay["condition"]=="clean":
                clean_errors[method].append(errors)
            trace = args.trace_dir/f"{path.stem}__{method}.npz"
            np.savez_compressed(
                trace, predicted_pose=predicted.numpy(), observed_pose=episode["following"].numpy(),
                errors=errors, score=scores, alarm=alarms, threshold=np.asarray(config["threshold"]),
                time_seconds=np.arange(1,len(scores)+1)/data["control_freq"],
                injection_step=np.asarray(replay["injection_step"]),
                control_freq=np.asarray(data["control_freq"]),
                final_success=np.asarray(replay["final_success"]), condition=np.asarray(replay["condition"]),
            )
        print(f"Scored {path.name}", flush=True)
    summary = {}
    for method in METHODS:
        method_rows = [row for row in rows if row["method"]==method]
        errors = np.concatenate(clean_errors[method])
        summary[method] = summarize(method_rows)
        summary[method]["clean_mean_errors"] = errors.mean(0).tolist()
        summary[method]["clean_p95_errors"] = np.quantile(errors,.95,axis=0).tolist()
        summary[method]["by_condition"] = {
            condition: summarize([row for row in method_rows if row["condition"]==condition])
            for condition in CONDITIONS}
    report = {"manifest_sha256": manifest_hash, "model_sha256": file_hash(args.model),
              "calibration_sha256": file_hash(args.calibration), "test_source_episodes": len(tests),
              "trace_dir": str(args.trace_dir), "summary": summary, "cases": rows,
              "latency_definition": "time from intervention before action t to alarm after a physics/control step; minimum 0.05 seconds"}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps(summary,indent=2))


if __name__ == "__main__":
    main()

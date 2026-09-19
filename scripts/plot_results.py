"""Generate static figures and an honest report from the locked evaluation."""
import argparse
import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

METHODS=("learned","constant_velocity","persistence")
COLORS={"learned":"#2563eb","constant_velocity":"#d97706","persistence":"#64748b"}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evaluation",type=Path,default=Path("results/evaluation.json"))
    args=parser.parse_args()
    report=json.loads(args.evaluation.read_text())
    training=json.loads(Path("results/training.json").read_text())
    output=Path("results")
    trace_dir=Path(report["trace_dir"])
    plt.rcParams.update({"font.size":10,"axes.spines.top":False,"axes.spines.right":False})

    history=training["history"]
    fig,ax=plt.subplots(figsize=(8,4))
    ax.plot([r["epoch"] for r in history],[r.get("train_loss",np.nan) for r in history],label="Training")
    ax.plot([r["epoch"] for r in history],[r["validation_loss"] for r in history],label="Validation")
    ax.axvline(training["best_epoch"],color="gray",linestyle="--",label="Selected checkpoint")
    ax.set(xlabel="Epoch",ylabel="Scaled residual MSE",title="Clean-success predictor training")
    ax.grid(alpha=.2); ax.legend(); fig.tight_layout()
    fig.savefig(output/"training_curve.png",dpi=160); plt.close(fig)

    fig,axes=plt.subplots(2,2,figsize=(10,7))
    labels=("TCP position (mm)","TCP rotation (mrad)","Cube position (mm)","Cube rotation (mrad)")
    for i,ax in enumerate(axes.flat):
        values=[report["summary"][method]["clean_mean_errors"][i]*1000 for method in METHODS]
        bars=ax.bar(["GRU","Constant velocity","Persistence"],values,color=[COLORS[m] for m in METHODS])
        ax.bar_label(bars,fmt="%.3f",padding=3)
        ax.set(title=labels[i],ylabel="Mean next-step error",ylim=(0,max(values)*1.25))
        ax.grid(axis="y",alpha=.2)
    fig.suptitle("Held-out clean episodes: prediction error")
    fig.tight_layout(); fig.savefig(output/"forecast_errors.png",dpi=160); plt.close(fig)

    first_source=report["cases"][0]["source_episode_id"]
    selected=[r for r in report["cases"] if r["method"]=="learned" and r["source_episode_id"]==first_source]
    fig,axes=plt.subplots(len(selected),1,figsize=(10,10),sharex=True)
    for ax,row in zip(axes,selected):
        for method in METHODS:
            path=trace_dir/f"{Path(row['file']).stem}__{method}.npz"
            with np.load(path,allow_pickle=False) as trace:
                ax.plot(trace["time_seconds"],np.maximum(trace["score"]/trace["threshold"],1e-4),
                        color=COLORS[method],label=method.replace("_"," "),linewidth=1.3)
                frequency=int(trace["control_freq"])
        ax.axhline(1,color="black",linestyle="--",linewidth=1,label="Alarm threshold")
        if row["injection_step"]>=0:
            ax.axvline(row["injection_step"]/frequency,color="#dc2626",linestyle=":")
        outcome="success" if row["final_success"] else "failure"
        ax.set(title=f"{row['condition']} - final task {outcome}",ylabel="Score / threshold",yscale="log")
        ax.grid(alpha=.2)
    axes[0].legend(ncol=4,fontsize=8)
    axes[-1].set_xlabel("Elapsed time (s); red dotted line = intervention")
    fig.suptitle(f"Paired held-out episode {first_source:03d} (first test identity)")
    fig.tight_layout(); fig.savefig(output/"score_traces.png",dpi=160); plt.close(fig)

    missed=[r for r in report["cases"] if r["method"]=="learned" and not r["final_success"]
            and r["first_post_injection_alarm_action"] is None]
    if missed:
        row=missed[0]
        with np.load(trace_dir/f"{Path(row['file']).stem}__learned.npz",allow_pickle=False) as trace:
            time=trace["time_seconds"]; ratio=trace["score"]/trace["threshold"]
            predicted=trace["predicted_pose"]; observed=trace["observed_pose"]
            onset=row["injection_step"]/int(trace["control_freq"])
        with np.load(row["file"],allow_pickle=False) as data:
            goal=data["goal_pos"][1:,2]
            intended=data["action"][:,-1]; applied=data["applied_action"][:,-1]
        fig,axes=plt.subplots(3,1,figsize=(10,8),sharex=True)
        axes[0].plot(time,ratio,label="Learned residual / threshold",color=COLORS["learned"])
        axes[0].axhline(1,color="black",linestyle="--",label="Alarm threshold")
        axes[0].set_ylabel("Score / threshold")
        axes[1].plot(time,observed[:,9],label="Observed cube z")
        axes[1].plot(time,predicted[:,9],linestyle="--",label="Predicted next cube z")
        axes[1].plot(time,goal,linestyle=":",label="Goal z")
        axes[1].set_ylabel("World z (m)")
        axes[2].plot(time,intended,label="Intended gripper command")
        axes[2].plot(time,applied,linestyle="--",label="Applied gripper command")
        axes[2].set(xlabel="Elapsed time (s)",ylabel="Normalized command",ylim=(-1.1,1.1))
        for ax in axes:
            ax.axvline(onset,color="#dc2626",linestyle=":")
            ax.grid(alpha=.2); ax.legend(fontsize=8)
        fig.suptitle(f"Error analysis: {Path(row['file']).stem}, no post-intervention alarm")
        fig.tight_layout(); fig.savefig(output/"missed_failure.png",dpi=160); plt.close(fig)

    def percent(value):
        return "n/a" if value is None else f"{100*value:.1f}%"
    lines=[
        "# Held-out PickCube failure-detection results", "",
        "The complete state-based prototype runs from official clean demonstrations to causal",
        "next-pose prediction, clean-only threshold calibration, perturbed replay, and evaluation.",
        "**Residual alarms are not yet a reliable classifier of eventual task failure.**", "",
        "The trained checkpoint and thresholds were fixed before scoring the test set.",
        "There are 100 clean episodes: 60 train, 10 validation, 15 calibration, 15 test.",
        "The 15 test identities each have four paired replays (60 trials total).",
        "They produced 30 final task failures and 30 successes. All 15 unperturbed controls",
        "reproduced their source states, RGB, rewards, and flags exactly.", "",
        "## Detection results", "",
        "| Method | Failures detected after injection | Episode-alarm precision for final failure | Clean control false alarms | Alarms on recovered perturbations | Median delay on detected failures |",
        "|---|---:|---:|---:|---:|---:|"]
    for method in METHODS:
        s=report["summary"][method]
        lines.append(f"| {method.replace('_',' ')} | {s['failed_trials_detected_after_injection']}/{s['task_failures']} ({percent(s['post_injection_failure_recall'])}) | {percent(s['task_failure_precision'])} | {s['clean_control_alarms']}/{s['clean_controls']} | {s['recovered_trial_alarms']}/{s['recovered_trials']} | {s['median_detected_failure_delay_seconds']:.2f} s |")
    learned=report["summary"]["learned"]
    lines += [
        "", f"The learned detector has {learned['premature_alarm_trials']} perturbed trials with alarms before injection.",
        f"Counting any alarm anywhere gives {learned['true_positive']}/{learned['task_failures']} task-failure recall,",
        "but the table uses the stricter post-injection count to avoid crediting premature alarms.",
        "Latency begins when the intervention is applied before action t and ends when the",
        "post-step observation triggers an alarm. At 20 Hz the minimum is 0.05 seconds;",
        "the reported median is conditional on detection, not a measured semantic failure-onset delay.", "",
        "## Held-out clean prediction errors", "",
        "| Error | GRU | Constant velocity | Persistence |",
        "|---|---:|---:|---:|"]
    for i,label in enumerate(labels):
        values=[report["summary"][m]["clean_mean_errors"][i]*1000 for m in METHODS]
        lines.append(f"| {label} | {values[0]:.4f} | {values[1]:.4f} | {values[2]:.4f} |")
    lines += [
        "", "The GRU improves position forecasting and TCP rotation; cube rotation is worse",
        "than the simpler baselines. These are one-step, observation-conditioned predictions.", "",
        "![Held-out forecast errors](results/forecast_errors.png)", "",
        "![Paired score traces](results/score_traces.png)", "",
        "The trace figure uses the first test identity, selected before inspecting detector scores.",
        "A score/threshold ratio above 1 triggers an alarm. Successful recovery after an arm",
        "stall is still abnormal motion, so treating every alarm as eventual task failure",
        "produces false positives.", "",
        "## Failure analysis and limits", "",
        f"- The learned detector misses post-injection detection on {len(missed)} of 30 failed trials.",
        "- One-step predictions condition on the observed state. A failed but stationary cube",
        "  can become easy to predict even while it remains far from the goal.",
        "- Output targets are TCP and cube poses; gripper joint positions are inputs, not",
        "  prediction targets. Gripper faults may not create a large immediate pose residual.",
        "- Only 15 independent test identities are used. Their four conditions are paired,",
        "  not 60 independent examples. Treat rates as small-sample research results.",
        "- The designed test set has 50% task-failure prevalence; its precision does not",
        "  estimate deployment precision when failures are rare.",
        "- Calibration uses 15 clean episode maxima, with no certified low false-alarm guarantee.",
        "- Inputs are privileged simulator state from one task and robot. RGB is recorded",
        "  but unused by this baseline. Cross-task and real-robot generalization are untested.", "",
        "![First missed post-injection failure](results/missed_failure.png)", "",
        "The error-analysis figure selects the first failed trial with no post-injection",
        "alarm. This is explicit diagnostic selection, not a representative accuracy claim.", "",
        "## Reproduce / use", "",
        "Use the environment setup in README.md and commands in docs/STEP2.md and docs/STEP3.md.",
        "After those outputs exist:", "",
        chr(96)*3+"bash",
        "python scripts/evaluate_detector.py",
        "python scripts/plot_results.py",
        "python scripts/score_episode.py data/perturbed/episode_041__cube_shift.npz --output runs/scored_cube_shift.npz",
        "python -m unittest discover -s tests -v",
        chr(96)*3, "",
        "Evaluation/scoring preserve existing results; choose new --output and --trace-dir",
        "paths for a repeat. plot_results.py regenerates derived figures and this report.", "",
        "Full results: results/evaluation.json; thresholds: results/calibration.json;",
        "checkpoint: artifacts/predictor.pt; streaming scorer: scripts/score_episode.py.",
        "Each streaming forecast is computed before comparing it with observation t+1.",
        "Tests check causal features and recurrent streaming equivalence. Actual perturbed",
        "episode forecasts and alarm flags were also compared against batch evaluation.", "",
        "Trace NPZs under runs/evaluation contain predicted_pose and observed_pose (T,14),",
        "TCP [xyz,wxyz] followed by cube [xyz,wxyz]; errors (T,4) in the units above;",
        "score (T,), alarm (T,), threshold (scalar), time_seconds (T,), injection_step,",
        "control_freq, condition, and final_success. These are evaluation artifacts,",
        "not additional training data.", "",
    ]
    Path("RESULTS.md").write_text("\n".join(lines))
    print("Saved RESULTS.md and results/*.png")


if __name__=="__main__":
    main()

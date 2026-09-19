"""Compute causal predictions and alarms one step at a time on a saved NPZ."""
import argparse
import json
from pathlib import Path
import numpy as np
import torch
from calibrate_detector import residual_score
from evaluate_detector import alarm_timing
from pose_model import apply_delta, file_hash, load_episode, load_model, pose_errors, prepare_episode


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("episode",type=Path)
    parser.add_argument("--model",type=Path,default=Path("artifacts/predictor.pt"))
    parser.add_argument("--calibration",type=Path,default=Path("results/calibration.json"))
    parser.add_argument("--output",type=Path,default=Path("runs/scored_episode.npz"))
    args=parser.parse_args()
    if args.output.exists():
        raise FileExistsError("Choose a new output path")
    torch.set_num_threads(4)
    model,checkpoint=load_model(args.model)
    calibration=json.loads(args.calibration.read_text())
    if calibration["model_sha256"]!=file_hash(args.model) or calibration["manifest_sha256"]!=checkpoint["manifest_sha256"]:
        raise ValueError("Model/calibration provenance mismatch")
    config=calibration["methods"]["learned"]
    data=load_episode(args.episode,require_success=False)
    episode=prepare_episode(data)
    predicted=[]; errors=[]; hidden=None
    with torch.no_grad():
        for t in range(len(data["action"])):
            # This input contains observations only through t and intended action t.
            output,hidden=model(episode["x"][None,t:t+1],hidden)
            delta=episode["base"][t:t+1]+output[0]*model.target_scale
            forecast=apply_delta(episode["current"][t:t+1],delta)
            predicted.append(forecast[0].numpy())
            # The observed t+1 pose is used only after the forecast is computed.
            errors.append(pose_errors(forecast,episode["following"][t:t+1])[0].numpy())
    errors=np.stack(errors)
    scores=residual_score(errors,config["scales"])
    alarms=scores>config["threshold"]
    with np.load(args.episode,allow_pickle=False) as archive:
        injection=int(archive["injection_step"]) if "injection_step" in archive.files else -1
    args.output.parent.mkdir(parents=True,exist_ok=True)
    np.savez_compressed(args.output,predicted_pose=np.stack(predicted),
                        observed_pose=episode["following"].numpy(),errors=errors,
                        score=scores,alarm=alarms,threshold=np.asarray(config["threshold"]))
    print(json.dumps({"episode":str(args.episode),"final_task_success":bool(data["success"][-1]),
                      "max_score":float(scores.max()),"threshold":config["threshold"],
                      **alarm_timing(alarms,injection,data["control_freq"]),
                      "output":str(args.output)},indent=2))


if __name__=="__main__":
    main()

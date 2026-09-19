"""Train only on clean successes; select a checkpoint using clean validation."""
import os
os.environ.setdefault("CUBLAS_WORKSPACE_CONFIG", ":4096:8")
import argparse
import json
from pathlib import Path

import numpy as np
import torch
from torch.nn.utils.rnn import pad_sequence
from pose_model import PosePredictor, file_hash, load_episode, prepare_episode, predict, split_paths


def batch(episodes, device):
    lengths = torch.tensor([len(ep["x"]) for ep in episodes], device=device)
    x = pad_sequence([ep["x"] for ep in episodes], batch_first=True).to(device)
    residual = pad_sequence([ep["target"]-ep["base"] for ep in episodes], batch_first=True).to(device)
    mask = torch.arange(x.shape[1], device=device)[None] < lengths[:, None]
    return x, residual, mask


@torch.no_grad()
def validation_loss(model, episodes, device):
    model.eval()
    total, count = 0.0, 0
    for start in range(0, len(episodes), 16):
        x, residual, mask = batch(episodes[start:start+16], device)
        output, _ = model(x)
        squared = ((output-residual/model.target_scale)**2).mean(-1)
        total += float(squared[mask].sum())
        count += int(mask.sum())
    return total/count


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=Path("results/splits.json"))
    parser.add_argument("--output-dir", type=Path, default=Path("runs/predictor"))
    parser.add_argument("--epochs", type=int, default=250)
    parser.add_argument("--patience", type=int, default=35)
    parser.add_argument("--hidden-size", type=int, default=64)
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu")
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    if (args.output_dir/"model.pt").exists():
        raise FileExistsError("Choose a new output directory; existing checkpoints are preserved")
    torch.set_num_threads(4)
    torch.manual_seed(args.seed)
    np.random.seed(args.seed)
    torch.use_deterministic_algorithms(True)
    device = torch.device(args.device)
    train = [prepare_episode(load_episode(p)) for p in split_paths(args.manifest, "train")]
    validation = [prepare_episode(load_episode(p)) for p in split_paths(args.manifest, "validation")]
    model = PosePredictor(args.hidden_size).to(device)
    all_x = torch.cat([ep["x"] for ep in train])
    residuals = torch.cat([ep["target"]-ep["base"] for ep in train])
    floors = torch.tensor([1e-4]*3+[1e-3]*3+[1e-4]*3+[1e-3]*3)
    model.input_mean.copy_(all_x.mean(0).to(device))
    model.input_scale.copy_(all_x.std(0).clamp_min(1e-3).to(device))
    model.target_scale.copy_(torch.maximum(residuals.std(0), floors).to(device))
    optimizer = torch.optim.AdamW(model.parameters(), lr=1e-3, weight_decay=1e-4)
    best_loss = validation_loss(model, validation, device)
    best_state = {key: value.detach().cpu().clone() for key, value in model.state_dict().items()}
    best_epoch = 0
    history = [{"epoch": 0, "validation_loss": best_loss}]
    for epoch in range(1, args.epochs+1):
        model.train()
        order = torch.randperm(len(train)).tolist()
        loss_sum, count = 0.0, 0
        for start in range(0, len(order), 16):
            episodes = [train[i] for i in order[start:start+16]]
            x, residual, mask = batch(episodes, device)
            optimizer.zero_grad()
            output, _ = model(x)
            loss = ((output-residual/model.target_scale)**2).mean(-1)[mask].mean()
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()
            loss_sum += float(loss.detach())*int(mask.sum())
            count += int(mask.sum())
        val_loss = validation_loss(model, validation, device)
        history.append({"epoch": epoch, "train_loss": loss_sum/count, "validation_loss": val_loss})
        if val_loss < best_loss:
            best_loss, best_epoch = val_loss, epoch
            best_state = {key: value.detach().cpu().clone() for key, value in model.state_dict().items()}
        if epoch % 10 == 0:
            print(f"epoch={epoch} train={loss_sum/count:.5f} validation={val_loss:.5f} best={best_epoch}", flush=True)
        if epoch-best_epoch >= args.patience:
            break
    model.load_state_dict(best_state)
    model.eval()
    metrics = {}
    for name in ("learned", "persistence", "constant_velocity"):
        errors = torch.cat([predict(model, ep, None if name=="learned" else name)[1] for ep in validation])
        metrics[name] = {"mean_errors": errors.mean(0).tolist(),
                         "p95_errors": torch.quantile(errors, .95, dim=0).tolist()}
    checkpoint = {"model_state": best_state, "hidden_size": args.hidden_size,
                  "seed": args.seed, "best_epoch": best_epoch,
                  "manifest_sha256": file_hash(args.manifest), "torch_version": str(torch.__version__),
                  "prediction": "one control step; TCP and cube world poses"}
    torch.save(checkpoint, args.output_dir/"model.pt")
    report = {"best_epoch": best_epoch, "epochs_run": history[-1]["epoch"],
              "device": str(device), "train_episodes": len(train), "validation_episodes": len(validation),
              "train_transitions": sum(len(ep["x"]) for ep in train),
              "validation_transitions": sum(len(ep["x"]) for ep in validation),
              "error_order": ["tcp_position_m", "tcp_rotation_rad", "cube_position_m", "cube_rotation_rad"],
              "validation_metrics": metrics, "history": history,
              "model_sha256": file_hash(args.output_dir/"model.pt"),
              "manifest_sha256": file_hash(args.manifest)}
    (args.output_dir/"training.json").write_text(json.dumps(report, indent=2)+"\n")
    print(json.dumps({key:value for key,value in report.items() if key!="history"}, indent=2))


if __name__ == "__main__":
    main()

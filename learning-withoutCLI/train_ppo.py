"""THE TRAINING SCRIPT: edit SETTINGS, then run this file.

lift_task.py defines the world/measurements; ppo.py defines actor and critic.
The original ManiSkill PPO loop collects experience and adjusts the networks.
"""
from datetime import datetime, timezone
import hashlib
from importlib.metadata import version
import json
import os
from pathlib import Path
import subprocess
import sys
import uuid
import torch
from lift_task import ACTION_DESCRIPTION, ENV_ID, ENV_SETTINGS, HORIZON, INPUT_FIELDS, INPUT_SIZES, ORIGIN
from ppo import Agent, SOURCE_COMMIT, initialize_from_pretrained

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SOURCE = HERE / "examples" / "maniskill_pick_cube" / "ppo_upstream.py"
SETTINGS = {
    "seed": 1,
    "total_timesteps": 10_001_250, # 3,175 whole rollouts, close to the reference 10M budget.
    "num_envs": 63,               # 21 parallel robots at each mass.
    "num_steps": 50,              # 63 * 50 = 3,150 transitions before learning.
    "num_minibatches": 7,         # 450 transitions per optimizer step.
    "num_eval_envs": 9,           # Three separate evaluation robots per mass.
    "num_eval_steps": 50,
    "eval_freq": 25,
    "learning_rate": 3e-4,
    "gamma": 0.8,
    "gae_lambda": 0.9,
    "update_epochs": 4,
    "clip_coef": 0.2,
    "ent_coef": 0.0,
    "vf_coef": 0.5,
    "max_grad_norm": 0.5,
    "target_kl": 0.1,
    "finite_horizon_gae": True,
    "partial_reset": True,       # Original training reset/final-value handling.
    "eval_partial_reset": False, # Check the entire attempt, including holding.
    "control_mode": "pd_ee_delta_pos",
    "sim_backend": "physx_cuda",
    "masses_kg": ENV_SETTINGS["masses_kg"],
    "goal_clearance_m": ENV_SETTINGS["goal_clearance_m"],
    "initialize_from_pretrained": True, # Optional start from the published working policy.
    "checkpoint": None,          # Alternatively continue from this setup's saved weights.
    "run_root": str(ROOT / "runs" / "learning"),
}


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load_checkpoint(path):
    path = Path(path).resolve()
    manifest_path = path.parent / "manifest.json"
    if not manifest_path.exists():
        raise ValueError("This checkpoint has no weighted-run manifest; old custom checkpoints require a new run")
    saved = json.loads(manifest_path.read_text())
    if (saved.get("artifact_origin") != ORIGIN or saved.get("input_sizes") != INPUT_SIZES
            or saved.get("action_description") != ACTION_DESCRIPTION):
        raise ValueError("Choose a new 43-input/four-output checkpoint; old custom checkpoints are incompatible")
    agent = Agent()
    agent.load_state_dict(torch.load(path, map_location="cpu", weights_only=True))
    agent.eval()
    return agent, saved


def main(settings=None):
    settings = {**SETTINGS, **(settings or {})}
    for key in ("total_timesteps", "num_envs", "num_steps", "num_minibatches", "num_eval_envs", "num_eval_steps", "eval_freq", "update_epochs"):
        if not isinstance(settings[key], int) or settings[key] <= 0:
            raise ValueError(f"{key} must be a positive integer")
    batch = settings["num_envs"] * settings["num_steps"]
    if settings["total_timesteps"] % batch or batch % settings["num_minibatches"] or batch // settings["num_minibatches"] < 2:
        raise ValueError("Use whole rollouts and evenly divided minibatches with at least two samples")
    if settings["eval_freq"] < 2 or settings["num_eval_steps"] % HORIZON:
        raise ValueError("Use eval_freq >= 2 and complete 50-step evaluation episodes")
    if settings["control_mode"] != "pd_ee_delta_pos" or settings["sim_backend"] not in ("physx_cpu", "physx_cuda"):
        raise ValueError("Use the native four-action controller and CPU/CUDA physics")
    masses = settings["masses_kg"]
    if not masses or any(not isinstance(m, (int, float)) or not 0 < m < float("inf") for m in masses):
        raise ValueError("Choose positive finite masses")
    if settings["sim_backend"] == "physx_cpu":
        if settings["num_envs"] != 1 or settings["num_eval_envs"] != 1:
            raise ValueError("CPU physics supports one robot; its mass cycles at reset")
    elif settings["num_envs"] % len(masses) or settings["num_eval_envs"] % len(masses):
        raise ValueError("Use equal numbers of GPU robots for each mass")
    torch.set_num_threads(4)
    torch.manual_seed(settings["seed"])
    name = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S") + "-" + uuid.uuid4().hex[:8]
    output = Path(settings["run_root"]).resolve() / name
    output.mkdir(parents=True, exist_ok=False)
    # Imports in the runtime resolve to these frozen sources.
    for filename in ("lift_task.py", "ppo.py", "train_ppo.py"):
        (output / filename).write_bytes((HERE / filename).read_bytes())
    pinned = output / "examples" / "maniskill_pick_cube"
    pinned.mkdir(parents=True)
    (pinned / "ppo_upstream.py").write_bytes(SOURCE.read_bytes())
    (pinned / "MANISKILL_LICENSE").write_bytes((HERE / "MANISKILL_LICENSE").read_bytes())
    original = SOURCE.read_text()
    old = 'env_kwargs = dict(obs_mode="state", render_mode="rgb_array", sim_backend="physx_cuda")'
    replacement = 'env_kwargs = ' + repr(dict(obs_mode="state", render_mode="rgb_array", sim_backend=settings["sim_backend"],
        render_backend="cpu", reward_mode="normalized_dense", masses_kg=masses, goal_clearance_m=settings["goal_clearance_m"],
        sensor_configs={"shader_pack": "minimal"}, human_render_camera_configs={"shader_pack": "minimal"}))
    if original.count(old) != 1:
        raise RuntimeError("Pinned upstream source changed")
    runtime = original.replace(old, replacement).replace("import mani_skill.envs\n", "import mani_skill.envs\nimport lift_task\n", 1)
    start, end = runtime.index("class Agent(nn.Module):"), runtime.index("class Logger:")
    runtime = runtime[:start] + "from ppo import Agent\n\n" + runtime[end:]
    runtime = runtime.replace("import torch\n", "import torch\ntorch.set_num_threads(4)\n", 1)
    runtime = runtime.replace("eval_envs.step(agent.get_action(eval_obs, deterministic=True))", "eval_envs.step(clip_action(agent.get_action(eval_obs, deterministic=True)))")
    runtime = runtime.replace("runs/{run_name}", "{run_name}")
    runtime = runtime.replace("torch.load(args.checkpoint)", "torch.load(args.checkpoint, map_location=device, weights_only=True)")
    (output / "ppo_runtime.py").write_text(runtime)
    initialization = dict(kind="random")
    checkpoint = settings["checkpoint"]
    if checkpoint:
        _, previous = load_checkpoint(checkpoint)
        if previous["settings"]["masses_kg"] != masses or previous["settings"]["goal_clearance_m"] != settings["goal_clearance_m"]:
            raise ValueError("Saved task settings differ; explicitly start a fresh experiment")
        checkpoint = str(Path(checkpoint).resolve())
        initialization = dict(kind="weighted_checkpoint", checkpoint=checkpoint, sha256=digest(checkpoint), optimizer_restarted=True)
    elif settings["initialize_from_pretrained"]:
        sys.path.insert(0, str(SOURCE.parent))
        from run_pretrained import download_model
        published, _, url = download_model("pd_ee_delta_pos")
        agent = initialize_from_pretrained(Agent(), published)
        checkpoint = str(output / "initialization.pt")
        torch.save(agent.state_dict(), checkpoint)
        initialization = dict(kind="published_42_input_policy", checkpoint=str(published), url=url,
                              sha256=digest(published), added_weight_column="zero", weight_input_initially_used=False)
    manifest = dict(artifact_origin=ORIGIN, environment=ENV_ID, observations=43, actions=4,
                    action_description=ACTION_DESCRIPTION, input_fields=INPUT_FIELDS, input_sizes=INPUT_SIZES,
                    settings=settings, horizon=HORIZON, initialization=initialization,
                    source_commit=SOURCE_COMMIT, source_sha256=digest(SOURCE),
                    task_sha256=digest(HERE / "lift_task.py"), model_sha256=digest(HERE / "ppo.py"),
                    versions={p: version(p) for p in ("torch", "mani_skill", "sapien")},
                    differences_from_example=["floating goal range", "varied physical masses/inertias", "true weight appended to 42 inputs",
                                              "smaller balanced parallel batch", "optional published-policy initialization"],
                    checkpoint_contents="model weights only; continuation restarts Adam and simulation", status="running")
    manifest_path = output / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
    (output / "settings.json").write_text(json.dumps(settings, indent=2) + "\n")
    command = [sys.executable, "-u", str(output / "ppo_runtime.py"), "--exp-name", str(output), "--env-id", ENV_ID, "--no-capture-video", "--no-track"]
    excluded = {"run_root", "masses_kg", "goal_clearance_m", "initialize_from_pretrained", "checkpoint", "sim_backend"}
    for key, value in settings.items():
        if key in excluded:
            continue
        flag = key.replace("_", "-")
        command.extend(["--" + ("" if value else "no-") + flag] if isinstance(value, bool) else ["--" + flag, str(value)])
    if checkpoint:
        command.extend(["--checkpoint", checkpoint])
    if settings["sim_backend"] == "physx_cpu":
        # Rebuild CPU scenes at reset to clear stale pairwise-contact caches.
        command.extend(["--no-cuda", "--reconfiguration-freq", "1"])
    child_env = dict(os.environ)
    child_env["LD_LIBRARY_PATH"] = "/usr/lib/wsl/lib:" + child_env.get("LD_LIBRARY_PATH", "")
    print("Weighted PickCube training:", output, flush=True)
    try:
        with (output / "console.log").open("w") as log:
            process = subprocess.Popen(command, cwd=ROOT, env=child_env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
            try:
                for line in process.stdout:
                    print(line, end="", flush=True)
                    log.write(line)
                    log.flush()
                code = process.wait()
            except BaseException:
                process.terminate()
                process.wait()
                raise
        manifest.update(status="complete" if code == 0 else "failed", exit_code=code)
        if code:
            raise RuntimeError("Training failed; see " + str(output / "console.log"))
    except BaseException:
        if manifest["status"] == "running":
            manifest["status"] = "interrupted_or_failed"
        raise
    finally:
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
    return output


if __name__ == "__main__":
    main()

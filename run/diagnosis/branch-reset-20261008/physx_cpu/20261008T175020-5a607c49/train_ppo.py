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
from lift_task import ACTION_DESCRIPTION, ENV_ID, ENV_SETTINGS, HORIZON, INPUT_FIELDS, INPUT_SIZES, ORIGIN, LEGACY_ORIGIN
from ppo import Agent, SOURCE_COMMIT, POLICY_ARCHITECTURE, initialize_from_pretrained
from hold_task import HOLD_ENV_ID

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SOURCE = HERE / "examples" / "maniskill_pick_cube" / "ppo_upstream.py"
SETTINGS = {
    "seed": 1,
    "training_stage": "hold_strength", # Hold the arm still; PPO learns only the strength branch.
    # Set training_stage="carry_strength" later to test strength learning during carrying.
    "total_timesteps": 1_002_000,  # Fine-tuning starting budget: 334 collect/learn cycles.
    "num_envs": 60,               # 12 robots at each of five physical masses.
    "num_steps": 50,              # 60 * 50 = 3,000 transitions before learning.
    "num_minibatches": 10,        # 300 transitions per optimizer step.
    "num_eval_envs": 10,          # Two separate evaluation robots per mass.
    "num_eval_steps": 50,
    "eval_freq": 25,
    "learning_rate": 1e-4,         # Smaller updates while extending the trained policy.
    "gamma": 0.8,
    "gae_lambda": 0.9,
    "update_epochs": 4,
    "clip_coef": 0.2,
    "ent_coef": 0.0,
    "vf_coef": 0.5,
    "max_grad_norm": 0.5,
    "target_kl": 0.1,
    "finite_horizon_gae": True,
    "partial_reset": False,      # Continue holding after reaching the target, until the time limit.
    "eval_partial_reset": False, # Check the entire attempt, including holding.
    "control_mode": "pd_ee_delta_pos",
    "sim_backend": "physx_cuda",
    "masses_kg": ENV_SETTINGS["masses_kg"],
    "goal_clearance_m": ENV_SETTINGS["goal_clearance_m"],
    "grip_force_limits_n": ENV_SETTINGS["grip_force_limits_n"],
    "grip_force_cost": ENV_SETTINGS["grip_force_cost"],
    "initialize_from_pretrained": True, # Fallback for checkpoint=None; published 42-input policy.
    "checkpoint": "latest",      # Newest completed grip-aware or previous weighted policy.
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
        raise ValueError("Choose a 45-input/five-output grip-aware checkpoint; train_ppo converts previous weighted policies")
    agent = initialize_from_pretrained(Agent(), path)
    agent.eval()
    return agent, saved


def latest_checkpoint(allow_legacy=False):
    """Select completed main-training models; exclude check runs and unsupported layouts."""
    choices = sorted((ROOT / "runs" / "learning").glob("*/final_ckpt.pt"),
                     key=lambda p: p.stat().st_mtime_ns, reverse=True)
    for path in choices:
        manifest = path.parent / "manifest.json"
        if not manifest.exists():
            continue
        saved = json.loads(manifest.read_text())
        if saved.get("status") != "complete":
            continue
        current = (saved.get("artifact_origin") == ORIGIN and
                   saved.get("input_sizes") == INPUT_SIZES and
                   saved.get("action_description") == ACTION_DESCRIPTION)
        legacy = (allow_legacy and saved.get("artifact_origin") == LEGACY_ORIGIN and
                  saved.get("observations") == 43 and saved.get("actions") == 4)
        if current or legacy:
            return path
    raise FileNotFoundError("No compatible completed training model. Set checkpoint=None to use the published policy.")


def main(settings=None):
    settings = {**SETTINGS, **(settings or {})}
    if settings['training_stage'] not in ('hold_strength', 'carry_strength'):
        raise ValueError('Choose hold_strength or carry_strength')
    if settings['training_stage'] == 'hold_strength' and (settings['partial_reset'] or settings['eval_partial_reset']):
        raise ValueError('Hold practice needs synchronized full resets: partial_reset=False and eval_partial_reset=False')
    training_env_id = HOLD_ENV_ID if settings['training_stage'] == 'hold_strength' else ENV_ID
    for key in ("total_timesteps", "num_envs", "num_steps", "num_minibatches", "num_eval_envs", "num_eval_steps", "eval_freq", "update_epochs"):
        if not isinstance(settings[key], int) or settings[key] <= 0:
            raise ValueError(f"{key} must be a positive integer")
    batch = settings["num_envs"] * settings["num_steps"]
    if settings["total_timesteps"] % batch or batch % settings["num_minibatches"] or batch // settings["num_minibatches"] < 2:
        raise ValueError("Use whole rollouts and evenly divided minibatches with at least two samples")
    if settings["eval_freq"] < 2 or settings["num_eval_steps"] % HORIZON:
        raise ValueError("Use eval_freq >= 2 and complete 50-step evaluation episodes")
    if settings["control_mode"] != "pd_ee_delta_pos" or settings["sim_backend"] not in ("physx_cpu", "physx_cuda"):
        raise ValueError("Use the native arm controller with strength extension and CPU/CUDA physics")
    masses = settings["masses_kg"]
    if not masses or any(not isinstance(m, (int, float)) or not 0 < m < float("inf") for m in masses):
        raise ValueError("Choose positive finite masses")
    if settings["sim_backend"] == "physx_cpu":
        if settings["num_envs"] != 1 or settings["num_eval_envs"] != 1:
            raise ValueError("CPU physics supports one robot; its mass cycles at reset")
    elif settings["num_envs"] % len(masses) or settings["num_eval_envs"] % len(masses):
        raise ValueError(f"With {len(masses)} masses, num_envs ({settings['num_envs']}) and num_eval_envs ({settings['num_eval_envs']}) must both be multiples of {len(masses)}")
    torch.set_num_threads(4)
    torch.manual_seed(settings["seed"])
    name = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S") + "-" + uuid.uuid4().hex[:8]
    output = Path(settings["run_root"]).resolve() / name
    output.mkdir(parents=True, exist_ok=False)
    # Imports in the runtime resolve to these frozen sources.
    for filename in ("lift_task.py", "hold_task.py", "grip_controller.py", "ppo.py", "train_ppo.py"):
        (output / filename).write_bytes((HERE / filename).read_bytes())
    pinned = output / "examples" / "maniskill_pick_cube"
    pinned.mkdir(parents=True)
    (pinned / "ppo_upstream.py").write_bytes(SOURCE.read_bytes())
    (pinned / "MANISKILL_LICENSE").write_bytes((HERE / "MANISKILL_LICENSE").read_bytes())
    original = SOURCE.read_text()
    old = 'env_kwargs = dict(obs_mode="state", render_mode="rgb_array", sim_backend="physx_cuda")'
    replacement = 'env_kwargs = ' + repr(dict(obs_mode="state", render_mode="rgb_array", sim_backend=settings["sim_backend"],
        render_backend="cpu", reward_mode="normalized_dense", masses_kg=masses, goal_clearance_m=settings["goal_clearance_m"],
        grip_force_limits_n=settings["grip_force_limits_n"], grip_force_cost=settings["grip_force_cost"],
        sensor_configs={"shader_pack": "minimal"}, human_render_camera_configs={"shader_pack": "minimal"}))
    if original.count(old) != 1:
        raise RuntimeError("Pinned upstream source changed")
    runtime = original.replace(old, replacement).replace("import mani_skill.envs\n", "import mani_skill.envs\nimport lift_task\nimport hold_task\n", 1)
    start, end = runtime.index("class Agent(nn.Module):"), runtime.index("class Logger:")
    runtime = runtime[:start] + "from ppo import Agent\n\n" + runtime[end:]
    runtime = runtime.replace("optim.Adam(agent.parameters(),", "optim.Adam((p for p in agent.parameters() if p.requires_grad),")
    runtime = runtime.replace("import torch\n", "import torch\ntorch.set_num_threads(4)\n", 1)
    runtime = runtime.replace("eval_envs.step(agent.get_action(eval_obs, deterministic=True))", "eval_envs.step(clip_action(agent.get_action(eval_obs, deterministic=True)))")
    runtime = runtime.replace("runs/{run_name}", "{run_name}")
    runtime = runtime.replace("torch.load(args.checkpoint)", "torch.load(args.checkpoint, map_location=device, weights_only=True)")
    (output / "ppo_runtime.py").write_text(runtime)
    initialization = dict(kind="random")
    checkpoint = settings["checkpoint"]
    if checkpoint:
        source_checkpoint = latest_checkpoint(allow_legacy=True) if checkpoint == "latest" else Path(checkpoint).resolve()
        previous = json.loads((source_checkpoint.parent / "manifest.json").read_text())
        if previous.get("artifact_origin") not in (ORIGIN, LEGACY_ORIGIN):
            raise ValueError("Choose a grip-aware or previous weighted training checkpoint")
        agent = initialize_from_pretrained(Agent(), source_checkpoint)
        checkpoint = str(output / "initialization.pt")
        torch.save(agent.state_dict(), checkpoint)
        initialization = dict(kind="latest_trained_policy" if settings["checkpoint"] == "latest" else "trained_policy",
                              checkpoint=str(source_checkpoint), sha256=digest(source_checkpoint),
                              source_observations=previous.get("observations"), source_actions=previous.get("actions"),
                              source_settings=previous.get("settings"), optimizer_restarted=True,
                              source_policy_architecture=previous.get("policy_architecture", "shared_actor"),
                              branch_initialization="copy trained actor into separate strength branch; freeze movement",
                              added_force_columns="zero when extending 43 inputs", added_strength_action="maximum when extending four actions")
    elif settings["initialize_from_pretrained"]:
        sys.path.insert(0, str(SOURCE.parent))
        from run_pretrained import download_model
        published, _, url = download_model("pd_ee_delta_pos")
        agent = initialize_from_pretrained(Agent(), published)
        checkpoint = str(output / "initialization.pt")
        torch.save(agent.state_dict(), checkpoint)
        initialization = dict(kind="published_42_input_policy", checkpoint=str(published), url=url,
                              sha256=digest(published), added_weight_and_force_columns="zero", added_strength_action="maximum", weight_input_initially_used=False)
    manifest = dict(artifact_origin=ORIGIN, environment=training_env_id, evaluation_environment=ENV_ID, observations=45, actions=5,
                    policy_architecture=POLICY_ARCHITECTURE, optimized_actions=["grip_strength_limit"],
                    frozen_actions=["x", "y", "z", "finger_opening"],
                    action_description=ACTION_DESCRIPTION, input_fields=INPUT_FIELDS, input_sizes=INPUT_SIZES,
                    settings=settings, horizon=HORIZON, initialization=initialization,
                    source_commit=SOURCE_COMMIT, source_sha256=digest(SOURCE),
                    task_sha256=digest(HERE / "lift_task.py"), model_sha256=digest(HERE / "ppo.py"), controller_sha256=digest(HERE / "grip_controller.py"),
                    versions={p: version(p) for p in ("torch", "mani_skill", "sapien")},
                    differences_from_example=["floating goal range", "varied physical masses/inertias", "true weight and measured finger forces appended to 42 inputs",
                                              "independent per-finger motor strength action", "held-goal success and measured-force cost",
                                              "smaller balanced parallel batch", "warm start from latest trained policy", "full-episode holding during training"],
                    training_stage=settings["training_stage"],
                    checkpoint_contents="model weights only; continuation restarts Adam and simulation", status="running")
    manifest_path = output / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
    (output / "settings.json").write_text(json.dumps(settings, indent=2) + "\n")
    command = [sys.executable, "-u", str(output / "ppo_runtime.py"), "--exp-name", str(output), "--env-id", training_env_id, "--no-capture-video", "--no-track"]
    excluded = {"training_stage", "run_root", "masses_kg", "goal_clearance_m", "initialize_from_pretrained", "checkpoint", "sim_backend", "grip_force_limits_n", "grip_force_cost"}
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
    print("Grip-strength branch training (" + settings["training_stage"] + "):", output, flush=True)
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

"""Run the article-inspired cube lift in ManiSkill. Edit SETTINGS, run this file.

lift_env.py describes the robot's world and score; model.py describes the actor
and critic. This launcher connects them to the pinned ManiSkill PPO training loop.
"""
from datetime import datetime, timezone
from importlib.metadata import version
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import uuid

from lift_env import ARTICLE_COMMIT, ARTICLE_URL, ENV_ID, HORIZON, INPUT_FIELDS, ORIGIN

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SOURCE = HERE.parent / "maniskill_pick_cube" / "ppo_upstream.py"
SOURCE_COMMIT = "a4a4f9272ad64b1564035874b605ceb687b63ed8"
SETTINGS = {
    "total_timesteps": 1_024_000,  # 160 collect-and-learn cycles with these settings.
    "num_envs": 64,               # Parallel robots collecting from the same policy.
    "num_steps": 100,             # 64 * 100 = 6,400 transitions per rollout.
    "num_minibatches": 8,         # 800 transitions per optimizer step.
    "num_eval_envs": 9,           # Three robots at each of the three masses.
    "num_eval_steps": 100,
    "eval_freq": 25,              # Periodic separate evaluation, before learning.
    "seed": 1,
    "control_mode": "pd_ee_delta_pos",  # Three XYZ changes, one finger opening.
    "learning_rate": 3e-4,
    "gamma": 0.99,
    "gae_lambda": 0.95,
    "update_epochs": 5,
    "clip_coef": 0.2,
    "partial_reset": False,       # Continue to 100 steps even after a lift succeeds.
    "eval_partial_reset": False,
}


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main(settings=None):
    settings = {**SETTINGS, **(settings or {})}
    for name in ("total_timesteps", "num_envs", "num_steps", "num_minibatches", "num_eval_envs", "num_eval_steps", "eval_freq", "update_epochs"):
        if not isinstance(settings[name], int) or settings[name] <= 0:
            raise ValueError(f"{name} must be a positive integer")
    if settings["control_mode"] != "pd_ee_delta_pos" or settings["partial_reset"] or settings["eval_partial_reset"]:
        raise ValueError("Use the four-action controller and continue until the time limit")
    if settings["num_eval_steps"] < HORIZON or settings["num_eval_steps"] % HORIZON:
        raise ValueError("num_eval_steps must contain whole evaluation episodes")
    if settings["eval_freq"] < 2:
        raise ValueError("The pinned baseline requires eval_freq >= 2")
    batch = settings["num_envs"] * settings["num_steps"]
    if settings["total_timesteps"] % batch or batch % settings["num_minibatches"] or batch // settings["num_minibatches"] < 2:
        raise ValueError("Divide total_timesteps into whole rollouts and rollouts into minibatches of at least two")
    name = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S") + "-" + uuid.uuid4().hex[:8]
    experiment = "article_inspired/cube_lift/" + name
    output = ROOT / "runs" / experiment
    output.mkdir(parents=True, exist_ok=False)
    # Preserve the precise task/model source used by this run beside its model.
    for filename in ("lift_env.py", "model.py"):
        (output / filename).write_bytes((HERE / filename).read_bytes())
    original = SOURCE.read_text()
    old = 'env_kwargs = dict(obs_mode="state", render_mode="rgb_array", sim_backend="physx_cuda")'
    new = 'env_kwargs = dict(obs_mode="state", render_mode="rgb_array", sim_backend="physx_cuda", render_backend="cpu", sensor_configs={"shader_pack": "minimal"}, human_render_camera_configs={"shader_pack": "minimal"})'
    if original.count(old) != 1:
        raise RuntimeError("Pinned ManiSkill source changed")
    runtime = original.replace(old, new).replace("import mani_skill.envs\n", "import mani_skill.envs\nimport lift_env\n", 1)
    start, end = runtime.index("class Agent(nn.Module):"), runtime.index("class Logger:")
    runtime = runtime[:start] + "from model import Agent\n\n" + runtime[end:]
    runtime = runtime.replace("import torch\n", "import torch\ntorch.set_num_threads(4)\n", 1)
    runtime = runtime.replace("eval_envs.step(agent.get_action(eval_obs, deterministic=True))",
                              "eval_envs.step(clip_action(agent.get_action(eval_obs, deterministic=True)))")
    (output / "ppo_runtime.py").write_text(runtime)
    manifest = {
        "artifact_origin": ORIGIN, "environment": ENV_ID,
        "article_url": ARTICLE_URL,
        "article_repository_commit": ARTICLE_COMMIT,
        "ppo_source_commit": SOURCE_COMMIT, "ppo_source_sha256": digest(SOURCE),
        "task_sha256": digest(HERE / "lift_env.py"), "model_sha256": digest(HERE / "model.py"),
        "settings": settings, "horizon": HORIZON, "masses_kg": [0.040, 0.064, 0.100],
        "input_fields": INPUT_FIELDS,
        "observations": 38, "actions": 4,
        "from_article": ["XYZ plus finger opening", "object and TCP pose/velocities and finger width", "LeakyReLU actor/critic widths", "fixed Gaussian variance 0.5", "learning rate 0.0003, gamma 0.99, clip 0.2, five epochs"],
        "adaptations": ["ManiSkill instead of PyBullet", "grasped 8 cm cube lift instead of sorting", "contact force and true weight observations", "fixed input scaling", "GAE and minibatches from ManiSkill PPO", "parallel GPU simulation", f"fixed {HORIZON}-step attempts continue after success", "CPU rendering", "four CPU threads", "WSL driver search path"],
        "versions": {package: version(package) for package in ("torch", "mani_skill", "sapien")},
        "status": "running",
    }
    manifest_path = output / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
    command = [sys.executable, "-u", str(output / "ppo_runtime.py"), "--exp-name", experiment,
               "--env-id", ENV_ID, "--no-capture-video", "--no-track"]
    for key, value in settings.items():
        flag = key.replace("_", "-")
        command.extend(["--" + ("" if value else "no-") + flag] if isinstance(value, bool) else ["--" + flag, str(value)])
    runtime_env = dict(os.environ)
    runtime_env["LD_LIBRARY_PATH"] = "/usr/lib/wsl/lib:" + runtime_env.get("LD_LIBRARY_PATH", "")
    print("Article-inspired cube lift output:", output, flush=True)
    with (output / "console.log").open("w") as log:
        process = subprocess.Popen(command, cwd=ROOT, env=runtime_env, stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT, text=True, bufsize=1)
        try:
            for line in process.stdout:
                print(line, end="", flush=True)
                log.write(line)
                log.flush()
            result = process.wait()
        except KeyboardInterrupt:
            process.terminate()
            process.wait()
            manifest["status"] = "interrupted"
            manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
            raise
    manifest.update(status="complete" if result == 0 else "failed", exit_code=result)
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
    if result:
        raise RuntimeError("Training failed; see " + str(output / "console.log"))
    return output


if __name__ == "__main__":
    main()

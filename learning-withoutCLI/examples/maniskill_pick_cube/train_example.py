"""Run the pinned ManiSkill PPO example. Edit SETTINGS, then run this file.

The upstream source is preserved beside this file. Only runtime environment
configuration is patched: CPU rendering and four PyTorch CPU threads.
The task, state observations, joint-delta actions, network and PPO remain upstream.
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

ROOT = Path(__file__).resolve().parents[3]
SOURCE = Path(__file__).with_name("ppo_upstream.py")
SOURCE_COMMIT = "a4a4f9272ad64b1564035874b605ceb687b63ed8"
SETTINGS = {
    "total_timesteps": 256000,
    "num_envs": 64,
    "num_eval_envs": 8,
    "num_steps": 50,
    "num_eval_steps": 100,
    "num_minibatches": 8,
    "eval_freq": 25,
    "seed": 1,
    "control_mode": "pd_joint_delta_pos",
}


def main(settings=None):
    settings = {**SETTINGS, **(settings or {})}
    batch_size = settings["num_envs"] * settings["num_steps"]
    if settings["total_timesteps"] < batch_size or settings["total_timesteps"] % batch_size:
        raise ValueError("total_timesteps must be a positive multiple of num_envs * num_steps")
    if batch_size % settings["num_minibatches"] or batch_size // settings["num_minibatches"] < 2:
        raise ValueError("Use minibatches with at least two samples and evenly dividing the batch")
    name = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S") + "-" + uuid.uuid4().hex[:8]
    experiment = "maniskill_example/pick_cube/" + name
    output = ROOT / "runs" / experiment
    output.mkdir(parents=True, exist_ok=False)
    original = SOURCE.read_text()
    old = 'env_kwargs = dict(obs_mode="state", render_mode="rgb_array", sim_backend="physx_cuda")'
    new = 'env_kwargs = dict(obs_mode="state", render_mode="rgb_array", sim_backend="physx_cuda", render_backend="cpu", sensor_configs={"shader_pack": "minimal"}, human_render_camera_configs={"shader_pack": "minimal"})'
    if original.count(old) != 1:
        raise RuntimeError("Pinned upstream environment configuration changed")
    runtime = original.replace(old, new).replace("import torch\n", "import torch\ntorch.set_num_threads(4)\n", 1)
    runtime_path = output / "ppo_runtime.py"
    runtime_path.write_text(runtime)
    manifest = {
        "artifact_origin": "official_maniskill_example",
        "environment": "PickCube-v1", "source_commit": SOURCE_COMMIT,
        "source_url": "https://github.com/mani-skill/ManiSkill/blob/" + SOURCE_COMMIT + "/examples/baselines/ppo/ppo.py",
        "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        "settings_overrides": settings,
        "runtime_adjustments": ["CPU minimal-shader rendering", "4 CPU threads", "WSL CUDA driver search path"],
        "unchanged": ["PickCube reward and success", "state observations", "controller", "network", "PPO calculations"],
        "versions": {name: version(name) for name in ("torch", "mani_skill", "sapien")},
        "status": "running",
    }
    manifest_path = output / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
    command = [sys.executable, "-u", str(runtime_path), "--exp-name", experiment,
               "--env-id", "PickCube-v1", "--no-capture-video", "--no-track"]
    for key, value in settings.items():
        command.extend(["--" + key.replace("_", "-"), str(value)])
    runtime_env = dict(os.environ)
    runtime_env["LD_LIBRARY_PATH"] = "/usr/lib/wsl/lib:" + runtime_env.get("LD_LIBRARY_PATH", "")
    print("Official ManiSkill example output:", output, flush=True)
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
    manifest["status"] = "complete" if result == 0 else "failed"
    manifest["exit_code"] = result
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
    if result:
        raise RuntimeError("Official example failed; see " + str(output / "console.log"))
    return output


if __name__ == "__main__":
    main()

"""THE COORDINATOR: run python learning-withoutCLI/train_ppo.py.

This is the only file you run to train. It imports the other files for you:
  lift_task.py = simulated task, measurements, reward and robot controller.
  ppo.py       = actor/critic networks and the calculations that teach them.

Start reading main(), following its numbered comments:
  set up -> observe -> choose -> move -> record -> learn -> save -> repeat.
The helper functions above main() are called when those jobs are needed.
Defining a function does not run it; the main() call at the bottom starts work.
The check_*.py scripts and 00_simulator_starter.py are separate, optional runs.
PPO adaptation provenance/license are in ppo.py.
"""

from copy import deepcopy
from datetime import datetime, timezone
from importlib.metadata import version
import json
from pathlib import Path
import uuid

import numpy as np
import torch

from lift_task import (
    ACTION_DESCRIPTION, INPUT_FIELDS, INPUT_SIZES, REWARD_SETTINGS,
    LiftTask, controller_action, read_inputs,
)
from ppo import Agent, SOURCE_COMMIT, generalized_advantages, update_ppo


# These settings describe the experiment; they are not learned network weights.
# STEP = one simulator action. EPISODE = one attempt, from reset to its end.
# ROLLOUT = the steps collected before learning; it can span several episodes.
# UPDATE = learning from one rollout, with several small optimizer steps inside.
# Small CPU starting experiment, NOT settings demonstrated to learn a grasp.
SETTINGS = {
    "seed": 0,
    "updates": 8,                 # 8 * 128 = 1,024 environment steps.
    "rollout_steps": 128,
    "episode_steps": 100,         # A time limit, not a success condition.
    "masses_kg": [0.040, 0.064, 0.100],  # Cycle each reset; fixed shape/friction.
    "hidden_size": 64,            # Separate actor/critic, two tanh layers each.
    "learning_rate": 3e-4,        # Adam; reference-style clipped PPO.
    "gamma": 0.99,
    "gae_lambda": 0.95,
    "update_epochs": 4,
    "minibatch_size": 32,
    "clip_coef": 0.2,
    "vf_coef": 0.5,
    "max_grad_norm": 0.5,
    "target_kl": 0.03,
    "position_step_m": 0.015,     # Maximum per-axis world TCP change per action.
    "rotation_step_rad": 0.10,    # Per-axis world XYZ Euler increment.
    "workspace_low_m": [-0.25, -0.25, 0.025],
    "workspace_high_m": [0.25, 0.25, 0.40],
    "max_force_n": 8.0,           # Desired normal force PER finger, not total.
    "force_gain_m_per_n": 0.0004, # Target-opening change per force error/step.
    "finger_step_m": 0.002,       # Bound each servo change; fingers move together.
    "save_every_updates": 2,     # Checkpoint every 256 steps, plus final/interrupt.
    "run_root": str(Path(__file__).resolve().parent.parent / "runs" / "learning"),
    "resume_from": None,         # Set to a saved .pt path, increase updates total.
}


def save_checkpoint(path, agent, optimizer, settings, counters, status):
    """Save tensors/primitives atomically; no simulator state or partial rollout."""
    # Save what has been learned AND Adam's bookkeeping, so learning can continue.
    # This is different from saving the robot's exact pose for replay.
    payload = {
        "schema_version": 1, "agent": agent.state_dict(),
        "optimizer": optimizer.state_dict(), "settings": deepcopy(settings),
        "counters": dict(counters), "status": status,
        "input_fields": INPUT_FIELDS, "input_sizes": INPUT_SIZES,
        "action_description": ACTION_DESCRIPTION, "reward_settings": REWARD_SETTINGS,
        "source_commit": SOURCE_COMMIT, "torch_rng_state": torch.get_rng_state(),
        "versions": {name: version(name) for name in ("torch", "mani_skill", "sapien")},
    }
    path = Path(path)
    temporary = path.with_suffix(".tmp")
    torch.save(payload, temporary)
    temporary.replace(path)
    print("Saved:", path, flush=True)


def load_checkpoint(path):
    """Return (model, saved data); model.get_action(x, deterministic=True) for use."""
    # Recreate the network structure, then fill it with previously learned weights.
    saved = torch.load(path, map_location="cpu", weights_only=True)
    if (saved["schema_version"] != 1 or saved["input_fields"] != INPUT_FIELDS
            or saved["input_sizes"] != INPUT_SIZES
            or saved["action_description"] != ACTION_DESCRIPTION
            or saved["reward_settings"] != REWARD_SETTINGS):
        raise ValueError("Checkpoint input/action/reward schema does not match this code")
    agent = Agent(saved["settings"]["hidden_size"])
    agent.load_state_dict(saved["agent"])
    agent.eval()
    return agent, saved


def reset_episode(env, settings, episode_index):
    """Change real mass/inertia before collecting a new episode's observations."""
    # Called for the first attempt and whenever an episode finishes.
    # reset() changes the simulation; it does NOT erase what the networks learned.
    mass = settings["masses_kg"][episode_index % len(settings["masses_kg"])]
    observation, _ = env.reset(seed=settings["seed"] + episode_index, options={"mass_kg": mass})
    inputs, vector = read_inputs(env, observation)
    actual_mass = float(env.cube.mass.item())
    gravity = torch.as_tensor(env.scene.px.get_config().gravity)
    weight = float(inputs["object_weight_n"].item())
    if not np.isclose(actual_mass, mass) or not np.isclose(weight, mass * float(gravity.norm())):
        raise RuntimeError("Policy weight does not match requested physical mass/gravity")
    return inputs, vector, actual_mass


def main(settings=None):
    # 1. SET UP: choose settings, create actor/critic, and create Adam to train them.
    settings = {**deepcopy(SETTINGS), **(settings or {})}
    for name in ("updates", "rollout_steps", "episode_steps", "hidden_size", "update_epochs", "minibatch_size", "save_every_updates"):
        if not isinstance(settings[name], int) or settings[name] <= 0:
            raise ValueError(f"{name} must be a positive integer")
    if settings["rollout_steps"] < 2 or settings["minibatch_size"] < 2:
        raise ValueError("PPO needs at least two samples per rollout/minibatch")
    if not settings["masses_kg"] or any(not np.isfinite(m) or m <= 0 for m in settings["masses_kg"]):
        raise ValueError("masses_kg must contain positive finite masses")
    torch.set_num_threads(4)
    torch.manual_seed(settings["seed"])
    agent = Agent(settings["hidden_size"])
    saved = None
    counters = dict(updates=0, steps=0, next_episode=0, completed_episodes=0, successes=0)
    if settings["resume_from"] is not None:
        agent, saved = load_checkpoint(settings["resume_from"])
        # Keep dynamics, model and optimizer settings consistent across resumption.
        flexible = {"updates", "save_every_updates", "run_root", "resume_from"}
        for key in settings.keys() - flexible:
            if settings[key] != saved["settings"][key]:
                raise ValueError(f"Resume setting mismatch: {key}")
        counters = dict(saved["counters"])
        if settings["updates"] <= counters["updates"]:
            raise ValueError("Set updates above the checkpoint's completed update count")
    # PPO defines the learning objective; Adam adjusts the weights to reduce it.
    optimizer = torch.optim.Adam(agent.parameters(), lr=settings["learning_rate"], eps=1e-5)
    if saved is not None:
        optimizer.load_state_dict(saved["optimizer"])

    run_name = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S") + "-" + uuid.uuid4().hex[:8]
    run_dir = Path(settings["run_root"]) / run_name
    run_dir.mkdir(parents=True, exist_ok=False)
    (run_dir / "settings.json").write_text(json.dumps(settings, indent=2) + "\n")
    print("Run:", run_dir, flush=True)
    # LiftTask is defined in lift_task.py. This creates the actual simulated task.
    env = LiftTask(control_mode="pd_ee_pose")
    events = (run_dir / "metrics.jsonl").open("w")
    try:
        # 2. OBSERVE: inputs is the named dictionary; vector is the same 21 numbers
        # laid out in a fixed order for the neural networks (shape: one row, 21).
        inputs, vector, mass = reset_episode(env, settings, counters["next_episode"])
        counters["next_episode"] += 1
        episode_return, episode_length = 0.0, 0
        if saved is not None:
            torch.set_rng_state(saved["torch_rng_state"])
            print("Resumed weights/optimizer/counters; starting a fresh episode.", flush=True)
        agent.train()  # Select training mode; this line does not update weights.
        # Outer loop: collect a rollout, learn from it, then collect another.
        for update in range(counters["updates"] + 1, settings["updates"] + 1):
            # Collect on-policy transitions. Each next value comes from the
            # actual post-action state BEFORE any episode reset.
            storage = {name: [] for name in (
                "inputs", "latents", "logprobs", "values", "rewards", "next_values",
                "terminated", "truncated",
            )}
            rollout_masses = set()
            # Inner loop: interact with the robot. Weights stay fixed here.
            for _ in range(settings["rollout_steps"]):
                # 3. CHOOSE: actor proposes an action; critic estimates future reward.
                # no_grad means "use the networks without building a learning graph".
                with torch.no_grad():
                    action, latent, logprob, value = agent.get_action_and_value(vector)
                # 4. MOVE: translate the policy's pose/force request to robot commands.
                # controller_action() prepares commands; env.step() advances physics.
                command, targets = controller_action(env, inputs, action, settings)
                observation, reward, terminated, truncated, info = env.step(command)
                if not torch.isfinite(reward).all() or not torch.equal(reward, info["task_score"]):
                    raise FloatingPointError("Invalid reward or custom reward bypassed")
                # LiftTask supplied the reward during step(). Now collect the NEW
                # measurements, so the next action responds to the robot's new state.
                next_inputs, next_vector = read_inputs(env, observation)
                with torch.no_grad():
                    next_value = agent.get_value(next_vector)
                episode_length += 1
                # terminated = task ended (success here); truncated = time ran out.
                truncated = truncated | torch.tensor([episode_length >= settings["episode_steps"]])
                # 5. RECORD: keep the old inputs, chosen action information, reward
                # and value estimates together. PPO will use this experience later.
                values = (vector[0], latent[0], logprob[0], value[0], reward[0],
                          next_value[0], terminated[0], truncated[0])
                for name, data in zip(storage, values):
                    storage[name].append(data.detach().clone())
                counters["steps"] += 1
                rollout_masses.add(mass)
                episode_return += float(reward.item())
                inputs, vector = next_inputs, next_vector
                # Ending an episode starts another attempt, possibly within the SAME
                # rollout. An episode ending does not itself trigger a PPO update.
                if bool((terminated | truncated).item()):
                    success = bool(info["success"].item())
                    counters["completed_episodes"] += 1
                    counters["successes"] += int(success)
                    record = dict(kind="episode", steps=counters["steps"], mass_kg=mass,
                                  length=episode_length, episode_return=episode_return,
                                  success=success, terminated=bool(terminated.item()),
                                  truncated=bool(truncated.item()))
                    events.write(json.dumps(record) + "\n")
                    print(f"Episode {counters['completed_episodes']}: mass={mass:.3f} kg "
                          f"return={episode_return:.3f} success={success}", flush=True)
                    inputs, vector, mass = reset_episode(env, settings, counters["next_episode"])
                    counters["next_episode"] += 1
                    episode_return, episode_length = 0.0, 0

            # 6. LEARN: the rollout is full. Turn its lists into tensors for PPO.
            batch = {name: torch.stack(data) for name, data in storage.items()}
            # Advantage: was the outcome better/worse than the critic expected?
            # Return: estimated future reward used as a target for the critic.
            batch["advantages"], batch["returns"] = generalized_advantages(
                batch["rewards"], batch["values"], batch["next_values"],
                batch["terminated"], batch["truncated"], settings["gamma"], settings["gae_lambda"],
            )
            if not all(torch.isfinite(data).all() for data in batch.values()):
                raise FloatingPointError("Nonfinite rollout")
            # This call in ppo.py actually changes the actor and critic weights.
            metrics = update_ppo(agent, optimizer, batch, settings)
            counters["updates"] = update
            record = dict(kind="update", **counters, **metrics, masses_kg=sorted(rollout_masses))
            events.write(json.dumps(record, allow_nan=False) + "\n")
            events.flush()
            print(f"Update {update}: steps={counters['steps']} "
                  f"policy_loss={metrics['policy_loss']:.4f} value_loss={metrics['value_loss']:.4f} "
                  f"parameter_change={metrics['parameter_change_l2']:.5f}", flush=True)
            # 7. SAVE when due. The next outer-loop iteration uses updated networks.
            if update % settings["save_every_updates"] == 0:
                save_checkpoint(run_dir / f"update_{update:04d}.pt", agent, optimizer, settings, counters, "periodic")
        save_checkpoint(run_dir / "final.pt", agent, optimizer, settings, counters, "complete")
    except KeyboardInterrupt:
        # Resuming drops any incomplete rollout/episode; an interrupted optimizer
        # update may be partial. This is a continuation, not exact replay.
        save_checkpoint(run_dir / "interrupted.pt", agent, optimizer, settings, counters, "interrupted")
        print("Interrupted; saved current weights and optimizer.", flush=True)
    finally:
        events.close()
        env.close()
    return run_dir


# Running this file starts main(). Importing it (e.g. from a check script) only
# makes its functions available; it does not automatically start training.
if __name__ == "__main__":
    main()

"""Optional integration checks: python learning-withoutCLI/checks/check_training.py.

Synthetic checks verify math; scripted contact verifies the servo; a 32-step
PPO run verifies plumbing. None of these is an evaluation of learned lifting.
Unlike check_reward.py, this DOES perform a tiny training run and save models.
It imports main() from train_ppo.py as train(), then calls it with small settings.
Normal training never calls this file; use it when checking that the parts work.
"""

import json
from pathlib import Path
import sys

import numpy as np
import torch
from torch.distributions import TanhTransform, TransformedDistribution
from mani_skill.utils.geometry.rotation_conversions import euler_angles_to_matrix, quaternion_to_matrix

# Make the main scripts importable when running this file directly.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from lift_task import INPUT_FIELDS, LiftTask, controller_action, normal_forces, read_inputs
from ppo import Agent, generalized_advantages
from train_ppo import SETTINGS, load_checkpoint, main as train, reset_episode, save_checkpoint


def check_ppo_math():
    # Terminal bootstrap must be zero; timeout bootstrap must use final state;
    # neither boundary may propagate advantages from the next episode.
    advantage, _ = generalized_advantages(
        torch.tensor([1., 2., 3., 4.]), torch.zeros(4), torch.tensor([10., 20., 30., 40.]),
        torch.tensor([False, True, False, False]), torch.tensor([False, False, True, False]), 0.9, 0.8,
    )
    assert torch.allclose(advantage, torch.tensor([11.44, 2., 30., 40.]))
    agent = Agent()
    inputs = torch.randn(4, 21)
    action, latent, logprob, _ = agent.get_action_and_value(inputs)
    reference = TransformedDistribution(agent.distribution(inputs), [TanhTransform()])
    assert torch.allclose(logprob, reference.log_prob(action).sum(-1), atol=2e-5)
    assert torch.equal(action, latent.tanh()) and (action.abs() <= 1).all()
    print("GAE boundaries and bounded-action likelihood checks passed.")


def check_mass_and_controller():
    env = LiftTask(control_mode="pd_ee_pose")
    try:
        inertia_per_kg = None
        for index, mass in enumerate(SETTINGS["masses_kg"]):
            inputs, vector, actual = reset_episode(env, SETTINGS, index)
            assert np.isclose(actual, mass)
            body = env.cube._bodies[0]
            ratio = np.array(body.inertia) / mass
            assert (ratio > 0).all()
            if inertia_per_kg is not None:
                assert np.allclose(ratio, inertia_per_kg)
            inertia_per_kg = ratio
            assert vector.shape == (1, 21) and torch.isfinite(vector).all()
            assert list(inputs) == INPUT_FIELDS
        original_pose = inputs[INPUT_FIELDS[0]].clone()
        action = torch.tensor([[0.4, -0.5, 0.6, 0.3, 0.4, -0.2, 0.0]])
        command, target = controller_action(env, inputs, action, SETTINGS)
        expected_position = original_pose[:, :3] + action[:, :3] * SETTINGS["position_step_m"]
        expected_rotation = euler_angles_to_matrix(action[:, 3:6] * SETTINGS["rotation_step_rad"], "XYZ") @ quaternion_to_matrix(original_pose[:, 3:])
        assert torch.allclose(target["tcp_pose_world_m_wxyz"][:, :3], expected_position)
        assert torch.allclose(quaternion_to_matrix(target["tcp_pose_world_m_wxyz"][:, 3:]), expected_rotation, atol=1e-5)
        arm = env.agent.controller.controllers["arm"]
        simulator_target = arm.root_link.pose * arm.compute_target_pose(arm.ee_pose_at_base, command[:, :6])
        assert torch.allclose(simulator_target.p, expected_position, atol=1e-5)
        assert torch.allclose(quaternion_to_matrix(simulator_target.q), expected_rotation, atol=1e-5)
        gripper = env.agent.controller.controllers["gripper"]
        decoded_grip = gripper._preprocess_action(command[:, 6:])
        assert torch.allclose(decoded_grip[:, 0], target["finger_position_target_m"], atol=1e-6)

        # Isolated servo checks use synthetic contacts along verified world axes.
        fake = {key: value.clone() for key, value in inputs.items()}
        fake[INPUT_FIELDS[3]].zero_()
        fake[INPUT_FIELDS[4]].zero_()
        action = torch.zeros(1, 7)  # Request 4 N per finger.
        env.force_finger_target_m = torch.tensor([0.03])
        _, low = controller_action(env, fake, action, SETTINGS)
        assert low["finger_position_target_m"].item() < 0.03
        left_axis = env.agent.finger1_link.pose.to_transformation_matrix()[:, :3, 1]
        right_axis = -env.agent.finger2_link.pose.to_transformation_matrix()[:, :3, 1]
        fake[INPUT_FIELDS[3]] = 12 * left_axis
        fake[INPUT_FIELDS[4]] = 12 * right_axis
        assert torch.allclose(normal_forces(env, fake), torch.full((1, 2), 12.), atol=1e-4)
        env.force_finger_target_m = torch.tensor([0.03])
        _, high = controller_action(env, fake, action, SETTINGS)
        assert high["finger_position_target_m"].item() > 0.03
        # Opening saturates; closing saturates; pose targets stay inside the box.
        env.force_finger_target_m = torch.tensor([0.04])
        action[:, 6] = -1
        _, released = controller_action(env, fake, action, SETTINGS)
        assert torch.allclose(released["finger_position_target_m"], torch.tensor([0.04]))
        fake[INPUT_FIELDS[3]].zero_()
        fake[INPUT_FIELDS[4]].zero_()
        env.force_finger_target_m = torch.tensor([-0.002])
        action[:, 6] = 1
        _, closed = controller_action(env, fake, action, SETTINGS)
        assert torch.allclose(closed["finger_position_target_m"], torch.tensor([-0.002]))
        fake[INPUT_FIELDS[0]][:, :3] = torch.tensor(SETTINGS["workspace_high_m"])
        action[:, :3] = 1
        _, bounded = controller_action(env, fake, action, SETTINGS)
        assert torch.equal(bounded["tcp_pose_world_m_wxyz"][:, :3], torch.tensor([SETTINGS["workspace_high_m"]]))
        # Real command passes through the simulator with valid finite inputs.
        obs, _, _, _, _ = env.step(command)
        _, vector = read_inputs(env, obs)
        assert torch.isfinite(vector).all()
        assert torch.allclose(arm._target_pose.p, (arm.root_link.pose.inv() * simulator_target).p, atol=1e-5)
        print("Physical mass/inertia/weight, pose frames, force sign and action bounds passed.")
    finally:
        env.close()


def check_scripted_contact():
    """Hand-scripted approach, not policy learning; compare 2 N vs 6 N requests."""
    env = LiftTask(control_mode="pd_ee_pose")
    measured = {}
    try:
        obs, _ = env.reset(seed=0, options={"mass_kg": 0.064})
        for phase, steps, force in [("approach", 25, 0.), ("contact_low", 30, 2.),
                                    ("contact_high", 30, 6.), ("release", 15, 0.)]:
            forces = []
            for _ in range(steps):
                inputs, _ = read_inputs(env, obs)
                action = torch.zeros(1, 7)
                target = env.cube.pose.p.clone()
                target[:, 2] = 0.025
                action[:, :3] = ((target - env.agent.tcp_pose.p) / SETTINGS["position_step_m"]).clamp(-1, 1)
                action[:, 6] = 2 * force / SETTINGS["max_force_n"] - 1
                command, _ = controller_action(env, inputs, action, SETTINGS)
                obs, _, _, _, _ = env.step(command)
                inputs, _ = read_inputs(env, obs)
                forces.append(normal_forces(env, inputs)[0].clone())
            measured[phase] = torch.stack(forces[-10:]).mean(0)
            print(phase, "mean measured normal force (N):", measured[phase].tolist())
        assert torch.isfinite(torch.stack(list(measured.values()))).all()
        assert (measured["contact_low"] > 0.5).all()
        assert (measured["contact_high"] > measured["contact_low"] + 1).all()
        assert (measured["release"] < 0.1).all()
        print("Scripted contact responds to force targets and releases; no learned lift tested.")
    finally:
        env.close()


def check_checkpoints(run_dir):
    run_dir = Path(run_dir)
    agent, saved = load_checkpoint(run_dir / "final.pt")
    records = [json.loads(line) for line in (run_dir / "metrics.jsonl").read_text().splitlines()]
    updates = [row for row in records if row["kind"] == "update"]
    assert all(row["parameter_change_l2"] > 0 for row in updates)
    assert all(row["optimizer_steps"] > 0 for row in updates)
    assert len({mass for row in updates for mass in row["masses_kg"]}) >= 2
    assert saved["optimizer"]["state"]
    optimizer = torch.optim.Adam(agent.parameters(), lr=saved["settings"]["learning_rate"], eps=1e-5)
    optimizer.load_state_dict(saved["optimizer"])
    probe = torch.randn(4, 21)
    with torch.no_grad():
        before = agent.get_action(probe, deterministic=True)
    copy_path = run_dir / "reload_check.pt"
    save_checkpoint(copy_path, agent, optimizer, saved["settings"], saved["counters"], "reload_check")
    loaded, _ = load_checkpoint(copy_path)
    with torch.no_grad():
        assert torch.equal(before, loaded.get_action(probe, deterministic=True))
    resume_settings = {**saved["settings"], "resume_from": str(run_dir / "final.pt"),
                       "updates": saved["counters"]["updates"] + 1}
    resumed_dir = train(resume_settings)
    _, resumed = load_checkpoint(resumed_dir / "final.pt")
    assert resumed["counters"]["steps"] == saved["counters"]["steps"] + saved["settings"]["rollout_steps"]
    assert resumed["counters"]["updates"] == saved["counters"]["updates"] + 1
    assert torch.equal(loaded.input_scale, agent.input_scale)
    print("Checkpoint deterministic actions match exactly; optimizer/counter resume passed.")


def main():
    torch.set_num_threads(4)
    check_ppo_math()
    check_mass_and_controller()
    check_scripted_contact()
    run_dir = train({"updates": 2, "rollout_steps": 16, "episode_steps": 8,
                     "minibatch_size": 8, "update_epochs": 2, "save_every_updates": 1,
                     "run_root": str(Path(__file__).resolve().parents[2] / "runs" / "checks" / "training")})
    check_checkpoints(run_dir)
    print("All training integration checks passed. This is not policy-quality validation.")


if __name__ == "__main__":
    main()

"""Optional reward check: python learning-withoutCLI/checks/check_reward.py.

Run this to inspect example scores or check reward edits. train_ppo.py does not
call this script. It checks the scoring rules, then one real simulator step;
it does not create or train an actor/critic.
"""

from pathlib import Path
import sys

import torch

# Make the main scripts importable when running this file directly.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from lift_task import LiftTask, REWARD_SETTINGS, reward_components


def main():
    # Synthetic conditions test the formula, not physically achieved grasps/lifts.
    names = ["far, no grasp", "near, no grasp", "grasp on table",
             "grasp + half lift", "grasp + full lift", "lifted WITHOUT grasp"]
    distance = torch.tensor([0.50, 0.01, 0.02, 0.02, 0.02, 0.01])
    height = REWARD_SETTINGS["lift_clearance_m"]
    clearance = torch.tensor([0.0, 0.0, 0.0, height / 2, height, height])
    grasped = torch.tensor([False, False, True, True, True, False])
    parts = reward_components(distance, clearance, grasped)
    scores = parts["task_score"]
    for i, name in enumerate(names):
        print(f"{name:24s} score={scores[i]:.4f} "
              f"reach={parts['reach_score'][i]:.4f} "
              f"grasp={parts['grasp_score'][i]:.4f} "
              f"lift={parts['lift_score'][i]:.4f}")
    assert torch.isfinite(scores).all() and ((0 <= scores) & (scores <= 1)).all()
    assert scores[0] < scores[1] < scores[2] < scores[3] < scores[4]
    assert scores[4] == 1 and scores[1] == scores[5]
    assert (parts["grasp_score"][~grasped] == 0).all()
    assert (parts["lift_score"][~grasped] == 0).all()
    assert parts["success"].tolist() == [False, False, False, False, True, False]
    # Check the full curves, including below-table and above-threshold heights.
    distances = torch.linspace(0, 1, 101)
    far_curve = reward_components(distances, torch.zeros(101), torch.zeros(101, dtype=torch.bool))
    assert (torch.diff(far_curve["task_score"]) <= 0).all()
    heights = torch.linspace(-height, 2 * height, 101)
    lift_curve = reward_components(torch.zeros(101), heights, torch.ones(101, dtype=torch.bool))
    assert (torch.diff(lift_curve["task_score"]) >= 0).all()
    assert torch.isfinite(lift_curve["task_score"]).all()
    assert ((0 <= lift_curve["task_score"]) & (lift_curve["task_score"] <= 1)).all()
    print("Synthetic reward checks passed. These are not learned behaviours.")

    # Use the familiar joint-position controller only for this one-step check.
    # The pose/force adapter is checked separately by check_training.py.
    env = LiftTask()
    try:
        observation, info = env.reset(seed=0)
        print("\nActual simulation after reset:")
        for name in ("distance_m", "clearance_m", "is_grasped", "reach_score",
                     "grasp_score", "lift_score", "task_score", "success"):
            print(name, info[name].item())
        env.action_space.seed(0)
        observation, reward, terminated, truncated, info = env.step(env.action_space.sample())
        assert torch.isfinite(reward).all() and ((0 <= reward) & (reward <= 1)).all()
        assert torch.equal(reward, info["task_score"])
        assert torch.equal(terminated, info["success"])
        assert torch.equal(reward, env.compute_normalized_dense_reward(observation, None, info))
        print("\nActual simulation after one random action:")
        for name in ("distance_m", "clearance_m", "is_grasped", "reach_score",
                     "grasp_score", "lift_score", "task_score", "success"):
            print(name, info[name].item())
        print("Simulation reward check passed; no policy was trained.")
    finally:
        env.close()


if __name__ == "__main__":
    main()

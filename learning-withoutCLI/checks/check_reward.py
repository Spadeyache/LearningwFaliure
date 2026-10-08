"""Optional check of physical observations and the force-aware lift reward."""
from pathlib import Path
import sys
import numpy as np
import torch
from mani_skill.envs.tasks.tabletop.pick_cube import PickCubeEnv
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from lift_task import LiftTask, read_inputs, normal_forces, WEIGHT_INPUT_INDEX


def main():
    torch.set_num_threads(4)
    env = LiftTask()
    try:
        for mass in (.04, .1, .5):
            obs, info = env.reset(seed=42, options={"mass_kg": mass, "reconfigure": True})
            _, vector = read_inputs(env, obs)
            assert vector.shape == (1, 45)
            assert np.isclose(vector[0, WEIGHT_INPUT_INDEX].item(), 9.81*mass)
            assert torch.allclose(vector[:,43:], normal_forces(env))
            assert env.goal_site.pose.p[0,2] >= env.cube_half_size + env.goal_clearance_m[0]
            for _ in range(5):
                action = torch.tensor([[0.,0.,0.,1.,0.]])
                obs, reward, _, _, info = env.step(action)
                original = PickCubeEnv.compute_dense_reward(env, obs, action, info)/5
                expected_cost = env.grip_force_cost * (normal_forces(env).mean(-1)/env.grip_force_limits_n[1]).clamp(0,1)
                assert torch.allclose(info["task_score"], original, atol=1e-6)
                assert torch.allclose(info["grip_force_cost"], expected_cost)
                assert torch.allclose(reward, original-expected_cost, atol=1e-6)
                assert torch.isfinite(reward).all()
                assert (reward >= -env.grip_force_cost-1e-6).all() and (reward <= 1+1e-6).all()
            print("Physical mass, weight/force observations and reward minus measured-force cost:", mass)
        print("Force-aware reward and observations passed.")
    finally:
        env.close()


if __name__ == "__main__":
    main()

"""Optional check of the original PickCube reward in our weighted environment."""
from pathlib import Path
import sys
import numpy as np
import torch
from mani_skill.envs.tasks.tabletop.pick_cube import PickCubeEnv
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from lift_task import LiftTask, read_inputs


def main():
    torch.set_num_threads(4)
    env = LiftTask()
    try:
        for mass in (.04, .064, .1):
            obs, info = env.reset(seed=42, options={"mass_kg": mass})
            _, vector = read_inputs(env, obs)
            assert vector.shape == (1, 43)
            assert np.isclose(vector[0,-1].item(), 9.81*mass)
            assert env.goal_site.pose.p[0,2] >= env.cube_half_size + env.goal_clearance_m[0]
            assert not info["success"].item()
            for _ in range(5):
                action = torch.tensor([[0.,0.,0.,1.]])
                obs, reward, _, _, info = env.step(action)
                original = PickCubeEnv.compute_dense_reward(env, obs, action, info)/5
                parts = sum(info[k] for k in ("reach_score","grasp_score","goal_score","static_score","success_bonus"))
                assert torch.allclose(reward, original, atol=1e-6)
                assert torch.allclose(reward, parts, atol=1e-6)
                assert torch.isfinite(reward).all() and (reward>=0).all() and (reward<=1+1e-6).all()
            print("Mass",mass,"weight N",vector[0,-1].item(),"goal",env.goal_site.pose.p.tolist(),"reward",reward.tolist())
        print("Original PickCube reward, floating goal and true physical weight checks passed.")
    finally:
        env.close()


if __name__ == "__main__":
    main()

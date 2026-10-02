"""Reset PickCube, save a camera image, and try one random action."""

from pathlib import Path

import gymnasium as gym
import mani_skill.envs  # Registers ManiSkill environments with Gymnasium.
from PIL import Image


# Change settings here, then run this file again.
seed = 0
render_backend = "cpu"
output_folder = Path(__file__).resolve().parent.parent / "checks" / "learning"

# 1. Create the simulator using the same settings as the working check script.
env = gym.make(
    "PickCube-v1",
    num_envs=2,
    obs_mode="state_dist+rgb",
    control_mode="pd_joint_pos",
    sim_backend="physx_cpu",
    render_backend=render_backend,
    sensor_configs={"shader_pack": "minimal"},
    human_render_camera_configs={"shader_pack": "minimal"},
)

try:
    # 2. Reset starts an episode and returns the first observation.
    observation, info = env.reset(seed=seed)

    # 3. Take the first environment's camera image and save it as a PNG.
    rgb = observation["sensor_data"]["base_camera"]["rgb"][0].cpu().numpy()
    output_folder.mkdir(parents=True, exist_ok=True)
    image_path = output_folder / "first_frame.png"
    Image.fromarray(rgb).save(image_path)
    print("Image shape:", rgb.shape)
    print("Image saved to:", image_path)

    # 4. Sample one random action and advance the simulation once.
    env.action_space.seed(seed)
    action = env.action_space.sample()
    observation, reward, terminated, truncated, info = env.step(action)
    print("Reward:", reward.item())
    print("Success:", info["success"].item())
finally:
    # Release simulator resources even if a step above raises an error.
    env.close()

# Our next learning steps:
# 1. Define observations. First inspect what the environment returns, then find
#    how to obtain object/gripper poses, object weight, gripper width and contact
#    force. Use true weight for training and estimated weight later.
# 2. Define the task and reward: what should the robot accomplish, and how will
#    we measure progress and success?
# 3. Connect a policy and PPO: collect experience and use it to update the model.
# 4. Run a short experiment to check that learning works before longer training.
# Immediate next step: inspect the observations returned by env.reset().

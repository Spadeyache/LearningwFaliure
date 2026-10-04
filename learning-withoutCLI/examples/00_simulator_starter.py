"""Reset PickCube, save a camera image, and try one random action."""

from pathlib import Path

import gymnasium as gym
import mani_skill.envs  # Registers ManiSkill environments with Gymnasium.
from PIL import Image
import torch


# Change settings here, then run this file again.
seed = 0
render_backend = "cpu"
output_folder = Path(__file__).resolve().parents[2] / "runs" / "examples"

# 1. Create the simulator using the same settings as the working check script.
env = gym.make(
    "PickCube-v1",
    num_envs=1,  # The CPU simulation backend supports one environment here.
    obs_mode="state_dict+rgb",
    control_mode="pd_joint_pos",
    sim_backend="physx_cpu",
    render_backend=render_backend,
    sensor_configs={"shader_pack": "minimal"},
    human_render_camera_configs={"shader_pack": "minimal"},
)

try:
    # 2. Reset starts an episode and returns the first observation.
    observation, info = env.reset(seed=seed)

    # unwrapped accesses the underlying PickCube task.
    # These reads do not advance physics, so they refer to the same initial state.
    task = env.unwrapped
    # Poses use world coordinates: [x, y, z, qw, qx, qy, qz].
    # Positions are in metres; orientation is a unit quaternion (w first).
    gripper_tcp_pose = observation["extra"]["tcp_pose"]
    object_pose = observation["extra"]["obj_pose"]

    # Read actual simulator mass (kg) and configured gravity (m/s^2).
    # Weight here means gravitational force magnitude in newtons: mass * |gravity|.
    object_mass_kg = task.cube.mass.reshape(-1, 1)  # One mass per environment.
    gravity_m_s2 = torch.as_tensor(task.scene.px.get_config().gravity)
    object_weight_n = object_mass_kg * torch.linalg.vector_norm(gravity_m_s2)

    # World-coordinate x/y/z forces on each finger from the cube, in newtons.
    # Just after reset, forces may be zero because contacts are not yet established.
    left_contact_force = task.scene.get_pairwise_contact_forces(
        task.agent.finger1_link, task.cube
    )
    right_contact_force = task.scene.get_pairwise_contact_forces(
        task.agent.finger2_link, task.cube
    )
    # Agreed inputs for a future policy; each tensor has one row per environment.
    # True weight is available in simulation; an estimator would supply it later.
    # Arm joints, gripper width and RGB are not included in these policy inputs.
    policy_inputs = {
        "gripper_tcp_pose_world_m_wxyz": gripper_tcp_pose,
        "object_pose_world_m_wxyz": object_pose,
        "object_weight_n": object_weight_n,
        "left_finger_cube_force_world_n": left_contact_force,
        "right_finger_cube_force_world_n": right_contact_force,
    }
    print("Initial policy inputs (before choosing an action):")
    for name, value in policy_inputs.items():
        print(name, ":", value)
    print("Diagnostic object mass (kg):", object_mass_kg)
    print("Diagnostic gravity vector (m/s^2):", gravity_m_s2)

    # 3. Save RGB for us to inspect visually, separate from future policy inputs.
    rgb = observation["sensor_data"]["base_camera"]["rgb"][0].cpu().numpy()
    output_folder.mkdir(parents=True, exist_ok=True)
    image_path = output_folder / "first_frame.png"
    Image.fromarray(rgb).save(image_path)
    print("Image shape:", rgb.shape)
    print("Image saved to:", image_path)

    # 4. Separate simulator check: sample a random joint-position action.
    # This does not use policy_inputs or implement the future pose/force outputs.
    env.action_space.seed(seed)
    action = env.action_space.sample()
    observation, reward, terminated, truncated, info = env.step(action)

    print("After action - reward:", reward.item())
    print("After action - success:", info["success"].item())
finally:
    # Release simulator resources even if a step above raises an error.
    env.close()

# Our next learning steps:
# 1. Inspect policy_inputs: current gripper TCP pose, object pose, object weight
#    in newtons, and separate left/right finger-object force vectors in newtons.
#    Use true simulator weight for initial training and a separate estimator later.
# Intended outputs: target gripper TCP pose (world metres + wxyz quaternion)
# and target grip force (newtons). A future policy and controller must produce
# and apply these targets; neither is implemented by this random-action check.

# 2. Define the task and reward: what should the robot accomplish, and how will
#    we measure progress and success?
# 3. Connect a policy and PPO: collect experience and use it to update the model.
# 4. Run a short experiment to check that learning works before longer training.
# Immediate next step: inspect the collected policy_inputs and their units.

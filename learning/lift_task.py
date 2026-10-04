"""CPU lift reward, agreed observations, and a simple pose/force adapter.

The reward check uses joint positions; train_ppo.py uses the pose/force adapter.
Its bounded feedback servo is approximate, not a physical-robot guarantee.
Only project code is changed; the installed ManiSkill library is untouched.
"""

import numpy as np
import torch
from mani_skill.envs.tasks.tabletop.pick_cube import PickCubeEnv
from mani_skill.utils.geometry.rotation_conversions import (
    euler_angles_to_matrix, matrix_to_euler_angles, matrix_to_quaternion,
    quaternion_multiply, quaternion_to_matrix,
)
from mani_skill.utils.structs.pose import Pose


INPUT_FIELDS = [
    "gripper_tcp_pose_world_m_wxyz", "object_pose_world_m_wxyz",
    "object_weight_n", "left_finger_cube_force_world_n",
    "right_finger_cube_force_world_n",
]
INPUT_SIZES = [7, 7, 1, 3, 3]
ACTION_DESCRIPTION = (
    "7 values in [-1,1]: world xyz increments, world XYZ Euler rotation "
    "increments, then per-finger normal contact force mapped to [0,max_force_n]. "
    "The adapter produces an absolute world TCP pose and finger position target."
)

# Editable starting choices, not universally optimal reward settings.
REWARD_SETTINGS = {
    "reach_scale_m": 0.10,  # At 10 cm, proximity is exp(-1), about 0.37.
    "lift_clearance_m": 0.08,  # Cube's lowest point must be 8 cm above the table.
    "reach_weight": 0.20,  # Some guidance before contact; most credit is for the task.
    "grasp_weight": 0.30,
    "lift_weight": 0.50,
}


def reward_components(distance_m, clearance_m, is_grasped, settings=REWARD_SETTINGS):
    """One bounded score from TCP-to-object distance, cube clearance and grasp.

    A confirmed grasp completes reaching, even when TCP and cube centres differ.
    Lift credit is zero without grasp. Force/slip penalties and holding time are
    deliberately absent. Grasp detection uses Panda's existing contact predicate.
    """
    weights = [settings[name] for name in ("reach_weight", "grasp_weight", "lift_weight")]
    if (not np.isfinite(weights).all() or min(weights) < 0
            or not np.isclose(sum(weights), 1.0)):
        raise ValueError("Reward weights must be nonnegative, finite and sum to 1")
    for name in ("reach_scale_m", "lift_clearance_m"):
        if not np.isfinite(settings[name]) or settings[name] <= 0:
            raise ValueError(f"{name} must be positive and finite")
    if not torch.isfinite(distance_m).all() or not torch.isfinite(clearance_m).all():
        raise ValueError("Distance and clearance must be finite")
    proximity = torch.exp(-distance_m.clamp_min(0) / settings["reach_scale_m"])
    grasp = is_grasped.float()
    reach = torch.where(is_grasped, torch.ones_like(proximity), proximity)
    lift = grasp * (clearance_m / settings["lift_clearance_m"]).clamp(0, 1)
    reach_score = settings["reach_weight"] * reach
    grasp_score = settings["grasp_weight"] * grasp
    lift_score = settings["lift_weight"] * lift
    return {
        "distance_m": distance_m,
        "clearance_m": clearance_m,
        "proximity": proximity,
        "reach_score": reach_score,
        "grasp_score": grasp_score,
        "lift_score": lift_score,
        "task_score": (reach_score + grasp_score + lift_score).clamp(0, 1),
        "success": is_grasped & (clearance_m >= settings["lift_clearance_m"]),
    }


def read_inputs(task, observation):
    """Read everything before another step; one row per environment, no images."""
    mass_kg = task.cube.mass.reshape(-1, 1)
    gravity = torch.as_tensor(task.scene.px.get_config().gravity)
    inputs = dict(zip(INPUT_FIELDS, [
        observation["extra"]["tcp_pose"],
        observation["extra"]["obj_pose"],
        mass_kg * torch.linalg.vector_norm(gravity),
        task.scene.get_pairwise_contact_forces(task.agent.finger1_link, task.cube),
        task.scene.get_pairwise_contact_forces(task.agent.finger2_link, task.cube),
    ]))
    # Cloning makes a snapshot that later physics steps cannot overwrite.
    inputs = {name: value.detach().clone().float() for name, value in inputs.items()}
    vector = torch.cat(list(inputs.values()), dim=1)
    if vector.shape != (1, 21) or not torch.isfinite(vector).all():
        raise ValueError("Expected 21 finite numerical inputs for one CPU environment")
    return inputs, vector


def normal_forces(task, inputs):
    """Compressive force on each finger, projected on its outward opening axis.

    These are the same axes used by installed Panda.is_grasping(). The world
    vectors are forces ON the fingers, so compression pushes each finger outward.
    Opposing vectors must never be added together to measure grip strength.
    """
    left_axis = task.agent.finger1_link.pose.to_transformation_matrix()[:, :3, 1]
    right_axis = -task.agent.finger2_link.pose.to_transformation_matrix()[:, :3, 1]
    left = (inputs[INPUT_FIELDS[3]] * left_axis).sum(1).clamp_min(0)
    right = (inputs[INPUT_FIELDS[4]] * right_axis).sum(1).clamp_min(0)
    return torch.stack([left, right], dim=1)


class LiftTask(PickCubeEnv):
    """Grasp and lift clear of the table; success terminates without a hold timer."""

    def __init__(self, settings=None, control_mode="pd_joint_pos"):
        self.settings = {**REWARD_SETTINGS, **(settings or {})}
        super().__init__(
            num_envs=1, obs_mode="state_dict", control_mode=control_mode,
            sim_backend="physx_cpu", render_backend="cpu", reward_mode="dense",
            sensor_configs={"shader_pack": "minimal"},
            human_render_camera_configs={"shader_pack": "minimal"},
        )

    def _initialize_episode(self, env_idx, options):
        super()._initialize_episode(env_idx, options)
        self.force_finger_target_m = None  # Reset the force servo's integral state.
        # PickCube resets upright on the table; its initial bottom gives table z.
        self.table_surface_z = self.cube.pose.p[:, 2].clone() - self.cube_half_size
        # The inherited goal is only a marker. Our reward never uses its position.
        self.goal_site.set_pose(Pose.create_from_pq(
            torch.tensor([[0.0, 0.0, float(self.table_surface_z.item())
                           + self.cube_half_size + self.settings["lift_clearance_m"]]])
        ))
        # Training passes an explicit mass. The reward check keeps the default.
        if "mass_kg" not in options:
            return
        mass = float(options["mass_kg"])
        if not np.isfinite(mass) or mass <= 0:
            raise ValueError("Mass must be positive and finite")
        # Actor exposes mass publicly, but inertia requires its SAPIEN body.
        # Scale existing inertia by the mass ratio: same shape/density distribution.
        body = self.cube._bodies[0]
        inertia = np.array(body.inertia, copy=True) * (mass / body.mass)
        body.set_mass(mass)
        body.set_inertia(inertia)
        if not np.isclose(body.mass, mass) or not np.allclose(body.inertia, inertia):
            raise RuntimeError("Physics mass/inertia update did not take effect")

    def evaluate(self):
        position = self.cube.pose.p
        # For a rotated cube, its vertical half-extent is h * sum(abs(R[z, :])).
        # This measures its LOWEST point, so tilting alone cannot fake clearance.
        rotation = quaternion_to_matrix(self.cube.pose.q)
        bottom_z = position[:, 2] - self.cube_half_size * rotation[:, 2, :].abs().sum(1)
        distance = torch.linalg.vector_norm(position - self.agent.tcp_pose.p, dim=1)
        grasped = self.agent.is_grasping(self.cube)
        components = reward_components(
            distance, bottom_z - self.table_surface_z, grasped, self.settings
        )
        return {
            "is_grasped": grasped,
            **components,
        }

    def compute_dense_reward(self, obs, action, info):
        return info["task_score"]

    def compute_normalized_dense_reward(self, obs, action, info):
        # Already normalized; do not inherit PickCube's division by five.
        return self.compute_dense_reward(obs, action, info)


def controller_action(task, inputs, action, settings):
    """Requires pd_ee_pose mode; unused by the joint-position reward check.

    Map a bounded policy action to an absolute pose and grip servo command.

    The force servo runs once per control step. It changes a position target,
    not the actuator force limit. It is an approximate feedback controller, not
    a guarantee of exact contact force or a validated physical-robot controller.
    """
    if action.shape != (1, 7) or not torch.isfinite(action).all() or (action.abs() > 1).any():
        raise ValueError("Policy action must be finite with shape (1, 7) in [-1,1]")
    current = inputs[INPUT_FIELDS[0]]
    target_position = current[:, :3] + settings["position_step_m"] * action[:, :3]
    target_position = target_position.clamp(
        torch.tensor(settings["workspace_low_m"]), torch.tensor(settings["workspace_high_m"])
    )
    delta_q = matrix_to_quaternion(euler_angles_to_matrix(
        settings["rotation_step_rad"] * action[:, 3:6], "XYZ"
    ))
    target_q = quaternion_multiply(delta_q, current[:, 3:])
    target_world = Pose.create_from_pq(target_position, target_q)

    # pd_ee_pose expects an absolute pose in the arm ROOT frame, with XYZ Euler
    # angles (not quaternion components). Use the actual root transform.
    arm = task.agent.controller.controllers["arm"]
    if arm.config.use_delta or arm.config.normalize_action:
        raise ValueError("The adapter requires absolute, unnormalized pd_ee_pose")
    target_root = arm.root_link.pose.inv() * target_world
    target_euler = matrix_to_euler_angles(quaternion_to_matrix(target_root.q), "XYZ")

    desired_force = settings["max_force_n"] * (action[:, 6] + 1) / 2
    measured = normal_forces(task, inputs)
    # Protect the more heavily loaded finger; the mimic gripper cannot command
    # the two fingers independently. Zero contact + positive demand closes it.
    error = desired_force - measured.max(dim=1).values
    change = (-settings["force_gain_m_per_n"] * error).clamp(
        -settings["finger_step_m"], settings["finger_step_m"]
    )
    gripper = task.agent.controller.controllers["gripper"]
    if task.force_finger_target_m is None:
        task.force_finger_target_m = gripper.qpos.mean(1).clone()
    # Zero requested grip releases the cube, even when both measured forces are 0.
    change = torch.where(desired_force < 0.05, settings["finger_step_m"], change)
    # Integrate force error into the target, with saturation preventing windup.
    # Finger position is used inside this controller, never as a policy input.
    finger_target = (task.force_finger_target_m + change).clamp(-0.002, 0.04)
    task.force_finger_target_m = finger_target.clone()
    # Installed Panda mimic controller normalizes [-0.01, 0.04] metres to [-1,1].
    low, high = float(gripper.config.lower), float(gripper.config.upper)
    grip_action = 2 * (finger_target - low) / (high - low) - 1
    command = task.agent.controller.from_action_dict({
        "arm": torch.cat([target_root.p, target_euler], dim=1),
        "gripper": grip_action[:, None],
    })
    low_bound = torch.as_tensor(task.action_space.low)
    high_bound = torch.as_tensor(task.action_space.high)
    if (not torch.isfinite(command).all() or (command < low_bound).any()
            or (command > high_bound).any()):
        raise ValueError("Pose/force adapter produced an invalid simulator command")
    targets = {
        "tcp_pose_world_m_wxyz": target_world.raw_pose.clone(),
        "grip_force_per_finger_n": desired_force.clone(),
        "measured_normal_forces_n": measured.clone(),
        "finger_position_target_m": finger_target.clone(),
    }
    return command, targets

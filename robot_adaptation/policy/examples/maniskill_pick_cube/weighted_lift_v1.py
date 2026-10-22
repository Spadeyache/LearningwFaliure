"""THE ENVIRONMENT: original PickCube, plus true weight and floating goals.

Carry the cube to the green target. Keep ManiSkill's robot, native four-action
controller, reward and success condition. Add real mass variation and one input.
"""
import numpy as np
import torch
from mani_skill.envs.tasks.tabletop.pick_cube import PickCubeEnv
from mani_skill.utils.common import flatten_state_dict
from mani_skill.utils.geometry.rotation_conversions import quaternion_to_matrix
from mani_skill.utils.registration import register_env
from mani_skill.utils.structs.pose import Pose

ENV_ID = "WeightedPickCube-v1"
HORIZON = 50
ORIGIN = "maniskill_weighted_pick_cube"
ENV_SETTINGS = {"masses_kg": [0.040, 0.064, 0.100], "goal_clearance_m": [0.10, 0.30]}
INPUT_FIELDS = ["joint_positions", "joint_velocities", "is_grasped", "tcp_pose_world_m_wxyz",
                "goal_position_world_m", "cube_pose_world_m_wxyz", "tcp_to_cube_world_m",
                "cube_to_goal_world_m", "object_weight_n"]
INPUT_SIZES = [9, 9, 1, 7, 3, 7, 3, 3, 1]
ACTION_DESCRIPTION = "4 native pd_ee_delta_pos actions: root-frame XYZ increments and finger opening (-1 closed, +1 open)"


def reward_components(distance, goal_distance, grasped, joint_speed, at_goal, static):
    """Expose the ORIGINAL normalized PickCube score for inspection."""
    reach = (1 - torch.tanh(5 * distance)) / 5
    grasp = grasped.float() / 5
    move = (1 - torch.tanh(5 * goal_distance)) * grasped / 5
    still = (1 - torch.tanh(5 * joint_speed)) * at_goal / 5
    bonus = torch.where(at_goal & static, 1 - reach - grasp - move - still, 0)
    return dict(reach_score=reach, grasp_score=grasp, goal_score=move, static_score=still,
                success_bonus=bonus, task_score=reach + grasp + move + still + bonus)


@register_env(ENV_ID, max_episode_steps=HORIZON)
class LiftTask(PickCubeEnv):
    def __init__(self, *args, masses_kg=None, goal_clearance_m=None, **kwargs):
        self.masses_kg = tuple(masses_kg if masses_kg is not None else ENV_SETTINGS["masses_kg"])
        self.goal_clearance_m = tuple(goal_clearance_m if goal_clearance_m is not None else ENV_SETTINGS["goal_clearance_m"])
        if not self.masses_kg or any(not np.isfinite(m) or m <= 0 for m in self.masses_kg):
            raise ValueError("masses_kg must contain positive finite masses")
        if (len(self.goal_clearance_m) != 2 or not np.isfinite(self.goal_clearance_m).all()
                or self.goal_clearance_m[0] <= .025 or self.goal_clearance_m[1] < self.goal_clearance_m[0]):
            raise ValueError("Choose an ordered floating-goal clearance range above the 2.5 cm goal tolerance")
        kwargs.setdefault("num_envs", 1)
        kwargs.setdefault("obs_mode", "state")
        kwargs.setdefault("control_mode", "pd_ee_delta_pos")
        kwargs.setdefault("sim_backend", "physx_cpu")
        kwargs.setdefault("render_backend", "cpu")
        kwargs.setdefault("reward_mode", "normalized_dense")
        kwargs.setdefault("sensor_configs", {"shader_pack": "minimal"})
        kwargs.setdefault("human_render_camera_configs", {"shader_pack": "minimal"})
        if kwargs["control_mode"] != "pd_ee_delta_pos" or kwargs["reward_mode"] != "normalized_dense":
            raise ValueError("Use the native four-action controller and normalized dense reward")
        self._cpu_episode = 0
        super().__init__(*args, **kwargs)

    @staticmethod
    def _set_mass(body, mass):
        inertia = np.array(body.inertia, copy=True) * float(mass) / body.mass
        body.set_mass(float(mass))
        body.set_inertia(inertia)
        if not np.isclose(body.mass, mass) or not np.allclose(body.inertia, inertia):
            raise RuntimeError("Physical mass/inertia assignment failed")

    def _load_scene(self, options):
        super()._load_scene(options)
        # GPU PhysX requires mass assignment BEFORE initialization. Each parallel
        # robot has one mass, retained across resets. Shape/friction stay fixed.
        for index, body in enumerate(self.cube._bodies):
            self._set_mass(body, self.masses_kg[index % len(self.masses_kg)])

    def _initialize_episode(self, env_idx, options):
        # CPU inspection can select a different physical mass each attempt.
        if not self.gpu_sim_enabled and "mass_kg" not in options:
            options = {**options, "mass_kg": self.masses_kg[self._cpu_episode % len(self.masses_kg)]}
            self._cpu_episode += 1
        if "mass_kg" in options:
            mass = float(options["mass_kg"])
            if not np.isfinite(mass) or mass <= 0:
                raise ValueError("mass_kg must be positive and finite")
            if self.gpu_sim_enabled:
                raise ValueError("For GPU simulation assign masses_kg when constructing the scene")
            for body in self.cube._bodies:
                self._set_mass(body, mass)
        super()._initialize_episode(env_idx, options)
        goal = self.goal_site.pose.p[env_idx].clone()
        low, high = self.goal_clearance_m
        # Random XY from PickCube; Z is a floating target for the CUBE centre.
        # This range expresses bottom clearance for an upright cube.
        goal[:, 2] = self.cube_half_size + low + (high - low) * torch.rand(len(env_idx), device=self.device)
        self.goal_site.set_pose(Pose.create_from_pq(goal))

    def _get_obs_extra(self, info):
        measurements = super()._get_obs_extra(info)
        gravity = torch.as_tensor(self.scene.px.get_config().gravity, device=self.device).norm()
        # Append LAST so the existing 42 entries retain exactly their order.
        measurements["object_weight_n"] = self.cube.mass.to(self.device).reshape(-1, 1) * gravity
        return measurements

    def evaluate(self):
        info = super().evaluate()  # Original cube-at-goal + stationary-arm success.
        distance = (self.cube.pose.p - self.agent.tcp_pose.p).norm(dim=-1)
        goal_distance = (self.cube.pose.p - self.goal_site.pose.p).norm(dim=-1)
        speed = self.agent.robot.get_qvel()[..., :-2].norm(dim=-1)
        rotation = quaternion_to_matrix(self.cube.pose.q)
        clearance = self.cube.pose.p[:, 2] - self.cube_half_size * rotation[:, 2].abs().sum(-1)
        return dict(info, distance_m=distance, goal_distance_m=goal_distance, clearance_m=clearance,
                    held_goal_success=info["success"] & info["is_grasped"],
                    **reward_components(distance, goal_distance, info["is_grasped"], speed,
                                        info["is_obj_placed"], info["is_robot_static"]))


def read_inputs(task, observation):
    """One row of 43 state measurements per robot: original 42 plus true weight."""
    vector = flatten_state_dict(observation, use_torch=True, device=task.device) if isinstance(observation, dict) else observation
    vector = vector.detach().clone().float()
    if vector.shape != (task.num_envs, 43) or not torch.isfinite(vector).all():
        raise ValueError("Expected 43 finite measurements per robot")
    inputs, start = {}, 0
    for name, size in zip(INPUT_FIELDS, INPUT_SIZES):
        inputs[name] = vector[:, start:start + size]
        start += size
    return inputs, vector


def normal_forces(task):
    """Log contact for us; raw forces are not additional policy inputs."""
    left = task.scene.get_pairwise_contact_forces(task.agent.finger1_link, task.cube)
    right = task.scene.get_pairwise_contact_forces(task.agent.finger2_link, task.cube)
    la = task.agent.finger1_link.pose.to_transformation_matrix()[:, :3, 1]
    ra = -task.agent.finger2_link.pose.to_transformation_matrix()[:, :3, 1]
    return torch.stack([(left * la).sum(-1).clamp_min(0), (right * ra).sum(-1).clamp_min(0)], dim=-1)

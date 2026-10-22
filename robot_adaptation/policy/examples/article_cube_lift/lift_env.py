"""The article's simpler control/state idea, adapted to our actual cube lift.

This is a ManiSkill task, not the author's PyBullet sorting environment.
The policy sees current measurements; it has no memory of previous attempts.
"""
import numpy as np
import torch
from mani_skill.envs.tasks.tabletop.pick_cube import PickCubeEnv
from mani_skill.sensors.camera import CameraConfig
from mani_skill.utils import sapien_utils
from mani_skill.utils.geometry.rotation_conversions import matrix_to_euler_angles, quaternion_to_matrix
from mani_skill.utils.registration import register_env
from mani_skill.utils.structs.pose import Pose

ENV_ID = "ArticleCubeLift-v1"
HORIZON = 100
ORIGIN = "article_inspired_cube_lift"
ARTICLE_URL = "https://hlfshell.ai/posts/ppo-pick-and-place/"
ARTICLE_COMMIT = "e13011177332b481eba9df9acfa3b4151cef29f5"
INPUT_FIELDS = {
    "cube_position_m": 3, "cube_euler_xyz_rad": 3,
    "cube_linear_velocity_m_s": 3, "cube_angular_velocity_rad_s": 3,
    "shape_one_hot_cube": 3, "cube_half_sizes_m": 3,
    "tcp_position_m": 3, "tcp_euler_xyz_rad": 3,
    "tcp_linear_velocity_m_s": 3, "tcp_angular_velocity_rad_s": 3,
    "finger_width_m": 1, "left_contact_force_world_n": 3,
    "right_contact_force_world_n": 3, "object_weight_n": 1,
}


def lift_scores(distance, clearance, grasped):
    """Reward reaching, grasping and lifting; completed lift earns most reward.

    Training continues to the time limit after success. Keeping the cube lifted
    keeps earning the maximum, so success does not cut off future reward.
    """
    reach = 1 - torch.tanh(5 * distance.clamp_min(0))
    grasp = grasped.float()
    lift = grasp * (clearance / 0.08).clamp(0, 1)
    success = grasped & (clearance >= 0.08)
    score = torch.where(success, torch.full_like(reach, 5), reach + grasp + lift)
    return dict(reach_score=reach / 5, grasp_score=grasp / 5,
                lift_score=lift / 5, success_bonus=torch.where(success, (5 - reach - grasp - lift) / 5, 0),
                task_score=score / 5, success=success)


@register_env(ENV_ID, max_episode_steps=HORIZON)
class ArticleCubeLift(PickCubeEnv):
    """One cube, 8 cm bottom clearance while grasped, four position actions."""

    def __init__(self, *args, masses_kg=(0.040, 0.064, 0.100), **kwargs):
        self.masses_kg = tuple(float(mass) for mass in masses_kg)
        if not self.masses_kg or any(not np.isfinite(mass) or mass <= 0 for mass in self.masses_kg):
            raise ValueError("masses_kg must contain positive finite masses")
        kwargs.setdefault("control_mode", "pd_ee_delta_pos")
        if kwargs["control_mode"] != "pd_ee_delta_pos":
            raise ValueError("This experiment uses XYZ movement plus finger opening")
        super().__init__(*args, **kwargs)

    def _load_scene(self, options):
        super()._load_scene(options)
        # Set real masses AND inertias before GPU simulation is initialized.
        # Each parallel environment keeps its assigned mass across resets.
        for index, body in enumerate(self.cube._bodies):
            mass = self.masses_kg[index % len(self.masses_kg)]
            inertia = np.array(body.inertia, copy=True) * mass / body.mass
            body.set_mass(mass)
            body.set_inertia(inertia)
            if not np.isclose(body.mass, mass) or not np.allclose(body.inertia, inertia):
                raise RuntimeError("Physical cube mass/inertia did not update")

    def _initialize_episode(self, env_idx, options):
        super()._initialize_episode(env_idx, options)
        # A fixed visual height marker; reward measures actual bottom clearance.
        marker = self.cube.pose.p[env_idx].clone()
        marker[:, 2] = self.cube_half_size + 0.08
        self.goal_site.set_pose(Pose.create_from_pq(marker))

    def _get_obs_agent(self):
        # Supply our explicit input list instead of inherited qpos/qvel fields.
        return {}

    def _get_obs_extra(self, info):
        cube, tcp = self.cube, self.agent.tcp
        rotation = lambda pose: matrix_to_euler_angles(quaternion_to_matrix(pose.q), "XYZ")
        n = self.num_envs
        return dict(zip(INPUT_FIELDS, [
            cube.pose.p, rotation(cube.pose), cube.linear_velocity, cube.angular_velocity,
            torch.tensor([1., 0., 0.], device=self.device).expand(n, -1),
            torch.full((n, 3), self.cube_half_size, device=self.device),
            tcp.pose.p, rotation(tcp.pose), tcp.linear_velocity, tcp.angular_velocity,
            self.agent.robot.get_qpos()[:, -2:].sum(-1, keepdim=True),
            self.scene.get_pairwise_contact_forces(self.agent.finger1_link, cube),
            self.scene.get_pairwise_contact_forces(self.agent.finger2_link, cube),
            cube.mass.to(self.device).reshape(-1, 1) * torch.as_tensor(self.scene.px.get_config().gravity, device=self.device).norm(),
        ]))

    def evaluate(self):
        rotation = quaternion_to_matrix(self.cube.pose.q)
        bottom = self.cube.pose.p[:, 2] - self.cube_half_size * rotation[:, 2].abs().sum(-1)
        distance = (self.cube.pose.p - self.agent.tcp_pose.p).norm(dim=-1)
        grasped = self.agent.is_grasping(self.cube)
        return dict(is_grasped=grasped, distance_m=distance, clearance_m=bottom,
                    **lift_scores(distance, bottom, grasped))

    def compute_dense_reward(self, obs, action, info):
        return 5 * info["task_score"]

    def compute_normalized_dense_reward(self, obs, action, info):
        return info["task_score"]


class ViewingTask(ArticleCubeLift):
    @property
    def _default_human_render_camera_configs(self):
        original = super()._default_human_render_camera_configs
        eye = list(self.human_cam_eye_pos)
        eye[1] = -eye[1]
        other = CameraConfig("front_left_top", sapien_utils.look_at(eye=eye, target=self.human_cam_target_pos),
                             512, 512, 1, 0.01, 100)
        return [original, other]

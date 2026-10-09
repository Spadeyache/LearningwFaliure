"""STRENGTH PRACTICE: begin with a real grasp; hold the arm still.

Place the cube between the fingers and settle it with native position drives.
Only the fifth policy action is applied during this stage. No cube is attached
or locked to the hand: weak gripping can physically drop it. The trained policy
can then be inspected in the ordinary carrying environment.
"""
import torch
from mani_skill.utils.registration import register_env
from mani_skill.utils.structs.pose import Pose
from lift_task import LiftTask, HORIZON

HOLD_ENV_ID = 'GripWeightedHoldCube-v1'


@register_env(HOLD_ENV_ID, max_episode_steps=HORIZON)
class HoldStrengthTask(LiftTask):
    def __init__(self, *args, **kwargs):
        self._hold_target = None
        super().__init__(*args, **kwargs)

    def _holding_action(self, strength):
        arm = self.agent.controller.controllers['arm']
        action = torch.zeros((self.num_envs, 5), device=self.device)
        action[:, :3] = ((self._hold_target - arm.ee_pose_at_base.p) / .1).clamp(-1, 1)
        action[:, 3] = -1.  # Keep fingers commanded closed; motor cap controls squeeze.
        action[:, 4] = strength
        return action

    def reset(self, seed=None, options=None):
        options = options or {}
        # Warm-up steps affect the whole PhysX scene. This synchronized practice
        # stage therefore resets all robots together, not an active subset.
        if 'env_idx' in options and len(options['env_idx']) != self.num_envs:
            raise ValueError('Hold-strength practice needs synchronized full resets; use partial_reset=False')
        # BaseEnv calls reset once while still constructing action spaces.
        # Physical preparation starts at the normal public reset after setup.
        if not hasattr(self, '_orig_single_action_space'):
            return super().reset(seed=seed, options=options)
        _, reset_info = super().reset(seed=seed, options=options)
        self._hold_target = self.agent.controller.controllers['arm'].ee_pose_at_base.p.clone()
        pose = self.agent.tcp_pose
        self.cube.set_pose(Pose.create_from_pq(pose.p.clone(), pose.q.clone()))
        self.cube.set_linear_velocity(torch.zeros((self.num_envs, 3), device=self.device))
        self.cube.set_angular_velocity(torch.zeros((self.num_envs, 3), device=self.device))
        qpos = self.agent.robot.get_qpos().clone()
        qpos[:, -2:] = self.cube_half_size + .001  # Just outside the 4 cm cube.
        self.agent.robot.set_qpos(qpos)
        self.agent.robot.set_qvel(torch.zeros_like(qpos))
        if self.gpu_sim_enabled:
            self.scene._gpu_apply_all()
            self.scene.px.gpu_update_articulation_kinematics()
            self.scene._gpu_fetch_all()
        self.agent.controller.reset()
        # Establish physical finger contact before the first PPO observation.
        # Preparation transitions are excluded from rewards/rollouts/time limits.
        for _ in range(10):
            super().step(self._holding_action(torch.ones(self.num_envs, device=self.device)))
        self.goal_site.set_pose(Pose.create_from_pq(self.cube.pose.p.clone()))
        if self.gpu_sim_enabled:
            # Unlike initialization inside BaseEnv.reset, this target placement
            # happens after warm-up: apply it or the next GPU fetch restores the
            # old random goal and a correctly held cube gets marked unsuccessful.
            self.scene._gpu_apply_all()
            self.scene._gpu_fetch_all()
        info = self.get_info()
        if not (info['is_grasped'] & (info['clearance_m'] > .06)).all():
            raise RuntimeError('Hold preparation did not produce a real airborne grasp')
        self._elapsed_steps.zero_()
        info = self.get_info()
        info['reconfigure'] = reset_info['reconfigure']
        obs = self.get_obs(info)
        self._last_obs = obs
        return obs, info

    def step(self, action):
        # Movement/opening are supplied by the fixed holding controller. PPO's
        # only stochastic decision is strength, so its likelihood is one-dimensional.
        result = super().step(self._holding_action(action[:, 4]))
        return result

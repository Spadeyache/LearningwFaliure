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

    def _place_cube_in_fingers(self, env_idx):
        """Prepare only the requested robots; keep successful grasps in place."""
        pose = self.cube.pose.raw_pose.clone()
        pose[env_idx] = self.agent.tcp_pose.raw_pose[env_idx]
        self.cube.set_pose(Pose.create(pose))
        linear = self.cube.linear_velocity.clone()
        angular = self.cube.angular_velocity.clone()
        linear[env_idx] = 0
        angular[env_idx] = 0
        self.cube.set_linear_velocity(linear)
        self.cube.set_angular_velocity(angular)
        qpos = self.agent.robot.get_qpos().clone()
        qvel = self.agent.robot.get_qvel().clone()
        qpos[env_idx, -2:] = self.cube_half_size + .001
        qvel[env_idx] = 0
        self.agent.robot.set_qpos(qpos)
        self.agent.robot.set_qvel(qvel)
        self._contacts_stale[env_idx] = True
        if self.gpu_sim_enabled:
            self.scene._gpu_apply_all()
            self.scene.px.gpu_update_articulation_kinematics()
            self.scene._gpu_fetch_all()
        self.agent.controller.reset()

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
        self._place_cube_in_fingers(torch.arange(self.num_envs, device=self.device))
        # Preparation is outside PPO: real contact must exist before returning
        # the first observation. A single ten-step settle can miss contact on
        # a rare randomized reset; allow settling, then re-seat only failed cubes.
        # Never turn a failed preparation into a successful training episode.
        self._hold_preparation_retries = 0
        for attempt in range(5):
            for _ in range(10):
                super().step(self._holding_action(torch.ones(self.num_envs, device=self.device)))
            info = self.get_info()
            ready = info['is_grasped'] & (info['clearance_m'] > .06)
            if ready.all():
                break
            if attempt == 4:
                failed = torch.nonzero(~ready).flatten().tolist()
                clearance = info['clearance_m'][~ready].tolist()
                raise RuntimeError(
                    f'Hold preparation failed after 50 steps: robots={failed}, '
                    f'clearance_m={clearance}. No invalid episode was returned.'
                )
            self._hold_preparation_retries += 1
            # First give the drives more time. If that does not recover contact,
            # reposition the failed cubes in the CURRENT hand pose and retry.
            if attempt >= 1:
                self._place_cube_in_fingers(torch.nonzero(~ready).flatten())
        self.goal_site.set_pose(Pose.create_from_pq(self.cube.pose.p.clone()))
        if self.gpu_sim_enabled:
            # Unlike initialization inside BaseEnv.reset, this target placement
            # happens after warm-up: apply it or the next GPU fetch restores the
            # old random goal and a correctly held cube gets marked unsuccessful.
            self.scene._gpu_apply_all()
            self.scene._gpu_fetch_all()
        info = self.get_info()
        self._elapsed_steps.zero_()
        info = self.get_info()
        info['reconfigure'] = reset_info['reconfigure']
        obs = self.get_obs(info)
        self._last_obs = obs
        return obs, info

    def step(self, action):
        # Movement/opening are supplied by the fixed holding controller. PPO's
        # only stochastic decision is strength, so its likelihood is one-dimensional.
        applied = self._holding_action(action[:, 4])
        self.last_applied_action = applied.detach().clone()
        return super().step(applied)

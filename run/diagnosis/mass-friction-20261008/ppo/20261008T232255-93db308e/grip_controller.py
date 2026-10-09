"""GRIPPER CONTROL: keep Panda's finger-position drive, choose its strength limit.

The policy sends [opening, strength], both normalized to [-1, 1].
Opening retains ManiSkill's mapping. Strength sets a motor force limit PER FINGER,
not a target contact force. Contact forces remain physical measurements.
"""
from dataclasses import dataclass
import numpy as np
import torch
from gymnasium import spaces
from mani_skill.agents.controllers.base_controller import CombinedController
from mani_skill.agents.controllers.pd_joint_pos import PDJointPosMimicController, PDJointPosMimicControllerConfig


class StrengthGripperController(PDJointPosMimicController):
    def _initialize_action_space(self):
        super()._initialize_action_space()
        self.single_action_space = spaces.Box(
            np.array([self.config.lower, self.config.strength_min_n], dtype=np.float32),
            np.array([self.config.upper, self.config.strength_max_n], dtype=np.float32))
        self.force_limit_n = torch.full((self.scene.num_envs,), self.config.strength_max_n, device=self.device)
        self._applied_limits = None
        self.reset_env_idx = None

    def _apply_limits(self, limits):
        # SAPIEN's drive-property API takes Python scalars. Updating each robot's
        # native drive preserves its implicit PD integration on CPU and GPU.
        values = limits.detach().cpu().tolist()
        if values == self._applied_limits:
            return
        for joint in self.joints:
            for obj, cap in zip(joint._objs, values):
                obj.set_drive_properties(float(self.config.stiffness), float(self.config.damping),
                                         float(cap), "force")
        self._applied_limits = values
        self.force_limit_n.copy_(limits)

    def set_drive_property(self):
        super().set_drive_property()
        self._applied_limits = None
        self._apply_limits(self.force_limit_n)

    def reset(self):
        super().reset()
        # BaseEnv restores its scene mask before resetting controllers. The task
        # therefore passes the actual episode indices explicitly.
        if self.reset_env_idx is not None:
            limits = self.force_limit_n.clone()
            limits[self.reset_env_idx] = self.config.strength_max_n
            self._apply_limits(limits)
            self.reset_env_idx = None

    def set_action(self, action):
        decoded = self._preprocess_action(action)
        self._apply_limits(decoded[:, 1])
        # Same position-target calculation as native PDJointPosMimicController.
        self._step = 0
        self._start_qpos = self.qpos
        self._target_qpos[:, self.control_joint_indices] = decoded[:, :1]
        self._target_qpos[:, self.mimic_joint_indices] = (
            self._target_qpos[:, self.mimic_control_joint_indices] * self._multiplier[None, :]
            + self._offset[None, :])
        if self.config.interpolate:
            self._step_size = (self._target_qpos - self._start_qpos) / self._sim_steps
        else:
            self.set_drive_targets(self._target_qpos)


@dataclass
class StrengthGripperConfig(PDJointPosMimicControllerConfig):
    strength_min_n: float = .25
    strength_max_n: float = 40.
    controller_cls = StrengthGripperController


def install_strength_controller(task):
    """Replace only the gripper controller; keep robot identity and arm config."""
    from dataclasses import asdict
    native = task.agent.controller
    configs = dict(native.configs)
    values = asdict(configs["gripper"])
    values.update(strength_min_n=task.grip_force_limits_n[0],
                  strength_max_n=task.grip_force_limits_n[1],
                  force_limit=task.grip_force_limits_n[1])
    configs["gripper"] = StrengthGripperConfig(**values)
    combined = CombinedController(configs, task.agent.robot, task.control_freq, scene=task.scene)
    combined.set_drive_property()
    task.agent.controllers[task.agent.control_mode] = combined

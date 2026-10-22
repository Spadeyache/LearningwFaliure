"""Panda pick/lift adapter and a seven-parameter waypoint skill for CREST.

This deliberately does not optimize millions of PPO network weights. CREST
requires a fixed low-level skill with a small, identifiable controller vector.
The skill reads TCP pose to track fixed waypoints; it never reads true mass,
friction, object motion, goal changes or an intervened context during execution.
Privileged simulator data is used only for optimization rewards and evaluation.
"""
from __future__ import annotations

import hashlib
import json

import numpy as np
import torch

from robot_adaptation.collection.design import FACTOR_NAMES, properties_for
from robot_adaptation.simulation.collection_lift import WeightedCollectionEnv

from .core import Evaluation

COLOR_FACTORS = ("object_color_r", "object_color_g", "object_color_b")
PARAMETER_NAMES = ("grasp_x_m", "grasp_y_m", "grasp_z_m", "lift_target_z_m",
                   "lift_speed_m_s", "close_duration_s", "grip_limit_n")


class CrestLiftEnv(WeightedCollectionEnv):
    def __init__(self, properties, *, object_color_rgb, **kwargs):
        self.crest_color = list(object_color_rgb)
        super().__init__(properties, **kwargs)

    def object_color_rgba(self):
        return self.crest_color + [1.]


class WaypointSkill:
    """Approach, descend, close, lift and hold at context-independent targets."""
    def __init__(self, theta, *, control_freq, delta_scale, grip_limits):
        self.theta = dict(zip(PARAMETER_NAMES, np.asarray(theta, float)))
        self.grasp = np.asarray(theta[:3], float)
        self.dt = 1 / control_freq
        self.delta_scale = float(delta_scale)
        self.grip_limits = grip_limits
        self.phase, self.elapsed = "approach", 0.
        self.lift_z = float(theta[2])

    def action(self, tcp):
        tcp = np.asarray(tcp, float)
        target = self.grasp.copy()
        opening = 1.
        if self.phase == "approach":
            target[2] += .10
            if np.linalg.norm(target - tcp) < .006:
                self.phase = "descend"
        elif self.phase == "descend":
            if np.linalg.norm(target - tcp) < .004:
                self.phase, self.elapsed = "close", 0.
        elif self.phase == "close":
            opening = -1.
            self.elapsed += self.dt
            if self.elapsed >= self.theta["close_duration_s"]:
                self.phase = "lift"
        else:
            opening = -1.
            self.lift_z = min(self.theta["lift_target_z_m"],
                              self.lift_z + self.theta["lift_speed_m_s"] * self.dt)
            target[2] = self.lift_z
        # Limit waypoint tracking speed during approach/descend as well.
        delta = target - tcp
        norm = np.linalg.norm(delta)
        if norm > .25 * self.dt:
            delta *= .25 * self.dt / norm
        low, high = self.grip_limits
        strength = 2 * (self.theta["grip_limit_n"] - low) / (high - low) - 1
        return np.clip(np.r_[delta / self.delta_scale, opening, strength], -1., 1.).astype(np.float32)


def scene_arguments(context):
    """Reuse physical factors, with an explicit origin for the spawn offsets.

    CREST's context must specify the actual pose. The old collector offsets a
    random seeded spawn; here offsets refer to a fixed upright origin, so reset
    seeds cannot secretly change object position/yaw outside the context vector.
    """
    properties = properties_for({name: context[name] for name in FACTOR_NAMES})
    properties["initial_pose_world"] = [0., 0., context["size"] / 2, 1., 0., 0., 0.]
    return dict(properties=properties,
                reported_mass_kg=.04,  # compatibility observation, not read by skill
                goal_clearance_m=context["goal_height"],
                spawn_offset_m=[context["spawn_x"], context["spawn_y"]],
                spawn_yaw_offset_rad=context["spawn_yaw"],
                object_color_rgb=[context[name] for name in COLOR_FACTORS])


class LiftingTask:
    def __init__(self, contexts, parameters, *, episode_steps=160, hold_steps=5,
                 grip_limits=(.25, 40.), on_evaluation=None):
        if parameters.names != PARAMETER_NAMES:
            raise ValueError(f"Lifting skill requires parameter order {PARAMETER_NAMES}")
        if (not 1 <= hold_steps <= episode_steps or len(grip_limits) != 2
                or not 0 < grip_limits[0] < grip_limits[1]):
            raise ValueError("Invalid lift horizon/hold duration/grip limits")
        force_index = parameters.names.index("grip_limit_n")
        if parameters.low[force_index] < grip_limits[0] or parameters.high[force_index] > grip_limits[1]:
            raise ValueError("Controller grip search must lie within the physical motor limits")
        self.contexts, self.parameters = contexts, parameters
        self.episode_steps, self.hold_steps = episode_steps, hold_steps
        self.grip_limits = tuple(grip_limits)
        self.on_evaluation = on_evaluation
        self.env, self.env_key = None, None

    def validate_context(self, context):
        self.contexts.validate(context)
        expected = set(FACTOR_NAMES) | set(COLOR_FACTORS)
        if set(context) != expected:
            raise ValueError(f"Lift adapter needs the 18 collection factors and RGB: {sorted(expected)}")
        scene_arguments(context)  # checks geometry, COM, material and spawn validity

    def _environment(self, context):
        key = json.dumps(context, sort_keys=True, allow_nan=False)
        if key != self.env_key:
            self.close()
            self.env = CrestLiftEnv(**scene_arguments(context), grip_force_limits_n=self.grip_limits)
            self.env_key = key
        return self.env

    def initial_parameters(self, context, seed):
        self.validate_context(context)
        env = self._environment(context)
        env.reset(seed=seed, options={"reconfigure": True})
        position = env.cube.pose.p[0].detach().cpu().numpy()
        goal = env.goal_site.pose.p[0].detach().cpu().numpy()
        # Pose and task goal seed the search. Physics does not initialize strength.
        guess = np.r_[position, goal[2], .20, .4, 10.]
        return np.clip(guess, self.parameters.low, self.parameters.high)

    def evaluate(self, context, theta, seed):
        self.validate_context(context)
        self.parameters.validate(theta)
        env = self._environment(context)
        _, _ = env.reset(seed=seed, options={"reconfigure": True})
        arm = env.agent.controller.controllers["arm"]
        bounds = np.broadcast_to(np.asarray(arm.config.pos_upper, float), (3,))
        lower = np.broadcast_to(np.asarray(arm.config.pos_lower, float), (3,))
        if (not arm.config.use_delta or arm.config.frame != "root_translation"
                or not np.allclose(bounds, bounds[0]) or not np.allclose(lower, -bounds)):
            raise RuntimeError("Waypoint skill requires symmetric root-frame delta-position control")
        # Panda root is world-axis aligned in CollectionEnv; validate this assumption.
        root_q = env.agent.robot.pose.q[0].detach().cpu().numpy()
        if not np.allclose(np.abs(root_q), [1., 0., 0., 0.], atol=1e-6):
            raise RuntimeError("World-frame waypoint tracking requires an unrotated robot root")
        skill = WaypointSkill(theta, control_freq=env.control_freq,
                              delta_scale=bounds[0], grip_limits=self.grip_limits)
        initial_pose = env.cube.pose.raw_pose[0].detach().cpu().numpy().copy()
        initial_robot = env.agent.robot.get_qpos()[0].detach().cpu().numpy().copy()
        initial_state_hash = hashlib.sha256(np.r_[initial_pose, initial_robot].tobytes()).hexdigest()
        final_success = []
        peak_force = 0.
        best_distance = float("inf")
        max_clearance = 0.
        grasped_any = False
        with torch.inference_mode():
            for _ in range(self.episode_steps):
                tcp = env.agent.tcp_pose.p[0].detach().cpu().numpy()
                action = skill.action(tcp)
                _, _, _, _, info = env.step(torch.as_tensor(action[None], device=env.device))
                object_pos = env.cube.pose.p[0]
                goal = env.goal_site.pose.p[0]
                goal_error = float(torch.linalg.norm(goal - object_pos))
                grasped = bool(info["is_grasped"].item())
                clearance = float((object_pos[2] - env.support_height()[0]).item())
                max_clearance = max(max_clearance, clearance)
                grasped_any |= grasped
                best_distance = min(best_distance, float(torch.linalg.norm(object_pos - env.agent.tcp_pose.p[0])))
                final_success.append(bool(info["success"].item()) and clearance >= .02)
                for link in (env.agent.finger1_link, env.agent.finger2_link):
                    force = env.scene.get_pairwise_contact_forces(link, env.cube)
                    peak_force = max(peak_force, float(torch.linalg.norm(force)))
        success = all(final_success[-self.hold_steps:])
        progress = ((1 - np.tanh(10 * best_distance)) + 2 * int(grasped_any)
                    + 2 * min(1., max_clearance / context["goal_height"])
                    + (1 - np.tanh(10 * goal_error)))
        result = Evaluation(success, float(progress + 10 * success), dict(
            goal_error_m=goal_error, max_clearance_m=max_clearance,
            grasped_any=grasped_any, peak_pairwise_contact_force_n=peak_force,
            final_phase=skill.phase, hold_steps=self.hold_steps,
            initial_object_pose=initial_pose.tolist(), initial_state_sha256=initial_state_hash,
            physics=env.physics_readback(), object_color_rgb=list(env.crest_color),
            sim_freq_hz=env.sim_freq, control_freq_hz=env.control_freq,
        ))
        if self.on_evaluation:
            self.on_evaluation(context, theta, seed, result)
        return result

    def close(self):
        if self.env is not None:
            self.env.close()
        self.env, self.env_key = None, None

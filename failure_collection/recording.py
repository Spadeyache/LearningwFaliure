"""CPU recorder. Sensor proxies never contain oracle object/body attribution.

State arrays have T+1 rows, command/response arrays T rows, physics arrays T*K
rows. Exact object contacts, velocities and policy observations are sim-only.
"""
import numpy as np
from scipy.spatial.transform import Rotation

from .outcomes import classify_outcome


def array(value):
    if hasattr(value, "detach"):
        value = value.detach().cpu().numpy()
    return np.asarray(value).copy()


def first(value):
    return array(value)[0]


def rotation_delta(poses):
    rotations = Rotation.from_quat(poses[:, 3:], scalar_first=True)
    return (rotations[1:] * rotations[:-1].inv()).as_rotvec().astype(np.float32)


class EpisodeRecorder:
    def __init__(self, env, contact_threshold_n=0.05):
        self.env = env
        self.threshold = contact_threshold_n
        self.states, self.transitions, self.physics = [], [], []
        self.points, self.point_offsets = [], [0]
        self.fingers = [env.agent.finger1_link, env.agent.finger2_link]
        self.finger_entities = [link._bodies[0].entity for link in self.fingers]
        self.object_entity = env.cube._bodies[0].entity
        self.last_force = np.zeros((2, 3), dtype=np.float32)
        self.last_pair_force = self.last_force.copy()
        self.control_start = 0

    def physics_step(self, env):
        """Sample each actual physics step; impulse/dt is a substep mean force."""
        net = np.zeros((2, 3), dtype=np.float64)
        pair = net.copy()
        for contact in env.scene.px.get_contacts():
            entities = [body.entity for body in contact.bodies]
            for finger, entity in enumerate(self.finger_entities):
                if entity not in entities:
                    continue
                side = entities.index(entity)
                sign = 1 if side == 0 else -1
                for point in contact.points:
                    impulse = sign * np.asarray(point.impulse)
                    net[finger] += impulse
                    if entities[1 - side] == self.object_entity:
                        pair[finger] += impulse
                        self.points.append((finger, np.asarray(point.position).copy(),
                                            sign * np.asarray(point.normal), impulse.copy(),
                                            float(point.separation)))
        net = (net * env.sim_freq).astype(np.float32)
        pair = (pair * env.sim_freq).astype(np.float32)
        self.last_force, self.last_pair_force = net, pair
        tcp, obj = env.agent.tcp_pose, env.cube.pose
        finger_rotations = np.stack([first(f.pose.to_transformation_matrix())[:3, :3]
                                    for f in self.fingers])
        # Wrench proxy expressed in each finger link frame; total across all bodies.
        local = np.einsum("nji,nj->ni", finger_rotations, net)
        self.physics.append(dict(
            finger_net_force_world_n=net, finger_net_force_local_n=local,
            object_pair_force_world_n=pair,
            object_pose_tcp_m_wxyz=first((tcp.inv() * obj).raw_pose),
            object_pose_world_m_wxyz=first(obj.raw_pose),
            tcp_pose_world_m_wxyz=first(tcp.raw_pose),
            finger_width_m=float(env.agent.robot.get_qpos()[0, -2:].sum()),
        ))
        self.point_offsets.append(len(self.points))

    def snapshot(self, observation, info, initial=False):
        env = self.env
        obj, tcp = env.cube.pose, env.agent.tcp_pose
        qpos, qvel = first(env.agent.robot.get_qpos()), first(env.agent.robot.get_qvel())
        if initial:
            contact = False
        else:
            recent = self.physics[self.control_start:]
            contact = any(np.linalg.norm(p["object_pair_force_world_n"], axis=-1).max() > self.threshold
                          for p in recent)
        self.states.append(dict(
            object_pose_world_m_wxyz=first(obj.raw_pose),
            object_pose_tcp_m_wxyz=first((tcp.inv() * obj).raw_pose),
            tcp_pose_world_m_wxyz=first(tcp.raw_pose),
            finger_pose_world_m_wxyz=np.stack([first(f.pose.raw_pose) for f in self.fingers]),
            joint_position_rad_m=qpos, joint_velocity_rad_m_s=qvel,
            finger_width_m=float(qpos[-2:].sum()),
            finger_width_velocity_m_s=float(qvel[-2:].sum()),
            finger_net_force_world_n=self.last_force.copy(),
            object_linear_velocity_world_m_s=first(env.cube.linear_velocity),
            object_angular_velocity_world_rad_s=first(env.cube.angular_velocity),
            policy_observation=first(observation),
            object_contact=contact,
            is_grasped=False if initial else bool(info["is_grasped"].item()),
            task_success=bool(info["success"].item()),
            object_clearance_m=float((obj.p[:, 2] - env.support_height()).item()),
            at_goal=bool(info["is_obj_placed"].item()),
            robot_static=bool(info["is_robot_static"].item()),
        ))

    def begin_action(self):
        self.control_start = len(self.physics)

    def end_action(self, raw, applied, reward, terminated, truncated):
        env = self.env
        arm = env.agent.controller.controllers["arm"]
        gripper = env.agent.controller.controllers["gripper"]
        target_world = arm.root_link.pose * arm._target_pose
        self.transitions.append(dict(
            action_raw=first(raw), action_applied=first(applied),
            tcp_target_pose_world_m_wxyz=first(target_world.raw_pose),
            joint_target_rad_m=np.concatenate([first(arm._target_qpos), first(gripper._target_qpos)]),
            finger_joint_target_m=first(gripper._target_qpos),
            grip_motor_limit_n=np.broadcast_to(float(gripper.force_limit_n.item())
                if hasattr(gripper, "force_limit_n") else gripper.config.force_limit, (2,)).copy(),
            reward=float(reward.item()), terminated=bool(terminated.item()),
            truncated=bool(truncated.item()),
        ))

    def finish(self):
        env = self.env
        state = {k: np.asarray([row[k] for row in self.states]) for k in self.states[0]}
        trans = {k: np.asarray([row[k] for row in self.transitions]) for k in self.transitions[0]}
        phys = {k: np.asarray([row[k] for row in self.physics]) for k in self.physics[0]}
        t, k = len(self.transitions), env.sim_freq // env.control_freq
        if len(self.states) != t + 1 or len(self.physics) != t * k:
            raise RuntimeError("Incomplete action/state/physics alignment")
        sim_state = {"object_linear_velocity_world_m_s", "object_angular_velocity_world_rad_s",
                     "policy_observation", "object_contact", "is_grasped", "task_success",
                     "object_clearance_m", "at_goal", "robot_static"}
        result = {( "sim__" if name in sim_state else "input__") + name: value
                  for name, value in state.items()}
        for name, value in trans.items():
            prefix = "sim__" if name in ("reward", "terminated", "truncated") else "input__"
            result[prefix + name] = value
        for name, value in phys.items():
            prefix = "sim__" if name == "object_pair_force_world_n" else "input__"
            result[prefix + "physics_" + name] = value
        forces = phys["finger_net_force_world_n"].reshape(t, k, 2, 3)
        local_forces = phys["finger_net_force_local_n"].reshape(t, k, 2, 3)
        # Compression along each finger's closing axis, not a contact-normal oracle.
        compression = np.maximum(local_forces[:, :, :, 1] * [1, -1], 0)
        result.update({
            "input__object_tcp_distance_m": np.linalg.norm(state["object_pose_tcp_m_wxyz"][:, :3], axis=1),
            "input__object_goal_distance_m": np.linalg.norm(state["object_pose_world_m_wxyz"][:, :3]
                - first(env.goal_site.pose.p), axis=1),
            "input__finger_object_distance_m": np.linalg.norm(state["finger_pose_world_m_wxyz"][:, :, :3]
                - state["object_pose_world_m_wxyz"][:, None, :3], axis=-1),
            "sim__object_pair_force_mean_world_n": phys["object_pair_force_world_n"].reshape(t, k, 2, 3).mean(axis=1),
            "sim__object_pair_force_peak_norm_n": np.linalg.norm(phys["object_pair_force_world_n"].reshape(t, k, 2, 3), axis=-1).max(axis=1),
            "input__finger_force_mean_world_n": forces.mean(axis=1),
            "input__finger_force_peak_norm_n": np.linalg.norm(forces, axis=-1).max(axis=1),
            "input__finger_compression_mean_n": compression.mean(axis=1),
            "input__finger_force_imbalance_n": compression.mean(axis=1)[:, 0] - compression.mean(axis=1)[:, 1],
            "input__object_translation_response_world_m": np.diff(state["object_pose_world_m_wxyz"][:, :3], axis=0),
            "input__object_rotation_response_world_rotvec_rad": rotation_delta(state["object_pose_world_m_wxyz"]),
            "input__relative_translation_response_tcp_m": np.diff(state["object_pose_tcp_m_wxyz"][:, :3], axis=0),
            "input__relative_rotation_response_tcp_rotvec_rad": rotation_delta(state["object_pose_tcp_m_wxyz"]),
            "input__tcp_translation_response_world_m": np.diff(state["tcp_pose_world_m_wxyz"][:, :3], axis=0),
            "input__explicit_grip_point_world_m": np.full((t, 3), np.nan, dtype=np.float32),
            "meta__explicit_grip_point_available": np.asarray(False),
            "meta__force_valid_state": np.arange(t + 1) > 0,
            "input__finger_force_valid": np.arange(t + 1) > 0,
            "meta__state_time_s": np.arange(t + 1, dtype=np.float64) / env.control_freq,
            "meta__action_time_s": np.arange(t, dtype=np.float64) / env.control_freq,
            "meta__physics_time_s": (np.arange(t * k, dtype=np.float64) + 1) / env.sim_freq,
            "meta__physics_action_index": np.repeat(np.arange(t, dtype=np.int32), k),
            "meta__collection_horizon_reached": np.asarray(True),
        })
        # Object contact is an oracle event mask for alignment/labels, not a sensor.
        physics_contact = np.linalg.norm(phys["object_pair_force_world_n"], axis=-1).max(axis=1) > self.threshold
        result["sim__physics_object_contact"] = physics_contact
        result["sim__from_contact_state_mask"] = np.maximum.accumulate(state["object_contact"])
        result["sim__from_contact_physics_mask"] = np.maximum.accumulate(physics_contact)
        indices = np.flatnonzero(physics_contact)
        result["meta__first_contact_time_s"] = np.asarray((indices[0] + 1) / env.sim_freq if indices.size else np.nan)
        result["sim__contact_point_offsets"] = np.asarray(self.point_offsets, dtype=np.int64)
        specs = [("finger_index", 0, (), np.int8), ("position_world_m", 1, (3,), np.float32),
                 ("normal_on_finger_world", 2, (3,), np.float32),
                 ("impulse_on_finger_world_ns", 3, (3,), np.float32),
                 ("separation_m", 4, (), np.float32)]
        for name, index, shape, dtype in specs:
            result["sim__contact_" + name] = np.asarray([p[index] for p in self.points], dtype=dtype).reshape((-1,) + shape)
        result["input__object_velocity_from_pose_world_m_s"] = result["input__object_translation_response_world_m"] * env.control_freq
        result["input__object_angular_velocity_from_pose_world_rad_s"] = result["input__object_rotation_response_world_rotvec_rad"] * env.control_freq
        outcome = classify_outcome(state["object_contact"], state["is_grasped"],
                                   state["object_clearance_m"], state["task_success"])
        result.update({"label__" + key: np.asarray(value) for key, value in outcome.items()})
        result["label__held_goal_success_final"] = np.asarray(state["task_success"][-1] and state["is_grasped"][-1])
        return result, outcome

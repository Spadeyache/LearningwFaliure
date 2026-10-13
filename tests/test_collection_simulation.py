"""Opt-in checks against actual CPU PhysX; no assets or models are downloaded.

Run after sourcing scripts/activate_grip.sh:
RUN_MANISKILL_INTEGRATION=1 python -m unittest discover -s tests -p 'test_collection_simulation.py' -v
"""
import os
import unittest
from unittest.mock import patch

import numpy as np


@unittest.skipUnless(os.environ.get("RUN_MANISKILL_INTEGRATION") == "1",
                     "set RUN_MANISKILL_INTEGRATION=1 for CPU PhysX checks")
class CollectionSimulationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import torch
        from failure_collection.policy import load_policy

        torch.set_num_threads(1)
        cls.policy, _ = load_policy(os.environ.get("COLLECTION_CHECKPOINT"))

    def _run(self, properties):
        from scipy.spatial.transform import Rotation
        from failure_collection.collect import rollout
        from failure_collection.environment import CollectionEnv
        from failure_collection.recording import EpisodeRecorder, first

        testcase = self
        checked_contact_samples = []

        class CheckedRecorder(EpisodeRecorder):
            def physics_step(self, env):
                super().physics_step(env)
                public_net = first(env.agent.robot.get_net_contact_forces(
                    [finger.name for finger in self.fingers]))
                public_pair = np.stack([
                    first(env.scene.get_pairwise_contact_forces(finger, env.cube))
                    for finger in self.fingers
                ])
                # These APIs independently aggregate contacts and establish
                # both world-frame convention and the force-on-finger sign.
                np.testing.assert_allclose(self.last_force, public_net, rtol=1e-5, atol=1e-6)
                np.testing.assert_allclose(self.last_pair_force, public_pair, rtol=1e-5, atol=1e-6)
                for i, finger in enumerate(self.fingers):
                    rotation = Rotation.from_quat(first(finger.pose.raw_pose)[3:], scalar_first=True)
                    expected = rotation.inv().apply(public_net[i])
                    np.testing.assert_allclose(self.physics[-1]["finger_net_force_local_n"][i],
                                               expected, rtol=1e-4, atol=2e-5)
                checked_contact_samples.append(bool(np.linalg.norm(public_pair, axis=1).max() > self.threshold))
                testcase.assertEqual(len(self.point_offsets), len(self.physics) + 1)

        env = CollectionEnv(properties)
        try:
            with patch("failure_collection.collect.EpisodeRecorder", CheckedRecorder):
                data, outcome = rollout(env, self.policy, 1000,
                                        {"episode_steps": 10, "contact_threshold_n": 0.05})
            self._check_physics_properties(env, properties, data)
            self.assertEqual(env.physics_step_callback, None)
            self.assertEqual(outcome["failure_cause"], "unknown")
            np.testing.assert_array_equal(data["sim__physics_object_contact"], checked_contact_samples)
            return data
        finally:
            env.close()

    def _check_physics_properties(self, env, requested, data):
        body = env.cube._bodies[0]
        collision = body.get_collision_shapes()[0]
        self.assertAlmostEqual(body.mass, requested["mass_kg"], places=7)
        np.testing.assert_allclose(body.cmass_local_pose.p, requested["com_offset_m"], atol=1e-8)
        np.testing.assert_allclose(body.cmass_local_pose.q, [1, 0, 0, 0], atol=1e-8)
        size = np.asarray(requested["size_xyz_m"])
        if requested["shape"] == "sphere":
            np.testing.assert_allclose(2 * collision.radius, size, atol=1e-8)
            inertia = np.repeat(0.4 * requested["mass_kg"] * (size[0] / 2) ** 2, 3)
        else:
            np.testing.assert_allclose(2 * collision.half_size, size, atol=1e-8)
            inertia = requested["mass_kg"] * (np.sum(size**2) - size**2) / 12
        if requested.get("inertia_principal_kg_m2") is not None:
            inertia = requested["inertia_principal_kg_m2"]
        np.testing.assert_allclose(body.inertia, inertia, rtol=1e-6, atol=1e-12)
        np.testing.assert_allclose(data["label__inertia_principal_kg_m2"], body.inertia)
        np.testing.assert_allclose(data["label__size_xyz_m"], size, atol=1e-8)
        np.testing.assert_allclose(data["label__com_offset_m"], requested["com_offset_m"], atol=1e-8)
        self.assertEqual(str(data["label__shape"]), requested["shape"])
        self.assertAlmostEqual(float(data["label__weight_n"]),
                               requested["mass_kg"] * np.linalg.norm(env.scene.px.get_config().gravity), places=6)
        for name in ("static_friction", "dynamic_friction", "restitution"):
            self.assertAlmostEqual(getattr(collision.physical_material, name), requested[name], places=7)
            self.assertAlmostEqual(float(data["label__object_" + name]), requested[name], places=7)
        for finger in (env.agent.finger1_link, env.agent.finger2_link):
            for shape in finger._bodies[0].get_collision_shapes():
                self.assertAlmostEqual(shape.physical_material.static_friction, requested["finger_friction"], places=7)
                self.assertAlmostEqual(shape.physical_material.dynamic_friction, requested["finger_friction"], places=7)
        for shape in env.table_scene.table._bodies[0].get_collision_shapes():
            self.assertAlmostEqual(shape.physical_material.static_friction, requested["table_friction"], places=7)
            self.assertAlmostEqual(shape.physical_material.dynamic_friction, requested["table_friction"], places=7)

    def _check_timelines(self, data):
        import torch
        from scipy.spatial.transform import Rotation
        from failure_collection.schema import validate_episode

        validate_episode(data)
        t = len(data["input__action_applied"])
        sim_hz = int(data["meta__simulation_frequency_hz"])
        control_hz = int(data["meta__control_frequency_hz"])
        k = sim_hz // control_hz
        self.assertEqual(t, 10)
        np.testing.assert_array_equal(data["meta__physics_action_index"], np.repeat(np.arange(t), k))
        np.testing.assert_allclose(data["meta__state_time_s"], np.arange(t + 1) / control_hz)
        np.testing.assert_allclose(data["meta__action_time_s"], np.arange(t) / control_hz)
        np.testing.assert_allclose(data["meta__physics_time_s"], np.arange(1, t * k + 1) / sim_hz)
        # Ensure action[i] was chosen from the pre-action observation i.
        for i in range(t):
            raw = self.policy(torch.as_tensor(data["sim__policy_observation"][i:i + 1])).numpy()[0]
            np.testing.assert_array_equal(data["input__action_raw"][i], raw)
        np.testing.assert_array_equal(data["input__action_applied"], np.clip(data["input__action_raw"], -1, 1))

        for prefix in ("", "physics_"):
            obj = data["input__" + prefix + "object_pose_world_m_wxyz"]
            tcp = data["input__" + prefix + "tcp_pose_world_m_wxyz"]
            rel = data["input__" + prefix + "object_pose_tcp_m_wxyz"]
            tcp_rotation = Rotation.from_quat(tcp[:, 3:], scalar_first=True)
            expected_translation = tcp_rotation.inv().apply(obj[:, :3] - tcp[:, :3])
            expected_rotation = tcp_rotation.inv() * Rotation.from_quat(obj[:, 3:], scalar_first=True)
            np.testing.assert_allclose(rel[:, :3], expected_translation, atol=2e-7)
            np.testing.assert_allclose(Rotation.from_quat(rel[:, 3:], scalar_first=True).as_matrix(),
                                       expected_rotation.as_matrix(), atol=5e-7)
        for field in ("object_pose_world_m_wxyz", "object_pose_tcp_m_wxyz", "tcp_pose_world_m_wxyz", "finger_width_m"):
            np.testing.assert_array_equal(data["input__" + field][1:], data["input__physics_" + field][k - 1::k])

        for pose_name, translation_name, rotation_name in (
            ("object_pose_world_m_wxyz", "object_translation_response_world_m", "object_rotation_response_world_rotvec_rad"),
            ("object_pose_tcp_m_wxyz", "relative_translation_response_tcp_m", "relative_rotation_response_tcp_rotvec_rad"),
        ):
            poses = data["input__" + pose_name]
            np.testing.assert_array_equal(data["input__" + translation_name], poses[1:, :3] - poses[:-1, :3])
            delta = Rotation.from_quat(poses[1:, 3:], scalar_first=True) * Rotation.from_quat(poses[:-1, 3:], scalar_first=True).inv()
            np.testing.assert_allclose(data["input__" + rotation_name], delta.as_rotvec(), atol=1e-7)

        offsets = data["sim__contact_point_offsets"]
        reconstructed = np.zeros((t * k, 2, 3), dtype=np.float64)
        for j in range(t * k):
            for index in range(offsets[j], offsets[j + 1]):
                finger = data["sim__contact_finger_index"][index]
                reconstructed[j, finger] += data["sim__contact_impulse_on_finger_world_ns"][index] * sim_hz
        np.testing.assert_allclose(data["sim__physics_object_pair_force_world_n"], reconstructed, rtol=1e-5, atol=1e-6)
        physics_contact = np.linalg.norm(reconstructed, axis=-1).max(axis=-1) > float(data["meta__contact_threshold_n"])
        state_contact = np.concatenate([[False], physics_contact.reshape(t, k).any(axis=1)])
        np.testing.assert_array_equal(data["sim__object_contact"], state_contact)
        np.testing.assert_array_equal(data["sim__from_contact_state_mask"], np.maximum.accumulate(state_contact))
        np.testing.assert_array_equal(data["sim__from_contact_physics_mask"], np.maximum.accumulate(physics_contact))
        np.testing.assert_array_equal(data["meta__force_valid_state"], np.arange(t + 1) > 0)
        np.testing.assert_array_equal(data["input__finger_net_force_world_n"][0], np.zeros((2, 3)))
        self.assertFalse(bool(data["meta__explicit_grip_point_available"]))
        self.assertTrue(np.isnan(data["input__explicit_grip_point_world_m"]).all())
        contacts = np.flatnonzero(physics_contact)
        if len(contacts):
            self.assertEqual(float(data["meta__first_contact_time_s"]), (contacts[0] + 1) / sim_hz)
        else:
            self.assertTrue(np.isnan(data["meta__first_contact_time_s"]))

    def test_primitive_physics_force_frames_alignment_and_fresh_replay(self):
        cases = [
            {"shape": "cube", "size_xyz_m": [0.04, 0.04, 0.04], "mass_kg": 0.08},
            {"shape": "box", "size_xyz_m": [0.034, 0.05, 0.036], "mass_kg": 0.14},
            {"shape": "sphere", "size_xyz_m": [0.04, 0.04, 0.04], "mass_kg": 0.05,
             "inertia_principal_kg_m2": [9e-6, 1e-5, 1.2e-5]},
        ]
        common = {"com_offset_m": [0.004, -0.002, 0.001], "static_friction": 0.23,
                  "dynamic_friction": 0.17, "restitution": 0.02,
                  "finger_friction": 1.5, "table_friction": 0.4}
        reference = None
        for case in cases:
            with self.subTest(shape=case["shape"]):
                data = self._run({**common, **case})
                self._check_timelines(data)
                if case["shape"] == "cube":
                    reference = data
                    self.assertTrue(data["sim__physics_object_contact"].any(),
                                    "force/frame checks need at least one nonzero object contact")
        self.assertIsNotNone(reference)
        repeated = self._run({**common, **cases[0]})
        self.assertEqual(set(reference), set(repeated))
        point_fields = ["sim__contact_finger_index", "sim__contact_position_world_m",
                        "sim__contact_normal_on_finger_world", "sim__contact_impulse_on_finger_world_ns",
                        "sim__contact_separation_m"]
        for name in reference:
            if name in point_fields:
                continue
            with self.subTest(replay_field=name):
                # All states, actions, aggregate forces, labels and contact
                # counts repeat exactly. PhysX point enumeration can permute
                # within a substep when a fresh scene allocates new bodies.
                np.testing.assert_array_equal(reference[name], repeated[name])
        offsets = reference["sim__contact_point_offsets"]
        for j in range(len(offsets) - 1):
            canonical = []
            for data in (reference, repeated):
                rows = np.column_stack([data[name][offsets[j]:offsets[j + 1]] for name in point_fields])
                order = np.lexsort(tuple(rows[:, i] for i in reversed(range(rows.shape[1]))))
                canonical.append(rows[order])
            with self.subTest(replay_contact_sample=j):
                np.testing.assert_array_equal(*canonical)

    def test_episode_history_cannot_change_matched_seed_trajectory(self):
        """A reused PhysX scene previously diverged at first object contact.

        Visible reset states were identical, but the contact solver retained
        history across episodes. Full scene reconfiguration must make the
        1004 -> 1000 -> 1004 sequence reproduce the complete first trajectory.
        """
        from failure_collection.collect import rollout
        from failure_collection.environment import CollectionEnv

        env = CollectionEnv({"mass_kg": 0.032, "finger_friction": 0.2})
        config = {"episode_steps": 100, "contact_threshold_n": 0.05}
        try:
            reference, _ = rollout(env, self.policy, 1004, config)
            rollout(env, self.policy, 1000, config)
            repeated, _ = rollout(env, self.policy, 1004, config)
        finally:
            env.close()
        self.assertTrue(reference["sim__physics_object_contact"].any(),
                        "reset regression must exercise object contact")
        for field in (
            "label__reset_state_hash", "label__failure_mode",
            "input__object_pose_world_m_wxyz", "input__tcp_pose_world_m_wxyz",
            "input__joint_position_rad_m", "input__joint_velocity_rad_m_s",
            "input__action_raw", "input__action_applied",
            "input__physics_finger_net_force_world_n",
            "sim__physics_object_pair_force_world_n",
        ):
            with self.subTest(replay_field=field):
                np.testing.assert_array_equal(reference[field], repeated[field])


if __name__ == "__main__":
    unittest.main()

"""Matched-run residual semantics, padding and reset-state guards."""

import copy
import unittest

import numpy as np
from scipy.spatial.transform import Rotation

from failure_collection.residuals import RESIDUAL_CHANNELS, build_residual


def episode(count=3, name="normal-42"):
    poses = np.zeros((count + 1, 7), dtype=np.float64)
    poses[:, 3] = 1
    return {
        "meta__episode_id": np.asarray(name),
        "label__seed": np.asarray(42),
        "label__initial_object_pose_world_m_wxyz": poses[0].copy(),
        "meta__control_frequency_hz": np.asarray(20),
        "meta__simulation_frequency_hz": np.asarray(100),
        "meta__state_time_s": np.arange(count + 1) / 20,
        "meta__physics_time_s": np.arange(1, count * 5 + 1) / 100,
        "meta__physics_action_index": np.repeat(np.arange(count), 5),
        "input__action_applied": np.zeros((count, 4)),
        "input__object_pose_tcp_m_wxyz": poses.copy(),
        "input__object_pose_world_m_wxyz": poses.copy(),
        "input__tcp_pose_world_m_wxyz": poses.copy(),
        "input__joint_position_rad_m": np.zeros((count + 1, 9)),
        "input__joint_velocity_rad_m_s": np.zeros((count + 1, 9)),
        "input__finger_width_m": np.full(count + 1, 0.04),
        "input__finger_force_valid": np.arange(count + 1) > 0,
        "input__goal_position_world_m": np.asarray([0, 0, 0.3]),
        "sim__physics_object_pair_force_world_n": np.zeros((count * 5, 2, 3)),
    }


class ResidualTests(unittest.TestCase):
    def test_post_action_differences_and_interval_mean_forces(self):
        normal = episode()
        shifted = copy.deepcopy(normal)
        shifted["input__object_pose_tcp_m_wxyz"][1:, :3] = [0.01, 0.02, -0.03]
        shifted["input__object_pose_world_m_wxyz"][1:, :3] = [-0.02, 0.01, 0.03]
        shifted["input__finger_width_m"][1:] += 0.01
        # Distinct left/right force components preserve ordering. A contact early
        # in the interval contributes even when its last physics sample is zero.
        shifted["sim__physics_object_pair_force_world_n"][0] = [[5, 10, 15], [-5, -10, -15]]
        result = build_residual(shifted, normal)
        self.assertEqual(result["residual"].shape, (3, 19))
        np.testing.assert_allclose(result["residual"][0], [
            0.01, 0.02, -0.03, 0, 0, 0,
            -0.02, 0.01, 0.03, 0, 0, 0, 0.01,
            1, 2, 3, -1, -2, -3,
        ], atol=1e-8)
        np.testing.assert_array_equal(result["residual"][1:, 13:], 0)
        np.testing.assert_allclose(result["residual_time_s"], [0.05, 0.1, 0.15])
        np.testing.assert_array_equal(result["residual_valid_mask"], True)
        self.assertEqual(str(result["matched_normal_run_id"]), "normal-42")
        self.assertEqual(len(set(RESIDUAL_CHANNELS)), 19)
        self.assertTrue(all(not np.asarray(value).dtype.hasobject for value in result.values()))

    def test_quaternion_sign_does_not_create_rotation_gap(self):
        normal = episode()
        normal["input__object_pose_world_m_wxyz"][1:, 3:] = Rotation.from_euler("xyz", [0.3, -0.2, 0.7]).as_quat(scalar_first=True)
        shifted = copy.deepcopy(normal)
        for key in ("input__object_pose_world_m_wxyz", "input__object_pose_tcp_m_wxyz", "input__tcp_pose_world_m_wxyz"):
            shifted[key][:, 3:] *= -1
        shifted["label__initial_object_pose_world_m_wxyz"][3:] *= -1
        result = build_residual(shifted, normal)
        np.testing.assert_allclose(result["residual"], 0, atol=1e-7)

    def test_noncommuting_orientation_uses_shifted_times_inverse_normal(self):
        normal, shifted = episode(), episode()
        normal_rotation = Rotation.from_euler("x", 0.8)
        gap_rotation = Rotation.from_rotvec([0, 0.15, 0])
        shifted_rotation = gap_rotation * normal_rotation
        for key, rotation in ((normal, normal_rotation), (shifted, shifted_rotation)):
            key["input__object_pose_world_m_wxyz"][1:, 3:] = rotation.as_quat(scalar_first=True)
            key["input__object_pose_tcp_m_wxyz"][1:, 3:] = rotation.as_quat(scalar_first=True)
        result = build_residual(shifted, normal)["residual"]
        np.testing.assert_allclose(result[:, 3:6], np.tile([0, 0.15, 0], (3, 1)), atol=1e-7)
        np.testing.assert_allclose(result[:, 9:12], np.tile([0, 0.15, 0], (3, 1)), atol=1e-7)

    def test_shorter_normal_is_last_value_padded_and_masked(self):
        normal, shifted = episode(2), episode(4)
        normal["input__finger_width_m"][1:] = [0.03, 0.02]
        shifted["input__finger_width_m"][1:] = [0.04, 0.03, 0.04, 0.05]
        result = build_residual(shifted, normal)
        np.testing.assert_allclose(result["residual"][:, 12], [0.01, 0.01, 0.02, 0.03], atol=1e-7)
        np.testing.assert_array_equal(result["residual_source_valid_mask"], [[1, 1], [1, 1], [1, 0], [1, 0]])
        np.testing.assert_array_equal(result["residual_valid_mask"], [1, 1, 0, 0])

    def test_shorter_shifted_and_unavailable_force_are_masked(self):
        normal, shifted = episode(4), episode(2)
        shifted["input__finger_force_valid"][2] = False
        result = build_residual(shifted, normal)
        np.testing.assert_array_equal(result["residual_source_valid_mask"], [[1, 1], [0, 1], [0, 1], [0, 1]])
        np.testing.assert_array_equal(result["residual_valid_mask"], [1, 0, 0, 0])

    def test_matching_rejects_seed_reset_robot_goal_and_frequency_changes(self):
        for key, index, delta in (
            ("label__seed", (), 1),
            ("input__object_pose_world_m_wxyz", (0, 0), 0.01),
            ("input__object_pose_tcp_m_wxyz", (0, 0), 0.01),
            ("input__tcp_pose_world_m_wxyz", (0, 0), 0.01),
            ("input__joint_position_rad_m", (0, 0), 0.01),
            ("input__joint_velocity_rad_m_s", (0, 0), 0.01),
            ("input__goal_position_world_m", 0, 0.01),
            ("label__initial_object_pose_world_m_wxyz", 0, 0.01),
            ("meta__control_frequency_hz", (), 1),
        ):
            normal, shifted = episode(), episode()
            shifted[key][index] += delta
            with self.subTest(key=key), self.assertRaises(ValueError):
                build_residual(shifted, normal)

    def test_corrupt_timelines_and_invalid_force_rejected(self):
        for key, index, value in (
            ("meta__state_time_s", 1, 0.051),
            ("meta__physics_time_s", 1, 0.021),
            ("meta__physics_action_index", 1, 1),
            ("sim__physics_object_pair_force_world_n", (0, 0, 0), np.nan),
            ("input__object_pose_world_m_wxyz", (1, 3), 0),
        ):
            normal, shifted = episode(), episode()
            shifted[key][index] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                build_residual(shifted, normal)

    def test_ground_truth_labels_do_not_enter_features(self):
        normal, shifted = episode(), episode()
        shifted.update(label__mass_kg=np.asarray(4.0), label__failure_mode=np.asarray("drop"),
                       label__object_static_friction=np.asarray(0.01))
        np.testing.assert_array_equal(build_residual(shifted, normal)["residual"], 0)

    def test_missing_baseline_identity_and_empty_episodes_rejected(self):
        normal = episode()
        normal["meta__episode_id"] = np.asarray("")
        with self.assertRaisesRegex(ValueError, "meta__episode_id"):
            build_residual(episode(), normal)
        with self.assertRaisesRegex(ValueError, "completed action"):
            build_residual(episode(0), episode())


if __name__ == "__main__":
    unittest.main()

"""Current collection failure-event timing regressions."""
import unittest

import numpy as np

from failure_collection.events import episode_events


def episode(grasp=(False, True, True, True, True, True), success=False):
    count = len(grasp)
    pose = np.zeros((count, 7))
    pose[:, 3] = 1
    pose[:, 2] = .06
    return {
        "meta__state_time_s": np.arange(count) * .05,
        "sim__is_grasped": np.asarray(grasp),
        "sim__object_clearance_m": np.full(count, .04),
        "input__object_pose_tcp_m_wxyz": pose.copy(),
        "input__object_pose_world_m_wxyz": pose.copy(),
        "input__tcp_pose_world_m_wxyz": pose.copy(),
        "label__success_final": np.asarray(success),
        "label__failure_mode": np.asarray("goal_not_reached_or_not_static"),
        "input__action_raw": np.zeros((count - 1, 4)),
        "input__action_applied": np.zeros((count - 1, 4)),
        "sim__physics_object_pair_force_world_n": np.ones((count - 1, 2, 3)),
    }


class EventTests(unittest.TestCase):
    def test_miss_onset_unknown_detection_at_horizon(self):
        result = episode_events(episode((False,) * 6))
        self.assertEqual(result["label__failure_type"], "miss")
        self.assertTrue(np.isnan(result["label__failure_time_s"]))
        self.assertEqual(result["label__failure_detection_time_s"], .25)

    def test_slip_needs_consecutive_grasp_and_lift(self):
        data = episode()
        data["input__object_pose_tcp_m_wxyz"][2:, 0] += .006
        result = episode_events(data)
        self.assertEqual(result["label__failure_type"], "slip")
        self.assertEqual(result["label__first_slip_time_s"], .1)
        data["sim__object_clearance_m"][:] = 0
        self.assertFalse(episode_events(data)["label__slip_observed"])
        data["sim__object_clearance_m"][:] = .04
        data["sim__is_grasped"][1] = False
        self.assertFalse(episode_events(data)["label__slip_observed"])

    def test_rotation_slip_and_quaternion_sign_invariance(self):
        data = episode()
        data["input__object_pose_tcp_m_wxyz"][2:, 3:] *= -1
        self.assertFalse(episode_events(data)["label__slip_observed"])
        data["input__object_pose_tcp_m_wxyz"][2:, 3] = np.cos(.2 / 2)
        data["input__object_pose_tcp_m_wxyz"][2:, 6] = np.sin(.2 / 2)
        self.assertTrue(episode_events(data)["label__slip_observed"])

    def test_drop_requires_sustained_loss_and_descent(self):
        data = episode((False, True, True, False, False, False))
        self.assertFalse(episode_events(data)["label__drop_observed"])
        data["input__object_pose_world_m_wxyz"][3:, 2] = [.05, .04, .03]
        result = episode_events(data)
        self.assertEqual(result["label__failure_type"], "drop")
        self.assertAlmostEqual(result["label__first_drop_time_s"], .15)
        self.assertEqual(result["label__drop_detection_time_s"], .25)
        self.assertEqual(np.flatnonzero(result["sim__drop_event_mask"]).tolist(), [5])
        data["sim__is_grasped"][-1] = True
        self.assertFalse(episode_events(data)["label__drop_observed"])

    def test_event_survives_later_success(self):
        data = episode((False, True, True, False, False, False, True), success=True)
        data["input__object_pose_world_m_wxyz"][3:6, 2] = [.05, .04, .03]
        result = episode_events(data)
        self.assertTrue(result["label__drop_observed"])
        self.assertEqual(result["label__failure_type"], "none")
        self.assertTrue(np.isnan(result["label__failure_time_s"]))

    def test_single_state_and_invalid_time(self):
        self.assertEqual(episode_events(episode((False,)))["label__failure_type"], "miss")
        data = episode()
        data["meta__state_time_s"][2] = 0
        with self.assertRaises(ValueError):
            episode_events(data)


if __name__ == "__main__":
    unittest.main()

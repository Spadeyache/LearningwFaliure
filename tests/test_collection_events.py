"""Event timing, transient recovery, and correction capability regressions."""
import unittest
from types import SimpleNamespace

import numpy as np

from failure_collection.events import episode_events
from failure_collection.recovery import (
    apply_correction, correction_context, normalize_recovery,
    recovery_capability, recovery_result,
)


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


class FakeGripper:
    def __init__(self, limit):
        self.config = SimpleNamespace(force_limit=limit)
        self.actual = limit
        self.joints = [SimpleNamespace(get_force_limit=lambda: np.asarray(self.actual))]

    def set_drive_property(self):
        self.actual = self.config.force_limit


def fake_env(limit=100, grasping=True):
    return SimpleNamespace(cube=object(), agent=SimpleNamespace(
        is_grasping=lambda _: np.asarray([grasping]),
        controller=SimpleNamespace(controllers={
            "arm": SimpleNamespace(config=SimpleNamespace(use_delta=True)),
            "gripper": FakeGripper(limit),
        })))


class RecoveryTests(unittest.TestCase):
    def test_normal_run_context_is_noop(self):
        env = fake_env()
        gripper = env.agent.controller.controllers["gripper"]
        with correction_context(env, None) as capability:
            self.assertEqual(capability["reason"], "no_correction")
            self.assertEqual(gripper.actual, 100)
        self.assertEqual(gripper.actual, 100)

    def test_bounded_grip_limit_skip_and_restore_even_on_exception(self):
        spec = {"kind": "grip_limit", "factor": 2, "max_grip_limit_n": 100}
        self.assertEqual(recovery_capability(fake_env(), spec)["reason"], "no_motor_limit_headroom")
        env = fake_env(40)
        gripper = env.agent.controller.controllers["gripper"]
        with self.assertRaises(RuntimeError):
            with correction_context(env, spec):
                self.assertEqual(gripper.actual, 80)
                raise RuntimeError("rollout failure")
        self.assertEqual(gripper.actual, 40)
        self.assertEqual(gripper.config.force_limit, 40)

    def test_slow_ascent_preserves_raw_and_other_axes(self):
        spec = {"kind": "slow_lift", "factor": .5}
        raw = np.array([[.3, .4, .8, -.9]])
        corrected = apply_correction(raw, fake_env(), spec)
        np.testing.assert_allclose(corrected, [[.3, .4, .4, -.9]])
        np.testing.assert_allclose(raw, [[.3, .4, .8, -.9]])
        np.testing.assert_allclose(apply_correction(raw, fake_env(grasping=False), spec), raw)
        stale = fake_env()
        stale._contacts_stale = True
        np.testing.assert_allclose(apply_correction(raw, stale, spec), raw)
        raw[0, 2] = -.8
        np.testing.assert_allclose(apply_correction(raw, fake_env(), spec), raw)

    def test_success_without_force_increase_is_not_force_recovery(self):
        parent, retry = episode(), episode(success=True)
        spec = {"kind": "grip_limit", "factor": 2}
        result = recovery_result(parent, retry, spec)
        self.assertTrue(result["label__recovery_retry_success"])
        self.assertFalse(result["label__recovery_recovered"])
        retry["sim__physics_object_pair_force_world_n"] *= 2
        self.assertTrue(recovery_result(parent, retry, spec)["label__recovery_recovered"])

    def test_slow_recovery_requires_action_change(self):
        parent, retry = episode(), episode(success=True)
        spec = {"kind": "slow_lift", "factor": .5}
        self.assertFalse(recovery_result(parent, retry, spec)["label__recovery_recovered"])
        retry["input__action_raw"][1, 2] = .8
        retry["input__action_applied"][1, 2] = .4
        self.assertTrue(recovery_result(parent, retry, spec)["label__recovery_recovered"])

    def test_config_validation(self):
        self.assertFalse(normalize_recovery()["enabled"])
        for invalid in ([], False, {"enabled": "yes"}, {"corrections": [{"kind": "lower_grasp", "factor": 1}]},
                        {"max_grip_limit_n": np.inf}, {"corrections": [{"kind": "slow_lift", "factor": 2}]}):
            with self.subTest(config=invalid), self.assertRaises(ValueError):
                normalize_recovery(invalid)


if __name__ == "__main__":
    unittest.main()

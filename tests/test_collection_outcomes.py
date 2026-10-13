"""Checks for descriptive episode outcomes and state-index alignment."""

import unittest

import numpy as np

from failure_collection.outcomes import classify_outcome


class OutcomeTests(unittest.TestCase):
    def test_no_contact_has_no_event_indices(self):
        result = classify_outcome([False] * 3, [False] * 3, [0.0] * 3, [False] * 3)
        self.assertEqual(result["failure_mode"], "never_contacted")
        self.assertFalse(result["success_final"])
        self.assertFalse(result["success_any"])
        for event in ("contact", "grasp", "lift"):
            self.assertEqual(result[f"first_{event}_state_index"], -1)
        self.assertEqual(result["failure_mode_source"], "outcome_rules_v1")
        self.assertEqual(result["failure_cause"], "unknown")

    def test_contact_without_grasp(self):
        result = classify_outcome(
            [False, True, False], [False] * 3, [0.0, 0.03, 0.0], [False] * 3
        )
        self.assertEqual(result["failure_mode"], "contact_without_grasp")
        self.assertEqual(result["first_contact_state_index"], 1)
        self.assertEqual(result["first_lift_state_index"], -1)

    def test_height_only_when_not_grasped_does_not_count_as_lift(self):
        result = classify_outcome(
            [False, True, True], [False, True, False], [0.05, 0.0, 0.05], [False] * 3
        )
        self.assertEqual(result["failure_mode"], "grasped_no_lift")
        self.assertEqual(result["first_grasp_state_index"], 1)
        self.assertEqual(result["first_lift_state_index"], -1)

    def test_lost_grasp_after_lift(self):
        result = classify_outcome(
            [False, True, True, False],
            [False, True, True, False],
            [0.0, 0.0, 0.02, 0.0],
            [False] * 4,
        )
        self.assertEqual(result["failure_mode"], "lifted_then_lost_grasp")
        self.assertEqual(result["first_lift_state_index"], 2)

    def test_regained_grasp_is_not_final_lost_grasp(self):
        result = classify_outcome(
            [True, True, False, True],
            [True, True, False, True],
            [0.0, 0.04, 0.0, 0.01],
            [False] * 4,
        )
        self.assertEqual(result["failure_mode"], "goal_not_reached_or_not_static")
        self.assertEqual(result["first_contact_state_index"], 0)
        self.assertEqual(result["first_grasp_state_index"], 0)

    def test_transient_success_does_not_override_final_failure(self):
        result = classify_outcome(
            [True, True, False],
            [True, True, False],
            [0.0, 0.04, 0.0],
            [False, True, False],
        )
        self.assertTrue(result["success_any"])
        self.assertFalse(result["success_final"])
        self.assertEqual(result["failure_mode"], "lifted_then_lost_grasp")

    def test_final_success_and_single_state_input(self):
        result = classify_outcome([True], [True], [0.04], [True])
        self.assertTrue(result["success_final"])
        self.assertTrue(result["success_any"])
        self.assertEqual(result["failure_mode"], "success")
        self.assertEqual(result["first_lift_state_index"], 0)

    def test_custom_threshold(self):
        result = classify_outcome([True], [True], [0.04], [False], lift_threshold_m=0.05)
        self.assertEqual(result["failure_mode"], "grasped_no_lift")

    def test_empty_mismatched_and_nonvector_inputs_rejected(self):
        cases = [
            ([], [], [], []),
            ([True], [True, False], [0.0], [False]),
            ([[True]], [True], [0.0], [False]),
            ([True], [True], 0.0, [False]),
        ]
        for args in cases:
            with self.subTest(args=args), self.assertRaises(ValueError):
                classify_outcome(*args)

    def test_nonfinite_clearance_and_invalid_threshold_rejected(self):
        for value in (np.nan, np.inf, -np.inf):
            with self.subTest(clearance=value), self.assertRaises(ValueError):
                classify_outcome([True], [True], [value], [False])
        for value in (0.0, -0.01, np.nan, np.inf):
            with self.subTest(threshold=value), self.assertRaises(ValueError):
                classify_outcome([True], [True], [0.0], [False], lift_threshold_m=value)


if __name__ == "__main__":
    unittest.main()

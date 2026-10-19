"""Synthetic checks of metrics; no simulator or robot trials."""
import unittest
import numpy as np
from analyze import extract, longest_steady_hold, SIGNALS


class MetricsTest(unittest.TestCase):
    def setUp(self):
        self.time = np.arange(21) / 20
        self.pose = np.zeros((21, 7))
        self.pose[:, 3] = 1
        self.distance = np.zeros(21)
        self.force = np.ones((21, 2))

    def hold(self, **kwargs):
        return longest_steady_hold(self.time, self.pose, self.distance, self.force, **kwargs)

    def test_steady_at_target(self):
        self.assertAlmostEqual(self.hold(), 1.)

    def test_no_contact_is_not_stable_grasp(self):
        self.force[:] = 0
        self.assertEqual(self.hold(), 0)

    def test_far_from_goal(self):
        self.distance[:] = .1
        self.assertEqual(self.hold(), 0)

    def test_translation_drift(self):
        self.pose[:, 0] = np.arange(21) * .002
        self.assertLess(self.hold(), .1)

    def test_rotation_drift(self):
        angle = np.arange(21) * .1
        self.pose[:, 3] = np.cos(angle / 2)
        self.pose[:, 6] = np.sin(angle / 2)
        self.assertEqual(self.hold(), 0)

    def test_quaternion_sign_does_not_create_wobble(self):
        self.pose[::2, 3:] *= -1
        self.assertAlmostEqual(self.hold(), 1.)

    def test_early_hold_then_drop_is_not_final_success(self):
        self.distance[-3:] = .2
        self.assertGreater(self.hold(), .5)
        self.assertEqual(self.hold(terminal_only=True), 0)

    def test_no_labels_needed_and_features_match_channel_count(self):
        from analyze import CHANNELS
        signals = dict(zip(SIGNALS, [self.pose, self.pose, self.pose, np.ones(21) * .04,
                        np.ones((20, 2, 3)), np.zeros((20, 5)), self.distance, self.time]))
        x, metrics = extract(signals)
        self.assertEqual(x.shape, (60, len(CHANNELS)))
        self.assertTrue(metrics['stability_success_proxy'])
        # Extra physical labels are never referenced by the transform.
        x2, metrics2 = extract(dict(signals, label__mass_kg=999, label__failure_type='invented'))
        np.testing.assert_array_equal(x, x2)
        self.assertEqual(metrics, metrics2)

    def test_missing_force_is_unknown_motion_not_zero(self):
        signals = dict(zip(SIGNALS, [self.pose, self.pose, self.pose, np.ones(21) * .04,
                        np.zeros((20, 2, 3)), np.zeros((20, 5)), self.distance, self.time]))
        _, metrics = extract(signals)
        self.assertIsNone(metrics['relative_translation_path_during_bilateral_force_m'])
        self.assertFalse(metrics['stability_success_proxy'])


class SelectionTest(unittest.TestCase):
    def test_single_factor_selection_preserves_nominal_and_excludes_pairs(self):
        import json
        from pathlib import Path
        from tempfile import TemporaryDirectory
        from analyze import select_episodes
        entries=[dict(file='base.npz',seed=1,changed_factors=[]),
                 dict(file='mass.npz',seed=1,changed_factors=['mass']),
                 dict(file='friction.npz',seed=2,changed_factors=['object_friction']),
                 dict(file='pair.npz',seed=2,changed_factors=['mass','object_friction']),
                 dict(file='shape.npz',seed=2,changed_factors=['shape'])]
        with TemporaryDirectory() as temp:
            path=Path(temp);(path/'episodes.json').write_text(json.dumps(entries))
            selected=select_episodes(path,100,['mass','object_friction'])
            self.assertEqual({p.name for _,p in selected},{'base.npz','mass.npz','friction.npz'})
            self.assertEqual(selected,select_episodes(path,100,['mass','object_friction']))

    def test_filter_requires_explicit_factor_metadata(self):
        import json
        from pathlib import Path
        from tempfile import TemporaryDirectory
        from analyze import select_episodes
        with TemporaryDirectory() as temp:
            path=Path(temp);(path/'episodes.json').write_text(json.dumps([dict(file='a.npz',seed=1)]))
            with self.assertRaisesRegex(ValueError,'independent experiment factors'):
                select_episodes(path,100,['mass'])


if __name__ == '__main__':
    unittest.main()

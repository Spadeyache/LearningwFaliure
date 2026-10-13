"""Check held-out-seed scoring, padding exclusion and complete atlas artifacts."""

import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import numpy as np

from failure_collection.atlas import (
    build_atlas, build_features, evaluate_separability, load_residual_runs, make_seed_folds,
)


class AtlasTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.directory = Path(self.temporary.name)

    def write_run(self, seed=0, variable="mass", magnitude=0.5, role="shifted", **updates):
        path = self.directory / f"{role}_{seed}_{variable}_{magnitude}.npz"
        data = {
            "meta__run_id": np.asarray(path.stem),
            "meta__run_role": np.asarray(role),
            "label__shifted_variable": np.asarray(variable),
            "label__shift_magnitude": np.asarray(magnitude),
            "label__seed": np.asarray(seed),
            "matched_normal_run_id": np.asarray(f"normal_{seed}"),
            "residual_channels": np.asarray(["relative_position_x_m", "finger_force_left_n"]),
            "residual_time_s": np.asarray([0.0, 1.0, 2.0, 3.0]),
            "residual_valid_mask": np.asarray([False, True, True, False]),
            # Deliberately invalid padding must never become an analysis feature.
            "residual": np.asarray([[np.nan, np.nan], [1.0, 2.0], [2.0, 4.0], [1e30, -1e30]]),
        }
        data.update(updates)
        np.savez_compressed(path, **data)
        return path

    def write_balanced_experiment(self, seed_count=5):
        for seed in range(seed_count):
            for variable in ("mass", "friction"):
                for magnitude in (0.5, 2.0, 4.0):
                    sign = 1 if variable == "mass" else -1
                    signal = sign * (1 + magnitude * 0.1)
                    self.write_run(seed, variable, magnitude,
                                   residual=np.asarray([[0., 0.], [signal, 0.1 * seed],
                                                        [2 * signal, 0.1 * seed], [999., 999.]]))

    def test_common_seconds_exclude_padding_and_do_not_warp_episode_duration(self):
        self.write_run()
        self.write_run(seed=1, residual_time_s=np.asarray([0., 1., 2., 4.]),
                       residual_valid_mask=np.asarray([True, True, True, True]),
                       residual=np.asarray([[0., 0.], [10., 20.], [20., 40.], [40., 80.]]))
        runs = load_residual_runs(self.directory)
        features, trajectories, times = build_features(runs, time_points=3)
        np.testing.assert_array_equal(times, [1., 1.5, 2.])
        np.testing.assert_allclose(trajectories[0], [[1., 2.], [1.5, 3.], [2., 4.]])
        np.testing.assert_allclose(trajectories[1], [[10., 20.], [15., 30.], [20., 40.]])
        self.assertTrue(np.isfinite(features).all())
        # Only the observed segment is allowed to change the representation.
        runs[0].residual[~runs[0].valid] = -7e100
        np.testing.assert_array_equal(features, build_features(runs, time_points=3)[0])

    def test_normal_and_retry_labels_and_outcomes_never_enter_features(self):
        self.write_run(label__success_final=np.asarray(True), label__mass_kg=np.asarray(500.))
        self.write_run(role="normal", residual=np.asarray("not a trajectory"))
        self.write_run(role="retry", residual=np.asarray("not a trajectory"))
        runs = load_residual_runs(self.directory)
        self.assertEqual(len(runs), 1)
        features, _, _ = build_features(runs, time_points=2)
        np.testing.assert_array_equal(features, [[1., 2., 2., 4.]])

    def test_missing_samples_cannot_be_bridged_by_interpolation(self):
        self.write_run(residual_valid_mask=np.asarray([True, False, True, False]))
        with self.assertRaisesRegex(ValueError, "contiguous"):
            load_residual_runs(self.directory)

    def test_channel_order_and_duplicated_seed_conditions_rejected(self):
        original = self.write_run()
        self.write_run(seed=1, residual_channels=np.asarray(["finger_force_left_n", "relative_position_x_m"]))
        with self.assertRaisesRegex(ValueError, "channel names/order"):
            load_residual_runs(self.directory)
        (self.directory / "shifted_1_mass_0.5.npz").unlink()
        (self.directory / "duplicate.npz").write_bytes(original.read_bytes())
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            load_residual_runs(self.directory)

    def test_shared_normal_id_cannot_leak_across_seed_groups(self):
        self.write_run()
        self.write_run(seed=1, matched_normal_run_id=np.asarray("normal_0"))
        with self.assertRaisesRegex(ValueError, "multiple seed groups"):
            load_residual_runs(self.directory)

    def test_no_common_window_and_invalid_resampling_count_rejected(self):
        self.write_run()
        self.write_run(seed=1, residual_time_s=np.asarray([3., 4., 5., 6.]))
        runs = load_residual_runs(self.directory)
        with self.assertRaisesRegex(ValueError, "no shared"):
            build_features(runs)
        for count in (1, 1.5, True):
            with self.subTest(count=count), self.assertRaises(ValueError):
                build_features(runs, count)

    def test_all_magnitudes_and_variables_of_seed_stay_together(self):
        labels = np.tile(np.repeat(["mass", "friction"], 3), 10)
        seeds = np.repeat(np.arange(10), 6)
        folds = make_seed_folds(labels, seeds)
        covered = []
        for train, test in folds:
            self.assertFalse(set(seeds[train]) & set(seeds[test]))
            self.assertEqual(set(labels[test]), {"mass", "friction"})
            for seed in np.unique(seeds[test]):
                self.assertEqual(np.sum(seeds[test] == seed), 6)
            covered.extend(test.tolist())
        self.assertEqual(sorted(covered), list(range(len(labels))))

    def test_five_seeds_needed_in_each_class(self):
        labels = np.tile(["mass", "friction"], 4)
        seeds = np.repeat(np.arange(4), 2)
        with self.assertRaisesRegex(ValueError, "five distinct seeds"):
            make_seed_folds(labels, seeds)
        with self.assertRaisesRegex(ValueError, "Both mass and friction"):
            make_seed_folds(np.repeat("mass", 10), np.arange(10))

    def test_scaler_never_fits_held_out_seed_samples(self):
        from sklearn.preprocessing import StandardScaler
        labels = np.tile(["mass", "friction"], 5)
        seeds = np.repeat(np.arange(5), 2)
        features = np.column_stack([np.arange(10), np.where(labels == "mass", 1., -1.)])
        fitted_samples = []
        original_fit = StandardScaler.fit

        def record_fit(scaler, values, *args, **kwargs):
            fitted_samples.append(values.copy())
            return original_fit(scaler, values, *args, **kwargs)

        with patch.object(StandardScaler, "fit", record_fit):
            scores = evaluate_separability(features, labels, seeds)
        self.assertEqual(len(fitted_samples), 5)
        for values, (train, test) in zip(fitted_samples, make_seed_folds(labels, seeds)):
            np.testing.assert_array_equal(values, features[train])
            self.assertFalse(set(values[:, 0]) & set(features[test, 0]))
        self.assertEqual(sum(map(sum, scores["confusion_matrix"])), len(labels))

    def test_identical_residuals_cannot_predict_variable_from_metadata(self):
        labels = np.tile(["mass", "friction"], 5)
        scores = evaluate_separability(np.ones((10, 8)), labels, np.repeat(np.arange(5), 2))
        self.assertEqual(scores["accuracy"], 0.5)

    def test_end_to_end_writes_real_pngs_and_finite_scores(self):
        self.write_balanced_experiment()
        scores = build_atlas(self.directory, time_points=5)
        self.assertEqual(scores["run_count"], 30)
        self.assertEqual(scores["seed_count"], 5)
        self.assertEqual(scores["feature_shape"], [30, 10])
        self.assertEqual(scores["time_window_s"], [1., 2.])
        self.assertEqual(scores["accuracy"], 1.)
        self.assertEqual(scores["confusion_matrix"], [[15, 0], [0, 15]])
        saved = json.loads((self.directory / "atlas" / "separability.json").read_text())
        self.assertEqual(saved, scores)
        for name in scores["figures"]:
            image = (self.directory / "atlas" / name).read_bytes()
            self.assertEqual(image[:8], b"\x89PNG\r\n\x1a\n")
            self.assertGreater(len(image), 1000)
        # Rerunning on a directory containing the atlas should be deterministic.
        self.assertEqual(build_atlas(self.directory, time_points=5), scores)

    def test_insufficient_seeds_do_not_leave_partial_deliverables(self):
        self.write_balanced_experiment(seed_count=4)
        with self.assertRaisesRegex(ValueError, "five distinct seeds"):
            build_atlas(self.directory)
        self.assertFalse((self.directory / "atlas").exists())


if __name__ == "__main__":
    unittest.main()

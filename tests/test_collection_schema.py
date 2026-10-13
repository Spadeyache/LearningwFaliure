"""Guard the deployment-feature boundary, archive checks and sweep pairing."""

import json
from pathlib import Path
import tempfile
import unittest

import numpy as np

from failure_collection import SCHEMA_VERSION
from failure_collection.collect import load_config
from failure_collection.schema import INPUT_LAYOUTS, load_inputs, save_episode, validate_episode


def episode_fixture():
    """Two commands, three states and four physics samples without contacts."""
    lengths = {"state": (3,), "transition": (2,), "physics": (4,), "constant": ()}
    data = {}
    for key, (timeline, shape) in INPUT_LAYOUTS.items():
        data[key] = np.zeros(lengths[timeline] + shape, dtype=np.float32)
        if key.endswith("_m_wxyz"):
            data[key][..., 3] = 1
    data["input__explicit_grip_point_world_m"][:] = np.nan
    data["input__finger_force_valid"] = np.asarray([False, True, True])
    data.update({
        "meta__schema_version": np.asarray(SCHEMA_VERSION),
        "meta__physics_time_s": np.arange(1, 5, dtype=np.float64) / 240,
        "meta__first_contact_time_s": np.asarray(np.nan),
        "sim__contact_point_offsets": np.zeros(5, dtype=np.int64),
        "sim__contact_position_world_m": np.empty((0, 3), dtype=np.float32),
        "sim__task_success": np.zeros(3, dtype=bool),
        "sim__policy_observation": np.zeros((3, 42)),
        "sim__is_grasped": np.zeros(3, dtype=bool),
        "sim__object_contact": np.zeros(3, dtype=bool),
        "label__success_final": np.asarray(False),
        "label__mass_kg": np.asarray(0.064),
        "label__seed": np.asarray(42),
    })
    return data


class SchemaTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.path = Path(self.directory.name) / "episode.npz"

    def test_roundtrip_excludes_privileged_fields_and_missing_grip_point(self):
        source = episode_fixture()
        save_episode(self.path, source)
        inputs = load_inputs(self.path)
        self.assertIn("input__action_applied", inputs)
        self.assertIn("input__object_pose_tcp_m_wxyz", inputs)
        self.assertIn("input__finger_net_force_world_n", inputs)
        self.assertNotIn("input__explicit_grip_point_world_m", inputs)
        for name in source:
            if name.startswith(("sim__", "label__", "meta__")):
                self.assertNotIn(name, inputs)
        np.testing.assert_array_equal(inputs["input__action_applied"], source["input__action_applied"])
        # Returned arrays remain usable after the archive context was closed.
        inputs["input__action_applied"][0, 0] = 0.5
        with np.load(self.path, allow_pickle=False) as saved:
            self.assertEqual(saved["input__action_applied"][0, 0], 0.0)

    def test_sensor_family_switches_remove_object_pose_derivatives_and_forces(self):
        save_episode(self.path, episode_fixture())
        inputs = load_inputs(self.path, include_pose=False, include_force=False)
        self.assertIn("input__tcp_pose_world_m_wxyz", inputs)
        self.assertIn("input__action_raw", inputs)
        self.assertIn("input__finger_width_m", inputs)
        for name in inputs:
            self.assertFalse(any(token in name for token in ("object_", "relative_", "force", "compression", "imbalance")), name)

    def test_fabricated_input_names_are_excluded_even_when_prefix_is_correct(self):
        data = episode_fixture()
        data["input__policy_observation"] = data["sim__policy_observation"]
        data["input__object_mass_kg"] = data["label__mass_kg"]
        np.savez(self.path, **data)
        inputs = load_inputs(self.path)
        self.assertNotIn("input__policy_observation", inputs)
        self.assertNotIn("input__object_mass_kg", inputs)
        with self.assertRaisesRegex(ValueError, "Unapproved classifier inputs"):
            validate_episode(data)

    def test_missing_or_misaligned_state_transition_and_physics_fields_rejected(self):
        for key in (
            "input__finger_width_m",
            "input__finger_force_mean_world_n",
            "input__physics_finger_net_force_world_n",
        ):
            data = episode_fixture()
            data[key] = data[key][:-1]
            with self.subTest(key=key), self.assertRaisesRegex(ValueError, "Invalid or missing"):
                validate_episode(data)
        data = episode_fixture()
        del data["input__action_raw"]
        with self.assertRaisesRegex(ValueError, "Invalid or missing"):
            validate_episode(data)

    def test_atomic_save_refuses_overwrite_and_leaves_no_temporary_file(self):
        data = episode_fixture()
        save_episode(self.path, data)
        original = self.path.read_bytes()
        with self.assertRaises(FileExistsError):
            save_episode(self.path, data)
        self.assertEqual(self.path.read_bytes(), original)
        self.assertFalse(self.path.with_suffix(".npz.tmp").exists())

    def test_schema_mismatch_rejected_by_validator_and_loader(self):
        data = episode_fixture()
        data["meta__schema_version"] = np.asarray("unsupported-version")
        with self.assertRaises(ValueError):
            validate_episode(data)
        np.savez(self.path, **data)
        with self.assertRaises(ValueError):
            load_inputs(self.path)

    def test_object_arrays_forbidden_even_in_metadata(self):
        data = episode_fixture()
        data["meta__unsafe"] = np.asarray({"anything": 1}, dtype=object)
        with self.assertRaisesRegex(ValueError, "Pickle/object array"):
            save_episode(self.path, data)
        self.assertFalse(self.path.exists())

    def test_nan_sensor_rejected_but_documented_missing_grip_and_contact_allowed(self):
        data = episode_fixture()
        validate_episode(data)
        data["input__finger_width_m"][1] = np.nan
        with self.assertRaisesRegex(ValueError, "Nonfinite"):
            validate_episode(data)

    def test_bad_pose_or_out_of_range_command_rejected(self):
        for mutate in (
            lambda data: data["input__object_pose_tcp_m_wxyz"].__setitem__((1, slice(3, None)), 0),
            lambda data: data["input__action_applied"].__setitem__((0, 0), 1.01),
            lambda data: data.__setitem__("input__action_applied", np.zeros((2, 5))),
            lambda data: data.__setitem__("input__tcp_pose_world_m_wxyz", data["input__tcp_pose_world_m_wxyz"][:-1]),
        ):
            data = episode_fixture()
            mutate(data)
            with self.subTest(data=data), self.assertRaises(ValueError):
                validate_episode(data)

    def test_corrupt_ragged_offsets_and_final_success_rejected(self):
        for offsets in ([0, 0, 0, 0], [1, 1, 1, 1, 1], [0, 1, 0, 0, 0], [0, 0, 0, 0, 1]):
            data = episode_fixture()
            data["sim__contact_point_offsets"] = np.asarray(offsets)
            with self.subTest(offsets=offsets), self.assertRaises(ValueError):
                validate_episode(data)
        data = episode_fixture()
        data["label__success_final"] = np.asarray(True)
        with self.assertRaisesRegex(ValueError, "success"):
            validate_episode(data)


class SweepConfigTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.path = Path(self.directory.name) / "config.json"

    def load(self, config):
        self.path.write_text(json.dumps(config))
        return load_config(self.path)

    def test_cartesian_axes_preserve_coupled_properties_and_shared_seeds(self):
        source = {
            "base_properties": {"finger_friction": 0.7},
            "axes": {
                "mass": [{"mass_kg": 0.04}, {"mass_kg": 0.3}],
                "surface": [
                    {"static_friction": 0.2, "dynamic_friction": 0.1},
                    {"static_friction": 0.8, "dynamic_friction": 0.6},
                ],
                "geometry": [
                    {"shape": "cube", "size_xyz_m": [0.04] * 3},
                    {"shape": "box", "size_xyz_m": [0.03, 0.04, 0.05]},
                ],
            },
            "seeds": [42, 43],
        }
        config, conditions = self.load(source)
        self.assertEqual(len(conditions), 8)
        self.assertEqual(config["seeds"], [42, 43])
        self.assertEqual(config["episode_steps"], 100)
        self.assertEqual([c["condition_index"] for c in conditions], list(range(8)))
        self.assertEqual(len({c["condition_id"] for c in conditions}), 8)
        combinations = set()
        for condition in conditions:
            props = condition["properties"]
            self.assertEqual(props["finger_friction"], 0.7)
            pair = (props["static_friction"], props["dynamic_friction"])
            self.assertIn(pair, {(0.2, 0.1), (0.8, 0.6)})
            combinations.add((props["mass_kg"], pair, props["shape"]))
        self.assertEqual(len(combinations), 8)
        self.assertEqual(self.load(source)[1], conditions)

    def test_default_condition_and_canonical_duplicate_detection(self):
        _, conditions = self.load({"seeds": [0]})
        self.assertEqual(len(conditions), 1)
        self.assertEqual(conditions[0]["properties"]["shape"], "cube")
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            self.load({"seeds": [0], "axes": {"mass": [{"mass_kg": 1}, {"mass_kg": 1.0}]}})

    def test_overlapping_or_inconsistent_axis_keys_rejected(self):
        for axes in (
            {"a": [{"mass_kg": 0.1}], "b": [{"mass_kg": 0.2}]},
            {"surface": [{"static_friction": 0.3}, {"dynamic_friction": 0.2}]},
            {"mass": []},
        ):
            with self.subTest(axes=axes), self.assertRaises(ValueError):
                self.load({"seeds": [0], "axes": axes})

    def test_duplicate_invalid_or_absent_seeds_rejected(self):
        for seeds in ([], [1, 1], [-1], [2**31], [True], [1.0]):
            with self.subTest(seeds=seeds), self.assertRaises(ValueError):
                self.load({"seeds": seeds})

    def test_unknown_properties_and_invalid_material_pair_rejected(self):
        for properties in ({"mas_kg": 0.1}, {"static_friction": 0.1, "dynamic_friction": 0.2}):
            with self.subTest(properties=properties), self.assertRaises(ValueError):
                self.load({"seeds": [0], "base_properties": properties})


if __name__ == "__main__":
    unittest.main()

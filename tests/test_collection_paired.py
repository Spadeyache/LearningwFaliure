"""Guard experimental isolation, scale counts and force-validation semantics."""
import json
from pathlib import Path
import tempfile
import unittest

import numpy as np

from failure_collection.collect import load_config
from failure_collection.paired import force_evidence, matched_conditions


class MatchedPlanTests(unittest.TestCase):
    def load(self, config):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "config.json"
            path.write_text(json.dumps(config))
            return load_config(path)

    def test_one_family_changes_per_condition_with_mass_inertia_recomputed(self):
        conditions = matched_conditions({})
        base = conditions[0]["properties"]
        self.assertEqual(len(conditions), 7)
        self.assertEqual(len({c["condition_id"] for c in conditions}), 7)
        for condition in conditions[1:]:
            props, factor = condition["properties"], condition["shift_magnitude"]
            changed = {key for key in base if base[key] != props[key]}
            if condition["shifted_variable"] == "mass":
                self.assertEqual(changed, {"mass_kg"})
                self.assertAlmostEqual(props["mass_kg"], base["mass_kg"] * factor)
                self.assertIsNone(props["inertia_principal_kg_m2"])
            else:
                self.assertEqual(changed, {"static_friction", "dynamic_friction"})
                self.assertAlmostEqual(props["static_friction"], base["static_friction"] * factor)

    def test_single_seed_count_controls_seventy_and_three_fifty_attempts(self):
        for count in (10, 50):
            config, conditions = self.load({"experiment": "matched_mass_friction", "seed_count": count})
            self.assertEqual(config["seeds"], list(range(1000, 1000 + count)))
            self.assertEqual(len(config["seeds"]) * len(conditions), 7 * count)

    def test_conflicting_or_invalid_plan_rejected(self):
        base = {"experiment": "matched_mass_friction", "seed_count": 10}
        for invalid in ({"seeds": [1]}, {"seed_count": True}, {"seed_count": 0},
                        {"start_seed": 2**31}, {"axes": {"mass": [{"mass_kg": .1}]}},
                        {"base_properties": {"dynamic_friction": 0.0}},
                        {"base_properties": {"inertia_principal_kg_m2": [.01] * 3}}):
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                self.load({**base, **invalid})

    def test_no_grasp_zero_force_is_not_a_verified_grasp(self):
        data = {"sim__object_pair_force_peak_norm_n": np.zeros((3, 2)),
                "sim__is_grasped": np.zeros(4, dtype=bool)}
        evidence = force_evidence(data)
        self.assertEqual(evidence["grasp_samples"], 0)
        self.assertFalse(evidence["nonzero_during_grasp"])
        data["sim__is_grasped"][2] = True
        data["sim__object_pair_force_peak_norm_n"][1] = [3.0, 0.0]
        self.assertFalse(force_evidence(data)["nonzero_during_grasp"])
        data["sim__object_pair_force_peak_norm_n"][1] = [3.0, 2.0]
        self.assertTrue(force_evidence(data)["nonzero_during_grasp"])


if __name__ == "__main__":
    unittest.main()

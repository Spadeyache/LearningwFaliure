"""Guard experimental controls and the trained-policy archive interface."""
import unittest
import numpy as np
from failure_collection.varied import ROOT, conditions, load_settings
from failure_collection.schema import validate_episode
from test_collection_schema import episode_fixture


class VariedTests(unittest.TestCase):
    def test_design_contains_controls_and_both_pair_directions(self):
        config = load_settings(ROOT/'configs/failure_collection_varied.json')
        plan = conditions(config)
        self.assertEqual(len(plan), 60)
        self.assertEqual(plan, conditions(config))
        self.assertEqual(len({c['condition_id'] for c in plan}), len(plan))
        for family in ('together:mass+object_friction', 'opposite:mass+object_friction'):
            rows = [c['properties'] for c in plan if family in c['design_families']]
            self.assertEqual(len(rows), 3)
            covariance = np.cov([r['mass_kg'] for r in rows], [r['static_friction'] for r in rows])[0, 1]
            self.assertGreater(covariance if family.startswith('together') else -covariance, 0)
        singles = [c for c in plan if 'single:mass' in c['design_families']]
        self.assertEqual(len(singles), 3)
        self.assertTrue(all(set(c['changed_properties']) <= {'mass_kg'} for c in singles))

    def test_seed_count_changes_repetitions_not_physical_conditions(self):
        path = ROOT/'configs/failure_collection_varied.json'
        a, b = load_settings(path), load_settings(path, 2)
        self.assertEqual(conditions(a), conditions(b))
        with self.assertRaises(ValueError):
            load_settings(path, 0)

    def test_v3_requires_five_actions_and_preserves_v2(self):
        data = episode_fixture()
        validate_episode(data)
        data['meta__schema_version'] = np.asarray('pick_failure_v3')
        with self.assertRaises(ValueError):
            validate_episode(data)
        for key in ('input__action_raw', 'input__action_applied'):
            data[key] = np.zeros((2, 5), dtype=np.float32)
        validate_episode(data)
        del data['input__object_goal_distance_m']
        with self.assertRaises(ValueError):
            validate_episode(data)


if __name__ == '__main__':
    unittest.main()

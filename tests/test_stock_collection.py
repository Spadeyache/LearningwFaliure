"""Short-plan isolation and native-baseline recording checks."""
from copy import deepcopy
import json
from pathlib import Path
import unittest
import numpy as np

from failure_collection.stock import make_plan, validate_config, StockCollectionEnv

ROOT = Path(__file__).resolve().parents[1]


class ShortPlanTests(unittest.TestCase):
    def setUp(self):
        self.config = validate_config(json.loads((ROOT/'configs/failure_collection_stock_short.json').read_text()))
        self.plan = make_plan(self.config)

    def test_short_budget_and_single_factor_limit(self):
        self.assertEqual(len(self.plan),76)
        self.assertEqual(self.config['seed_count'],10)
        self.assertTrue(all(len(c['changed_factors'])<=1 for c in self.plan))
        self.assertEqual(len({c['condition_id'] for c in self.plan}),len(self.plan))

    def test_true_native_nominal_and_no_weight_input_configuration(self):
        b=self.plan[0]
        self.assertEqual(b['factor_values']['mass'],.064)
        self.assertEqual(b['factor_values']['object_friction'],.3)
        self.assertEqual(b['factor_values']['finger_friction'],2.)
        self.assertEqual(b['factor_values']['goal_height'],.3)
        self.assertEqual(b['changed_factors'],[])
        self.assertNotIn('reported_mass_kg',self.config)
        self.assertEqual(self.config['episode_steps'],50)

    def test_both_directions_for_interior_nominal(self):
        for name,spec in self.config['factors'].items():
            if spec['type']!='numeric' or spec['nominal'] in (spec['min'],spec['max']):continue
            values={c['factor_values'][name] for c in self.plan}
            self.assertLess(min(values),spec['nominal'],name)
            self.assertGreater(max(values),spec['nominal'],name)

    def test_no_pairs_and_reproducible_ids(self):
        self.assertEqual(self.plan,make_plan(deepcopy(self.config)))
        self.assertFalse(any('together:' in f or 'opposite:' in f for c in self.plan for f in c['design_families']))


class SavedBaselineTests(unittest.TestCase):
    @unittest.skipUnless((ROOT/'runs/failure_collection/stock_short/episodes.json').exists(),'requires saved native pilot')
    def test_stock_interface_force_and_success_semantics(self):
        folder=ROOT/'runs/failure_collection/stock_short'
        records=json.loads((folder/'episodes.json').read_text())
        for row in records:
            with np.load(folder/row['file'],allow_pickle=False) as data:
                self.assertEqual(data['sim__policy_observation'].shape,(51,42))
                self.assertEqual(data['input__action_applied'].shape,(50,4))
                self.assertNotIn('input__reported_mass_kg',data)
                np.testing.assert_array_equal(data['sim__task_success'],data['sim__at_goal'] & data['sim__robot_static'])
                self.assertEqual(bool(data['label__success_final']),row['success'])
                if row['grasped']:
                    self.assertTrue(row['bilateral_force_verified'])


if __name__=='__main__':unittest.main()

"""Dense experiment isolation and archive-interface guards."""
from copy import deepcopy
from itertools import combinations
from pathlib import Path
import tempfile
import unittest
import json
import numpy as np
from robot_adaptation.collection.varied import ROOT, conditions, load_settings
from robot_adaptation.collection.design import levels
from robot_adaptation.collection.schema import validate_episode
from test_collection_schema import episode_fixture


class VariedTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config=load_settings(ROOT/'configs/failure_collection_varied.json')
        cls.plan=conditions(cls.config)

    def test_dense_design_is_reproducible_unique_and_never_more_than_two(self):
        self.assertEqual(self.plan,conditions(self.config))
        self.assertEqual(len({c['condition_id'] for c in self.plan}),len(self.plan))
        self.assertTrue(all(len(c['changed_factors'])<=2 for c in self.plan))
        self.assertFalse(any('mixed' in c['design_families'] for c in self.plan))
        base={k:s['nominal'] for k,s in self.config['factors'].items()}
        for c in self.plan:
            self.assertEqual(set(c['changed_factors']),{k for k,v in c['factor_values'].items() if v!=base[k]})

    def test_every_numeric_variable_has_intermediate_values_and_nominal(self):
        for name,s in self.config['factors'].items():
            sampled=[c['factor_values'][name] for c in self.plan if 'single:'+name in c['design_families']]
            self.assertEqual(set(sampled),set(levels(s,self.config['levels_per_factor'])))
            self.assertIn(s['nominal'],sampled)
            if s['type']=='numeric':self.assertGreaterEqual(len(set(sampled)),11)
        mass=sorted({c['factor_values']['mass'] for c in self.plan if 'single:mass' in c['design_families']})
        self.assertIn(.1,mass);self.assertLess(max(np.diff(mass)),.05)

    def test_all_numeric_pairs_have_both_directions(self):
        specs=self.config['factors']
        for a,b in combinations(specs,2):
            for prefix in (('together:','opposite:') if specs[a]['type']==specs[b]['type']=='numeric' else ('categorical_cross:',)):
                family=prefix+a+'+'+b
                rows=[c for c in self.plan if family in c['design_families']]
                self.assertTrue(rows,family)
                self.assertTrue(all(set(c['changed_factors'])<={a,b} for c in rows))
                if prefix!='categorical_cross:':
                    covariance=np.cov([c['factor_values'][a] for c in rows],[c['factor_values'][b] for c in rows])[0,1]
                    self.assertGreater(covariance if prefix=='together:' else -covariance,0,family)

    def test_com_components_and_friction_ratio_compose_independently(self):
        pair=next(c for c in self.plan if set(c['changed_factors'])=={'com_x','com_y'} and c['factor_values']['com_x']!=0 and c['factor_values']['com_y']!=0)
        self.assertEqual(pair['properties']['com_offset_m'],[pair['factor_values']['com_x'],pair['factor_values']['com_y'],0.])
        for c in self.plan:
            p=c['properties'];v=c['factor_values']
            self.assertAlmostEqual(p['dynamic_friction'],v['object_friction']*v['dynamic_friction_ratio'],places=10)
            self.assertLessEqual(p['dynamic_friction'],p['static_friction'])

    def test_seed_count_and_disabled_factors(self):
        path=ROOT/'configs/failure_collection_varied.json'
        self.assertEqual(self.plan,conditions(load_settings(path,2)))
        with self.assertRaises(ValueError):load_settings(path,0)
        changed=deepcopy(self.config)
        for s in changed['factors'].values():s['enabled']=False
        changed['factors']['mass']['enabled']=True
        self.assertTrue(all(set(c['changed_factors'])<={'mass'} for c in conditions(changed)))

    def test_v3_requires_five_actions_and_preserves_v2(self):
        data=episode_fixture();validate_episode(data)
        data['meta__schema_version']=np.asarray('pick_failure_v3')
        with self.assertRaises(ValueError):validate_episode(data)
        for key in ('input__action_raw','input__action_applied'):data[key]=np.zeros((2,5),dtype=np.float32)
        validate_episode(data)
        del data['input__object_goal_distance_m']
        with self.assertRaises(ValueError):validate_episode(data)


if __name__=='__main__':unittest.main()

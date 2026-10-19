"""Control for confounding, missing evidence and joint-only responses."""
import unittest
from copy import deepcopy
from response_groups import find_grid, observed_profile, build_profiles


def sample_records():
    return {(m,f,0):dict(episode=f'{m}_{f}_0',file=f'{m}_{f}_0.npz',seed=0,mass=m,friction=f,success=m==2 and f==2)
            for m in [1,2] for f in [1,2]}


class ResponseTests(unittest.TestCase):
    def test_only_one_factor_changes_in_each_response(self):
        records=sample_records();source=records[(1,1,0)]
        responses=observed_profile(source,records,[1,2],[1,2])
        self.assertEqual([r['target_episode'] for r in responses],['1_1_0','2_1_0','1_1_0','1_2_0'])
        self.assertEqual([r['changed'] for r in responses],[False,True,False,True])
        self.assertFalse(any(r['success'] for r in responses))

    def test_joint_success_does_not_become_single_variable_success(self):
        records=sample_records();rows,_,_=build_profiles(records,[1,2],[1,2])
        row=next(r for r in rows if r['episode']=='1_1_0')
        self.assertEqual(row['minimum_changed_factors_among_tested_successes'],2)
        self.assertEqual(row['signature'],'0000')
        self.assertEqual(row['successful_joint_settings'],'[[2, 2]]')

    def test_missing_trial_is_not_imputed_as_failure(self):
        records=sample_records();del records[(2,1,0)]
        with self.assertRaisesRegex(ValueError,'Missing counterfactual'):
            observed_profile(records[(1,1,0)],records,[1,2],[1,2])

    def test_no_motion_or_failure_name_is_needed(self):
        records=sample_records();expected=build_profiles(records,[1,2],[1,2])
        for r in records.values():r.update(failure_type='invented',motion='arbitrary')
        self.assertEqual(expected,build_profiles(records,[1,2],[1,2]))

    def test_groups_reproduce_across_order(self):
        records=sample_records();self.assertEqual(build_profiles(records,[1,2],[1,2]),
            build_profiles(dict(reversed(list(records.items()))),[1,2],[1,2]))

    def test_grid_excludes_changes_in_other_factors(self):
        conditions=[]
        for m in [1,2]:
            for f in [1,2]:conditions.append(dict(condition_id=f'{m}_{f}',changed_factors=[] if (m,f)==(1,1) else ['mass'],
                factor_values=dict(mass=m,object_friction=f,size=1)))
        changed=deepcopy(conditions[-1]);changed['condition_id']='confounded';changed['factor_values']['size']=2
        self.assertEqual(len(find_grid(conditions+[changed],[1,2],[1,2])),4)
        with self.assertRaisesRegex(ValueError,'Missing grid'):
            find_grid(conditions[:-1]+[changed],[1,2],[1,2])


if __name__=='__main__':unittest.main()

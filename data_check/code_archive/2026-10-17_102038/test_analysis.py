"""Focused guards for rotation gaps, missing-time masks and seed leakage."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent/'.deps'))
import unittest
import numpy as np
from data import rotation_gap,masked_interpolate,CHANNELS,load_dataset
from models import predict_cv


class AnalysisTests(unittest.TestCase):
    def test_quaternion_sign_is_not_a_gap(self):
        q=np.array([[1.,0,0,0],[np.cos(.2),0,0,np.sin(.2)]])
        np.testing.assert_allclose(rotation_gap(q,-q),0,atol=1e-12)

    def test_rotation_gap_is_relative_rotation(self):
        a=np.array([[np.cos(np.pi/4),0,0,np.sin(np.pi/4)]])
        np.testing.assert_allclose(rotation_gap(a,np.array([[1,0,0,0]])),[[0,0,np.pi/2]],atol=1e-12)

    def test_alignment_never_extrapolates(self):
        value,valid=masked_interpolate(np.array([0.,1.]),np.array([[1.,2.],[3.,4.]]),np.array([-.1,.5,1.1]))
        np.testing.assert_array_equal(valid,[False,True,False])
        self.assertTrue(np.isnan(value[[0,2]]).all())
        np.testing.assert_allclose(value[1],[2,3])

    def test_folds_keep_seeds_disjoint(self):
        seeds=np.repeat(np.arange(10),2);y=np.tile(np.array(['mass','friction']),10)
        x=np.random.default_rng(0).normal(size=(20,3,len(CHANNELS)))
        result=predict_cv(x,y,seeds,top=2)
        self.assertEqual(len(result['pred']),len(y))
        tests=[]
        for fold in result['folds']:
            self.assertFalse(set(fold['train_seeds'])&set(fold['test_seeds']))
            tests.extend(fold['test_seeds'])
        self.assertEqual(sorted(tests),list(range(10)))

    def test_current_dataset_pairing_and_coverage(self):
        d=load_dataset(Path(__file__).resolve().parents[1]/'runs/failure_collection/varied_fixed40g')
        self.assertEqual(len(d['records']),600)
        self.assertEqual(int(d['success'].sum()),202)
        self.assertTrue(d['valid'].all())
        np.testing.assert_allclose(d['gap'][d['single']=='nominal'],0,atol=1e-12)
        ix=d['seed']==2000
        self.assertTrue(np.isnan(d['lift_gap'][ix]).all())
        self.assertFalse(d['lift_valid'][ix].any())
        self.assertTrue(all(r['reset_matches_nominal'] for r in d['records'] if r['single'] in ('mass','object_friction')))
        self.assertEqual(d['gap'].shape[-1],len(CHANNELS))


if __name__=='__main__':unittest.main()

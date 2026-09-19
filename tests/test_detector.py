import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
import numpy as np
import torch
from calibrate_detector import residual_score
from pose_model import INPUT_DIM, PosePredictor, prepare_episode


class DetectorTests(unittest.TestCase):
    def test_group_scores_respect_units(self):
        errors=np.array([[.002,.03,.001,.01]])
        score=residual_score(errors,np.array([.001,.01,.001,.01]))
        self.assertEqual(float(score[0]),3.)

    def test_feature_alignment_excludes_future_observations(self):
        T=5
        pose=np.tile(np.array([0,0,0,1,0,0,0],dtype=np.float32),(T+1,1))
        pose[:,0]=np.arange(T+1)*.01
        data={"qpos":np.zeros((T+1,9)), "qvel":np.zeros((T+1,9)),
              "ee_pose":pose.copy(),"cube_pose":pose.copy(),
              "goal_pos":np.zeros((T+1,3)),"action":np.zeros((T,8))}
        before=prepare_episode(data)
        data["cube_pose"][4:,0]+=10
        after=prepare_episode(data)
        self.assertTrue(torch.equal(before["x"][:4],after["x"][:4]))
        self.assertTrue(torch.allclose(before["target"][:,0],torch.full((T,),.01),atol=1e-7))
        self.assertEqual(float(before["base"][0,0]),0.)

    def test_streaming_matches_full_causal_sequence(self):
        torch.manual_seed(3)
        model=PosePredictor().eval()
        torch.nn.init.normal_(model.head[-1].weight,std=.01)
        x=torch.randn(1,9,INPUT_DIM)
        full,_=model(x)
        outputs=[]; hidden=None
        for t in range(9):
            output,hidden=model(x[:,t:t+1],hidden)
            outputs.append(output)
        self.assertTrue(torch.allclose(full,torch.cat(outputs,dim=1),atol=1e-6))


if __name__=="__main__":
    unittest.main()

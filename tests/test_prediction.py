import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/"scripts"))
import torch
from pose_model import INPUT_DIM, PosePredictor, apply_delta, pose_delta, pose_errors


class PoseMathTests(unittest.TestCase):
    def test_quaternion_sign_does_not_change_error(self):
        p = torch.tensor([[0.,0.,0.,1.,0.,0.,0.]*2])
        q = p.clone()
        q[:,3:7] *= -1
        q[:,10:14] *= -1
        self.assertTrue(torch.allclose(pose_errors(p,q), torch.zeros(1,4)))

    def test_rotation_and_translation_round_trip(self):
        p = torch.tensor([[0.,0.,0.,1.,0.,0.,0.]*2])
        d = torch.tensor([[.01,.02,-.03,.1,-.2,.3,-.02,.04,.1,-.4,.2,.1]])
        restored = pose_delta(p,apply_delta(p,d))
        self.assertTrue(torch.allclose(restored,d,atol=1e-6))

    def test_model_is_causal(self):
        torch.manual_seed(0)
        model = PosePredictor()
        torch.nn.init.normal_(model.head[-1].weight, std=.02)
        x = torch.randn(1,12,INPUT_DIM)
        altered = x.clone()
        altered[:,7:] += 100
        a,_ = model(x)
        b,_ = model(altered)
        self.assertTrue(torch.allclose(a[:,:7],b[:,:7],atol=1e-6))

    def test_fresh_model_starts_at_constant_velocity(self):
        model = PosePredictor()
        output,_ = model(torch.randn(2,5,INPUT_DIM))
        self.assertTrue(torch.equal(output,torch.zeros_like(output)))


if __name__ == "__main__":
    unittest.main()

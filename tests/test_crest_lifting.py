"""Small opt-in CPU integration: held lift, appearance control, goal repair."""
import os
import json
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
import tempfile
import unittest
import numpy as np


@unittest.skipUnless(os.environ.get("RUN_CREST_INTEGRATION") == "1", "set RUN_CREST_INTEGRATION=1")
class LiftIntegrationTests(unittest.TestCase):
    def test_cli_budget_resume_and_provenance(self):
        from experiments.crest.__main__ import main
        from experiments.crest.config import ROOT
        with tempfile.TemporaryDirectory() as folder:
            directory = Path(folder)
            config = json.loads((ROOT / "configs/crest_lift.json").read_text())
            config["factor_config"] = str(ROOT / "configs/failure_collection_varied.json")
            config["experiment"].update(context_count=1, random_interventions=0)
            config_path = directory / "config.json"
            config_path.write_text(json.dumps(config))
            output = directory / "run"
            args = ["--config", str(config_path), "--run", "--only", "object_color_r", "--output", str(output)]
            with redirect_stdout(StringIO()):
                self.assertEqual(main(args + ["--max-rollouts", "1"]), 2)
                self.assertEqual(json.loads((output / "manifest.json").read_text())["status"], "budget_exhausted")
                self.assertFalse((output / "report.json").exists())
                self.assertEqual(main(args + ["--resume", "--max-rollouts", "2"]), 0)
                first_journal = (output / "evaluations.jsonl").read_bytes()
                self.assertEqual(main(args + ["--resume", "--max-rollouts", "2"]), 0)
            self.assertEqual(first_journal, (output / "evaluations.jsonl").read_bytes())
            report = json.loads((output / "report.json").read_text())
            self.assertEqual(report["physical_rollouts"], 2)
            self.assertEqual(report["not_detected"], ["object_color_r"])
            self.assertEqual(report["solved_anchors"], 1)
            self.assertTrue((output / "source/experiments/crest/core.py").is_file())
            config["experiment"]["seed"] += 1
            config_path.write_text(json.dumps(config))
            with redirect_stdout(StringIO()), self.assertRaisesRegex(ValueError, "identical scientific"):
                main(args + ["--resume"])

    def test_success_color_invariance_and_sparse_goal_repair(self):
        import torch
        from experiments.crest.config import load_config
        from experiments.crest.core import minimum_support_repair
        from experiments.crest.lifting import LiftingTask
        torch.set_num_threads(1)
        config, contexts, parameters = load_config()
        task = LiftingTask(contexts, parameters, **config["task"])
        try:
            base = contexts.nominal
            theta = task.initial_parameters(base, 2000)
            baseline = task.evaluate(base, theta, 2000)
            self.assertTrue(baseline.success, baseline.metrics)
            np.testing.assert_allclose(baseline.metrics["initial_object_pose"][:3], [0., 0., .02], atol=1e-7)
            color = dict(base, object_color_g=1.)
            painted = task.evaluate(color, theta, 2000)
            self.assertTrue(painted.success)
            self.assertEqual(painted.metrics["initial_state_sha256"], baseline.metrics["initial_state_sha256"])
            self.assertAlmostEqual(painted.score, baseline.score, places=6)
            shifted = dict(base, goal_height=.3)
            frozen = task.evaluate(shifted, theta, 2000)
            self.assertFalse(frozen.success)
            repaired = theta.copy()
            repaired[3] += .1
            result = task.evaluate(shifted, repaired, 2000)
            self.assertTrue(result.success, result.metrics)
            sparse = minimum_support_repair(lambda t: task.evaluate(shifted, t, 2000), theta, repaired)
            self.assertEqual(sparse.indices, (3,))
            physical = baseline.metrics["physics"]
            self.assertAlmostEqual(physical["mass_kg"], base["mass"], places=6)
            self.assertAlmostEqual(physical["object_materials"][0]["static_friction"], base["object_friction"], places=6)
        finally:
            task.close()


if __name__ == "__main__":
    unittest.main()

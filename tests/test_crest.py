"""CREST invariants on known causal systems, independently of simulation."""
from contextlib import redirect_stdout
from io import StringIO
from itertools import product
from pathlib import Path
import builtins
import tempfile
import unittest
from unittest.mock import patch

import numpy as np

from experiments.crest.config import load_config
from experiments.crest.core import Evaluation, minimum_support_repair, run_crest
from experiments.crest.optimization import REPSOptimizer, Solution, reps_weights
from experiments.crest.spaces import ContextSpace, Factor, ParameterSpace


def numeric(name, nominal=0., enabled=True):
    return Factor.from_spec(name, dict(type="numeric", min=-1., max=1., nominal=nominal, enabled=enabled))


class KnownTask:
    def __init__(self):
        self.calls = []

    def validate_context(self, context):
        pass

    def initial_parameters(self, context, seed):
        return np.zeros(2)

    def evaluate(self, context, theta, seed):
        self.calls.append((dict(context), np.array(theta), seed))
        error = abs(theta[0] - context["x"]) + abs(theta[1] - context["y"])
        return Evaluation(bool(error < 1e-9), -float(error))


class GridSolver:
    def solve(self, evaluate, initial, rng):
        for count, values in enumerate([initial, *product((-1., 0., 1.), repeat=2)], 1):
            theta = np.asarray(values, float)
            result = evaluate(theta)
            if result.success:
                return Solution(theta, result, count)
        return Solution(theta, result, count)


class CrestTests(unittest.TestCase):
    def setUp(self):
        self.contexts = ContextSpace([numeric("x"), numeric("y"), numeric("nuisance")])
        self.parameters = ParameterSpace({"a": dict(min=-1., max=1.), "b": dict(min=-1., max=1.)})

    def test_known_structure_and_frozen_controller_interventions(self):
        task = KnownTask()
        report = run_crest(task, self.contexts, self.parameters, GridSolver(), context_count=2,
                           nominal_first=True, random_interventions=0)
        self.assertEqual(set(report["confirmed_relevant"]), {"x", "y"})
        self.assertEqual(report["observed_parents"], {"a": ["x"], "b": ["y"]})
        self.assertEqual(report["not_detected"], ["nuisance"])
        for row in report["records"]:
            if row["kind"] != "intervention":
                continue
            delta = {name for name in row["context"]
                     if row["context"][name] != row["original_context"][name]}
            self.assertEqual(delta, {row["factor"]})
            frozen = list(row["original_theta"].values())
            # Dict insertion order here is parameter order before JSON serialization.
            self.assertTrue(any(c == row["context"] and seed == row["seed"]
                                and np.array_equal(t, frozen) for c, t, seed in task.calls))

    def test_sparse_search_minimizes_count_not_delta_magnitude(self):
        def evaluate(theta):
            return Evaluation(bool(theta[2] == 100. or (theta[0] == .01 and theta[1] == .01)), 0.)
        found = minimum_support_repair(evaluate, [0, 0, 0], [.01, .01, 100])
        self.assertEqual(found.indices, (2,))
        self.assertEqual(found.status, "minimum_subset")

    def test_sparse_budget_is_unknown_not_false_mapping(self):
        found = minimum_support_repair(lambda t: Evaluation(bool(np.all(t == 1)), 0.),
                                      [0, 0, 0], [1, 1, 1], max_evaluations=2)
        self.assertIsNone(found.indices)
        self.assertEqual(found.status, "budget_exhausted")

    def test_unsolved_baseline_does_not_claim_irrelevance(self):
        class NeverSolves(KnownTask):
            def evaluate(self, context, theta, seed):
                return Evaluation(False, -1.)
        report = run_crest(NeverSolves(), self.contexts, self.parameters, GridSolver(), context_count=1)
        self.assertEqual(report["solved_anchors"], 0)
        self.assertEqual(report["not_detected"], [])
        self.assertEqual(set(report["selected_context"]), set(self.contexts.names))

    def test_failed_repair_keeps_ambiguous_factor_in_every_head(self):
        class CannotRepair(KnownTask):
            def evaluate(self, context, theta, seed):
                return Evaluation(context["x"] == 0, -1.)
        report = run_crest(CannotRepair(), self.contexts, self.parameters, GridSolver(),
                           context_count=1, random_interventions=0)
        self.assertIn("x", report["unresolved"])
        self.assertNotIn("x", report["confirmed_relevant"])
        for names in report["conservative_parents"].values():
            self.assertIn("x", names)

    def test_categorical_encoding_and_single_factor_interventions(self):
        shape = Factor.from_spec("shape", dict(type="categorical", nominal="cube", values=["cube", "sphere"]))
        space = ContextSpace([shape, numeric("fixed", enabled=False)])
        np.testing.assert_array_equal(space.encode(space.nominal), [1., 0., .5])
        rows = list(space.interventions(space.nominal, 5, np.random.default_rng(0)))
        self.assertEqual(rows, [("shape", {"shape": "sphere", "fixed": 0.})])
        self.assertEqual(space.feature_indices(["shape"]), [0, 1])

    def test_reps_weights_obey_kl_bound_and_prefer_high_reward(self):
        weights = reps_weights([-10., -1., 0., 2.], .2)
        self.assertAlmostEqual(float(weights.sum()), 1.)
        self.assertTrue(np.all(np.diff(weights) > 0))
        kl = np.sum(weights * np.log(weights * len(weights)))
        self.assertLessEqual(kl, .2001)
        np.testing.assert_allclose(reps_weights([1., 1.], .5), [.5, .5])

    def test_reps_solves_a_bounded_continuous_problem(self):
        space = ParameterSpace({"x": dict(min=-2., max=2.)})
        optimizer = REPSOptimizer(space, population=20, iterations=10, initial_std=.3)
        fit = optimizer.solve(lambda x: Evaluation(bool(abs(x[0] - 1) < .06), -float((x[0] - 1) ** 2)),
                              [-1.], np.random.default_rng(9))
        self.assertTrue(fit.result.success)
        space.validate(fit.theta)

    def test_default_plan_is_simulator_free_and_includes_existing_factors(self):
        from experiments.crest.__main__ import main
        config, contexts, parameters = load_config()
        self.assertEqual(len(contexts.names), 21)
        self.assertEqual(len(contexts.feature_names), 22)
        original_import = builtins.__import__

        def guarded(name, *args, **kwargs):
            if name.split(".")[0] in {"mani_skill", "sapien", "torch"}:
                raise AssertionError("Plan tried to import simulation")
            return original_import(name, *args, **kwargs)

        with patch("builtins.__import__", guarded), redirect_stdout(StringIO()):
            self.assertEqual(main(["--plan-only"]), 0)

    def test_cache_caps_real_rollouts_and_recovers_them_without_reexecution(self):
        from experiments.crest.__main__ import CachedTask, RolloutBudgetExceeded
        task = KnownTask()
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "evaluations.jsonl"
            cached = CachedTask(task, self.parameters, path, 1)
            result = cached.evaluate(self.contexts.nominal, [0., 0.], 2000)
            self.assertTrue(result.success)
            recovered = CachedTask(task, self.parameters, path, 1)
            recovered.evaluate(self.contexts.nominal, [0., 0.], 2000)
            self.assertEqual(len(task.calls), 1)
            with self.assertRaises(RolloutBudgetExceeded):
                recovered.evaluate(self.contexts.nominal, [1., 0.], 2000)

    def test_reduced_and_partitioned_policies_do_not_read_removed_inputs(self):
        import torch
        from experiments.crest.policies import PartitionedMLP, ReducedMLP
        report = run_crest(KnownTask(), self.contexts, self.parameters, GridSolver(),
                           context_count=1, random_interventions=0)
        x = torch.tensor([[.2, .4, .1], [.2, .4, .9]])
        for model in (ReducedMLP(report), PartitionedMLP(report)):
            output = model(x)
            self.assertEqual(output.shape, (2, 2))
            torch.testing.assert_close(output[0], output[1])
            output.sum().backward()


if __name__ == "__main__":
    unittest.main()

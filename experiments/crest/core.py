"""CREST Section IV-B: intervention screening and minimum-support repair.

The task interface is independent of ManiSkill, torch and neural architectures.
Every anchor and intervention uses the SAME reset seed. Different reset seeds
are independently solved anchors, not confounded changes within an intervention.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from itertools import combinations
from typing import Protocol

import numpy as np

from .optimization import REPSOptimizer
from .spaces import ContextSpace, ParameterSpace


@dataclass(frozen=True)
class Evaluation:
    success: bool
    score: float
    metrics: dict = field(default_factory=dict)

    def __post_init__(self):
        if not isinstance(self.success, (bool, np.bool_)) or not np.isfinite(self.score):
            raise ValueError("Evaluation needs a boolean success and finite score")


class Task(Protocol):
    def validate_context(self, context: dict) -> None: ...
    def initial_parameters(self, context: dict, seed: int) -> np.ndarray: ...
    def evaluate(self, context: dict, theta: np.ndarray, seed: int) -> Evaluation: ...


@dataclass
class SparseRepair:
    status: str
    indices: tuple[int, ...] | None
    theta: np.ndarray | None
    evaluations: int


def minimum_support_repair(evaluate, original, repaired, *, max_evaluations=256):
    """Breadth-first search over subsets of the discovered parameter delta.

This is minimal among subsets of THIS repair, not all possible controller
solutions. Budget exhaustion returns unknown, never a fabricated dependency.
"""
    original, repaired = np.asarray(original, float), np.asarray(repaired, float)
    if original.shape != repaired.shape or original.ndim != 1 or max_evaluations < 1:
        raise ValueError("Sparse repair requires matching vectors and a positive budget")
    changed = np.flatnonzero(repaired != original).tolist()
    count = 0
    # Include the empty subset: stochastic/non-repeatable evaluations must not
    # create an apparent dependence if the original now succeeds.
    for size in range(len(changed) + 1):
        for subset in combinations(changed, size):
            if count >= max_evaluations:
                return SparseRepair("budget_exhausted", None, None, count)
            candidate = original.copy()
            candidate[list(subset)] = repaired[list(subset)]
            result = evaluate(candidate)
            count += 1
            if result.success:
                return SparseRepair("minimum_subset" if subset else "original_succeeds",
                                    subset, candidate, count)
    return SparseRepair("repair_not_reproduced", None, None, count)


def run_crest(task: Task, contexts: ContextSpace, parameters: ParameterSpace,
              optimizer: REPSOptimizer, *, seed=0, context_count=4, start_seed=2000,
              random_interventions=1, nominal_first=True, max_sparse_evaluations=256,
              on_record=None):
    """Identify context relevance and per-controller-parameter parent sets.

Unsolved anchors, invalid interventions and failed repairs are explicitly
retained. ``not_detected`` only means no failure was seen in tested contexts.
Neither this implementation nor CREST establishes global causal irrelevance.
"""
    if context_count < 1 or random_interventions < 0 or start_seed < 0:
        raise ValueError("Invalid experiment counts or reset seed")
    rng = np.random.default_rng(seed)
    records, training_examples = [], []
    evidence = {f.name: dict(tested=0, failures=0, repaired=0, mapped=0, invalid=0)
                for f in contexts.factors if f.enabled}
    parents = {name: set() for name in parameters.names}
    unresolved = set()

    def record(item):
        records.append(item)
        if on_record:
            on_record(item)

    for anchor in range(context_count):
        context = contexts.nominal if nominal_first and anchor == 0 else contexts.sample(rng)
        reset_seed = start_seed + anchor
        try:
            task.validate_context(context)
        except ValueError as error:
            record(dict(kind="anchor", anchor=anchor, context=context, seed=reset_seed,
                        status="invalid_context", reason=str(error)))
            continue
        evaluate_base = lambda theta: task.evaluate(context, theta, reset_seed)
        baseline = optimizer.solve(evaluate_base, task.initial_parameters(context, reset_seed), rng)
        record(dict(kind="anchor", anchor=anchor, context=context, seed=reset_seed,
                    status="solved" if baseline.result.success else "unsolved",
                    theta=parameters.as_dict(baseline.theta), result=asdict(baseline.result)))
        if not baseline.result.success:
            continue
        training_examples.append(dict(context=context, theta=baseline.theta.tolist(),
                                      seed=reset_seed, source="anchor"))
        for factor, modified in contexts.interventions(context, random_interventions, rng):
            info = evidence[factor]
            item = dict(kind="intervention", anchor=anchor, seed=reset_seed, factor=factor,
                        original_context=context, context=modified,
                        original_theta=parameters.as_dict(baseline.theta))
            try:
                task.validate_context(modified)
            except ValueError as error:
                info["invalid"] += 1
                unresolved.add(factor)
                record(dict(item, status="invalid_context", reason=str(error)))
                continue
            frozen_result = task.evaluate(modified, baseline.theta, reset_seed)
            info["tested"] += 1
            item["frozen_result"] = asdict(frozen_result)
            if frozen_result.success:
                record(dict(item, status="unchanged_controller_succeeds"))
                continue
            info["failures"] += 1
            evaluate_modified = lambda theta: task.evaluate(modified, theta, reset_seed)
            repair = optimizer.solve(evaluate_modified, baseline.theta, rng)
            item.update(repaired_theta=parameters.as_dict(repair.theta),
                        repaired_result=asdict(repair.result))
            if not repair.result.success:
                unresolved.add(factor)
                record(dict(item, status="unresolved_repair"))
                continue
            info["repaired"] += 1
            training_examples.append(dict(context=modified, theta=repair.theta.tolist(),
                                          seed=reset_seed, source="repair"))
            sparse = minimum_support_repair(evaluate_modified, baseline.theta, repair.theta,
                                           max_evaluations=max_sparse_evaluations)
            item.update(sparse_status=sparse.status, sparse_evaluations=sparse.evaluations)
            if sparse.indices:
                changed_names = [parameters.names[index] for index in sparse.indices]
                for name in changed_names:
                    parents[name].add(factor)
                info["mapped"] += 1
                item.update(status="mapped", changed_parameters=changed_names,
                            sparse_theta=parameters.as_dict(sparse.theta))
                training_examples.append(dict(context=modified, theta=sparse.theta.tolist(),
                                              seed=reset_seed, source="sparse_repair"))
            else:
                unresolved.add(factor)
                item["status"] = "mapping_unresolved"
            record(item)

    observed_relevant = [name for name, e in evidence.items() if e["failures"]]
    confirmed = [name for name, e in evidence.items() if e["repaired"]]
    untested = [name for name, e in evidence.items() if not e["tested"]]
    not_detected = [name for name, e in evidence.items() if e["tested"] and not e["failures"]]
    # Never silently discard factors when a baseline/repair/mapping failed.
    uncertain = unresolved | set(untested)
    selected = [name for name in contexts.names if name in set(observed_relevant) | uncertain]
    conservative_parents = {name: [f for f in contexts.names if f in found | uncertain]
                            for name, found in parents.items()}
    return dict(
        method="CREST_section_IV_B", context_names=list(contexts.names),
        feature_names=list(contexts.feature_names), parameter_names=list(parameters.names),
        solved_anchors=sum(r["kind"] == "anchor" and r["status"] == "solved" for r in records),
        observed_relevant=observed_relevant, confirmed_relevant=confirmed,
        not_detected=not_detected, untested=untested, unresolved=sorted(unresolved),
        evidence=evidence, observed_parents={k: sorted(v) for k, v in parents.items()},
        selected_context=selected, conservative_parents=conservative_parents,
        reduced_feature_indices=contexts.feature_indices(selected),
        partitioned_feature_indices={k: contexts.feature_indices(v)
                                     for k, v in conservative_parents.items()},
        records=records, training_examples=training_examples,
        interpretation="Finite tested contexts/ranges and this lower controller only; "
                       "not_detected is not proof of irrelevance. Unresolved factors remain in masks.",
    )

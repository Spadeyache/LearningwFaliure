"""Load the existing experiment factors and a separate CREST configuration."""
from copy import deepcopy
import json
from pathlib import Path

from .optimization import REPSOptimizer
from .spaces import ContextSpace, Factor, ParameterSpace

from robot_adaptation.paths import ROOT


def load_config(path=ROOT / "configs/crest_lift.json", *, only=None):
    path = Path(path).resolve()
    config = json.loads(path.read_text())
    required = {"factor_config", "extra_factors", "parameters", "experiment", "optimizer", "task", "max_rollouts"}
    if set(config) != required:
        raise ValueError(f"CREST config requires exactly {sorted(required)}")
    collection = json.loads((path.parent / config["factor_config"]).read_text())
    factors = deepcopy(collection["factors"])
    if set(factors) & set(config["extra_factors"]):
        raise ValueError("Extra factors cannot replace existing collection factors")
    factors.update(config["extra_factors"])
    if only is not None:
        unknown = set(only) - set(factors)
        if unknown or not only:
            raise ValueError(f"--only needs known factors, got {sorted(unknown)}")
        for name, spec in factors.items():
            spec["enabled"] = name in only
    contexts = ContextSpace([Factor.from_spec(name, spec) for name, spec in factors.items()])
    parameters = ParameterSpace(config["parameters"])
    REPSOptimizer(parameters, **config["optimizer"])  # validates without running
    integers = {"seed": 0, "context_count": 1, "start_seed": 0,
                "random_interventions": 0, "max_sparse_evaluations": 1}
    experiment = config["experiment"]
    if set(experiment) != set(integers) | {"nominal_first"}:
        raise ValueError("Unknown/missing CREST experiment settings")
    for name, minimum in integers.items():
        if type(experiment[name]) is not int or experiment[name] < minimum:
            raise ValueError(f"Invalid integer experiment setting: {name}")
    if type(experiment["nominal_first"]) is not bool:
        raise ValueError("nominal_first must be boolean")
    if experiment["start_seed"] + experiment["context_count"] >= 2 ** 31:
        raise ValueError("Reset seeds must fit in 31 bits")
    if type(config["max_rollouts"]) is not int or config["max_rollouts"] < 1:
        raise ValueError("max_rollouts must be a positive integer")
    task = config["task"]
    if set(task) != {"episode_steps", "hold_steps", "grip_limits"}:
        raise ValueError("Unknown/missing lift task settings")
    if any(type(task[k]) is not int or task[k] < 1 for k in ("episode_steps", "hold_steps")):
        raise ValueError("Task durations must be positive integers")
    if task["hold_steps"] > task["episode_steps"]:
        raise ValueError("Hold window exceeds episode length")
    effective = {**config, "factors": factors}
    return effective, contexts, parameters


def describe_plan(config, contexts, parameters):
    enabled = [f for f in contexts.factors if f.enabled]
    per_context = sum((len(f.choices) - 1 if f.kind == "categorical" else
                       2 + config["experiment"]["random_interventions"]) for f in enabled)
    anchors = config["experiment"]["context_count"]
    max_solve = 1 + config["optimizer"]["iterations"] * config["optimizer"]["population"]
    upper_bound = anchors * (max_solve + per_context * (
        1 + max_solve + config["experiment"]["max_sparse_evaluations"]))
    return dict(candidate_factors=len(contexts.factors), enabled_factors=[f.name for f in enabled],
                encoded_features=len(contexts.feature_names), controller_parameters=list(parameters.names),
                anchors=anchors, intervention_upper_bound=anchors * per_context,
                rollout_upper_bound_before_cache_or_early_stopping=upper_bound,
                enforced_rollout_budget=config["max_rollouts"],
                episode_steps=config["task"]["episode_steps"],
                physics_started=False, files_written=False)

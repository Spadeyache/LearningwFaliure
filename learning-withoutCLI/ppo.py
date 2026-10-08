"""THE MODEL: pinned ManiSkill actor/critic, extended to 43 inputs.

Three 256-unit tanh layers per network, four action outputs, learned Gaussian
exploration. The original ManiSkill PPO loop is used by train_ppo.py as well.
"""
import importlib.util
from pathlib import Path
from types import SimpleNamespace
import sys
import torch

SOURCE_COMMIT = "a4a4f9272ad64b1564035874b605ceb687b63ed8"
SOURCE = Path(__file__).resolve().parent / "examples" / "maniskill_pick_cube" / "ppo_upstream.py"


def _upstream():
    name = "weighted_pick_cube_upstream"
    if name not in sys.modules:
        spec = importlib.util.spec_from_file_location(name, SOURCE)
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)
    return sys.modules[name]


class Agent(_upstream().Agent):
    def __init__(self, envs=None):
        if envs is None:
            envs = SimpleNamespace(single_observation_space=SimpleNamespace(shape=(43,)),
                                   single_action_space=SimpleNamespace(shape=(4,)))
        if envs.single_observation_space.shape != (43,) or envs.single_action_space.shape != (4,):
            raise ValueError("Weighted PickCube requires 43 measurements and four actions")
        super().__init__(envs)


def initialize_from_pretrained(agent, checkpoint):
    """Copy the published 42-input policy; start the new weight column at ZERO.

    Initial behavior remains exactly the same and initially ignores weight.
    PPO can learn the new column. Initialization alone is NOT adaptation.
    """
    published = torch.load(checkpoint, map_location="cpu", weights_only=True)
    current = agent.state_dict()
    if set(published) != set(current):
        raise ValueError("Expected the official state-policy checkpoint")
    for name, target in current.items():
        source = published[name]
        if name in ("actor_mean.0.weight", "critic.0.weight"):
            if source.shape != (256, 42):
                raise ValueError("Expected the published 42-input, 256-unit network")
            target.zero_()
            target[:, :42].copy_(source)
        else:
            if source.shape != target.shape:
                raise ValueError("Checkpoint/controller dimensions do not match")
            target.copy_(source)
    agent.load_state_dict(current)
    return agent

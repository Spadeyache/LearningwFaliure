"""THE MODEL: ManiSkill PPO networks extended to 45 inputs and five actions.

Keep the first 43 inputs and first four actions in their existing order.
Append two measured finger forces and a motor-strength-limit action.
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
            envs = SimpleNamespace(single_observation_space=SimpleNamespace(shape=(45,)),
                                   single_action_space=SimpleNamespace(shape=(5,)))
        if envs.single_observation_space.shape != (45,) or envs.single_action_space.shape != (5,):
            raise ValueError("Grip-aware PickCube requires 45 measurements and five actions")
        super().__init__(envs)


def initialize_from_pretrained(agent, checkpoint, initial_strength_action=1.):
    """Warm-start from the user's 43/4 policy, official 42/4, or current 45/5.

    New force-input columns start at zero. Preserve learned arm/opening actions
    and critic predictions. The new strength output initially requests the
    maximum allowed strength, with exploration; PPO can learn to reduce it.
    The motor cap differs from the former fixed 100 N, so identical network
    outputs do not imply identical physical trajectories.
    """
    source = torch.load(checkpoint, map_location="cpu", weights_only=True)
    current = agent.state_dict()
    if set(source) != set(current):
        raise ValueError("Unsupported actor/critic checkpoint")
    inputs = source["actor_mean.0.weight"].shape[1]
    actions = source["actor_mean.6.weight"].shape[0]
    if (inputs, actions) not in ((42, 4), (43, 4), (45, 5)):
        raise ValueError("Expected a published 42/4, weighted 43/4, or grip-aware 45/5 policy")
    for name, target in current.items():
        old = source[name]
        if name in ("actor_mean.0.weight", "critic.0.weight"):
            if old.shape != (256, inputs):
                raise ValueError("First-layer architecture mismatch")
            target.zero_()
            target[:, :inputs].copy_(old)
        elif name == "actor_mean.6.weight":
            if old.shape != (actions, 256):
                raise ValueError("Actor-output architecture mismatch")
            target.zero_()
            target[:actions].copy_(old)
        elif name == "actor_mean.6.bias":
            target.zero_()
            target[:actions].copy_(old)
            if actions == 4:
                target[4] = initial_strength_action
        elif name == "actor_logstd":
            target.fill_(-1.)
            target[:, :actions].copy_(old)
        else:
            if old.shape != target.shape:
                raise ValueError("Checkpoint architecture mismatch: " + name)
            target.copy_(old)
    agent.load_state_dict(current)
    return agent

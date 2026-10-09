"""ONE POLICY, TWO BRANCHES: preserve movement; learn grip strength separately.

actor_mean is the saved movement/opening network, frozen byte-for-byte.
strength_mean is an independent copy whose last output learns the motor cap.
The critic learns expected rewards. PPO likelihood/entropy use ONLY strength:
the other four actions are deterministic and are not optimized or resampled.
"""
from copy import deepcopy
import importlib.util
from pathlib import Path
from types import SimpleNamespace
import sys
import torch
from torch import nn
from torch.distributions import Normal

SOURCE_COMMIT = 'a4a4f9272ad64b1564035874b605ceb687b63ed8'
SOURCE = Path(__file__).resolve().parent / 'examples' / 'maniskill_pick_cube' / 'ppo_upstream.py'
POLICY_ARCHITECTURE = 'frozen_movement_independent_strength_v1'


def _upstream():
    name = 'weighted_pick_cube_upstream'
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
            raise ValueError('Grip-aware policy requires 45 measurements and five actions')
        super().__init__(envs)
        self.strength_mean = deepcopy(self.actor_mean)
        # Keep the original five-row movement network intact for exact copying;
        # its fifth row is retained for provenance but never used for movement.
        self.strength_logstd = nn.Parameter(self.actor_logstd[:, 4:5].detach().clone())
        self.actor_mean.requires_grad_(False)
        self.actor_logstd.requires_grad_(False)

    def action_mean(self, x):
        with torch.no_grad():
            movement = self.actor_mean(x)[:, :4]
        return torch.cat((movement, self.strength_mean(x)[:, 4:5]), dim=-1)

    def get_action(self, x, deterministic=False):
        mean = self.action_mean(x)
        if deterministic:
            return mean
        strength = Normal(mean[:, 4:5], self.strength_logstd.exp()).sample()
        return torch.cat((mean[:, :4], strength), dim=-1)

    def get_action_and_value(self, x, action=None):
        mean = self.action_mean(x)
        distribution = Normal(mean[:, 4:5], self.strength_logstd.exp())
        if action is None:
            action = torch.cat((mean[:, :4], distribution.sample()), dim=-1)
        return action, distribution.log_prob(action[:, 4:5]).sum(1), distribution.entropy().sum(1), self.critic(x)


def initialize_from_pretrained(agent, checkpoint, initial_strength_action=1.):
    """Copy old 42/4, 43/4 or 45/5 weights; resume branched checkpoints exactly.

    Original checkpoints are never edited. Copy all old actor/critic weights.
    Duplicate the actor into the strength branch; initialize only previously
    missing force columns/output. A copied movement network stays frozen.
    """
    source = torch.load(checkpoint, map_location='cpu', weights_only=True)
    current = agent.state_dict()
    if 'strength_mean.0.weight' in source:
        if set(source) != set(current):
            raise ValueError('Unsupported branched checkpoint architecture')
        agent.load_state_dict(source)
        return agent
    legacy = {k: v for k, v in current.items() if not k.startswith('strength_')}
    if set(source) != set(legacy):
        raise ValueError('Unsupported actor/critic checkpoint')
    inputs = source['actor_mean.0.weight'].shape[1]
    actions = source['actor_mean.6.weight'].shape[0]
    if (inputs, actions) not in ((42, 4), (43, 4), (45, 5)):
        raise ValueError('Expected a published 42/4, weighted 43/4, or grip-aware 45/5 policy')
    for name, target in legacy.items():
        old = source[name]
        if name in ('actor_mean.0.weight', 'critic.0.weight'):
            if old.shape != (256, inputs):
                raise ValueError('First-layer architecture mismatch')
            target.zero_(); target[:, :inputs].copy_(old)
        elif name == 'actor_mean.6.weight':
            if old.shape != (actions, 256):
                raise ValueError('Actor-output architecture mismatch')
            target.zero_(); target[:actions].copy_(old)
        elif name == 'actor_mean.6.bias':
            target.zero_(); target[:actions].copy_(old)
            if actions == 4:
                target[4] = initial_strength_action
        elif name == 'actor_logstd':
            target.fill_(-1.); target[:, :actions].copy_(old)
        else:
            if old.shape != target.shape:
                raise ValueError('Checkpoint architecture mismatch: ' + name)
            target.copy_(old)
    for name in agent.strength_mean.state_dict():
        current['strength_mean.' + name].copy_(legacy['actor_mean.' + name])
    current['strength_logstd'].copy_(legacy['actor_logstd'][:, 4:5])
    agent.load_state_dict(current)
    return agent

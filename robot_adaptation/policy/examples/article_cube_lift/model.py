"""Independently implemented article architecture with ManiSkill PPO's API.

Actor: 1024 -> 512 -> 256 -> 128 -> 64 -> 32 -> four actions.
Critic: 128 -> 64 -> 32 -> one value. Hidden activations are LeakyReLU.
As in the article, exploration variance stays fixed at 0.5 per action.
"""
import math
import numpy as np
import torch
from torch import nn
from torch.distributions import Normal


def network(input_size, widths, output_size):
    layers = []
    for width in widths:
        layers.extend([nn.Linear(input_size, width), nn.LeakyReLU()])
        input_size = width
    layers.append(nn.Linear(input_size, output_size))
    return nn.Sequential(*layers)


class Agent(nn.Module):
    def __init__(self, envs):
        super().__init__()
        inputs = int(np.prod(envs.single_observation_space.shape))
        actions = int(np.prod(envs.single_action_space.shape))
        if (inputs, actions) != (38, 4):
            raise ValueError("Article cube lift requires 38 observations and 4 actions")
        self.actor_mean = network(inputs, [1024, 512, 256, 128, 64, 32], actions)
        self.critic = network(inputs, [128, 64, 32], 1)
        self.register_buffer("action_std", torch.full((1, actions), math.sqrt(0.5)))
        # Our addition: keep units manageable, particularly raw contact forces.
        scales = [0.3] * 3 + [1.] * 9 + [1.] * 3 + [0.04] * 3
        scales += [0.3] * 3 + [1.] * 9 + [0.08] + [10.] * 6 + [1.]
        self.register_buffer("input_scale", torch.tensor(scales))

    def get_value(self, inputs):
        return self.critic(inputs / self.input_scale)

    def get_action(self, inputs, deterministic=False):
        mean = self.actor_mean(inputs / self.input_scale)
        return mean if deterministic else Normal(mean, self.action_std).sample()

    def get_action_and_value(self, inputs, action=None):
        distribution = Normal(self.actor_mean(inputs / self.input_scale), self.action_std)
        if action is None:
            action = distribution.sample()
        return action, distribution.log_prob(action).sum(-1), distribution.entropy().sum(-1), self.get_value(inputs)

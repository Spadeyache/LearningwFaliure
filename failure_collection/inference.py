"""Inference-only architecture pinned to the retained 600-episode dataset.

45 observations, four movement/opening outputs and an independent strength
output. Strict checkpoint loading restores every parameter; no training here.
Network layout follows ManiSkill PPO (see MANISKILL_LICENSE).
"""
import torch
from torch import nn

POLICY_ARCHITECTURE = 'frozen_movement_independent_strength_v1'


def network(outputs):
    return nn.Sequential(nn.Linear(45, 256), nn.Tanh(),
                         nn.Linear(256, 256), nn.Tanh(),
                         nn.Linear(256, 256), nn.Tanh(), nn.Linear(256, outputs))


class Agent(nn.Module):
    def __init__(self):
        super().__init__()
        self.critic = network(1)
        self.actor_mean = network(5)
        self.actor_logstd = nn.Parameter(torch.zeros(1, 5))
        self.strength_mean = network(5)
        self.strength_logstd = nn.Parameter(torch.zeros(1, 1))

    def get_action(self, observation, deterministic=True):
        if not deterministic:
            raise ValueError('Collection uses deterministic frozen-policy inference')
        return torch.cat((self.actor_mean(observation)[:, :4],
                          self.strength_mean(observation)[:, 4:5]), dim=-1)

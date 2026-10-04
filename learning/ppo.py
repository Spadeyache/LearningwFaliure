"""Small CPU adaptation of ManiSkill's official numerical-observation PPO.

Source: examples/baselines/ppo/ppo.py, ManiSkill v3.0.1,
commit a4a4f9272ad64b1564035874b605ceb687b63ed8 (Apache-2.0).
https://github.com/mani-skill/ManiSkill/blob/a4a4f9272ad64b1564035874b605ceb687b63ed8/examples/baselines/ppo/ppo.py
See MANISKILL_LICENSE. Original authors: ManiSkill contributors.

Adaptations: 2x64 MLPs; fixed input scaling; tanh-bounded Gaussian actions;
explicit terminal/truncation GAE for one CPU environment; no CLI or GPU wrappers.
Orthogonal initialization, actor/critic separation and clipped PPO/Adam update
follow the reference. Defaults live in train_ppo.py and are provisional.
"""

import math

import torch
from torch import nn
from torch.distributions import Normal
from torch.nn import functional as F


SOURCE_COMMIT = "a4a4f9272ad64b1564035874b605ceb687b63ed8"
# Divide raw inputs by these fixed scales. No running statistics or images.
# Each pose: xyz metres / 0.3, quaternion / 1; weight / 1 N; forces / 10 N.
INPUT_SCALE = [0.3] * 3 + [1.0] * 4 + [0.3] * 3 + [1.0] * 4 + [1.0] + [10.0] * 6


def layer_init(layer, std=math.sqrt(2), bias_const=0.0):
    nn.init.orthogonal_(layer.weight, std)
    nn.init.constant_(layer.bias, bias_const)
    return layer


class Agent(nn.Module):
    """Actor chooses actions; critic estimates future discounted reward."""

    def __init__(self, hidden_size=64):
        super().__init__()
        self.register_buffer("input_scale", torch.tensor(INPUT_SCALE))
        self.critic = nn.Sequential(
            layer_init(nn.Linear(21, hidden_size)), nn.Tanh(),
            layer_init(nn.Linear(hidden_size, hidden_size)), nn.Tanh(),
            layer_init(nn.Linear(hidden_size, 1)),
        )
        self.actor_mean = nn.Sequential(
            layer_init(nn.Linear(21, hidden_size)), nn.Tanh(),
            layer_init(nn.Linear(hidden_size, hidden_size)), nn.Tanh(),
            layer_init(nn.Linear(hidden_size, 7), std=0.01 * math.sqrt(2)),
        )
        self.actor_logstd = nn.Parameter(torch.full((1, 7), -0.5))

    def get_value(self, inputs):
        return self.critic(inputs / self.input_scale).squeeze(-1)

    def distribution(self, inputs):
        mean = self.actor_mean(inputs / self.input_scale)
        std = self.actor_logstd.clamp(-5, 1).exp().expand_as(mean)
        return Normal(mean, std)

    def get_action(self, inputs, deterministic=False):
        distribution = self.distribution(inputs)
        latent = distribution.mean if deterministic else distribution.sample()
        return latent.tanh()

    def get_action_and_value(self, inputs, latent=None):
        distribution = self.distribution(inputs)
        if latent is None:
            latent = distribution.sample()
        action = latent.tanh()
        # Stable log(1 - tanh(z)^2). Store z to avoid inverse-tanh rounding.
        # PPO likelihoods refer to bounded policy actions, not clipped Gaussians.
        log_jacobian = 2 * (math.log(2) - latent - F.softplus(-2 * latent))
        logprob = (distribution.log_prob(latent) - log_jacobian).sum(-1)
        return action, latent, logprob, self.get_value(inputs)


def generalized_advantages(rewards, values, next_values, terminated, truncated, gamma, gae_lambda):
    """Bootstrap at time limits from the FINAL state, never from a reset state.

    True success termination has no bootstrap. Both boundaries stop the GAE
    trace so later episodes cannot leak into this episode's advantage.
    """
    advantages = torch.zeros_like(rewards)
    last = torch.zeros(())
    for t in reversed(range(len(rewards))):
        bootstrap = (~terminated[t]).float()
        continuation = (~(terminated[t] | truncated[t])).float()
        delta = rewards[t] + gamma * bootstrap * next_values[t] - values[t]
        last = delta + gamma * gae_lambda * continuation * last
        advantages[t] = last
    return advantages, advantages + values


def update_ppo(agent, optimizer, batch, settings):
    """Reference clipped policy objective + value regression and Adam."""
    advantages = batch["advantages"]
    advantages = (advantages - advantages.mean()) / (advantages.std(unbiased=False) + 1e-8)
    before = torch.nn.utils.parameters_to_vector(agent.parameters()).detach().clone()
    losses = []
    stop = False
    for _ in range(settings["update_epochs"]):
        indices = torch.randperm(len(advantages))
        for start in range(0, len(indices), settings["minibatch_size"]):
            chosen = indices[start:start + settings["minibatch_size"]]
            _, _, logprob, value = agent.get_action_and_value(batch["inputs"][chosen], batch["latents"][chosen])
            logratio = logprob - batch["logprobs"][chosen]
            ratio = logratio.exp()
            approx_kl = ((ratio - 1) - logratio).mean()
            if not torch.isfinite(approx_kl):
                raise FloatingPointError("Nonfinite PPO likelihood ratio")
            if approx_kl.item() > settings["target_kl"]:
                stop = True
                break
            pg_loss1 = -advantages[chosen] * ratio
            pg_loss2 = -advantages[chosen] * ratio.clamp(1 - settings["clip_coef"], 1 + settings["clip_coef"])
            policy_loss = torch.maximum(pg_loss1, pg_loss2).mean()
            value_loss = 0.5 * (value - batch["returns"][chosen]).square().mean()
            # Reference default entropy coefficient is 0; exploration is from
            # the learned Gaussian std. No incorrect unsquashed entropy bonus.
            loss = policy_loss + settings["vf_coef"] * value_loss
            if not torch.isfinite(loss):
                raise FloatingPointError("Nonfinite PPO loss")
            optimizer.zero_grad()
            loss.backward()
            nn.utils.clip_grad_norm_(agent.parameters(), settings["max_grad_norm"], error_if_nonfinite=True)
            optimizer.step()
            losses.append([policy_loss.item(), value_loss.item(), approx_kl.item()])
        if stop:
            break
    after = torch.nn.utils.parameters_to_vector(agent.parameters()).detach()
    if not torch.isfinite(after).all() or not losses:
        raise FloatingPointError("PPO update failed or made no optimizer steps")
    mean = torch.tensor(losses).mean(0).tolist()
    return dict(policy_loss=mean[0], value_loss=mean[1], approx_kl=mean[2],
                optimizer_steps=len(losses), parameter_change_l2=float((after - before).norm()))

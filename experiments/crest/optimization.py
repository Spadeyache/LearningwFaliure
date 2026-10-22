"""Bounded Gaussian REPS search for a SINGLE task context.

Implements the REPS dual and reward-weighted Gaussian fitting. Normalized box
clipping and covariance regularization are practical adaptations for the lifting
controller, not an exact reproduction of the authors' optimizer settings.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import numpy as np
from scipy.optimize import minimize_scalar
from scipy.special import logsumexp

from .spaces import ParameterSpace


@dataclass
class Solution:
    theta: np.ndarray
    result: object
    evaluations: int


def reps_weights(rewards, epsilon: float):
    rewards = np.asarray(rewards, dtype=float)
    if rewards.ndim != 1 or not len(rewards) or not np.isfinite(rewards).all() or epsilon <= 0:
        raise ValueError("REPS needs finite rewards and positive KL bound")
    # Rescaling rewards leaves the optimum normalized weights unchanged.
    centered = (rewards - rewards.max()) / max(float(np.ptp(rewards)), 1e-12)
    if np.ptp(rewards) < 1e-12:
        return np.full(len(rewards), 1 / len(rewards))

    def dual(log_eta):
        eta = np.exp(log_eta)
        return eta * (epsilon + logsumexp(centered / eta) - np.log(len(centered)))

    fit = minimize_scalar(dual, bounds=(-20., 20.), method="bounded")
    logits = centered / np.exp(fit.x)
    return np.exp(logits - logsumexp(logits))


class REPSOptimizer:
    def __init__(self, space: ParameterSpace, *, iterations=6, population=12,
                 epsilon=.5, initial_std=.12, min_std=.01):
        if (type(iterations) is not int or iterations < 1 or type(population) is not int
                or population < 2 or not 0 < min_std <= initial_std <= 1
                or not np.isfinite([epsilon, initial_std, min_std]).all() or epsilon <= 0):
            raise ValueError("Invalid REPS settings")
        self.space = space
        self.iterations, self.population = iterations, population
        self.epsilon, self.initial_std, self.min_std = epsilon, initial_std, min_std

    def solve(self, evaluate: Callable, initial, rng) -> Solution:
        """Warm-start, stop at a successful solution, retain best failed attempt."""
        mean = self.space.normalize(initial)
        covariance = np.eye(len(mean)) * self.initial_std ** 2
        best_theta = self.space.validate(initial).copy()
        best = evaluate(best_theta)
        count = 1
        if best.success:
            return Solution(best_theta, best, count)
        for _ in range(self.iterations):
            draws = np.clip(rng.multivariate_normal(mean, covariance, self.population), 0, 1)
            rewards = []
            for draw in draws:
                theta = self.space.denormalize(draw)
                result = evaluate(theta)
                count += 1
                rewards.append(result.score)
                if result.success or result.score > best.score:
                    best_theta, best = theta.copy(), result
                if result.success:
                    return Solution(best_theta, best, count)
            weights = reps_weights(rewards, self.epsilon)
            mean = weights @ draws
            residuals = draws - mean
            covariance = (residuals * weights[:, None]).T @ residuals
            covariance += np.eye(len(mean)) * self.min_std ** 2
        return Solution(best_theta, best, count)

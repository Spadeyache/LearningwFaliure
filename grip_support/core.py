"""LEARNER IMPLEMENTATION REQUIRED.

Do not reuse the built-in PickCube observation/reward as your task by accident.
Choose dynamics, observation/action spaces, rewards, termination and PPO settings.
Training uses true weight; deployment uses your estimator's weight. Define units,
frames, normalization and how estimator state persists/reset per object yourself.
"""


def missing(config, mode):
    """Remove items only when their implementation and checks exist."""
    return [
        "Custom gripping/lifting environment: dynamics, spaces, reward and termination",
        "Observation/action validation, including true versus estimated weight",
        "PPO framework choice, implementation/adapter and hyperparameters",
        "Weight estimator and object-specific persistence/reset rules",
        "Training/resume state restoration and small-run validation",
        "Evaluation protocol and performance metrics",
    ]


def run(mode, config, context, checkpoint):
    """Implement after missing() reports readiness for the requested mode.

mode: train/resume/evaluate. context: RunContext with directory, log(), save().
checkpoint: None or a loaded checkpoint payload. Use context.load() if needed.
Implement actual rollout/training/evaluation here; the support CLI creates no policy.
"""
    raise NotImplementedError("Implement the learner-owned core before running")

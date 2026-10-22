"""CREST Reduced/Partitioned upper-policy networks; output normalized theta.

These are untrained architectures, not added inputs to an existing PPO
checkpoint. Pass ContextSpace.encode vectors and denormalize the output with
ParameterSpace. No unknown feature is silently removed by the report masks.
"""
import torch
from torch import nn


def _network(inputs, outputs, hidden):
    layers = []
    for width in hidden:
        layers.extend([nn.Linear(inputs, width), nn.Tanh()])
        inputs = width
    return nn.Sequential(*layers, nn.Linear(inputs, outputs), nn.Sigmoid())


class _Selection(nn.Module):
    def __init__(self, indices, outputs, hidden):
        super().__init__()
        self.register_buffer("indices", torch.as_tensor(indices, dtype=torch.long))
        # An empty context learns a constant from a dummy input, avoiding a
        # zero-width Linear and making context-independent parameters explicit.
        self.network = _network(max(1, len(indices)), outputs, hidden)

    def forward(self, context):
        selected = (context.index_select(-1, self.indices) if self.indices.numel()
                    else context.new_ones((*context.shape[:-1], 1)))
        return self.network(selected)


class FullMLP(_Selection):
    """Comparison baseline consuming every encoded environmental factor."""
    def __init__(self, contexts, parameters, hidden=(64, 64)):
        super().__init__(list(range(len(contexts.feature_names))), len(parameters.names), hidden)


class ReducedMLP(_Selection):
    def __init__(self, report, hidden=(64, 64)):
        if not report["solved_anchors"]:
            raise ValueError("Cannot construct a selected policy from zero solved anchors")
        super().__init__(report["reduced_feature_indices"], len(report["parameter_names"]), hidden)


class PartitionedMLP(nn.Module):
    def __init__(self, report, hidden=(32, 32)):
        super().__init__()
        if not report["solved_anchors"]:
            raise ValueError("Cannot construct a selected policy from zero solved anchors")
        self.heads = nn.ModuleList([_Selection(report["partitioned_feature_indices"][name], 1, hidden)
                                    for name in report["parameter_names"]])

    def forward(self, context):
        return torch.cat([head(context) for head in self.heads], dim=-1)

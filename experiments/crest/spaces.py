"""Named, bounded contexts and controller parameters; no simulator imports."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np


@dataclass(frozen=True)
class Factor:
    name: str
    kind: str
    nominal: Any
    low: float | None = None
    high: float | None = None
    choices: tuple = ()
    unit: str = ""
    enabled: bool = True

    @classmethod
    def from_spec(cls, name: str, spec: dict) -> "Factor":
        if type(spec.get("enabled", True)) is not bool:
            raise ValueError(f"{name}: enabled must be a boolean")
        factor = cls(name, spec["type"], spec["nominal"], spec.get("min"),
                     spec.get("max"), tuple(spec.get("values", ())),
                     spec.get("unit", ""), spec.get("enabled", True))
        if factor.kind == "numeric":
            if (not np.isfinite([factor.low, factor.nominal, factor.high]).all()
                    or not factor.low < factor.high
                    or not factor.low <= factor.nominal <= factor.high):
                raise ValueError(f"{name}: invalid numeric bounds")
        elif factor.kind == "categorical":
            if (len(factor.choices) < 2 or len(set(factor.choices)) != len(factor.choices)
                    or factor.nominal not in factor.choices):
                raise ValueError(f"{name}: need distinct categories including nominal")
        else:
            raise ValueError(f"{name}: unsupported factor type")
        return factor

    def validate(self, value):
        if self.kind == "categorical":
            valid = value in self.choices
        else:
            valid = np.isfinite(value) and self.low <= value <= self.high
        if not valid:
            raise ValueError(f"{self.name}: out-of-domain value {value!r}")

    def sample(self, rng):
        if self.kind == "categorical":
            return self.choices[int(rng.integers(len(self.choices)))]
        return float(rng.uniform(self.low, self.high))


class ContextSpace:
    def __init__(self, factors: list[Factor]):
        self.factors = tuple(factors)
        self.names = tuple(f.name for f in factors)
        if not factors or len(set(self.names)) != len(self.names):
            raise ValueError("Context factors must be nonempty and uniquely named")
        self.feature_names = tuple(name for f in factors for name in
                                   ([f.name] if f.kind == "numeric" else
                                    [f"{f.name}={value}" for value in f.choices]))

    @property
    def nominal(self):
        return {f.name: f.nominal for f in self.factors}

    def sample(self, rng):
        return {f.name: f.sample(rng) if f.enabled else f.nominal for f in self.factors}

    def validate(self, values):
        if set(values) != set(self.names):
            raise ValueError("Context keys must match the declared factors exactly")
        for f in self.factors:
            f.validate(values[f.name])

    def encode(self, values):
        """Normalize numeric values; one-hot encode shape rather than rank it."""
        self.validate(values)
        features = []
        for f in self.factors:
            value = values[f.name]
            features.extend([(value - f.low) / (f.high - f.low)] if f.kind == "numeric"
                            else [float(value == item) for item in f.choices])
        return np.asarray(features, dtype=np.float64)

    def feature_indices(self, selected):
        unknown = set(selected) - set(self.names)
        if unknown:
            raise ValueError(f"Unknown context factors: {sorted(unknown)}")
        indices, start = [], 0
        for f in self.factors:
            width = 1 if f.kind == "numeric" else len(f.choices)
            if f.name in selected:
                indices.extend(range(start, start + width))
            start += width
        return indices

    def interventions(self, context, random_count, rng):
        """Endpoints/categories plus uniform draws, changing ONE semantic factor."""
        self.validate(context)
        for f in self.factors:
            if not f.enabled:
                continue
            candidates = (list(f.choices) if f.kind == "categorical" else
                          [f.low, f.high] + [f.sample(rng) for _ in range(random_count)])
            seen = {context[f.name]}
            for value in candidates:
                if value in seen:
                    continue
                seen.add(value)
                modified = dict(context)
                modified[f.name] = value
                yield f.name, modified


class ParameterSpace:
    def __init__(self, specs: dict):
        self.names = tuple(specs)
        if not self.names:
            raise ValueError("Need at least one controller parameter")
        self.low = np.asarray([specs[n]["min"] for n in self.names], dtype=float)
        self.high = np.asarray([specs[n]["max"] for n in self.names], dtype=float)
        if not np.isfinite([self.low, self.high]).all() or np.any(self.low >= self.high):
            raise ValueError("Controller bounds must be finite and ordered")

    def normalize(self, theta):
        theta = self.validate(theta)
        return (theta - self.low) / (self.high - self.low)

    def denormalize(self, values):
        return self.low + np.asarray(values) * (self.high - self.low)

    def validate(self, theta):
        theta = np.asarray(theta, dtype=float)
        if (theta.shape != self.low.shape or not np.isfinite(theta).all()
                or np.any(theta < self.low) or np.any(theta > self.high)):
            raise ValueError("Controller vector must be finite, bounded and correctly sized")
        return theta

    def as_dict(self, theta):
        return dict(zip(self.names, self.validate(theta).tolist()))

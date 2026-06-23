"""Bounded-coupling and equivalence decision helpers."""

from __future__ import annotations

from dataclasses import dataclass
from math import sqrt
from statistics import mean


@dataclass(frozen=True)
class EquivalenceDecision:
    """Equivalence decision from a declared margin."""

    estimate: float
    ci_low: float
    ci_high: float
    margin: float
    interval_inside_margin: bool
    rope_mass: float | None = None
    rope_threshold: float = 0.95

    @property
    def passes(self) -> bool:
        rope_ok = True if self.rope_mass is None else self.rope_mass >= self.rope_threshold
        return self.interval_inside_margin and rope_ok


def equivalence_from_interval(
    estimate: float,
    ci_low: float,
    ci_high: float,
    margin: float,
    *,
    rope_mass: float | None = None,
    rope_threshold: float = 0.95,
) -> EquivalenceDecision:
    """Classify whether an interval lies fully inside +/- margin."""

    if margin <= 0:
        raise ValueError("margin must be positive")
    return EquivalenceDecision(
        estimate=estimate,
        ci_low=ci_low,
        ci_high=ci_high,
        margin=margin,
        interval_inside_margin=(-margin <= ci_low and ci_high <= margin),
        rope_mass=rope_mass,
        rope_threshold=rope_threshold,
    )


def rope_mass(samples: list[float], margin: float) -> float:
    """Return posterior mass inside +/- margin from supplied samples."""

    if not samples:
        raise ValueError("samples cannot be empty")
    if margin <= 0:
        raise ValueError("margin must be positive")
    return sum(-margin <= value <= margin for value in samples) / len(samples)


def pearson_correlation(x: list[float], y: list[float]) -> float:
    """Return Pearson correlation without external dependencies."""

    if len(x) != len(y) or len(x) < 2:
        raise ValueError("x and y must have the same length of at least 2")
    mx = mean(x)
    my = mean(y)
    numerator = sum((a - mx) * (b - my) for a, b in zip(x, y))
    denom_x = sqrt(sum((a - mx) ** 2 for a in x))
    denom_y = sqrt(sum((b - my) ** 2 for b in y))
    if denom_x == 0 or denom_y == 0:
        raise ValueError("correlation is undefined for constant input")
    return numerator / (denom_x * denom_y)


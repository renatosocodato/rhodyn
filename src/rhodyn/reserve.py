"""Reserve-style normalization helpers."""

from __future__ import annotations

from statistics import mean


def ff_over_f0(values: list[float], baseline_points: int = 3) -> list[float]:
    """Return F/F0 values from a signal series."""

    if not values:
        return []
    if baseline_points <= 0:
        raise ValueError("baseline_points must be positive")
    baseline = mean(values[: min(len(values), baseline_points)])
    if baseline == 0:
        raise ValueError("baseline mean is zero")
    return [value / baseline for value in values]


def reserve_coordinate(values: list[float], *, floor: float, ceiling: float) -> float:
    """Map a reserve-like response to a bounded 0-1 coordinate.

    Larger values indicate greater remaining reserve.
    """

    if not values:
        raise ValueError("reserve_coordinate requires at least one value")
    if ceiling <= floor:
        raise ValueError("ceiling must exceed floor")
    response = max(values)
    scaled = 1.0 - ((response - floor) / (ceiling - floor))
    return max(0.0, min(1.0, scaled))


"""Bootstrap and permutation uncertainty helpers."""

from __future__ import annotations

import random
from collections import defaultdict
from dataclasses import dataclass
from statistics import mean
from typing import Callable

from rhodyn.results import GroupMetadata, ResultProvenance, UncertaintyInterval


Statistic = Callable[[list[float]], float]
ContrastStatistic = Callable[[list[float], list[float]], float]


@dataclass(frozen=True)
class BootstrapResult:
    """Bootstrap interval and resampled statistic distribution."""

    interval: UncertaintyInterval
    distribution: tuple[float, ...]
    resample_level: str
    diagnostics: dict[str, object]


@dataclass(frozen=True)
class PermutationResult:
    """Permutation-test result with the null distribution."""

    observed: float
    p_value: float
    null_distribution: tuple[float, ...]
    alternative: str
    exchangeability_level: str
    n_units_a: int
    n_units_b: int
    diagnostics: dict[str, object]


def mean_difference(a: list[float], b: list[float]) -> float:
    """Return ``mean(a) - mean(b)``."""

    if not a or not b:
        raise ValueError("mean_difference requires non-empty groups")
    return mean(a) - mean(b)


def _as_floats(values: list[float]) -> list[float]:
    if not values:
        raise ValueError("values cannot be empty")
    return [float(value) for value in values]


def _percentile(values: list[float], fraction: float) -> float:
    if not 0 <= fraction <= 1:
        raise ValueError("fraction must be between 0 and 1")
    ordered = sorted(values)
    if len(ordered) == 1:
        return ordered[0]
    position = fraction * (len(ordered) - 1)
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)
    weight = position - lower
    return ordered[lower] * (1 - weight) + ordered[upper] * weight


def _group_values(values: list[float], group_labels: list[str]) -> dict[str, list[float]]:
    if len(values) != len(group_labels):
        raise ValueError("group_labels must match values length")
    grouped: dict[str, list[float]] = defaultdict(list)
    for value, label in zip(values, group_labels):
        if not str(label):
            raise ValueError("group labels cannot be empty")
        grouped[str(label)].append(value)
    return dict(grouped)


def _unit_values(values: list[float], group_labels: list[str] | None) -> tuple[list[float], str]:
    if group_labels is None:
        return values, "observation"
    grouped = _group_values(values, group_labels)
    return [mean(group) for group in grouped.values()], "group"


def bootstrap_interval(
    values: list[float],
    *,
    statistic: Statistic = mean,
    n_resamples: int = 1000,
    confidence_level: float = 0.95,
    seed: int | None = None,
    group_labels: list[str] | None = None,
    group: GroupMetadata | None = None,
    schema_kind: str = "derived",
    parameters: dict[str, object] | None = None,
) -> BootstrapResult:
    """Estimate a percentile bootstrap interval.

    If ``group_labels`` are supplied, groups are resampled as units and then all
    observations belonging to selected groups are carried into each resample.
    """

    sample = _as_floats(values)
    if n_resamples <= 0:
        raise ValueError("n_resamples must be positive")
    if not 0 < confidence_level < 1:
        raise ValueError("confidence_level must be between 0 and 1")
    rng = random.Random(seed)

    distribution: list[float] = []
    if group_labels is None:
        for _ in range(n_resamples):
            resample = [sample[rng.randrange(len(sample))] for _ in sample]
            distribution.append(float(statistic(resample)))
        resample_level = "observation"
        unit_count = len(sample)
    else:
        grouped = _group_values(sample, group_labels)
        labels = list(grouped)
        for _ in range(n_resamples):
            resample: list[float] = []
            for _ in labels:
                resample.extend(grouped[rng.choice(labels)])
            distribution.append(float(statistic(resample)))
        resample_level = "group"
        unit_count = len(labels)

    alpha = 1 - confidence_level
    estimate = float(statistic(sample))
    interval = UncertaintyInterval(
        method="percentile_bootstrap",
        estimate=estimate,
        lower=_percentile(distribution, alpha / 2),
        upper=_percentile(distribution, 1 - alpha / 2),
        confidence_level=confidence_level,
        n=len(sample),
        group=group or GroupMetadata(),
        provenance=ResultProvenance(
            schema_kind=schema_kind,
            parameters={"n_resamples": n_resamples, "seed": seed, **(parameters or {})},
        ),
    )
    return BootstrapResult(
        interval=interval,
        distribution=tuple(distribution),
        resample_level=resample_level,
        diagnostics={"unit_count": unit_count, "statistic": getattr(statistic, "__name__", "callable")},
    )


def permutation_test(
    a: list[float],
    b: list[float],
    *,
    statistic: ContrastStatistic = mean_difference,
    n_resamples: int = 1000,
    seed: int | None = None,
    alternative: str = "two-sided",
    group_labels_a: list[str] | None = None,
    group_labels_b: list[str] | None = None,
) -> PermutationResult:
    """Run a permutation test for a declared exchangeability structure."""

    sample_a = _as_floats(a)
    sample_b = _as_floats(b)
    if n_resamples <= 0:
        raise ValueError("n_resamples must be positive")
    if alternative not in {"two-sided", "greater", "less"}:
        raise ValueError("alternative must be two-sided, greater, or less")
    units_a, level_a = _unit_values(sample_a, group_labels_a)
    units_b, level_b = _unit_values(sample_b, group_labels_b)
    if level_a != level_b:
        raise ValueError("both groups must use the same exchangeability level")
    if len(units_a) < 2 or len(units_b) < 2:
        raise ValueError("permutation_test requires at least two exchangeable units per group")

    observed = float(statistic(units_a, units_b))
    pooled = units_a + units_b
    n_a = len(units_a)
    rng = random.Random(seed)
    null_distribution: list[float] = []
    for _ in range(n_resamples):
        shuffled = pooled[:]
        rng.shuffle(shuffled)
        null_distribution.append(float(statistic(shuffled[:n_a], shuffled[n_a:])))

    if alternative == "greater":
        extreme = sum(value >= observed for value in null_distribution)
    elif alternative == "less":
        extreme = sum(value <= observed for value in null_distribution)
    else:
        extreme = sum(abs(value) >= abs(observed) for value in null_distribution)
    p_value = (extreme + 1) / (n_resamples + 1)
    return PermutationResult(
        observed=observed,
        p_value=p_value,
        null_distribution=tuple(null_distribution),
        alternative=alternative,
        exchangeability_level=level_a,
        n_units_a=len(units_a),
        n_units_b=len(units_b),
        diagnostics={"n_resamples": n_resamples, "seed": seed, "statistic": getattr(statistic, "__name__", "callable")},
    )

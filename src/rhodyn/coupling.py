"""Bounded-coupling and equivalence decision helpers."""

from __future__ import annotations

from dataclasses import dataclass
from math import sqrt
from statistics import NormalDist, mean, variance


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


@dataclass(frozen=True)
class TostDecision:
    """Two-one-sided-tests decision from raw-array summaries."""

    estimate: float
    se: float
    df: float
    ci_low: float
    ci_high: float
    margin: float
    p_lower: float
    p_upper: float
    p_tost: float
    interval_inside_margin: bool
    alpha: float
    method: str
    n: int
    n_a: int | None = None
    n_b: int | None = None
    rope_mass: float | None = None
    rope_threshold: float = 0.95

    @property
    def passes(self) -> bool:
        rope_ok = True if self.rope_mass is None else self.rope_mass >= self.rope_threshold
        return self.interval_inside_margin and self.p_tost < self.alpha and rope_ok


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


def _validate_sample(values: list[float], label: str) -> list[float]:
    if len(values) < 2:
        raise ValueError(f"{label} requires at least two values")
    return [float(value) for value in values]


def _t_distribution_helpers(df: float, prefer_scipy: bool) -> tuple[object, str]:
    if prefer_scipy:
        try:
            from scipy import stats  # type: ignore

            return stats.t(df=df), "scipy_t"
        except Exception:
            pass
    return NormalDist(), "normal_approximation"


def _cdf(dist: object, value: float) -> float:
    return float(dist.cdf(value))  # type: ignore[attr-defined]


def _ppf(dist: object, value: float) -> float:
    if hasattr(dist, "ppf"):
        return float(dist.ppf(value))  # type: ignore[attr-defined]
    return float(dist.inv_cdf(value))  # type: ignore[attr-defined]


def _welch_df(var_a: float, n_a: int, var_b: float, n_b: int) -> float:
    term_a = var_a / n_a
    term_b = var_b / n_b
    numerator = (term_a + term_b) ** 2
    denominator = (term_a**2 / (n_a - 1)) + (term_b**2 / (n_b - 1))
    if denominator <= 0:
        raise ValueError("Welch degrees of freedom are undefined for zero variance inputs")
    return numerator / denominator


def _tost_from_summary(
    estimate: float,
    se: float,
    df: float,
    margin: float,
    *,
    alpha: float,
    n: int,
    n_a: int | None = None,
    n_b: int | None = None,
    rope_mass_value: float | None = None,
    rope_threshold: float = 0.95,
    prefer_scipy: bool = True,
) -> TostDecision:
    if margin <= 0:
        raise ValueError("margin must be positive")
    if se <= 0:
        raise ValueError("standard error must be positive")
    if not 0 < alpha < 0.5:
        raise ValueError("alpha must be between 0 and 0.5")

    dist, method = _t_distribution_helpers(df, prefer_scipy)
    critical = _ppf(dist, 1 - alpha)
    ci_low = estimate - critical * se
    ci_high = estimate + critical * se
    t_lower = (estimate + margin) / se
    t_upper = (estimate - margin) / se
    p_lower = 1 - _cdf(dist, t_lower)
    p_upper = _cdf(dist, t_upper)
    return TostDecision(
        estimate=estimate,
        se=se,
        df=df,
        ci_low=ci_low,
        ci_high=ci_high,
        margin=margin,
        p_lower=p_lower,
        p_upper=p_upper,
        p_tost=max(p_lower, p_upper),
        interval_inside_margin=(-margin <= ci_low and ci_high <= margin),
        alpha=alpha,
        method=method,
        n=n,
        n_a=n_a,
        n_b=n_b,
        rope_mass=rope_mass_value,
        rope_threshold=rope_threshold,
    )


def one_sample_tost(
    values: list[float],
    margin: float,
    *,
    target: float = 0.0,
    alpha: float = 0.05,
    rope_samples: list[float] | None = None,
    rope_threshold: float = 0.95,
    prefer_scipy: bool = True,
) -> TostDecision:
    """Run one-sample TOST against a declared target and margin.

    Passing this decision means the mean contrast is equivalent within the
    declared margin, not that the true biological effect is exactly zero.
    """

    sample = _validate_sample(values, "one_sample_tost")
    n = len(sample)
    estimate = mean(sample) - target
    sample_variance = variance(sample)
    se = sqrt(sample_variance / n)
    rope_mass_value = None if rope_samples is None else rope_mass(rope_samples, margin)
    return _tost_from_summary(
        estimate,
        se,
        n - 1,
        margin,
        alpha=alpha,
        n=n,
        rope_mass_value=rope_mass_value,
        rope_threshold=rope_threshold,
        prefer_scipy=prefer_scipy,
    )


def two_sample_welch_tost(
    a: list[float],
    b: list[float],
    margin: float,
    *,
    alpha: float = 0.05,
    rope_samples: list[float] | None = None,
    rope_threshold: float = 0.95,
    prefer_scipy: bool = True,
) -> TostDecision:
    """Run Welch TOST for the mean difference ``a - b``."""

    sample_a = _validate_sample(a, "two_sample_welch_tost group a")
    sample_b = _validate_sample(b, "two_sample_welch_tost group b")
    n_a = len(sample_a)
    n_b = len(sample_b)
    var_a = variance(sample_a)
    var_b = variance(sample_b)
    se = sqrt((var_a / n_a) + (var_b / n_b))
    df = _welch_df(var_a, n_a, var_b, n_b)
    rope_mass_value = None if rope_samples is None else rope_mass(rope_samples, margin)
    return _tost_from_summary(
        mean(sample_a) - mean(sample_b),
        se,
        df,
        margin,
        alpha=alpha,
        n=n_a + n_b,
        n_a=n_a,
        n_b=n_b,
        rope_mass_value=rope_mass_value,
        rope_threshold=rope_threshold,
        prefer_scipy=prefer_scipy,
    )


def rope_decision(samples: list[float], margin: float, *, threshold: float = 0.95) -> EquivalenceDecision:
    """Return a ROPE-only decision from posterior contrast samples."""

    sample = _validate_sample(samples, "rope_decision")
    mass = rope_mass(sample, margin)
    ordered = sorted(sample)
    n = len(ordered)
    lo = ordered[max(0, int(0.05 * (n - 1)))]
    hi = ordered[min(n - 1, int(0.95 * (n - 1)))]
    return equivalence_from_interval(mean(sample), lo, hi, margin, rope_mass=mass, rope_threshold=threshold)


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

"""Reduced-controller model comparison helpers."""

from __future__ import annotations

from dataclasses import dataclass
from math import log
from statistics import mean

from rhodyn.schema import EndpointRecord


@dataclass(frozen=True)
class ModelFit:
    """A compact endpoint-level fit summary."""

    model: str
    n: int
    rss: float
    rmse: float
    aic: float
    bic: float


def residual_sum_squares(rows: list[EndpointRecord]) -> float:
    """Weighted residual sum of squares."""

    return sum(row.weight * (row.observed - row.predicted) ** 2 for row in rows)


def fit_model_rows(rows: list[EndpointRecord], *, parameter_count: int = 1) -> ModelFit:
    """Summarize one model's endpoint compatibility."""

    if not rows:
        raise ValueError("fit_model_rows requires at least one row")
    model = rows[0].model
    rss = residual_sum_squares(rows)
    n = len(rows)
    safe_rss = max(rss, 1e-12)
    aic = n * log(safe_rss / n) + 2 * parameter_count
    bic = n * log(safe_rss / n) + parameter_count * log(n)
    squared = [(row.observed - row.predicted) ** 2 for row in rows]
    return ModelFit(model=model, n=n, rss=rss, rmse=mean(squared) ** 0.5, aic=aic, bic=bic)


def rank_model_fits(rows: list[EndpointRecord], *, parameter_count: int = 1) -> list[ModelFit]:
    """Rank models by BIC, then RSS."""

    grouped: dict[str, list[EndpointRecord]] = {}
    for row in rows:
        grouped.setdefault(row.model, []).append(row)
    fits = [fit_model_rows(model_rows, parameter_count=parameter_count) for model_rows in grouped.values()]
    return sorted(fits, key=lambda fit: (fit.bic, fit.rss))


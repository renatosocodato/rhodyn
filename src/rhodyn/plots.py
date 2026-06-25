"""Optional Matplotlib diagnostic plots."""

from __future__ import annotations

from typing import Any

from rhodyn.compare import ModelFit
from rhodyn.coupling import EquivalenceDecision, TostDecision
from rhodyn.extras import require_extra
from rhodyn.residence import ResidenceWindow
from rhodyn.results import SensitivityCurveResult
from rhodyn.schema import TrajectoryRecord


def _pyplot(feature: str) -> Any:
    require_extra("plots", feature=feature)
    import matplotlib.pyplot as plt  # type: ignore

    return plt


def _axis(ax: Any, feature: str) -> tuple[Any, Any]:
    plt = _pyplot(feature)
    if ax is None:
        fig, ax = plt.subplots()
    else:
        fig = ax.figure
    return fig, ax


def plot_residence_trace(
    records: list[TrajectoryRecord],
    window: ResidenceWindow | None = None,
    *,
    ax: Any = None,
) -> tuple[Any, Any]:
    """Plot a measured trajectory with an optional derived residence window."""

    if not records:
        raise ValueError("plot_residence_trace requires at least one record")
    fig, ax = _axis(ax, "plot_residence_trace")
    ordered = sorted(records, key=lambda row: row.time)
    ax.plot([row.time for row in ordered], [row.signal for row in ordered], marker="o", label="measured signal")
    if window is not None:
        ax.axhspan(window.low, window.high, alpha=0.15, label="declared residence window")
    ax.set_xlabel("time")
    ax.set_ylabel("signal")
    ax.legend()
    return fig, ax


def plot_coupling_interval(
    decision: EquivalenceDecision | TostDecision,
    *,
    ax: Any = None,
) -> tuple[Any, Any]:
    """Plot an equivalence interval against a declared margin."""

    fig, ax = _axis(ax, "plot_coupling_interval")
    estimate = decision.estimate
    ci_low = decision.ci_low
    ci_high = decision.ci_high
    ax.errorbar([estimate], [0], xerr=[[estimate - ci_low], [ci_high - estimate]], fmt="o", label="derived contrast")
    ax.axvline(-decision.margin, linestyle="--", color="tab:red", label="declared margin")
    ax.axvline(decision.margin, linestyle="--", color="tab:red")
    ax.axvline(0, color="black", linewidth=0.8)
    ax.set_yticks([])
    ax.set_xlabel("contrast")
    ax.legend()
    return fig, ax


def plot_reserve_summary(
    labels: list[str],
    reserves: list[float],
    *,
    ax: Any = None,
) -> tuple[Any, Any]:
    """Plot reserve-like derived summaries."""

    if len(labels) != len(reserves):
        raise ValueError("labels and reserves must have matching length")
    fig, ax = _axis(ax, "plot_reserve_summary")
    ax.bar(labels, reserves, label="derived reserve coordinate")
    ax.set_ylabel("reserve")
    ax.set_ylim(0, 1)
    ax.legend()
    return fig, ax


def plot_sensitivity_curve(
    curve: SensitivityCurveResult,
    *,
    ax: Any = None,
) -> tuple[Any, Any]:
    """Plot residence fraction across a declared window grid."""

    fig, ax = _axis(ax, "plot_sensitivity_curve")
    x = list(range(len(curve.points)))
    ax.plot(x, [point.residence_fraction for point in curve.points], marker="o", label="derived residence fraction")
    ax.set_xlabel("window index")
    ax.set_ylabel("residence fraction")
    ax.set_ylim(0, 1)
    ax.legend()
    return fig, ax


def plot_model_residuals(
    fits: list[ModelFit] | tuple[ModelFit, ...],
    *,
    ax: Any = None,
) -> tuple[Any, Any]:
    """Plot model RMSE values for endpoint-fit diagnostics."""

    if not fits:
        raise ValueError("plot_model_residuals requires at least one fit")
    fig, ax = _axis(ax, "plot_model_residuals")
    ax.bar([fit.model for fit in fits], [fit.rmse for fit in fits], label="model-derived RMSE")
    ax.set_ylabel("RMSE")
    ax.tick_params(axis="x", rotation=30)
    ax.legend()
    return fig, ax

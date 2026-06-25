"""Residence-window sensitivity curves."""

from __future__ import annotations

from rhodyn.residence import ResidenceWindow, score_trace
from rhodyn.results import GroupMetadata, ResultProvenance, SensitivityCurveResult, SensitivityPoint
from rhodyn.schema import TrajectoryRecord, group_trajectories


def linear_grid(start: float, stop: float, steps: int) -> tuple[float, ...]:
    """Return an inclusive linear grid."""

    if steps <= 0:
        raise ValueError("steps must be positive")
    if steps == 1:
        return (float(start),)
    step = (stop - start) / (steps - 1)
    return tuple(float(start + i * step) for i in range(steps))


def residence_window_grid(
    *,
    low_min: float,
    low_max: float,
    high_min: float,
    high_max: float,
    steps: int,
) -> tuple[ResidenceWindow, ...]:
    """Create all valid low/high windows across two declared grids."""

    lows = linear_grid(low_min, low_max, steps)
    highs = linear_grid(high_min, high_max, steps)
    windows = [ResidenceWindow(low, high) for low in lows for high in highs if low < high]
    if not windows:
        raise ValueError("window grid contains no valid low < high windows")
    return tuple(windows)


def score_trace_window_sensitivity(
    records: list[TrajectoryRecord],
    windows: tuple[ResidenceWindow, ...] | list[ResidenceWindow],
    *,
    min_residence_fraction: float = 0.0,
    parameters: dict[str, object] | None = None,
) -> SensitivityCurveResult:
    """Score one trajectory across residence windows."""

    if not records:
        raise ValueError("score_trace_window_sensitivity requires at least one trajectory record")
    if not 0 <= min_residence_fraction <= 1:
        raise ValueError("min_residence_fraction must be between 0 and 1")
    points: list[SensitivityPoint] = []
    qualifying = 0
    for window in windows:
        summary = score_trace(records, window)
        if summary.residence_fraction >= min_residence_fraction:
            qualifying += 1
        points.append(
            SensitivityPoint(
                low=window.low,
                high=window.high,
                residence_fraction=summary.residence_fraction,
                residence_time=summary.residence_time,
                mean_signal=summary.mean_signal,
                max_signal=summary.max_signal,
                min_signal=summary.min_signal,
                segment_count=len(summary.segments),
            )
        )
    ordered = sorted(records, key=lambda item: item.time)
    return SensitivityCurveResult(
        group=GroupMetadata(condition=ordered[0].condition, cell_id=ordered[0].cell_id, replicate=ordered[0].replicate),
        points=tuple(points),
        qualifying_window_count=qualifying,
        provenance=ResultProvenance(
            schema_kind="trajectory",
            parameters={"min_residence_fraction": min_residence_fraction, **(parameters or {})},
        ),
    )


def score_records_window_sensitivity(
    records: list[TrajectoryRecord],
    windows: tuple[ResidenceWindow, ...] | list[ResidenceWindow],
    *,
    min_residence_fraction: float = 0.0,
    parameters: dict[str, object] | None = None,
) -> list[SensitivityCurveResult]:
    """Score all trajectories across a declared window grid."""

    return [
        score_trace_window_sensitivity(
            trace,
            windows,
            min_residence_fraction=min_residence_fraction,
            parameters=parameters,
        )
        for trace in group_trajectories(records).values()
    ]

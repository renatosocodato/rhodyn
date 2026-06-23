"""Residence-window scoring for live-cell trajectories."""

from __future__ import annotations

from dataclasses import dataclass
from statistics import mean

from rhodyn.schema import TrajectoryRecord, group_trajectories


@dataclass(frozen=True)
class ResidenceWindow:
    """A permissive signal interval."""

    low: float
    high: float

    def contains(self, value: float) -> bool:
        return self.low <= value <= self.high


@dataclass(frozen=True)
class DwellSegment:
    """A contiguous in-window segment."""

    start: float
    end: float
    duration: float


@dataclass(frozen=True)
class TraceResidenceSummary:
    """Residence and amplitude summary for one trajectory."""

    condition: str
    cell_id: str
    n_points: int
    residence_fraction: float
    residence_time: float
    total_time: float
    mean_signal: float
    max_signal: float
    min_signal: float
    segments: tuple[DwellSegment, ...]


def dwell_segments(records: list[TrajectoryRecord], window: ResidenceWindow) -> tuple[DwellSegment, ...]:
    """Return contiguous intervals where the signal is inside the residence window."""

    if not records:
        return ()
    ordered = sorted(records, key=lambda item: item.time)
    segments: list[DwellSegment] = []
    start: float | None = None
    last_time = ordered[0].time
    for record in ordered:
        inside = window.contains(record.signal)
        if inside and start is None:
            start = record.time
        if not inside and start is not None:
            segments.append(DwellSegment(start=start, end=last_time, duration=max(0.0, last_time - start)))
            start = None
        last_time = record.time
    if start is not None:
        segments.append(DwellSegment(start=start, end=last_time, duration=max(0.0, last_time - start)))
    return tuple(segments)


def score_trace(records: list[TrajectoryRecord], window: ResidenceWindow) -> TraceResidenceSummary:
    """Score dwell time and amplitude summaries for one trajectory."""

    if not records:
        raise ValueError("score_trace requires at least one trajectory record")
    ordered = sorted(records, key=lambda item: item.time)
    condition = ordered[0].condition
    cell_id = ordered[0].cell_id
    values = [item.signal for item in ordered]

    if len(ordered) == 1:
        residence_fraction = 1.0 if window.contains(values[0]) else 0.0
        residence_time = residence_fraction
        total_time = 1.0
    else:
        intervals = [max(0.0, ordered[i + 1].time - ordered[i].time) for i in range(len(ordered) - 1)]
        total_time = sum(intervals)
        if total_time <= 0:
            residence_fraction = sum(window.contains(value) for value in values) / len(values)
            residence_time = residence_fraction
            total_time = 1.0
        else:
            residence_time = sum(dt for dt, record in zip(intervals, ordered[:-1]) if window.contains(record.signal))
            residence_fraction = residence_time / total_time

    return TraceResidenceSummary(
        condition=condition,
        cell_id=cell_id,
        n_points=len(ordered),
        residence_fraction=residence_fraction,
        residence_time=residence_time,
        total_time=total_time,
        mean_signal=mean(values),
        max_signal=max(values),
        min_signal=min(values),
        segments=dwell_segments(ordered, window),
    )


def score_records(records: list[TrajectoryRecord], window: ResidenceWindow) -> list[TraceResidenceSummary]:
    """Score all trajectories grouped by condition and cell."""

    return [score_trace(trace, window) for trace in group_trajectories(records).values()]


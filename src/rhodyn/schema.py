"""Input schema helpers for tidy live-cell and endpoint tables."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True)
class TrajectoryRecord:
    """One tidy live-cell signal observation."""

    cell_id: str
    time: float
    condition: str
    signal: float
    replicate: str = ""


@dataclass(frozen=True)
class EndpointRecord:
    """One observed-versus-predicted endpoint row."""

    model: str
    endpoint: str
    observed: float
    predicted: float
    weight: float = 1.0


@dataclass(frozen=True)
class ValidationIssue:
    """A schema validation issue."""

    row: int
    field: str
    message: str


def _as_float(value: str, field: str, row: int, issues: list[ValidationIssue]) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        issues.append(ValidationIssue(row=row, field=field, message=f"expected numeric value, got {value!r}"))
        return float("nan")


def read_trajectory_csv(
    path: str | Path,
    *,
    cell_id_column: str = "cell_id",
    time_column: str = "time",
    condition_column: str = "condition",
    signal_column: str = "signal",
    replicate_column: str = "replicate",
) -> tuple[list[TrajectoryRecord], list[ValidationIssue]]:
    """Read a tidy trajectory CSV and return records plus validation issues."""

    rows: list[TrajectoryRecord] = []
    issues: list[ValidationIssue] = []
    with Path(path).open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        required = [cell_id_column, time_column, condition_column, signal_column]
        missing = [field for field in required if field not in (reader.fieldnames or [])]
        if missing:
            return [], [ValidationIssue(row=0, field=",".join(missing), message="missing required column")]
        for i, row in enumerate(reader, start=2):
            cell_id = (row.get(cell_id_column) or "").strip()
            condition = (row.get(condition_column) or "").strip()
            if not cell_id:
                issues.append(ValidationIssue(row=i, field=cell_id_column, message="empty cell identifier"))
            if not condition:
                issues.append(ValidationIssue(row=i, field=condition_column, message="empty condition"))
            rows.append(
                TrajectoryRecord(
                    cell_id=cell_id,
                    time=_as_float(row.get(time_column, ""), time_column, i, issues),
                    condition=condition,
                    signal=_as_float(row.get(signal_column, ""), signal_column, i, issues),
                    replicate=(row.get(replicate_column) or "").strip(),
                )
            )
    return rows, issues


def read_endpoint_csv(path: str | Path) -> tuple[list[EndpointRecord], list[ValidationIssue]]:
    """Read endpoint model-comparison rows from CSV."""

    rows: list[EndpointRecord] = []
    issues: list[ValidationIssue] = []
    with Path(path).open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        required = ["model", "endpoint", "observed", "predicted"]
        missing = [field for field in required if field not in (reader.fieldnames or [])]
        if missing:
            return [], [ValidationIssue(row=0, field=",".join(missing), message="missing required column")]
        for i, row in enumerate(reader, start=2):
            rows.append(
                EndpointRecord(
                    model=(row.get("model") or "").strip(),
                    endpoint=(row.get("endpoint") or "").strip(),
                    observed=_as_float(row.get("observed", ""), "observed", i, issues),
                    predicted=_as_float(row.get("predicted", ""), "predicted", i, issues),
                    weight=_as_float(row.get("weight", "1.0") or "1.0", "weight", i, issues),
                )
            )
    return rows, issues


def group_trajectories(records: Iterable[TrajectoryRecord]) -> dict[tuple[str, str], list[TrajectoryRecord]]:
    """Group trajectory records by condition and cell identifier."""

    grouped: dict[tuple[str, str], list[TrajectoryRecord]] = {}
    for record in records:
        grouped.setdefault((record.condition, record.cell_id), []).append(record)
    for key in grouped:
        grouped[key] = sorted(grouped[key], key=lambda item: item.time)
    return grouped


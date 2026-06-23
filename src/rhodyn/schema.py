"""Input schema helpers for tidy live-cell and endpoint tables."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from math import isfinite
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
class ReserveRecord:
    """One reserve-like response observation."""

    sample_id: str
    time: float
    condition: str
    response: float
    replicate: str = ""


@dataclass(frozen=True)
class CouplingIntervalRecord:
    """One bounded-coupling interval or ROPE summary."""

    contrast: str
    estimate: float
    ci_low: float
    ci_high: float
    margin: float
    rope_mass: float | None = None


@dataclass(frozen=True)
class ValidationIssue:
    """A schema validation issue."""

    row: int
    field: str
    message: str


@dataclass(frozen=True)
class SchemaSpec:
    """Column contract for a tidy input role."""

    name: str
    required: tuple[str, ...]
    optional: tuple[str, ...] = ()


TRAJECTORY_SCHEMA = SchemaSpec(
    name="trajectory",
    required=("cell_id", "time", "condition", "signal"),
    optional=("replicate",),
)
ENDPOINT_SCHEMA = SchemaSpec(
    name="endpoint",
    required=("model", "endpoint", "observed", "predicted"),
    optional=("weight",),
)
RESERVE_SCHEMA = SchemaSpec(
    name="reserve",
    required=("sample_id", "time", "condition", "response"),
    optional=("replicate",),
)
COUPLING_SCHEMA = SchemaSpec(
    name="coupling",
    required=("contrast", "estimate", "ci_low", "ci_high", "margin"),
    optional=("rope_mass",),
)


def _as_float(value: str, field: str, row: int, issues: list[ValidationIssue]) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        issues.append(ValidationIssue(row=row, field=field, message=f"expected numeric value, got {value!r}"))
        return float("nan")
    if not isfinite(number):
        issues.append(ValidationIssue(row=row, field=field, message=f"expected finite numeric value, got {value!r}"))
    return number


def _as_optional_float(value: str | None, field: str, row: int, issues: list[ValidationIssue]) -> float | None:
    if value is None or str(value).strip() == "":
        return None
    return _as_float(str(value), field, row, issues)


def _require_columns(fieldnames: list[str] | None, schema: SchemaSpec) -> list[ValidationIssue]:
    available = set(fieldnames or [])
    issues: list[ValidationIssue] = []
    for field in schema.required:
        if field not in available:
            issues.append(ValidationIssue(row=0, field=field, message=f"missing required {schema.name} column"))
    return issues


def _required_text(row: dict[str, str], field: str, row_number: int, issues: list[ValidationIssue], label: str) -> str:
    value = (row.get(field) or "").strip()
    if not value:
        issues.append(ValidationIssue(row=row_number, field=field, message=f"empty {label} identifier"))
    return value


def _optional_text(row: dict[str, str], field: str) -> str:
    return (row.get(field) or "").strip()


def _check_nonnegative_time(value: float, field: str, row_number: int, issues: list[ValidationIssue]) -> None:
    if isfinite(value) and value < 0:
        issues.append(ValidationIssue(row=row_number, field=field, message="time must be non-negative"))


def schema_specs() -> dict[str, SchemaSpec]:
    """Return the stable input contracts exposed by RhoDyn."""

    return {
        TRAJECTORY_SCHEMA.name: TRAJECTORY_SCHEMA,
        ENDPOINT_SCHEMA.name: ENDPOINT_SCHEMA,
        RESERVE_SCHEMA.name: RESERVE_SCHEMA,
        COUPLING_SCHEMA.name: COUPLING_SCHEMA,
    }


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
            return [], [
                ValidationIssue(row=0, field=field, message="missing required trajectory column") for field in missing
            ]
        for i, row in enumerate(reader, start=2):
            cell_id = _required_text(row, cell_id_column, i, issues, "cell")
            condition = _required_text(row, condition_column, i, issues, "condition")
            time = _as_float(row.get(time_column, ""), time_column, i, issues)
            _check_nonnegative_time(time, time_column, i, issues)
            rows.append(
                TrajectoryRecord(
                    cell_id=cell_id,
                    time=time,
                    condition=condition,
                    signal=_as_float(row.get(signal_column, ""), signal_column, i, issues),
                    replicate=_optional_text(row, replicate_column),
                )
            )
    return rows, issues


def read_endpoint_csv(path: str | Path) -> tuple[list[EndpointRecord], list[ValidationIssue]]:
    """Read endpoint model-comparison rows from CSV."""

    rows: list[EndpointRecord] = []
    issues: list[ValidationIssue] = []
    with Path(path).open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        missing = _require_columns(reader.fieldnames, ENDPOINT_SCHEMA)
        if missing:
            return [], missing
        for i, row in enumerate(reader, start=2):
            rows.append(
                EndpointRecord(
                    model=_required_text(row, "model", i, issues, "model"),
                    endpoint=_required_text(row, "endpoint", i, issues, "endpoint"),
                    observed=_as_float(row.get("observed", ""), "observed", i, issues),
                    predicted=_as_float(row.get("predicted", ""), "predicted", i, issues),
                    weight=_as_float(row.get("weight", "1.0") or "1.0", "weight", i, issues),
                )
            )
    return rows, issues


def read_reserve_csv(path: str | Path) -> tuple[list[ReserveRecord], list[ValidationIssue]]:
    """Read reserve-like response rows from CSV."""

    rows: list[ReserveRecord] = []
    issues: list[ValidationIssue] = []
    with Path(path).open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        missing = _require_columns(reader.fieldnames, RESERVE_SCHEMA)
        if missing:
            return [], missing
        for i, row in enumerate(reader, start=2):
            time = _as_float(row.get("time", ""), "time", i, issues)
            _check_nonnegative_time(time, "time", i, issues)
            rows.append(
                ReserveRecord(
                    sample_id=_required_text(row, "sample_id", i, issues, "sample"),
                    time=time,
                    condition=_required_text(row, "condition", i, issues, "condition"),
                    response=_as_float(row.get("response", ""), "response", i, issues),
                    replicate=_optional_text(row, "replicate"),
                )
            )
    return rows, issues


def read_coupling_csv(path: str | Path) -> tuple[list[CouplingIntervalRecord], list[ValidationIssue]]:
    """Read bounded-coupling interval rows from CSV."""

    rows: list[CouplingIntervalRecord] = []
    issues: list[ValidationIssue] = []
    with Path(path).open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        missing = _require_columns(reader.fieldnames, COUPLING_SCHEMA)
        if missing:
            return [], missing
        for i, row in enumerate(reader, start=2):
            margin = _as_float(row.get("margin", ""), "margin", i, issues)
            if isfinite(margin) and margin <= 0:
                issues.append(ValidationIssue(row=i, field="margin", message="margin must be positive"))
            rows.append(
                CouplingIntervalRecord(
                    contrast=_required_text(row, "contrast", i, issues, "contrast"),
                    estimate=_as_float(row.get("estimate", ""), "estimate", i, issues),
                    ci_low=_as_float(row.get("ci_low", ""), "ci_low", i, issues),
                    ci_high=_as_float(row.get("ci_high", ""), "ci_high", i, issues),
                    margin=margin,
                    rope_mass=_as_optional_float(row.get("rope_mass"), "rope_mass", i, issues),
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

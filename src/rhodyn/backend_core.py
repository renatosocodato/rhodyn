"""Backend service core for RhoDyn.

The functions in this module are transport-independent. They accept table rows
as JSON-like dictionaries, run the same library functions used by the CLI, and
return JSON-friendly payloads with deterministic job metadata.
"""

from __future__ import annotations

import csv
import hashlib
import json
import tempfile
from pathlib import Path
from typing import Any

from rhodyn.compare import rank_model_fits
from rhodyn.coupling import equivalence_from_interval
from rhodyn.report import markdown_summary, to_plain
from rhodyn.reserve import ff_over_f0, reserve_coordinate
from rhodyn.residence import ResidenceWindow, score_records
from rhodyn.results import (
    GroupMetadata,
    ReserveResult,
    ResultProvenance,
    coupling_result_from_decision,
    model_comparison_result_from_fits,
    residence_result_from_summary,
    software_version,
)
from rhodyn.schema import read_coupling_csv, read_endpoint_csv, read_reserve_csv, read_trajectory_csv, schema_specs


API_SOURCE = "api_payload"


def _stable_payload_hash(payload: object) -> str:
    data = json.dumps(to_plain(payload), sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


def _coerce_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if not isinstance(rows, list):
        raise ValueError("rows must be a list of row dictionaries")
    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            raise ValueError(f"rows[{index}] must be a dictionary")
    return rows


def _fieldnames(kind: str, rows: list[dict[str, Any]]) -> list[str]:
    if rows:
        fields: list[str] = []
        for row in rows:
            for key in row:
                if key not in fields:
                    fields.append(str(key))
        return fields
    spec = schema_specs().get(kind)
    if spec is None:
        return []
    return list(spec.required + spec.optional)


def _write_rows_csv(path: Path, kind: str, rows: list[dict[str, Any]]) -> None:
    fields = _fieldnames(kind, rows)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})


def _read_table(
    kind: str,
    rows: list[dict[str, Any]],
    *,
    signal_column: str = "signal",
) -> tuple[list[Any], list[Any]]:
    rows = _coerce_rows(rows)
    with tempfile.TemporaryDirectory(prefix="rhodyn_backend_") as directory:
        path = Path(directory) / f"{kind}.csv"
        _write_rows_csv(path, kind, rows)
        if kind == "trajectory":
            return read_trajectory_csv(path, signal_column=signal_column)
        if kind == "endpoint":
            return read_endpoint_csv(path)
        if kind == "reserve":
            return read_reserve_csv(path)
        if kind == "coupling":
            return read_coupling_csv(path)
    raise ValueError(f"unsupported table kind: {kind!r}")


def _job(operation: str, kind: str, rows: list[dict[str, Any]], parameters: dict[str, Any]) -> dict[str, Any]:
    payload = {
        "operation": operation,
        "kind": kind,
        "input_rows": len(rows),
        "input_hash": _stable_payload_hash(rows),
        "parameters": parameters,
        "software_version": software_version(),
    }
    return {"job_id": _stable_payload_hash(payload)[:20], **payload}


def validate_table(kind: str, rows: list[dict[str, Any]], *, signal_column: str = "signal") -> dict[str, Any]:
    """Validate one API-submitted table against a RhoDyn schema."""

    parameters = {"signal_column": signal_column} if kind == "trajectory" else {}
    records, issues = _read_table(kind, rows, signal_column=signal_column)
    return {
        "status": "pass" if not issues else "fail",
        "job": _job("validate", kind, rows, parameters),
        "kind": kind,
        "schema": schema_specs()[kind],
        "rows": len(records),
        "issues": issues,
    }


def score_residence_table(
    rows: list[dict[str, Any]],
    *,
    low: float,
    high: float,
    signal_column: str = "signal",
) -> dict[str, Any]:
    """Score residence-window summaries from submitted trajectory rows."""

    parameters = {"low": low, "high": high, "signal_column": signal_column}
    records, issues = _read_table("trajectory", rows, signal_column=signal_column)
    if issues:
        return {"status": "fail", "job": _job("score_residence", "trajectory", rows, parameters), "issues": issues}
    summaries = score_records(records, ResidenceWindow(low=low, high=high))
    typed = [
        residence_result_from_summary(summary, parameters=parameters, source=API_SOURCE)
        for summary in summaries
    ]
    return {
        "status": "pass",
        "job": _job("score_residence", "trajectory", rows, parameters),
        "window": {"low": low, "high": high},
        "summaries": summaries,
        "typed_results": typed,
    }


def decide_coupling_table(
    rows: list[dict[str, Any]],
    *,
    rope_threshold: float = 0.95,
) -> dict[str, Any]:
    """Classify supplied bounded-coupling intervals or ROPE rows."""

    parameters = {"rope_threshold": rope_threshold}
    records, issues = _read_table("coupling", rows)
    if issues:
        return {"status": "fail", "job": _job("decide_coupling", "coupling", rows, parameters), "issues": issues}
    decisions = [
        equivalence_from_interval(
            record.estimate,
            record.ci_low,
            record.ci_high,
            record.margin,
            rope_mass=record.rope_mass,
            rope_threshold=rope_threshold,
        )
        for record in records
    ]
    typed = [
        coupling_result_from_decision(
            record.contrast,
            decision,
            parameters=parameters,
            source=API_SOURCE,
        )
        for record, decision in zip(records, decisions)
    ]
    return {
        "status": "pass",
        "job": _job("decide_coupling", "coupling", rows, parameters),
        "records": records,
        "decisions": decisions,
        "typed_results": typed,
    }


def summarize_reserve_table(
    rows: list[dict[str, Any]],
    *,
    floor: float,
    ceiling: float,
    baseline_points: int = 3,
    normalize: bool = True,
) -> dict[str, Any]:
    """Summarize reserve-like response rows by condition and sample."""

    parameters = {
        "floor": floor,
        "ceiling": ceiling,
        "baseline_points": baseline_points,
        "normalize": normalize,
    }
    records, issues = _read_table("reserve", rows)
    if issues:
        return {"status": "fail", "job": _job("summarize_reserve", "reserve", rows, parameters), "issues": issues}
    grouped: dict[tuple[str, str], list[Any]] = {}
    for record in records:
        grouped.setdefault((record.condition, record.sample_id), []).append(record)
    typed: list[ReserveResult] = []
    summaries: list[dict[str, Any]] = []
    for (condition, sample_id), sample_records in sorted(grouped.items()):
        ordered = sorted(sample_records, key=lambda item: item.time)
        values = [record.response for record in ordered]
        normalized = ff_over_f0(values, baseline_points=baseline_points) if normalize else values
        reserve = reserve_coordinate(normalized, floor=floor, ceiling=ceiling)
        peak_response = max(normalized)
        group = GroupMetadata(
            condition=condition,
            sample_id=sample_id,
            replicate=ordered[0].replicate,
        )
        result = ReserveResult(
            group=group,
            reserve=reserve,
            peak_response=peak_response,
            n_points=len(ordered),
            provenance=ResultProvenance(schema_kind="reserve", parameters=parameters, source=API_SOURCE),
        )
        typed.append(result)
        summaries.append(
            {
                "condition": condition,
                "sample_id": sample_id,
                "replicate": ordered[0].replicate,
                "n_points": len(ordered),
                "peak_response": peak_response,
                "reserve": reserve,
            }
        )
    return {
        "status": "pass",
        "job": _job("summarize_reserve", "reserve", rows, parameters),
        "summaries": summaries,
        "typed_results": typed,
    }


def compare_endpoint_models(rows: list[dict[str, Any]], *, parameter_count: int = 1) -> dict[str, Any]:
    """Rank endpoint model fits from submitted endpoint rows."""

    parameters = {"parameter_count": parameter_count}
    records, issues = _read_table("endpoint", rows)
    if issues:
        return {"status": "fail", "job": _job("compare_models", "endpoint", rows, parameters), "issues": issues}
    fits = rank_model_fits(records, parameter_count=parameter_count)
    typed = model_comparison_result_from_fits(fits, parameters=parameters, source=API_SOURCE)
    return {
        "status": "pass",
        "job": _job("compare_models", "endpoint", rows, parameters),
        "fits": fits,
        "typed_result": typed,
    }


def export_markdown_report(title: str, rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Return a compact Markdown table from submitted rows."""

    parameters = {"title": title}
    return {
        "status": "pass",
        "job": _job("export_markdown", "report", rows, parameters),
        "markdown": markdown_summary(title, rows),
    }

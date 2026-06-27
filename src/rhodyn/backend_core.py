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
import zipfile
from dataclasses import dataclass
from io import BytesIO, StringIO
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
BUNDLE_FORMAT = "rhodyn.analysis_bundle.v1"
ZIP_TIMESTAMP = (1980, 1, 1, 0, 0, 0)


@dataclass(frozen=True)
class AnalysisBundle:
    """A deterministic downloadable bundle for one backend job."""

    filename: str
    content_type: str
    data: bytes
    sha256: str
    manifest: dict[str, Any]


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


def _rows_to_csv_bytes(kind: str, rows: list[dict[str, Any]]) -> bytes:
    fields = _fieldnames(kind, rows)
    buffer = StringIO()
    writer = csv.DictWriter(buffer, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    for row in rows:
        writer.writerow({field: row.get(field, "") for field in fields})
    return buffer.getvalue().encode("utf-8")


def _dict_rows_to_csv_bytes(rows: list[dict[str, Any]]) -> bytes:
    if not rows:
        return b""
    fields: list[str] = []
    for row in rows:
        for key in row:
            if key not in fields:
                fields.append(str(key))
    buffer = StringIO()
    writer = csv.DictWriter(buffer, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    for row in rows:
        flat = {
            field: json.dumps(row.get(field), sort_keys=True) if isinstance(row.get(field), (dict, list)) else row.get(field)
            for field in fields
        }
        writer.writerow(flat)
    return buffer.getvalue().encode("utf-8")


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


def _require_float(parameters: dict[str, Any], key: str) -> float:
    if key not in parameters:
        raise ValueError(f"missing required parameter {key!r}")
    return float(parameters[key])


def _require_int(parameters: dict[str, Any], key: str, default: int) -> int:
    return int(parameters.get(key, default))


def run_backend_operation(
    operation: str,
    rows: list[dict[str, Any]],
    *,
    parameters: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Run one declared backend operation through the stable library API."""

    params = dict(parameters or {})
    if operation == "validate":
        return validate_table(
            str(params.get("kind", "trajectory")),
            rows,
            signal_column=str(params.get("signal_column", "signal")),
        )
    if operation == "score_residence":
        return score_residence_table(
            rows,
            low=_require_float(params, "low"),
            high=_require_float(params, "high"),
            signal_column=str(params.get("signal_column", "signal")),
        )
    if operation == "decide_coupling":
        return decide_coupling_table(rows, rope_threshold=float(params.get("rope_threshold", 0.95)))
    if operation == "summarize_reserve":
        return summarize_reserve_table(
            rows,
            floor=_require_float(params, "floor"),
            ceiling=_require_float(params, "ceiling"),
            baseline_points=_require_int(params, "baseline_points", 3),
            normalize=bool(params.get("normalize", True)),
        )
    if operation == "compare_models":
        return compare_endpoint_models(rows, parameter_count=_require_int(params, "parameter_count", 1))
    if operation == "export_markdown":
        return export_markdown_report(str(params.get("title", "RhoDyn report")), rows)
    known = ", ".join(
        [
            "validate",
            "score_residence",
            "decide_coupling",
            "summarize_reserve",
            "compare_models",
            "export_markdown",
        ]
    )
    raise ValueError(f"unsupported backend operation {operation!r}; known operations are {known}")


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


def _result_summary_rows(result: dict[str, Any]) -> list[dict[str, Any]]:
    plain = to_plain(result)
    for key in ("summaries", "fits", "typed_results", "decisions", "records"):
        value = plain.get(key)
        if isinstance(value, list) and all(isinstance(row, dict) for row in value):
            return value
    if "typed_result" in plain and isinstance(plain["typed_result"], dict):
        return [plain["typed_result"]]
    return [{"status": plain.get("status", ""), "operation": plain.get("job", {}).get("operation", "")}]


def _readme_text(operation: str, result: dict[str, Any]) -> str:
    job = result.get("job", {})
    status = result.get("status", "")
    lines = [
        "# RhoDyn analysis bundle",
        "",
        f"Operation: `{operation}`",
        f"Status: `{status}`",
        f"Job ID: `{job.get('job_id', '')}`",
        f"Software version: `{job.get('software_version', software_version())}`",
        "",
        "This bundle contains the submitted rows, declared parameters, exact JSON result,",
        "a compact result table, a Markdown report, and a manifest with SHA-256 checksums.",
        "The analysis result is generated by the same Python library functions exposed by",
        "the RhoDyn CLI and public API.",
        "",
        "A passing bounded-coupling decision means the submitted interval lies inside the",
        "declared biological margin. It does not mean zero coupling.",
        "",
    ]
    return "\n".join(lines)


def _markdown_job_report(operation: str, result: dict[str, Any]) -> str:
    plain = to_plain(result)
    rows = _result_summary_rows(plain)
    title = f"RhoDyn {operation} result"
    return markdown_summary(title, rows)


def _zip_bytes(files: dict[str, bytes]) -> bytes:
    buffer = BytesIO()
    with zipfile.ZipFile(buffer, mode="w", compression=zipfile.ZIP_DEFLATED) as archive:
        for name in sorted(files):
            info = zipfile.ZipInfo(name, ZIP_TIMESTAMP)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            archive.writestr(info, files[name])
    return buffer.getvalue()


def build_analysis_bundle(
    operation: str,
    rows: list[dict[str, Any]],
    *,
    parameters: dict[str, Any] | None = None,
) -> AnalysisBundle:
    """Build a deterministic ZIP bundle for one backend analysis job."""

    params = dict(parameters or {})
    result = run_backend_operation(operation, rows, parameters=params)
    plain_result = to_plain(result)
    job = plain_result.get("job", _job(operation, "unknown", rows, params))
    kind = str(job.get("kind", operation))
    files: dict[str, bytes] = {
        "README.md": _readme_text(operation, plain_result).encode("utf-8"),
        "input_rows.csv": _rows_to_csv_bytes(kind, _coerce_rows(rows)),
        "parameters.json": json.dumps(params, indent=2, sort_keys=True).encode("utf-8") + b"\n",
        "result.json": json.dumps(plain_result, indent=2, sort_keys=True).encode("utf-8") + b"\n",
        "result_rows.csv": _dict_rows_to_csv_bytes(_result_summary_rows(plain_result)),
        "report.md": _markdown_job_report(operation, plain_result).encode("utf-8"),
    }
    file_records = [
        {
            "path": path,
            "bytes": len(data),
            "sha256": hashlib.sha256(data).hexdigest(),
        }
        for path, data in sorted(files.items())
    ]
    manifest = {
        "bundle_format": BUNDLE_FORMAT,
        "operation": operation,
        "status": plain_result.get("status", ""),
        "job": job,
        "files": file_records,
        "interpretation_boundary": "Results are scoped to submitted rows and declared parameters. No backend bundle upgrades an association, interval, or model fit into a direct biological mechanism.",
    }
    files["manifest.json"] = json.dumps(manifest, indent=2, sort_keys=True).encode("utf-8") + b"\n"
    data = _zip_bytes(files)
    sha = hashlib.sha256(data).hexdigest()
    filename = f"rhodyn_{operation}_{job.get('job_id', 'job')}.zip"
    return AnalysisBundle(
        filename=filename,
        content_type="application/zip",
        data=data,
        sha256=sha,
        manifest=manifest,
    )


def write_analysis_bundle(
    path: str | Path,
    operation: str,
    rows: list[dict[str, Any]],
    *,
    parameters: dict[str, Any] | None = None,
) -> AnalysisBundle:
    """Write an analysis bundle to disk and return its manifest metadata."""

    bundle = build_analysis_bundle(operation, rows, parameters=parameters)
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(bundle.data)
    return bundle

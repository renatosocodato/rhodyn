"""Audit the Stage 4 backend service contract.

The audit is intentionally dependency-light. It exercises the transport-
independent backend core rather than FastAPI so it can run in the base package
environment. Each operation must return the same result through the direct
backend helper, generic job dispatcher, deterministic bundle, and durable job
store.
"""

from __future__ import annotations

import csv
import hashlib
import json
import tempfile
import zipfile
from dataclasses import dataclass
from io import BytesIO
from pathlib import Path
from typing import Any, Callable

from rhodyn.backend_core import (
    FileJobStore,
    build_analysis_bundle,
    compare_endpoint_models,
    decide_coupling_table,
    export_markdown_report,
    run_backend_operation,
    score_residence_table,
    summarize_reserve_table,
    validate_table,
)
from rhodyn.report import to_plain


ROOT = Path(__file__).resolve().parents[1]
REPORT_FORMAT = "rhodyn.stage4_service_contract_audit.v1"


@dataclass(frozen=True)
class OperationCase:
    """One backend operation and its direct library-backed reference call."""

    operation: str
    table_path: str
    parameters: dict[str, Any]
    direct: Callable[[list[dict[str, str]], dict[str, Any]], dict[str, Any]]


def _rows(path: str | Path) -> list[dict[str, str]]:
    with Path(path).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _bundle_json_member(data: bytes, name: str) -> dict[str, Any]:
    with zipfile.ZipFile(BytesIO(data)) as archive:
        return json.loads(archive.read(name).decode("utf-8"))


def _operation_cases() -> list[OperationCase]:
    return [
        OperationCase(
            operation="validate",
            table_path="examples/synthetic_trajectory.csv",
            parameters={"kind": "trajectory", "signal_column": "signal"},
            direct=lambda rows, params: validate_table(
                str(params["kind"]),
                rows,
                signal_column=str(params["signal_column"]),
            ),
        ),
        OperationCase(
            operation="score_residence",
            table_path="examples/synthetic_trajectory.csv",
            parameters={"low": 0.35, "high": 0.75, "signal_column": "signal"},
            direct=lambda rows, params: score_residence_table(
                rows,
                low=float(params["low"]),
                high=float(params["high"]),
                signal_column=str(params["signal_column"]),
            ),
        ),
        OperationCase(
            operation="decide_coupling",
            table_path="examples/synthetic_coupling.csv",
            parameters={"rope_threshold": 0.95},
            direct=lambda rows, params: decide_coupling_table(
                rows,
                rope_threshold=float(params["rope_threshold"]),
            ),
        ),
        OperationCase(
            operation="summarize_reserve",
            table_path="examples/synthetic_reserve.csv",
            parameters={"floor": 1.0, "ceiling": 1.7, "baseline_points": 1, "normalize": True},
            direct=lambda rows, params: summarize_reserve_table(
                rows,
                floor=float(params["floor"]),
                ceiling=float(params["ceiling"]),
                baseline_points=int(params["baseline_points"]),
                normalize=bool(params["normalize"]),
            ),
        ),
        OperationCase(
            operation="compare_models",
            table_path="examples/synthetic_endpoints.csv",
            parameters={"parameter_count": 1},
            direct=lambda rows, params: compare_endpoint_models(
                rows,
                parameter_count=int(params["parameter_count"]),
            ),
        ),
        OperationCase(
            operation="export_markdown",
            table_path="examples/synthetic_coupling.csv",
            parameters={"title": "RhoDyn report"},
            direct=lambda rows, params: export_markdown_report(str(params["title"]), rows),
        ),
    ]


def _audit_case(case: OperationCase, root: Path) -> dict[str, Any]:
    rows = _rows(root / case.table_path)
    direct_result = to_plain(case.direct(rows, case.parameters))
    job_result = to_plain(run_backend_operation(case.operation, rows, parameters=case.parameters))
    direct_matches_job = direct_result == job_result

    bundle = build_analysis_bundle(case.operation, rows, parameters=case.parameters)
    bundle_result = _bundle_json_member(bundle.data, "result.json")
    bundle_manifest = _bundle_json_member(bundle.data, "manifest.json")
    bundle_matches_job = bundle_result == job_result
    bundle_hash_valid = bundle.sha256 == hashlib.sha256(bundle.data).hexdigest()

    manifest_file_hashes_valid = True
    with zipfile.ZipFile(BytesIO(bundle.data)) as archive:
        for file_record in bundle_manifest["files"]:
            data = archive.read(file_record["path"])
            if hashlib.sha256(data).hexdigest() != file_record["sha256"]:
                manifest_file_hashes_valid = False
                break

    with tempfile.TemporaryDirectory(prefix="rhodyn_stage4_contract_") as tmp:
        store = FileJobStore(tmp)
        stored = store.submit(case.operation, rows, parameters=case.parameters)
        stored_result = store.get_result(stored.job_id)
        metadata, stored_bundle = store.read_bundle(stored.job_id)

    stored_matches_job = stored_result == job_result
    stored_bundle_hash_valid = metadata["bundle_sha256"] == hashlib.sha256(stored_bundle).hexdigest()
    job_id_matches = (
        direct_result.get("job", {}).get("job_id")
        == job_result.get("job", {}).get("job_id")
        == bundle_manifest.get("job", {}).get("job_id")
        == metadata.get("job_id")
    )

    checks = {
        "direct_matches_job": direct_matches_job,
        "bundle_matches_job": bundle_matches_job,
        "bundle_hash_valid": bundle_hash_valid,
        "manifest_file_hashes_valid": manifest_file_hashes_valid,
        "stored_matches_job": stored_matches_job,
        "stored_bundle_hash_valid": stored_bundle_hash_valid,
        "job_id_matches": job_id_matches,
    }
    return {
        "operation": case.operation,
        "table_path": case.table_path,
        "row_count": len(rows),
        "parameters": case.parameters,
        "job_id": job_result.get("job", {}).get("job_id"),
        "status": "pass" if all(checks.values()) else "fail",
        "checks": checks,
    }


def audit_stage4_service_contract(root: Path = ROOT) -> dict[str, Any]:
    """Return a machine-readable Stage 4 service-contract audit."""

    cases = [_audit_case(case, root) for case in _operation_cases()]
    failures = [
        f"{case['operation']} failed {name}"
        for case in cases
        for name, passed in case["checks"].items()
        if not passed
    ]
    return {
        "report_format": REPORT_FORMAT,
        "status": "pass" if not failures else "fail",
        "failures": failures,
        "operation_count": len(cases),
        "operations": cases,
        "interpretation_boundary": (
            "This audit checks backend service equivalence for retained example tables. "
            "It does not add a new biological system or new biological interpretation."
        ),
    }


def main() -> int:
    payload = audit_stage4_service_contract()
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())

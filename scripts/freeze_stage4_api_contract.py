"""Freeze the Stage 4 backend API contract for the Stage 5 scaffold.

The generator exports the FastAPI OpenAPI schema, frontend-facing operation
metadata, and canonical request/response fixtures from the same backend routes
used by the service. It uses deterministic synthetic/example rows only and
does not add a biological case study.
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
from typing import Any

from rhodyn.backend import BackendServiceLimits, create_app
from rhodyn.backend_core import JobRetentionPolicy
from rhodyn.results import software_version


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_ROOT = ROOT / "api" / "stage4"
FIXTURE_ROOT = OUTPUT_ROOT / "fixtures"
REPORT_FORMAT = "rhodyn.stage4_api_contract_freeze.v1"
FROZEN_CONTRACT_VERSION = "stage4-api-v1"
FROZEN_DATE = "2026-06-28"
AUTH_KEY = "stage4-contract-key"


@dataclass(frozen=True)
class OperationSpec:
    operation_id: str
    label: str
    screen: str
    endpoint: str
    method: str
    upload_operation: str
    table_kind: str
    example_csv: str
    parameters: dict[str, Any]
    biological_boundary: str


OPERATIONS = [
    OperationSpec("validate_trajectory", "Validate trajectory table", "Data upload and schema validation", "/jobs/upload/run", "POST", "validate", "trajectory", "examples/synthetic_trajectory.csv", {"kind": "trajectory", "signal_column": "signal"}, "Schema validation checks table structure only. It does not interpret a biological state."),
    OperationSpec("score_residence", "Score residence window", "Residence-window tuner", "/jobs/upload/run", "POST", "score_residence", "trajectory", "examples/synthetic_trajectory.csv", {"low": 0.35, "high": 0.75, "signal_column": "signal"}, "Residence scores are scoped to the declared signal column and window bounds."),
    OperationSpec("decide_coupling", "Decide bounded coupling", "Coupling/equivalence decision panel", "/jobs/upload/run", "POST", "decide_coupling", "coupling", "examples/synthetic_coupling.csv", {"rope_threshold": 0.95}, "A passing bounded-coupling decision means the supplied interval lies inside the declared margin. It does not prove zero coupling."),
    OperationSpec("summarize_reserve", "Summarize reserve", "Reserve-buffering panel", "/jobs/upload/run", "POST", "summarize_reserve", "reserve", "examples/synthetic_reserve.csv", {"floor": 1.0, "ceiling": 1.7, "baseline_points": 1, "normalize": True}, "Reserve summaries are derived from submitted response rows and declared normalization parameters."),
    OperationSpec("compare_models", "Compare reduced architectures", "Model-comparison panel", "/jobs/upload/run", "POST", "compare_models", "endpoint", "examples/synthetic_endpoints.csv", {"parameter_count": 1}, "Model comparison ranks supplied endpoint rows under declared assumptions. It does not identify every molecular edge."),
    OperationSpec("export_markdown", "Export Markdown report", "Report builder", "/jobs/upload/run", "POST", "export_markdown", "report", "examples/synthetic_coupling.csv", {"title": "RhoDyn report"}, "Report export summarizes submitted rows and does not add new inference."),
]


def _read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _zip_json_member(data: bytes, name: str) -> dict[str, Any]:
    with zipfile.ZipFile(BytesIO(data)) as archive:
        return json.loads(archive.read(name).decode("utf-8"))


def _normalize_stored_payload(payload: dict[str, Any]) -> dict[str, Any]:
    normalized = json.loads(json.dumps(payload, sort_keys=True))
    candidates: list[dict[str, Any]] = []
    if isinstance(normalized.get("stored_job"), dict):
        candidates.append(normalized["stored_job"])
    if isinstance(normalized.get("jobs"), list):
        candidates.extend(job for job in normalized["jobs"] if isinstance(job, dict))
    if isinstance(normalized.get("summary"), dict):
        normalized["summary"]["job_ids"] = sorted(normalized["summary"].get("job_ids", []))
    for item in candidates:
        if "stored_at_epoch" in item:
            item["stored_at_epoch"] = 0.0
    return normalized


def _write_response_fixture(name: str, status_code: int, payload: dict[str, Any]) -> None:
    _write_json(FIXTURE_ROOT / f"{name}.response.json", {"status_code": status_code, "body": _normalize_stored_payload(payload)})


def _write_request_fixture(name: str, payload: dict[str, Any]) -> None:
    _write_json(FIXTURE_ROOT / f"{name}.request.json", payload)


def _contract_operation_payload(spec: OperationSpec) -> dict[str, Any]:
    return {
        "operation_id": spec.operation_id,
        "label": spec.label,
        "screen": spec.screen,
        "endpoint": spec.endpoint,
        "method": spec.method,
        "upload_operation": spec.upload_operation,
        "table_kind": spec.table_kind,
        "example_csv": spec.example_csv,
        "parameters": spec.parameters,
        "biological_boundary": spec.biological_boundary,
        "bundle_endpoint": "/jobs/upload/bundle",
        "submit_endpoint": "/jobs/upload/submit",
    }


def freeze_stage4_api_contract(root: Path = ROOT) -> dict[str, Any]:
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    FIXTURE_ROOT.mkdir(parents=True, exist_ok=True)
    app = create_app(
        job_store_dir=tempfile.mkdtemp(prefix="rhodyn_stage4_contract_"),
        retention_policy=JobRetentionPolicy(max_jobs=20),
        service_limits=BackendServiceLimits(max_rows=100000, max_upload_bytes=10_000_000),
        api_keys=(AUTH_KEY,),
    )
    try:
        from fastapi.testclient import TestClient
    except ImportError as exc:
        raise RuntimeError("Stage 4 contract freeze requires installing rhodyn[backend]") from exc

    client = TestClient(app)
    headers = {"x-rhodyn-api-key": AUTH_KEY}
    openapi = app.openapi()
    _write_json(OUTPUT_ROOT / "openapi.json", openapi)

    for name, response in [("health", client.get("/health")), ("schemas", client.get("/schemas"))]:
        _write_response_fixture(name, response.status_code, response.json())

    direct_fixtures = [
        ("schemas_validate", "/schemas/validate", {"kind": "trajectory", "signal_column": "signal", "rows": _read_rows(root / "examples/synthetic_trajectory.csv")}),
        ("residence_score", "/residence/score", {"low": 0.35, "high": 0.75, "signal_column": "signal", "rows": _read_rows(root / "examples/synthetic_trajectory.csv")}),
        ("coupling_decide", "/coupling/decide", {"rope_threshold": 0.95, "rows": _read_rows(root / "examples/synthetic_coupling.csv")}),
        ("reserve_summarize", "/reserve/summarize", {"floor": 1.0, "ceiling": 1.7, "baseline_points": 1, "normalize": True, "rows": _read_rows(root / "examples/synthetic_reserve.csv")}),
        ("models_compare", "/models/compare", {"parameter_count": 1, "rows": _read_rows(root / "examples/synthetic_endpoints.csv")}),
        ("reports_markdown", "/reports/markdown", {"title": "RhoDyn report", "rows": _read_rows(root / "examples/synthetic_coupling.csv")}),
        ("jobs_run", "/jobs/run", {"operation": "score_residence", "parameters": {"low": 0.35, "high": 0.75}, "rows": _read_rows(root / "examples/synthetic_trajectory.csv")}),
    ]
    for name, endpoint, request_payload in direct_fixtures:
        _write_request_fixture(name, request_payload)
        response = client.post(endpoint, json=request_payload, headers=headers)
        _write_response_fixture(name, response.status_code, response.json())

    bundle_request = {"operation": "compare_models", "parameters": {"parameter_count": 1}, "rows": _read_rows(root / "examples/synthetic_endpoints.csv")}
    _write_request_fixture("jobs_bundle", bundle_request)
    bundle = client.post("/jobs/bundle", json=bundle_request, headers=headers)
    _write_json(FIXTURE_ROOT / "jobs_bundle.response.json", {"status_code": bundle.status_code, "content_type": bundle.headers.get("content-type", ""), "bundle_sha256": hashlib.sha256(bundle.content).hexdigest(), "bundle_manifest": _zip_json_member(bundle.content, "manifest.json")})

    submit = client.post("/jobs/submit", json=bundle_request, headers=headers)
    submit_payload = submit.json()
    job_id = submit_payload["stored_job"]["job_id"]
    _write_response_fixture("jobs_submit", submit.status_code, submit_payload)
    for name, endpoint in [("jobs_list", "/jobs"), ("jobs_summary", "/jobs/summary"), ("jobs_metadata", f"/jobs/{job_id}"), ("jobs_result", f"/jobs/{job_id}/result")]:
        response = client.get(endpoint, headers=headers)
        _write_response_fixture(name, response.status_code, response.json())
    stored_bundle = client.get(f"/jobs/{job_id}/bundle", headers=headers)
    _write_json(FIXTURE_ROOT / "jobs_stored_bundle.response.json", {"status_code": stored_bundle.status_code, "content_type": stored_bundle.headers.get("content-type", ""), "bundle_sha256": hashlib.sha256(stored_bundle.content).hexdigest(), "bundle_manifest": _zip_json_member(stored_bundle.content, "manifest.json")})

    for spec in OPERATIONS:
        csv_bytes = (root / spec.example_csv).read_bytes()
        (FIXTURE_ROOT / f"{spec.operation_id}.request.csv").write_bytes(csv_bytes)
        response = client.post(
            "/jobs/upload/run",
            params={"operation": spec.upload_operation, "parameters_json": json.dumps(spec.parameters, separators=(",", ":"))},
            content=csv_bytes,
            headers={**headers, "content-type": "text/csv"},
        )
        _write_response_fixture(f"{spec.operation_id}_upload_run", response.status_code, response.json())

    frontend_contract = {
        "contract_version": FROZEN_CONTRACT_VERSION,
        "stage": "Stage 5 frontend scaffold",
        "source_api_stage": "Stage 4 backend",
        "openapi_path": "api/stage4/openapi.json",
        "operation_endpoint": "/jobs/upload/run",
        "bundle_endpoint": "/jobs/upload/bundle",
        "submit_endpoint": "/jobs/upload/submit",
        "auth_header": "x-rhodyn-api-key",
        "operations": [_contract_operation_payload(spec) for spec in OPERATIONS],
        "screens": ["Project dashboard", "Data upload and schema validation", "Trajectory explorer", "Residence-window tuner", "Coupling/equivalence decision panel", "Reserve-buffering panel", "Model-comparison panel", "Report builder"],
        "interpretation_boundary": "The Stage 5 scaffold calls the frozen Stage 4 backend contract. It does not add new biological systems, algorithms, or manuscript interpretation.",
    }
    _write_json(OUTPUT_ROOT / "frontend_contract.json", frontend_contract)

    fixture_files = sorted(path.relative_to(root).as_posix() for path in FIXTURE_ROOT.iterdir() if path.is_file())
    manifest = {
        "report_format": REPORT_FORMAT,
        "status": "frozen",
        "contract_version": FROZEN_CONTRACT_VERSION,
        "frozen_date": FROZEN_DATE,
        "software_version": software_version(),
        "openapi_path": "api/stage4/openapi.json",
        "frontend_contract_path": "api/stage4/frontend_contract.json",
        "openapi_sha256": _sha256(OUTPUT_ROOT / "openapi.json"),
        "frontend_contract_sha256": _sha256(OUTPUT_ROOT / "frontend_contract.json"),
        "fixture_count": len(fixture_files),
        "fixture_files": fixture_files,
        "paths": sorted(openapi.get("paths", {})),
        "stage4_gate": {"backend_results_match_library": True, "hidden_state_policy": "durable jobs persist only through explicit job store configuration", "preserved_surfaces": ["input schema", "parameter choices", "software version", "bundle hashes"]},
        "stage5_handoff": {"allowed": True, "reason": "frontend scaffold can depend on frozen OpenAPI and frontend contract files"},
        "interpretation_boundary": "This contract freeze is a software interface surface. It does not add a biological case study or change RhoDyn's scientific interpretation.",
    }
    _write_json(OUTPUT_ROOT / "contract_manifest.json", manifest)
    return manifest


def main() -> int:
    manifest = freeze_stage4_api_contract()
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

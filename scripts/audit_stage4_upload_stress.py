"""Stress-test Stage 4 FastAPI upload and durable-job routes.

This audit uses deterministic synthetic tables only. It checks deployment-like
controls around authentication, upload size limits, row limits, durable storage,
bundle retrieval, retention, and repeated larger-table submissions without
adding a new biological case study.
"""

from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
import tempfile
import zipfile
from concurrent.futures import ThreadPoolExecutor
from io import BytesIO, StringIO
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
REPORT_FORMAT = "rhodyn.stage4_upload_stress_audit.v1"


def _trajectory_rows(cell_count: int = 320, time_points: int = 8) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for cell_index in range(cell_count):
        condition = "stress_control" if cell_index % 2 == 0 else "stress_shifted"
        replicate = f"well_{cell_index % 8 + 1:02d}"
        baseline = 0.25 + 0.02 * (cell_index % 5)
        for time_index in range(time_points):
            signal = baseline + 0.07 * time_index + (0.05 if condition == "stress_shifted" else 0.0)
            rows.append(
                {
                    "cell_id": f"cell_{cell_index:04d}",
                    "time": f"{time_index}",
                    "condition": condition,
                    "signal": f"{signal:.6f}",
                    "replicate": replicate,
                }
            )
    return rows


def _rows_to_csv_bytes(rows: list[dict[str, Any]]) -> bytes:
    if not rows:
        return b""
    fields = list(rows[0])
    buffer = StringIO()
    writer = csv.DictWriter(buffer, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue().encode("utf-8")


def _zip_json_member(data: bytes, name: str) -> dict[str, Any]:
    with zipfile.ZipFile(BytesIO(data)) as archive:
        return json.loads(archive.read(name).decode("utf-8"))


def _client_post_upload(client: Any, path: str, csv_data: bytes, params: dict[str, Any], key: str) -> Any:
    return client.post(
        path,
        params=params,
        content=csv_data,
        headers={"content-type": "text/csv", "x-rhodyn-api-key": key},
    )


def audit_stage4_upload_stress(root: Path = ROOT) -> dict[str, Any]:
    """Return a machine-readable FastAPI upload stress audit."""

    if not importlib.util.find_spec("fastapi") or not importlib.util.find_spec("httpx2"):
        return {
            "report_format": REPORT_FORMAT,
            "status": "fail",
            "failures": ["missing backend test dependencies; install rhodyn[backend]"],
            "checks": {},
        }
    from fastapi.testclient import TestClient

    from rhodyn.backend import BackendServiceLimits, create_app
    from rhodyn.backend_core import JobRetentionPolicy

    rows = _trajectory_rows()
    csv_data = _rows_to_csv_bytes(rows)
    parameters = {"low": 0.35, "high": 0.75}
    auth_key = "stage4-upload-key"
    checks: dict[str, bool] = {}
    details: dict[str, Any] = {
        "row_count": len(rows),
        "csv_bytes": len(csv_data),
        "operation": "score_residence",
        "parameters": parameters,
    }

    with tempfile.TemporaryDirectory(prefix="rhodyn_stage4_upload_stress_") as tmp:
        client = TestClient(
            create_app(
                job_store_dir=tmp,
                retention_policy=JobRetentionPolicy(max_jobs=2),
                service_limits=BackendServiceLimits(max_rows=len(rows) + 10, max_upload_bytes=len(csv_data) + 1024),
                api_keys=(auth_key,),
            )
        )

        health = client.get("/health")
        health_json = health.json()
        checks["health_reports_deployment_controls"] = (
            health.status_code == 200
            and health_json.get("authentication_required") is True
            and health_json.get("durable_job_storage") is True
            and health_json.get("service_limits", {}).get("max_rows") == len(rows) + 10
            and health_json.get("retention_policy", {}).get("max_jobs") == 2
        )

        no_auth = client.post(
            "/jobs/upload/run",
            params={"operation": "score_residence", "parameters_json": json.dumps(parameters)},
            content=csv_data,
            headers={"content-type": "text/csv"},
        )
        checks["auth_blocks_unauthorized_upload"] = no_auth.status_code == 401

        upload_run = _client_post_upload(
            client,
            "/jobs/upload/run",
            csv_data,
            {"operation": "score_residence", "parameters_json": json.dumps(parameters)},
            auth_key,
        )
        json_run = client.post(
            "/jobs/run",
            json={"operation": "score_residence", "parameters": parameters, "rows": rows},
            headers={"x-rhodyn-api-key": auth_key},
        )
        checks["upload_run_matches_json_job"] = (
            upload_run.status_code == 200
            and json_run.status_code == 200
            and upload_run.json() == json_run.json()
            and upload_run.json().get("status") == "pass"
        )
        reference_result = upload_run.json()

        upload_bundle = _client_post_upload(
            client,
            "/jobs/upload/bundle",
            csv_data,
            {"operation": "score_residence", "parameters_json": json.dumps(parameters)},
            auth_key,
        )
        bundle_sha = hashlib.sha256(upload_bundle.content).hexdigest()
        bundle_result = _zip_json_member(upload_bundle.content, "result.json") if upload_bundle.status_code == 200 else {}
        checks["upload_bundle_hash_valid"] = (
            upload_bundle.status_code == 200
            and upload_bundle.headers.get("x-rhodyn-bundle-sha256") == bundle_sha
        )
        checks["upload_bundle_result_matches_run"] = bundle_result == reference_result

        upload_submit = _client_post_upload(
            client,
            "/jobs/upload/submit",
            csv_data,
            {"operation": "score_residence", "parameters_json": json.dumps(parameters)},
            auth_key,
        )
        submit_json = upload_submit.json()
        job_id = submit_json.get("stored_job", {}).get("job_id")
        stored_result = client.get(f"/jobs/{job_id}/result", headers={"x-rhodyn-api-key": auth_key}) if job_id else None
        stored_bundle = client.get(f"/jobs/{job_id}/bundle", headers={"x-rhodyn-api-key": auth_key}) if job_id else None
        checks["upload_submit_result_matches_run"] = (
            upload_submit.status_code == 200
            and submit_json.get("result") == reference_result
            and submit_json.get("status") == "pass"
        )
        checks["stored_result_matches_submit"] = (
            stored_result is not None
            and stored_result.status_code == 200
            and stored_result.json().get("result") == reference_result
        )
        checks["stored_bundle_hash_valid"] = (
            stored_bundle is not None
            and stored_bundle.status_code == 200
            and stored_bundle.headers.get("x-rhodyn-bundle-sha256") == hashlib.sha256(stored_bundle.content).hexdigest()
        )

        def repeat_upload(_: int) -> str:
            response = _client_post_upload(
                client,
                "/jobs/upload/run",
                csv_data,
                {"operation": "score_residence", "parameters_json": json.dumps(parameters)},
                auth_key,
            )
            response.raise_for_status()
            return str(response.json()["job"]["job_id"])

        with ThreadPoolExecutor(max_workers=6) as executor:
            repeated_job_ids = list(executor.map(repeat_upload, range(12)))
        checks["concurrent_upload_job_ids_stable"] = len(set(repeated_job_ids)) == 1 and repeated_job_ids[0] == reference_result["job"]["job_id"]

        for low in (0.25, 0.45):
            _client_post_upload(
                client,
                "/jobs/upload/submit",
                csv_data,
                {"operation": "score_residence", "parameters_json": json.dumps({"low": low, "high": 0.75})},
                auth_key,
            )
        listing = client.get("/jobs", headers={"x-rhodyn-api-key": auth_key})
        jobs = listing.json().get("jobs", []) if listing.status_code == 200 else []
        checks["retention_prunes_to_configured_job_limit"] = listing.status_code == 200 and len(jobs) == 2
        details["retained_job_ids"] = [job.get("job_id") for job in jobs]

    row_limit_client = TestClient(
        create_app(service_limits=BackendServiceLimits(max_rows=len(rows) - 1, max_upload_bytes=len(csv_data) + 1024))
    )
    row_limit = row_limit_client.post(
        "/jobs/upload/run",
        params={"operation": "score_residence", "parameters_json": json.dumps(parameters)},
        content=csv_data,
        headers={"content-type": "text/csv"},
    )
    checks["row_limit_blocks_large_upload"] = row_limit.status_code == 413 and "RHODYN_MAX_ROWS" in row_limit.json().get("error", "")

    byte_limit_client = TestClient(
        create_app(service_limits=BackendServiceLimits(max_rows=len(rows) + 10, max_upload_bytes=max(1, len(csv_data) // 3)))
    )
    byte_limit = byte_limit_client.post(
        "/jobs/upload/run",
        params={"operation": "score_residence", "parameters_json": json.dumps(parameters)},
        content=csv_data,
        headers={"content-type": "text/csv"},
    )
    checks["byte_limit_blocks_large_upload"] = (
        byte_limit.status_code == 413 and "RHODYN_MAX_UPLOAD_BYTES" in byte_limit.json().get("error", "")
    )

    failures = [name for name, passed in checks.items() if not passed]
    return {
        "report_format": REPORT_FORMAT,
        "status": "pass" if not failures else "fail",
        "failures": failures,
        "checks": checks,
        "details": details,
        "interpretation_boundary": (
            "This stress audit uses deterministic synthetic upload tables. It exercises deployment-style "
            "FastAPI behavior and does not add a biological case study or new biological interpretation."
        ),
    }


def main() -> int:
    payload = audit_stage4_upload_stress()
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())

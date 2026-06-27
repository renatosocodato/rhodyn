"""Smoke-test the Stage 4 backend in a Docker deployment shape.

The smoke test builds the Stage 4 image, starts the FastAPI backend with
deployment-like environment variables, and exercises HTTP upload, job,
bundle, authentication, quota, and retention behavior. It uses deterministic
synthetic rows only and does not add a biological case study.
"""

from __future__ import annotations

import csv
import hashlib
import json
import socket
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from dataclasses import dataclass
from io import BytesIO, StringIO
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
REPORT_FORMAT = "rhodyn.stage4_docker_smoke_audit.v1"
IMAGE_TAG = "rhodyn-stage4-smoke:local"
AUTH_KEY = "stage4-smoke-key"
REQUIRED_ENV_KEYS = [
    "RHODYN_JOB_STORE_DIR",
    "RHODYN_API_KEYS",
    "RHODYN_MAX_ROWS",
    "RHODYN_MAX_UPLOAD_BYTES",
    "RHODYN_JOB_RETENTION_MAX_JOBS",
    "RHODYN_JOB_RETENTION_MAX_BYTES",
    "RHODYN_JOB_RETENTION_MAX_AGE_SECONDS",
]


@dataclass(frozen=True)
class HttpResult:
    """Small HTTP result wrapper for stdlib requests."""

    status: int
    headers: dict[str, str]
    body: bytes

    def json(self) -> dict[str, Any]:
        return json.loads(self.body.decode("utf-8"))


def _run(command: list[str], *, cwd: Path = ROOT, timeout: int = 120) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(
            command,
            cwd=cwd,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
            check=False,
        )
    except FileNotFoundError as exc:
        return subprocess.CompletedProcess(command, 127, "", str(exc))
    except subprocess.TimeoutExpired as exc:
        stdout = exc.stdout if isinstance(exc.stdout, str) else ""
        stderr = exc.stderr if isinstance(exc.stderr, str) else ""
        return subprocess.CompletedProcess(command, 124, stdout, stderr or f"timed out after {timeout} seconds")


def _trajectory_rows(cell_count: int = 320, time_points: int = 8) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for cell_index in range(cell_count):
        condition = "docker_control" if cell_index % 2 == 0 else "docker_shifted"
        replicate = f"well_{cell_index % 8 + 1:02d}"
        baseline = 0.25 + 0.02 * (cell_index % 5)
        for time_index in range(time_points):
            signal = baseline + 0.07 * time_index + (0.05 if condition == "docker_shifted" else 0.0)
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


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def _request(
    method: str,
    url: str,
    *,
    body: bytes | None = None,
    headers: dict[str, str] | None = None,
    timeout: int = 20,
) -> HttpResult:
    request = urllib.request.Request(url, data=body, method=method, headers=headers or {})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return HttpResult(response.status, dict(response.headers.items()), response.read())
    except urllib.error.HTTPError as exc:
        return HttpResult(exc.code, dict(exc.headers.items()), exc.read())


def _post_csv(base_url: str, path: str, csv_data: bytes, params: dict[str, str], *, key: str | None) -> HttpResult:
    query = urllib.parse.urlencode(params)
    headers = {"content-type": "text/csv"}
    if key is not None:
        headers["x-rhodyn-api-key"] = key
    return _request("POST", f"{base_url}{path}?{query}", body=csv_data, headers=headers)


def _zip_json_member(data: bytes, name: str) -> dict[str, Any]:
    with zipfile.ZipFile(BytesIO(data)) as archive:
        return json.loads(archive.read(name).decode("utf-8"))


def _header(headers: dict[str, str], name: str) -> str | None:
    wanted = name.lower()
    for key, value in headers.items():
        if key.lower() == wanted:
            return value
    return None


def _wait_for_health(base_url: str, timeout_seconds: int = 60) -> HttpResult | None:
    deadline = time.monotonic() + timeout_seconds
    last: HttpResult | None = None
    while time.monotonic() < deadline:
        try:
            last = _request("GET", f"{base_url}/health", timeout=3)
            if last.status == 200:
                return last
        except Exception:
            pass
        time.sleep(1)
    return last


def _template_declares_env(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    return all(key in text for key in REQUIRED_ENV_KEYS)


def _compose_command_status() -> dict[str, Any]:
    docker_compose = _run(["docker", "compose", "version"], timeout=10)
    if docker_compose.returncode == 0:
        return {"available": True, "command": "docker compose", "version": docker_compose.stdout.strip()}
    legacy = _run(["docker-compose", "version"], timeout=10)
    if legacy.returncode == 0:
        return {"available": True, "command": "docker-compose", "version": legacy.stdout.strip()}
    return {
        "available": False,
        "command": None,
        "version": None,
        "note": "Compose CLI not available in this shell; compose template was still checked.",
    }


def audit_stage4_docker_smoke(root: Path = ROOT) -> dict[str, Any]:
    """Build and run the Stage 4 backend container, then exercise HTTP routes."""

    compose_path = root / "deploy" / "docker-compose.stage4.yml"
    env_example_path = root / "deploy" / "stage4.env.example"
    compose_text = compose_path.read_text(encoding="utf-8") if compose_path.exists() else ""
    checks: dict[str, bool] = {
        "dockerfile_exists": (root / "deploy" / "stage4.Dockerfile").exists(),
        "compose_file_exists": compose_path.exists(),
        "env_example_exists": env_example_path.exists(),
        "compose_template_declares_required_env": _template_declares_env(compose_path) if compose_path.exists() else False,
        "env_example_declares_required_env": _template_declares_env(env_example_path) if env_example_path.exists() else False,
        "compose_template_declares_backend_service": "rhodyn-backend:" in compose_text,
        "compose_template_uses_stage4_dockerfile": "dockerfile: deploy/stage4.Dockerfile" in compose_text,
        "compose_template_exposes_configurable_port": "${RHODYN_PORT:-8000}:8000" in compose_text,
        "compose_template_uses_durable_job_volume": (
            "rhodyn_jobs:" in compose_text
            and "rhodyn_jobs:/var/lib/rhodyn/jobs" in compose_text
            and "RHODYN_JOB_STORE_DIR: /var/lib/rhodyn/jobs" in compose_text
        ),
    }
    details: dict[str, Any] = {"compose": _compose_command_status()}
    failures: list[str] = [name for name, passed in checks.items() if not passed]
    if failures:
        return {
            "report_format": REPORT_FORMAT,
            "status": "fail",
            "failures": failures,
            "checks": checks,
            "details": details,
        }

    docker_version = _run(["docker", "--version"], timeout=10)
    docker_info = _run(["docker", "info", "--format", "{{json .ServerVersion}}"], timeout=20)
    checks["docker_cli_available"] = docker_version.returncode == 0
    checks["docker_daemon_available"] = docker_info.returncode == 0
    details["docker_version"] = docker_version.stdout.strip()
    details["docker_daemon"] = docker_info.stdout.strip()
    if not checks["docker_cli_available"] or not checks["docker_daemon_available"]:
        failures = [name for name, passed in checks.items() if not passed]
        details["docker_error"] = docker_info.stderr.strip()
        return {
            "report_format": REPORT_FORMAT,
            "status": "fail",
            "failures": failures,
            "checks": checks,
            "details": details,
            "interpretation_boundary": "Docker daemon was not available, so container HTTP behavior was not exercised.",
        }

    rows = _trajectory_rows()
    csv_data = _rows_to_csv_bytes(rows)
    high_row_csv = _rows_to_csv_bytes(_trajectory_rows(cell_count=390, time_points=8))
    high_byte_csv = csv_data + (b"#padding\n" * 15000)
    parameters = {"low": 0.35, "high": 0.75}
    query_params = {"operation": "score_residence", "parameters_json": json.dumps(parameters, separators=(",", ":"))}
    port = _free_port()
    base_url = f"http://127.0.0.1:{port}"
    container_id = ""
    details.update({"row_count": len(rows), "csv_bytes": len(csv_data), "host_port": port})

    build = _run(["docker", "build", "-f", "deploy/stage4.Dockerfile", "-t", IMAGE_TAG, "."], timeout=300)
    checks["docker_build_passes"] = build.returncode == 0
    details["docker_build_tail"] = "\n".join((build.stdout + build.stderr).splitlines()[-12:])
    if not checks["docker_build_passes"]:
        failures = [name for name, passed in checks.items() if not passed]
        return {
            "report_format": REPORT_FORMAT,
            "status": "fail",
            "failures": failures,
            "checks": checks,
            "details": details,
        }

    try:
        run = _run(
            [
                "docker",
                "run",
                "-d",
                "--rm",
                "-p",
                f"127.0.0.1:{port}:8000",
                "-e",
                "RHODYN_JOB_STORE_DIR=/var/lib/rhodyn/jobs",
                "-e",
                f"RHODYN_API_KEYS={AUTH_KEY}",
                "-e",
                "RHODYN_MAX_ROWS=3000",
                "-e",
                "RHODYN_MAX_UPLOAD_BYTES=200000",
                "-e",
                "RHODYN_JOB_RETENTION_MAX_JOBS=2",
                "-e",
                "RHODYN_JOB_RETENTION_MAX_BYTES=20000000",
                "-e",
                "RHODYN_JOB_RETENTION_MAX_AGE_SECONDS=3600",
                IMAGE_TAG,
            ],
            timeout=60,
        )
        checks["docker_run_starts_container"] = run.returncode == 0 and bool(run.stdout.strip())
        container_id = run.stdout.strip()
        details["container_id"] = container_id[:12]
        if not checks["docker_run_starts_container"]:
            details["docker_run_error"] = run.stderr.strip()
            failures = [name for name, passed in checks.items() if not passed]
            return {
                "report_format": REPORT_FORMAT,
                "status": "fail",
                "failures": failures,
                "checks": checks,
                "details": details,
            }

        health = _wait_for_health(base_url)
        health_json = health.json() if health and health.status == 200 else {}
        checks["health_reports_env_controls"] = (
            health is not None
            and health.status == 200
            and health_json.get("authentication_required") is True
            and health_json.get("durable_job_storage") is True
            and health_json.get("service_limits", {}).get("max_rows") == 3000
            and health_json.get("service_limits", {}).get("max_upload_bytes") == 200000
            and health_json.get("retention_policy", {}).get("max_jobs") == 2
        )

        unauthorized = _post_csv(base_url, "/jobs/upload/run", csv_data, query_params, key=None)
        checks["auth_blocks_unauthorized_upload"] = unauthorized.status == 401

        upload_run = _post_csv(base_url, "/jobs/upload/run", csv_data, query_params, key=AUTH_KEY)
        reference = upload_run.json() if upload_run.status == 200 else {}
        checks["authorized_upload_run_passes"] = upload_run.status == 200 and reference.get("status") == "pass"

        upload_bundle = _post_csv(base_url, "/jobs/upload/bundle", csv_data, query_params, key=AUTH_KEY)
        bundle_sha = hashlib.sha256(upload_bundle.body).hexdigest()
        bundle_result = _zip_json_member(upload_bundle.body, "result.json") if upload_bundle.status == 200 else {}
        checks["bundle_hash_valid"] = upload_bundle.status == 200 and _header(upload_bundle.headers, "X-RhoDyn-Bundle-SHA256") == bundle_sha
        checks["bundle_result_matches_upload_run"] = bundle_result == reference

        upload_submit = _post_csv(base_url, "/jobs/upload/submit", csv_data, query_params, key=AUTH_KEY)
        submit_json = upload_submit.json() if upload_submit.status == 200 else {}
        job_id = submit_json.get("stored_job", {}).get("job_id", "")
        stored_result = _request("GET", f"{base_url}/jobs/{job_id}/result", headers={"x-rhodyn-api-key": AUTH_KEY}) if job_id else None
        stored_bundle = _request("GET", f"{base_url}/jobs/{job_id}/bundle", headers={"x-rhodyn-api-key": AUTH_KEY}) if job_id else None
        checks["upload_submit_matches_run"] = upload_submit.status == 200 and submit_json.get("result") == reference
        checks["stored_result_matches_submit"] = stored_result is not None and stored_result.status == 200 and stored_result.json().get("result") == reference
        checks["stored_bundle_hash_valid"] = (
            stored_bundle is not None
            and stored_bundle.status == 200
            and _header(stored_bundle.headers, "X-RhoDyn-Bundle-SHA256") == hashlib.sha256(stored_bundle.body).hexdigest()
        )

        row_limit = _post_csv(base_url, "/jobs/upload/run", high_row_csv, query_params, key=AUTH_KEY)
        byte_limit = _post_csv(base_url, "/jobs/upload/run", high_byte_csv, query_params, key=AUTH_KEY)
        checks["row_limit_blocks_large_upload"] = row_limit.status == 413 and "RHODYN_MAX_ROWS" in row_limit.body.decode("utf-8")
        checks["byte_limit_blocks_large_upload"] = byte_limit.status == 413 and "RHODYN_MAX_UPLOAD_BYTES" in byte_limit.body.decode("utf-8")

        for low in (0.25, 0.45):
            params = {"operation": "score_residence", "parameters_json": json.dumps({"low": low, "high": 0.75}, separators=(",", ":"))}
            _post_csv(base_url, "/jobs/upload/submit", csv_data, params, key=AUTH_KEY)
        listing = _request("GET", f"{base_url}/jobs", headers={"x-rhodyn-api-key": AUTH_KEY})
        jobs = listing.json().get("jobs", []) if listing.status == 200 else []
        checks["retention_prunes_to_configured_job_limit"] = listing.status == 200 and len(jobs) == 2
        details["retained_job_ids"] = [job.get("job_id") for job in jobs]
    finally:
        if container_id:
            _run(["docker", "rm", "-f", container_id], timeout=30)

    failures = [name for name, passed in checks.items() if not passed]
    return {
        "report_format": REPORT_FORMAT,
        "status": "pass" if not failures else "fail",
        "failures": failures,
        "checks": checks,
        "details": details,
        "interpretation_boundary": (
            "This Docker smoke audit uses deterministic synthetic upload rows. "
            "It exercises Stage 4 deployment behavior and does not add a biological case study or new interpretation."
        ),
    }


def main() -> int:
    payload = audit_stage4_docker_smoke()
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())

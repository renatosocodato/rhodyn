"""FastAPI application factory for the RhoDyn backend."""

from __future__ import annotations

import csv
import json
import os
from dataclasses import dataclass
from io import BytesIO, StringIO
from pathlib import Path
from typing import Any, Callable, Iterable

from rhodyn.backend_core import (
    FileJobStore,
    JobRetentionPolicy,
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
from rhodyn.results import software_version
from rhodyn.schema import schema_specs


class ServiceLimitError(ValueError):
    """Raised when an API payload exceeds configured service limits."""


@dataclass(frozen=True)
class BackendServiceLimits:
    """Optional service-level limits for uploaded tables."""

    max_rows: int | None = None
    max_upload_bytes: int | None = None

    def is_enabled(self) -> bool:
        return self.max_rows is not None or self.max_upload_bytes is not None

    def as_dict(self) -> dict[str, Any]:
        return {
            "max_rows": self.max_rows,
            "max_upload_bytes": self.max_upload_bytes,
        }


def _require_rows(payload: dict[str, Any]) -> list[dict[str, Any]]:
    rows = payload.get("rows")
    if not isinstance(rows, list):
        raise ValueError("payload must include rows as a list")
    return rows


def _env_int(name: str) -> int | None:
    value = os.environ.get(name)
    return int(value) if value not in (None, "") else None


def _env_float(name: str) -> float | None:
    value = os.environ.get(name)
    return float(value) if value not in (None, "") else None


def _retention_from_env() -> JobRetentionPolicy | None:
    policy = JobRetentionPolicy(
        max_jobs=_env_int("RHODYN_JOB_RETENTION_MAX_JOBS"),
        max_bytes=_env_int("RHODYN_JOB_RETENTION_MAX_BYTES"),
        max_age_seconds=_env_float("RHODYN_JOB_RETENTION_MAX_AGE_SECONDS"),
    )
    return policy if policy.is_enabled() else None


def _limits_from_env() -> BackendServiceLimits | None:
    limits = BackendServiceLimits(
        max_rows=_env_int("RHODYN_MAX_ROWS"),
        max_upload_bytes=_env_int("RHODYN_MAX_UPLOAD_BYTES"),
    )
    return limits if limits.is_enabled() else None


def _api_keys_from_env() -> tuple[str, ...]:
    value = os.environ.get("RHODYN_API_KEYS", "")
    return tuple(key.strip() for key in value.split(",") if key.strip())


def _parameters_from_json(text: str | None) -> dict[str, Any]:
    if text in (None, ""):
        return {}
    payload = json.loads(text)
    if not isinstance(payload, dict):
        raise ValueError("parameters_json must decode to a JSON object")
    return payload


def _csv_rows_from_bytes(data: bytes) -> list[dict[str, Any]]:
    if not data.strip():
        raise ValueError("CSV upload is empty")
    text = data.decode("utf-8-sig")
    reader = csv.DictReader(StringIO(text))
    if not reader.fieldnames:
        raise ValueError("CSV upload must include a header row")
    return [dict(row) for row in reader]


def create_app(
    job_store_dir: str | Path | None = None,
    *,
    retention_policy: JobRetentionPolicy | None = None,
    service_limits: BackendServiceLimits | None = None,
    api_keys: Iterable[str] | None = None,
) -> Any:
    """Create the FastAPI app.

    FastAPI is optional so importing :mod:`rhodyn.backend` does not add runtime
    dependencies to the core library. Install ``rhodyn[backend]`` to run this
    application.
    """

    try:
        from fastapi import Depends, FastAPI, HTTPException, Request
        from fastapi.responses import JSONResponse, StreamingResponse
    except ImportError as exc:  # pragma: no cover - exercised only without optional extra
        raise RuntimeError("FastAPI backend requires installing rhodyn[backend]") from exc
    globals()["Request"] = Request

    store_dir = job_store_dir if job_store_dir is not None else os.environ.get("RHODYN_JOB_STORE_DIR")
    policy = retention_policy if retention_policy is not None else _retention_from_env()
    limits = service_limits if service_limits is not None else _limits_from_env()
    required_keys = tuple(api_keys) if api_keys is not None else _api_keys_from_env()
    job_store = FileJobStore(store_dir, retention_policy=policy) if store_dir else None

    app = FastAPI(
        title="RhoDyn backend",
        version=software_version(),
        description="API around RhoDyn dynamic-state analysis helpers with optional durable job storage.",
    )

    def require_api_key(request: Request) -> None:
        if not required_keys:
            return
        supplied = request.headers.get("x-rhodyn-api-key")
        authorization = request.headers.get("authorization", "")
        if not supplied and authorization.lower().startswith("bearer "):
            supplied = authorization[7:].strip()
        if supplied not in required_keys:
            raise HTTPException(
                status_code=401,
                detail="valid RhoDyn API key required",
                headers={"WWW-Authenticate": "Bearer"},
            )

    protected = [Depends(require_api_key)]

    def enforce_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
        if limits and limits.max_rows is not None and len(rows) > limits.max_rows:
            raise ServiceLimitError(f"payload has {len(rows)} rows, exceeding RHODYN_MAX_ROWS={limits.max_rows}")
        return rows

    def require_rows(payload: dict[str, Any]) -> list[dict[str, Any]]:
        return enforce_rows(_require_rows(payload))

    async def read_upload_rows(request: Request) -> list[dict[str, Any]]:
        chunks: list[bytes] = []
        total = 0
        async for chunk in request.stream():
            total += len(chunk)
            if limits and limits.max_upload_bytes is not None and total > limits.max_upload_bytes:
                raise ServiceLimitError(
                    f"CSV upload has at least {total} bytes, exceeding RHODYN_MAX_UPLOAD_BYTES={limits.max_upload_bytes}"
                )
            chunks.append(chunk)
        return enforce_rows(_csv_rows_from_bytes(b"".join(chunks)))

    def call(func: Callable[[], dict[str, Any]]) -> Any:
        try:
            return to_plain(func())
        except ServiceLimitError as exc:
            return JSONResponse({"status": "fail", "error": str(exc)}, status_code=413)
        except Exception as exc:
            return {"status": "fail", "error": str(exc)}

    @app.get("/health")
    def health() -> dict[str, Any]:
        return {
            "status": "pass",
            "software_version": software_version(),
            "durable_job_storage": bool(job_store),
            "retention_policy": policy.as_dict() if policy else None,
            "service_limits": limits.as_dict() if limits else None,
            "authentication_required": bool(required_keys),
        }

    @app.get("/schemas")
    def schemas() -> dict[str, Any]:
        return to_plain({"status": "pass", "schemas": schema_specs()})

    @app.post("/schemas/validate", dependencies=protected)
    def validate(payload: dict[str, Any]) -> dict[str, Any]:
        def run() -> dict[str, Any]:
            kind = str(payload.get("kind", "trajectory"))
            signal_column = str(
                payload.get("signal_column", payload.get("parameters", {}).get("signal_column", "signal"))
            )
            return validate_table(kind, require_rows(payload), signal_column=signal_column)

        return call(run)

    @app.post("/residence/score", dependencies=protected)
    def residence(payload: dict[str, Any]) -> dict[str, Any]:
        def run() -> dict[str, Any]:
            parameters = dict(payload.get("parameters") or {})
            low = float(payload.get("low", parameters.get("low")))
            high = float(payload.get("high", parameters.get("high")))
            signal_column = str(payload.get("signal_column", parameters.get("signal_column", "signal")))
            return score_residence_table(require_rows(payload), low=low, high=high, signal_column=signal_column)

        return call(run)

    @app.post("/coupling/decide", dependencies=protected)
    def coupling(payload: dict[str, Any]) -> dict[str, Any]:
        def run() -> dict[str, Any]:
            parameters = dict(payload.get("parameters") or {})
            rope_threshold = float(payload.get("rope_threshold", parameters.get("rope_threshold", 0.95)))
            return decide_coupling_table(require_rows(payload), rope_threshold=rope_threshold)

        return call(run)

    @app.post("/reserve/summarize", dependencies=protected)
    def reserve(payload: dict[str, Any]) -> dict[str, Any]:
        def run() -> dict[str, Any]:
            parameters = dict(payload.get("parameters") or {})
            floor = float(payload.get("floor", parameters.get("floor")))
            ceiling = float(payload.get("ceiling", parameters.get("ceiling")))
            baseline_points = int(payload.get("baseline_points", parameters.get("baseline_points", 3)))
            normalize = bool(payload.get("normalize", parameters.get("normalize", True)))
            return summarize_reserve_table(
                require_rows(payload),
                floor=floor,
                ceiling=ceiling,
                baseline_points=baseline_points,
                normalize=normalize,
            )

        return call(run)

    @app.post("/models/compare", dependencies=protected)
    def models(payload: dict[str, Any]) -> dict[str, Any]:
        def run() -> dict[str, Any]:
            parameters = dict(payload.get("parameters") or {})
            parameter_count = int(payload.get("parameter_count", parameters.get("parameter_count", 1)))
            return compare_endpoint_models(require_rows(payload), parameter_count=parameter_count)

        return call(run)

    @app.post("/reports/markdown", dependencies=protected)
    def report(payload: dict[str, Any]) -> dict[str, Any]:
        def run() -> dict[str, Any]:
            title = str(payload.get("title", payload.get("parameters", {}).get("title", "RhoDyn report")))
            return export_markdown_report(title, require_rows(payload))

        return call(run)

    @app.post("/jobs/run", dependencies=protected)
    def job_run(payload: dict[str, Any]) -> dict[str, Any]:
        def run() -> dict[str, Any]:
            operation = str(payload.get("operation", ""))
            parameters = dict(payload.get("parameters") or {})
            return run_backend_operation(operation, require_rows(payload), parameters=parameters)

        return call(run)

    @app.post("/jobs/bundle", dependencies=protected)
    def job_bundle(payload: dict[str, Any]) -> Any:
        try:
            operation = str(payload.get("operation", ""))
            parameters = dict(payload.get("parameters") or {})
            bundle = build_analysis_bundle(operation, require_rows(payload), parameters=parameters)
        except ServiceLimitError as exc:
            return JSONResponse({"status": "fail", "error": str(exc)}, status_code=413)
        except Exception as exc:
            return JSONResponse({"status": "fail", "error": str(exc)}, status_code=400)
        headers = {
            "Content-Disposition": f'attachment; filename="{bundle.filename}"',
            "X-RhoDyn-Bundle-SHA256": bundle.sha256,
        }
        return StreamingResponse(BytesIO(bundle.data), media_type=bundle.content_type, headers=headers)

    @app.post("/jobs/upload/run", dependencies=protected)
    async def job_upload_run(request: Request, operation: str, parameters_json: str = "") -> Any:
        try:
            rows = await read_upload_rows(request)
            parameters = _parameters_from_json(parameters_json)
        except ServiceLimitError as exc:
            return JSONResponse({"status": "fail", "error": str(exc)}, status_code=413)
        except Exception as exc:
            return JSONResponse({"status": "fail", "error": str(exc)}, status_code=400)

        return call(lambda: run_backend_operation(operation, rows, parameters=parameters))

    @app.post("/jobs/upload/bundle", dependencies=protected)
    async def job_upload_bundle(request: Request, operation: str, parameters_json: str = "") -> Any:
        try:
            rows = await read_upload_rows(request)
            parameters = _parameters_from_json(parameters_json)
            bundle = build_analysis_bundle(operation, rows, parameters=parameters)
        except ServiceLimitError as exc:
            return JSONResponse({"status": "fail", "error": str(exc)}, status_code=413)
        except Exception as exc:
            return JSONResponse({"status": "fail", "error": str(exc)}, status_code=400)
        headers = {
            "Content-Disposition": f'attachment; filename="{bundle.filename}"',
            "X-RhoDyn-Bundle-SHA256": bundle.sha256,
        }
        return StreamingResponse(BytesIO(bundle.data), media_type=bundle.content_type, headers=headers)

    def require_job_store() -> FileJobStore:
        if job_store is None:
            raise RuntimeError("durable job storage requires RHODYN_JOB_STORE_DIR or create_app(job_store_dir=...)")
        return job_store

    @app.post("/jobs/submit", dependencies=protected)
    def job_submit(payload: dict[str, Any]) -> Any:
        try:
            operation = str(payload.get("operation", ""))
            parameters = dict(payload.get("parameters") or {})
            stored = require_job_store().submit(operation, require_rows(payload), parameters=parameters)
            return {
                "status": "pass",
                "stored_job": stored.metadata,
                "result": to_plain(stored.result),
            }
        except RuntimeError as exc:
            return JSONResponse({"status": "fail", "error": str(exc)}, status_code=503)
        except ServiceLimitError as exc:
            return JSONResponse({"status": "fail", "error": str(exc)}, status_code=413)
        except Exception as exc:
            return JSONResponse({"status": "fail", "error": str(exc)}, status_code=400)

    @app.post("/jobs/upload/submit", dependencies=protected)
    async def job_upload_submit(request: Request, operation: str, parameters_json: str = "") -> Any:
        try:
            rows = await read_upload_rows(request)
            parameters = _parameters_from_json(parameters_json)
            stored = require_job_store().submit(operation, rows, parameters=parameters)
            return {
                "status": "pass",
                "stored_job": stored.metadata,
                "result": to_plain(stored.result),
            }
        except RuntimeError as exc:
            return JSONResponse({"status": "fail", "error": str(exc)}, status_code=503)
        except ServiceLimitError as exc:
            return JSONResponse({"status": "fail", "error": str(exc)}, status_code=413)
        except Exception as exc:
            return JSONResponse({"status": "fail", "error": str(exc)}, status_code=400)

    @app.get("/jobs", dependencies=protected)
    def job_list() -> Any:
        try:
            return {"status": "pass", "jobs": require_job_store().list_jobs()}
        except RuntimeError as exc:
            return JSONResponse({"status": "fail", "error": str(exc)}, status_code=503)

    @app.get("/jobs/summary", dependencies=protected)
    def job_summary() -> Any:
        try:
            return {"status": "pass", "summary": require_job_store().storage_summary()}
        except RuntimeError as exc:
            return JSONResponse({"status": "fail", "error": str(exc)}, status_code=503)

    @app.post("/jobs/prune", dependencies=protected)
    def job_prune(payload: dict[str, Any] | None = None) -> Any:
        try:
            body = dict(payload or {})
            dry_run = bool(body.get("dry_run", False))
            return {"status": "pass", "prune": require_job_store().prune(dry_run=dry_run)}
        except RuntimeError as exc:
            return JSONResponse({"status": "fail", "error": str(exc)}, status_code=503)

    @app.get("/jobs/{job_id}", dependencies=protected)
    def job_metadata(job_id: str) -> Any:
        try:
            return {"status": "pass", "stored_job": require_job_store().get_metadata(job_id)}
        except RuntimeError as exc:
            return JSONResponse({"status": "fail", "error": str(exc)}, status_code=503)
        except (KeyError, ValueError) as exc:
            return JSONResponse({"status": "fail", "error": str(exc)}, status_code=404)

    @app.get("/jobs/{job_id}/result", dependencies=protected)
    def job_result(job_id: str) -> Any:
        try:
            return {"status": "pass", "result": require_job_store().get_result(job_id)}
        except RuntimeError as exc:
            return JSONResponse({"status": "fail", "error": str(exc)}, status_code=503)
        except (KeyError, ValueError) as exc:
            return JSONResponse({"status": "fail", "error": str(exc)}, status_code=404)

    @app.get("/jobs/{job_id}/bundle", dependencies=protected)
    def job_stored_bundle(job_id: str) -> Any:
        try:
            metadata, data = require_job_store().read_bundle(job_id)
        except RuntimeError as exc:
            return JSONResponse({"status": "fail", "error": str(exc)}, status_code=503)
        except (KeyError, ValueError) as exc:
            return JSONResponse({"status": "fail", "error": str(exc)}, status_code=404)
        headers = {
            "Content-Disposition": f'attachment; filename="{metadata["bundle_filename"]}"',
            "X-RhoDyn-Bundle-SHA256": metadata["bundle_sha256"],
        }
        return StreamingResponse(BytesIO(data), media_type="application/zip", headers=headers)

    return app


app = create_app()

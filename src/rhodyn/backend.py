"""FastAPI application factory for the RhoDyn backend."""

from __future__ import annotations

import os
from io import BytesIO
from pathlib import Path
from typing import Any, Callable

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


def _require_rows(payload: dict[str, Any]) -> list[dict[str, Any]]:
    rows = payload.get("rows")
    if not isinstance(rows, list):
        raise ValueError("payload must include rows as a list")
    return rows


def _call(func: Callable[[], dict[str, Any]]) -> dict[str, Any]:
    try:
        return to_plain(func())
    except Exception as exc:
        return {"status": "fail", "error": str(exc)}


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


def create_app(
    job_store_dir: str | Path | None = None,
    *,
    retention_policy: JobRetentionPolicy | None = None,
) -> Any:
    """Create the FastAPI app.

    FastAPI is optional so importing :mod:`rhodyn.backend` does not add runtime
    dependencies to the core library. Install ``rhodyn[backend]`` to run this
    application.
    """

    try:
        from fastapi import FastAPI
        from fastapi.responses import JSONResponse, StreamingResponse
    except ImportError as exc:  # pragma: no cover - exercised only without optional extra
        raise RuntimeError("FastAPI backend requires installing rhodyn[backend]") from exc

    store_dir = job_store_dir if job_store_dir is not None else os.environ.get("RHODYN_JOB_STORE_DIR")
    policy = retention_policy if retention_policy is not None else _retention_from_env()
    job_store = FileJobStore(store_dir, retention_policy=policy) if store_dir else None

    app = FastAPI(
        title="RhoDyn backend",
        version=software_version(),
        description="API around RhoDyn dynamic-state analysis helpers with optional durable job storage.",
    )

    @app.get("/health")
    def health() -> dict[str, Any]:
        return {
            "status": "pass",
            "software_version": software_version(),
            "durable_job_storage": bool(job_store),
            "retention_policy": policy.as_dict() if policy else None,
        }

    @app.get("/schemas")
    def schemas() -> dict[str, Any]:
        return to_plain({"status": "pass", "schemas": schema_specs()})

    @app.post("/schemas/validate")
    def validate(payload: dict[str, Any]) -> dict[str, Any]:
        def run() -> dict[str, Any]:
            kind = str(payload.get("kind", "trajectory"))
            signal_column = str(
                payload.get("signal_column", payload.get("parameters", {}).get("signal_column", "signal"))
            )
            return validate_table(kind, _require_rows(payload), signal_column=signal_column)

        return _call(run)

    @app.post("/residence/score")
    def residence(payload: dict[str, Any]) -> dict[str, Any]:
        def run() -> dict[str, Any]:
            parameters = dict(payload.get("parameters") or {})
            low = float(payload.get("low", parameters.get("low")))
            high = float(payload.get("high", parameters.get("high")))
            signal_column = str(payload.get("signal_column", parameters.get("signal_column", "signal")))
            return score_residence_table(_require_rows(payload), low=low, high=high, signal_column=signal_column)

        return _call(run)

    @app.post("/coupling/decide")
    def coupling(payload: dict[str, Any]) -> dict[str, Any]:
        def run() -> dict[str, Any]:
            parameters = dict(payload.get("parameters") or {})
            rope_threshold = float(payload.get("rope_threshold", parameters.get("rope_threshold", 0.95)))
            return decide_coupling_table(_require_rows(payload), rope_threshold=rope_threshold)

        return _call(run)

    @app.post("/reserve/summarize")
    def reserve(payload: dict[str, Any]) -> dict[str, Any]:
        def run() -> dict[str, Any]:
            parameters = dict(payload.get("parameters") or {})
            floor = float(payload.get("floor", parameters.get("floor")))
            ceiling = float(payload.get("ceiling", parameters.get("ceiling")))
            baseline_points = int(payload.get("baseline_points", parameters.get("baseline_points", 3)))
            normalize = bool(payload.get("normalize", parameters.get("normalize", True)))
            return summarize_reserve_table(
                _require_rows(payload),
                floor=floor,
                ceiling=ceiling,
                baseline_points=baseline_points,
                normalize=normalize,
            )

        return _call(run)

    @app.post("/models/compare")
    def models(payload: dict[str, Any]) -> dict[str, Any]:
        def run() -> dict[str, Any]:
            parameters = dict(payload.get("parameters") or {})
            parameter_count = int(payload.get("parameter_count", parameters.get("parameter_count", 1)))
            return compare_endpoint_models(_require_rows(payload), parameter_count=parameter_count)

        return _call(run)

    @app.post("/reports/markdown")
    def report(payload: dict[str, Any]) -> dict[str, Any]:
        def run() -> dict[str, Any]:
            title = str(payload.get("title", payload.get("parameters", {}).get("title", "RhoDyn report")))
            return export_markdown_report(title, _require_rows(payload))

        return _call(run)

    @app.post("/jobs/run")
    def job_run(payload: dict[str, Any]) -> dict[str, Any]:
        def run() -> dict[str, Any]:
            operation = str(payload.get("operation", ""))
            parameters = dict(payload.get("parameters") or {})
            return run_backend_operation(operation, _require_rows(payload), parameters=parameters)

        return _call(run)

    @app.post("/jobs/bundle")
    def job_bundle(payload: dict[str, Any]) -> Any:
        try:
            operation = str(payload.get("operation", ""))
            parameters = dict(payload.get("parameters") or {})
            bundle = build_analysis_bundle(operation, _require_rows(payload), parameters=parameters)
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

    @app.post("/jobs/submit")
    def job_submit(payload: dict[str, Any]) -> Any:
        try:
            operation = str(payload.get("operation", ""))
            parameters = dict(payload.get("parameters") or {})
            stored = require_job_store().submit(operation, _require_rows(payload), parameters=parameters)
            return {
                "status": "pass",
                "stored_job": stored.metadata,
                "result": to_plain(stored.result),
            }
        except RuntimeError as exc:
            return JSONResponse({"status": "fail", "error": str(exc)}, status_code=503)
        except Exception as exc:
            return JSONResponse({"status": "fail", "error": str(exc)}, status_code=400)

    @app.get("/jobs")
    def job_list() -> Any:
        try:
            return {"status": "pass", "jobs": require_job_store().list_jobs()}
        except RuntimeError as exc:
            return JSONResponse({"status": "fail", "error": str(exc)}, status_code=503)

    @app.get("/jobs/summary")
    def job_summary() -> Any:
        try:
            return {"status": "pass", "summary": require_job_store().storage_summary()}
        except RuntimeError as exc:
            return JSONResponse({"status": "fail", "error": str(exc)}, status_code=503)

    @app.post("/jobs/prune")
    def job_prune(payload: dict[str, Any] | None = None) -> Any:
        try:
            body = dict(payload or {})
            dry_run = bool(body.get("dry_run", False))
            return {"status": "pass", "prune": require_job_store().prune(dry_run=dry_run)}
        except RuntimeError as exc:
            return JSONResponse({"status": "fail", "error": str(exc)}, status_code=503)

    @app.get("/jobs/{job_id}")
    def job_metadata(job_id: str) -> Any:
        try:
            return {"status": "pass", "stored_job": require_job_store().get_metadata(job_id)}
        except RuntimeError as exc:
            return JSONResponse({"status": "fail", "error": str(exc)}, status_code=503)
        except (KeyError, ValueError) as exc:
            return JSONResponse({"status": "fail", "error": str(exc)}, status_code=404)

    @app.get("/jobs/{job_id}/result")
    def job_result(job_id: str) -> Any:
        try:
            return {"status": "pass", "result": require_job_store().get_result(job_id)}
        except RuntimeError as exc:
            return JSONResponse({"status": "fail", "error": str(exc)}, status_code=503)
        except (KeyError, ValueError) as exc:
            return JSONResponse({"status": "fail", "error": str(exc)}, status_code=404)

    @app.get("/jobs/{job_id}/bundle")
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

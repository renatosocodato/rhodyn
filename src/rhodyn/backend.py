"""FastAPI application factory for the RhoDyn backend."""

from __future__ import annotations

from typing import Any, Callable

from rhodyn.backend_core import (
    compare_endpoint_models,
    decide_coupling_table,
    export_markdown_report,
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


def create_app() -> Any:
    """Create the FastAPI app.

    FastAPI is optional so importing :mod:`rhodyn.backend` does not add runtime
    dependencies to the core library. Install ``rhodyn[backend]`` to run this
    application.
    """

    try:
        from fastapi import FastAPI
    except ImportError as exc:  # pragma: no cover - exercised only without optional extra
        raise RuntimeError("FastAPI backend requires installing rhodyn[backend]") from exc

    app = FastAPI(
        title="RhoDyn backend",
        version=software_version(),
        description="Stateless API around RhoDyn dynamic-state analysis helpers.",
    )

    @app.get("/health")
    def health() -> dict[str, Any]:
        return {"status": "pass", "software_version": software_version()}

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

    return app


app = create_app()

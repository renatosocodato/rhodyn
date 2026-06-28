"""Audit Stage 5 upload-flow parity across frontend contract, backend core, and CLI.

The audit uses the frozen Stage 4 frontend contract and committed example CSVs.
It verifies that every Stage 5 operation has a command-line counterpart, a
backend-core result, and a frozen upload fixture with the same scientific result
after transport-only metadata are removed.
"""

from __future__ import annotations

import csv
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from rhodyn.backend_core import run_backend_operation
from rhodyn.report import to_plain


REPORT_FORMAT = "rhodyn.stage5_upload_flow_parity_audit.v1"
EXPECTED_OPERATIONS = {
    "validate_trajectory",
    "score_residence",
    "decide_coupling",
    "summarize_reserve",
    "compare_models",
    "export_markdown",
}


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _cli_command(operation: dict[str, Any], csv_path: Path) -> list[str]:
    params = dict(operation.get("parameters") or {})
    op_id = operation["operation_id"]
    if op_id == "validate_trajectory":
        return [
            sys.executable,
            "-m",
            "rhodyn.cli",
            "validate",
            str(csv_path),
            "--kind",
            str(params.get("kind", operation.get("table_kind", "trajectory"))),
            "--signal-column",
            str(params.get("signal_column", "signal")),
        ]
    if op_id == "score_residence":
        return [
            sys.executable,
            "-m",
            "rhodyn.cli",
            "score-residence",
            str(csv_path),
            "--low",
            str(params["low"]),
            "--high",
            str(params["high"]),
            "--signal-column",
            str(params.get("signal_column", "signal")),
        ]
    if op_id == "decide_coupling":
        return [
            sys.executable,
            "-m",
            "rhodyn.cli",
            "decide-coupling",
            str(csv_path),
            "--rope-threshold",
            str(params.get("rope_threshold", 0.95)),
        ]
    if op_id == "summarize_reserve":
        command = [
            sys.executable,
            "-m",
            "rhodyn.cli",
            "summarize-reserve",
            str(csv_path),
            "--floor",
            str(params["floor"]),
            "--ceiling",
            str(params["ceiling"]),
            "--baseline-points",
            str(params.get("baseline_points", 3)),
        ]
        command.append("--normalize" if params.get("normalize", True) else "--no-normalize")
        return command
    if op_id == "compare_models":
        return [
            sys.executable,
            "-m",
            "rhodyn.cli",
            "compare",
            str(csv_path),
            "--parameters",
            str(params.get("parameter_count", 1)),
        ]
    if op_id == "export_markdown":
        return [
            sys.executable,
            "-m",
            "rhodyn.cli",
            "export-markdown",
            str(csv_path),
            "--title",
            str(params.get("title", "RhoDyn report")),
        ]
    raise ValueError(f"no CLI parity command declared for {op_id}")


def _strip_transport(value: Any) -> Any:
    plain = to_plain(value)
    if isinstance(plain, dict):
        result: dict[str, Any] = {}
        for key, item in plain.items():
            if key == "job":
                continue
            if key == "source":
                result[key] = "<source>"
            else:
                result[key] = _strip_transport(item)
        return result
    if isinstance(plain, list):
        return [_strip_transport(item) for item in plain]
    return plain


def _run_cli(command: list[str]) -> dict[str, Any]:
    env = dict(os.environ)
    env["PYTHONPATH"] = str(SRC) + (os.pathsep + env["PYTHONPATH"] if env.get("PYTHONPATH") else "")
    result = subprocess.run(
        command,
        cwd=ROOT,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )
    return json.loads(result.stdout)


def _run_live_upload(operation: dict[str, Any], csv_path: Path) -> dict[str, Any] | None:
    try:
        from fastapi.testclient import TestClient  # type: ignore

        from rhodyn.backend import create_app
    except Exception:
        return None

    client = TestClient(create_app())
    response = client.post(
        operation["endpoint"],
        params={
            "operation": operation["upload_operation"],
            "parameters_json": json.dumps(operation.get("parameters") or {}),
        },
        content=csv_path.read_bytes(),
        headers={"content-type": "text/csv"},
    )
    return {"status_code": response.status_code, "body": response.json()}


def _operation_case(operation: dict[str, Any]) -> dict[str, Any]:
    csv_path = ROOT / operation["example_csv"]
    rows = _read_rows(csv_path)
    parameters = dict(operation.get("parameters") or {})
    backend = run_backend_operation(operation["upload_operation"], rows, parameters=parameters)
    fixture_path = ROOT / "api" / "stage4" / "fixtures" / f"{operation['operation_id']}_upload_run.response.json"
    fixture = _load_json(fixture_path)["body"]
    command = _cli_command(operation, csv_path)
    cli = _run_cli(command)
    live_upload = _run_live_upload(operation, csv_path)

    normalized_backend = _strip_transport(backend)
    normalized_fixture = _strip_transport(fixture)
    normalized_cli = _strip_transport(cli)
    normalized_live = None if live_upload is None else _strip_transport(live_upload["body"])
    live_matches = None if normalized_live is None else live_upload["status_code"] == 200 and normalized_live == normalized_backend
    mismatch_summary = {
        "cli_backend_equal": normalized_cli == normalized_backend,
        "fixture_backend_equal": normalized_fixture == normalized_backend,
        "live_backend_equal": live_matches,
        "cli_keys": sorted(normalized_cli) if isinstance(normalized_cli, dict) else [],
        "backend_keys": sorted(normalized_backend) if isinstance(normalized_backend, dict) else [],
        "fixture_keys": sorted(normalized_fixture) if isinstance(normalized_fixture, dict) else [],
    }
    return {
        "operation_id": operation["operation_id"],
        "upload_operation": operation["upload_operation"],
        "table_kind": operation["table_kind"],
        "example_csv": operation["example_csv"],
        "row_count": len(rows),
        "parameter_keys": sorted(parameters),
        "frontend_run_endpoint": operation["endpoint"],
        "frontend_submit_endpoint": operation["submit_endpoint"],
        "frontend_bundle_endpoint": operation["bundle_endpoint"],
        "cli_command": command[2:],
        "cli_matches_backend_core": normalized_cli == normalized_backend,
        "fixture_matches_backend_core": normalized_fixture == normalized_backend,
        "live_upload_route_checked": live_matches is not None,
        "live_upload_route_matches_backend_core": live_matches,
        "mismatch_summary": mismatch_summary,
        "status": "pass" if normalized_cli == normalized_backend and normalized_fixture == normalized_backend and live_matches is not False else "fail",
    }


def audit_stage5_upload_flow_parity(root: Path = ROOT) -> dict[str, Any]:
    contract = _load_json(root / "api" / "stage4" / "frontend_contract.json")
    app_js = (root / "frontend" / "stage5" / "app.js").read_text(encoding="utf-8")
    index = (root / "frontend" / "stage5" / "index.html").read_text(encoding="utf-8")
    operations = contract.get("operations", [])
    cases = [_operation_case(operation) for operation in operations]
    operation_ids = {case["operation_id"] for case in cases}
    checks = {
        "all_expected_operations_present": EXPECTED_OPERATIONS <= operation_ids,
        "every_operation_has_example_rows": all(case["row_count"] > 0 for case in cases),
        "every_operation_cli_matches_backend_core": all(case["cli_matches_backend_core"] for case in cases),
        "every_frozen_upload_fixture_matches_backend_core": all(case["fixture_matches_backend_core"] for case in cases),
        "live_fastapi_upload_routes_match_backend_core_if_available": all(case["live_upload_route_matches_backend_core"] is not False for case in cases),
        "frontend_loads_schema_fixture": "SCHEMA_FIXTURE_URL" in app_js and "schemas.response.json" in app_js,
        "frontend_exposes_parameter_payload": "parameterPayload" in index and "renderParameterPayload" in app_js,
        "frontend_exposes_route_preview": "routePanel" in index and "routeUrl" in app_js,
        "frontend_exposes_local_validation": "validationState" in index and "localValidationIssues" in app_js,
        "frontend_exposes_example_upload_loader": "sampleButton" in index and "loadExampleCsv" in app_js,
    }
    failures = [name for name, passed in checks.items() if not passed]
    failures.extend(case["operation_id"] for case in cases if case["status"] != "pass")
    return {
        "report_format": REPORT_FORMAT,
        "status": "pass" if not failures else "fail",
        "failures": failures,
        "warnings": [],
        "checks": checks,
        "operation_count": len(cases),
        "live_fastapi_upload_routes_checked": all(case["live_upload_route_checked"] for case in cases),
        "operations": cases,
        "interpretation_boundary": "This audit proves transport parity for retained example tables. It does not add new biological data or change RhoDyn analysis logic.",
    }


def main() -> int:
    payload = audit_stage5_upload_flow_parity()
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())

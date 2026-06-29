"""Audit the Stage 4 contract freeze and Stage 5 frontend scaffold.

This check is dependency-free. It verifies that the committed frontend scaffold
is bound to the frozen Stage 4 API contract and that the scaffold does not add
new biological systems or algorithmic routes outside that contract.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
REPORT_FORMAT = "rhodyn.stage5_frontend_scaffold_audit.v1"
EXPECTED_PATHS = {
    "/health",
    "/schemas",
    "/schemas/validate",
    "/residence/score",
    "/coupling/decide",
    "/reserve/summarize",
    "/models/compare",
    "/reports/markdown",
    "/jobs/run",
    "/jobs/bundle",
    "/jobs/upload/run",
    "/jobs/upload/bundle",
    "/jobs/submit",
    "/jobs/upload/submit",
    "/jobs",
    "/jobs/summary",
    "/jobs/prune",
    "/jobs/{job_id}",
    "/jobs/{job_id}/result",
    "/jobs/{job_id}/bundle",
}
EXPECTED_SCREENS = {
    "Project dashboard",
    "Data upload and schema validation",
    "Trajectory explorer",
    "Residence-window tuner",
    "Coupling/equivalence decision panel",
    "Reserve-buffering panel",
    "Model-comparison panel",
    "Report builder",
}
EXPECTED_OPERATIONS = {
    "validate_trajectory",
    "score_residence",
    "decide_coupling",
    "summarize_reserve",
    "compare_models",
    "export_markdown",
}
REQUIRED_FILES = [
    "api/stage4/openapi.json",
    "api/stage4/frontend_contract.json",
    "api/stage4/contract_manifest.json",
    "frontend/stage5/index.html",
    "frontend/stage5/styles.css",
    "frontend/stage5/app.js",
    "docs/stage4_closeout.md",
    "docs/stage5_frontend.md",
    "docs/stage5_closeout.md",
    "docs/stage5_public_mlci_workflow.md",
    "examples/mlci_public_intensity_trajectory.csv",
]


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def audit_stage5_frontend_scaffold(root: Path = ROOT) -> dict[str, Any]:
    failures: list[str] = []
    warnings: list[str] = []
    checks: dict[str, bool] = {}

    for rel in REQUIRED_FILES:
        exists = (root / rel).exists()
        checks[f"required_file::{rel}"] = exists
        if not exists:
            failures.append(f"missing required file: {rel}")
    if failures:
        return {"report_format": REPORT_FORMAT, "status": "fail", "failures": failures, "warnings": warnings, "checks": checks}

    openapi = _load_json(root / "api/stage4/openapi.json")
    contract = _load_json(root / "api/stage4/frontend_contract.json")
    manifest = _load_json(root / "api/stage4/contract_manifest.json")
    index = (root / "frontend/stage5/index.html").read_text(encoding="utf-8")
    app_js = (root / "frontend/stage5/app.js").read_text(encoding="utf-8")
    stage5_doc = (root / "docs/stage5_frontend.md").read_text(encoding="utf-8")
    stage5_closeout_doc = (root / "docs/stage5_closeout.md").read_text(encoding="utf-8")
    closeout_doc = (root / "docs/stage4_closeout.md").read_text(encoding="utf-8")

    paths = set(openapi.get("paths", {}))
    operations = {item.get("operation_id") for item in contract.get("operations", [])}
    screens = set(contract.get("screens", []))

    checks["openapi_contains_expected_paths"] = EXPECTED_PATHS <= paths
    checks["frontend_contract_has_expected_operations"] = EXPECTED_OPERATIONS <= operations
    checks["frontend_contract_has_expected_screens"] = EXPECTED_SCREENS <= screens
    checks["manifest_hashes_match_contract_files"] = (
        manifest.get("openapi_sha256") == _sha256(root / "api/stage4/openapi.json")
        and manifest.get("frontend_contract_sha256") == _sha256(root / "api/stage4/frontend_contract.json")
    )
    checks["manifest_allows_stage5_handoff"] = manifest.get("stage5_handoff", {}).get("allowed") is True
    checks["frontend_loads_frozen_contract"] = "../../api/stage4/frontend_contract.json" in app_js and "../../api/stage4/openapi.json" in app_js
    checks["frontend_loads_frozen_schema_fixture"] = "SCHEMA_FIXTURE_URL" in app_js and "schemas.response.json" in app_js
    checks["frontend_uses_contract_upload_bundle_submit_routes"] = all(
        token in app_js for token in ["operation.endpoint", "operation.bundle_endpoint", "operation.submit_endpoint"]
    )
    checks["frontend_exposes_required_screens"] = all(screen in index for screen in EXPECTED_SCREENS)
    checks["frontend_exposes_parameter_inspection"] = all(token in index for token in ["operationMeta", "schemaPanel", "parameterPayload", "routePanel", "validationState", "sampleButton"])
    checks["frontend_exposes_richer_trajectory_inspection"] = all(
        token in index + app_js
        for token in ["trajectoryStats", "traceSummaryTable", "trajectoryInspection", "residenceForPoints"]
    )
    checks["frontend_exposes_result_visualization"] = all(
        token in index + app_js
        for token in ["resultVisual", "renderResultVisual", "comparisonSuite", "rankedBarRows", "couplingIntervalPlot"]
    )
    checks["frontend_exposes_operation_specific_comparison_suites"] = all(
        token in app_js
        for token in [
            "renderResidenceComparison",
            "renderCouplingComparison",
            "renderReserveComparison",
            "renderModelComparison",
            "Delta BIC",
            "Zero coupling",
        ]
    )
    checks["frontend_styles_professional_comparison_panels"] = all(
        token in (root / "frontend/stage5/styles.css").read_text(encoding="utf-8")
        for token in ["comparison-suite", "metric-strip", "metric-card", "ranked-bars", "margin-axis", "status-chip"]
    )
    checks["frontend_exposes_report_export_controls"] = all(
        token in index + app_js
        for token in ["downloadJsonButton", "downloadCsvButton", "downloadMarkdownButton", "copyJsonButton", "resultMarkdown"]
    )
    checks["frontend_exposes_public_mlci_workflow"] = all(
        token in index + app_js
        for token in ["publicWorkflowButton", "PUBLIC_WORKFLOW", "mlci_public_intensity_trajectory.csv", "Zenodo 7260137"]
    )
    checks["frontend_not_marketing_hero"] = "hero" not in index.lower() and "hero" not in (root / "frontend/stage5/styles.css").read_text(encoding="utf-8").lower()
    checks["frontend_uses_local_upload_preflight"] = "localValidationIssues" in app_js and "Load a CSV table" in app_js
    checks["docs_state_stage4_frozen"] = "Stage 4 API contract is frozen" in closeout_doc
    checks["docs_state_stage5_contract_bound"] = "Stage 5 scaffold is contract-bound" in stage5_doc
    checks["docs_state_stage5_completed"] = (
        "Stage 5 status. Completed." in stage5_closeout_doc
        and "Stage 6 handoff. Active." in stage5_closeout_doc
        and "No blocking Stage 5 technical debt remains." in stage5_closeout_doc
    )
    checks["boundary_no_new_biology"] = all(
        phrase in text
        for phrase, text in [
            ("does not add a biological case study", json.dumps(manifest)),
            ("does not add new biological systems", json.dumps(contract)),
            ("does not add new biological systems", stage5_doc),
        ]
    )

    for operation in contract.get("operations", []):
        endpoint = operation.get("endpoint")
        bundle = operation.get("bundle_endpoint")
        submit = operation.get("submit_endpoint")
        if endpoint not in paths or bundle not in paths or submit not in paths:
            failures.append(f"operation {operation.get('operation_id')} references endpoint absent from OpenAPI")
    missing_fixture_ops = []
    for operation_id in EXPECTED_OPERATIONS:
        if not (root / "api/stage4/fixtures" / f"{operation_id}.request.csv").exists():
            missing_fixture_ops.append(operation_id)
        if not (root / "api/stage4/fixtures" / f"{operation_id}_upload_run.response.json").exists():
            missing_fixture_ops.append(operation_id)
    checks["operation_upload_fixtures_present"] = not missing_fixture_ops
    if missing_fixture_ops:
        failures.append(f"missing operation upload fixtures: {sorted(set(missing_fixture_ops))}")

    for name, passed in checks.items():
        if not passed:
            failures.append(name)

    return {
        "report_format": REPORT_FORMAT,
        "status": "pass" if not failures else "fail",
        "failures": failures,
        "warnings": warnings,
        "checks": checks,
        "openapi_path_count": len(paths),
        "operation_count": len(operations),
        "screen_count": len(screens),
        "interpretation_boundary": "The scaffold is a UI and contract surface only. It does not change RhoDyn analysis outputs or add biological interpretation.",
    }


def main() -> int:
    payload = audit_stage5_frontend_scaffold()
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())

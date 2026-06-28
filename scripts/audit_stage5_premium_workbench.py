"""Audit Stage 5 browser regression and premium workbench hardening.

This check is intentionally static and dependency-light. The Playwright suite
does the browser work; this audit makes sure the regression harness, CI wiring,
and comparison-panel safety coverage remain present in normal release checks.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
REPORT_FORMAT = "rhodyn.stage5_premium_workbench_audit.v1"
REQUIRED_FILES = [
    "package.json",
    "package-lock.json",
    "playwright.config.mjs",
    "tests/playwright/stage5.visual.spec.mjs",
]
REQUIRED_OPERATIONS = ["score_residence", "decide_coupling", "summarize_reserve", "compare_models"]
REQUIRED_VISUAL_TOKENS = [
    "comparisonSuite",
    "rankedBarRows",
    "couplingIntervalPlot",
    "renderResidenceComparison",
    "renderCouplingComparison",
    "renderReserveComparison",
    "renderModelComparison",
]
REQUIRED_CSS_TOKENS = [
    "comparison-suite",
    "metric-strip",
    "comparison-plot",
    "comparison-table",
    "status-chip",
    "margin-axis",
]
REQUIRED_SPEC_TOKENS = [
    "toHaveScreenshot",
    "mockStage4Api",
    "adversarial coupling",
    "expectNoDocumentOverflow",
    "not claimed",
    "does not identify every molecular edge",
]
SNAPSHOT_CASES = [
    "stage5-adversarial-coupling",
    "stage5-coupling-comparison",
    "stage5-model-comparison",
    "stage5-public-trajectory-workflow",
    "stage5-reserve-comparison",
    "stage5-residence-comparison",
]
SNAPSHOT_PROJECTS = ["chromium-desktop", "chromium-mobile"]
SNAPSHOT_PLATFORMS = ["darwin", "linux"]


def _read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def audit_stage5_premium_workbench(root: Path = ROOT) -> dict[str, Any]:
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

    package = json.loads(_read("package.json"))
    lock = json.loads(_read("package-lock.json"))
    app_js = _read("frontend/stage5/app.js")
    css = _read("frontend/stage5/styles.css")
    spec = _read("tests/playwright/stage5.visual.spec.mjs")
    config = _read("playwright.config.mjs")
    workflow = _read(".github/workflows/tests.yml")
    snapshot_dir = root / "tests/playwright/stage5.visual.spec.mjs-snapshots"
    snapshot_names = sorted(path.name for path in snapshot_dir.glob("*.png"))

    scripts = package.get("scripts", {})
    dev_deps = package.get("devDependencies", {})
    checks["playwright_dev_dependency_pinned"] = dev_deps.get("@playwright/test") == "1.61.1"
    checks["package_lock_records_playwright"] = "node_modules/@playwright/test" in lock.get("packages", {})
    checks["stage5_browser_script_present"] = scripts.get("test:stage5") == "playwright test"
    checks["stage5_snapshot_update_script_present"] = "--update-snapshots" in scripts.get("test:stage5:update-screenshots", "")
    checks["playwright_uses_static_repo_server"] = "python3 -m http.server 9013" in config and "frontend/stage5" in config
    checks["playwright_has_desktop_and_mobile_projects"] = "chromium-desktop" in config and "chromium-mobile" in config
    expected_snapshots = {
        f"{case}-{project}-{platform}.png"
        for case in SNAPSHOT_CASES
        for project in SNAPSHOT_PROJECTS
        for platform in SNAPSHOT_PLATFORMS
    }
    checks["playwright_uses_platform_specific_snapshots"] = "snapshotPathTemplate" not in config
    checks["playwright_has_darwin_and_linux_baselines"] = expected_snapshots.issubset(set(snapshot_names))
    checks["playwright_has_expected_snapshot_count"] = len(snapshot_names) == len(expected_snapshots)
    checks["comparison_panel_functions_present"] = all(token in app_js for token in REQUIRED_VISUAL_TOKENS)
    checks["comparison_panel_css_present"] = all(token in css for token in REQUIRED_CSS_TOKENS)
    checks["spec_covers_all_core_comparison_operations"] = all(token in spec for token in REQUIRED_OPERATIONS)
    checks["spec_contains_visual_and_adversarial_guards"] = all(token in spec for token in REQUIRED_SPEC_TOKENS)
    checks["spec_mocks_frozen_stage4_contract_transport"] = "api/stage4/fixtures" in spec and (
        "jobs/upload/run" in spec or "jobs\\/upload\\/run" in spec
    )
    checks["ci_runs_stage5_browser_regression"] = all(
        token in workflow
        for token in ["setup-node", "npm ci", "npx playwright install --with-deps chromium", "npm run test:stage5"]
    )
    checks["ci_uploads_playwright_report_on_failure"] = "playwright-report" in workflow and "actions/upload-artifact" in workflow
    checks["stage5_no_new_backend_route"] = all(token not in app_js for token in ["/new", "/analysis", "/inference"])

    for name, passed in checks.items():
        if not passed:
            failures.append(name)

    return {
        "report_format": REPORT_FORMAT,
        "status": "pass" if not failures else "fail",
        "failures": failures,
        "warnings": warnings,
        "checks": checks,
        "interpretation_boundary": "Stage 5 browser regression hardens the workbench presentation only. It does not change backend analysis outputs or introduce new biological examples.",
    }


def main() -> int:
    payload = audit_stage5_premium_workbench()
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())

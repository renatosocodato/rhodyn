"""Audit the Stage 5.1 Simulation Workbench repair.

The workbench is a frontend mirror of the existing deterministic controller
simulation. It must not add backend routes or biological claims.
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from rhodyn.models import simulate_controller
REPORT_FORMAT = "rhodyn.stage5_simulation_workbench_audit.v1"


def _read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def audit_stage5_simulation_workbench(root: Path = ROOT) -> dict[str, Any]:
    failures: list[str] = []
    warnings: list[str] = []
    checks: dict[str, bool] = {}

    index = _read("frontend/stage5/index.html")
    app_js = _read("frontend/stage5/app.js")
    css = _read("frontend/stage5/styles.css")
    spec = _read("tests/playwright/stage5.visual.spec.mjs")
    stage5_doc = _read("docs/stage5_frontend.md")
    closeout = _read("docs/stage5_closeout.md")

    rows = simulate_controller(duration=20, dt=0.5)
    final = rows[-1]
    checks["python_reference_row_count"] = len(rows) == 41
    checks["python_reference_final_burden"] = math.isclose(final["burden"], 0.7990020641137685, rel_tol=0, abs_tol=1e-12)
    checks["index_exposes_simulation_screen"] = all(
        token in index for token in ["Simulation workbench", "simulationPreset", "simulationPlot", "simulationExportJsonButton"]
    )
    checks["frontend_mirrors_controller_terms"] = all(
        token in app_js
        for token in [
            "simulateControllerLocal",
            "windowGateLocal",
            "rhoa += params.dt * (params.rhoa_input - params.rhoa_decay * rhoa)",
            "src += params.dt * (params.src_drive * (1 - gate) - params.src_decay * src)",
            "reserve += params.dt * (params.reserve_recovery * gate - params.reserve_decay * src * reserve)",
            "myh10_route",
            "burden_first_passage",
        ]
    )
    checks["frontend_declares_no_backend_route"] = all(token not in app_js for token in ["/simulate", "/simulations", "/new", "/analysis", "/inference"])
    checks["frontend_exposes_export_and_cli_parity"] = all(
        token in app_js + index for token in ["rhodyn simulate", "Export JSON", "Export CSV", "Export Markdown"]
    )
    checks["css_styles_simulation_surface"] = all(
        token in css for token in ["simulation-layout", "simulation-plot-surface", "sim-trace", "sim-threshold"]
    )
    checks["playwright_checks_simulation_parity"] = all(
        token in spec for token in ["simulation workbench mirrors", "0.7990020641", "stage5-simulation-workbench.png"]
    )
    checks["docs_record_simulation_repair"] = all(
        token in stage5_doc + closeout for token in ["Simulation Workbench", "deterministic controller", "not a new backend route"]
    )

    for name, passed in checks.items():
        if not passed:
            failures.append(name)

    return {
        "report_format": REPORT_FORMAT,
        "status": "pass" if not failures else "fail",
        "failures": failures,
        "warnings": warnings,
        "checks": checks,
        "reference_final_burden": final["burden"],
        "interpretation_boundary": "The Simulation Workbench mirrors the deterministic controller for parameter exploration. It does not fit data, add a backend route, or introduce a biological claim.",
    }


def main() -> int:
    payload = audit_stage5_simulation_workbench()
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())

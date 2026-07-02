"""Preflight harness for Stage 9.6b PanelForge figure rendering.

This script is intentionally non-executing by default. It records the checks
that must pass before the future Stage 9.6b rendering substage is allowed to
clone PanelForge, create `.venv-panelforge`, validate a real manifest, or render
figures. It exists so the roadmap has executable guardrails before the roadmap
itself is run.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT / "manuscript" / "nature_methods"
FIGURE_LEDGER = WORKSPACE / "ledgers" / "figure_to_claim_to_artifact.csv"
FIGURE_MANIFEST = WORKSPACE / "figures" / "figures.manifest.yaml"
STAGE96_GATE = WORKSPACE / "gate_verdicts" / "9.6.json"
PANELFORGE_PLACEHOLDER = ROOT / "tools" / "panelforge-figures" / "STAGE9_PLACEHOLDER.md"


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def preflight(root: Path = ROOT) -> dict[str, object]:
    workspace = root / WORKSPACE.relative_to(ROOT)
    binding = _read_json(workspace / "contracts" / "stage9_project_binding.json")
    figure_engine = binding.get("figure_engine_binding", {}) if isinstance(binding.get("figure_engine_binding"), dict) else {}
    gate96 = _read_json(root / STAGE96_GATE.relative_to(ROOT))
    manifest = root / FIGURE_MANIFEST.relative_to(ROOT)
    placeholder = root / PANELFORGE_PLACEHOLDER.relative_to(ROOT)
    ledger = root / FIGURE_LEDGER.relative_to(ROOT)

    checks = [
        {
            "name": "figure_engine_binding_present",
            "passed": figure_engine.get("name") == "panelforge-figures"
            and figure_engine.get("pinned_ref") == "v3.14.1",
            "detail": figure_engine.get("repo_url", ""),
        },
        {
            "name": "stage_9_6_gate_passed",
            "passed": gate96.get("pass") is True,
            "detail": "Stage 9.6 must freeze the figure-to-claim-to-artifact contract before rendering.",
        },
        {
            "name": "figure_ledger_present",
            "passed": ledger.exists(),
            "detail": ledger.relative_to(root).as_posix(),
        },
        {
            "name": "manifest_is_placeholder_before_execution",
            "passed": manifest.exists()
            and "scaffold_placeholder_not_renderable" in manifest.read_text(encoding="utf-8"),
            "detail": manifest.relative_to(root).as_posix(),
        },
        {
            "name": "panelforge_not_cloned_yet",
            "passed": placeholder.exists() and not (placeholder.parent / ".git").exists(),
            "detail": placeholder.parent.relative_to(root).as_posix(),
        },
        {
            "name": "runtime_env_not_created_yet",
            "passed": not (root / ".venv-panelforge").exists(),
            "detail": ".venv-panelforge",
        },
    ]
    blocking = [check["name"] for check in checks if not check["passed"]]
    return {
        "status": "ready_for_execution" if not blocking else "blocked_preconditions",
        "substage": "9.6b",
        "mode": "preflight_only",
        "checks": checks,
        "blocking": blocking,
        "next_allowed_action": "Run Stage 9.6 first and freeze the figure contract." if blocking else "Explicit 9.6b execution may be authorized.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Reserved for future Stage 9.6b execution. This scaffolded harness refuses execution until implemented.",
    )
    args = parser.parse_args()
    payload = preflight(ROOT)
    if args.execute:
        payload["status"] = "execution_not_implemented_in_scaffold"
        payload["next_allowed_action"] = "Implement execution only after Stage 9.6 has passed and the user explicitly authorizes Stage 9.6b."
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["status"] in {"blocked_preconditions", "ready_for_execution", "execution_not_implemented_in_scaffold"} else 1


if __name__ == "__main__":
    raise SystemExit(main())

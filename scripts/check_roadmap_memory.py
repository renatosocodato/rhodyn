"""Check that RhoDyn's roadmap memory preserves the Stage 3-8 lock."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MEMORY_PATH = ROOT / "docs" / "roadmap_execution_memory.json"
ROADMAP_PATH = ROOT / "docs" / "roadmap.md"
STAGE3_GATE_PATH = ROOT / "case_studies" / "stage3_case_study_bank_gate_report.json"
STAGE5_CLOSEOUT_PATH = ROOT / "docs" / "stage5_closeout.md"


def check_roadmap_memory(root: Path = ROOT) -> dict[str, object]:
    failures: list[str] = []
    warnings: list[str] = []

    memory_path = root / MEMORY_PATH.relative_to(ROOT)
    roadmap_path = root / ROADMAP_PATH.relative_to(ROOT)
    gate_path = root / STAGE3_GATE_PATH.relative_to(ROOT)
    stage5_closeout_path = root / STAGE5_CLOSEOUT_PATH.relative_to(ROOT)

    if not memory_path.exists():
        failures.append("missing docs/roadmap_execution_memory.json")
        memory: dict[str, object] = {}
    else:
        memory = json.loads(memory_path.read_text(encoding="utf-8"))

    if not roadmap_path.exists():
        failures.append("missing docs/roadmap.md")
        roadmap = ""
    else:
        roadmap = roadmap_path.read_text(encoding="utf-8")

    if not gate_path.exists():
        failures.append("missing Stage 3 gate report")
        gate: dict[str, object] = {}
    else:
        gate = json.loads(gate_path.read_text(encoding="utf-8"))

    current = memory.get("current_position", {}) if isinstance(memory, dict) else {}
    if current.get("active_stage") != "Stage 6. Official software release":
        failures.append("active stage must be Stage 6. Official software release after Stage 5 closeout")

    stages = {entry.get("stage"): entry for entry in memory.get("stage_lock", []) if isinstance(entry, dict)}
    expected_status = {
        3: "complete_for_current_gate",
        4: "frozen_for_stage5",
        5: "completed",
        6: "public_citable_v0.1.0",
        7: "not_ready",
        8: "conceptual_only",
    }
    for stage, status in expected_status.items():
        if stages.get(stage, {}).get("status") != status:
            failures.append(f"Stage {stage} status must be {status}")

    stage6 = stages.get(6, {})
    subphases = stage6.get("subphases", []) if isinstance(stage6, dict) else []
    subphase_ids = [entry.get("id") for entry in subphases if isinstance(entry, dict)]
    expected_subphase_ids = ["6.1", "6.2", "6.3", "6.4", "6.5", "6.6", "6.7"]
    if subphase_ids != expected_subphase_ids:
        failures.append("Stage 6 subphases must be bound as 6.1 through 6.7 in roadmap execution memory")
    for entry in subphases:
        if isinstance(entry, dict) and (not entry.get("goal") or not entry.get("gate")):
            failures.append(f"Stage 6 subphase {entry.get('id', '?')} must include goal and gate")

    roadmap_flat = " ".join(roadmap.split())
    required_roadmap_phrases = [
        "The original Stage 3 to Stage 8 blueprint is retained as the controlling sequence",
        "Stage 3 is satisfied for the current evidence-bank gate",
        "Stage 4 is frozen for the first Stage 5 scaffold",
        "Stage 5 is completed as a contract-bound scientific workbench",
        "Stage 6 is the active release-hardening stage",
        "6.1 Release boundary",
        "6.2 Packaging",
        "6.3 Documentation",
        "6.4 Release automation",
        "6.5 Archive and citation",
        "6.6 Clean-room reproducibility",
        "6.7 Final ultra-hardening",
        "Stage 7 is the future Nature Methods-first scientific-methods campaign",
        "Stage 8 inherits from Stage 7",
    ]
    for phrase in required_roadmap_phrases:
        if phrase not in roadmap_flat:
            failures.append(f"roadmap is missing lock phrase: {phrase}")

    if gate.get("status") != "pass":
        failures.append("Stage 3 gate report must pass")

    if not stage5_closeout_path.exists():
        failures.append("missing docs/stage5_closeout.md")
        stage5_closeout = ""
    else:
        stage5_closeout = stage5_closeout_path.read_text(encoding="utf-8")
    if "Stage 5 status. Completed." not in stage5_closeout:
        failures.append("Stage 5 closeout must mark Stage 5 completed")
    if "Stage 6 handoff. Active." not in stage5_closeout:
        failures.append("Stage 5 closeout must mark Stage 6 active")
    if "No blocking Stage 5 technical debt remains." not in stage5_closeout:
        failures.append("Stage 5 closeout must declare no blocking Stage 5 technical debt")
    if "Stage 7 evidence-expansion" not in str(gate.get("current_position", "")):
        failures.append("Stage 3 gate report must keep additional public systems in Stage 7")
    if "They do not imply that RhoDyn generated" not in str(gate.get("interpretation_boundary", "")):
        failures.append("Stage 3 gate report must preserve manuscript-independence boundary")

    if not failures and gate.get("status") == "pass":
        warnings.append("Stage 3 is frozen for the current gate; new public systems should be Stage 7 unless a Stage 3 defect is documented")
        warnings.append("Stage 6 v0.1.0 is publicly citable through GitHub and Zenodo; PyPI remains dry-run only until a later distribution decision")

    return {
        "status": "pass" if not failures else "fail",
        "failures": failures,
        "warnings": warnings,
        "active_stage": current.get("active_stage"),
        "stage3_gate_status": gate.get("status"),
    }


def main() -> int:
    payload = check_roadmap_memory()
    print(json.dumps(payload, indent=2))
    return 0 if payload["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())

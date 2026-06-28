"""Check that RhoDyn's roadmap memory preserves the Stage 3-8 lock."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MEMORY_PATH = ROOT / "docs" / "roadmap_execution_memory.json"
ROADMAP_PATH = ROOT / "docs" / "roadmap.md"
STAGE3_GATE_PATH = ROOT / "case_studies" / "stage3_case_study_bank_gate_report.json"


def check_roadmap_memory(root: Path = ROOT) -> dict[str, object]:
    failures: list[str] = []
    warnings: list[str] = []

    memory_path = root / MEMORY_PATH.relative_to(ROOT)
    roadmap_path = root / ROADMAP_PATH.relative_to(ROOT)
    gate_path = root / STAGE3_GATE_PATH.relative_to(ROOT)

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
    if current.get("active_stage") != "Stage 5. Frontend":
        failures.append("active stage must be Stage 5. Frontend after the Stage 4 API freeze")

    stages = {entry.get("stage"): entry for entry in memory.get("stage_lock", []) if isinstance(entry, dict)}
    expected_status = {
        3: "complete_for_current_gate",
        4: "frozen_for_stage5",
        5: "active_scaffold",
        6: "partly_prepared_not_citable",
        7: "not_ready",
        8: "conceptual_only",
    }
    for stage, status in expected_status.items():
        if stages.get(stage, {}).get("status") != status:
            failures.append(f"Stage {stage} status must be {status}")

    roadmap_flat = " ".join(roadmap.split())
    required_roadmap_phrases = [
        "The original Stage 3 to Stage 8 blueprint is retained as the controlling sequence",
        "Stage 3 is satisfied for the current evidence-bank gate",
        "Stage 4 is frozen for the first Stage 5 scaffold",
        "Stage 5 is the active execution stage",
        "Stage 7 is the future Nature Methods-first scientific-methods campaign",
        "Stage 8 inherits from Stage 7",
    ]
    for phrase in required_roadmap_phrases:
        if phrase not in roadmap_flat:
            failures.append(f"roadmap is missing lock phrase: {phrase}")

    if gate.get("status") != "pass":
        failures.append("Stage 3 gate report must pass")
    if "Stage 7 evidence-expansion" not in str(gate.get("current_position", "")):
        failures.append("Stage 3 gate report must keep additional public systems in Stage 7")
    if "They do not imply that RhoDyn generated" not in str(gate.get("interpretation_boundary", "")):
        failures.append("Stage 3 gate report must preserve manuscript-independence boundary")

    if not failures and gate.get("status") == "pass":
        warnings.append("Stage 3 is frozen for the current gate; new public systems should be Stage 7 unless a Stage 3 defect is documented")
        warnings.append("Stage 5 is active only as a contract-bound frontend scaffold; Stage 6 remains downstream")

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

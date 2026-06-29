"""Check that RhoDyn's roadmap memory preserves the Stage 3-8 lock."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MEMORY_PATH = ROOT / "docs" / "roadmap_execution_memory.json"
ROADMAP_PATH = ROOT / "docs" / "roadmap.md"
STAGE3_GATE_PATH = ROOT / "case_studies" / "stage3_case_study_bank_gate_report.json"
STAGE5_CLOSEOUT_PATH = ROOT / "docs" / "stage5_closeout.md"
STAGE7_PROGRAM_PATH = ROOT / "docs" / "stage7_methods_program.md"
STAGE7_EXECUTION_PATH = ROOT / "docs" / "stage7_serialized_execution_plan.md"
STAGE7_SOURCE_REGISTER_PATH = ROOT / "docs" / "stage7_0_source_register.md"
STAGE7_BASELINE_INVENTORY_PATH = ROOT / "docs" / "stage7_0_baseline_method_inventory.md"
STAGE7_DATASET_RUBRIC_PATH = ROOT / "docs" / "stage7_0_dataset_selection_rubric.md"
STAGE7_ARTIFACT_MAP_PATH = ROOT / "docs" / "stage7_0_artifact_map.md"
STAGE7_GATE_REPORT_PATH = ROOT / "docs" / "stage7_0_gate_report.json"
STAGE7_1_GATE_REPORT_PATH = ROOT / "docs" / "stage7_1_gate_report.json"
STAGE7_1_TRUTH_REPORT_PATH = ROOT / "case_studies" / "stage7_synthetic_truth" / "stage7_1_synthetic_truth_report.json"


def check_roadmap_memory(root: Path = ROOT) -> dict[str, object]:
    failures: list[str] = []
    warnings: list[str] = []

    memory_path = root / MEMORY_PATH.relative_to(ROOT)
    roadmap_path = root / ROADMAP_PATH.relative_to(ROOT)
    gate_path = root / STAGE3_GATE_PATH.relative_to(ROOT)
    stage5_closeout_path = root / STAGE5_CLOSEOUT_PATH.relative_to(ROOT)
    stage7_program_path = root / STAGE7_PROGRAM_PATH.relative_to(ROOT)
    stage7_execution_path = root / STAGE7_EXECUTION_PATH.relative_to(ROOT)
    stage7_source_register_path = root / STAGE7_SOURCE_REGISTER_PATH.relative_to(ROOT)
    stage7_baseline_inventory_path = root / STAGE7_BASELINE_INVENTORY_PATH.relative_to(ROOT)
    stage7_dataset_rubric_path = root / STAGE7_DATASET_RUBRIC_PATH.relative_to(ROOT)
    stage7_artifact_map_path = root / STAGE7_ARTIFACT_MAP_PATH.relative_to(ROOT)
    stage7_gate_report_path = root / STAGE7_GATE_REPORT_PATH.relative_to(ROOT)
    stage7_1_gate_report_path = root / STAGE7_1_GATE_REPORT_PATH.relative_to(ROOT)
    stage7_1_truth_report_path = root / STAGE7_1_TRUTH_REPORT_PATH.relative_to(ROOT)

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
    if current.get("active_stage") != "Stage 7.1 method formalization complete":
        failures.append("active stage must be Stage 7.1 method formalization complete after Stage 7.1 execution")

    stages = {entry.get("stage"): entry for entry in memory.get("stage_lock", []) if isinstance(entry, dict)}
    expected_status = {
        3: "complete_for_current_gate",
        4: "frozen_for_stage5",
        5: "completed",
        6: "public_citable_v0.1.0",
        7: "stage7_1_complete_7_2_not_started",
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

    stage7 = stages.get(7, {})
    stage7_subphases = stage7.get("subphases", []) if isinstance(stage7, dict) else []
    stage7_subphase_status = {entry.get("id"): entry.get("status") for entry in stage7_subphases if isinstance(entry, dict)}
    if stage7_subphase_status.get("7.0") != "complete_planning_only":
        failures.append("Stage 7.0 must be marked complete_planning_only")
    if stage7_subphase_status.get("7.1") != "complete_method_formalization":
        failures.append("Stage 7.1 must be marked complete_method_formalization")
    if stage7_subphase_status.get("7.2") != "not_started_next_authorization_required":
        failures.append("Stage 7.2 must remain not_started_next_authorization_required")

    roadmap_flat = " ".join(roadmap.split())
    required_roadmap_phrases = [
        "The original Stage 3 to Stage 8 blueprint is retained as the controlling sequence",
        "Stage 3 is satisfied for the current evidence-bank gate",
        "Stage 4 is frozen for the first Stage 5 scaffold",
        "Stage 5 is completed as a contract-bound scientific workbench",
        "Stage 6 has produced a professionally citable RhoDyn `v0.1.0` GitHub",
        "6.1 Release boundary",
        "6.2 Packaging",
        "6.3 Documentation",
        "6.4 Release automation",
        "6.5 Archive and citation",
        "6.6 Clean-room reproducibility",
        "6.7 Final ultra-hardening",
        "7.0 Planning freeze and evidence source register. Complete as a planning-only",
        "Stage 7.1 is complete as a method-formalization phase",
        "docs/stage7_methods_program.md",
        "docs/stage7_serialized_execution_plan.md",
        "docs/stage7_0_*",
        "Stage 8 inherits from Stage 7",
    ]
    for phrase in required_roadmap_phrases:
        if phrase not in roadmap_flat:
            failures.append(f"roadmap is missing lock phrase: {phrase}")

    if gate.get("status") != "pass":
        failures.append("Stage 3 gate report must pass")

    if not stage7_program_path.exists():
        failures.append("missing docs/stage7_methods_program.md")
        stage7_program = ""
    else:
        stage7_program = stage7_program_path.read_text(encoding="utf-8")
    if not stage7_execution_path.exists():
        failures.append("missing docs/stage7_serialized_execution_plan.md")
        stage7_execution = ""
    else:
        stage7_execution = stage7_execution_path.read_text(encoding="utf-8")
    for phrase in [
        "Evidence basis",
        "Gap analysis",
        "Independent biological demonstration strategy",
        "Software maturity roadmap",
        "Publication alignment roadmap",
        "Subphase dependency and success-metric matrix",
        "Nature Methods is the primary reference point",
        "No Stage 7 implementation begins",
        "Stage 7.1 method formalization outputs",
    ]:
        if phrase not in stage7_program:
            failures.append(f"Stage 7 methods program is missing phrase: {phrase}")
    for phrase in [
        "strictly serialized",
        "7.0. Planning freeze and evidence source register",
        "7.8. Methods manuscript readiness package",
        "No downstream subphase should begin",
        "Subphase bookkeeping and roadmap updates",
    ]:
        if phrase not in stage7_execution:
            failures.append(f"Stage 7 execution plan is missing phrase: {phrase}")

    stage7_doc_specs = [
        (stage7_source_register_path, "source register", ["Official and community guidance sources", "Representative methods papers", "Candidate dataset classes", "RhoA/microglia reference case"]),
        (stage7_baseline_inventory_path, "baseline inventory", ["Endpoint value", "Peak amplitude", "Generic trajectory features", "Domain-standard method"]),
        (stage7_dataset_rubric_path, "dataset rubric", ["Missing time units", "Missing condition labels", "Missing replicate", "Non-reviewable access"]),
        (stage7_artifact_map_path, "artifact map", ["Created planning artifact", "Planned future artifact", "Out of scope for Stage 7.0"]),
    ]
    for path, label, phrases in stage7_doc_specs:
        if not path.exists():
            failures.append(f"missing {path.relative_to(root)}")
            continue
        body = path.read_text(encoding="utf-8")
        for phrase in phrases:
            if phrase not in body:
                failures.append(f"Stage 7.0 {label} missing phrase: {phrase}")

    if not stage7_gate_report_path.exists():
        failures.append("missing docs/stage7_0_gate_report.json")
    else:
        stage7_gate = json.loads(stage7_gate_report_path.read_text(encoding="utf-8"))
        if stage7_gate.get("status") != "pass":
            failures.append("Stage 7.0 gate report must pass")
        for field in ["scientific_implementation_started", "software_implementation_started", "manuscript_drafting_started"]:
            if stage7_gate.get(field):
                failures.append(f"Stage 7.0 gate report must keep {field} false")


    stage7_1_docs = [
        (root / "docs" / "stage7_method_specification.md", "Stage 7.1 method specification", ["Tidy trajectory", "Residence window", "Bounded-coupling", "Failure modes"]),
        (root / "docs" / "stage7_synthetic_truth_cases.md", "Stage 7.1 synthetic truth cases", ["positive", "counterexample", "ambiguous", "not biological evidence"]),
        (root / "docs" / "stage7_limitations_matrix.md", "Stage 7.1 limitations matrix", ["failure modes", "interpretation boundaries", "does not add new biological claims"]),
        (root / "docs" / "stage7_api_stability_notes.md", "Stage 7.1 API stability notes", ["existing RhoDyn public API", "No key Stage 7.1 method object is blocked"]),
    ]
    for path, label, phrases in stage7_1_docs:
        if not path.exists():
            failures.append(f"missing {path.relative_to(root)}")
            continue
        body = path.read_text(encoding="utf-8")
        for phrase in phrases:
            if phrase not in body:
                failures.append(f"{label} missing phrase: {phrase}")

    if not stage7_1_gate_report_path.exists():
        failures.append("missing docs/stage7_1_gate_report.json")
    else:
        stage7_1_gate = json.loads(stage7_1_gate_report_path.read_text(encoding="utf-8"))
        if stage7_1_gate.get("status") != "pass":
            failures.append("Stage 7.1 gate report must pass")
        if stage7_1_gate.get("completion_state") != "complete_method_formalization":
            failures.append("Stage 7.1 gate report must record complete_method_formalization")
        if stage7_1_gate.get("truth_suite_status") != "pass":
            failures.append("Stage 7.1 truth suite must pass")
        checkpoints = stage7_1_gate.get("validation_checkpoints", {}) if isinstance(stage7_1_gate.get("validation_checkpoints", {}), dict) else {}
        for checkpoint in [
            "every_definition_has_executable_example_and_counterexample",
            "synthetic_truth_cases_include_positive_negative_ambiguous_regimes",
            "existing_apis_can_represent_declared_results",
        ]:
            if checkpoints.get(checkpoint) != "pass":
                failures.append(f"Stage 7.1 gate checkpoint must pass: {checkpoint}")

    if not stage7_1_truth_report_path.exists():
        failures.append("missing case_studies/stage7_synthetic_truth/stage7_1_synthetic_truth_report.json")
    else:
        truth_report = json.loads(stage7_1_truth_report_path.read_text(encoding="utf-8"))
        if truth_report.get("status") != "pass":
            failures.append("Stage 7.1 synthetic truth report must pass")

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
        warnings.append("Stage 7.1 method formalization is complete; Stage 7.2 benchmark harness has not started")

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

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
STAGE7_2_GATE_REPORT_PATH = ROOT / "docs" / "stage7_2_gate_report.json"
STAGE7_2_BENCHMARK_REPORT_PATH = ROOT / "case_studies" / "stage7_benchmarks" / "stage7_2_benchmark_report.json"
STAGE7_3_GATE_REPORT_PATH = ROOT / "docs" / "stage7_3_gate_report.json"
STAGE7_3_PUBLIC_REPORT_PATH = ROOT / "case_studies" / "stage7_public_signaling" / "stage7_3_public_signaling_gate_report.json"
STAGE7_4_GATE_REPORT_PATH = ROOT / "docs" / "stage7_4_gate_report.json"
STAGE7_4_CASE_REPORT_PATH = ROOT / "case_studies" / "stage7_endpoint_reserve_routing" / "stage7_4_endpoint_reserve_routing_gate_report.json"
STAGE7_5_GATE_REPORT_PATH = ROOT / "docs" / "stage7_5_gate_report.json"
STAGE7_5_CASE_REPORT_PATH = ROOT / "case_studies" / "stage7_heldout_validation" / "stage7_5_heldout_validation_gate_report.json"
STAGE7_6_GATE_REPORT_PATH = ROOT / "docs" / "stage7_6_gate_report.json"
STAGE7_6_CASE_REPORT_PATH = ROOT / "case_studies" / "stage7_methods_reproducibility" / "stage7_6_methods_reproducibility_gate_report.json"
STAGE7_7_GATE_REPORT_PATH = ROOT / "docs" / "stage7_7_gate_report.json"
STAGE7_7_CASE_REPORT_PATH = ROOT / "case_studies" / "stage7_usability_rehearsal" / "stage7_7_usability_gate_report.json"
STAGE7_8_GATE_REPORT_PATH = ROOT / "docs" / "stage7_8_gate_report.json"
STAGE7_8_CASE_REPORT_PATH = ROOT / "case_studies" / "stage7_methods_readiness" / "stage7_8_methods_readiness_gate_report.json"
STAGE9_PLAN_PATH = ROOT / "docs" / "stage9_manuscript_assembly_plan.md"
STAGE9_MEMORY_PATH = ROOT / "docs" / "stage9_execution_memory.json"
STAGE9_CHECKER_PATH = ROOT / "scripts" / "check_stage9_scaffold.py"
STAGE9_0_RUNNER_PATH = ROOT / "scripts" / "run_stage9_0_evidence_intake_lock.py"
STAGE9_1_RUNNER_PATH = ROOT / "scripts" / "run_stage9_1_venue_guidance_register.py"
STAGE9_2_RUNNER_PATH = ROOT / "scripts" / "run_stage9_2_methods_paper_corpus.py"
STAGE9_3_RUNNER_PATH = ROOT / "scripts" / "run_stage9_3_narrative_spine.py"
STAGE9_4_RUNNER_PATH = ROOT / "scripts" / "run_stage9_4_claim_freeze.py"
STAGE9_5_RUNNER_PATH = ROOT / "scripts" / "run_stage9_5_paragraph_claim_ledger.py"
STAGE9_6_RUNNER_PATH = ROOT / "scripts" / "run_stage9_6_figure_spine.py"
STAGE9_PANELFORGE_PREFLIGHT_PATH = ROOT / "scripts" / "run_stage9_6b_panelforge_rendering.py"
STAGE9_7_RUNNER_PATH = ROOT / "scripts" / "run_stage9_7_supplementary_display_plan.py"
STAGE9_8_RUNNER_PATH = ROOT / "scripts" / "run_stage9_8_section_contract_blueprint.py"
STAGE9_9_RUNNER_PATH = ROOT / "scripts" / "run_stage9_9_title_abstract_strategy.py"
STAGE9_10_RUNNER_PATH = ROOT / "scripts" / "run_stage9_10_results_architecture.py"
STAGE9_11_RUNNER_PATH = ROOT / "scripts" / "run_stage9_11_results_drafting.py"
STAGE9_12_RUNNER_PATH = ROOT / "scripts" / "run_stage9_12_introduction_literature_binding.py"
STAGE9_13_RUNNER_PATH = ROOT / "scripts" / "run_stage9_13_discussion_interpretation_map.py"
STAGE9_14_RUNNER_PATH = ROOT / "scripts" / "run_stage9_14_discussion_drafting.py"
STAGE9_15_RUNNER_PATH = ROOT / "scripts" / "run_stage9_15_methods_architecture.py"
STAGE9_16_RUNNER_PATH = ROOT / "scripts" / "run_stage9_16_methods_drafting.py"
STAGE9_17_RUNNER_PATH = ROOT / "scripts" / "run_stage9_17_availability_assembly.py"
STAGE9_18_RUNNER_PATH = ROOT / "scripts" / "run_stage9_18_supplementary_methods.py"
STAGE9_19_RUNNER_PATH = ROOT / "scripts" / "run_stage9_19_supplementary_tables.py"
STAGE9_20_RUNNER_PATH = ROOT / "scripts" / "run_stage9_20_reference_audit.py"
STAGE9_21_RUNNER_PATH = ROOT / "scripts" / "run_stage9_21_cross_document_consistency.py"
STAGE9_GATE_PATH = ROOT / "manuscript" / "nature_methods" / "gate_verdicts" / "9.-1.json"
STAGE9_0_GATE_PATH = ROOT / "manuscript" / "nature_methods" / "gate_verdicts" / "9.0.json"
STAGE9_1_GATE_PATH = ROOT / "manuscript" / "nature_methods" / "gate_verdicts" / "9.1.json"
STAGE9_2_GATE_PATH = ROOT / "manuscript" / "nature_methods" / "gate_verdicts" / "9.2.json"
STAGE9_3_GATE_PATH = ROOT / "manuscript" / "nature_methods" / "gate_verdicts" / "9.3.json"
STAGE9_4_GATE_PATH = ROOT / "manuscript" / "nature_methods" / "gate_verdicts" / "9.4.json"
STAGE9_5_GATE_PATH = ROOT / "manuscript" / "nature_methods" / "gate_verdicts" / "9.5.json"
STAGE9_6_GATE_PATH = ROOT / "manuscript" / "nature_methods" / "gate_verdicts" / "9.6.json"
STAGE9_6B_GATE_PATH = ROOT / "manuscript" / "nature_methods" / "gate_verdicts" / "9.6b.json"
STAGE9_7_GATE_PATH = ROOT / "manuscript" / "nature_methods" / "gate_verdicts" / "9.7.json"
STAGE9_8_GATE_PATH = ROOT / "manuscript" / "nature_methods" / "gate_verdicts" / "9.8.json"
STAGE9_9_GATE_PATH = ROOT / "manuscript" / "nature_methods" / "gate_verdicts" / "9.9.json"
STAGE9_10_GATE_PATH = ROOT / "manuscript" / "nature_methods" / "gate_verdicts" / "9.10.json"
STAGE9_11_GATE_PATH = ROOT / "manuscript" / "nature_methods" / "gate_verdicts" / "9.11.json"
STAGE9_12_GATE_PATH = ROOT / "manuscript" / "nature_methods" / "gate_verdicts" / "9.12.json"
STAGE9_13_GATE_PATH = ROOT / "manuscript" / "nature_methods" / "gate_verdicts" / "9.13.json"
STAGE9_14_GATE_PATH = ROOT / "manuscript" / "nature_methods" / "gate_verdicts" / "9.14.json"
STAGE9_15_GATE_PATH = ROOT / "manuscript" / "nature_methods" / "gate_verdicts" / "9.15.json"
STAGE9_16_GATE_PATH = ROOT / "manuscript" / "nature_methods" / "gate_verdicts" / "9.16.json"
STAGE9_17_GATE_PATH = ROOT / "manuscript" / "nature_methods" / "gate_verdicts" / "9.17.json"
STAGE9_18_GATE_PATH = ROOT / "manuscript" / "nature_methods" / "gate_verdicts" / "9.18.json"
STAGE9_19_GATE_PATH = ROOT / "manuscript" / "nature_methods" / "gate_verdicts" / "9.19.json"
STAGE9_20_GATE_PATH = ROOT / "manuscript" / "nature_methods" / "gate_verdicts" / "9.20.json"
STAGE9_21_GATE_PATH = ROOT / "manuscript" / "nature_methods" / "gate_verdicts" / "9.21.json"


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
    stage7_2_gate_report_path = root / STAGE7_2_GATE_REPORT_PATH.relative_to(ROOT)
    stage7_2_benchmark_report_path = root / STAGE7_2_BENCHMARK_REPORT_PATH.relative_to(ROOT)
    stage7_3_gate_report_path = root / STAGE7_3_GATE_REPORT_PATH.relative_to(ROOT)
    stage7_3_public_report_path = root / STAGE7_3_PUBLIC_REPORT_PATH.relative_to(ROOT)
    stage7_4_gate_report_path = root / STAGE7_4_GATE_REPORT_PATH.relative_to(ROOT)
    stage7_4_case_report_path = root / STAGE7_4_CASE_REPORT_PATH.relative_to(ROOT)
    stage7_5_gate_report_path = root / STAGE7_5_GATE_REPORT_PATH.relative_to(ROOT)
    stage7_5_case_report_path = root / STAGE7_5_CASE_REPORT_PATH.relative_to(ROOT)
    stage7_6_gate_report_path = root / STAGE7_6_GATE_REPORT_PATH.relative_to(ROOT)
    stage7_6_case_report_path = root / STAGE7_6_CASE_REPORT_PATH.relative_to(ROOT)
    stage7_7_gate_report_path = root / STAGE7_7_GATE_REPORT_PATH.relative_to(ROOT)
    stage7_7_case_report_path = root / STAGE7_7_CASE_REPORT_PATH.relative_to(ROOT)
    stage7_8_gate_report_path = root / STAGE7_8_GATE_REPORT_PATH.relative_to(ROOT)
    stage7_8_case_report_path = root / STAGE7_8_CASE_REPORT_PATH.relative_to(ROOT)
    stage9_plan_path = root / STAGE9_PLAN_PATH.relative_to(ROOT)
    stage9_memory_path = root / STAGE9_MEMORY_PATH.relative_to(ROOT)
    stage9_checker_path = root / STAGE9_CHECKER_PATH.relative_to(ROOT)
    stage9_0_runner_path = root / STAGE9_0_RUNNER_PATH.relative_to(ROOT)
    stage9_1_runner_path = root / STAGE9_1_RUNNER_PATH.relative_to(ROOT)
    stage9_2_runner_path = root / STAGE9_2_RUNNER_PATH.relative_to(ROOT)
    stage9_3_runner_path = root / STAGE9_3_RUNNER_PATH.relative_to(ROOT)
    stage9_4_runner_path = root / STAGE9_4_RUNNER_PATH.relative_to(ROOT)
    stage9_5_runner_path = root / STAGE9_5_RUNNER_PATH.relative_to(ROOT)
    stage9_6_runner_path = root / STAGE9_6_RUNNER_PATH.relative_to(ROOT)
    stage9_panelforge_preflight_path = root / STAGE9_PANELFORGE_PREFLIGHT_PATH.relative_to(ROOT)
    stage9_7_runner_path = root / STAGE9_7_RUNNER_PATH.relative_to(ROOT)
    stage9_8_runner_path = root / STAGE9_8_RUNNER_PATH.relative_to(ROOT)
    stage9_9_runner_path = root / STAGE9_9_RUNNER_PATH.relative_to(ROOT)
    stage9_10_runner_path = root / STAGE9_10_RUNNER_PATH.relative_to(ROOT)
    stage9_11_runner_path = root / STAGE9_11_RUNNER_PATH.relative_to(ROOT)
    stage9_12_runner_path = root / STAGE9_12_RUNNER_PATH.relative_to(ROOT)
    stage9_13_runner_path = root / STAGE9_13_RUNNER_PATH.relative_to(ROOT)
    stage9_14_runner_path = root / STAGE9_14_RUNNER_PATH.relative_to(ROOT)
    stage9_15_runner_path = root / STAGE9_15_RUNNER_PATH.relative_to(ROOT)
    stage9_16_runner_path = root / STAGE9_16_RUNNER_PATH.relative_to(ROOT)
    stage9_17_runner_path = root / STAGE9_17_RUNNER_PATH.relative_to(ROOT)
    stage9_18_runner_path = root / STAGE9_18_RUNNER_PATH.relative_to(ROOT)
    stage9_19_runner_path = root / STAGE9_19_RUNNER_PATH.relative_to(ROOT)
    stage9_20_runner_path = root / STAGE9_20_RUNNER_PATH.relative_to(ROOT)
    stage9_21_runner_path = root / STAGE9_21_RUNNER_PATH.relative_to(ROOT)
    stage9_gate_path = root / STAGE9_GATE_PATH.relative_to(ROOT)
    stage9_0_gate_path = root / STAGE9_0_GATE_PATH.relative_to(ROOT)
    stage9_1_gate_path = root / STAGE9_1_GATE_PATH.relative_to(ROOT)
    stage9_2_gate_path = root / STAGE9_2_GATE_PATH.relative_to(ROOT)
    stage9_3_gate_path = root / STAGE9_3_GATE_PATH.relative_to(ROOT)
    stage9_4_gate_path = root / STAGE9_4_GATE_PATH.relative_to(ROOT)
    stage9_5_gate_path = root / STAGE9_5_GATE_PATH.relative_to(ROOT)
    stage9_6_gate_path = root / STAGE9_6_GATE_PATH.relative_to(ROOT)
    stage9_6b_gate_path = root / STAGE9_6B_GATE_PATH.relative_to(ROOT)
    stage9_7_gate_path = root / STAGE9_7_GATE_PATH.relative_to(ROOT)
    stage9_8_gate_path = root / STAGE9_8_GATE_PATH.relative_to(ROOT)
    stage9_9_gate_path = root / STAGE9_9_GATE_PATH.relative_to(ROOT)
    stage9_10_gate_path = root / STAGE9_10_GATE_PATH.relative_to(ROOT)
    stage9_11_gate_path = root / STAGE9_11_GATE_PATH.relative_to(ROOT)
    stage9_12_gate_path = root / STAGE9_12_GATE_PATH.relative_to(ROOT)
    stage9_13_gate_path = root / STAGE9_13_GATE_PATH.relative_to(ROOT)
    stage9_14_gate_path = root / STAGE9_14_GATE_PATH.relative_to(ROOT)
    stage9_15_gate_path = root / STAGE9_15_GATE_PATH.relative_to(ROOT)
    stage9_16_gate_path = root / STAGE9_16_GATE_PATH.relative_to(ROOT)
    stage9_17_gate_path = root / STAGE9_17_GATE_PATH.relative_to(ROOT)
    stage9_18_gate_path = root / STAGE9_18_GATE_PATH.relative_to(ROOT)
    stage9_19_gate_path = root / STAGE9_19_GATE_PATH.relative_to(ROOT)
    stage9_20_gate_path = root / STAGE9_20_GATE_PATH.relative_to(ROOT)
    stage9_21_gate_path = root / STAGE9_21_GATE_PATH.relative_to(ROOT)

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
    if current.get("active_stage") != "Stage 9.21 Cross-document consistency audit complete; statistical and quantitative language audit not started":
        failures.append("active stage must record the Stage 9.21 cross-document consistency boundary")

    stages = {entry.get("stage"): entry for entry in memory.get("stage_lock", []) if isinstance(entry, dict)}
    expected_status = {
        3: "complete_for_current_gate",
        4: "frozen_for_stage5",
        5: "completed",
        6: "public_citable_v0.1.0",
        7: "stage7_8_complete_methods_readiness",
        8: "conceptual_only",
        9: "stage9_21_cross_document_consistency_bound",
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
    if stage7_subphase_status.get("7.2") != "complete_benchmark_harness":
        failures.append("Stage 7.2 must be marked complete_benchmark_harness")
    if stage7_subphase_status.get("7.3") != "complete_public_signaling_demonstrations":
        failures.append("Stage 7.3 must be marked complete_public_signaling_demonstrations")
    if stage7_subphase_status.get("7.4") != "complete_endpoint_reserve_routing_demonstrations":
        failures.append("Stage 7.4 must be marked complete_endpoint_reserve_routing_demonstrations")
    if stage7_subphase_status.get("7.5") != "complete_external_heldout_validation":
        failures.append("Stage 7.5 must be marked complete_external_heldout_validation")
    if stage7_subphase_status.get("7.6") != "complete_methods_reproducibility_hardening":
        failures.append("Stage 7.6 must be marked complete_methods_reproducibility_hardening")
    if stage7_subphase_status.get("7.7") != "complete_usability_adoption_rehearsal":
        failures.append("Stage 7.7 must be marked complete_usability_adoption_rehearsal")
    if stage7_subphase_status.get("7.8") != "complete_methods_manuscript_readiness_package":
        failures.append("Stage 7.8 must be marked complete_methods_manuscript_readiness_package")
    stage9 = stages.get(9, {})
    if stage9.get("substage_count") != 33:
        failures.append("Stage 9 must record 33 serialized substages")
    stage9_substages = stage9.get("subphases", []) if isinstance(stage9, dict) else []
    stage9_status = {entry.get("id"): entry.get("status") for entry in stage9_substages if isinstance(entry, dict)}
    if stage9_status.get("9.-1") != "complete_scaffold_only":
        failures.append("Stage 9.-1 must be complete_scaffold_only")
    if "9.6b" not in stage9_status:
        failures.append("Stage 9.6b PanelForge rendering substage must be serialized")
    if stage9_status.get("9.0") != "complete_evidence_locked":
        failures.append("Stage 9.0 must be complete_evidence_locked")
    if stage9_status.get("9.1") != "complete_guidance_registered":
        failures.append("Stage 9.1 must be complete_guidance_registered")
    if stage9_status.get("9.2") != "complete_methods_corpus_registered":
        failures.append("Stage 9.2 must be complete_methods_corpus_registered")
    if stage9_status.get("9.3") != "complete_narrative_spine_registered":
        failures.append("Stage 9.3 must be complete_narrative_spine_registered")
    if stage9_status.get("9.4") != "complete_claim_freeze_registered":
        failures.append("Stage 9.4 must be complete_claim_freeze_registered")
    if stage9_status.get("9.5") != "complete_paragraph_claim_ledger_registered":
        failures.append("Stage 9.5 must be complete_paragraph_claim_ledger_registered")
    if stage9_status.get("9.6") != "complete_figure_spine_registered":
        failures.append("Stage 9.6 must be complete_figure_spine_registered")
    if stage9_status.get("9.6b") != "complete_panelforge_rendering_registered":
        failures.append("Stage 9.6b must be complete_panelforge_rendering_registered")
    if stage9_status.get("9.7") != "complete_supplementary_display_plan_registered":
        failures.append("Stage 9.7 must be complete_supplementary_display_plan_registered")
    if stage9_status.get("9.8") != "complete_section_contract_blueprint_registered":
        failures.append("Stage 9.8 must be complete_section_contract_blueprint_registered")
    if stage9_status.get("9.9") != "complete_title_abstract_strategy_registered":
        failures.append("Stage 9.9 must be complete_title_abstract_strategy_registered")
    if stage9_status.get("9.10") != "complete_results_architecture_registered":
        failures.append("Stage 9.10 must be complete_results_architecture_registered")
    if stage9_status.get("9.11") != "complete_results_draft_registered":
        failures.append("Stage 9.11 must be complete_results_draft_registered")
    if stage9_status.get("9.12") != "complete_introduction_literature_bound":
        failures.append("Stage 9.12 must be complete_introduction_literature_bound")
    if stage9_status.get("9.13") != "complete_discussion_interpretation_mapped":
        failures.append("Stage 9.13 must be complete_discussion_interpretation_mapped")
    if stage9_status.get("9.14") != "complete_discussion_drafted":
        failures.append("Stage 9.14 must be complete_discussion_drafted")
    if stage9_status.get("9.15") != "complete_methods_architecture_registered":
        failures.append("Stage 9.15 must be complete_methods_architecture_registered")
    if stage9_status.get("9.16") != "complete_methods_drafted":
        failures.append("Stage 9.16 must be complete_methods_drafted")
    if stage9_status.get("9.17") != "complete_availability_assembled":
        failures.append("Stage 9.17 must be complete_availability_assembled")
    if stage9_status.get("9.18") != "complete_supplementary_methods_drafted":
        failures.append("Stage 9.18 must be complete_supplementary_methods_drafted")
    if stage9_status.get("9.19") != "complete_supplementary_tables_bound":
        failures.append("Stage 9.19 must be complete_supplementary_tables_bound")
    if stage9_status.get("9.20") != "complete_reference_library_bound":
        failures.append("Stage 9.20 must be complete_reference_library_bound")
    if stage9_status.get("9.21") != "complete_cross_document_consistency_bound":
        failures.append("Stage 9.21 must be complete_cross_document_consistency_bound")
    for entry in stage9_substages:
        if isinstance(entry, dict) and entry.get("id") not in {"9.-1", "9.0", "9.1", "9.2", "9.3", "9.4", "9.5", "9.6", "9.6b", "9.7", "9.8", "9.9", "9.10", "9.11", "9.12", "9.13", "9.14", "9.15", "9.16", "9.17", "9.18", "9.19", "9.20", "9.21"} and entry.get("status") != "not_started":
            failures.append(f"Stage {entry.get('id')} must remain not_started")

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
        "Stage 7.2 is complete as a benchmark-harness phase",
        "Stage 7.3 is complete as an independent public live-cell signaling",
        "Stage 7.4 is complete as a perturbation endpoint, reserve-like",
        "Stage 7.5 adds a held-out public validation route",
        "Stage 7.6 closes the methods-evidence reproducibility gate",
        "Stage 7.7 is complete",
        "Stage 7.8 is complete",
        "docs/stage7_methods_program.md",
        "docs/stage7_serialized_execution_plan.md",
        "docs/stage7_0_*",
        "Stage 8 inherits from Stage 7",
        "Stage 9 scaffold has been serialized",
        "Stage 9.0 evidence lock has been completed",
        "Stage 9.1 venue guidance source register has been completed",
        "Stage 9.2 representative methods-paper corpus has been completed",
        "Stage 9.3 narrative spine has been completed",
        "Stage 9.4 claim freeze has been completed",
        "Stage 9.5 paragraph-level claim ledger has been completed",
        "Stage 9.6 figure-first manuscript spine has been completed",
        "Stage 9.6b PanelForge rendering has been completed",
        "Stage 9.7 supplementary display planning has been completed",
        "Stage 9.8 section contract blueprint has been completed",
        "Stage 9.9 title, subtitle, and abstract strategy has been completed",
        "Stage 9.10 Results subsection architecture has been completed",
        "Stage 9.11 Results drafting pass has been completed",
        "Stage 9.12 Introduction literature binding has been completed",
        "Stage 9.13 Discussion interpretation map has been completed",
        "Stage 9.14 Discussion drafting pass has been completed",
        "Stage 9.15 Methods architecture has been completed",
        "Stage 9.16 Methods drafting pass has been completed",
        "Stage 9.17 software, data, and code availability assembly has been completed",
        "Stage 9.18 Supplementary Methods drafting has been completed",
        "Stage 9.19 Supplementary tables and source-data binding has been completed",
        "Stage 9.20 Reference library and citation audit has been completed",
        "Stage 9.21 Cross-document consistency audit has been completed",
        "Stage 9.22 Statistical and quantitative language audit remains the next unstarted manuscript step",
        "Stage 9. Nature Methods manuscript assembly",
        "PanelForge",
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
        "Stage 7.2 benchmark harness outputs",
        "Stage 7.3 public signaling outputs",
        "Stage 7.4 endpoint, reserve-like, and routed-output outputs",
        "Stage 7.5 held-out validation outputs",
        "Stage 7.6 methods reproducibility outputs",
        "Stage 7.7 usability outputs",
        "Stage 7.8 methods manuscript readiness outputs",
        "Stage 9 scaffold handoff",
        "PanelForge",
    ]:
        if phrase not in stage7_program:
            failures.append(f"Stage 7 methods program is missing phrase: {phrase}")
    for phrase in [
        "strictly serialized",
        "7.0. Planning freeze and evidence source register",
        "7.8. Methods manuscript readiness package",
        "No downstream subphase should begin",
        "Subphase bookkeeping and roadmap updates",
        "Stage 7.2 execution status. Complete",
        "Stage 7.3 execution status. Complete",
        "Stage 7.4 execution status. Complete",
        "Stage 7.5 execution status. Complete",
        "Stage 7.6 execution status. Complete",
        "Stage 7.7 execution status. Complete",
        "Stage 7.8 execution status. Complete",
        "Stage 9 scaffold status. Serialized and followed by Stage 9.0 evidence lock",
        "PanelForge",
    ]:
        if phrase not in stage7_execution:
            failures.append(f"Stage 7 execution plan is missing phrase: {phrase}")

    stage9_docs = [
        (stage9_plan_path, "Stage 9 manuscript assembly plan", ["9.-1", "9.0", "9.1", "9.2", "9.3", "9.4", "9.5", "9.6", "9.6b", "9.7", "9.8", "9.9", "9.10", "9.11", "9.12", "9.13", "9.14", "9.15", "9.16", "9.17", "9.18", "9.19", "9.20", "9.21", "PanelForge", "evidence lock", "Results drafting", "Introduction literature binding", "Discussion drafting", "Methods architecture", "Methods prose", "data availability", "code availability", "Supplementary Methods", "supplementary table/source-data binding", "reference library", "Cross-document consistency"]),
        (stage9_memory_path, "Stage 9 execution memory", ["stage9_21_cross_document_consistency_bound", "9.-1", "9.0", "9.1", "9.2", "9.3", "9.4", "9.5", "9.6", "9.6b", "9.7", "9.8", "9.9", "9.10", "9.11", "9.12", "9.13", "9.14", "9.15", "9.16", "9.17", "9.18", "9.19", "9.20", "9.21", "figure_engine_clone_started", "reference_library_started", "cross_document_consistency_started"]),
        (stage9_checker_path, "Stage 9 scaffold checker", ["FORBIDDEN_DRAFTS", "FORBIDDEN_RENDER_SUFFIXES", "check_stage9_scaffold", "scaffold_only_boundary_preserved"]),
        (stage9_0_runner_path, "Stage 9.0 evidence intake runner", ["stage9_evidence_manifest.csv", "stage9_evidence_lock.md", "No drafting", "PanelForge execution"]),
        (stage9_1_runner_path, "Stage 9.1 venue guidance runner", ["nature_methods_guidance_register.md", "venue_policy_constraints.md", "No representative corpus", "No manuscript sections"]),
        (stage9_2_runner_path, "Stage 9.2 methods-paper corpus runner", ["representative_methods_papers.md", "methods_paper_archetype_analysis.md", "No reference bibliography", "No manuscript sections"]),
        (stage9_3_runner_path, "Stage 9.3 narrative-spine runner", ["stage9_narrative_spine.md", "venue_fit_rationale.md", "No claim freeze", "No manuscript sections"]),
        (stage9_4_runner_path, "Stage 9.4 claim-freeze runner", ["claim_hierarchy.md", "claim_hierarchy.csv", "non_claims_and_scope_boundaries.md", "No paragraph ledger", "No manuscript sections"]),
        (stage9_5_runner_path, "Stage 9.5 paragraph-ledger runner", ["paragraph_claim_ledger.csv", "claim_strength_rules.md", "No manuscript sections", "No manuscript prose"]),
        (stage9_6_runner_path, "Stage 9.6 figure-spine runner", ["main_figure_spine.md", "figure_to_claim_to_artifact.csv", "display_item_plan.md", "No rendered figures"]),
        (stage9_panelforge_preflight_path, "Stage 9.6b PanelForge render harness", ["preflight", "blocked_preconditions", "stage_9_6_gate_passed", "runtime_env_not_committed"]),
        (stage9_7_runner_path, "Stage 9.7 supplementary display runner", ["supplementary_item_plan.md", "supplementary_callout_ledger.csv", "No SI prose", "No manuscript sections"]),
        (stage9_8_runner_path, "Stage 9.8 section contract runner", ["section_contracts.md", "Abstract", "Discussion", "title_options.md", "manuscript prose"]),
        (stage9_9_runner_path, "Stage 9.9 title and abstract runner", ["title_options.md", "abstract_strategy.md", "abstract.md", "150-word", "CLM-0001"]),
        (stage9_10_runner_path, "Stage 9.10 Results architecture runner", ["results_blueprint.md", "FIG-001", "Allowed conclusion", "No Results prose"]),
        (stage9_11_runner_path, "Stage 9.11 Results drafting runner", ["results.md", "Fig. 1a", "PARA-RESULTS-001", "strength_caps_hold"]),
        (stage9_12_runner_path, "Stage 9.12 Introduction literature-binding runner", ["introduction.md", "introduction_citation_ledger.csv", "REF-0001", "review_source_share"]),
        (stage9_13_runner_path, "Stage 9.13 Discussion interpretation-map runner", ["discussion_blueprint.md", "Stage 7 limitations", "map_has_no_subheadings"]),
        (stage9_14_runner_path, "Stage 9.14 Discussion drafting runner", ["discussion.md", "Future directions", "limitations_remain_visible"]),
        (stage9_15_runner_path, "Stage 9.15 Methods architecture runner", ["methods_blueprint.md", "methods_to_code_ledger.csv", "dataset_version=", "methods_to_code_ledger_validates"]),
        (stage9_16_runner_path, "Stage 9.16 Methods drafting runner", ["methods.md", "methods_stmt_ids", "RhoDyn v0.1.0", "No availability statements"]),
        (stage9_17_runner_path, "Stage 9.17 availability assembly runner", ["data_availability.md", "code_availability.md", "reproducibility_command_index.md", "Reporting Summary", "PanelForge"]),
        (stage9_18_runner_path, "Stage 9.18 Supplementary Methods runner", ["supplementary_methods.md", "SUPP-001", "No supplementary tables", "claim_ids_limited_to_claim_freeze"]),
        (stage9_19_runner_path, "Stage 9.19 supplementary table runner", ["supplementary_tables_plan.md", "source_data_binding_ledger.csv", "statistic_ledger.csv", "STAT-0001", "figure-source mapping"]),
        (stage9_20_runner_path, "Stage 9.20 reference-library runner", ["references.bib", "citation_claim_ledger.csv", "reference_audit.md", "reference_count", "retraction"]),
        (stage9_21_runner_path, "Stage 9.21 cross-document consistency runner", ["cross_document_consistency_audit.md", "orphan_claim_set_empty", "orphan_statistic_set_empty", "version_and_strength_coherence_hold", "Stage 9.22"]),
    ]
    for path, label, phrases in stage9_docs:
        if not path.exists():
            failures.append(f"missing {path.relative_to(root)}")
            continue
        body = path.read_text(encoding="utf-8")
        for phrase in phrases:
            if phrase not in body:
                failures.append(f"{label} missing phrase: {phrase}")
    if not stage9_gate_path.exists():
        failures.append("missing manuscript/nature_methods/gate_verdicts/9.-1.json")
    else:
        stage9_gate = json.loads(stage9_gate_path.read_text(encoding="utf-8"))
        if stage9_gate.get("pass") is not True:
            failures.append("Stage 9.-1 scaffold gate must pass")
        if stage9_gate.get("substage") != "9.-1":
            failures.append("Stage 9.-1 scaffold gate must remain bound to substage 9.-1")
    if not stage9_0_gate_path.exists():
        failures.append("missing manuscript/nature_methods/gate_verdicts/9.0.json")
    else:
        stage9_0_gate = json.loads(stage9_0_gate_path.read_text(encoding="utf-8"))
        if stage9_0_gate.get("pass") is not True:
            failures.append("Stage 9.0 evidence-lock gate must pass")
        if stage9_0_gate.get("substage") != "9.0":
            failures.append("Stage 9.0 evidence-lock gate must remain bound to substage 9.0")
    if not stage9_1_gate_path.exists():
        failures.append("missing manuscript/nature_methods/gate_verdicts/9.1.json")
    else:
        stage9_1_gate = json.loads(stage9_1_gate_path.read_text(encoding="utf-8"))
        if stage9_1_gate.get("pass") is not True:
            failures.append("Stage 9.1 venue-guidance gate must pass")
        if stage9_1_gate.get("substage") != "9.1":
            failures.append("Stage 9.1 venue-guidance gate must remain bound to substage 9.1")
    if not stage9_2_gate_path.exists():
        failures.append("missing manuscript/nature_methods/gate_verdicts/9.2.json")
    else:
        stage9_2_gate = json.loads(stage9_2_gate_path.read_text(encoding="utf-8"))
        if stage9_2_gate.get("pass") is not True:
            failures.append("Stage 9.2 methods-paper corpus gate must pass")
        if stage9_2_gate.get("substage") != "9.2":
            failures.append("Stage 9.2 methods-paper corpus gate must remain bound to substage 9.2")
        if stage9_2_gate.get("verified_doi_count") != 8:
            failures.append("Stage 9.2 methods-paper corpus gate must verify eight DOI records")
    if not stage9_3_gate_path.exists():
        failures.append("missing manuscript/nature_methods/gate_verdicts/9.3.json")
    else:
        stage9_3_gate = json.loads(stage9_3_gate_path.read_text(encoding="utf-8"))
        if stage9_3_gate.get("pass") is not True:
            failures.append("Stage 9.3 narrative-spine gate must pass")
        if stage9_3_gate.get("substage") != "9.3":
            failures.append("Stage 9.3 narrative-spine gate must remain bound to substage 9.3")
        if stage9_3_gate.get("content_type") != "Article":
            failures.append("Stage 9.3 narrative-spine gate must preserve Article content type")
    if not stage9_4_gate_path.exists():
        failures.append("missing manuscript/nature_methods/gate_verdicts/9.4.json")
    else:
        stage9_4_gate = json.loads(stage9_4_gate_path.read_text(encoding="utf-8"))
        if stage9_4_gate.get("pass") is not True:
            failures.append("Stage 9.4 claim-freeze gate must pass")
        if stage9_4_gate.get("substage") != "9.4":
            failures.append("Stage 9.4 claim-freeze gate must remain bound to substage 9.4")
        if stage9_4_gate.get("claim_count") != 5:
            failures.append("Stage 9.4 claim-freeze gate must preserve five central claims")
    if not stage9_5_gate_path.exists():
        failures.append("missing manuscript/nature_methods/gate_verdicts/9.5.json")
    else:
        stage9_5_gate = json.loads(stage9_5_gate_path.read_text(encoding="utf-8"))
        if stage9_5_gate.get("pass") is not True:
            failures.append("Stage 9.5 paragraph-ledger gate must pass")
        if stage9_5_gate.get("substage") != "9.5":
            failures.append("Stage 9.5 paragraph-ledger gate must remain bound to substage 9.5")
        if stage9_5_gate.get("paragraph_count", 0) < 10:
            failures.append("Stage 9.5 paragraph-ledger gate must register paragraph rows")
    if not stage9_6_gate_path.exists():
        failures.append("missing manuscript/nature_methods/gate_verdicts/9.6.json")
    else:
        stage9_6_gate = json.loads(stage9_6_gate_path.read_text(encoding="utf-8"))
        if stage9_6_gate.get("pass") is not True:
            failures.append("Stage 9.6 figure-spine gate must pass")
        if stage9_6_gate.get("substage") != "9.6":
            failures.append("Stage 9.6 figure-spine gate must remain bound to substage 9.6")
        if stage9_6_gate.get("main_display_count") != 6:
            failures.append("Stage 9.6 figure-spine gate must register six main display items")
    if not stage9_6b_gate_path.exists():
        failures.append("missing manuscript/nature_methods/gate_verdicts/9.6b.json")
    else:
        stage9_6b_gate = json.loads(stage9_6b_gate_path.read_text(encoding="utf-8"))
        if stage9_6b_gate.get("pass") is not True:
            failures.append("Stage 9.6b PanelForge render gate must pass")
        if stage9_6b_gate.get("substage") != "9.6b":
            failures.append("Stage 9.6b PanelForge render gate must remain bound to substage 9.6b")
        if stage9_6b_gate.get("rendered_file_count") != 18:
            failures.append("Stage 9.6b PanelForge render gate must record 18 rendered files")
    if not stage9_7_gate_path.exists():
        failures.append("missing manuscript/nature_methods/gate_verdicts/9.7.json")
    else:
        stage9_7_gate = json.loads(stage9_7_gate_path.read_text(encoding="utf-8"))
        if stage9_7_gate.get("pass") is not True:
            failures.append("Stage 9.7 supplementary display-plan gate must pass")
        if stage9_7_gate.get("substage") != "9.7":
            failures.append("Stage 9.7 supplementary display-plan gate must remain bound to substage 9.7")
        if stage9_7_gate.get("supplementary_item_count") != 9:
            failures.append("Stage 9.7 supplementary display-plan gate must record nine items")
    if not stage9_8_gate_path.exists():
        failures.append("missing manuscript/nature_methods/gate_verdicts/9.8.json")
    else:
        stage9_8_gate = json.loads(stage9_8_gate_path.read_text(encoding="utf-8"))
        if stage9_8_gate.get("pass") is not True:
            failures.append("Stage 9.8 section-contract gate must pass")
        if stage9_8_gate.get("substage") != "9.8":
            failures.append("Stage 9.8 section-contract gate must remain bound to substage 9.8")
        if stage9_8_gate.get("section_contract_count") != 15:
            failures.append("Stage 9.8 section-contract gate must record fifteen section contracts")
    if not stage9_9_gate_path.exists():
        failures.append("missing manuscript/nature_methods/gate_verdicts/9.9.json")
    else:
        stage9_9_gate = json.loads(stage9_9_gate_path.read_text(encoding="utf-8"))
        if stage9_9_gate.get("pass") is not True:
            failures.append("Stage 9.9 title/abstract gate must pass")
        if stage9_9_gate.get("substage") != "9.9":
            failures.append("Stage 9.9 title/abstract gate must remain bound to substage 9.9")
        if stage9_9_gate.get("abstract_word_count", 999) > 150:
            failures.append("Stage 9.9 abstract must stay within the sourced 150-word budget")
        if stage9_9_gate.get("abstract_unreferenced") is not True:
            failures.append("Stage 9.9 abstract must remain unreferenced")
        if stage9_9_gate.get("title_option_count", 0) < 3:
            failures.append("Stage 9.9 title strategy must contain multiple title options")
    if not stage9_10_gate_path.exists():
        failures.append("missing manuscript/nature_methods/gate_verdicts/9.10.json")
    else:
        stage9_10_gate = json.loads(stage9_10_gate_path.read_text(encoding="utf-8"))
        if stage9_10_gate.get("pass") is not True:
            failures.append("Stage 9.10 Results architecture gate must pass")
        if stage9_10_gate.get("substage") != "9.10":
            failures.append("Stage 9.10 Results architecture gate must remain bound to substage 9.10")
        if stage9_10_gate.get("results_unit_count") != 6:
            failures.append("Stage 9.10 Results architecture gate must record six Results units")
        if stage9_10_gate.get("figure_ids") != ["FIG-001", "FIG-002", "FIG-003", "FIG-004", "FIG-005", "FIG-006"]:
            failures.append("Stage 9.10 Results architecture gate must preserve FIG-001 through FIG-006 order")
    if not stage9_11_gate_path.exists():
        failures.append("missing manuscript/nature_methods/gate_verdicts/9.11.json")
    else:
        stage9_11_gate = json.loads(stage9_11_gate_path.read_text(encoding="utf-8"))
        if stage9_11_gate.get("pass") is not True:
            failures.append("Stage 9.11 Results drafting gate must pass")
        if stage9_11_gate.get("substage") != "9.11":
            failures.append("Stage 9.11 Results drafting gate must remain bound to substage 9.11")
        if stage9_11_gate.get("paragraph_count") != 6:
            failures.append("Stage 9.11 Results drafting gate must record six Results paragraphs")
        if stage9_11_gate.get("next_substage") != "9.12":
            failures.append("Stage 9.11 Results drafting gate must point to Stage 9.12")
    if not stage9_12_gate_path.exists():
        failures.append("missing manuscript/nature_methods/gate_verdicts/9.12.json")
    else:
        stage9_12_gate = json.loads(stage9_12_gate_path.read_text(encoding="utf-8"))
        if stage9_12_gate.get("pass") is not True:
            failures.append("Stage 9.12 Introduction literature-binding gate must pass")
        if stage9_12_gate.get("substage") != "9.12":
            failures.append("Stage 9.12 Introduction literature-binding gate must remain bound to substage 9.12")
        if not (450 <= stage9_12_gate.get("introduction_word_count", 0) <= 650):
            failures.append("Stage 9.12 Introduction word count must remain within contract")
        if stage9_12_gate.get("citation_count") != 11:
            failures.append("Stage 9.12 Introduction must cite eleven resolved reference IDs")
        if stage9_12_gate.get("review_source_share", 1.0) > 0.25:
            failures.append("Stage 9.12 review-source share must remain under threshold")
        if stage9_12_gate.get("next_substage") != "9.13":
            failures.append("Stage 9.12 Introduction literature-binding gate must point to Stage 9.13")
    if not stage9_13_gate_path.exists():
        failures.append("missing manuscript/nature_methods/gate_verdicts/9.13.json")
    else:
        stage9_13_gate = json.loads(stage9_13_gate_path.read_text(encoding="utf-8"))
        if stage9_13_gate.get("pass") is not True:
            failures.append("Stage 9.13 Discussion interpretation-map gate must pass")
        if stage9_13_gate.get("substage") != "9.13":
            failures.append("Stage 9.13 Discussion interpretation-map gate must remain bound to substage 9.13")
        if stage9_13_gate.get("paragraph_count") != 5:
            failures.append("Stage 9.13 Discussion map must record five paragraphs")
        if stage9_13_gate.get("next_substage") != "9.14":
            failures.append("Stage 9.13 Discussion interpretation-map gate must point to Stage 9.14")
    if not stage9_14_gate_path.exists():
        failures.append("missing manuscript/nature_methods/gate_verdicts/9.14.json")
    else:
        stage9_14_gate = json.loads(stage9_14_gate_path.read_text(encoding="utf-8"))
        if stage9_14_gate.get("pass") is not True:
            failures.append("Stage 9.14 Discussion drafting gate must pass")
        if stage9_14_gate.get("substage") != "9.14":
            failures.append("Stage 9.14 Discussion drafting gate must remain bound to substage 9.14")
        if stage9_14_gate.get("paragraph_count") != 5:
            failures.append("Stage 9.14 Discussion drafting gate must record five paragraphs")
        if not (650 <= stage9_14_gate.get("discussion_word_count", 0) <= 900):
            failures.append("Stage 9.14 Discussion word count must remain within contract")
        if stage9_14_gate.get("next_substage") != "9.15":
            failures.append("Stage 9.14 Discussion drafting gate must point to Stage 9.15")
    if not stage9_15_gate_path.exists():
        failures.append("missing manuscript/nature_methods/gate_verdicts/9.15.json")
    else:
        stage9_15_gate = json.loads(stage9_15_gate_path.read_text(encoding="utf-8"))
        if stage9_15_gate.get("pass") is not True:
            failures.append("Stage 9.15 Methods architecture gate must pass")
        if stage9_15_gate.get("substage") != "9.15":
            failures.append("Stage 9.15 Methods architecture gate must remain bound to substage 9.15")
        if stage9_15_gate.get("methods_statement_count", 0) < 6:
            failures.append("Stage 9.15 Methods architecture must record Methods statements")
        if stage9_15_gate.get("methods_subheading_count") != 6:
            failures.append("Stage 9.15 Methods architecture must record six Methods subheadings")
        if stage9_15_gate.get("ledger_row_count") != stage9_15_gate.get("methods_statement_count"):
            failures.append("Stage 9.15 Methods ledger row count must match Methods statement count")
        if stage9_15_gate.get("next_substage") != "9.16":
            failures.append("Stage 9.15 Methods architecture gate must point to Stage 9.16")
    if not stage9_16_gate_path.exists():
        failures.append("missing manuscript/nature_methods/gate_verdicts/9.16.json")
    else:
        stage9_16_gate = json.loads(stage9_16_gate_path.read_text(encoding="utf-8"))
        if stage9_16_gate.get("pass") is not True:
            failures.append("Stage 9.16 Methods drafting gate must pass")
        if stage9_16_gate.get("substage") != "9.16":
            failures.append("Stage 9.16 Methods drafting gate must remain bound to substage 9.16")
        if not (900 <= stage9_16_gate.get("methods_word_count", 0) <= 3000):
            failures.append("Stage 9.16 Methods word count must remain within contract")
        if len(stage9_16_gate.get("methods_statement_ids", [])) != 9:
            failures.append("Stage 9.16 Methods drafting must cover nine Methods statements")
        if stage9_16_gate.get("next_substage") != "9.17":
            failures.append("Stage 9.16 Methods drafting gate must point to Stage 9.17")
    if not stage9_17_gate_path.exists():
        failures.append("missing manuscript/nature_methods/gate_verdicts/9.17.json")
    else:
        stage9_17_gate = json.loads(stage9_17_gate_path.read_text(encoding="utf-8"))
        if stage9_17_gate.get("pass") is not True:
            failures.append("Stage 9.17 availability assembly gate must pass")
        if stage9_17_gate.get("substage") != "9.17":
            failures.append("Stage 9.17 availability assembly gate must remain bound to substage 9.17")
        if stage9_17_gate.get("next_substage") != "9.18":
            failures.append("Stage 9.17 availability assembly gate must point to Stage 9.18")
        if stage9_17_gate.get("software_version") != "v0.1.0":
            failures.append("Stage 9.17 availability assembly must preserve RhoDyn v0.1.0")
        if stage9_17_gate.get("release_commit") != "4b1211cadd1fb3af34a1ec3e21f62383ffd9e368":
            failures.append("Stage 9.17 availability assembly must pin the v0.1.0 release commit")
        if stage9_17_gate.get("software_version_doi") != "10.5281/zenodo.21036616":
            failures.append("Stage 9.17 availability assembly must record the RhoDyn version DOI")
        if stage9_17_gate.get("panel_engine_version_doi") != "10.5281/zenodo.20811171":
            failures.append("Stage 9.17 availability assembly must record the PanelForge version DOI")
        if stage9_17_gate.get("command_count", 0) < 10:
            failures.append("Stage 9.17 availability assembly must record the reproducibility commands")
        if stage9_17_gate.get("reporting_summary_required") is not True:
            failures.append("Stage 9.17 availability assembly must register Reporting Summary as required")
    if not stage9_18_gate_path.exists():
        failures.append("missing manuscript/nature_methods/gate_verdicts/9.18.json")
    else:
        stage9_18_gate = json.loads(stage9_18_gate_path.read_text(encoding="utf-8"))
        if stage9_18_gate.get("pass") is not True:
            failures.append("Stage 9.18 Supplementary Methods gate must pass")
        if stage9_18_gate.get("substage") != "9.18":
            failures.append("Stage 9.18 Supplementary Methods gate must remain bound to substage 9.18")
        if stage9_18_gate.get("next_substage") != "9.19":
            failures.append("Stage 9.18 Supplementary Methods gate must point to Stage 9.19")
        if stage9_18_gate.get("supplementary_methods_section_count") != 7:
            failures.append("Stage 9.18 Supplementary Methods gate must record seven sections")
        if set(stage9_18_gate.get("supp_ids", [])) != {f"SUPP-{idx:03d}" for idx in range(1, 10)}:
            failures.append("Stage 9.18 Supplementary Methods gate must cover SUPP-001 through SUPP-009")
        if set(stage9_18_gate.get("claim_ids", [])) != {"CLM-0001", "CLM-0002", "CLM-0003", "CLM-0004", "CLM-0005"}:
            failures.append("Stage 9.18 Supplementary Methods gate must stay within frozen claim IDs")
    if not stage9_19_gate_path.exists():
        failures.append("missing manuscript/nature_methods/gate_verdicts/9.19.json")
    else:
        stage9_19_gate = json.loads(stage9_19_gate_path.read_text(encoding="utf-8"))
        if stage9_19_gate.get("pass") is not True:
            failures.append("Stage 9.19 supplementary table gate must pass")
        if stage9_19_gate.get("substage") != "9.19":
            failures.append("Stage 9.19 supplementary table gate must remain bound to substage 9.19")
        if stage9_19_gate.get("next_substage") != "9.20":
            failures.append("Stage 9.19 supplementary table gate must point to Stage 9.20")
        if stage9_19_gate.get("table_count") != 9:
            failures.append("Stage 9.19 supplementary table gate must record nine table rows")
        if stage9_19_gate.get("statistic_row_count") != 19:
            failures.append("Stage 9.19 supplementary table gate must record nineteen statistic rows")
        if set(stage9_19_gate.get("table_ids", [])) != {f"STBL-{idx:03d}" for idx in range(1, 10)}:
            failures.append("Stage 9.19 supplementary table gate must cover STBL-001 through STBL-009")
        if set(stage9_19_gate.get("stat_ids", [])) != {f"STAT-{idx:04d}" for idx in range(1, 20)}:
            failures.append("Stage 9.19 supplementary table gate must cover STAT-0001 through STAT-0019")
        if set(stage9_19_gate.get("linked_figures", [])) != {f"FIG-{idx:03d}" for idx in range(1, 7)}:
            failures.append("Stage 9.19 supplementary table gate must bind all six main figures")
    if not stage9_20_gate_path.exists():
        failures.append("missing manuscript/nature_methods/gate_verdicts/9.20.json")
    else:
        stage9_20_gate = json.loads(stage9_20_gate_path.read_text(encoding="utf-8"))
        if stage9_20_gate.get("pass") is not True:
            failures.append("Stage 9.20 reference-library gate must pass")
        if stage9_20_gate.get("substage") != "9.20":
            failures.append("Stage 9.20 reference-library gate must remain bound to substage 9.20")
        if stage9_20_gate.get("next_substage") != "9.21":
            failures.append("Stage 9.20 reference-library gate must point to Stage 9.21")
        if stage9_20_gate.get("reference_count") != 13:
            failures.append("Stage 9.20 reference-library gate must record thirteen references")
        if stage9_20_gate.get("reference_cap") != 50:
            failures.append("Stage 9.20 reference-library gate must preserve the Nature Methods 50-reference cap")
        if set(stage9_20_gate.get("ref_ids", [])) != {f"REF-{idx:04d}" for idx in range(1, 14)}:
            failures.append("Stage 9.20 reference-library gate must cover REF-0001 through REF-0013")
        stage9_20_checks = {
            item.get("name"): item.get("passed")
            for item in stage9_20_gate.get("checks", [])
            if isinstance(item, dict)
        }
        for check_name in ["references_resolve_with_doi", "retraction_checks_clear_or_justified"]:
            if stage9_20_checks.get(check_name) is not True:
                failures.append(f"Stage 9.20 reference-library gate check must pass: {check_name}")
        bib_path = root / "manuscript" / "nature_methods" / "refs" / "references.bib"
        citation_ledger_path = root / "manuscript" / "nature_methods" / "refs" / "citation_claim_ledger.csv"
        reference_audit_path = root / "manuscript" / "nature_methods" / "audits" / "reference_audit.md"
        for output_path in [bib_path, citation_ledger_path, reference_audit_path]:
            if not output_path.exists():
                failures.append(f"missing Stage 9.20 output: {output_path.relative_to(root)}")
        if bib_path.exists():
            bib_text = bib_path.read_text(encoding="utf-8")
            for doi in [
                "10.1038/s41587-019-0071-9",
                "10.5281/zenodo.21036616",
                "10.5281/zenodo.20811171",
            ]:
                if doi not in bib_text:
                    failures.append(f"Stage 9.20 BibTeX is missing DOI {doi}")
        if citation_ledger_path.exists():
            ledger_text = citation_ledger_path.read_text(encoding="utf-8")
            for phrase in ["source_type", "software", "dataset", "methods", "REF-0013"]:
                if phrase not in ledger_text:
                    failures.append(f"Stage 9.20 citation ledger missing phrase: {phrase}")
        if reference_audit_path.exists():
            audit_text = reference_audit_path.read_text(encoding="utf-8")
            for phrase in ["Reference count", "DOI-resolved references", "Retraction-check clear or not applicable"]:
                if phrase not in audit_text:
                    failures.append(f"Stage 9.20 reference audit missing phrase: {phrase}")
    if not stage9_21_gate_path.exists():
        failures.append("missing manuscript/nature_methods/gate_verdicts/9.21.json")
    else:
        stage9_21_gate = json.loads(stage9_21_gate_path.read_text(encoding="utf-8"))
        if stage9_21_gate.get("pass") is not True:
            failures.append("Stage 9.21 cross-document gate must pass")
        if stage9_21_gate.get("substage") != "9.21":
            failures.append("Stage 9.21 cross-document gate must remain bound to substage 9.21")
        if stage9_21_gate.get("next_substage") != "9.22":
            failures.append("Stage 9.21 cross-document gate must point to Stage 9.22")
        expected_counts = {
            "claim_count": 5,
            "figure_count": 6,
            "statistic_count": 19,
            "source_data_table_count": 9,
            "reference_count": 13,
        }
        for field, expected in expected_counts.items():
            if stage9_21_gate.get(field) != expected:
                failures.append(f"Stage 9.21 cross-document gate must record {field}={expected}")
        for field in [
            "orphan_claims",
            "unknown_claim_refs",
            "orphan_figures",
            "unknown_figure_refs",
            "orphan_statistics",
            "unknown_statistic_refs",
            "dangling_references",
            "unknown_paragraph_refs",
            "unknown_table_refs",
            "strength_mismatches",
            "missing_render_paths",
            "bad_engine_rows",
            "missing_source_paths",
            "missing_binding_render_paths",
        ]:
            if stage9_21_gate.get(field) not in ([], None):
                failures.append(f"Stage 9.21 cross-document gate must have empty {field}")
        stage9_21_checks = {
            item.get("name"): item.get("passed")
            for item in stage9_21_gate.get("checks", [])
            if isinstance(item, dict)
        }
        for check_name in [
            "orphan_claim_set_empty",
            "orphan_figure_set_empty",
            "orphan_statistic_set_empty",
            "dangling_reference_set_empty",
            "version_and_strength_coherence_hold",
        ]:
            if stage9_21_checks.get(check_name) is not True:
                failures.append(f"Stage 9.21 cross-document gate check must pass: {check_name}")
        cross_document_audit_path = root / "manuscript" / "nature_methods" / "audits" / "cross_document_consistency_audit.md"
        if not cross_document_audit_path.exists():
            failures.append("missing Stage 9.21 output: manuscript/nature_methods/audits/cross_document_consistency_audit.md")
        else:
            audit_text = cross_document_audit_path.read_text(encoding="utf-8")
            for phrase in ["The cross-document joins passed", "no orphan claims", "Cross-document joins only"]:
                if phrase not in audit_text:
                    failures.append(f"Stage 9.21 cross-document audit missing phrase: {phrase}")

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


    stage7_2_docs = [
        (root / "docs" / "stage7_benchmark_harness_guide.md", "Stage 7.2 benchmark harness guide", ["baseline", "method-validation", "not a new biological demonstration"]),
        (root / "docs" / "stage7_baseline_comparison_report.md", "Stage 7.2 baseline comparison report", ["RhoDyn adds decision value", "stop condition", "not counted as new independent biological demonstrations"]),
        (root / "docs" / "stage7_performance_uncertainty_report.md", "Stage 7.2 performance and uncertainty report", ["Sensitivity outputs", "Performance output", "Failure behavior"]),
    ]
    for path, label, phrases in stage7_2_docs:
        if not path.exists():
            failures.append(f"missing {path.relative_to(root)}")
            continue
        body = path.read_text(encoding="utf-8")
        for phrase in phrases:
            if phrase not in body:
                failures.append(f"{label} missing phrase: {phrase}")

    if not stage7_2_gate_report_path.exists():
        failures.append("missing docs/stage7_2_gate_report.json")
    else:
        stage7_2_gate = json.loads(stage7_2_gate_report_path.read_text(encoding="utf-8"))
        if stage7_2_gate.get("status") != "pass":
            failures.append("Stage 7.2 gate report must pass")
        if stage7_2_gate.get("completion_state") != "complete_benchmark_harness":
            failures.append("Stage 7.2 gate report must record complete_benchmark_harness")
        checkpoints = stage7_2_gate.get("validation_checkpoints", {}) if isinstance(stage7_2_gate.get("validation_checkpoints", {}), dict) else {}
        for checkpoint in [
            "baselines_run_on_same_inputs",
            "synthetic_truth_outcomes_match_known_truth",
            "sensitivity_to_windows_margins_grouping_sample_size_reported",
            "performance_measured_on_representative_sizes",
            "residence_amplitude_disagreement_with_known_truth_detected",
            "negative_or_inconclusive_case_correctly_bounded",
            "public_fixture_benchmarks_run_where_inputs_available",
            "failure_behavior_reported",
        ]:
            if checkpoints.get(checkpoint) != "pass":
                failures.append(f"Stage 7.2 gate checkpoint must pass: {checkpoint}")
        if checkpoints.get("stop_condition_no_added_value_beyond_baselines") != "not_triggered":
            failures.append("Stage 7.2 stop condition must remain not_triggered")

    if not stage7_2_benchmark_report_path.exists():
        failures.append("missing case_studies/stage7_benchmarks/stage7_2_benchmark_report.json")
    else:
        benchmark_report = json.loads(stage7_2_benchmark_report_path.read_text(encoding="utf-8"))
        if benchmark_report.get("status") != "pass":
            failures.append("Stage 7.2 benchmark report must pass")
        if benchmark_report.get("gates", {}).get("stop_condition_no_added_value_beyond_baselines", {}).get("status") != "not_triggered":
            failures.append("Stage 7.2 benchmark report must record stop condition as not_triggered")


    stage7_3_docs = [
        (root / "docs" / "stage7_public_data_adapters.md", "Stage 7.3 public-data adapters", ["drg_calcium_vonbuchholtz2025", "erk_gpcr_wan2021", "Interpretation boundary"]),
        (root / "docs" / "stage7_public_signaling_demonstrations.md", "Stage 7.3 public signaling demonstrations", ["DRG calcium", "ERK GPCR", "What RhoDyn adds"]),
        (root / "notebooks" / "04_stage7_drg_calcium_public_signaling.ipynb", "Stage 7.3 DRG notebook", ["drg_calcium_residence_amplitude_summary.csv", "drg_calcium_tidy_trajectories.csv"]),
        (root / "notebooks" / "05_stage7_erk_gpcr_public_signaling.ipynb", "Stage 7.3 ERK notebook", ["erk_gpcr_residence_amplitude_summary.csv", "erk_gpcr_tidy_trajectories.csv"]),
    ]
    for path, label, phrases in stage7_3_docs:
        if not path.exists():
            failures.append(f"missing {path.relative_to(root)}")
            continue
        body = path.read_text(encoding="utf-8")
        for phrase in phrases:
            if phrase not in body:
                failures.append(f"{label} missing phrase: {phrase}")

    if not stage7_3_gate_report_path.exists():
        failures.append("missing docs/stage7_3_gate_report.json")
    else:
        stage7_3_gate = json.loads(stage7_3_gate_report_path.read_text(encoding="utf-8"))
        if stage7_3_gate.get("status") != "pass":
            failures.append("Stage 7.3 gate report must pass")
        if stage7_3_gate.get("completion_state") != "complete_public_signaling_demonstrations":
            failures.append("Stage 7.3 gate report must record complete_public_signaling_demonstrations")
        checkpoints = stage7_3_gate.get("validation_checkpoints", {}) if isinstance(stage7_3_gate.get("validation_checkpoints", {}), dict) else {}
        for checkpoint in [
            "dataset_source_citation_access_metadata_grouping_preprocessing_notes",
            "each_case_states_what_rhodyn_adds",
            "two_independent_public_live_cell_systems_represented",
            "residence_amplitude_disagreement_detected_in_each_case",
            "examples_do_not_imply_manuscript_generation",
        ]:
            if checkpoints.get(checkpoint) != "pass":
                failures.append(f"Stage 7.3 gate checkpoint must pass: {checkpoint}")
        if checkpoints.get("stop_condition_public_dataset_failure") != "not_triggered":
            failures.append("Stage 7.3 stop condition must remain not_triggered")

    if not stage7_3_public_report_path.exists():
        failures.append("missing case_studies/stage7_public_signaling/stage7_3_public_signaling_gate_report.json")
    else:
        public_report = json.loads(stage7_3_public_report_path.read_text(encoding="utf-8"))
        if public_report.get("status") != "pass":
            failures.append("Stage 7.3 public signaling report must pass")
        selected = set(public_report.get("selected_datasets", []))
        if selected != {"drg_calcium_vonbuchholtz2025", "erk_gpcr_wan2021"}:
            failures.append("Stage 7.3 public signaling report must select DRG calcium and ERK GPCR")



    stage7_4_docs = [
        (root / "docs" / "stage7_endpoint_reserve_routing_demonstrations.md", "Stage 7.4 endpoint reserve routing docs", ["bounded coupling", "reserve-like endpoint", "routed-output", "not live metabolic reserve"]),
        (root / "notebooks" / "06_stage7_endpoint_reserve_routing.ipynb", "Stage 7.4 notebook", ["stage7_4_endpoint_reserve_routing_gate_report.json", "cell_painting_routed_model_comparison.csv", "erk_akt_bounded_coupling_decisions.csv"]),
    ]
    for path, label, phrases in stage7_4_docs:
        if not path.exists():
            failures.append(f"missing {path.relative_to(root)}")
            continue
        body = path.read_text(encoding="utf-8")
        for phrase in phrases:
            if phrase not in body:
                failures.append(f"{label} missing phrase: {phrase}")

    if not stage7_4_gate_report_path.exists():
        failures.append("missing docs/stage7_4_gate_report.json")
    else:
        stage7_4_gate = json.loads(stage7_4_gate_report_path.read_text(encoding="utf-8"))
        if stage7_4_gate.get("status") != "pass":
            failures.append("Stage 7.4 gate report must pass")
        if stage7_4_gate.get("completion_state") != "complete_endpoint_reserve_routing_demonstrations":
            failures.append("Stage 7.4 gate report must record complete_endpoint_reserve_routing_demonstrations")
        checkpoints = stage7_4_gate.get("validation_checkpoints", {}) if isinstance(stage7_4_gate.get("validation_checkpoints", {}), dict) else {}
        for checkpoint in [
            "declared_margins_present_for_bounded_coupling",
            "model_comparisons_include_reduced_alternatives",
            "routed_output_comparison_distinguishes_alternatives",
            "reserve_like_labels_scoped_to_measurement",
            "schema_validation_endpoint_rows",
            "schema_validation_reserve_like_rows",
            "schema_validation_coupling_rows",
            "uncertainty_present_for_reserve_like_coordinate",
            "examples_do_not_imply_manuscript_generation",
        ]:
            if checkpoints.get(checkpoint) != "pass":
                failures.append(f"Stage 7.4 gate checkpoint must pass: {checkpoint}")
        if checkpoints.get("stop_condition_non_trajectory_model_indistinguishable") != "not_triggered":
            failures.append("Stage 7.4 stop condition must remain not_triggered")

    if not stage7_4_case_report_path.exists():
        failures.append("missing case_studies/stage7_endpoint_reserve_routing/stage7_4_endpoint_reserve_routing_gate_report.json")
    else:
        stage7_4_case_report = json.loads(stage7_4_case_report_path.read_text(encoding="utf-8"))
        if stage7_4_case_report.get("status") != "pass":
            failures.append("Stage 7.4 endpoint/reserve/routing report must pass")
        if stage7_4_case_report.get("routing_diagnostics", {}).get("best_model") != "compartment_route_5nn":
            failures.append("Stage 7.4 routed-output report must retain compartment_route_5nn")



    stage7_5_docs = [
        (root / "docs" / "stage7_heldout_validation_report.md", "Stage 7.5 held-out validation docs", ["held-out", "four bounded-coupling pass", "three margin-boundary inconclusive", "not establish biochemical equivalence"]),
        (root / "notebooks" / "07_stage7_heldout_validation.ipynb", "Stage 7.5 notebook", ["heldout_bounded_coupling_decisions.csv", "not imply biochemical equivalence"]),
    ]
    for path, label, phrases in stage7_5_docs:
        if not path.exists():
            failures.append(f"missing {path.relative_to(root)}")
            continue
        body = path.read_text(encoding="utf-8")
        for phrase in phrases:
            if phrase not in body:
                failures.append(f"{label} missing phrase: {phrase}")

    if not stage7_5_gate_report_path.exists():
        failures.append("missing docs/stage7_5_gate_report.json")
    else:
        stage7_5_gate = json.loads(stage7_5_gate_report_path.read_text(encoding="utf-8"))
        if stage7_5_gate.get("status") != "pass":
            failures.append("Stage 7.5 gate report must pass")
        if stage7_5_gate.get("completion_state") != "complete_external_heldout_validation":
            failures.append("Stage 7.5 gate report must record complete_external_heldout_validation")
        if stage7_5_gate.get("pass_context_count") != 4 or stage7_5_gate.get("inconclusive_context_count") != 3:
            failures.append("Stage 7.5 gate report must preserve four pass contexts and three inconclusive contexts")
        checkpoints = stage7_5_gate.get("validation_checkpoints", {}) if isinstance(stage7_5_gate.get("validation_checkpoints", {}), dict) else {}
        for checkpoint in [
            "stage7_3_and_7_4_prerequisites_complete",
            "heldout_analysis_plan_fixed_before_outputs",
            "public_access_reviewable",
            "schema_validation_tidy_trajectories",
            "schema_validation_coupling_rows",
            "fixed_windows_margins_baselines_grouping_recorded",
            "no_hidden_tuning_after_result",
            "pass_fail_inconclusive_outcomes_visible",
            "controlled_access_constraints_documented",
            "evidence_set_decision_recorded",
        ]:
            if checkpoints.get(checkpoint) != "pass":
                failures.append(f"Stage 7.5 gate checkpoint must pass: {checkpoint}")
        if stage7_5_gate.get("stop_condition_access_restriction") != "not_triggered":
            failures.append("Stage 7.5 access stop condition must remain not_triggered")

    if not stage7_5_case_report_path.exists():
        failures.append("missing case_studies/stage7_heldout_validation/stage7_5_heldout_validation_gate_report.json")
    else:
        stage7_5_case_report = json.loads(stage7_5_case_report_path.read_text(encoding="utf-8"))
        if stage7_5_case_report.get("status") != "pass":
            failures.append("Stage 7.5 held-out validation report must pass")
        if stage7_5_case_report.get("evidence_set_decision") != "scoped_heldout_boundary_validation":
            failures.append("Stage 7.5 held-out validation report must keep the scoped evidence-set decision")

    stage7_6_docs = [
        (root / "docs" / "stage7_6_api_stability_policy.md", "Stage 7.6 API stability policy", ["Stable method surfaces", "Deprecation policy", "Cross-surface parity rule"]),
        (root / "docs" / "stage7_methods_reproducibility_card.md", "Stage 7.6 methods reproducibility card", ["Stage 7.6 hardens", "Regenerated output comparison", "Cross-surface parity"]),
    ]
    for path, label, phrases in stage7_6_docs:
        if not path.exists():
            failures.append(f"missing {path.relative_to(root)}")
            continue
        body = path.read_text(encoding="utf-8")
        for phrase in phrases:
            if phrase not in body:
                failures.append(f"{label} missing phrase: {phrase}")

    if not stage7_6_gate_report_path.exists():
        failures.append("missing docs/stage7_6_gate_report.json")
    else:
        stage7_6_gate = json.loads(stage7_6_gate_report_path.read_text(encoding="utf-8"))
        if stage7_6_gate.get("status") != "pass":
            failures.append("Stage 7.6 gate report must pass")
        if stage7_6_gate.get("completion_state") != "complete_methods_reproducibility_hardening":
            failures.append("Stage 7.6 gate report must record complete_methods_reproducibility_hardening")
        checkpoints = stage7_6_gate.get("validation_checkpoints", {}) if isinstance(stage7_6_gate.get("validation_checkpoints", {}), dict) else {}
        for checkpoint in [
            "fresh_environment_reproduces_benchmark_tables",
            "tutorial_outputs_execute",
            "public_release_scan_finds_no_private_paths_or_secrets",
            "frontend_backend_cli_python_outputs_agree",
            "ci_covers_selected_examples_docs_notebooks_benchmarks_package_docker_frontend",
            "clean_room_reproduction_from_release_archive",
        ]:
            if checkpoints.get(checkpoint) != "pass":
                failures.append(f"Stage 7.6 gate checkpoint must pass: {checkpoint}")
        if checkpoints.get("stop_condition_clean_room_failure") != "not_triggered":
            failures.append("Stage 7.6 clean-room stop condition must remain not_triggered")

    if not stage7_6_case_report_path.exists():
        failures.append("missing case_studies/stage7_methods_reproducibility/stage7_6_methods_reproducibility_gate_report.json")
    else:
        stage7_6_case_report = json.loads(stage7_6_case_report_path.read_text(encoding="utf-8"))
        if stage7_6_case_report.get("status") != "pass":
            failures.append("Stage 7.6 methods reproducibility report must pass")
        if stage7_6_case_report.get("mode") != "full_release_archive":
            failures.append("Stage 7.6 methods reproducibility report must come from full release-archive mode")

    stage7_7_docs = [
        (root / "docs" / "stage7_usability_rehearsal.md", "Stage 7.7 usability rehearsal", ["public MLCI", "bounded-coupling fixture", "does not add a new biological system"]),
        (root / "docs" / "stage7_user_path_findings.md", "Stage 7.7 user-path findings", ["Biologist residence task", "Quantitative bounded-coupling task", "Python, CLI, and backend"]),
    ]
    for path, label, phrases in stage7_7_docs:
        if not path.exists():
            failures.append(f"missing {path.relative_to(root)}")
            continue
        body = path.read_text(encoding="utf-8")
        for phrase in phrases:
            if phrase not in body:
                failures.append(f"{label} missing phrase: {phrase}")

    if not stage7_7_gate_report_path.exists():
        failures.append("missing docs/stage7_7_gate_report.json")
    else:
        stage7_7_gate = json.loads(stage7_7_gate_report_path.read_text(encoding="utf-8"))
        if stage7_7_gate.get("status") != "pass":
            failures.append("Stage 7.7 gate report must pass")
        if stage7_7_gate.get("completion_state") != "complete_usability_adoption_rehearsal":
            failures.append("Stage 7.7 gate report must record complete_usability_adoption_rehearsal")
        checkpoints = stage7_7_gate.get("validation_checkpoints", {}) if isinstance(stage7_7_gate.get("validation_checkpoints", {}), dict) else {}
        for checkpoint in [
            "stage7_6_prerequisite_complete",
            "biologist_task_reaches_interpretable_decision",
            "quantitative_user_reproduces_cli_python_backend_output",
            "workbench_public_tutorial_flow_present",
            "exports_include_parameters_schema_grouping_version",
            "tutorial_or_interface_fixes_preserve_analysis_contract",
            "no_unvalidated_analysis_routes_added",
        ]:
            if checkpoints.get(checkpoint) != "pass":
                failures.append(f"Stage 7.7 gate checkpoint must pass: {checkpoint}")
        if checkpoints.get("stop_condition_user_cannot_interpret_result") != "not_triggered":
            failures.append("Stage 7.7 user-path stop condition must remain not_triggered")

    if not stage7_7_case_report_path.exists():
        failures.append("missing case_studies/stage7_usability_rehearsal/stage7_7_usability_gate_report.json")
    else:
        stage7_7_case_report = json.loads(stage7_7_case_report_path.read_text(encoding="utf-8"))
        if stage7_7_case_report.get("status") != "pass":
            failures.append("Stage 7.7 usability case report must pass")
        if stage7_7_case_report.get("completion_state") != "complete_usability_adoption_rehearsal":
            failures.append("Stage 7.7 usability case report must record complete_usability_adoption_rehearsal")

    stage7_8_docs = [
        (root / "docs" / "stage7_methods_evidence_index.md", "Stage 7.8 methods evidence index", ["Figure-level evidence", "Claim-level evidence", "does not add analyses or biological claims"]),
        (root / "docs" / "stage7_figure_artifact_crosswalk.md", "Stage 7.8 figure-artifact crosswalk", ["reproducible output", "limitation boundary"]),
        (root / "docs" / "stage7_claim_evidence_crosswalk.md", "Stage 7.8 claim-evidence crosswalk", ["limitation artifact", "supported_for_methods_drafting"]),
        (root / "docs" / "stage7_methods_submission_readiness.md", "Stage 7.8 submission readiness", ["Known inconclusive cases are visible", "does not add a biological system"]),
    ]
    for path, label, phrases in stage7_8_docs:
        if not path.exists():
            failures.append(f"missing {path.relative_to(root)}")
            continue
        body = path.read_text(encoding="utf-8")
        for phrase in phrases:
            if phrase not in body:
                failures.append(f"{label} missing phrase: {phrase}")

    if not stage7_8_gate_report_path.exists():
        failures.append("missing docs/stage7_8_gate_report.json")
    else:
        stage7_8_gate = json.loads(stage7_8_gate_report_path.read_text(encoding="utf-8"))
        if stage7_8_gate.get("status") != "pass":
            failures.append("Stage 7.8 gate report must pass")
        if stage7_8_gate.get("completion_state") != "complete_methods_manuscript_readiness_package":
            failures.append("Stage 7.8 gate report must record complete_methods_manuscript_readiness_package")
        checkpoints = stage7_8_gate.get("validation_checkpoints", {}) if isinstance(stage7_8_gate.get("validation_checkpoints", {}), dict) else {}
        for checkpoint in [
            "stages_7_1_to_7_7_gates_pass",
            "all_planned_figures_have_artifacts",
            "all_planned_claims_have_evidence_and_limitations",
            "known_inconclusive_contexts_visible",
            "release_checksums_and_archive_manifest_present",
            "nature_methods_not_used_as_acceptance_claim",
        ]:
            if checkpoints.get(checkpoint) != "pass":
                failures.append(f"Stage 7.8 gate checkpoint must pass: {checkpoint}")
        if checkpoints.get("stop_condition_unlinked_claim_or_figure") != "not_triggered":
            failures.append("Stage 7.8 unlinked-claim stop condition must remain not_triggered")

    if not stage7_8_case_report_path.exists():
        failures.append("missing case_studies/stage7_methods_readiness/stage7_8_methods_readiness_gate_report.json")
    else:
        stage7_8_case_report = json.loads(stage7_8_case_report_path.read_text(encoding="utf-8"))
        if stage7_8_case_report.get("status") != "pass":
            failures.append("Stage 7.8 methods readiness case report must pass")
        if stage7_8_case_report.get("completion_state") != "complete_methods_manuscript_readiness_package":
            failures.append("Stage 7.8 methods readiness case report must record complete_methods_manuscript_readiness_package")

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
        warnings.append("Stage 7.8 methods manuscript readiness package is complete; Stage 8 remains conceptual")
    warnings.append("Stage 9.21 cross-document consistency audit is registered; statistical-language audit, figure legends, full manuscript assembly, and final package assembly have not started")

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

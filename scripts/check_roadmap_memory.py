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
    if current.get("active_stage") != "Stage 7.5 external or held-out biological validation complete":
        failures.append("active stage must be Stage 7.5 external or held-out biological validation complete after Stage 7.5 execution")

    stages = {entry.get("stage"): entry for entry in memory.get("stage_lock", []) if isinstance(entry, dict)}
    expected_status = {
        3: "complete_for_current_gate",
        4: "frozen_for_stage5",
        5: "completed",
        6: "public_citable_v0.1.0",
        7: "stage7_5_complete_7_6_not_started",
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
    if stage7_subphase_status.get("7.2") != "complete_benchmark_harness":
        failures.append("Stage 7.2 must be marked complete_benchmark_harness")
    if stage7_subphase_status.get("7.3") != "complete_public_signaling_demonstrations":
        failures.append("Stage 7.3 must be marked complete_public_signaling_demonstrations")
    if stage7_subphase_status.get("7.4") != "complete_endpoint_reserve_routing_demonstrations":
        failures.append("Stage 7.4 must be marked complete_endpoint_reserve_routing_demonstrations")
    if stage7_subphase_status.get("7.5") != "complete_external_heldout_validation":
        failures.append("Stage 7.5 must be marked complete_external_heldout_validation")
    if stage7_subphase_status.get("7.6") != "not_started_next_authorization_required":
        failures.append("Stage 7.6 must remain not_started_next_authorization_required")

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
        "Stage 7.2 benchmark harness outputs",
        "Stage 7.3 public signaling outputs",
        "Stage 7.4 endpoint, reserve-like, and routed-output outputs",
        "Stage 7.5 held-out validation outputs",
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
        warnings.append("Stage 7.5 external or held-out validation is complete; Stage 7.6 software maturity has not started")

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

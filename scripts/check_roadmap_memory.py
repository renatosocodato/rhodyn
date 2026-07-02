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
    if current.get("active_stage") != "Stage 9.7 supplementary display planning registered; manuscript production not started":
        failures.append("active stage must record the Stage 9.7 supplementary display-planning boundary")

    stages = {entry.get("stage"): entry for entry in memory.get("stage_lock", []) if isinstance(entry, dict)}
    expected_status = {
        3: "complete_for_current_gate",
        4: "frozen_for_stage5",
        5: "completed",
        6: "public_citable_v0.1.0",
        7: "stage7_8_complete_methods_readiness",
        8: "conceptual_only",
        9: "stage9_7_supplementary_display_plan_registered",
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
    for entry in stage9_substages:
        if isinstance(entry, dict) and entry.get("id") not in {"9.-1", "9.0", "9.1", "9.2", "9.3", "9.4", "9.5", "9.6", "9.6b", "9.7"} and entry.get("status") != "not_started":
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
        "Stage 9.8 section contract blueprint remains the next unstarted manuscript step",
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
        (stage9_plan_path, "Stage 9 manuscript assembly plan", ["9.-1", "9.0", "9.1", "9.2", "9.3", "9.4", "9.5", "9.6", "9.6b", "9.7", "PanelForge", "evidence lock", "manuscript drafting"]),
        (stage9_memory_path, "Stage 9 execution memory", ["stage9_7_supplementary_display_plan_registered", "9.-1", "9.0", "9.1", "9.2", "9.3", "9.4", "9.5", "9.6", "9.6b", "9.7", "figure_engine_clone_started"]),
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
    warnings.append("Stage 9.7 supplementary display planning is registered; manuscript production, citation resolution, section contracts, and drafting have not started")

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

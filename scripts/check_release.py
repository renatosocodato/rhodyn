"""Release-safety checks for the private RhoDyn package."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REQUIRED_FILES = [
    "README.md",
    "LICENSE",
    "NOTICE",
    "CITATION.cff",
    "CHANGELOG.md",
    "CONTRIBUTING.md",
    "REPRODUCING.md",
    "pyproject.toml",
    ".zenodo.json",
    "docs/roadmap.md",
    "docs/roadmap_execution_memory.json",
    "mkdocs.yml",
    "docs/index.md",
    "docs/api_reference.md",
    "docs/cli_reference.md",
    "docs/input_schema_guide.md",
    "docs/interpretation_guide.md",
    "docs/reproducibility_card.md",
    "docs/clean_room_reproducibility.md",
    "docs/clean_room_reproducibility_report.md",
    "docs/release_notes_v0.1.0.md",
    "docs/release_checksums.csv",
    "docs/release_checksums.json",
    "docs/final_release_hardening.md",
    "docs/pypi_dry_run_report.json",
    "docs/pypi_dry_run_report.md",
    "docs/zenodo_dry_run_report.json",
    "docs/zenodo_dry_run_report.md",
    "docs/zenodo_publication_report.json",
    "docs/public_release_integrity_report.json",
    "docs/public_release_integrity_report.md",
    "docs/broken_link_scan_report.json",
    "docs/broken_link_scan_report.md",
    "docs/dependency_review_report.json",
    "docs/dependency_review_report.md",
    "docs/docker_smoke_audit_report.json",
    "docs/screenshot_regression_report.json",
    "docs/screenshot_regression_report.md",
    "scripts/audit_stage4_service_contract.py",
    "scripts/audit_stage4_upload_stress.py",
    "scripts/audit_stage4_docker_smoke.py",
    "scripts/freeze_stage4_api_contract.py",
    "scripts/audit_stage5_frontend_scaffold.py",
    "scripts/audit_stage5_premium_workbench.py",
    "scripts/audit_stage5_upload_flow_parity.py",
    "scripts/audit_stage5_simulation_workbench.py",
    "scripts/audit_phase6_release_readiness.py",
    "scripts/write_release_checksums.py",
    "scripts/run_clean_room_reproducibility.py",
    "scripts/pypi_dry_run.py",
    "scripts/zenodo_dry_run.py",
    "scripts/check_public_release_integrity.py",
    "scripts/check_docs_links.py",
    "scripts/check_dependency_security.py",
    "scripts/run_stage5_screenshot_regression.py",
    "package.json",
    "package-lock.json",
    "playwright.config.mjs",
    "tests/playwright/stage5.visual.spec.mjs",
    "api/stage4/openapi.json",
    "api/stage4/frontend_contract.json",
    "api/stage4/contract_manifest.json",
    "docs/stage4_closeout.md",
    "docs/stage5_frontend.md",
    "docs/stage5_closeout.md",
    "docs/stage7_serialized_execution_plan.md",
    "docs/stage7_0_source_register.md",
    "docs/stage7_0_baseline_method_inventory.md",
    "docs/stage7_0_dataset_selection_rubric.md",
    "docs/stage7_0_artifact_map.md",
    "docs/stage7_0_gate_report.json",
    "docs/stage7_methods_program.md",
    "docs/stage7_method_specification.md",
    "docs/stage7_synthetic_truth_cases.md",
    "docs/stage7_limitations_matrix.md",
    "docs/stage7_api_stability_notes.md",
    "docs/stage7_1_gate_report.json",
    "scripts/build_stage7_1_synthetic_truth_cases.py",
    "tests/test_stage7_1_synthetic_truth.py",
    "case_studies/stage7_synthetic_truth/stage7_1_synthetic_truth_report.json",
    "case_studies/stage7_synthetic_truth/trajectory_positive_residence.csv",
    "case_studies/stage7_synthetic_truth/trajectory_counterexample_amplitude_only.csv",
    "case_studies/stage7_synthetic_truth/trajectory_ambiguous_window_edge.csv",
    "case_studies/stage7_synthetic_truth/coupling_interval_cases.csv",
    "case_studies/stage7_synthetic_truth/endpoint_positive_routed_best.csv",
    "docs/stage7_benchmark_harness_guide.md",
    "docs/stage7_baseline_comparison_report.md",
    "docs/stage7_performance_uncertainty_report.md",
    "docs/stage7_2_gate_report.json",
    "scripts/run_stage7_2_benchmark_harness.py",
    "tests/test_stage7_2_benchmarks.py",
    "case_studies/stage7_benchmarks/stage7_2_benchmark_report.json",
    "case_studies/stage7_benchmarks/synthetic_residence_baseline_comparison.csv",
    "case_studies/stage7_benchmarks/window_sensitivity_summary.csv",
    "case_studies/stage7_benchmarks/synthetic_coupling_baseline_comparison.csv",
    "case_studies/stage7_benchmarks/margin_sensitivity_summary.csv",
    "case_studies/stage7_benchmarks/synthetic_model_baseline_comparison.csv",
    "case_studies/stage7_benchmarks/synthetic_reserve_baseline_comparison.csv",
    "case_studies/stage7_benchmarks/grouping_sample_size_sensitivity.csv",
    "case_studies/stage7_benchmarks/performance_summary.csv",
    "case_studies/stage7_benchmarks/public_fixture_benchmark_summary.csv",
    "case_studies/stage7_benchmarks/failure_behavior_summary.csv",
    "case_studies/stage7_benchmarks/invalid_trajectory_missing_time.csv",
    "docs/stage7_public_data_adapters.md",
    "docs/stage7_public_signaling_demonstrations.md",
    "docs/stage7_3_gate_report.json",
    "scripts/run_stage7_3_public_signaling.py",
    "tests/test_stage7_3_public_signaling.py",
    "notebooks/04_stage7_drg_calcium_public_signaling.ipynb",
    "notebooks/05_stage7_erk_gpcr_public_signaling.ipynb",
    "case_studies/stage7_public_signaling/candidate_ranking.tsv",
    "case_studies/stage7_public_signaling/public_signaling_case_summary.tsv",
    "case_studies/stage7_public_signaling/drg_calcium_tidy_trajectories.csv",
    "case_studies/stage7_public_signaling/drg_calcium_residence_amplitude_summary.csv",
    "case_studies/stage7_public_signaling/drg_calcium_window_sensitivity.csv",
    "case_studies/stage7_public_signaling/drg_calcium_uncertainty_summary.csv",
    "case_studies/stage7_public_signaling/drg_calcium_provenance.json",
    "case_studies/stage7_public_signaling/drg_calcium_case_report.md",
    "case_studies/stage7_public_signaling/erk_gpcr_tidy_trajectories.csv",
    "case_studies/stage7_public_signaling/erk_gpcr_residence_amplitude_summary.csv",
    "case_studies/stage7_public_signaling/erk_gpcr_window_sensitivity.csv",
    "case_studies/stage7_public_signaling/erk_gpcr_uncertainty_summary.csv",
    "case_studies/stage7_public_signaling/erk_gpcr_provenance.json",
    "case_studies/stage7_public_signaling/erk_gpcr_case_report.md",
    "case_studies/stage7_public_signaling/stage7_3_public_signaling_gate_report.json",
    "docs/stage7_endpoint_reserve_routing_demonstrations.md",
    "docs/stage7_4_gate_report.json",
    "scripts/run_stage7_4_endpoint_reserve_routing.py",
    "tests/test_stage7_4_endpoint_reserve_routing.py",
    "notebooks/06_stage7_endpoint_reserve_routing.ipynb",
    "case_studies/stage7_endpoint_reserve_routing/candidate_ranking.tsv",
    "case_studies/stage7_endpoint_reserve_routing/stage7_4_case_summary.tsv",
    "case_studies/stage7_endpoint_reserve_routing/cell_painting_tidy_endpoint_model_rows.csv",
    "case_studies/stage7_endpoint_reserve_routing/cell_painting_routed_model_comparison.csv",
    "case_studies/stage7_endpoint_reserve_routing/cell_painting_reduced_alternative_decisions.tsv",
    "case_studies/stage7_endpoint_reserve_routing/cell_painting_reserve_like_endpoint_rows.csv",
    "case_studies/stage7_endpoint_reserve_routing/cell_painting_reserve_like_model_summary.csv",
    "case_studies/stage7_endpoint_reserve_routing/cell_painting_reserve_like_uncertainty.csv",
    "case_studies/stage7_endpoint_reserve_routing/erk_akt_bounded_coupling_decisions.csv",
    "case_studies/stage7_endpoint_reserve_routing/stage7_4_endpoint_reserve_routing_gate_report.json",
    "case_studies/stage7_endpoint_reserve_routing/stage7_4_provenance.json",
    "case_studies/stage7_endpoint_reserve_routing/stage7_4_case_report.md",
    "case_studies/stage7_endpoint_reserve_routing/cell_painting_endpoint_reserve_routing_report.md",
    "case_studies/stage7_endpoint_reserve_routing/erk_akt_bounded_coupling_stage7_4_report.md",
    "docs/stage7_heldout_validation_report.md",
    "docs/stage7_5_gate_report.json",
    "scripts/run_stage7_5_heldout_validation.py",
    "tests/test_stage7_5_heldout_validation.py",
    "notebooks/07_stage7_heldout_validation.ipynb",
    "case_studies/stage7_heldout_validation/candidate_ranking.tsv",
    "case_studies/stage7_heldout_validation/heldout_analysis_plan.json",
    "case_studies/stage7_heldout_validation/heldout_analysis_plan.md",
    "case_studies/stage7_heldout_validation/heldout_paired_reporter_tidy_trajectories.csv",
    "case_studies/stage7_heldout_validation/heldout_residence_summary.csv",
    "case_studies/stage7_heldout_validation/heldout_bounded_coupling_decisions.csv",
    "case_studies/stage7_heldout_validation/heldout_margin_sensitivity.csv",
    "case_studies/stage7_heldout_validation/heldout_validation_outcomes.tsv",
    "case_studies/stage7_heldout_validation/stage7_5_heldout_validation_gate_report.json",
    "case_studies/stage7_heldout_validation/stage7_5_provenance.json",
    "case_studies/stage7_heldout_validation/stage7_5_heldout_validation_report.md",
    "case_studies/stage7_heldout_validation/controlled_access_note.md",
    "docs/stage7_6_api_stability_policy.md",
    "docs/stage7_methods_reproducibility_card.md",
    "docs/stage7_6_gate_report.json",
    "docs/stage7_6_clean_room_report.json",
    "scripts/run_stage7_6_methods_reproducibility.py",
    "case_studies/stage7_methods_reproducibility/methods_reproducibility_commands.tsv",
    "case_studies/stage7_methods_reproducibility/methods_output_comparison.tsv",
    "case_studies/stage7_methods_reproducibility/cross_surface_parity.tsv",
    "case_studies/stage7_methods_reproducibility/stage7_6_methods_reproducibility_gate_report.json",
    "case_studies/stage7_methods_reproducibility/stage7_6_methods_reproducibility_report.md",
    "docs/stage5_public_mlci_workflow.md",
    "frontend/stage5/index.html",
    "frontend/stage5/styles.css",
    "frontend/stage5/app.js",
    "examples/mlci_public_intensity_trajectory.csv",
]
LEAK_PATTERNS = [
    re.compile("/" + "Users/"),
    re.compile("/" + "Volumes/"),
    re.compile("Library/" + "LaunchAgents"),
    re.compile(r"sk-[A-Za-z0-9]"),
    re.compile("ghp" + r"_[A-Za-z0-9_]+"),
    re.compile("github" + r"_pat_[A-Za-z0-9_]+"),
    re.compile(r"xox[baprs]-[A-Za-z0-9-]+"),
]
RAW_EXTENSIONS = {".lif", ".czi", ".nd2", ".oir", ".oib", ".lsm", ".tif", ".tiff", ".prism", ".xml"}
GENERATED_DIRS = {"dist", "build", "htmlcov", ".pytest_cache", "node_modules", "playwright-report", "test-results", "blob-report"}


def _text_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for path in root.rglob("*"):
        if ".git" in path.parts or not path.is_file():
            continue
        if any(part in GENERATED_DIRS for part in path.parts):
            continue
        if path.suffix.lower() in {
            ".py",
            ".md",
            ".toml",
            ".yml",
            ".yaml",
            ".cff",
            ".txt",
            ".json",
            ".html",
            ".css",
            ".js",
            ".csv",
            ".in",
            ".ipynb",
            ".example",
            ".Dockerfile",
        }:
            files.append(path)
    return files


def _tracked_paths(root: Path) -> set[str] | None:
    try:
        result = subprocess.run(
            ["git", "ls-files"],
            cwd=root,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return None
    return {line.strip() for line in result.stdout.splitlines() if line.strip()}


def _tracked_or_unknown(rel: Path, tracked: set[str] | None) -> bool:
    if tracked is None:
        return True
    rel_text = rel.as_posix()
    prefix = rel_text.rstrip("/") + "/"
    return rel_text in tracked or any(path.startswith(prefix) for path in tracked)


def check_release(root: Path = ROOT) -> dict[str, object]:
    failures: list[str] = []
    warnings: list[str] = []
    tracked = _tracked_paths(root)

    for name in REQUIRED_FILES:
        if not (root / name).exists():
            failures.append(f"missing required release file: {name}")

    pyproject = (root / "pyproject.toml").read_text(encoding="utf-8") if (root / "pyproject.toml").exists() else ""
    if 'version = "0.1.0"' not in pyproject:
        failures.append("pyproject.toml does not declare version 0.1.0")
    if "dependencies = []" not in pyproject:
        failures.append("core dependencies are not empty")
    if "[project.optional-dependencies]" not in pyproject:
        failures.append("optional dependency groups are not declared")

    readme = (root / "README.md").read_text(encoding="utf-8") if (root / "README.md").exists() else ""
    if "The manuscript was not generated with RhoDyn" not in readme:
        failures.append("README does not preserve manuscript independence boundary")
    if "optional reference case study" not in readme:
        failures.append("README does not describe the manuscript package as an optional case study")

    memory_path = root / "docs" / "roadmap_execution_memory.json"
    gate_path = root / "case_studies" / "stage3_case_study_bank_gate_report.json"
    if memory_path.exists():
        try:
            memory = json.loads(memory_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            failures.append(f"roadmap execution memory is not valid JSON: {exc}")
            memory = {}
        current = memory.get("current_position", {}) if isinstance(memory, dict) else {}
        if current.get("active_stage") != "Stage 7.6 software maturity for methods-paper reproducibility complete":
            failures.append("roadmap execution memory does not mark Stage 7.6 software maturity for methods-paper reproducibility as complete")
        stages = {entry.get("stage"): entry for entry in memory.get("stage_lock", []) if isinstance(entry, dict)}
        if stages.get(3, {}).get("status") != "complete_for_current_gate":
            failures.append("roadmap execution memory does not keep Stage 3 complete for the current gate")
        if stages.get(4, {}).get("status") != "frozen_for_stage5":
            failures.append("roadmap execution memory does not mark Stage 4 frozen for Stage 5")
        if stages.get(5, {}).get("status") != "completed":
            failures.append("roadmap execution memory does not mark Stage 5 completed")
        if stages.get(6, {}).get("status") != "public_citable_v0.1.0":
            failures.append("roadmap execution memory does not mark Stage 6 as public_citable_v0.1.0")
        if stages.get(7, {}).get("status") != "stage7_6_complete_7_7_not_started":
            failures.append("roadmap execution memory does not mark Stage 7.6 complete and Stage 7.7 not started")
        if stages.get(8, {}).get("status") != "conceptual_only":
            failures.append("roadmap execution memory does not keep Stage 8 conceptual only")

        stage7 = stages.get(7, {})
        subphases = stage7.get("subphases", []) if isinstance(stage7, dict) else []
        subphase_status = {entry.get("id"): entry.get("status") for entry in subphases if isinstance(entry, dict)}
        if subphase_status.get("7.0") != "complete_planning_only":
            failures.append("Stage 7.0 must be complete_planning_only in roadmap execution memory")
        if subphase_status.get("7.1") != "complete_method_formalization":
            failures.append("Stage 7.1 must be complete_method_formalization in roadmap execution memory")
        if subphase_status.get("7.2") != "complete_benchmark_harness":
            failures.append("Stage 7.2 must be complete_benchmark_harness in roadmap execution memory")
        if subphase_status.get("7.3") != "complete_public_signaling_demonstrations":
            failures.append("Stage 7.3 must be complete_public_signaling_demonstrations in roadmap execution memory")
        if subphase_status.get("7.4") != "complete_endpoint_reserve_routing_demonstrations":
            failures.append("Stage 7.4 must be complete_endpoint_reserve_routing_demonstrations in roadmap execution memory")
        if subphase_status.get("7.5") != "complete_external_heldout_validation":
            failures.append("Stage 7.5 must be complete_external_heldout_validation in roadmap execution memory")
        if subphase_status.get("7.6") != "complete_methods_reproducibility_hardening":
            failures.append("Stage 7.6 must be complete_methods_reproducibility_hardening in roadmap execution memory")
        if subphase_status.get("7.7") != "not_started_next_authorization_required":
            failures.append("Stage 7.7 must remain not started and require authorization")
    if gate_path.exists():
        try:
            gate = json.loads(gate_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            failures.append(f"Stage 3 gate report is not valid JSON: {exc}")
            gate = {}
        if gate.get("status") != "pass":
            failures.append("Stage 3 case-study gate report does not pass")
        boundary = str(gate.get("interpretation_boundary", ""))
        if "do not imply that RhoDyn generated" not in boundary:
            failures.append("Stage 3 gate report does not preserve manuscript-independence boundary")

    stage7_gate_path = root / "docs" / "stage7_0_gate_report.json"
    if stage7_gate_path.exists():
        try:
            stage7_gate = json.loads(stage7_gate_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            failures.append(f"Stage 7.0 gate report is not valid JSON: {exc}")
            stage7_gate = {}
        if stage7_gate.get("status") != "pass":
            failures.append("Stage 7.0 gate report does not pass")
        if stage7_gate.get("software_implementation_started") or stage7_gate.get("scientific_implementation_started") or stage7_gate.get("manuscript_drafting_started"):
            failures.append("Stage 7.0 gate report must remain planning-only")


    stage7_1_gate_path = root / "docs" / "stage7_1_gate_report.json"
    if stage7_1_gate_path.exists():
        try:
            stage7_1_gate = json.loads(stage7_1_gate_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            failures.append(f"Stage 7.1 gate report is not valid JSON: {exc}")
            stage7_1_gate = {}
        if stage7_1_gate.get("status") != "pass":
            failures.append("Stage 7.1 gate report does not pass")
        if stage7_1_gate.get("completion_state") != "complete_method_formalization":
            failures.append("Stage 7.1 gate report does not mark method formalization complete")
        if stage7_1_gate.get("truth_suite_status") != "pass":
            failures.append("Stage 7.1 truth suite does not pass")
        if stage7_1_gate.get("validation_checkpoints", {}).get("existing_apis_can_represent_declared_results") != "pass":
            failures.append("Stage 7.1 gate does not confirm current APIs represent declared results")

    stage7_1_truth_report_path = root / "case_studies" / "stage7_synthetic_truth" / "stage7_1_synthetic_truth_report.json"
    if stage7_1_truth_report_path.exists():
        try:
            truth_report = json.loads(stage7_1_truth_report_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            failures.append(f"Stage 7.1 synthetic truth report is not valid JSON: {exc}")
            truth_report = {}
        if truth_report.get("status") != "pass":
            failures.append("Stage 7.1 synthetic truth report does not pass")


    stage7_2_gate_path = root / "docs" / "stage7_2_gate_report.json"
    if stage7_2_gate_path.exists():
        try:
            stage7_2_gate = json.loads(stage7_2_gate_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            failures.append(f"Stage 7.2 gate report is not valid JSON: {exc}")
            stage7_2_gate = {}
        if stage7_2_gate.get("status") != "pass":
            failures.append("Stage 7.2 gate report does not pass")
        if stage7_2_gate.get("completion_state") != "complete_benchmark_harness":
            failures.append("Stage 7.2 gate report does not mark benchmark harness complete")
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
                failures.append(f"Stage 7.2 gate checkpoint does not pass: {checkpoint}")
        if checkpoints.get("stop_condition_no_added_value_beyond_baselines") != "not_triggered":
            failures.append("Stage 7.2 stop condition must remain not_triggered")
        boundary = str(stage7_2_gate.get("interpretation_boundary", ""))
        if "do not add independent biological demonstrations" not in boundary:
            failures.append("Stage 7.2 gate report must preserve biological-demonstration boundary")

    stage7_2_benchmark_report_path = root / "case_studies" / "stage7_benchmarks" / "stage7_2_benchmark_report.json"
    if stage7_2_benchmark_report_path.exists():
        try:
            benchmark_report = json.loads(stage7_2_benchmark_report_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            failures.append(f"Stage 7.2 benchmark report is not valid JSON: {exc}")
            benchmark_report = {}
        if benchmark_report.get("status") != "pass":
            failures.append("Stage 7.2 benchmark report does not pass")
        gates = benchmark_report.get("gates", {}) if isinstance(benchmark_report.get("gates", {}), dict) else {}
        if gates.get("stop_condition_no_added_value_beyond_baselines", {}).get("status") != "not_triggered":
            failures.append("Stage 7.2 benchmark stop condition is not recorded as not_triggered")
        public_fixtures = benchmark_report.get("public_fixtures", []) if isinstance(benchmark_report.get("public_fixtures", []), list) else []
        if len(public_fixtures) < 4:
            failures.append("Stage 7.2 benchmark report does not include all retained public fixture summaries")


    stage7_3_gate_path = root / "docs" / "stage7_3_gate_report.json"
    if stage7_3_gate_path.exists():
        try:
            stage7_3_gate = json.loads(stage7_3_gate_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            failures.append(f"Stage 7.3 gate report is not valid JSON: {exc}")
            stage7_3_gate = {}
        if stage7_3_gate.get("status") != "pass":
            failures.append("Stage 7.3 gate report does not pass")
        if stage7_3_gate.get("completion_state") != "complete_public_signaling_demonstrations":
            failures.append("Stage 7.3 gate report does not mark public signaling demonstrations complete")
        selected = stage7_3_gate.get("selected_datasets", []) if isinstance(stage7_3_gate.get("selected_datasets", []), list) else []
        if set(selected) != {"drg_calcium_vonbuchholtz2025", "erk_gpcr_wan2021"}:
            failures.append("Stage 7.3 gate report does not record the selected public signaling datasets")
        checkpoints = stage7_3_gate.get("validation_checkpoints", {}) if isinstance(stage7_3_gate.get("validation_checkpoints", {}), dict) else {}
        for checkpoint in [
            "dataset_source_citation_access_metadata_grouping_preprocessing_notes",
            "each_case_states_what_rhodyn_adds",
            "two_independent_public_live_cell_systems_represented",
            "residence_amplitude_disagreement_detected_in_each_case",
            "examples_do_not_imply_manuscript_generation",
        ]:
            if checkpoints.get(checkpoint) != "pass":
                failures.append(f"Stage 7.3 gate checkpoint does not pass: {checkpoint}")
        if checkpoints.get("stop_condition_public_dataset_failure") != "not_triggered":
            failures.append("Stage 7.3 public dataset stop condition must remain not_triggered")
        boundary = str(stage7_3_gate.get("interpretation_boundary", ""))
        if "does not imply that RhoDyn generated" not in boundary:
            failures.append("Stage 7.3 gate report must preserve manuscript-independence boundary")

    stage7_3_public_report_path = root / "case_studies" / "stage7_public_signaling" / "stage7_3_public_signaling_gate_report.json"
    if stage7_3_public_report_path.exists():
        try:
            public_signaling_report = json.loads(stage7_3_public_report_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            failures.append(f"Stage 7.3 public signaling report is not valid JSON: {exc}")
            public_signaling_report = {}
        if public_signaling_report.get("status") != "pass":
            failures.append("Stage 7.3 public signaling report does not pass")
        cases = public_signaling_report.get("case_summaries", []) if isinstance(public_signaling_report.get("case_summaries", []), list) else []
        if len(cases) < 2:
            failures.append("Stage 7.3 public signaling report does not include two public systems")
        for case in cases:
            if int(case.get("amplitude_residence_disagreement_count", 0)) <= 0:
                failures.append(f"Stage 7.3 case lacks amplitude/residence disagreement: {case.get('dataset_id')}")



    stage7_4_gate_path = root / "docs" / "stage7_4_gate_report.json"
    if stage7_4_gate_path.exists():
        try:
            stage7_4_gate = json.loads(stage7_4_gate_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            failures.append(f"Stage 7.4 gate report is not valid JSON: {exc}")
            stage7_4_gate = {}
        if stage7_4_gate.get("status") != "pass":
            failures.append("Stage 7.4 gate report does not pass")
        if stage7_4_gate.get("completion_state") != "complete_endpoint_reserve_routing_demonstrations":
            failures.append("Stage 7.4 gate report does not mark endpoint/reserve/routing demonstrations complete")
        selected = set(stage7_4_gate.get("selected_cases", [])) if isinstance(stage7_4_gate.get("selected_cases", []), list) else set()
        if selected != {"cell_painting_mitotox_seal2023", "erk_akt_wan2021_bounded_coupling"}:
            failures.append("Stage 7.4 gate report does not record the selected endpoint and paired-reporter cases")
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
                failures.append(f"Stage 7.4 gate checkpoint does not pass: {checkpoint}")
        if checkpoints.get("stop_condition_non_trajectory_model_indistinguishable") != "not_triggered":
            failures.append("Stage 7.4 stop condition must remain not_triggered")
        boundary = str(stage7_4_gate.get("interpretation_boundary", ""))
        if "not live metabolic reserve" not in boundary:
            failures.append("Stage 7.4 gate report must scope reserve-like endpoint interpretation")

    stage7_4_case_report_path = root / "case_studies" / "stage7_endpoint_reserve_routing" / "stage7_4_endpoint_reserve_routing_gate_report.json"
    if stage7_4_case_report_path.exists():
        try:
            stage7_4_case_report = json.loads(stage7_4_case_report_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            failures.append(f"Stage 7.4 case report is not valid JSON: {exc}")
            stage7_4_case_report = {}
        if stage7_4_case_report.get("status") != "pass":
            failures.append("Stage 7.4 endpoint/reserve/routing case report does not pass")
        routing = stage7_4_case_report.get("routing_diagnostics", {}) if isinstance(stage7_4_case_report.get("routing_diagnostics", {}), dict) else {}
        if routing.get("best_model") != "compartment_route_5nn":
            failures.append("Stage 7.4 routed-output comparison does not retain compartment_route_5nn")
        coupling = stage7_4_case_report.get("bounded_coupling_diagnostics", {}) if isinstance(stage7_4_case_report.get("bounded_coupling_diagnostics", {}), dict) else {}
        if coupling.get("primary_passes") is not True:
            failures.append("Stage 7.4 bounded-coupling primary contrast does not pass")


    stage7_5_gate_path = root / "docs" / "stage7_5_gate_report.json"
    if stage7_5_gate_path.exists():
        try:
            stage7_5_gate = json.loads(stage7_5_gate_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            failures.append(f"Stage 7.5 gate report is not valid JSON: {exc}")
            stage7_5_gate = {}
        if stage7_5_gate.get("status") != "pass":
            failures.append("Stage 7.5 gate report does not pass")
        if stage7_5_gate.get("completion_state") != "complete_external_heldout_validation":
            failures.append("Stage 7.5 gate report does not mark external/held-out validation complete")
        if stage7_5_gate.get("pass_context_count") != 4 or stage7_5_gate.get("inconclusive_context_count") != 3:
            failures.append("Stage 7.5 held-out validation must preserve four pass contexts and three inconclusive contexts")
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
                failures.append(f"Stage 7.5 gate checkpoint does not pass: {checkpoint}")
        if stage7_5_gate.get("stop_condition_access_restriction") != "not_triggered":
            failures.append("Stage 7.5 access stop condition must remain not_triggered")
        boundary = str(stage7_5_gate.get("interpretation_boundary", ""))
        if "inconclusive contexts" not in boundary or "residence summaries only" not in boundary:
            failures.append("Stage 7.5 gate report must keep held-out boundary interpretation visible")

    stage7_5_case_report_path = root / "case_studies" / "stage7_heldout_validation" / "stage7_5_heldout_validation_gate_report.json"
    if stage7_5_case_report_path.exists():
        try:
            stage7_5_case_report = json.loads(stage7_5_case_report_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            failures.append(f"Stage 7.5 case report is not valid JSON: {exc}")
            stage7_5_case_report = {}
        if stage7_5_case_report.get("status") != "pass":
            failures.append("Stage 7.5 held-out validation case report does not pass")
        if stage7_5_case_report.get("evidence_set_decision") != "scoped_heldout_boundary_validation":
            failures.append("Stage 7.5 case report does not keep the scoped evidence-set decision")

    stage7_6_gate_path = root / "docs" / "stage7_6_gate_report.json"
    stage7_6_case_report_path = root / "case_studies" / "stage7_methods_reproducibility" / "stage7_6_methods_reproducibility_gate_report.json"
    if stage7_6_gate_path.exists():
        try:
            stage7_6_gate = json.loads(stage7_6_gate_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            failures.append(f"Stage 7.6 gate report is not valid JSON: {exc}")
            stage7_6_gate = {}
        if stage7_6_gate.get("status") != "pass":
            failures.append("Stage 7.6 gate report does not pass")
        if stage7_6_gate.get("completion_state") != "complete_methods_reproducibility_hardening":
            failures.append("Stage 7.6 gate report does not mark methods reproducibility hardening complete")
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
                failures.append(f"Stage 7.6 gate checkpoint does not pass: {checkpoint}")
        if checkpoints.get("stop_condition_clean_room_failure") != "not_triggered":
            failures.append("Stage 7.6 stop condition must remain not_triggered")
        summary = stage7_6_gate.get("comparison_summary", {}) if isinstance(stage7_6_gate.get("comparison_summary", {}), dict) else {}
        if summary.get("matched_outputs") != summary.get("checked_outputs") or not summary.get("checked_outputs"):
            failures.append("Stage 7.6 must match all selected regenerated outputs")
        parity = stage7_6_gate.get("parity_summary", {}) if isinstance(stage7_6_gate.get("parity_summary", {}), dict) else {}
        if parity.get("matching_operations") != parity.get("checked_operations") or not parity.get("checked_operations"):
            failures.append("Stage 7.6 must preserve Python/CLI/backend/frontend-contract parity")
        boundary = str(stage7_6_gate.get("interpretation_boundary", ""))
        if "does not add biological evidence" not in boundary:
            failures.append("Stage 7.6 gate report must preserve the no-new-biological-evidence boundary")

    if stage7_6_case_report_path.exists():
        try:
            stage7_6_case_report = json.loads(stage7_6_case_report_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            failures.append(f"Stage 7.6 case report is not valid JSON: {exc}")
            stage7_6_case_report = {}
        if stage7_6_case_report.get("status") != "pass":
            failures.append("Stage 7.6 methods reproducibility case report does not pass")
        if stage7_6_case_report.get("mode") != "full_release_archive":
            failures.append("Stage 7.6 methods reproducibility report must come from full_release_archive mode")

    zenodo_publication_path = root / "docs" / "zenodo_publication_report.json"
    if zenodo_publication_path.exists():
        try:
            zenodo_publication = json.loads(zenodo_publication_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            failures.append(f"Zenodo publication report is not valid JSON: {exc}")
            zenodo_publication = {}
        if zenodo_publication.get("status") != "pass":
            failures.append("Zenodo publication report does not pass")
        if zenodo_publication.get("doi") != "10.5281/zenodo.21036616":
            failures.append("Zenodo publication report does not record the v0.1.0 version DOI")
        if zenodo_publication.get("conceptdoi") != "10.5281/zenodo.21036615":
            failures.append("Zenodo publication report does not record the concept DOI")

    public_release_path = root / "docs" / "public_release_integrity_report.json"
    if public_release_path.exists():
        try:
            public_release = json.loads(public_release_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            failures.append(f"public release integrity report is not valid JSON: {exc}")
            public_release = {}
        if public_release.get("status") != "pass":
            failures.append("public release integrity report does not pass")
        public_checks = public_release.get("checks", {}) if isinstance(public_release.get("checks", {}), dict) else {}
        for check_name in [
            "github_repo_api_public",
            "github_release_api_public",
            "github_tag_archive_public",
            "github_release_expected_assets_public",
            "zenodo_version_doi_resolves",
            "zenodo_concept_doi_resolves",
            "zenodo_expected_assets_present",
        ]:
            if not public_checks.get(check_name):
                failures.append(f"public release integrity check failed or missing: {check_name}")

    for path in _text_files(root):
        text = path.read_text(encoding="utf-8", errors="ignore")
        for pattern in LEAK_PATTERNS:
            if pattern.search(text):
                failures.append(f"possible local path or credential pattern in {path.relative_to(root)}")
                break

    for path in root.rglob("*"):
        if ".git" in path.parts:
            continue
        rel = path.relative_to(root)
        if path.is_dir() and path.name in GENERATED_DIRS:
            if _tracked_or_unknown(rel, tracked):
                failures.append(f"generated directory should not be committed: {rel}")
            else:
                warnings.append(f"ignoring untracked generated directory: {rel}")
        if path.is_dir() and path.name.endswith(".egg-info"):
            if _tracked_or_unknown(rel, tracked):
                failures.append(f"egg-info directory should not be committed: {rel}")
            else:
                warnings.append(f"ignoring untracked egg-info directory: {rel}")
        if path.is_file() and path.suffix.lower() in RAW_EXTENSIONS and _tracked_or_unknown(rel, tracked):
            failures.append(f"raw or manuscript-private data-like file should not be packaged: {rel}")


    for script, label in [
        ("scripts/audit_stage5_frontend_scaffold.py", "Stage 5 frontend scaffold audit"),
        ("scripts/audit_stage5_premium_workbench.py", "Stage 5 premium workbench audit"),
        ("scripts/audit_stage5_upload_flow_parity.py", "Stage 5 upload-flow parity audit"),
        ("scripts/audit_stage5_simulation_workbench.py", "Stage 5 simulation workbench audit"),
    ]:
        check = subprocess.run(
            [sys.executable, script],
            cwd=root,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        if check.returncode != 0:
            detail = (check.stdout or check.stderr).strip()
            failures.append(f"{label} does not pass: {detail[:1200]}")

    if not (root / ".github" / "workflows" / "package.yml").exists():
        warnings.append("package build workflow is missing")

    return {
        "status": "pass" if not failures else "fail",
        "failures": failures,
        "warnings": warnings,
    }


def main() -> int:
    payload = check_release()
    print(json.dumps(payload, indent=2))
    return 0 if payload["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())

"""Release-safety checks for the private RhoDyn package."""

from __future__ import annotations

import csv
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


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
    "docs/stage7_6_recursive_hardening.md",
    "docs/stage7_methods_reproducibility_card.md",
    "docs/stage7_6_gate_report.json",
    "docs/stage7_6_clean_room_report.json",
    "docs/stage7_6_recursive_hardening_report.json",
    "docs/stage7_7_8_recursive_hardening.md",
    "docs/stage7_7_8_recursive_hardening_report.json",
    "scripts/run_stage7_6_methods_reproducibility.py",
    "scripts/audit_stage7_6_recursive_hardening.py",
    "scripts/audit_stage7_7_8_recursive_hardening.py",
    "tests/test_stage7_6_methods_reproducibility.py",
    "tests/test_stage7_7_8_recursive_hardening.py",
    "case_studies/stage7_methods_reproducibility/methods_reproducibility_commands.tsv",
    "case_studies/stage7_methods_reproducibility/methods_output_comparison.tsv",
    "case_studies/stage7_methods_reproducibility/cross_surface_parity.tsv",
    "case_studies/stage7_methods_reproducibility/release_archive_manifest.tsv",
    "case_studies/stage7_methods_reproducibility/stage7_6_methods_reproducibility_gate_report.json",
    "case_studies/stage7_methods_reproducibility/stage7_6_recursive_hardening_report.json",
    "case_studies/stage7_methods_reproducibility/stage7_6_methods_reproducibility_report.md",
    "docs/stage7_usability_rehearsal.md",
    "docs/stage7_user_path_findings.md",
    "docs/stage7_7_gate_report.json",
    "scripts/run_stage7_7_usability_rehearsal.py",
    "tests/test_stage7_7_usability_rehearsal.py",
    "case_studies/stage7_usability_rehearsal/usability_task_protocol.tsv",
    "case_studies/stage7_usability_rehearsal/biologist_residence_task_result.json",
    "case_studies/stage7_usability_rehearsal/biologist_residence_bundle.zip",
    "case_studies/stage7_usability_rehearsal/quantitative_reproduction_result.json",
    "case_studies/stage7_usability_rehearsal/quantitative_bounded_coupling_bundle.zip",
    "case_studies/stage7_usability_rehearsal/user_path_findings.tsv",
    "case_studies/stage7_usability_rehearsal/export_examples_manifest.tsv",
    "case_studies/stage7_usability_rehearsal/workbench_flow_check.json",
    "case_studies/stage7_usability_rehearsal/stage7_7_usability_gate_report.json",
    "case_studies/stage7_usability_rehearsal/stage7_7_usability_rehearsal_report.md",
    "docs/stage7_methods_evidence_index.md",
    "docs/stage7_figure_artifact_crosswalk.md",
    "docs/stage7_claim_evidence_crosswalk.md",
    "docs/stage7_methods_submission_readiness.md",
    "docs/stage7_8_gate_report.json",
    "scripts/run_stage7_8_methods_readiness.py",
    "tests/test_stage7_8_methods_readiness.py",
    "case_studies/stage7_methods_readiness/figure_artifact_crosswalk.tsv",
    "case_studies/stage7_methods_readiness/claim_evidence_crosswalk.tsv",
    "case_studies/stage7_methods_readiness/methods_readiness_checklist.tsv",
    "case_studies/stage7_methods_readiness/limitations_traceability.tsv",
    "case_studies/stage7_methods_readiness/stage7_8_methods_readiness_gate_report.json",
    "case_studies/stage7_methods_readiness/stage7_7_8_recursive_hardening_report.json",
    "case_studies/stage7_methods_readiness/stage7_8_methods_readiness_report.md",
    "docs/stage5_public_mlci_workflow.md",
    "frontend/stage5/index.html",
    "frontend/stage5/styles.css",
    "frontend/stage5/app.js",
    "examples/mlci_public_intensity_trajectory.csv",
    "docs/stage9_manuscript_assembly_plan.md",
    "docs/stage9_execution_memory.json",
    "scripts/scaffold_stage9_manuscript_assembly.py",
    "scripts/check_stage9_scaffold.py",
    "scripts/run_stage9_0_evidence_intake_lock.py",
    "scripts/run_stage9_1_venue_guidance_register.py",
    "scripts/run_stage9_2_methods_paper_corpus.py",
    "scripts/run_stage9_3_narrative_spine.py",
    "scripts/run_stage9_4_claim_freeze.py",
    "scripts/run_stage9_5_paragraph_claim_ledger.py",
    "scripts/run_stage9_6_figure_spine.py",
    "scripts/run_stage9_6b_panelforge_rendering.py",
    "scripts/run_stage9_7_supplementary_display_plan.py",
    "scripts/run_stage9_8_section_contract_blueprint.py",
    "scripts/run_stage9_9_title_abstract_strategy.py",
    "scripts/run_stage9_10_results_architecture.py",
    "scripts/run_stage9_11_results_drafting.py",
    "scripts/run_stage9_12_introduction_literature_binding.py",
    "scripts/run_stage9_13_discussion_interpretation_map.py",
    "scripts/run_stage9_14_discussion_drafting.py",
    "scripts/run_stage9_15_methods_architecture.py",
    "scripts/run_stage9_16_methods_drafting.py",
    "scripts/run_stage9_17_availability_assembly.py",
    "scripts/run_stage9_18_supplementary_methods.py",
    "scripts/run_stage9_19_supplementary_tables.py",
    "scripts/run_stage9_20_reference_audit.py",
    "scripts/run_stage9_21_cross_document_consistency.py",
    "scripts/run_stage9_22_statistical_language_audit.py",
    "scripts/run_stage9_23_figure_legend_audit.py",
    "scripts/run_stage9_24_editorial_polish_pass1.py",
    "scripts/run_stage9_25_editorial_polish_pass2.py",
    "scripts/run_stage9_25b_reader_surface_hygiene.py",
    "scripts/run_stage9_26_internal_peer_review.py",
    "scripts/run_stage9_27_submission_package_assembly.py",
    "scripts/run_stage9_28_pi_review_auto_revision.py",
    "scripts/run_stage9_29_closure_assembly.py",
    "scripts/run_stage9_public_access_verification.py",
    "scripts/run_stage9_submit_or_hold_decision.py",
    "tests/test_stage9_scaffold.py",
    "tests/test_stage9_0_evidence_lock.py",
    "tests/test_stage9_1_venue_guidance.py",
    "tests/test_stage9_2_methods_paper_corpus.py",
    "tests/test_stage9_3_narrative_spine.py",
    "tests/test_stage9_4_claim_freeze.py",
    "tests/test_stage9_5_paragraph_claim_ledger.py",
    "tests/test_stage9_6_figure_spine.py",
    "tests/test_stage9_7_supplementary_display_plan.py",
    "tests/test_stage9_8_section_contract_blueprint.py",
    "tests/test_stage9_9_title_abstract_strategy.py",
    "tests/test_stage9_10_results_architecture.py",
    "tests/test_stage9_11_results_drafting.py",
    "tests/test_stage9_12_introduction_literature_binding.py",
    "tests/test_stage9_13_discussion_interpretation_map.py",
    "tests/test_stage9_14_discussion_drafting.py",
    "tests/test_stage9_15_methods_architecture.py",
    "tests/test_stage9_16_methods_drafting.py",
    "tests/test_stage9_17_availability_assembly.py",
    "tests/test_stage9_18_supplementary_methods.py",
    "tests/test_stage9_19_supplementary_tables.py",
    "tests/test_stage9_20_reference_audit.py",
    "tests/test_stage9_21_cross_document_consistency.py",
    "tests/test_stage9_22_statistical_language_audit.py",
    "tests/test_stage9_23_figure_legend_audit.py",
    "tests/test_stage9_24_editorial_polish_pass1.py",
    "tests/test_stage9_25_editorial_polish_pass2.py",
    "tests/test_stage9_25b_reader_surface_hygiene.py",
    "tests/test_stage9_26_internal_peer_review.py",
    "tests/test_stage9_27_submission_package_assembly.py",
    "tests/test_stage9_28_pi_review_auto_revision.py",
    "tests/test_stage9_29_closure_assembly.py",
    "tests/test_stage9_public_access_verification.py",
    "tests/test_stage9_submit_or_hold_decision.py",
    "manuscript/nature_methods/README.md",
    "manuscript/nature_methods/contracts/id_namespace.md",
    "manuscript/nature_methods/contracts/machine_gate_spec.md",
    "manuscript/nature_methods/contracts/atomic_write_protocol.md",
    "manuscript/nature_methods/contracts/stage9_project_binding.json",
    "manuscript/nature_methods/contracts/stage9_substage_registry.json",
    "manuscript/nature_methods/contracts/ledger_schema_map.json",
    "manuscript/nature_methods/figures/figures.manifest.yaml",
    "manuscript/nature_methods/figures/.panelforge_commit",
    "manuscript/nature_methods/gate_verdicts/9.-1.json",
    "manuscript/nature_methods/gate_verdicts/9.0.json",
    "manuscript/nature_methods/gate_verdicts/9.1.json",
    "manuscript/nature_methods/gate_verdicts/9.2.json",
    "manuscript/nature_methods/gate_verdicts/9.3.json",
    "manuscript/nature_methods/gate_verdicts/9.4.json",
    "manuscript/nature_methods/gate_verdicts/9.5.json",
    "manuscript/nature_methods/gate_verdicts/9.6.json",
    "manuscript/nature_methods/gate_verdicts/9.6b.json",
    "manuscript/nature_methods/gate_verdicts/9.7.json",
    "manuscript/nature_methods/gate_verdicts/9.27.json",
    "manuscript/nature_methods/gate_verdicts/9.28.json",
    "manuscript/nature_methods/gate_verdicts/9.29.json",
    "manuscript/nature_methods/stage9_completion_report.md",
    "manuscript/nature_methods/stage9_closure_version_binding.json",
    "manuscript/nature_methods/submission_package/main_text_for_submission.md",
    "manuscript/nature_methods/submission_package/supplementary_information_for_submission.md",
    "manuscript/nature_methods/submission_package/submission_manifest.md",
    "manuscript/nature_methods/submission_package/submission_readiness_checklist.md",
    "manuscript/nature_methods/submission_package/editor_triage_note_for_cover_letter.md",
    "manuscript/nature_methods/submission_package/editorial_pitch_for_submission.md",
    "manuscript/nature_methods/submission_package/cover_letter_for_submission_AUTHOR_CONFIRMATION_REQUIRED.md",
    "manuscript/nature_methods/submission_package/final_upload_runbook_AUTHOR_CONFIRMATION_REQUIRED.md",
    "manuscript/nature_methods/submission_package/prior_art_positioning_matrix.md",
    "manuscript/nature_methods/submission_package/validation_breadth_and_boundary_map.md",
    "manuscript/nature_methods/submission_package/editor_objection_response_map.md",
    "manuscript/nature_methods/submission_package/editor_two_minute_triage_simulation.md",
    "manuscript/nature_methods/submission_package/nature_methods_editorial_bar_rescue_audit.md",
    "manuscript/nature_methods/submission_package/current_nature_methods_policy_preflight.md",
    "manuscript/nature_methods/submission_package/reviewer_editor_fit_planner_AUTHOR_CONFIRMATION_REQUIRED.md",
    "manuscript/nature_methods/submission_package/software_reporting_checklist.md",
    "manuscript/nature_methods/submission_package/article_fit_checklist.md",
    "manuscript/nature_methods/submission_package/author_declarations_REQUIRED.md",
    "manuscript/nature_methods/submission_package/ai_disclosure_AUTHOR_CONFIRMATION_REQUIRED.md",
    "manuscript/nature_methods/submission_package/title_author_metadata_AUTHOR_CONFIRMATION_REQUIRED.md",
    "manuscript/nature_methods/submission_package/reporting_summary_answer_bank_AUTHOR_CONFIRMATION_REQUIRED.md",
    "manuscript/nature_methods/submission_package/code_for_review.md",
    "manuscript/nature_methods/submission_package/package_consistency_audit.md",
    "manuscript/nature_methods/submission_package/figure_file_inventory.csv",
    "manuscript/nature_methods/submission_package/source_data_and_statistics_inventory.csv",
    "manuscript/nature_methods/submission_package/references_for_submission.bib",
    "manuscript/nature_methods/submission_package/reporting_summary_REQUIRED.md",
    "manuscript/nature_methods/submission_package/submission_package_manifest.json",
    "manuscript/nature_methods/submission_package/pi_review_packet.md",
    "manuscript/nature_methods/submission_package/pi_review_action_matrix.csv",
    "manuscript/nature_methods/submission_package/pi_review_revision_log.md",
    "manuscript/nature_methods/submission_package/pi_review_literature_calibration.md",
    "manuscript/nature_methods/submission_package/pi_review_action_decisions.csv",
    "manuscript/nature_methods/gate_verdicts/9.8.json",
    "manuscript/nature_methods/gate_verdicts/9.9.json",
    "manuscript/nature_methods/gate_verdicts/9.10.json",
    "manuscript/nature_methods/gate_verdicts/9.11.json",
    "manuscript/nature_methods/gate_verdicts/9.12.json",
    "manuscript/nature_methods/gate_verdicts/9.13.json",
    "manuscript/nature_methods/gate_verdicts/9.14.json",
    "manuscript/nature_methods/gate_verdicts/9.15.json",
    "manuscript/nature_methods/gate_verdicts/9.16.json",
    "manuscript/nature_methods/gate_verdicts/9.17.json",
    "manuscript/nature_methods/gate_verdicts/9.18.json",
    "manuscript/nature_methods/gate_verdicts/9.19.json",
    "manuscript/nature_methods/gate_verdicts/9.20.json",
    "manuscript/nature_methods/gate_verdicts/9.21.json",
    "manuscript/nature_methods/gate_verdicts/9.22.json",
    "manuscript/nature_methods/gate_verdicts/9.23.json",
    "manuscript/nature_methods/gate_verdicts/9.24.json",
    "manuscript/nature_methods/gate_verdicts/9.25.json",
    "manuscript/nature_methods/gate_verdicts/9.25b.json",
    "manuscript/nature_methods/gate_verdicts/9.26.json",
    "manuscript/nature_methods/sections/results_blueprint.md",
    "manuscript/nature_methods/sections/results.md",
    "manuscript/nature_methods/sections/introduction.md",
    "manuscript/nature_methods/sections/discussion_blueprint.md",
    "manuscript/nature_methods/sections/discussion.md",
    "manuscript/nature_methods/sections/methods_blueprint.md",
    "manuscript/nature_methods/sections/methods.md",
    "manuscript/nature_methods/audits/editorial_pass_1.md",
    "manuscript/nature_methods/audits/editorial_pass_2.md",
    "manuscript/nature_methods/audits/reader_surface_hygiene_report.md",
    "manuscript/nature_methods/audits/internal_peer_review_simulation.md",
    "manuscript/nature_methods/audits/reviewer_action_matrix.csv",
    "manuscript/nature_methods/sections/data_availability.md",
    "manuscript/nature_methods/sections/code_availability.md",
    "manuscript/nature_methods/supplementary/supplementary_methods.md",
    "manuscript/nature_methods/supplementary/supplementary_tables_plan.md",
    "manuscript/nature_methods/supplementary/source_data_binding_ledger.csv",
    "manuscript/nature_methods/ledgers/statistic_ledger.csv",
    "manuscript/nature_methods/ledgers/reproducibility_command_index.md",
    "manuscript/nature_methods/submission_package/reporting_summary_REQUIRED.md",
    "manuscript/nature_methods/submission_package/reporting_summary_answer_bank_AUTHOR_CONFIRMATION_REQUIRED.md",
    "manuscript/nature_methods/submission_package/cover_letter_for_submission_AUTHOR_CONFIRMATION_REQUIRED.md",
    "manuscript/nature_methods/submission_package/final_upload_runbook_AUTHOR_CONFIRMATION_REQUIRED.md",
    "manuscript/nature_methods/submission_package/prior_art_positioning_matrix.md",
    "manuscript/nature_methods/submission_package/validation_breadth_and_boundary_map.md",
    "manuscript/nature_methods/submission_package/editor_objection_response_map.md",
    "manuscript/nature_methods/submission_package/editor_two_minute_triage_simulation.md",
    "manuscript/nature_methods/submission_package/nature_methods_editorial_bar_rescue_audit.md",
    "manuscript/nature_methods/submission_package/current_nature_methods_policy_preflight.md",
    "manuscript/nature_methods/submission_package/reviewer_editor_fit_planner_AUTHOR_CONFIRMATION_REQUIRED.md",
    "manuscript/nature_methods/refs/introduction_citation_ledger.csv",
    "manuscript/nature_methods/refs/references.bib",
    "manuscript/nature_methods/refs/citation_claim_ledger.csv",
    "manuscript/nature_methods/audits/reference_audit.md",
    "manuscript/nature_methods/audits/cross_document_consistency_audit.md",
    "manuscript/nature_methods/audits/statistical_language_audit.md",
    "manuscript/nature_methods/audits/live_numbers_diff.csv",
    "manuscript/nature_methods/audits/figure_legend_audit.md",
    "manuscript/nature_methods/figures/figure_legends.md",
    "manuscript/nature_methods/ledgers/stage9_evidence_manifest.csv",
    "manuscript/nature_methods/ledgers/stage9_evidence_lock.md",
    "manuscript/nature_methods/ledgers/stage7_output_contract.md",
    "manuscript/nature_methods/refs/nature_methods_guidance_register.md",
    "manuscript/nature_methods/audits/venue_policy_constraints.md",
    "manuscript/nature_methods/refs/_cache/nature_initial_submission.meta.json",
    "manuscript/nature_methods/refs/_cache/nature_initial_submission.txt",
    "manuscript/nature_methods/refs/_cache/nature_portfolio_reporting_standards.meta.json",
    "manuscript/nature_methods/refs/_cache/nature_portfolio_reporting_standards.txt",
    "manuscript/nature_methods/refs/_cache/nmeth_aims_scope.meta.json",
    "manuscript/nature_methods/refs/_cache/nmeth_aims_scope.txt",
    "manuscript/nature_methods/refs/_cache/nmeth_content_types.meta.json",
    "manuscript/nature_methods/refs/_cache/nmeth_content_types.txt",
    "manuscript/nature_methods/refs/_cache/nmeth_editorial_policies.meta.json",
    "manuscript/nature_methods/refs/_cache/nmeth_editorial_policies.txt",
    "manuscript/nature_methods/refs/_cache/nmeth_submission_guidelines.meta.json",
    "manuscript/nature_methods/refs/_cache/nmeth_submission_guidelines.txt",
    "manuscript/nature_methods/refs/_cache/springer_nature_code_policy.meta.json",
    "manuscript/nature_methods/refs/_cache/springer_nature_code_policy.txt",
    "manuscript/nature_methods/refs/_cache/methods_corpus/mp-001.crossref.json",
    "manuscript/nature_methods/refs/_cache/methods_corpus/mp-002.crossref.json",
    "manuscript/nature_methods/refs/_cache/methods_corpus/mp-003.crossref.json",
    "manuscript/nature_methods/refs/_cache/methods_corpus/mp-004.crossref.json",
    "manuscript/nature_methods/refs/_cache/methods_corpus/mp-005.crossref.json",
    "manuscript/nature_methods/refs/_cache/methods_corpus/mp-006.crossref.json",
    "manuscript/nature_methods/refs/_cache/methods_corpus/mp-007.crossref.json",
    "manuscript/nature_methods/refs/_cache/methods_corpus/mp-008.crossref.json",
    "tools/panelforge-figures/STAGE9_PLACEHOLDER.md",
    "manuscript/nature_methods/refs/representative_methods_papers.md",
    "manuscript/nature_methods/audits/methods_paper_archetype_analysis.md",
    "manuscript/nature_methods/stage9_narrative_spine.md",
    "manuscript/nature_methods/audits/venue_fit_rationale.md",
    "manuscript/nature_methods/ledgers/claim_hierarchy.md",
    "manuscript/nature_methods/ledgers/claim_hierarchy.csv",
    "manuscript/nature_methods/ledgers/non_claims_and_scope_boundaries.md",
    "manuscript/nature_methods/ledgers/paragraph_claim_ledger.csv",
    "manuscript/nature_methods/ledgers/claim_strength_rules.md",
    "manuscript/nature_methods/ledgers/methods_to_code_ledger.csv",
    "manuscript/nature_methods/figures/main_figure_spine.md",
    "manuscript/nature_methods/ledgers/figure_to_claim_to_artifact.csv",
    "manuscript/nature_methods/figures/display_item_plan.md",
    "manuscript/nature_methods/supplementary/supplementary_item_plan.md",
    "manuscript/nature_methods/ledgers/supplementary_callout_ledger.csv",
    "manuscript/nature_methods/sections/section_contracts.md",
    "manuscript/nature_methods/sections/title_options.md",
    "manuscript/nature_methods/sections/abstract_strategy.md",
    "manuscript/nature_methods/sections/abstract.md",
    "manuscript/nature_methods/audits/panelforge_render_report.md",
    "manuscript/nature_methods/audits/nature_methods_public_access_verification.json",
    "manuscript/nature_methods/audits/nature_methods_public_access_verification.md",
    "manuscript/nature_methods/audits/nature_methods_submit_or_hold_decision.json",
    "manuscript/nature_methods/audits/nature_methods_submit_or_hold_decision.md",
    "manuscript/nature_methods/figures/rendered/FIG-001/FIG-001.pdf",
    "manuscript/nature_methods/figures/rendered/FIG-001/FIG-001.png",
    "manuscript/nature_methods/figures/rendered/FIG-001/FIG-001.svg",
    "manuscript/nature_methods/figures/rendered/FIG-002/FIG-002.pdf",
    "manuscript/nature_methods/figures/rendered/FIG-002/FIG-002.png",
    "manuscript/nature_methods/figures/rendered/FIG-002/FIG-002.svg",
    "manuscript/nature_methods/figures/rendered/FIG-003/FIG-003.pdf",
    "manuscript/nature_methods/figures/rendered/FIG-003/FIG-003.png",
    "manuscript/nature_methods/figures/rendered/FIG-003/FIG-003.svg",
    "manuscript/nature_methods/figures/rendered/FIG-004/FIG-004.pdf",
    "manuscript/nature_methods/figures/rendered/FIG-004/FIG-004.png",
    "manuscript/nature_methods/figures/rendered/FIG-004/FIG-004.svg",
    "manuscript/nature_methods/figures/rendered/FIG-005/FIG-005.pdf",
    "manuscript/nature_methods/figures/rendered/FIG-005/FIG-005.png",
    "manuscript/nature_methods/figures/rendered/FIG-005/FIG-005.svg",
    "manuscript/nature_methods/figures/rendered/FIG-006/FIG-006.pdf",
    "manuscript/nature_methods/figures/rendered/FIG-006/FIG-006.png",
    "manuscript/nature_methods/figures/rendered/FIG-006/FIG-006.svg",
]
LEAK_PATTERNS = [
    re.compile("/" + "Users/"),
    re.compile("/" + "Volumes/"),
    re.compile("Library/" + "LaunchAgents"),
    re.compile(r"sk-[A-Za-z0-9_-]{16,}"),
    re.compile("ghp" + r"_[A-Za-z0-9_]+"),
    re.compile("github" + r"_pat_[A-Za-z0-9_]+"),
    re.compile(r"xox[baprs]-[A-Za-z0-9-]+"),
]
RAW_EXTENSIONS = {".lif", ".czi", ".nd2", ".oir", ".oib", ".lsm", ".tif", ".tiff", ".prism", ".xml"}
GENERATED_DIRS = {
    "__pycache__",
    "dist",
    "build",
    "htmlcov",
    ".pytest_cache",
    "node_modules",
    "playwright-report",
    "test-results",
    "blob-report",
}


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
        active_stage = current.get("active_stage")
        allowed_active_stages = {
            "Stage 9.29 closed and version-bound",
            "Stage 10.0 Nature Methods EIC rescue roadmap scaffold serialized; implementation not started",
            "Stage 10.1 method object v2 complete; Stage 10.2 named benchmarking not started",
            "Stage 10.2 named benchmarking complete; Stage 10.3 expanded public biological demonstrations not started",
            "Stage 10.3 expanded public biological demonstrations complete; Stage 10.4 held-out validation not started",
        }
        if active_stage not in allowed_active_stages:
            failures.append("roadmap execution memory does not mark the Stage 9.29 closure boundary or Stage 10.0 post-closure scaffold as active")
        stages = {entry.get("stage"): entry for entry in memory.get("stage_lock", []) if isinstance(entry, dict)}
        if stages.get(3, {}).get("status") != "complete_for_current_gate":
            failures.append("roadmap execution memory does not keep Stage 3 complete for the current gate")
        if stages.get(4, {}).get("status") != "frozen_for_stage5":
            failures.append("roadmap execution memory does not mark Stage 4 frozen for Stage 5")
        if stages.get(5, {}).get("status") != "completed":
            failures.append("roadmap execution memory does not mark Stage 5 completed")
        if stages.get(6, {}).get("status") != "public_citable_v0.1.0":
            failures.append("roadmap execution memory does not mark Stage 6 as public_citable_v0.1.0")
        if stages.get(7, {}).get("status") != "stage7_8_complete_methods_readiness":
            failures.append("roadmap execution memory does not mark Stage 7.8 methods readiness complete")
        if stages.get(8, {}).get("status") != "conceptual_only":
            failures.append("roadmap execution memory does not keep Stage 8 conceptual only")
        if stages.get(9, {}).get("status") != "stage9_29_closed_version_bound":
            failures.append("roadmap execution memory does not mark Stage 9.29 closure as registered")
        if 10 in stages:
            stage10 = stages.get(10, {})
            if stage10.get("status") != "stage10_3_complete_public_biological_breadth":
                failures.append("roadmap execution memory does not mark Stage 10.3 public biological breadth as complete")
            for artifact in [
                "docs/stage10_nature_methods_eic_rescue_roadmap.md",
                "docs/stage10_method_object_v2.md",
                "case_studies/stage10_method_object_v2/stage10_1_method_object_gate_report.json",
                "docs/stage10_2_named_benchmarking.md",
                "scripts/run_stage10_2_named_benchmarking.py",
                "tests/test_stage10_2_named_benchmarking.py",
                "src/rhodyn/named_baselines.py",
                "case_studies/stage10_named_benchmarks/stage10_2_named_benchmark_report.json",
                "case_studies/stage10_named_benchmarks/stage10_2_synthetic_named_baseline_benchmark.csv",
                "case_studies/stage10_named_benchmarks/stage10_2_named_baseline_accuracy_summary.csv",
                "case_studies/stage10_named_benchmarks/stage10_2_public_input_named_baseline_summary.csv",
                "case_studies/stage10_named_benchmarks/stage10_2_named_tool_availability.tsv",
                "case_studies/stage10_named_benchmarks/stage10_2_runtime_memory.tsv",
                "case_studies/stage10_named_benchmarks/stage10_2_failure_boundary_report.md",
                "case_studies/stage10_named_benchmarks/stage10_2_named_benchmark_brief.md",
                "docs/stage10_3_public_biological_breadth.md",
                "scripts/run_stage10_3_public_biological_breadth.py",
                "tests/test_stage10_3_public_biological_breadth.py",
                "case_studies/stage10_public_breadth/stage10_3_public_breadth_report.json",
                "case_studies/stage10_public_breadth/stage10_3_public_system_matrix.tsv",
                "case_studies/stage10_public_breadth/stage10_3_mlci_tracking_residence_summary.csv",
                "case_studies/stage10_public_breadth/stage10_3_candidate_resolution.tsv",
                "case_studies/stage10_public_breadth/stage10_3_source_access_ledger.tsv",
                "case_studies/stage10_public_breadth/stage10_3_birtwistle_source_probe.json",
                "case_studies/stage10_public_breadth/stage10_3_public_breadth_brief.md",
            ]:
                if artifact not in stage10.get("artifacts", []):
                    failures.append(f"roadmap execution memory does not register Stage 10 artifact: {artifact}")
                if not (root / artifact).exists():
                    failures.append(f"Stage 10 artifact is missing: {artifact}")
            stage10_gate = root / "case_studies" / "stage10_method_object_v2" / "stage10_1_method_object_gate_report.json"
            if stage10_gate.exists():
                try:
                    gate_payload = json.loads(stage10_gate.read_text(encoding="utf-8"))
                except json.JSONDecodeError as exc:
                    failures.append(f"Stage 10.1 gate report is not valid JSON: {exc}")
                else:
                    if gate_payload.get("status") != "pass" or gate_payload.get("decision_count") != 12:
                        failures.append("Stage 10.1 method-object gate report must pass with 12 decisions")
            stage10_named_gate = root / "case_studies" / "stage10_named_benchmarks" / "stage10_2_named_benchmark_report.json"
            if stage10_named_gate.exists():
                try:
                    named_payload = json.loads(stage10_named_gate.read_text(encoding="utf-8"))
                except json.JSONDecodeError as exc:
                    failures.append(f"Stage 10.2 named-benchmark report is not valid JSON: {exc}")
                else:
                    if named_payload.get("status") != "pass":
                        failures.append("Stage 10.2 named-benchmark report must pass")
                    gates = named_payload.get("gates", {})
                    if not isinstance(gates, dict) or not all(gates.values()):
                        failures.append("Stage 10.2 named-benchmark gates must all pass")
                    summary = named_payload.get("summary_metrics", {})
                    if not isinstance(summary, dict) or summary.get("direct_optional_package_family_count", 0) < 3:
                        failures.append("Stage 10.2 must report at least three direct optional package families")
            else:
                failures.append("Stage 10.2 named-benchmark report is missing")
            stage10_breadth_gate = root / "case_studies" / "stage10_public_breadth" / "stage10_3_public_breadth_report.json"
            if stage10_breadth_gate.exists():
                try:
                    breadth_payload = json.loads(stage10_breadth_gate.read_text(encoding="utf-8"))
                except json.JSONDecodeError as exc:
                    failures.append(f"Stage 10.3 public-breadth report is not valid JSON: {exc}")
                else:
                    if breadth_payload.get("status") != "pass":
                        failures.append("Stage 10.3 public-breadth report must pass")
                    gates = breadth_payload.get("gates", {})
                    if not isinstance(gates, dict) or not all(gates.values()):
                        failures.append("Stage 10.3 public-breadth gates must all pass")
                    summary = breadth_payload.get("summary_metrics", {})
                    if not isinstance(summary, dict) or summary.get("counted_independent_public_systems", 0) < 4:
                        failures.append("Stage 10.3 must count at least four independent public systems")
                    if not isinstance(summary, dict) or summary.get("counted_biological_domains", 0) < 3:
                        failures.append("Stage 10.3 must count at least three biological domains")
            else:
                failures.append("Stage 10.3 public-breadth report is missing")

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
        if subphase_status.get("7.7") != "complete_usability_adoption_rehearsal":
            failures.append("Stage 7.7 must be complete_usability_adoption_rehearsal in roadmap execution memory")
        if subphase_status.get("7.8") != "complete_methods_manuscript_readiness_package":
            failures.append("Stage 7.8 must be complete_methods_manuscript_readiness_package in roadmap execution memory")
        stage9 = stages.get(9, {})
        if isinstance(stage9, dict):
            if stage9.get("current_gate") != "Stage 9 closed and version-bound":
                failures.append("Stage 9 current gate must record the Stage 9.29 closure state")
            if stage9.get("substage_count") != 33:
                failures.append("Stage 9 must serialize 33 substages")
            substage_ids = [entry.get("id") for entry in stage9.get("subphases", []) if isinstance(entry, dict)]
            if "9.6b" not in substage_ids:
                failures.append("Stage 9 must serialize the 9.6b PanelForge rendering substage")
            if "9.7" not in substage_ids:
                failures.append("Stage 9 must serialize the 9.7 supplementary display-plan substage")
            if "9.8" not in substage_ids:
                failures.append("Stage 9 must serialize the 9.8 section-contract substage")
            if "9.9" not in substage_ids:
                failures.append("Stage 9 must serialize the 9.9 title/abstract substage")
            if "9.10" not in substage_ids:
                failures.append("Stage 9 must serialize the 9.10 Results architecture substage")
            if "9.11" not in substage_ids:
                failures.append("Stage 9 must serialize the 9.11 Results drafting substage")
            if "9.12" not in substage_ids:
                failures.append("Stage 9 must serialize the 9.12 Introduction literature-binding substage")
            if "9.13" not in substage_ids:
                failures.append("Stage 9 must serialize the 9.13 Discussion interpretation-map substage")
            if "9.14" not in substage_ids:
                failures.append("Stage 9 must serialize the 9.14 Discussion drafting substage")
            if "9.15" not in substage_ids:
                failures.append("Stage 9 must serialize the 9.15 Methods architecture substage")
            if "9.16" not in substage_ids:
                failures.append("Stage 9 must serialize the 9.16 Methods drafting substage")
            if "9.17" not in substage_ids:
                failures.append("Stage 9 must serialize the 9.17 availability assembly substage")
            if "9.18" not in substage_ids:
                failures.append("Stage 9 must serialize the 9.18 Supplementary Methods substage")
            if "9.19" not in substage_ids:
                failures.append("Stage 9 must serialize the 9.19 supplementary table/source-data substage")
            if "9.20" not in substage_ids:
                failures.append("Stage 9 must serialize the 9.20 reference-library substage")
            if "9.21" not in substage_ids:
                failures.append("Stage 9 must serialize the 9.21 cross-document consistency substage")
            if "9.22" not in substage_ids:
                failures.append("Stage 9 must serialize the 9.22 statistical-language audit substage")
            if "9.23" not in substage_ids:
                failures.append("Stage 9 must serialize the 9.23 figure-legend substage")
            if "9.24" not in substage_ids:
                failures.append("Stage 9 must serialize the 9.24 editorial-polish substage")
            if "9.25" not in substage_ids:
                failures.append("Stage 9 must serialize the 9.25 editorial-polish substage")
            if "9.25b" not in substage_ids:
                failures.append("Stage 9 must serialize the 9.25b reader-surface hygiene substage")
            if "9.26" not in substage_ids:
                failures.append("Stage 9 must serialize the 9.26 internal peer-review substage")
            substage_status = {entry.get("id"): entry.get("status") for entry in stage9.get("subphases", []) if isinstance(entry, dict)}
            if substage_status.get("9.0") != "complete_evidence_locked":
                failures.append("Stage 9.0 must be marked complete_evidence_locked")
            if substage_status.get("9.1") != "complete_guidance_registered":
                failures.append("Stage 9.1 must be marked complete_guidance_registered")
            if substage_status.get("9.2") != "complete_methods_corpus_registered":
                failures.append("Stage 9.2 must be marked complete_methods_corpus_registered")
            if substage_status.get("9.3") != "complete_narrative_spine_registered":
                failures.append("Stage 9.3 must be marked complete_narrative_spine_registered")
            if substage_status.get("9.4") != "complete_claim_freeze_registered":
                failures.append("Stage 9.4 must be marked complete_claim_freeze_registered")
            if substage_status.get("9.5") != "complete_paragraph_claim_ledger_registered":
                failures.append("Stage 9.5 must be marked complete_paragraph_claim_ledger_registered")
            if substage_status.get("9.6") != "complete_figure_spine_registered":
                failures.append("Stage 9.6 must be marked complete_figure_spine_registered")
            if substage_status.get("9.6b") != "complete_panelforge_rendering_registered":
                failures.append("Stage 9.6b must be marked complete_panelforge_rendering_registered")
            if substage_status.get("9.7") != "complete_supplementary_display_plan_registered":
                failures.append("Stage 9.7 must be marked complete_supplementary_display_plan_registered")
            if substage_status.get("9.8") != "complete_section_contract_blueprint_registered":
                failures.append("Stage 9.8 must be marked complete_section_contract_blueprint_registered")
            if substage_status.get("9.9") != "complete_title_abstract_strategy_registered":
                failures.append("Stage 9.9 must be marked complete_title_abstract_strategy_registered")
            if substage_status.get("9.10") != "complete_results_architecture_registered":
                failures.append("Stage 9.10 must be marked complete_results_architecture_registered")
            if substage_status.get("9.11") != "complete_results_draft_registered":
                failures.append("Stage 9.11 must be marked complete_results_draft_registered")
            if substage_status.get("9.12") != "complete_introduction_literature_bound":
                failures.append("Stage 9.12 must be marked complete_introduction_literature_bound")
            if substage_status.get("9.13") != "complete_discussion_interpretation_mapped":
                failures.append("Stage 9.13 must be marked complete_discussion_interpretation_mapped")
            if substage_status.get("9.14") != "complete_discussion_drafted":
                failures.append("Stage 9.14 must be marked complete_discussion_drafted")
            if substage_status.get("9.15") != "complete_methods_architecture_registered":
                failures.append("Stage 9.15 must be marked complete_methods_architecture_registered")
            if substage_status.get("9.16") != "complete_methods_drafted":
                failures.append("Stage 9.16 must be marked complete_methods_drafted")
            if substage_status.get("9.17") != "complete_availability_assembled":
                failures.append("Stage 9.17 must be marked complete_availability_assembled")
            if substage_status.get("9.18") != "complete_supplementary_methods_drafted":
                failures.append("Stage 9.18 must be marked complete_supplementary_methods_drafted")
            if substage_status.get("9.19") != "complete_supplementary_tables_bound":
                failures.append("Stage 9.19 must be marked complete_supplementary_tables_bound")
            if substage_status.get("9.20") != "complete_reference_library_bound":
                failures.append("Stage 9.20 must be marked complete_reference_library_bound")
            if substage_status.get("9.21") != "complete_cross_document_consistency_bound":
                failures.append("Stage 9.21 must be marked complete_cross_document_consistency_bound")
            if substage_status.get("9.22") != "complete_statistical_language_audit_bound":
                failures.append("Stage 9.22 must be marked complete_statistical_language_audit_bound")
            if substage_status.get("9.23") != "complete_figure_legend_caption_audit_bound":
                failures.append("Stage 9.23 must be marked complete_figure_legend_caption_audit_bound")
            if substage_status.get("9.24") != "complete_editorial_polish_pass_1_bound":
                failures.append("Stage 9.24 must be marked complete_editorial_polish_pass_1_bound")
        if substage_status.get("9.25") != "complete_editorial_polish_pass_2_bound":
            failures.append("Stage 9.25 must be marked complete_editorial_polish_pass_2_bound")
        if substage_status.get("9.25b") != "complete_reader_surface_hygiene_bound":
            failures.append("Stage 9.25b must be marked complete_reader_surface_hygiene_bound")
        if substage_status.get("9.26") != "complete_internal_peer_review_bound":
            failures.append("Stage 9.26 must be marked complete_internal_peer_review_bound")
        stage9_20_gate_path = root / "manuscript" / "nature_methods" / "gate_verdicts" / "9.20.json"
        if stage9_20_gate_path.exists():
            try:
                stage9_20_gate = json.loads(stage9_20_gate_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError as exc:
                failures.append(f"Stage 9.20 gate is not valid JSON: {exc}")
                stage9_20_gate = {}
            if stage9_20_gate.get("pass") is not True:
                failures.append("Stage 9.20 reference-library gate must pass")
            if stage9_20_gate.get("next_substage") != "9.21":
                failures.append("Stage 9.20 reference-library gate must point to Stage 9.21")
            if stage9_20_gate.get("reference_count") != 14:
                failures.append("Stage 9.20 reference-library gate must record fourteen references")
            if stage9_20_gate.get("reference_cap") != 50:
                failures.append("Stage 9.20 reference-library gate must preserve the 50-reference cap")
        bib_text = (root / "manuscript" / "nature_methods" / "refs" / "references.bib").read_text(encoding="utf-8") if (root / "manuscript" / "nature_methods" / "refs" / "references.bib").exists() else ""
        citation_ledger_text = (root / "manuscript" / "nature_methods" / "refs" / "citation_claim_ledger.csv").read_text(encoding="utf-8") if (root / "manuscript" / "nature_methods" / "refs" / "citation_claim_ledger.csv").exists() else ""
        for doi in ["10.5281/zenodo.21036616", "10.5281/zenodo.20811171", "10.1038/s41587-019-0071-9", "10.1038/s42003-023-04837-8"]:
            if doi not in bib_text:
                failures.append(f"Stage 9.20 BibTeX is missing DOI {doi}")
        for source_type in ["methods", "dataset", "software"]:
            if source_type not in citation_ledger_text:
                failures.append(f"Stage 9.20 citation ledger is missing source type {source_type}")
        stage9_21_gate_path = root / "manuscript" / "nature_methods" / "gate_verdicts" / "9.21.json"
        if stage9_21_gate_path.exists():
            try:
                stage9_21_gate = json.loads(stage9_21_gate_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError as exc:
                failures.append(f"Stage 9.21 gate is not valid JSON: {exc}")
                stage9_21_gate = {}
            if stage9_21_gate.get("pass") is not True:
                failures.append("Stage 9.21 cross-document gate must pass")
            if stage9_21_gate.get("next_substage") != "9.22":
                failures.append("Stage 9.21 cross-document gate must point to Stage 9.22")
            for field, expected in {"claim_count": 5, "figure_count": 6, "statistic_count": 19, "reference_count": 14}.items():
                if stage9_21_gate.get(field) != expected:
                    failures.append(f"Stage 9.21 cross-document gate must record {field}={expected}")
            for field in ["orphan_claims", "orphan_figures", "orphan_statistics", "dangling_references", "strength_mismatches"]:
                if stage9_21_gate.get(field) not in ([], None):
                    failures.append(f"Stage 9.21 cross-document gate must have empty {field}")
        else:
            failures.append("missing Stage 9.21 cross-document gate")
        cross_document_audit = root / "manuscript" / "nature_methods" / "audits" / "cross_document_consistency_audit.md"
        if not cross_document_audit.exists():
            failures.append("missing Stage 9.21 cross-document audit")
        elif "The cross-document joins passed" not in cross_document_audit.read_text(encoding="utf-8"):
            failures.append("Stage 9.21 cross-document audit does not report passed joins")
        stage9_22_gate_path = root / "manuscript" / "nature_methods" / "gate_verdicts" / "9.22.json"
        if stage9_22_gate_path.exists():
            try:
                stage9_22_gate = json.loads(stage9_22_gate_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError as exc:
                failures.append(f"Stage 9.22 gate is not valid JSON: {exc}")
                stage9_22_gate = {}
            if stage9_22_gate.get("pass") is not True:
                failures.append("Stage 9.22 statistical-language gate must pass")
            if stage9_22_gate.get("next_substage") != "9.23":
                failures.append("Stage 9.22 statistical-language gate must point to Stage 9.23")
            if stage9_22_gate.get("statistic_count") != 19 or stage9_22_gate.get("live_number_row_count") != 19:
                failures.append("Stage 9.22 statistical-language gate must record nineteen statistic/live-number rows")
            updated_stat_ids = stage9_22_gate.get("updated_stat_ids", [])
            if stage9_22_gate.get("updated_statistic_count") != len(updated_stat_ids):
                failures.append("Stage 9.22 statistical-language gate updated_statistic_count must match updated_stat_ids")
            if any(stat_id != "STAT-0018" for stat_id in updated_stat_ids):
                failures.append("Stage 9.22 statistical-language gate may update only STAT-0018")
            if stage9_22_gate.get("figure_stat_id_map_complete") is not True:
                failures.append("Stage 9.22 statistical-language gate must complete figure statistic bindings")
            if stage9_22_gate.get("unsupported_quantitative_statements") not in ([], None):
                failures.append("Stage 9.22 statistical-language gate must have no unsupported quantitative statements")
        else:
            failures.append("missing Stage 9.22 statistical-language gate")
        statistical_audit = root / "manuscript" / "nature_methods" / "audits" / "statistical_language_audit.md"
        live_diff = root / "manuscript" / "nature_methods" / "audits" / "live_numbers_diff.csv"
        statistic_ledger = root / "manuscript" / "nature_methods" / "ledgers" / "statistic_ledger.csv"
        figure_ledger = root / "manuscript" / "nature_methods" / "ledgers" / "figure_to_claim_to_artifact.csv"
        if not statistical_audit.exists():
            failures.append("missing Stage 9.22 statistical-language audit")
        elif "The live-number audit passed" not in statistical_audit.read_text(encoding="utf-8"):
            failures.append("Stage 9.22 statistical-language audit does not report passed live-number checks")
        if live_diff.exists():
            with live_diff.open(newline="", encoding="utf-8") as handle:
                diff_rows = list(csv.DictReader(handle))
            if len(diff_rows) != 19:
                failures.append("Stage 9.22 live-number diff must contain nineteen rows")
            source_manifest = root / "case_studies" / "stage7_methods_reproducibility" / "release_archive_manifest.tsv"
            expected_stat18 = None
            if source_manifest.exists():
                with source_manifest.open(newline="", encoding="utf-8") as handle:
                    source_rows = list(csv.DictReader(handle, delimiter="\t"))
                expected_stat18 = f"row_count={len(source_rows)}"
            stat18 = next((row for row in diff_rows if row.get("stat_id") == "STAT-0018"), {})
            if stat18.get("expected_value") != expected_stat18 or stat18.get("status") not in {"pass", "updated"}:
                failures.append("Stage 9.22 live-number diff must record the STAT-0018 row_count update")
        else:
            failures.append("missing Stage 9.22 live-number diff")
        if statistic_ledger.exists():
            with statistic_ledger.open(newline="", encoding="utf-8") as handle:
                stat_rows = {row.get("stat_id"): row for row in csv.DictReader(handle)}
            source_manifest = root / "case_studies" / "stage7_methods_reproducibility" / "release_archive_manifest.tsv"
            expected_stat18 = None
            if source_manifest.exists():
                with source_manifest.open(newline="", encoding="utf-8") as handle:
                    source_rows = list(csv.DictReader(handle, delimiter="\t"))
                expected_stat18 = f"row_count={len(source_rows)}"
            if stat_rows.get("STAT-0018", {}).get("value") != expected_stat18:
                failures.append("Stage 9.22 statistic ledger must align STAT-0018 to the archive manifest row count")
        if figure_ledger.exists() and "pending_stage9.22" in figure_ledger.read_text(encoding="utf-8"):
            failures.append("Stage 9.22 figure ledger must not retain pending_stage9.22")
        stage9_23_gate_path = root / "manuscript" / "nature_methods" / "gate_verdicts" / "9.23.json"
        if stage9_23_gate_path.exists():
            try:
                stage9_23_gate = json.loads(stage9_23_gate_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError as exc:
                failures.append(f"Stage 9.23 gate is not valid JSON: {exc}")
                stage9_23_gate = {}
            if stage9_23_gate.get("pass") is not True:
                failures.append("Stage 9.23 figure-legend gate must pass")
            if stage9_23_gate.get("substage") != "9.23":
                failures.append("Stage 9.23 figure-legend gate must remain bound to substage 9.23")
            if stage9_23_gate.get("next_substage") != "9.24":
                failures.append("Stage 9.23 figure-legend gate must point to Stage 9.24")
            expected_923_counts = {
                "main_figure_legend_count": 6,
                "supplementary_figure_caption_count": 9,
                "supplementary_table_caption_count": 9,
                "statistic_count": 19,
            }
            for field, expected in expected_923_counts.items():
                if stage9_23_gate.get(field) != expected:
                    failures.append(f"Stage 9.23 figure-legend gate must record {field}={expected}")
            for field in [
                "panel_coverage_errors",
                "stat_resolution_errors",
                "supplementary_link_errors",
                "leakage_hits",
                "unsafe_claim_hits",
                "forbidden_package_paths",
            ]:
                if stage9_23_gate.get(field) not in ([], None):
                    failures.append(f"Stage 9.23 figure-legend gate must have empty {field}")
            expected_923_checks = {
                "stage_9_22_gate_passed",
                "each_main_figure_has_legend",
                "each_supplementary_figure_and_table_has_caption",
                "main_figure_panel_coverage_complete",
                "legend_statistics_resolve",
                "supplementary_callouts_resolve_to_captions",
                "legends_do_not_assert_absent_claims",
                "legend_seed_text_has_no_internal_or_panelforge_leakage",
                "no_final_package_started",
            }
            actual_923_checks = {
                item.get("name")
                for item in stage9_23_gate.get("checks", [])
                if isinstance(item, dict) and item.get("passed") is True
            }
            if actual_923_checks != expected_923_checks:
                failures.append(f"Stage 9.23 checks do not match expected checks: {sorted(actual_923_checks)}")
        else:
            failures.append("missing Stage 9.23 figure-legend gate")
        figure_legends = root / "manuscript" / "nature_methods" / "figures" / "figure_legends.md"
        figure_legend_audit = root / "manuscript" / "nature_methods" / "audits" / "figure_legend_audit.md"
        for output_path in [figure_legends, figure_legend_audit]:
            if not output_path.exists():
                failures.append(f"missing Stage 9.23 output: {output_path.relative_to(root)}")
        if figure_legends.exists():
            legend_text = figure_legends.read_text(encoding="utf-8")
            for phrase in [
                "Figure legends and table captions",
                "Figure 1 | RhoDyn defines residence-state inference as an executable method object.",
                "Figure 6 | Software parity and archive reproduction make RhoDyn decisions inspectable.",
                "Supplementary Fig. 9 | Interpretation boundaries and non-example cases.",
                "Supplementary Table 9 | Failure modes, ambiguous regimes, claim-strength caps, and wording boundaries",
            ]:
                if phrase not in legend_text:
                    failures.append(f"Stage 9.23 figure legends missing phrase: {phrase}")
            leakage_pattern = re.compile(
                r"\b(?:FIG|SFIG|STBL|SUPP|STAT|ART|CLM|PARA|MTH)-\d{3,}\b|"
                r"PanelForge|panelforge|Stage 9|stage9|manifest|ledger|audit|provenance|"
                r"render_path|source_paths|/" + r"Users/|/" + r"Volumes/"
            )
            if leakage_pattern.search(legend_text):
                failures.append("Stage 9.23 figure legends must not expose internal IDs, paths, or engine provenance")
            for unsafe in [
                "no crosstalk",
                "absence of all pathway communication",
                "literal molecular edge",
                "direct live metabolic reserve assay",
                "universal coupling rule",
                "PyPI publication",
            ]:
                if unsafe.lower() in legend_text.lower():
                    failures.append(f"Stage 9.23 figure legends contain unsafe claim wording: {unsafe}")
        if figure_legend_audit.exists():
            audit_text = figure_legend_audit.read_text(encoding="utf-8")
            for phrase in [
                "The figure legend and caption audit passed",
                "Six main figure legends, nine supplementary figure legends, and nine supplementary table captions were written",
                "every figure and table statistic binding resolves",
                "does not assemble the full manuscript",
            ]:
                if phrase not in audit_text:
                    failures.append(f"Stage 9.23 figure-legend audit missing phrase: {phrase}")
        stage9_24_gate_path = root / "manuscript" / "nature_methods" / "gate_verdicts" / "9.24.json"
        if stage9_24_gate_path.exists():
            try:
                stage9_24_gate = json.loads(stage9_24_gate_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError as exc:
                failures.append(f"Stage 9.24 gate is not valid JSON: {exc}")
                stage9_24_gate = {}
            if stage9_24_gate.get("pass") is not True:
                failures.append("Stage 9.24 editorial-polish gate must pass")
            if stage9_24_gate.get("substage") != "9.24":
                failures.append("Stage 9.24 editorial-polish gate must remain bound to substage 9.24")
            if stage9_24_gate.get("next_substage") != "9.25":
                failures.append("Stage 9.24 editorial-polish gate must point to Stage 9.25")
            for field in ["paragraph_errors", "unsafe_hits", "missing_limits", "reader_stage_hits", "downstream_paths"]:
                if stage9_24_gate.get(field) not in ([], None):
                    failures.append(f"Stage 9.24 editorial-polish gate must have empty {field}")
            if stage9_24_gate.get("terminal_calls") not in ({}, None):
                failures.append("Stage 9.24 editorial-polish gate must have no terminal figure calls")
            expected_924_checks = {
                "stage_9_23_gate_passed",
                "paragraph_id_set_unchanged",
                "strength_caps_hold",
                "limitations_remain_present",
                "dynamic_figure_call_flow_preserved",
                "reader_surface_stage_language_absent",
                "recursive_editorial_replacements_resolved",
                "no_downstream_stage_started",
            }
            actual_924_checks = {
                item.get("name")
                for item in stage9_24_gate.get("checks", [])
                if isinstance(item, dict) and item.get("passed") is True
            }
            if actual_924_checks != expected_924_checks:
                failures.append(f"Stage 9.24 checks do not match expected checks: {sorted(actual_924_checks)}")
        else:
            failures.append("missing Stage 9.24 editorial-polish gate")
        editorial_audit = root / "manuscript" / "nature_methods" / "audits" / "editorial_pass_1.md"
        if not editorial_audit.exists():
            failures.append("missing Stage 9.24 output: manuscript/nature_methods/audits/editorial_pass_1.md")
        else:
            audit_text = editorial_audit.read_text(encoding="utf-8")
            for phrase in [
                "Stage 9.24 editorial polish pass I",
                "Paragraph IDs were preserved",
                "claim-strength caps remained intact",
                "limitations stayed present",
                "does not broaden the residence",
            ]:
                if phrase not in audit_text:
                    failures.append(f"Stage 9.24 editorial-polish audit missing phrase: {phrase}")
        stage9_25_gate_path = root / "manuscript" / "nature_methods" / "gate_verdicts" / "9.25.json"
        if stage9_25_gate_path.exists():
            try:
                stage9_25_gate = json.loads(stage9_25_gate_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError as exc:
                failures.append(f"Stage 9.25 gate is not valid JSON: {exc}")
                stage9_25_gate = {}
            if stage9_25_gate.get("pass") is not True:
                failures.append("Stage 9.25 editorial-polish gate must pass")
            if stage9_25_gate.get("substage") != "9.25":
                failures.append("Stage 9.25 editorial-polish gate must remain bound to substage 9.25")
            if stage9_25_gate.get("next_substage") != "9.25b":
                failures.append("Stage 9.25 editorial-polish gate must point to Stage 9.25b")
            for field in ["paragraph_errors", "claim_id_errors", "figure_call_errors", "style_errors", "unsafe_hits", "missing_limits", "process_hits", "reader_stage_hits", "downstream_paths"]:
                if stage9_25_gate.get(field) not in ([], None):
                    failures.append(f"Stage 9.25 editorial-polish gate must have empty {field}")
            if stage9_25_gate.get("terminal_calls") not in ({}, None):
                failures.append("Stage 9.25 editorial-polish gate must have no terminal figure calls")
            expected_925_checks = {
                "stage_9_24_gate_passed",
                "meaning_preserved",
                "style_metrics_pass_thresholds",
                "no_claim_broadened",
                "venue_style_replacements_resolved",
                "dynamic_figure_call_flow_preserved",
                "reader_surface_stage_language_absent",
                "no_reader_hygiene_or_package_started",
            }
            actual_925_checks = {
                item.get("name")
                for item in stage9_25_gate.get("checks", [])
                if isinstance(item, dict) and item.get("passed") is True
            }
            if actual_925_checks != expected_925_checks:
                failures.append(f"Stage 9.25 checks do not match expected checks: {sorted(actual_925_checks)}")
        else:
            failures.append("missing Stage 9.25 editorial-polish gate")
        editorial_audit_2 = root / "manuscript" / "nature_methods" / "audits" / "editorial_pass_2.md"
        if not editorial_audit_2.exists():
            failures.append("missing Stage 9.25 output: manuscript/nature_methods/audits/editorial_pass_2.md")
        else:
            audit_text = editorial_audit_2.read_text(encoding="utf-8")
            for phrase in [
                "Stage 9.25 editorial polish pass II",
                "second reader-facing polish loop",
                "Paragraph IDs, claim IDs, and Results figure calls were preserved",
                "within threshold",
                "does not broaden the residence",
            ]:
                if phrase not in audit_text:
                    failures.append(f"Stage 9.25 editorial-polish audit missing phrase: {phrase}")
        stage9_25b_gate_path = root / "manuscript" / "nature_methods" / "gate_verdicts" / "9.25b.json"
        if stage9_25b_gate_path.exists():
            try:
                stage9_25b_gate = json.loads(stage9_25b_gate_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError as exc:
                failures.append(f"Stage 9.25b gate is not valid JSON: {exc}")
                stage9_25b_gate = {}
            if stage9_25b_gate.get("pass") is not True:
                failures.append("Stage 9.25b reader-surface hygiene gate must pass")
            if stage9_25b_gate.get("substage") != "9.25b":
                failures.append("Stage 9.25b reader-surface hygiene gate must remain bound to substage 9.25b")
            if stage9_25b_gate.get("next_substage") != "9.26":
                failures.append("Stage 9.25b reader-surface hygiene gate must point to Stage 9.26")
            for field in [
                "comment_hits",
                "internal_id_hits",
                "stage_language_hits",
                "unsafe_hits",
                "local_path_hits",
                "secret_hits",
                "missing_required_terms",
                "figure_call_errors",
                "downstream_paths",
                "panel_s3_crossrefs",
            ]:
                if stage9_25b_gate.get(field) not in ([], None):
                    failures.append(f"Stage 9.25b reader-surface hygiene gate must have empty {field}")
            if stage9_25b_gate.get("terminal_calls") not in ({}, None):
                failures.append("Stage 9.25b reader-surface hygiene gate must have no terminal figure calls")
            if stage9_25b_gate.get("missing_surface_phrases") not in ({}, None):
                failures.append("Stage 9.25b reader-surface hygiene gate must have no missing surface phrases")
            expected_925b_checks = {
                "stage_9_25_gate_passed",
                "reader_comments_removed",
                "internal_ids_absent_from_reader_surfaces",
                "stage_and_build_language_absent",
                "legends_and_captions_free_of_lineage_language",
                "meaning_and_figure_flow_preserved",
                "claim_boundaries_preserved",
                "local_path_and_secret_scan_clear",
                "no_internal_peer_review_or_package_started",
            }
            actual_925b_checks = {
                item.get("name")
                for item in stage9_25b_gate.get("checks", [])
                if isinstance(item, dict) and item.get("passed") is True
            }
            if actual_925b_checks != expected_925b_checks:
                failures.append(f"Stage 9.25b checks do not match expected checks: {sorted(actual_925b_checks)}")
        else:
            failures.append("missing Stage 9.25b reader-surface hygiene gate")
        hygiene_audit = root / "manuscript" / "nature_methods" / "audits" / "reader_surface_hygiene_report.md"
        if not hygiene_audit.exists():
            failures.append("missing Stage 9.25b output: manuscript/nature_methods/audits/reader_surface_hygiene_report.md")
        else:
            audit_text = hygiene_audit.read_text(encoding="utf-8")
            for phrase in [
                "Stage 9.25b reader-surface hygiene report",
                "Hidden comments were removed",
                "Introduction reference tokens were converted",
                "does not add new biological evidence",
            ]:
                if phrase not in audit_text:
                    failures.append(f"Stage 9.25b reader-surface hygiene audit missing phrase: {phrase}")
        stage9_26_gate_path = root / "manuscript" / "nature_methods" / "gate_verdicts" / "9.26.json"
        if stage9_26_gate_path.exists():
            try:
                stage9_26_gate = json.loads(stage9_26_gate_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError as exc:
                failures.append(f"Stage 9.26 gate is not valid JSON: {exc}")
                stage9_26_gate = {}
            if stage9_26_gate.get("pass") is not True:
                failures.append("Stage 9.26 internal peer-review gate must pass")
            if stage9_26_gate.get("substage") != "9.26":
                failures.append("Stage 9.26 internal peer-review gate must remain bound to substage 9.26")
            if stage9_26_gate.get("next_substage") != "9.27":
                failures.append("Stage 9.26 internal peer-review gate must point to Stage 9.27")
            if stage9_26_gate.get("reviewer_perspective_count") != 8:
                failures.append("Stage 9.26 gate must include eight reviewer perspectives")
            if stage9_26_gate.get("action_row_count") != 16:
                failures.append("Stage 9.26 gate must include sixteen action rows")
            for field in [
                "missing_perspectives",
                "unsupported_rows",
                "blocking_without_resolution",
                "schema_errors",
                "downstream_paths",
            ]:
                if stage9_26_gate.get(field) not in ([], None):
                    failures.append(f"Stage 9.26 internal peer-review gate must have empty {field}")
            expected_926_checks = {
                "stage_9_25b_gate_passed",
                "all_eight_perspectives_present",
                "blocking_concerns_have_resolution_status",
                "unsupported_central_claims_are_routed",
                "panelforge_figure_assembly_status_recorded",
                "no_submission_package_started",
            }
            actual_926_checks = {
                item.get("name")
                for item in stage9_26_gate.get("checks", [])
                if isinstance(item, dict) and item.get("passed") is True
            }
            if actual_926_checks != expected_926_checks:
                failures.append(f"Stage 9.26 checks do not match expected checks: {sorted(actual_926_checks)}")
            panelforge_status = stage9_26_gate.get("panelforge_status", {})
            if not isinstance(panelforge_status, dict):
                failures.append("Stage 9.26 gate must include a PanelForge status object")
                panelforge_status = {}
            if panelforge_status.get("rendered_file_count") != 18:
                failures.append("Stage 9.26 PanelForge status must record eighteen rendered files")
            if panelforge_status.get("missing_rendered_paths") not in ([], None):
                failures.append("Stage 9.26 PanelForge status must have no missing rendered paths")
            if panelforge_status.get("legend_gate_pass") is not True:
                failures.append("Stage 9.26 PanelForge status must preserve the Stage 9.23 legend gate pass")
        else:
            failures.append("missing Stage 9.26 internal peer-review gate")
        peer_review_audit = root / "manuscript" / "nature_methods" / "audits" / "internal_peer_review_simulation.md"
        if not peer_review_audit.exists():
            failures.append("missing Stage 9.26 output: manuscript/nature_methods/audits/internal_peer_review_simulation.md")
        else:
            audit_text = peer_review_audit.read_text(encoding="utf-8")
            for phrase in [
                "Stage 9.26 internal peer-review simulation",
                "PanelForge figure assembly status",
                "No fatal scientific blocker is left without a resolution status",
                "Proceed to Stage 9.27 package assembly",
            ]:
                if phrase not in audit_text:
                    failures.append(f"Stage 9.26 internal peer-review audit missing phrase: {phrase}")
        reviewer_matrix = root / "manuscript" / "nature_methods" / "audits" / "reviewer_action_matrix.csv"
        if not reviewer_matrix.exists():
            failures.append("missing Stage 9.26 output: manuscript/nature_methods/audits/reviewer_action_matrix.csv")
        else:
            rows = list(csv.DictReader(reviewer_matrix.open(encoding="utf-8")))
            perspectives = {row.get("reviewer_perspective") for row in rows}
            if len(rows) != 16:
                failures.append("Stage 9.26 reviewer action matrix must contain sixteen rows")
            if len(perspectives) != 8:
                failures.append("Stage 9.26 reviewer action matrix must contain eight perspectives")
            allowed_statuses = {"resolved", "narrowed", "routed_upstream"}
            bad_statuses = sorted(
                {
                    row.get("resolution_status", "")
                    for row in rows
                    if row.get("resolution_status", "") not in allowed_statuses
                }
            )
            if bad_statuses:
                failures.append(f"Stage 9.26 reviewer action matrix has unsupported statuses: {bad_statuses}")
            if any(not row.get("resolution", "").strip() for row in rows):
                failures.append("Stage 9.26 reviewer action matrix must include a resolution for every row")
        stage9_27_gate_path = root / "manuscript" / "nature_methods" / "gate_verdicts" / "9.27.json"
        if stage9_27_gate_path.exists():
            try:
                stage9_27_gate = json.loads(stage9_27_gate_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError as exc:
                failures.append(f"Stage 9.27 gate is not valid JSON: {exc}")
                stage9_27_gate = {}
            if stage9_27_gate.get("pass") is not True:
                failures.append("Stage 9.27 submission package gate must pass")
            if stage9_27_gate.get("substage") != "9.27":
                failures.append("Stage 9.27 submission package gate must remain bound to substage 9.27")
            if stage9_27_gate.get("next_substage") != "9.28":
                failures.append("Stage 9.27 submission package gate must point to Stage 9.28")
            if stage9_27_gate.get("figure_file_count") != 18:
                failures.append("Stage 9.27 submission package gate must record eighteen figure files")
            if stage9_27_gate.get("source_inventory_rows") != 28:
                failures.append("Stage 9.27 submission package gate must record twenty-eight source/statistics inventory rows")
            expected_927_checks = {
                "stage_9_26_gate_passed",
                "required_inputs_present",
                "main_text_present",
                "supplement_present",
                "reader_surface_hygiene_passed",
                "cross_document_consistency_gate_passed",
                "legend_gate_passed",
                "figure_files_present",
                "panelforge_status_bound",
                "reporting_summary_present",
                "reporting_summary_answer_bank_present",
                "code_for_review_present",
            "editor_triage_note_present",
            "editorial_pitch_present",
            "cover_letter_draft_present",
            "final_upload_runbook_present",
            "prior_art_positioning_matrix_present",
                "validation_breadth_map_present",
                "editor_objection_response_map_present",
                "editor_two_minute_triage_simulation_present",
                "editorial_bar_rescue_audit_present",
                "current_policy_preflight_present",
                "reviewer_editor_fit_planner_present",
                "software_reporting_checklist_present",
                "article_fit_checklist_present",
                "author_declarations_present",
                "ai_disclosure_draft_present",
                "title_author_metadata_present",
                "package_safety_scan_clear",
                "no_downstream_pi_or_closure_started",
                "package_consistency_audit_passed",
            }
            actual_927_checks = {
                item.get("name")
                for item in stage9_27_gate.get("checks", [])
                if isinstance(item, dict) and item.get("passed") is True
            }
            if actual_927_checks != expected_927_checks:
                failures.append(f"Stage 9.27 checks do not match expected checks: {sorted(actual_927_checks)}")
        else:
            failures.append("missing Stage 9.27 submission package gate")
        for rel in [
            "manuscript/nature_methods/submission_package/main_text_for_submission.md",
            "manuscript/nature_methods/submission_package/supplementary_information_for_submission.md",
            "manuscript/nature_methods/submission_package/code_for_review.md",
            "manuscript/nature_methods/submission_package/editor_triage_note_for_cover_letter.md",
            "manuscript/nature_methods/submission_package/editorial_pitch_for_submission.md",
            "manuscript/nature_methods/submission_package/cover_letter_for_submission_AUTHOR_CONFIRMATION_REQUIRED.md",
            "manuscript/nature_methods/submission_package/final_upload_runbook_AUTHOR_CONFIRMATION_REQUIRED.md",
            "manuscript/nature_methods/submission_package/prior_art_positioning_matrix.md",
            "manuscript/nature_methods/submission_package/validation_breadth_and_boundary_map.md",
            "manuscript/nature_methods/submission_package/editor_objection_response_map.md",
            "manuscript/nature_methods/submission_package/editor_two_minute_triage_simulation.md",
            "manuscript/nature_methods/submission_package/nature_methods_editorial_bar_rescue_audit.md",
            "manuscript/nature_methods/submission_package/current_nature_methods_policy_preflight.md",
            "manuscript/nature_methods/submission_package/reviewer_editor_fit_planner_AUTHOR_CONFIRMATION_REQUIRED.md",
            "manuscript/nature_methods/submission_package/software_reporting_checklist.md",
            "manuscript/nature_methods/submission_package/article_fit_checklist.md",
            "manuscript/nature_methods/submission_package/author_declarations_REQUIRED.md",
            "manuscript/nature_methods/submission_package/ai_disclosure_AUTHOR_CONFIRMATION_REQUIRED.md",
            "manuscript/nature_methods/submission_package/title_author_metadata_AUTHOR_CONFIRMATION_REQUIRED.md",
            "manuscript/nature_methods/submission_package/reporting_summary_answer_bank_AUTHOR_CONFIRMATION_REQUIRED.md",
            "manuscript/nature_methods/submission_package/submission_readiness_checklist.md",
            "manuscript/nature_methods/submission_package/package_consistency_audit.md",
        ]:
            if not (root / rel).exists():
                failures.append(f"missing Stage 9.27 package output: {rel}")
        stage9_28_gate_path = root / "manuscript" / "nature_methods" / "gate_verdicts" / "9.28.json"
        if stage9_28_gate_path.exists():
            try:
                stage9_28_gate = json.loads(stage9_28_gate_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError as exc:
                failures.append(f"Stage 9.28 gate is not valid JSON: {exc}")
                stage9_28_gate = {}
            if stage9_28_gate.get("pass") is not True:
                failures.append("Stage 9.28 PI-review gate must pass")
            if stage9_28_gate.get("substage") != "9.28":
                failures.append("Stage 9.28 PI-review gate must remain bound to substage 9.28")
            if stage9_28_gate.get("next_substage") != "9.29":
                failures.append("Stage 9.28 PI-review gate must point to Stage 9.29")
            if stage9_28_gate.get("auto_revision_count") != 5:
                failures.append("Stage 9.28 must retain five evidence-safe source revisions")
            if stage9_28_gate.get("major_review_item_count") != 7:
                failures.append("Stage 9.28 PI review packet must contain seven major items")
            if stage9_28_gate.get("minor_review_item_count") != 8:
                failures.append("Stage 9.28 PI review packet must contain eight minor items")
            if stage9_28_gate.get("action_matrix_rows") != 6:
                failures.append("Stage 9.28 action matrix must contain six rows")
            expected_928_checks = {
                "stage_9_27_package_regenerated",
                "persona_prompt_available",
                "pi_review_packet_present",
                "required_review_headings_exact",
                "major_minor_review_items_present",
                "confidential_recommendation_allowed",
                "review_surface_hygiene_passed",
                "safe_source_revisions_applied",
                "action_matrix_present",
                "revision_log_present",
                "literature_calibration_present",
                "reader_surface_hygiene_passed",
                "package_safety_scan_clear",
                "panelforge_status_unchanged",
                "no_stage9_closure_started",
            }
            actual_928_checks = {
                item.get("name")
                for item in stage9_28_gate.get("checks", [])
                if isinstance(item, dict) and item.get("passed") is True
            }
            if actual_928_checks != expected_928_checks:
                failures.append(f"Stage 9.28 checks do not match expected checks: {sorted(actual_928_checks)}")
        else:
            failures.append("missing Stage 9.28 PI-review gate")
        for rel in [
            "manuscript/nature_methods/submission_package/pi_review_packet.md",
            "manuscript/nature_methods/submission_package/pi_review_action_matrix.csv",
            "manuscript/nature_methods/submission_package/pi_review_revision_log.md",
            "manuscript/nature_methods/submission_package/pi_review_literature_calibration.md",
        ]:
            if not (root / rel).exists():
                failures.append(f"missing Stage 9.28 PI-review output: {rel}")
        stage9_29_gate_path = root / "manuscript" / "nature_methods" / "gate_verdicts" / "9.29.json"
        if stage9_29_gate_path.exists():
            try:
                stage9_29_gate = json.loads(stage9_29_gate_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError as exc:
                failures.append(f"Stage 9.29 gate is not valid JSON: {exc}")
                stage9_29_gate = {}
            if stage9_29_gate.get("pass") is not True:
                failures.append("Stage 9.29 closure gate must pass")
            if stage9_29_gate.get("substage") != "9.29":
                failures.append("Stage 9.29 closure gate must remain bound to substage 9.29")
            if stage9_29_gate.get("next_substage") != "none":
                failures.append("Stage 9.29 closure gate must be terminal")
            if stage9_29_gate.get("closure_status") != "complete_stage9_closed_version_bound":
                failures.append("Stage 9.29 closure status must be complete_stage9_closed_version_bound")
            expected_929_checks = {
                "stage_9_28_gate_passed",
                "all_stage9_gates_pass",
                "quarantine_has_no_unresolved_blocker",
                "package_files_present",
                "assembly_source_commit_in_history",
                "package_version_bound",
                "evidence_version_bound",
                "release_version_bound",
                "limitation_version_bound",
                "pi_review_action_decisions_recorded",
                "human_submission_actions_retained",
                "completion_report_present",
                "version_binding_present",
                "package_safety_scan_clear",
                "panelforge_status_bound",
            }
            actual_929_checks = {
                item.get("name")
                for item in stage9_29_gate.get("checks", [])
                if isinstance(item, dict) and item.get("passed") is True
            }
            if actual_929_checks != expected_929_checks:
                failures.append(f"Stage 9.29 checks do not match expected checks: {sorted(actual_929_checks)}")
            if stage9_29_gate.get("action_decision_rows") != 6:
                failures.append("Stage 9.29 must record six PI-review action decisions")
            if stage9_29_gate.get("human_submission_action_rows") != 1:
                failures.append("Stage 9.29 must retain one human submission action")
            if stage9_29_gate.get("package_file_count") != 32:
                failures.append("Stage 9.29 must bind thirty-two package files")
            if stage9_29_gate.get("rendered_figure_file_count") != 18:
                failures.append("Stage 9.29 must bind eighteen rendered figure files")
            binding_path = root / "manuscript" / "nature_methods" / "stage9_closure_version_binding.json"
            if binding_path.exists():
                try:
                    binding = json.loads(binding_path.read_text(encoding="utf-8"))
                except json.JSONDecodeError as exc:
                    failures.append(f"Stage 9.29 version binding is not valid JSON: {exc}")
                    binding = {}
                assembly_commit = binding.get("assembly_source_commit") or binding.get("closure_commit")
                if not assembly_commit:
                    failures.append("Stage 9.29 version binding must record an assembly source commit")
                else:
                    ancestor = subprocess.run(
                        ["git", "merge-base", "--is-ancestor", str(assembly_commit), "HEAD"],
                        cwd=root,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                        check=False,
                    )
                    if ancestor.returncode != 0:
                        failures.append("Stage 9.29 assembly source commit must be in the current repository history")
                for row in binding.get("package_files", []):
                    rel = row.get("path")
                    if not rel:
                        failures.append("Stage 9.29 package file row is missing a path")
                        continue
                    path = root / rel
                    if not path.exists():
                        failures.append(f"Stage 9.29 package file listed in binding is missing: {rel}")
                        continue
                    expected_hash = row.get("sha256")
                    if expected_hash and _sha256(path) != expected_hash:
                        failures.append(f"Stage 9.29 package file hash is stale: {rel}")
        else:
            failures.append("missing Stage 9.29 closure gate")
        for rel in [
            "manuscript/nature_methods/stage9_completion_report.md",
            "manuscript/nature_methods/stage9_closure_version_binding.json",
            "manuscript/nature_methods/submission_package/pi_review_action_decisions.csv",
        ]:
            if not (root / rel).exists():
                failures.append(f"missing Stage 9.29 closure output: {rel}")
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
    stage7_6_recursive_report_path = root / "docs" / "stage7_6_recursive_hardening_report.json"
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
            "release_archive_manifest_is_complete",
            "release_archive_deterministic_outputs_present",
            "source_distribution_members_complete",
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
        archive_manifest = stage7_6_gate.get("release_archive_manifest_summary", {})
        if not isinstance(archive_manifest, dict) or archive_manifest.get("manifest_status") != "pass":
            failures.append("Stage 7.6 gate report must include a passing release archive manifest summary")
        elif archive_manifest.get("raw_private_like_file_count") != 0:
            failures.append("Stage 7.6 release archive manifest must not include raw/private-like files")
        elif archive_manifest.get("missing_deterministic_outputs"):
            failures.append("Stage 7.6 release archive manifest must include all selected deterministic outputs")
        distribution_summary = stage7_6_gate.get("distribution_member_summary", {})
        if not isinstance(distribution_summary, dict) or distribution_summary.get("sdist_status") != "pass":
            failures.append("Stage 7.6 source distribution member summary must pass")

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

    if stage7_6_recursive_report_path.exists():
        try:
            stage7_6_recursive = json.loads(stage7_6_recursive_report_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            failures.append(f"Stage 7.6 recursive hardening report is not valid JSON: {exc}")
            stage7_6_recursive = {}
        if stage7_6_recursive.get("status") != "pass":
            failures.append("Stage 7.6 recursive hardening report does not pass")
        checks = stage7_6_recursive.get("checks", {}) if isinstance(stage7_6_recursive.get("checks", {}), dict) else {}
        for check_name in [
            "gate_reports_identical",
            "full_archive_mode",
            "deterministic_outputs_match",
            "cross_surface_parity_matches",
            "archive_manifest_complete",
            "workflow_checks_pass",
            "scope_boundary_preserved",
            "deterministic_outputs_in_archive_manifest",
            "source_distribution_members_complete",
            "release_checksums_cover_stage7_6",
            "report_surfaces_sanitized",
        ]:
            if checks.get(check_name) != "pass":
                failures.append(f"Stage 7.6 recursive hardening check does not pass: {check_name}")
        boundary = str(stage7_6_recursive.get("interpretation_boundary", ""))
        if "does not add biological evidence" not in boundary:
            failures.append("Stage 7.6 recursive hardening report must preserve the no-new-biological-evidence boundary")

    stage7_7_gate_path = root / "docs" / "stage7_7_gate_report.json"
    stage7_7_case_report_path = root / "case_studies" / "stage7_usability_rehearsal" / "stage7_7_usability_gate_report.json"
    biologist_result_path = root / "case_studies" / "stage7_usability_rehearsal" / "biologist_residence_task_result.json"
    quantitative_result_path = root / "case_studies" / "stage7_usability_rehearsal" / "quantitative_reproduction_result.json"
    export_manifest_path = root / "case_studies" / "stage7_usability_rehearsal" / "export_examples_manifest.tsv"
    if stage7_7_gate_path.exists():
        try:
            stage7_7_gate = json.loads(stage7_7_gate_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            failures.append(f"Stage 7.7 gate report is not valid JSON: {exc}")
            stage7_7_gate = {}
        if stage7_7_gate.get("status") != "pass":
            failures.append("Stage 7.7 gate report does not pass")
        if stage7_7_gate.get("completion_state") != "complete_usability_adoption_rehearsal":
            failures.append("Stage 7.7 gate report does not mark usability/adoption rehearsal complete")
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
                failures.append(f"Stage 7.7 gate checkpoint does not pass: {checkpoint}")
        if checkpoints.get("stop_condition_user_cannot_interpret_result") != "not_triggered":
            failures.append("Stage 7.7 user-path stop condition must remain not_triggered")
        boundary = str(stage7_7_gate.get("interpretation_boundary", ""))
        if "does not add a new biological system" not in boundary:
            failures.append("Stage 7.7 gate report must preserve the no-new-biological-system boundary")

    if stage7_7_case_report_path.exists():
        try:
            stage7_7_case_report = json.loads(stage7_7_case_report_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            failures.append(f"Stage 7.7 case report is not valid JSON: {exc}")
            stage7_7_case_report = {}
        if stage7_7_case_report.get("status") != "pass":
            failures.append("Stage 7.7 usability case report does not pass")
        if stage7_7_case_report.get("completion_state") != "complete_usability_adoption_rehearsal":
            failures.append("Stage 7.7 usability case report does not mark usability/adoption rehearsal complete")

    if biologist_result_path.exists():
        try:
            biologist_result = json.loads(biologist_result_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            failures.append(f"Stage 7.7 biologist task result is not valid JSON: {exc}")
            biologist_result = {}
        if biologist_result.get("status") != "pass":
            failures.append("Stage 7.7 biologist residence task does not pass")
        if biologist_result.get("python_cli_backend_parity") is not True:
            failures.append("Stage 7.7 biologist task must preserve Python/CLI/backend parity")

    if quantitative_result_path.exists():
        try:
            quantitative_result = json.loads(quantitative_result_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            failures.append(f"Stage 7.7 quantitative task result is not valid JSON: {exc}")
            quantitative_result = {}
        if quantitative_result.get("status") != "pass":
            failures.append("Stage 7.7 quantitative reproduction task does not pass")
        if quantitative_result.get("python_cli_backend_coupling_parity") is not True:
            failures.append("Stage 7.7 quantitative task must preserve bounded-coupling parity")

    if export_manifest_path.exists():
        rows = [line.split("\t") for line in export_manifest_path.read_text(encoding="utf-8").splitlines()]
        if len(rows) < 3:
            failures.append("Stage 7.7 export manifest must contain both rehearsal bundles")
        else:
            header = rows[0]
            for required in ["has_parameters", "has_input_schema", "has_grouping", "software_version"]:
                if required not in header:
                    failures.append(f"Stage 7.7 export manifest missing column: {required}")
            for row in rows[1:]:
                values = dict(zip(header, row))
                if values.get("has_parameters") != "1" or values.get("has_input_schema") != "1" or values.get("has_grouping") != "1":
                    failures.append(f"Stage 7.7 export bundle missing required metadata: {values.get('bundle')}")
                if values.get("software_version") != "0.1.0":
                    failures.append(f"Stage 7.7 export bundle must record software version 0.1.0: {values.get('bundle')}")

    stage7_8_gate_path = root / "docs" / "stage7_8_gate_report.json"
    stage7_8_case_report_path = root / "case_studies" / "stage7_methods_readiness" / "stage7_8_methods_readiness_gate_report.json"
    if stage7_8_gate_path.exists():
        try:
            stage7_8_gate = json.loads(stage7_8_gate_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            failures.append(f"Stage 7.8 gate report is not valid JSON: {exc}")
            stage7_8_gate = {}
        if stage7_8_gate.get("status") != "pass":
            failures.append("Stage 7.8 gate report does not pass")
        if stage7_8_gate.get("completion_state") != "complete_methods_manuscript_readiness_package":
            failures.append("Stage 7.8 gate report does not mark methods manuscript readiness complete")
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
                failures.append(f"Stage 7.8 gate checkpoint does not pass: {checkpoint}")
        if checkpoints.get("stop_condition_unlinked_claim_or_figure") != "not_triggered":
            failures.append("Stage 7.8 unlinked-claim stop condition must remain not_triggered")
        boundary = str(stage7_8_gate.get("interpretation_boundary", ""))
        if "does not add a biological system" not in boundary or "new analysis route" not in boundary:
            failures.append("Stage 7.8 gate report must preserve the no-new-analysis boundary")

    if stage7_8_case_report_path.exists():
        try:
            stage7_8_case_report = json.loads(stage7_8_case_report_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            failures.append(f"Stage 7.8 case report is not valid JSON: {exc}")
            stage7_8_case_report = {}
        if stage7_8_case_report.get("status") != "pass":
            failures.append("Stage 7.8 methods readiness case report does not pass")
        if stage7_8_case_report.get("completion_state") != "complete_methods_manuscript_readiness_package":
            failures.append("Stage 7.8 methods readiness case report does not mark readiness complete")

    stage7_7_8_recursive_path = root / "docs" / "stage7_7_8_recursive_hardening_report.json"
    stage7_7_8_recursive_case_path = root / "case_studies" / "stage7_methods_readiness" / "stage7_7_8_recursive_hardening_report.json"
    if stage7_7_8_recursive_path.exists():
        try:
            stage7_7_8_recursive = json.loads(stage7_7_8_recursive_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            failures.append(f"Stage 7.7/7.8 recursive hardening report is not valid JSON: {exc}")
            stage7_7_8_recursive = {}
        if stage7_7_8_recursive.get("status") != "pass":
            failures.append("Stage 7.7/7.8 recursive hardening report does not pass")
        if stage7_7_8_recursive.get("completion_state") != "stage7_7_8_recursively_hardened":
            failures.append("Stage 7.7/7.8 recursive hardening report does not mark recursive hardening complete")
        checks = stage7_7_8_recursive.get("checks", {}) if isinstance(stage7_7_8_recursive.get("checks", {}), dict) else {}
        for check_name in [
            "stage7_7_gate_pair_identical",
            "stage7_8_gate_pair_identical",
            "stage7_7_export_bundles_verified",
            "stage7_8_crosswalks_match_runner_constants",
            "stage7_8_evidence_paths_and_validation_status_pass",
            "release_checksums_cover_stage7_7_8",
            "release_archive_manifest_covers_nonbinary_stage7_7_8",
            "phase9_boundary_preserved",
        ]:
            if checks.get(check_name) != "pass":
                failures.append(f"Stage 7.7/7.8 recursive hardening check does not pass: {check_name}")
        boundary = str(stage7_7_8_recursive.get("interpretation_boundary", ""))
        if "does not add biological evidence" not in boundary or "Phase 9" not in boundary:
            failures.append("Stage 7.7/7.8 recursive hardening report must preserve the no-new-evidence and Phase 9 boundary")
    if stage7_7_8_recursive_path.exists() and stage7_7_8_recursive_case_path.exists():
        try:
            doc_recursive = json.loads(stage7_7_8_recursive_path.read_text(encoding="utf-8"))
            case_recursive = json.loads(stage7_7_8_recursive_case_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            doc_recursive = {}
            case_recursive = {}
        if doc_recursive != case_recursive:
            failures.append("Stage 7.7/7.8 recursive hardening doc and case reports must be identical")

    stage9_check = subprocess.run(
        [sys.executable, "scripts/check_stage9_scaffold.py"],
        cwd=root,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if stage9_check.returncode != 0:
        detail = (stage9_check.stdout or stage9_check.stderr).strip()
        failures.append(f"Stage 9 scaffold check does not pass: {detail[:1200]}")

    public_access_path = root / "manuscript" / "nature_methods" / "audits" / "nature_methods_public_access_verification.json"
    public_access_md = root / "manuscript" / "nature_methods" / "audits" / "nature_methods_public_access_verification.md"
    if public_access_path.exists():
        try:
            public_access = json.loads(public_access_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            failures.append(f"Nature Methods public-access verification is not valid JSON: {exc}")
            public_access = {}
        if public_access.get("status") != "pass":
            failures.append("Nature Methods public-access verification does not pass")
        public_access_checks = (
            public_access.get("checks", {}) if isinstance(public_access.get("checks", {}), dict) else {}
        )
        for check_name in [
            "all_visible_public_urls_resolve",
            "expected_release_dataset_and_renderer_urls_present",
            "unresolved_optional_reference_case_links_not_advertised",
        ]:
            if public_access_checks.get(check_name) is not True:
                failures.append(f"Nature Methods public-access check failed or missing: {check_name}")
        if public_access.get("failed_urls") not in ([], None):
            failures.append("Nature Methods public-access verification must not contain failed URLs")
        if public_access.get("forbidden_public_reference_hits") not in ([], None):
            failures.append("Nature Methods package still advertises unresolved optional RhoA reference-case links")
        if public_access.get("missing_expected_urls") not in ([], None):
            failures.append("Nature Methods public-access verification is missing expected release, dataset, or renderer URLs")
        if int(public_access.get("url_count", 0)) < 10:
            failures.append("Nature Methods public-access verification did not check enough package URLs")
    else:
        failures.append("missing Nature Methods public-access verification report")
    if public_access_md.exists():
        public_access_text = public_access_md.read_text(encoding="utf-8")
        for phrase in [
            "Status. `pass`.",
            "all_visible_public_urls_resolve. pass.",
            "unresolved_optional_reference_case_links_not_advertised. pass.",
            "expected_release_dataset_and_renderer_urls_present. pass.",
        ]:
            if phrase not in public_access_text:
                failures.append(f"Nature Methods public-access Markdown report missing phrase: {phrase}")
    else:
        failures.append("missing Nature Methods public-access Markdown report")

    submit_hold_path = root / "manuscript" / "nature_methods" / "audits" / "nature_methods_submit_or_hold_decision.json"
    submit_hold_md = root / "manuscript" / "nature_methods" / "audits" / "nature_methods_submit_or_hold_decision.md"
    if submit_hold_path.exists():
        try:
            submit_hold = json.loads(submit_hold_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            failures.append(f"Nature Methods submit-or-hold report is not valid JSON: {exc}")
            submit_hold = {}
        if submit_hold.get("status") != "hold_for_human_upload_actions":
            failures.append("Nature Methods submit-or-hold report must retain hold_for_human_upload_actions status")
        if submit_hold.get("collaborator_review_ready") is not True:
            failures.append("Nature Methods submit-or-hold report must mark collaborator review ready")
        if submit_hold.get("journal_upload_ready") is not False:
            failures.append("Nature Methods submit-or-hold report must not mark final journal upload ready")
        for group_name in ["science_package_checks", "upload_hold_checks"]:
            checks = submit_hold.get(group_name, [])
            if not checks or any(item.get("passed") is not True for item in checks if isinstance(item, dict)):
                failures.append(f"Nature Methods submit-or-hold report has failing or missing {group_name}")
        actions = submit_hold.get("human_submission_actions", [])
        if not isinstance(actions, list) or len(actions) < 5:
            failures.append("Nature Methods submit-or-hold report must retain at least five human submission actions")
        else:
            joined_actions = "\n".join(str(action) for action in actions)
            for phrase in ["Reporting Summary", "AI-assisted content disclosure", "author", "title page", "reviewer suggestions", "portal metadata"]:
                if phrase not in joined_actions:
                    failures.append(f"Nature Methods submit-or-hold human actions missing phrase: {phrase}")
    else:
        failures.append("missing Nature Methods submit-or-hold JSON report")
    if submit_hold_md.exists():
        submit_hold_text = submit_hold_md.read_text(encoding="utf-8")
        for phrase in [
            "Decision. `hold_for_human_upload_actions`.",
            "## Science package checks",
            "## Upload hold checks",
            "## Required human submission actions",
        ]:
            if phrase not in submit_hold_text:
                failures.append(f"Nature Methods submit-or-hold Markdown report missing phrase: {phrase}")
    else:
        failures.append("missing Nature Methods submit-or-hold Markdown report")

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

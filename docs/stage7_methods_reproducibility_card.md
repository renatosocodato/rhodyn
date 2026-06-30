# Stage 7.6 methods-program reproducibility card

Generated UTC. 2026-06-30T16:15:48.300103Z

Overall status. pass

## Scope

Stage 7.6 hardens the methods-paper evidence set. It checks whether the Stage 7.1 to Stage 7.5 outputs can be regenerated from a declared release-candidate archive, whether selected tutorial notebooks execute, and whether Python, CLI, backend, and frontend-contract surfaces remain aligned for shared workflows.

## Validation checkpoints

- fresh_environment_reproduces_benchmark_tables. pass.
- tutorial_outputs_execute. pass.
- public_release_scan_finds_no_private_paths_or_secrets. pass.
- frontend_backend_cli_python_outputs_agree. pass.
- ci_covers_selected_examples_docs_notebooks_benchmarks_package_docker_frontend. pass.
- clean_room_reproduction_from_release_archive. pass.
- stop_condition_clean_room_failure. not_triggered.
- release_archive_manifest_is_complete. pass.

## Regenerated output comparison

| Output | Match |
|---|---:|
| `case_studies/stage7_synthetic_truth/stage7_1_synthetic_truth_report.json` | 1 |
| `case_studies/stage7_benchmarks/synthetic_residence_baseline_comparison.csv` | 1 |
| `case_studies/stage7_benchmarks/synthetic_reserve_baseline_comparison.csv` | 1 |
| `case_studies/stage7_benchmarks/synthetic_coupling_baseline_comparison.csv` | 1 |
| `case_studies/stage7_benchmarks/synthetic_model_baseline_comparison.csv` | 1 |
| `case_studies/stage7_benchmarks/window_sensitivity_summary.csv` | 1 |
| `case_studies/stage7_benchmarks/margin_sensitivity_summary.csv` | 1 |
| `case_studies/stage7_benchmarks/grouping_sample_size_sensitivity.csv` | 1 |
| `case_studies/stage7_benchmarks/public_fixture_benchmark_summary.csv` | 1 |
| `case_studies/stage7_benchmarks/failure_behavior_summary.csv` | 1 |
| `case_studies/stage7_benchmarks/stage7_2_benchmark_report.json` | 1 |
| `case_studies/stage7_public_signaling/public_signaling_case_summary.tsv` | 1 |
| `case_studies/stage7_public_signaling/drg_calcium_residence_amplitude_summary.csv` | 1 |
| `case_studies/stage7_public_signaling/drg_calcium_window_sensitivity.csv` | 1 |
| `case_studies/stage7_public_signaling/drg_calcium_uncertainty_summary.csv` | 1 |
| `case_studies/stage7_public_signaling/erk_gpcr_residence_amplitude_summary.csv` | 1 |
| `case_studies/stage7_public_signaling/erk_gpcr_window_sensitivity.csv` | 1 |
| `case_studies/stage7_public_signaling/erk_gpcr_uncertainty_summary.csv` | 1 |
| `case_studies/stage7_public_signaling/stage7_3_public_signaling_gate_report.json` | 1 |
| `case_studies/stage7_endpoint_reserve_routing/stage7_4_case_summary.tsv` | 1 |
| `case_studies/stage7_endpoint_reserve_routing/cell_painting_routed_model_comparison.csv` | 1 |
| `case_studies/stage7_endpoint_reserve_routing/cell_painting_reduced_alternative_decisions.tsv` | 1 |
| `case_studies/stage7_endpoint_reserve_routing/cell_painting_reserve_like_model_summary.csv` | 1 |
| `case_studies/stage7_endpoint_reserve_routing/cell_painting_reserve_like_uncertainty.csv` | 1 |
| `case_studies/stage7_endpoint_reserve_routing/erk_akt_bounded_coupling_decisions.csv` | 1 |
| `case_studies/stage7_endpoint_reserve_routing/stage7_4_endpoint_reserve_routing_gate_report.json` | 1 |
| `case_studies/stage7_heldout_validation/heldout_analysis_plan.json` | 1 |
| `case_studies/stage7_heldout_validation/heldout_bounded_coupling_decisions.csv` | 1 |
| `case_studies/stage7_heldout_validation/heldout_validation_outcomes.tsv` | 1 |
| `case_studies/stage7_heldout_validation/stage7_5_heldout_validation_gate_report.json` | 1 |

## Cross-surface parity

| Operation | Pass | Frontend status |
|---|---:|---|
| score_residence | 1 | fixture_contract_checked |
| decide_coupling | 1 | fixture_contract_checked |
| summarize_reserve | 1 | fixture_contract_checked |
| compare_models | 1 | fixture_contract_checked |

## Release archive manifest

Manifest status. pass

Files inspected. 393

Text files inspected. 323

Raw/private-like files. 0

## Interpretation boundary

A passing Stage 7.6 result supports reproducibility of the software and methods-evidence surface. It does not add a new biological system, does not change any Stage 7 biological interpretation, and does not imply that every future user dataset will support residence, reserve, bounded-coupling, or routed-output claims.

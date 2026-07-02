# Stage 7 output contract for Stage 9

Evidence version. `stage7.8-methods-readiness@242f06c49e8310b81ac1c06a270bb6810f3f4cfc`

Each row defines a Stage 7 output that may be used by Stage 9 only within the
listed scope. The contract supports manuscript assembly, not new scientific
inference.

| component | path | schema | required_for_stage9 | scope_status |
| --- | --- | --- | --- | --- |
| Method concept and workflow | docs/stage7_method_specification.md | md | true | Formal method definitions and executable truth cases, not biological discovery. |
| Synthetic benchmarking against simpler summaries | docs/stage7_baseline_comparison_report.md | md | true | Benchmark value over baselines is regime-dependent and includes negative and ambiguous cases. |
| Independent public live-cell signaling demonstrations | docs/stage7_public_signaling_demonstrations.md | md | true | Public trajectory demonstrations show residence-amplitude separation in two systems and do not imply manuscript generation. |
| Perturbation endpoint, reserve-like, and routed-output demonstrations | docs/stage7_endpoint_reserve_routing_demonstrations.md | md | true | Bounded coupling, reserve-like endpoint behavior, and routed-output comparison remain scoped to measured public-derived tables. |
| Held-out public validation | docs/stage7_heldout_validation_report.md | md | true | Held-out validation contains four pass contexts and three margin-boundary inconclusive contexts. |
| Software workbench and reproducibility architecture | docs/stage7_methods_reproducibility_card.md | md | true | Reproducibility and usability evidence support inspectable software behavior, not a new biological result. |
| C1 | case_studies/stage7_benchmarks/synthetic_residence_baseline_comparison.csv; case_studies/stage7_public_signaling/drg_calcium_residence_amplitude_summary.csv; case_studies/stage7_public_signaling/erk_gpcr_residence_amplitude_summary.csv | csv | true | supported_for_methods_drafting |
| C2 | case_studies/stage7_endpoint_reserve_routing/erk_akt_bounded_coupling_decisions.csv; case_studies/stage7_heldout_validation/heldout_bounded_coupling_decisions.csv | csv | true | supported_with_inconclusive_contexts_visible |
| C3 | case_studies/stage7_endpoint_reserve_routing/cell_painting_reserve_like_endpoint_rows.csv; case_studies/stage7_endpoint_reserve_routing/cell_painting_reserve_like_uncertainty.csv | csv | true | supported_with_reserve_like_language |
| C4 | case_studies/stage7_endpoint_reserve_routing/cell_painting_routed_model_comparison.csv; case_studies/stage7_endpoint_reserve_routing/cell_painting_reduced_alternative_decisions.tsv | tsv | true | supported_without_molecular_edge_claim |
| C5 | docs/stage7_6_gate_report.json; docs/stage7_7_gate_report.json; case_studies/stage7_usability_rehearsal/export_examples_manifest.tsv | tsv | true | supported_for_software_reproducibility_claim |

# Stage 7.8 methods evidence index

This index assembles the current methods-program evidence for drafting. It does not add analyses or biological claims.

## Gate status

Overall status. pass

## Figure-level evidence

| component | stage | primary_artifact | validation_artifact | readiness | scope |
| --- | --- | --- | --- | --- | --- |
| Method concept and workflow | 7.1 | docs/stage7_method_specification.md | docs/stage7_1_gate_report.json | ready_for_drafting | Formal method definitions and executable truth cases, not biological discovery. |
| Synthetic benchmarking against simpler summaries | 7.2 | docs/stage7_baseline_comparison_report.md | docs/stage7_2_gate_report.json | ready_for_drafting | Benchmark value over baselines is regime-dependent and includes negative and ambiguous cases. |
| Independent public live-cell signaling demonstrations | 7.3 | docs/stage7_public_signaling_demonstrations.md | docs/stage7_3_gate_report.json | ready_for_drafting | Public trajectory demonstrations show residence-amplitude separation in two systems and do not imply manuscript generation. |
| Perturbation endpoint, reserve-like, and routed-output demonstrations | 7.4 | docs/stage7_endpoint_reserve_routing_demonstrations.md | docs/stage7_4_gate_report.json | ready_for_drafting | Bounded coupling, reserve-like endpoint behavior, and routed-output comparison remain scoped to measured public-derived tables. |
| Held-out public validation | 7.5 | docs/stage7_heldout_validation_report.md | docs/stage7_5_gate_report.json | ready_for_supplement_or_main_with_scope | Held-out validation contains four pass contexts and three margin-boundary inconclusive contexts. |
| Software workbench and reproducibility architecture | 7.6-7.7 | docs/stage7_methods_reproducibility_card.md | case_studies/stage7_methods_reproducibility/stage7_6_methods_reproducibility_gate_report.json | ready_for_drafting | Reproducibility and usability evidence support inspectable software behavior, not a new biological result. |

## Claim-level evidence

| claim_id | claim | validation | status |
| --- | --- | --- | --- |
| C1 | Residence-window summaries can expose time-in-state behavior that amplitude summaries miss. | docs/stage7_2_gate_report.json; docs/stage7_3_gate_report.json | supported_for_methods_drafting |
| C2 | Bounded-coupling decisions require predeclared margins, uncertainty intervals, and ROPE or interval support when supplied. | docs/stage7_4_gate_report.json; docs/stage7_5_gate_report.json | supported_with_inconclusive_contexts_visible |
| C3 | Reserve-like summaries can be integrated when the readout is scoped to the measured endpoint. | docs/stage7_4_gate_report.json | supported_with_reserve_like_language |
| C4 | Reduced-architecture comparison can expose when simpler endpoint mappings do not satisfy routed-output constraints. | docs/stage7_4_gate_report.json | supported_without_molecular_edge_claim |
| C5 | The current RhoDyn release can reproduce retained Stage 7 evidence from a source distribution and expose user-facing export provenance. | docs/stage7_6_recursive_hardening_report.json; docs/stage7_7_gate_report.json | supported_for_software_reproducibility_claim |

## Interpretation boundary

Stage 7.8 assembles a methods-manuscript readiness package from existing Stage 7 evidence. It does not add a biological system, new analysis route, new benchmark result, or manuscript claim.

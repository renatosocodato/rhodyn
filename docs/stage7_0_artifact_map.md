# Stage 7.0 artifact map

This artifact map names the expected Stage 7 outputs before they are created. It distinguishes Stage 7.0 planning outputs from future analysis, software, benchmark, and manuscript-support outputs.

## Artifact-status definitions

| status | meaning |
| --- | --- |
| Created planning artifact | A Stage 7.0 planning document created now. |
| Planned future artifact | A named future output that must not yet exist as analysis or implementation. |
| Existing prerequisite artifact | A pre-existing release, Stage 3, Stage 4, Stage 5, or Stage 6 artifact used to justify Stage 7.0 entry. |
| Out of scope | A tempting output that must not be produced during Stage 7.0. |

## Created Stage 7.0 planning artifacts

| artifact | path | status | purpose |
| --- | --- | --- | --- |
| Source register | `docs/stage7_0_source_register.md` | Created planning artifact | Freezes guidance, representative papers, current state, and candidate dataset classes. |
| Baseline-method inventory | `docs/stage7_0_baseline_method_inventory.md` | Created planning artifact | Defines baseline comparator classes for future benchmarks. |
| Dataset selection rubric | `docs/stage7_0_dataset_selection_rubric.md` | Created planning artifact | Defines inclusion, rejection, scoring, and fallback rules for Stage 7 datasets. |
| Artifact map | `docs/stage7_0_artifact_map.md` | Created planning artifact | Names expected future outputs without creating them. |
| Stage 7.0 gate report | `docs/stage7_0_gate_report.json` | Created planning artifact | Records prerequisite and completion status for Stage 7.0. |

## Existing prerequisite artifacts

| artifact | path | status | Stage 7.0 role |
| --- | --- | --- | --- |
| Stage 3 gate report | `case_studies/stage3_case_study_bank_gate_report.json` | Existing prerequisite artifact | Confirms current evidence bank passes and additional systems belong to Stage 7. |
| Stage 4 OpenAPI schema | `api/stage4/openapi.json` | Existing prerequisite artifact | Confirms service contract exists. |
| Stage 4 frontend contract | `api/stage4/frontend_contract.json` | Existing prerequisite artifact | Confirms frontend/backend contract exists. |
| Stage 5 closeout | `docs/stage5_closeout.md` | Existing prerequisite artifact | Confirms workbench closeout exists. |
| Public release integrity report | `docs/public_release_integrity_report.json` | Existing prerequisite artifact | Confirms public release checks have a recorded pass state. |
| Zenodo publication report | `docs/zenodo_publication_report.json` | Existing prerequisite artifact | Confirms the v0.1.0 software DOI record. |

## Planned future Stage 7 artifacts

| subphase | planned artifact class | planned path pattern | current status |
| --- | --- | --- | --- |
| 7.1 | Formal method specification | `docs/stage7_method_specification.md` | Planned future artifact. |
| 7.1 | Synthetic truth cases | `case_studies/stage7_synthetic_truth/` | Planned future artifact. |
| 7.1 | Limitations matrix | `docs/stage7_limitations_matrix.md` | Planned future artifact. |
| 7.2 | Benchmark harness outputs | `case_studies/stage7_benchmarks/` | Created benchmark artifact. |
| 7.2 | Baseline comparison report | `docs/stage7_baseline_comparison_report.md` | Created benchmark artifact. |
| 7.2 | Benchmark harness guide | `docs/stage7_benchmark_harness_guide.md` | Created benchmark artifact. |
| 7.2 | Performance and uncertainty report | `docs/stage7_performance_uncertainty_report.md` | Created benchmark artifact. |
| 7.2 | Gate report | `docs/stage7_2_gate_report.json` | Created benchmark artifact. |
| 7.3 | Public live-cell signaling demonstrations | `case_studies/stage7_public_signaling/` | Planned future artifact. |
| 7.3 | Public-data adapter documentation | `docs/stage7_public_data_adapters.md` | Planned future artifact. |
| 7.4 | Perturbation, reserve, and routed-output demonstrations | `case_studies/stage7_endpoint_reserve_routing/` | Planned future artifact. |
| 7.5 | Held-out or collaborator validation report | `docs/stage7_external_validation_report.md` | Planned future artifact. |
| 7.6 | Methods-paper reproducibility card | `docs/stage7_reproducibility_card.md` | Planned future artifact. |
| 7.6 | Clean-room reproduction report | `docs/stage7_clean_room_report.md` | Planned future artifact. |
| 7.7 | Usability rehearsal report | `docs/stage7_usability_rehearsal.md` | Planned future artifact. |
| 7.8 | Figure-to-artifact crosswalk | `docs/stage7_figure_artifact_crosswalk.md` | Planned future artifact. |
| 7.8 | Claim-to-evidence crosswalk | `docs/stage7_claim_evidence_crosswalk.md` | Planned future artifact. |
| 7.8 | Submission-readiness checklist | `docs/stage7_methods_submission_readiness.md` | Planned future artifact. |

## Out of scope for Stage 7.0

- New biological analyses.
- New public-data adapters.
- New benchmark code.
- New software API surfaces.
- New manuscript text.
- New figures.
- New hosted product features.
- New claims that RhoDyn generated the RhoA/microglia manuscript.

## Completion decision

This map distinguishes created planning outputs from future analysis and implementation outputs. It is sufficient to close the Stage 7.0 artifact-map requirement.

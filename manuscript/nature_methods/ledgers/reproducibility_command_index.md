<!-- REPRODUCIBILITY-COMMAND-INDEX stage=9.17 generated_utc=2026-07-03T16:36:31.772873Z -->

# Reproducibility command index

Commands are run from the root of the RhoDyn repository at release tag `v0.1.0` and commit `4b1211cadd1fb3af34a1ec3e21f62383ffd9e368` unless a command states a different tool boundary. RhoDyn commands use RhoDyn v0.1.0. PanelForge commands use panelforge-figures v3.14.1 with version DOI https://doi.org/10.5281/zenodo.20811171.

| Command ID | Analysis output | Command | Expected output | Software version | Purpose |
|---|---|---|---|---|---|
| CMD-001 | ART-REPRO-001 | `python scripts/build_stage7_1_synthetic_truth_cases.py` | regenerate retained methods-paper evidence output | v0.1.0 | 7.1 synthetic truth cases evidence regeneration |
| CMD-002 | ART-REPRO-002 | `python scripts/run_stage7_2_benchmark_harness.py` | regenerate retained methods-paper evidence output | v0.1.0 | 7.2 benchmark harness evidence regeneration |
| CMD-003 | ART-REPRO-003 | `python scripts/run_stage7_3_public_signaling.py` | regenerate retained methods-paper evidence output | v0.1.0 | 7.3 public signaling demonstrations evidence regeneration |
| CMD-004 | ART-REPRO-004 | `python scripts/run_stage7_4_endpoint_reserve_routing.py` | regenerate retained methods-paper evidence output | v0.1.0 | 7.4 endpoint reserve routing evidence regeneration |
| CMD-005 | ART-REPRO-005 | `python scripts/run_stage7_5_heldout_validation.py` | regenerate retained methods-paper evidence output | v0.1.0 | 7.5 held-out validation evidence regeneration |
| CMD-006 | ART-REPRO-006 | `mkdocs build --strict` | render methods-program documentation | v0.1.0 | docs evidence regeneration |
| CMD-007 | ART-REPRO-007 | `python scripts/audit_stage4_service_contract.py && python scripts/audit_stage5_premium_workbench.py` | check backend/frontend surfaces against retained examples and frozen fixtures | v0.1.0 | surface parity evidence regeneration |
| CMD-008 | ART-REPRO-008 | `python scripts/run_stage7_7_usability_rehearsal.py` | case_studies/stage7_usability_rehearsal/stage7_7_usability_gate_report.json | v0.1.0 | Workbench usability and report-export parity |
| CMD-009 | ART-REPRO-009 | `python scripts/run_stage7_8_methods_readiness.py` | case_studies/stage7_methods_readiness/stage7_8_methods_readiness_gate_report.json | v0.1.0 | Methods-evidence readiness package |
| CMD-010 | ART-REPRO-010 | `python scripts/check_release.py` | release validation report printed to stdout | v0.1.0 | Release-surface integrity check |
| CMD-011 | ART-REPRO-011 | `figures render manuscript/nature_methods/figures/figures.manifest.yaml` | manuscript/nature_methods/figures/rendered/FIG-001 through FIG-006 in PDF, PNG, and SVG | panelforge-figures v3.14.1; DOI 10.5281/zenodo.20811171 | Render the figure panels used by the methods-manuscript display spine |
| CMD-012 | ART-REPRO-012 | `figures validate figures.manifest.yaml` | figure manifest validation output | panelforge-figures v3.14.1; DOI 10.5281/zenodo.20811171 | Validate the figure manifest before rendering |

The command index is a manuscript-facing map of the reproducibility routes. It does not replace the source release, the Zenodo archive, or the public source records listed in the availability statements.

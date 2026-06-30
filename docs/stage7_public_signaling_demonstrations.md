# Stage 7.3 public live-cell signaling demonstrations

Stage 7.3 tests whether residence-state inference adds value in public live-cell signaling data outside the RhoA/microglia manuscript logic. The two selected systems are excitable-neuron calcium dynamics and GPCR-driven ERK kinase dynamics.

## Outputs

- `case_studies/stage7_public_signaling/drg_calcium_tidy_trajectories.csv`
- `case_studies/stage7_public_signaling/drg_calcium_residence_amplitude_summary.csv`
- `case_studies/stage7_public_signaling/drg_calcium_window_sensitivity.csv`
- `case_studies/stage7_public_signaling/drg_calcium_uncertainty_summary.csv`
- `case_studies/stage7_public_signaling/drg_calcium_case_report.md`
- `case_studies/stage7_public_signaling/erk_gpcr_tidy_trajectories.csv`
- `case_studies/stage7_public_signaling/erk_gpcr_residence_amplitude_summary.csv`
- `case_studies/stage7_public_signaling/erk_gpcr_window_sensitivity.csv`
- `case_studies/stage7_public_signaling/erk_gpcr_uncertainty_summary.csv`
- `case_studies/stage7_public_signaling/erk_gpcr_case_report.md`
- `case_studies/stage7_public_signaling/public_signaling_case_summary.tsv`
- `case_studies/stage7_public_signaling/stage7_3_public_signaling_gate_report.json`

## Biological result

The DRG calcium demonstration retains 72,000 tidy trajectory rows and 360 episode-level residence/amplitude summaries. It contains 16 amplitude-only and 16 residence-only top-quartile rows, showing that peak calcium and time spent in the declared high-calcium window are not interchangeable.

The ERK GPCR demonstration retains 4,320 tidy trajectory rows and 180 single-cell residence/amplitude summaries. It contains 11 amplitude-only and 11 residence-only top-quartile rows, showing that peak ERK KTR activity and high-ERK residence are also separable in a kinase-reporter system.

## What RhoDyn adds

RhoDyn contributes an explicit residence-state readout beside amplitude summaries. In both public systems, the analysis identifies cells or episodes whose high-state dwell behavior is not captured by peak signal alone. This supports the Stage 7.3 gate that at least two independent biological systems show a residence/amplitude distinction.

## What this does not show

The Stage 7.3 outputs do not infer DRG pain mechanism, GPCR ligand mechanism, or universal activation thresholds. They do not show that RhoDyn generated the RhoA/microglia manuscript results. They establish public live-cell signaling demonstrations for the methods program and set up Stage 7.4, where perturbation endpoint, reserve, and routed-output demonstrations can be selected separately.

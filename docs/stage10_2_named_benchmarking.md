# Stage 10.2 named-baseline benchmarking

Stage 10.2 addresses the first desk-rejection vulnerability in the Stage 10 roadmap. It asks whether RhoDyn's method object remains interpretable when compared on the same inputs against simple summaries, named external-tool families, state-segmentation comparators, and generic feature classifiers.

This phase is not a new biological demonstration. Synthetic rows test known method behavior, and public rows summarize retained DRG calcium and ERK GPCR trajectory inputs. Stage 10.3 remains responsible for adding more independent biological systems.

## Command

```bash
python3 scripts/run_stage10_2_named_benchmarking.py
```

The runner writes outputs to `case_studies/stage10_named_benchmarks/`.

## Comparator set

| family | implementation in this run | role |
| --- | --- | --- |
| RhoDyn method object | `trajectory_method_decision` | Declared residence-versus-comparator decision with abstention. |
| Internal simple summaries | endpoint, peak, mean/AUC, threshold occupancy, latency | Minimum amplitude and endpoint comparators. |
| SciPy signal peak detection | direct `scipy` package when available | Event and peak-like baseline. |
| scikit-learn feature classifier | direct `sklearn.RandomForestClassifier` leave-one-out when available | Tests whether generic features recover synthetic labels without a residence object. |
| hmmlearn Gaussian HMM family | direct `hmmlearn` availability, HMM-style state summary | Tests whether state segmentation substitutes for a declared residence window. |
| catch22 feature family | compatibility feature screen when pycatch22/catch22 is unavailable | Tests named generic time-series feature logic without adding a hard dependency. |
| tsfresh feature family | compatibility selected-feature screen when tsfresh is unavailable | Tests broad aggregate feature summaries. |
| MiniROCKET/ROCKET family | compatibility interval-kernel screen when sktime is unavailable | Tests interval-kernel-style classification logic. |
| ruptures changepoint family | compatibility changepoint screen when ruptures is unavailable | Tests whether a state-transition summary replaces residence. |

Direct package availability is recorded in `stage10_2_named_tool_availability.tsv`. Compatibility implementations are not presented as direct package runs. They are documented named-family comparators used when the corresponding package is absent.

## Outputs

| output | purpose |
| --- | --- |
| `stage10_2_synthetic_named_baseline_benchmark.csv` | One row per synthetic case and comparator. |
| `stage10_2_named_baseline_accuracy_summary.csv` | Accuracy by comparator family on positive, amplitude-sufficient, and ambiguous synthetic regimes. |
| `stage10_2_public_input_named_baseline_summary.csv` | Shared-input public DRG calcium and ERK GPCR top-quartile overlaps and discordance. |
| `stage10_2_named_tool_availability.tsv` | Direct package availability and execution policy. |
| `stage10_2_runtime_memory.tsv` | Runtime and memory on representative synthetic table sizes. |
| `stage10_2_failure_boundary_report.md` | Biological and methodological boundaries when baselines match or outperform. |
| `stage10_2_named_benchmark_report.json` | Gate report. |

## Current result

The current gate report passes. It includes seven named external-style families plus internal simple summaries. Three direct optional package families were available in the local runtime, comprising SciPy signal, scikit-learn, and hmmlearn.

The RhoDyn method object matches all synthetic known-truth calls in this fixture. Peak-amplitude summaries preserve the amplitude-sufficient regime but miss the residence-added regime. The scikit-learn feature classifier and the catch22-style compatibility family also match the synthetic labels. That result is reported deliberately. It shows that generic feature methods can perform well when labels are available and the regime is separable, while RhoDyn provides a declared, interpretable decision object with explicit abstention and biological boundaries.

Public DRG calcium and ERK GPCR rows are used as shared-input summaries rather than truth-labeled superiority tests. The public tables show that high-scoring trace sets differ across residence, peak, mean/AUC, peak-event, feature-family, interval-kernel, changepoint, and HMM-style summaries. This supports the need to report comparator behavior directly, but it does not prove that any method is biologically superior in those public systems.

## Gate interpretation

Stage 10.2 strengthens the method claim by making comparator behavior visible. It does not yet solve the biological-breadth vulnerability. The next required step remains Stage 10.3, which must add additional independent public biological demonstrations beyond the retained DRG calcium and ERK GPCR trajectory inputs.


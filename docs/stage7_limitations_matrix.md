# Stage 7.1 limitations matrix

This matrix records the formal boundaries of the Stage 7.1 method object. It is intended to prevent a future methods manuscript from converting useful dynamic summaries into unsupported biological mechanisms.

| component | supported use | not supported | mitigation |
| --- | --- | --- | --- |
| Tidy trajectory schema | Represents cell-level time, condition, signal, and optional replicate grouping. | Cannot repair missing time units, missing condition labels, or merged trace identities. | Reject or repair input before dynamic-state analysis. |
| Residence window | Quantifies dwell time inside a declared biological interval. | Does not discover the correct biological window by itself. | Use predeclared windows, sensitivity curves, and independent justification. |
| Dwell fraction and dwell time | Separate time-in-state behavior from amplitude. | Do not prove the dwell state causes the downstream endpoint. | Pair with perturbation or external validation before mechanistic claims. |
| Segment count | Captures fragmentation of residence. | Does not define molecular pulse identity without sampling-rate and reporter validation. | Report alongside time resolution and trajectory sampling limits. |
| Amplitude comparators | Provide endpoint, peak, mean, and broad exposure baselines. | Cannot substitute for residence when dwell time is the tested variable. | Benchmark against residence summaries directly. |
| Reserve-like coordinate | Scales a response into a bounded buffering-style coordinate. | Is not biological reserve unless the readout measures reserve capacity. | Use reserve-like language unless experimental support is direct. |
| Bounded coupling | Supports equivalence inside a declared margin with interval and ROPE evidence. | Does not prove absence of all crosstalk or slower coupling. | Predeclare margins and report timescale/context limits. |
| TOST/ROPE | Provides formal bounded-effect support. | Cannot rescue underpowered or post hoc margins. | Pair with sensitivity curves and sample-size interpretation. |
| Routed-output comparison | Compares reduced architectures against endpoint constraints. | Does not identify literal molecular edges from effective parameters. | Report model alternatives, near ties, and biological assumptions. |
| Uncertainty intervals | Quantify sampling uncertainty under declared resampling level. | Cell-level intervals can overstate evidence if biological grouping is ignored. | Use group-level resampling where grouping is meaningful. |
| Window sensitivity | Tests robustness across declared windows. | A favorable window grid is not an independent discovery. | Record grid ranges and interpret window-dependent results as ambiguous. |
| Stochastic timing | Summarizes model-derived or trajectory-derived threshold timing. | Simulated timing is not measured cell death, hazard, or injury. | Label model-derived timing explicitly. |
| Public demonstrations | Test generality across biological systems. | Do not show that RhoDyn generated the original RhoA/microglia manuscript. | Keep the manuscript as a reference use case only. |

## Completion decision

The limitations matrix defines the failure modes, non-example cases, and interpretation boundaries required by Stage 7.1. It supports method formalization but does not add new biological claims.

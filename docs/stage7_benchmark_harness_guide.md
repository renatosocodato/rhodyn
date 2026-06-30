# Stage 7.2 benchmark harness guide

Stage 7.2 compares RhoDyn's declared dynamic-state decisions against simpler summaries and relevant alternatives. The harness is a method-validation layer, not a new biological demonstration. It tests whether residence windows, bounded coupling, reserve-like summaries, and reduced-architecture comparisons behave correctly when the truth state is known, while also making baseline behavior explicit for comparison.

## Command

```bash
python scripts/run_stage7_2_benchmark_harness.py
```

The default output directory is `case_studies/stage7_benchmarks/`. The runner regenerates the Stage 7.1 synthetic truth fixtures before benchmarking so the benchmark inputs stay synchronized with the formal method definitions.

## Benchmark components

- Residence and amplitude benchmarks compare RhoDyn residence-window sensitivity against peak-amplitude and mean-inside-window summaries.
- Bounded-coupling benchmarks compare interval plus ROPE decisions against point-estimate and interval-only alternatives.
- Reduced-architecture benchmarks compare routed-output ranking against endpoint-only and one-dimensional alternatives.
- Reserve-like benchmarks compare reserve-coordinate decisions against peak and late-response summaries.
- Window, margin, grouping, and sample-size sensitivity tables expose where the decision is robust, fragile, or inconclusive.
- Public fixture summaries re-use the current DRG calcium, ERK GPCR, Cell Painting/MitoTox, and ERK/Akt bounded-coupling examples without converting them into new Stage 7 biological evidence.

## Interpretation boundary

A passing benchmark means the software behavior matches declared truth or retained fixture expectations under the tested assumptions. It does not prove a biological mechanism, add independent biological systems, or imply that RhoDyn generated the RhoA/microglia manuscript results.

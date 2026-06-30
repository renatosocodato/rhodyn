# Stage 7.2 performance and uncertainty report

Stage 7.2 records robustness and size behavior for method decisions rather than only reporting a best-case outcome.

## Sensitivity outputs

- `case_studies/stage7_benchmarks/window_sensitivity_summary.csv` reports residence decisions across low/high window choices.
- `case_studies/stage7_benchmarks/margin_sensitivity_summary.csv` reports bounded-coupling decisions across declared margins.
- `case_studies/stage7_benchmarks/grouping_sample_size_sensitivity.csv` reports how grouping-aware bootstrap intervals and sample size alter uncertainty width.

These tables are intended to show when RhoDyn decisions are stable, when they are margin-dependent, and when the safe result is inconclusive.

## Performance output

`case_studies/stage7_benchmarks/performance_summary.csv` records runtime and approximate peak memory for representative trajectory counts. These values are environment-dependent and should be interpreted as release-local scaling checks rather than absolute hardware benchmarks.

## Failure behavior

`case_studies/stage7_benchmarks/failure_behavior_summary.csv` records expected rejection of invalid input, including the missing-time-column fixture in `case_studies/stage7_benchmarks/invalid_trajectory_missing_time.csv`. The purpose is to confirm that invalid inputs fail visibly instead of producing unreviewable biological decisions.

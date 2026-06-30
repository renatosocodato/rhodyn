# Stage 7.2 baseline comparison report

The Stage 7.2 benchmark harness tests whether RhoDyn adds decision value beyond simpler summaries while also preserving inconclusive outcomes when the input regime is ambiguous.

## Synthetic truth results

The persisted benchmark report is `case_studies/stage7_benchmarks/stage7_2_benchmark_report.json`. The current report passes all declared gates and records `stop_condition_no_added_value_beyond_baselines` as `not_triggered`.

| method family | RhoDyn summary | simpler baseline summary | biological interpretation |
| --- | --- | --- | --- |
| Residence | `3/3` known-truth decisions correct | peak-amplitude baseline `1/3` correct | Residence scoring detects the amplitude-only counterexample and preserves the ambiguous window-edge case as inconclusive. |
| Bounded coupling | `3/3` known-truth decisions correct | point-estimate baseline `2/3` correct | Interval plus ROPE logic avoids upgrading an ambiguous margin-crossing case. |
| Reduced architecture | `3/3` known-truth decisions correct | endpoint-only baseline `1/3` correct | Routed-output ranking avoids collapsing architecture when endpoint summaries are insufficient. |
| Reserve-like summaries | `3/3` known-truth decisions correct | peak-response baseline `2/3` correct | Reserve-like scoring preserves the mid-reserve case as inconclusive rather than forcing a fragile/buffered label. |

## Public fixture summaries

The public fixture table is `case_studies/stage7_benchmarks/public_fixture_benchmark_summary.csv`. It reports retained summaries for DRG calcium, ERK GPCR, Cell Painting/MitoTox, and ERK/Akt bounded coupling. These fixture rows are included to verify that the benchmark harness can read and summarize the current public examples. They are not counted as new independent biological demonstrations for Stage 7.3.

## Stop condition

The Stage 7.2 stop condition would trigger if benchmarks showed no added value beyond amplitude or endpoint summaries. The current benchmark report does not trigger that stop condition because the synthetic truth suite includes residence/amplitude disagreement, correctly bounded negative or ambiguous cases, and routed-output cases where endpoint-only summaries are insufficient.

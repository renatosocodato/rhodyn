# Stage 7.1 synthetic truth cases

The Stage 7.1 truth suite provides executable positive, counterexample, and ambiguous cases for the formal method specification. These are synthetic method-validation fixtures. They are not biological evidence and should not be used as demonstrations of disease biology.

## Generated outputs

The generator is `scripts/build_stage7_1_synthetic_truth_cases.py`. Its default output directory is `case_studies/stage7_synthetic_truth/`.

Generated files include trajectory, reserve, coupling, endpoint, uncertainty, and report outputs.

| component | positive case | counterexample | ambiguous case |
| --- | --- | --- | --- |
| Residence | `trajectory_positive_residence.csv` has high dwell in the declared window. | `trajectory_counterexample_amplitude_only.csv` has high peaks but low residence. | `trajectory_ambiguous_window_edge.csv` depends on the window grid. |
| Reserve-like summary | `reserve_positive_buffered.csv` retains a high reserve coordinate. | `reserve_counterexample_fragile.csv` has a low reserve coordinate. | `reserve_ambiguous_midreserve.csv` lies in the middle of the declared scaling. |
| Bounded coupling | `positive_equivalent` interval is inside the margin with high ROPE mass. | `counterexample_shift` is outside the margin. | `ambiguous_margin_crossing` crosses the margin or misses ROPE support. |
| Model comparison | `endpoint_positive_routed_best.csv` ranks the routed model first. | `endpoint_counterexample_endpoint_sufficient.csv` ranks endpoint-only first. | `endpoint_ambiguous_close_fit.csv` keeps fits close. |
| Uncertainty | `positive_stable` gives a narrow bootstrap interval. | `counterexample_shifted` gives a shifted distribution. | `ambiguous_broad` gives a wider interval. |
| Timing | Above-threshold first passage occurs in the positive case. | No crossing occurs in the counterexample. | A late crossing marks an ambiguous timing boundary. |

## Expected decisions

The persisted report `case_studies/stage7_synthetic_truth/stage7_1_synthetic_truth_report.json` records the current expected decisions. The report passes only if all expectation checks hold.

The key expectations are:

- residence positive case has residence fraction above 0.50;
- amplitude-only counterexample has a high peak but residence fraction below 0.30;
- ambiguous residence case depends on window choice;
- buffered reserve case remains high and fragile reserve case remains low;
- bounded coupling passes only for the positive equivalence case;
- routed model is best only in the positive routed case;
- ambiguous uncertainty is broader than stable uncertainty;
- timing includes a positive crossing, a no-crossing counterexample, and a late-crossing ambiguous case.

## Executable validation

Run the generator:

```bash
python scripts/build_stage7_1_synthetic_truth_cases.py
```

Run the tests:

```bash
python -m pytest tests/test_stage7_1_synthetic_truth.py
```

These checks prove that every Stage 7.1 method definition has at least one executable example and one counterexample, with ambiguous cases represented where the method should not overclaim.

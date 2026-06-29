# Stage 7.1 API stability notes

Stage 7.1 uses the existing RhoDyn public API to represent formal method objects and synthetic truth cases. It does not add a new stable package API.

## Stable objects used by Stage 7.1

| method object | current API surface |
| --- | --- |
| Tidy trajectory input | `rhodyn.schema.TrajectoryRecord`, `read_trajectory_csv`, `TRAJECTORY_SCHEMA` |
| Endpoint comparison input | `rhodyn.schema.EndpointRecord`, `read_endpoint_csv`, `ENDPOINT_SCHEMA` |
| Reserve-like input | `rhodyn.schema.ReserveRecord`, `read_reserve_csv`, `RESERVE_SCHEMA` |
| Coupling interval input | `rhodyn.schema.CouplingIntervalRecord`, `read_coupling_csv`, `COUPLING_SCHEMA` |
| Residence window and scoring | `rhodyn.residence.ResidenceWindow`, `score_trace`, `score_records` |
| Residence sensitivity | `rhodyn.sensitivity.residence_window_grid`, `score_trace_window_sensitivity` |
| Reserve-like normalization | `rhodyn.reserve.ff_over_f0`, `reserve_coordinate` |
| Bounded coupling | `rhodyn.coupling.equivalence_from_interval`, `one_sample_tost`, `two_sample_welch_tost`, `rope_decision` |
| Routed-output comparison | `rhodyn.compare.rank_model_fits` |
| Uncertainty | `rhodyn.uncertainty.bootstrap_interval`, `permutation_test` |
| Timing | `rhodyn.sim.first_passage_time`, `gillespie`, `tau_leap` |

## New Stage 7.1 script status

`scripts/build_stage7_1_synthetic_truth_cases.py` is a reproducibility and validation script. It is not a public package module and does not change the stable import surface.

## API gap decision

No key Stage 7.1 method object is blocked by the current API. No package API reopening is required before Stage 7.2. Future Stage 7 phases may still request API changes if benchmark harnesses or independent datasets require a stable adapter interface, but that decision belongs to the relevant later subphase.

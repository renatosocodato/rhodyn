# API reference

RhoDyn exposes a small, dependency-light Python API for dynamic operating-state
analysis from tidy live-cell and endpoint tables. The base package uses only
the Python standard library. Optional extras add statistics, plotting, backend,
notebook, and release-development tooling without changing the core import
path.

## Public package version

```python
import rhodyn
print(rhodyn.__version__)
```

The version value is also carried in backend job metadata and analysis bundles
so exported results can be tied to a software release.

## Input schemas

`rhodyn.schema` defines the four stable table roles used by the library, CLI,
backend, and workbench.

| schema | reader | record type | required columns |
| --- | --- | --- | --- |
| trajectory | `read_trajectory_csv` | `TrajectoryRecord` | `cell_id`, `time`, `condition`, `signal` |
| endpoint | `read_endpoint_csv` | `EndpointRecord` | `model`, `endpoint`, `observed`, `predicted` |
| reserve | `read_reserve_csv` | `ReserveRecord` | `sample_id`, `time`, `condition`, `response` |
| coupling | `read_coupling_csv` | `CouplingIntervalRecord` | `contrast`, `estimate`, `ci_low`, `ci_high`, `margin` |

`schema_specs()` returns these contracts as structured objects for user
interfaces and external validation.

## Residence-window scoring

`rhodyn.residence.ResidenceWindow` declares the low/high signal interval.
`score_trace()` scores one trajectory and `score_records()` scores all
trajectories grouped by condition and cell.

```python
from rhodyn.residence import ResidenceWindow, score_records
from rhodyn.schema import read_trajectory_csv

rows, issues = read_trajectory_csv("examples/synthetic_trajectory.csv")
if issues:
    raise ValueError(issues)
summaries = score_records(rows, ResidenceWindow(low=0.35, high=0.75))
```

Returned summaries include residence fraction, residence time, total time,
mean signal, maximum signal, minimum signal, and contiguous dwell segments.

## Reserve-style response summaries

`rhodyn.reserve.ff_over_f0()` normalizes a signal series by its early baseline.
`rhodyn.reserve.reserve_coordinate()` maps the peak response to a bounded
0-to-1 coordinate where larger values indicate greater remaining reserve under
the declared floor and ceiling.

These helpers summarize reserve-like behavior. They do not make a direct injury
or fate measurement.

## Bounded coupling and equivalence

`rhodyn.coupling.equivalence_from_interval()` classifies whether a supplied
confidence or credible interval lies fully inside a declared margin.
`one_sample_tost()` and `two_sample_welch_tost()` compute TOST decisions from
raw arrays. `rope_decision()` and `rope_mass()` summarize posterior samples
relative to the same margin.

A passing bounded-coupling decision means the contrast is contained within the
declared margin under the supplied uncertainty. It does not prove that two
pathways never communicate.

## Reduced-architecture comparison

`rhodyn.compare.rank_model_fits()` groups endpoint rows by model and ranks
reduced architectures by BIC, then residual sum of squares. Each row contains
an observed endpoint, a predicted endpoint, and an optional weight.

The ranking tests endpoint compatibility for declared alternatives. It does
not convert effective model parameters into literal molecular edges.

## Uncertainty and sensitivity

`rhodyn.uncertainty` provides percentile bootstrap intervals and permutation
tests. When grouping labels are supplied, the resampling or exchangeability
unit follows the declared group rather than silently treating every row as an
independent replicate.

`rhodyn.sensitivity` evaluates residence-window summaries across a low/high
grid. This is useful for asking whether a conclusion depends on one exact
window choice.

## Backend and typed results

`rhodyn.backend_core` provides dependency-light service functions used by the
FastAPI backend and the Stage 5 workbench. `rhodyn.results` wraps outputs in
JSON-friendly typed objects that retain condition, sample, replicate, input
schema, parameter choices, source labels, and software version.

Install `rhodyn[backend]` only when the FastAPI app is needed.

# RhoDyn architecture

RhoDyn separates reusable dynamic-state analysis from manuscript-specific
biological interpretation.

## Core layers

1. `rhodyn.schema`
   Validates tidy trajectory and endpoint tables.

2. `rhodyn.ctc`
   Converts Cell Tracking Challenge-style lineage and pre-extracted object
   feature tables into RhoDyn trajectory records. The v0.3.0 public case-study
   path uses this adapter for the MLCI microbial tracking benchmark while
   keeping raw video and segmentation-mask extraction outside the core package.

3. `rhodyn.residence`
   Scores signal dwell time inside a declared window and compares residence
   summaries with amplitude summaries.

4. `rhodyn.reserve`
   Provides normalization helpers for reserve-like buffering readouts.

5. `rhodyn.sensitivity`
   Scores residence summaries across declared low/high window grids, exposing
   how residence fraction, dwell time, segment count, and amplitude summaries
   change as the permissive interval is varied. This supports robustness checks
   over window choice rather than automatic discovery of a measured biological
   window.

6. `rhodyn.coupling`
   Encodes bounded-coupling decisions from confidence intervals or posterior
   samples supplied by the user. It also provides one-sample and Welch
   two-sample TOST helpers from raw arrays, with optional SciPy-backed
   t-distribution calculations under `rhodyn[stats]` and a dependency-free
   normal approximation for lightweight use. A passing decision means
   equivalence inside the declared biological margin, not proof that the
   underlying coupling is exactly zero.

7. `rhodyn.models`
   Simulates a minimal residence-gated controller.

8. `rhodyn.sim`
   Provides stochastic timing helpers, including first-passage and simple
   Gillespie/tau-leap routines.

9. `rhodyn.compare`
   Compares reduced controller predictions against endpoint constraints.

10. `rhodyn.uncertainty`
   Provides percentile bootstrap intervals and permutation tests for residence,
   reserve, coupling, endpoint-fit, and other one-dimensional summaries. When
   grouping labels are supplied, resampling and exchangeability operate at the
   declared group level rather than silently treating every row as an
   independent biological replicate.

11. `rhodyn.plots`
   Provides optional Matplotlib diagnostics for residence traces, bounded
   coupling intervals, reserve summaries, sensitivity curves, and endpoint-fit
   residuals. Plot labels distinguish measured signals from declared windows,
   derived decisions, and model-derived summaries.

12. `rhodyn.results`
   Wraps residence, reserve, coupling, uncertainty, sensitivity, and
   model-comparison outputs in typed, JSON-friendly result objects. Each result
   carries grouping metadata and provenance fields so condition, cell, replicate,
   well, donor, batch, input schema, analysis parameters, and software version
   remain visible beside the quantitative value.

13. `rhodyn.paper`
   Documents the manuscript repository and Zenodo data package as an optional
   case study without making them package dependencies.

## What stays outside the core

- raw microscopy reading;
- image segmentation;
- manuscript figure composition;
- disease-specific claims;
- private data adapters;
- dashboard or hosted analysis.

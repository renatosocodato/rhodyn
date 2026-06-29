# RhoDyn architecture

RhoDyn separates reusable dynamic-state analysis from manuscript-specific
biological interpretation.

The staged scientific and product roadmap is anchored in `docs/roadmap.md`.
The current architecture keeps the Stage 3 evidence bank frozen, preserves
the Stage 4 service contract, and treats the Stage 5 workbench plus Stage 6
public release as completed foundations. Stage 7 is now a roadmap-defined
methods-program layer for independent biological demonstrations, benchmark
expansion, software maturity, and future methods-manuscript readiness. Stage 8
commercial product work remains downstream of Stage 7 evidence.

## Core layers

1. `rhodyn.schema`
   Validates tidy trajectory and endpoint tables.

2. `rhodyn.ctc`
   Converts Cell Tracking Challenge-style lineage and pre-extracted object
   feature tables into RhoDyn trajectory records. It also contains a
   dependency-light reader for the simple uncompressed grayscale TIFF masks used
   by the public MLCI benchmark, allowing selected tracking masks and raw frames
   to become centroid, area, and mean-intensity feature rows without retaining
   raw image files. When a feature table includes CTC sequence identifiers,
   `rhodyn.ctc` preserves them in sequence-aware `cell_id` values and
   per-sequence replicate labels, preventing identical track labels from
   different sequences from being merged. The public helpers
   `ctc_track_cell_id()` and `ctc_sequence_replicate()` expose the same naming
   rule for external workflows.

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

12. `rhodyn.backend_core`
   Provides dependency-light service functions for schema validation,
   residence scoring, bounded-coupling decisions, reserve summaries,
   endpoint-model comparison, compact Markdown report export, and deterministic
   analysis bundle creation. It also provides the explicit filesystem-backed
   durable job store. These functions are the Stage 4 backend contract and call
   the same library helpers used by the CLI.

13. `rhodyn.backend`
   Provides the optional FastAPI application factory under `rhodyn[backend]`.
   The app delegates to `rhodyn.backend_core`; durable storage is enabled only
   when a job-store directory is configured.

14. `rhodyn.results`
   Wraps residence, reserve, coupling, uncertainty, sensitivity, and
   model-comparison outputs in typed, JSON-friendly result objects. Each result
   carries grouping metadata and provenance fields so condition, cell, replicate,
   well, donor, batch, input schema, analysis parameters, and software version
   remain visible beside the quantitative value.

15. `rhodyn.paper`
   Documents the manuscript repository and Zenodo data package as an optional
   case study without making them package dependencies.

## What stays outside the core

- general raw microscopy reading;
- image segmentation;
- manuscript figure composition;
- disease-specific claims;
- private data adapters;
- dashboard or hosted analysis beyond the first stateless FastAPI service;
- Stage 7 biological demonstrations before they are explicitly selected by the
  Stage 7 dataset rubric.

## Stage 4 to Stage 5 boundary

The frozen backend contract lives under `api/stage4/`. `openapi.json` is the
FastAPI schema, `frontend_contract.json` is the UI-facing operation map, and
`contract_manifest.json` records hashes plus the handoff state. The first
frontend scaffold in `frontend/stage5/` must consume those files and must not
add backend routes, biological systems, algorithms, or release surfaces.

Regenerate the contract only with `scripts/freeze_stage4_api_contract.py`, then
run `scripts/audit_stage5_frontend_scaffold.py` before changing frontend
behavior.

## Stage 7 boundary

The Stage 7 planning surfaces live in `docs/stage7_methods_program.md` and
`docs/stage7_serialized_execution_plan.md`. They do not change the core API by
themselves. Future Stage 7 implementation may add adapters, benchmarks,
reproducibility fixtures, or usability evidence only after the relevant subphase
gate is authorized.

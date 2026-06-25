# Changelog

## Unreleased

Started:

- CTC-style public live-cell tracking adapter for the MLCI benchmark tutorial;
- `ctc-to-trajectory` CLI conversion from pre-extracted track features to RhoDyn trajectory tables;
- tiny CTC-style schema fixture and runnable public-case-study workflow scaffold;
- MLCI tutorial documentation connecting conversion, residence scoring, sensitivity, uncertainty, and optional plots.

Boundary:

- The bundled fixture validates the adapter and workflow only. Biological interpretation requires features extracted from the public Zenodo benchmark.

## v0.1.0

Private hardening release for the standalone RhoDyn toolkit.

Added:

- typed CSV schemas for trajectory, endpoint, reserve, and coupling inputs;
- residence-window scoring and reserve-style normalization helpers;
- bounded-coupling decisions from supplied intervals or posterior mass;
- minimal deterministic and stochastic controller utilities;
- reduced-model endpoint comparison helpers;
- dependency-free synthetic workflows and examples;
- optional dependency groups for future pandas, statistics, plotting, and notebook workflows;
- a local paper case-study adapter that maps user-supplied release tables into generic RhoDyn schemas.

Boundaries:

- RhoDyn is independent from the manuscript repository;
- the manuscript repository and Zenodo package are optional case-study inputs, not runtime dependencies;
- the package does not ship raw microscopy, manuscript figures, private data, or clinical prediction tools.

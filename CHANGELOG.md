# Changelog

## Unreleased

Started:

- CTC-style public live-cell tracking adapter for the MLCI benchmark tutorial;
- `ctc-to-trajectory` CLI conversion from pre-extracted track features to RhoDyn trajectory tables;
- dependency-light CTC TIFF-mask feature extraction for centroid, area, and mean raw-intensity rows;
- range-based MLCI feature-subset helper that writes derived features and provenance without retaining raw TIFF images;
- denser v0.3.2 public feature subset sampled every 10 frames from frame 0 through frame 140;
- multi-sequence v0.3.3 public feature subset from sequences `00` and `01`, with sequence-aware track identifiers and per-sequence replicate labels;
- public helper functions for stable sequence-aware CTC `cell_id` and replicate-label construction;
- tiny CTC-style schema fixture and runnable public-case-study workflow scaffold;
- MLCI tutorial documentation connecting conversion, residence scoring, sensitivity, uncertainty, and optional plots.

Boundary:

- The bundled public feature subset validates the adapter and workflow only. Biological interpretation requires a declared signal, residence window, grouping structure, and uncertainty rule.

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

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
- Stage 3A public DRG calcium residence-versus-amplitude benchmark;
- Stage 3B public ERK/GPCR kinase-signaling residence-versus-amplitude benchmark;
- Stage 3C public Cell Painting/MitoTox endpoint model-comparison benchmark;
- Stage 3D public ERK/Akt bounded-coupling benchmark from paired GPCR
  residence summaries;
- Stage 3D margin-sensitivity, threshold-sensitivity, and hardening-report
  outputs for the ERK/Akt bounded-coupling benchmark;
- Stage 3 case-study bank gate audit and report tying the public examples back
  to the original roadmap gate;
- three tutorial notebooks covering the synthetic primer, public
  residence-versus-amplitude benchmarks, and public endpoint/coupling
  benchmarks;
- Stage 4 stateless backend service core and optional FastAPI app for schema
  validation, residence scoring, bounded-coupling decisions, reserve summaries,
  endpoint-model comparison, Markdown report export, and downloadable analysis
  bundles with manifests and checksums;
- tiny CTC-style schema fixture and runnable public-case-study workflow scaffold;
- MLCI tutorial documentation connecting conversion, residence scoring, sensitivity, uncertainty, and optional plots.

Boundary:

- The bundled public feature subset validates the adapter and workflow only. Biological interpretation requires a declared signal, residence window, grouping structure, and uncertainty rule.
- The DRG calcium and ERK/GPCR benchmarks support residence-versus-amplitude separation across two public signaling systems, and the Cell Painting/MitoTox benchmark adds an independent endpoint model-comparison case.
- Stage 3D closes the v0.3 evidence-bank gate with a public bounded-coupling
  case. The UK ERK/Akt residence contrast is bounded under the declared margin,
  while S1P and histamine do not pass, so the result is context-limited.
- The Stage 3D hardening pass keeps the all-ligand pooled result secondary and
  records that within-ligand replicate sensitivity is unavailable for the
  selected public DMSO-control slice.
- The Cell Painting/MitoTox endpoint benchmark compares reduced morphology architectures, but it does not infer drug mechanism or convert morphology into a live dynamic-state measurement.

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

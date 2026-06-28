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
- explicit Stage 4 filesystem job store that persists submitted rows,
  parameters, exact result JSON, result rows, reports, bundle manifests, and ZIP
  bundles only when a job-store directory is configured;
- Stage 4 retention-policy controls, storage summary and prune routes,
  concurrent submit/read stress tests, and deployment environment example;
- Stage 4 service-contract hardening for optional API-key authentication,
  row/upload quotas, raw CSV upload routes, and Docker/Compose deployment
  templates;
- Stage 4 service-contract audit checking direct backend helpers, generic job
  dispatch, deterministic bundles, and durable stored jobs against the same
  submitted rows and declared parameters;
- Stage 4 FastAPI upload stress audit for larger synthetic tables,
  authentication, row/upload quotas, durable submit/retrieve behavior,
  concurrent upload determinism, and retention pruning;
- Stage 4 Docker deployment smoke audit for hosted-service environment
  variables, image build, container startup, HTTP upload/job routes, bundle
  hashes, authentication, quotas, and retention behavior;
- Stage 4 API contract freeze with committed OpenAPI, frontend operation
  metadata, canonical request/response fixtures, and closeout documentation;
- first Stage 5 static frontend scaffold bound to the frozen Stage 4 contract;
- Stage 5 upload-flow hardening with CLI coverage for all six contract
  operations, schema and parameter inspection in the static workbench, and a
  parity audit comparing CLI output, backend-core output, and frozen upload
  fixtures;
- Stage 5 UX-depth pass with richer trajectory inspection, explicit exported
  parameter provenance, and a guided MLCI public trajectory workflow;
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

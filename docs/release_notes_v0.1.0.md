# RhoDyn v0.1.0 release notes

Release date. 2026-06-29.

Release type. Versioned software release with GitHub archive and Zenodo software deposition.

## Summary

RhoDyn v0.1.0 establishes the first citable software boundary for the standalone
RhoDyn toolkit. The release exposes residence-window scoring, bounded-coupling
decisions, reserve-style summaries, reduced-architecture comparison,
stochastic timing utilities, uncertainty helpers, a command-line interface, a
contract-bound backend service, and the Stage 5 browser workbench.

The release is independent from the RhoA/microglia manuscript. Manuscript and
Zenodo paper materials may be used later as an optional reference case study,
but they are not runtime dependencies and are not bundled as private source
material in this software archive.

## User-facing additions

- Dependency-light Python package with the `rhodyn` CLI entry point.
- Tidy CSV input schemas for trajectory, endpoint, reserve, and coupling tables.
- Residence, amplitude, dwell-time, reserve, bounded-coupling, uncertainty, and
  reduced-model comparison helpers.
- Synthetic examples and public case-study scaffolds for residence-versus-
  amplitude separation, bounded coupling, endpoint model comparison, and
  Cell Tracking Challenge-style trajectory conversion.
- Optional extras for statistics, plotting, backend service use, notebooks, and
  release-development tooling.
- FastAPI-compatible backend service with schema validation, analysis endpoints,
  deterministic job bundles, and optional durable job storage.
- Stage 5 static workbench for upload validation, trajectory exploration,
  residence-window tuning, coupling decisions, reserve summaries,
  model-comparison panels, and report export.

## Archive and citation surfaces

- `CITATION.cff` defines the software citation metadata for v0.1.0.
- `.zenodo.json` prepares Zenodo software-deposit metadata without claiming a DOI
  before deposition.
- `docs/release_checksums.csv` and `docs/release_checksums.json` record SHA-256
  checksums for the release-critical text, code, documentation, example, API,
  frontend, deployment, and workflow surfaces.
- `CONTRIBUTING.md` defines development checks and the boundary between RhoDyn
  software examples and manuscript-private materials.

## Validation status

The release state passes the local release-safety check, Phase 6 readiness audit through subphase 6.7, unit tests, documentation build, package dry run, Zenodo dry run, Docker smoke testing, clean-room reproducibility, and Stage 5 screenshot regression.

## Public citation record

The v0.1.0 tag is pushed, the GitHub release archive is published, and the Zenodo software record is public. No local hardening gate remains open for v0.1.0.

## Interpretation boundary

RhoDyn outputs dynamic operating-state summaries from user-supplied live-cell or
perturbation tables. It does not infer clinical state, does not replace
experiment-specific biological interpretation, and does not ship raw microscopy
or manuscript-private source data.


## Zenodo software record

Version DOI. https://doi.org/10.5281/zenodo.21036616

Concept DOI. https://doi.org/10.5281/zenodo.21036615

Public record. https://zenodo.org/records/21036616

# Stage 10.9 one-page EIC-safe presubmission pitch

## Working title

Residence-state inference for live-cell perturbation data

## Pitch

RhoDyn is a residence-state inference method for live-cell perturbation biology that asks when time spent inside a declared biological response regime changes interpretation relative to endpoint, amplitude, threshold, and generic time-series summaries. It benchmarks that decision object against simple summaries, SciPy peak summaries, scikit-learn feature models, HMM state summaries, catch22-style, tsfresh-style, MiniROCKET-style, and ruptures-style comparator families, retaining cases where simpler summaries are sufficient rather than claiming universal superiority. Public demonstrations span DRG calcium dynamics, GPCR-linked ERK trajectories, Cell Painting/MitoTox endpoint profiling, and MLCI tracking, so the method is not presented as a single-system extension of the RhoA/microglia manuscript. A sealed no-retuning validation route preserves positive residence-divergence, comparator-sufficient, bounded-coupling, and inconclusive calls across held-out public-derived contexts. The software implementation makes the method inspectable through Python, command-line, API, workbench, checksum, and archive surfaces, but reproducibility supports the method claim rather than replacing it. The intended Nature Methods contribution is therefore not a biology-only manuscript and not a software wrapper; it is a scoped decision framework for deciding when residence, bounded coupling, reserve-like preservation, or routed-output structure changes interpretation, and when it does not.

## Residual boundaries for the editor-facing version

- Declared residence windows are analysis objects, not automatically discovered biological mechanisms.
- Held-out validation is no-retuning public-derived replay, not a prospective blinded collaborator study.
- Reserve-like and routed-output calls are measurement-scoped and effective-model decisions.
- Named feature and classifier baselines can be sufficient in some regimes.

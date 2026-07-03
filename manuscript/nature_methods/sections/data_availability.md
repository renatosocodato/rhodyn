<!-- DATA-AVAILABILITY stage=9.17 generated_utc=2026-07-03T16:36:31.772873Z -->

# Data availability

The evidence tables used for the RhoDyn Nature Methods Article are retained with the RhoDyn v0.1.0 source release and software archive. The citable release is available from https://github.com/renatosocodato/rhodyn and the Zenodo version DOI https://doi.org/10.5281/zenodo.21036616. The concept DOI https://doi.org/10.5281/zenodo.21036615 resolves to the current RhoDyn software concept. The released repository contains synthetic truth cases, public-derived trajectory tables, public-derived endpoint tables, reserve-like summaries, bounded-coupling summaries, routed-output comparison outputs, held-out validation outputs, checksums, and report files needed to inspect the manuscript evidence set.

Public source datasets used to construct the retained derived demonstrations are:

- DRG calcium live-cell trajectories. Source record https://zenodo.org/records/14907827; DOI https://doi.org/10.5281/zenodo.14907827; retained derived outputs `case_studies/stage7_public_signaling/drg_calcium_*`.
- ERK GPCR and ERK/Akt reporter trajectories. Source record https://zenodo.org/records/5836623; DOI https://doi.org/10.5281/zenodo.5836623; retained derived outputs `case_studies/stage7_public_signaling/erk_gpcr_* and case_studies/stage7_endpoint_reserve_routing/erk_akt_*`.
- Cell Painting and MitoTox endpoint tables. Source record https://zenodo.org/records/10011861; DOI https://doi.org/10.5281/zenodo.10011861; retained derived outputs `case_studies/stage7_endpoint_reserve_routing/cell_painting_*`.

Raw public source archives are not duplicated in the repository when they can be recovered from their public records. The retained derived tables preserve the identifiers, condition fields, time or endpoint variables, grouping fields when available, declared analysis parameters, and output summaries required to reproduce the RhoDyn method demonstrations. Controlled-access or private microscopy data are not required for the RhoDyn method-evidence claims in this Article.

The RhoA/microglia manuscript materials are treated as an optional biological reference use case rather than as hidden inputs to the RhoDyn methods evidence. That separate reference case is available at https://github.com/renatosocodato/windowed_rhoA_model pinned to commit `e63cc93a4b23d8b3d27cf25136b00d53fa6144f4`, with software archive DOI https://doi.org/10.5281/zenodo.19796404 and data/replication DOI https://doi.org/10.5281/zenodo.19796406. Those materials illustrate a motivating biological context, but the RhoDyn package, benchmarks, and public demonstrations do not depend on manuscript-private raw microscopy or unpublished model files.

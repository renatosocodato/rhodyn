# Cell Painting endpoint model-comparison benchmark

This Stage 3C benchmark uses public Cell Painting morphology profiles and
MitoTox biological activity endpoints from Seal et al. 2023 to test whether
reduced endpoint architectures preserve the same perturbation information.

Source record: https://zenodo.org/records/10011861  
DOI: https://doi.org/10.5281/zenodo.10011861  
License: CC-BY-4.0

The source files used here are
`Cell_Painting_data_658_compounds_827_Features_scaled.csv` and
`Endpoints_9_Mitotox_biological_activities_658_compounds.csv`. RhoDyn does not
retain these source CSV files. The builder downloads them into memory, aligns
compounds by standardized InChI, compares reduced endpoint architectures, and
writes only derived benchmark rows plus provenance.

## Regenerate

```bash
PYTHONPATH=src python scripts/fetch_cell_painting_endpoint_benchmark.py
```

Default settings use five leave-one-compound-out nearest neighbors for
morphology-derived architectures. Endpoints are weighted so positive and
negative labels each contribute half of the residual weight within each endpoint.
This prevents the inactive majority from dominating the comparison.

Outputs:

- `case_studies/cell_painting_mitotox_endpoint_model_rows.csv`
- `case_studies/cell_painting_mitotox_model_ranking.csv`
- `case_studies/cell_painting_mitotox_endpoint_summary.csv`
- `case_studies/cell_painting_mitotox_model_comparison.provenance.json`

## Architectures compared

- `endpoint_prevalence` predicts each endpoint from its leave-one-compound-out
  prevalence.
- `morphology_magnitude_5nn` reduces the full morphology profile to one global
  profile magnitude before nearest-neighbor prediction.
- `cells_block_5nn`, `cytoplasm_block_5nn`, and `nuclei_block_5nn` use one
  Cell Painting compartment at a time.
- `compartment_route_5nn` keeps three routed compartment magnitudes, one each
  for Cells, Cytoplasm, and Nuclei.

## Benchmark result

The retained endpoint table contains 35,532 model rows from 658 compounds,
nine endpoints, and six endpoint architectures. In the default derived ranking,
`compartment_route_5nn` is best by BIC and weighted RMSE:

- `compartment_route_5nn`: weighted RMSE 0.6150, BIC -44160.06
- `endpoint_prevalence`: weighted RMSE 0.6253, delta BIC 248.56
- `morphology_magnitude_5nn`: weighted RMSE 0.6334, delta BIC 331.52
- single-compartment blocks have larger delta BIC values after dimensional
  penalty.

The narrow biological lesson is that endpoint prevalence and one-dimensional
morphology summaries miss endpoint structure that is retained by a routed
compartment summary. This is the first public Stage 3 endpoint/model-comparison
case for RhoDyn and complements the DRG calcium and ERK/GPCR signaling
benchmarks.

## Boundary

This case study compares endpoint compatibility among declared reduced
architectures. It does not infer drug mechanism, does not train a production
classifier, and does not treat Cell Painting morphology as a live dynamic-state
measurement.

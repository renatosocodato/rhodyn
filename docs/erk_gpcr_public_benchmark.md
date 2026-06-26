# ERK/GPCR public signaling benchmark

This Stage 3B benchmark uses public single-cell ERK KTR trajectories from Wan
et al. 2021 to test whether RhoDyn separates peak kinase activity from
high-ERK residence in a second biological signaling system.

Source record: https://zenodo.org/records/5836623  
DOI: https://doi.org/10.5281/zenodo.5836623  
License: CC-BY-4.0

The source archive used here is `Figure_3.zip`, which contains single-cell ERK
and Akt KTR measurements for GPCR ligand conditions. RhoDyn does not retain the
source ZIP or member CSV files. The builder downloads the archive into memory,
extracts a bounded DMSO-control subset from `ALL_UK.csv`, `ALL_S1P.csv`, and
`ALL_His.csv`, and writes only derived benchmark rows plus provenance.

## Regenerate

```bash
PYTHONPATH=src python scripts/fetch_erk_gpcr_benchmark.py
```

Default settings retain up to 60 cells per ligand, score `CN_ERK`, and define
the high-ERK residence window from the 75th percentile of the retained ERK KTR
values. This threshold is analytical. It is not a calibrated biological
activation boundary.

Outputs:

- `case_studies/erk_gpcr_residence_amplitude_benchmark.csv`
- `case_studies/erk_gpcr_residence_amplitude_benchmark.provenance.json`

## Benchmark shape

The retained table contains 180 single-cell trajectory summaries from three
ligand contexts. Each row reports the maximum ERK KTR value, mean ERK KTR value,
high-ERK residence fraction, residence time, and top-quartile classification.

Default class counts:

- `amplitude_and_residence_top_quartile`: 34
- `amplitude_only_top_quartile`: 11
- `residence_only_top_quartile`: 11
- `neither_top_quartile`: 124

## Scientific use

This benchmark gives RhoDyn a second independent live-cell signaling example,
now in ERK/GPCR kinase dynamics rather than DRG calcium dynamics. The narrow
result is that peak ERK KTR signal and high-ERK residence are related but not
interchangeable in the retained public subset. Some cells rank highly by peak
ERK but not by time spent above the high-ERK threshold, while other cells show
the reverse pattern.

The table is a software-methods benchmark. It does not infer GPCR mechanism,
does not compare ligand pharmacology, and does not claim that the quantile
threshold is a universal ERK activation regime.

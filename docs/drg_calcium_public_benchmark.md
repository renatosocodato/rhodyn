# DRG calcium public benchmark

This case study is the first Stage 3A live-cell signaling benchmark for RhoDyn.
It uses a public calcium-imaging trace table from von Buchholtz 2025,
`A distributed coding logic for thermosensation and inflammatory pain`, released
on Zenodo under CC-BY-4.0.

Source record: https://zenodo.org/records/14907827  
DOI: https://doi.org/10.5281/zenodo.14907827  
Trace file used: `sstlineage_ly_drg_traces.csv`  
Metadata file used: `sstlineage_ly_drg_info.csv`

## Biological scope

The source trace file contains deltaF/F0 calcium fluorescence traces for
individual dorsal-root-ganglion neurons. The public README states that calcium
trace files contain 40 second episodes concatenated across 200 frames. RhoDyn
uses this file as an independent public live-cell signaling example, separate
from the RhoA/microglia manuscript.

The retained benchmark does not assign stimulus identities. The source notebook
contains the original figure/stimulus mapping, but this Stage 3A benchmark uses
neutral episode labels only. The residence window is a declared high-calcium
analysis window, not a calibrated biological threshold.

## Regenerate the derived benchmark

```bash
python scripts/fetch_drg_calcium_benchmark.py
```

The script downloads the source trace and metadata CSV files into memory,
converts the first 120 cells into RhoDyn trajectory records internally, scores
three 200-frame episodes per cell, and writes only derived benchmark outputs.
Raw source CSV files are not retained in the repository.

Generated outputs:

- `case_studies/drg_calcium_residence_amplitude_benchmark.csv`
- `case_studies/drg_calcium_residence_amplitude_benchmark.provenance.json`

## Benchmark logic

The benchmark compares two single-cell summaries for each episode.

- Amplitude summary. The maximum deltaF/F0 value in the episode.
- Residence summary. The fraction and duration of time spent in the declared
  high-calcium window, using `ResidenceWindow(low=10.0, high=1e12)`.

Rows are ranked by maximum amplitude and by residence fraction. Top-quartile
membership is then compared across the two rankings.

Current derived table:

- 120 selected neurons.
- 3 episodes per neuron.
- 360 episode-cell benchmark rows.
- 74 rows are top quartile by both amplitude and residence.
- 16 rows are amplitude-only top quartile.
- 16 rows are residence-only top quartile.
- 254 rows are in neither top quartile.

## Interpretation

This benchmark shows that a public calcium-imaging dataset can be mapped into
RhoDyn's trajectory logic and used to compare amplitude-only and
residence-based summaries. The amplitude-only and residence-only top-quartile
rows are the key Stage 3A result. They show that peak calcium and high-calcium
dwell time are related but not identical descriptions of the same traces.

This does not prove a disease mechanism, stimulus encoding rule, or calibrated
calcium threshold. It is a software-methods benchmark demonstrating that RhoDyn
can expose a residence-versus-amplitude distinction in an independent public
live-cell signaling dataset.

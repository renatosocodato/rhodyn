# Public-data case-study candidates

This note records the first Nature Methods-facing public-data candidates for
RhoDyn. The manuscript repository and Zenodo data package remain the reference
use case, but they should not be the only evidence that the software generalizes.
No biological claim is made from any public candidate until the data are
ingested, analyzed, and validated in a later release.

## Selection criteria

A strong public-data case study should satisfy these requirements.

- It should provide single-cell or single-object measurements over time, or a
  high-quality static comparator that tests the limits of dynamic-state
  inference.
- It should expose enough grouping metadata to preserve experiment, replicate,
  field, well, donor, batch, or stimulus context.
- It should have a clear public access path and license.
- It should map naturally to RhoDyn schemas, especially trajectory,
  endpoint-comparison, reserve-like, or coupling-decision tables.
- It should support a tutorial that is scientifically useful without importing
  manuscript-specific claims.
- It should be appropriate for eventual public documentation and, if used in a
  commercial setting, should have reuse terms compatible with that use.

## Shortlist

### Primary v0.3.0 tutorial target

**Tracking one-in-a-million microbial single-cell tracking benchmark.** This
Zenodo dataset is the strongest first public tutorial candidate because it is
live-cell, time-resolved, annotated, and licensed CC-BY-4.0. The record provides
Cell Tracking Challenge-format annotations and videos through `ctc_format.zip`
and `videos.zip`. RhoDyn should not analyze raw videos in v0.3.0. Instead, the
tutorial should extract or use pre-extracted track-level features such as motion,
growth, division timing, or activity-like trajectory summaries, then map them to
`cell_id`, `time`, `condition`, `signal`, and grouping metadata. This gives the
software a clean public demonstration of residence-window sensitivity,
first-passage summaries, grouped uncertainty, and diagnostic plots outside the
microglia manuscript.

Source: https://zenodo.org/records/7260137  
Concept DOI: https://doi.org/10.5281/zenodo.7260136  
Version DOI: https://doi.org/10.5281/zenodo.7260137

### Secondary static-phenotype comparator

**Cell Painting Gallery.** This AWS Open Data resource is a large CC0 collection
of microscopy images, extracted features, and metadata from Cell Painting assays.
It is not a live-cell signaling dataset, so it should not be used to claim
residence dynamics. Its value is different. It can serve as a morphology-rich
static-state comparator that shows how RhoDyn separates static phenotype
profiles from dynamic trajectory-derived state variables. Because the license is
CC0, it is also attractive for documentation and product-facing examples.

Source: https://registry.opendata.aws/cellpainting-gallery/

### Selected Stage 3A live-cell signaling benchmark

**DRG calcium dynamics from von Buchholtz 2025.** This Zenodo dataset provides
deltaF/F0 calcium traces for individual dorsal-root-ganglion neurons, with
40 second episodes concatenated across 200 frames. It is a better Stage 3A
signaling benchmark than the microbial tracking example because the measured
quantity is a calcium activity trace rather than motion or morphology. RhoDyn
uses the `sstlineage_ly_drg_traces.csv` trace file and
`sstlineage_ly_drg_info.csv` metadata file to build a derived
residence-versus-amplitude benchmark. The retained table shows both
amplitude-only and residence-only top-quartile rows under a declared
high-calcium window, which is the first independent public-data example of the
distinction RhoDyn is designed to expose.

Source: https://zenodo.org/records/14907827

DOI: https://doi.org/10.5281/zenodo.14907827

License: CC-BY-4.0

Tutorial: `docs/drg_calcium_public_benchmark.md`

### Secondary calcium-dynamics candidate with license review

**Allen Brain Observatory visual coding two-photon calcium imaging.** The Allen
SDK documentation describes a public database of visually evoked neuronal
responses measured by two-photon fluorescence imaging, with traces stored in NWB
files. The processing includes cell-mask segmentation, fluorescence extraction,
neuropil correction, demixing, and dF/F computation. This is biologically useful
for testing trajectory, reserve-like, and first-passage summaries on calcium
dynamics. The caution is commercial reuse. The SDK license is an Allen
Institute noncommercial software license, so this candidate should undergo
license review before being used in product-positioning examples.

Source: https://allensdk.readthedocs.io/en/latest/brain_observatory.html  
SDK license: https://github.com/AllenInstitute/AllenSDK/blob/master/LICENSE.txt

## Watchlist

ERK/KTR and NF-kB live-cell dynamics remain high-value targets because they are
closer to signaling-residence use cases than tracking or static morphology.
They are deliberately kept on the watchlist until a dataset has a verified URL,
license, access format, and schema mapping. They should not be used for public
claims or tutorials until that check is complete.

## Recommended next move

Use the microbial tracking benchmark as the v0.3.0 tutorial target. It is the
best current balance of public access, time-resolved biology, annotation quality,
and license clarity. Use Cell Painting as a static-state comparator and keep
Allen calcium as a scientifically strong but license-sensitive candidate.

The v0.3.0 adapter and tutorial scaffold are now started in `rhodyn.ctc`, the
`ctc-to-trajectory` and `ctc-lineage-to-trajectory` CLI commands, and
`docs/mlci_public_tutorial.md`. The v0.3.1 path adds a small public
segmentation-derived feature table at
`case_studies/mlci_public_track_features_subset.csv`, with provenance in the
neighboring JSON file. The v0.3.2 refresh samples the public benchmark every 10
frames from frame 0 through frame 140 while retaining only centroid, area, and
mean-intensity rows. The v0.3.3 refresh extends the retained feature table to
sequences `00` and `01`, sampled every 20 frames from frame 0 through frame 140,
and preserves sequence identity when converting tracks into trajectory records.
The earlier
`case_studies/mlci_public_man_track_subset.txt` lineage subset remains as a
fallback for tests that need track intervals without object-level features.

The Stage 3A live-cell signaling benchmark is now started through
`scripts/fetch_drg_calcium_benchmark.py` and the retained derived table
`case_studies/drg_calcium_residence_amplitude_benchmark.csv`. This moves RhoDyn
from public-data infrastructure into the first independent calcium-signaling
benchmark, but it does not complete the full Stage 3 evidence gate by itself.

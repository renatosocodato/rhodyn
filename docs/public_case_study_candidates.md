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

### Selected Stage 3C endpoint/model-comparison benchmark

**Cell Painting and MitoTox endpoints from Seal 2023.** This Zenodo record
pairs scaled Cell Painting morphology profiles with nine MitoTox biological
endpoint labels for the same 658 compounds. RhoDyn uses the scaled Cell
Painting profile table and the endpoint table to build leave-one-compound-out
predictions from reduced architectures. The retained ranking compares endpoint
prevalence, one-dimensional morphology magnitude, single-compartment
morphology, and a routed three-compartment summary. The routed compartment
architecture is best by BIC and endpoint-balanced weighted RMSE, showing that
the endpoint table retains structure missed by simpler summaries.

Source: https://zenodo.org/records/10011861

DOI: https://doi.org/10.5281/zenodo.10011861

License: CC-BY-4.0

Tutorial: `docs/cell_painting_endpoint_benchmark.md`

Builder: `scripts/fetch_cell_painting_endpoint_benchmark.py`

Derived ranking: `case_studies/cell_painting_mitotox_model_ranking.csv`

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

NF-kB live-cell dynamics remains a high-value target because it is close to the
immune-signaling residence use case. It is deliberately kept on the watchlist
until a dataset has a verified URL, license, access format, and schema mapping.
It should not be used for public claims or tutorials until that check is
complete. ERK/KTR dynamics is no longer only a watchlist item because the Wan
2021 GPCR source-data archive now provides a selected Stage 3B kinase-signaling
benchmark.

## Current public-data surfaces

The v0.3.x adapter and tutorial scaffold are in place in `rhodyn.ctc`, the
`ctc-to-trajectory` and `ctc-lineage-to-trajectory` CLI commands, and
`docs/mlci_public_tutorial.md`. The retained MLCI feature table samples public
benchmark sequences `00` and `01`, preserves sequence identity, and demonstrates
public-data ingestion without retaining raw TIFF masks. The earlier
`case_studies/mlci_public_man_track_subset.txt` lineage subset remains as a
fallback for tests that need track intervals without object-level features.

The Stage 3A live-cell signaling benchmark is in place through
`scripts/fetch_drg_calcium_benchmark.py` and the retained derived table
`case_studies/drg_calcium_residence_amplitude_benchmark.csv`. This moves RhoDyn
from public-data infrastructure into an independent calcium-signaling benchmark,
but it does not complete the full Stage 3 evidence gate by itself.

### Selected Stage 3B kinase-signaling benchmark

**ERK KTR dynamics after GPCR stimulation from Wan 2021.** This Zenodo source
archive provides single-cell ERK and Akt KTR trajectories after GPCR ligand
stimulation. RhoDyn uses the Figure 3 source archive, extracts a bounded
DMSO-control subset from `ALL_UK.csv`, `ALL_S1P.csv`, and `ALL_His.csv`, and
builds a derived residence-versus-amplitude benchmark from `CN_ERK`. The
retained table shows both amplitude-only and residence-only top-quartile rows
under a declared high-ERK quantile threshold. This is the second independent
public live-cell signaling benchmark and extends the evidence bank from calcium
dynamics into kinase-reporter dynamics.

Source: https://zenodo.org/records/5836623

DOI: https://doi.org/10.5281/zenodo.5836623

License: CC-BY-4.0

Tutorial: `docs/erk_gpcr_public_benchmark.md`

Builder: `scripts/fetch_erk_gpcr_benchmark.py`

Derived table: `case_studies/erk_gpcr_residence_amplitude_benchmark.csv`

### Selected Stage 3D bounded-coupling benchmark

**ERK and Akt residence after GPCR stimulation from Wan 2021.** This benchmark
uses the same public Figure 3 source archive but reads paired ERK and Akt KTR
trajectories from the same selected cells. RhoDyn summarizes high-state
residence for each reporter, computes the paired ERK-minus-Akt residence
contrast, and applies one-sample TOST under a declared +/-0.20 residence
fraction margin. The UK context falls inside the declared bounded-coupling
margin, while S1P and histamine do not. The all-ligand summary also falls
inside the margin, but it mixes ligand-specific directional effects and should
be treated as a summary check rather than as the biological conclusion.

Source: https://zenodo.org/records/5836623

DOI: https://doi.org/10.5281/zenodo.5836623

License: CC-BY-4.0

Tutorial: `docs/erk_akt_bounded_coupling_benchmark.md`

Builder: `scripts/fetch_erk_akt_bounded_coupling.py`

Derived summary: `case_studies/erk_gpcr_erk_akt_residence_summary.csv`

Derived coupling table: `case_studies/erk_gpcr_erk_akt_bounded_coupling.csv`

## Recommended next move

Stage 3 can now be frozen for the v0.3 evidence bank. The DRG calcium and
ERK/GPCR benchmarks support the residence-versus-amplitude distinction across
two public signaling systems. The Cell Painting/MitoTox benchmark supplies a
public endpoint model-comparison case. The ERK/Akt benchmark supplies a public
bounded-coupling case with an explicit context limit. The next aligned build is
Stage 4 backend work around these stable Python and file-output surfaces.

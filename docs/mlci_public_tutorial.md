# v0.3.x public tutorial lane

This tutorial starts the first public-data case study for RhoDyn using the
Tracking one-in-a-million microbial single-cell tracking benchmark. The public
benchmark is a live-cell tracking dataset distributed through Zenodo in Cell
Tracking Challenge format. RhoDyn does not read raw videos or segmentation masks
as a persistent local dataset in v0.3.3. Instead, the public helper range-fetches
selected tracking masks and raw frames across declared CTC sequences, derives
centroid, area, and mean intensity features, and keeps only the resulting
feature table plus provenance. Those features are then converted into the
standard trajectory schema used by the residence, sensitivity, uncertainty, and
plotting layers.

Public source: https://zenodo.org/records/7260137  
Concept DOI: https://doi.org/10.5281/zenodo.7260136  
Version DOI: https://doi.org/10.5281/zenodo.7260137  
License: CC-BY-4.0

## Biological question

The tutorial asks whether time-resolved microbial track behavior can be handled
as a dynamic trajectory problem rather than as a static image phenotype. A
track-level signal can represent speed, displacement, area, or intensity after
features are extracted from the public CTC masks or videos. The resulting signal
is not a molecular activity measurement. It is a public live-cell dynamics
readout that exercises the same RhoDyn software surfaces used for signaling
residence analysis.

## Input contract

Prepare a feature table with these columns.

| column | meaning |
| --- | --- |
| `sequence` | optional CTC sequence identifier, such as `00` or `01` |
| `track_id` | CTC object or track label |
| `frame` | frame index |
| `x` | centroid x coordinate |
| `y` | centroid y coordinate |
| `area` | object area or mask size |
| `intensity` | optional object intensity summary |

If available, keep the CTC `man_track.txt` file beside the feature table. RhoDyn
uses it to check that feature frames fall within the lineage interval declared
for each track.

The repository includes two small real public subsets from the benchmark. The
primary v0.3.3 subset is
`case_studies/mlci_public_track_features_subset.csv`, a derived table of
centroids, areas, and mean raw intensities from selected tracking masks and raw
frames in sequences `00` and `01`, sampled every 20 frames from frame 0 through
frame 140. The companion provenance file records the Zenodo source, selected
ZIP entries, checksum, sequence list, and raw-file policy. A lighter lineage-only
subset remains at
`case_studies/mlci_public_man_track_subset.txt` for fallback tests when mask
features are not available.

## Derive public mask features without keeping raw images

The helper below reads only selected entries from the Zenodo `ctc_format.zip`
archive by HTTP byte range. It decodes TIFF masks and raw frames in memory,
writes the derived feature table, and does not write raw image files.

```bash
python scripts/fetch_mlci_feature_subset.py \
  --sequences 00,01 \
  --frames 0:140:20 \
  --output case_studies/mlci_public_track_features_subset.csv \
  --provenance case_studies/mlci_public_track_features_subset.provenance.json
```

The generated CSV is the tutorial's public feature input. The provenance JSON
records the exact frame entries and states that raw TIFF entries were decoded in
memory only. If a local development run writes temporary raw images for
debugging, those files should be deleted before the run is closed.

## Convert tracks to RhoDyn trajectories

The adapter supports four signal choices.

- `speed` computes frame-to-frame centroid motion.
- `displacement` computes distance from each track's first centroid.
- `area` uses object area directly.
- `intensity` uses an optional extracted intensity column.

Example using the bundled schema fixture.

```bash
python -m rhodyn.cli ctc-to-trajectory \
  examples/mlci_ctc_features.csv \
  --lineage examples/mlci_man_track.txt \
  --signal speed \
  --condition mlci_tracking \
  --replicate zenodo_7260137 \
  --output mlci_speed_trajectory.csv
```

The output is a normal RhoDyn trajectory table with `cell_id`, `time`,
`condition`, `signal`, and `replicate`. When the feature table includes
`sequence`, RhoDyn keeps same-numbered labels from different sequences separate.
For example, track `1` in sequence `00` becomes `sequence_00_track_1`, while
track `1` in sequence `01` becomes `sequence_01_track_1`. The supplied replicate
label is also split by sequence, such as `zenodo_7260137_sequence_00`, so grouped
uncertainty can avoid pooling distinct public sequences as a single replicate.

Example using the real public feature subset.

```bash
python -m rhodyn.cli ctc-to-trajectory \
  case_studies/mlci_public_track_features_subset.csv \
  --signal intensity \
  --condition mlci_public_segmentation_features \
  --replicate zenodo_7260137 \
  --output mlci_public_intensity_trajectory.csv
```

Use `--signal speed` to convert centroid movement into a trajectory table, or
`--signal area` to analyze mask size directly. The `intensity` signal is the
mean raw image intensity under each tracking-mask label.

Do not pass the bundled `mlci_public_man_track_subset.txt` lineage file for the
multi-sequence feature table. That fallback lineage subset covers sequence `00`
only. Lineage validation should be used only with a matching sequence-specific
lineage table or a future merged lineage table that carries sequence identity.

## Convert lineage intervals when mask features are not available

If centroid or intensity features have not yet been extracted, the CTC lineage
table can still demonstrate a lighter public-data path. This conversion derives
trajectory signals from track intervals rather than from object geometry or
image intensity.

```bash
python -m rhodyn.cli ctc-lineage-to-trajectory \
  case_studies/mlci_public_man_track_subset.txt \
  --signal normalized_track_age \
  --condition mlci_public_lineage_subset \
  --replicate zenodo_7260137 \
  --max-tracks 10 \
  --output mlci_public_lineage_trajectory.csv
```

Supported lineage signals are `presence`, `track_age`,
`normalized_track_age`, and `duration`. These are useful for testing grouping,
residence, sensitivity, uncertainty, and plotting when masks are unavailable.
They do not replace centroid, intensity, or morphology features for biological
interpretation.

## Score residence

After conversion, residence scoring uses the same API as any other trajectory
table.

```bash
python -m rhodyn.cli score-residence mlci_public_intensity_trajectory.csv \
  --low 13.0 \
  --high 14.5
```

For the real public benchmark, the residence window is an analysis choice over
the selected signal. It should not be presented as a measured biological
threshold unless supported by an external calibration.

## Run sensitivity

Residence-window sensitivity asks whether the qualitative result depends on a
narrowly chosen window.

```bash
python -m rhodyn.cli sensitivity mlci_public_intensity_trajectory.csv \
  --low-min 12.8 \
  --low-max 13.2 \
  --high-min 14.2 \
  --high-max 14.6 \
  --steps 4 \
  --min-residence-fraction 0.25
```

This produces typed sensitivity-curve outputs with the low/high window,
residence fraction, residence time, amplitude summaries, and qualifying-window
counts for each track.

## Add uncertainty

For a tutorial-level uncertainty summary, compute residence fractions per track
and bootstrap the mean. If biological replicate labels are available, pass those
labels to `bootstrap_interval` so uncertainty is estimated at the declared
grouping level rather than at an inflated row level.

```python
from rhodyn.residence import ResidenceWindow, score_records
from rhodyn.schema import read_trajectory_csv
from rhodyn.uncertainty import bootstrap_interval

rows, issues = read_trajectory_csv("mlci_public_intensity_trajectory.csv")
if issues:
    raise ValueError(issues)
summaries = score_records(rows, ResidenceWindow(low=13.0, high=14.5))
interval = bootstrap_interval(
    [summary.residence_fraction for summary in summaries],
    n_resamples=1000,
    seed=13,
)
```

## Generate diagnostic plots

Plotting remains optional through `rhodyn[plots]`. The plot helper returns a
figure and axis without displaying anything.

```python
from rhodyn.plots import plot_residence_trace
from rhodyn.residence import ResidenceWindow

first_track = [row for row in rows if row.cell_id == rows[0].cell_id]
fig, ax = plot_residence_trace(first_track, ResidenceWindow(low=13.0, high=14.5))
fig.savefig("mlci_residence_trace.png", dpi=200)
```

## Runnable fixture workflow

The repository includes a tiny CTC-style fixture to validate the adapter and
analysis path.

```bash
python examples/mlci_public_case_study_workflow.py
```

The same script also analyzes the small public segmentation-derived feature
subset, which demonstrates RhoDyn's public-data path on real benchmark
centroids, mask areas, and mean raw intensities. Biological interpretation
remains limited until the selected signal, residence window, grouping
structure, and uncertainty rule are declared for a specific scientific question.

## Relation to the manuscript

The manuscript motivated RhoDyn by showing why residence time, reserve,
bounded-coupling decisions, and model comparison are useful for live-cell
biology. This tutorial uses that logic as inspiration only. The microbial
tracking benchmark is a separate public case study and should not be interpreted
as evidence for the manuscript's microglial RhoA/Src/reserve biology.

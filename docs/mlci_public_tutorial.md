# v0.3.0 public tutorial lane

This tutorial starts the first public-data case study for RhoDyn using the
Tracking one-in-a-million microbial single-cell tracking benchmark. The public
benchmark is a live-cell tracking dataset distributed through Zenodo in Cell
Tracking Challenge format. RhoDyn does not read raw videos or segmentation masks
directly in v0.3.0. Instead, it consumes a pre-extracted track-feature table and
converts it into the standard trajectory schema used by the residence,
sensitivity, uncertainty, and plotting layers.

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
| `track_id` | CTC object or track label |
| `frame` | frame index |
| `x` | centroid x coordinate |
| `y` | centroid y coordinate |
| `area` | object area or mask size |
| `intensity` | optional object intensity summary |

If available, keep the CTC `man_track.txt` file beside the feature table. RhoDyn
uses it to check that feature frames fall within the lineage interval declared
for each track.

The repository also includes a small real public subset from the benchmark
lineage file at `case_studies/mlci_public_man_track_subset.txt`. This subset was
extracted from `00_GT/TRA/man_track.txt` inside the Zenodo `ctc_format.zip`
archive. It can be used immediately to exercise the public-data path without
downloading the multi-GB archive.

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
`condition`, `signal`, and `replicate`.

## Convert lineage intervals when mask features are not available

If centroid or intensity features have not yet been extracted, the CTC lineage
table can still demonstrate the public-data path. This conversion derives
trajectory signals from track intervals rather than from object geometry.

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
`normalized_track_age`, and `duration`. These are useful for proving the
public-data workflow and testing grouping, residence, sensitivity, uncertainty,
and plotting. They do not replace centroid, intensity, or morphology features
for biological interpretation.

## Score residence

After conversion, residence scoring uses the same API as any other trajectory
table.

```bash
python -m rhodyn.cli score-residence mlci_public_lineage_trajectory.csv \
  --low 0.25 \
  --high 0.75
```

For the real public benchmark, the residence window should be declared as an
analysis choice before interpretation. It should not be presented as a measured
biological threshold unless supported by an external calibration.

## Run sensitivity

Residence-window sensitivity asks whether the qualitative result depends on a
narrowly chosen window.

```bash
python -m rhodyn.cli sensitivity mlci_public_lineage_trajectory.csv \
  --low-min 0.2 \
  --low-max 0.3 \
  --high-min 0.7 \
  --high-max 0.8 \
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

rows, issues = read_trajectory_csv("mlci_public_lineage_trajectory.csv")
if issues:
    raise ValueError(issues)
summaries = score_records(rows, ResidenceWindow(low=0.25, high=0.75))
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
fig, ax = plot_residence_trace(first_track, ResidenceWindow(low=0.25, high=0.75))
fig.savefig("mlci_residence_trace.png", dpi=200)
```

## Runnable fixture workflow

The repository includes a tiny CTC-style fixture to validate the adapter and
analysis path.

```bash
python examples/mlci_public_case_study_workflow.py
```

This fixture is not a biological result from the public benchmark. It is a
schema and workflow check. The same script also analyzes the small public
lineage subset, which demonstrates RhoDyn's public-data path on real benchmark
track intervals. Biological interpretation remains limited until centroid,
intensity, or morphology features are extracted from the Zenodo masks or videos
and analyzed with a declared signal, residence window, grouping structure, and
uncertainty rule.

## Relation to the manuscript

The manuscript motivated RhoDyn by showing why residence time, reserve,
bounded-coupling decisions, and model comparison are useful for live-cell
biology. This tutorial uses that logic as inspiration only. The microbial
tracking benchmark is a separate public case study and should not be interpreted
as evidence for the manuscript's microglial RhoA/Src/reserve biology.

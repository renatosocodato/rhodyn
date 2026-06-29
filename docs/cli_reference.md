# CLI reference

The `rhodyn` command exposes the same core operations as the Python library and
the Stage 4 backend. Commands print JSON to standard output unless an explicit
output file is requested.

## Validate a table

```bash
rhodyn validate examples/synthetic_trajectory.csv
rhodyn validate examples/synthetic_endpoints.csv --kind endpoint
rhodyn validate examples/synthetic_reserve.csv --kind reserve
rhodyn validate examples/synthetic_coupling.csv --kind coupling
```

Use `--signal-column` when a trajectory table stores the measured signal under
a non-default column name.

## Score residence

```bash
rhodyn score-residence examples/synthetic_trajectory.csv --low 0.35 --high 0.75
```

This groups rows by condition and cell, then reports residence fraction, dwell
time, total time, amplitude summaries, and dwell segments for each trajectory.

## Run residence-window sensitivity

```bash
rhodyn sensitivity examples/synthetic_trajectory.csv \
  --low-min 0.20 --low-max 0.45 \
  --high-min 0.65 --high-max 0.90 \
  --steps 4 --min-residence-fraction 0.25
```

The sensitivity command declares a grid of low/high windows and reports how
residence summaries change across that grid.

## Decide bounded coupling

```bash
rhodyn decide-coupling examples/synthetic_coupling.csv
```

The input table supplies estimate, interval, margin, and optional ROPE mass.
The command reports whether the supplied interval is contained inside the
declared margin and, when present, whether ROPE mass clears the threshold.

## Summarize reserve-like responses

```bash
rhodyn summarize-reserve examples/synthetic_reserve.csv \
  --floor 1.0 --ceiling 1.7 --baseline-points 1
```

By default, the command normalizes each sample to `F/F0` before mapping the
peak response to the reserve coordinate. Use `--no-normalize` only when the
input response is already on the desired scale.

## Compare reduced architectures

```bash
rhodyn compare examples/synthetic_endpoints.csv --parameters 1
```

The command ranks model names by BIC and residual sum of squares. The endpoint
rows define the model alternatives and observed-versus-predicted values.

## Export a compact Markdown report

```bash
rhodyn export-markdown examples/synthetic_coupling.csv --title "RhoDyn report"
```

This is a lightweight report surface for tabular outputs, not a manuscript
figure generator.

## Run a minimal controller simulation

```bash
rhodyn simulate --duration 20 --dt 0.5
```

The simulation command exposes the deterministic controller used by the Stage 5
workbench for parameter exploration. It does not fit data.

## Convert CTC-style public tracking tables

```bash
rhodyn ctc-to-trajectory examples/mlci_ctc_features.csv \
  --lineage examples/mlci_man_track.txt \
  --signal speed \
  --condition mlci_tracking \
  --replicate schema_fixture \
  --output mlci_speed_trajectory.csv
```

`ctc-lineage-to-trajectory` can also convert a lineage table directly to a
trajectory-like table for tutorial use.

## Inspect optional manuscript case-study metadata

```bash
rhodyn paper-case-study
rhodyn paper-case-study --data-root examples
```

The manuscript repository and Zenodo data package are optional reference inputs
for future examples. They are not required for normal RhoDyn use.

## Inspect optional dependency groups

```bash
rhodyn extras
```

This reports optional extras for table handling, statistics, plots, backend
service deployment, notebooks, and release development.

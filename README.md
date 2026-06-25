# RhoDyn

Dynamic residence-state analysis for live-cell signaling and perturbation data.

RhoDyn is a standalone Python toolkit for asking whether live-cell trajectories
and perturbation endpoints are better described by signal amplitude, residence
time, pathway coupling, reserve-like buffering, or routed output structure.

The project was motivated by the RhoA residence-control framework developed in
the `windowed_rhoA_model` manuscript repository, but it is independent from that
manuscript. The manuscript was not generated with RhoDyn. The paper repository
and Zenodo data package are treated only as an optional reference case study for
future examples.

## Current status

This is an early open-core scaffold moving into the `v0.3.x` public
case-study lane.

Included now:

- tidy live-cell trajectory validation;
- Cell Tracking Challenge-style feature-table conversion for the first public
  microbial tracking tutorial;
- selected CTC TIFF-mask feature extraction for centroid, area, and mean
  intensity rows without retaining raw images;
- residence-window scoring;
- amplitude and dwell-time summaries;
- reserve-style normalization helpers;
- bounded-equivalence decision helpers from supplied intervals or posterior
  samples and raw arrays;
- bootstrap and permutation uncertainty helpers;
- residence-window sensitivity curves;
- optional diagnostic plots;
- simple deterministic controller simulation;
- stochastic first-passage utilities;
- reduced-model comparison helpers;
- a CLI;
- synthetic examples;
- a documented paper-data adapter stub;
- a public-data candidate matrix and MLCI tutorial scaffold.

Not included yet:

- image segmentation;
- general raw microscopy ingestion beyond the selected CTC TIFF path;
- manuscript-specific figure generation;
- disease-state prediction;
- a graphical dashboard.

## Install for development

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -e .
python -m unittest discover tests
```

The package currently uses only the Python standard library.

Optional scientific-computing extras are declared for future table, statistics,
plotting, and notebook workflows.

```bash
python -m pip install 'rhodyn[pandas]'
python -m pip install 'rhodyn[stats]'
python -m pip install 'rhodyn[plots]'
python -m pip install 'rhodyn[notebooks]'
```

## Quick examples

Validate a synthetic live-cell trajectory table.

```bash
rhodyn validate examples/synthetic_trajectory.csv
```

Score residence in a signaling window.

```bash
rhodyn score-residence examples/synthetic_trajectory.csv --low 0.35 --high 0.75
```

Convert a CTC-style microbial tracking feature table into a RhoDyn trajectory
table.

```bash
rhodyn ctc-to-trajectory examples/mlci_ctc_features.csv \
  --lineage examples/mlci_man_track.txt \
  --signal speed \
  --condition mlci_tracking \
  --replicate schema_fixture \
  --output mlci_speed_trajectory.csv
```

Run the public case-study workflow scaffold.

```bash
PYTHONPATH=src python examples/mlci_public_case_study_workflow.py
```

Regenerate the small public feature subset without keeping raw image files.

```bash
python scripts/fetch_mlci_feature_subset.py \
  --lineage-filter case_studies/mlci_public_man_track_subset.txt \
  --output case_studies/mlci_public_track_features_subset.csv \
  --provenance case_studies/mlci_public_track_features_subset.provenance.json
```

Run a minimal controller simulation.

```bash
rhodyn simulate --duration 20 --dt 0.5
```

Compare reduced model predictions from a tidy endpoint table.

```bash
rhodyn compare examples/synthetic_endpoints.csv
```

Run the dependency-free synthetic walkthrough.

```bash
PYTHONPATH=src python examples/residence_reserve_workflow.py
```

Print the optional manuscript case-study metadata.

```bash
rhodyn paper-case-study
```

Inspect a local release-like table root and map discovered CSVs to RhoDyn roles.

```bash
rhodyn paper-case-study --data-root examples
```

Inspect optional dependency groups.

```bash
rhodyn extras
```

The v0.3.x public tutorial scaffold is documented in
`docs/mlci_public_tutorial.md`. The included CTC-style fixture validates the
adapter, and the small public feature subset demonstrates centroid, area, and
mean-intensity ingestion from the Zenodo MLCI benchmark. Biological
interpretation requires a declared signal, residence window, grouping
structure, and uncertainty rule.

## Input schemas

RhoDyn accepts tidy CSV inputs. Required columns must be present and non-empty
where they identify a biological grouping or comparison. Optional columns can be
omitted without failing validation.

Trajectory tables describe live-cell signaling traces.

| column | meaning |
| --- | --- |
| `cell_id` | required cell or trace identifier |
| `time` | required non-negative time coordinate |
| `condition` | treatment, genotype, or perturbation group |
| `signal` | measured signaling value |
| `replicate` | optional replicate, field, well, or experiment identifier |

Endpoint-comparison tables describe observed-versus-predicted model outputs.

| column | meaning |
| --- | --- |
| `model` | required model or architecture name |
| `endpoint` | required measured endpoint |
| `observed` | observed value |
| `predicted` | model-predicted value |
| `weight` | optional endpoint weight, defaulting to `1.0` |

Reserve tables describe calcium, viability, or other reserve-like response
coordinates.

| column | meaning |
| --- | --- |
| `sample_id` | required cell, field, well, or sample identifier |
| `time` | required non-negative time coordinate |
| `condition` | treatment, genotype, or perturbation group |
| `response` | measured reserve-like response |
| `replicate` | optional replicate, field, well, or experiment identifier |

Coupling tables describe bounded-coupling interval or ROPE summaries supplied
by the user.

| column | meaning |
| --- | --- |
| `contrast` | required perturbation or condition contrast |
| `estimate` | contrast estimate |
| `ci_low` | lower confidence or credible interval bound |
| `ci_high` | upper confidence or credible interval bound |
| `margin` | positive declared equivalence or biological-negligibility margin |
| `rope_mass` | optional posterior mass inside the margin |

## Relationship to the RhoA manuscript

The reference manuscript reproducibility repository is:

`https://github.com/renatosocodato/windowed_rhoA_model`

Reference release commit:

`e63cc93a4b23d8b3d27cf25136b00d53fa6144f4`

Software archive DOI:

`10.5281/zenodo.19796404`

Data and replication package DOI:

`10.5281/zenodo.19796406`

RhoDyn may later include tutorials that use those public release artifacts as a
case study. That does not make RhoDyn part of the manuscript analysis pipeline.

## Scientific boundaries

RhoDyn tests whether supplied readouts are compatible with particular dynamic
controller descriptions. It does not infer a molecular mechanism by itself, and
it does not convert fitted parameters into literal biochemical edges without
external evidence.

Useful interpretations include:

- residence-compatible versus amplitude-compatible behavior;
- bounded immediate coupling under a declared equivalence margin;
- reserve-like buffering summaries;
- model classes that fail to reproduce supplied endpoint constraints.

Unsupported interpretations include:

- clinical prediction;
- universal microglial fate classification;
- proof of causal molecular mechanism from model fit alone;
- direct injury measurement from a model-derived burden coordinate.

## License

Apache License 2.0. See `LICENSE`.

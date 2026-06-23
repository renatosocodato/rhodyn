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

This is an early open-core scaffold for `v0.1.0`.

Included now:

- tidy live-cell trajectory validation;
- residence-window scoring;
- amplitude and dwell-time summaries;
- reserve-style normalization helpers;
- bounded-equivalence decision helpers from supplied intervals or posterior
  samples;
- simple deterministic controller simulation;
- stochastic first-passage utilities;
- reduced-model comparison helpers;
- a CLI;
- synthetic examples;
- a documented paper-data adapter stub.

Not included yet:

- image segmentation;
- raw microscopy ingestion;
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

## Quick examples

Validate a synthetic live-cell trajectory table.

```bash
rhodyn validate examples/synthetic_trajectory.csv
```

Score residence in a signaling window.

```bash
rhodyn score-residence examples/synthetic_trajectory.csv --low 0.35 --high 0.75
```

Run a minimal controller simulation.

```bash
rhodyn simulate --duration 20 --dt 0.5
```

Compare reduced model predictions from a tidy endpoint table.

```bash
rhodyn compare examples/synthetic_endpoints.csv
```

Print the optional manuscript case-study metadata.

```bash
rhodyn paper-case-study
```

## Input schema

Trajectory tables are expected to be tidy CSV files with at least:

| column | meaning |
| --- | --- |
| `cell_id` | cell or trace identifier |
| `time` | time coordinate |
| `condition` | treatment, genotype, or perturbation group |
| `signal` | measured signaling value |

Endpoint-comparison tables are expected to contain:

| column | meaning |
| --- | --- |
| `model` | model or architecture name |
| `endpoint` | measured endpoint |
| `observed` | observed value |
| `predicted` | model-predicted value |

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


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

This is an early open-core scaffold at the end of the `v0.3.x` public
case-study lane.

The staged development plan is anchored in `docs/roadmap.md`. The current
position is Stage 3D completed and the Stage 3 evidence bank is closable for
v0.3. Backend, frontend, official release, Nature Methods, and product work
remain downstream of this evidence bank.

Included now:

- tidy live-cell trajectory validation;
- Cell Tracking Challenge-style feature-table conversion for the first public
  microbial tracking tutorial;
- selected CTC TIFF-mask feature extraction for centroid, area, and mean
  intensity rows without retaining raw images;
- a multi-sequence public MLCI feature subset sampled from sequences `00` and
  `01`, with sequence-aware track identities and per-sequence replicate labels;
- a first independent public calcium-signaling benchmark comparing amplitude
  and high-calcium residence in DRG neuron traces;
- a second independent public kinase-signaling benchmark comparing peak ERK
  KTR activity and high-ERK residence in GPCR-stimulated cells;
- a first public perturbation endpoint/model-comparison benchmark using Cell
  Painting morphology profiles and MitoTox endpoints;
- a public bounded-coupling benchmark comparing ERK and Akt residence
  summaries in paired GPCR-stimulated cells;
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
- the first Stage 4 stateless backend service core and FastAPI app for schema
  validation, residence scoring, bounded-coupling decisions, reserve summaries,
  model comparison, Markdown report export, and downloadable analysis bundles.
- explicit durable server-side job storage for backend jobs when
  `RHODYN_JOB_STORE_DIR` or `create_app(job_store_dir=...)` is configured.
- a machine-checkable Stage 3 gate report and three tutorial notebooks covering
  the synthetic primer, public signaling benchmarks, and public endpoint plus
  bounded-coupling benchmarks.

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
python -m pip install 'rhodyn[backend]'
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

Audit the Stage 3 public case-study bank.

```bash
python scripts/audit_stage3_case_study_bank.py
```

Regenerate the small public feature subset without keeping raw image files.

```bash
python scripts/fetch_mlci_feature_subset.py \
  --sequences 00,01 \
  --frames 0:140:20 \
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

Run the Stage 4 backend after installing the backend extra.

```bash
uvicorn rhodyn.backend:app --reload
```

Run the backend with explicit durable job storage.

```bash
RHODYN_JOB_STORE_DIR=.rhodyn_jobs uvicorn rhodyn.backend:app --reload
```

The v0.3.x public tutorial scaffold is documented in
`docs/mlci_public_tutorial.md`. The included CTC-style fixture validates the
adapter, and the small public feature subset demonstrates centroid, area, and
mean-intensity ingestion from two Zenodo MLCI benchmark sequences. Sequence
identity is preserved in trajectory `cell_id` values and replicate labels, so
same-numbered CTC track labels from different sequences are not merged.
Biological interpretation requires a declared signal, residence window,
grouping structure, and uncertainty rule.

For code that needs to predict the converted identifiers before building a
trajectory table, `ctc_track_cell_id("1", sequence="00")` returns
`sequence_00_track_1`, and `ctc_sequence_replicate("zenodo_7260137",
sequence="00")` returns `zenodo_7260137_sequence_00`.

The first Stage 3A signaling benchmark is documented in
`docs/drg_calcium_public_benchmark.md`. It uses public DRG calcium traces from
Zenodo DOI `10.5281/zenodo.14907827` to compare maximum amplitude with
high-calcium residence. The retained derived table contains 360 episode-cell
rows and includes both amplitude-only and residence-only top-quartile cases.

The Stage 3B kinase-signaling benchmark is documented in
`docs/erk_gpcr_public_benchmark.md`. It uses public ERK KTR source data from
Zenodo DOI `10.5281/zenodo.5836623` to compare maximum ERK signal with
high-ERK residence. The retained derived table contains 180 single-cell
trajectory summaries and includes both amplitude-only and residence-only
top-quartile cases.

The Stage 3C endpoint/model-comparison benchmark is documented in
`docs/cell_painting_endpoint_benchmark.md`. It uses public Cell Painting and
MitoTox endpoint tables from Zenodo DOI `10.5281/zenodo.10011861` to compare
endpoint prevalence, one-dimensional morphology, single-compartment morphology,
and routed compartment architectures. The retained ranking shows that the
three-coordinate compartment-route architecture fits the endpoint table better
than the reduced alternatives under endpoint-balanced residuals.

The Stage 3D bounded-coupling benchmark is documented in
`docs/erk_akt_bounded_coupling_benchmark.md`. It uses the same public Wan 2021
ERK/GPCR source-data archive to compare paired ERK and Akt high-state residence
within cells. The UK context falls inside the declared bounded-coupling margin,
while S1P and histamine do not, so the interpretation is context-limited rather
than a broad ERK/Akt equivalence claim. Margin and threshold sensitivity outputs
are retained to show that UK is not dependent on a single high-state threshold
or only the widest tested margin.

The Stage 4 backend start is documented in `docs/stage4_backend.md`. It exposes
the frozen Stage 3 operations through FastAPI while preserving the Python
library as the source of analysis behavior. The job-bundle endpoint returns a
ZIP archive with submitted rows, parameters, exact result JSON, summary rows,
Markdown report, manifest, and SHA-256 checksums. Durable job storage is
available only when a job-store directory is explicitly configured, so uploaded
tables are not silently written to disk by default.

The Stage 3 bank is summarized in `docs/stage3_case_study_bank.md` and audited
by `case_studies/stage3_case_study_bank_gate_report.json`. Three lightweight
tutorial notebooks live under `notebooks/` and use retained derived tables
rather than raw public archives.

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

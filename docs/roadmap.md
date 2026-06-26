# RhoDyn roadmap

This roadmap is the project anchor after the v0.2.0 core-methods pass and the
v0.3.x public-data adapter pass. It preserves the original staged plan while
making the current position explicit, so future work does not drift into a
different product, manuscript, or branding direction.

## Current position

RhoDyn has completed the v0.3 Stage 3 evidence-bank build. The core Python API,
CLI, synthetic examples, uncertainty helpers, bounded-coupling helpers,
residence-window sensitivity, reduced-model comparison, plotting helpers, the
first public CTC-style adapter, two independent public signaling benchmarks, one
public endpoint/model-comparison benchmark, and one public bounded-coupling
benchmark are in place. The multi-sequence public MLCI example demonstrates
public-data ingestion and sequence-aware grouping, the DRG calcium benchmark
demonstrates a residence-versus-amplitude comparison in neuronal calcium
traces, the ERK GPCR benchmark demonstrates the same distinction in
kinase-reporter dynamics, the Cell Painting/MitoTox endpoint benchmark adds a
public reduced-architecture comparison case, and the ERK/Akt residence
benchmark adds a context-limited public bounded-coupling case.

Current status in one sentence. RhoDyn can analyze declared dynamic readouts and
the v0.3 Stage 3 evidence bank is closable, with two public signaling systems,
one public endpoint/model-comparison case, and one public bounded-coupling
case.

## Non-drift principles

- RhoDyn is a general method for dynamic operating-state analysis in live-cell
  perturbation biology.
- RhoDyn is not a rebranded reproduction pipeline for the RhoA/microglia paper.
- The RhoA/microglia manuscript remains a reference use case and biological
  depth example, not the source of the software's generality claim.
- Public examples must teach what residence, buffering, bounded coupling, or
  routed outputs reveal beyond amplitude-only summaries.
- Product and interface work should not outrun the evidence bank.
- Nature Methods remains the first high-impact scientific-methods target once
  the evidence gate is met.

## Stage 3. Case-study evidence bank

Goal. Show generality without tying the software to one paper.

Case-study ladder.

1. Synthetic examples that teach the method.
2. The RhoA/microglia manuscript as a reference use case.
3. One independent public live-cell signaling dataset, ideally ERK, NF-kB,
   calcium, Rho-family, or kinase dynamics.
4. One perturbation endpoint dataset where model comparison matters.

Deliverables.

- Tutorial notebooks.
- Reproducible case-study folders.
- Public-data adapters.
- Benchmark tables.
- A clear summary of what RhoDyn finds that amplitude-only summaries miss.

Gate.

- At least two biological systems show a residence/amplitude distinction.
- At least one case shows bounded coupling or reserve logic.
- Examples do not imply RhoDyn generated the original manuscript results.

Current evidence.

- Synthetic examples exist and exercise residence, reserve-like behavior,
  coupling decisions, uncertainty, sensitivity, and model comparison.
- The RhoA/microglia manuscript is represented as an optional reference case
  study through metadata and local table discovery.
- The public MLCI/CTC adapter exists and preserves multi-sequence track identity.
  This is useful as public-data infrastructure, but it is a microbial tracking
  demonstration rather than an ideal live-cell signaling benchmark.
- A first independent calcium-signaling benchmark is in place using public DRG
  deltaF/F0 traces from von Buchholtz 2025. The retained derived table contains
  360 episode-cell rows from 120 neurons and identifies both amplitude-only and
  residence-only top-quartile cases under a declared high-calcium window.
- A second independent kinase-signaling benchmark is in place using public ERK
  KTR traces from Wan et al. 2021. The retained derived table contains 180
  single-cell trajectory summaries from histamine, S1P, and UK ligand contexts
  and identifies both amplitude-only and residence-only top-quartile cases
  under a declared high-ERK quantile threshold.
- A public perturbation endpoint/model-comparison benchmark is in place using
  Cell Painting and MitoTox endpoint tables from Seal et al. 2023. The retained
  model-ranking table compares endpoint prevalence, one-dimensional morphology,
  single-compartment morphology, and routed compartment architectures. The
  routed compartment model is best by BIC and endpoint-balanced weighted RMSE.
- A public bounded-coupling benchmark is in place using paired ERK and Akt KTR
  trajectories from Wan et al. 2021. The retained derived tables contain 180
  paired single-cell summaries from histamine, S1P, and UK ligand contexts. The
  UK ERK-minus-Akt residence contrast falls inside a declared +/-0.20
  residence-fraction margin, while S1P and histamine do not. The mixed
  all-ligand summary also falls inside the margin but is treated only as a
  summary check because it combines ligand-specific directional effects.
- Stage 3D hardening adds margin sensitivity, threshold sensitivity, and an
  explicit replicate-structure note. UK remains bounded across the tested
  0.60-0.85 high-state threshold grid and passes at margins of 0.10 and larger.
  S1P and histamine fail across the threshold grid at the primary +/-0.20
  margin.

Status. Stage 3A and Stage 3B have produced two independent public signaling
benchmarks, Stage 3C has produced a public endpoint/model-comparison benchmark,
and Stage 3D has produced a public bounded-coupling benchmark. The v0.3 Stage 3
gate is satisfied without tying the software's generality to the RhoA/microglia
manuscript.

The public MLCI adapter remains as infrastructure and tutorial proof, not as the
main biological generality claim. Stage 4 backend work can begin from the
stable Stage 3 surfaces, provided backend results match the Python library
outputs exactly. Additional NF-kB, ERK perturbation, reserve-like, or
multi-reporter public datasets should be treated as Stage 7 evidence-expansion
routes rather than prerequisites for starting the backend.

## Stage 4. Backend

Goal. Make RhoDyn executable as a service.

Backend architecture.

- FastAPI service around the stable Python API.
- Job model for uploaded tables.
- Schema validation endpoint.
- Residence scoring endpoint.
- Coupling/equivalence endpoint.
- Reserve endpoint.
- Reduced-architecture comparison endpoint.
- Report export endpoint.

Outputs.

- JSON.
- CSV.
- Markdown.
- Figure-ready SVG/PNG.
- Downloadable analysis bundle.

Gate.

- Every backend result matches the Python library output exactly.
- No hidden state.
- Jobs preserve input schema, parameter choices, and software version.

Status. Started. The first backend service core and FastAPI app expose schema
validation, residence scoring, bounded-coupling decisions, reserve summaries,
endpoint-model comparison, and Markdown report export while delegating to the
same Python library functions used by the CLI. The next backend increment
should add durable job packaging only if it preserves exact library-output
agreement and records input schema, parameter choices, and software version.

## Stage 5. Frontend

Goal. Build a serious scientific workbench.

Core screens.

- Project dashboard.
- Data upload and schema validation.
- Trajectory explorer.
- Residence-window tuner.
- Coupling/equivalence decision panel.
- Reserve-buffering panel.
- Model-comparison panel.
- Report builder.

Design.

- Dense but calm scientific UI.
- No marketing hero as the app entry point.
- Plots first, explanations second.
- Strong export pathway for figures and reports.

Gate.

- A biologist can upload a tidy table and understand whether the signal is
  amplitude-like or residence-like without reading code.
- A quantitative user can inspect every parameter and reproduce the result from
  CLI.

Status. Not started. Frontend work should follow a backend/API contract and
should not replace the Stage 3 evidence bank.

## Stage 6. Official software release

Goal. Make RhoDyn professionally citable.

Release surfaces.

- GitHub public or controlled-release repository.
- PyPI package.
- Docker image.
- Zenodo DOI for RhoDyn itself.
- Documentation site.
- API reference.
- Tutorials.
- Changelog.
- Citation file.
- Reproducibility card.
- CI across supported Python versions.

Gate.

- Wheel and source distribution install cleanly.
- Docs build cleanly.
- Examples run from scratch.
- Release archive contains no private data, manuscript-private files, raw
  microscopy, or local paths.

Status. Partly prepared, not complete. The repository has CI, docs, examples,
and release checks, but it is not yet a professional public/citable release with
PyPI, Docker, Zenodo, documentation site, citation metadata, and cross-version
CI.

## Stage 7. Nature Methods first

Goal. Build the main scientific-methods campaign.

Nature Methods framing.

RhoDyn is a computational method for detecting dynamic control regimes in
live-cell perturbation biology, where cell state depends on dwell time,
buffering, and routed output structure rather than endpoint amplitude.

The Nature Methods paper should not be software for the RhoA paper. The core
paper-level claim should be:

Residence-state inference reveals hidden dynamic control variables in live-cell
perturbation data.

Required evidence.

- Formal method definition.
- Clear mathematical model.
- Benchmark against amplitude-only, endpoint-only, threshold-only, and generic
  time-series summaries.
- Multiple biological systems.
- Robust uncertainty handling.
- Practical software implementation.
- Usability proof through tutorials and GUI or hosted demo.
- Strong limitations section.

Figure plan.

1. Method concept and workflow.
2. Synthetic benchmarking across known regimes.
3. Public live-cell signaling benchmark.
4. RhoA/microglia case study as biological depth.
5. Cross-system generalization.
6. Software workbench and reproducibility architecture.

Primary target. Nature Methods.

Strong pivots.

- Nature Biotechnology, if the product/workbench becomes broadly enabling.
- Nature Computational Science, if the computational method dominates.
- Cell Systems, if the dynamic systems biology story is strongest.
- Science Advances, if generality is broad but method novelty is less
  platform-level.
- PLOS Computational Biology or Bioinformatics Advances as safer
  software-methods venues.
- JOSS only for software credit, not as the main high-impact target.

Gate.

Do not submit until RhoDyn has at least two independent biological
demonstrations beyond the original manuscript logic.

Status. Not ready. The v0.3 evidence bank now supports method development, but
Nature Methods readiness still requires a broader formal methods campaign and
at least two independent biological demonstrations beyond the original
manuscript logic.

## Stage 8. Product and commercial alignment

Goal. Let product development inherit the Nature Methods framing.

Open-core.

- Python library.
- CLI.
- Core statistics.
- Synthetic examples.
- Public adapters.
- Basic reports.

Paid/pro.

- Hosted workbench.
- Team projects.
- Private datasets.
- Batch jobs.
- Rich dashboards.
- Regulated export logs.
- Microscopy/plate-reader adapters.
- Custom enterprise deployments.
- Collaboration and review tools.

Customer targets.

- Academic live-cell imaging labs.
- Pharma perturbation biology groups.
- Biotech imaging and screening teams.
- Systems biology cores.
- Neuroinflammation and immunology groups.

Commercial thesis.

Many labs collect time-lapse signaling data but reduce it to endpoints. RhoDyn
sells the missing layer, dynamic operating-state interpretation.

Status. Conceptual only. Commercial buildout should not lead the scientific
evidence path. Stage 8 inherits from Stage 7, and Stage 7 depends on Stage 3.

## Immediate next path

The next scientifically aligned move is Stage 4 backend work.

1. Freeze the v0.3 Stage 3 evidence bank as the reference public case-study
   surface.
2. Build a FastAPI service around the stable Python API, beginning with schema
   validation, residence scoring, bounded-coupling decisions, reserve summaries,
   and reduced-architecture comparison.
3. Require every backend result to match the Python library output exactly and
   preserve input schema, parameter choices, and software version in the job
   record.

Frontend, official release, Nature Methods, and product work should remain
downstream of this service contract rather than replacing it.

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
benchmark adds a context-limited public bounded-coupling case. The Stage 4
API contract is now frozen for a first Stage 5 frontend scaffold.

Current status in one sentence. RhoDyn can analyze declared dynamic readouts,
the v0.3 Stage 3 evidence bank is closable, the Stage 4 API contract is
frozen, and Stage 5 has started as a contract-bound frontend scaffold.

## Execution memory

This file is the roadmap memory for RhoDyn. When a future change modifies
scope, evidence, backend behavior, release posture, Nature Methods strategy, or
commercial positioning, it must be mapped to one of the stages below before it
is treated as project-direction work. The original Stage 3 to Stage 8 blueprint
is retained as the controlling sequence, not as loose inspiration.
The compact machine-readable companion is
`docs/roadmap_execution_memory.json`.

Current position after the v0.2.0 core-methods pass and v0.3.x public-data
passes.

1. Stage 3 is satisfied for the current evidence-bank gate and should be
   frozen unless a documented defect in the evidence bank is found.
2. Stage 4 is frozen for the first Stage 5 scaffold. The committed OpenAPI
   schema, frontend contract, fixtures, and closeout document are now the
   frontend dependency.
3. Stage 5 is the active execution stage. Work here is frontend behavior around
   the frozen Stage 4 contract, uploaded-table jobs, reproducible exports, and
   parameter inspection.
4. Stage 6 is preparatory only until PyPI, Docker, Zenodo, docs, citation
   metadata, release hygiene, and cross-version CI all pass together.
5. Stage 7 is the future Nature Methods-first scientific-methods campaign. It
   is not a rebranding of the RhoA/microglia manuscript and not a replacement
   for Stage 3.
6. Stage 8 inherits from Stage 7. Product strategy should not lead or reshape
   the evidence path.

Decision rule for new work. If a proposed task adds another public biological
system, it is Stage 7 evidence expansion unless it fixes a Stage 3 defect. If a
task adds service routes, storage, authentication, upload handling, or export
bundles, it is Stage 4. If a task adds visual screens or user interaction, it is
Stage 5. If a task adds packaging, DOI, distribution, or public citation
surfaces, it is Stage 6. If a task changes commercial packaging, pricing,
deployment, or team features, it is Stage 8 and must remain downstream of the
Nature Methods method frame.

## Roadmap lock

This section binds the original Stage 3 to Stage 8 blueprint to the current
execution state. New work should map to one of these stages before it is treated
as roadmap work.

| stage | current state | binding rule |
| --- | --- | --- |
| Stage 3. Case-study evidence bank | Complete for the v0.3 gate. | Keep the evidence bank stable. Additional public biological systems are Stage 7 evidence expansion unless they repair a documented Stage 3 defect. |
| Stage 4. Backend | Frozen for Stage 5. | Reopen only for documented API-contract defects. The OpenAPI schema, frontend contract, fixtures, and closeout document are the Stage 5 dependency. |
| Stage 5. Frontend | Active scaffold. | Build only frontend behavior that consumes the frozen Stage 4 contract and preserves parameter inspection plus CLI reproducibility. |
| Stage 6. Official software release | Partly prepared. | Do not call the package professionally citable until PyPI, Docker, Zenodo, docs, citation metadata, CI, and release hygiene are complete. |
| Stage 7. Nature Methods first | Not ready. | Treat this as a later scientific-methods campaign, not as a rebranding of the RhoA/microglia manuscript or the Stage 3 examples. |
| Stage 8. Product and commercial alignment | Conceptual only. | Product strategy inherits the Nature Methods framing and should not lead the scientific evidence path. |

## Non-drift principles

- RhoDyn is a general method for dynamic operating-state analysis in live-cell
  perturbation biology.
- RhoDyn is not a rebranded reproduction pipeline for the RhoA/microglia paper.
- The RhoA/microglia manuscript remains a reference use case and biological
  depth example, not the source of the software's generality claim.
- Public examples must teach what residence, buffering, bounded coupling, or
  routed outputs reveal beyond amplitude-only summaries.
- Product and interface work should not outrun the evidence bank.
- Stage 5 frontend work must consume the frozen Stage 4 API contract.
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
- Three lightweight tutorial notebooks now expose the synthetic primer, the
  public signaling residence-versus-amplitude benchmarks, and the public
  endpoint plus bounded-coupling benchmarks without requiring raw public
  archives.
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
- The machine-checkable Stage 3 gate report at
  `case_studies/stage3_case_study_bank_gate_report.json` records the current
  pass state for notebooks, case-study docs, public-data adapters, benchmark
  tables, the two-system residence/amplitude gate, the endpoint model-comparison
  gate, the bounded-coupling gate, and the manuscript-independence boundary.

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

Status. Frozen for Stage 5. The backend service core and FastAPI app expose
schema validation, residence scoring, bounded-coupling decisions, reserve
summaries, endpoint-model comparison, Markdown report export, upload routes,
durable jobs, and downloadable analysis bundles while delegating to the same
Python library functions used by the CLI. Bundle outputs preserve submitted
rows, parameters, exact result JSON, result rows, Markdown reports, manifests,
and SHA-256 checksums. Durable job storage remains explicit through
`RHODYN_JOB_STORE_DIR` or `create_app(job_store_dir=...)`, and retrieval returns
persisted outputs rather than re-running analysis.

The Stage 4 closeout surface now contains `api/stage4/openapi.json`,
`api/stage4/frontend_contract.json`, `api/stage4/contract_manifest.json`,
canonical fixtures under `api/stage4/fixtures/`, and `docs/stage4_closeout.md`.
Reopen Stage 4 only for a documented API-contract defect. New analysis
capabilities or additional public biological systems belong to later stages
unless they repair a documented contract failure.

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

Status. Active scaffold. The static workbench lives under `frontend/stage5/`
and loads the frozen Stage 4 contract files from `api/stage4/`. It exposes
upload, schema validation, trajectory preview, residence tuning,
coupling/equivalence, reserve, model-comparison, and report export surfaces
without adding new analysis routes. The current Stage 5 depth pass adds
per-trace residence inspection for uploaded trajectories, clearer parameter
provenance in exported bundles, and a guided MLCI public trajectory workflow
that can be reproduced from CLI. Frontend work should keep following the frozen
backend/API contract and should not replace the Stage 3 evidence bank.

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

The current roadmap should not drift away from the original Stage 3 to Stage 8
sequence.

1. Treat the v0.3 Stage 3 evidence bank and its gate report as the reference
   public case-study surface.
2. Continue Stage 5 only where frontend behavior consumes the frozen Stage 4
   contract and preserves input schema, parameter choices, software version,
   and reproducible exports.
3. For the Nature Methods trajectory, expand evidence through additional
   independent public systems only as Stage 7 method-evidence work, not as a
   rebranding of the RhoA/microglia paper or a substitute for the Stage 3 gate.

Official release, Nature Methods, and product work remain downstream of the
evidence bank, frozen service contract, and Stage 5 workbench rather than
replacing them.

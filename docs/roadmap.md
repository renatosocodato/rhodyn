# RhoDyn roadmap

This roadmap is the project anchor after the v0.2.0 core-methods pass and the
v0.3.x public-data adapter pass. It preserves the original staged plan while
making the current position explicit, so future work does not drift into a
different product, manuscript, or branding direction.

## Current position

RhoDyn is currently at the boundary between a Stage 2 foundation and a Stage 3
evidence-bank build. The core Python API, CLI, synthetic examples, uncertainty
helpers, bounded-coupling helpers, residence-window sensitivity, reduced-model
comparison, plotting helpers, and the first public CTC-style adapter are in
place. The multi-sequence public MLCI example now demonstrates public-data
ingestion and sequence-aware grouping, but it is not enough to satisfy the
Stage 3 biological generality gate.

Current status in one sentence. RhoDyn can already analyze declared dynamic
readouts, but it has not yet earned a high-impact methods claim across multiple
independent biological systems.

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
- No independent ERK, NF-kB, calcium, Rho-family, or kinase signaling benchmark
  is complete yet.
- No independent perturbation endpoint dataset has been promoted as the
  model-comparison case study yet.

Status. Stage 3 is seeded, not passed.

Next Stage 3 work should prioritize one public live-cell signaling dataset and
one perturbation endpoint/model-comparison dataset. The public MLCI adapter
should remain as infrastructure and tutorial proof, not as the main biological
generality claim.

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

Status. Not started. Backend work should wait until the Stage 3 case-study
surfaces are stable enough to define real service payloads.

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

Status. Not ready. The core methods scaffold exists, but the independent
biological demonstrations are not yet complete.

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

The next scientifically aligned move is Stage 3A.

1. Select one independent public live-cell signaling dataset with compatible
   licensing and time-resolved single-cell traces.
2. Build a minimal adapter that maps the public traces to `TrajectoryRecord`
   rows while preserving condition, replicate, cell, and time metadata.
3. Produce a benchmark table comparing residence summaries with amplitude-only
   summaries.
4. Decide whether the dataset genuinely shows a residence/amplitude distinction.

Only after Stage 3A should RhoDyn move toward backend service work. The backend
should be built around proven analysis surfaces, not speculative screens.

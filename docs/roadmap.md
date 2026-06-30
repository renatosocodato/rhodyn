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
API contract is frozen, and Stage 5 has closed as a contract-bound scientific
workbench.

Current status in one sentence. RhoDyn can analyze declared dynamic readouts,
the v0.3 Stage 3 evidence bank is closed for the current gate, the Stage 4 API
contract is frozen, Stage 5 is completed as a contract-bound scientific
workbench with a narrow simulation UX repair, and Stage 6 has produced a
publicly citable `v0.1.0` GitHub and Zenodo software release while PyPI remains
a future distribution decision. Stage 7.8 is complete as the current
methods-readiness state. Stage 7.6 hardens the Stage 7.1 to Stage 7.5 evidence
set through release-archive clean-room reproduction, cross-surface parity,
documentation, CI wiring, and API stability policy. Stage 7.7 adds a scoped
usability rehearsal, and Stage 7.8 maps planned methods-manuscript components
to reproducible evidence, validation, and limitations. The Stage 7.7 and 7.8
surfaces are now recursively checked against the Stage 7.6 archive and release
checksums. Stage 8 remains conceptual, and Phase 9 manuscript-production work
has not been scaffolded.

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
2. Stage 4 is frozen for the first Stage 5 scaffold and remains the service
   dependency. The committed OpenAPI schema, frontend contract, fixtures, and
   closeout document are now the frontend dependency.
3. Stage 5 is completed as a contract-bound scientific workbench. The closed
   surface covers uploaded-table jobs, reproducible exports, parameter
   inspection, operation-specific comparison panels, simulation parameter exploration, and
   browser regression around the frozen Stage 4 contract.
4. Stage 6 has produced a professionally citable RhoDyn `v0.1.0` GitHub
   release archive and Zenodo DOI; PyPI remains a future distribution decision
   and should not be implied.
5. Stage 7.2 is complete as a benchmark-harness phase, Stage 7.3
   is complete as an independent public live-cell signaling demonstration
   phase, Stage 7.4 is complete as a perturbation endpoint, reserve-like,
   and routed-output demonstration phase, Stage 7.5 is complete as a held-out
   public validation, Stage 7.6 closes the methods-evidence reproducibility
   gate, Stage 7.7 completes usability rehearsal, and Stage 7.8 completes the
   methods-readiness package. Stage 7 remains a methods-manuscript readiness
   program aligned to standards exemplified by strong computational methods
   papers, with Nature Methods as the primary reference point rather than a
   guaranteed formula. Recursive hardening verifies the Stage 7.7 and 7.8
   outputs against the release checksum and archive surfaces without starting
   Phase 9.
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
| Stage 5. Frontend | Completed. | The closed workbench consumes the frozen Stage 4 contract, exposes the existing deterministic simulation surface, and preserves parameter inspection plus CLI reproducibility. Reopen only for a documented frontend defect. |
| Stage 6. Official software release | Public `v0.1.0` GitHub and Zenodo software release live. | RhoDyn is citable through the GitHub release archive and Zenodo DOI. Do not imply PyPI publication until a package-index upload is completed. |
| Stage 7. Independent methods-program roadmap | Stage 7.8 methods manuscript readiness package complete and recursively hardened against release surfaces. | Treat this as an evidence-expansion and methods-platform maturation program aligned to standards exemplified by strong computational methods papers. Nature Methods is the primary reference point, not an acceptance formula. |
| Stage 8. Product and commercial alignment | Conceptual only. | Product strategy inherits the Stage 7 methods evidence and should not lead the scientific evidence path. |

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
- Nature Methods remains the primary reference point for a future methods
  manuscript once the Stage 7 evidence gate is met, but the project should align
  to standards exemplified by strong methodology papers rather than overfitting
  to a venue.

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

### Stage 7.4 evidence-expansion status

Stage 7.4 adds a dedicated non-single-reporter demonstration layer. The
Cell Painting/MitoTox public endpoint case distinguishes a routed compartment
architecture from endpoint prevalence and one-dimensional morphology summaries,
and it derives a cell-health endpoint preservation coordinate from MitoTox
burden labels. The ERK/Akt public paired-reporter case preserves the declared
+/-0.20 residence-fraction margin and promotes only the UK ERK-minus-Akt
contrast as a context-limited bounded-coupling case while keeping histamine and
S1P outside the promoted claim.

The Stage 7.4 outputs are recorded under
`case_studies/stage7_endpoint_reserve_routing/`, with documentation in
`docs/stage7_endpoint_reserve_routing_demonstrations.md` and the gate report in
`docs/stage7_4_gate_report.json`. The reserve-like label is deliberately scoped
to endpoint-level cell-health preservation and does not claim live metabolic
reserve.

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

Status. Completed. The static workbench lives under `frontend/stage5/` and
loads the frozen Stage 4 contract files from `api/stage4/`. It exposes upload,
schema validation, trajectory preview, residence tuning, coupling/equivalence,
reserve, model-comparison, and report export surfaces without adding new
analysis routes. The completed Stage 5 surface adds per-trace residence
inspection for uploaded trajectories, clearer parameter provenance in exported
bundles, a guided MLCI public trajectory workflow that can be reproduced from
CLI, operation-specific comparison panels for residence, bounded coupling,
reserve, and reduced-model ranking, and one-click JSON, CSV, and Markdown
exports for the last run. A narrow simulation UX repair adds a local Simulation
Workbench for the existing deterministic controller, with parameter presets,
trajectory plots, first-passage timing, route readouts, and exports. The
hardening pass adds Playwright screenshot regression across desktop and mobile
viewports, adversarial bounded-coupling labels, simulation workbench coverage,
horizontal-overflow guards, and CI wiring. `docs/stage5_closeout.md` records the
closeout. Reopen Stage 5 only for a documented frontend defect;
new release, distribution, and citation surfaces belong to Stage 6.

## Stage 6. Official software release

Goal. Prepare RhoDyn for a professionally citable software release.

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

Status. Public GitHub and Zenodo software release live for `v0.1.0`. The
repository is public, the `v0.1.0` GitHub release and tag archive are available,
and the Zenodo software record provides version DOI `10.5281/zenodo.21036616`
and concept DOI `10.5281/zenodo.21036615`. PyPI publication remains a future
distribution decision and should not be implied by the current release. Stage 6
now remains the active post-release hardening lane for public accessibility,
checksums, documentation, and future distribution surfaces.

### Stage 6 subphase horizon

6.1 Release boundary. Define the first official RhoDyn release as a Python
library plus CLI for residence-window scoring, bounded coupling, reserve
summaries, reduced-architecture comparison, uncertainty, diagnostics, reports,
and the Stage 5 workbench. Gate. The release contains no manuscript-private
data, hidden local paths, raw microscopy, or claim that RhoDyn generated the
RhoA/microglia manuscript.

6.2 Packaging. Make installation professional with a clean `pyproject.toml`,
wheel and source distribution, optional extras such as `rhodyn[stats]`,
`rhodyn[plots]`, `rhodyn[backend]`, and `rhodyn[dev]`, CLI entry points, and
version stamping in outputs. Gate. A fresh clone can install the package and
run examples from scratch.

6.3 Documentation. Make the user path obvious through a quickstart, API
reference, CLI reference, input-schema guide, interpretation guide, tutorials,
example reports, and reproducibility card. Gate. A biologist can run the basic
workflow, and a quantitative user can audit parameter choices.

6.4 Release automation. Make releases repeatable through CI across Python
versions, package-build workflow, documentation-build workflow, release
checklist, changelog discipline, citation metadata, license and contribution
docs, and Docker build. Gate. Every release surface builds from CI rather than
from a local machine.

6.5 Archive and citation. Make RhoDyn independently citable through a GitHub
release, Zenodo DOI for RhoDyn itself, `CITATION.cff`, release notes, archived
source tarball, and checksum manifest. Gate. The archive contains only intended
software and public examples.

6.6 Clean-room reproducibility. Test from zero with a fresh clone, fresh virtual
environment, installed wheel, CLI examples, notebooks, documentation build,
workbench run, and report export. Gate. No release path depends on the
developer's local machine.

6.7 Final ultra-hardening. Close the release through local-path and secret
scans, dependency review, broken-link docs scan, screenshot regression, CLI/API
parity, Docker parity, PyPI dry run, Zenodo dry run, clean-room
reproducibility, and frontend/backend output parity. Gate. All official release
surfaces pass together.

## Stage 7. Independent biological demonstration and methods manuscript roadmap

Goal. Build the independent biological validation and methods-platform maturity
program needed before RhoDyn can support a high-impact computational methods
manuscript.

Planning stance.

RhoDyn should align to standards exemplified by strong computational methods
papers. Nature Methods is the primary reference point for rigor, biological
breadth, software maturity, reproducibility, and methodological clarity, but the
roadmap does not assume that any venue has a formula for acceptance.

Core methods-program claim to test.

Residence-state inference can reveal dynamic control variables in live-cell
perturbation data when cell state depends on dwell time, buffering, routed
output structure, and bounded coupling rather than endpoint amplitude alone.

Detailed planning surfaces.

- `docs/stage7_methods_program.md` records the evidence-based editorial
  reconnaissance, gap analysis, Stage 7 architecture, biological demonstration
  strategy, software maturity roadmap, and publication alignment roadmap.
- `docs/stage7_serialized_execution_plan.md` records the strictly ordered future
  execution plan for Stage 7 subphases.

Subphase horizon.

7.0 Planning freeze and evidence source register. Complete as a planning-only
phase. The source register, baseline-method inventory, dataset rubric, artifact
map, and gate report are now recorded under `docs/stage7_0_*`. Gate. Passed for
planning outputs only. No biological analysis, benchmark implementation,
software expansion, or manuscript drafting has started.

7.1 Formal method definition and assumption ledger. Complete as a
method-formalization phase. The method specification, synthetic truth cases,
limitations matrix, API notes, generator, tests, fixtures, and gate report are
recorded. Gate. Passed for formal definitions and synthetic truth fixtures. No
independent biological analysis or manuscript drafting has started.

7.2 Benchmark harness against baselines and alternatives. Compare RhoDyn against
amplitude-only, endpoint-only, threshold-only, generic trajectory, and reduced
architecture alternatives. Gate. Benchmarks show value-added, no-added-value,
and inconclusive regimes with runtime, uncertainty, and sensitivity evidence.

7.3 Independent public live-cell signaling demonstrations. Add public biological
systems that stress residence-versus-amplitude behavior outside the
RhoA/microglia manuscript. Gate. At least two independent public systems beyond
the original manuscript logic pass reproducibility and interpretation checks.

7.4 Perturbation endpoint, reserve, and routed-output demonstrations. Test
bounded coupling, reserve-like buffering, and routed-output model comparison in
non-trajectory or multi-readout cases. Gate. At least one case supports bounded
coupling, reserve logic, or routed-output interpretation without overclaiming
mechanism.



### Stage 7.5 held-out validation status

Stage 7.5 adds a held-out public validation route using non-DMSO inhibitor
contexts from the Wan 2021 ERK/Akt GPCR archive. The validation fixes the
Stage 7.4 DMSO-derived residence thresholds, the +/-0.20 ERK-minus-Akt
residence-fraction margin, the alpha threshold, and the cell-selection rule
before writing outcomes. Four held-out ligand-inhibitor contexts pass the
bounded-coupling rule and three remain margin-boundary inconclusive. The output
therefore enters the Stage 7 evidence set as scoped boundary validation rather
than as a universal ERK/Akt GPCR coupling claim.

The Stage 7.5 outputs are recorded under
`case_studies/stage7_heldout_validation/`, `docs/stage7_heldout_validation_report.md`,
and `docs/stage7_5_gate_report.json`.

### Stage 7.6 methods reproducibility status

Stage 7.6 closes the software-maturity gate for the methods evidence set. The
source-distribution clean-room run regenerates the Stage 7.1 to Stage 7.5
outputs, executes retained tutorial notebooks, builds documentation, checks
release-archive safety, and verifies agreement across Python, CLI, backend, and
frontend-contract surfaces for the shared method operations.

The Stage 7.6 outputs are recorded under
`case_studies/stage7_methods_reproducibility/`,
`docs/stage7_methods_reproducibility_card.md`,
`docs/stage7_6_gate_report.json`, `docs/stage7_6_clean_room_report.json`,
`docs/stage7_6_api_stability_policy.md`, and
`scripts/run_stage7_6_methods_reproducibility.py`. This phase adds no new
biological system and does not change the Stage 7.3 to Stage 7.5 biological
interpretations.

7.5 External or held-out biological validation. Run RhoDyn on a collaborator or
held-out dataset under predeclared criteria. Gate. Success, failure, or
inconclusive outcome is reported without hidden tuning.

7.6 Software maturity for methods-paper reproducibility. Harden APIs,
documentation, examples, CI, notebooks, Docker, benchmark fixtures, and clean-room
reproduction for the methods evidence set. Gate. A fresh environment reproduces
planned benchmark tables, reports, and tutorials.

7.7 Usability and adoption rehearsal. Test whether biological and quantitative
users can run and interpret RhoDyn results through tutorials and the workbench.
Gate. Biologist-facing interpretation and quantitative CLI/Python reproduction
both pass without adding unvalidated analysis routes.

Stage 7.7 is complete. The rehearsal is recorded in
`docs/stage7_7_gate_report.json`, `docs/stage7_usability_rehearsal.md`,
`docs/stage7_user_path_findings.md`, and
`case_studies/stage7_usability_rehearsal/`. The public MLCI workflow supports a
scoped residence-versus-amplitude interpretation over an intensity trajectory
table, the bounded-coupling fixture reproduces across Python, CLI, and backend
outputs, and the exported bundles include parameters, input schema, grouping,
software version, result JSON, result rows, Markdown report, and checksums.

Stage 7.8 is complete. The readiness package is recorded in
`docs/stage7_8_gate_report.json`, `docs/stage7_methods_evidence_index.md`,
`docs/stage7_figure_artifact_crosswalk.md`,
`docs/stage7_claim_evidence_crosswalk.md`,
`docs/stage7_methods_submission_readiness.md`, and
`case_studies/stage7_methods_readiness/`. The package maps planned figure
components and method claims to existing evidence, validation reports, and
limitation artifacts. It does not add a biological system, new analysis route,
benchmark result, or manuscript claim.

7.8 Methods manuscript readiness package. Assemble the figure-to-artifact,
claim-to-evidence, reproducibility, limitations, and release-candidate surfaces
needed before manuscript drafting. Gate. Every planned manuscript component maps
to a reproducible output and documented limitation.

Primary reference venue. Nature Methods, if the completed evidence demonstrates
methodological novelty, biological breadth, benchmark rigor, and software
maturity.

Strong pivots.

- Nature Biotechnology, if the workbench becomes broadly enabling for
  perturbation biology and screening.
- Nature Computational Science, if the computational method and benchmark theory
  dominate.
- Cell Systems, if the dynamic systems-biology story is strongest.
- Science Advances, if generality is broad but method novelty is less
  platform-level.
- PLOS Computational Biology, Bioinformatics Advances, or JOSS only if the
  evidence shape supports a software-methods or software-credit route rather
  than the primary high-impact methods claim.

Status. Stage 7.8 methods manuscript readiness package complete. The
v0.3 evidence bank and v0.1.0 release support Stage 7, and the method objects
now have formal definitions, executable synthetic examples, baseline benchmarks,
sensitivity outputs, performance measurements, failure-behavior checks, two
independent public live-cell signaling demonstrations, and a public non-single-reporter
demonstration layer. The held-out validation and methods-evidence
reproducibility gates are now closed, and the first usability/adoption rehearsal
passes. The methods-manuscript readiness package now links planned figures,
claims, limitations, release evidence, and known inconclusive outcomes to
reproducible outputs.

## Stage 8. Product and commercial alignment

Goal. Let product development inherit the Stage 7 methods-program evidence.

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
evidence path. Stage 8 inherits from Stage 7, and Stage 7 depends on the Stage 3
evidence bank plus the Stage 7 independent-demonstration program.

## Immediate next path

The current roadmap should not drift away from the original Stage 3 to Stage 8
sequence.

1. Treat the v0.3 Stage 3 evidence bank and its gate report as the reference
   public case-study surface.
2. Treat Stage 5 as closed unless a documented frontend defect is found.
3. Treat Stage 6 as publicly citable through GitHub and Zenodo while keeping
   PyPI as a future distribution decision.
4. Execute Stage 7 only from the serialized plan in
   `docs/stage7_serialized_execution_plan.md`. Additional independent biological
   systems are Stage 7 method-evidence work, not a rebranding of the
   RhoA/microglia paper or a substitute for the Stage 3 gate.

Official release work now sits downstream of the evidence bank, frozen service
contract, and completed Stage 5 workbench. Stage 7.1 is complete as a method-formalization phase, Stage 7.2 has not
started, and product work remains downstream of Stage 7 evidence.

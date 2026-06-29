# Stage 7 methods-program roadmap

Stage 7 turns RhoDyn from a released research-software toolkit into a methods-program candidate. The aim is not to claim that RhoDyn is ready for a high-impact methods manuscript now. The aim is to define the evidence, software maturity, biological validation, and reproducibility work required before that claim would be scientifically credible.

Nature Methods is the primary reference point for rigor, reporting, software maturity, biological breadth, and reproducibility. The roadmap does not treat any journal as a formula for acceptance. It extracts common standards from public author guidance and representative computational methods papers, then maps those standards onto RhoDyn's current state.

No Stage 7 implementation begins in this document. The current outcome is a planned, serialized evidence program.

## Evidence basis

The planning synthesis used public editorial guidance and representative methods papers available on 2026-06-29.

| source | planning signal for RhoDyn |
| --- | --- |
| [Nature Portfolio reporting standards and availability policy](https://www.nature.com/nature-portfolio/editorial-policies/reporting-standards) | Published claims should be reproducible from available data, code, materials, and protocols. Nature requires data availability statements for original research, expects the minimum dataset needed to interpret and verify the article, and expects code or algorithms central to the main claims to be available for editors and reviewers and described in a Code Availability section. |
| [PLOS Computational Biology submission guidelines](https://journals.plos.org/ploscompbiol/s/submission-guidelines) | Computational biology manuscripts should make underlying data and author-generated code openly available except for rare restrictions, with repository names, persistent identifiers, and code documentation. |
| [JOSS review criteria](https://joss.readthedocs.io/en/latest/review_criteria.html) | Sustainable scientific software is not a one-time code dump. Reviewable software has a statement of need, installation instructions, usage examples, API documentation, a license, tests, CI or objective verification, tagged releases, and contribution/support pathways. |
| [Cellpose, Nature Methods 2021](https://www.nature.com/articles/s41592-020-01018-x) | A strong methods paper states a broad biological bottleneck, introduces a general method, tests generalization across diverse image types, compares performance against existing methods, and provides data, GUI, code, web use, and community extension routes. |
| [Squidpy, Nature Methods 2022](https://www.nature.com/articles/s41592-021-01358-2) | A platform method can earn breadth by integrating multiple data modalities, providing scalable infrastructure, packaging, documentation, reproducibility code, and analysis datasets that users can access through the software. |
| [CellRank, Nature Methods 2022](https://www.nature.com/articles/s41592-021-01346-6) | A computational method is stronger when it combines a formal inference object with biological demonstrations in different systems, uncertainty handling, reproducible notebooks, public processed data, and a software/tutorial surface. |
| [Single-cell trajectory inference benchmark, Nature Biotechnology 2019](https://www.nature.com/articles/s41587-019-0071-9) | Benchmark papers become useful when they compare many methods across synthetic and real datasets, evaluate topology, scalability, usability, and give users explicit method-selection guidance. |

## Common standards extracted from strong computational methods papers

High-quality computational methods papers usually make six kinds of evidence visible.

1. A formal method definition. The paper defines the input object, output object, assumptions, objective functions, uncertainty quantities, and failure modes.
2. Benchmarks against simpler and competing summaries. The method is compared against amplitude-only, endpoint-only, threshold-only, generic time-series, and domain-standard alternatives rather than only against its own intuition.
3. Synthetic tests with known truth. The method is stress-tested where the generating regime is known, including cases where it should succeed, fail, or become ambiguous.
4. Independent biological demonstrations. The software is used on biological systems that stress different assumptions, not just one manuscript's data.
5. Reproducible software and data. Versioned code, archived data, notebooks or scripts, package metadata, documentation, and persistent identifiers make the work reviewable and reusable.
6. Usability and maintenance evidence. The tool has installation paths, examples, API documentation, tests, CI, release versioning, and a clear user path for both biological and quantitative users.

For RhoDyn, the biological standard is sharper than ordinary software maturity. Stage 7 must show that residence-state inference detects dynamic operating-state structure in live-cell perturbation data that amplitude-only or endpoint-only summaries miss, and it must do so across biological systems that were not constructed to support the RhoA/microglia manuscript.

## Current RhoDyn strengths

RhoDyn already has several assets that make Stage 7 plausible.

- A public `v0.1.0` GitHub and Zenodo software release with version DOI `10.5281/zenodo.21036616` and concept DOI `10.5281/zenodo.21036615`.
- A modular Python API covering tidy schema validation, residence scoring, reserve summaries, bounded coupling, model comparison, uncertainty, sensitivity, stochastic helpers, plotting, CLI, backend core, FastAPI app, and typed results.
- Stage 3 public evidence examples showing residence-versus-amplitude behavior in DRG calcium and ERK signaling, endpoint architecture comparison in public Cell Painting/MitoTox tables, and a bounded-coupling example in public ERK/Akt traces.
- A frozen Stage 4 service contract and Stage 5 scientific workbench that preserve uploaded rows, parameters, software version, report exports, and CLI/API/frontend parity.
- Release checks for local paths, raw/private data exclusion, docs links, dependency review, package builds, Docker smoke testing, public GitHub/Zenodo release integrity, and screenshot regression.

These strengths support Stage 7 entry. They do not yet satisfy Stage 7 readiness.

## Gap analysis

| priority | gap | why it matters | current evidence | required Stage 7 closure |
| --- | --- | --- | --- | --- |
| Critical | Formal method specification is incomplete for manuscript-level review. | A methods paper needs explicit definitions of residence windows, dwell metrics, bounded coupling, reserve-like readouts, routed-output comparisons, uncertainty, and failure modes. | API and docs define functions, but not a unified method paper specification. | Stage 7.1 must produce a formal mathematical and algorithmic specification with examples and non-example boundaries. |
| Critical | Benchmarks do not yet compare RhoDyn against enough baseline and alternative summaries. | A methods claim requires showing what residence-state inference adds beyond amplitude, endpoints, thresholds, generic trajectory features, and domain-standard alternatives. | Stage 3 compares residence with amplitude in examples and has model comparison, but no broad benchmark harness. | Stage 7.2 must create a benchmark suite with synthetic truth, baselines, metrics, and failure cases. |
| Critical | Independent biological demonstrations are not broad enough for a high-impact methods manuscript. | The manuscript cannot rest on the RhoA/microglia use case or lightweight public examples alone. | Stage 3 contains public examples, but the gate was intentionally minimal. | Stage 7.3 to 7.5 must add at least two independent biological systems beyond the original manuscript logic, ideally with one collaborator or held-out dataset. |
| Critical | External validation and blind reuse are missing. | A methods paper is stronger when another dataset, collaborator, or blinded analysis confirms usability and boundary behavior. | Current examples are internal analyses of public tables. | Stage 7.5 must include a held-out or collaborator-provided analysis route with predeclared success criteria. |
| High | Software APIs are public but not yet declared stable for a methods manuscript. | Manuscript examples should run against stable APIs that will not change under readers. | v0.1.0 is released, but PyPI and semantic API policy remain future decisions. | Stage 7.6 must define API stability, version support, deprecation policy, and reproducibility fixtures. |
| High | Performance and scalability are not benchmarked as a formal claim. | Methods papers often need evidence of dataset size, runtime, memory, and scaling behavior. | Backend and frontend function on fixtures and examples. | Stage 7.2 and 7.6 must add runtime/memory benchmarks and size-stress tests. |
| High | Uncertainty handling needs manuscript-facing validation. | RhoDyn decisions should show sensitivity to window choice, replicate grouping, margins, posterior/interval thresholds, and sample size. | The library has uncertainty, sensitivity, TOST/ROPE helpers, and grouped resampling. | Stage 7.2 must test uncertainty calibration and fragility across synthetic and public cases. |
| High | Biological demonstration selection criteria are not yet frozen. | Dataset choices should stress different method assumptions rather than maximize novelty. | Public candidates exist, but Stage 7 has no selection rubric. | Stage 7.0 and 7.3 must define inclusion, exclusion, and fallback criteria for public and collaborator datasets. |
| Medium | User documentation is good for release use but not yet a methods-paper teaching path. | Readers need tutorial narratives that map method concepts to biological interpretation. | Quickstart, CLI/API docs, interpretation guide, and notebooks exist. | Stage 7.6 and 7.7 must add methods-paper tutorials, decision-tree guidance, and reproducible figure recipes. |
| Medium | Hosted or GUI usability evidence is preliminary. | A future methods paper may need evidence that biologists can use the workbench without reading code. | Stage 5 static workbench exists with screenshot regression. | Stage 7.7 must run a usability rehearsal with defined tasks and reproducible outcomes. |
| Medium | Documentation lacks a methods-paper limitations matrix. | Failure modes increase trust and prevent overclaiming. | Interpretation guide contains scientific boundaries. | Stage 7.1 and 7.8 must produce a limitations table tied to each method component. |
| Future enhancement | Commercial product alignment is intentionally deferred. | Product claims should not lead scientific evidence. | Stage 8 is conceptual only. | Stage 8 remains downstream until Stage 7 demonstrates method generality. |

## Stage 7.0 planning-freeze outputs

Stage 7.0 has now been executed as a planning-only phase. It created the source register, baseline-method inventory, dataset selection rubric, artifact map, and gate report required to begin the Stage 7 program without starting analysis implementation.

- `docs/stage7_0_source_register.md` records official guidance, representative methods papers, current RhoDyn state, and candidate dataset classes.
- `docs/stage7_0_baseline_method_inventory.md` records amplitude, endpoint, threshold, generic trajectory, domain-standard, null-control, and method-ablation comparators.
- `docs/stage7_0_dataset_selection_rubric.md` records inclusion, rejection, scoring, and fallback rules for future datasets.
- `docs/stage7_0_artifact_map.md` distinguishes created planning artifacts from future analysis, software, and manuscript-support artifacts.
- `docs/stage7_0_gate_report.json` records prerequisite and completion status for the planning-freeze phase.

Stage 7.0 does not add biological analyses, benchmark code, public-data adapters, manuscript text, figures, or product features. Stage 7.1 remains the next phase and requires explicit authorization.

## Stage 7.1 method formalization outputs

Stage 7.1 has now been executed as a method-formalization phase. It defines RhoDyn's method objects in mathematical, algorithmic, and biological terms, records failure modes and interpretation boundaries, and adds executable synthetic truth cases with positive, counterexample, and ambiguous regimes.

- `docs/stage7_method_specification.md` records the formal method definitions for input tables, residence, reserve-like summaries, bounded coupling, model comparison, uncertainty, sensitivity, and timing.
- `docs/stage7_synthetic_truth_cases.md` documents the executable synthetic cases.
- `docs/stage7_limitations_matrix.md` records non-example cases and interpretation boundaries.
- `docs/stage7_api_stability_notes.md` records that current APIs can represent the Stage 7.1 method objects without reopening the stable package surface.
- `scripts/build_stage7_1_synthetic_truth_cases.py` generates the synthetic truth fixtures under `case_studies/stage7_synthetic_truth/`.
- `docs/stage7_1_gate_report.json` records the 7.1 completion gate.

Stage 7.1 does not add independent biological evidence, manuscript claims, product features, or new stable public APIs. Stage 7.2 remains the next phase and requires explicit authorization.

## Stage 7 architecture

Stage 7 is a sequential program. Each subphase must close before the next begins unless the stated contingency route is activated.

### Stage 7.0. Planning freeze and evidence source register

Scientific objective. Freeze the Stage 7 scope as a methods-program, not a rebranding of the RhoA/microglia manuscript.

Engineering objective. Identify which current APIs, notebooks, fixtures, and reports are in scope for Stage 7 and which remain release-only surfaces.

Validation objective. Confirm the current repository state, public release state, and Stage 3 case-study status are internally consistent.

Reproducibility objective. Record source guidance, representative papers, candidate datasets, and planned artifacts with stable links.

Expected deliverables.

- Stage 7 source register.
- Dataset selection rubric.
- Baseline method inventory.
- Stage 7 artifact map.

Entry criteria. Public v0.1.0 release resolves, Stage 3 gate report passes, and Stage 4 to Stage 5 contract surfaces are available.

Exit criteria. The Stage 7 dataset rubric, baseline list, and artifact map are approved without starting implementation.

Quality gates.

- No Stage 7 demonstration is counted unless it maps to a method component and a biological stress test.
- No manuscript figure is planned without a corresponding reproducible analysis output.
- No claim says RhoDyn generated the RhoA/microglia manuscript.

### Stage 7.1. Formal method definition and assumption ledger

Scientific objective. Define residence-state inference as a formal method for dynamic operating-state analysis in live-cell perturbation biology.

Engineering objective. Map each method object to a stable API function, input schema, result object, and serialization format.

Validation objective. Create synthetic cases where residence, amplitude, reserve, bounded coupling, and routed-output structure are known by construction.

Reproducibility objective. Ensure every formal definition has an executable example and a counterexample.

Expected deliverables.

- Method specification document.
- Mathematical notation for input tables, residence windows, dwell metrics, amplitude summaries, reserve summaries, bounded-coupling regions, architecture comparison, and uncertainty.
- Synthetic truth generator suite.
- Limitations matrix.

Entry criteria. Stage 7.0 source register and dataset rubric complete.

Exit criteria. Every method claim has a formal definition, a test fixture, and a documented failure boundary.

Quality gates.

- Residence is never treated as automatically discovered when a window is user-declared.
- Bounded coupling means equivalence within a declared margin, not absence of all coupling.
- Reserve-like summaries are not promoted to biological reserve without a measured reserve readout.

### Stage 7.2. Benchmark harness against baselines and alternatives

Scientific objective. Show when residence-state inference improves interpretation over amplitude-only, endpoint-only, threshold-only, generic trajectory, and reduced-architecture alternatives.

Engineering objective. Build a reproducible benchmark harness that can run all baselines against the same input tables and emit comparable metrics.

Validation objective. Quantify accuracy, calibration, sensitivity, robustness, runtime, memory, and failure rates across synthetic and public datasets.

Reproducibility objective. Archive benchmark inputs, parameters, outputs, and result summaries with deterministic rerun commands.

Expected deliverables.

- Synthetic benchmark matrix.
- Baseline comparator library or wrappers.
- Performance benchmark report.
- Sensitivity and uncertainty benchmark report.
- Benchmark summary tables for a future methods manuscript.

Entry criteria. Stage 7.1 formal definitions and synthetic generators pass.

Exit criteria. Benchmarks identify regimes where RhoDyn adds value, regimes where amplitude or endpoint summaries are sufficient, and regimes where RhoDyn is inconclusive.

Quality gates.

- At least one benchmark must show a residence/amplitude disagreement with known truth.
- At least one benchmark must show a negative or inconclusive boundary where RhoDyn should not overcall.
- Runtime and memory are reported for representative table sizes.

### Stage 7.3. Independent public live-cell signaling demonstrations

Scientific objective. Demonstrate that residence-state inference is useful outside the RhoA/microglia manuscript by analyzing public live-cell signaling datasets.

Engineering objective. Add public-data adapters that convert selected datasets into stable tidy trajectory inputs without embedding raw private or manuscript data.

Validation objective. Show at least two independent biological systems with residence/amplitude distinctions or clearly bounded non-differences.

Reproducibility objective. Provide notebooks and command-line reproductions for every public demonstration.

Expected deliverables.

- Public live-cell signaling case-study folders.
- Adapter scripts with source citations and download/recovery instructions.
- Residence versus amplitude benchmark tables.
- Biological interpretation notes with explicit scope.

Entry criteria. Stage 7.2 benchmark harness can run on public inputs.

Exit criteria. At least two independent public systems beyond the original manuscript logic pass reproducibility and interpretation gates.

Quality gates.

- Candidate systems should prioritize ERK, NF-kB, calcium, Rho-family, kinase, or multiplexed reporter dynamics when available.
- Each case must state what RhoDyn finds that endpoint or amplitude summaries miss, or why it does not add value.
- Each case must preserve replicate, condition, and time-series grouping structure.

### Stage 7.4. Perturbation endpoint, reserve, and routed-output demonstrations

Scientific objective. Test whether RhoDyn generalizes beyond single-signal trajectories to reserve-like buffering, bounded coupling, and routed-output model comparison.

Engineering objective. Extend adapters and result reports for endpoint tables, paired reporters, reserve-like readouts, and routed-output comparisons.

Validation objective. Demonstrate at least one public or collaborator case where bounded coupling or reserve logic is biologically informative.

Reproducibility objective. Provide model-comparison and uncertainty reports with declared margins, grouping, and sensitivity.

Expected deliverables.

- Endpoint or perturbation benchmark case study.
- Reserve-like or buffering case study.
- Routed-output comparison report.
- Sensitivity and uncertainty tables.

Entry criteria. Stage 7.3 public signaling cases pass.

Exit criteria. At least one non-trajectory demonstration supports bounded coupling, reserve logic, or routed-output architecture without overclaiming direct mechanism.

Quality gates.

- Equivalence or bounded-coupling claims require declared margins and uncertainty support.
- Model comparison must include reduced alternatives and report cases where alternatives remain plausible.
- Reserve-like labels must remain scoped unless the dataset directly measures biological reserve.

### Stage 7.5. External or held-out biological validation

Scientific objective. Test whether RhoDyn remains useful when applied to a dataset not selected, tuned, or interpreted solely by the software author.

Engineering objective. Provide a reproducible intake path for collaborator-provided or held-out public data.

Validation objective. Run the method under predeclared criteria and report success, failure, or inconclusive boundaries.

Reproducibility objective. Preserve enough metadata, schema, parameters, and outputs for review while respecting any access restrictions.

Expected deliverables.

- Held-out analysis plan.
- Intake schema checklist.
- External validation report.
- Reviewer-ready reproducibility bundle or controlled-access note.

Entry criteria. Stage 7.3 and 7.4 demonstrations pass and the software contract is stable enough for external use.

Exit criteria. At least one external or held-out analysis completes with a documented biological interpretation and explicit limitations.

Quality gates.

- No post hoc window or margin tuning without being labeled exploratory.
- Failed or inconclusive external validation is reported as method boundary evidence, not hidden.
- Controlled-access data must not be committed to the public release repository.

### Stage 7.6. Software maturity for methods-paper reproducibility

Scientific objective. Ensure every biological conclusion in the future methods manuscript can be rerun, inspected, and stress-tested.

Engineering objective. Harden the package, CLI, backend, documentation, examples, tests, CI, packaging, Docker, and release process for methods-paper review.

Validation objective. Confirm examples, notebooks, public data adapters, benchmarks, backend outputs, and workbench exports agree with the Python library outputs.

Reproducibility objective. Produce a clean-room method-paper reproduction path from fresh clone or release archive.

Expected deliverables.

- API stability policy.
- Methods-paper reproducibility card.
- Public benchmark fixture suite.
- CI matrix for examples, docs, notebooks, package, Docker, and frontend regression.
- Versioned release candidate.

Entry criteria. Stage 7.5 validation route complete or explicitly deferred with justification.

Exit criteria. A fresh environment can reproduce the benchmark tables, figures, reports, and tutorials planned for the methods manuscript.

Quality gates.

- Package install, docs build, notebooks, benchmark scripts, and workbench smoke tests pass from a clean environment.
- No local paths, secrets, private raw data, or manuscript-private files enter public release artifacts.
- Every result stores software version, input schema, parameters, and grouping metadata.

### Stage 7.7. Usability and adoption rehearsal

Scientific objective. Test whether target users can interpret residence-like versus amplitude-like behavior and bounded coupling without reading source code.

Engineering objective. Improve the workbench and tutorials only where user tasks fail.

Validation objective. Run a small structured usability rehearsal with biologist and quantitative-user tasks.

Reproducibility objective. Record task scripts, expected outputs, user-facing exports, and failure fixes.

Expected deliverables.

- Usability task protocol.
- User-path findings report.
- Workbench/tutorial fixes if needed.
- Export and report examples for a methods paper supplement.

Entry criteria. Stage 7.6 software maturity path passes.

Exit criteria. A biologist can run a public tutorial and understand the dynamic-state result, while a quantitative user can reproduce the same result from CLI.

Quality gates.

- Usability fixes must not add new biological claims.
- Interface output must match library output exactly.
- Exports must include parameters and version metadata.

### Stage 7.8. Methods manuscript readiness package

Scientific objective. Assemble the evidence needed for a methods manuscript without writing around missing analyses.

Engineering objective. Freeze the manuscript-supporting code, data, notebooks, figures, and reports as a versioned candidate release.

Validation objective. Check that every manuscript figure and claim maps to a reproducible output and a documented limitation.

Reproducibility objective. Produce a reviewer-access package with archived software, data, benchmark results, notebooks, and documentation.

Expected deliverables.

- Methods manuscript evidence index.
- Figure-to-artifact crosswalk.
- Benchmark result tables.
- Limitations and failure-mode table.
- Submission-readiness checklist.

Entry criteria. Stages 7.1 through 7.7 are complete or explicitly scoped.

Exit criteria. The project is ready to draft a methods manuscript because every planned claim has supporting software, data, validation, and reproducibility assets.

Quality gates.

- No manuscript component can be promoted without a reproducible supporting artifact.
- Nature Methods remains a reference point, not an acceptance claim.
- Alternative venues are chosen based on evidence shape, not on aspiration.

## Subphase dependency and success-metric matrix

This matrix makes the dependencies and success metrics explicit for every Stage 7 subphase. It complements the objectives, deliverables, entry criteria, exit criteria, and quality gates above.

| subphase | dependencies | success metrics |
| --- | --- | --- |
| 7.0 Planning freeze and evidence source register | Public v0.1.0 release, Stage 3 gate report, Stage 4 contract, Stage 5 closeout, current roadmap memory. | Source register, dataset rubric, baseline inventory, and artifact map exist and no implementation artifacts are created. |
| 7.1 Formal method definition and assumption ledger | 7.0 source register, dataset rubric, baseline inventory, and artifact map. | Every method component has a formal definition, executable example, counterexample, failure boundary, and mapped API or documented API gap. |
| 7.2 Benchmark harness against baselines and alternatives | 7.1 formal definitions, synthetic truth generators, and baseline inventory. | Benchmarks report RhoDyn-positive, baseline-sufficient, and inconclusive regimes with uncertainty, sensitivity, runtime, and memory summaries. |
| 7.3 Independent public live-cell signaling demonstrations | 7.2 benchmark harness and public dataset selection rubric. | At least two independent public live-cell systems beyond the original manuscript logic pass reproducibility, grouping, and scoped-interpretation checks. |
| 7.4 Perturbation endpoint, reserve, and routed-output demonstrations | 7.3 public signaling demonstrations plus endpoint, paired-reporter, or reserve-like input schemas. | At least one non-trajectory or multi-readout case supports bounded coupling, reserve logic, or routed-output comparison without overclaiming mechanism. |
| 7.5 External or held-out biological validation | 7.3 and 7.4 demonstrations, stable intake schema, and collaborator or held-out data access. | A predeclared held-out analysis reports success, failure, or inconclusive status with no hidden tuning and reviewable reproducibility metadata. |
| 7.6 Software maturity for methods-paper reproducibility | 7.2 to 7.5 benchmark and demonstration outputs. | Fresh-environment reproduction regenerates the methods evidence tables, reports, tutorials, and workbench outputs without local paths or private data. |
| 7.7 Usability and adoption rehearsal | 7.6 stable software, tutorials, reports, and workbench flows. | A biologist can complete a tutorial-level interpretation task, and a quantitative user can reproduce the same result from CLI or Python. |
| 7.8 Methods manuscript readiness package | 7.1 to 7.7 completed or explicitly scoped with documented limitations. | Every planned manuscript figure and claim maps to a reproducible artifact, validation result, and limitation entry. |

## Independent biological demonstration strategy

The Stage 7 demonstrations should be selected to stress different parts of the method.

1. Live-cell signaling residence versus amplitude. Public ERK, NF-kB, calcium, Rho-family, or kinase reporter trajectories should test whether residence-state inference finds biologically meaningful dwell-time structure that amplitude alone misses.
2. Paired-reporter bounded coupling. Public or collaborator datasets with two reporters should test equivalence margins, coupling boundaries, and cases where the method refuses overclaiming.
3. Reserve or buffering logic. Public calcium, mitochondrial, stress-response, or viability-linked time series should test whether reserve-like summaries can be distinguished from amplitude responses.
4. Routed-output model comparison. Endpoint or multiplexed feature tables should test whether reduced architectures fail in specific ways and whether routed-output models improve interpretability.
5. RhoA/microglia reference use case. The manuscript remains a biological-depth example and stress test, but it cannot supply the software generality claim.

Dataset inclusion criteria.

- Public or collaborator-authorized access.
- Time-resolved or perturbation-resolved measurements.
- Clear biological conditions and replicate structure.
- Sufficient metadata to preserve grouping.
- A plausible baseline summary to compare against.
- A failure mode that can be stated without damaging the method.

Dataset rejection criteria.

- Missing time units, condition labels, or replicate structure.
- Only endpoint means when the question requires trajectories.
- Unclear preprocessing that prevents reviewable reconstruction.
- Access restrictions incompatible with review or public release.
- Datasets selected only because they make RhoDyn look favorable.

## Software maturity roadmap

Stage 7 software work should be tied to manuscript evidence rather than generic product expansion.

| maturity area | Stage 7 target | linked subphases |
| --- | --- | --- |
| API stability | Declare stable public functions, result schemas, and deprecation rules for methods-paper examples. | 7.1, 7.6 |
| Input schemas | Support trajectory, endpoint, paired-reporter, reserve-like, and model-comparison tables with validation examples. | 7.1, 7.3, 7.4 |
| Benchmark engine | Run declared baselines and RhoDyn analyses on the same synthetic and public inputs. | 7.2 |
| Uncertainty | Make grouping, bootstrap/permutation, sensitivity, TOST/ROPE, and failure boundaries visible in reports. | 7.2, 7.4 |
| Public adapters | Convert selected datasets into tidy inputs without committing raw restricted data. | 7.3, 7.4 |
| Reports | Export JSON, CSV, Markdown, and figure-ready outputs that preserve parameters and version metadata. | 7.6, 7.7 |
| Documentation | Add method concept, tutorials, limitations, benchmark interpretation, and reproducibility pages. | 7.6, 7.7 |
| CI and release | Test examples, notebooks, docs, benchmark fixtures, package builds, Docker, and frontend regression. | 7.6, 7.8 |
| Security and privacy | Keep private data, local paths, credentials, and collaborator-restricted inputs out of public artifacts. | 7.5, 7.6, 7.8 |
| Performance | Report runtime and memory for representative synthetic and public sizes. | 7.2, 7.6 |

## Publication alignment roadmap

The future methods manuscript should emerge from Stage 7 evidence, not from a writing exercise.

Candidate narrative. Residence-state inference reveals dynamic control variables in live-cell perturbation data.

Potential method-level claims.

- Residence windows can encode cell-state behavior that amplitude summaries miss.
- Bounded coupling can distinguish context-limited stability from unresolved crosstalk when margins are predeclared.
- Reserve-like readouts can be integrated without treating every model-derived coordinate as a direct biological endpoint.
- Reduced-architecture comparison can expose when endpoint-only or single-axis interpretations fail.
- A reproducible software surface can make these dynamic operating-state analyses inspectable by both biologists and quantitative users.

Planned manuscript evidence map.

| manuscript component | required supporting milestone |
| --- | --- |
| Concept and formal method figure | Stage 7.1 formal specification and synthetic examples. |
| Benchmark figure | Stage 7.2 synthetic and baseline benchmark suite. |
| Public live-cell signaling figure | Stage 7.3 independent public demonstrations. |
| Perturbation/reserve/routed-output figure | Stage 7.4 endpoint and reserve demonstrations. |
| External validation figure or supplement | Stage 7.5 held-out or collaborator validation. |
| Software workbench and reproducibility figure | Stage 7.6 and 7.7 software and usability evidence. |
| Limitations section | Stage 7.1 limitations matrix plus all negative or inconclusive benchmark outcomes. |
| Data/code availability | Stage 7.6 and 7.8 archived release, dataset identifiers, notebooks, and checksums. |

Primary reference venue. Nature Methods, if the evidence demonstrates methodological novelty, biological breadth, and software maturity.

Strong pivots.

- Nature Biotechnology if the workbench becomes broadly enabling for perturbation biology and screening.
- Nature Computational Science if the computational method and benchmark theory dominate.
- Cell Systems if the dynamic systems-biology insight is strongest.
- Science Advances if biological breadth is strong but platform novelty is more modest.
- PLOS Computational Biology, Bioinformatics Advances, or JOSS only if the evidence shape supports a software-methods or software-credit route rather than a primary high-impact methods claim.

## Stage 8 boundary

Stage 8 should inherit Stage 7's strongest supported method statement. It should not change the evidence path. Commercial or hosted features become appropriate only after Stage 7 shows that users beyond the original manuscript can obtain reliable dynamic operating-state interpretations from their own live-cell perturbation data.

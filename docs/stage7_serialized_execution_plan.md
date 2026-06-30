# Stage 7 serialized execution plan

This execution plan turns the Stage 7 roadmap into a strictly serialized future work program. No downstream subphase should begin until the preceding subphase satisfies its gates or a documented contingency is approved.

This document is planning only. It does not start implementation, manuscript drafting, software development, dataset acquisition, or external collaboration.

## Global execution rule

Each subphase must close with four records before the next one starts.

1. A scientific output that states the biological or methodological result.
2. A reproducibility output that identifies inputs, parameters, versions, and commands.
3. A validation output that reports pass, fail, or inconclusive status against the predeclared gate.
4. A roadmap update that states whether the next phase proceeds, pivots, narrows, or stops.

## Subphase bookkeeping and roadmap updates

For every Stage 7 subphase, repository bookkeeping and roadmap updates are part of the completion gate rather than optional cleanup.

| subphase | repository bookkeeping | roadmap update |
| --- | --- | --- |
| 7.0 | Add source register, dataset rubric, baseline inventory, and artifact map without adding analysis outputs. | Mark 7.0 complete only if implementation has not started and 7.1 is authorized as the next action. |
| 7.1 | Add method specification, synthetic truth fixtures, limitation matrix, and any API-gap notes. | Record which method objects are stable, which remain scoped, and whether 7.2 can start. |
| 7.2 | Add benchmark harness outputs, baseline summaries, performance reports, and uncertainty reports. | Record value-added, no-added-value, and inconclusive benchmark regimes before selecting biological demonstrations. |
| 7.3 | Add public-data adapters, trajectory tables, provenance records, notebooks, and interpretation reports. | Record which public systems count as independent demonstrations and which remain exploratory. |
| 7.4 | Add endpoint, reserve-like, paired-reporter, routed-output, margin, and model-comparison reports. | Record whether bounded coupling, reserve logic, or routed-output evidence is strong enough for methods-manuscript planning. |
| 7.5 | Add held-out analysis plan, intake checklist, validation report, and controlled-access note if needed. | Record whether external validation supports, narrows, or challenges the Stage 7 method claim. |
| 7.6 | Add API stability policy, CI reports, clean-room reproduction report, docs updates, and release-candidate metadata. | Record whether the methods evidence set is reproducible from a clean environment. |
| 7.7 | Add usability protocol, task results, export examples, and any tutorial or workbench fixes. | Record whether the user path is ready for a methods manuscript or needs another usability iteration. |
| 7.8 | Add claim-to-evidence, figure-to-artifact, limitations, reproducibility, and submission-readiness crosswalks. | Record whether manuscript drafting can begin, which venue frame fits the evidence, and what remains out of scope. |

## 7.0. Planning freeze and evidence source register

Stage 7.0 execution status. Complete as a planning-only phase. The created planning artifacts are `docs/stage7_0_source_register.md`, `docs/stage7_0_baseline_method_inventory.md`, `docs/stage7_0_dataset_selection_rubric.md`, `docs/stage7_0_artifact_map.md`, and `docs/stage7_0_gate_report.json`. Stage 7.1 is not started.

Objectives.

- Freeze Stage 7 as an independent methods-program roadmap.
- Record public editorial guidance, representative methods papers, current RhoDyn state, candidate dataset classes, and baseline methods.
- Keep the RhoA/microglia manuscript as a reference use case only.

Prerequisites.

- Public `v0.1.0` GitHub and Zenodo release resolves.
- Stage 3 gate report passes.
- Stage 4 contract and Stage 5 workbench closeout documents exist.

Implementation order.

1. Build a source register for guidance, representative methods papers, and candidate datasets.
2. Build a baseline-method inventory covering amplitude, endpoints, thresholds, generic trajectory features, and domain-standard methods.
3. Build a dataset selection rubric with inclusion, rejection, and fallback criteria.
4. Build an artifact map that names the expected Stage 7 outputs without creating them.

Validation checkpoints.

- Source register contains official guidance and representative papers.
- Dataset rubric rejects datasets lacking metadata, time units, grouping, or reviewable access.
- Artifact map distinguishes planning outputs from future analysis outputs.

Documentation updates.

- `docs/stage7_methods_program.md`.
- `docs/stage7_serialized_execution_plan.md`.
- `docs/roadmap.md`.
- `docs/roadmap_execution_memory.json`.
- `docs/architecture.md` if Stage 7 boundaries change.

Completion criteria.

- Stage 7 is marked as roadmap-defined but not started.
- No code, analysis, or manuscript implementation has begun.

Stop condition.

- If current release or Stage 3 gate evidence is inconsistent, stop and repair the upstream state before Stage 7 planning continues.

## 7.1. Formal method definition and assumption ledger

Stage 7.1 execution status. Complete as a method-formalization phase. The method specification, synthetic truth documentation, limitations matrix, API stability notes, truth-case generator, tests, truth fixtures, and gate report are recorded. Stage 7.2 is not started.

Objectives.

- Define RhoDyn's method object in mathematical, algorithmic, and biological terms.
- State assumptions, inputs, outputs, and failure modes for each component.

Prerequisites.

- 7.0 complete.
- Stable source register and baseline inventory.

Implementation order.

1. Define tidy trajectory and endpoint input objects.
2. Define residence windows, dwell fraction, dwell time, segment count, and amplitude comparators.
3. Define reserve-like summaries, bounded-coupling decisions, routed-output model comparison, and uncertainty summaries.
4. Define failure modes, non-example cases, and interpretation boundaries.
5. Build synthetic generators with known truth for each component.
6. Write method specification and limitations matrix.

Validation checkpoints.

- Every definition has an executable example and counterexample.
- Synthetic truth cases include positive, negative, and ambiguous regimes.
- Existing APIs can represent each declared result or the gap is documented for later implementation.

Documentation updates.

- Method specification page.
- Synthetic truth case documentation.
- Limitations matrix.
- API stability notes if new stable objects are required.

Completion criteria.

- Formal definitions and synthetic examples pass tests.
- No method claim lacks an executable support path.

Stop condition.

- If a key method object cannot be represented in the current API, stop and decide whether to narrow the manuscript scope or reopen the API in a later authorized implementation phase.

## 7.2. Benchmark harness against baselines and alternatives

Stage 7.2 execution status. Complete as a benchmark-harness phase. The benchmark harness, retained output tables, baseline comparison report, performance and uncertainty report, tests, and gate report are recorded. This phase provided the prerequisite for the now-completed Stage 7.3 public signaling demonstrations.

Objectives.

- Compare RhoDyn to simpler summaries and relevant alternative approaches.
- Identify regimes where RhoDyn helps, where it is unnecessary, and where it is inconclusive.

Prerequisites.

- 7.1 complete.
- Synthetic generators and method definitions are stable.

Implementation order.

1. Implement or wrap baseline methods.
2. Define benchmark metrics for classification, estimation, calibration, runtime, memory, usability, and failure behavior.
3. Run synthetic benchmarks across declared regimes.
4. Run public fixture benchmarks where inputs are already available.
5. Write a benchmark report with positive, negative, and inconclusive cases.

Validation checkpoints.

- Baselines run on the same inputs as RhoDyn.
- Synthetic benchmark outcomes match known truth.
- Sensitivity to window choice, margins, grouping, and sample size is reported.
- Performance is measured on representative data sizes.

Documentation updates.

- Benchmark harness guide.
- Baseline comparison report.
- Performance and uncertainty report.

Completion criteria.

- At least one residence/amplitude disagreement with known truth is detected.
- At least one negative or inconclusive case is correctly bounded.
- Benchmark outputs are reproducible from a clean command sequence.

Stop condition.

- If benchmarks show no added value beyond amplitude or endpoint summaries, stop and re-evaluate the method claim before choosing biological demonstrations.

## 7.3. Independent public live-cell signaling demonstrations

Stage 7.3 execution status. Complete as an independent public live-cell signaling demonstration phase. The selected public-data adapters, tidy trajectory tables, residence-amplitude summaries, window sensitivity, grouped uncertainty, case reports, notebooks, tests, and gate report are recorded. This phase enabled the now-completed Stage 7.4 endpoint, reserve-like, and routed-output demonstration layer.

Objectives.

- Demonstrate residence-state inference in public live-cell signaling data outside the original manuscript logic.
- Preserve biological grouping and source-data transparency.

Prerequisites.

- 7.2 complete.
- Public dataset rubric approved.

Implementation order.

1. Rank candidate datasets by biological fit, metadata quality, access, and stress-test value.
2. Build adapters only for selected datasets.
3. Convert public data into tidy trajectory tables with provenance.
4. Run residence, amplitude, sensitivity, uncertainty, and reporting workflows.
5. Write case-study reports with scoped biological interpretation.

Validation checkpoints.

- Each dataset has source citation, access route, metadata, grouping, and preprocessing notes.
- Each case says what RhoDyn adds or why it does not add value.
- At least two biological systems beyond the original manuscript are represented.

Documentation updates.

- Public-data adapter docs.
- Case-study notebooks.
- Residence/amplitude benchmark tables.
- Interpretation notes.

Completion criteria.

- Two independent public live-cell systems pass reproducibility and interpretation gates.
- Examples do not imply that RhoDyn generated the RhoA/microglia manuscript results.

Stop condition.

- If public datasets cannot support clean grouping or time-resolved interpretation, stop and switch to a collaborator or held-out validation route rather than weakening the method claim.

## 7.4. Perturbation endpoint, reserve, and routed-output demonstrations

Objectives.

- Show that RhoDyn can support bounded coupling, reserve-like buffering, and routed-output model comparison beyond single-reporter trajectories.

Prerequisites.

- 7.3 complete.
- Benchmark harness supports endpoint and paired-reporter inputs.

Implementation order.

1. Select endpoint, reserve-like, or paired-reporter datasets using the Stage 7 rubric.
2. Build adapters and derived tidy tables.
3. Predeclare margins, grouping, and model alternatives where needed.
4. Run bounded-coupling, reserve, uncertainty, and reduced-architecture comparisons.
5. Write scoped case-study reports.

Validation checkpoints.

- Equivalence or bounded-coupling claims have declared margins and uncertainty.
- Model comparisons include reduced alternatives.
- Reserve-like labels are biologically scoped to the measurement actually present.

Documentation updates.

- Endpoint and reserve case-study docs.
- Margin and model-comparison reports.
- Reproducible notebooks or CLI workflows.

Completion criteria.

- At least one case demonstrates bounded coupling, reserve logic, or routed-output comparison in a way that is biologically interpretable and reproducible.

Stop condition.

- If non-trajectory data cannot distinguish model alternatives, report the failure as a method boundary and do not promote a routed-output claim.

## 7.5. External or held-out biological validation

Objectives.

- Test RhoDyn outside the author's fully controlled example-selection path.
- Preserve predeclared criteria and honest reporting of failures.

Prerequisites.

- 7.3 and 7.4 complete or explicitly scoped.
- External or held-out candidate data meet access and metadata criteria.

Implementation order.

1. Draft a held-out analysis plan with fixed windows, margins, baselines, and grouping where possible.
2. Ingest the dataset through documented schema checks.
3. Run the predeclared workflow.
4. Report the outcome as pass, fail, or inconclusive.
5. Decide whether the external case enters the methods-manuscript evidence set or remains a limitations note.

Validation checkpoints.

- No hidden tuning after seeing the result.
- Controlled-access constraints are clearly documented.
- Failure or inconclusive outcomes remain visible.

Documentation updates.

- Held-out analysis plan.
- External validation report.
- Controlled-access note if needed.

Completion criteria.

- One external or held-out analysis completes with reviewable outputs and a scoped interpretation.

Stop condition.

- If access restrictions prevent peer review or reproducibility, stop and choose a different validation route.

## 7.6. Software maturity for methods-paper reproducibility

Stage 7.6 execution status. Complete. The API stability policy, source-distribution clean-room runner, generated reproducibility card, gate reports, cross-surface parity table, workflow wiring, and methods-output comparison table are recorded. Stage 7.7 usability and adoption rehearsal is complete, and Stage 7.8 methods manuscript readiness has not started.

Objectives.

- Harden RhoDyn so every methods-paper result can be rerun and inspected.

Prerequisites.

- Demonstration and benchmark outputs from 7.2 through 7.5 exist.

Implementation order.

1. Define API stability and deprecation policy.
2. Add methods-paper fixtures and reproducibility commands.
3. Expand CI to run selected examples, docs, notebooks, benchmarks, package builds, Docker, and frontend regression.
4. Refresh documentation around method concepts, limitations, tutorials, and exports.
5. Run clean-room reproduction from a release archive.

Validation checkpoints.

- Fresh environment reproduces benchmark tables and tutorial outputs.
- Public release scan finds no local paths, secrets, raw private data, or manuscript-private files.
- Frontend, backend, CLI, and Python outputs agree for shared workflows.

Documentation updates.

- Methods-program reproducibility card.
- API stability policy.
- CI and clean-room reports.

Completion criteria.

- The methods-paper evidence set is reproducible from the declared release candidate.

Stop condition.

- If clean-room reproduction fails, do not begin usability rehearsal or manuscript readiness until the failure is repaired.

## 7.7. Usability and adoption rehearsal

Objectives.

- Test whether target users can obtain and interpret RhoDyn results without reading source code.

Prerequisites.

- 7.6 complete.
- Tutorials and workbench flows are stable.

Implementation order.

1. Define biologist and quantitative-user tasks.
2. Run the tasks on public tutorials and workbench flows.
3. Record failures, confusion points, and parameter-inspection needs.
4. Apply only fixes that preserve the analysis contract.
5. Re-run tasks after fixes.

Validation checkpoints.

- Biologist task reaches an interpretable residence/amplitude or bounded-coupling decision.
- Quantitative-user task reproduces the same output from CLI or Python.
- Exports include parameters, input schema, grouping, and software version.

Documentation updates.

- Usability protocol.
- User-path findings.
- Tutorial/workbench update notes if changed.

Completion criteria.

- User tasks pass without adding new unvalidated analysis routes.

Stop condition.

- If users cannot understand the result without source-code reading, improve the tutorial or interface before manuscript assembly.

## 7.8. Methods manuscript readiness package

Objectives.

- Freeze the evidence package needed to draft a high-impact methods manuscript.

Prerequisites.

- 7.1 through 7.7 complete or explicitly scoped.

Implementation order.

1. Build a figure-to-artifact crosswalk.
2. Build a claim-to-evidence crosswalk.
3. Assemble benchmark tables, biological demonstration reports, software reproducibility reports, and limitations matrix.
4. Freeze a release candidate for the methods manuscript.
5. Decide whether Nature Methods remains the primary target or a pivot venue better matches the evidence.

Validation checkpoints.

- Every planned manuscript figure maps to reproducible outputs.
- Every planned claim has a method definition, validation, and limitation.
- Data and code availability statements can identify repositories and persistent identifiers.

Documentation updates.

- Manuscript evidence index.
- Figure-to-artifact crosswalk.
- Claim-to-evidence crosswalk.
- Submission-readiness checklist.

Completion criteria.

- The project is ready to begin manuscript drafting without filling evidence gaps through prose.

Stop condition.

- If any central claim lacks reproducible evidence, stop and either run the missing validation or narrow the manuscript claim.

## Stage 8 handoff boundary

Stage 8 begins only after Stage 7 has produced a supported method statement. Commercial planning may use the Stage 7 evidence and software maturity surfaces, but it must not change the biological demonstrations, method claims, or manuscript evidence path.


Stage 7.4 execution status. Complete. The endpoint, reserve-like, and routed-output demonstration layer is recorded in `docs/stage7_4_gate_report.json` and `case_studies/stage7_endpoint_reserve_routing/`. Stage 7.5 external or held-out biological validation is complete and Stage 7.6 methods reproducibility is complete.


Stage 7.5 execution status. Complete. The held-out public validation layer is recorded in `docs/stage7_5_gate_report.json`, `docs/stage7_heldout_validation_report.md`, and `case_studies/stage7_heldout_validation/`. Stage 7.6 software maturity for methods-paper reproducibility is complete.


Stage 7.6 execution status. Complete. The methods-program reproducibility layer is recorded in `docs/stage7_6_gate_report.json`, `docs/stage7_methods_reproducibility_card.md`, `docs/stage7_6_api_stability_policy.md`, and `case_studies/stage7_methods_reproducibility/`. Stage 7.7 usability and adoption rehearsal is complete.


Stage 7.7 execution status. Complete. The usability and adoption rehearsal is recorded in `docs/stage7_7_gate_report.json`, `docs/stage7_usability_rehearsal.md`, `docs/stage7_user_path_findings.md`, and `case_studies/stage7_usability_rehearsal/`. The rehearsal checks a biologist-facing public MLCI residence interpretation path and a quantitative bounded-coupling reproduction path across Python, CLI, and backend outputs. Stage 7.8 methods manuscript readiness has not started and requires explicit authorization.

# Stage 10. Nature Methods EIC rescue and methodological-elevation roadmap

Stage 10 is a post-closure elevation program for the current RhoDyn Nature Methods package. It exists because the Stage 9.29 package is scientifically coherent but still vulnerable to a severe editorial reading as useful workflow/software integration rather than as a sufficiently distinctive Nature Methods-level method.

The goal is not to reassure the author team. The goal is to make the next EIC-facing version materially harder to desk reject by turning the three highest-risk weaknesses into explicit evidence tracks:

1. limited named-tool and named-baseline benchmarking;
2. small number of independent public biological demonstrations;
3. novelty being perceived as an integrated decision workflow rather than a mathematically and algorithmically distinctive method.

Stage 10 should not reopen Stage 9 prose polishing. It should produce new evidence, new comparison structure, and a stronger method identity before any second EIC contact.

## Executive verdict

The current package can be read as a credible computational-methods Article, but it is not yet protected enough against a skeptical Nature Methods editor who asks whether RhoDyn is more than a clean software/workflow integration. Stage 10 is the desk-rejection blockade program. It should be completed before asking the EIC to reconsider unless the communication is only a low-risk presubmission query.

## Primary method claim to earn

RhoDyn is a residence-state inference method for live-cell perturbation biology that formalizes when time spent inside a declared operating regime, margin-bounded reporter coupling, reserve-like endpoint preservation, or routed-output structure changes biological interpretation relative to endpoint, amplitude, threshold, generic time-series, and reduced-architecture baselines.

This is the primary reading.

The software/workflow reading remains true, but secondary. RhoDyn is software because the method must be inspectable, reproducible, and reusable. It is not submitted primarily as a software wrapper.

## Claim hierarchy after Stage 10

| Claim layer | Desired reading | Evidence required | Claims to avoid |
| --- | --- | --- | --- |
| Primary | RhoDyn introduces a reviewable residence-state decision method. | Formal method object, mathematical decision function, named baselines, synthetic truth, public biological breadth, held-out validation. | RhoDyn is just a toolkit that bundles summaries. |
| Secondary | RhoDyn is mature software implementing the method. | Python, CLI, backend, workbench, exports, tests, GitHub, Zenodo, checksums. | Software maturity alone is the scientific advance. |
| Biological | RhoDyn reveals where dynamic operating-state structure changes interpretation. | Multiple systems with positive, negative, and inconclusive outcomes. | Every live-cell system has a residence regime. |
| Boundary | RhoDyn withholds unsupported calls. | Explicit fail and inconclusive cases. | RhoDyn discovers mechanisms automatically. |

## Stage 10 phase table

| phase | goal | work to execute | expected outputs | gate |
| --- | --- | --- | --- | --- |
| 10.0 | Freeze rescue objective and no-contact rule. | Record that no second EIC request should be sent until the Stage 10 evidence gates close or a deliberately limited presubmission note is approved. | `docs/stage10_nature_methods_eic_rescue_roadmap.md`; updated roadmap memory. | Stage 10 begins as a post-closure evidence program, not a Stage 9 wording pass. |
| 10.1 | Define the upgraded mathematical method object. | Formalize a decision object that links residence windows, amplitude comparators, abstention, bounded coupling, reserve-like endpoints, routed-output alternatives, and uncertainty into one method-level inference object. | `docs/stage10_method_object_v2.md`; executable fixtures; API gap list. | Every mathematical definition has an executable positive, negative, and ambiguous example. |
| 10.2 | Build named-baseline and named-tool benchmarking. | Compare RhoDyn against amplitude, endpoint, AUC, peak, latency, threshold, tsfresh/catch22-style feature summaries, sktime/ROCKET-style classifiers where appropriate, changepoint/HMM-style state summaries, and reduced-architecture baselines. | Benchmark runner; baseline wrappers; results tables; runtime/memory table; failure-boundary report. | At least three named external baseline families plus internal simple summaries are evaluated on common synthetic and public inputs. |
| 10.3 | Expand independent public biological demonstrations. | Add at least two additional public live-cell or perturbation systems beyond current DRG calcium and ERK examples, prioritizing NF-kB, p53, kinase, calcium, optogenetic Rho-family, or multiplexed reporter datasets with usable metadata. | Public adapters, retained derived tables, notebooks, case reports, source DOI/access ledger. | At least four total independent public systems, at least three biological domains, and at least one negative or amplitude-sufficient case. |
| 10.4 | Add a blinded or held-out challenge route. | Seal thresholds/margins on training examples, then evaluate held-out public contexts or collaborator-provided tables without retuning. | Predeclaration file; held-out report; pass/fail/inconclusive table. | RhoDyn must preserve at least one positive, one negative, and one inconclusive call without hidden tuning. |
| 10.5 | Convert benchmarking into manuscript figure architecture. | Rebuild the Nature Methods figure spine around method novelty, named-baseline benchmarking, biological breadth, held-out validation, and software reproducibility. | Revised figure-spine blueprint and PanelForge manifest plan. | First three figures must make method novelty and performance visible before software maturity appears. |
| 10.6 | Rehydrate manuscript prose around method superiority and boundaries. | Rewrite title, Abstract, cover-letter paragraph, Results openers, Discussion landing, and limitations to lead with method-level advance and named-comparator evidence. | Stage 10 manuscript delta draft; presubmission pitch v2. | A two-minute editor can identify the method object, comparator set, biological breadth, and non-claims without reading the SI. |
| 10.7 | Release a benchmark-ready RhoDyn version. | Prepare a benchmark evidence release, versioned case-study bundle, and clean-room reproduction route for Stage 10 outputs. | Release candidate tag, archive manifest, command index, benchmark checksum table. | A fresh clone can reproduce all Stage 10 benchmark and case-study outputs. |
| 10.8 | Run adversarial editorial simulation before EIC contact. | Simulate Nature Methods EIC, methods editor, computational reviewer, live-cell biologist, statistician, and software reviewer. | Red-team report and action matrix. | No high-severity desk-rejection risk remains unresolved; any remaining risk is explicitly accepted by the PI. |
| 10.9 | Decide EIC-contact route. | Choose full submission, presubmission query, delay for another dataset, or pivot venue. | EIC-contact decision memo and final one-page pitch. | Send only if the expected desk-negative risk is materially lower than the Stage 9.29 estimate. |

## Stage 10.1 mathematical elevation

The upgraded method object must make RhoDyn read as a method rather than only as a workflow. The minimum formal object should include:

- an input object for trajectory, paired-reporter, and endpoint perturbation tables;
- a declared operating-window family rather than a single hand-picked threshold;
- residence summaries and amplitude comparators defined on the same observations;
- a decision-divergence quantity showing when residence changes interpretation relative to amplitude;
- an abstention rule when windows, uncertainty, grouping, or margins do not support a call;
- bounded-coupling decision rules with margin and uncertainty components;
- reserve-like endpoint coordinates tied to measured endpoints;
- routed-output comparison against reduced alternatives;
- a decision report object that serializes pass, fail, inconclusive, assumptions, parameters, and reproducibility fields.

Candidate mathematical centerpiece:

\[
D_{\mathrm{RhoDyn}}(x; W, B) =
\mathcal{I}_{\mathrm{residence}}(x, W) -
\mathcal{I}_{\mathrm{baseline}}(x, B),
\]

where \(W\) is a declared residence-window family and \(B\) is a declared comparator family such as endpoint, peak, mean, AUC, threshold occupancy, latency, or generic time-series features. The value is not a biological mechanism. It is a decision divergence that indicates whether residence changes the interpretation relative to the chosen comparator under uncertainty and predeclared failure rules.

Stage 10 should refine this into the exact notation supported by the API. If the current API cannot express the method object, the implementation must stop and either narrow the method claim or authorize an API expansion.

### Stage 10.1 completion update

Stage 10.1 is now implemented as an additive public method-object layer. The formal specification is `docs/stage10_method_object_v2.md`, the API gap list is `docs/stage10_1_api_gap_list.md`, the executable runner is `scripts/run_stage10_1_method_object_v2.py`, and the fixture outputs are under `case_studies/stage10_method_object_v2/`.

The completed fixture set contains positive, counterexample, and ambiguous decisions for trajectory residence-versus-comparator divergence, bounded coupling, reserve-like endpoints, and routed-output model comparison. This makes the method object reviewable as a decision structure while preserving the biological boundary that decision divergence is not a mechanism-discovery statistic and does not imply that every live-cell system has a residence regime.

### Stage 10.2 completion update

Stage 10.2 is now implemented as a named-baseline benchmark surface. The executable runner is `scripts/run_stage10_2_named_benchmarking.py`, the documentation page is `docs/stage10_2_named_benchmarking.md`, and the benchmark outputs are under `case_studies/stage10_named_benchmarks/`.

The completed benchmark evaluates RhoDyn against internal simple summaries plus SciPy signal peak detection, scikit-learn feature classification, hmmlearn state summaries, catch22-style, tsfresh-style, MiniROCKET-style, and ruptures-style comparator families. The gate report passes with seven named external-style families and three direct optional package families available in the current runtime. The benchmark deliberately reports that generic feature methods can match the synthetic labels in this fixture. That result defines where classifier-like summaries may be sufficient and where RhoDyn's declared residence-state decision object remains more interpretable.

Stage 10.2 does not add a new biological system. The DRG calcium and ERK GPCR public inputs are included as shared-input comparator summaries, not as new truth-labeled evidence of method superiority.

### Stage 10.3 completion update

Stage 10.3 is now implemented as an expanded public biological breadth surface. The executable runner is `scripts/run_stage10_3_public_biological_breadth.py`, the documentation page is `docs/stage10_3_public_biological_breadth.md`, and the breadth outputs are under `case_studies/stage10_public_breadth/`.

The completed breadth matrix counts four independent public systems across live-cell calcium dynamics, GPCR-linked ERK trajectories, perturbation endpoint morphology and cell-health profiling, and microbial live-cell tracking. It adds Cell Painting/MitoTox and MLCI tracking as public systems beyond the earlier DRG and ERK trajectory examples. It also retains ERK/AKT bounded-coupling evidence as method support while not counting it as another independent public system because it shares the Wan source family. A public Birtwistle ERK/AKT cell-division source was verified as readable but deferred because no explicit repository license was detected, so no derivative table is retained and it is not counted as release-ready evidence.

Stage 10.3 reduces the biological-breadth vulnerability. It does not show that every live-cell system has a residence regime and does not remove the need for Stage 10.4 held-out validation.

### Stage 10.4 completion update

Stage 10.4 is now implemented as a sealed held-out validation route. The executable runner is `scripts/run_stage10_4_heldout_validation.py`, the documentation page is `docs/stage10_4_heldout_validation.md`, and the held-out outputs are under `case_studies/stage10_heldout_validation/`.

The completed challenge writes a predeclaration before interpreting the Stage 10.4 output tables, then evaluates retained public-derived contexts without retuning. It preserves a positive residence/amplitude divergence call in held-out MLCI tracking, a negative or comparator-sufficient boundary in held-out ERK GPCR dynamics, a positive ERK/Akt bounded-coupling held-out call, and an inconclusive ERK/Akt margin-boundary call. This strengthens the method-level reading because RhoDyn is shown as a rule-preserving decision method that can pass, withhold, or report comparator sufficiency under fixed settings.

Stage 10.4 does not replace a prospective blinded collaborator study. It is a sealed replay over public-derived tables and should be described as no-retuning held-out validation rather than as universal external validation.

### Stage 10.5 completion update

Stage 10.5 is now implemented as a method-first Nature Methods figure architecture. The executable runner is `scripts/run_stage10_5_figure_architecture.py`, the documentation page is `docs/stage10_5_method_first_figure_architecture.md`, the active Stage 10 figure spine is `manuscript/nature_methods/figures/stage10_5_method_first_figure_spine.md`, and the panel-evidence crosswalk is `manuscript/nature_methods/figures/stage10_5_panel_evidence_crosswalk.csv`.

The completed architecture uses six main figures. Figure 1 defines the RhoDyn method object and decision divergence. Figure 2 displays named-baseline benchmarking and comparator boundaries. Figure 3 shows public biological breadth across four counted independent public systems. Figure 4 extends the method to endpoint, reserve-like, bounded-coupling, and routed-output decisions. Figure 5 shows sealed held-out validation with positive, comparator-sufficient, and inconclusive outcomes. Figure 6 then shows software parity, archive reproduction, and user-path support. This ordering moves the method and validation evidence before software maturity.

Stage 10.5 does not add new biological evidence, does not render new PanelForge figures, and does not replace the historical Stage 9 rendered mockups. It is the figure-architecture bridge that should control the next PanelForge rebuild and the Stage 10.6 manuscript-pitch transformation.

### Stage 10.6 completion update

Stage 10.6 is now implemented as the method-first manuscript and editor-pitch transformation. The executable runner is `scripts/run_stage10_6_manuscript_pitch.py`, the documentation page is `docs/stage10_6_manuscript_pitch_transformation.md`, the gate report is `case_studies/stage10_manuscript_pitch/stage10_6_gate_report.json`, and the draft manuscript/pitch surfaces are under `manuscript/nature_methods/stage10_6/`.

The preferred title is `Residence-state inference for live-cell perturbation data`. The abstract now names named baseline families, four public demonstration systems, sealed held-out positive, comparator-sufficient, and inconclusive outcomes, and the reproducible Python, command-line, API, workbench, and archive surfaces. The Results route follows the Stage 10.5 method-first figure architecture, with the method object, named baselines, public biological breadth, endpoint and routed-output extensions, held-out validation, and only then software reproducibility. This change is a presentation and pitch transformation only. It does not add biological data, benchmark results, rendered figures, or software capabilities.

### Stage 10.7 completion update

Stage 10.7 is now implemented as a benchmark-ready release-candidate package. The executable runner is `scripts/run_stage10_7_benchmark_release_candidate.py`, the documentation page is `docs/stage10_7_benchmark_release_candidate.md`, and the release-candidate outputs are under `case_studies/stage10_release_candidate/`.

The completed package records a fresh-clone command index for Stages 10.1 through 10.6, a checksum manifest over the registered Stage 10 evidence surfaces, an archive manifest, a gate report, and a short release-candidate brief. This stage does not add biological data, benchmark results, rendered figures, or manuscript claims. Its purpose is to make the Stage 10 method-elevation evidence replayable before adversarial EIC red-team review.

## Stage 10.2 named benchmarking ladder

The named benchmarking track must be explicit enough that a methods editor does not see only self-comparison against simple summaries.

### Baseline classes

| baseline class | examples | role | direct benchmark? |
| --- | --- | --- | --- |
| Simple summaries | endpoint, peak, mean, AUC, latency, threshold occupancy | Minimum comparator set for all examples. | yes |
| Time-series features | catch22/pycatch22, tsfresh-style features | Tests whether generic features can match RhoDyn decisions without declared biological windows. | yes, where installable and data-compatible |
| Time-series classifiers | sktime/ROCKET or MiniROCKET-style features | Tests predictive utility when labels exist. | yes, for labeled synthetic and public examples |
| State segmentation | ruptures changepoint, Gaussian HMM/hmmlearn-style summaries | Tests whether unsupervised state segmentation substitutes for declared residence. | yes, when time density supports it |
| Reduced architecture | one-dimensional, endpoint-only, morphology-only, coupling-only, route-collapsed alternatives | Tests routed-output and endpoint claims. | yes |
| Non-comparable methods | CellRank, scVelo, Squidpy, Cellpose, DeepLabCut | Prior-art positioning and scope contrast. | no direct benchmark unless data object matches |

### Benchmark gates

- RhoDyn must beat or uniquely complement simple amplitude summaries in known-truth residence regimes.
- RhoDyn must not overcall when amplitude summaries are sufficient.
- Named feature-based baselines must be reported even when they perform well.
- Any "win" must specify metric and context.
- If named baselines outperform RhoDyn in a regime, that regime becomes a boundary, not a hidden result.
- Runtime and memory must be reported on representative table sizes.

## Stage 10.3 public biological demonstration expansion

The current public evidence contains DRG calcium, ERK GPCR, ERK/Akt, and Cell Painting/MitoTox-derived endpoints. This is useful but still vulnerable to the editorial critique that biological breadth is thin. Stage 10 should expand breadth deliberately, not opportunistically.

### Candidate systems

| target system | desired source type | why it matters | acceptance condition |
| --- | --- | --- | --- |
| NF-kB/p65 nuclear translocation | public live-cell single-cell trajectories | Immune/inflammatory signaling domain, different dynamics from calcium/ERK. | source license, metadata, time, condition, and cell/replicate identifiers recoverable |
| p53 stress pulses | public live-cell reporter trajectories | Canonical dwell/pulse/amplitude biology with non-monotonic timing. | enough sampling density to evaluate residence or pulse-state windows |
| additional calcium system | public live-cell trajectories in non-neuronal context | Tests whether calcium example is not only DRG-specific. | grouping and stimulus conditions recoverable |
| kinase or Rho-family reporter | public KTR/FRET/optogenetic trajectory data | Closest to RhoDyn's live-cell signaling target. | trajectory table recoverable without private raw imaging |
| perturbation endpoint screen | public Cell Painting, Cell Health, or multiplexed endpoint data | Strengthens endpoint/reserve/routed-output claims. | endpoints support reduced alternatives and measurement-scoped reserve-like coordinate |

### Biological breadth gates

- At least four independent public systems total.
- At least three biological domains, for example neuronal calcium, kinase signaling, inflammatory signaling, DNA damage/stress signaling, or phenotypic endpoint screening.
- At least one system where residence adds value.
- At least one system where amplitude or endpoint summaries are sufficient.
- At least one system where RhoDyn withholds interpretation.
- No use case may imply RhoDyn generated the RhoA/microglia manuscript.

## Stage 10.4 held-out validation

The held-out layer is now implemented as a sealed public-derived replay with predeclared rules. Future work can make it stronger by adding a prospective collaborator-blind table, but the current Stage 10.4 gate already records whether fixed settings preserve positive, negative, and inconclusive calls.

Minimum held-out design:

1. choose one public live-cell dataset with multiple ligands, inhibitors, doses, or batches;
2. predeclare residence windows and comparator families on a training subset;
3. lock the parameters in a JSON file;
4. apply to held-out contexts;
5. record pass, fail, and inconclusive outcomes;
6. report whether conclusions are stable under window and margin sensitivity.

Gate. The current gate passes because the output includes positive, negative or comparator-sufficient, and inconclusive decisions under fixed rules. If a later prospective held-out expansion collapses, the manuscript should narrow to demonstrated contexts or delay the EIC contact.

## Stage 10.5 revised Nature Methods figure spine

The Stage 9 figure spine is coherent but too balanced between method, examples, and software. Stage 10.5 makes the first half of the figure sequence unmistakably methodological and validation-driven.

| figure | completed editorial job | key panels |
| --- | --- | --- |
| Fig. 1 | Define the RhoDyn method object and decision divergence. | input objects, decision divergence, executable positive/negative/ambiguous fixtures, abstention and failure modes |
| Fig. 2 | Show synthetic truth and named-baseline benchmarking. | known-truth regimes, named comparator families, accuracy and boundary outcomes, public-input comparator summaries, runtime |
| Fig. 3 | Demonstrate public biological breadth. | public system matrix, DRG calcium, ERK GPCR, Cell Painting/MitoTox, MLCI tracking, source eligibility |
| Fig. 4 | Demonstrate endpoint, reserve-like, bounded-coupling, and routed-output extension. | endpoint schema, bounded coupling, reserve-like endpoint, routed alternatives, measurement-scope limits |
| Fig. 5 | Show held-out validation and uncertainty boundaries. | predeclared settings, held-out decision table, object-level calls, no-hidden-tuning gates, prospective-validation boundary |
| Fig. 6 | Show reproducibility and user adoption. | Python/CLI/API/workbench parity, export bundles, clean-room reproduction, archive checksums, user-path rehearsal |

The software figure remains essential but moves after the method and validation evidence have already established the advance.

## Stage 10.6 manuscript-pitch transformation

The Stage 10 manuscript should pivot from:

"RhoDyn integrates residence scoring, coupling, reserve-like endpoints, model comparison, and software surfaces"

to:

"RhoDyn defines a residence-state decision object that exposes when dynamic operating-state interpretation changes relative to named baseline and competing summaries across synthetic truth, public biological systems, held-out contexts, and endpoint perturbation designs."

Required prose changes after evidence is generated:

- Title must contain "method" or "inference" plus the data class.
- Abstract must mention named baselines and multiple biological domains.
- Introduction must position the missing method as a decision problem, not a convenience workflow.
- Results must lead with mathematical object and benchmark performance before software.
- Discussion must state where RhoDyn does not beat simpler summaries.
- Cover letter must lead with named-comparator validation and biological breadth.

## Stage 10.7 release and reproducibility upgrade

Stage 10 should produce a benchmark-ready release candidate rather than only manuscript-support files.

Required release surfaces:

- benchmark command index;
- named-baseline dependency lock;
- derived public-data table manifest;
- held-out predeclaration JSON files;
- benchmark checksum table;
- runtime and memory report;
- clean-room reproduction report;
- documentation page titled "Benchmarking RhoDyn against baseline methods";
- documentation page titled "Public biological demonstrations".

Gate. A reviewer must be able to reproduce all Stage 10 benchmark and case-study tables from a fresh clone or archived release.

## Stage 10.8 adversarial EIC simulation

Before any EIC contact, run a six-perspective red team:

1. Nature Methods EIC;
2. methods editor;
3. computational methods reviewer;
4. live-cell signaling biologist;
5. statistician/benchmarking reviewer;
6. software reproducibility reviewer.

Required verdict categories:

- desk-reject likely;
- presubmission only;
- full submission viable;
- delay for another dataset;
- pivot venue.

The EIC-contact gate passes only if no reviewer gives an unresolved high-severity desk-reject risk for novelty, validation breadth, named benchmarking, or overclaiming.

## Stage 10.9 EIC-contact decision rule

Do not ask the EIC to "take another look" at the old paper. If contact is made, it should be a new, concise presubmission-style note framed around the Stage 10 evidence.

Minimum EIC-safe message:

- one sentence defining the method advance;
- one sentence naming the comparator classes;
- one sentence naming public biological breadth;
- one sentence naming held-out validation;
- one sentence naming software/reproducibility;
- one sentence naming limits and why the work is not a biology-only manuscript.

If Stage 10 cannot produce stronger named benchmarking and at least two additional public biological demonstrations, the safer route is to delay or pivot rather than risk a second informal negative EIC read.

## Stop and pivot conditions

| trigger | implication | decision |
| --- | --- | --- |
| No suitable additional public live-cell systems can be recovered. | Biological breadth remains vulnerable. | Do not re-ask EIC; either delay or submit elsewhere. |
| Named baselines match or outperform RhoDyn in most positive regimes. | Novel method claim weakens. | Reframe as niche decision/reporting tool or pivot venue. |
| RhoDyn only wins after post hoc window tuning. | Method claim becomes unsafe. | Add predeclaration/held-out design or stop. |
| Held-out validation is mostly inconclusive. | Generality claim too weak. | Narrow claims or add more datasets. |
| Runtime or usability is poor relative to baselines. | Practical relevance weakens. | Harden implementation before submission. |
| Red team still sees software wrapper first. | EIC risk remains high. | Rebuild title, Abstract, Fig. 1, and cover letter before contact. |

## Immediate next commands

These are planning commands only. They should be run after Stage 10 implementation scripts are created.

```bash
python3 scripts/run_stage10_1_method_object_v2.py
python3 scripts/run_stage10_2_named_benchmarking.py
python3 scripts/run_stage10_3_public_biological_breadth.py
python3 scripts/run_stage10_4_heldout_validation.py
python3 scripts/run_stage10_5_figure_architecture.py
python3 scripts/run_stage10_6_manuscript_pitch.py
python3 scripts/run_stage10_7_benchmark_release_candidate.py
python3 scripts/run_stage10_8_eic_red_team.py
python3 scripts/check_release.py
```

## Reflection update

Stage 9.29 closure remains valid for the current package, but it should not be treated as the safest basis for a second EIC approach. Stage 10 is now the active scientific-methods elevation program. It is justified because the remaining risk is not manuscript grammar or package completeness. The remaining risk is whether the method is seen as a Nature Methods-level advance. Stages 10.1 through 10.7 have now strengthened the mathematical method object, named benchmarking, public biological breadth, no-retuning held-out validation, method-first figure architecture, method-first manuscript/pitch surfaces, and benchmark-ready replay packaging. The next risk is adversarial editorial review, where the package must be stress-tested as a Nature Methods submission rather than as a software workflow.

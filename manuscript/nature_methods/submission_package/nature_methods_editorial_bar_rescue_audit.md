# Nature Methods editorial-bar rescue audit

This is a severe pre-submission triage and rescue audit for the current RhoDyn Nature Methods package. It does not add new analyses, figures, datasets, citations, performance results, manuscript claims, reviewer names, conflicts, declarations, or portal metadata. Its purpose is to keep the submission aligned with the Nature Methods Article bar before human upload.

Source basis. The audit applies the Nature Methods content-type statement that an Article describes a novel method or tool with strong validation for performance, reproducibility, general applicability, and potential for discovering new biology. It also applies Nature Portfolio reporting expectations for availability of data, materials, code, and protocols, and the Nature Methods guidance for algorithms and software requiring accessible source code, documentation, sample data or expected outputs where appropriate, dependencies, version information, licensing, restrictions, and sufficient algorithmic description.

## 1. Executive Summary

The current package nearly clears the Nature Methods editorial bar only if it is read as a methods Article about a reusable residence-state decision framework. It would remain desk-rejection-prone if framed as a RhoA/microglia biology paper, a software wrapper around known summaries, or a broad claim that residence is always superior to amplitude. The rescue path is not to inflate novelty. The defensible elevation is to keep the method object visible within the first two minutes, preserve the validation ladder across synthetic truth, public live-cell reporters, endpoint demonstrations, held-out contexts, and software parity, and keep all negative or inconclusive decisions explicit.

The dominant EIC-style concern is a communication and validation-visibility problem, with a secondary benchmarking problem. The package now has enough reproducibility and generality evidence for collaborator and PI review, but it should not be submitted with language that hides the comparator baselines, over-centers the biological reference use case, or implies automatic state discovery.

## 2. Nature Methods Bar Assessment

| Nature Methods requirement | Current evidence | Weakness under severe triage | Risk | Required rescue position |
| --- | --- | --- | --- | --- |
| Novel method or tool | Title, Abstract, Figure 1, Methods, prior-art matrix, and cover letter define RhoDyn as residence-state inference for live-cell perturbation data. | Editors may see integration rather than invention if the decision object is not named immediately. | medium | Lead with RhoDyn as an executable decision framework, not as general dynamic-signaling commentary. |
| Full technical description | Online Methods define schemas, residence windows, amplitude comparators, bounded coupling, reserve-like endpoints, routed-output comparison, and reproducibility surfaces. | Methods must stay declarative enough that users can reproduce decisions without reading code first. | low | Preserve input-output definitions, failure modes, margins, and grouping rules. |
| Performance validation | Synthetic truth cases, reduced alternatives, public demonstrations, held-out contexts, margin sensitivity, and inconclusive cases are present. | Direct competitor-tool benchmarking is not the central evidence. | medium | Present amplitude, endpoint, peak, mean, latency, threshold, reduced architectures, and withheld outcomes as the fair comparators for this method object. |
| Reproducibility | GitHub, Zenodo, command index, tests, checksums, source distribution, public data, expected outputs, backend/workbench parity, and PanelForge DOI are present. | Human Reporting Summary and portal metadata remain external. | low | Keep the package as reproducible evidence and complete official forms before upload. |
| General applicability | Public calcium, ERK, ERK/Akt, Cell Painting/MitoTox, held-out, and synthetic settings are present. | Generality is demonstrated as method portability, not as universal biology. | medium | State that RhoDyn travels across input classes and reporters while preserving amplitude-sufficient and unresolved cases. |
| Potential for discovering new biology | Method exposes residence-amplitude divergence, bounded coupling, reserve-like endpoint structure, and routed-output alternatives that simpler summaries can miss. | Discovery potential could be overread as mechanism discovery. | medium | Frame biological discovery as capability gain under scoped inputs, not automatic mechanism identification. |
| Soundness of conclusions | Boundaries state declared windows, margin-limited equivalence, measured endpoint scope, and effective-parameter limits. | Claims can become unsafe if cover-letter or title drifts. | low | Preserve boundary language throughout upload. |
| Appropriate data and analyses | Source-data/statistics inventory maps figures to public-derived and synthetic evidence; Methods define decision rules. | Optional RhoA/microglia reference use case must not become hidden evidence. | low | Keep public/synthetic/package evidence as the Article support. |
| Wide relevance | Live-cell perturbation data, endpoints, screening, reporter dynamics, and reproducible software users are all named. | Relevance is broad only if the title and abstract do not read as a niche cell-biology use case. | medium | Keep the method title and method-first abstract. |
| Code/data/software availability | Code/data availability, software checklist, public-access verification, and DOI records are present. | Official upload forms remain author-confirmed. | low | Use final upload runbook. |

## 3. Top Desk-Rejection Risks

| Rank | Risk | Root cause | Why it matters at editorial triage | Current rescue |
| --- | --- | --- | --- | --- |
| 1 | The paper is read as a software wrapper rather than a method. | Methodological identity. | Nature Methods needs a method or tool with a capability gain, not only a packaged implementation. | Title, Abstract, Figure 1, cover letter, and editor note define the decision object. |
| 2 | Novelty is mistaken for the broad claim that dynamics matter. | Novelty positioning. | Prior art already establishes dynamic-state analysis and live-cell trajectory value. | Prior-art matrix states that RhoDyn contributes the operational decision workflow, not first-in-field dynamic analysis. |
| 3 | Validation looks narrow or case-study dominated. | Generality and benchmark visibility. | Editors may reject if RhoDyn appears supported only by a motivating biological system. | Validation ladder foregrounds synthetic truth, public reporters, endpoint demonstrations, held-out contexts, and software parity. |
| 4 | Bounded-coupling or reserve language sounds mechanistic. | Evidence/conclusion mismatch. | Overclaiming can trigger desk rejection even when the method is useful. | Methods, legends, Discussion, and runbook keep margins, measured endpoints, and effective parameters scoped. |
| 5 | Human upload requirements are incomplete. | Reporting/package action. | Technical return or editorial hesitation can occur if forms and declarations are incomplete. | Reporting Summary answer bank, declarations files, reviewer/editor planner, and final upload runbook retain these as human actions. |

## 4. Root Cause Diagnosis

The EIC concern is mostly a communication plus validation-visibility problem, not a fatal reproducibility-package problem. It is also partly a benchmarking problem because the comparator set is summary-level and decision-level rather than a standard leaderboard against named software tools. It is not currently a true manuscript-scope failure if the submission remains a computational methods Article and the cover letter preserves the validation ladder. It would become a scope failure if the RhoA/microglia reference use case or broad biological promise displaced the method object.

## 5. One-Sentence Nature Methods Advance

RhoDyn turns residence-state interpretation of live-cell perturbation data into an executable, uncertainty-aware decision framework that tests when dwell within declared biological windows, bounded coupling, reserve-like endpoint structure, or routed-output alternatives change interpretation relative to amplitude or endpoint summaries, while preserving amplitude-sufficient and unresolved cases.

Support verdict. The current package supports this sentence through the main text, six-figure spine, Methods, source-data/statistics inventory, public-derived examples, held-out contexts, software parity, and reproducibility surfaces. It would not support a stronger sentence claiming automatic state discovery, universal residence regimes, or direct mechanism discovery.

## 6. Method Identity Paragraph

RhoDyn is a computational method for live-cell perturbation and endpoint data. It takes tidy trajectory tables or paired endpoint tables with declared windows, contrasts, margins, grouping fields, and readout labels. It returns residence summaries, amplitude comparators, bounded-coupling decisions, reserve-like endpoint coordinates, routed-output model comparisons, uncertainty summaries, figure-ready outputs, reports, and explicit withheld decisions. The new technical operation is not any single statistic. It is the integration of declared residence windows, amplitude baselines, equivalence-style coupling margins, endpoint-coordinate boundaries, reduced-architecture tests, and reproducible export surfaces into one reviewable decision object for perturbation biology. The method unlocks the ability for biologists and quantitative users to ask whether dynamic operating-state structure changes interpretation relative to simpler summaries without converting every positive call into a mechanism.

## 7. Nature Methods Requirement Matrix

| Requirement | Current evidence | Current weakness | Desk-rejection risk | Required elevation | Can fix now with existing material? | Requires new analysis? | Requires new data? |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Novel method/tool | Method-first title, Abstract, Fig. 1, Methods, prior-art matrix | Integration could seem incremental | medium | Keep decision-object language in all triage surfaces | yes | no | no |
| Full technical description | Online Methods and Supplementary Information | Could be overlooked if editor reads only Abstract/Fig. 1 | low | Keep Fig. 1 and cover letter explicit | yes | no | no |
| Performance validation | Synthetic truth, reduced alternatives, held-out contexts | No named-tool leaderboard | medium | Present comparators as amplitude/endpoint/reduced-architecture baselines and list optional future direct tool benchmark | yes | optional | no |
| Reproducibility | GitHub, Zenodo, checksums, tests, commands, sample data | Official forms incomplete | low | Complete human upload actions | partly | no | no |
| General applicability | Public calcium, ERK, endpoint, paired reporter, held-out cases | Could be under-read as examples rather than validation | medium | Keep validation ladder visible in cover letter and first figure sequence | yes | no | no |
| Discovery potential | Residence/amplitude divergence and endpoint decision examples | Biological novelty is scoped | medium | Frame as capability gain enabling biological questions | yes | no | no |
| Soundness | Boundaries and withheld decisions visible | Wording drift can overclaim | low | Preserve limitations and final runbook stop checks | yes | no | no |
| Appropriate evidence | Source-data/statistics inventory and public-derived data | Optional reference use case must not dominate | low | Keep Article evidence public/synthetic/package-based | yes | no | no |
| Wide relevance | Live-cell perturbation and endpoint scope | Title/abstract must stay broad | medium | Keep current method title | yes | no | no |
| Code/data/software | Public release and DOI records | Human forms and author metadata remain | low | Complete official Reporting Summary and declarations | partly | no | no |

## 8. Novelty Ledger

| Claimed advance | Closest prior art | Actual differentiator | Magnitude | Current support | Required elevation | Verdict |
| --- | --- | --- | --- | --- | --- | --- |
| Residence-state inference as a reviewable decision object | Dynamic-state and trajectory-inference methods | Declared dwell metrics compared directly with amplitude baselines for live-cell perturbation tables | moderate to strong | Fig. 1-3 and Methods | Keep method object explicit | strong |
| Bounded-coupling decisions in the same workflow | Equivalence/TOST and statistical decision frameworks | Margin-declared pass, fail, and inconclusive coupling outcomes exported with context | moderate | Fig. 4-5 and Methods | Avoid "no coupling" language | moderate |
| Reserve-like endpoint summaries | Endpoint modeling and phenotypic profiling | Measurement-scoped buffering coordinate integrated with uncertainty and boundaries | moderate | Fig. 4 and Methods | Keep "reserve-like" measured-endpoint scope | moderate |
| Routed-output reduced-architecture comparison | Model comparison and endpoint fitting | Reduced alternatives tied to perturbation readouts without claiming biochemical edges | moderate | Fig. 4 and SI | Do not over-mechanize | moderate |
| Cross-surface reproducibility | Software-release best practice | Python, CLI, backend, workbench, export bundle, source distribution, checksums, DOI records | practical and strong | Fig. 6, code-for-review, software checklist | Keep as method reviewability, not the novelty itself | strong |
| Broad biological discovery | Live-cell biology and perturbation methods | Method can reveal when residence or endpoint structure changes interpretation | context-limited | Public and held-out examples | Do not claim universal biology | moderate |

## 9. Comparator Ledger

| Comparator class | Closest comparison | What RhoDyn does better | What RhoDyn does not do better | Improvement type | Nature Methods strength |
| --- | --- | --- | --- | --- | --- |
| Endpoint, peak, mean, latency, threshold summaries | Standard live-cell analysis summaries | Tests whether dwell in a declared window changes interpretation | Does not replace these summaries when they are sufficient | quantitative and practical | strong if shown beside positive and negative cases |
| Trajectory inference/state-space methods | Saelens, CellRank, transient-state models, state-space visualization | Provides a narrower perturbation-decision workflow for tidy live-cell reporter data | Does not infer fate direction or discover states automatically | conceptual and practical | moderate |
| Live-cell morphodynamic embeddings | Live-cell trajectory embedding literature | Adds declared residence and endpoint decision rules rather than general embedding | Does not provide a new imaging segmentation model | conceptual | moderate |
| General software workbenches | Cellpose, Squidpy, scvi-tools, DeepLabCut | Provides a focused dynamic operating-state interpretation workflow | Does not compete as a general segmentation/spatial/omics platform | practical | moderate |
| Equivalence/statistical decision tools | TOST/ROPE-style frameworks | Embeds bounded-coupling decisions in perturbation data workflow with withheld outcomes | Does not invent equivalence testing | integration and reporting | moderate |

## 10. Minimum Elevation Package

| Category | Required before submission | Current state | Priority |
| --- | --- | --- | --- |
| Immediate manuscript rewrites | Keep current title, method-first Abstract, Fig. 1 method-object logic, and final Discussion boundaries. Do not revert to biology-first framing. | implemented | critical |
| New analysis from existing data | No mandatory new analysis if the current validation ladder remains intact. Optional high-value addition would be a compact runtime/scalability table on existing examples. | optional | medium |
| Public dataset or semi-synthetic validation | Current public calcium, ERK, ERK/Akt, Cell Painting/MitoTox, synthetic truth, and held-out contexts are sufficient for submission-readiness. | implemented | critical |
| Benchmark/comparator additions | Keep amplitude, endpoint, reduced-architecture, and withheld-outcome comparators visible. Optional addition is a named-feature baseline comparison if editors request more benchmarking. | mostly implemented | medium |
| Software/reproducibility additions | Complete official Reporting Summary and declarations; keep GitHub/Zenodo/PanelForge URLs verified immediately before upload. | human action remains | critical |
| Optional new experiments | Not recommended for first submission. New wet-lab data would not efficiently solve the editorial methods identity problem. | not needed | low |

## 11. Revised Title Options

1. RhoDyn infers residence states in live-cell perturbation data.
2. Residence-state inference for live-cell perturbation biology with RhoDyn.
3. RhoDyn resolves when signaling dwell time changes perturbation-state interpretation.
4. A reproducible decision framework for residence states in live-cell reporter data.
5. RhoDyn compares residence, amplitude, coupling, and routed outputs in perturbation data.

Ranked decision. Option 1 remains the best Nature Methods title because it names the software/method object, the inference target, and the data class without overclaiming biology.

## 12. Revised Abstract

Live-cell perturbation experiments often lose dynamic control information when trajectories are reduced to endpoints, amplitudes, or generic time-series features. RhoDyn is a computational method for residence-state inference that scores dwell within user-declared biological windows, compares residence and amplitude summaries, evaluates bounded coupling under declared margins, constructs measurement-scoped reserve-like endpoint summaries, and tests routed-output alternatives against reduced architectures. Across synthetic truth cases, public calcium and ERK reporter trajectories, public-derived endpoint demonstrations, held-out coupling contexts, and software-parity checks, RhoDyn exposes cases in which residence, buffering, coupling boundaries, or routed outputs change interpretation while preserving amplitude-sufficient and unresolved regimes. The Python, CLI, backend, workbench, and archived release surfaces produce matched, inspectable outputs. RhoDyn provides a reproducible route for identifying dynamic operating-state structure in live-cell perturbation data without treating every window, endpoint coordinate, or effective model term as a literal mechanism.

## 13. Revised Figure Architecture

| Figure | Editorial job | Panels required | Claim supported | Current source material | Missing analysis or visualization |
| --- | --- | --- | --- | --- | --- |
| Fig. 1 | Method identity and capability gain | Input contract, residence definitions, failure modes, truth cases | RhoDyn is an executable method object | current Fig. 1 | none |
| Fig. 2 | Performance validation | Synthetic regimes, amplitude baselines, reduced alternatives, ambiguous cases | Decision rules recover known truth and withhold unsupported calls | current Fig. 2 | optional runtime inset |
| Fig. 3 | Generality across public trajectories | Adapter map, calcium, ERK, sensitivity | Residence/amplitude separation travels beyond reference use case | current Fig. 3 | none |
| Fig. 4 | Endpoint/reserve/routed-output demonstrations | Schema, bounded coupling, reserve-like endpoint, routed alternatives, limitations | RhoDyn supports non-trajectory perturbation decisions | current Fig. 4 | none |
| Fig. 5 | Held-out and robustness | Plan, pass cases, inconclusive cases, margin sensitivity, access boundary | Method exposes scoped support and non-resolution | current Fig. 5 | none |
| Fig. 6 | Reproducibility/software workbench | parity, export, clean-room, archive, user path | Reviewers can inspect and reproduce decisions | current Fig. 6 | none |

## 14. Cover Letter Significance Paragraph

RhoDyn is submitted as a Nature Methods computational-methods Article because it turns a common but under-operationalized problem in live-cell perturbation biology into a reproducible decision workflow. Many experiments collect rich time-lapse reporter or endpoint perturbation data but still decide biological state from endpoints, peaks, means, thresholds, or generic trajectory features. RhoDyn asks a more specific and testable question: when does time spent inside a declared response regime, a declared bounded-coupling margin, a reserve-like endpoint coordinate, or a routed-output alternative change interpretation relative to simpler summaries, and when should the answer remain amplitude-sufficient or unresolved? The validation ladder spans known-truth synthetic regimes, public live-cell reporters, public-derived endpoint demonstrations, held-out contexts, and software parity across Python, CLI, backend, workbench, GitHub, Zenodo, and figure-rendering surfaces.

## 15. Final Decision

Submit after minor narrative elevation and completion of human upload actions. Do not delay for new wet-lab experiments. Do not delay for new public data unless the author team wants an additional safety margin. The current package is viable only if the method-first title, abstract, figure spine, validation ladder, prior-art positioning, and claim boundaries remain intact. If the submission drifts back toward a RhoA/microglia biology story, a generic software platform, or a universal residence-state claim, the desk-rejection risk rises sharply.

## 16. Final Action List

1. Keep the current method-first title and abstract.
2. Use the cover-letter draft and final upload runbook without adding unsupported claims.
3. Complete the official Springer Nature Reporting Summary, declarations, author metadata, reviewer/editor choices, and final author approval.
4. Verify GitHub, Zenodo, PanelForge, and public-data links from a clean browser immediately before upload.
5. Preserve the validation ladder in the cover letter and portal-facing significance text.
6. Do not add mechanistic language to bounded coupling, reserve-like endpoints, or routed-output parameters.
7. If the author team wants one optional extra safety check, add a compact runtime/scalability table from existing examples, but do not make submission dependent on new wet-lab data.

# Editorial pitch for Nature Methods

## Cover-letter draft

Dear Nature Methods editors,

We submit "RhoDyn infers residence states in live-cell perturbation data" as a computational methods Article for consideration in Nature Methods. The paper addresses a practical bottleneck shared by live-cell signaling, imaging, perturbation, and screening studies. Many experiments collect trajectories but still make decisions from endpoints, peaks, thresholds, means, or generic time-series features. RhoDyn asks a narrower and more testable question. Does the time a cell spends inside a declared response regime change the biological interpretation relative to amplitude-based summaries?

The contribution is not the broad observation that cell signaling is dynamic, and it is not a claim to replace trajectory-inference, state-space, or amplitude analyses. RhoDyn defines an inspectable method object that combines declared residence windows, dwell fraction, dwell time, segment count, amplitude comparators, bounded-coupling margins, reserve-like endpoint coordinates, routed-output alternatives, uncertainty summaries, and explicit failure modes in one reproducible workflow. The method therefore tells users when residence adds information beyond amplitude, when a simpler summary is sufficient, and when the supplied data should withhold a stronger interpretation.

The validation ladder is designed to avoid a single-case methods claim. The manuscript includes known-truth synthetic regimes, public DRG calcium trajectories, public ERK reporter trajectories, public-derived endpoint and paired-reporter demonstrations, held-out bounded-coupling contexts, margin-sensitivity cases, inconclusive examples, and parity across Python, command-line, backend, workbench, export-bundle, source-distribution, checksum, GitHub, and Zenodo surfaces. The RhoA/microglia work is treated as a reference use case rather than as hidden evidence for every methods claim.

We believe the manuscript fits Nature Methods because it presents an Article-level computational method, not a software wrapper around existing summaries, with immediate practical relevance for live-cell perturbation studies that now reduce trajectories to endpoints. A biologist can use RhoDyn to decide whether a tidy live-cell or endpoint perturbation table supports residence-state interpretation, amplitude-only interpretation, bounded coupling, reserve-like buffering, routed-output comparison, or a withheld conclusion. A quantitative reader can inspect the same decision through declared windows, margins, uncertainty summaries, versioned commands, reproducible exports, and source-linked example outputs.

The paper is deliberately scoped. Residence windows are declared analysis choices, not automatically discovered biological states. A bounded-coupling result means equivalence within a stated margin and context, not absence of all coupling. Reserve-like endpoint summaries remain tied to measured assays, and routed-output comparisons constrain tested alternatives without identifying direct biochemical edges. RhoDyn v0.1.0 is publicly available with GitHub and Zenodo release records, documented commands, public-derived example tables, tests, figure-ready outputs, and reviewable reproducibility surfaces. The submission package includes data and code availability statements, a Reporting Summary placeholder and answer bank for final portal completion, author-declaration prompts, a code-for-review surface, figure inventories, source-data/statistics inventories, prior-art positioning, and a desk-review objection map.

Sincerely,

The authors

## Cover-letter upload checklist

Complete or replace these author-confirmed statements before journal upload. They are not inferred from repository files.

- Related manuscripts. State whether any related manuscripts by any author are under consideration or in press elsewhere, or state that there are none.
- Prior editor discussions. State whether there have been prior discussions with a Nature Methods editor about this work, or state that there have been none.
- Dual consideration and approval. Insert only after author confirmation. "We confirm that this manuscript has not been published elsewhere and is not under consideration by another journal. All authors have approved the manuscript and agree with its submission to Nature Methods."
- Double-blind review. If choosing double-blind peer review, include author affiliations and contact information in the cover letter rather than the manuscript file.
- Reviewer suggestions and exclusions. Add recommended or excluded reviewers only if the authors choose to provide them, with brief reasons for exclusions.

## Presubmission-inquiry draft

Presubmission enquiries are optional and should not replace full manuscript submission. If the authors choose to ask for an editorial read before upload, the core question is whether Nature Methods sees RhoDyn as an Article-level computational method for live-cell perturbation biology.

RhoDyn is a computational method for residence-state inference in live-cell perturbation data. It is designed for situations in which endpoint, peak, mean, latency, or threshold summaries may miss the time a cell spends inside a biologically declared response window, giving the method immediate practical relevance for laboratories that already collect time-lapse reporter or endpoint perturbation tables. The method defines dwell fraction, dwell time, segment count, amplitude comparators, bounded-coupling margins, reserve-like endpoint coordinates, routed-output alternatives, uncertainty summaries, and explicit failure modes as inspectable outputs.

The proposed Article emphasizes method definition and validation rather than a new primary disease-biology claim. The evidence ladder includes known-truth synthetic regimes, public calcium and ERK live-cell reporter trajectories, public-derived endpoint and paired-reporter demonstrations, held-out bounded-coupling contexts, margin-sensitivity checks, inconclusive examples, and software parity across Python, command-line, backend, workbench, export bundle, source distribution, checksums, GitHub, and Zenodo release surfaces. The RhoA/microglia study is presented as a reference use case rather than as the sole basis for the methods claim.

The editorial point is that RhoDyn does not claim novelty for live-cell dynamics, trajectory inference, or morphodynamic embedding broadly. It contributes a practical decision framework for determining when declared residence carries state information beyond amplitude, when endpoint or amplitude summaries are sufficient, and when evidence is insufficient. The manuscript is scoped to avoid overclaiming. Declared windows are not automatically discovered states, bounded coupling is margin- and context-limited, reserve-like summaries are tied to measured endpoints, and routed-output comparisons do not identify biochemical edges.

We would value the editors' view on whether this framing fits Nature Methods as an Article describing a reusable computational method for live-cell perturbation biology, rather than as a software note or a single-system biological study.

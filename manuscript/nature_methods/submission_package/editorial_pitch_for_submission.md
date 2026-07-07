# Editorial pitch for Nature Methods

## Cover-letter draft

Dear Nature Methods editors,

We submit "RhoDyn infers residence states in live-cell perturbation data" as a computational methods Article for consideration in Nature Methods. RhoDyn addresses a common bottleneck in live-cell perturbation biology. Time-lapse reporters are routinely reduced to endpoints, peaks, thresholds, or generic trajectory features, which can obscure whether the relevant biological information lies in how long a cell remains inside a response regime rather than how high the signal becomes. RhoDyn turns that question into a reviewable analysis object.

The method defines residence windows, dwell fraction, dwell time, segment count, amplitude comparators, bounded-coupling margins, reserve-like endpoint coordinates, routed-output alternatives, and uncertainty summaries in one reproducible workflow. The central advance is not the general claim that cell signaling is dynamic. It is a practical decision framework that tells users when residence adds information beyond amplitude, when a simpler summary is sufficient, and when the supplied data do not support a stronger interpretation.

The validation strategy is built for a methods journal. The manuscript includes known-truth synthetic regimes, public DRG calcium trajectories, public ERK reporter trajectories, public-derived endpoint and paired-reporter demonstrations, held-out bounded-coupling contexts, margin-sensitivity cases, inconclusive examples, and parity across Python, command-line, backend, workbench, export-bundle, source-distribution, checksum, GitHub, and Zenodo surfaces. The RhoA/microglia work is treated as a reference use case rather than as hidden evidence for the methods Article.

We believe the manuscript fits Nature Methods because it presents a reusable computational method with immediate practical relevance for live-cell signaling, imaging, perturbation, and screening studies. The paper is deliberately scoped. A residence window is a declared analysis choice, not an automatically discovered biological state. A bounded-coupling result means equivalence within a stated margin and context, not absence of all coupling. Reserve-like endpoint summaries remain tied to the measured assay, and routed-output comparisons constrain tested alternatives without identifying direct biochemical edges.

The software is publicly available as RhoDyn v0.1.0 with GitHub and Zenodo release records, documented commands, public-derived example tables, tests, figure-ready outputs, and reviewable reproducibility surfaces. We have included data and code availability statements, a Reporting Summary placeholder for final portal completion, a code-for-review surface, figure inventories, and source-data/statistics inventories.

Sincerely,

The authors

## Presubmission-inquiry draft

RhoDyn is a computational method for residence-state inference in live-cell perturbation data. It is designed for situations in which endpoint, peak, mean, or threshold summaries may miss the time a cell spends inside a biologically declared response window. The method defines dwell fraction, dwell time, segment count, amplitude comparators, bounded-coupling margins, reserve-like endpoint coordinates, routed-output alternatives, and uncertainty summaries as inspectable outputs.

The proposed Nature Methods Article would emphasize method definition and validation rather than a new primary disease-biology claim. The evidence ladder includes known-truth synthetic regimes, public calcium and ERK live-cell reporter trajectories, public-derived endpoint and paired-reporter demonstrations, held-out bounded-coupling contexts, margin-sensitivity checks, inconclusive examples, and software parity across Python, command-line, backend, workbench, export bundle, source distribution, checksums, GitHub, and Zenodo release surfaces.

The main editorial point is that RhoDyn does not claim novelty for live-cell dynamics, trajectory inference, or morphodynamic embedding broadly. Instead, it contributes a practical decision framework for determining when residence carries state information beyond amplitude, when endpoint or amplitude summaries are sufficient, and when evidence is insufficient. The manuscript is scoped to avoid overclaiming. Declared windows are not automatically discovered states, bounded coupling is margin- and context-limited, reserve-like summaries are tied to measured endpoints, and routed-output comparisons do not identify biochemical edges.

We would value the editors' view on whether this framing fits Nature Methods as an Article describing a reusable computational method for live-cell perturbation biology.

# Stage 7.0 baseline-method inventory

This inventory defines the comparator classes RhoDyn must face during Stage 7 benchmarking. It is planning only. No baseline implementation or analysis begins here.

## Baseline decision rule

A baseline belongs in Stage 7 if it represents an interpretation a reasonable live-cell or perturbation biologist might use instead of RhoDyn. The benchmark must test whether RhoDyn adds information beyond that baseline, when the baseline is sufficient, and when neither approach resolves the biological question.

## Baseline classes

| id | baseline class | what it measures | why it matters | planned Stage 7 use |
| --- | --- | --- | --- | --- |
| B1 | Endpoint value | Final or selected-timepoint signal value. | Many experiments reduce time series to a final readout. | Compare against residence-state summaries in synthetic and public trajectory data. |
| B2 | Peak amplitude | Maximum signal value or max-minus-baseline. | Captures signal strength but not dwell time. | Primary comparator for residence versus amplitude claims. |
| B3 | Mean activity or area under curve | Average trajectory level or integrated signal. | Common summary for sustained signaling. | Tests whether residence windows add information beyond broad exposure. |
| B4 | Threshold crossing count | Number of excursions above or below a fixed threshold. | Captures event frequency but may ignore duration. | Compare against dwell fraction and dwell time. |
| B5 | Time above threshold | Total time above a single threshold. | Similar to residence but usually one-sided and not window-bounded. | Clarifies when RhoDyn's windowed regime is distinct from high-state duration. |
| B6 | Time-to-peak and response latency | Time of maximum response or first response. | Useful for acute stimulation kinetics. | Tests whether timing alone explains state differences. |
| B7 | Generic trajectory features | Slopes, volatility, autocorrelation, Fourier/wavelet features, dynamic time warping, and feature libraries such as catch22 or tsfresh. | These can classify time series without a biological residence model. | Compare predictive performance and interpretability. |
| B8 | Simple clustering of trajectory features | Unsupervised clustering on extracted time-series features. | Common exploratory route for single-cell dynamics. | Tests whether clusters recover interpretable operating states. |
| B9 | Endpoint-only architecture comparison | Reduced model using endpoint prevalence or condition means. | Tests whether dynamic information is necessary for architecture discrimination. | Used in endpoint and model-comparison benchmarks. |
| B10 | Single-axis morphology or phenotype model | One-dimensional morphology or feature-score model. | Tests whether visible phenotype explains output state. | Routed-output and endpoint demonstration comparator. |
| B11 | Generic state-space or dimensionality reduction summary | PCA, UMAP/t-SNE on features, or low-dimensional embeddings. | Common way to situate cells without explicit dynamic controller variables. | Compare against interpretable residence, reserve, and routed-output summaries. |
| B12 | Domain-standard method where available | Existing accepted tool for the domain, such as trajectory inference, single-cell dynamics, segmentation, or signaling-analysis packages. | Prevents benchmarking only against weak baselines. | Selected case-by-case for Stage 7 public datasets. |
| B13 | Null or shuffled-control baseline | Label permutation, time shuffling, or grouped null model. | Tests whether apparent residence structure depends on biological grouping. | Required for uncertainty and sensitivity checks. |
| B14 | Reduced RhoDyn component | RhoDyn with residence, reserve, bounded coupling, or routed-output component removed. | Tests which method component is necessary. | Required for method-ablation benchmarks. |

## Baseline inclusion criteria

A baseline can enter Stage 7 if it satisfies all of the following conditions.

- It can be computed from the same tidy input table as RhoDyn or from a documented transformation of that table.
- It preserves cell, replicate, condition, donor, well, field, or sequence grouping where relevant.
- It emits interpretable outputs that can be compared against RhoDyn on the same biological question.
- It can fail or be inconclusive without being treated as a software failure.
- It has a clear role in the biological decision being tested.

## Baseline rejection criteria

Reject or defer a baseline if any of the following apply.

- It requires data not available to RhoDyn for the same comparison.
- It silently discards replicate or grouping structure that is biologically required.
- It only provides a black-box prediction without a usable interpretation for the planned method claim.
- It requires private, licensed, or non-reviewable software that cannot be reproduced by reviewers.
- It is selected only because it is weak.

## Required benchmark contrasts

Stage 7.2 must include, at minimum, these comparator groups.

1. RhoDyn residence summaries versus amplitude summaries.
2. RhoDyn windowed residence versus one-sided threshold-duration summaries.
3. RhoDyn bounded-coupling decisions versus ordinary difference tests or correlation summaries.
4. RhoDyn reserve-like summaries versus raw stimulus-response amplitude.
5. RhoDyn routed-output or reduced-architecture comparison versus endpoint-only and one-dimensional phenotype models.
6. RhoDyn outputs versus at least one relevant domain-standard method where a credible comparator exists.

## Completion decision

This inventory covers amplitude, endpoint, threshold, generic trajectory, domain-standard, null-control, and method-ablation baselines. It is sufficient to close the Stage 7.0 baseline-inventory requirement.

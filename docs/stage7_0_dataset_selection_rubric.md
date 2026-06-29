# Stage 7.0 dataset selection rubric

This rubric controls how Stage 7 datasets are selected. It prevents the evidence program from choosing datasets simply because they are convenient or favorable. No dataset is ingested or analyzed by this document.

## Selection principles

1. Select datasets because they stress a RhoDyn method component.
2. Prefer datasets that allow a baseline comparator and an interpretable biological result.
3. Preserve biological grouping and metadata before computing summaries.
4. Include cases where RhoDyn may fail, be unnecessary, or be inconclusive.
5. Keep the RhoA/microglia manuscript as a reference use case only.

## Inclusion criteria

A dataset can enter Stage 7 only if it satisfies all required criteria.

| criterion | requirement |
| --- | --- |
| Reviewable access | Public access, reviewer-access archive, or documented controlled-access route exists. |
| Biological question | The dataset can test residence, amplitude, bounded coupling, reserve-like buffering, routed output, or model-comparison behavior. |
| Time or perturbation axis | Live-cell datasets must include time units. Endpoint datasets must include perturbation, dose, condition, or response context. |
| Metadata | Condition labels, cell identifiers, replicate identifiers, and acquisition or batch context are available or reconstructable. |
| Grouping | Biological or technical grouping variables can be preserved. |
| Baseline comparator | At least one credible non-RhoDyn baseline can be computed. |
| Reproducibility | Source citation, download or recovery route, preprocessing assumptions, and output schema can be documented. |
| Scope boundary | The dataset can support a clear statement of what it does not prove. |

## Rejection criteria

Reject the dataset from Stage 7 demonstrations if any required property is missing and cannot be repaired without hidden assumptions.

| rejection trigger | reason |
| --- | --- |
| Missing time units in a trajectory dataset | Residence, dwell time, and transition timing cannot be interpreted. |
| Missing condition labels | Perturbation or state comparisons cannot be made. |
| Missing cell or trace identifiers | Single-cell trajectories cannot be reconstructed safely. |
| Missing replicate, donor, well, field, or sequence information where biology requires it | Grouping-aware uncertainty and pseudoreplication control cannot be supported. |
| Non-reviewable access | The evidence cannot support a methods manuscript. |
| Unclear preprocessing that cannot be reconstructed or documented | The derived input table cannot be trusted for a benchmark. |
| Only aggregate means are available when the method question requires single-cell traces | Residence-state inference cannot be tested directly. |
| Dataset selected only because it produces a favorable RhoDyn result | This would bias the method evidence program. |

## Scoring rubric

Candidate datasets should be scored before selection. A candidate needs no minimum score to be retained as exploratory, but it should not become a Stage 7 demonstration unless it scores well on scientific stress value and reproducibility.

| score | meaning |
| --- | --- |
| 0 | Criterion absent or unusable. |
| 1 | Criterion present but weak, incomplete, or requires assumptions. |
| 2 | Criterion present, documented, and suitable for review. |
| 3 | Criterion strong, richly annotated, and ideal for benchmark or demonstration use. |

Scored dimensions.

- Biological relevance to live-cell perturbation or endpoint-state interpretation.
- Method-component stress value.
- Metadata completeness.
- Replicate and grouping structure.
- Baseline comparator availability.
- Public or reviewable access.
- Preprocessing transparency.
- Expected interpretability for a biologist.
- Failure-mode value.
- Fit to a specific Stage 7 subphase.

## Fallback logic

If no candidate dataset passes the rubric for a planned demonstration class, use the following fallback order.

1. Search for a better public dataset in the same biological class.
2. Switch to a collaborator or held-out dataset with controlled-access documentation.
3. Narrow the Stage 7 claim to exclude that method component.
4. Keep the failed search as a limitation rather than substituting a weak dataset.

## Candidate-class readiness

| class | readiness after Stage 7.0 | next action |
| --- | --- | --- |
| Live-cell kinase reporter trajectories | Candidate class accepted. | Rank ERK, Akt, Src, PKA, JNK, or MAPK reporter datasets during Stage 7.3. |
| NF-kB or transcription-factor dynamics | Candidate class accepted. | Search public single-cell translocation or reporter datasets during Stage 7.3. |
| Calcium or excitable-cell dynamics | Candidate class accepted. | Reassess existing DRG calcium example and search for independent calcium datasets during Stage 7.3. |
| Paired reporter trajectories | Candidate class accepted. | Rank ERK/Akt, ERK/calcium, or other paired reporter datasets for Stage 7.4. |
| Endpoint perturbation phenotyping | Candidate class accepted. | Use Cell Painting or cytometry-style tables only if replicate structure is preserved. |
| Reserve or stress-buffering data | Candidate class accepted with caution. | Use reserve language only when the readout supports it directly. |
| RhoA/microglia manuscript | Reference case only. | Do not count as independent Stage 7 generality evidence. |

## Completion decision

This rubric explicitly rejects datasets lacking metadata, time units, grouping, or reviewable access and defines fallback behavior. It is sufficient to close the Stage 7.0 dataset-rubric requirement.

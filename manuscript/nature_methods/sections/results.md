# Results

<!-- RESULTS-DRAFT stage=9.11 generated_utc=2026-07-03T13:14:53.681879Z draft_version=results-draft@2026-07-03@3e952a3de6128f2c9074c6f40b2c19fb3790106e -->

## RhoDyn defines residence-state inference as an executable method object

<!-- para_ids=PARA-RESULTS-001 unit_id=RES-001 figure_id=FIG-001 claim_ids=CLM-0001;CLM-0005 -->

RhoDyn first had to be defined as a method object rather than as a collection of post hoc trajectory summaries. The input contract and workflow schematic (Fig. 1a) specify tidy trajectory or endpoint tables, declared biological windows, replicate variables, and exportable decision outputs. The residence-window panel (Fig. 1b) separates dwell fraction, dwell time, and segment count from peak, endpoint, and average amplitude, making time-in-state an explicit summary of the supplied trajectory rather than a hidden fitted state. Boundary cases (Fig. 1c) identify inputs that remain unresolved when time, condition, replicate, or window definitions are missing. Executable truth cases (Fig. 1d) then provide positive, negative, and ambiguous examples in which the same API returns a result or withholds one. This establishes RhoDyn as an inspectable residence-state analysis object with explicit failure modes, and it creates the need to test whether those summaries change interpretation relative to simpler baselines.

## Synthetic benchmarks separate residence structure from simpler summaries

<!-- para_ids=PARA-RESULTS-001 unit_id=RES-002 figure_id=FIG-002 claim_ids=CLM-0001;CLM-0004 -->

Known synthetic regimes provide the first controlled test because the correct interpretation is available before any biological example is considered. The regime grid (Fig. 2a) places amplitude-like, residence-like, ambiguous, and negative cases on shared simulated inputs. Comparing residence and amplitude summaries on those inputs (Fig. 2b) shows when dwell within a declared window changes the state assignment relative to endpoint, peak, or mean activity. The reduced-alternative comparison (Fig. 2c) asks whether simpler summaries can reproduce the same decision structure, while the negative and ambiguous cases (Fig. 2d) keep unsupported calls visible instead of forcing classification. Together, these benchmarks support residence-state inference in tested trajectory regimes while preserving cases where RhoDyn should remain inconclusive.

## Public live-cell trajectories test residence-amplitude separation beyond the reference use case

<!-- para_ids=PARA-RESULTS-002 unit_id=RES-003 figure_id=FIG-003 claim_ids=CLM-0001 -->

After synthetic truth cases, independent public trajectories tested whether the same analysis object could expose residence-amplitude separation outside the reference use case. The public-data adapter map (Fig. 3a) shows how external calcium and ERK time-series tables are converted into the tidy input schema without changing their biological provenance. In the DRG calcium example (Fig. 3b), residence summaries capture time spent inside the declared response window separately from the amplitude of the calcium trace. In the ERK GPCR example (Fig. 3c), the same comparison separates window occupancy from peak or endpoint signaling. Window-sensitivity and uncertainty summaries (Fig. 3d) then show whether the interpretation is stable, fragile, or unresolved as the declared window changes. These public examples support the claim that residence and amplitude can diverge in more than one live-cell signaling system, without implying that residence summaries replace amplitude analysis for every reporter.

## Endpoint demonstrations link bounded coupling, reserve-like buffering, and routed-output alternatives

<!-- para_ids=PARA-RESULTS-003;PARA-RESULTS-004;PARA-RESULTS-005 unit_id=RES-004 figure_id=FIG-004 claim_ids=CLM-0002;CLM-0003;CLM-0004 -->

Trajectory summaries do not cover all perturbation biology, so the next test moved to endpoint and paired-reporter inputs. The endpoint schema contract (Fig. 4a) defines the grouping, contrast, margin, and readout fields needed before any bounded-coupling or model-comparison decision is made. Bounded-coupling decisions under declared margins (Fig. 4b) distinguish passing, failing, and inconclusive contrasts rather than treating a non-significant difference as equivalence. The reserve-like coordinate (Fig. 4c) is explicitly tied to the measured endpoint, so the draft can describe buffering-like behavior without claiming unmeasured biological reserve capacity. Routed-output reduced-architecture comparisons (Fig. 4d) test whether simpler alternatives satisfy the observed endpoint structure, and the limitations panel (Fig. 4e) records which mechanistic interpretations remain outside the measured scope. This extends RhoDyn from trajectory residence scoring to endpoint decision support, while keeping coupling, reserve-like, and routed-output claims conditional on declared margins, uncertainty, and model alternatives.

## Held-out contexts expose bounded-coupling pass and inconclusive regimes

<!-- para_ids=PARA-RESULTS-003 unit_id=RES-005 figure_id=FIG-005 claim_ids=CLM-0002 -->

Because bounded-coupling calls depend on the declared margin and context, held-out cases were used to test whether the decision rule exposes both support and non-resolution. The held-out analysis plan (Fig. 5a) separates the primary decision rule from later margin and access-boundary checks. Passing contexts (Fig. 5b) show where the declared margin and uncertainty support a bounded-coupling decision. Inconclusive margin-boundary contexts (Fig. 5c) show the complementary case, where available evidence does not justify upgrading the contrast to equivalence. Margin-sensitivity behavior (Fig. 5d) makes that dependence visible, and the controlled-access boundary (Fig. 5e) records cases where the input cannot be fully redistributed. The held-out Results unit therefore keeps pass and inconclusive states side by side, which is essential for using RhoDyn as a decision framework rather than an automatic equivalence engine.

## Software parity and archive reproduction make the method inspectable

<!-- para_ids=PARA-RESULTS-006 unit_id=RES-006 figure_id=FIG-006 claim_ids=CLM-0005 -->

The final Results step asks whether the method can be inspected and reproduced through the software surfaces a user would actually encounter. The parity panel (Fig. 6a) compares Python, CLI, backend, and workbench outputs for the retained evidence paths. The export-bundle view (Fig. 6b) shows that inputs, parameter choices, summaries, figures, and reports are written together rather than hidden in session state. Source-distribution clean-room reproduction (Fig. 6c) tests the archived package from an installable release boundary, while the archive and checksum panel (Fig. 6d) records the release identity and file-level reproducibility surface. The adoption and user-path rehearsal (Fig. 6e) then checks whether a biologist-facing and a quantitative workflow can reach the same reviewable outputs. These results support cross-surface reproducibility for the retained Stage 7 evidence and close the Results section by making RhoDyn's computational decisions inspectable rather than merely available as code.

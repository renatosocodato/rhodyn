# Results

<!-- RESULTS-DRAFT stage=9.11 generated_utc=2026-07-03T13:14:53.681879Z draft_version=results-draft@2026-07-03@3e952a3de6128f2c9074c6f40b2c19fb3790106e -->

## RhoDyn defines residence-state inference as an executable method object

<!-- para_ids=PARA-RESULTS-001 unit_id=RES-001 figure_id=FIG-001 claim_ids=CLM-0001;CLM-0005 -->

Before examples could be interpreted, RhoDyn required a formal analysis object rather than a collection of post hoc trajectory summaries. In the input contract and workflow schematic (Fig. 1a), tidy trajectory and endpoint tables are linked to declared biological windows, replicate variables, and exportable decisions. In the residence-window summary panel (Fig. 1b), dwell fraction, dwell time, and segment count are separated from peak, endpoint, and average amplitude, making time in state a visible property of the supplied trajectory rather than an implicit fitted state. Boundary cases for incomplete inputs (Fig. 1c) show when missing time, condition, replicate, or window definitions should prevent interpretation. Executable truth cases (Fig. 1d) complete the definition by showing positive, negative, and ambiguous examples in which the same API returns a result or withholds one. Together, these definitions establish RhoDyn as an inspectable residence-state analysis object with explicit failure modes, setting up the benchmark question of when those summaries change interpretation relative to simpler baselines.

## Synthetic benchmarks separate residence structure from simpler summaries

<!-- para_ids=PARA-RESULTS-001 unit_id=RES-002 figure_id=FIG-002 claim_ids=CLM-0001;CLM-0004 -->

Synthetic regimes provide the first controlled test because the correct interpretation is known before any biological example is considered. Within the regime grid (Fig. 2a), amplitude-like, residence-like, ambiguous, and negative cases are placed on matched simulated inputs. On those same traces, the residence-versus-amplitude comparison (Fig. 2b) shows when dwell inside a declared window changes the state assignment relative to endpoint, peak, or mean activity. Reduced-alternative comparisons (Fig. 2c) test whether simpler summaries can reproduce the same decision structure. Negative and ambiguous cases (Fig. 2d) keep unsupported calls visible rather than forcing classification. These benchmarks support residence-state inference in the tested trajectory regimes while preserving cases where RhoDyn should remain inconclusive.

## Public live-cell trajectories test residence-amplitude separation beyond the reference use case

<!-- para_ids=PARA-RESULTS-002 unit_id=RES-003 figure_id=FIG-003 claim_ids=CLM-0001 -->

Independent public trajectories then tested whether the same analysis object could expose residence-amplitude separation outside the reference use case. The public-data adapter map (Fig. 3a) shows how external calcium and ERK time-series tables enter the tidy input schema while retaining their biological context. In the DRG calcium demonstration (Fig. 3b), residence summaries capture time spent inside the declared response window separately from calcium-trace amplitude. In the ERK GPCR demonstration (Fig. 3c), the same comparison separates window occupancy from peak or endpoint signaling. Window-sensitivity and uncertainty summaries (Fig. 3d) show whether each interpretation is stable, fragile, or unresolved as the declared window changes. These public examples support residence-amplitude divergence in more than one live-cell signaling system, without implying that residence summaries replace amplitude analysis for every reporter.

## Endpoint demonstrations link bounded coupling, reserve-like buffering, and routed-output alternatives

<!-- para_ids=PARA-RESULTS-003;PARA-RESULTS-004;PARA-RESULTS-005 unit_id=RES-004 figure_id=FIG-004 claim_ids=CLM-0002;CLM-0003;CLM-0004 -->

Perturbation biology also produces endpoint and paired-reporter inputs that cannot be reduced to trajectory residence alone. In the endpoint schema contract (Fig. 4a), grouping, contrast, margin, and readout fields are defined before any bounded-coupling or model-comparison decision is made. Under those declared margins, the bounded-coupling decision panel (Fig. 4b) distinguishes passing, failing, and inconclusive contrasts rather than treating a non-significant difference as equivalence. For the reserve-like coordinate (Fig. 4c), the readout remains tied to the measured endpoint, allowing buffering-like behavior to be described without claiming unmeasured biological reserve capacity. Routed-output reduced-architecture comparisons (Fig. 4d) test whether simpler alternatives satisfy the observed endpoint structure, and the limitation panel (Fig. 4e) states which mechanistic interpretations remain outside the measured scope. This extends RhoDyn from trajectory residence scoring to endpoint decision support while keeping coupling, reserve-like, and routed-output claims conditional on declared margins, uncertainty, and model alternatives.

## Held-out contexts expose bounded-coupling pass and inconclusive regimes

<!-- para_ids=PARA-RESULTS-003 unit_id=RES-005 figure_id=FIG-005 claim_ids=CLM-0002 -->

Because bounded-coupling calls depend on the declared margin and context, held-out cases were used to test whether the decision rule exposes both support and non-resolution. The held-out analysis plan (Fig. 5a) separates the primary decision rule from later margin and access-boundary checks. Passing contexts (Fig. 5b) show where the declared margin and uncertainty support a bounded-coupling decision. Inconclusive margin-boundary contexts (Fig. 5c) show the complementary case, where available evidence does not justify upgrading the contrast to equivalence. Margin-sensitivity behavior (Fig. 5d) makes that dependence visible, and the controlled-access boundary (Fig. 5e) records cases where the input cannot be fully redistributed. The held-out Results unit therefore keeps pass and inconclusive states side by side, which is essential for using RhoDyn as a decision framework rather than an automatic equivalence engine.

## Software parity and archive reproduction make the method inspectable

<!-- para_ids=PARA-RESULTS-006 unit_id=RES-006 figure_id=FIG-006 claim_ids=CLM-0005 -->

The final Results step asks whether the method can be inspected and reproduced through the software surfaces a user would actually encounter. The parity panel (Fig. 6a) compares Python, command-line, backend, and workbench outputs for the retained evidence paths. In the export-bundle view (Fig. 6b), inputs, parameter choices, summaries, figures, and reports are written together rather than hidden in session state. Source-distribution clean-room reproduction (Fig. 6c) tests the archived package from an installable release boundary, while the archive and checksum panel (Fig. 6d) records the release identity and file-level reproducibility surface. The adoption and user-path rehearsal (Fig. 6e) then checks whether biologist-facing and quantitative workflows can reach the same reviewable outputs. These results support cross-surface reproducibility for the retained evidence set and close the Results section by making RhoDyn's computational decisions inspectable rather than merely available as code.

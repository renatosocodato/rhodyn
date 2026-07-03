<!-- DISCUSSION-BLUEPRINT stage=9.13 generated_utc=2026-07-03T13:54:32.775220Z map_version=discussion-map@2026-07-03@679ca73472fbc8bdb2b32c2f449b31cf36bc26d2 -->

<!-- map_rule=no_markdown_subheadings; source_contract=SEC-005; next_surface=discussion.md only after Stage 9.13 gate passes -->

<!-- discussion_paragraph=1 role=Opening synthesis para_ids=PARA-DISCUSSION-001 claim_ids=CLM-0001;CLM-0005 -->

The Discussion should open by stating that RhoDyn makes residence-state inference a reviewable method object for live-cell perturbation data. The central interpretation is that dwell fraction, dwell time, and segment count can preserve time-in-state information that endpoints, peaks, mean activity, or generic trajectory summaries may miss in tested trajectory regimes. The paragraph must also state the first boundary directly. A declared biological window is an author-specified analysis choice, not a causal mechanism, and amplitude or endpoint summaries can be sufficient when residence does not change the interpretation.

<!-- discussion_paragraph=2 role=Scope of public biological demonstrations para_ids=PARA-DISCUSSION-001 claim_ids=CLM-0001 -->

The second paragraph should explain why the public DRG calcium and ERK GPCR examples matter for method scope. They show that residence-amplitude separation is not confined to the RhoA/microglia reference use case, but they do not establish a universal residence regime across all reporters or perturbations. This paragraph should preserve the distinction between a methods demonstration and a new primary disease-biology claim.

<!-- discussion_paragraph=3 role=Decision boundaries for non-trajectory inputs para_ids=PARA-DISCUSSION-002 claim_ids=CLM-0002;CLM-0003;CLM-0004 -->

The third paragraph should synthesize bounded-coupling, reserve-like, and routed-output behavior without upgrading any limitation into a strength. Bounded-coupling decisions are admissible only under declared margins, uncertainty support, and visible inconclusive cases, and they do not exclude slower or context-specific coupling. Reserve-like summaries should remain tied to the measured endpoint rather than unmeasured biological reserve capacity. Routed-output comparisons can reject reduced alternatives in the tested endpoint demonstration without treating effective parameters as direct biochemical interactions.

<!-- discussion_paragraph=4 role=Software and reproducibility boundary para_ids=PARA-DISCUSSION-002 claim_ids=CLM-0005 -->

The fourth paragraph should discuss inspectability through Python, CLI, backend, workbench, export bundles, checksums, and source-distribution clean-room reproduction. The supported claim is software reproducibility for the retained Stage 7 evidence, not a new biological result, regulatory qualification, hidden private-data reproduction, or PyPI publication claim. This paragraph should also make clear that controlled-access or non-redistributable inputs remain boundary cases rather than defects that the method can erase.

<!-- discussion_paragraph=5 role=Closing scope and future-use plan para_ids=PARA-DISCUSSION-001;PARA-DISCUSSION-002 claim_ids=CLM-0001;CLM-0002;CLM-0003;CLM-0004;CLM-0005 -->

The closing paragraph should connect the method contribution to future use without adding new evidence. It should say that future applications should predeclare windows, margins, grouping levels, and reduced alternatives, then report pass, fail, and inconclusive outcomes with the same visibility. The final note should position RhoDyn as a decision framework for dynamic operating-state interpretation, not as an automatic mechanism-discovery engine.

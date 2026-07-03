# Stage 9.10 Results subsection architecture

Generated UTC. 2026-07-03T12:54:20.139675Z

Architecture version. results-architecture@2026-07-03@be61043e8cfb614028ea9d8a940357ba0e579c67

Stage. 9.10 Results subsection architecture.

Scope. This file defines the Results drafting architecture for a future Nature
Methods Article. It is not Results prose, not a reference library, not figure
legend text, not Methods text, and not a submission package.

## Results architecture rule

The Results section must follow the evidence-bearing display sequence in
`FIG-001` through `FIG-006` order. Each subsection must name the specific figure,
claim IDs, evidence artifact IDs, supplementary support when needed, allowed
conclusion, prohibited overclaim, and transition pressure. A future Stage 9.11
Results draft may use these units as paragraph scaffolds, but this blueprint does
not draft reader-facing Results prose.

## Results unit map

| unit_id | subheading | paragraph_ids | figure_id | claim_ids | art_ids | supplementary_ids |
| --- | --- | --- | --- | --- | --- | --- |
| RES-001 | RhoDyn defines residence-state inference as an executable method object | PARA-RESULTS-001 | FIG-001 | CLM-0001;CLM-0005 | ART-0025;ART-0026;ART-0016;ART-0017 | SUPP-001;SUPP-002 |
| RES-002 | Synthetic benchmarks separate residence structure from simpler summaries | PARA-RESULTS-001 | FIG-002 | CLM-0001;CLM-0004 | ART-0027;ART-0028;ART-0029;ART-0030;ART-0031 | SUPP-001;SUPP-002 |
| RES-003 | Public live-cell trajectories test residence-amplitude separation beyond the reference use case | PARA-RESULTS-002 | FIG-003 | CLM-0001 | ART-0032;ART-0033;ART-0034;ART-0035 | SUPP-003 |
| RES-004 | Endpoint demonstrations link bounded coupling, reserve-like buffering, and routed-output alternatives | PARA-RESULTS-003;PARA-RESULTS-004;PARA-RESULTS-005 | FIG-004 | CLM-0002;CLM-0003;CLM-0004 | ART-0036;ART-0037;ART-0038;ART-0039;ART-0040;ART-0049;ART-0050;ART-0051 | SUPP-004;SUPP-005;SUPP-006;SUPP-007 |
| RES-005 | Held-out contexts expose bounded-coupling pass and inconclusive regimes | PARA-RESULTS-003 | FIG-005 | CLM-0002 | ART-0041;ART-0042;ART-0043;ART-0044;ART-0048 | SUPP-004;SUPP-007 |
| RES-006 | Software parity and archive reproduction make the method inspectable | PARA-RESULTS-006 | FIG-006 | CLM-0005 | ART-0045;ART-0046;ART-0047;ART-0052;ART-0053;ART-0010;ART-0021;ART-0022;ART-0023;ART-0024 | SUPP-008 |

## Global drafting constraints for Stage 9.11

- Draft in the locked main-figure order from `FIG-001` through `FIG-006`.
- Keep every subsection evidence-bearing. No subsection may rely on narrative
  framing without at least one main display item and one locked evidence artifact.
- Use topical subheadings, consistent with the Nature Methods Results contract.
- Keep inconclusive cases visible for bounded-coupling and margin-sensitive
  contexts.
- Use reserve-like language unless the measurement directly assays biological
  reserve capacity.
- Do not convert effective routed-output model terms into direct molecular
  wiring.
- Do not claim that RhoDyn generated the RhoA/microglia manuscript results.
- Do not start citation resolution, reference bibliography, full Results prose,
  figure legends, Methods, Discussion, or submission-package assembly in this
  stage.

## Unit details

### RES-001. RhoDyn defines residence-state inference as an executable method object

- Primary display item. FIG-001.
- Paragraph planning rows. PARA-RESULTS-001.
- Claim IDs. CLM-0001; CLM-0005.
- Evidence artifact IDs. ART-0025; ART-0026; ART-0016; ART-0017.
- Supplementary support. SUPP-001; SUPP-002.
- Panel structure. A method object and input contract; B residence-window metrics; C failure modes and interpretation boundaries; D executable truth-case ladder.
- Paragraph purpose. Define the RhoDyn method object and show how residence-window summaries differ from amplitude summaries in synthetic trajectory regimes.
- Results-unit purpose. Define the input, metric, output, and failure-mode object before the manuscript evaluates any biological example.
- Evidence move. Use the method-object schematic, residence-window metrics, failure-mode boundary, and truth-case ladder as the visible evidence chain.
- Drafting task for Stage 9.11. Explain what RhoDyn accepts, what it scores, what it returns, and what it refuses to infer from insufficient inputs.
- Allowed conclusion. May conclude that RhoDyn formalizes residence-state analysis with executable truth cases and explicit interpretation boundaries.
- Strength cap. May claim residence summaries reveal time-in-state structure beyond amplitude summaries in tested trajectory regimes. | May claim source-distribution reproduction, cross-surface parity, and export provenance for retained Stage 7 evidence.
- Prohibited overclaim. Do not imply that every live-cell dataset contains a residence regime or that RhoDyn automatically discovers the correct biological window.
- Transition pressure. Once the method object is explicit, the Results must test whether it adds information beyond endpoint and amplitude summaries.

### RES-002. Synthetic benchmarks separate residence structure from simpler summaries

- Primary display item. FIG-002.
- Paragraph planning rows. PARA-RESULTS-001.
- Claim IDs. CLM-0001; CLM-0004.
- Evidence artifact IDs. ART-0027; ART-0028; ART-0029; ART-0030; ART-0031.
- Supplementary support. SUPP-001; SUPP-002.
- Panel structure. A synthetic regime grid; B residence-versus-amplitude benchmark; C reduced-alternative comparison; D negative and ambiguous failure behavior.
- Paragraph purpose. Define the RhoDyn method object and show how residence-window summaries differ from amplitude summaries in synthetic trajectory regimes.
- Results-unit purpose. Benchmark residence summaries against amplitude, endpoint, threshold, and reduced-architecture alternatives on shared inputs.
- Evidence move. Use the synthetic regime grid, residence-versus-amplitude comparison, reduced-alternative comparison, and negative or ambiguous failure behavior.
- Drafting task for Stage 9.11. Show where residence-state inference changes the interpretation and where the same inputs remain ambiguous or unsupported.
- Allowed conclusion. May conclude that residence summaries reveal time-in-state structure beyond simpler summaries in tested synthetic regimes while preserving negative and ambiguous cases.
- Strength cap. May claim residence summaries reveal time-in-state structure beyond amplitude summaries in tested trajectory regimes. | May claim reduced alternatives can fail routed-output constraints in the tested endpoint demonstration.
- Prohibited overclaim. Do not describe synthetic truth cases as new biological evidence or as proof of a universal residence law.
- Transition pressure. A synthetic benchmark is necessary but not sufficient, so the Results must next test independent public live-cell signaling systems.

### RES-003. Public live-cell trajectories test residence-amplitude separation beyond the reference use case

- Primary display item. FIG-003.
- Paragraph planning rows. PARA-RESULTS-002.
- Claim IDs. CLM-0001.
- Evidence artifact IDs. ART-0032; ART-0033; ART-0034; ART-0035.
- Supplementary support. SUPP-003.
- Panel structure. A public-data adapter map; B DRG calcium residence-amplitude separation; C ERK GPCR residence-amplitude separation; D window-sensitivity and uncertainty summary.
- Paragraph purpose. Use independent public trajectory demonstrations to show residence-amplitude separation beyond the reference use case.
- Results-unit purpose. Show that residence-amplitude separation is not restricted to the RhoA/microglia reference logic.
- Evidence move. Use the public-data adapter map, DRG calcium trajectory summary, ERK GPCR trajectory summary, and window-sensitivity or uncertainty summary.
- Drafting task for Stage 9.11. Describe how public trajectory inputs are converted into tidy residence and amplitude summaries, then compare the readout-level interpretation.
- Allowed conclusion. May conclude that independent public calcium and ERK systems contain tested cases where residence and amplitude summaries diverge.
- Strength cap. May claim residence summaries reveal time-in-state structure beyond amplitude summaries in tested trajectory regimes.
- Prohibited overclaim. Do not claim that residence logic replaces amplitude analysis in all reporters or perturbation systems.
- Transition pressure. Trajectory evidence does not cover endpoint perturbation experiments, so the Results must define how RhoDyn handles coupling, reserve-like, and routed-output readouts.

### RES-004. Endpoint demonstrations link bounded coupling, reserve-like buffering, and routed-output alternatives

- Primary display item. FIG-004.
- Paragraph planning rows. PARA-RESULTS-003; PARA-RESULTS-004; PARA-RESULTS-005.
- Claim IDs. CLM-0002; CLM-0003; CLM-0004.
- Evidence artifact IDs. ART-0036; ART-0037; ART-0038; ART-0039; ART-0040; ART-0049; ART-0050; ART-0051.
- Supplementary support. SUPP-004; SUPP-005; SUPP-006; SUPP-007.
- Panel structure. A endpoint schema contract; B bounded-coupling decisions under declared margins; C reserve-like endpoint coordinate; D routed-output reduced-architecture comparison; E measurement-scoped limitations.
- Paragraph purpose. Present bounded-coupling decisions under declared margins, uncertainty intervals, and visible inconclusive cases. | Describe reserve-like endpoint summaries as measurement-scoped buffering coordinates. | Compare routed-output alternatives and reduced architectures in the tested endpoint demonstration.
- Results-unit purpose. Extend the Results from trajectory-only summaries to perturbation endpoint, paired-reporter, reserve-like, and routed-output demonstrations.
- Evidence move. Use the endpoint schema contract, bounded-coupling decisions under declared margins, reserve-like coordinate, routed-output architecture comparison, and measurement-scoped limitations.
- Drafting task for Stage 9.11. Keep the declared margin, uncertainty state, measurement scope, and reduced alternatives visible before drawing any local conclusion.
- Allowed conclusion. May conclude that RhoDyn can support bounded-coupling, measurement-scoped reserve-like, and routed-output decisions when margins, uncertainty, and model alternatives are explicit.
- Strength cap. May claim bounded coupling is decision-ready only under declared margins, uncertainty, and visible inconclusive cases. | May claim reserve-like endpoint summaries are interpretable when scoped to the measured readout. | May claim reduced alternatives can fail routed-output constraints in the tested endpoint demonstration.
- Prohibited overclaim. Do not claim absence of all coupling, unmeasured biological reserve capacity, or direct biochemical wiring from effective model terms.
- Transition pressure. Because bounded decisions depend on margins and context, the Results must test held-out cases and expose inconclusive boundaries.

### RES-005. Held-out contexts expose bounded-coupling pass and inconclusive regimes

- Primary display item. FIG-005.
- Paragraph planning rows. PARA-RESULTS-003.
- Claim IDs. CLM-0002.
- Evidence artifact IDs. ART-0041; ART-0042; ART-0043; ART-0044; ART-0048.
- Supplementary support. SUPP-004; SUPP-007.
- Panel structure. A held-out analysis plan; B bounded-coupling pass contexts; C inconclusive margin-boundary contexts; D margin sensitivity; E controlled-access boundary.
- Paragraph purpose. Present bounded-coupling decisions under declared margins, uncertainty intervals, and visible inconclusive cases.
- Results-unit purpose. Show that bounded-coupling decisions remain conditional on declared margins, held-out context, and controlled-access limits.
- Evidence move. Use the held-out analysis plan, passing bounded-coupling contexts, inconclusive margin-boundary contexts, margin sensitivity, and controlled-access boundary.
- Drafting task for Stage 9.11. Report the pass, inconclusive, and boundary cases together so the method is not presented as an automatic equivalence engine.
- Allowed conclusion. May conclude that bounded-coupling calls are decision-ready in passing contexts and intentionally inconclusive near margin or access boundaries.
- Strength cap. May claim bounded coupling is decision-ready only under declared margins, uncertainty, and visible inconclusive cases.
- Prohibited overclaim. Do not convert inconclusive or margin-sensitive held-out behavior into equivalence language.
- Transition pressure. After the method boundaries are visible, the Results must show that the implementation reproduces the same outputs across user-facing surfaces.

### RES-006. Software parity and archive reproduction make the method inspectable

- Primary display item. FIG-006.
- Paragraph planning rows. PARA-RESULTS-006.
- Claim IDs. CLM-0005.
- Evidence artifact IDs. ART-0045; ART-0046; ART-0047; ART-0052; ART-0053; ART-0010; ART-0021; ART-0022; ART-0023; ART-0024.
- Supplementary support. SUPP-008.
- Panel structure. A Python, CLI, backend, and workbench parity; B export bundle anatomy; C source-distribution clean-room reproduction; D archive and checksum provenance; E adoption and user-path rehearsal.
- Paragraph purpose. Report software cross-surface parity, export provenance, and reproducibility of retained Stage 7 evidence.
- Results-unit purpose. Make reproducibility and adoption evidence part of the methods result rather than a back-matter assertion.
- Evidence move. Use the Python, CLI, backend, and workbench parity checks, export bundle anatomy, source-distribution clean-room reproduction, archive checksums, and user-path rehearsal.
- Drafting task for Stage 9.11. Describe cross-surface parity, inspectable export contents, archive identity, and user-path behavior without implying private-data reproduction.
- Allowed conclusion. May conclude that retained Stage 7 evidence is reproducible across the documented RhoDyn software surfaces and archived release package.
- Strength cap. May claim source-distribution reproduction, cross-surface parity, and export provenance for retained Stage 7 evidence.
- Prohibited overclaim. Do not claim PyPI publication, hidden private-data reproduction, or production-grade regulated deployment.
- Transition pressure. The Results can then hand the manuscript to the Discussion, where the method contribution and biological interpretation limits are synthesized without adding new evidence.

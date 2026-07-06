# Figure legends and table captions

## Main figure legends

### Figure 1 | RhoDyn defines residence-state inference as an executable method object.

**a**, The method-object schematic defines the input contract for trajectory and endpoint analyses, including tidy records, declared biological windows, replicate variables, and exportable decisions. **b**, Residence-window summaries separate dwell fraction, dwell time, and segment count from peak, endpoint, and average amplitude so that time spent inside a declared interval is visible as its own measurement. **c**, Failure-mode examples show when missing time, condition, replicate, or window definitions should prevent a residence call. **d**, Executable positive, negative, and ambiguous truth cases show that the same method object can return a result or withhold one when the input does not support interpretation. The figure establishes the analysis object and its boundaries before biological demonstrations are interpreted.

### Figure 2 | Synthetic benchmarks distinguish residence structure from amplitude-only summaries.

**a**, Known-truth synthetic regimes place amplitude-like, residence-like, ambiguous, and negative signals on matched simulated inputs. **b**, The residence-versus-amplitude benchmark summarizes twelve synthetic comparisons and shows when dwell inside the declared window changes the state assignment relative to endpoint, peak, or mean activity. **c**, Reduced-alternative comparisons test whether simpler summaries reproduce the same decision structure. **d**, The negative and ambiguous boundary case keeps unsupported calls visible rather than forcing classification. The figure supports residence-state inference in tested trajectory regimes while preserving cases where the method should remain inconclusive.

### Figure 3 | Public live-cell reporters show residence-amplitude separation beyond the reference use case.

**a**, The public-data adapter map shows how external calcium and ERK reporter time series enter the same tidy trajectory schema without changing their source biological context. **b**, In the DRG calcium demonstration, 360 trace summaries separate time spent inside the declared response window from calcium amplitude. **c**, In the ERK GPCR demonstration, 180 trace summaries show the same separation between window occupancy and peak or endpoint signaling. **d**, Window-sensitivity and uncertainty summaries show where the interpretation is stable, fragile, or unresolved as the declared window changes. These examples show that residence and amplitude can diverge in more than one public live-cell reporter system while leaving amplitude-sufficient and unresolved reporters within the method boundary.

### Figure 4 | Endpoint analyses expose bounded coupling, reserve-like buffering, and routed-output alternatives.

**a**, The endpoint schema contract defines grouping, contrast, margin, and readout fields before any bounded-coupling or model-comparison decision is made. **b**, Four bounded-coupling decisions distinguish one primary margin-compatible context, one secondary pooled or contextual summary, and two contrasts that are not promoted beyond their declared margin. **c**, The reserve-like endpoint coordinate is summarized across six endpoint rows with two uncertainty summaries, keeping the buffering interpretation tied to the measured readout. **d**, Routed-output comparison evaluates six endpoint model rows and five reduced alternatives to identify which candidate architectures satisfy the observed endpoint structure. **e**, The limitation panel states the measurement scope for coupling, reserve-like behavior, and routed outputs. The figure extends RhoDyn from trajectory residence scoring to endpoint decision support while keeping each decision conditional on declared margins, uncertainty, and tested alternatives.

### Figure 5 | Held-out contexts separate bounded-coupling support from unresolved margin-boundary cases.

**a**, The held-out analysis plan separates the primary decision rule from later margin and access-boundary checks. **b**, Seven held-out contexts include four cases in which the declared margin and uncertainty support a bounded-coupling decision. **c**, The complementary contexts remain inconclusive when the available interval does not justify promotion to equivalence within the declared bound. **d**, Seventy margin-sensitivity rows make the dependence on the chosen biological margin visible. **e**, The controlled-access boundary records cases where the input can be reviewed only through derived tables or notes. The figure keeps pass and inconclusive states side by side, making bounded coupling a scoped decision rather than an automatic output.

### Figure 6 | Software parity and archive reproduction make RhoDyn decisions inspectable.

**a**, The parity panel compares Python, command-line, backend, and workbench outputs for retained evidence paths. **b**, The export-bundle view shows that inputs, schema details, parameter choices, summaries, figures, and reports are written together rather than hidden in session state. **c**, Source-distribution clean-room reproduction checks the installable release boundary against selected retained outputs. **d**, The archive and checksum panel records a four-surface parity check and a 632-row release archive inventory. **e**, The adoption and user-path rehearsal tests whether biologist-facing and quantitative workflows can reach the same reviewable outputs. The figure supports reproducibility of the demonstrated analyses without turning software availability into a new biological result.

## Supplementary figure legends

### Supplementary Fig. 1 | Input contracts, method definitions, and executable truth cases.

Expanded method-object panels place tidy trajectory and endpoint schemas, residence-window metric definitions, executable positive and negative truth cases, and boundary examples next to the main display.

### Supplementary Fig. 2 | Synthetic benchmark grid, baseline comparisons, and failure behavior.

The known-truth benchmark grid, residence-versus-amplitude comparisons, reduced-summary comparisons, and negative or ambiguous cases provide the detailed support for the synthetic benchmark display.

### Supplementary Fig. 3 | Public live-cell signaling adapters and residence-amplitude sensitivity.

Public-data adapter panels document the DRG calcium and ERK GPCR residence-amplitude summaries and the window or uncertainty sensitivity analyses used to scope the public reporter demonstrations.

### Supplementary Fig. 4 | Bounded-coupling decisions under declared margins.

Endpoint-pairing panels show the declared margin table, bounded-coupling interval display, and inconclusive decision examples that keep coupling claims tied to the stated margin and context.

### Supplementary Fig. 5 | Reserve-like endpoint construction and uncertainty.

Measured endpoint panels separate reserve-like coordinate construction, uncertainty summaries, and label-scope boundaries so that buffering language remains tied to the assay.

### Supplementary Fig. 6 | Routed-output reduced-architecture comparison.

The routed-output supplement provides the architecture matrix, reduced-alternative comparison, residual profile, and decision-boundary table behind the endpoint model-comparison display.

### Supplementary Fig. 7 | Held-out validation pass and boundary cases.

Held-out validation panels show the fixed analysis plan, pass contexts, margin-boundary inconclusive contexts, margin sensitivity, and controlled-access notes that prevent validation from becoming a single unqualified score.

### Supplementary Fig. 8 | Software parity, clean-room reproduction, and archive contents.

Cross-surface reproducibility panels document parity, export-bundle contents, clean-room reproduction summaries, archive records, checksums, and usability-path boundaries for the retained evidence surfaces.

### Supplementary Fig. 9 | Interpretation boundaries and non-example cases.

Non-example panels collect ambiguous regimes, claim-strength caps, and recommended wording boundaries so that limitations remain visible without carrying the main argument.

## Supplementary table captions

### Supplementary Table 1 | Input requirements, residence-window metrics, and truth-case support layers for the method-object figure.

### Supplementary Table 2 | Known-truth synthetic benchmark outcomes, baseline comparisons, and failure-behavior rows for the synthetic benchmark figure.

### Supplementary Table 3 | Public-data adapter details, DRG calcium and ERK GPCR residence-amplitude summaries, and uncertainty support for the public reporter figure.

### Supplementary Table 4 | Endpoint pairing, declared margins, interval decisions, and inconclusive bounded-coupling cases for the endpoint decision figure.

### Supplementary Table 5 | Measured endpoint-preservation coordinate, reserve-like summary rows, and uncertainty support for the reserve-like endpoint panels.

### Supplementary Table 6 | Endpoint model rows, retained and reduced architectures, residual profiles, and model-comparison decisions for routed-output analysis.

### Supplementary Table 7 | Held-out bounded-coupling pass cases, inconclusive contexts, margin-sensitivity rows, and controlled-access boundaries.

### Supplementary Table 8 | Python, command-line, backend, workbench, export-bundle, clean-room reproduction, and archive surfaces used for reproducibility support.

### Supplementary Table 9 | Failure modes, ambiguous regimes, claim-strength caps, and wording boundaries used to keep interpretation within the tested evidence.

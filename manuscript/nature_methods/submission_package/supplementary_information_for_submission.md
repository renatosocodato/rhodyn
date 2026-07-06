# Supplementary Information

## Supplementary Methods

These Supplementary Methods expand the technical details behind the planned supplementary support items while preserving the main Article as the evidence-bearing surface. They provide schema, decision-rule, sensitivity, model-comparison, and software-reproducibility detail that is callable from the Results, Online Methods, and Discussion through the planned supplementary-item callouts. The sections below do not add new biological claims, new datasets, new model outputs, or new figure legends.

### Supplementary Methods 1. Input contracts, method definitions, and truth cases

The supplementary input-contract section makes the method object reconstructable from table structure before any biological interpretation is attached. Trajectory inputs retain `cell_id`, non-negative `time`, `condition`, numeric `signal`, and optional grouping fields such as `replicate`; endpoint-model rows retain `model`, `endpoint`, `observed`, `predicted`, and optional non-negative `weight`; reserve-like and bounded-coupling rows retain the measured response or contrast fields needed for their own decision rules. This section also records the declared window indicator \(I_W(t_k)\), residence time \(R_T=\sum_k \Delta t_k I_W(t_k)\), residence fraction \(R_F=R_T/\sum_k \Delta t_k\), dwell-segment count, and amplitude comparators used in the main Methods. Synthetic positive, negative, and ambiguous truth cases are kept with the same schema so reviewers can see when residence-state inference changes the decision, when it agrees with amplitude summaries, and when the input is insufficient. These supplementary items support method definition and benchmark behavior only; they are not independent biological evidence.

### Supplementary Methods 2. Public live-cell signaling adapters

The public-adapter section specifies how retained DRG calcium and ERK GPCR reporter tables were converted into the same tidy trajectory object used for synthetic truth cases. Adapters preserve the public source record, trace or object identifier, condition label, sampled time, reporter signal, and available grouping fields before residence, amplitude, window-sensitivity, and uncertainty summaries are calculated. The DRG calcium route uses the public source DOI 10.5281/zenodo.14907827, and the ERK GPCR route uses DOI 10.5281/zenodo.5836623. The supplementary sensitivity summaries expose how a declared window changes residence calls, which makes fragile and unresolved regions visible rather than promoting a single preferred threshold. The purpose is to show that the same analysis object can be applied to independent public live-cell reporters; it is not a universal biological rule for all calcium, ERK, kinase, or GTPase trajectories.

### Supplementary Methods 3. Bounded-coupling decisions and held-out contexts

The bounded-coupling supplementary section preserves the predeclared contrast, uncertainty interval, grouping level, and biological margin that must be present before a contrast can be interpreted. For an estimate \(\hat\delta\), interval \([L,U]\), and positive margin \(\Delta\), the interval decision passes only when \(-\Delta \le L \le U \le \Delta\); where posterior samples or a ROPE mass are available, the reported decision also records whether the declared posterior mass threshold is met. Held-out ERK/Akt contexts reuse fixed thresholds and margins from the preceding evidence stage, then report pass, fail, and inconclusive states side by side. The supplementary margin-sensitivity records show when the decision depends on a narrow choice of \(\Delta\), and access-boundary notes identify cases where retained derived tables represent source material that is not redistributed. A passing bounded-coupling decision is therefore equivalence within a declared margin and context, not proof that all coupling is absent.

### Supplementary Methods 4. Reserve-like endpoint construction

The reserve-like supplementary section separates the measured endpoint coordinate from broader biological reserve language. Response series are baseline-normalized as \(F/F_0(t)=F(t)/\bar F_0\), where \(\bar F_0\) is calculated from declared baseline samples. The retained bounded coordinate is \(H=\mathrm{clip}(1-(\max(F/F_0)-f_{\min})/(f_{\max}-f_{\min}),0,1)\), with larger values indicating that the observed response remained closer to the low-response bound under the supplied scale. Uncertainty summaries and label-scope tables are retained so the reader can see whether a reserve-like statement is supported by the measured endpoint or should remain descriptive. These outputs are not direct assays of unmeasured biological reserve capacity.

### Supplementary Methods 5. Routed-output reduced-architecture comparison

The routed-output supplementary section records how endpoint rows are used to compare candidate readout architectures. For each model \(m\), observed endpoint \(y_j\), prediction \(\hat y_{jm}\), and optional weight \(w_j\), RhoDyn computes \(RSS_m=\sum_j w_j(y_j-\hat y_{jm})^2\), RMSE, AIC, and BIC, then sorts alternatives by BIC and residual structure. Reduced alternatives are retained explicitly so a successful routed-output architecture is compared against simpler endpoint summaries rather than interpreted in isolation. Residual profiles and decision-boundary tables show which endpoint constraints are satisfied or missed under the tested alternatives. This constrains the measured readout architecture but does not identify direct biochemical interactions.

### Supplementary Methods 6. Software parity, export bundles, and archive reproduction

The software-reproducibility supplementary section describes how the same retained examples are exercised through Python, command-line, backend, and workbench surfaces. Each export bundle is expected to include input rows, schema information, grouping fields when available, effective parameters, result JSON, result rows, Markdown report text, and file checksums. The source-distribution clean-room route rebuilds selected evidence outputs from the released archive and compares deterministic tables against retained snapshots. The archive-manifest and checksum records make the release inspectable as a software object rather than as a transient development state. This supports reproducibility of the retained evidence surfaces and does not imply PyPI publication, regulatory qualification, or private-data reproduction.

### Supplementary Methods 7. Non-example cases and interpretation boundaries

The interpretation-boundary section collects cases in which RhoDyn should withhold, narrow, or downgrade a claim. Examples include missing time units, missing condition labels, insufficient sampling density, absent grouping structure, undeclared biological windows, undeclared bounded-coupling margins, and endpoint data that cannot distinguish reduced alternatives. Ambiguous synthetic regimes and margin-boundary public cases are treated as valid outputs because they mark where residence, coupling, reserve-like, or routed-output interpretation is not resolved by the available data. Recommended wording keeps each result tied to its measured object, declared window, margin, grouping level, and model alternative. This section is a claim-boundary support surface, not a new result or a tool that infers mechanism without a declared measurement and model context.

### Supplementary figure legends

#### Supplementary Fig. 1 | Input contracts, method definitions, and executable truth cases.

Expanded method-object panels place tidy trajectory and endpoint schemas, residence-window metric definitions, executable positive and negative truth cases, and boundary examples next to the main display.

#### Supplementary Fig. 2 | Synthetic benchmark grid, baseline comparisons, and failure behavior.

The known-truth benchmark grid, residence-versus-amplitude comparisons, reduced-summary comparisons, and negative or ambiguous cases provide the detailed support for the synthetic benchmark display.

#### Supplementary Fig. 3 | Public live-cell signaling adapters and residence-amplitude sensitivity.

Public-data adapter panels document the DRG calcium and ERK GPCR residence-amplitude summaries and the window or uncertainty sensitivity analyses used to scope the public reporter demonstrations.

#### Supplementary Fig. 4 | Bounded-coupling decisions under declared margins.

Endpoint-pairing panels show the declared margin table, bounded-coupling interval display, and inconclusive decision examples that keep coupling claims tied to the stated margin and context.

#### Supplementary Fig. 5 | Reserve-like endpoint construction and uncertainty.

Measured endpoint panels separate reserve-like coordinate construction, uncertainty summaries, and label-scope boundaries so that buffering language remains tied to the assay.

#### Supplementary Fig. 6 | Routed-output reduced-architecture comparison.

The routed-output supplement provides the architecture matrix, reduced-alternative comparison, residual profile, and decision-boundary table behind the endpoint model-comparison display.

#### Supplementary Fig. 7 | Held-out validation pass and boundary cases.

Held-out validation panels show the fixed analysis plan, pass contexts, margin-boundary inconclusive contexts, margin sensitivity, and controlled-access notes that prevent validation from becoming a single unqualified score.

#### Supplementary Fig. 8 | Software parity, clean-room reproduction, and archive contents.

Cross-surface reproducibility panels document parity, export-bundle contents, clean-room reproduction summaries, archive records, checksums, and usability-path boundaries for the retained evidence surfaces.

#### Supplementary Fig. 9 | Interpretation boundaries and non-example cases.

Non-example panels collect ambiguous regimes, claim-strength caps, and recommended wording boundaries so that limitations remain visible without carrying the main argument.

### Supplementary table captions

#### Supplementary Table 1 | Input requirements, residence-window metrics, and truth-case support layers for the method-object figure.

#### Supplementary Table 2 | Known-truth synthetic benchmark outcomes, baseline comparisons, and failure-behavior rows for the synthetic benchmark figure.

#### Supplementary Table 3 | Public-data adapter details, DRG calcium and ERK GPCR residence-amplitude summaries, and uncertainty support for the public reporter figure.

#### Supplementary Table 4 | Endpoint pairing, declared margins, interval decisions, and inconclusive bounded-coupling cases for the endpoint decision figure.

#### Supplementary Table 5 | Measured endpoint-preservation coordinate, reserve-like summary rows, and uncertainty support for the reserve-like endpoint panels.

#### Supplementary Table 6 | Endpoint model rows, retained and reduced architectures, residual profiles, and model-comparison decisions for routed-output analysis.

#### Supplementary Table 7 | Held-out bounded-coupling pass cases, inconclusive contexts, margin-sensitivity rows, and controlled-access boundaries.

#### Supplementary Table 8 | Python, command-line, backend, workbench, export-bundle, clean-room reproduction, and archive surfaces used for reproducibility support.

#### Supplementary Table 9 | Failure modes, ambiguous regimes, claim-strength caps, and wording boundaries used to keep interpretation within the tested evidence.

## Supporting-data traceability note

Source-data workbooks, supplementary table bindings, processed measurement tables, model inputs and outputs, software commands, checksums, and replication metadata are retained in the package-support inventories and the public RhoDyn release surfaces. The Supplementary Information text keeps the scientific definitions, decision rules, figure legends, and table captions separate from file-path-level traceability.

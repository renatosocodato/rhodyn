<!-- METHODS-DRAFT stage=9.16 generated_utc=2026-07-03T16:13:13.527153Z draft_version=methods-draft@2026-07-03@bfe93b9fa845ed730a4b11a0edeb559ba781100c -->

# Online Methods

<!-- methods_stmt_ids=MTH-0001;MTH-0002;MTH-0003;MTH-0004;MTH-0005;MTH-0006;MTH-0007;MTH-0008;MTH-0009 claim_ids=CLM-0001;CLM-0002;CLM-0003;CLM-0004;CLM-0005 repo_paths=src/rhodyn/schema.py;src/rhodyn/residence.py;src/rhodyn/coupling.py;src/rhodyn/reserve.py;src/rhodyn/compare.py;src/rhodyn/sim.py;src/rhodyn/backend_core.py -->

All analyses in this Methods draft refer to RhoDyn v0.1.0 and to the locked evidence snapshot `stage7.8-methods-readiness@242f06c49e8310b81ac1c06a270bb6810f3f4cfc` dated 2026-06-30. The software implements residence-aware interpretation of biological trajectories and endpoint perturbation tables. The manuscript use cases are treated as reproducible demonstrations of the method object, not as evidence that the software generated the motivating RhoA/microglia manuscript. Each analysis route returns a structured result, the effective parameters used to produce it, and a boundary statement describing what the result can and cannot support.

## Input schemas and preprocessing

<!-- methods_stmt_ids=MTH-0001 claim_ids=CLM-0001;CLM-0002;CLM-0003;CLM-0004 repo_paths=src/rhodyn/schema.py -->

Input tables were parsed as typed tidy records before any residence, coupling, reserve-like, or model-comparison calculation. Trajectory rows required `cell_id`, non-negative `time`, `condition`, and numeric `signal`, with `replicate` retained when supplied. Endpoint model-comparison rows required `model`, `endpoint`, `observed`, and `predicted`, with optional non-negative `weight`. Reserve-like rows required `sample_id`, `time`, `condition`, and `response`, and bounded-coupling rows required `contrast`, `estimate`, `ci_low`, `ci_high`, and positive `margin`, with optional `rope_mass`. Rows with missing identifiers, missing columns, non-finite numeric values, negative time, or invalid margins were returned with validation issues rather than silently coerced. This preprocessing protects trace identity and biological grouping, but it cannot reconstruct missing time units, missing condition labels, or replicate structure that was not present in the input.

## Residence windows and amplitude comparators

<!-- methods_stmt_ids=MTH-0002 claim_ids=CLM-0001 repo_paths=src/rhodyn/residence.py -->

Residence analysis used a declared signal interval \(W=[\ell,h]\), where \(\ell<h\), as the biological window to be tested. For each sampled value \(x(t_k)\), RhoDyn evaluated \(I_W(t_k)=1\) when \(\ell \le x(t_k) \le h\) and \(I_W(t_k)=0\) otherwise. For ordered samples, residence time was computed as \(R_T=\sum_k \Delta t_k I_W(t_k)\), where \(\Delta t_k=t_{k+1}-t_k\), and residence fraction was \(R_F=R_T/\sum_k \Delta t_k\). The same trace also retained mean signal, maximum signal, minimum signal, total time, and the number of contiguous in-window dwell segments. The residence window is therefore a declared analysis choice, not an automatically discovered causal state.

<!-- methods_stmt_ids=MTH-0002;MTH-0003 claim_ids=CLM-0001 repo_paths=src/rhodyn/residence.py;scripts/run_stage7_3_public_signaling.py -->

Amplitude comparators were calculated on the same tidy trajectories so that residence and simpler summaries could be compared without changing the input object. The public DRG calcium and ERK GPCR demonstrations were converted into this schema from Zenodo sources 10.5281/zenodo.14907827 and 10.5281/zenodo.5836623, respectively. Derived tables preserved condition, trace identity, time, signal, and available grouping variables, and each demonstration reported window sensitivity and uncertainty summaries rather than a single unqualified residence call. These public examples test whether the residence-amplitude comparison travels across reporter systems. They do not establish a universal residence regime for every signaling trajectory.

<!-- methods_stmt_ids=MTH-0008 claim_ids=CLM-0001 repo_paths=src/rhodyn/sim.py -->

Synthetic timing utilities were used to provide positive, negative, and ambiguous truth cases for the method. First-passage summaries used \(\tau=\inf\{t:x(t)\ge q\}\) for above-threshold events, with the analogous definition for below-threshold events. Stochastic simulations used simple Gillespie and tau-leap helpers only as method-support examples. Those timing outputs are model-derived or trajectory-derived summaries, not measured cell death, injury, or molecular hazard rates unless a supplied endpoint directly measures those quantities.

## Bounded-coupling and uncertainty decisions

<!-- methods_stmt_ids=MTH-0004 claim_ids=CLM-0002 repo_paths=src/rhodyn/coupling.py -->

Bounded-coupling decisions were made only after a contrast estimate, uncertainty interval, and positive biological margin had been declared. For an estimated contrast \(\hat\delta\), interval \([L,U]\), and margin \(\Delta>0\), interval equivalence passed when \(-\Delta \le L \le U \le \Delta\). When posterior samples or a ROPE mass were available, the decision also required \(P(|\delta|\le \Delta)\ge 0.95\), unless a different threshold was explicitly supplied. For raw arrays, one-sample or Welch two-sample TOST decisions required both one-sided tests to pass at the declared alpha and the confidence interval to remain inside \(\pm\Delta\). A passing decision means equivalence within the stated margin and context, not proof that all coupling is absent.

<!-- methods_stmt_ids=MTH-0007 claim_ids=CLM-0002 repo_paths=scripts/run_stage7_5_heldout_validation.py -->

Held-out paired-reporter contexts used the same bounded-coupling decision rule with fixed thresholds, fixed margins, and recorded grouping choices. Each context was reported as passing, failing, or inconclusive, and margin-boundary cases were kept visible rather than promoted to equivalence. Bootstrap and interval summaries were interpreted at the declared grouping level. Controlled-access boundaries were recorded when a source input could be inspected only through derived tables or notes. This convention makes inconclusive evidence a valid method output rather than a failed analysis.

## Reserve-like endpoint construction

<!-- methods_stmt_ids=MTH-0005 claim_ids=CLM-0003 repo_paths=src/rhodyn/reserve.py -->

Reserve-like summaries were constructed only for response series where the measured endpoint could support a buffering-style interpretation. Signals were baseline-normalized as \(F/F_0(t)=F(t)/\bar F_0\), where \(\bar F_0\) was the mean of the declared baseline points. A bounded coordinate was then computed as \(H=\mathrm{clip}(1-(\max(F/F_0)-f_{\min})/(f_{\max}-f_{\min}),0,1)\). Larger values indicate that the observed response remained closer to the low-response bound under the supplied scaling. These values are reserve-like endpoint coordinates tied to the measured assay and are not direct assays of unmeasured biological reserve capacity.

## Routed-output model comparison

<!-- methods_stmt_ids=MTH-0006 claim_ids=CLM-0004 repo_paths=src/rhodyn/compare.py -->

Routed-output comparisons used endpoint rows containing observed values, model-predicted values, model labels, endpoint labels, and optional weights. For each candidate architecture \(m\), RhoDyn computed \(RSS_m=\sum_j w_j(y_j-\hat y_{jm})^2\), RMSE, AIC, and BIC. The reported ranking sorted candidate architectures by BIC and then by residual sum of squares. Reduced alternatives were interpreted as tested endpoint architectures, not as exhaustive mechanistic possibilities. A retained routed-output model constrains the readout structure under the supplied endpoints but does not identify direct biochemical interactions.

## Software surfaces, versioning, and reproducibility

<!-- methods_stmt_ids=MTH-0009 claim_ids=CLM-0005 repo_paths=src/rhodyn/backend_core.py -->

RhoDyn v0.1.0 was the software boundary used for the Methods evidence surface. The public GitHub release and Zenodo version DOI 10.5281/zenodo.21036616 define the citable software record, while the concept DOI 10.5281/zenodo.21036615 resolves to the current RhoDyn software concept. Python, command-line, backend, and workbench routes were checked for parity on retained examples, and export bundles retained input rows, schema information, grouping fields, effective parameters, result tables, reports, and file checksums. The source-distribution clean-room route rebuilt selected evidence outputs from the packaged archive and compared deterministic tables against committed snapshots. This supports reproducibility of the demonstrated analyses, not a new biological result, hidden private-data reproduction claim, or package-index publication claim.

# Stage 10.1 method object v2

Stage 10.1 formalizes the method-level object that RhoDyn must be judged on in a Nature Methods setting. The object is not the graphical workbench, the CLI, or the report bundle. Those are implementation surfaces. The method object is the decision structure that asks whether residence-state interpretation changes the biological conclusion relative to declared baseline summaries, bounded-coupling margins, reserve-like endpoints, routed-output alternatives, and uncertainty rules.

## Method claim

RhoDyn defines a residence-state decision object for live-cell and perturbation biology. The object reports when a declared dynamic operating window changes interpretation relative to baseline summaries and when evidence should be withheld because uncertainty, margins, grouping, or reduced alternatives do not support a call.

This is stronger than a workflow claim because the method object has explicit inputs, mathematical decision rules, counterexamples, and abstention states. It is still scoped. RhoDyn does not claim to discover the true biological window automatically, to replace amplitude analysis in all systems, or to infer molecular mechanism from fitted effective parameters.

## Input objects

RhoDyn v2 accepts four method-facing evidence objects.

| object | public representation | method role |
| --- | --- | --- |
| Trajectory table | `TrajectoryRecord` or trajectory CSV | Supports residence windows, amplitude comparators, dwell summaries, and uncertainty-sensitive trajectory calls. |
| Bounded-coupling contrast | `CouplingIntervalRecord`, `EquivalenceDecision`, or `TostDecision` | Supports margin-bounded coupling decisions for paired or contrastive reporter designs. |
| Reserve-like endpoint | `ReserveRecord` plus normalized reserve coordinate | Supports measurement-scoped buffering or fragility calls. |
| Endpoint model-comparison table | `EndpointRecord` and ranked `ModelFit` objects | Supports routed-output comparisons against reduced alternatives. |

Paired-reporter measurements can be represented at Stage 10.1 as declared bounded-coupling contrasts after extraction. A native paired-reporter tidy schema remains a useful Stage 10.2 extension for named benchmarking, but it is not a blocker for expressing the method object.

## Residence-versus-comparator decision

For trajectory \(x_i(t)\), a declared residence-window family \(W\), and a comparator family \(B\), define a residence indicator

\[
I_{\mathrm{res}}(x_i, W) =
\mathbb{1}\{R_F(x_i, W) \ge \rho_{\min}\},
\]

where \(R_F\) is the residence fraction and \(\rho_{\min}\) is declared before the call.

For an amplitude comparator \(b(x_i, B)\), define

\[
I_{\mathrm{base}}(x_i, B) =
\mathbb{1}\{b(x_i, B) \ge b_{\min}\}.
\]

The decision-divergence object is

\[
D_{\mathrm{RhoDyn}}(x_i; W, B) =
I_{\mathrm{res}}(x_i, W) -
I_{\mathrm{base}}(x_i, B).
\]

The call is interpreted as follows.

| value | call | interpretation |
| --- | --- | --- |
| \(D_{\mathrm{RhoDyn}} > 0\) | `residence_added_information` | Residence supports a dynamic operating-state interpretation that the comparator does not. |
| \(D_{\mathrm{RhoDyn}} < 0\) | `baseline_or_amplitude_sufficient` | The baseline comparator carries the positive call while residence does not. |
| \(D_{\mathrm{RhoDyn}} = 0\) | `residence_baseline_aligned` | Residence and comparator agree under the declared thresholds. |

If uncertainty exceeds the declared limit, the decision abstains regardless of the divergence value.

\[
\mathrm{call}(x_i) = \mathrm{inconclusive}
\quad \mathrm{if}\quad U(x_i) > U_{\max}.
\]

Biological interpretation. This divergence is not a mechanism score. It is a decision object that tests whether residence changes the readout interpretation relative to the comparator under declared rules.

## Bounded-coupling decision

For a contrast \(\hat\delta\), confidence interval \([L, U]\), and predeclared margin \(\Delta\), bounded coupling is supported only when

\[
-\Delta \le L \le U \le \Delta.
\]

When posterior samples are supplied, the ROPE condition must also pass.

\[
P(|\delta| \le \Delta) \ge \pi.
\]

The Stage 10.1 default is \(\pi = 0.95\).

Biological interpretation. This supports coupling bounded within the declared margin and measurement context. It does not prove absence of all coupling.

## Reserve-like endpoint decision

For a normalized response \(F/F_0(t)\), the bounded reserve-like coordinate remains

\[
H =
\mathrm{clip}
\left(
1 - \frac{\max(F/F_0)-f_{\min}}{f_{\max}-f_{\min}},
0,
1
\right).
\]

Stage 10.1 classifies \(H\) as buffered, fragile, or inconclusive using declared boundaries.

\[
\mathrm{call}(H) =
\begin{cases}
\mathrm{reserve\_like\_buffered}, & H \ge H_{\mathrm{high}},\\
\mathrm{reserve\_like\_fragile}, & H \le H_{\mathrm{low}},\\
\mathrm{inconclusive}, & H_{\mathrm{low}} < H < H_{\mathrm{high}}.
\end{cases}
\]

Biological interpretation. \(H\) is a measurement-scoped buffering coordinate. It should be called reserve only when the assay supports that biological interpretation.

## Routed-output model decision

For candidate models \(m\), RhoDyn ranks tested alternatives by BIC and requires a declared separation between the best and runner-up models.

\[
\Delta_{\mathrm{BIC}} =
\mathrm{BIC}_{\mathrm{runner\ up}} -
\mathrm{BIC}_{\mathrm{best}}.
\]

The routed-output call is promoted only when

\[
\Delta_{\mathrm{BIC}} \ge \Delta_{\min}.
\]

Otherwise the method abstains.

Biological interpretation. Routed-output selection ranks tested readout alternatives. It does not identify literal biochemical edges.

## Decision report object

Every method-object decision serializes the following fields.

| field | purpose |
| --- | --- |
| `case_id` | Stable label for the evaluated trace, contrast, endpoint, or model table. |
| `component` | Method component that produced the decision. |
| `call` | Supported, counterexample, aligned, or inconclusive method call. |
| `decision_divergence` | Residence-versus-comparator divergence when applicable. |
| `residence_score` and `baseline_score` | Paired scores used for trajectory decisions. |
| `estimate`, interval, margin, and ROPE fields | Bounded-coupling and endpoint decision support. |
| `best_model`, `runner_up_model`, and `model_delta` | Routed-output support. |
| `rationale` | Local reason for the call. |
| `interpretation_boundary` | Biological or methodological limit that prevents overclaiming. |

## Executable fixtures

Stage 10.1 adds executable fixtures under `case_studies/stage10_method_object_v2/`.

| fixture output | role |
| --- | --- |
| `stage10_1_method_object_decisions.csv` | One row per positive, counterexample, or ambiguous method-object decision. |
| `stage10_1_method_object_gate_report.json` | Machine-readable decision report and expectation checks. |
| `stage10_1_method_object_brief.md` | Reader-facing summary of the method-object fixture set. |
| `docs/stage10_1_api_gap_list.md` | API gap and extension list. |

The fixture gate passes only when every component has a positive case, a counterexample or reduced-call case, and an ambiguous or withheld-call case. This is the core Stage 10.1 advance over Stage 7.1, which defined components separately but did not make the unified method object explicit.

## Stop condition

If a future Stage 10 phase cannot express named baselines, public demonstrations, or held-out validation through this decision object, the method claim must be narrowed or the public API must be reopened before manuscript promotion.

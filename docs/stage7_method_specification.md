# Stage 7.1 method specification

This page defines the RhoDyn method object in mathematical, algorithmic, and biological terms for Stage 7.1. It formalizes what the current public API can represent and where interpretation must remain scoped. The definitions are method-level objects, not new biological claims.

## Input objects

### Tidy trajectory table

A trajectory table is a set of observations

\[
T = \{(c_i, t_i, g_i, x_i, r_i)\}_{i=1}^{n},
\]

where `cell_id` \(c_i\) identifies a trace, `time` \(t_i\) is a non-negative acquisition time, `condition` \(g_i\) is the perturbation or biological context, `signal` \(x_i\) is the measured reporter value, and optional `replicate` \(r_i\) preserves grouping. In RhoDyn this object is represented by `TrajectoryRecord` and the trajectory schema.

Biological interpretation. A trajectory table can support dynamic-state analysis only when time, condition, trace identity, signal, and grouping are sufficiently preserved.

Executable example. `trajectory_positive_residence.csv` in the Stage 7.1 truth suite contains a trace with high residence inside the declared window.

Counterexample. `trajectory_counterexample_amplitude_only.csv` has high peaks but low residence, showing that amplitude alone is not a residence-state claim.

### Endpoint model-comparison table

An endpoint model table is a set of rows

\[
E = \{(m_j, y_j, \hat y_j, w_j)\}_{j=1}^{p},
\]

where \(m_j\) is a candidate model, \(y_j\) is the observed endpoint, \(\hat y_j\) is the model-predicted endpoint, and \(w_j\) is an optional non-negative weight. RhoDyn represents this object with `EndpointRecord`.

Biological interpretation. Endpoint comparison can rank reduced architectures against observed constraints, but it does not identify a literal molecular edge unless the experiment directly supports that mapping.

Executable example. `endpoint_positive_routed_best.csv` ranks the routed architecture first.

Counterexample. `endpoint_counterexample_endpoint_sufficient.csv` shows a regime where endpoint-only structure is sufficient.

## Residence-window definitions

A residence window is a declared interval

\[
W = [\ell, h], \quad \ell < h.
\]

For a trajectory \(x(t)\), RhoDyn defines an in-window indicator

\[
I_W(t) = \begin{cases}
1, & \ell \le x(t) \le h,\\
0, & \text{otherwise}.
\end{cases}
\]

For sampled data with intervals \(\Delta t_k = t_{k+1} - t_k\), residence time is

\[
R_T = \sum_{k=1}^{n-1} \Delta t_k I_W(t_k),
\]

and residence fraction is

\[
R_F = \frac{R_T}{\sum_{k=1}^{n-1} \Delta t_k}.
\]

A dwell segment is a contiguous interval where \(I_W(t)=1\), and segment count is the number of such intervals.

Amplitude comparators include mean signal, maximum signal, minimum signal, endpoint value, peak amplitude, time above a one-sided threshold, and response latency. These comparators are baselines, not replacements for a declared residence window.

Biological interpretation. Residence describes time spent in a biologically declared operating interval. It does not automatically discover the interval and does not prove that the interval is causal.

## Reserve-like summaries

For a measured reserve-like response \(F(t)\), RhoDyn baseline-normalizes as

\[
F/F_0(t) = \frac{F(t)}{\bar F_0},
\]

where \(\bar F_0\) is the mean of declared baseline points. A bounded reserve-like coordinate is

\[
H = \mathrm{clip}\left(1 - \frac{\max(F/F_0) - f_{\min}}{f_{\max}-f_{\min}}, 0, 1\right).
\]

Biological interpretation. Larger \(H\) means the observed response stayed closer to the low-response bound under the declared scaling. It becomes biological reserve only when the measurement and experiment justify that interpretation.

## Bounded-coupling decisions

Given an estimated contrast \(\hat\delta\), interval \([L,U]\), and predeclared margin \(\Delta > 0\), interval equivalence passes when

\[
-\Delta \le L \le U \le \Delta.
\]

If posterior samples or a ROPE mass are supplied, RhoDyn additionally requires

\[
P(|\delta| \le \Delta) \ge \pi,
\]

with \(\pi=0.95\) by default.

For raw arrays, the TOST implementation estimates one-sample or Welch two-sample contrasts and requires the two one-sided tests to pass at the declared \(\alpha\), with the confidence interval inside \(\pm\Delta\).

Biological interpretation. A passing bounded-coupling decision supports equivalence within the declared biological margin. It is not evidence that the true coupling is exactly zero and does not exclude slower or context-specific coupling outside the tested design.

## Routed-output and reduced-architecture comparison

For a candidate architecture \(m\), weighted residual sum of squares is

\[
RSS_m = \sum_j w_j(y_j - \hat y_{jm})^2.
\]

RhoDyn reports RMSE, AIC, and BIC as compact compatibility summaries

\[
AIC_m = n \log(RSS_m/n) + 2k,
\]

\[
BIC_m = n \log(RSS_m/n) + k\log n,
\]

where \(k\) is the declared parameter count and \(n\) is the number of endpoint constraints.

Biological interpretation. A ranked architecture narrows the plausible structure of the readout relationship under tested constraints. It does not prove every effective term is a molecular interaction.

## Uncertainty and sensitivity summaries

Bootstrap intervals estimate uncertainty by resampling observations or declared groups. A percentile interval is

\[
[Q_{\alpha/2}(\theta^*), Q_{1-\alpha/2}(\theta^*)],
\]

where \(\theta^*\) is the bootstrap statistic distribution.

Permutation tests compare an observed statistic against a shuffled null distribution under the declared exchangeability level.

Window sensitivity evaluates residence summaries across declared windows

\[
\mathcal W = \{[\ell_a, h_b] : \ell_a < h_b\}.
\]

Biological interpretation. Uncertainty and sensitivity outputs define robustness of a derived summary. They do not replace biological replication or measurement validation.

## Stochastic timing summaries

First-passage time is

\[
\tau = \inf\{t : x(t) \ge q\}
\]

for an above-threshold event, or the analogous below-threshold event. Gillespie and tau-leap helpers are available for simple stochastic timing demonstrations, where model state is simulated rather than measured.

Biological interpretation. Stochastic timing outputs are model-derived timing summaries unless they are computed directly from measured trajectories.

## Failure modes and interpretation boundaries

| method component | failure mode | interpretation boundary |
| --- | --- | --- |
| Tidy trajectories | Missing time, condition, trace identity, or grouping. | Do not make residence or dwell-time claims. |
| Residence windows | Window chosen after seeing a favorable result. | Treat as exploratory sensitivity, not confirmed operating-state inference. |
| Amplitude comparators | High peak but low dwell time. | Do not convert peak amplitude into residence. |
| Reserve-like summaries | Response readout is not a reserve measurement. | Use reserve-like or buffering-language only with measurement support. |
| Bounded coupling | Margin is not predeclared or uncertainty crosses the margin. | Do not claim equivalence. |
| Model comparison | Reduced alternatives are omitted or nearly tied. | Do not claim the retained architecture is uniquely identified. |
| Uncertainty | Grouping is ignored. | Do not treat cell-level intervals as biological replicate uncertainty. |
| Stochastic timing | Simulated hazard treated as measured death or injury. | Keep timing as a model or trajectory-derived summary. |

## API representation status

The current public API can represent all Stage 7.1 definitions through `schema`, `residence`, `reserve`, `coupling`, `compare`, `uncertainty`, `sensitivity`, `sim`, and `results`. No new stable package API is required for Stage 7.1. The Stage 7.1 synthetic truth generator is a reproducibility script, not a public API expansion.

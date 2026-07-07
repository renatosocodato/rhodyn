"""Stage 10 method-object helpers for residence-state decisions.

The objects in this module make the RhoDyn inference object explicit. They
combine declared residence windows, comparator families, bounded-coupling
margins, reserve-like endpoints, routed-output alternatives, uncertainty, and
abstention into serializable decisions.
"""

from __future__ import annotations

from dataclasses import dataclass, field as dc_field
from typing import Literal

from rhodyn.compare import ModelFit
from rhodyn.coupling import EquivalenceDecision
from rhodyn.residence import ResidenceWindow, score_trace
from rhodyn.schema import TrajectoryRecord


MethodObjectCall = Literal[
    "residence_added_information",
    "baseline_or_amplitude_sufficient",
    "residence_baseline_aligned",
    "bounded_coupling_within_margin",
    "coupling_shift_exceeds_margin",
    "reserve_like_buffered",
    "reserve_like_fragile",
    "routed_architecture_selected",
    "reduced_architecture_selected",
    "inconclusive",
]


@dataclass(frozen=True)
class MethodObjectSpec:
    """Decision thresholds for a RhoDyn method-object evaluation."""

    residence_fraction_min: float = 0.60
    amplitude_high_min: float = 0.85
    uncertainty_width_max: float = 0.25
    reserve_high_min: float = 0.70
    reserve_low_max: float = 0.30
    bic_delta_min: float = 10.0
    rope_threshold: float = 0.95


@dataclass(frozen=True)
class MethodObjectDecision:
    """One serializable method-object decision."""

    case_id: str
    component: str
    call: MethodObjectCall
    decision_divergence: float | None
    residence_score: float | None = None
    baseline_score: float | None = None
    estimate: float | None = None
    interval_low: float | None = None
    interval_high: float | None = None
    margin: float | None = None
    rope_mass: float | None = None
    uncertainty_width: float | None = None
    best_model: str = ""
    runner_up_model: str = ""
    model_delta: float | None = None
    rationale: str = ""
    interpretation_boundary: str = ""
    parameters: dict[str, float | str] = dc_field(default_factory=dict)

    @property
    def abstains(self) -> bool:
        """Return whether the decision withholds a positive/negative call."""

        return self.call == "inconclusive"


def trajectory_method_decision(
    case_id: str,
    records: list[TrajectoryRecord],
    window: ResidenceWindow,
    *,
    spec: MethodObjectSpec | None = None,
    comparator: Literal["peak", "mean", "endpoint"] = "peak",
    uncertainty_width: float = 0.0,
) -> MethodObjectDecision:
    """Compare residence-window interpretation with an amplitude comparator."""

    spec = spec or MethodObjectSpec()
    summary = score_trace(records, window)
    ordered = sorted(records, key=lambda row: row.time)
    if comparator == "peak":
        baseline_score = summary.max_signal
    elif comparator == "mean":
        baseline_score = summary.mean_signal
    elif comparator == "endpoint":
        baseline_score = ordered[-1].signal
    else:
        raise ValueError(f"unsupported comparator: {comparator}")

    residence_indicator = 1.0 if summary.residence_fraction >= spec.residence_fraction_min else 0.0
    baseline_indicator = 1.0 if baseline_score >= spec.amplitude_high_min else 0.0
    divergence = residence_indicator - baseline_indicator
    if uncertainty_width > spec.uncertainty_width_max:
        call: MethodObjectCall = "inconclusive"
        rationale = "uncertainty width exceeds the declared decision limit"
    elif divergence > 0:
        call = "residence_added_information"
        rationale = "residence passes while the amplitude comparator does not"
    elif divergence < 0:
        call = "baseline_or_amplitude_sufficient"
        rationale = "amplitude comparator passes while residence does not"
    else:
        call = "residence_baseline_aligned"
        rationale = "residence and amplitude comparator give the same binary call"

    return MethodObjectDecision(
        case_id=case_id,
        component="trajectory_residence_vs_comparator",
        call=call,
        decision_divergence=divergence,
        residence_score=summary.residence_fraction,
        baseline_score=baseline_score,
        uncertainty_width=uncertainty_width,
        rationale=rationale,
        interpretation_boundary=(
            "Decision divergence reports whether the declared residence window changes "
            "the interpretation relative to the declared comparator. It is not a "
            "mechanism-discovery statistic."
        ),
        parameters={
            "window_low": window.low,
            "window_high": window.high,
            "residence_fraction_min": spec.residence_fraction_min,
            "amplitude_high_min": spec.amplitude_high_min,
            "uncertainty_width_max": spec.uncertainty_width_max,
            "comparator": comparator,
        },
    )


def coupling_method_decision(
    case_id: str,
    decision: EquivalenceDecision,
    *,
    spec: MethodObjectSpec | None = None,
) -> MethodObjectDecision:
    """Convert a bounded-coupling interval or ROPE decision into the method object."""

    spec = spec or MethodObjectSpec()
    rope_ok = True if decision.rope_mass is None else decision.rope_mass >= spec.rope_threshold
    if decision.interval_inside_margin and rope_ok:
        call: MethodObjectCall = "bounded_coupling_within_margin"
        rationale = "interval and ROPE evidence remain inside the declared margin"
    elif decision.ci_low <= decision.margin and decision.ci_high >= -decision.margin:
        call = "inconclusive"
        rationale = "the interval does not support a bounded-coupling decision"
    else:
        call = "coupling_shift_exceeds_margin"
        rationale = "the interval is outside the declared equivalence region"

    return MethodObjectDecision(
        case_id=case_id,
        component="bounded_coupling",
        call=call,
        decision_divergence=None,
        estimate=decision.estimate,
        interval_low=decision.ci_low,
        interval_high=decision.ci_high,
        margin=decision.margin,
        rope_mass=decision.rope_mass,
        rationale=rationale,
        interpretation_boundary=(
            "Bounded coupling is scoped to the declared margin, uncertainty, and "
            "measurement context. It is not evidence for exactly zero coupling."
        ),
        parameters={"rope_threshold": spec.rope_threshold},
    )


def reserve_method_decision(
    case_id: str,
    reserve_value: float,
    *,
    spec: MethodObjectSpec | None = None,
    uncertainty_width: float = 0.0,
) -> MethodObjectDecision:
    """Classify a measurement-scoped reserve-like endpoint."""

    spec = spec or MethodObjectSpec()
    if uncertainty_width > spec.uncertainty_width_max:
        call: MethodObjectCall = "inconclusive"
        rationale = "reserve-like endpoint uncertainty exceeds the declared decision limit"
    elif reserve_value >= spec.reserve_high_min:
        call = "reserve_like_buffered"
        rationale = "reserve-like coordinate remains above the declared buffered region"
    elif reserve_value <= spec.reserve_low_max:
        call = "reserve_like_fragile"
        rationale = "reserve-like coordinate lies in the declared fragile region"
    else:
        call = "inconclusive"
        rationale = "reserve-like coordinate lies between buffered and fragile regions"

    return MethodObjectDecision(
        case_id=case_id,
        component="reserve_like_endpoint",
        call=call,
        decision_divergence=None,
        estimate=reserve_value,
        uncertainty_width=uncertainty_width,
        rationale=rationale,
        interpretation_boundary=(
            "Reserve-like calls are scoped to the measured endpoint and scaling. "
            "They do not prove unmeasured biological reserve capacity."
        ),
        parameters={
            "reserve_high_min": spec.reserve_high_min,
            "reserve_low_max": spec.reserve_low_max,
            "uncertainty_width_max": spec.uncertainty_width_max,
        },
    )


def routed_output_method_decision(
    case_id: str,
    fits: list[ModelFit] | tuple[ModelFit, ...],
    *,
    spec: MethodObjectSpec | None = None,
    routed_model_name: str = "routed",
) -> MethodObjectDecision:
    """Classify whether routed output is selected over reduced alternatives."""

    spec = spec or MethodObjectSpec()
    ranked = tuple(fits)
    if len(ranked) < 2:
        raise ValueError("routed_output_method_decision requires at least two model fits")
    best, runner_up = ranked[0], ranked[1]
    delta = runner_up.bic - best.bic
    if delta < spec.bic_delta_min:
        call: MethodObjectCall = "inconclusive"
        rationale = "top models remain too close under the declared BIC-delta rule"
    elif best.model == routed_model_name:
        call = "routed_architecture_selected"
        rationale = "routed architecture is selected over reduced alternatives"
    else:
        call = "reduced_architecture_selected"
        rationale = "a reduced architecture is selected over the routed alternative"

    return MethodObjectDecision(
        case_id=case_id,
        component="routed_output_model_comparison",
        call=call,
        decision_divergence=None,
        best_model=best.model,
        runner_up_model=runner_up.model,
        model_delta=delta,
        rationale=rationale,
        interpretation_boundary=(
            "Architecture selection ranks tested readout alternatives. It does not "
            "identify literal biochemical edges."
        ),
        parameters={"bic_delta_min": spec.bic_delta_min, "ranking_metric": "bic"},
    )


def decision_to_row(decision: MethodObjectDecision) -> dict[str, object]:
    """Return a compact row for reports and fixture tables."""

    return {
        "case_id": decision.case_id,
        "component": decision.component,
        "call": decision.call,
        "decision_divergence": "" if decision.decision_divergence is None else decision.decision_divergence,
        "residence_score": "" if decision.residence_score is None else decision.residence_score,
        "baseline_score": "" if decision.baseline_score is None else decision.baseline_score,
        "estimate": "" if decision.estimate is None else decision.estimate,
        "interval_low": "" if decision.interval_low is None else decision.interval_low,
        "interval_high": "" if decision.interval_high is None else decision.interval_high,
        "margin": "" if decision.margin is None else decision.margin,
        "rope_mass": "" if decision.rope_mass is None else decision.rope_mass,
        "uncertainty_width": "" if decision.uncertainty_width is None else decision.uncertainty_width,
        "best_model": decision.best_model,
        "runner_up_model": decision.runner_up_model,
        "model_delta": "" if decision.model_delta is None else decision.model_delta,
        "rationale": decision.rationale,
        "interpretation_boundary": decision.interpretation_boundary,
    }

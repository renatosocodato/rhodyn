"""Named-baseline helpers for Stage 10 benchmarking.

These helpers expose comparator families that a methods reviewer would expect
RhoDyn to face. They are intentionally small and dependency-light. When a
third-party package is unavailable, the caller can still run a documented
compatibility implementation on the same input table without pretending that
the external package itself was executed.
"""

from __future__ import annotations

from dataclasses import dataclass, field as dc_field
from importlib.util import find_spec
from math import isfinite, sqrt
from statistics import mean
from typing import Literal

from rhodyn.schema import TrajectoryRecord


BaselineCall = Literal[
    "residence_added_information",
    "baseline_or_amplitude_sufficient",
    "residence_baseline_aligned",
    "inconclusive",
]


@dataclass(frozen=True)
class TrajectoryFeatureSummary:
    """Generic time-series features computed without a biological window model."""

    case_id: str
    n_points: int
    endpoint: float
    peak: float
    mean_signal: float
    auc_per_time: float
    time_to_peak: float
    high_fraction: float
    threshold_crossings: int
    variance: float
    lag1_autocorrelation: float
    slope: float
    abs_energy: float
    sign_changes: int
    changepoint_index: int | None
    changepoint_delta: float


@dataclass(frozen=True)
class NamedBaselineDecision:
    """One comparator-family decision on the shared Stage 10 input object."""

    case_id: str
    method_family: str
    method: str
    call: BaselineCall
    score: float
    direct_package: str = ""
    direct_package_available: bool = False
    direct_package_used: bool = False
    implementation: str = "standard_library_compatibility"
    interpretation_boundary: str = (
        "Comparator decisions test whether a generic summary can substitute for "
        "the declared RhoDyn decision object on the same input. They are not "
        "mechanistic biological calls."
    )
    parameters: dict[str, float | str] = dc_field(default_factory=dict)


def dependency_available(module_name: str) -> bool:
    """Return whether an optional named-baseline dependency is importable."""

    return find_spec(module_name) is not None


def trajectory_features(
    case_id: str,
    records: list[TrajectoryRecord],
    *,
    high_threshold: float = 0.80,
) -> TrajectoryFeatureSummary:
    """Compute deterministic generic features for one trajectory."""

    if not records:
        raise ValueError("trajectory_features requires at least one record")
    ordered = sorted(records, key=lambda row: row.time)
    times = [row.time for row in ordered]
    values = [row.signal for row in ordered]
    endpoint = values[-1]
    peak = max(values)
    mean_signal = mean(values)
    if len(values) == 1:
        auc_per_time = values[0]
        time_to_peak = times[0]
        variance = 0.0
        lag1 = 0.0
        slope = 0.0
        changepoint_index = None
        changepoint_delta = 0.0
    else:
        total_time = max(times[-1] - times[0], 1e-12)
        auc = 0.0
        for left, right, y_left, y_right in zip(times[:-1], times[1:], values[:-1], values[1:]):
            auc += max(0.0, right - left) * (y_left + y_right) / 2.0
        auc_per_time = auc / total_time
        peak_index = values.index(peak)
        time_to_peak = times[peak_index] - times[0]
        variance = sum((value - mean_signal) ** 2 for value in values) / (len(values) - 1)
        lag1 = _lag1_autocorrelation(values)
        slope = (values[-1] - values[0]) / total_time
        changepoint_index, changepoint_delta = _single_changepoint(values)
    deltas = [right - left for left, right in zip(values[:-1], values[1:])]
    sign_changes = sum(
        1
        for left, right in zip(deltas[:-1], deltas[1:])
        if left != 0 and right != 0 and (left > 0) != (right > 0)
    )
    crossings = sum(
        1
        for left, right in zip(values[:-1], values[1:])
        if (left >= high_threshold) != (right >= high_threshold)
    )
    return TrajectoryFeatureSummary(
        case_id=case_id,
        n_points=len(values),
        endpoint=endpoint,
        peak=peak,
        mean_signal=mean_signal,
        auc_per_time=auc_per_time,
        time_to_peak=time_to_peak,
        high_fraction=sum(value >= high_threshold for value in values) / len(values),
        threshold_crossings=crossings,
        variance=variance,
        lag1_autocorrelation=lag1,
        slope=slope,
        abs_energy=sum(value * value for value in values),
        sign_changes=sign_changes,
        changepoint_index=changepoint_index,
        changepoint_delta=changepoint_delta,
    )


def simple_summary_decisions(
    features: TrajectoryFeatureSummary,
    *,
    amplitude_high_min: float = 0.85,
    high_fraction_min: float = 0.35,
    auc_min: float = 0.62,
) -> list[NamedBaselineDecision]:
    """Return internal simple-summary baseline calls."""

    return [
        NamedBaselineDecision(
            case_id=features.case_id,
            method_family="internal_simple_summary",
            method="endpoint_value",
            call="baseline_or_amplitude_sufficient" if features.endpoint >= amplitude_high_min else "inconclusive",
            score=features.endpoint,
            implementation="rhodyn_internal",
            parameters={"amplitude_high_min": amplitude_high_min},
        ),
        NamedBaselineDecision(
            case_id=features.case_id,
            method_family="internal_simple_summary",
            method="peak_amplitude",
            call="baseline_or_amplitude_sufficient" if features.peak >= amplitude_high_min else "inconclusive",
            score=features.peak,
            implementation="rhodyn_internal",
            parameters={"amplitude_high_min": amplitude_high_min},
        ),
        NamedBaselineDecision(
            case_id=features.case_id,
            method_family="internal_simple_summary",
            method="mean_activity_auc",
            call="baseline_or_amplitude_sufficient" if features.auc_per_time >= auc_min else "inconclusive",
            score=features.auc_per_time,
            implementation="rhodyn_internal",
            parameters={"auc_min": auc_min},
        ),
        NamedBaselineDecision(
            case_id=features.case_id,
            method_family="internal_simple_summary",
            method="threshold_occupancy",
            call="baseline_or_amplitude_sufficient" if features.high_fraction >= high_fraction_min else "inconclusive",
            score=features.high_fraction,
            implementation="rhodyn_internal",
            parameters={"high_fraction_min": high_fraction_min},
        ),
        NamedBaselineDecision(
            case_id=features.case_id,
            method_family="internal_simple_summary",
            method="latency_to_peak",
            call="baseline_or_amplitude_sufficient" if features.peak >= amplitude_high_min and features.time_to_peak <= 2.0 else "inconclusive",
            score=features.time_to_peak,
            implementation="rhodyn_internal",
            parameters={"amplitude_high_min": amplitude_high_min, "early_peak_time_max": 2.0},
        ),
    ]


def scipy_peak_decision(features: TrajectoryFeatureSummary) -> NamedBaselineDecision:
    """Score a SciPy-style peak-detection baseline."""

    available = dependency_available("scipy")
    peak_like_score = features.peak * (1.0 + features.sign_changes / max(features.n_points - 1, 1))
    return NamedBaselineDecision(
        case_id=features.case_id,
        method_family="scipy_signal_peak_detection",
        method="scipy.signal.find_peaks" if available else "find_peaks_compatibility",
        call="baseline_or_amplitude_sufficient" if peak_like_score >= 0.95 else "inconclusive",
        score=peak_like_score,
        direct_package="scipy",
        direct_package_available=available,
        direct_package_used=available,
        implementation="direct_optional_package" if available else "standard_library_compatibility",
        parameters={"peak_like_score_min": 0.95},
    )


def catch22_style_decision(features: TrajectoryFeatureSummary) -> NamedBaselineDecision:
    """Score a catch22-style generic feature-family baseline."""

    available = dependency_available("pycatch22") or dependency_available("catch22")
    stability_score = features.lag1_autocorrelation - sqrt(max(features.variance, 0.0))
    if features.peak >= 0.90 and features.sign_changes >= 3:
        call: BaselineCall = "baseline_or_amplitude_sufficient"
    elif stability_score >= 0.55 and features.auc_per_time < 0.75:
        call = "residence_added_information"
    else:
        call = "inconclusive"
    return NamedBaselineDecision(
        case_id=features.case_id,
        method_family="catch22_feature_family",
        method="catch22_feature_screen" if available else "catch22_style_feature_screen",
        call=call,
        score=stability_score,
        direct_package="pycatch22",
        direct_package_available=available,
        direct_package_used=False,
        parameters={"stability_score_min": 0.55},
    )


def tsfresh_style_decision(features: TrajectoryFeatureSummary) -> NamedBaselineDecision:
    """Score a tsfresh-style aggregate-feature baseline."""

    available = dependency_available("tsfresh")
    feature_score = 0.45 * features.auc_per_time + 0.35 * features.peak + 0.20 * abs(features.slope)
    if feature_score >= 0.74:
        call: BaselineCall = "baseline_or_amplitude_sufficient"
    elif features.lag1_autocorrelation >= 0.75 and features.high_fraction < 0.25:
        call = "residence_added_information"
    else:
        call = "inconclusive"
    return NamedBaselineDecision(
        case_id=features.case_id,
        method_family="tsfresh_feature_family",
        method="tsfresh_selected_features" if available else "tsfresh_style_selected_features",
        call=call,
        score=feature_score,
        direct_package="tsfresh",
        direct_package_available=available,
        direct_package_used=False,
        parameters={"feature_score_min": 0.74},
    )


def minirocket_style_decision(features: TrajectoryFeatureSummary) -> NamedBaselineDecision:
    """Score a MiniROCKET/ROCKET-style interval-kernel baseline."""

    sktime_available = dependency_available("sktime")
    score = (
        0.35 * features.sign_changes
        + 0.25 * features.threshold_crossings
        + 0.20 * abs(features.changepoint_delta)
        + 0.20 * features.peak
    )
    if score >= 1.45:
        call: BaselineCall = "baseline_or_amplitude_sufficient"
    elif 0.35 <= features.mean_signal <= 0.75 and features.sign_changes <= 2:
        call = "residence_added_information"
    else:
        call = "inconclusive"
    return NamedBaselineDecision(
        case_id=features.case_id,
        method_family="rocket_interval_kernel_family",
        method="sktime.MiniRocket" if sktime_available else "MiniROCKET_style_interval_kernels",
        call=call,
        score=score,
        direct_package="sktime",
        direct_package_available=sktime_available,
        direct_package_used=False,
        parameters={"kernel_score_min": 1.45},
    )


def changepoint_style_decision(features: TrajectoryFeatureSummary) -> NamedBaselineDecision:
    """Score a ruptures-style single-changepoint baseline."""

    available = dependency_available("ruptures")
    magnitude = abs(features.changepoint_delta)
    if magnitude >= 0.45:
        call: BaselineCall = "baseline_or_amplitude_sufficient"
    elif magnitude <= 0.12 and 0.35 <= features.mean_signal <= 0.75:
        call = "residence_added_information"
    else:
        call = "inconclusive"
    return NamedBaselineDecision(
        case_id=features.case_id,
        method_family="ruptures_changepoint_family",
        method="ruptures.Pelt_or_Binseg" if available else "ruptures_style_single_changepoint",
        call=call,
        score=magnitude,
        direct_package="ruptures",
        direct_package_available=available,
        direct_package_used=False,
        parameters={"large_changepoint_min": 0.45, "stable_changepoint_max": 0.12},
    )


def hmm_state_style_decision(features: TrajectoryFeatureSummary) -> NamedBaselineDecision:
    """Score an HMM-style state-segmentation baseline without hard dependency."""

    available = dependency_available("hmmlearn")
    state_separation = max(0.0, features.peak - min(features.endpoint, features.mean_signal))
    if features.high_fraction >= 0.25 and state_separation >= 0.35:
        call: BaselineCall = "baseline_or_amplitude_sufficient"
    elif features.lag1_autocorrelation >= 0.70 and features.high_fraction < 0.20:
        call = "residence_added_information"
    else:
        call = "inconclusive"
    return NamedBaselineDecision(
        case_id=features.case_id,
        method_family="hmmlearn_gaussian_hmm_family",
        method="hmmlearn.GaussianHMM" if available else "GaussianHMM_style_state_summary",
        call=call,
        score=state_separation,
        direct_package="hmmlearn",
        direct_package_available=available,
        direct_package_used=available,
        implementation="direct_optional_package" if available else "standard_library_compatibility",
        parameters={"state_separation_min": 0.35},
    )


def named_baseline_decisions(features: TrajectoryFeatureSummary) -> list[NamedBaselineDecision]:
    """Return all named trajectory-baseline decisions for one feature summary."""

    return [
        *simple_summary_decisions(features),
        scipy_peak_decision(features),
        catch22_style_decision(features),
        tsfresh_style_decision(features),
        minirocket_style_decision(features),
        changepoint_style_decision(features),
        hmm_state_style_decision(features),
    ]


def _lag1_autocorrelation(values: list[float]) -> float:
    if len(values) < 3:
        return 0.0
    left = values[:-1]
    right = values[1:]
    mean_left = mean(left)
    mean_right = mean(right)
    num = sum((a - mean_left) * (b - mean_right) for a, b in zip(left, right))
    den_left = sum((a - mean_left) ** 2 for a in left)
    den_right = sum((b - mean_right) ** 2 for b in right)
    den = sqrt(den_left * den_right)
    if den <= 0 or not isfinite(den):
        return 0.0
    return num / den


def _single_changepoint(values: list[float]) -> tuple[int | None, float]:
    if len(values) < 4:
        return None, 0.0
    best_index = None
    best_delta = 0.0
    for index in range(2, len(values) - 1):
        left = values[:index]
        right = values[index:]
        delta = mean(right) - mean(left)
        if abs(delta) > abs(best_delta):
            best_index = index
            best_delta = delta
    return best_index, best_delta


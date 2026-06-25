"""Typed result objects for dynamic-state analyses."""

from __future__ import annotations

from dataclasses import dataclass, field as dc_field
from importlib.metadata import PackageNotFoundError, version
from typing import Any

from rhodyn.compare import ModelFit
from rhodyn.coupling import EquivalenceDecision
from rhodyn.residence import TraceResidenceSummary


def software_version() -> str:
    """Return the installed RhoDyn version, with a source-tree fallback."""

    try:
        return version("rhodyn")
    except PackageNotFoundError:
        return "0.1.0"


@dataclass(frozen=True)
class GroupMetadata:
    """Biological and acquisition grouping carried with a result."""

    condition: str = ""
    cell_id: str = ""
    sample_id: str = ""
    replicate: str = ""
    field: str = ""
    well: str = ""
    donor: str = ""
    batch: str = ""
    experiment: str = ""
    extra: dict[str, str] = dc_field(default_factory=dict)
    grouping_levels: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.grouping_levels:
            object.__setattr__(self, "grouping_levels", self.present_levels)

    @property
    def present_levels(self) -> tuple[str, ...]:
        """Return grouping fields that are populated."""

        core = {
            "condition": self.condition,
            "cell_id": self.cell_id,
            "sample_id": self.sample_id,
            "replicate": self.replicate,
            "field": self.field,
            "well": self.well,
            "donor": self.donor,
            "batch": self.batch,
            "experiment": self.experiment,
        }
        return tuple(key for key, value in core.items() if value)


@dataclass(frozen=True)
class ResultProvenance:
    """Schema, parameter, and version context for a result."""

    schema_kind: str
    parameters: dict[str, Any] = dc_field(default_factory=dict)
    software_version: str = dc_field(default_factory=software_version)
    source: str = ""


@dataclass(frozen=True)
class ResidenceResult:
    """Residence-window result for one trajectory."""

    group: GroupMetadata
    n_points: int
    residence_fraction: float
    residence_time: float
    total_time: float
    mean_signal: float
    max_signal: float
    min_signal: float
    segment_count: int
    segments: tuple[Any, ...]
    provenance: ResultProvenance
    value_kind: str = "derived_summary"


@dataclass(frozen=True)
class ReserveResult:
    """Reserve-like buffering result for one biological sample."""

    group: GroupMetadata
    reserve: float
    peak_response: float
    n_points: int
    provenance: ResultProvenance
    value_kind: str = "derived_summary"


@dataclass(frozen=True)
class CouplingResult:
    """Bounded-coupling or equivalence decision with its declared margin."""

    contrast: str
    group: GroupMetadata
    estimate: float
    ci_low: float
    ci_high: float
    margin: float
    interval_inside_margin: bool
    passes: bool
    decision_rule: str
    provenance: ResultProvenance
    rope_mass: float | None = None
    rope_threshold: float = 0.95
    value_kind: str = "decision_rule"


@dataclass(frozen=True)
class UncertaintyInterval:
    """Uncertainty interval for a declared statistic and grouping assumption."""

    method: str
    estimate: float
    lower: float
    upper: float
    confidence_level: float
    n: int
    group: GroupMetadata
    provenance: ResultProvenance
    value_kind: str = "uncertainty_interval"


@dataclass(frozen=True)
class SensitivityPoint:
    """One residence-window sensitivity coordinate."""

    low: float
    high: float
    residence_fraction: float
    residence_time: float
    mean_signal: float
    segment_count: int


@dataclass(frozen=True)
class SensitivityCurveResult:
    """Residence sensitivity result across a declared window grid."""

    group: GroupMetadata
    points: tuple[SensitivityPoint, ...]
    qualifying_window_count: int
    provenance: ResultProvenance
    value_kind: str = "sensitivity_curve"


@dataclass(frozen=True)
class ModelComparisonResult:
    """Reduced-model comparison result."""

    fits: tuple[ModelFit, ...]
    best_model: str
    ranking_metric: str
    provenance: ResultProvenance
    value_kind: str = "model_comparison"


def residence_result_from_summary(
    summary: TraceResidenceSummary,
    *,
    parameters: dict[str, Any] | None = None,
    source: str = "",
) -> ResidenceResult:
    """Attach group and provenance context to a residence summary."""

    return ResidenceResult(
        group=GroupMetadata(condition=summary.condition, cell_id=summary.cell_id),
        n_points=summary.n_points,
        residence_fraction=summary.residence_fraction,
        residence_time=summary.residence_time,
        total_time=summary.total_time,
        mean_signal=summary.mean_signal,
        max_signal=summary.max_signal,
        min_signal=summary.min_signal,
        segment_count=len(summary.segments),
        segments=summary.segments,
        provenance=ResultProvenance(schema_kind="trajectory", parameters=parameters or {}, source=source),
    )


def coupling_result_from_decision(
    contrast: str,
    decision: EquivalenceDecision,
    *,
    group: GroupMetadata | None = None,
    parameters: dict[str, Any] | None = None,
    source: str = "",
    decision_rule: str = "interval_inside_margin_and_rope",
) -> CouplingResult:
    """Attach group and provenance context to a coupling decision."""

    return CouplingResult(
        contrast=contrast,
        group=group or GroupMetadata(),
        estimate=decision.estimate,
        ci_low=decision.ci_low,
        ci_high=decision.ci_high,
        margin=decision.margin,
        interval_inside_margin=decision.interval_inside_margin,
        rope_mass=decision.rope_mass,
        rope_threshold=decision.rope_threshold,
        passes=decision.passes,
        decision_rule=decision_rule,
        provenance=ResultProvenance(schema_kind="coupling", parameters=parameters or {}, source=source),
    )


def model_comparison_result_from_fits(
    fits: list[ModelFit] | tuple[ModelFit, ...],
    *,
    parameters: dict[str, Any] | None = None,
    source: str = "",
    ranking_metric: str = "bic",
) -> ModelComparisonResult:
    """Attach provenance context to ranked model fits."""

    ranked = tuple(fits)
    return ModelComparisonResult(
        fits=ranked,
        best_model=ranked[0].model if ranked else "",
        ranking_metric=ranking_metric,
        provenance=ResultProvenance(schema_kind="endpoint", parameters=parameters or {}, source=source),
    )

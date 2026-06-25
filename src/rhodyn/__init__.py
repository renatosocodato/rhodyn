"""RhoDyn core package."""

from rhodyn.compare import ModelFit, rank_model_fits
from rhodyn.extras import MissingOptionalDependency, OptionalExtra, extra_plan, require_extra
from rhodyn.models import ControllerParams, simulate_controller
from rhodyn.residence import ResidenceWindow, score_trace
from rhodyn.results import (
    CouplingResult,
    GroupMetadata,
    ModelComparisonResult,
    ResidenceResult,
    ReserveResult,
    ResultProvenance,
    SensitivityCurveResult,
    SensitivityPoint,
    UncertaintyInterval,
    coupling_result_from_decision,
    model_comparison_result_from_fits,
    residence_result_from_summary,
)
from rhodyn.schema import CouplingIntervalRecord, EndpointRecord, ReserveRecord, TrajectoryRecord, schema_specs

__all__ = [
    "ControllerParams",
    "CouplingIntervalRecord",
    "CouplingResult",
    "EndpointRecord",
    "GroupMetadata",
    "MissingOptionalDependency",
    "ModelFit",
    "ModelComparisonResult",
    "OptionalExtra",
    "ResidenceResult",
    "ResidenceWindow",
    "ReserveRecord",
    "ReserveResult",
    "ResultProvenance",
    "SensitivityCurveResult",
    "SensitivityPoint",
    "TrajectoryRecord",
    "UncertaintyInterval",
    "coupling_result_from_decision",
    "extra_plan",
    "model_comparison_result_from_fits",
    "rank_model_fits",
    "residence_result_from_summary",
    "require_extra",
    "schema_specs",
    "score_trace",
    "simulate_controller",
]

__version__ = "0.1.0"

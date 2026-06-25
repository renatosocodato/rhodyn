"""RhoDyn core package."""

from rhodyn.compare import ModelFit, rank_model_fits
from rhodyn.coupling import (
    EquivalenceDecision,
    TostDecision,
    equivalence_from_interval,
    one_sample_tost,
    rope_decision,
    rope_mass,
    two_sample_welch_tost,
)
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
    coupling_result_from_tost,
    model_comparison_result_from_fits,
    residence_result_from_summary,
)
from rhodyn.schema import CouplingIntervalRecord, EndpointRecord, ReserveRecord, TrajectoryRecord, schema_specs

__all__ = [
    "ControllerParams",
    "CouplingIntervalRecord",
    "CouplingResult",
    "EndpointRecord",
    "EquivalenceDecision",
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
    "TostDecision",
    "TrajectoryRecord",
    "UncertaintyInterval",
    "coupling_result_from_decision",
    "coupling_result_from_tost",
    "equivalence_from_interval",
    "extra_plan",
    "model_comparison_result_from_fits",
    "one_sample_tost",
    "rank_model_fits",
    "residence_result_from_summary",
    "require_extra",
    "rope_decision",
    "rope_mass",
    "schema_specs",
    "score_trace",
    "simulate_controller",
    "two_sample_welch_tost",
]

__version__ = "0.1.0"

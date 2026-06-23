"""RhoDyn core package."""

from rhodyn.compare import ModelFit, rank_model_fits
from rhodyn.extras import MissingOptionalDependency, OptionalExtra, extra_plan, require_extra
from rhodyn.models import ControllerParams, simulate_controller
from rhodyn.residence import ResidenceWindow, score_trace
from rhodyn.schema import CouplingIntervalRecord, EndpointRecord, ReserveRecord, TrajectoryRecord, schema_specs

__all__ = [
    "ControllerParams",
    "CouplingIntervalRecord",
    "EndpointRecord",
    "MissingOptionalDependency",
    "ModelFit",
    "OptionalExtra",
    "ResidenceWindow",
    "ReserveRecord",
    "TrajectoryRecord",
    "extra_plan",
    "rank_model_fits",
    "require_extra",
    "schema_specs",
    "score_trace",
    "simulate_controller",
]

__version__ = "0.1.0"

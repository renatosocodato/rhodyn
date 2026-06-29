"""Build Stage 7.1 synthetic truth cases for RhoDyn method definitions.

The generated cases are method-validation fixtures, not biological evidence.
They exercise positive, counterexample, and ambiguous regimes for the public
RhoDyn analysis objects without adding a new stable API surface.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from dataclasses import asdict
from pathlib import Path
from statistics import mean

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from rhodyn.compare import rank_model_fits
from rhodyn.coupling import equivalence_from_interval
from rhodyn.reserve import ff_over_f0, reserve_coordinate
from rhodyn.residence import ResidenceWindow, score_records, score_trace
from rhodyn.schema import CouplingIntervalRecord, EndpointRecord, ReserveRecord, TrajectoryRecord
from rhodyn.sensitivity import residence_window_grid, score_trace_window_sensitivity
from rhodyn.sim import first_passage_time
from rhodyn.uncertainty import bootstrap_interval

DEFAULT_OUTPUT_DIR = Path("case_studies/stage7_synthetic_truth")
PRIMARY_WINDOW = ResidenceWindow(0.35, 0.75)


def residence_truth_cases() -> dict[str, list[TrajectoryRecord]]:
    """Return trajectory cases with known residence/amplitude behavior."""

    return {
        "positive_residence": [
            TrajectoryRecord("pos_a", 0, "positive_residence", 0.20, "r1"),
            TrajectoryRecord("pos_a", 1, "positive_residence", 0.45, "r1"),
            TrajectoryRecord("pos_a", 2, "positive_residence", 0.55, "r1"),
            TrajectoryRecord("pos_a", 3, "positive_residence", 0.65, "r1"),
            TrajectoryRecord("pos_a", 4, "positive_residence", 0.90, "r1"),
        ],
        "counterexample_amplitude_only": [
            TrajectoryRecord("neg_a", 0, "counterexample_amplitude_only", 0.15, "r1"),
            TrajectoryRecord("neg_a", 1, "counterexample_amplitude_only", 0.95, "r1"),
            TrajectoryRecord("neg_a", 2, "counterexample_amplitude_only", 0.15, "r1"),
            TrajectoryRecord("neg_a", 3, "counterexample_amplitude_only", 0.95, "r1"),
            TrajectoryRecord("neg_a", 4, "counterexample_amplitude_only", 0.15, "r1"),
        ],
        "ambiguous_window_edge": [
            TrajectoryRecord("amb_a", 0, "ambiguous_window_edge", 0.32, "r1"),
            TrajectoryRecord("amb_a", 1, "ambiguous_window_edge", 0.35, "r1"),
            TrajectoryRecord("amb_a", 2, "ambiguous_window_edge", 0.75, "r1"),
            TrajectoryRecord("amb_a", 3, "ambiguous_window_edge", 0.78, "r1"),
            TrajectoryRecord("amb_a", 4, "ambiguous_window_edge", 0.74, "r1"),
        ],
    }


def reserve_truth_cases() -> dict[str, list[ReserveRecord]]:
    """Return reserve-like cases with known high and low buffering behavior."""

    return {
        "positive_buffered": [
            ReserveRecord("buf_a", 0, "positive_buffered", 1.0, "r1"),
            ReserveRecord("buf_a", 1, "positive_buffered", 1.05, "r1"),
            ReserveRecord("buf_a", 2, "positive_buffered", 1.10, "r1"),
        ],
        "counterexample_fragile": [
            ReserveRecord("frag_a", 0, "counterexample_fragile", 1.0, "r1"),
            ReserveRecord("frag_a", 1, "counterexample_fragile", 1.55, "r1"),
            ReserveRecord("frag_a", 2, "counterexample_fragile", 1.90, "r1"),
        ],
        "ambiguous_midreserve": [
            ReserveRecord("mid_a", 0, "ambiguous_midreserve", 1.0, "r1"),
            ReserveRecord("mid_a", 1, "ambiguous_midreserve", 1.35, "r1"),
            ReserveRecord("mid_a", 2, "ambiguous_midreserve", 1.50, "r1"),
        ],
    }


def coupling_truth_cases() -> dict[str, CouplingIntervalRecord]:
    """Return interval cases with known bounded-coupling outcomes."""

    return {
        "positive_equivalent": CouplingIntervalRecord("positive_equivalent", 0.01, -0.04, 0.05, 0.10, 0.99),
        "counterexample_shift": CouplingIntervalRecord("counterexample_shift", 0.16, 0.11, 0.22, 0.10, 0.40),
        "ambiguous_margin_crossing": CouplingIntervalRecord("ambiguous_margin_crossing", 0.02, -0.12, 0.08, 0.10, 0.92),
    }


def model_truth_cases() -> dict[str, list[EndpointRecord]]:
    """Return endpoint model-comparison cases with known model rankings."""

    return {
        "positive_routed_best": [
            EndpointRecord("routed", "morphology", 0.20, 0.20),
            EndpointRecord("routed", "inflammatory", 0.80, 0.78),
            EndpointRecord("routed", "reserve", 0.70, 0.69),
            EndpointRecord("endpoint_only", "morphology", 0.20, 0.45),
            EndpointRecord("endpoint_only", "inflammatory", 0.80, 0.45),
            EndpointRecord("endpoint_only", "reserve", 0.70, 0.45),
        ],
        "counterexample_endpoint_sufficient": [
            EndpointRecord("routed", "morphology", 0.50, 0.50),
            EndpointRecord("routed", "inflammatory", 0.50, 0.51),
            EndpointRecord("routed", "reserve", 0.50, 0.49),
            EndpointRecord("endpoint_only", "morphology", 0.50, 0.50),
            EndpointRecord("endpoint_only", "inflammatory", 0.50, 0.50),
            EndpointRecord("endpoint_only", "reserve", 0.50, 0.50),
        ],
        "ambiguous_close_fit": [
            EndpointRecord("routed", "morphology", 0.40, 0.39),
            EndpointRecord("routed", "inflammatory", 0.60, 0.61),
            EndpointRecord("routed", "reserve", 0.50, 0.49),
            EndpointRecord("endpoint_only", "morphology", 0.40, 0.42),
            EndpointRecord("endpoint_only", "inflammatory", 0.60, 0.58),
            EndpointRecord("endpoint_only", "reserve", 0.50, 0.52),
        ],
    }


def uncertainty_truth_cases() -> dict[str, list[float]]:
    """Return compact uncertainty cases for narrow and broad intervals."""

    return {
        "positive_stable": [0.48, 0.50, 0.51, 0.49, 0.52, 0.50, 0.51, 0.49],
        "counterexample_shifted": [0.20, 0.22, 0.25, 0.24, 0.23, 0.21, 0.24, 0.22],
        "ambiguous_broad": [0.10, 0.90, 0.20, 0.80, 0.30, 0.70, 0.40, 0.60],
    }


def _write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def _trajectory_row(record: TrajectoryRecord) -> dict[str, object]:
    return asdict(record)


def _reserve_row(record: ReserveRecord) -> dict[str, object]:
    return asdict(record)


def _endpoint_row(record: EndpointRecord) -> dict[str, object]:
    return asdict(record)


def _coupling_row(record: CouplingIntervalRecord) -> dict[str, object]:
    return asdict(record)


def evaluate_truth_cases() -> dict[str, object]:
    """Evaluate all Stage 7.1 truth cases through existing RhoDyn APIs."""

    residence_cases = residence_truth_cases()
    residence = {}
    for name, records in residence_cases.items():
        summary = score_trace(records, PRIMARY_WINDOW)
        windows = residence_window_grid(low_min=0.30, low_max=0.40, high_min=0.70, high_max=0.80, steps=3)
        sensitivity = score_trace_window_sensitivity(records, windows, min_residence_fraction=0.45)
        residence[name] = {
            "residence_fraction": summary.residence_fraction,
            "residence_time": summary.residence_time,
            "segment_count": len(summary.segments),
            "mean_signal": summary.mean_signal,
            "max_signal": summary.max_signal,
            "qualifying_window_count": sensitivity.qualifying_window_count,
            "window_count": len(sensitivity.points),
        }

    reserve = {}
    for name, records in reserve_truth_cases().items():
        values = [record.response for record in records]
        normalized = ff_over_f0(values, baseline_points=1)
        reserve[name] = {
            "ff_over_f0_peak": max(normalized),
            "reserve_coordinate": reserve_coordinate(normalized, floor=1.0, ceiling=2.0),
        }

    coupling = {}
    for name, record in coupling_truth_cases().items():
        decision = equivalence_from_interval(
            record.estimate,
            record.ci_low,
            record.ci_high,
            record.margin,
            rope_mass=record.rope_mass,
        )
        coupling[name] = {
            "estimate": decision.estimate,
            "ci_low": decision.ci_low,
            "ci_high": decision.ci_high,
            "margin": decision.margin,
            "rope_mass": decision.rope_mass,
            "passes": decision.passes,
            "interval_inside_margin": decision.interval_inside_margin,
        }

    models = {}
    for name, rows in model_truth_cases().items():
        fits = rank_model_fits(rows)
        models[name] = {
            "best_model": fits[0].model,
            "fits": [asdict(fit) for fit in fits],
        }

    uncertainty = {}
    for name, values in uncertainty_truth_cases().items():
        interval = bootstrap_interval(values, n_resamples=200, seed=7, confidence_level=0.90).interval
        uncertainty[name] = {
            "estimate": interval.estimate,
            "lower": interval.lower,
            "upper": interval.upper,
            "width": interval.upper - interval.lower,
        }

    timing = {
        "positive_crossing": first_passage_time([0, 1, 2, 3], [0.1, 0.2, 0.8, 0.9], 0.75),
        "counterexample_no_crossing": first_passage_time([0, 1, 2, 3], [0.1, 0.2, 0.3, 0.4], 0.75),
        "ambiguous_late_crossing": first_passage_time([0, 1, 2, 3], [0.1, 0.2, 0.4, 0.76], 0.75),
    }

    expectations = {
        "residence_positive_passes": residence["positive_residence"]["residence_fraction"] > 0.50,
        "residence_counterexample_low_residence_despite_high_peak": residence["counterexample_amplitude_only"]["residence_fraction"] < 0.30
        and residence["counterexample_amplitude_only"]["max_signal"] > 0.90,
        "residence_ambiguous_window_dependent": 0
        < residence["ambiguous_window_edge"]["qualifying_window_count"]
        < residence["ambiguous_window_edge"]["window_count"],
        "reserve_buffered_high": reserve["positive_buffered"]["reserve_coordinate"] > 0.85,
        "reserve_fragile_low": reserve["counterexample_fragile"]["reserve_coordinate"] < 0.20,
        "coupling_equivalence_passes_only_positive": coupling["positive_equivalent"]["passes"]
        and not coupling["counterexample_shift"]["passes"]
        and not coupling["ambiguous_margin_crossing"]["passes"],
        "model_positive_routed_best": models["positive_routed_best"]["best_model"] == "routed",
        "model_counterexample_endpoint_best": models["counterexample_endpoint_sufficient"]["best_model"] == "endpoint_only",
        "uncertainty_ambiguous_broader_than_stable": uncertainty["ambiguous_broad"]["width"] > uncertainty["positive_stable"]["width"],
        "timing_positive_and_ambiguous_cross_but_counterexample_not": timing["positive_crossing"] is not None
        and timing["counterexample_no_crossing"] is None
        and timing["ambiguous_late_crossing"] is not None,
    }

    return {
        "report_format": "rhodyn.stage7_1_synthetic_truth.v1",
        "primary_window": {"low": PRIMARY_WINDOW.low, "high": PRIMARY_WINDOW.high},
        "residence": residence,
        "reserve": reserve,
        "coupling": coupling,
        "model_comparison": models,
        "uncertainty": uncertainty,
        "timing": timing,
        "expectations": expectations,
        "status": "pass" if all(expectations.values()) else "fail",
    }


def write_truth_cases(output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, object]:
    """Write Stage 7.1 truth-case tables and report."""

    output_dir.mkdir(parents=True, exist_ok=True)
    for name, records in residence_truth_cases().items():
        _write_csv(
            output_dir / f"trajectory_{name}.csv",
            [_trajectory_row(record) for record in records],
            ["cell_id", "time", "condition", "signal", "replicate"],
        )
    for name, records in reserve_truth_cases().items():
        _write_csv(
            output_dir / f"reserve_{name}.csv",
            [_reserve_row(record) for record in records],
            ["sample_id", "time", "condition", "response", "replicate"],
        )
    _write_csv(
        output_dir / "coupling_interval_cases.csv",
        [_coupling_row(record) for record in coupling_truth_cases().values()],
        ["contrast", "estimate", "ci_low", "ci_high", "margin", "rope_mass"],
    )
    for name, rows in model_truth_cases().items():
        _write_csv(
            output_dir / f"endpoint_{name}.csv",
            [_endpoint_row(row) for row in rows],
            ["model", "endpoint", "observed", "predicted", "weight"],
        )
    uncertainty_rows = []
    for name, values in uncertainty_truth_cases().items():
        for i, value in enumerate(values):
            uncertainty_rows.append({"case": name, "unit_id": f"{name}_{i}", "value": value})
    _write_csv(output_dir / "uncertainty_cases.csv", uncertainty_rows, ["case", "unit_id", "value"])

    report = evaluate_truth_cases()
    (output_dir / "stage7_1_synthetic_truth_report.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args()
    report = write_truth_cases(args.output_dir)
    print(json.dumps({"status": report["status"], "output_dir": args.output_dir.as_posix()}, indent=2))
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())

"""Generate Stage 10.1 method-object v2 fixtures and gate report.

This runner turns the Stage 10.1 mathematical-method plan into executable
positive, counterexample, and ambiguous fixtures. The outputs are method
validation fixtures, not biological evidence.
"""

from __future__ import annotations

import csv
import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from rhodyn.compare import rank_model_fits
from rhodyn.coupling import equivalence_from_interval
from rhodyn.method_object import (
    MethodObjectDecision,
    MethodObjectSpec,
    coupling_method_decision,
    decision_to_row,
    reserve_method_decision,
    routed_output_method_decision,
    trajectory_method_decision,
)
from rhodyn.reserve import ff_over_f0, reserve_coordinate
from rhodyn.residence import ResidenceWindow
from rhodyn.schema import TrajectoryRecord


OUTPUT_DIR = ROOT / "case_studies" / "stage10_method_object_v2"
DOC_API_GAP_PATH = ROOT / "docs" / "stage10_1_api_gap_list.md"
PRIMARY_WINDOW = ResidenceWindow(0.35, 0.75)
SPEC = MethodObjectSpec()


def _stage7_truth_module():
    script = ROOT / "scripts" / "build_stage7_1_synthetic_truth_cases.py"
    spec = importlib.util.spec_from_file_location("stage7_truth", script)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def trajectory_v2_cases() -> dict[str, tuple[list[TrajectoryRecord], float]]:
    """Return trajectory cases for the decision-divergence method object."""

    return {
        "trajectory_residence_added": (
            [
                TrajectoryRecord("res_a", 0, "trajectory_residence_added", 0.42, "r1"),
                TrajectoryRecord("res_a", 1, "trajectory_residence_added", 0.55, "r1"),
                TrajectoryRecord("res_a", 2, "trajectory_residence_added", 0.62, "r1"),
                TrajectoryRecord("res_a", 3, "trajectory_residence_added", 0.58, "r1"),
                TrajectoryRecord("res_a", 4, "trajectory_residence_added", 0.48, "r1"),
            ],
            0.05,
        ),
        "trajectory_amplitude_sufficient": (
            [
                TrajectoryRecord("amp_a", 0, "trajectory_amplitude_sufficient", 0.10, "r1"),
                TrajectoryRecord("amp_a", 1, "trajectory_amplitude_sufficient", 0.96, "r1"),
                TrajectoryRecord("amp_a", 2, "trajectory_amplitude_sufficient", 0.12, "r1"),
                TrajectoryRecord("amp_a", 3, "trajectory_amplitude_sufficient", 0.94, "r1"),
                TrajectoryRecord("amp_a", 4, "trajectory_amplitude_sufficient", 0.10, "r1"),
            ],
            0.05,
        ),
        "trajectory_ambiguous_uncertainty": (
            [
                TrajectoryRecord("amb_a", 0, "trajectory_ambiguous_uncertainty", 0.36, "r1"),
                TrajectoryRecord("amb_a", 1, "trajectory_ambiguous_uncertainty", 0.74, "r1"),
                TrajectoryRecord("amb_a", 2, "trajectory_ambiguous_uncertainty", 0.34, "r1"),
                TrajectoryRecord("amb_a", 3, "trajectory_ambiguous_uncertainty", 0.76, "r1"),
                TrajectoryRecord("amb_a", 4, "trajectory_ambiguous_uncertainty", 0.50, "r1"),
            ],
            0.40,
        ),
    }


def evaluate_stage10_1() -> dict[str, object]:
    """Evaluate the Stage 10.1 method-object fixtures."""

    stage7_truth = _stage7_truth_module()
    decisions: list[MethodObjectDecision] = []

    for case_id, (records, uncertainty_width) in trajectory_v2_cases().items():
        decisions.append(
            trajectory_method_decision(
                case_id,
                records,
                PRIMARY_WINDOW,
                spec=SPEC,
                comparator="peak",
                uncertainty_width=uncertainty_width,
            )
        )

    for case_id, record in stage7_truth.coupling_truth_cases().items():
        interval = equivalence_from_interval(
            record.estimate,
            record.ci_low,
            record.ci_high,
            record.margin,
            rope_mass=record.rope_mass,
            rope_threshold=SPEC.rope_threshold,
        )
        decisions.append(coupling_method_decision(f"coupling_{case_id}", interval, spec=SPEC))

    for case_id, records in stage7_truth.reserve_truth_cases().items():
        normalized = ff_over_f0([record.response for record in records], baseline_points=1)
        reserve_value = reserve_coordinate(normalized, floor=1.0, ceiling=2.0)
        decisions.append(reserve_method_decision(f"reserve_{case_id}", reserve_value, spec=SPEC))

    for case_id, rows in stage7_truth.model_truth_cases().items():
        fits = rank_model_fits(rows)
        decisions.append(routed_output_method_decision(f"model_{case_id}", fits, spec=SPEC))

    calls_by_component: dict[str, set[str]] = {}
    for decision in decisions:
        calls_by_component.setdefault(decision.component, set()).add(decision.call)

    expectations = {
        "trajectory_has_positive_counterexample_and_ambiguous": {
            "residence_added_information",
            "baseline_or_amplitude_sufficient",
            "inconclusive",
        }.issubset(calls_by_component.get("trajectory_residence_vs_comparator", set())),
        "coupling_has_pass_shift_and_ambiguous": {
            "bounded_coupling_within_margin",
            "coupling_shift_exceeds_margin",
            "inconclusive",
        }.issubset(calls_by_component.get("bounded_coupling", set())),
        "reserve_has_buffered_fragile_and_ambiguous": {
            "reserve_like_buffered",
            "reserve_like_fragile",
            "inconclusive",
        }.issubset(calls_by_component.get("reserve_like_endpoint", set())),
        "model_has_routed_reduced_and_ambiguous": {
            "routed_architecture_selected",
            "reduced_architecture_selected",
            "inconclusive",
        }.issubset(calls_by_component.get("routed_output_model_comparison", set())),
        "all_decisions_have_interpretation_boundaries": all(
            bool(decision.interpretation_boundary) for decision in decisions
        ),
    }

    api_gaps = [
        {
            "object": "native paired-reporter tidy schema",
            "status": "non_blocking_extension",
            "reason": (
                "Stage 10.1 can represent paired-reporter evidence through declared "
                "bounded-coupling contrasts. A native paired-reporter table would make "
                "Stage 10.2 named benchmarks cleaner but is not required to express the "
                "method object."
            ),
        }
    ]

    return {
        "report_format": "rhodyn.stage10_1_method_object_v2.v1",
        "primary_window": {"low": PRIMARY_WINDOW.low, "high": PRIMARY_WINDOW.high},
        "spec": {
            "residence_fraction_min": SPEC.residence_fraction_min,
            "amplitude_high_min": SPEC.amplitude_high_min,
            "uncertainty_width_max": SPEC.uncertainty_width_max,
            "reserve_high_min": SPEC.reserve_high_min,
            "reserve_low_max": SPEC.reserve_low_max,
            "bic_delta_min": SPEC.bic_delta_min,
            "rope_threshold": SPEC.rope_threshold,
        },
        "decision_count": len(decisions),
        "decisions": [decision_to_row(decision) for decision in decisions],
        "expectations": expectations,
        "api_gaps": api_gaps,
        "status": "pass" if all(expectations.values()) else "fail",
    }


def _write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def _write_api_gap_list(path: Path, report: dict[str, object]) -> None:
    gaps = report["api_gaps"]
    lines = [
        "# Stage 10.1 API gap list",
        "",
        "The Stage 10.1 method object is expressible with the current public API plus the additive `rhodyn.method_object` helpers.",
        "",
        "| object | status | reason |",
        "| --- | --- | --- |",
    ]
    for gap in gaps:  # type: ignore[assignment]
        lines.append(f"| {gap['object']} | {gap['status']} | {gap['reason']} |")
    lines.extend(
        [
            "",
            "No blocking API gap was found for Stage 10.1. The native paired-reporter schema remains a useful Stage 10.2 extension for broader named benchmarking, not a blocker for the current method-object formalization.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_brief(path: Path, report: dict[str, object]) -> None:
    lines = [
        "# Stage 10.1 method-object v2 fixture brief",
        "",
        "Stage 10.1 converts RhoDyn from a collection of compatible analysis components into an explicit decision object. The object reports when a declared residence window changes interpretation relative to a declared comparator, when bounded coupling is supported only within a margin, when reserve-like endpoints are buffered or fragile under their own measurement scale, and when routed-output alternatives are selected or withheld.",
        "",
        f"Status. `{report['status']}`.",
        f"Decision rows. `{report['decision_count']}`.",
        "",
        "## Component calls",
        "",
        "| component | required decision types represented |",
        "| --- | --- |",
        "| Trajectory residence versus comparator | residence-added, amplitude-sufficient, inconclusive |",
        "| Bounded coupling | inside margin, exceeds margin, inconclusive |",
        "| Reserve-like endpoint | buffered, fragile, inconclusive |",
        "| Routed-output comparison | routed selected, reduced selected, inconclusive |",
        "",
        "## Biological interpretation boundary",
        "",
        "These fixtures demonstrate method behavior, not new biology. Decision divergence is a reporting object for comparing residence and baseline interpretations under declared rules. It is not a molecular mechanism, and it does not imply that every live-cell reporter contains a residence regime.",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_stage10_1_outputs(output_dir: Path = OUTPUT_DIR) -> dict[str, object]:
    """Write Stage 10.1 fixtures, reports, and API gap list."""

    report = evaluate_stage10_1()
    output_dir.mkdir(parents=True, exist_ok=True)
    _write_csv(output_dir / "stage10_1_method_object_decisions.csv", report["decisions"])  # type: ignore[arg-type]
    (output_dir / "stage10_1_method_object_gate_report.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    _write_brief(output_dir / "stage10_1_method_object_brief.md", report)
    _write_api_gap_list(DOC_API_GAP_PATH, report)
    return report


def main() -> int:
    report = write_stage10_1_outputs()
    print(json.dumps({"status": report["status"], "decision_count": report["decision_count"]}, indent=2))
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())

"""Notebook-style synthetic RhoDyn workflow.

Run from the repository root with:

    PYTHONPATH=src python examples/residence_reserve_workflow.py

The example uses synthetic tables only. It teaches the RhoDyn analysis pattern
without using manuscript data or reproducing manuscript figures.
"""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path

from rhodyn.compare import rank_model_fits
from rhodyn.coupling import equivalence_from_interval
from rhodyn.reserve import ff_over_f0, reserve_coordinate
from rhodyn.residence import ResidenceWindow, score_records
from rhodyn.schema import read_coupling_csv, read_endpoint_csv, read_reserve_csv, read_trajectory_csv


EXAMPLE_ROOT = Path(__file__).resolve().parent


def _fail_if_issues(label: str, issues: object) -> None:
    if issues:
        raise SystemExit(f"{label} failed validation: {issues}")


def residence_section() -> None:
    rows, issues = read_trajectory_csv(EXAMPLE_ROOT / "synthetic_trajectory.csv")
    _fail_if_issues("trajectory table", issues)
    summaries = score_records(rows, ResidenceWindow(low=0.35, high=0.75))
    print("Residence workflow")
    for summary in summaries:
        print(
            f"- {summary.condition}/{summary.cell_id}: "
            f"residence_fraction={summary.residence_fraction:.2f}, "
            f"mean_signal={summary.mean_signal:.2f}, segments={len(summary.segments)}"
        )
    print("Interpretation: residence and mean amplitude can separate even in a small synthetic trace set.")


def reserve_section() -> None:
    rows, issues = read_reserve_csv(EXAMPLE_ROOT / "synthetic_reserve.csv")
    _fail_if_issues("reserve table", issues)
    grouped: dict[str, list[float]] = defaultdict(list)
    conditions: dict[str, str] = {}
    for row in rows:
        grouped[row.sample_id].append(row.response)
        conditions[row.sample_id] = row.condition
    print("\nReserve workflow")
    for sample_id, values in sorted(grouped.items()):
        normalized = ff_over_f0(values, baseline_points=1)
        reserve = reserve_coordinate(normalized, floor=1.0, ceiling=1.8)
        print(f"- {conditions[sample_id]}/{sample_id}: peak_FF0={max(normalized):.2f}, reserve={reserve:.2f}")
    print("Interpretation: larger stimulated response maps to lower remaining reserve in this toy coordinate.")


def coupling_section() -> None:
    rows, issues = read_coupling_csv(EXAMPLE_ROOT / "synthetic_coupling.csv")
    _fail_if_issues("coupling table", issues)
    print("\nBounded-coupling workflow")
    for row in rows:
        decision = equivalence_from_interval(
            estimate=row.estimate,
            ci_low=row.ci_low,
            ci_high=row.ci_high,
            margin=row.margin,
            rope_mass=row.rope_mass,
        )
        status = "passes" if decision.passes else "does not pass"
        print(f"- {row.contrast}: {status} the declared margin and ROPE rule")
    print("Interpretation: a bounded-coupling result depends on the declared margin and posterior support.")


def model_section() -> None:
    rows, issues = read_endpoint_csv(EXAMPLE_ROOT / "synthetic_endpoints.csv")
    _fail_if_issues("endpoint table", issues)
    fits = rank_model_fits(rows)
    print("\nReduced-model workflow")
    for fit in fits:
        print(f"- {fit.model}: rmse={fit.rmse:.3f}, bic={fit.bic:.2f}")
    print(
        "Interpretation: model ranking compares endpoint compatibility from model-derived summaries, "
        "not literal molecular edges."
    )


def main() -> int:
    residence_section()
    reserve_section()
    coupling_section()
    model_section()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

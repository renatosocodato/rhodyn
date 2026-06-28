"""Command-line interface for RhoDyn."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from rhodyn.compare import rank_model_fits
from rhodyn.coupling import equivalence_from_interval
from rhodyn.ctc import (
    CTC_LINEAGE_SIGNAL_CHOICES,
    CTC_SIGNAL_CHOICES,
    ctc_features_to_trajectory_records,
    ctc_lineage_coverage_issues,
    ctc_lineage_to_trajectory_records,
    read_ctc_feature_csv,
    read_ctc_lineage,
    write_trajectory_csv,
)
from rhodyn.extras import extra_plan
from rhodyn.models import simulate_controller
from rhodyn.paper import inspect_case_study_root, paper_case_study_metadata
from rhodyn.report import markdown_summary, to_plain
from rhodyn.reserve import ff_over_f0, reserve_coordinate
from rhodyn.residence import ResidenceWindow, score_records
from rhodyn.results import (
    GroupMetadata,
    ReserveResult,
    ResultProvenance,
    coupling_result_from_decision,
    model_comparison_result_from_fits,
    residence_result_from_summary,
)
from rhodyn.schema import read_coupling_csv, read_endpoint_csv, read_reserve_csv, read_trajectory_csv, schema_specs
from rhodyn.sensitivity import residence_window_grid, score_records_window_sensitivity


def _print_json(payload: object) -> None:
    print(json.dumps(to_plain(payload), indent=2))


def _read_dict_csv(path: str | Path) -> tuple[list[dict[str, str]], list[dict[str, object]]]:
    issues: list[dict[str, object]] = []
    with Path(path).open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames:
            return [], [{"row": 0, "field": "header", "message": "CSV must include a header row"}]
        rows = [dict(row) for row in reader]
    return rows, issues


def cmd_validate(args: argparse.Namespace) -> int:
    if args.kind == "trajectory":
        rows, issues = read_trajectory_csv(args.csv, signal_column=args.signal_column)
    elif args.kind == "endpoint":
        rows, issues = read_endpoint_csv(args.csv)
    elif args.kind == "reserve":
        rows, issues = read_reserve_csv(args.csv)
    else:
        rows, issues = read_coupling_csv(args.csv)
    _print_json(
        {
            "status": "pass" if not issues else "fail",
            "kind": args.kind,
            "schema": schema_specs()[args.kind],
            "rows": len(rows),
            "issues": issues,
        }
    )
    return 0 if not issues else 1


def cmd_score_residence(args: argparse.Namespace) -> int:
    rows, issues = read_trajectory_csv(args.csv, signal_column=args.signal_column)
    if issues:
        _print_json({"status": "fail", "issues": issues})
        return 1
    window = ResidenceWindow(low=args.low, high=args.high)
    summaries = score_records(rows, window)
    typed = [
        residence_result_from_summary(
            summary,
            parameters={"low": args.low, "high": args.high, "signal_column": args.signal_column},
            source=str(args.csv),
        )
        for summary in summaries
    ]
    _print_json(
        {
            "status": "pass",
            "window": {"low": args.low, "high": args.high},
            "summaries": summaries,
            "typed_results": typed,
        }
    )
    return 0


def cmd_decide_coupling(args: argparse.Namespace) -> int:
    rows, issues = read_coupling_csv(args.csv)
    if issues:
        _print_json({"status": "fail", "issues": issues})
        return 1
    parameters = {"rope_threshold": args.rope_threshold}
    decisions = [
        equivalence_from_interval(
            row.estimate,
            row.ci_low,
            row.ci_high,
            row.margin,
            rope_mass=row.rope_mass,
            rope_threshold=args.rope_threshold,
        )
        for row in rows
    ]
    typed = [
        coupling_result_from_decision(
            row.contrast,
            decision,
            parameters=parameters,
            source=str(args.csv),
        )
        for row, decision in zip(rows, decisions)
    ]
    _print_json({"status": "pass", "records": rows, "decisions": decisions, "typed_results": typed})
    return 0


def cmd_summarize_reserve(args: argparse.Namespace) -> int:
    rows, issues = read_reserve_csv(args.csv)
    if issues:
        _print_json({"status": "fail", "issues": issues})
        return 1
    parameters = {
        "floor": args.floor,
        "ceiling": args.ceiling,
        "baseline_points": args.baseline_points,
        "normalize": args.normalize,
    }
    grouped: dict[tuple[str, str], list[object]] = {}
    for row in rows:
        grouped.setdefault((row.condition, row.sample_id), []).append(row)
    summaries: list[dict[str, object]] = []
    typed: list[ReserveResult] = []
    for (condition, sample_id), sample_rows in sorted(grouped.items()):
        ordered = sorted(sample_rows, key=lambda item: item.time)  # type: ignore[attr-defined]
        values = [row.response for row in ordered]  # type: ignore[attr-defined]
        normalized = ff_over_f0(values, baseline_points=args.baseline_points) if args.normalize else values
        reserve = reserve_coordinate(normalized, floor=args.floor, ceiling=args.ceiling)
        peak_response = max(normalized)
        replicate = ordered[0].replicate  # type: ignore[attr-defined]
        summaries.append(
            {
                "condition": condition,
                "sample_id": sample_id,
                "replicate": replicate,
                "n_points": len(ordered),
                "peak_response": peak_response,
                "reserve": reserve,
            }
        )
        typed.append(
            ReserveResult(
                group=GroupMetadata(condition=condition, sample_id=sample_id, replicate=replicate),
                reserve=reserve,
                peak_response=peak_response,
                n_points=len(ordered),
                provenance=ResultProvenance(schema_kind="reserve", parameters=parameters, source=str(args.csv)),
            )
        )
    _print_json({"status": "pass", "summaries": summaries, "typed_results": typed})
    return 0


def cmd_export_markdown(args: argparse.Namespace) -> int:
    rows, issues = _read_dict_csv(args.csv)
    if issues:
        _print_json({"status": "fail", "issues": issues})
        return 1
    _print_json({"status": "pass", "markdown": markdown_summary(args.title, rows)})
    return 0


def cmd_simulate(args: argparse.Namespace) -> int:
    rows = simulate_controller(duration=args.duration, dt=args.dt)
    _print_json({"status": "pass", "rows": rows})
    return 0


def cmd_compare(args: argparse.Namespace) -> int:
    rows, issues = read_endpoint_csv(args.csv)
    if issues:
        _print_json({"status": "fail", "issues": issues})
        return 1
    fits = rank_model_fits(rows, parameter_count=args.parameters)
    typed = model_comparison_result_from_fits(
        fits,
        parameters={"parameter_count": args.parameters},
        source=str(args.csv),
    )
    _print_json({"status": "pass", "fits": fits, "typed_result": typed})
    return 0


def cmd_sensitivity(args: argparse.Namespace) -> int:
    rows, issues = read_trajectory_csv(args.csv, signal_column=args.signal_column)
    if issues:
        _print_json({"status": "fail", "issues": issues})
        return 1
    windows = residence_window_grid(
        low_min=args.low_min,
        low_max=args.low_max,
        high_min=args.high_min,
        high_max=args.high_max,
        steps=args.steps,
    )
    parameters = {
        "low_min": args.low_min,
        "low_max": args.low_max,
        "high_min": args.high_min,
        "high_max": args.high_max,
        "steps": args.steps,
        "signal_column": args.signal_column,
    }
    curves = score_records_window_sensitivity(
        rows,
        windows,
        min_residence_fraction=args.min_residence_fraction,
        parameters=parameters,
    )
    _print_json(
        {
            "status": "pass",
            "window_count": len(windows),
            "min_residence_fraction": args.min_residence_fraction,
            "curves": curves,
        }
    )
    return 0


def cmd_ctc_to_trajectory(args: argparse.Namespace) -> int:
    features, issues = read_ctc_feature_csv(args.features_csv)
    lineage_rows = []
    if args.lineage:
        lineage_rows, lineage_issues = read_ctc_lineage(args.lineage)
        issues.extend(lineage_issues)
        if not lineage_issues:
            issues.extend(ctc_lineage_coverage_issues(features, lineage_rows))
    if issues:
        _print_json({"status": "fail", "issues": issues})
        return 1

    records = ctc_features_to_trajectory_records(
        features,
        signal=args.signal,
        condition=args.condition,
        replicate=args.replicate,
    )
    if args.output:
        write_trajectory_csv(records, args.output)
    _print_json(
        {
            "status": "pass",
            "input_rows": len(features),
            "lineage_rows": len(lineage_rows),
            "trajectory_rows": len(records),
            "signal": args.signal,
            "condition": args.condition,
            "replicate": args.replicate,
            "output": args.output,
            "rows": [] if args.output else records,
        }
    )
    return 0


def cmd_ctc_lineage_to_trajectory(args: argparse.Namespace) -> int:
    lineage_rows, issues = read_ctc_lineage(args.lineage)
    if issues:
        _print_json({"status": "fail", "issues": issues})
        return 1
    records = ctc_lineage_to_trajectory_records(
        lineage_rows,
        signal=args.signal,
        condition=args.condition,
        replicate=args.replicate,
        max_tracks=args.max_tracks,
    )
    if args.output:
        write_trajectory_csv(records, args.output)
    _print_json(
        {
            "status": "pass",
            "lineage_rows": len(lineage_rows),
            "trajectory_rows": len(records),
            "signal": args.signal,
            "condition": args.condition,
            "replicate": args.replicate,
            "max_tracks": args.max_tracks,
            "output": args.output,
            "rows": [] if args.output else records,
        }
    )
    return 0


def cmd_paper_case_study(args: argparse.Namespace) -> int:
    payload = paper_case_study_metadata()
    if args.data_root:
        payload["local_data_root"] = inspect_case_study_root(args.data_root)
    _print_json(payload)
    return 0


def cmd_extras(args: argparse.Namespace) -> int:
    _print_json({"status": "pass", "extras": extra_plan()})
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="rhodyn", description="Dynamic residence-state analysis toolkit.")
    sub = parser.add_subparsers(dest="command", required=True)

    validate = sub.add_parser("validate", help="Validate a tidy input CSV.")
    validate.add_argument("csv")
    validate.add_argument("--kind", choices=["trajectory", "endpoint", "reserve", "coupling"], default="trajectory")
    validate.add_argument("--signal-column", default="signal")
    validate.set_defaults(func=cmd_validate)

    score = sub.add_parser("score-residence", help="Score residence-window summaries for a trajectory table.")
    score.add_argument("csv")
    score.add_argument("--low", type=float, required=True)
    score.add_argument("--high", type=float, required=True)
    score.add_argument("--signal-column", default="signal")
    score.set_defaults(func=cmd_score_residence)

    coupling = sub.add_parser("decide-coupling", help="Classify bounded-coupling interval rows.")
    coupling.add_argument("csv")
    coupling.add_argument("--rope-threshold", type=float, default=0.95)
    coupling.set_defaults(func=cmd_decide_coupling)

    reserve = sub.add_parser("summarize-reserve", help="Summarize reserve-like response rows.")
    reserve.add_argument("csv")
    reserve.add_argument("--floor", type=float, required=True)
    reserve.add_argument("--ceiling", type=float, required=True)
    reserve.add_argument("--baseline-points", type=int, default=3)
    reserve.add_argument("--normalize", action=argparse.BooleanOptionalAction, default=True)
    reserve.set_defaults(func=cmd_summarize_reserve)

    report = sub.add_parser("export-markdown", help="Export a compact Markdown summary for a CSV table.")
    report.add_argument("csv")
    report.add_argument("--title", default="RhoDyn report")
    report.set_defaults(func=cmd_export_markdown)

    sim = sub.add_parser("simulate", help="Run a minimal controller simulation.")
    sim.add_argument("--duration", type=float, default=20.0)
    sim.add_argument("--dt", type=float, default=0.5)
    sim.set_defaults(func=cmd_simulate)

    compare = sub.add_parser("compare", help="Rank reduced-model endpoint fits.")
    compare.add_argument("csv")
    compare.add_argument("--parameters", type=int, default=1)
    compare.set_defaults(func=cmd_compare)

    sensitivity = sub.add_parser("sensitivity", help="Score residence summaries across a low/high window grid.")
    sensitivity.add_argument("csv")
    sensitivity.add_argument("--low-min", type=float, required=True)
    sensitivity.add_argument("--low-max", type=float, required=True)
    sensitivity.add_argument("--high-min", type=float, required=True)
    sensitivity.add_argument("--high-max", type=float, required=True)
    sensitivity.add_argument("--steps", type=int, default=5)
    sensitivity.add_argument("--min-residence-fraction", type=float, default=0.0)
    sensitivity.add_argument("--signal-column", default="signal")
    sensitivity.set_defaults(func=cmd_sensitivity)

    ctc = sub.add_parser("ctc-to-trajectory", help="Convert CTC-style track features into trajectory CSV.")
    ctc.add_argument("features_csv")
    ctc.add_argument("--lineage", default="", help="Optional CTC man_track.txt file for interval validation.")
    ctc.add_argument("--signal", choices=CTC_SIGNAL_CHOICES, default="speed")
    ctc.add_argument("--condition", default="mlci_tracking")
    ctc.add_argument("--replicate", default="")
    ctc.add_argument("--output", default="", help="Optional output CSV path. If omitted, rows are printed as JSON.")
    ctc.set_defaults(func=cmd_ctc_to_trajectory)

    lineage = sub.add_parser(
        "ctc-lineage-to-trajectory",
        help="Convert a CTC man_track.txt lineage table into trajectory CSV.",
    )
    lineage.add_argument("lineage")
    lineage.add_argument("--signal", choices=CTC_LINEAGE_SIGNAL_CHOICES, default="normalized_track_age")
    lineage.add_argument("--condition", default="mlci_tracking")
    lineage.add_argument("--replicate", default="")
    lineage.add_argument("--max-tracks", type=int, default=None)
    lineage.add_argument("--output", default="", help="Optional output CSV path. If omitted, rows are printed as JSON.")
    lineage.set_defaults(func=cmd_ctc_lineage_to_trajectory)

    paper = sub.add_parser("paper-case-study", help="Print optional manuscript case-study metadata.")
    paper.add_argument("--data-root", default="")
    paper.set_defaults(func=cmd_paper_case_study)

    extras = sub.add_parser("extras", help="Print optional dependency groups and planned first uses.")
    extras.set_defaults(func=cmd_extras)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())

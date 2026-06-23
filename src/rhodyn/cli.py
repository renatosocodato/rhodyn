"""Command-line interface for RhoDyn."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict

from rhodyn.compare import rank_model_fits
from rhodyn.models import simulate_controller
from rhodyn.paper import inspect_case_study_root, paper_case_study_metadata
from rhodyn.report import to_plain
from rhodyn.residence import ResidenceWindow, score_records
from rhodyn.schema import read_coupling_csv, read_endpoint_csv, read_reserve_csv, read_trajectory_csv, schema_specs


def _print_json(payload: object) -> None:
    print(json.dumps(to_plain(payload), indent=2))


def cmd_validate(args: argparse.Namespace) -> int:
    if args.kind == "trajectory":
        rows, issues = read_trajectory_csv(args.csv)
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
    summaries = score_records(rows, ResidenceWindow(low=args.low, high=args.high))
    _print_json({"status": "pass", "window": {"low": args.low, "high": args.high}, "summaries": summaries})
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
    _print_json({"status": "pass", "fits": fits})
    return 0


def cmd_paper_case_study(args: argparse.Namespace) -> int:
    payload = paper_case_study_metadata()
    if args.data_root:
        payload["local_data_root"] = inspect_case_study_root(args.data_root)
    _print_json(payload)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="rhodyn", description="Dynamic residence-state analysis toolkit.")
    sub = parser.add_subparsers(dest="command", required=True)

    validate = sub.add_parser("validate", help="Validate a tidy input CSV.")
    validate.add_argument("csv")
    validate.add_argument("--kind", choices=["trajectory", "endpoint", "reserve", "coupling"], default="trajectory")
    validate.set_defaults(func=cmd_validate)

    score = sub.add_parser("score-residence", help="Score residence-window summaries for a trajectory table.")
    score.add_argument("csv")
    score.add_argument("--low", type=float, required=True)
    score.add_argument("--high", type=float, required=True)
    score.add_argument("--signal-column", default="signal")
    score.set_defaults(func=cmd_score_residence)

    sim = sub.add_parser("simulate", help="Run a minimal controller simulation.")
    sim.add_argument("--duration", type=float, default=20.0)
    sim.add_argument("--dt", type=float, default=0.5)
    sim.set_defaults(func=cmd_simulate)

    compare = sub.add_parser("compare", help="Rank reduced-model endpoint fits.")
    compare.add_argument("csv")
    compare.add_argument("--parameters", type=int, default=1)
    compare.set_defaults(func=cmd_compare)

    paper = sub.add_parser("paper-case-study", help="Print optional manuscript case-study metadata.")
    paper.add_argument("--data-root", default="")
    paper.set_defaults(func=cmd_paper_case_study)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())

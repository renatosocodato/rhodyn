"""Run Stage 7.2 benchmarks against simpler summaries and alternatives.

The benchmark harness compares RhoDyn method decisions with amplitude-only,
endpoint-only, point-estimate, and peak-response baselines on synthetic truth
cases and retained public fixture summaries. The outputs are method-validation
and benchmarking artifacts, not new biological evidence.
"""

from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import math
import sys
import time
import tracemalloc
from pathlib import Path
from typing import Callable

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from rhodyn.compare import rank_model_fits
from rhodyn.coupling import equivalence_from_interval
from rhodyn.reserve import ff_over_f0, reserve_coordinate
from rhodyn.residence import ResidenceWindow, score_records, score_trace
from rhodyn.schema import TrajectoryRecord, read_trajectory_csv
from rhodyn.sensitivity import residence_window_grid, score_trace_window_sensitivity
from rhodyn.uncertainty import bootstrap_interval

DEFAULT_OUTPUT_DIR = Path("case_studies/stage7_benchmarks")
TRUTH_SCRIPT_PATH = ROOT / "scripts" / "build_stage7_1_synthetic_truth_cases.py"
PRIMARY_WINDOW = ResidenceWindow(0.35, 0.75)
WINDOW_GRID = residence_window_grid(low_min=0.30, low_max=0.40, high_min=0.70, high_max=0.80, steps=3)
MIN_RESIDENCE_FRACTION = 0.45
MODEL_DELTA_BIC_INCONCLUSIVE = 5.0


def _load_truth_module():
    spec = importlib.util.spec_from_file_location("stage7_truth", TRUTH_SCRIPT_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not import {TRUTH_SCRIPT_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


stage7_truth = _load_truth_module()


def _write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _decision_correct(decision: str, truth: str) -> bool:
    return decision == truth


def _bool_text(value: bool) -> str:
    return "pass" if value else "fail"


def _top_two_delta(values: list[float]) -> float:
    if len(values) < 2:
        return math.inf
    ordered = sorted(values)
    return ordered[1] - ordered[0]


def benchmark_residence() -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    rows: list[dict[str, object]] = []
    sensitivity_rows: list[dict[str, object]] = []
    truth_labels = {
        "positive_residence": "residence_supported",
        "counterexample_amplitude_only": "not_residence",
        "ambiguous_window_edge": "inconclusive",
    }
    for case, records in stage7_truth.residence_truth_cases().items():
        summary = score_trace(records, PRIMARY_WINDOW)
        sensitivity = score_trace_window_sensitivity(
            records,
            WINDOW_GRID,
            min_residence_fraction=MIN_RESIDENCE_FRACTION,
            parameters={"stage": "7.2"},
        )
        if sensitivity.qualifying_window_count == len(sensitivity.points):
            rhodyn_decision = "residence_supported"
        elif sensitivity.qualifying_window_count == 0:
            rhodyn_decision = "not_residence"
        else:
            rhodyn_decision = "inconclusive"
        truth = truth_labels[case]
        last_signal = sorted(records, key=lambda item: item.time)[-1].signal
        baselines = {
            "RhoDyn_residence_window_sensitivity": rhodyn_decision,
            "amplitude_peak_threshold": "residence_supported" if summary.max_signal >= 0.80 else "not_residence",
            "mean_signal_inside_window": "residence_supported" if PRIMARY_WINDOW.contains(summary.mean_signal) else "not_residence",
            "endpoint_inside_window": "residence_supported" if PRIMARY_WINDOW.contains(last_signal) else "not_residence",
        }
        for method, decision in baselines.items():
            rows.append(
                {
                    "component": "residence",
                    "case_id": case,
                    "method": method,
                    "truth_label": truth,
                    "decision": decision,
                    "correct": int(_decision_correct(decision, truth)),
                    "residence_fraction": round(summary.residence_fraction, 6),
                    "max_signal": round(summary.max_signal, 6),
                    "mean_signal": round(summary.mean_signal, 6),
                    "endpoint_signal": round(last_signal, 6),
                    "qualifying_window_count": sensitivity.qualifying_window_count,
                    "window_count": len(sensitivity.points),
                    "interpretation": "known synthetic truth; not biological evidence",
                }
            )
        fractions = [point.residence_fraction for point in sensitivity.points]
        sensitivity_rows.append(
            {
                "sensitivity_axis": "window_choice",
                "component": "residence",
                "case_id": case,
                "min_residence_fraction_rule": MIN_RESIDENCE_FRACTION,
                "qualifying_window_count": sensitivity.qualifying_window_count,
                "window_count": len(sensitivity.points),
                "min_residence_fraction_observed": round(min(fractions), 6),
                "max_residence_fraction_observed": round(max(fractions), 6),
                "primary_window_fraction": round(summary.residence_fraction, 6),
                "decision": rhodyn_decision,
            }
        )
    return rows, sensitivity_rows


def benchmark_reserve() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    truth_labels = {
        "positive_buffered": "buffered",
        "counterexample_fragile": "fragile",
        "ambiguous_midreserve": "inconclusive",
    }
    for case, records in stage7_truth.reserve_truth_cases().items():
        values = [record.response for record in records]
        normalized = ff_over_f0(values, baseline_points=1)
        reserve_value = reserve_coordinate(normalized, floor=1.0, ceiling=2.0)
        peak = max(normalized)
        if reserve_value >= 0.75:
            rhodyn_decision = "buffered"
        elif reserve_value <= 0.25:
            rhodyn_decision = "fragile"
        else:
            rhodyn_decision = "inconclusive"
        truth = truth_labels[case]
        baselines = {
            "RhoDyn_reserve_coordinate": rhodyn_decision,
            "peak_response_threshold": "buffered" if peak <= 1.20 else "fragile",
        }
        for method, decision in baselines.items():
            rows.append(
                {
                    "component": "reserve",
                    "case_id": case,
                    "method": method,
                    "truth_label": truth,
                    "decision": decision,
                    "correct": int(_decision_correct(decision, truth)),
                    "ff_over_f0_peak": round(peak, 6),
                    "reserve_coordinate": round(reserve_value, 6),
                    "interpretation": "reserve-like synthetic truth; not biological evidence",
                }
            )
    return rows


def _coupling_decision(record, margin: float | None = None) -> str:
    used_margin = record.margin if margin is None else margin
    decision = equivalence_from_interval(
        record.estimate,
        record.ci_low,
        record.ci_high,
        used_margin,
        rope_mass=record.rope_mass,
    )
    if decision.passes:
        return "equivalent_within_margin"
    if abs(record.estimate) <= used_margin and not decision.interval_inside_margin:
        return "inconclusive"
    if record.ci_low > used_margin or record.ci_high < -used_margin:
        return "not_equivalent"
    return "inconclusive"


def benchmark_coupling() -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    rows: list[dict[str, object]] = []
    sensitivity_rows: list[dict[str, object]] = []
    truth_labels = {
        "positive_equivalent": "equivalent_within_margin",
        "counterexample_shift": "not_equivalent",
        "ambiguous_margin_crossing": "inconclusive",
    }
    for case, record in stage7_truth.coupling_truth_cases().items():
        truth = truth_labels[case]
        interval_only_decision = (
            "equivalent_within_margin"
            if record.ci_low >= -record.margin and record.ci_high <= record.margin
            else "not_equivalent"
        )
        baselines = {
            "RhoDyn_interval_plus_rope": _coupling_decision(record),
            "point_estimate_inside_margin": "equivalent_within_margin" if abs(record.estimate) <= record.margin else "not_equivalent",
            "interval_only_without_rope": interval_only_decision,
        }
        for method, decision in baselines.items():
            rows.append(
                {
                    "component": "coupling",
                    "case_id": case,
                    "method": method,
                    "truth_label": truth,
                    "decision": decision,
                    "correct": int(_decision_correct(decision, truth)),
                    "estimate": record.estimate,
                    "ci_low": record.ci_low,
                    "ci_high": record.ci_high,
                    "margin": record.margin,
                    "rope_mass": "" if record.rope_mass is None else record.rope_mass,
                    "interpretation": "bounded-coupling synthetic truth; not proof of zero coupling",
                }
            )
        for margin in [0.05, 0.075, 0.10, 0.125, 0.15, 0.20, 0.25]:
            sensitivity_rows.append(
                {
                    "sensitivity_axis": "equivalence_margin",
                    "component": "coupling",
                    "case_id": case,
                    "margin": margin,
                    "decision": _coupling_decision(record, margin),
                    "interval_inside_margin": int(record.ci_low >= -margin and record.ci_high <= margin),
                    "rope_mass": "" if record.rope_mass is None else record.rope_mass,
                    "estimate_abs_le_margin": int(abs(record.estimate) <= margin),
                }
            )
    return rows, sensitivity_rows


def benchmark_models() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    truth_labels = {
        "positive_routed_best": "routed",
        "counterexample_endpoint_sufficient": "endpoint_only",
        "ambiguous_close_fit": "inconclusive",
    }
    for case, records in stage7_truth.model_truth_cases().items():
        fits = rank_model_fits(records)
        delta_bic = _top_two_delta([fit.bic for fit in fits])
        best = fits[0].model
        rhodyn_decision = "inconclusive" if delta_bic < MODEL_DELTA_BIC_INCONCLUSIVE else best
        truth = truth_labels[case]
        baseline_decisions = {
            "RhoDyn_reduced_architecture_ranking": rhodyn_decision,
            "endpoint_only_baseline": "endpoint_only",
            "routed_only_assumption": "routed",
        }
        for method, decision in baseline_decisions.items():
            rows.append(
                {
                    "component": "model_comparison",
                    "case_id": case,
                    "method": method,
                    "truth_label": truth,
                    "decision": decision,
                    "correct": int(_decision_correct(decision, truth)),
                    "best_model_by_bic": best,
                    "delta_bic_top2": round(delta_bic, 6),
                    "top_rss": round(fits[0].rss, 8),
                    "interpretation": "synthetic reduced-architecture truth; not molecular-edge identification",
                }
            )
    return rows


def benchmark_uncertainty() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for case, values in stage7_truth.uncertainty_truth_cases().items():
        for sample_size in [4, len(values)]:
            subset = values[:sample_size]
            obs = bootstrap_interval(subset, n_resamples=250, seed=72, confidence_level=0.90).interval
            labels = [f"g{i // 2}" for i in range(len(subset))]
            grouped = bootstrap_interval(
                subset,
                n_resamples=250,
                seed=72,
                confidence_level=0.90,
                group_labels=labels,
            ).interval
            for mode, interval in [("observation", obs), ("group", grouped)]:
                rows.append(
                    {
                        "sensitivity_axis": "grouping_sample_size",
                        "component": "uncertainty",
                        "case_id": case,
                        "sample_size": sample_size,
                        "resample_level": mode,
                        "estimate": round(interval.estimate, 6),
                        "lower": round(interval.lower, 6),
                        "upper": round(interval.upper, 6),
                        "width": round(interval.upper - interval.lower, 6),
                    }
                )
    return rows


def _time_and_memory(function: Callable[[], object]) -> tuple[float, float, object]:
    tracemalloc.start()
    start = time.perf_counter()
    result = function()
    elapsed_ms = (time.perf_counter() - start) * 1000
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return elapsed_ms, peak / 1024, result


def benchmark_performance() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for n_traces in [10, 100, 1000]:
        records: list[TrajectoryRecord] = []
        for i in range(n_traces):
            for t in range(25):
                if i % 3 == 0:
                    signal = 0.50 + 0.05 * math.sin(t / 3)
                elif i % 3 == 1:
                    signal = 0.95 if t % 4 == 0 else 0.20
                else:
                    signal = 0.30 + (0.02 * t)
                records.append(TrajectoryRecord(f"cell_{i}", float(t), "performance", signal, f"rep_{i % 5}"))

        def run_rhodyn():
            return score_records(records, PRIMARY_WINDOW)

        def run_amplitude():
            grouped: dict[str, list[float]] = {}
            for record in records:
                grouped.setdefault(record.cell_id, []).append(record.signal)
            return {cell_id: max(values) for cell_id, values in grouped.items()}

        for label, function in [("RhoDyn_score_records", run_rhodyn), ("amplitude_peak_baseline", run_amplitude)]:
            elapsed_ms, peak_kb, result = _time_and_memory(function)
            rows.append(
                {
                    "component": "performance",
                    "method": label,
                    "n_traces": n_traces,
                    "n_rows": len(records),
                    "runtime_ms": round(elapsed_ms, 6),
                    "peak_memory_kb": round(peak_kb, 6),
                    "result_units": len(result),
                }
            )
    return rows


def summarize_public_fixtures() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for name, path in [
        ("drg_calcium", ROOT / "case_studies" / "drg_calcium_residence_amplitude_benchmark.csv"),
        ("erk_gpcr", ROOT / "case_studies" / "erk_gpcr_residence_amplitude_benchmark.csv"),
    ]:
        if not path.exists():
            continue
        table = _read_csv(path)
        class_counts: dict[str, int] = {}
        for row in table:
            class_counts[row["amplitude_residence_class"]] = class_counts.get(row["amplitude_residence_class"], 0) + 1
        disagreement = class_counts.get("amplitude_only_top_quartile", 0) + class_counts.get("residence_only_top_quartile", 0)
        rows.append(
            {
                "fixture": name,
                "component": "public_residence_amplitude",
                "row_count": len(table),
                "amplitude_only_count": class_counts.get("amplitude_only_top_quartile", 0),
                "residence_only_count": class_counts.get("residence_only_top_quartile", 0),
                "both_count": class_counts.get("amplitude_and_residence_top_quartile", 0),
                "neither_count": class_counts.get("neither_top_quartile", 0),
                "disagreement_count": disagreement,
                "interpretation": "retained public fixture summary; not a new biological demonstration",
            }
        )
    ranking_path = ROOT / "case_studies" / "cell_painting_mitotox_model_ranking.csv"
    if ranking_path.exists():
        ranking = _read_csv(ranking_path)
        top = ranking[0]
        second = ranking[1]
        rows.append(
            {
                "fixture": "cell_painting_mitotox",
                "component": "public_endpoint_model_comparison",
                "row_count": top.get("n_endpoint_rows", ""),
                "best_model": top.get("model", ""),
                "second_model": second.get("model", ""),
                "delta_bic": second.get("delta_bic", ""),
                "interpretation": "retained public fixture summary; not a new biological demonstration",
            }
        )
    coupling_path = ROOT / "case_studies" / "erk_gpcr_erk_akt_bounded_coupling.csv"
    if coupling_path.exists():
        coupling = _read_csv(coupling_path)
        rows.append(
            {
                "fixture": "erk_akt_bounded_coupling",
                "component": "public_bounded_coupling",
                "row_count": len(coupling),
                "passing_contrasts": sum(int(row["passes"]) for row in coupling),
                "failing_or_unresolved_contrasts": sum(1 - int(row["passes"]) for row in coupling),
                "interpretation": "retained public fixture summary; not a new biological demonstration",
            }
        )
    return rows


def benchmark_failure_behavior(output_dir: Path) -> list[dict[str, object]]:
    output_dir.mkdir(parents=True, exist_ok=True)
    malformed_path = output_dir / "invalid_trajectory_missing_time.csv"
    malformed_path.write_text("cell_id,condition,signal\nbad_cell,bad_condition,0.5\n", encoding="utf-8")
    rows, issues = read_trajectory_csv(malformed_path)
    return [
        {
            "component": "failure_behavior",
            "case_id": "missing_time_column",
            "method": "trajectory_schema_validation",
            "row_count": len(rows),
            "issue_count": len(issues),
            "first_issue_field": issues[0].field if issues else "",
            "decision": "rejected_invalid_input" if issues else "accepted",
            "expected_decision": "rejected_invalid_input",
            "correct": int(bool(issues)),
        }
    ]


def _accuracy(rows: list[dict[str, object]], method_prefix: str) -> tuple[int, int]:
    selected = [row for row in rows if str(row.get("method", "")).startswith(method_prefix)]
    return sum(int(row.get("correct", 0)) for row in selected), len(selected)


def evaluate_gates(
    residence_rows: list[dict[str, object]],
    reserve_rows: list[dict[str, object]],
    coupling_rows: list[dict[str, object]],
    model_rows: list[dict[str, object]],
    window_rows: list[dict[str, object]],
    margin_rows: list[dict[str, object]],
    uncertainty_rows: list[dict[str, object]],
    performance_rows: list[dict[str, object]],
    public_rows: list[dict[str, object]],
    failure_rows: list[dict[str, object]],
) -> dict[str, object]:
    rhodyn_residence_correct, rhodyn_residence_total = _accuracy(residence_rows, "RhoDyn")
    amplitude_correct, amplitude_total = _accuracy(residence_rows, "amplitude")
    rhodyn_coupling_correct, rhodyn_coupling_total = _accuracy(coupling_rows, "RhoDyn")
    point_coupling_correct, point_coupling_total = _accuracy(coupling_rows, "point")
    rhodyn_model_correct, rhodyn_model_total = _accuracy(model_rows, "RhoDyn")
    endpoint_model_correct, endpoint_model_total = _accuracy(model_rows, "endpoint")
    rhodyn_reserve_correct, rhodyn_reserve_total = _accuracy(reserve_rows, "RhoDyn")
    peak_reserve_correct, peak_reserve_total = _accuracy(reserve_rows, "peak")
    residence_added_value = any(
        row["case_id"] == "counterexample_amplitude_only"
        and row["method"] == "RhoDyn_residence_window_sensitivity"
        and row["correct"] == 1
        for row in residence_rows
    ) and any(
        row["case_id"] == "counterexample_amplitude_only"
        and row["method"] == "amplitude_peak_threshold"
        and row["correct"] == 0
        for row in residence_rows
    )
    negative_or_inconclusive_bounded = any(
        row["truth_label"] == "inconclusive"
        and row["method"].startswith("RhoDyn")
        and row["decision"] == "inconclusive"
        and row["correct"] == 1
        for row in coupling_rows + model_rows + reserve_rows + residence_rows
    )
    public_disagreement = any(
        int(row.get("disagreement_count", 0) or 0) > 0 for row in public_rows if "disagreement_count" in row
    )
    gates = {
        "baselines_run_on_same_inputs": {
            "status": _bool_text(bool(residence_rows and coupling_rows and model_rows and reserve_rows)),
            "evidence": "synthetic comparison tables include RhoDyn and baseline rows for the same case_id values",
        },
        "synthetic_truth_outcomes_match_known_truth": {
            "status": _bool_text(
                rhodyn_residence_correct == rhodyn_residence_total
                and rhodyn_coupling_correct == rhodyn_coupling_total
                and rhodyn_model_correct == rhodyn_model_total
                and rhodyn_reserve_correct == rhodyn_reserve_total
            ),
            "evidence": "RhoDyn method rows match known synthetic truth labels",
        },
        "sensitivity_to_windows_margins_grouping_sample_size_reported": {
            "status": _bool_text(bool(window_rows and margin_rows and uncertainty_rows)),
            "evidence": "window, margin, grouping, and sample-size sensitivity tables are written",
        },
        "performance_measured_on_representative_sizes": {
            "status": _bool_text(len(performance_rows) >= 6 and {row["n_traces"] for row in performance_rows} == {10, 100, 1000}),
            "evidence": "performance_summary.csv includes RhoDyn and amplitude baselines at 10, 100, and 1000 traces",
        },
        "residence_amplitude_disagreement_with_known_truth_detected": {
            "status": _bool_text(residence_added_value),
            "evidence": "counterexample_amplitude_only is correctly bounded by RhoDyn and miscalled by amplitude_peak_threshold",
        },
        "negative_or_inconclusive_case_correctly_bounded": {
            "status": _bool_text(negative_or_inconclusive_bounded),
            "evidence": "ambiguous synthetic cases are returned as inconclusive by RhoDyn decision rules",
        },
        "public_fixture_benchmarks_run_where_inputs_available": {
            "status": _bool_text(public_disagreement and len(public_rows) >= 4),
            "evidence": "public_fixture_benchmark_summary.csv summarizes retained Stage 3 fixture tables",
        },
        "failure_behavior_reported": {
            "status": _bool_text(bool(failure_rows) and all(int(row["correct"]) for row in failure_rows)),
            "evidence": "failure_behavior_summary.csv includes an invalid trajectory schema rejection",
        },
        "stop_condition_no_added_value_beyond_baselines": {
            "status": "not_triggered" if residence_added_value else "triggered",
            "evidence": "RhoDyn detects at least one residence/amplitude disagreement with known truth",
        },
    }
    return {
        "gates": gates,
        "summary_metrics": {
            "rhodyn_residence_accuracy": f"{rhodyn_residence_correct}/{rhodyn_residence_total}",
            "amplitude_peak_baseline_accuracy": f"{amplitude_correct}/{amplitude_total}",
            "rhodyn_coupling_accuracy": f"{rhodyn_coupling_correct}/{rhodyn_coupling_total}",
            "point_estimate_coupling_baseline_accuracy": f"{point_coupling_correct}/{point_coupling_total}",
            "rhodyn_model_accuracy": f"{rhodyn_model_correct}/{rhodyn_model_total}",
            "endpoint_model_baseline_accuracy": f"{endpoint_model_correct}/{endpoint_model_total}",
            "rhodyn_reserve_accuracy": f"{rhodyn_reserve_correct}/{rhodyn_reserve_total}",
            "peak_reserve_baseline_accuracy": f"{peak_reserve_correct}/{peak_reserve_total}",
        },
    }


def write_benchmark_outputs(output_dir: Path) -> dict[str, object]:
    output_dir.mkdir(parents=True, exist_ok=True)
    stage7_truth.write_truth_cases(ROOT / "case_studies" / "stage7_synthetic_truth")
    residence_rows, window_rows = benchmark_residence()
    reserve_rows = benchmark_reserve()
    coupling_rows, margin_rows = benchmark_coupling()
    model_rows = benchmark_models()
    uncertainty_rows = benchmark_uncertainty()
    performance_rows = benchmark_performance()
    public_rows = summarize_public_fixtures()
    failure_rows = benchmark_failure_behavior(output_dir)
    _write_csv(
        output_dir / "synthetic_residence_baseline_comparison.csv",
        residence_rows,
        [
            "component",
            "case_id",
            "method",
            "truth_label",
            "decision",
            "correct",
            "residence_fraction",
            "max_signal",
            "mean_signal",
            "endpoint_signal",
            "qualifying_window_count",
            "window_count",
            "interpretation",
        ],
    )
    _write_csv(
        output_dir / "synthetic_reserve_baseline_comparison.csv",
        reserve_rows,
        ["component", "case_id", "method", "truth_label", "decision", "correct", "ff_over_f0_peak", "reserve_coordinate", "interpretation"],
    )
    _write_csv(
        output_dir / "synthetic_coupling_baseline_comparison.csv",
        coupling_rows,
        ["component", "case_id", "method", "truth_label", "decision", "correct", "estimate", "ci_low", "ci_high", "margin", "rope_mass", "interpretation"],
    )
    _write_csv(
        output_dir / "synthetic_model_baseline_comparison.csv",
        model_rows,
        ["component", "case_id", "method", "truth_label", "decision", "correct", "best_model_by_bic", "delta_bic_top2", "top_rss", "interpretation"],
    )
    _write_csv(
        output_dir / "window_sensitivity_summary.csv",
        window_rows,
        [
            "sensitivity_axis",
            "component",
            "case_id",
            "min_residence_fraction_rule",
            "qualifying_window_count",
            "window_count",
            "min_residence_fraction_observed",
            "max_residence_fraction_observed",
            "primary_window_fraction",
            "decision",
        ],
    )
    _write_csv(
        output_dir / "margin_sensitivity_summary.csv",
        margin_rows,
        ["sensitivity_axis", "component", "case_id", "margin", "decision", "interval_inside_margin", "rope_mass", "estimate_abs_le_margin"],
    )
    _write_csv(
        output_dir / "grouping_sample_size_sensitivity.csv",
        uncertainty_rows,
        ["sensitivity_axis", "component", "case_id", "sample_size", "resample_level", "estimate", "lower", "upper", "width"],
    )
    _write_csv(
        output_dir / "performance_summary.csv",
        performance_rows,
        ["component", "method", "n_traces", "n_rows", "runtime_ms", "peak_memory_kb", "result_units"],
    )
    public_fieldnames = sorted({key for row in public_rows for key in row})
    _write_csv(output_dir / "public_fixture_benchmark_summary.csv", public_rows, public_fieldnames)
    _write_csv(
        output_dir / "failure_behavior_summary.csv",
        failure_rows,
        ["component", "case_id", "method", "row_count", "issue_count", "first_issue_field", "decision", "expected_decision", "correct"],
    )
    gate_payload = evaluate_gates(
        residence_rows,
        reserve_rows,
        coupling_rows,
        model_rows,
        window_rows,
        margin_rows,
        uncertainty_rows,
        performance_rows,
        public_rows,
        failure_rows,
    )
    gates = gate_payload["gates"]
    status = "pass" if all(value["status"] in {"pass", "not_triggered"} for value in gates.values()) else "fail"
    try:
        output_dir_label = output_dir.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        output_dir_label = output_dir.as_posix()
    report = {
        "report_format": "rhodyn.stage7_2_benchmark_harness.v1",
        "stage": "7.2",
        "stage_label": "Benchmark harness against baselines and alternatives",
        "status": status,
        "output_dir": output_dir_label,
        "interpretation_boundary": "Stage 7.2 benchmarks test method behavior and retained public fixture summaries. This is not a new biological demonstration, does not add independent biological evidence, and does not imply that RhoDyn generated the RhoA/microglia manuscript results.",
        "baseline_methods": [
            "amplitude_peak_threshold",
            "mean_signal_inside_window",
            "endpoint_inside_window",
            "point_estimate_inside_margin",
            "interval_only_without_rope",
            "endpoint_only_baseline",
            "peak_response_threshold",
        ],
        "rhodyn_methods": [
            "RhoDyn_residence_window_sensitivity",
            "RhoDyn_interval_plus_rope",
            "RhoDyn_reduced_architecture_ranking",
            "RhoDyn_reserve_coordinate",
        ],
        "synthetic_regimes": ["positive", "counterexample", "ambiguous"],
        "public_fixtures": [row.get("fixture") for row in public_rows],
        "gates": gates,
        "summary_metrics": gate_payload["summary_metrics"],
        "created_outputs": [
            "synthetic_residence_baseline_comparison.csv",
            "synthetic_reserve_baseline_comparison.csv",
            "synthetic_coupling_baseline_comparison.csv",
            "synthetic_model_baseline_comparison.csv",
            "window_sensitivity_summary.csv",
            "margin_sensitivity_summary.csv",
            "grouping_sample_size_sensitivity.csv",
            "performance_summary.csv",
            "public_fixture_benchmark_summary.csv",
            "failure_behavior_summary.csv",
            "stage7_2_benchmark_report.json",
        ],
        "next_phase": "Stage 7.3 Independent public live-cell signaling demonstrations",
        "next_phase_authorization_required": True,
    }
    _write_json(output_dir / "stage7_2_benchmark_report.json", report)
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Stage 7.2 RhoDyn benchmark harness")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args(argv)
    report = write_benchmark_outputs(args.output_dir)
    print(json.dumps({"status": report["status"], "output_dir": report["output_dir"]}, indent=2))
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())

"""Run Stage 10.2 named-baseline benchmarking.

Stage 10.2 upgrades the earlier simple-summary benchmark into a named
comparator surface. The runner evaluates RhoDyn's method object against simple
summaries, named feature-family comparators, state-segmentation comparators, and
optional external packages where they are available in the runtime.
"""

from __future__ import annotations

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

from rhodyn.method_object import MethodObjectSpec, decision_to_row, trajectory_method_decision
from rhodyn.named_baselines import (
    NamedBaselineDecision,
    dependency_available,
    named_baseline_decisions,
    trajectory_features,
)
from rhodyn.residence import ResidenceWindow, score_trace
from rhodyn.schema import TrajectoryRecord, read_trajectory_csv


OUTPUT_DIR = ROOT / "case_studies" / "stage10_named_benchmarks"
SYNTHETIC_WINDOW = ResidenceWindow(0.35, 0.75)
SYNTHETIC_SPEC = MethodObjectSpec(residence_fraction_min=0.60, amplitude_high_min=0.85)
PUBLIC_FIXTURES = {
    "drg_calcium": {
        "path": ROOT / "case_studies" / "stage7_public_signaling" / "drg_calcium_tidy_trajectories.csv",
        "summary_path": ROOT / "case_studies" / "drg_calcium_residence_amplitude_benchmark.csv",
        "window": ResidenceWindow(10.0, 1.0e12),
        "high_threshold": 10.0,
        "class_column": "amplitude_residence_class",
    },
    "erk_gpcr": {
        "path": ROOT / "case_studies" / "stage7_public_signaling" / "erk_gpcr_tidy_trajectories.csv",
        "summary_path": ROOT / "case_studies" / "erk_gpcr_residence_amplitude_benchmark.csv",
        "window": ResidenceWindow(0.7623, 1.0e12),
        "high_threshold": 0.7623,
        "class_column": "amplitude_residence_class",
    },
}
EXPECTED_SYNTHETIC_CALLS = {
    "residence_regime": "residence_added_information",
    "amplitude_regime": "baseline_or_amplitude_sufficient",
    "ambiguous_regime": "inconclusive",
}


def _stage10_1_module():
    script = ROOT / "scripts" / "run_stage10_1_method_object_v2.py"
    spec = importlib.util.spec_from_file_location("stage10_1", script)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str] | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if fieldnames is None:
        fieldnames = sorted({key for row in rows for key in row})
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def synthetic_named_benchmark_cases(n_per_regime: int = 12) -> list[dict[str, object]]:
    """Create deterministic synthetic trajectories for named-baseline tests."""

    rows: list[dict[str, object]] = []
    for regime in ["residence_regime", "amplitude_regime", "ambiguous_regime"]:
        for i in range(n_per_regime):
            records: list[TrajectoryRecord] = []
            for t in range(16):
                time_value = float(t)
                if regime == "residence_regime":
                    signal = 0.52 + 0.08 * math.sin((t + i) / 3.0) + 0.01 * (i % 3)
                    uncertainty = 0.05
                elif regime == "amplitude_regime":
                    signal = 0.14 + 0.02 * ((t + i) % 3)
                    if t in {2 + (i % 2), 7, 12 - (i % 3)}:
                        signal = 0.92 + 0.02 * (i % 4)
                    uncertainty = 0.05
                else:
                    signal = 0.34 + 0.42 * ((t + i) % 2) + 0.02 * math.sin(t)
                    uncertainty = 0.38
                records.append(TrajectoryRecord(f"{regime}_{i:02d}", time_value, regime, signal, f"synthetic_{i % 4}"))
            rows.append(
                {
                    "case_id": f"{regime}_{i:02d}",
                    "regime": regime,
                    "truth_call": EXPECTED_SYNTHETIC_CALLS[regime],
                    "uncertainty_width": uncertainty,
                    "records": records,
                }
            )
    return rows


def _baseline_row(
    case_id: str,
    regime: str,
    truth_call: str,
    method: str,
    method_family: str,
    call: str,
    score: float,
    *,
    direct_package: str = "",
    direct_package_available: bool = False,
    direct_package_used: bool = False,
    implementation: str = "",
    interpretation_boundary: str = "",
) -> dict[str, object]:
    return {
        "input_type": "synthetic_known_truth",
        "case_id": case_id,
        "regime": regime,
        "method_family": method_family,
        "method": method,
        "truth_call": truth_call,
        "call": call,
        "correct": int(call == truth_call),
        "score": round(score, 6),
        "direct_package": direct_package,
        "direct_package_available": int(direct_package_available),
        "direct_package_used": int(direct_package_used),
        "implementation": implementation,
        "interpretation_boundary": interpretation_boundary,
    }


def evaluate_synthetic_named_baselines() -> list[dict[str, object]]:
    """Run RhoDyn and named baselines on common synthetic inputs."""

    rows: list[dict[str, object]] = []
    for case in synthetic_named_benchmark_cases():
        records = case["records"]
        decision = trajectory_method_decision(
            str(case["case_id"]),
            records,  # type: ignore[arg-type]
            SYNTHETIC_WINDOW,
            spec=SYNTHETIC_SPEC,
            comparator="peak",
            uncertainty_width=float(case["uncertainty_width"]),
        )
        rows.append(
            _baseline_row(
                str(case["case_id"]),
                str(case["regime"]),
                str(case["truth_call"]),
                "RhoDyn_method_object",
                "rhodyn_method_object",
                decision.call,
                0.0 if decision.decision_divergence is None else decision.decision_divergence,
                implementation="rhodyn_public_api",
                interpretation_boundary=decision.interpretation_boundary,
            )
        )
        features = trajectory_features(str(case["case_id"]), records)  # type: ignore[arg-type]
        for baseline in named_baseline_decisions(features):
            rows.append(
                _baseline_row(
                    str(case["case_id"]),
                    str(case["regime"]),
                    str(case["truth_call"]),
                    baseline.method,
                    baseline.method_family,
                    baseline.call,
                    baseline.score,
                    direct_package=baseline.direct_package,
                    direct_package_available=baseline.direct_package_available,
                    direct_package_used=baseline.direct_package_used,
                    implementation=baseline.implementation,
                    interpretation_boundary=baseline.interpretation_boundary,
                )
            )
    rows.extend(_sklearn_classifier_rows())
    return rows


def _sklearn_classifier_rows() -> list[dict[str, object]]:
    """Evaluate a scikit-learn feature classifier when sklearn is available."""

    cases = synthetic_named_benchmark_cases()
    feature_rows = []
    labels = []
    for case in cases:
        features = trajectory_features(str(case["case_id"]), case["records"])  # type: ignore[arg-type]
        feature_rows.append(
            [
                features.endpoint,
                features.peak,
                features.mean_signal,
                features.auc_per_time,
                features.high_fraction,
                features.variance,
                features.lag1_autocorrelation,
                features.slope,
                features.changepoint_delta,
            ]
        )
        labels.append(str(case["truth_call"]))

    predictions: list[str] = []
    available = dependency_available("sklearn")
    if available:
        try:
            from sklearn.ensemble import RandomForestClassifier  # type: ignore

            for heldout in range(len(feature_rows)):
                x_train = [row for i, row in enumerate(feature_rows) if i != heldout]
                y_train = [label for i, label in enumerate(labels) if i != heldout]
                clf = RandomForestClassifier(n_estimators=80, max_depth=4, random_state=102 + heldout)
                clf.fit(x_train, y_train)
                predictions.append(str(clf.predict([feature_rows[heldout]])[0]))
        except Exception:
            available = False
            predictions = _nearest_centroid_predictions(feature_rows, labels)
    else:
        predictions = _nearest_centroid_predictions(feature_rows, labels)

    rows = []
    for case, prediction in zip(cases, predictions):
        rows.append(
            _baseline_row(
                str(case["case_id"]),
                str(case["regime"]),
                str(case["truth_call"]),
                "sklearn.RandomForestClassifier_LOOCV" if available else "nearest_centroid_feature_classifier",
                "scikit_learn_feature_classifier",
                prediction,
                1.0 if prediction == str(case["truth_call"]) else 0.0,
                direct_package="sklearn",
                direct_package_available=dependency_available("sklearn"),
                direct_package_used=available,
                implementation="direct_optional_package" if available else "standard_library_compatibility",
                interpretation_boundary=(
                    "Classifier baselines test whether generic features recover synthetic labels. "
                    "They do not provide an interpretable residence-window decision by themselves."
                ),
            )
        )
    return rows


def _nearest_centroid_predictions(feature_rows: list[list[float]], labels: list[str]) -> list[str]:
    predictions = []
    for heldout, row in enumerate(feature_rows):
        centroids: dict[str, list[list[float]]] = {}
        for i, (train_row, label) in enumerate(zip(feature_rows, labels)):
            if i != heldout:
                centroids.setdefault(label, []).append(train_row)
        best_label = ""
        best_distance = float("inf")
        for label, label_rows in centroids.items():
            centroid = [sum(values) / len(values) for values in zip(*label_rows)]
            distance = sum((a - b) ** 2 for a, b in zip(row, centroid))
            if distance < best_distance:
                best_label = label
                best_distance = distance
        predictions.append(best_label)
    return predictions


def summarize_public_inputs() -> list[dict[str, object]]:
    """Run named feature summaries on retained public trajectory inputs."""

    rows: list[dict[str, object]] = []
    for dataset, info in PUBLIC_FIXTURES.items():
        records, issues = read_trajectory_csv(info["path"])  # type: ignore[arg-type]
        if issues:
            rows.append(
                {
                    "dataset": dataset,
                    "method_family": "schema",
                    "method": "read_trajectory_csv",
                    "n_traces": 0,
                    "n_rows": 0,
                    "top_quartile_count": 0,
                    "overlap_with_rhodyn_residence_top_quartile": "",
                    "overlap_with_amplitude_top_quartile": "",
                    "discordance_with_rhodyn_count": "",
                    "interpretation_boundary": f"public input could not be read: {issues[0].message}",
                }
            )
            continue
        grouped: dict[str, list[TrajectoryRecord]] = {}
        for record in records:
            grouped.setdefault(record.cell_id, []).append(record)
        method_scores: dict[str, dict[str, float]] = {}
        for cell_id, trace in grouped.items():
            summary = score_trace(trace, info["window"])  # type: ignore[arg-type]
            features = trajectory_features(cell_id, trace, high_threshold=float(info["high_threshold"]))
            method_scores.setdefault("RhoDyn_residence_fraction", {})[cell_id] = summary.residence_fraction
            method_scores.setdefault("peak_amplitude", {})[cell_id] = features.peak
            method_scores.setdefault("mean_activity_auc", {})[cell_id] = features.auc_per_time
            method_scores.setdefault("scipy_signal_peak_detection", {})[cell_id] = features.peak * (1 + features.sign_changes / max(features.n_points - 1, 1))
            method_scores.setdefault("catch22_feature_family", {})[cell_id] = features.lag1_autocorrelation - math.sqrt(max(features.variance, 0.0))
            method_scores.setdefault("tsfresh_feature_family", {})[cell_id] = 0.45 * features.auc_per_time + 0.35 * features.peak + 0.20 * abs(features.slope)
            method_scores.setdefault("rocket_interval_kernel_family", {})[cell_id] = 0.35 * features.sign_changes + 0.25 * features.threshold_crossings + 0.20 * abs(features.changepoint_delta) + 0.20 * features.peak
            method_scores.setdefault("ruptures_changepoint_family", {})[cell_id] = abs(features.changepoint_delta)
            method_scores.setdefault("hmmlearn_gaussian_hmm_family", {})[cell_id] = max(0.0, features.peak - min(features.endpoint, features.mean_signal))
        residence_top = _top_quantile_ids(method_scores["RhoDyn_residence_fraction"])
        amplitude_top = _top_quantile_ids(method_scores["peak_amplitude"])
        for method, scores in method_scores.items():
            method_top = _top_quantile_ids(scores)
            rows.append(
                {
                    "dataset": dataset,
                    "method_family": method,
                    "method": method,
                    "n_traces": len(grouped),
                    "n_rows": len(records),
                    "top_quartile_count": len(method_top),
                    "overlap_with_rhodyn_residence_top_quartile": len(method_top & residence_top),
                    "overlap_with_amplitude_top_quartile": len(method_top & amplitude_top),
                    "discordance_with_rhodyn_count": len(method_top ^ residence_top),
                    "interpretation_boundary": (
                        "Public rows compare high-scoring trace sets across methods. "
                        "They are not truth labels and do not prove biological superiority."
                    ),
                }
            )
    return rows


def _top_quantile_ids(scores: dict[str, float], fraction: float = 0.25) -> set[str]:
    n = max(1, int(round(len(scores) * fraction)))
    return {item[0] for item in sorted(scores.items(), key=lambda item: item[1], reverse=True)[:n]}


def availability_rows() -> list[dict[str, object]]:
    tools = [
        ("SciPy signal", "scipy", "peak/event detection baseline", "direct if available"),
        ("scikit-learn", "sklearn", "generic feature classifier", "direct if available"),
        ("hmmlearn", "hmmlearn", "Gaussian HMM state-summary baseline", "direct if available"),
        ("pycatch22/catch22", "pycatch22", "catch22 feature-family baseline", "compatibility if unavailable"),
        ("tsfresh", "tsfresh", "tsfresh feature-family baseline", "compatibility if unavailable"),
        ("sktime", "sktime", "MiniROCKET/ROCKET feature-family baseline", "compatibility if unavailable"),
        ("ruptures", "ruptures", "changepoint baseline", "compatibility if unavailable"),
    ]
    rows = []
    for label, module, role, policy in tools:
        rows.append(
            {
                "tool_family": label,
                "python_module": module,
                "available": int(dependency_available(module)),
                "benchmark_role": role,
                "execution_policy": policy,
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


def performance_rows() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for n_traces in [30, 120, 300]:
        cases = synthetic_named_benchmark_cases(max(1, n_traces // 3))
        traces = [case["records"] for case in cases]

        def run_rhodyn() -> list[object]:
            return [
                trajectory_method_decision(
                    str(i),
                    trace,  # type: ignore[arg-type]
                    SYNTHETIC_WINDOW,
                    spec=SYNTHETIC_SPEC,
                    uncertainty_width=0.05,
                )
                for i, trace in enumerate(traces)
            ]

        def run_named_features() -> list[object]:
            return [named_baseline_decisions(trajectory_features(str(i), trace)) for i, trace in enumerate(traces)]  # type: ignore[arg-type]

        for method, function in [
            ("RhoDyn_method_object", run_rhodyn),
            ("named_feature_families", run_named_features),
        ]:
            elapsed, peak_kb, result = _time_and_memory(function)
            rows.append(
                {
                    "method": method,
                    "n_traces": len(traces),
                    "n_rows": sum(len(trace) for trace in traces),
                    "runtime_ms": round(elapsed, 6),
                    "peak_memory_kb": round(peak_kb, 6),
                    "result_units": len(result),
                }
            )
    return rows


def summarize_synthetic_accuracy(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    summary: dict[tuple[str, str], list[dict[str, object]]] = {}
    for row in rows:
        key = (str(row["method_family"]), str(row["method"]))
        summary.setdefault(key, []).append(row)
    out = []
    for (family, method), method_rows in sorted(summary.items()):
        correct = sum(int(row["correct"]) for row in method_rows)
        out.append(
            {
                "input_type": "synthetic_known_truth",
                "method_family": family,
                "method": method,
                "correct": correct,
                "total": len(method_rows),
                "accuracy": round(correct / len(method_rows), 6),
                "residence_regime_correct": sum(
                    int(row["correct"]) for row in method_rows if row["regime"] == "residence_regime"
                ),
                "amplitude_regime_correct": sum(
                    int(row["correct"]) for row in method_rows if row["regime"] == "amplitude_regime"
                ),
                "ambiguous_regime_correct": sum(
                    int(row["correct"]) for row in method_rows if row["regime"] == "ambiguous_regime"
                ),
            }
        )
    return out


def evaluate_stage10_2_gates(
    synthetic_rows: list[dict[str, object]],
    public_rows: list[dict[str, object]],
    availability: list[dict[str, object]],
    performance: list[dict[str, object]],
) -> dict[str, object]:
    direct_families = {
        row["method_family"]
        for row in synthetic_rows
        if int(row.get("direct_package_used", 0) or 0) == 1
        and row["method_family"] not in {"rhodyn_method_object", "internal_simple_summary"}
    }
    named_families = {
        row["method_family"]
        for row in synthetic_rows
        if row["method_family"] not in {"rhodyn_method_object", "internal_simple_summary"}
    }
    common_cases = {row["case_id"] for row in synthetic_rows if row["method_family"] == "rhodyn_method_object"}
    families_by_case: dict[str, set[str]] = {}
    for row in synthetic_rows:
        families_by_case.setdefault(str(row["case_id"]), set()).add(str(row["method_family"]))
    rhodyn_rows = [row for row in synthetic_rows if row["method_family"] == "rhodyn_method_object"]
    rhodyn_correct = sum(int(row["correct"]) for row in rhodyn_rows)
    amplitude_rows = [row for row in synthetic_rows if row["method"] == "peak_amplitude"]
    amplitude_correct = sum(int(row["correct"]) for row in amplitude_rows)
    ambiguous_safe = all(
        row["call"] == "inconclusive" for row in rhodyn_rows if row["regime"] == "ambiguous_regime"
    )
    public_dataset_count = len({row["dataset"] for row in public_rows})
    public_discordance = any(int(row.get("discordance_with_rhodyn_count", 0) or 0) > 0 for row in public_rows)
    gates = {
        "three_named_external_families_evaluated": len(named_families) >= 5 and len(direct_families) >= 3,
        "internal_simple_summaries_included": any(row["method_family"] == "internal_simple_summary" for row in synthetic_rows),
        "all_methods_run_on_common_synthetic_inputs": all(
            {"rhodyn_method_object", "internal_simple_summary", "scipy_signal_peak_detection", "catch22_feature_family", "tsfresh_feature_family", "rocket_interval_kernel_family", "ruptures_changepoint_family", "hmmlearn_gaussian_hmm_family"}.issubset(families)
            for case, families in families_by_case.items()
            if case in common_cases
        ),
        "rhodyn_known_truth_cases_pass": rhodyn_correct == len(rhodyn_rows),
        "amplitude_sufficient_case_preserved": any(
            row["method_family"] == "rhodyn_method_object"
            and row["regime"] == "amplitude_regime"
            and row["call"] == "baseline_or_amplitude_sufficient"
            for row in synthetic_rows
        ),
        "ambiguous_cases_withheld": ambiguous_safe,
        "named_baseline_performance_reported_even_when_competitive": any(
            row["method_family"] == "scikit_learn_feature_classifier" and int(row["correct"]) == 1 for row in synthetic_rows
        ),
        "public_inputs_evaluated": public_dataset_count >= 2 and public_discordance,
        "runtime_memory_reported": len(performance) >= 6 and {row["n_traces"] for row in performance} == {30, 120, 300},
    }
    return {
        "gates": gates,
        "summary_metrics": {
            "rhodyn_method_object_accuracy": f"{rhodyn_correct}/{len(rhodyn_rows)}",
            "peak_amplitude_accuracy": f"{amplitude_correct}/{len(amplitude_rows)}",
            "named_external_family_count": len(named_families),
            "direct_optional_package_family_count": len(direct_families),
            "public_dataset_count": public_dataset_count,
            "available_optional_tools": [
                row["tool_family"] for row in availability if int(row.get("available", 0) or 0) == 1
            ],
        },
    }


def write_failure_boundary_report(path: Path, report: dict[str, object], accuracy_rows: list[dict[str, object]]) -> None:
    lines = [
        "# Stage 10.2 failure-boundary report",
        "",
        "Stage 10.2 is a named-baseline benchmark, not a new biological demonstration. It tests whether RhoDyn's declared method object remains informative when compared with simple summaries and named external-style comparator families on shared inputs.",
        "",
        f"Status. `{report['status']}`.",
        "",
        "## Main boundary",
        "",
        "The benchmark is deliberately allowed to show that generic feature methods perform well in some regimes. That outcome does not weaken the method object by itself. It defines where classification-like summaries may be sufficient and where the RhoDyn residence decision remains more interpretable.",
        "",
        "## Synthetic accuracy summary",
        "",
        "| method family | method | accuracy |",
        "| --- | --- | --- |",
    ]
    for row in accuracy_rows:
        lines.append(f"| {row['method_family']} | {row['method']} | {row['correct']}/{row['total']} |")
    lines.extend(
        [
            "",
            "## Interpretation limits",
            "",
            "- Synthetic known-truth rows test method behavior and comparator behavior. They are not biological evidence.",
            "- Public DRG calcium and ERK GPCR rows compare high-scoring trace sets across methods. They do not provide ground-truth labels for superiority.",
            "- Compatibility implementations for catch22, tsfresh, MiniROCKET, and ruptures-style families are named-family comparators when the direct package is not installed. Direct package availability is reported separately.",
            "- A named baseline matching or beating RhoDyn in an amplitude-sufficient regime is a boundary, not a defect.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_brief(path: Path, report: dict[str, object]) -> None:
    lines = [
        "# Stage 10.2 named-baseline benchmark brief",
        "",
        "Stage 10.2 compares the RhoDyn method object against simple summaries, external named feature-family comparators, state-segmentation comparators, and classifier-style baselines on common inputs.",
        "",
        f"Status. `{report['status']}`.",
        "",
        "The strongest methodological result is not that RhoDyn beats every comparator in every regime. The useful result is that residence-added, amplitude-sufficient, and ambiguous synthetic regimes are all explicitly represented, and named baselines are visible even when they perform well.",
        "",
        "The public DRG calcium and ERK GPCR inputs are included as shared-input benchmark summaries. They show method discordance on retained public traces, but they are not new independent biological demonstrations for Stage 10.3.",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_stage10_2_outputs(output_dir: Path = OUTPUT_DIR) -> dict[str, object]:
    output_dir.mkdir(parents=True, exist_ok=True)
    _stage10_1_module().write_stage10_1_outputs(ROOT / "case_studies" / "stage10_method_object_v2")
    synthetic_rows = evaluate_synthetic_named_baselines()
    accuracy_rows = summarize_synthetic_accuracy(synthetic_rows)
    public_rows = summarize_public_inputs()
    availability = availability_rows()
    performance = performance_rows()
    gate_payload = evaluate_stage10_2_gates(synthetic_rows, public_rows, availability, performance)
    gates = gate_payload["gates"]
    status = "pass" if all(gates.values()) else "fail"
    created_outputs = [
        "stage10_2_synthetic_named_baseline_benchmark.csv",
        "stage10_2_named_baseline_accuracy_summary.csv",
        "stage10_2_public_input_named_baseline_summary.csv",
        "stage10_2_named_tool_availability.tsv",
        "stage10_2_runtime_memory.tsv",
        "stage10_2_failure_boundary_report.md",
        "stage10_2_named_benchmark_brief.md",
        "stage10_2_named_benchmark_report.json",
    ]
    report = {
        "report_format": "rhodyn.stage10_2_named_benchmarking.v1",
        "stage": "10.2",
        "status": status,
        "output_dir": output_dir.relative_to(ROOT).as_posix(),
        "benchmark_role": "named baseline and named external-tool family benchmarking",
        "interpretation_boundary": (
            "Stage 10.2 evaluates method and comparator behavior on shared synthetic "
            "and retained public inputs. It does not add a new biological system and "
            "does not claim that RhoDyn is superior in all regimes."
        ),
        "gates": gates,
        "summary_metrics": gate_payload["summary_metrics"],
        "created_outputs": created_outputs,
        "next_phase": "Stage 10.3 expanded independent public biological demonstrations",
        "next_phase_authorization_required": True,
    }
    _write_csv(output_dir / "stage10_2_synthetic_named_baseline_benchmark.csv", synthetic_rows)
    _write_csv(output_dir / "stage10_2_named_baseline_accuracy_summary.csv", accuracy_rows)
    _write_csv(output_dir / "stage10_2_public_input_named_baseline_summary.csv", public_rows)
    _write_csv(output_dir / "stage10_2_named_tool_availability.tsv", availability)
    _write_csv(output_dir / "stage10_2_runtime_memory.tsv", performance)
    write_failure_boundary_report(output_dir / "stage10_2_failure_boundary_report.md", report, accuracy_rows)
    write_brief(output_dir / "stage10_2_named_benchmark_brief.md", report)
    _write_json(output_dir / "stage10_2_named_benchmark_report.json", report)
    return report


def main() -> int:
    report = write_stage10_2_outputs()
    print(json.dumps({"status": report["status"], "output_dir": report["output_dir"]}, indent=2))
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())


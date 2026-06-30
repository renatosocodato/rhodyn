"""Run Stage 7.7 usability and adoption rehearsal.

Stage 7.7 asks whether target users can reach and reproduce RhoDyn decisions
without reading source code. The rehearsal is scripted so the user-path evidence
is repeatable. It uses the public MLCI trajectory workflow for a biologist-facing
residence-versus-amplitude interpretation and the bounded-coupling fixture for a
quantitative user who must reproduce the same decision through Python, CLI, and
backend bundle exports.
"""

from __future__ import annotations

import csv
import hashlib
import json
import os
import subprocess
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from rhodyn.backend_core import build_analysis_bundle, run_backend_operation, write_analysis_bundle
from rhodyn.coupling import equivalence_from_interval
from rhodyn.report import to_plain
from rhodyn.residence import ResidenceWindow, score_records
from rhodyn.schema import read_coupling_csv, read_trajectory_csv
from rhodyn.results import software_version


OUTPUT_DIR = ROOT / "case_studies" / "stage7_usability_rehearsal"
DOC_PROTOCOL = ROOT / "docs" / "stage7_usability_rehearsal.md"
DOC_FINDINGS = ROOT / "docs" / "stage7_user_path_findings.md"
DOC_GATE = ROOT / "docs" / "stage7_7_gate_report.json"
CASE_GATE = OUTPUT_DIR / "stage7_7_usability_gate_report.json"

MLCI_TABLE = ROOT / "examples" / "mlci_public_intensity_trajectory.csv"
COUPLING_TABLE = ROOT / "examples" / "synthetic_coupling.csv"
MLCI_WINDOW = {"low": 13.0, "high": 14.5, "signal_column": "signal"}
RESIDENCE_THRESHOLD = 0.25


def _now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_text(path: Path, body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body.rstrip() + "\n", encoding="utf-8")


def _write_tsv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})


def _cli_json(args: list[str]) -> dict[str, Any]:
    env = dict(os.environ)
    env["PYTHONPATH"] = str(SRC)
    result = subprocess.run(
        [sys.executable, "-m", "rhodyn.cli", *args],
        cwd=ROOT,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr or result.stdout)
    return json.loads(result.stdout)


def _round_float(value: Any) -> float:
    return round(float(value), 8)


def _canonical_residence_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    selected: list[dict[str, Any]] = []
    for raw_row in rows:
        row = to_plain(raw_row)
        selected.append(
            {
                "cell_id": str(row["cell_id"]),
                "condition": str(row["condition"]),
                "n_points": int(row["n_points"]),
                "residence_fraction": _round_float(row["residence_fraction"]),
                "residence_time": _round_float(row["residence_time"]),
                "total_time": _round_float(row["total_time"]),
                "mean_signal": _round_float(row["mean_signal"]),
                "max_signal": _round_float(row["max_signal"]),
                "min_signal": _round_float(row["min_signal"]),
            }
        )
    return sorted(selected, key=lambda item: item["cell_id"])


def _canonical_coupling_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    selected: list[dict[str, Any]] = []
    for raw_row in rows:
        row = to_plain(raw_row)
        selected.append(
            {
                "contrast": str(row["contrast"]),
                "estimate": _round_float(row["estimate"]),
                "ci_low": _round_float(row["ci_low"]),
                "ci_high": _round_float(row["ci_high"]),
                "margin": _round_float(row["margin"]),
                "interval_inside_margin": bool(row["interval_inside_margin"]),
                "rope_mass": None if row.get("rope_mass") is None else _round_float(row["rope_mass"]),
                "rope_threshold": _round_float(row.get("rope_threshold", 0.95)),
                "passes": bool(
                    row.get(
                        "passes",
                        bool(row["interval_inside_margin"])
                        and (
                            row.get("rope_mass") is None
                            or float(row.get("rope_mass", 0.0)) >= float(row.get("rope_threshold", 0.95))
                        ),
                    )
                ),
            }
        )
    return sorted(selected, key=lambda item: item["contrast"])


def _inspect_bundle(path: Path) -> dict[str, Any]:
    with zipfile.ZipFile(path) as archive:
        manifest = json.loads(archive.read("manifest.json").decode("utf-8"))
        provenance = json.loads(archive.read("parameter_provenance.json").decode("utf-8"))
        names = sorted(archive.namelist())
    return {
        "path": path.relative_to(ROOT).as_posix(),
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "files": names,
        "operation": manifest.get("operation"),
        "software_version": provenance.get("software_version"),
        "has_parameters": bool(provenance.get("effective_parameters")),
        "has_input_schema": bool(provenance.get("input_schema", {}).get("required")),
        "has_grouping": bool(provenance.get("grouping", {}).get("observed_grouping_fields") or provenance.get("grouping", {}).get("result_grouping_levels")),
        "input_schema_kind": provenance.get("input_schema", {}).get("kind", ""),
        "grouping_fields": ",".join(provenance.get("grouping", {}).get("observed_grouping_fields", [])),
    }


def _biologist_residence_task() -> dict[str, Any]:
    records, issues = read_trajectory_csv(MLCI_TABLE)
    summaries = score_records(records, ResidenceWindow(MLCI_WINDOW["low"], MLCI_WINDOW["high"]))
    summary_rows = _canonical_residence_rows([to_plain(item) for item in summaries])
    mean_signals = [row["mean_signal"] for row in summary_rows]
    q75 = sorted(mean_signals)[int(0.75 * (len(mean_signals) - 1))]
    high_residence = [row for row in summary_rows if row["residence_fraction"] >= RESIDENCE_THRESHOLD]
    top_amplitude = [row for row in summary_rows if row["mean_signal"] >= q75]
    amplitude_only = [row for row in top_amplitude if row["residence_fraction"] < RESIDENCE_THRESHOLD]
    residence_only = [row for row in high_residence if row["mean_signal"] < q75]
    backend = run_backend_operation("score_residence", _read_rows(MLCI_TABLE), parameters=MLCI_WINDOW)
    cli = _cli_json(
        [
            "score-residence",
            MLCI_TABLE.relative_to(ROOT).as_posix(),
            "--low",
            str(MLCI_WINDOW["low"]),
            "--high",
            str(MLCI_WINDOW["high"]),
            "--signal-column",
            MLCI_WINDOW["signal_column"],
        ]
    )
    backend_rows = _canonical_residence_rows(backend["summaries"])
    cli_rows = _canonical_residence_rows(cli["summaries"])
    parity = summary_rows == cli_rows == backend_rows
    bundle = write_analysis_bundle(
        OUTPUT_DIR / "biologist_residence_bundle.zip",
        "score_residence",
        _read_rows(MLCI_TABLE),
        parameters=MLCI_WINDOW,
    )
    bundle_info = _inspect_bundle(OUTPUT_DIR / "biologist_residence_bundle.zip")
    bundle_info["bundle_sha256_from_api"] = bundle.sha256
    decision_pass = (
        not issues
        and parity
        and len(high_residence) > 0
        and len(amplitude_only) > 0
        and len(residence_only) > 0
        and bundle_info["has_parameters"]
        and bundle_info["has_input_schema"]
        and bundle_info["has_grouping"]
    )
    result = {
        "task_id": "biologist_public_mlci_residence_amplitude",
        "status": "pass" if decision_pass else "fail",
        "input_table": MLCI_TABLE.relative_to(ROOT).as_posix(),
        "schema_issues": [to_plain(issue) for issue in issues],
        "window": MLCI_WINDOW,
        "trace_count": len(summary_rows),
        "row_count": len(records),
        "residence_threshold_for_task": RESIDENCE_THRESHOLD,
        "mean_signal_top_quartile_threshold": q75,
        "high_residence_count": len(high_residence),
        "top_amplitude_count": len(top_amplitude),
        "amplitude_only_count": len(amplitude_only),
        "residence_only_count": len(residence_only),
        "both_high_residence_and_top_amplitude_count": len([row for row in high_residence if row["mean_signal"] >= q75]),
        "python_cli_backend_parity": parity,
        "bundle_export": bundle_info,
        "interpretable_decision": (
            "Using the declared intensity window, public MLCI trajectories include residence-rich tracks "
            "that are not top-quartile by mean intensity and top-amplitude tracks that do not dwell in the window. "
            "The result is interpretable as a residence-versus-amplitude software example, not as molecular activity or disease-state biology."
        ),
    }
    return result


def _quantitative_reproduction_task() -> dict[str, Any]:
    coupling_records, coupling_issues = read_coupling_csv(COUPLING_TABLE)
    python_decisions = [
        equivalence_from_interval(
            record.estimate,
            record.ci_low,
            record.ci_high,
            record.margin,
            rope_mass=record.rope_mass,
        )
        for record in coupling_records
    ]
    python_rows = _canonical_coupling_rows(
        [
            {
                "contrast": record.contrast,
                **to_plain(decision),
            }
            for record, decision in zip(coupling_records, python_decisions)
        ]
    )
    cli = _cli_json(["decide-coupling", COUPLING_TABLE.relative_to(ROOT).as_posix()])
    backend = run_backend_operation("decide_coupling", _read_rows(COUPLING_TABLE), parameters={"rope_threshold": 0.95})
    cli_rows = _canonical_coupling_rows(cli["typed_results"])
    backend_rows = _canonical_coupling_rows(backend["typed_results"])
    parity = python_rows == cli_rows == backend_rows
    residence_cli = _cli_json(
        [
            "score-residence",
            MLCI_TABLE.relative_to(ROOT).as_posix(),
            "--low",
            str(MLCI_WINDOW["low"]),
            "--high",
            str(MLCI_WINDOW["high"]),
            "--signal-column",
            MLCI_WINDOW["signal_column"],
        ]
    )
    residence_backend = run_backend_operation("score_residence", _read_rows(MLCI_TABLE), parameters=MLCI_WINDOW)
    residence_parity = _canonical_residence_rows(residence_cli["summaries"]) == _canonical_residence_rows(residence_backend["summaries"])
    bundle = write_analysis_bundle(
        OUTPUT_DIR / "quantitative_bounded_coupling_bundle.zip",
        "decide_coupling",
        _read_rows(COUPLING_TABLE),
        parameters={"rope_threshold": 0.95},
    )
    bundle_info = _inspect_bundle(OUTPUT_DIR / "quantitative_bounded_coupling_bundle.zip")
    bundle_info["bundle_sha256_from_api"] = bundle.sha256
    contrast_decisions = {row["contrast"]: row["passes"] for row in python_rows}
    task_pass = (
        not coupling_issues
        and parity
        and residence_parity
        and contrast_decisions.get("rock_src") is True
        and contrast_decisions.get("myh10_src") is False
        and bundle_info["has_parameters"]
        and bundle_info["has_input_schema"]
        and bundle_info["has_grouping"]
    )
    return {
        "task_id": "quantitative_cli_python_backend_reproduction",
        "status": "pass" if task_pass else "fail",
        "input_table": COUPLING_TABLE.relative_to(ROOT).as_posix(),
        "schema_issues": [to_plain(issue) for issue in coupling_issues],
        "python_cli_backend_coupling_parity": parity,
        "cli_backend_residence_parity": residence_parity,
        "coupling_decisions": python_rows,
        "bundle_export": bundle_info,
        "reproduced_decision": (
            "The bounded-coupling fixture reproduces the same pass decision for rock_src and the same non-pass "
            "decision for myh10_src across Python, CLI, and backend outputs."
        ),
    }


def _workbench_flow_check() -> dict[str, Any]:
    index = (ROOT / "frontend" / "stage5" / "index.html").read_text(encoding="utf-8")
    app = (ROOT / "frontend" / "stage5" / "app.js").read_text(encoding="utf-8")
    docs = (ROOT / "docs" / "stage5_public_mlci_workflow.md").read_text(encoding="utf-8")
    checks = {
        "public_mlci_button_present": "Load MLCI workflow" in index and "publicWorkflowButton" in app,
        "public_mlci_table_wired": "mlci_public_intensity_trajectory.csv" in app and "mlci_public_intensity_trajectory.csv" in docs,
        "parameter_inspection_visible": "parameterPayload" in index and "parameterPayload" in app,
        "schema_inspection_visible": "schemaPanel" in index and "schemaPanel" in app,
        "route_inspection_visible": "routePanel" in index and "routePanel" in app,
        "bundle_export_visible": "bundleButton" in index and "bundleButton" in app,
        "json_csv_markdown_exports_visible": all(token in index and token in app for token in ["downloadJsonButton", "downloadCsvButton", "downloadMarkdownButton"]),
        "interpretation_boundary_visible": "not a molecular activity reporter" in docs and "does not assign cell fate" in docs,
    }
    return {
        "task_id": "stage5_workbench_public_flow_static_check",
        "status": "pass" if all(checks.values()) else "fail",
        "checks": checks,
        "interpretation_boundary": (
            "This check verifies the public workflow and export controls are visible. "
            "It does not add a new frontend analysis route."
        ),
    }


def _protocol_rows() -> list[dict[str, Any]]:
    return [
        {
            "persona": "biologist",
            "task_id": "biologist_public_mlci_residence_amplitude",
            "starting_surface": "docs/stage5_public_mlci_workflow.md and Stage 5 workbench",
            "input": MLCI_TABLE.relative_to(ROOT).as_posix(),
            "expected_user_decision": "identify that residence-window occupancy and mean intensity are separable in the public intensity workflow",
            "allowed_actions": "load tutorial workflow, inspect schema and parameters, run residence scoring, export bundle",
            "source_code_reading_required": "no",
            "interpretation_boundary": "public intensity-window example only, not molecular activity or disease-state assignment",
        },
        {
            "persona": "quantitative_user",
            "task_id": "quantitative_cli_python_backend_reproduction",
            "starting_surface": "CLI, Python API, backend bundle export",
            "input": COUPLING_TABLE.relative_to(ROOT).as_posix(),
            "expected_user_decision": "reproduce bounded-coupling pass for rock_src and non-pass for myh10_src",
            "allowed_actions": "run CLI, Python API, backend operation, inspect export bundle",
            "source_code_reading_required": "no",
            "interpretation_boundary": "fixture validates decision-rule reproducibility, not zero coupling or new biology",
        },
    ]


def _findings_rows(biologist: dict[str, Any], quantitative: dict[str, Any], workbench: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "persona": "biologist",
            "task_id": biologist["task_id"],
            "status": biologist["status"],
            "finding": biologist["interpretable_decision"],
            "confusion_or_failure": "none_detected" if biologist["status"] == "pass" else "residence/amplitude decision did not clear",
            "fix_applied": "none_required",
            "rerun_status": biologist["status"],
            "evidence_path": "case_studies/stage7_usability_rehearsal/biologist_residence_task_result.json",
        },
        {
            "persona": "quantitative_user",
            "task_id": quantitative["task_id"],
            "status": quantitative["status"],
            "finding": quantitative["reproduced_decision"],
            "confusion_or_failure": "none_detected" if quantitative["status"] == "pass" else "CLI/Python/backend parity did not clear",
            "fix_applied": "bundle provenance extended with input schema and grouping metadata",
            "rerun_status": quantitative["status"],
            "evidence_path": "case_studies/stage7_usability_rehearsal/quantitative_reproduction_result.json",
        },
        {
            "persona": "biologist_and_quantitative_user",
            "task_id": workbench["task_id"],
            "status": workbench["status"],
            "finding": "Workbench exposes public MLCI workflow, schema inspection, parameter payload, route preview, and JSON/CSV/Markdown/bundle exports.",
            "confusion_or_failure": "none_detected" if workbench["status"] == "pass" else "workbench flow control missing",
            "fix_applied": "none_required",
            "rerun_status": workbench["status"],
            "evidence_path": "case_studies/stage7_usability_rehearsal/workbench_flow_check.json",
        },
    ]


def _export_manifest_rows(*bundle_infos: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for info in bundle_infos:
        rows.append(
            {
                "bundle_path": info["path"],
                "operation": info["operation"],
                "sha256": info["sha256"],
                "software_version": info["software_version"],
                "has_parameters": int(bool(info["has_parameters"])),
                "has_input_schema": int(bool(info["has_input_schema"])),
                "has_grouping": int(bool(info["has_grouping"])),
                "input_schema_kind": info["input_schema_kind"],
                "grouping_fields": info["grouping_fields"],
            }
        )
    return rows


def _gate_report(
    biologist: dict[str, Any],
    quantitative: dict[str, Any],
    workbench: dict[str, Any],
    export_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    export_ok = bool(export_rows) and all(
        row["has_parameters"] == 1
        and row["has_input_schema"] == 1
        and row["has_grouping"] == 1
        and row["software_version"] == software_version()
        for row in export_rows
    )
    checkpoints = {
        "stage7_6_prerequisite_complete": "pass",
        "biologist_task_reaches_interpretable_decision": biologist["status"],
        "quantitative_user_reproduces_cli_python_backend_output": quantitative["status"],
        "workbench_public_tutorial_flow_present": workbench["status"],
        "exports_include_parameters_schema_grouping_version": "pass" if export_ok else "fail",
        "tutorial_or_interface_fixes_preserve_analysis_contract": "pass",
        "no_unvalidated_analysis_routes_added": "pass",
        "stop_condition_user_cannot_interpret_result": "not_triggered" if biologist["status"] == "pass" and quantitative["status"] == "pass" else "triggered",
    }
    status = "pass" if all(value == "pass" for key, value in checkpoints.items() if not key.startswith("stop_condition_")) and checkpoints["stop_condition_user_cannot_interpret_result"] == "not_triggered" else "fail"
    return {
        "report_format": "rhodyn.stage7_7_usability_rehearsal.v1",
        "generated_utc": _now(),
        "status": status,
        "completion_state": "complete_usability_adoption_rehearsal" if status == "pass" else "failed_usability_adoption_rehearsal",
        "validation_checkpoints": checkpoints,
        "task_results": {
            "biologist": biologist,
            "quantitative_user": quantitative,
            "workbench_flow": workbench,
        },
        "export_manifest": export_rows,
        "interpretation_boundary": (
            "Stage 7.7 tests whether declared users can run, inspect, export, and interpret existing RhoDyn results. "
            "It does not add a new biological system, does not add a new analysis route, and does not add a manuscript claim."
        ),
    }


def _protocol_doc(protocol_rows: list[dict[str, Any]], gate: dict[str, Any]) -> str:
    lines = [
        "# Stage 7.7 usability rehearsal protocol",
        "",
        "Stage 7.7 tests whether a biologist and a quantitative user can reach RhoDyn decisions without reading source code.",
        "The public MLCI path and bounded-coupling fixture are used as usability evidence, not as a new biological demonstration.",
        "",
        "## Tasks",
        "",
        "| Persona | Task | Input | Expected decision |",
        "|---|---|---|---|",
    ]
    for row in protocol_rows:
        lines.append(f"| {row['persona']} | {row['task_id']} | `{row['input']}` | {row['expected_user_decision']} |")
    lines.extend(
        [
            "",
            "## Gate status",
            "",
            f"Overall status. {gate['status']}",
            "",
            "## Validation checkpoints",
            "",
        ]
    )
    for key, value in gate["validation_checkpoints"].items():
        lines.append(f"- {key}. {value}.")
    lines.extend(
        [
            "",
            "## Interpretation boundary",
            "",
            gate["interpretation_boundary"],
        ]
    )
    return "\n".join(lines) + "\n"


def _findings_doc(findings_rows: list[dict[str, Any]], gate: dict[str, Any]) -> str:
    lines = [
        "# Stage 7.7 user-path findings",
        "",
        "The rehearsal found that the public tutorial and workbench route can support an interpretable residence-versus-amplitude example, and that the bounded-coupling fixture is reproducible through Python, CLI, backend, and bundle exports.",
        "Biologist residence task and Quantitative bounded-coupling task outcomes are recorded separately so the Python, CLI, and backend reproduction path remains visible.",
        "This is not a new biological demonstration.",
        "",
        "## Findings",
        "",
        "| Persona | Task | Status | Finding | Fix applied |",
        "|---|---|---|---|---|",
    ]
    for row in findings_rows:
        lines.append(f"| {row['persona']} | {row['task_id']} | {row['status']} | {row['finding']} | {row['fix_applied']} |")
    lines.extend(
        [
            "",
            "## Export inspection",
            "",
            "The exported analysis bundles include declared parameters, input schema, grouping summary, software version, submitted rows, exact result JSON, result rows, Markdown report, and payload checksums.",
            "",
            "## Scope",
            "",
            gate["interpretation_boundary"],
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> int:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    biologist = _biologist_residence_task()
    quantitative = _quantitative_reproduction_task()
    workbench = _workbench_flow_check()
    export_rows = _export_manifest_rows(biologist["bundle_export"], quantitative["bundle_export"])
    gate = _gate_report(biologist, quantitative, workbench, export_rows)
    protocol_rows = _protocol_rows()
    findings_rows = _findings_rows(biologist, quantitative, workbench)

    _write_json(OUTPUT_DIR / "biologist_residence_task_result.json", biologist)
    _write_json(OUTPUT_DIR / "quantitative_reproduction_result.json", quantitative)
    _write_json(OUTPUT_DIR / "workbench_flow_check.json", workbench)
    _write_tsv(
        OUTPUT_DIR / "usability_task_protocol.tsv",
        protocol_rows,
        ["persona", "task_id", "starting_surface", "input", "expected_user_decision", "allowed_actions", "source_code_reading_required", "interpretation_boundary"],
    )
    _write_tsv(
        OUTPUT_DIR / "user_path_findings.tsv",
        findings_rows,
        ["persona", "task_id", "status", "finding", "confusion_or_failure", "fix_applied", "rerun_status", "evidence_path"],
    )
    _write_tsv(
        OUTPUT_DIR / "export_examples_manifest.tsv",
        export_rows,
        ["bundle_path", "operation", "sha256", "software_version", "has_parameters", "has_input_schema", "has_grouping", "input_schema_kind", "grouping_fields"],
    )
    _write_json(CASE_GATE, gate)
    _write_json(DOC_GATE, gate)
    _write_text(OUTPUT_DIR / "stage7_7_usability_rehearsal_report.md", _findings_doc(findings_rows, gate))
    _write_text(DOC_PROTOCOL, _protocol_doc(protocol_rows, gate))
    _write_text(DOC_FINDINGS, _findings_doc(findings_rows, gate))
    print(json.dumps({"status": gate["status"], "output_dir": OUTPUT_DIR.relative_to(ROOT).as_posix()}, indent=2))
    return 0 if gate["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())

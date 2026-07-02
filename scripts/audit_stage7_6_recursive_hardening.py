"""Audit Stage 7.6 reproducibility evidence for recursive consistency.

This check is intentionally independent of the Stage 7.6 runner. It reads the
committed Stage 7.6 reports and tables and verifies that the clean-room archive
manifest, regenerated-output comparison, parity table, command table, and
release interpretation boundary still agree.
"""

from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
import re
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RUNNER_PATH = ROOT / "scripts" / "run_stage7_6_methods_reproducibility.py"
STAGE7_6_DIR = ROOT / "case_studies" / "stage7_methods_reproducibility"
DOC_GATE = ROOT / "docs" / "stage7_6_gate_report.json"
DOC_CLEAN_ROOM = ROOT / "docs" / "stage7_6_clean_room_report.json"
DOC_RECURSIVE_REPORT = ROOT / "docs" / "stage7_6_recursive_hardening_report.json"
CASE_RECURSIVE_REPORT = STAGE7_6_DIR / "stage7_6_recursive_hardening_report.json"
RELEASE_CHECKSUMS = ROOT / "docs" / "release_checksums.csv"
REPORT_SURFACES = [
    "docs/stage7_6_gate_report.json",
    "docs/stage7_6_clean_room_report.json",
    "docs/stage7_methods_reproducibility_card.md",
    "docs/stage7_6_recursive_hardening_report.json",
    "case_studies/stage7_methods_reproducibility/stage7_6_methods_reproducibility_gate_report.json",
    "case_studies/stage7_methods_reproducibility/stage7_6_methods_reproducibility_report.md",
    "case_studies/stage7_methods_reproducibility/stage7_6_recursive_hardening_report.json",
    "case_studies/stage7_methods_reproducibility/methods_output_comparison.tsv",
    "case_studies/stage7_methods_reproducibility/cross_surface_parity.tsv",
    "case_studies/stage7_methods_reproducibility/methods_reproducibility_commands.tsv",
    "case_studies/stage7_methods_reproducibility/release_archive_manifest.tsv",
]
REQUIRED_STAGE7_6_CHECKSUM_FILES = set(REPORT_SURFACES) | {
    "scripts/run_stage7_6_methods_reproducibility.py",
    "scripts/audit_stage7_6_recursive_hardening.py",
    "tests/test_stage7_6_methods_reproducibility.py",
}
REQUIRED_STAGE7_6_CHECKSUM_FILES -= {
    "docs/stage7_6_recursive_hardening_report.json",
    "case_studies/stage7_methods_reproducibility/stage7_6_recursive_hardening_report.json",
}


def _load_runner() -> Any:
    spec = importlib.util.spec_from_file_location("stage7_6_runner_contract", RUNNER_PATH)
    module = importlib.util.module_from_spec(spec)
    sys.modules[str(spec.name)] = module
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


RUNNER = _load_runner()


def _display_path(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def _read_json(path: Path, failures: list[str]) -> dict[str, Any]:
    if not path.exists():
        failures.append(f"missing JSON report: {_display_path(path)}")
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        failures.append(f"invalid JSON report {_display_path(path)}: {exc}")
        return {}


def _read_tsv(path: Path, failures: list[str]) -> list[dict[str, str]]:
    if not path.exists():
        failures.append(f"missing TSV report: {_display_path(path)}")
        return []
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def _read_csv(path: Path, failures: list[str]) -> list[dict[str, str]]:
    if not path.exists():
        failures.append(f"missing CSV report: {_display_path(path)}")
        return []
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _hex64(value: str) -> bool:
    return bool(re.fullmatch(r"[0-9a-f]{64}", value))


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _scan_report_surfaces(root: Path, failures: list[str]) -> dict[str, int]:
    scanned = 0
    for rel in REPORT_SURFACES:
        path = root / rel
        if not path.exists():
            failures.append(f"missing Stage 7.6 report surface: {rel}")
            continue
        scanned += 1
        text = path.read_text(encoding="utf-8", errors="ignore")
        for pattern in RUNNER.LEAK_PATTERNS:
            if pattern.search(text):
                failures.append(f"Stage 7.6 report surface contains local path or credential-like text: {rel}")
                break
    return {"report_surfaces_scanned": scanned}


def _validate_release_checksum_coverage(root: Path, failures: list[str]) -> dict[str, int]:
    rows = _read_csv(root / RELEASE_CHECKSUMS.relative_to(ROOT), failures)
    by_path = {row.get("path", ""): row for row in rows}
    missing = sorted(REQUIRED_STAGE7_6_CHECKSUM_FILES - set(by_path))
    if missing:
        failures.append(f"release checksum table does not cover Stage 7.6 files: {missing}")
    stale: list[str] = []
    for rel in sorted(REQUIRED_STAGE7_6_CHECKSUM_FILES & set(by_path)):
        path = root / rel
        if not path.exists():
            failures.append(f"checksum table references missing Stage 7.6 file: {rel}")
            continue
        if by_path[rel].get("sha256") != _sha256(path):
            stale.append(rel)
    if stale:
        failures.append(f"release checksum table has stale Stage 7.6 hashes: {stale}")
    return {"release_checksum_rows": len(rows), "required_stage7_6_checksum_files": len(REQUIRED_STAGE7_6_CHECKSUM_FILES)}


def audit_stage7_6_recursive_hardening(root: Path = ROOT) -> dict[str, object]:
    failures: list[str] = []
    warnings: list[str] = []

    doc_gate = _read_json(root / DOC_GATE.relative_to(ROOT), failures)
    clean_room = _read_json(root / DOC_CLEAN_ROOM.relative_to(ROOT), failures)
    case_gate = _read_json(root / "case_studies/stage7_methods_reproducibility/stage7_6_methods_reproducibility_gate_report.json", failures)
    comparison_rows = _read_tsv(root / "case_studies/stage7_methods_reproducibility/methods_output_comparison.tsv", failures)
    parity_rows = _read_tsv(root / "case_studies/stage7_methods_reproducibility/cross_surface_parity.tsv", failures)
    command_rows = _read_tsv(root / "case_studies/stage7_methods_reproducibility/methods_reproducibility_commands.tsv", failures)
    manifest_rows = _read_tsv(root / "case_studies/stage7_methods_reproducibility/release_archive_manifest.tsv", failures)
    scan_counts = _scan_report_surfaces(root, failures)
    checksum_counts = _validate_release_checksum_coverage(root, failures)

    if doc_gate and clean_room and doc_gate != clean_room:
        failures.append("docs/stage7_6_gate_report.json and docs/stage7_6_clean_room_report.json are not identical")
    if doc_gate and case_gate and doc_gate != case_gate:
        failures.append("docs and case-study Stage 7.6 gate reports are not identical")

    if doc_gate:
        if doc_gate.get("status") != "pass":
            failures.append("Stage 7.6 gate status is not pass")
        if doc_gate.get("mode") != "full_release_archive":
            failures.append("Stage 7.6 gate was not generated in full_release_archive mode")
        if doc_gate.get("completion_state") != "complete_methods_reproducibility_hardening":
            failures.append("Stage 7.6 gate does not record the completed hardening state")
        boundary = str(doc_gate.get("interpretation_boundary", ""))
        if "does not add biological evidence" not in boundary:
            failures.append("Stage 7.6 interpretation boundary no longer preserves the no-new-biological-evidence scope")
        checkpoints = doc_gate.get("validation_checkpoints", {}) if isinstance(doc_gate.get("validation_checkpoints"), dict) else {}
        for key, value in checkpoints.items():
            if key.startswith("stop_condition_"):
                if value != "not_triggered":
                    failures.append(f"Stage 7.6 stop condition is triggered: {key}")
            elif value != "pass":
                failures.append(f"Stage 7.6 validation checkpoint is not pass: {key}={value}")
        workflow_checks = doc_gate.get("workflow_checks", {}) if isinstance(doc_gate.get("workflow_checks"), dict) else {}
        for key, value in workflow_checks.items():
            if value != "pass":
                failures.append(f"Stage 7.6 workflow check is not pass: {key}={value}")
        if doc_gate.get("step_failures"):
            failures.append("Stage 7.6 gate records step failures")
        if doc_gate.get("workflow_failures"):
            failures.append("Stage 7.6 gate records workflow failures")
        dist_files = doc_gate.get("dist_files", []) if isinstance(doc_gate.get("dist_files"), list) else []
        dist_names = {str(item.get("name", "")) for item in dist_files if isinstance(item, dict)}
        if not any(name.endswith(".tar.gz") for name in dist_names):
            failures.append("Stage 7.6 gate does not record a source distribution")
        if not any(name.endswith(".whl") for name in dist_names):
            failures.append("Stage 7.6 gate does not record a wheel distribution")
        for item in dist_files:
            if not isinstance(item, dict):
                continue
            if int(item.get("size_bytes", 0) or 0) <= 0 or not _hex64(str(item.get("sha256", ""))):
                failures.append(f"Stage 7.6 distribution file has incomplete size/hash metadata: {item.get('name')}")
        distribution_summary = doc_gate.get("distribution_member_summary", {})
        if not isinstance(distribution_summary, dict):
            failures.append("Stage 7.6 gate lacks distribution_member_summary")
            distribution_summary = {}
        if distribution_summary.get("sdist_status") != "pass":
            failures.append("Stage 7.6 source distribution member summary does not pass")
        if distribution_summary.get("sdist_missing_required_files"):
            failures.append("Stage 7.6 source distribution is missing required files")
        if distribution_summary.get("sdist_missing_deterministic_outputs"):
            failures.append("Stage 7.6 source distribution is missing deterministic evidence outputs")

    expected_outputs = list(getattr(RUNNER, "DETERMINISTIC_OUTPUTS", []))
    comparison_paths = [row.get("path", "") for row in comparison_rows]
    if comparison_paths != expected_outputs:
        failures.append("methods_output_comparison.tsv does not preserve the runner deterministic-output order")
    if doc_gate:
        summary = doc_gate.get("comparison_summary", {}) if isinstance(doc_gate.get("comparison_summary"), dict) else {}
        if summary.get("checked_outputs") != len(comparison_rows):
            failures.append("comparison_summary checked output count does not match TSV row count")
        if summary.get("matched_outputs") != sum(row.get("matches") == "1" for row in comparison_rows):
            failures.append("comparison_summary matched output count does not match TSV")
    for row in comparison_rows:
        if row.get("reference_exists") != "1" or row.get("clean_room_exists") != "1" or row.get("matches") != "1":
            failures.append(f"Stage 7.6 deterministic output is not fully reproduced: {row.get('path')}")
        if not _hex64(row.get("reference_sha256", "")) or not _hex64(row.get("clean_room_sha256", "")):
            failures.append(f"Stage 7.6 deterministic output lacks full hashes: {row.get('path')}")

    expected_operations = ["score_residence", "decide_coupling", "summarize_reserve", "compare_models"]
    if [row.get("operation") for row in parity_rows] != expected_operations:
        failures.append("cross_surface_parity.tsv does not preserve the expected operation order")
    if doc_gate:
        parity_summary = doc_gate.get("parity_summary", {}) if isinstance(doc_gate.get("parity_summary"), dict) else {}
        if parity_summary.get("checked_operations") != len(parity_rows):
            failures.append("parity_summary checked operation count does not match TSV row count")
        if parity_summary.get("matching_operations") != sum(row.get("passes") == "1" for row in parity_rows):
            failures.append("parity_summary matching operation count does not match TSV")
    for row in parity_rows:
        if row.get("passes") != "1":
            failures.append(f"cross-surface parity does not pass for {row.get('operation')}")
        for field in ["python_value", "cli_value", "backend_value"]:
            try:
                json.loads(row.get(field, ""))
            except json.JSONDecodeError:
                failures.append(f"parity row has non-JSON {field} for {row.get('operation')}")
        if row.get("frontend_status") != "fixture_contract_checked":
            failures.append(f"frontend contract status is not recorded for {row.get('operation')}")

    expected_phases = [phase for phase, _ in getattr(RUNNER, "STAGE_REPRO_COMMANDS", [])] + ["docs", "surface parity"]
    if [row.get("phase") for row in command_rows] != expected_phases:
        failures.append("methods_reproducibility_commands.tsv does not preserve Stage 7.1 through Stage 7.5 command order")
    for row in command_rows:
        if row.get("mode") != "full_release_archive":
            failures.append(f"reproducibility command is not marked full_release_archive: {row.get('phase')}")
        if not row.get("command") or not row.get("purpose"):
            failures.append(f"reproducibility command lacks command or purpose: {row.get('phase')}")

    if doc_gate:
        manifest_summary = doc_gate.get("release_archive_manifest_summary", {})
        if not isinstance(manifest_summary, dict):
            failures.append("Stage 7.6 gate lacks release_archive_manifest_summary")
            manifest_summary = {}
        if manifest_summary.get("manifest_status") != "pass":
            failures.append("release archive manifest summary does not pass")
        if manifest_summary.get("file_count") != len(manifest_rows):
            failures.append("release archive manifest file count does not match TSV")
        if manifest_summary.get("raw_private_like_file_count") != 0:
            failures.append("release archive manifest contains raw/private-like files")
        if manifest_summary.get("missing_required_files"):
            failures.append("release archive manifest is missing required files")
        if manifest_summary.get("missing_deterministic_outputs"):
            failures.append("release archive manifest is missing deterministic evidence outputs")
        if manifest_summary.get("deterministic_output_file_count") != len(getattr(RUNNER, "DETERMINISTIC_OUTPUTS", [])):
            failures.append("release archive manifest does not count every selected deterministic output")
    for row in manifest_rows:
        if not row.get("path") or int(row.get("size_bytes", "0") or 0) <= 0 or not _hex64(row.get("sha256", "")):
            failures.append(f"release archive manifest row is incomplete: {row.get('path')}")
        if row.get("content_class") == "raw_private_like":
            failures.append(f"release archive manifest includes raw/private-like file: {row.get('path')}")
    manifest_paths = {row.get("path", "") for row in manifest_rows}
    missing_manifest_outputs = sorted(set(getattr(RUNNER, "DETERMINISTIC_OUTPUTS", [])) - manifest_paths)
    if missing_manifest_outputs:
        failures.append(f"release archive manifest lacks deterministic outputs: {missing_manifest_outputs}")

    report = {
        "report_format": "rhodyn.stage7_6_recursive_hardening.v1",
        "status": "pass" if not failures else "fail",
        "completion_state": "stage7_6_recursive_hardened" if not failures else "stage7_6_recursive_hardening_failed",
        "checks": {
            "gate_reports_identical": "pass" if doc_gate == clean_room == case_gate and doc_gate else "fail",
            "full_archive_mode": "pass" if doc_gate.get("mode") == "full_release_archive" else "fail",
            "deterministic_outputs_match": "pass" if comparison_rows and all(row.get("matches") == "1" for row in comparison_rows) else "fail",
            "cross_surface_parity_matches": "pass" if parity_rows and all(row.get("passes") == "1" for row in parity_rows) else "fail",
            "archive_manifest_complete": "pass" if doc_gate.get("release_archive_manifest_summary", {}).get("manifest_status") == "pass" else "fail",
            "workflow_checks_pass": "pass" if doc_gate and all(value == "pass" for value in doc_gate.get("workflow_checks", {}).values()) else "fail",
            "scope_boundary_preserved": "pass" if "does not add biological evidence" in str(doc_gate.get("interpretation_boundary", "")) else "fail",
            "deterministic_outputs_in_archive_manifest": "pass" if not missing_manifest_outputs else "fail",
            "source_distribution_members_complete": "pass" if doc_gate.get("distribution_member_summary", {}).get("sdist_status") == "pass" else "fail",
            "release_checksums_cover_stage7_6": "pass" if not any("checksum" in item for item in failures) else "fail",
            "report_surfaces_sanitized": "pass" if not any("local path or credential-like" in item for item in failures) else "fail",
        },
        "counts": {
            "comparison_rows": len(comparison_rows),
            "parity_rows": len(parity_rows),
            "command_rows": len(command_rows),
            "archive_manifest_rows": len(manifest_rows),
            **scan_counts,
            **checksum_counts,
        },
        "failures": failures,
        "warnings": warnings,
        "interpretation_boundary": (
            "This audit hardens Stage 7.6 software reproducibility evidence. "
            "It does not add biological evidence or change any method decision rule."
        ),
    }
    return report


def main() -> int:
    report = audit_stage7_6_recursive_hardening()
    for path in [DOC_RECURSIVE_REPORT, CASE_RECURSIVE_REPORT]:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "failures": report["failures"][:5]}, indent=2))
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())

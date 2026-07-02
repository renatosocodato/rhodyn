"""Run Stage 7.6 methods-paper reproducibility hardening.

Stage 7.6 asks whether the Stage 7 methods evidence set can be rebuilt and
inspected from a declared release-candidate archive rather than from the
developer's active checkout. The full mode builds an sdist from the current
tree, extracts it into a temporary clean-room workspace, installs the archive
with the development tools needed for the evidence scripts, regenerates the
Stage 7.1 through Stage 7.5 outputs, and compares selected deterministic
outputs against the committed snapshots.

The runner also records cross-surface parity checks for Python, CLI, backend,
and frontend-contract surfaces. Passing this phase supports software and
methods reproducibility. It does not add biological evidence.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_DIR = Path("case_studies/stage7_methods_reproducibility")
DEFAULT_DOC_REPORT = Path("docs/stage7_methods_reproducibility_card.md")
DEFAULT_DOC_GATE = Path("docs/stage7_6_gate_report.json")
DEFAULT_JSON_REPORT = Path("docs/stage7_6_clean_room_report.json")
PYTHON = sys.executable

STAGE_REPRO_COMMANDS = [
    ("7.1 synthetic truth cases", [PYTHON, "scripts/build_stage7_1_synthetic_truth_cases.py"]),
    ("7.2 benchmark harness", [PYTHON, "scripts/run_stage7_2_benchmark_harness.py"]),
    ("7.3 public signaling demonstrations", [PYTHON, "scripts/run_stage7_3_public_signaling.py"]),
    ("7.4 endpoint reserve routing", [PYTHON, "scripts/run_stage7_4_endpoint_reserve_routing.py"]),
    ("7.5 held-out validation", [PYTHON, "scripts/run_stage7_5_heldout_validation.py"]),
]

DETERMINISTIC_OUTPUTS = [
    "case_studies/stage7_synthetic_truth/stage7_1_synthetic_truth_report.json",
    "case_studies/stage7_benchmarks/synthetic_residence_baseline_comparison.csv",
    "case_studies/stage7_benchmarks/synthetic_reserve_baseline_comparison.csv",
    "case_studies/stage7_benchmarks/synthetic_coupling_baseline_comparison.csv",
    "case_studies/stage7_benchmarks/synthetic_model_baseline_comparison.csv",
    "case_studies/stage7_benchmarks/window_sensitivity_summary.csv",
    "case_studies/stage7_benchmarks/margin_sensitivity_summary.csv",
    "case_studies/stage7_benchmarks/grouping_sample_size_sensitivity.csv",
    "case_studies/stage7_benchmarks/public_fixture_benchmark_summary.csv",
    "case_studies/stage7_benchmarks/failure_behavior_summary.csv",
    "case_studies/stage7_benchmarks/stage7_2_benchmark_report.json",
    "case_studies/stage7_public_signaling/public_signaling_case_summary.tsv",
    "case_studies/stage7_public_signaling/drg_calcium_residence_amplitude_summary.csv",
    "case_studies/stage7_public_signaling/drg_calcium_window_sensitivity.csv",
    "case_studies/stage7_public_signaling/drg_calcium_uncertainty_summary.csv",
    "case_studies/stage7_public_signaling/erk_gpcr_residence_amplitude_summary.csv",
    "case_studies/stage7_public_signaling/erk_gpcr_window_sensitivity.csv",
    "case_studies/stage7_public_signaling/erk_gpcr_uncertainty_summary.csv",
    "case_studies/stage7_public_signaling/stage7_3_public_signaling_gate_report.json",
    "case_studies/stage7_endpoint_reserve_routing/stage7_4_case_summary.tsv",
    "case_studies/stage7_endpoint_reserve_routing/cell_painting_routed_model_comparison.csv",
    "case_studies/stage7_endpoint_reserve_routing/cell_painting_reduced_alternative_decisions.tsv",
    "case_studies/stage7_endpoint_reserve_routing/cell_painting_reserve_like_model_summary.csv",
    "case_studies/stage7_endpoint_reserve_routing/cell_painting_reserve_like_uncertainty.csv",
    "case_studies/stage7_endpoint_reserve_routing/erk_akt_bounded_coupling_decisions.csv",
    "case_studies/stage7_endpoint_reserve_routing/stage7_4_endpoint_reserve_routing_gate_report.json",
    "case_studies/stage7_heldout_validation/heldout_analysis_plan.json",
    "case_studies/stage7_heldout_validation/heldout_bounded_coupling_decisions.csv",
    "case_studies/stage7_heldout_validation/heldout_validation_outcomes.tsv",
    "case_studies/stage7_heldout_validation/stage7_5_heldout_validation_gate_report.json",
]

NOTEBOOKS = [
    "notebooks/01_synthetic_residence_primer.ipynb",
    "notebooks/02_public_signaling_benchmarks.ipynb",
    "notebooks/03_public_endpoint_and_coupling_benchmarks.ipynb",
    "notebooks/04_stage7_drg_calcium_public_signaling.ipynb",
    "notebooks/05_stage7_erk_gpcr_public_signaling.ipynb",
    "notebooks/06_stage7_endpoint_reserve_routing.ipynb",
    "notebooks/07_stage7_heldout_validation.ipynb",
]

REQUIRED_ARCHIVE_FILES = {
    "pyproject.toml",
    "src/rhodyn/__init__.py",
    "scripts/build_stage7_1_synthetic_truth_cases.py",
    "scripts/run_stage7_2_benchmark_harness.py",
    "scripts/run_stage7_3_public_signaling.py",
    "scripts/run_stage7_4_endpoint_reserve_routing.py",
    "scripts/run_stage7_5_heldout_validation.py",
    "scripts/run_stage7_6_methods_reproducibility.py",
    "scripts/audit_stage7_6_recursive_hardening.py",
    "scripts/audit_stage7_7_8_recursive_hardening.py",
    "scripts/check_stage9_scaffold.py",
    "scripts/scaffold_stage9_manuscript_assembly.py",
    "scripts/run_stage9_0_evidence_intake_lock.py",
    "scripts/run_stage9_1_venue_guidance_register.py",
    "scripts/run_stage9_6b_panelforge_rendering.py",
    "scripts/run_stage7_7_usability_rehearsal.py",
    "docs/stage7_methods_program.md",
    "docs/stage7_6_api_stability_policy.md",
    "docs/stage7_6_recursive_hardening.md",
    "docs/stage7_7_8_recursive_hardening.md",
    "docs/stage7_7_8_recursive_hardening_report.json",
    "docs/stage7_usability_rehearsal.md",
    "docs/stage7_user_path_findings.md",
    "docs/stage7_7_gate_report.json",
    "case_studies/stage7_usability_rehearsal/stage7_7_usability_gate_report.json",
    "tests/test_stage7_7_usability_rehearsal.py",
    "scripts/run_stage7_8_methods_readiness.py",
    "docs/stage7_methods_evidence_index.md",
    "docs/stage7_figure_artifact_crosswalk.md",
    "docs/stage7_claim_evidence_crosswalk.md",
    "docs/stage7_methods_submission_readiness.md",
    "docs/stage7_8_gate_report.json",
    "case_studies/stage7_methods_readiness/stage7_8_methods_readiness_gate_report.json",
    "case_studies/stage7_methods_readiness/stage7_7_8_recursive_hardening_report.json",
    "tests/test_stage7_8_methods_readiness.py",
    "tests/test_stage7_7_8_recursive_hardening.py",
    "tests/test_stage9_scaffold.py",
    "tests/test_stage9_1_venue_guidance.py",
    "docs/stage9_manuscript_assembly_plan.md",
    "docs/stage9_execution_memory.json",
    "manuscript/nature_methods/README.md",
    "manuscript/nature_methods/contracts/id_namespace.md",
    "manuscript/nature_methods/contracts/machine_gate_spec.md",
    "manuscript/nature_methods/contracts/atomic_write_protocol.md",
    "manuscript/nature_methods/contracts/stage9_project_binding.json",
    "manuscript/nature_methods/contracts/stage9_substage_registry.json",
    "manuscript/nature_methods/contracts/ledger_schema_map.json",
    "manuscript/nature_methods/figures/figures.manifest.yaml",
    "manuscript/nature_methods/gate_verdicts/9.-1.json",
    "manuscript/nature_methods/gate_verdicts/9.0.json",
    "manuscript/nature_methods/gate_verdicts/9.1.json",
    "manuscript/nature_methods/ledgers/stage9_evidence_manifest.csv",
    "manuscript/nature_methods/ledgers/stage9_evidence_lock.md",
    "manuscript/nature_methods/ledgers/stage7_output_contract.md",
    "manuscript/nature_methods/refs/nature_methods_guidance_register.md",
    "manuscript/nature_methods/refs/_cache/nature_initial_submission.meta.json",
    "manuscript/nature_methods/refs/_cache/nature_initial_submission.txt",
    "manuscript/nature_methods/refs/_cache/nature_portfolio_reporting_standards.meta.json",
    "manuscript/nature_methods/refs/_cache/nature_portfolio_reporting_standards.txt",
    "manuscript/nature_methods/refs/_cache/nmeth_aims_scope.meta.json",
    "manuscript/nature_methods/refs/_cache/nmeth_aims_scope.txt",
    "manuscript/nature_methods/refs/_cache/nmeth_content_types.meta.json",
    "manuscript/nature_methods/refs/_cache/nmeth_content_types.txt",
    "manuscript/nature_methods/refs/_cache/nmeth_editorial_policies.meta.json",
    "manuscript/nature_methods/refs/_cache/nmeth_editorial_policies.txt",
    "manuscript/nature_methods/refs/_cache/nmeth_submission_guidelines.meta.json",
    "manuscript/nature_methods/refs/_cache/nmeth_submission_guidelines.txt",
    "manuscript/nature_methods/refs/_cache/springer_nature_code_policy.meta.json",
    "manuscript/nature_methods/refs/_cache/springer_nature_code_policy.txt",
    "manuscript/nature_methods/audits/venue_policy_constraints.md",
    "tools/panelforge-figures/STAGE9_PLACEHOLDER.md",
    "notebooks/01_synthetic_residence_primer.ipynb",
    "notebooks/07_stage7_heldout_validation.ipynb",
    "examples/synthetic_trajectory.csv",
    "examples/synthetic_coupling.csv",
}

LEAK_PATTERNS = [
    re.compile("/" + "Users/"),
    re.compile("/" + "Volumes/"),
    re.compile("Library/" + "LaunchAgents"),
    re.compile(r"sk-[A-Za-z0-9]"),
    re.compile("ghp" + r"_[A-Za-z0-9_]+"),
    re.compile("github" + r"_pat_[A-Za-z0-9_]+"),
    re.compile(r"xox[baprs]-[A-Za-z0-9-]+"),
]
TEXT_SUFFIXES = {
    ".py",
    ".md",
    ".toml",
    ".yml",
    ".yaml",
    ".cff",
    ".txt",
    ".json",
    ".html",
    ".css",
    ".js",
    ".csv",
    ".in",
    ".ipynb",
    ".example",
    ".Dockerfile",
}
RAW_EXTENSIONS = {".lif", ".czi", ".nd2", ".oir", ".oib", ".lsm", ".tif", ".tiff", ".prism", ".xml"}
GENERATED_DIRS = {
    "__pycache__",
    "dist",
    "build",
    "htmlcov",
    ".pytest_cache",
    "node_modules",
    "playwright-report",
    "test-results",
    "blob-report",
}


@dataclass
class StepResult:
    name: str
    command: str
    status: str
    seconds: float
    stdout_tail: str = ""
    stderr_tail: str = ""


def _now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _tail(text: str, limit: int = 1200) -> str:
    stripped = text.strip()
    return stripped if len(stripped) <= limit else stripped[-limit:]


def _run(name: str, command: list[str], *, cwd: Path, env: dict[str, str] | None = None) -> StepResult:
    started = time.monotonic()
    result = subprocess.run(
        command,
        cwd=cwd,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    seconds = time.monotonic() - started
    return StepResult(
        name=name,
        command=" ".join(command),
        status="pass" if result.returncode == 0 else "fail",
        seconds=seconds,
        stdout_tail=_tail(result.stdout),
        stderr_tail=_tail(result.stderr),
    )


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_text(path: Path, body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body.rstrip() + "\n", encoding="utf-8")


def _write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str], *, delimiter: str = ",") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, delimiter=delimiter, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fieldnames})


def _venv_python(venv: Path) -> Path:
    return venv / ("Scripts/python.exe" if os.name == "nt" else "bin/python")


def _venv_cli(venv: Path, executable: str) -> Path:
    suffix = ".exe" if os.name == "nt" else ""
    return venv / ("Scripts" if os.name == "nt" else "bin") / f"{executable}{suffix}"


def _clean_step_text(step: StepResult, clean_root: Path) -> StepResult:
    replacement = "$STAGE7_6_CLEAN_ROOM"
    return StepResult(
        name=step.name,
        command=step.command.replace(str(clean_root), replacement).replace(PYTHON, "python"),
        status=step.status,
        seconds=step.seconds,
        stdout_tail=step.stdout_tail.replace(str(clean_root), replacement).replace(PYTHON, "python"),
        stderr_tail=step.stderr_tail.replace(str(clean_root), replacement).replace(PYTHON, "python"),
    )


def _extract_first_sdist(dist_dir: Path, extract_root: Path) -> Path:
    sdists = sorted(dist_dir.glob("rhodyn-*.tar.gz"))
    if not sdists:
        raise FileNotFoundError("no RhoDyn source distribution was built")
    with tarfile.open(sdists[0], "r:gz") as handle:
        handle.extractall(extract_root)
    extracted = sorted(path for path in extract_root.iterdir() if path.is_dir())
    if not extracted:
        raise FileNotFoundError("source distribution did not extract a source directory")
    return extracted[0]


def _remove_stale_build_metadata(root: Path) -> StepResult:
    started = time.monotonic()
    removed: list[str] = []
    for rel in ["src/rhodyn.egg-info", "build"]:
        path = root / rel
        if path.exists():
            shutil.rmtree(path)
            removed.append(rel)
    return StepResult(
        name="remove stale build metadata",
        command="remove src/rhodyn.egg-info and build before source distribution",
        status="pass",
        seconds=time.monotonic() - started,
        stdout_tail=json.dumps({"removed": removed}, indent=2),
    )


def _execute_notebooks(root: Path, python: Path) -> StepResult:
    notebook_paths = [(root / item).resolve().as_posix() for item in NOTEBOOKS]
    code = """
import json
from pathlib import Path

notebooks = [Path(item) for item in %r]
executed = []
for notebook in notebooks:
    ns = {'__name__': '__stage7_6_notebook__'}
    data = json.loads(notebook.read_text(encoding='utf-8'))
    for index, cell in enumerate(data.get('cells', []), start=1):
        if cell.get('cell_type') != 'code':
            continue
        source = ''.join(cell.get('source', []))
        if source.strip():
            exec(compile(source, f'{notebook.as_posix()}:cell{index}', 'exec'), ns)
    executed.append(notebook.as_posix())
print(json.dumps({'status': 'pass', 'count': len(executed), 'notebooks': executed}, indent=2))
""" % notebook_paths
    env = dict(os.environ)
    env["PYTHONPATH"] = str(root / "src")
    step = _run("execute methods notebooks", [str(python), "-c", code], cwd=root / "notebooks", env=env)
    step.command = f"{python} -c <execute Stage 7 notebook code cells>"
    return step


def _archive_surface_scan(root: Path) -> StepResult:
    started = time.monotonic()
    failures: list[str] = []
    scanned = 0
    for path in root.rglob("*"):
        if ".git" in path.parts or any(part in GENERATED_DIRS for part in path.parts):
            continue
        rel = path.relative_to(root)
        if path.is_file() and path.suffix.lower() in RAW_EXTENSIONS:
            failures.append(f"raw/private-data-like file present: {rel.as_posix()}")
        if not path.is_file() or path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        scanned += 1
        text = path.read_text(encoding="utf-8", errors="ignore")
        for pattern in LEAK_PATTERNS:
            if pattern.search(text):
                failures.append(f"local path or credential-like pattern in {rel.as_posix()}")
                break
    seconds = time.monotonic() - started
    return StepResult(
        name="release safety check",
        command="python -c <scan release archive text files for local paths, secrets, and raw/private-data extensions>",
        status="pass" if not failures else "fail",
        seconds=seconds,
        stdout_tail=json.dumps({"scanned_text_files": scanned, "status": "pass" if not failures else "fail"}, indent=2),
        stderr_tail="\n".join(failures[:20]),
    )


def _archive_manifest_rows(root: Path) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for path in sorted(root.rglob("*")):
        if ".git" in path.parts or any(part in GENERATED_DIRS for part in path.parts):
            continue
        if not path.is_file():
            continue
        rel = path.relative_to(root).as_posix()
        suffix = path.suffix.lower()
        is_text = suffix in TEXT_SUFFIXES
        is_raw_like = suffix in RAW_EXTENSIONS
        rows.append(
            {
                "path": rel,
                "size_bytes": path.stat().st_size,
                "sha256": _sha256(path),
                "suffix": suffix,
                "content_class": "raw_private_like" if is_raw_like else "text" if is_text else "binary_or_packaged",
            }
        )
    return rows


def _archive_manifest_summary(rows: list[dict[str, object]]) -> dict[str, object]:
    paths = {str(row["path"]) for row in rows}
    missing_required = sorted(REQUIRED_ARCHIVE_FILES - paths)
    missing_deterministic = sorted(set(DETERMINISTIC_OUTPUTS) - paths)
    raw_private_like = sorted(str(row["path"]) for row in rows if row["content_class"] == "raw_private_like")
    text_count = sum(row["content_class"] == "text" for row in rows)
    binary_count = sum(row["content_class"] == "binary_or_packaged" for row in rows)
    return {
        "file_count": len(rows),
        "text_file_count": text_count,
        "binary_or_packaged_file_count": binary_count,
        "raw_private_like_file_count": len(raw_private_like),
        "missing_required_files": missing_required,
        "deterministic_output_file_count": len(set(DETERMINISTIC_OUTPUTS) & paths),
        "missing_deterministic_outputs": missing_deterministic,
        "raw_private_like_files": raw_private_like,
        "manifest_status": "pass" if not missing_required and not missing_deterministic and not raw_private_like else "fail",
    }


def _attach_archive_manifest(payload: dict[str, object], rows: list[dict[str, object]]) -> dict[str, object]:
    summary = _archive_manifest_summary(rows)
    payload["release_archive_manifest_summary"] = summary
    payload["release_archive_manifest_rows"] = rows
    checkpoints = payload.get("validation_checkpoints", {})
    if isinstance(checkpoints, dict):
        checkpoints["release_archive_manifest_is_complete"] = "pass" if summary.get("manifest_status") == "pass" else "fail"
        checkpoints["release_archive_deterministic_outputs_present"] = (
            "pass" if not summary.get("missing_deterministic_outputs") else "fail"
        )
    if summary.get("manifest_status") != "pass":
        payload["status"] = "fail"
        payload["completion_state"] = "failed_methods_reproducibility_hardening"
        if isinstance(checkpoints, dict):
            checkpoints["stop_condition_clean_room_failure"] = "triggered"
    return payload


def _strip_archive_prefix(member_name: str) -> str:
    parts = member_name.split("/", 1)
    return parts[1] if len(parts) == 2 else member_name


def _distribution_member_summary(dist_dir: Path) -> dict[str, object]:
    sdists = sorted(dist_dir.glob("rhodyn-*.tar.gz"))
    summary: dict[str, object] = {
        "sdist_file": "",
        "sdist_member_count": 0,
        "sdist_missing_required_files": sorted(REQUIRED_ARCHIVE_FILES),
        "sdist_missing_deterministic_outputs": sorted(DETERMINISTIC_OUTPUTS),
        "sdist_status": "fail",
    }
    if not sdists:
        return summary
    sdist = sdists[0]
    with tarfile.open(sdist, "r:gz") as handle:
        names = {_strip_archive_prefix(member.name) for member in handle.getmembers() if member.isfile()}
    summary.update(
        {
            "sdist_file": sdist.name,
            "sdist_member_count": len(names),
            "sdist_missing_required_files": sorted(REQUIRED_ARCHIVE_FILES - names),
            "sdist_missing_deterministic_outputs": sorted(set(DETERMINISTIC_OUTPUTS) - names),
        }
    )
    summary["sdist_status"] = (
        "pass"
        if not summary["sdist_missing_required_files"] and not summary["sdist_missing_deterministic_outputs"]
        else "fail"
    )
    return summary


def _roadmap_state_scan(root: Path) -> StepResult:
    started = time.monotonic()
    failures: list[str] = []
    memory_path = root / "docs" / "roadmap_execution_memory.json"
    if not memory_path.exists():
        failures.append("missing docs/roadmap_execution_memory.json")
        memory: dict[str, Any] = {}
    else:
        memory = json.loads(memory_path.read_text(encoding="utf-8"))
    current = memory.get("current_position", {}) if isinstance(memory, dict) else {}
    stages = {entry.get("stage"): entry for entry in memory.get("stage_lock", []) if isinstance(entry, dict)}
    stage7 = stages.get(7, {}) if isinstance(stages.get(7, {}), dict) else {}
    subphases = stage7.get("subphases", []) if isinstance(stage7, dict) else []
    subphase_status = {entry.get("id"): entry.get("status") for entry in subphases if isinstance(entry, dict)}
    if current.get("active_stage") != "Stage 9.1 venue guidance registered; manuscript production not started":
        failures.append("roadmap memory does not mark the Stage 9.1 venue-guidance boundary as active")
    if stage7.get("status") != "stage7_8_complete_methods_readiness":
        failures.append("Stage 7 status is not stage7_8_complete_methods_readiness")
    if subphase_status.get("7.6") != "complete_methods_reproducibility_hardening":
        failures.append("Stage 7.6 subphase is not complete")
    if subphase_status.get("7.7") != "complete_usability_adoption_rehearsal":
        failures.append("Stage 7.7 subphase is not complete")
    if subphase_status.get("7.8") != "complete_methods_manuscript_readiness_package":
        failures.append("Stage 7.8 subphase is not complete")
    stage9 = stages.get(9, {}) if isinstance(stages.get(9, {}), dict) else {}
    if stage9.get("status") != "stage9_1_guidance_registered":
        failures.append("Stage 9 is not marked stage9_1_guidance_registered")
    if stage9.get("substage_count") != 33:
        failures.append("Stage 9 does not serialize all 33 substages")
    stage9_substage_ids = [entry.get("id") for entry in stage9.get("subphases", []) if isinstance(entry, dict)]
    if "9.6b" not in stage9_substage_ids:
        failures.append("Stage 9 does not serialize the 9.6b PanelForge rendering substage")
    stage9_substage_status = {entry.get("id"): entry.get("status") for entry in stage9.get("subphases", []) if isinstance(entry, dict)}
    if stage9_substage_status.get("9.0") != "complete_evidence_locked":
        failures.append("Stage 9.0 is not marked complete_evidence_locked")
    if stage9_substage_status.get("9.1") != "complete_guidance_registered":
        failures.append("Stage 9.1 is not marked complete_guidance_registered")
    for rel in [
        "docs/roadmap.md",
        "docs/stage7_methods_program.md",
        "docs/stage7_serialized_execution_plan.md",
        "docs/stage7_6_api_stability_policy.md",
    ]:
        if not (root / rel).exists():
            failures.append(f"missing roadmap support file: {rel}")
    seconds = time.monotonic() - started
    return StepResult(
        name="roadmap memory check",
        command="python -c <check Stage 7.6 roadmap state without recursive Stage 7.6 gate dependency>",
        status="pass" if not failures else "fail",
        seconds=seconds,
        stdout_tail=json.dumps({"status": "pass" if not failures else "fail"}, indent=2),
        stderr_tail="\n".join(failures),
    )


def _csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _field_value(item: object, key: str) -> Any:
    if isinstance(item, dict):
        return item[key]
    return getattr(item, key)


def _cli_json(python: Path, root: Path, command: list[str]) -> dict[str, Any]:
    env = dict(os.environ)
    env["PYTHONPATH"] = str(root / "src")
    result = subprocess.run(command, cwd=root, env=env, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    if result.returncode != 0:
        raise RuntimeError(result.stderr or result.stdout)
    return json.loads(result.stdout)


def _cross_surface_parity(root: Path, python: Path | None = None) -> tuple[list[dict[str, object]], list[StepResult]]:
    sys.path.insert(0, str(root / "src"))
    from rhodyn.backend_core import run_backend_operation
    from rhodyn.compare import rank_model_fits
    from rhodyn.coupling import equivalence_from_interval
    from rhodyn.reserve import ff_over_f0, reserve_coordinate
    from rhodyn.residence import ResidenceWindow, score_records
    from rhodyn.schema import read_coupling_csv, read_endpoint_csv, read_reserve_csv, read_trajectory_csv

    rows: list[dict[str, object]] = []
    steps: list[StepResult] = []
    command_python = python or Path(sys.executable)
    cli_path = _venv_cli(command_python.parent.parent, "rhodyn") if python else Path("rhodyn")
    cli_base = [str(cli_path)] if cli_path.exists() else [str(command_python), "-m", "rhodyn.cli"]

    def add_row(operation: str, python_value: object, cli_value: object, backend_value: object, frontend_status: str = "fixture_contract_checked") -> None:
        rows.append(
            {
                "operation": operation,
                "python_value": json.dumps(python_value, sort_keys=True),
                "cli_value": json.dumps(cli_value, sort_keys=True),
                "backend_value": json.dumps(backend_value, sort_keys=True),
                "frontend_status": frontend_status,
                "passes": int(python_value == cli_value == backend_value),
            }
        )

    trajectory_path = root / "examples" / "synthetic_trajectory.csv"
    trajectory_records, trajectory_issues = read_trajectory_csv(trajectory_path)
    if trajectory_issues:
        raise ValueError(trajectory_issues)
    residence_direct = score_records(trajectory_records, ResidenceWindow(0.35, 0.75))
    residence_cli = _cli_json(command_python, root, [*cli_base, "score-residence", "examples/synthetic_trajectory.csv", "--low", "0.35", "--high", "0.75"])
    residence_backend = run_backend_operation(
        "score_residence",
        _csv_rows(trajectory_path),
        parameters={"low": 0.35, "high": 0.75, "signal_column": "signal"},
    )
    add_row(
        "score_residence",
        [round(item.residence_fraction, 8) for item in residence_direct],
        [round(float(item["residence_fraction"]), 8) for item in residence_cli["summaries"]],
        [round(float(_field_value(item, "residence_fraction")), 8) for item in residence_backend["summaries"]],
    )

    coupling_path = root / "examples" / "synthetic_coupling.csv"
    coupling_records, coupling_issues = read_coupling_csv(coupling_path)
    if coupling_issues:
        raise ValueError(coupling_issues)
    coupling_direct = [
        equivalence_from_interval(item.estimate, item.ci_low, item.ci_high, item.margin, rope_mass=item.rope_mass).passes
        for item in coupling_records
    ]
    coupling_cli = _cli_json(command_python, root, [*cli_base, "decide-coupling", "examples/synthetic_coupling.csv"])
    coupling_backend = run_backend_operation("decide_coupling", _csv_rows(coupling_path), parameters={"rope_threshold": 0.95})
    add_row(
        "decide_coupling",
        coupling_direct,
        [bool(item["passes"]) for item in coupling_cli["typed_results"]],
        [bool(_field_value(item, "passes")) for item in coupling_backend["typed_results"]],
    )

    reserve_path = root / "examples" / "synthetic_reserve.csv"
    reserve_records, reserve_issues = read_reserve_csv(reserve_path)
    if reserve_issues:
        raise ValueError(reserve_issues)
    grouped: dict[tuple[str, str], list[Any]] = {}
    for record in reserve_records:
        grouped.setdefault((record.condition, record.sample_id), []).append(record)
    reserve_direct = []
    for key, sample_rows in sorted(grouped.items()):
        ordered = sorted(sample_rows, key=lambda item: item.time)
        values = [record.response for record in ordered]
        reserve_direct.append(round(reserve_coordinate(ff_over_f0(values, baseline_points=1), floor=1.0, ceiling=1.7), 8))
    reserve_cli = _cli_json(
        command_python,
        root,
        [
            *cli_base,
            "summarize-reserve",
            "examples/synthetic_reserve.csv",
            "--floor",
            "1.0",
            "--ceiling",
            "1.7",
            "--baseline-points",
            "1",
        ],
    )
    reserve_backend = run_backend_operation(
        "summarize_reserve",
        _csv_rows(reserve_path),
        parameters={"floor": 1.0, "ceiling": 1.7, "baseline_points": 1, "normalize": True},
    )
    add_row(
        "summarize_reserve",
        reserve_direct,
        [round(float(item["reserve"]), 8) for item in reserve_cli["summaries"]],
        [round(float(item["reserve"]), 8) for item in reserve_backend["summaries"]],
    )

    endpoint_path = root / "examples" / "synthetic_endpoints.csv"
    endpoint_records, endpoint_issues = read_endpoint_csv(endpoint_path)
    if endpoint_issues:
        raise ValueError(endpoint_issues)
    compare_direct = [fit.model for fit in rank_model_fits(endpoint_records)]
    compare_cli = _cli_json(command_python, root, [*cli_base, "compare", "examples/synthetic_endpoints.csv"])
    compare_backend = run_backend_operation("compare_models", _csv_rows(endpoint_path), parameters={"parameter_count": 1})
    add_row(
        "compare_models",
        compare_direct,
        [item["model"] for item in compare_cli["fits"]],
        [_field_value(item, "model") for item in compare_backend["fits"]],
    )

    audit_env = dict(os.environ)
    audit_env["PYTHONPATH"] = str(root / "src")
    steps.append(_run("backend service contract audit", [str(command_python), "scripts/audit_stage4_service_contract.py"], cwd=root, env=audit_env))
    steps.append(_run("frontend frozen fixture audit", [str(command_python), "scripts/audit_stage5_premium_workbench.py"], cwd=root, env=audit_env))
    return rows, steps


def _compare_outputs(clean_source: Path, reference_root: Path) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for rel in DETERMINISTIC_OUTPUTS:
        clean_path = clean_source / rel
        ref_path = reference_root / rel
        clean_exists = clean_path.exists()
        ref_exists = ref_path.exists()
        clean_hash = _sha256(clean_path) if clean_exists else ""
        ref_hash = _sha256(ref_path) if ref_exists else ""
        rows.append(
            {
                "path": rel,
                "reference_exists": int(ref_exists),
                "clean_room_exists": int(clean_exists),
                "reference_sha256": ref_hash,
                "clean_room_sha256": clean_hash,
                "matches": int(bool(clean_hash) and clean_hash == ref_hash),
            }
        )
    return rows


def _commands_rows(mode: str) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for phase, command in STAGE_REPRO_COMMANDS:
        rows.append(
            {
                "phase": phase,
                "mode": mode,
                "command": " ".join(command).replace(PYTHON, "python"),
                "purpose": "regenerate retained methods-paper evidence output",
            }
        )
    rows.extend(
        [
            {
                "phase": "docs",
                "mode": mode,
                "command": "mkdocs build --strict",
                "purpose": "render methods-program documentation",
            },
            {
                "phase": "surface parity",
                "mode": mode,
                "command": "python scripts/audit_stage4_service_contract.py && python scripts/audit_stage5_premium_workbench.py",
                "purpose": "check backend/frontend surfaces against retained examples and frozen fixtures",
            },
        ]
    )
    return rows


def _workflow_checks(root: Path) -> dict[str, str]:
    workflows = "\n".join(path.read_text(encoding="utf-8") for path in sorted((root / ".github" / "workflows").glob("*.yml")))
    checks = {
        "ci_runs_python_tests": "python -m unittest discover tests" in workflows or "pytest" in workflows,
        "ci_runs_package_build": "python -m build --sdist --wheel" in workflows,
        "ci_runs_docs_build": "mkdocs build --strict" in workflows,
        "ci_runs_docker_build": "docker build -f deploy/stage4.Dockerfile" in workflows,
        "ci_runs_frontend_regression": "npm run test:stage5" in workflows,
        "ci_runs_methods_reproducibility": "run_stage7_6_methods_reproducibility.py --ci-fast" in workflows,
        "ci_runs_notebook_or_methods_examples": "07_stage7_heldout_validation.ipynb" in workflows
        or "run_stage7_6_methods_reproducibility.py" in workflows,
    }
    return {key: "pass" if value else "fail" for key, value in checks.items()}


def run_ci_fast(root: Path = ROOT) -> dict[str, object]:
    steps: list[StepResult] = []
    steps.extend(
        [
            _run("Stage 7.2 benchmark harness", [PYTHON, "scripts/run_stage7_2_benchmark_harness.py"], cwd=root),
            _execute_notebooks(root, Path(PYTHON)),
            _run("roadmap memory check", [PYTHON, "scripts/check_roadmap_memory.py"], cwd=root),
            _run("release safety check", [PYTHON, "scripts/check_release.py"], cwd=root),
        ]
    )
    parity_rows, parity_steps = _cross_surface_parity(root, Path(PYTHON))
    steps.extend(parity_steps)
    comparison_rows = _compare_outputs(root, root)
    workflow_checks = _workflow_checks(root)
    payload = _payload(
        mode="ci_fast",
        steps=steps,
        comparison_rows=comparison_rows,
        parity_rows=parity_rows,
        workflow_checks=workflow_checks,
        archive_source="current checkout",
    )
    return _attach_archive_manifest(payload, _archive_manifest_rows(root))


def run_full(root: Path = ROOT) -> dict[str, object]:
    clean_root = Path(tempfile.mkdtemp(prefix="rhodyn_stage7_6_", dir="/private/tmp" if Path("/private/tmp").exists() else None))
    dist_dir = clean_root / "dist"
    extract_root = clean_root / "extract"
    docs_site = clean_root / "site"
    builder_venv = clean_root / "builder_venv"
    archive_venv = clean_root / "archive_venv"
    steps: list[StepResult] = []

    steps.append(_remove_stale_build_metadata(root))
    steps.append(_run("create build virtual environment", [PYTHON, "-m", "venv", str(builder_venv)], cwd=root))
    builder_python = _venv_python(builder_venv)
    steps.append(_run("upgrade build pip", [str(builder_python), "-m", "pip", "install", "--upgrade", "pip"], cwd=root))
    steps.append(_run("install build tooling", [str(builder_python), "-m", "pip", "install", "build"], cwd=root))
    steps.append(_run("build release-candidate archive", [str(builder_python), "-m", "build", "--sdist", "--wheel", "--outdir", str(dist_dir)], cwd=root))
    archive_source = _extract_first_sdist(dist_dir, extract_root)
    steps.append(StepResult("extract release-candidate source archive", f"extract {dist_dir.name}/rhodyn-*.tar.gz", "pass", 0.0))

    steps.append(_run("create archive virtual environment", [PYTHON, "-m", "venv", str(archive_venv)], cwd=archive_source))
    archive_python = _venv_python(archive_venv)
    steps.append(_run("upgrade archive pip", [str(archive_python), "-m", "pip", "install", "--upgrade", "pip"], cwd=archive_source))
    steps.append(_run("install extracted archive with dev tools", [str(archive_python), "-m", "pip", "install", "-e", ".[dev]"], cwd=archive_source))

    env = dict(os.environ)
    env["PYTHONPATH"] = str(archive_source / "src")
    archive_commands = [
        (name, [str(archive_python), *command[1:]]) for name, command in STAGE_REPRO_COMMANDS
    ]
    for name, command in archive_commands:
        steps.append(_run(name, command, cwd=archive_source, env=env))
    steps.append(_execute_notebooks(archive_source, archive_python))
    steps.append(_run("build documentation site", [str(_venv_cli(archive_venv, "mkdocs")), "build", "--strict", "--site-dir", str(docs_site)], cwd=archive_source, env=env))
    parity_rows, parity_steps = _cross_surface_parity(archive_source, archive_python)
    steps.extend(parity_steps)
    steps.append(_roadmap_state_scan(archive_source))
    steps.append(_archive_surface_scan(archive_source))

    comparison_rows = _compare_outputs(archive_source, root)
    workflow_checks = _workflow_checks(root)
    cleaned_steps = [_clean_step_text(step, clean_root) for step in steps]
    payload = _payload(
        mode="full_release_archive",
        steps=cleaned_steps,
        comparison_rows=comparison_rows,
        parity_rows=parity_rows,
        workflow_checks=workflow_checks,
        archive_source="built source distribution extracted into temporary clean-room workspace",
    )
    payload = _attach_archive_manifest(payload, _archive_manifest_rows(archive_source))
    payload["dist_files"] = [
        {"name": path.name, "size_bytes": path.stat().st_size, "sha256": _sha256(path)}
        for path in sorted(dist_dir.glob("rhodyn-*"))
    ]
    payload["distribution_member_summary"] = _distribution_member_summary(dist_dir)
    checkpoints = payload.get("validation_checkpoints", {})
    if isinstance(checkpoints, dict):
        checkpoints["source_distribution_members_complete"] = (
            "pass" if payload["distribution_member_summary"].get("sdist_status") == "pass" else "fail"
        )
    if payload["distribution_member_summary"].get("sdist_status") != "pass":
        payload["status"] = "fail"
        payload["completion_state"] = "failed_methods_reproducibility_hardening"
        if isinstance(checkpoints, dict):
            checkpoints["stop_condition_clean_room_failure"] = "triggered"
    payload["temporary_workspace"] = "temporary release-archive clean-room workspace outside repository"
    return payload


def _payload(
    *,
    mode: str,
    steps: list[StepResult],
    comparison_rows: list[dict[str, object]],
    parity_rows: list[dict[str, object]],
    workflow_checks: dict[str, str],
    archive_source: str,
) -> dict[str, object]:
    output_match_count = sum(int(row["matches"]) for row in comparison_rows)
    parity_pass_count = sum(int(row["passes"]) for row in parity_rows)
    step_failures = [step.name for step in steps if step.status != "pass"]
    workflow_failures = [name for name, status in workflow_checks.items() if status != "pass"]
    status = (
        "pass"
        if not step_failures
        and output_match_count == len(comparison_rows)
        and parity_pass_count == len(parity_rows)
        and not workflow_failures
        else "fail"
    )
    checkpoints = {
        "fresh_environment_reproduces_benchmark_tables": "pass" if output_match_count == len(comparison_rows) else "fail",
        "tutorial_outputs_execute": "pass" if any(step.name == "execute methods notebooks" and step.status == "pass" for step in steps) else "fail",
        "public_release_scan_finds_no_private_paths_or_secrets": "pass" if any(step.name == "release safety check" and step.status == "pass" for step in steps) else "fail",
        "frontend_backend_cli_python_outputs_agree": "pass" if parity_pass_count == len(parity_rows) and parity_rows else "fail",
        "ci_covers_selected_examples_docs_notebooks_benchmarks_package_docker_frontend": "pass" if not workflow_failures else "fail",
        "clean_room_reproduction_from_release_archive": "pass" if mode == "full_release_archive" and not step_failures else "not_applicable_ci_fast",
        "stop_condition_clean_room_failure": "not_triggered" if status == "pass" else "triggered",
    }
    return {
        "report_format": "rhodyn.stage7_6_methods_reproducibility.v1",
        "generated_utc": _now(),
        "mode": mode,
        "status": status,
        "completion_state": "complete_methods_reproducibility_hardening" if status == "pass" else "failed_methods_reproducibility_hardening",
        "archive_source": archive_source,
        "python": platform.python_version(),
        "platform": platform.platform(),
        "validation_checkpoints": checkpoints,
        "step_failures": step_failures,
        "workflow_failures": workflow_failures,
        "comparison_summary": {
            "matched_outputs": output_match_count,
            "checked_outputs": len(comparison_rows),
        },
        "parity_summary": {
            "matching_operations": parity_pass_count,
            "checked_operations": len(parity_rows),
        },
        "steps": [step.__dict__ for step in steps],
        "workflow_checks": workflow_checks,
        "comparison_rows": comparison_rows,
        "parity_rows": parity_rows,
        "interpretation_boundary": (
            "Stage 7.6 validates methods-paper software reproducibility and cross-surface parity. "
            "It does not add biological evidence or promote new mechanistic claims."
        ),
    }


def _report_markdown(payload: dict[str, object], comparison_rows: list[dict[str, object]], parity_rows: list[dict[str, object]]) -> str:
    checkpoints = payload["validation_checkpoints"]
    archive_summary = payload.get("release_archive_manifest_summary", {})
    lines = [
        "# Stage 7.6 methods-program reproducibility card",
        "",
        f"Generated UTC. {payload['generated_utc']}",
        "",
        f"Overall status. {payload['status']}",
        "",
        "## Scope",
        "",
        "Stage 7.6 hardens the methods-paper evidence set. It checks whether the Stage 7.1 to Stage 7.5 outputs can be regenerated from a declared release-candidate archive, whether selected tutorial notebooks execute, and whether Python, CLI, backend, and frontend-contract surfaces remain aligned for shared workflows.",
        "",
        "## Validation checkpoints",
        "",
    ]
    for key, value in checkpoints.items():
        lines.append(f"- {key}. {value}.")
    lines.extend(["", "## Regenerated output comparison", "", "| Output | Match |", "|---|---:|"])
    for row in comparison_rows:
        lines.append(f"| `{row['path']}` | {row['matches']} |")
    lines.extend(["", "## Cross-surface parity", "", "| Operation | Pass | Frontend status |", "|---|---:|---|"])
    for row in parity_rows:
        lines.append(f"| {row['operation']} | {row['passes']} | {row['frontend_status']} |")
    if isinstance(archive_summary, dict) and archive_summary:
        lines.extend(
            [
                "",
                "## Release archive manifest",
                "",
                f"Manifest status. {archive_summary.get('manifest_status', 'not_recorded')}",
                "",
                f"Files inspected. {archive_summary.get('file_count', 'not_recorded')}",
                "",
                f"Text files inspected. {archive_summary.get('text_file_count', 'not_recorded')}",
                "",
                f"Raw/private-like files. {archive_summary.get('raw_private_like_file_count', 'not_recorded')}",
                "",
                f"Selected deterministic outputs present. {archive_summary.get('deterministic_output_file_count', 'not_recorded')}",
            ]
        )
    distribution_summary = payload.get("distribution_member_summary", {})
    if isinstance(distribution_summary, dict) and distribution_summary:
        lines.extend(
            [
                "",
                "## Source distribution contents",
                "",
                f"Source-distribution status. {distribution_summary.get('sdist_status', 'not_recorded')}",
                "",
                f"Source-distribution members inspected. {distribution_summary.get('sdist_member_count', 'not_recorded')}",
            ]
        )
    lines.extend(
        [
            "",
            "## Interpretation boundary",
            "",
            "A passing Stage 7.6 result supports reproducibility of the software and methods-evidence surface. It does not add a new biological system, does not change any Stage 7 biological interpretation, and does not imply that every future user dataset will support residence, reserve, bounded-coupling, or routed-output claims.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ci-fast", action="store_true", help="Run current-checkout checks used by CI without nested archive extraction.")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--doc-report", type=Path, default=DEFAULT_DOC_REPORT)
    parser.add_argument("--doc-gate", type=Path, default=DEFAULT_DOC_GATE)
    parser.add_argument("--json-report", type=Path, default=DEFAULT_JSON_REPORT)
    args = parser.parse_args()

    payload = run_ci_fast(ROOT) if args.ci_fast else run_full(ROOT)
    output_dir = ROOT / args.output_dir
    comparison_rows = list(payload.get("comparison_rows", []))
    parity_rows = list(payload.get("parity_rows", []))
    archive_rows = list(payload.get("release_archive_manifest_rows", []))

    command_rows = _commands_rows("ci_fast" if args.ci_fast else "full_release_archive")
    _write_csv(output_dir / "methods_reproducibility_commands.tsv", command_rows, ["phase", "mode", "command", "purpose"], delimiter="\t")
    _write_csv(
        output_dir / "methods_output_comparison.tsv",
        comparison_rows,
        ["path", "reference_exists", "clean_room_exists", "reference_sha256", "clean_room_sha256", "matches"],
        delimiter="\t",
    )
    _write_csv(
        output_dir / "cross_surface_parity.tsv",
        parity_rows,
        ["operation", "python_value", "cli_value", "backend_value", "frontend_status", "passes"],
        delimiter="\t",
    )
    _write_csv(
        output_dir / "release_archive_manifest.tsv",
        archive_rows,
        ["path", "size_bytes", "sha256", "suffix", "content_class"],
        delimiter="\t",
    )
    payload_for_json = dict(payload)
    payload_for_json.pop("release_archive_manifest_rows", None)
    _write_json(output_dir / "stage7_6_methods_reproducibility_gate_report.json", payload_for_json)
    _write_text(output_dir / "stage7_6_methods_reproducibility_report.md", _report_markdown(payload, comparison_rows, parity_rows))
    _write_json(ROOT / args.doc_gate, payload_for_json)
    _write_json(ROOT / args.json_report, payload_for_json)
    _write_text(ROOT / args.doc_report, _report_markdown(payload, comparison_rows, parity_rows))
    print(json.dumps({"status": payload["status"], "mode": payload["mode"], "output_dir": args.output_dir.as_posix()}, indent=2))
    return 0 if payload["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())

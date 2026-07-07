"""Assemble the Stage 10.7 benchmark-ready release candidate.

Stage 10.7 does not add new biology, new benchmarks, or new manuscript claims.
It packages the Stage 10.1 through 10.6 method-elevation outputs into a
reproducibility surface with commands, checksums, source scripts, tests, and
gate summaries so the Nature Methods rescue evidence can be replayed from a
fresh clone.
"""

from __future__ import annotations

import csv
import hashlib
import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "case_studies" / "stage10_release_candidate"
DOC_PATH = ROOT / "docs" / "stage10_7_benchmark_release_candidate.md"
GATE_REPORT = OUTPUT_DIR / "stage10_7_gate_report.json"
BRIEF_PATH = OUTPUT_DIR / "stage10_7_release_candidate_brief.md"
COMMANDS_PATH = OUTPUT_DIR / "stage10_7_reproducibility_commands.tsv"
CHECKSUMS_PATH = OUTPUT_DIR / "stage10_7_checksum_manifest.tsv"
ARCHIVE_MANIFEST_PATH = OUTPUT_DIR / "stage10_7_archive_manifest.json"

DYNAMIC_OUTPUTS_EXCLUDED_FROM_CHECKSUM = {
    str(DOC_PATH.relative_to(ROOT)),
    str(GATE_REPORT.relative_to(ROOT)),
    str(BRIEF_PATH.relative_to(ROOT)),
    str(CHECKSUMS_PATH.relative_to(ROOT)),
    str(ARCHIVE_MANIFEST_PATH.relative_to(ROOT)),
}


GATE_REPORTS = {
    "10.1": "case_studies/stage10_method_object_v2/stage10_1_method_object_gate_report.json",
    "10.2": "case_studies/stage10_named_benchmarks/stage10_2_named_benchmark_report.json",
    "10.3": "case_studies/stage10_public_breadth/stage10_3_public_breadth_report.json",
    "10.4": "case_studies/stage10_heldout_validation/stage10_4_gate_report.json",
    "10.5": "case_studies/stage10_figure_architecture/stage10_5_gate_report.json",
    "10.6": "case_studies/stage10_manuscript_pitch/stage10_6_gate_report.json",
}


REPRO_COMMANDS = [
    {
        "step": "1",
        "stage": "10.1",
        "command": "python3 scripts/run_stage10_1_method_object_v2.py",
        "purpose": "Regenerate method-object decisions, fixtures, and gate report.",
        "expected_outputs": "case_studies/stage10_method_object_v2/stage10_1_method_object_gate_report.json",
    },
    {
        "step": "2",
        "stage": "10.2",
        "command": "python3 scripts/run_stage10_2_named_benchmarking.py",
        "purpose": "Regenerate named-baseline benchmark tables and boundary report.",
        "expected_outputs": "case_studies/stage10_named_benchmarks/stage10_2_named_benchmark_report.json",
    },
    {
        "step": "3",
        "stage": "10.3",
        "command": "python3 scripts/run_stage10_3_public_biological_breadth.py",
        "purpose": "Regenerate public-system breadth matrix and source-access records.",
        "expected_outputs": "case_studies/stage10_public_breadth/stage10_3_public_breadth_report.json",
    },
    {
        "step": "4",
        "stage": "10.4",
        "command": "python3 scripts/run_stage10_4_heldout_validation.py",
        "purpose": "Regenerate fixed-rule held-out validation decisions.",
        "expected_outputs": "case_studies/stage10_heldout_validation/stage10_4_gate_report.json",
    },
    {
        "step": "5",
        "stage": "10.5",
        "command": "python3 scripts/run_stage10_5_figure_architecture.py",
        "purpose": "Regenerate method-first figure architecture and panel-evidence crosswalk.",
        "expected_outputs": "case_studies/stage10_figure_architecture/stage10_5_gate_report.json",
    },
    {
        "step": "6",
        "stage": "10.6",
        "command": "python3 scripts/run_stage10_6_manuscript_pitch.py",
        "purpose": "Regenerate method-first manuscript and EIC-facing pitch surfaces.",
        "expected_outputs": "case_studies/stage10_manuscript_pitch/stage10_6_gate_report.json",
    },
    {
        "step": "7",
        "stage": "validation",
        "command": "PYTHONPATH=src python3 -m unittest discover -s tests -p 'test_stage10_*.py'",
        "purpose": "Run the Stage 10-specific regression tests.",
        "expected_outputs": "all Stage 10 tests pass",
    },
    {
        "step": "8",
        "stage": "validation",
        "command": "python3 scripts/check_release.py",
        "purpose": "Verify the full release surface still registers the Stage 10 evidence.",
        "expected_outputs": "status pass",
    },
    {
        "step": "9",
        "stage": "validation",
        "command": "python3 scripts/check_roadmap_memory.py",
        "purpose": "Verify the roadmap memory binds Stage 10.7 as the current completion state.",
        "expected_outputs": "status pass",
    },
]


def _git_sha() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "unknown"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _stage10_artifacts() -> list[str]:
    memory = json.loads((ROOT / "docs" / "roadmap_execution_memory.json").read_text(encoding="utf-8"))
    for entry in memory.get("stage_lock", []):
        if isinstance(entry, dict) and entry.get("stage") == 10:
            artifacts = [item for item in entry.get("artifacts", []) if isinstance(item, str)]
            return sorted(set(artifacts))
    return []


def _category(relpath: str) -> str:
    if relpath.startswith("scripts/"):
        return "script"
    if relpath.startswith("tests/"):
        return "test"
    if relpath.startswith("docs/"):
        return "documentation"
    if relpath.startswith("manuscript/"):
        return "manuscript_surface"
    if relpath.endswith(".json") and "gate_report" in relpath:
        return "gate_report"
    if relpath.startswith("case_studies/"):
        return "case_study_output"
    if relpath.startswith("src/"):
        return "library_source"
    return "support"


def _write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_text(path: Path, body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body.rstrip() + "\n", encoding="utf-8")


def command_rows() -> list[dict[str, str]]:
    return [{**row, "fresh_clone_ready": "yes"} for row in REPRO_COMMANDS]


def checksum_rows() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for relpath in _stage10_artifacts():
        if relpath in DYNAMIC_OUTPUTS_EXCLUDED_FROM_CHECKSUM:
            continue
        path = ROOT / relpath
        if path.is_file():
            rows.append(
                {
                    "relpath": relpath,
                    "category": _category(relpath),
                    "bytes": path.stat().st_size,
                    "sha256": _sha256(path),
                }
            )
    return rows


def gate_statuses() -> dict[str, dict[str, object]]:
    statuses: dict[str, dict[str, object]] = {}
    for stage, relpath in GATE_REPORTS.items():
        path = ROOT / relpath
        if not path.exists():
            statuses[stage] = {"exists": False, "status": "missing"}
            continue
        payload = json.loads(path.read_text(encoding="utf-8"))
        statuses[stage] = {
            "exists": True,
            "status": payload.get("status"),
            "path": relpath,
        }
    return statuses


def safety_scan(paths: list[str]) -> list[dict[str, str]]:
    patterns = {
        "local_user_path": re.compile("/" + "Users/"),
        "mounted_volume_path": re.compile("/" + "Volumes/"),
        "launch_agent_path": re.compile("Library/" + "LaunchAgents"),
        "openai_key_like": re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b"),
        "github_token_like": re.compile(r"\bghp_[A-Za-z0-9]{20,}\b"),
        "password_assignment": re.compile(r"(?i)\bpassword\s*[=:]"),
        "secret_assignment": re.compile(r"(?i)\bsecret\s*[=:]"),
    }
    hits: list[dict[str, str]] = []
    for relpath in paths:
        path = ROOT / relpath
        if not path.is_file() or path.stat().st_size > 2_000_000:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        for name, pattern in patterns.items():
            if pattern.search(text):
                hits.append({"relpath": relpath, "pattern": name})
    return hits


def validate_stage10_7() -> dict[str, object]:
    artifacts = _stage10_artifacts()
    checksum_manifest = checksum_rows()
    gates = gate_statuses()
    missing_artifacts = [relpath for relpath in artifacts if not (ROOT / relpath).exists()]
    safety_hits = safety_scan(artifacts)
    command_stages = {row["stage"] for row in REPRO_COMMANDS}
    all_stage_gates_pass = all(item.get("status") == "pass" for item in gates.values())
    validation = {
        "stage10_6_prerequisite_passed": gates.get("10.6", {}).get("status") == "pass",
        "all_stage10_gates_pass": all_stage_gates_pass,
        "all_stage10_artifacts_exist": not missing_artifacts,
        "checksum_manifest_covers_stage10": len(checksum_manifest) >= 50,
        "fresh_clone_commands_declared": {"10.1", "10.2", "10.3", "10.4", "10.5", "10.6", "validation"}.issubset(command_stages),
        "release_candidate_safety_scan_clear": not safety_hits,
    }
    return {
        "stage": "10.7",
        "status": "pass" if all(validation.values()) else "fail",
        "generated_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "git_sha": _git_sha(),
        "gates": validation,
        "summary_metrics": {
            "stage10_artifact_count": len(artifacts),
            "checksum_row_count": len(checksum_manifest),
            "reproducibility_command_count": len(REPRO_COMMANDS),
            "stage_gate_count": len(gates),
            "safety_hit_count": len(safety_hits),
        },
        "missing_artifacts": missing_artifacts,
        "safety_hits": safety_hits,
        "stage_gate_statuses": gates,
        "next_phase": "Stage 10.8 adversarial EIC red-team simulation",
        "interpretation_boundary": "Stage 10.7 is a release-candidate packaging and reproducibility layer. It does not add biological data, benchmarks, figures, or manuscript claims.",
    }


def run_stage10_7() -> dict[str, object]:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    commands = command_rows()
    checksums = checksum_rows()
    _write_csv(COMMANDS_PATH, commands, ["step", "stage", "command", "purpose", "expected_outputs", "fresh_clone_ready"])
    _write_csv(CHECKSUMS_PATH, checksums, ["relpath", "category", "bytes", "sha256"])
    report = validate_stage10_7()
    archive_manifest = {
        "release_candidate_id": f"stage10.7-benchmark-release-candidate@{report['git_sha']}",
        "generated_utc": report["generated_utc"],
        "git_sha": report["git_sha"],
        "command_index": str(COMMANDS_PATH.relative_to(ROOT)),
        "checksum_manifest": str(CHECKSUMS_PATH.relative_to(ROOT)),
        "stage_gate_statuses": report["stage_gate_statuses"],
        "artifact_count": report["summary_metrics"]["stage10_artifact_count"],
        "checksum_row_count": report["summary_metrics"]["checksum_row_count"],
        "scope": report["interpretation_boundary"],
    }
    _write_json(ARCHIVE_MANIFEST_PATH, archive_manifest)
    _write_json(GATE_REPORT, report)
    brief = f"""# Stage 10.7 benchmark-ready release candidate

Stage 10.7 packages the Stage 10 method-elevation evidence into a reproducible benchmark-ready surface. It binds the Stage 10.1 through 10.6 commands, gate reports, generated outputs, source scripts, tests, and checksums without adding new biological evidence.

Status. {report['status']}.

Artifacts covered. {report['summary_metrics']['checksum_row_count']} checksum rows from {report['summary_metrics']['stage10_artifact_count']} registered Stage 10 artifacts.

Next phase. {report['next_phase']}.
"""
    _write_text(BRIEF_PATH, brief)
    doc = f"""# Stage 10.7 benchmark-ready release candidate

Stage 10.7 makes the Nature Methods rescue evidence reproducible as a benchmark-ready release candidate. The package records how to regenerate the method object, named baselines, public biological breadth, held-out validation, method-first figure architecture, and method-first manuscript/pitch surfaces from a fresh clone.

## Outputs

- `case_studies/stage10_release_candidate/stage10_7_reproducibility_commands.tsv`
- `case_studies/stage10_release_candidate/stage10_7_checksum_manifest.tsv`
- `case_studies/stage10_release_candidate/stage10_7_archive_manifest.json`
- `case_studies/stage10_release_candidate/stage10_7_gate_report.json`
- `case_studies/stage10_release_candidate/stage10_7_release_candidate_brief.md`

## Gate status

{report['status']}

## Boundary

{report['interpretation_boundary']}
"""
    _write_text(DOC_PATH, doc)
    return report


if __name__ == "__main__":
    print(json.dumps(run_stage10_7(), indent=2, sort_keys=True))

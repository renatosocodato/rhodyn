"""Run Stage 9.0 evidence intake and lock.

Stage 9.0 converts the completed Stage 7 methods-readiness package into a
frozen manuscript-evidence ledger. It does not draft manuscript text, resolve
citations, render figures, clone PanelForge, or assemble a submission package.
"""

from __future__ import annotations

import csv
import hashlib
import json
import shutil
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT / "manuscript" / "nature_methods"
LEDGER_DIR = WORKSPACE / "ledgers"
GATE_DIR = WORKSPACE / "gate_verdicts"
STAGING_DIR = WORKSPACE / "_staging" / "9.0"
QUARANTINE_DIR = WORKSPACE / "_quarantine" / "9.0"
MEMORY_PATH = ROOT / "docs" / "stage9_execution_memory.json"
ROADMAP_MEMORY_PATH = ROOT / "docs" / "roadmap_execution_memory.json"
REGISTRY_PATH = WORKSPACE / "contracts" / "stage9_substage_registry.json"

FIGURE_CROSSWALK = ROOT / "case_studies" / "stage7_methods_readiness" / "figure_artifact_crosswalk.tsv"
CLAIM_CROSSWALK = ROOT / "case_studies" / "stage7_methods_readiness" / "claim_evidence_crosswalk.tsv"
READINESS_GATE = ROOT / "docs" / "stage7_8_gate_report.json"
READINESS_CASE_GATE = ROOT / "case_studies" / "stage7_methods_readiness" / "stage7_8_methods_readiness_gate_report.json"
RELEASE_MANIFEST = ROOT / "case_studies" / "stage7_methods_reproducibility" / "release_archive_manifest.tsv"
REPRO_COMMANDS = ROOT / "case_studies" / "stage7_methods_reproducibility" / "methods_reproducibility_commands.tsv"

OUTPUTS = {
    "manifest": LEDGER_DIR / "stage9_evidence_manifest.csv",
    "lock": LEDGER_DIR / "stage9_evidence_lock.md",
    "contract": LEDGER_DIR / "stage7_output_contract.md",
    "gate": GATE_DIR / "9.0.json",
}

REQUIRED_GATE_REPORTS = [
    "docs/stage7_1_gate_report.json",
    "docs/stage7_2_gate_report.json",
    "docs/stage7_3_gate_report.json",
    "docs/stage7_4_gate_report.json",
    "docs/stage7_5_gate_report.json",
    "docs/stage7_6_gate_report.json",
    "docs/stage7_7_gate_report.json",
    "docs/stage7_8_gate_report.json",
    "case_studies/stage7_methods_readiness/stage7_8_methods_readiness_gate_report.json",
    "case_studies/stage7_methods_reproducibility/stage7_6_methods_reproducibility_gate_report.json",
    "case_studies/stage7_methods_reproducibility/stage7_6_recursive_hardening_report.json",
    "case_studies/stage7_methods_readiness/stage7_7_8_recursive_hardening_report.json",
]

REQUIRED_SUPPORT_FILES = [
    "docs/stage7_methods_evidence_index.md",
    "docs/stage7_methods_submission_readiness.md",
    "docs/stage7_methods_program.md",
    "docs/stage7_method_specification.md",
    "docs/stage7_limitations_matrix.md",
    "docs/stage7_methods_reproducibility_card.md",
    "docs/release_checksums.json",
    "docs/release_checksums.csv",
    "case_studies/stage7_methods_reproducibility/release_archive_manifest.tsv",
    "case_studies/stage7_methods_reproducibility/methods_reproducibility_commands.tsv",
    "case_studies/stage7_methods_reproducibility/methods_output_comparison.tsv",
    "case_studies/stage7_methods_reproducibility/cross_surface_parity.tsv",
]

FORBIDDEN_STARTED_PATHS = [
    WORKSPACE / "sections" / "results.md",
    WORKSPACE / "sections" / "introduction.md",
    WORKSPACE / "sections" / "discussion.md",
    WORKSPACE / "sections" / "methods.md",
    WORKSPACE / "sections" / "abstract.md",
    WORKSPACE / "refs" / "references.bib",
    WORKSPACE / "submission_package" / "pi_review_packet.md",
    WORKSPACE / "submission_package" / "submission_readiness_checklist.md",
    WORKSPACE / "figures" / ".panelforge_commit",
    WORKSPACE / "audits" / "panelforge_render_report.md",
    ROOT / ".venv-panelforge",
    ROOT / "tools" / "panelforge-figures" / ".git",
]


def _now() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def _git_sha() -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if result.returncode != 0:
        return "unknown"
    return result.stdout.strip()


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_text(path: Path, body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body.rstrip() + "\n", encoding="utf-8")


def _write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fieldnames})


def _read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def _split_paths(value: str) -> list[str]:
    return [item.strip() for item in value.split(";") if item.strip()]


def _schema_label(path: Path) -> str:
    suffix = path.suffix.lower().lstrip(".")
    if suffix:
        return suffix
    return "text"


def _stage7_gate_passed(path: Path) -> bool:
    if not path.exists():
        return False
    try:
        data = _read_json(path)
    except json.JSONDecodeError:
        return False
    return data.get("status") == "pass"


def _collect_evidence_rows(evidence_version: str) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    evidence: dict[str, dict[str, str]] = {}
    contracts: dict[str, dict[str, str]] = {}

    def add_artifact(component: str, rel_path: str, status: str = "locked") -> None:
        path = ROOT / rel_path
        if rel_path not in evidence:
            evidence[rel_path] = {
                "art_id": "",
                "stage7_component": component,
                "path": rel_path,
                "schema": _schema_label(path),
                "status": status if path.exists() else "missing",
                "evidence_version": evidence_version,
            }

    def add_contract(component: str, rel_path: str, scope_status: str) -> None:
        path = ROOT / rel_path
        contracts[f"{component}|{rel_path}"] = {
            "component": component,
            "path": rel_path,
            "schema": _schema_label(path),
            "required_for_stage9": "true",
            "scope_status": scope_status,
        }

    for rel_path in REQUIRED_GATE_REPORTS + REQUIRED_SUPPORT_FILES:
        add_artifact("stage7_gate_or_support", rel_path)

    for row in _read_tsv(FIGURE_CROSSWALK):
        component = row["component"]
        for column in ["primary_artifact", "supporting_artifacts", "validation_artifact", "limitation_artifact"]:
            for rel_path in _split_paths(row[column]):
                add_artifact(component, rel_path)
        add_contract(component, row["primary_artifact"], row["scope"])

    for row in _read_tsv(CLAIM_CROSSWALK):
        component = row["claim_id"]
        for column in ["evidence", "validation", "limitation"]:
            for rel_path in _split_paths(row[column]):
                add_artifact(component, rel_path)
        add_contract(component, row["evidence"], row["status"])

    rows = list(evidence.values())
    for idx, row in enumerate(rows, start=1):
        row["art_id"] = f"ART-{idx:04d}"
    return rows, list(contracts.values())


def _validate(rows: list[dict[str, str]], contracts: list[dict[str, str]], evidence_version: str) -> list[dict[str, Any]]:
    manifest_paths = {row["path"] for row in rows}
    gate_paths = [ROOT / rel for rel in REQUIRED_GATE_REPORTS]
    figure_rows = _read_tsv(FIGURE_CROSSWALK)
    claim_rows = _read_tsv(CLAIM_CROSSWALK)
    rendered = [
        path
        for path in (WORKSPACE / "figures" / "rendered").rglob("*")
        if path.is_file() and path.suffix.lower() in {".png", ".pdf", ".svg"}
    ]

    checks = [
        {
            "name": "entry_artifacts_resolve",
            "passed": all((ROOT / row["path"]).exists() for row in rows),
            "detail": f"{sum((ROOT / row['path']).exists() for row in rows)} of {len(rows)} locked artifacts resolve",
        },
        {
            "name": "artifacts_validate_or_are_scoped_out",
            "passed": all(_stage7_gate_passed(path) for path in gate_paths),
            "detail": "Stage 7 gate reports and readiness reports retain pass status",
        },
        {
            "name": "headline_stage7_results_map_to_art_ids",
            "passed": all(
                rel_path in manifest_paths
                for row in figure_rows
                for rel_path in _split_paths(row["primary_artifact"])
            )
            and all(
                rel_path in manifest_paths
                for row in claim_rows
                for rel_path in _split_paths(row["evidence"])
            ),
            "detail": f"{len(figure_rows)} figure components and {len(claim_rows)} headline claims map to locked artifacts",
        },
        {
            "name": "evidence_version_is_immutable",
            "passed": bool(evidence_version.startswith("stage7.8-methods-readiness@")) and len(set(row["evidence_version"] for row in rows)) == 1,
            "detail": evidence_version,
        },
        {
            "name": "stage7_output_contract_present",
            "passed": len(contracts) >= len(figure_rows) + len(claim_rows),
            "detail": f"{len(contracts)} output-contract rows prepared",
        },
        {
            "name": "no_downstream_stage9_surfaces_started",
            "passed": not any(path.exists() for path in FORBIDDEN_STARTED_PATHS) and not rendered,
            "detail": "No manuscript sections, reference library, submission package, PanelForge clone, runtime environment, or rendered figures detected",
        },
    ]
    return checks


def _markdown_table(rows: list[dict[str, str]], columns: list[str]) -> str:
    lines = ["| " + " | ".join(columns) + " |", "| " + " | ".join("---" for _ in columns) + " |"]
    for row in rows:
        lines.append("| " + " | ".join(str(row.get(column, "")).replace("|", "\\|") for column in columns) + " |")
    return "\n".join(lines)


def _build_lock_markdown(
    rows: list[dict[str, str]],
    contracts: list[dict[str, str]],
    checks: list[dict[str, Any]],
    evidence_version: str,
    generated_utc: str,
) -> str:
    gate_status = "pass" if all(check["passed"] for check in checks) else "fail"
    locked_rows = [
        {
            "art_id": row["art_id"],
            "component": row["stage7_component"],
            "path": row["path"],
            "sha256": _sha256(ROOT / row["path"]) if (ROOT / row["path"]).exists() else "missing",
            "status": row["status"],
        }
        for row in rows
    ]
    check_rows = [
        {
            "check": check["name"],
            "status": "pass" if check["passed"] else "fail",
            "detail": check["detail"],
        }
        for check in checks
    ]
    body = f"""# Stage 9.0 evidence lock

Generated UTC. {generated_utc}

Evidence version. `{evidence_version}`

Gate status. {gate_status}

## Scope

This lock imports the completed Stage 7 methods-readiness evidence package into
Stage 9. It does not add a biological system, new analysis route, new benchmark
result, manuscript prose, citation library, figure render, or submission package.

## Gate checks

{_markdown_table(check_rows, ["check", "status", "detail"])}

## Locked evidence artifacts

{_markdown_table(locked_rows, ["art_id", "component", "path", "sha256", "status"])}

## Stage 7 output contract

{_markdown_table(contracts, ["component", "path", "schema", "required_for_stage9", "scope_status"])}
"""
    return body


def _build_contract_markdown(contracts: list[dict[str, str]], evidence_version: str) -> str:
    body = f"""# Stage 7 output contract for Stage 9

Evidence version. `{evidence_version}`

Each row defines a Stage 7 output that may be used by Stage 9 only within the
listed scope. The contract supports manuscript assembly, not new scientific
inference.

{_markdown_table(contracts, ["component", "path", "schema", "required_for_stage9", "scope_status"])}
"""
    return body


def _promote_staging() -> None:
    for key, destination in OUTPUTS.items():
        staged = STAGING_DIR / destination.relative_to(WORKSPACE)
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(staged, destination)


def _quarantine_staging(timestamp: str) -> Path:
    target = QUARANTINE_DIR / timestamp.replace(":", "").replace("-", "")
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        shutil.rmtree(target)
    shutil.move(str(STAGING_DIR), str(target))
    return target


def _update_registry() -> None:
    registry = _read_json(REGISTRY_PATH)
    for substage in registry.get("substages", []):
        if substage.get("id") == "9.0":
            substage["status"] = "completed"
    registry["last_completed_substage"] = "9.0"
    _write_json(REGISTRY_PATH, registry)


def _update_memory(evidence_version: str, generated_utc: str, passed: bool, checks: list[dict[str, Any]]) -> None:
    memory = _read_json(MEMORY_PATH)
    memory["generated_utc"] = generated_utc
    memory["current_substage"] = "9.0"
    memory["evidence_intake_started"] = True
    memory["evidence_version"] = evidence_version
    memory["status"] = "stage9_0_evidence_locked" if passed else "stage9_0_evidence_lock_failed"
    memory["next_substage"] = "9.1" if passed else "9.0"
    memory["next_substage_authorized"] = False
    memory.setdefault("completed_substages", [])
    if passed and not any(item.get("substage") == "9.0" for item in memory["completed_substages"]):
        memory["completed_substages"].append(
            {
                "substage": "9.0",
                "status": "pass",
                "pass": True,
                "gate_verdict_path": "manuscript/nature_methods/gate_verdicts/9.0.json",
                "validation_outcome": "Stage 7 evidence package locked for Stage 9 manuscript assembly",
                "evidence_dependencies": [
                    "case_studies/stage7_methods_readiness/figure_artifact_crosswalk.tsv",
                    "case_studies/stage7_methods_readiness/claim_evidence_crosswalk.tsv",
                    "docs/stage7_8_gate_report.json",
                    "case_studies/stage7_methods_reproducibility/release_archive_manifest.tsv",
                ],
                "files_created_or_modified": [str(path.relative_to(ROOT)) for path in OUTPUTS.values()],
                "remaining_blockers": [
                    "Stage 9.1 venue guidance has not started",
                    "Stage 9.2 representative corpus has not started",
                    "Stage 9.6 figure-to-claim contract has not started",
                    "Stage 9.6b PanelForge rendering remains blocked until Stage 9.6 passes",
                ],
            }
        )
    memory["stage9_0_checks"] = checks
    _write_json(MEMORY_PATH, memory)


def _update_roadmap_memory(evidence_version: str, passed: bool) -> None:
    if not ROADMAP_MEMORY_PATH.exists():
        return
    memory = _read_json(ROADMAP_MEMORY_PATH)
    current = memory.setdefault("current_position", {})
    if passed:
        current["active_stage"] = "Stage 9.0 evidence locked; manuscript production not started"
        current["stage9_active_gate"] = "Stage 9.0 evidence locked; manuscript production not started"
        current["after_stage9_0_evidence_lock"] = (
            "Stage 9.0 locked the completed Stage 7.8 methods-readiness evidence package into "
            "stage9_evidence_manifest.csv, stage9_evidence_lock.md, and stage7_output_contract.md. "
            "Stage 9.1 venue guidance, citation resolution, manuscript drafting, figure rendering, "
            "PanelForge execution, and submission-package assembly remain not started."
        )
    stages = memory.get("stage_lock", [])
    if isinstance(stages, list):
        for stage in stages:
            if not isinstance(stage, dict) or stage.get("stage") != 9:
                continue
            if passed:
                stage["status"] = "stage9_0_evidence_locked"
                stage["current_gate"] = "Stage 9.0 evidence locked; manuscript production not started"
                stage["scope_rule"] = (
                    "Stage 9 has completed evidence intake only. Do not start venue guidance, "
                    "citation resolution, drafting, figure rendering, review response, or submission "
                    "packaging without explicit substage authorization."
                )
                artifacts = stage.setdefault("artifacts", [])
                for artifact in [
                    "manuscript/nature_methods/ledgers/stage9_evidence_manifest.csv",
                    "manuscript/nature_methods/ledgers/stage9_evidence_lock.md",
                    "manuscript/nature_methods/ledgers/stage7_output_contract.md",
                    "manuscript/nature_methods/gate_verdicts/9.0.json",
                    "scripts/run_stage9_0_evidence_intake_lock.py",
                ]:
                    if artifact not in artifacts:
                        artifacts.append(artifact)
                for subphase in stage.get("subphases", []):
                    if isinstance(subphase, dict) and subphase.get("id") == "9.0":
                        subphase["status"] = "complete_evidence_locked"
                        subphase["evidence"] = "manuscript/nature_methods/gate_verdicts/9.0.json"
                        subphase["evidence_version"] = evidence_version
    _write_json(ROADMAP_MEMORY_PATH, memory)


def run() -> dict[str, Any]:
    generated_utc = _now()
    commit = _git_sha()
    evidence_version = f"stage7.8-methods-readiness@{commit}"
    if STAGING_DIR.exists():
        shutil.rmtree(STAGING_DIR)
    STAGING_DIR.mkdir(parents=True, exist_ok=True)

    rows, contracts = _collect_evidence_rows(evidence_version)
    checks = _validate(rows, contracts, evidence_version)
    passed = all(check["passed"] for check in checks)
    gate = {
        "substage": "9.0",
        "timestamp": generated_utc,
        "evidence_version": evidence_version,
        "pass": passed,
        "checks": checks,
        "outputs": [str(path.relative_to(ROOT)) for path in OUTPUTS.values()],
        "scope_boundary": "Evidence intake only. No drafting, citation resolution, figure rendering, PanelForge execution, or submission-package assembly.",
    }

    staged_outputs = {
        "manifest": STAGING_DIR / OUTPUTS["manifest"].relative_to(WORKSPACE),
        "lock": STAGING_DIR / OUTPUTS["lock"].relative_to(WORKSPACE),
        "contract": STAGING_DIR / OUTPUTS["contract"].relative_to(WORKSPACE),
        "gate": STAGING_DIR / OUTPUTS["gate"].relative_to(WORKSPACE),
    }
    _write_csv(
        staged_outputs["manifest"],
        rows,
        ["art_id", "stage7_component", "path", "schema", "status", "evidence_version"],
    )
    _write_text(staged_outputs["lock"], _build_lock_markdown(rows, contracts, checks, evidence_version, generated_utc))
    _write_text(staged_outputs["contract"], _build_contract_markdown(contracts, evidence_version))
    _write_json(staged_outputs["gate"], gate)

    if passed:
        _promote_staging()
        shutil.rmtree(STAGING_DIR)
        _update_registry()
        _update_memory(evidence_version, generated_utc, True, checks)
        _update_roadmap_memory(evidence_version, True)
    else:
        quarantine = _quarantine_staging(generated_utc)
        _update_memory(evidence_version, generated_utc, False, checks)
        _update_roadmap_memory(evidence_version, False)
        gate["quarantine_path"] = str(quarantine.relative_to(ROOT))
        _write_json(OUTPUTS["gate"], gate)

    return {
        "status": "pass" if passed else "fail",
        "substage": "9.0",
        "evidence_version": evidence_version,
        "artifact_count": len(rows),
        "contract_count": len(contracts),
        "failures": [check for check in checks if not check["passed"]],
        "outputs": gate["outputs"],
    }


def main() -> int:
    payload = run()
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())

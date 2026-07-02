"""Audit Stage 7.7 and 7.8 outputs for recursive release consistency.

This check is intentionally independent of the Stage 7.7 and Stage 7.8
generators. It verifies that the usability export bundles, methods-readiness
crosswalks, release checksums, and clean-room archive manifest still describe
the same release-facing evidence package.
"""

from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
import re
import subprocess
import sys
import zipfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
STAGE7_7_DIR = ROOT / "case_studies" / "stage7_usability_rehearsal"
STAGE7_8_DIR = ROOT / "case_studies" / "stage7_methods_readiness"
DOC_REPORT = ROOT / "docs" / "stage7_7_8_recursive_hardening_report.json"
CASE_REPORT = STAGE7_8_DIR / "stage7_7_8_recursive_hardening_report.json"
DOC_SUMMARY = ROOT / "docs" / "stage7_7_8_recursive_hardening.md"
STAGE7_8_RUNNER = ROOT / "scripts" / "run_stage7_8_methods_readiness.py"
STAGE9_CHECKER = ROOT / "scripts" / "check_stage9_scaffold.py"

FORBIDDEN_BUNDLE_SUFFIXES = {".tif", ".tiff", ".lif", ".czi", ".nd2", ".prism", ".xml", ".zip"}
EXPECTED_BUNDLE_MEMBERS = {
    "README.md",
    "input_rows.csv",
    "manifest.json",
    "parameter_provenance.json",
    "parameter_provenance.md",
    "parameters.json",
    "report.md",
    "result.json",
    "result_rows.csv",
}
REQUIRED_STAGE7_7_8_FILES = {
    "docs/stage7_usability_rehearsal.md",
    "docs/stage7_user_path_findings.md",
    "docs/stage7_7_gate_report.json",
    "scripts/run_stage7_7_usability_rehearsal.py",
    "tests/test_stage7_7_usability_rehearsal.py",
    "case_studies/stage7_usability_rehearsal/usability_task_protocol.tsv",
    "case_studies/stage7_usability_rehearsal/biologist_residence_task_result.json",
    "case_studies/stage7_usability_rehearsal/biologist_residence_bundle.zip",
    "case_studies/stage7_usability_rehearsal/quantitative_reproduction_result.json",
    "case_studies/stage7_usability_rehearsal/quantitative_bounded_coupling_bundle.zip",
    "case_studies/stage7_usability_rehearsal/export_examples_manifest.tsv",
    "case_studies/stage7_usability_rehearsal/workbench_flow_check.json",
    "case_studies/stage7_usability_rehearsal/stage7_7_usability_gate_report.json",
    "case_studies/stage7_usability_rehearsal/stage7_7_usability_rehearsal_report.md",
    "docs/stage7_methods_evidence_index.md",
    "docs/stage7_figure_artifact_crosswalk.md",
    "docs/stage7_claim_evidence_crosswalk.md",
    "docs/stage7_methods_submission_readiness.md",
    "docs/stage7_8_gate_report.json",
    "scripts/run_stage7_8_methods_readiness.py",
    "tests/test_stage7_8_methods_readiness.py",
    "case_studies/stage7_methods_readiness/figure_artifact_crosswalk.tsv",
    "case_studies/stage7_methods_readiness/claim_evidence_crosswalk.tsv",
    "case_studies/stage7_methods_readiness/methods_readiness_checklist.tsv",
    "case_studies/stage7_methods_readiness/limitations_traceability.tsv",
    "case_studies/stage7_methods_readiness/stage7_8_methods_readiness_gate_report.json",
    "case_studies/stage7_methods_readiness/stage7_8_methods_readiness_report.md",
}
REQUIRED_NONBINARY_ARCHIVE_FILES = {rel for rel in REQUIRED_STAGE7_7_8_FILES if not rel.endswith(".zip")}
ALLOWED_STAGE9_PREFIXES = {
    "docs/stage9_execution_memory.json",
    "docs/stage9_manuscript_assembly_plan.md",
    "manuscript/nature_methods/README.md",
    "manuscript/nature_methods/contracts/",
    "manuscript/nature_methods/figures/.gitkeep",
    "manuscript/nature_methods/figures/figures.manifest.yaml",
    "manuscript/nature_methods/figures/rendered/.gitkeep",
    "manuscript/nature_methods/gate_verdicts/9.-1.json",
    "manuscript/nature_methods/gate_verdicts/9.0.json",
    "manuscript/nature_methods/gate_verdicts/9.1.json",
    "manuscript/nature_methods/gate_verdicts/9.2.json",
    "manuscript/nature_methods/gate_verdicts/9.3.json",
    "manuscript/nature_methods/gate_verdicts/9.4.json",
    "manuscript/nature_methods/ledgers/.gitkeep",
    "manuscript/nature_methods/ledgers/stage9_evidence_manifest.csv",
    "manuscript/nature_methods/ledgers/stage9_evidence_lock.md",
    "manuscript/nature_methods/ledgers/stage7_output_contract.md",
    "manuscript/nature_methods/refs/.gitkeep",
    "manuscript/nature_methods/refs/_cache/.gitkeep",
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
    "manuscript/nature_methods/refs/_cache/methods_corpus/",
    "manuscript/nature_methods/refs/representative_methods_papers.md",
    "manuscript/nature_methods/refs/nature_methods_guidance_register.md",
    "manuscript/nature_methods/audits/.gitkeep",
    "manuscript/nature_methods/audits/venue_policy_constraints.md",
    "manuscript/nature_methods/audits/methods_paper_archetype_analysis.md",
    "manuscript/nature_methods/audits/venue_fit_rationale.md",
    "manuscript/nature_methods/stage9_narrative_spine.md",
    "manuscript/nature_methods/ledgers/claim_hierarchy.md",
    "manuscript/nature_methods/ledgers/claim_hierarchy.csv",
    "manuscript/nature_methods/ledgers/non_claims_and_scope_boundaries.md",
    "scripts/check_stage9_scaffold.py",
    "scripts/run_stage9_0_evidence_intake_lock.py",
    "scripts/run_stage9_1_venue_guidance_register.py",
    "scripts/run_stage9_2_methods_paper_corpus.py",
    "scripts/run_stage9_3_narrative_spine.py",
    "scripts/run_stage9_4_claim_freeze.py",
    "scripts/run_stage9_6b_panelforge_rendering.py",
    "scripts/scaffold_stage9_manuscript_assembly.py",
    "tests/test_stage9_0_evidence_lock.py",
    "tests/test_stage9_1_venue_guidance.py",
    "tests/test_stage9_2_methods_paper_corpus.py",
    "tests/test_stage9_3_narrative_spine.py",
    "tests/test_stage9_4_claim_freeze.py",
    "tests/test_stage9_scaffold.py",
    "tools/panelforge-figures/.gitkeep",
    "tools/panelforge-figures/STAGE9_PLACEHOLDER.md",
}
FORBIDDEN_STAGE9_DRAFT_FILES = {
    "manuscript/nature_methods/sections/results.md",
    "manuscript/nature_methods/sections/introduction.md",
    "manuscript/nature_methods/sections/discussion.md",
    "manuscript/nature_methods/sections/methods.md",
    "manuscript/nature_methods/refs/references.bib",
}


def _load_stage7_8_runner() -> Any:
    spec = importlib.util.spec_from_file_location("stage7_8_runner_contract", STAGE7_8_RUNNER)
    module = importlib.util.module_from_spec(spec)
    sys.modules[str(spec.name)] = module
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _read_json(path: Path, failures: list[str]) -> dict[str, Any]:
    if not path.exists():
        failures.append(f"missing JSON file: {path.relative_to(ROOT).as_posix()}")
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        failures.append(f"invalid JSON file {path.relative_to(ROOT).as_posix()}: {exc}")
        return {}


def _read_tsv(path: Path, failures: list[str]) -> list[dict[str, str]]:
    if not path.exists():
        failures.append(f"missing TSV file: {path.relative_to(ROOT).as_posix()}")
        return []
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def _read_csv(path: Path, failures: list[str]) -> list[dict[str, str]]:
    if not path.exists():
        failures.append(f"missing CSV file: {path.relative_to(ROOT).as_posix()}")
        return []
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _paths_from_cell(value: str) -> list[str]:
    return [part.strip() for part in value.split(";") if part.strip()]


def _gate_pair_status(
    doc_rel: str,
    case_rel: str,
    completion_state: str,
    failures: list[str],
) -> bool:
    doc = _read_json(ROOT / doc_rel, failures)
    case = _read_json(ROOT / case_rel, failures)
    if doc and case and doc != case:
        failures.append(f"{doc_rel} and {case_rel} are not identical")
    for rel, payload in [(doc_rel, doc), (case_rel, case)]:
        if not payload:
            continue
        if payload.get("status") != "pass":
            failures.append(f"{rel} does not pass")
        if payload.get("completion_state") != completion_state:
            failures.append(f"{rel} does not record completion_state={completion_state}")
    return bool(doc and case and doc == case and doc.get("status") == "pass" and doc.get("completion_state") == completion_state)


def _validate_zip_manifest(archive: zipfile.ZipFile, bundle_rel: str, failures: list[str]) -> None:
    manifest = json.loads(archive.read("manifest.json").decode("utf-8"))
    files = manifest.get("files", [])
    if not isinstance(files, list) or not files:
        failures.append(f"{bundle_rel} manifest.json does not list bundled files")
        return
    for item in files:
        if not isinstance(item, dict) or "path" not in item or "sha256" not in item:
            failures.append(f"{bundle_rel} manifest.json has an incomplete file row")
            continue
        member = str(item["path"])
        if member == "manifest.json":
            continue
        if member not in archive.namelist():
            failures.append(f"{bundle_rel} manifest.json references missing member {member}")
            continue
        data = archive.read(member)
        if _sha256_bytes(data) != str(item["sha256"]):
            failures.append(f"{bundle_rel} member hash does not match manifest.json for {member}")
        if int(item.get("bytes", len(data)) or 0) != len(data):
            failures.append(f"{bundle_rel} member byte count does not match manifest.json for {member}")


def _validate_export_bundles(failures: list[str]) -> dict[str, int]:
    rows = _read_tsv(STAGE7_7_DIR / "export_examples_manifest.tsv", failures)
    if len(rows) != 2:
        failures.append("Stage 7.7 export manifest must record exactly two rehearsal bundles")
    counts = {"bundles": len(rows), "members": 0}
    for row in rows:
        bundle_rel = row.get("bundle_path", "")
        bundle_path = ROOT / bundle_rel
        if not bundle_rel or not bundle_path.exists():
            failures.append(f"missing Stage 7.7 bundle: {bundle_rel}")
            continue
        if row.get("sha256") != _sha256(bundle_path):
            failures.append(f"Stage 7.7 bundle hash mismatch in export manifest: {bundle_rel}")
        if row.get("software_version") != "0.1.0":
            failures.append(f"Stage 7.7 bundle must record software version 0.1.0: {bundle_rel}")
        if row.get("has_parameters") != "1" or row.get("has_input_schema") != "1" or row.get("has_grouping") != "1":
            failures.append(f"Stage 7.7 bundle metadata columns are incomplete: {bundle_rel}")
        with zipfile.ZipFile(bundle_path) as archive:
            names = set(archive.namelist())
            counts["members"] += len(names)
            missing = sorted(EXPECTED_BUNDLE_MEMBERS - names)
            extra_forbidden = sorted(name for name in names if Path(name).suffix.lower() in FORBIDDEN_BUNDLE_SUFFIXES)
            if missing:
                failures.append(f"{bundle_rel} is missing expected members: {missing}")
            if extra_forbidden:
                failures.append(f"{bundle_rel} contains nested raw/private or archive-like members: {extra_forbidden}")
            _validate_zip_manifest(archive, bundle_rel, failures)
            provenance = json.loads(archive.read("parameter_provenance.json").decode("utf-8"))
            if provenance.get("operation") != row.get("operation"):
                failures.append(f"{bundle_rel} operation does not match export manifest")
            if provenance.get("software_version") != "0.1.0":
                failures.append(f"{bundle_rel} parameter provenance has the wrong software version")
            if not provenance.get("effective_parameters"):
                failures.append(f"{bundle_rel} parameter provenance lacks effective parameters")
            input_schema = provenance.get("input_schema", {})
            if not isinstance(input_schema, dict) or not input_schema.get("required") or input_schema.get("kind") != row.get("input_schema_kind"):
                failures.append(f"{bundle_rel} parameter provenance lacks the expected input schema")
            grouping = provenance.get("grouping", {})
            if not isinstance(grouping, dict) or not grouping.get("observed_grouping_fields"):
                failures.append(f"{bundle_rel} parameter provenance lacks grouping fields")
            if "does not change the submitted measurements" not in str(provenance.get("interpretation_boundary", "")):
                failures.append(f"{bundle_rel} parameter provenance does not preserve the interpretation boundary")
            provenance_md = archive.read("parameter_provenance.md").decode("utf-8")
            for phrase in ["Input schema", "Grouping", "Effective parameters"]:
                if phrase not in provenance_md:
                    failures.append(f"{bundle_rel} parameter_provenance.md is missing section: {phrase}")
            result = json.loads(archive.read("result.json").decode("utf-8"))
            if result.get("status") != "pass":
                failures.append(f"{bundle_rel} result.json does not pass")
    return counts


def _rows_equal(actual: list[dict[str, str]], expected: list[dict[str, str]], label: str, failures: list[str]) -> bool:
    if actual != expected:
        failures.append(f"{label} does not match the Stage 7.8 runner constants")
        return False
    return True


def _validation_status(rel: str, failures: list[str]) -> None:
    path = ROOT / rel
    if path.suffix.lower() != ".json":
        return
    payload = _read_json(path, failures)
    if payload and payload.get("status") != "pass":
        failures.append(f"validation JSON does not pass: {rel}")


def _validate_stage7_8_crosswalks(failures: list[str]) -> dict[str, int]:
    runner = _load_stage7_8_runner()
    figure_rows = _read_tsv(STAGE7_8_DIR / "figure_artifact_crosswalk.tsv", failures)
    claim_rows = _read_tsv(STAGE7_8_DIR / "claim_evidence_crosswalk.tsv", failures)
    checklist_rows = _read_tsv(STAGE7_8_DIR / "methods_readiness_checklist.tsv", failures)
    limitation_rows = _read_tsv(STAGE7_8_DIR / "limitations_traceability.tsv", failures)
    _rows_equal(figure_rows, list(getattr(runner, "FIGURE_ROWS")), "figure_artifact_crosswalk.tsv", failures)
    _rows_equal(claim_rows, list(getattr(runner, "CLAIM_ROWS")), "claim_evidence_crosswalk.tsv", failures)
    _rows_equal(checklist_rows, list(getattr(runner, "CHECKLIST_ROWS")), "methods_readiness_checklist.tsv", failures)
    expected_limitations = [
        {
            "source": row["component"],
            "limitation_artifact": row["limitation_artifact"],
            "scope": row["scope"],
        }
        for row in getattr(runner, "FIGURE_ROWS")
    ]
    _rows_equal(limitation_rows, expected_limitations, "limitations_traceability.tsv", failures)
    for row in figure_rows:
        for column in ["primary_artifact", "supporting_artifacts", "validation_artifact", "limitation_artifact"]:
            for rel in _paths_from_cell(row.get(column, "")):
                if not (ROOT / rel).exists():
                    failures.append(f"Stage 7.8 figure row references a missing file: {row.get('component')} -> {rel}")
                if column == "validation_artifact":
                    _validation_status(rel, failures)
    for row in claim_rows:
        for column in ["evidence", "validation", "limitation"]:
            for rel in _paths_from_cell(row.get(column, "")):
                if not (ROOT / rel).exists():
                    failures.append(f"Stage 7.8 claim row references a missing file: {row.get('claim_id')} -> {rel}")
                if column == "validation":
                    _validation_status(rel, failures)
    return {"figure_rows": len(figure_rows), "claim_rows": len(claim_rows), "checklist_rows": len(checklist_rows)}


def _validate_release_coverage(failures: list[str]) -> dict[str, int]:
    checksum_rows = _read_csv(ROOT / "docs" / "release_checksums.csv", failures)
    archive_rows = _read_tsv(ROOT / "case_studies" / "stage7_methods_reproducibility" / "release_archive_manifest.tsv", failures)
    checksum_paths = {row.get("path", "") for row in checksum_rows}
    archive_paths = {row.get("path", "") for row in archive_rows}
    missing_checksums = sorted(REQUIRED_STAGE7_7_8_FILES - checksum_paths)
    missing_archive = sorted(REQUIRED_NONBINARY_ARCHIVE_FILES - archive_paths)
    if missing_checksums:
        failures.append(f"release checksum table does not cover Stage 7.7/7.8 files: {missing_checksums}")
    if missing_archive:
        failures.append(f"Stage 7.6 archive manifest does not cover non-binary Stage 7.7/7.8 files: {missing_archive}")
    for rel in REQUIRED_STAGE7_7_8_FILES:
        path = ROOT / rel
        if not path.exists():
            failures.append(f"required Stage 7.7/7.8 file is missing: {rel}")
        elif rel in checksum_paths:
            row = next(item for item in checksum_rows if item.get("path") == rel)
            if row.get("sha256") != _sha256(path):
                failures.append(f"release checksum is stale for {rel}")
    return {
        "release_checksum_rows": len(checksum_rows),
        "archive_manifest_rows": len(archive_rows),
        "required_stage7_7_8_files": len(REQUIRED_STAGE7_7_8_FILES),
    }


def _validate_phase9_boundary(failures: list[str]) -> dict[str, int]:
    stage9_files = []
    unauthorized = []
    for path in ROOT.rglob("*"):
        if ".git" in path.parts or not path.is_file():
            continue
        rel = path.relative_to(ROOT).as_posix()
        if re.search(r"(^|/)(stage9|phase9)[^/]*", rel, flags=re.IGNORECASE):
            stage9_files.append(rel)
            if not any(rel == prefix or rel.startswith(prefix) for prefix in ALLOWED_STAGE9_PREFIXES):
                unauthorized.append(rel)
    if unauthorized:
        failures.append(f"unauthorized Phase 9 implementation files are present: {unauthorized}")
    draft_files = sorted(rel for rel in FORBIDDEN_STAGE9_DRAFT_FILES if (ROOT / rel).exists())
    if draft_files:
        failures.append(f"Stage 9 manuscript drafting or evidence files were created before authorization: {draft_files}")
    if not STAGE9_CHECKER.exists():
        failures.append("Stage 9 scaffold checker is missing")
        checker_status = "missing"
    else:
        result = subprocess.run(
            [sys.executable, str(STAGE9_CHECKER)],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        checker_status = "pass" if result.returncode == 0 else "fail"
        if result.returncode != 0:
            failures.append(f"Stage 9 scaffold checker failed: {result.stdout.strip()} {result.stderr.strip()}".strip())
    memory = _read_json(ROOT / "docs" / "roadmap_execution_memory.json", failures)
    stages = {entry.get("stage"): entry for entry in memory.get("stage_lock", []) if isinstance(entry, dict)}
    stage9 = stages.get(9, {})
    if stage9.get("status") != "stage9_4_claim_freeze_registered":
        failures.append("roadmap execution memory must record Stage 9 as stage9_4_claim_freeze_registered")
    if stage9.get("substage_count") != 33:
        failures.append("Stage 9 execution memory must record 33 serialized substages")
    substage_ids = [entry.get("id") for entry in stage9.get("subphases", []) if isinstance(entry, dict)]
    if "9.6b" not in substage_ids:
        failures.append("Stage 9 execution memory must include the 9.6b PanelForge rendering substage")
    if stages.get(8, {}).get("status") != "conceptual_only":
        failures.append("Stage 8 must remain conceptual after Stage 7.7/7.8 hardening")
    current = memory.get("current_position", {}) if isinstance(memory.get("current_position", {}), dict) else {}
    if current.get("active_stage") != "Stage 9.4 claim freeze registered; manuscript production not started":
        failures.append("roadmap active stage must record the Stage 9.4 claim-freeze boundary")
    return {
        "authorized_phase9_scaffold_files": len(stage9_files) - len(unauthorized),
        "unauthorized_phase9_files": len(unauthorized),
        "unauthorized_stage9_draft_files": len(draft_files),
        "stage9_checker_status": checker_status,
    }


def _write_summary(report: dict[str, object]) -> None:
    counts = report.get("counts", {}) if isinstance(report.get("counts"), dict) else {}
    checks = report.get("checks", {}) if isinstance(report.get("checks"), dict) else {}
    lines = [
        "# Stage 7.7 and 7.8 recursive hardening",
        "",
        "This check verifies that the usability rehearsal and methods-readiness package remain release-consistent after Stage 7.6 clean-room hardening. It inspects exported analysis bundles, crosswalk tables, validation files, release checksums, and the clean-room archive manifest.",
        "",
        "## Result",
        "",
        f"- Status: `{report.get('status')}`.",
        f"- Completion state: `{report.get('completion_state')}`.",
        f"- Stage 7.7 bundles verified: `{counts.get('stage7_7_bundles', 0)}`.",
        f"- Stage 7.8 figure rows verified: `{counts.get('stage7_8_figure_rows', 0)}`.",
        "",
        "## Checks",
        "",
    ]
    for key, value in checks.items():
        lines.append(f"- `{key}`: `{value}`.")
    lines.extend(
        [
            "",
            "## Interpretation boundary",
            "",
            str(report.get("interpretation_boundary", "")),
        ]
    )
    DOC_SUMMARY.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def audit_stage7_7_8_recursive_hardening(root: Path = ROOT) -> dict[str, object]:
    del root
    failures: list[str] = []
    warnings: list[str] = []
    gate77_ok = _gate_pair_status(
        "docs/stage7_7_gate_report.json",
        "case_studies/stage7_usability_rehearsal/stage7_7_usability_gate_report.json",
        "complete_usability_adoption_rehearsal",
        failures,
    )
    gate78_ok = _gate_pair_status(
        "docs/stage7_8_gate_report.json",
        "case_studies/stage7_methods_readiness/stage7_8_methods_readiness_gate_report.json",
        "complete_methods_manuscript_readiness_package",
        failures,
    )
    bundle_counts = _validate_export_bundles(failures)
    crosswalk_counts = _validate_stage7_8_crosswalks(failures)
    coverage_counts = _validate_release_coverage(failures)
    phase9_counts = _validate_phase9_boundary(failures)
    checks = {
        "stage7_7_gate_pair_identical": "pass" if gate77_ok else "fail",
        "stage7_8_gate_pair_identical": "pass" if gate78_ok else "fail",
        "stage7_7_export_bundles_verified": "pass" if not any("bundle" in item or "parameter provenance" in item for item in failures) else "fail",
        "stage7_8_crosswalks_match_runner_constants": "pass" if not any("runner constants" in item for item in failures) else "fail",
        "stage7_8_evidence_paths_and_validation_status_pass": "pass" if not any("references a missing file" in item or "validation JSON does not pass" in item for item in failures) else "fail",
        "release_checksums_cover_stage7_7_8": "pass" if not any("release checksum" in item for item in failures) else "fail",
        "release_archive_manifest_covers_nonbinary_stage7_7_8": "pass" if not any("archive manifest does not cover" in item for item in failures) else "fail",
        "phase9_boundary_preserved": "pass" if not any("Phase 9" in item or "Stage 9" in item for item in failures) else "fail",
    }
    report = {
        "report_format": "rhodyn.stage7_7_8_recursive_hardening.v1",
        "status": "pass" if not failures else "fail",
        "completion_state": "stage7_7_8_recursively_hardened" if not failures else "stage7_7_8_recursive_hardening_failed",
        "checks": checks,
        "counts": {
            "stage7_7_bundles": bundle_counts["bundles"],
            "stage7_7_bundle_members": bundle_counts["members"],
            "stage7_8_figure_rows": crosswalk_counts["figure_rows"],
            "stage7_8_claim_rows": crosswalk_counts["claim_rows"],
            "stage7_8_checklist_rows": crosswalk_counts["checklist_rows"],
            **coverage_counts,
            **phase9_counts,
        },
        "failures": failures,
        "warnings": warnings,
        "interpretation_boundary": (
            "This recursive hardening verifies release consistency for Stage 7.7 usability and Stage 7.8 methods-readiness outputs. "
            "It does not add biological evidence or change method decisions. Phase 9 is limited to the authorized manuscript-assembly scaffold plus Stage 9.0 evidence lock, with no citation resolution, figure rendering, or manuscript drafting started."
        ),
    }
    return report


def main() -> int:
    report = audit_stage7_7_8_recursive_hardening()
    for path in [DOC_REPORT, CASE_REPORT]:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    _write_summary(report)
    print(json.dumps({"status": report["status"], "failures": report["failures"][:5]}, indent=2))
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())

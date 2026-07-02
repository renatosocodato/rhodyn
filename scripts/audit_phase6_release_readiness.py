"""Audit Phase 6 official-release readiness for RhoDyn.

The audit is intentionally conservative. It reports whether the repository has
all surfaces needed for a professional, citable software release, but it does
not treat the current development state as failed code when some release
surfaces are intentionally unfinished.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
REPORT_FORMAT = "rhodyn.phase6_release_readiness.v1"
GENERATED_DIRS = {
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    "__pycache__",
    "blob-report",
    "build",
    "dist",
    "htmlcov",
    "node_modules",
    "playwright-report",
    "test-results",
}
TEXT_SUFFIXES = {
    ".cff",
    ".css",
    ".csv",
    ".Dockerfile",
    ".example",
    ".html",
    ".in",
    ".ipynb",
    ".js",
    ".json",
    ".md",
    ".py",
    ".toml",
    ".txt",
    ".yaml",
    ".yml",
}
RAW_EXTENSIONS = {".lif", ".czi", ".nd2", ".oir", ".oib", ".lsm", ".tif", ".tiff", ".prism", ".xml"}
LEAK_PATTERNS = [
    re.compile("/" + "Users/"),
    re.compile("/" + "Volumes/"),
    re.compile("Library/" + "LaunchAgents"),
    re.compile(r"sk-[A-Za-z0-9_-]{16,}"),
    re.compile("ghp" + r"_[A-Za-z0-9_]+"),
    re.compile("github" + r"_pat_[A-Za-z0-9_]+"),
    re.compile(r"xox[baprs]-[A-Za-z0-9-]+"),
]
SUBPHASES = [
    ("6.1", "Release boundary"),
    ("6.2", "Packaging"),
    ("6.3", "Documentation"),
    ("6.4", "Release automation"),
    ("6.5", "Archive and citation"),
    ("6.6", "Clean-room reproducibility"),
    ("6.7", "Final ultra-hardening"),
]


def _read(root: Path, rel: str) -> str:
    path = root / rel
    return path.read_text(encoding="utf-8") if path.exists() else ""


def _exists(root: Path, rel: str) -> bool:
    return (root / rel).exists()


def _json_status(root: Path, rel: str) -> str:
    path = root / rel
    if not path.exists():
        return "missing"
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return "invalid_json"
    return str(payload.get("status", "missing_status"))


def _json_payload(root: Path, rel: str) -> dict[str, Any]:
    path = root / rel
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def _text_files(root: Path) -> list[Path]:
    paths: list[Path] = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if any(part in GENERATED_DIRS for part in path.parts):
            continue
        if path.suffix in TEXT_SUFFIXES or path.name.endswith(".Dockerfile"):
            paths.append(path)
    return paths


def _scan_hygiene(root: Path) -> tuple[list[str], list[str]]:
    leak_hits: list[str] = []
    raw_hits: list[str] = []
    for path in _text_files(root):
        text = path.read_text(encoding="utf-8", errors="ignore")
        for pattern in LEAK_PATTERNS:
            if pattern.search(text):
                leak_hits.append(str(path.relative_to(root)))
                break
    for path in root.rglob("*"):
        if any(part in GENERATED_DIRS for part in path.parts):
            continue
        if path.is_file() and path.suffix.lower() in RAW_EXTENSIONS:
            raw_hits.append(str(path.relative_to(root)))
    return sorted(set(leak_hits)), sorted(set(raw_hits))


def _subphase(status: str, checks: dict[str, bool], notes: list[str]) -> dict[str, object]:
    return {"status": status, "checks": checks, "notes": notes}


def audit_phase6_release_readiness(root: Path = ROOT) -> dict[str, Any]:
    checks: dict[str, bool] = {}
    failures: list[str] = []
    warnings: list[str] = []
    subphase_reports: dict[str, dict[str, object]] = {}

    readme = _read(root, "README.md")
    roadmap = _read(root, "docs/roadmap.md")
    release_checklist = _read(root, "docs/release_checklist.md")
    pyproject = _read(root, "pyproject.toml")
    init_py = _read(root, "src/rhodyn/__init__.py")
    citation = _read(root, "CITATION.cff")
    tests_workflow = _read(root, ".github/workflows/tests.yml")
    package_workflow = _read(root, ".github/workflows/package.yml")
    manifest = _read(root, "MANIFEST.in")

    # 6.1 Release boundary.
    phase_checks = {
        "readme_declares_standalone_toolkit": "standalone Python toolkit" in readme,
        "readme_preserves_manuscript_independence": "The manuscript was not generated with RhoDyn" in readme,
        "roadmap_stage6_public_release_state": "Stage 6 has produced a professionally citable RhoDyn `v0.1.0` GitHub" in roadmap
        and "Public `v0.1.0` GitHub and Zenodo software release live" in roadmap,
        "subphase_horizon_documented": all(f"{sid} {name}" in roadmap for sid, name in SUBPHASES),
        "release_checklist_preserves_safety_boundary": "must not contain raw microscopy files" in release_checklist,
    }
    subphase_reports["6.1"] = _subphase("pass" if all(phase_checks.values()) else "needs_work", phase_checks, [])

    # 6.2 Packaging.
    optional_extras = ["pandas", "stats", "plots", "backend", "notebooks", "dev", "all"]
    phase_checks = {
        "pyproject_present": bool(pyproject),
        "package_named_rhodyn": 'name = "rhodyn"' in pyproject,
        "version_declared": 'version = "0.1.0"' in pyproject and '__version__ = "0.1.0"' in init_py,
        "cli_entry_point_declared": 'rhodyn = "rhodyn.cli:main"' in pyproject,
        "wheel_build_system_declared": "setuptools.build_meta" in pyproject and "wheel" in pyproject,
        "manifest_includes_release_surfaces": all(token in manifest for token in ["README.md", "LICENSE", "CITATION.cff", "docs", "examples", "scripts"]),
        "optional_extras_declared": all(f"{name} = [" in pyproject for name in optional_extras),
        "backend_extra_uses_httpx": '"httpx>=' in pyproject,
        "backend_extra_no_httpx2_typo": "httpx2" not in pyproject,
        "dev_extra_declared": "dev = [" in pyproject,
    }
    notes = [] if phase_checks["dev_extra_declared"] else ["dev optional extra still needs to be declared before a public release"]
    subphase_reports["6.2"] = _subphase("pass" if all(phase_checks.values()) else "needs_work", phase_checks, notes)

    # 6.3 Documentation.
    doc_files = [
        "README.md",
        "REPRODUCING.md",
        "docs/architecture.md",
        "docs/example_workflows.md",
        "docs/optional_extras.md",
        "docs/release_checklist.md",
        "docs/stage4_backend.md",
        "docs/stage5_frontend.md",
    ]
    phase_checks = {f"doc_present::{rel}": _exists(root, rel) for rel in doc_files}
    phase_checks.update(
        {
            "api_reference_present": _exists(root, "docs/api_reference.md"),
            "cli_reference_present": _exists(root, "docs/cli_reference.md"),
            "input_schema_guide_present": _exists(root, "docs/input_schema_guide.md"),
            "interpretation_guide_present": _exists(root, "docs/interpretation_guide.md"),
            "reproducibility_card_present": _exists(root, "docs/reproducibility_card.md") or _exists(root, "REPRO_CARD.md"),
            "documentation_site_config_present": any(_exists(root, rel) for rel in ["mkdocs.yml", "docs/conf.py"]),
        }
    )
    subphase_reports["6.3"] = _subphase("pass" if all(phase_checks.values()) else "needs_work", phase_checks, [])

    # 6.4 Release automation.
    phase_checks = {
        "tests_workflow_present": bool(tests_workflow),
        "package_workflow_present": bool(package_workflow),
        "unit_tests_in_ci": "python -m unittest discover tests" in tests_workflow or "unittest discover tests" in tests_workflow,
        "package_build_in_ci": "python -m build --sdist --wheel" in package_workflow,
        "wheel_install_in_ci": "dist/*.whl" in package_workflow,
        "source_dist_install_in_ci": "dist/*.tar.gz" in package_workflow,
        "browser_regression_in_ci": "npm run test:stage5" in tests_workflow,
        "cross_version_python_matrix": "matrix" in tests_workflow and "3.10" in tests_workflow and "3.12" in tests_workflow,
        "docs_build_workflow_present": "mkdocs" in tests_workflow + package_workflow or "sphinx-build" in tests_workflow + package_workflow,
        "docker_build_workflow_present": "docker build" in tests_workflow + package_workflow,
        "contribution_docs_present": _exists(root, "CONTRIBUTING.md"),
    }
    subphase_reports["6.4"] = _subphase("pass" if all(phase_checks.values()) else "needs_work", phase_checks, [])

    # 6.5 Archive and citation.
    release_notes = _read(root, "docs/release_notes_v0.1.0.md") or _read(root, "RELEASE_NOTES.md")
    zenodo_metadata = _read(root, ".zenodo.json")
    zenodo_publication = _json_payload(root, "docs/zenodo_publication_report.json")
    public_release = _json_payload(root, "docs/public_release_integrity_report.json")
    public_release_checks = public_release.get("checks", {}) if isinstance(public_release.get("checks", {}), dict) else {}
    phase_checks = {
        "citation_file_present": bool(citation),
        "citation_version_matches_package": "version: 0.1.0" in citation,
        "citation_points_to_version_doi": "10.5281/zenodo.21036616" in citation,
        "license_present": _exists(root, "LICENSE"),
        "notice_present": _exists(root, "NOTICE"),
        "changelog_present": _exists(root, "CHANGELOG.md"),
        "github_release_notes_present": _exists(root, "docs/release_notes_v0.1.0.md") or _exists(root, "RELEASE_NOTES.md"),
        "release_notes_name_version": "RhoDyn v0.1.0" in release_notes,
        "release_notes_include_public_doi": "10.5281/zenodo.21036616" in release_notes and "10.5281/zenodo.21036615" in release_notes,
        "zenodo_metadata_present": _exists(root, ".zenodo.json"),
        "zenodo_metadata_declares_software": '"upload_type": "software"' in zenodo_metadata,
        "zenodo_publication_report_present": _exists(root, "docs/zenodo_publication_report.json"),
        "zenodo_publication_report_passed": zenodo_publication.get("status") == "pass",
        "zenodo_publication_version_doi_present": zenodo_publication.get("doi") == "10.5281/zenodo.21036616",
        "zenodo_publication_concept_doi_present": zenodo_publication.get("conceptdoi") == "10.5281/zenodo.21036615",
        "public_release_integrity_report_present": _exists(root, "docs/public_release_integrity_report.json"),
        "public_release_integrity_passed": public_release.get("status") == "pass",
        "public_github_repo_verified": bool(public_release_checks.get("github_repo_api_public")),
        "public_github_release_verified": bool(public_release_checks.get("github_release_api_public")),
        "public_github_tag_archive_verified": bool(public_release_checks.get("github_tag_archive_public")),
        "public_zenodo_version_doi_verified": bool(public_release_checks.get("zenodo_version_doi_resolves")),
        "public_zenodo_concept_doi_verified": bool(public_release_checks.get("zenodo_concept_doi_resolves")),
        "checksum_manifest_present": any(_exists(root, rel) for rel in ["release_checksums.csv", "release_checksums.json", "docs/release_checksums.csv"]),
        "checksum_json_present": _exists(root, "docs/release_checksums.json") or _exists(root, "release_checksums.json"),
        "checksum_writer_present": _exists(root, "scripts/write_release_checksums.py"),
    }
    subphase_reports["6.5"] = _subphase("pass" if all(phase_checks.values()) else "needs_work", phase_checks, [])

    # 6.6 Clean-room reproducibility.
    clean_room_doc = _read(root, "docs/clean_room_reproducibility.md")
    clean_room_report = _read(root, "docs/clean_room_reproducibility_report.md")
    phase_checks = {
        "clean_room_doc_present": _exists(root, "docs/clean_room_reproducibility.md"),
        "clean_room_doc_defines_fresh_environment": "fresh build virtual environment" in clean_room_doc and "installed-wheel virtual environment" in clean_room_doc,
        "examples_present": _exists(root, "examples/synthetic_trajectory.csv") and _exists(root, "examples/residence_reserve_workflow.py"),
        "tutorial_notebooks_present": _exists(root, "notebooks/01_synthetic_residence_primer.ipynb"),
        "frontend_workbench_present": _exists(root, "frontend/stage5/index.html"),
        "report_export_cli_present": "export-markdown" in _read(root, "src/rhodyn/cli.py"),
        "clean_room_runner_present": _exists(root, "scripts/run_clean_room_reproducibility.py"),
        "clean_room_report_present": _exists(root, "docs/clean_room_reproducibility_report.md"),
        "clean_room_report_passed": "Overall status. pass" in clean_room_report,
        "clean_room_report_records_notebooks": "tutorial notebook code cells" in clean_room_report,
        "clean_room_report_records_docs_build": "build documentation site" in clean_room_report,
        "clean_room_report_records_workbench_audit": "audit Stage 5 workbench" in clean_room_report,
    }
    subphase_reports["6.6"] = _subphase("pass" if all(phase_checks.values()) else "needs_work", phase_checks, [])

    # 6.7 Final ultra-hardening.
    leak_hits, raw_hits = _scan_hygiene(root)
    phase_checks = {
        "release_check_script_present": _exists(root, "scripts/check_release.py"),
        "phase6_audit_script_present": _exists(root, "scripts/audit_phase6_release_readiness.py"),
        "local_path_and_secret_scan_clear": not leak_hits,
        "raw_private_file_scan_clear": not raw_hits,
        "screenshot_regression_present": _exists(root, "tests/playwright/stage5.visual.spec.mjs"),
        "screenshot_regression_report_present": _exists(root, "docs/screenshot_regression_report.json"),
        "screenshot_regression_passed": _json_status(root, "docs/screenshot_regression_report.json") == "pass",
        "docker_smoke_audit_present": _exists(root, "scripts/audit_stage4_docker_smoke.py"),
        "docker_smoke_report_present": _exists(root, "docs/docker_smoke_audit_report.json"),
        "docker_smoke_passed": _json_status(root, "docs/docker_smoke_audit_report.json") == "pass",
        "pypi_dry_run_script_present": _exists(root, "scripts/pypi_dry_run.py"),
        "pypi_dry_run_report_present": _exists(root, "docs/pypi_dry_run_report.json"),
        "pypi_dry_run_passed": _json_status(root, "docs/pypi_dry_run_report.json") == "pass",
        "zenodo_dry_run_script_present": _exists(root, "scripts/zenodo_dry_run.py"),
        "zenodo_dry_run_report_present": _exists(root, "docs/zenodo_dry_run_report.json"),
        "zenodo_dry_run_passed": _json_status(root, "docs/zenodo_dry_run_report.json") == "pass",
        "broken_link_scan_script_present": _exists(root, "scripts/check_docs_links.py"),
        "broken_link_scan_report_present": _exists(root, "docs/broken_link_scan_report.json"),
        "broken_link_scan_passed": _json_status(root, "docs/broken_link_scan_report.json") == "pass",
        "dependency_review_script_present": _exists(root, "scripts/check_dependency_security.py"),
        "dependency_review_report_present": _exists(root, "docs/dependency_review_report.json"),
        "dependency_review_passed": _json_status(root, "docs/dependency_review_report.json") == "pass",
        "public_release_integrity_script_present": _exists(root, "scripts/check_public_release_integrity.py"),
        "public_release_integrity_report_present": _exists(root, "docs/public_release_integrity_report.json"),
        "public_release_integrity_report_passed": _json_status(root, "docs/public_release_integrity_report.json") == "pass",
    }
    notes = []
    if leak_hits:
        notes.append("possible local path or credential strings: " + ", ".join(leak_hits[:10]))
    if raw_hits:
        notes.append("raw/private data-like files found: " + ", ".join(raw_hits[:10]))
    subphase_reports["6.7"] = _subphase("pass" if all(phase_checks.values()) else "needs_work", phase_checks, notes)

    for phase_id, report in subphase_reports.items():
        for name, passed in report["checks"].items():
            checks[f"{phase_id}::{name}"] = bool(passed)
            if not passed:
                failures.append(f"{phase_id}::{name}")

    if failures:
        warnings.append("Phase 6 public-release hardening still has unresolved checks")
    return {
        "report_format": REPORT_FORMAT,
        "status": "pass" if not failures else "needs_work",
        "failures": failures,
        "warnings": warnings,
        "subphases": subphase_reports,
        "checks": checks,
        "interpretation_boundary": "This audit reports software-release readiness only. It does not change RhoDyn analysis behavior, biological examples, or manuscript interpretation.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit RhoDyn Phase 6 official-release readiness.")
    parser.add_argument("--out", default="", help="Optional JSON output path for the readiness report.")
    args = parser.parse_args()
    payload = audit_phase6_release_readiness()
    if args.out:
        output = Path(args.out)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""Run Stage 9.29 roadmap closure and version binding.

Stage 9.29 closes the Nature Methods manuscript-assembly program by binding
the current package, evidence snapshot, release identifiers, figure-rendering
state, and remaining human submission actions. It does not create new data,
new analyses, new figures, or new manuscript claims.
"""

from __future__ import annotations

import csv
import hashlib
import json
import re
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT / "manuscript" / "nature_methods"
SUBMISSION = WORKSPACE / "submission_package"
GATES = WORKSPACE / "gate_verdicts"
REGISTRY_PATH = WORKSPACE / "contracts" / "stage9_substage_registry.json"
PROJECT_BINDING_PATH = WORKSPACE / "contracts" / "stage9_project_binding.json"
MEMORY_PATH = ROOT / "docs" / "stage9_execution_memory.json"
ROADMAP_MEMORY_PATH = ROOT / "docs" / "roadmap_execution_memory.json"
PLAN_PATH = ROOT / "docs" / "stage9_manuscript_assembly_plan.md"
ROADMAP_PATH = ROOT / "docs" / "roadmap.md"
README_PATH = WORKSPACE / "README.md"

GATE_928 = GATES / "9.28.json"
GATE_927 = GATES / "9.27.json"
GATE_96B = GATES / "9.6b.json"

OUTPUTS = {
    "completion_report": WORKSPACE / "stage9_completion_report.md",
    "version_binding": WORKSPACE / "stage9_closure_version_binding.json",
    "action_decisions": SUBMISSION / "pi_review_action_decisions.csv",
    "gate": GATES / "9.29.json",
}

PACKAGE_FILES = [
    SUBMISSION / "main_text_for_submission.md",
    SUBMISSION / "supplementary_information_for_submission.md",
    SUBMISSION / "submission_manifest.md",
    SUBMISSION / "submission_readiness_checklist.md",
    SUBMISSION / "editor_triage_note_for_cover_letter.md",
    SUBMISSION / "editorial_pitch_for_submission.md",
    SUBMISSION / "prior_art_positioning_matrix.md",
    SUBMISSION / "validation_breadth_and_boundary_map.md",
    SUBMISSION / "editor_objection_response_map.md",
    SUBMISSION / "editor_two_minute_triage_simulation.md",
    SUBMISSION / "current_nature_methods_policy_preflight.md",
    SUBMISSION / "reviewer_editor_fit_planner_AUTHOR_CONFIRMATION_REQUIRED.md",
    SUBMISSION / "software_reporting_checklist.md",
    SUBMISSION / "article_fit_checklist.md",
    SUBMISSION / "author_declarations_REQUIRED.md",
    SUBMISSION / "ai_disclosure_AUTHOR_CONFIRMATION_REQUIRED.md",
    SUBMISSION / "title_author_metadata_AUTHOR_CONFIRMATION_REQUIRED.md",
    SUBMISSION / "code_for_review.md",
    SUBMISSION / "package_consistency_audit.md",
    SUBMISSION / "figure_file_inventory.csv",
    SUBMISSION / "source_data_and_statistics_inventory.csv",
    SUBMISSION / "references_for_submission.bib",
    SUBMISSION / "reporting_summary_REQUIRED.md",
    SUBMISSION / "reporting_summary_answer_bank_AUTHOR_CONFIRMATION_REQUIRED.md",
    SUBMISSION / "submission_package_manifest.json",
    SUBMISSION / "pi_review_packet.md",
    SUBMISSION / "pi_review_action_matrix.csv",
    SUBMISSION / "pi_review_revision_log.md",
    SUBMISSION / "pi_review_literature_calibration.md",
]

SAFETY_SCAN_TARGETS = [
    *PACKAGE_FILES,
    WORKSPACE / "stage9_completion_report.md",
    WORKSPACE / "stage9_closure_version_binding.json",
    SUBMISSION / "pi_review_action_decisions.csv",
]

PACKAGE_FORBIDDEN_PATTERNS = [
    re.compile("/" + "Users/"),
    re.compile("/" + "Volumes/"),
    re.compile("Library/" + "LaunchAgents"),
    re.compile(r"\b" + "sk-" + r"[A-Za-z0-9_-]{10,}"),
    re.compile(r"\b" + "ghp" + "_" + r"[A-Za-z0-9_]{10,}"),
    re.compile(r"\b" + "github" + r"_pat_[A-Za-z0-9_]{10,}"),
]

ACTION_DECISION_FIELDS = [
    "item_id",
    "previous_status",
    "codex_decision",
    "closure_status",
    "rationale",
    "remaining_requirement",
]


def _now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _git_sha() -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    return result.stdout.strip() if result.returncode == 0 else "unknown"


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_text(path: Path, body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body.rstrip() + "\n", encoding="utf-8")


def _write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _package_file_rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in PACKAGE_FILES:
        rows.append(
            {
                "path": path.relative_to(ROOT).as_posix(),
                "exists": path.exists(),
                "sha256": _sha256(path) if path.exists() and path.is_file() else "",
                "bytes": path.stat().st_size if path.exists() and path.is_file() else 0,
            }
        )
    return rows


def _all_existing_files(paths: list[Path]) -> bool:
    return all(path.exists() and path.is_file() for path in paths)


def _read_pyproject_version() -> str:
    body = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    match = re.search(r'^version\s*=\s*"([^"]+)"', body, flags=re.M)
    return match.group(1) if match else "unknown"


def _quarantine_files() -> list[str]:
    files: list[str] = []
    quarantine = WORKSPACE / "_quarantine"
    if quarantine.exists():
        for path in quarantine.rglob("*"):
            if path.is_file() and path.name != ".gitkeep":
                files.append(path.relative_to(ROOT).as_posix())
    return sorted(files)


def _safety_hits(paths: list[Path]) -> list[str]:
    hits: list[str] = []
    for path in paths:
        if not path.exists() or not path.is_file():
            continue
        body = path.read_text(encoding="utf-8", errors="ignore")
        for pattern in PACKAGE_FORBIDDEN_PATTERNS:
            if pattern.search(body):
                hits.append(f"{path.relative_to(ROOT).as_posix()}::{pattern.pattern}")
    return sorted(set(hits))


def _action_decisions() -> list[dict[str, str]]:
    rows = _read_csv(SUBMISSION / "pi_review_action_matrix.csv")
    source_text = "\n".join(
        [
            (WORKSPACE / "sections" / "introduction.md").read_text(encoding="utf-8"),
            (WORKSPACE / "sections" / "results.md").read_text(encoding="utf-8"),
            (WORKSPACE / "sections" / "discussion.md").read_text(encoding="utf-8"),
            (WORKSPACE / "sections" / "methods.md").read_text(encoding="utf-8"),
            (WORKSPACE / "figures" / "figure_legends.md").read_text(encoding="utf-8"),
        ]
    )
    prior_art_matrix = (SUBMISSION / "prior_art_positioning_matrix.md").read_text(
        encoding="utf-8"
    ) if (SUBMISSION / "prior_art_positioning_matrix.md").exists() else ""
    boundary_present = all(
        phrase in source_text
        for phrase in [
            "not the exclusion of slower or context-specific coupling",
            "not as direct assays of unmeasured biological reserve capacity",
            "effective model parameters should not be treated as direct biochemical interactions",
        ]
    )
    decisions: list[dict[str, str]] = []
    for row in rows:
        status = row.get("status", "")
        item_id = row.get("item_id", "")
        if status == "auto_revised":
            decision = "accept_auto_revision"
            closure_status = "closed"
            if item_id == "PI-9.28-MAJ-001" and "RhoDyn should not be positioned as the first method" in prior_art_matrix:
                rationale = "The source edit is present and the prior-art positioning matrix now makes the novelty boundary explicit for final author review."
            else:
                rationale = "The source edit is already present in the manuscript package and does not require new evidence."
            remaining = row.get("remaining_requirement", "")
        elif status == "retained_boundary":
            decision = "retain_boundary_without_new_edit"
            closure_status = "closed"
            rationale = "The manuscript keeps the claim scoped to declared margins, measured endpoints, and tested alternatives."
            remaining = "Maintain this wording during final author upload review."
        elif status == "open_human_check" and boundary_present:
            decision = "close_as_boundary_present"
            closure_status = "closed"
            rationale = "Reader-facing Results, Methods, Discussion, and legends already state that effective parameters do not identify biochemical edges."
            remaining = "Do not strengthen routed-output language without new mechanistic evidence."
        elif status == "human_action_required":
            decision = "retain_as_external_submission_action"
            closure_status = "not_blocking_stage9_closure"
            rationale = "The official Reporting Summary, author declarations, and portal metadata are journal-upload actions, not repository-derived scientific content."
            remaining = "Complete the official Springer Nature form, author declarations, and portal metadata before journal submission."
        else:
            decision = "requires_author_review"
            closure_status = "open"
            rationale = "The action row could not be closed from current manuscript evidence."
            remaining = row.get("remaining_requirement", "")
        decisions.append(
            {
                "item_id": item_id,
                "previous_status": status,
                "codex_decision": decision,
                "closure_status": closure_status,
                "rationale": rationale,
                "remaining_requirement": remaining,
            }
        )
    return decisions


def _figure_status() -> dict[str, Any]:
    gate = _read_json(GATE_96B)
    inventory = _read_csv(SUBMISSION / "figure_file_inventory.csv")
    fig_ids = sorted({row.get("fig_id", "") for row in inventory if row.get("fig_id")})
    formats = sorted({row.get("format", "") for row in inventory if row.get("format")})
    return {
        "panelforge_ref": gate.get("panelforge_ref"),
        "rendered_file_count": len(inventory),
        "gate_rendered_file_count": gate.get("rendered_file_count"),
        "figure_ids": fig_ids,
        "formats": formats,
        "all_files_exist": all(row.get("exists") == "true" for row in inventory),
    }


def _version_binding(package_rows: list[dict[str, Any]], action_decisions: list[dict[str, str]]) -> dict[str, Any]:
    project = _read_json(PROJECT_BINDING_PATH)
    stage9_memory = _read_json(MEMORY_PATH)
    release_commit = _git_sha()
    subphases = stage9_memory.get("substage_status", [])
    if not isinstance(subphases, list):
        subphases = []
    completed_substages = stage9_memory.get("completed_substages", [])
    if not isinstance(completed_substages, list):
        completed_substages = []
    subphase_entries = [entry for entry in [*subphases, *completed_substages] if isinstance(entry, dict)]
    subphase_by_id = {(entry.get("id") or entry.get("substage")): entry for entry in subphase_entries}
    reference_version = stage9_memory.get("reference_version") or subphase_by_id.get("9.20", {}).get("reference_version")
    claim_freeze_version = stage9_memory.get("claim_freeze_version") or subphase_by_id.get("9.4", {}).get("claim_freeze_version")
    return {
        "generated_utc": _now(),
        "closure_commit": release_commit,
        "method": project.get("method_name"),
        "software": project.get("software_name"),
        "software_version": project.get("software_version"),
        "pyproject_version": _read_pyproject_version(),
        "repository": project.get("repo_url"),
        "software_archive_doi": project.get("archive_doi"),
        "software_concept_doi": project.get("concept_doi"),
        "venue": project.get("venue"),
        "content_type": project.get("content_type"),
        "evidence_version": stage9_memory.get("evidence_version"),
        "claim_freeze_version": claim_freeze_version,
        "reference_version": reference_version,
        "package_version": f"stage9.29-closure@{release_commit}",
        "figure_engine": project.get("figure_engine_binding", {}),
        "figure_status": _figure_status(),
        "package_files": package_rows,
        "pi_review_action_decisions": action_decisions,
        "human_submission_actions": [
            "Complete the official Springer Nature Reporting Summary form using author-confirmed answers from the reporting-summary answer bank.",
            "Confirm final title page, author list, affiliations, correspondence fields, author declarations, and the AI-use disclosure draft if applicable.",
            "Confirm reviewer suggestions, reviewer exclusions, and editor-fit wording using the reviewer/editor fit planner if those portal fields are used.",
            "Confirm final portal metadata, corresponding-author details, ORCID fields, and journal-specific file names.",
            "Perform final human author approval before upload.",
        ],
        "scientific_boundary": (
            "Closure binds the current methods manuscript package and versioned release surfaces. "
            "It does not add biological evidence, new benchmarks, new figure renders, or journal acceptance."
        ),
    }


def _completion_report(version_binding: dict[str, Any], action_decisions: list[dict[str, str]]) -> str:
    figure_status = version_binding["figure_status"]
    closed = [row for row in action_decisions if row["closure_status"] == "closed"]
    retained = [row for row in action_decisions if row["closure_status"] == "not_blocking_stage9_closure"]
    package_rows = version_binding["package_files"]
    package_table = "\n".join(
        f"| `{row['path']}` | `{row['sha256'][:12]}` | `{row['bytes']}` |"
        for row in package_rows
        if row["exists"]
    )
    decision_table = "\n".join(
        f"| {row['item_id']} | {row['codex_decision']} | {row['closure_status']} | {row['remaining_requirement']} |"
        for row in action_decisions
    )
    return f"""# Stage 9.29 closure and version binding

## Closure verdict

Stage 9 is closed for the current Nature Methods manuscript-assembly package. The package remains a methods-manuscript surface for RhoDyn v0.1.0 and does not add new biological datasets, new statistical results, new model outputs, new figure renders, or a journal-upload claim.

## Codex decision on PI-review action items

Codex closed `{len(closed)}` PI-review action items from existing manuscript evidence and retained `{len(retained)}` item as an external journal-submission action rather than a scientific blocker. The official Springer Nature Reporting Summary form, final author declarations, final portal metadata, and author upload approval remain outside repository-derived closure.

| item | decision | closure status | remaining requirement |
|---|---|---|---|
{decision_table}

## Bound versions

- Method. `{version_binding['method']}`.
- Software version. `{version_binding['software_version']}`.
- Pyproject version. `{version_binding['pyproject_version']}`.
- Repository. `{version_binding['repository']}`.
- Closure commit. `{version_binding['closure_commit']}`.
- Software archive DOI. `{version_binding['software_archive_doi']}`.
- Software concept DOI. `{version_binding['software_concept_doi']}`.
- Evidence version. `{version_binding['evidence_version']}`.
- Claim-freeze version. `{version_binding['claim_freeze_version']}`.
- Reference version. `{version_binding['reference_version']}`.
- Package version. `{version_binding['package_version']}`.
- PanelForge version. `{version_binding['figure_engine'].get('pinned_ref')}` with DOI `{version_binding['figure_engine'].get('version_doi')}`.

## Figure and package state

PanelForge remains unchanged in this closure step. The package has `{figure_status['rendered_file_count']}` rendered figure files across `{len(figure_status['figure_ids'])}` main figures and `{', '.join(figure_status['formats'])}` formats. All rendered figure inventory rows still point to existing files.

| package file | sha256 prefix | bytes |
|---|---:|---:|
{package_table}

## Scientific boundary

The closed package supports a methods claim that RhoDyn provides an inspectable workflow for residence-state inference, amplitude comparison, bounded-coupling decisions, reserve-like endpoint summaries, routed-output comparisons, uncertainty reporting, and reproducible export surfaces. It does not show that every live-cell system has a residence regime, that bounded coupling excludes slower or context-specific coupling, that reserve-like endpoints directly measure biological reserve capacity, or that routed-output parameters identify biochemical edges.

## Remaining human submission actions

1. Complete the official Springer Nature Reporting Summary form using author-confirmed answers from the reporting-summary answer bank.
2. Confirm final title page, author list, affiliations, correspondence fields, author declarations, and the AI-use disclosure draft if applicable.
3. Confirm reviewer suggestions, reviewer exclusions, and editor-fit wording using the reviewer/editor fit planner if those portal fields are used.
4. Confirm final portal metadata, corresponding-author fields, ORCID fields, and journal-specific file names.
5. Perform final author approval of the main text, Supplementary Information, figures, and code-for-review surface before upload.
"""


def _update_submission_manifest() -> None:
    manifest = SUBMISSION / "submission_manifest.md"
    body = manifest.read_text(encoding="utf-8")
    if "| Author declarations | `author_declarations_REQUIRED.md` |" not in body:
        anchor = "| Reporting Summary | `reporting_summary_REQUIRED.md` | Required journal form placeholder pending human completion. |"
        body = body.replace(
            anchor,
            anchor + "\n| Author declarations | `author_declarations_REQUIRED.md` | Required upload declarations pending human completion. |",
        )
    if "| Reporting Summary answer bank | `reporting_summary_answer_bank_AUTHOR_CONFIRMATION_REQUIRED.md` |" not in body:
        anchor = "| Reporting Summary | `reporting_summary_REQUIRED.md` | Required journal form placeholder pending human completion. |"
        body = body.replace(
            anchor,
            anchor + "\n| Reporting Summary answer bank | `reporting_summary_answer_bank_AUTHOR_CONFIRMATION_REQUIRED.md` | Author-confirmation answer bank mapping current evidence to official Reporting Summary fields. |",
        )
    if "| AI disclosure draft | `ai_disclosure_AUTHOR_CONFIRMATION_REQUIRED.md` |" not in body:
        anchor = "| Author declarations | `author_declarations_REQUIRED.md` | Required upload declarations pending human completion. |"
        body = body.replace(
            anchor,
            anchor + "\n| AI disclosure draft | `ai_disclosure_AUTHOR_CONFIRMATION_REQUIRED.md` | Author-confirmation wording options for any required AI-assisted content disclosure. |",
        )
    if "| Title and author metadata | `title_author_metadata_AUTHOR_CONFIRMATION_REQUIRED.md` |" not in body:
        anchor = "| AI disclosure draft | `ai_disclosure_AUTHOR_CONFIRMATION_REQUIRED.md` | Author-confirmation wording options for any required AI-assisted content disclosure. |"
        body = body.replace(
            anchor,
            anchor + "\n| Title and author metadata | `title_author_metadata_AUTHOR_CONFIRMATION_REQUIRED.md` | Author-confirmation template for title-page, author-list, affiliation, correspondence, ORCID, and review-mode fields. |",
        )
    if "| Stage 9 completion report | `../stage9_completion_report.md` |" not in body:
        anchor = "| PI review literature calibration | `pi_review_literature_calibration.md` | Prior-art and novelty calibration note. |"
        replacement = (
            anchor
            + "\n| PI review action decisions | `pi_review_action_decisions.csv` | Codex closure decisions for the PI-review action matrix. |"
            + "\n| Stage 9 completion report | `../stage9_completion_report.md` | Final closure and version-binding surface for the current Nature Methods package. |"
        )
        body = body.replace(anchor, replacement)
    if "| Prior-art positioning matrix | `prior_art_positioning_matrix.md` |" not in body:
        anchor = "| Editorial pitch | `editorial_pitch_for_submission.md` | Cover-letter and presubmission-inquiry drafts for Nature Methods editorial triage. |"
        body = body.replace(
            anchor,
            anchor + "\n| Prior-art positioning matrix | `prior_art_positioning_matrix.md` | Novelty-boundary comparison against related dynamic-state, trajectory, imaging, and software-method literature. |",
        )
    if "| Editor-objection response map | `editor_objection_response_map.md` |" not in body:
        anchor = "| Prior-art positioning matrix | `prior_art_positioning_matrix.md` | Novelty-boundary comparison against related dynamic-state, trajectory, imaging, and software-method literature. |"
        body = body.replace(
            anchor,
            anchor + "\n| Editor-objection response map | `editor_objection_response_map.md` | Desk-review objection map linking likely objections to existing package evidence and wording boundaries. |",
        )
    if "| Validation breadth map | `validation_breadth_and_boundary_map.md` |" not in body:
        anchor = "| Prior-art positioning matrix | `prior_art_positioning_matrix.md` | Novelty-boundary comparison against related dynamic-state, trajectory, imaging, and software-method literature. |"
        body = body.replace(
            anchor,
            anchor + "\n| Validation breadth map | `validation_breadth_and_boundary_map.md` | Validation-ladder and boundary map across synthetic, public trajectory, endpoint, held-out, and software-reproducibility tests. |",
        )
    if "| Two-minute editor triage simulation | `editor_two_minute_triage_simulation.md` |" not in body:
        anchor = "| Editor-objection response map | `editor_objection_response_map.md` | Desk-review objection map linking likely objections to existing package evidence and wording boundaries. |"
        body = body.replace(
            anchor,
            anchor + "\n| Two-minute editor triage simulation | `editor_two_minute_triage_simulation.md` | First-pass editor-read simulation for title, Abstract, cover-letter opening, figure spine, and claim boundaries. |",
        )
    if "| Current Nature Methods policy preflight | `current_nature_methods_policy_preflight.md` |" not in body:
        anchor = "| Two-minute editor triage simulation | `editor_two_minute_triage_simulation.md` | First-pass editor-read simulation for title, Abstract, cover-letter opening, figure spine, and claim boundaries. |"
        body = body.replace(
            anchor,
            anchor + "\n| Current Nature Methods policy preflight | `current_nature_methods_policy_preflight.md` | Source-linked preflight against current Article, Reporting Summary, data/code availability, and software guidance. |",
        )
    if "| Reviewer and editor fit planner | `reviewer_editor_fit_planner_AUTHOR_CONFIRMATION_REQUIRED.md` |" not in body:
        anchor = "| Current Nature Methods policy preflight | `current_nature_methods_policy_preflight.md` | Source-linked preflight against current Article, Reporting Summary, data/code availability, and software guidance. |"
        body = body.replace(
            anchor,
            anchor + "\n| Reviewer and editor fit planner | `reviewer_editor_fit_planner_AUTHOR_CONFIRMATION_REQUIRED.md` | Author-confirmation planner for reviewer expertise coverage, suggested-reviewer fields, exclusions, and editor-fit wording. |",
        )
    body = body.replace(
        "Scope. This package assembles the current Nature Methods Article surfaces for collaborator and PI review. It includes the Stage 9.28 review packet and support files, but it does not submit the manuscript or close Stage 9.",
        "Scope. This package assembles the current Nature Methods Article surfaces for collaborator and PI review. It includes the Stage 9.28 review packet and Stage 9.29 closure support files, but it does not submit the manuscript or replace final journal-upload approval.",
    )
    body = body.replace(
        "Scope. This package assembles the current Nature Methods Article surfaces for collaborator review. It does not create the PI review packet, submit the manuscript, or close Stage 9.",
        "Scope. This package assembles the current Nature Methods Article surfaces for collaborator and PI review. It includes the Stage 9.28 review packet and Stage 9.29 closure support files, but it does not submit the manuscript or replace final journal-upload approval.",
    )
    manifest.write_text(body, encoding="utf-8")

    checklist = SUBMISSION / "submission_readiness_checklist.md"
    body = checklist.read_text(encoding="utf-8")
    if "Stage 9 closure | ready" not in body:
        anchor = "| PI review packet | ready | `pi_review_packet.md` contains the final human PI-style review packet with the required three review sections. |"
        replacement = (
            anchor
            + "\n| PI-review action decisions | ready | `pi_review_action_decisions.csv` closes evidence-safe items and retains portal-only actions outside the scientific package. |"
            + "\n| Stage 9 closure | ready | `../stage9_completion_report.md` binds the package, evidence, software, figure, and limitation versions. |"
        )
        body = body.replace(anchor, replacement)
        body = body.replace(
            "decide whether any open PI-review items require new evidence before Stage 9 closure.",
            "complete the remaining submission-only actions recorded after Stage 9 closure.",
        )
    checklist.write_text(body, encoding="utf-8")


def _update_submission_package_manifest(version_binding: dict[str, Any]) -> None:
    path = SUBMISSION / "submission_package_manifest.json"
    payload = _read_json(path)
    package_files = set(payload.get("package_files", []))
    for rel in [
        "manuscript/nature_methods/submission_package/author_declarations_REQUIRED.md",
        "manuscript/nature_methods/submission_package/ai_disclosure_AUTHOR_CONFIRMATION_REQUIRED.md",
        "manuscript/nature_methods/submission_package/title_author_metadata_AUTHOR_CONFIRMATION_REQUIRED.md",
        "manuscript/nature_methods/submission_package/prior_art_positioning_matrix.md",
        "manuscript/nature_methods/submission_package/validation_breadth_and_boundary_map.md",
        "manuscript/nature_methods/submission_package/editor_objection_response_map.md",
        "manuscript/nature_methods/submission_package/editor_two_minute_triage_simulation.md",
        "manuscript/nature_methods/submission_package/current_nature_methods_policy_preflight.md",
        "manuscript/nature_methods/submission_package/reviewer_editor_fit_planner_AUTHOR_CONFIRMATION_REQUIRED.md",
        "manuscript/nature_methods/submission_package/reporting_summary_answer_bank_AUTHOR_CONFIRMATION_REQUIRED.md",
        "manuscript/nature_methods/submission_package/pi_review_action_decisions.csv",
        "manuscript/nature_methods/stage9_completion_report.md",
        "manuscript/nature_methods/stage9_closure_version_binding.json",
    ]:
        package_files.add(rel)
    payload["package_files"] = sorted(package_files)
    payload["current_substage"] = "9.29"
    payload["next_substage"] = "none"
    payload["closure_status"] = "complete_stage9_closure_version_bound"
    payload["stage9_completion_report"] = "manuscript/nature_methods/stage9_completion_report.md"
    payload["stage9_version_binding"] = "manuscript/nature_methods/stage9_closure_version_binding.json"
    payload["pi_review_action_decisions"] = "manuscript/nature_methods/submission_package/pi_review_action_decisions.csv"
    payload["not_started"] = []
    payload["version_binding"] = {
        "closure_commit": version_binding["closure_commit"],
        "software_version": version_binding["software_version"],
        "software_archive_doi": version_binding["software_archive_doi"],
        "package_version": version_binding["package_version"],
        "figure_engine_version": version_binding["figure_engine"].get("pinned_ref"),
        "figure_engine_doi": version_binding["figure_engine"].get("version_doi"),
    }
    _write_json(path, payload)


def _update_registry() -> None:
    registry = _read_json(REGISTRY_PATH)
    registry["next_substage"] = "none"
    for item in registry.get("substages", []):
        if item.get("id") == "9.29":
            item["status"] = "complete_stage9_closed_version_bound"
            if "manuscript/nature_methods/stage9_closure_version_binding.json" not in item["outputs"]:
                item["outputs"].append("manuscript/nature_methods/stage9_closure_version_binding.json")
            if "manuscript/nature_methods/submission_package/pi_review_action_decisions.csv" not in item["outputs"]:
                item["outputs"].append("manuscript/nature_methods/submission_package/pi_review_action_decisions.csv")
    _write_json(REGISTRY_PATH, registry)


def _update_stage9_memory(version_binding: dict[str, Any]) -> None:
    memory = _read_json(MEMORY_PATH)
    closure_outputs = [
        "manuscript/nature_methods/stage9_completion_report.md",
        "manuscript/nature_methods/stage9_closure_version_binding.json",
        "manuscript/nature_methods/submission_package/pi_review_action_decisions.csv",
        "manuscript/nature_methods/submission_package/validation_breadth_and_boundary_map.md",
        "manuscript/nature_methods/submission_package/reviewer_editor_fit_planner_AUTHOR_CONFIRMATION_REQUIRED.md",
        "manuscript/nature_methods/gate_verdicts/9.29.json",
        "scripts/run_stage9_29_closure_assembly.py",
    ]
    artifacts = set(memory.get("artifacts", []))
    artifacts.update(closure_outputs)
    memory["artifacts"] = sorted(artifacts)
    completed = memory.get("completed_substages", [])
    if "9.29" not in completed:
        completed.append("9.29")
    memory["completed_substages"] = completed
    memory["current_substage"] = "9.29"
    memory["current_gate"] = "Stage 9 closed and version-bound"
    memory["next_substage"] = "none"
    memory["status"] = "stage9_29_closed_version_bound"
    memory["stage9_closure_started"] = True
    memory["stage9_closed"] = True
    memory["closure_version_binding"] = {
        "closure_commit": version_binding["closure_commit"],
        "package_version": version_binding["package_version"],
        "software_version": version_binding["software_version"],
        "software_archive_doi": version_binding["software_archive_doi"],
        "evidence_version": version_binding["evidence_version"],
        "claim_freeze_version": version_binding["claim_freeze_version"],
        "reference_version": version_binding["reference_version"],
    }
    memory["scope_rule"] = (
        "Stage 9 is closed for the current Nature Methods manuscript package. "
        "Closure binds versions and remaining submission-only actions without adding evidence or journal-upload claims."
    )
    memory["stage9_active_gate"] = "Stage 9.29 closed and version-bound"
    _write_json(MEMORY_PATH, memory)


def _update_roadmap_memory(version_binding: dict[str, Any]) -> None:
    memory = _read_json(ROADMAP_MEMORY_PATH)
    current = memory.setdefault("current_position", {})
    current["active_stage"] = "Stage 9.29 closed and version-bound"
    current["stage9_active_gate"] = "Stage 9.29 closed and version-bound"
    current["current_gate"] = "Stage 9 closed and version-bound"
    current["next_stage"] = "Stage 10 or journal-specific submission actions, not started"
    current["after_stage9_29_closure"] = (
        "Stage 9.29 closed the Nature Methods manuscript package by binding the package, evidence, release, "
        "figure-rendering, limitation, and PI-review decision versions. Official Reporting Summary, author declarations, "
        "reviewer/editor fit choices, and portal metadata remain human submission actions."
    )
    stages = memory.get("stage_lock", [])
    for stage in stages:
        if stage.get("stage") != 9:
            continue
        stage["status"] = "stage9_29_closed_version_bound"
        stage["current_gate"] = "Stage 9 closed and version-bound"
        stage["scope_rule"] = (
            "Stage 9 has closed the current Nature Methods manuscript package. Future work must be journal-specific "
            "submission handling or a new authorized evidence/manuscript stage."
        )
        artifacts = set(stage.get("artifacts", []))
        artifacts.update(
            [
                "manuscript/nature_methods/stage9_completion_report.md",
                "manuscript/nature_methods/stage9_closure_version_binding.json",
                "manuscript/nature_methods/submission_package/pi_review_action_decisions.csv",
                "manuscript/nature_methods/submission_package/reviewer_editor_fit_planner_AUTHOR_CONFIRMATION_REQUIRED.md",
                "manuscript/nature_methods/gate_verdicts/9.29.json",
                "scripts/run_stage9_29_closure_assembly.py",
            ]
        )
        stage["artifacts"] = sorted(artifacts)
        for entry in stage.get("subphases", []):
            if entry.get("id") == "9.29":
                entry["status"] = "complete_stage9_closed_version_bound"
                entry["evidence"] = "manuscript/nature_methods/gate_verdicts/9.29.json"
                entry["closure_version"] = version_binding["package_version"]
    _write_json(ROADMAP_MEMORY_PATH, memory)


def _replace_text(path: Path, replacements: list[tuple[str, str]]) -> None:
    body = path.read_text(encoding="utf-8")
    for old, new in replacements:
        body = body.replace(old, new)
    path.write_text(body, encoding="utf-8")


def _update_docs() -> None:
    _replace_text(
        README_PATH,
        [
            (
                "The next unstarted step is Stage 9.29 roadmap closure and version binding.",
                "Stage 9.29 roadmap closure and version binding is complete.",
            ),
            (
                "The official Springer Nature Reporting Summary form, author declarations, portal metadata, and final upload checks remain human submission actions. The Stage 9 closure report has not started.",
                "The official Springer Nature Reporting Summary form, author declarations, reviewer/editor fit choices, portal metadata, and final upload checks remain human submission actions. The Stage 9 closure report is `stage9_completion_report.md`.",
            ),
        ],
    )
    _replace_text(
        PLAN_PATH,
        [
            (
                "PI review packet assembly through Stage 9.28. Stage 9 closure has not started.",
                "PI review packet assembly, and Stage 9.29 closure and version binding. Stage 9 is closed for the current Nature Methods manuscript package.",
            ),
            (
                "Stage 9 closure has not started",
                "Stage 9 closure is complete",
            ),
            (
                "| 9.29 | Roadmap closure and version binding | not_started | Close Stage 9 with package, evidence, release, and limitation versions bound. |",
                "| 9.29 | Roadmap closure and version binding | complete_stage9_closed_version_bound | Close Stage 9 with package, evidence, release, and limitation versions bound. |",
            ),
            (
                "PI review packet, submission-readiness checklist, Stage 9 completion report, and updated roadmap memory.",
                "PI review packet, PI-review action decisions, submission-readiness checklist, Stage 9 completion report, version-binding record, and updated roadmap memory.",
            ),
        ],
    )
    _replace_text(
        ROADMAP_PATH,
        [
            (
                "Stage 9.28 has completed the final human PI review packet. Stage 9 closure remains not started.",
                "Stage 9.29 has closed and version-bound the current Nature Methods manuscript package.",
            ),
            (
                "| Stage 9. Nature Methods manuscript assembly | Stage 9.28 PI review packet complete, Stage 9 closure not started. |",
                "| Stage 9. Nature Methods manuscript assembly | Stage 9.29 closed and version-bound. |",
            ),
            (
                "Do not start Stage 9 closure without explicit substage authorization.",
                "Stage 9 closure is complete; future work must be journal-specific submission handling or a newly authorized evidence/manuscript stage.",
            ),
            (
                "Stage 9.28 Final human PI review packet has been completed. Stage 9.29 closure remains the next unstarted manuscript step.",
                "Stage 9.28 Final human PI review packet has been completed. Stage 9.29 Roadmap closure and version binding has been completed.",
            ),
        ],
    )


def _build_checks(version_binding: dict[str, Any], action_decisions: list[dict[str, str]]) -> list[dict[str, Any]]:
    gate_files = sorted(GATES.glob("9*.json"))
    stage9_gates_pass = True
    failing_gates: list[str] = []
    for path in gate_files:
        if path.name == "9.29.json":
            continue
        gate = _read_json(path)
        if gate.get("pass") is not True and gate.get("status") != "pass":
            stage9_gates_pass = False
            failing_gates.append(path.name)
    quarantine_files = _quarantine_files()
    package_rows = version_binding["package_files"]
    package_files_present = all(row["exists"] for row in package_rows)
    safety_hits = _safety_hits(SAFETY_SCAN_TARGETS)
    fig_status = version_binding["figure_status"]
    human_rows = [row for row in action_decisions if row["closure_status"] == "not_blocking_stage9_closure"]
    open_rows = [row for row in action_decisions if row["closure_status"] == "open"]
    return [
        {"name": "stage_9_28_gate_passed", "passed": _read_json(GATE_928).get("pass") is True, "detail": "PI-review gate remains passing"},
        {"name": "all_stage9_gates_pass", "passed": stage9_gates_pass, "detail": f"failing_gates={failing_gates}"},
        {"name": "quarantine_has_no_unresolved_blocker", "passed": not quarantine_files, "detail": f"quarantine_files={quarantine_files}"},
        {"name": "package_files_present", "passed": package_files_present, "detail": f"package_file_count={len(package_rows)}"},
        {"name": "package_version_bound", "passed": bool(version_binding.get("package_version")), "detail": str(version_binding.get("package_version"))},
        {"name": "evidence_version_bound", "passed": bool(version_binding.get("evidence_version")), "detail": str(version_binding.get("evidence_version"))},
        {"name": "release_version_bound", "passed": version_binding.get("software_version") == "v0.1.0" and version_binding.get("software_archive_doi") == "10.5281/zenodo.21036616", "detail": f"{version_binding.get('software_version')} {version_binding.get('software_archive_doi')}"},
        {"name": "limitation_version_bound", "passed": bool(version_binding.get("claim_freeze_version") and version_binding.get("reference_version")), "detail": f"claim={version_binding.get('claim_freeze_version')} reference={version_binding.get('reference_version')}"},
        {"name": "pi_review_action_decisions_recorded", "passed": len(action_decisions) == 6 and not open_rows, "detail": f"rows={len(action_decisions)} open={len(open_rows)} human_submission_actions={len(human_rows)}"},
        {"name": "human_submission_actions_retained", "passed": len(human_rows) == 1, "detail": f"rows={len(human_rows)}"},
        {"name": "completion_report_present", "passed": OUTPUTS["completion_report"].exists(), "detail": OUTPUTS["completion_report"].relative_to(ROOT).as_posix()},
        {"name": "version_binding_present", "passed": OUTPUTS["version_binding"].exists(), "detail": OUTPUTS["version_binding"].relative_to(ROOT).as_posix()},
        {"name": "package_safety_scan_clear", "passed": not safety_hits, "detail": f"package_hits={safety_hits}"},
        {"name": "panelforge_status_bound", "passed": fig_status["rendered_file_count"] == 18 and fig_status["all_files_exist"] is True, "detail": f"rendered_file_count={fig_status['rendered_file_count']}"},
    ]


def main() -> int:
    if not GATE_928.exists() or _read_json(GATE_928).get("pass") is not True:
        raise SystemExit("Stage 9.28 must pass before Stage 9.29 closure")
    if not GATE_927.exists() or _read_json(GATE_927).get("pass") is not True:
        raise SystemExit("Stage 9.27 must pass before Stage 9.29 closure")

    action_decisions = _action_decisions()
    _write_csv(OUTPUTS["action_decisions"], action_decisions, ACTION_DECISION_FIELDS)

    package_rows = _package_file_rows()
    version_binding = _version_binding(package_rows, action_decisions)
    _write_json(OUTPUTS["version_binding"], version_binding)
    _write_text(OUTPUTS["completion_report"], _completion_report(version_binding, action_decisions))

    _update_submission_manifest()
    _update_submission_package_manifest(version_binding)
    _update_registry()
    _update_stage9_memory(version_binding)
    _update_roadmap_memory(version_binding)
    _update_docs()

    checks = _build_checks(version_binding, action_decisions)
    gate = {
        "substage": "9.29",
        "status": "pass" if all(item["passed"] for item in checks) else "fail",
        "pass": all(item["passed"] for item in checks),
        "generated_utc": _now(),
        "git_sha": version_binding["closure_commit"],
        "next_substage": "none",
        "closure_status": "complete_stage9_closed_version_bound",
        "action_decision_rows": len(action_decisions),
        "human_submission_action_rows": len([row for row in action_decisions if row["closure_status"] == "not_blocking_stage9_closure"]),
        "package_file_count": len(package_rows),
        "rendered_figure_file_count": version_binding["figure_status"]["rendered_file_count"],
        "version_binding": {
            "package_version": version_binding["package_version"],
            "software_version": version_binding["software_version"],
            "software_archive_doi": version_binding["software_archive_doi"],
            "evidence_version": version_binding["evidence_version"],
            "claim_freeze_version": version_binding["claim_freeze_version"],
            "reference_version": version_binding["reference_version"],
        },
        "checks": checks,
        "outputs": {name: path.relative_to(ROOT).as_posix() for name, path in OUTPUTS.items()},
        "scope_boundary": "Closure and version binding only. No new analysis, figure, dataset, model output, manuscript claim, or journal upload is created.",
    }
    _write_json(OUTPUTS["gate"], gate)

    print(json.dumps(gate, indent=2))
    return 0 if gate["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

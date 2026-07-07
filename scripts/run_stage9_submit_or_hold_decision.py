"""Write the post-closure Nature Methods submit-or-hold decision.

This check keeps the Stage 9.29 manuscript package scientifically ready for
collaborator review while preventing a procedural mistake at journal upload.
It does not alter manuscript text, figures, source data, or software evidence.
"""

from __future__ import annotations

import csv
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT / "manuscript" / "nature_methods"
PACKAGE = WORKSPACE / "submission_package"
AUDITS = WORKSPACE / "audits"

JSON_OUT = AUDITS / "nature_methods_submit_or_hold_decision.json"
MD_OUT = AUDITS / "nature_methods_submit_or_hold_decision.md"

REPORT_FORMAT = "rhodyn.stage9_submit_or_hold_decision.v1"
FORBIDDEN_REFERENCE_LINKS = [
    "https://github.com/renatosocodato/windowed_rhoA_model",
    "https://doi.org/10.5281/zenodo.19796404",
    "https://doi.org/10.5281/zenodo.19796406",
]


def _now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def _json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def _csv_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _check(name: str, passed: bool, detail: str) -> dict[str, Any]:
    return {"name": name, "passed": bool(passed), "detail": detail}


def build_report() -> dict[str, Any]:
    main_text = _read(PACKAGE / "main_text_for_submission.md")
    checklist = _read(PACKAGE / "submission_readiness_checklist.md")
    author_declarations = _read(PACKAGE / "author_declarations_REQUIRED.md")
    ai_disclosure = _read(PACKAGE / "ai_disclosure_AUTHOR_CONFIRMATION_REQUIRED.md")
    title_author_metadata = _read(PACKAGE / "title_author_metadata_AUTHOR_CONFIRMATION_REQUIRED.md")
    reporting_summary = _read(PACKAGE / "reporting_summary_REQUIRED.md")
    reporting_summary_answer_bank = _read(PACKAGE / "reporting_summary_answer_bank_AUTHOR_CONFIRMATION_REQUIRED.md")
    prior_art_positioning = _read(PACKAGE / "prior_art_positioning_matrix.md")
    editor_objection_response = _read(PACKAGE / "editor_objection_response_map.md")
    editor_two_minute_triage = _read(PACKAGE / "editor_two_minute_triage_simulation.md")
    article_fit = _read(PACKAGE / "article_fit_checklist.md")
    code_for_review = _read(PACKAGE / "code_for_review.md")
    editor_note = _read(PACKAGE / "editor_triage_note_for_cover_letter.md")
    editorial_pitch = _read(PACKAGE / "editorial_pitch_for_submission.md")
    package_manifest = _json(PACKAGE / "submission_package_manifest.json")
    public_access = _json(AUDITS / "nature_methods_public_access_verification.json")
    closure_gate = _json(WORKSPACE / "gate_verdicts" / "9.29.json")
    action_rows = _csv_rows(PACKAGE / "pi_review_action_decisions.csv")
    figure_rows = _csv_rows(PACKAGE / "figure_file_inventory.csv")

    package_text = "\n".join(_read(path) for path in sorted(PACKAGE.glob("*.md")))
    open_action_rows = [row for row in action_rows if row.get("closure_status") == "open"]
    upload_only_rows = [
        row for row in action_rows if row.get("closure_status") == "not_blocking_stage9_closure"
    ]
    declaration_human_rows = [
        line for line in author_declarations.splitlines() if "| " in line and "human action" in line
    ]

    science_checks = [
        _check(
            "nature_methods_article_fit",
            "Content-type decision | Nature Methods Article" in article_fit
            and "| Abstract length | 150 words |" in article_fit
            and "| Main display items | 6 figures |" in article_fit
            and "| Reference count | 14 references |" in article_fit,
            "Article-fit checklist records Article type, abstract length, six display items, and reference count.",
        ),
        _check(
            "manuscript_sections_present",
            all(
                phrase in main_text
                for phrase in [
                    "## Abstract",
                    "## Results",
                    "## Discussion",
                    "## Online Methods",
                    "## Data availability",
                    "## Code availability",
                    "## References",
                    "### Main figure legends",
                ]
            ),
            "Main manuscript includes the expected Article sections and legends.",
        ),
        _check(
            "figures_present_in_three_formats",
            len(figure_rows) == 18
            and {row.get("format") for row in figure_rows} == {"pdf", "png", "svg"},
            f"Figure inventory rows={len(figure_rows)}.",
        ),
        _check(
            "public_urls_resolve",
            public_access.get("status") == "pass"
            and public_access.get("checks", {}).get("all_visible_public_urls_resolve") is True,
            f"Public-access report status={public_access.get('status')}.",
        ),
        _check(
            "unresolved_reference_case_links_not_public_facing",
            not any(link in package_text for link in FORBIDDEN_REFERENCE_LINKS)
            and "controlled reviewer-access repository" in package_text,
            "The optional RhoA/microglia reference case is reviewer-access scoped rather than exposed as unresolved public links.",
        ),
        _check(
            "code_and_data_availability_present",
            "https://github.com/renatosocodato/rhodyn" in main_text
            and "https://doi.org/10.5281/zenodo.21036616" in main_text
            and "https://doi.org/10.5281/zenodo.20811171" in main_text,
            "RhoDyn release, software DOI, and PanelForge DOI appear in availability text.",
        ),
        _check(
            "editorial_fit_argument_present",
            "computational methods Article" in editor_note
            and "method travels beyond one motivating system" in editor_note,
            "Editor-triage note presents the Nature Methods fit and validation ladder.",
        ),
        _check(
            "cover_letter_pitch_boundary_present",
            "Article-level computational method, not a software wrapper around existing summaries" in editorial_pitch
            and "not the broad observation that cell signaling is dynamic" in editorial_pitch
            and "reference use case rather than as hidden evidence for every methods claim" in editorial_pitch
            and "rather than as a software note or a single-system biological study" in editorial_pitch,
            "Cover-letter and presubmission drafts state the method novelty, validation breadth, and non-overclaim boundaries.",
        ),
        _check(
            "prior_art_positioning_matrix_present",
            "Prior-art positioning matrix" in prior_art_positioning
            and "should not be positioned as the first method to treat live-cell signals as dynamic" in prior_art_positioning
            and "does not add citations, performance results, biological datasets, or manuscript claims" in prior_art_positioning,
            "Prior-art positioning matrix makes the RhoDyn novelty boundary explicit for collaborator/editorial review.",
        ),
        _check(
            "editor_objection_response_map_present",
            "Editor-objection response map" in editor_objection_response
            and "likely Nature Methods desk-review objections" in editor_objection_response
            and "does not add evidence, citations, figures, datasets, performance claims, or manuscript text" in editor_objection_response
            and "If answering an objection would require new data, new benchmarking, or a stronger biological claim" in editor_objection_response,
            "Editor-objection response map ties likely desk-review objections to existing evidence and claim boundaries.",
        ),
        _check(
            "editor_two_minute_triage_simulation_present",
            "Two-minute editor triage simulation" in editor_two_minute_triage
            and "does not add evidence, citations, analyses, figures, datasets, performance claims, or manuscript text" in editor_two_minute_triage
            and "What an editor can see quickly" in editor_two_minute_triage
            and "The current package should be readable as a Nature Methods computational-methods Article" in editor_two_minute_triage
            and "If an editor can answer these three questions in the first two minutes" in editor_two_minute_triage,
            "Two-minute editor triage simulation checks whether method novelty, validation breadth, and claim boundaries are visible on first pass.",
        ),
        _check(
            "stage9_closure_passed",
            closure_gate.get("pass") is True
            and closure_gate.get("closure_status") == "complete_stage9_closed_version_bound"
            and package_manifest.get("closure_status") == "complete_stage9_closure_version_bound",
            "Stage 9.29 closure and package manifest are closed and version-bound.",
        ),
        _check(
            "pi_review_actions_resolved_or_submission_only",
            not open_action_rows and len(upload_only_rows) == 1,
            f"open_action_rows={len(open_action_rows)}; submission_only_rows={len(upload_only_rows)}.",
        ),
    ]

    upload_hold_checks = [
        _check(
            "official_reporting_summary_not_completed_in_repo",
            "not the completed journal form" in reporting_summary
            and "The final Reporting Summary must be completed" in reporting_summary,
            "Repository contains a required-form placeholder, not the official completed Springer Nature form.",
        ),
        _check(
            "reporting_summary_answer_bank_requires_author_confirmation",
            "AUTHOR CONFIRMATION REQUIRED" in reporting_summary_answer_bank
            and "Statistics" in reporting_summary_answer_bank
            and "Software and code" in reporting_summary_answer_bank
            and "Life-science study design" in reporting_summary_answer_bank
            and "Materials and experimental systems" in reporting_summary_answer_bank,
            "Reporting Summary answer bank maps current package evidence to official form fields while preserving author confirmation.",
        ),
        _check(
            "author_attestations_remain_human_actions",
            len(declaration_human_rows) >= 6
            and "This package does not insert an AI declaration automatically" in author_declarations,
            f"author_declaration_human_rows={len(declaration_human_rows)}.",
        ),
        _check(
            "ai_disclosure_draft_requires_author_confirmation",
            "AUTHOR CONFIRMATION REQUIRED" in ai_disclosure
            and "does not assert final AI use" in ai_disclosure
            and "Option A" in ai_disclosure
            and "Option B" in ai_disclosure,
            "AI disclosure support file provides draft options while preserving author confirmation as the required decision.",
        ),
        _check(
            "title_author_metadata_requires_author_confirmation",
            "AUTHOR CONFIRMATION REQUIRED" in title_author_metadata
            and "Author list" in title_author_metadata
            and "Correspondence and materials" in title_author_metadata
            and "Double-blind review decision" in title_author_metadata,
            "Title-page and author metadata support file captures author-controlled manuscript-file and portal fields.",
        ),
        _check(
            "final_upload_approval_remains_human_action",
            "Human actions before journal upload" in checklist
            and "final author approval" in checklist,
            "Readiness checklist retains final upload and author approval actions.",
        ),
        _check(
            "controlled_reference_case_requires_upload_decision",
            "controlled reviewer-access repository" in main_text
            and "journal upload system" in main_text,
            "Optional RhoA/microglia reviewer-access records must be supplied only if authors include that reference case.",
        ),
    ]

    package_ready = all(item["passed"] for item in science_checks)
    upload_holds_present = all(item["passed"] for item in upload_hold_checks)
    return {
        "report_format": REPORT_FORMAT,
        "generated_utc": _now(),
        "status": "hold_for_human_upload_actions" if package_ready and upload_holds_present else "needs_revision",
        "collaborator_review_ready": package_ready,
        "journal_upload_ready": False,
        "science_package_checks": science_checks,
        "upload_hold_checks": upload_hold_checks,
        "human_submission_actions": [
            "Complete the official Springer Nature Reporting Summary form using author-confirmed answers from the reporting-summary answer bank.",
            "Confirm title page, author order, affiliations, ORCID, corresponding-author metadata, funding, competing interests, and author contributions.",
            "Confirm whether AI-assisted content disclosure is required, revise the AI disclosure draft with final author-confirmed wording if applicable, and insert it in the journal-designated location.",
            "Confirm ethics, biological materials, and controlled-access or reviewer-access statements.",
            "Perform final file naming, portal metadata, and author approval checks.",
        ],
        "decision": (
            "The Stage 9.29 package is ready for collaborator and PI review as a Nature Methods Article package. "
            "Final journal upload should remain on hold until the listed human-attested submission fields are completed."
        ),
        "scientific_boundary": (
            "This report does not add data, analyses, figures, citations, or manuscript claims. "
            "It separates evidence readiness from author-attested submission requirements."
        ),
    }


def _write_markdown(report: dict[str, Any]) -> None:
    def table(checks: list[dict[str, Any]]) -> list[str]:
        lines = ["| Check | Status | Detail |", "| --- | --- | --- |"]
        for check in checks:
            lines.append(
                f"| {check['name']} | {'pass' if check['passed'] else 'fail'} | {check['detail']} |"
            )
        return lines

    lines = [
        "# Nature Methods submit-or-hold decision",
        "",
        f"Generated UTC. `{report['generated_utc']}`.",
        "",
        f"Decision. `{report['status']}`.",
        "",
        "The Stage 9.29 package is ready for collaborator and PI review as a Nature Methods Article package. It should not be treated as ready for final journal upload until the official Springer Nature Reporting Summary has been completed from author-confirmed answers, title and author metadata, author declarations, AI-use disclosure decision using the author-confirmation draft, portal metadata, and final author approval are complete.",
        "",
        "## Science package checks",
        "",
        *table(report["science_package_checks"]),
        "",
        "## Upload hold checks",
        "",
        *table(report["upload_hold_checks"]),
        "",
        "## Required human submission actions",
        "",
    ]
    lines.extend(f"- {action}" for action in report["human_submission_actions"])
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            report["scientific_boundary"],
        ]
    )
    MD_OUT.parent.mkdir(parents=True, exist_ok=True)
    MD_OUT.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def main() -> int:
    report = build_report()
    JSON_OUT.parent.mkdir(parents=True, exist_ok=True)
    JSON_OUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    _write_markdown(report)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["status"] == "hold_for_human_upload_actions" else 1


if __name__ == "__main__":
    raise SystemExit(main())

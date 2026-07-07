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
    reporting_summary = _read(PACKAGE / "reporting_summary_REQUIRED.md")
    article_fit = _read(PACKAGE / "article_fit_checklist.md")
    code_for_review = _read(PACKAGE / "code_for_review.md")
    editor_note = _read(PACKAGE / "editor_triage_note_for_cover_letter.md")
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
            "author_attestations_remain_human_actions",
            len(declaration_human_rows) >= 6
            and "This package does not insert an AI declaration automatically" in author_declarations,
            f"author_declaration_human_rows={len(declaration_human_rows)}.",
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
            "Complete the official Springer Nature Reporting Summary form.",
            "Confirm funding, competing interests, author contributions, author order, affiliations, ORCID, and corresponding-author metadata.",
            "Confirm whether AI-assisted content disclosure is required and insert the final journal-compliant wording if applicable.",
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
        "The Stage 9.29 package is ready for collaborator and PI review as a Nature Methods Article package. It should not be treated as ready for final journal upload until the official Springer Nature Reporting Summary, author declarations, AI-use disclosure decision, portal metadata, and final author approval are complete.",
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

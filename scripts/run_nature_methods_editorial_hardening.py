"""Create a Nature Methods desk-rejection hardening addendum.

This runner deliberately does not change the closed Stage 9.29 submission
package. It produces author-facing editorial surfaces that can be reviewed
before any later package promotion.
"""

from __future__ import annotations

import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT / "manuscript" / "nature_methods"
SUBMISSION = WORKSPACE / "submission_package"
AUDITS = WORKSPACE / "audits"
STAGING = WORKSPACE / "_staging"

MAIN_TEXT = SUBMISSION / "main_text_for_submission.md"
PI_REVIEW = SUBMISSION / "pi_review_packet.md"
COMPLETION_REPORT = WORKSPACE / "stage9_completion_report.md"
GATE_929 = WORKSPACE / "gate_verdicts" / "9.29.json"
VERSION_BINDING = WORKSPACE / "stage9_closure_version_binding.json"

RISK_MATRIX = AUDITS / "nature_methods_desk_rejection_risk_matrix.csv"
HARDENING_REPORT = AUDITS / "nature_methods_editorial_hardening_report.md"
TRIAGE_NOTE = STAGING / "nature_methods_editor_triage_note_draft.md"
PRIOR_ART_NOTE = STAGING / "live_cell_prior_art_candidate_for_promotion.md"


NATURE_METHODS_AIMS_URL = "https://www.nature.com/nmeth/aims"
NATURE_REPORTING_URL = "https://www.nature.com/nature-portfolio/editorial-policies/reporting-standards"
COPPERMAN_DOI = "10.1038/s42003-023-04837-8"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def _word_count(text: str) -> int:
    return len(re.findall(r"\b[\w'-]+\b", text))


def _section(text: str, heading: str) -> str:
    pattern = re.compile(rf"^## {re.escape(heading)}\n(?P<body>.*?)(?=^## |\Z)", re.M | re.S)
    match = pattern.search(text)
    return match.group("body").strip() if match else ""


def _gate_ok() -> bool:
    if not GATE_929.exists():
        return False
    try:
        gate = json.loads(GATE_929.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return False
    return gate.get("pass") is True and gate.get("substage") == "9.29"


def _risk_rows(main_text: str, pi_review: str) -> list[dict[str, str]]:
    intro = _section(main_text, "Introduction")
    methods = _section(main_text, "Online Methods")
    data_availability = _section(main_text, "Data availability")
    code_availability = _section(main_text, "Code availability")
    abstract = _section(main_text, "Abstract")
    results = _section(main_text, "Results")
    discussion = _section(main_text, "Discussion")
    references = _section(main_text, "References")
    figure_legends_present = "### Main figure legends" in main_text and "#### Figure 6" in main_text
    invalid_input_language = (
        "validation issues" in methods
        and "missing time units" in methods
        and "not automatically discovered" in methods + intro
    )
    coupling_reserve_boundary = (
        "not proof that all coupling is absent" in methods
        and "not direct assays of unmeasured biological reserve capacity" in methods
        and "slower or context-specific coupling" in discussion
    )
    return [
        {
            "risk_id": "NM-DESK-001",
            "editorial_risk": "Method novelty could be read as another trajectory-summary tool rather than a distinct decision framework.",
            "nature_methods_requirement": "Novel method or substantial improvement with broad practical relevance.",
            "current_evidence": "Introduction and PI review distinguish RhoDyn from generic live-cell dynamics by naming residence windows, amplitude comparators, bounded-coupling margins, reserve-like endpoints, routed alternatives, and cross-surface reproducibility.",
            "status": "hardened_in_current_text" if "not that signaling dynamics" in intro and "reviewable analysis object" in intro else "needs_revision",
            "recommended_action": "Keep the novelty sentence centered on the integrated decision object. Do not broaden into a general theory of cell dynamics.",
            "promotion_target": "No package change required unless title or abstract is later reopened.",
        },
        {
            "risk_id": "NM-DESK-002",
            "editorial_risk": "Validation may look too narrow for Nature Methods if public examples are over-presented as broad generality.",
            "nature_methods_requirement": "Strong validation, biological application, and performance comparison with available approaches.",
            "current_evidence": "Figures 2-5 cover synthetic truth cases, public calcium, public ERK, public endpoint data, held-out contexts, margin sensitivity, and inconclusive outcomes.",
            "status": "hardened_in_current_text" if "not whether every biological system contains a residence regime" in intro + discussion else "needs_revision",
            "recommended_action": "Frame examples as portability and decision-behavior tests, not field-wide biological generality.",
            "promotion_target": "Maintain current Results and Discussion boundary language.",
        },
        {
            "risk_id": "NM-DESK-003",
            "editorial_risk": "Prior-art contrast for live-cell morphodynamic trajectory methods is compact and could be questioned by a methods editor.",
            "nature_methods_requirement": "Novelty must be calibrated against related methods and established approaches.",
            "current_evidence": "References 1-8 cover trajectory inference, transient state modeling, state-space visualization, CellRank, Cellpose, Squidpy, scvi-tools, and DeepLabCut. A specific live-cell morphodynamic trajectory-embedding citation is not yet in the submitted reference list.",
            "status": "candidate_revision_prepared",
            "recommended_action": f"Consider adding Copperman et al. 2023, Communications Biology, doi:{COPPERMAN_DOI}, only if the Introduction is reopened for reference renumbering.",
            "promotion_target": "Staged prior-art note, not automatically promoted.",
        },
        {
            "risk_id": "NM-DESK-004",
            "editorial_risk": "Declared windows, margins, and grouping choices may be seen as user-tuned unless failure modes are explicit.",
            "nature_methods_requirement": "Comprehensive technical description that facilitates immediate application.",
            "current_evidence": "Methods state that windows are declared, not discovered automatically, and invalid/missing schema fields withhold interpretation.",
            "status": "hardened_in_current_text" if invalid_input_language else "needs_revision",
            "recommended_action": "Keep invalid-input and withheld-decision language visible. Do not describe RhoDyn as fully automated state discovery.",
            "promotion_target": "No package change required.",
        },
        {
            "risk_id": "NM-DESK-005",
            "editorial_risk": "Bounded coupling and reserve-like endpoints could be overread as mechanistic absence or direct reserve measurement.",
            "nature_methods_requirement": "Claims must match methodological validation and biological application.",
            "current_evidence": "Methods and Discussion explicitly state bounded coupling is margin/context limited and reserve-like summaries are endpoint coordinates, not direct unmeasured reserve assays.",
            "status": "hardened_in_current_text" if coupling_reserve_boundary else "needs_revision",
            "recommended_action": "Preserve the margin/context and measured-endpoint boundary in all upload-facing files.",
            "promotion_target": "No package change required.",
        },
        {
            "risk_id": "NM-DESK-006",
            "editorial_risk": "Software/reproducibility might look like availability rather than methodological validation.",
            "nature_methods_requirement": "Immediate practical relevance, reproducible code, peer-reviewable software, and reusable outputs.",
            "current_evidence": "Figure 6, Methods, data availability, code availability, and package inventories bind Python, CLI, backend, workbench, source distribution, Zenodo DOI, checksums, and exported analysis bundles.",
            "status": "hardened_in_current_text" if "Python, command-line, backend, and workbench" in methods and "Zenodo version DOI" in code_availability else "needs_revision",
            "recommended_action": "Use the editor-triage note to make software parity part of the method validation argument, not a back-matter afterthought.",
            "promotion_target": "Staged editor-triage note.",
        },
        {
            "risk_id": "NM-DESK-007",
            "editorial_risk": "References and reporting surfaces may fail Nature Portfolio availability expectations if dataset DOIs and code access are not explicit.",
            "nature_methods_requirement": "Data and Code availability sections, repository identifiers, DOI-minting archive, and peer-review access to code and algorithms.",
            "current_evidence": "Data availability lists public source dataset DOIs and retained derived outputs; Code availability lists GitHub release, commit, Zenodo DOI, license, package contents, and PanelForge DOI.",
            "status": "hardened_in_current_text" if "10.5281/zenodo.21036616" in code_availability and "10.5281/zenodo.14907827" in data_availability else "needs_revision",
            "recommended_action": "Complete the official Reporting Summary and portal metadata before submission.",
            "promotion_target": "Human submission action retained from Stage 9.29.",
        },
        {
            "risk_id": "NM-DESK-008",
            "editorial_risk": "Manuscript may appear too compressed or figure-light if the editor cannot see the six-display-item logic immediately.",
            "nature_methods_requirement": "Clear results illustrating performance and comparison with available approaches.",
            "current_evidence": f"Results section has {_word_count(results)} words and six figure-anchored subsections; main legends describe six figures with panel-level roles.",
            "status": "hardened_by_staged_triage_note" if "### RhoDyn defines" in results and figure_legends_present else "needs_revision",
            "recommended_action": "Use the triage note to state the six-figure logic in one paragraph for editors.",
            "promotion_target": "Staged editor-triage note.",
        },
        {
            "risk_id": "NM-DESK-009",
            "editorial_risk": "Conclusion could be desk-rejected if it sounds like RhoDyn is a mechanism-discovery engine.",
            "nature_methods_requirement": "Methodological conclusions must remain supported by validation and application data.",
            "current_evidence": "Discussion ends by stating RhoDyn is not a mechanism-discovery engine, not a substitute for perturbation experiments, and not a claim that one dynamical summary is privileged in every cell-state problem.",
            "status": "hardened_in_current_text" if "not a mechanism-discovery engine" in discussion else "needs_revision",
            "recommended_action": "Do not strengthen the terminal Discussion claim without additional independent demonstrations.",
            "promotion_target": "No package change required.",
        },
        {
            "risk_id": "NM-DESK-010",
            "editorial_risk": "Human-upload requirements could still block submission even if repository-derived checks pass.",
            "nature_methods_requirement": "Completed reporting summary, portal metadata, file naming, and author approval.",
            "current_evidence": "Stage 9.29 retains the official Reporting Summary and portal metadata as external human submission actions.",
            "status": "human_submission_action_remaining",
            "recommended_action": "Complete the official Springer Nature Reporting Summary and portal fields after author approval.",
            "promotion_target": "Human action, not repository-derived manuscript edit.",
        },
    ]


def _write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def _write_report(rows: list[dict[str, str]], main_text: str) -> None:
    abstract = _section(main_text, "Abstract")
    intro = _section(main_text, "Introduction")
    results = _section(main_text, "Results")
    discussion = _section(main_text, "Discussion")
    methods = _section(main_text, "Online Methods")
    remaining = [
        row
        for row in rows
        if row["status"] not in {"hardened_in_current_text", "hardened_by_staged_triage_note"}
    ]
    lines = [
        "# Nature Methods desk-rejection hardening addendum",
        "",
        "Generated by deterministic runner from the current Stage 9.29 package state.",
        "",
        "## Purpose",
        "",
        "This addendum stress-tests the closed Stage 9.29 manuscript package against Nature Methods editorial triage concerns. It is an author-facing hardening surface, not a new analysis and not a journal-upload claim.",
        "",
        "## Venue calibration used",
        "",
        f"- Nature Methods Aims & Scope. {NATURE_METHODS_AIMS_URL}",
        f"- Nature Portfolio reporting, data, and code availability policies. {NATURE_REPORTING_URL}",
        "",
        "The relevant editorial bar is a novel method or substantial improvement with broad practical relevance, strong validation, biological application, comparison with available approaches, and enough technical description for immediate application.",
        "",
        "## Current manuscript profile",
        "",
        f"- Abstract word count. `{_word_count(abstract)}`.",
        f"- Introduction word count. `{_word_count(intro)}`.",
        f"- Results word count. `{_word_count(results)}`.",
        f"- Discussion word count. `{_word_count(discussion)}`.",
        f"- Online Methods word count. `{_word_count(methods)}`.",
        f"- Stage 9.29 gate passed. `{_gate_ok()}`.",
        "",
        "## Desk-rejection risk decisions",
        "",
        "| risk | status | action |",
        "|---|---|---|",
    ]
    for row in rows:
        lines.append(f"| {row['risk_id']} | {row['status']} | {row['recommended_action']} |")
    lines.extend(
        [
            "",
            "## Recommended author action",
            "",
            "The package is defensible for editor triage if the cover/editor note foregrounds the method contribution as a decision framework rather than a generic dynamics statement. The strongest optional manuscript improvement is to add one specific live-cell morphodynamic trajectory prior-art citation if the Introduction is reopened for reference renumbering.",
            "",
            "## Items not automatically promoted",
            "",
            "- No new reference was inserted automatically, because that would require reference renumbering across the closed package.",
            "- No title, Abstract, Results, Methods, figure, or data changes were made.",
            "- The official Reporting Summary remains a human submission action.",
            "",
            "## Remaining non-hardened rows",
            "",
        ]
    )
    if remaining:
        for row in remaining:
            lines.append(f"- `{row['risk_id']}`. {row['status']}. {row['recommended_action']}")
    else:
        lines.append("- None.")
    HARDENING_REPORT.parent.mkdir(parents=True, exist_ok=True)
    HARDENING_REPORT.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def _write_triage_note() -> None:
    lines = [
        "# Draft editor-triage note for Nature Methods",
        "",
        "RhoDyn is submitted as a computational methods Article for live-cell perturbation biology. The central contribution is not the broad observation that cell signaling is dynamic. The contribution is an executable decision framework that makes residence-state summaries, amplitude comparators, bounded-coupling margins, reserve-like endpoint coordinates, routed-output alternatives, uncertainty behavior, and cross-surface reproducibility inspectable in one workflow.",
        "",
        "The manuscript has been calibrated to Nature Methods' emphasis on immediate practical relevance, strong validation, biological application, performance comparison, and comprehensive technical description. The validation ladder includes synthetic truth cases, public calcium and ERK reporter trajectories, public-derived endpoint and paired-reporter demonstrations, held-out bounded-coupling contexts, and parity across Python, command-line, backend, workbench, export-bundle, source-distribution, checksum, GitHub, and Zenodo surfaces.",
        "",
        "The manuscript deliberately reports pass, fail, and inconclusive outcomes. A residence window is a declared analysis choice rather than an automatically discovered biological state. A bounded-coupling call means equivalence within a stated margin and context rather than absence of all coupling. Reserve-like endpoint summaries remain tied to the measured readout, and routed-output comparisons constrain tested endpoint alternatives without identifying direct biochemical edges.",
        "",
        "The current package is therefore best read as a method for reviewable dynamic operating-state interpretation, not as a new primary disease-biology claim and not as a universal assertion that every live-cell reporter contains a residence regime. The RhoA/microglia work is a reference use case; the method evidence for this Article is carried by the released RhoDyn package, public-derived demonstrations, software parity checks, and reproducibility archive.",
    ]
    TRIAGE_NOTE.parent.mkdir(parents=True, exist_ok=True)
    TRIAGE_NOTE.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def _write_prior_art_note() -> None:
    lines = [
        "# Optional live-cell prior-art citation candidate",
        "",
        "This note records one evidence-safe prior-art addition candidate for a later package-promotion pass. It is not promoted into the closed Stage 9.29 package by this runner.",
        "",
        "## Candidate reference",
        "",
        f"Copperman, J. et al. Morphodynamical cell state description via live-cell imaging trajectory embedding. Communications Biology 6, 484 (2023). doi:{COPPERMAN_DOI}.",
        "",
        "## Why this may help",
        "",
        "The current Introduction already cites trajectory inference, dynamic transient-state modeling, state-space visualization, CellRank, Cellpose, Squidpy, scvi-tools, and DeepLabCut. A Nature Methods editor may still ask whether live-cell morphodynamic trajectory embedding is directly acknowledged. This reference would sharpen the claim that RhoDyn is not claiming novelty for time-lapse trajectory analysis itself, but for the integrated residence, bounded-coupling, reserve-like, routed-output, and reproducibility decision object.",
        "",
        "## Candidate insertion",
        "",
        "In the third Introduction paragraph, revise the citation range in the sentence beginning `The novelty claimed here is not...` so that live-cell morphodynamic trajectory embedding is explicitly included among established prior dynamic live-cell approaches.",
        "",
        "## Promotion requirements",
        "",
        "- Renumber dataset, software, and PanelForge references consistently in `main_text_for_submission.md`, `references.bib`, `references_for_submission.bib`, citation ledgers, and availability sections.",
        "- Re-run package assembly and Stage 9 validation after promotion.",
        "- Do not add this citation if the final author decision is to keep the reference list compact for triage.",
    ]
    PRIOR_ART_NOTE.parent.mkdir(parents=True, exist_ok=True)
    PRIOR_ART_NOTE.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def run() -> dict[str, object]:
    main_text = _read(MAIN_TEXT)
    pi_review = _read(PI_REVIEW)
    if not main_text:
        raise FileNotFoundError(MAIN_TEXT)
    rows = _risk_rows(main_text, pi_review)
    _write_csv(RISK_MATRIX, rows)
    _write_report(rows, main_text)
    _write_triage_note()
    _write_prior_art_note()
    statuses = {row["status"] for row in rows}
    status = "pass" if "needs_revision" not in statuses else "warning"
    return {
        "status": status,
        "open_statuses": sorted(statuses - {"hardened_in_current_text", "hardened_by_staged_triage_note"}),
        "risk_rows": len(rows),
        "hardened_rows": sum(row["status"] == "hardened_in_current_text" for row in rows),
        "triage_note_hardened_rows": sum(row["status"] == "hardened_by_staged_triage_note" for row in rows),
        "candidate_revision_rows": sum(row["status"] == "candidate_revision_prepared" for row in rows),
        "human_submission_rows": sum(row["status"] == "human_submission_action_remaining" for row in rows),
        "outputs": {
            "risk_matrix": RISK_MATRIX.relative_to(ROOT).as_posix(),
            "hardening_report": HARDENING_REPORT.relative_to(ROOT).as_posix(),
            "triage_note": TRIAGE_NOTE.relative_to(ROOT).as_posix(),
            "prior_art_note": PRIOR_ART_NOTE.relative_to(ROOT).as_posix(),
        },
        "scope": "Editorial hardening addendum only. No data, figures, model outputs, manuscript claims, or closed package files were changed.",
    }


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, sort_keys=True))

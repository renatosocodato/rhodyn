"""Run Stage 9.27 submission package assembly.

Stage 9.27 assembles the current reader-clean Nature Methods Article surfaces
into a collaborator-review package. It does not create the final PI review
packet or close Stage 9.
"""

from __future__ import annotations

import csv
import hashlib
import json
import re
import shutil
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT / "manuscript" / "nature_methods"
SECTIONS = WORKSPACE / "sections"
FIGURES = WORKSPACE / "figures"
SUPPLEMENTARY = WORKSPACE / "supplementary"
LEDDERS = WORKSPACE / "ledgers"
REFS = WORKSPACE / "refs"
AUDITS = WORKSPACE / "audits"
SUBMISSION = WORKSPACE / "submission_package"
GATES = WORKSPACE / "gate_verdicts"
STAGING = WORKSPACE / "_staging" / "9.27"
QUARANTINE = WORKSPACE / "_quarantine" / "9.27"
MEMORY_PATH = ROOT / "docs" / "stage9_execution_memory.json"
ROADMAP_MEMORY_PATH = ROOT / "docs" / "roadmap_execution_memory.json"
REGISTRY_PATH = WORKSPACE / "contracts" / "stage9_substage_registry.json"
PLAN_PATH = ROOT / "docs" / "stage9_manuscript_assembly_plan.md"
ROADMAP_PATH = ROOT / "docs" / "roadmap.md"
README_PATH = WORKSPACE / "README.md"

GATE_926 = GATES / "9.26.json"
GATE_925B = GATES / "9.25b.json"
GATE_921 = GATES / "9.21.json"
GATE_923 = GATES / "9.23.json"
GATE_96B = GATES / "9.6b.json"
GATE_928 = GATES / "9.28.json"
GATE_929 = GATES / "9.29.json"

OUTPUTS = {
    "main_text": SUBMISSION / "main_text_for_submission.md",
    "supplement": SUBMISSION / "supplementary_information_for_submission.md",
    "manifest": SUBMISSION / "submission_manifest.md",
    "readiness": SUBMISSION / "submission_readiness_checklist.md",
    "editor_triage_note": SUBMISSION / "editor_triage_note_for_cover_letter.md",
    "editorial_pitch": SUBMISSION / "editorial_pitch_for_submission.md",
    "cover_letter_draft": SUBMISSION / "cover_letter_for_submission_AUTHOR_CONFIRMATION_REQUIRED.md",
    "prior_art_positioning_matrix": SUBMISSION / "prior_art_positioning_matrix.md",
    "validation_breadth_map": SUBMISSION / "validation_breadth_and_boundary_map.md",
    "editor_objection_response_map": SUBMISSION / "editor_objection_response_map.md",
    "editor_two_minute_triage_simulation": SUBMISSION / "editor_two_minute_triage_simulation.md",
    "current_policy_preflight": SUBMISSION / "current_nature_methods_policy_preflight.md",
    "reviewer_editor_fit_planner": SUBMISSION / "reviewer_editor_fit_planner_AUTHOR_CONFIRMATION_REQUIRED.md",
    "software_reporting_checklist": SUBMISSION / "software_reporting_checklist.md",
    "article_fit_checklist": SUBMISSION / "article_fit_checklist.md",
    "author_declarations": SUBMISSION / "author_declarations_REQUIRED.md",
    "ai_disclosure_draft": SUBMISSION / "ai_disclosure_AUTHOR_CONFIRMATION_REQUIRED.md",
    "title_author_metadata": SUBMISSION / "title_author_metadata_AUTHOR_CONFIRMATION_REQUIRED.md",
    "reporting_summary_answer_bank": SUBMISSION / "reporting_summary_answer_bank_AUTHOR_CONFIRMATION_REQUIRED.md",
    "code_review": SUBMISSION / "code_for_review.md",
    "package_audit": SUBMISSION / "package_consistency_audit.md",
    "figure_inventory": SUBMISSION / "figure_file_inventory.csv",
    "source_inventory": SUBMISSION / "source_data_and_statistics_inventory.csv",
    "bib": SUBMISSION / "references_for_submission.bib",
    "reporting_summary": SUBMISSION / "reporting_summary_REQUIRED.md",
    "json_manifest": SUBMISSION / "submission_package_manifest.json",
    "gate": GATES / "9.27.json",
}

REQUIRED_READER_INPUTS = [
    SECTIONS / "abstract.md",
    SECTIONS / "introduction.md",
    SECTIONS / "results.md",
    SECTIONS / "discussion.md",
    SECTIONS / "methods.md",
    SECTIONS / "data_availability.md",
    SECTIONS / "code_availability.md",
    FIGURES / "figure_legends.md",
    SUPPLEMENTARY / "supplementary_methods.md",
    REFS / "references.bib",
]

FORBIDDEN_DOWNSTREAM_PATHS = [
    SUBMISSION / "pi_review_packet.md",
    WORKSPACE / "stage9_completion_report.md",
]

READER_FORBIDDEN_PATTERNS = [
    re.compile(r"<!--|-->"),
    re.compile(r"\b(?:PARA|CLM|MTH|FIG|SFIG|STBL|STAT|ART|SUPP|REF)-\d{3,4}\b"),
    re.compile(r"\bStage 9\b|stage9", re.IGNORECASE),
    re.compile(r"figure package|panel package", re.IGNORECASE),
]

PACKAGE_FORBIDDEN_PATTERNS = [
    re.compile("/" + "Users/"),
    re.compile("/" + "Volumes/"),
    re.compile("Library/" + "LaunchAgents"),
    re.compile(r"\b" + "sk-" + r"[A-Za-z0-9_-]{10,}"),
    re.compile(r"\b" + "ghp" + "_" + r"[A-Za-z0-9_]{10,}"),
    re.compile(r"\b" + "github" + r"_pat_[A-Za-z0-9_]{10,}"),
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


def _closed_stage9_refresh_allowed() -> bool:
    if not GATE_929.exists():
        return False
    gate = _read_json(GATE_929)
    return (
        gate.get("pass") is True
        and gate.get("closure_status") == "complete_stage9_closed_version_bound"
    )


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


def _strip_html_comments(text: str) -> str:
    return re.sub(r"<!--.*?-->\s*", "", text, flags=re.S).strip()


def _drop_first_heading(text: str) -> str:
    return re.sub(r"^# .+?\n+", "", text.strip(), count=1)


def _word_count(text: str) -> int:
    return len(re.findall(r"\b[\w'-]+\b", text))


def _assembled_section(text: str, heading: str) -> str:
    if heading == "Abstract":
        match = re.search(r"^## Abstract\n+(?P<body>.*?)(?:\n{2,}|\Z)", text, flags=re.M | re.S)
        return match.group("body").strip() if match else ""
    if heading == "Introduction":
        match = re.search(
            r"^## Abstract\n+.*?\n{2,}(?P<body>.*?)(?=^## Results\n)",
            text,
            flags=re.M | re.S,
        )
        return match.group("body").strip() if match else ""
    pattern = re.compile(rf"^## {re.escape(heading)}\n(?P<body>.*?)(?=^## |\Z)", re.M | re.S)
    match = pattern.search(text)
    return match.group("body").strip() if match else ""


def _demote_headings(text: str) -> str:
    lines: list[str] = []
    for line in text.splitlines():
        if line.startswith("#") and not line.startswith("######"):
            lines.append("#" + line)
        else:
            lines.append(line)
    return "\n".join(lines).strip()


def _section(title: str, path: Path, demote: bool = True) -> str:
    body = _strip_html_comments(path.read_text(encoding="utf-8"))
    body = _drop_first_heading(body)
    if demote:
        body = _demote_headings(body)
    return f"## {title}\n\n{body.strip()}\n"


def _unheaded_section(path: Path, demote: bool = True) -> str:
    body = _strip_html_comments(path.read_text(encoding="utf-8"))
    body = _drop_first_heading(body)
    if demote:
        body = _demote_headings(body)
    return body.strip() + "\n"


def _preferred_title() -> str:
    body = (SECTIONS / "title_options.md").read_text(encoding="utf-8")
    for line in body.splitlines():
        if line.startswith("| TITLE-001 |"):
            parts = [part.strip() for part in line.strip("|").split("|")]
            if len(parts) >= 2 and parts[1]:
                return parts[1]
    return "RhoDyn infers residence states in live-cell perturbation data"


def _parse_bib_entries() -> list[dict[str, str]]:
    body = (REFS / "references.bib").read_text(encoding="utf-8")
    entries: list[dict[str, str]] = []
    for match in re.finditer(r"@\w+\{(REF-\d{4}),\s*(.*?)\n\}", body, flags=re.S):
        key, content = match.groups()
        fields: dict[str, str] = {"key": key}
        for field in ["title", "author", "year", "journal", "publisher", "doi", "url", "howpublished"]:
            found = re.search(rf"\b{field}\s*=\s*\{{(.*?)\}},", content, flags=re.S)
            fields[field] = re.sub(r"\s+", " ", found.group(1)).strip() if found else ""
        entries.append(fields)
    return sorted(entries, key=lambda row: row["key"])


def _references_markdown() -> str:
    rows = _parse_bib_entries()
    lines = ["## References", ""]
    for index, row in enumerate(rows, start=1):
        author = row.get("author", "").split(" and ")[0] if row.get("author") else "Reference"
        venue = row.get("journal") or row.get("publisher") or row.get("howpublished") or "source record"
        doi = row.get("doi", "")
        doi_text = f" doi:{doi}." if doi else ""
        lines.append(f"{index}. {author} et al. {row.get('title', '').rstrip('.')}. {venue} ({row.get('year', '')}).{doi_text}")
    return "\n".join(lines).rstrip() + "\n"


def _submission_bib() -> str:
    body = (REFS / "references.bib").read_text(encoding="utf-8")
    return "\n".join(line for line in body.splitlines() if not line.lstrip().startswith("%")).strip() + "\n"


def _supplemental_legend_block(heading: str, next_heading: str | None = None) -> str:
    body = _strip_html_comments((FIGURES / "figure_legends.md").read_text(encoding="utf-8"))
    start = body.index(heading)
    end = body.index(next_heading, start) if next_heading else len(body)
    block = body[start:end].strip()
    return _demote_headings(block)


def _main_legend_block() -> str:
    body = _strip_html_comments((FIGURES / "figure_legends.md").read_text(encoding="utf-8"))
    start = body.index("## Main figure legends")
    end = body.index("## Supplementary figure legends", start)
    return _demote_headings(body[start:end].strip())


def _assemble_main_text() -> str:
    parts = [
        f"# {_preferred_title()}",
        "",
        _section("Abstract", SECTIONS / "abstract.md", demote=False),
        _unheaded_section(SECTIONS / "introduction.md"),
        _section("Results", SECTIONS / "results.md"),
        _section("Discussion", SECTIONS / "discussion.md"),
        _section("Online Methods", SECTIONS / "methods.md"),
        _section("Data availability", SECTIONS / "data_availability.md"),
        _section("Code availability", SECTIONS / "code_availability.md"),
        _references_markdown(),
        _main_legend_block(),
    ]
    return "\n\n".join(part.strip() for part in parts if part.strip()) + "\n"


def _assemble_supplement() -> str:
    methods = _section("Supplementary Methods", SUPPLEMENTARY / "supplementary_methods.md")
    supp_figs = _supplemental_legend_block("## Supplementary figure legends", "## Supplementary table captions")
    supp_tables = _supplemental_legend_block("## Supplementary table captions")
    traceability = (
        "## Supporting-data traceability note\n\n"
        "Source-data workbooks, supplementary table bindings, processed measurement tables, model inputs and outputs, "
        "software commands, checksums, and replication metadata are retained in the package-support inventories and "
        "the public RhoDyn release surfaces. The Supplementary Information text keeps the scientific definitions, "
        "decision rules, figure legends, and table captions separate from file-path-level traceability.\n"
    )
    return "\n".join([
        "# Supplementary Information",
        "",
        methods.strip(),
        "",
        supp_figs,
        "",
        supp_tables,
        "",
        traceability.strip(),
        "",
    ])


def _figure_inventory() -> list[dict[str, Any]]:
    rows = _read_csv(LEDDERS / "figure_to_claim_to_artifact.csv")
    out: list[dict[str, Any]] = []
    for row in rows:
        fig_id = row["fig_id"]
        for fmt in ["pdf", "png", "svg"]:
            rel = f"manuscript/nature_methods/figures/rendered/{fig_id}/{fig_id}.{fmt}"
            path = ROOT / rel
            out.append(
                {
                    "fig_id": fig_id,
                    "format": fmt,
                    "path": rel,
                    "exists": str(path.exists()).lower(),
                    "size_bytes": path.stat().st_size if path.exists() else 0,
                    "sha256": _sha256(path) if path.exists() else "",
                    "engine_version": row.get("engine_version", ""),
                    "engine_commit": row.get("engine_commit", ""),
                    "placement": row.get("placement", ""),
                }
            )
    return out


def _source_inventory() -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for row in _read_csv(LEDDERS / "statistic_ledger.csv"):
        out.append(
            {
                "record_type": "statistic",
                "record_id": row["stat_id"],
                "display_or_table": row["fig_id"],
                "source_or_command": row["source_command"],
                "summary": row["value"],
                "boundary": row["test"],
            }
        )
    for row in _read_csv(SUPPLEMENTARY / "source_data_binding_ledger.csv"):
        out.append(
            {
                "record_type": "source_data",
                "record_id": row["table_id"],
                "display_or_table": row["linked_main_figures"],
                "source_or_command": row["source_paths"],
                "summary": row["role"],
                "boundary": row["interpretation_boundary"],
            }
        )
    return out


def _code_for_review() -> str:
    code = _strip_html_comments((SECTIONS / "code_availability.md").read_text(encoding="utf-8"))
    commands = _strip_html_comments((LEDDERS / "reproducibility_command_index.md").read_text(encoding="utf-8"))
    return f"""# Code for review

## Release identity

{code}

## Reproducibility commands

{commands}

## Review boundary

The commands are run from the RhoDyn repository root at the cited release tag and commit unless the command states a separate tool boundary. The review package does not redistribute controlled-access source material and does not claim package-index publication beyond the cited GitHub and Zenodo release surfaces.
"""


def _editor_triage_note() -> str:
    return """# Editor-triage note for Nature Methods

RhoDyn is submitted as a computational methods Article for live-cell perturbation biology. The central contribution is not the broad observation that cell signaling is dynamic, and it is not a claim that one trajectory summary should replace all endpoint or amplitude summaries. The contribution is an executable decision framework that places residence-state summaries, amplitude comparators, bounded-coupling margins, reserve-like endpoint coordinates, routed-output alternatives, uncertainty behavior, and cross-surface reproducibility into one inspectable workflow.

The validation ladder is designed to answer the editorial question of whether the method travels beyond one motivating system. It includes known-truth synthetic regimes, public DRG calcium trajectories, public ERK reporter trajectories, public-derived endpoint and paired-reporter demonstrations, held-out bounded-coupling contexts, margin-sensitivity checks, inconclusive examples, and parity across Python, command-line, backend, workbench, export bundle, source distribution, checksums, GitHub, and Zenodo surfaces. These examples are used as method stress tests rather than as a new disease-biology claim.

RhoDyn deliberately reports pass, fail, and inconclusive outcomes. A residence window is a declared analysis choice rather than an automatically discovered biological state. A bounded-coupling call means equivalence within a stated margin and context rather than absence of all coupling. Reserve-like endpoint summaries remain tied to the measured readout, and routed-output comparisons constrain tested endpoint alternatives without identifying direct biochemical edges.

The package is therefore best read as a method for reviewable dynamic operating-state interpretation, with the RhoA/microglia work serving as a reference use case rather than as hidden evidence for the methods Article. The method evidence for this Article is carried by the released RhoDyn package, public-derived demonstrations, software parity checks, and reproducibility archive.
"""


def _editorial_pitch() -> str:
    return """# Editorial pitch for Nature Methods

## Cover-letter draft

Dear Nature Methods editors,

We submit "RhoDyn infers residence states in live-cell perturbation data" as a computational methods Article for consideration in Nature Methods. The paper addresses a practical bottleneck shared by live-cell signaling, imaging, perturbation, and screening studies. Many experiments collect trajectories but still make decisions from endpoints, peaks, thresholds, means, or generic time-series features. RhoDyn asks a narrower and more testable question. Does the time a cell spends inside a declared response regime change the biological interpretation relative to amplitude-based summaries?

The contribution is not the broad observation that cell signaling is dynamic, and it is not a claim to replace trajectory-inference, state-space, or amplitude analyses. RhoDyn defines an inspectable method object that combines declared residence windows, dwell fraction, dwell time, segment count, amplitude comparators, bounded-coupling margins, reserve-like endpoint coordinates, routed-output alternatives, uncertainty summaries, and explicit failure modes in one reproducible workflow. The method therefore tells users when residence adds information beyond amplitude, when a simpler summary is sufficient, and when the supplied data should withhold a stronger interpretation.

The validation ladder is designed to avoid a single-case methods claim. The manuscript includes known-truth synthetic regimes, public DRG calcium trajectories, public ERK reporter trajectories, public-derived endpoint and paired-reporter demonstrations, held-out bounded-coupling contexts, margin-sensitivity cases, inconclusive examples, and parity across Python, command-line, backend, workbench, export-bundle, source-distribution, checksum, GitHub, and Zenodo surfaces. The RhoA/microglia work is treated as a reference use case rather than as hidden evidence for every methods claim.

We believe the manuscript fits Nature Methods because it presents an Article-level computational method, not a software wrapper around existing summaries, with immediate practical relevance for live-cell perturbation studies that now reduce trajectories to endpoints. A biologist can use RhoDyn to decide whether a tidy live-cell or endpoint perturbation table supports residence-state interpretation, amplitude-only interpretation, bounded coupling, reserve-like buffering, routed-output comparison, or a withheld conclusion. A quantitative reader can inspect the same decision through declared windows, margins, uncertainty summaries, versioned commands, reproducible exports, and source-linked example outputs.

The paper is deliberately scoped. Residence windows are declared analysis choices, not automatically discovered biological states. A bounded-coupling result means equivalence within a stated margin and context, not absence of all coupling. Reserve-like endpoint summaries remain tied to measured assays, and routed-output comparisons constrain tested alternatives without identifying direct biochemical edges. RhoDyn v0.1.0 is publicly available with GitHub and Zenodo release records, documented commands, public-derived example tables, tests, figure-ready outputs, and reviewable reproducibility surfaces. The submission package includes data and code availability statements, a Reporting Summary placeholder and answer bank for final portal completion, author-declaration prompts, a code-for-review surface, figure inventories, source-data/statistics inventories, prior-art positioning, and a desk-review objection map.

Sincerely,

The authors

## Cover-letter upload checklist

Complete or replace these author-confirmed statements before journal upload. They are not inferred from repository files.

- Related manuscripts. State whether any related manuscripts by any author are under consideration or in press elsewhere, or state that there are none.
- Prior editor discussions. State whether there have been prior discussions with a Nature Methods editor about this work, or state that there have been none.
- Dual consideration and approval. Insert only after author confirmation. "We confirm that this manuscript has not been published elsewhere and is not under consideration by another journal. All authors have approved the manuscript and agree with its submission to Nature Methods."
- Double-blind review. If choosing double-blind peer review, include author affiliations and contact information in the cover letter rather than the manuscript file.
- Reviewer suggestions and exclusions. Add recommended or excluded reviewers only if the authors choose to provide them, with brief reasons for exclusions.

## Presubmission-inquiry draft

Presubmission enquiries are optional and should not replace full manuscript submission. If the authors choose to ask for an editorial read before upload, the core question is whether Nature Methods sees RhoDyn as an Article-level computational method for live-cell perturbation biology.

RhoDyn is a computational method for residence-state inference in live-cell perturbation data. It is designed for situations in which endpoint, peak, mean, latency, or threshold summaries may miss the time a cell spends inside a biologically declared response window, giving the method immediate practical relevance for laboratories that already collect time-lapse reporter or endpoint perturbation tables. The method defines dwell fraction, dwell time, segment count, amplitude comparators, bounded-coupling margins, reserve-like endpoint coordinates, routed-output alternatives, uncertainty summaries, and explicit failure modes as inspectable outputs.

The proposed Article emphasizes method definition and validation rather than a new primary disease-biology claim. The evidence ladder includes known-truth synthetic regimes, public calcium and ERK live-cell reporter trajectories, public-derived endpoint and paired-reporter demonstrations, held-out bounded-coupling contexts, margin-sensitivity checks, inconclusive examples, and software parity across Python, command-line, backend, workbench, export bundle, source distribution, checksums, GitHub, and Zenodo release surfaces. The RhoA/microglia study is presented as a reference use case rather than as the sole basis for the methods claim.

The editorial point is that RhoDyn does not claim novelty for live-cell dynamics, trajectory inference, or morphodynamic embedding broadly. It contributes a practical decision framework for determining when declared residence carries state information beyond amplitude, when endpoint or amplitude summaries are sufficient, and when evidence is insufficient. The manuscript is scoped to avoid overclaiming. Declared windows are not automatically discovered states, bounded coupling is margin- and context-limited, reserve-like summaries are tied to measured endpoints, and routed-output comparisons do not identify biochemical edges.

We would value the editors' view on whether this framing fits Nature Methods as an Article describing a reusable computational method for live-cell perturbation biology, rather than as a software note or a single-system biological study.
"""


def _cover_letter_for_submission() -> str:
    return """# Cover letter for submission AUTHOR CONFIRMATION REQUIRED

This draft is prepared for Nature Methods upload after author confirmation. It does not add data, analyses, citations, figures, datasets, performance claims, manuscript text, reviewer names, conflicts, declarations, or portal metadata. Before upload, the authors must confirm related-manuscript status, prior editor discussions, author approval, reviewer suggestions or exclusions if used, double-blind review choice, declarations, and the official Reporting Summary.

Dear Nature Methods editors,

We submit "RhoDyn infers residence states in live-cell perturbation data" as a computational methods Article for consideration in Nature Methods. Many live-cell signaling, imaging, perturbation, and screening studies collect trajectories but still make biological decisions from endpoints, peaks, thresholds, means, or generic time-series features. RhoDyn addresses this gap with a reusable method for asking when the time a cell spends inside a declared response regime changes interpretation relative to amplitude-based summaries.

The contribution is not the broad observation that cell signaling is dynamic, and it is not a claim that residence should replace trajectory inference, state-space analysis, or endpoint summaries in every setting. RhoDyn defines an inspectable decision workflow that combines declared residence windows, dwell fraction, dwell time, segment count, amplitude comparators, bounded-coupling margins, reserve-like endpoint coordinates, routed-output alternatives, uncertainty summaries, and explicit failure modes. The method tells users when residence adds information beyond amplitude, when amplitude or endpoint summaries are sufficient, and when the supplied data should withhold a stronger interpretation.

The validation ladder is designed to avoid a single-case methods claim. The manuscript includes known-truth synthetic regimes, public DRG calcium trajectories, public ERK reporter trajectories, public-derived endpoint and paired-reporter demonstrations, held-out bounded-coupling contexts, margin-sensitivity checks, inconclusive examples, and parity across Python, command-line, backend, workbench, export-bundle, source-distribution, checksum, GitHub, and Zenodo surfaces. The RhoA/microglia material is treated as a reference use case rather than as hidden evidence for every method claim.

We believe the manuscript fits Nature Methods because it presents an Article-level computational method with immediate practical relevance for live-cell perturbation studies that now reduce trajectories to endpoints. A biologist can use RhoDyn to decide whether a tidy live-cell or endpoint perturbation table supports residence-state interpretation, amplitude-only interpretation, bounded coupling, reserve-like buffering, routed-output comparison, or a withheld conclusion. A quantitative reader can inspect the same decision through declared windows, margins, uncertainty summaries, versioned commands, reproducible exports, and source-linked examples.

The paper is deliberately scoped. Residence windows are declared analysis choices, not automatically discovered biological states. A bounded-coupling result means equivalence within a stated margin and context, not absence of all coupling. Reserve-like endpoint summaries remain tied to measured assays, and routed-output comparisons constrain tested alternatives without identifying direct biochemical edges. RhoDyn v0.1.0 is publicly available with GitHub and Zenodo release records, documented commands, public-derived example tables, tests, figure-ready outputs, and reviewable reproducibility surfaces.

[Author-confirmed related-manuscript, prior-editor-contact, dual-submission, double-blind-review, reviewer-suggestion, reviewer-exclusion, and declaration statements should be inserted here if required by the portal or journal instructions.]

Sincerely,

The authors
"""


def _prior_art_positioning_matrix() -> str:
    return """# Prior-art positioning matrix

This matrix is a collaborator-review aid for preserving the Nature Methods novelty boundary. It does not add citations, performance results, biological datasets, or manuscript claims. It maps the current reference library and representative methods-paper corpus onto the question an editor is likely to ask first, namely what RhoDyn contributes beyond existing dynamic-state, trajectory, imaging, and software-method literature.

## Editorial distinction

RhoDyn should not be positioned as the first method to treat live-cell signals as dynamic, the first trajectory-inference tool, the first single-cell state-space method, or a replacement for endpoint or amplitude summaries. Its methods contribution is the operational decision object that places declared residence windows, amplitude comparators, bounded-coupling margins, reserve-like endpoint coordinates, routed-output alternatives, uncertainty behavior, failure modes, and reproducibility surfaces into one inspectable workflow for live-cell perturbation data.

## Prior-art comparison

| Prior-art class | Representative support in the package | What the prior work already establishes | RhoDyn contribution being claimed | Boundary that must remain visible |
| --- | --- | --- | --- | --- |
| Trajectory inference and method benchmarking | Saelens et al.; CellRank; transient-state dynamical modeling; state-space visualization references in `references_for_submission.bib` and `refs/representative_methods_papers.md`. | Biological interpretation can depend on trajectories, transition structure, state geometry, uncertainty, and benchmark design rather than static labels alone. | RhoDyn applies a narrower live-cell perturbation decision object that asks whether time in a declared response window changes interpretation relative to endpoint, peak, mean, latency, or threshold summaries. | Do not imply that RhoDyn replaces trajectory-inference methods, learns cell fate direction, or discovers biological states automatically. |
| Live-cell reporter and morphodynamic analyses | Public DRG calcium and ERK reporter source records, plus the live-cell morphodynamic prior-art reference. | Reporter trajectories and cell morphology can encode time-dependent biological information. | RhoDyn makes residence-amplitude separation reviewable on tidy trajectory inputs, with window sensitivity and uncertainty surfaced alongside the decision. | Do not claim that every reporter has a biologically meaningful residence regime or that residence is always more informative than amplitude. |
| Generalist software workbenches and reusable method platforms | Cellpose, Squidpy, scvi-tools, DeepLabCut, and related corpus entries. | A methods paper can contribute reusable software, documentation, examples, and reproducible workflows across biological contexts. | RhoDyn packages residence scoring, coupling decisions, reserve-like endpoints, routed alternatives, backend/workbench parity, command-indexed reproduction, and citable archives as one analysis workflow. | Do not let the manuscript become software marketing. The paper must remain a method definition plus validation argument. |
| Bounded-coupling and equivalence-style statistical decisions | Bounded-coupling Methods, source-data/statistics inventory, held-out ERK/Akt contexts, and Reporting Summary answer bank. | Non-significant contrasts do not by themselves establish equivalence, and margins must be declared before interpretation. | RhoDyn keeps passing, failing, and inconclusive bounded-coupling outcomes visible under declared margins and uncertainty rules. | A passing call means equivalence within the stated margin and context, not absence of all slower or condition-specific coupling. |
| Endpoint, reserve-like, and routed-output model comparison | Cell Painting/MitoTox endpoint demonstrations, reduced-architecture comparisons, source-data/statistics inventory, and Supplementary Information. | Endpoint datasets can be used for model comparison, but measured endpoints do not automatically identify mechanisms. | RhoDyn extends beyond trajectory-only summaries to decision support for endpoint rows, measured reserve-like coordinates, and routed-output alternatives. | Reserve-like summaries remain tied to the measured endpoint, and effective routed-output parameters do not identify direct biochemical interactions. |
| Reproducible computational-method release practice | RhoDyn GitHub and Zenodo record, PanelForge DOI, code-for-review surface, software checklist, and public-access verification. | Reusable methods require documented code, versioning, examples, command routes, and release identifiers. | RhoDyn makes Python, CLI, backend, workbench, figure-ready outputs, checksums, GitHub, and Zenodo surfaces mutually inspectable for the reported demonstrations. | Do not claim package-index distribution or unrestricted redistribution of optional controlled-access reference-case material unless authors provide those records. |

## Desk-rejection risk controlled by this matrix

The matrix protects the manuscript from two opposite errors. It prevents novelty inflation by acknowledging that dynamic-state and live-cell analysis are established areas. It also prevents novelty dilution by making the specific RhoDyn method object visible as an integrated, executable decision framework rather than as a loose set of trajectory summaries.

## Author use

Use this matrix when checking the title, Abstract, Introduction, cover letter, presubmission inquiry, reviewer suggestions, and editor-facing portal text. Do not paste the matrix into the manuscript unless the authors intentionally add a short related-methods note. If any wording says or implies that RhoDyn is a universal residence detector, an automatic state-discovery method, a mechanism-discovery engine, or a replacement for amplitude analysis, revise it back to the scoped method claim above.
"""


def _validation_breadth_map() -> str:
    return """# Validation breadth and boundary map

This map is a collaborator-review aid for the Nature Methods validation argument. It does not add data, analyses, citations, figures, datasets, performance claims, or manuscript text. It condenses where the current package tests RhoDyn, what each validation layer can support, and what each layer must not be used to claim.

## Core editorial question

The relevant validation question is whether RhoDyn behaves as a reusable residence-state decision framework beyond one motivating biological example. The current package answers that question through a ladder of known-truth, public trajectory, endpoint, held-out, and software-reproducibility tests. The ladder supports portability of the method object and its decision boundaries. It does not claim that every biological system contains a residence regime.

## Validation ladder

| Layer | Package evidence | What it tests | Decision value | Boundary |
| --- | --- | --- | --- | --- |
| Known-truth synthetic regimes | Main Fig. 2, Supplementary Methods, Stage 7.2 benchmark outputs | Whether residence, amplitude, bounded-coupling, reserve-like, and routed-output decisions behave correctly when truth is known | Establishes that the declared decision rules can recover positive, negative, and ambiguous cases | Synthetic truth is method validation, not biological generality |
| Public live-cell trajectory examples | Main Fig. 3, public DRG calcium and ERK reporter examples, source-data/statistics inventory | Whether tidy public time-lapse reporter tables can be analyzed without private manuscript data | Shows that residence and amplitude summaries can separate or agree depending on the reporter and window | Public examples are portability tests, not proof that residence is always superior |
| Public-derived endpoint and paired-reporter demonstrations | Main Fig. 4, endpoint/reserve/routed-output case-study tables | Whether RhoDyn can handle non-trajectory endpoints, bounded coupling, reserve-like coordinates, and reduced alternatives | Extends the method beyond single-reporter trajectories | Reserve-like labels remain tied to measured endpoints and do not directly measure unobserved biological reserve |
| Held-out contexts and margin sensitivity | Main Fig. 5, held-out bounded-coupling decisions, margin-sensitivity outputs | Whether declared decisions remain inspectable when contexts, margins, or evidence strength change | Keeps pass, fail, and inconclusive outcomes visible | Held-out success is scoped transfer, not universal coupling or residence biology |
| Software and reproducibility parity | Main Fig. 6, code-for-review file, release checks, source distribution, workbench/backend parity, GitHub, Zenodo, checksums | Whether a reviewer can run the method, inspect parameters, and reproduce representative outputs | Makes the method reviewable as software and algorithm, not only as manuscript prose | Reproducibility surfaces support reviewability but do not create new biological evidence |
| RhoA/microglia reference use case | Optional reviewer-access reference-use-case surfaces and controlled-access boundary notes | Whether the method language remains biologically interpretable in a deep motivating application | Provides biological depth without carrying every method claim | The reference use case should not dominate validation breadth or reviewer assignment |

## What the validation ladder supports

- RhoDyn can report residence-supported, amplitude-sufficient, bounded-coupling, reserve-like, routed-output, and withheld decisions from declared inputs.
- The package tests the same method object across synthetic, public trajectory, public-derived endpoint, held-out, and software-reproducibility settings.
- The manuscript is strongest when the validation ladder is described as method portability plus decision-boundary behavior, not as a universal biological law.

## Claims to avoid during upload

- Do not say that RhoDyn discovers biological states automatically.
- Do not say that residence is always more informative than amplitude.
- Do not say that every live-cell reporter contains a residence regime.
- Do not say that bounded coupling proves absence of all coupling.
- Do not say that reserve-like endpoint summaries directly measure unobserved biological reserve.
- Do not let the RhoA/microglia reference use case replace the synthetic, public, endpoint, held-out, and software-validation evidence.

## Cover-letter use

If validation breadth is challenged, the safest response is that the manuscript tests decision behavior across known-truth regimes, public live-cell reporters, endpoint and paired-reporter demonstrations, held-out contexts, and software parity. The response should also state that RhoDyn deliberately returns amplitude-sufficient and inconclusive outcomes where the evidence does not support a residence-state interpretation.
"""


def _editor_objection_response_map() -> str:
    return """# Editor-objection response map

This map is a collaborator-review aid for the most likely Nature Methods desk-review objections. It does not add evidence, citations, figures, datasets, performance claims, or manuscript text. It links each objection to the current package evidence and the wording boundary that should be preserved during cover-letter, presubmission, and portal preparation.

| Likely editorial objection | Evidence already present in the package | Safe response | Boundary to preserve |
| --- | --- | --- | --- |
| This reads like software packaging rather than a methods Article. | Main text, Supplementary Information, software-reporting checklist, method specification, public case-study demonstrations, and parity checks across Python, CLI, backend, workbench, exports, source distribution, checksums, GitHub, and Zenodo. | RhoDyn is framed as a method because it defines a decision object for residence-state inference, amplitude comparison, bounded coupling, reserve-like endpoints, routed-output alternatives, uncertainty, and failure modes. | Do not describe UI, backend, or archive parity as the scientific contribution by itself. |
| The novelty may be too close to existing live-cell trajectory and state-space methods. | Prior-art positioning matrix, reference library, representative methods-paper corpus, editor-triage note, and main Introduction. | The claim is not novelty for dynamic signaling, trajectories, or state-space analysis. The claim is an inspectable workflow that asks when declared residence windows change interpretation relative to amplitude, endpoint, peak, latency, or threshold summaries. | Do not claim first-in-field status for live-cell dynamics or automatic state discovery. |
| The validation may be too centered on one motivating biology problem. | Known-truth synthetic regimes, public DRG calcium trajectories, public ERK reporter trajectories, public-derived endpoint and paired-reporter demonstrations, held-out bounded-coupling contexts, margin-sensitivity checks, and inconclusive examples. | The RhoA/microglia work is a reference use case, while the Nature Methods evidence ladder tests the method across synthetic, public trajectory, endpoint, reserve-like, routed-output, and held-out contexts. | Do not imply that the reference use case generated the method evidence for every claim. |
| The method may overinterpret residence as mechanism. | Claim-strength rules, limitations matrix, Results and Discussion boundaries, figure legends, and Reporting Summary answer bank. | Residence windows are declared analysis choices. Passing residence-amplitude separation supports a reviewable dynamic operating-state interpretation, not automatic mechanism discovery. | Do not state that every reporter contains a biologically meaningful residence regime. |
| Equivalence or bounded-coupling language could be mistaken for no coupling. | Bounded-coupling Methods, source-data/statistics inventory, held-out examples, and editor-triage note. | A bounded-coupling call means equivalence within a stated margin and context. Failing and inconclusive calls remain visible. | Do not say absence of all coupling, especially slower, delayed, or condition-specific coupling. |
| Reserve-like and routed-output examples could be read as direct biology. | Supplementary Information, source-data/statistics inventory, limitations matrix, PI review action decisions, and figure legends. | Reserve-like summaries are tied to measured endpoints, and routed-output comparisons constrain tested alternatives. Effective parameters are not biochemical edges. | Do not turn endpoint coordinates into direct reserve capacity or motor-routing mechanism claims. |
| Reproducibility may not be strong enough for a software-methods paper. | Code-for-review file, public-access verification, GitHub and Zenodo identifiers, software checklist, command index, source-data/statistics inventory, package manifest, and release checks. | The package gives versioned commands, expected outputs, checksums, public release surfaces, and reviewable examples for the current RhoDyn release. | Do not claim package-index distribution or unrestricted access to optional controlled reference-case material. |
| The paper may not tell a broad enough story for Nature Methods. | Title, Abstract, editor-triage note, editorial pitch, prior-art matrix, and figure spine. | The broad story is dynamic operating-state interpretation for live-cell perturbation data when endpoint or amplitude summaries may be insufficient. | Do not overextend to disease prediction, clinical utility, or universal residence superiority. |

## Use during final preparation

Use this map as an editor-facing stress test before submission. If a cover letter, presubmission inquiry, title, Abstract, or portal note cannot answer these objections using the safe-response column, revise the wording or keep the point out of the submission package. If answering an objection would require new data, new benchmarking, or a stronger biological claim than the package supports, retain it as a limitation rather than filling the gap rhetorically.
"""


def _editor_two_minute_triage_simulation() -> str:
    return """# Two-minute editor triage simulation

This simulation is a collaborator-review aid for the first two minutes of editorial triage. It does not add evidence, citations, analyses, figures, datasets, performance claims, or manuscript text. It checks whether the title, Abstract, cover-letter opening, figure spine, availability surfaces, and claim boundaries make the Nature Methods fit visible before a detailed review begins.

## What an editor can see quickly

| First-pass item | What it must communicate | Current package signal | Triage verdict | Wording to preserve |
| --- | --- | --- | --- | --- |
| Title | The object is residence-state inference in live-cell perturbation data, not a single RhoA biology result. | `RhoDyn infers residence states in live-cell perturbation data`. | visible | Keep residence states, live-cell perturbation data, and method identity together. |
| Abstract | The problem, method object, validation breadth, output decisions, and limits are all present without citation dependence. | The Abstract moves from endpoint-reduction loss to residence windows, amplitude comparators, bounded coupling, reserve-like endpoints, routed alternatives, synthetic and public cases, and reproducible software surfaces. | visible | Preserve amplitude-sufficient, unresolved, and measurement-limited cases alongside positive residence examples. |
| Cover-letter opening | The submission is an Article-level computational method rather than a software wrapper or a single-system biology story. | The pitch states that RhoDyn asks whether time inside a declared response regime changes interpretation relative to amplitude summaries. | visible | Keep the method question narrow and testable. |
| Figure spine | The six main figures carry the full method argument. | Figures 1-6 cover method definition, synthetic truth, public live-cell trajectories, endpoint/reserve/routed demonstrations, held-out validation, and software reproducibility. | visible | Keep the six-figure sequence as concept, truth, public trajectories, endpoint demonstrations, held-out tests, and reproducibility. |
| Code and data availability | The review package can be inspected through public release and archive surfaces. | The package points to the public GitHub release, Zenodo software archive, PanelForge figure-rendering DOI, command routes, checksums, and package inventories. | visible | Do not imply package-index distribution or unrestricted redistribution of optional controlled-access reference-case material. |
| Claim boundaries | Positive calls remain scoped to the measured inputs and declared decision rules. | Declared windows are not automatic state discovery, bounded coupling is margin- and context-limited, reserve-like endpoints stay tied to measured readouts, and routed-output parameters are not biochemical edges. | visible | Preserve the distinction between method-supported decisions and mechanism discovery. |

## Simulated first-pass decision

The current package should be readable as a Nature Methods computational-methods Article if the title, Abstract, cover letter, and figure spine are kept together. The two-minute read has a clear method object, a validation ladder beyond one motivating system, visible software and archive surfaces, and explicit interpretation limits.

The residual desk-review risk is not missing evidence in this package; it is loss of focus if the submission text drifts toward software marketing, universal residence claims, or a single-system biology story. The safest first-pass message is that RhoDyn is a reviewable decision framework for asking when declared residence, bounded coupling, reserve-like endpoint coordinates, or routed-output alternatives change interpretation relative to simpler summaries, and when they do not.

## Final author check before upload

If an editor can answer these three questions in the first two minutes, the package is aligned for triage.

1. What is the method object?
2. What evidence shows it travels beyond one motivating system?
3. What claims are explicitly not being made?
"""


def _current_policy_preflight() -> str:
    return """# Current Nature Methods policy preflight

This preflight is a collaborator-review aid tied to official Nature Methods and Nature Portfolio guidance checked on 2026-07-07. It does not add evidence, citations, analyses, figures, datasets, performance claims, or manuscript text. It asks whether the current RhoDyn submission package makes the Article fit, reporting requirements, data/code availability, and algorithm/software review surfaces visible before upload.

## Official sources used

- Nature Methods content types. https://www.nature.com/nmeth/content
- Nature Portfolio reporting standards and availability of data, materials, code and protocols. https://www.nature.com/nature-portfolio/editorial-policies/reporting-standards
- Nature Methods guidelines for algorithms and software. https://communities.springernature.com/posts/guidelines-for-algorithms-and-software-in-nature-methods

## Policy-to-package check

| Policy item | Official expectation being checked | Current package evidence | Preflight verdict | Remaining author action |
| --- | --- | --- | --- | --- |
| Article content type | An Article is a report describing a novel method or tool, with full technical description and strong validation for performance, reproducibility, general applicability, and potential for discovering new biology. | Title, Abstract, Results, Online Methods, six-figure spine, Supplementary Information, software checklist, and code-for-review surface frame RhoDyn as a residence-state inference method rather than as a single biology case. | aligned | Preserve Article framing during cover-letter and portal entry. |
| Article format | Abstract up to 150 words, main text target 3,000 words with editorial discretion to 5,000, up to 6 display items, unheaded Introduction, Results and Online Methods subheadings, no Discussion subheadings, and approximately 50 references. | `article_fit_checklist.md` records the 150-word Abstract, six display items, reference count, section order, Results and Methods subheadings, and unheaded Discussion. | aligned | Final uploaded files should preserve the same structure. |
| Reporting Summary | Life-science research submissions must include a completed Reporting Summary for editors and reviewers. | `reporting_summary_REQUIRED.md` and `reporting_summary_answer_bank_AUTHOR_CONFIRMATION_REQUIRED.md` are present and mapped to current evidence. | registered | Complete the official Springer Nature Reporting Summary form by author confirmation. |
| Data availability | The minimum dataset needed to interpret, verify, and extend the article should be transparent, preferably through repositories, and restrictions must be disclosed at submission and in the manuscript. | Main text availability statements, code-for-review surface, source-data/statistics inventory, public URL report, Zenodo records, and controlled reference-case wording are present. | aligned | Confirm final portal metadata and any controlled-access language. |
| Code and algorithm availability | Previously unreported custom code or algorithms central to the paper must be available to editors and reviewers; best practice is release through a DOI-minting repository with access and restrictions described. | Public GitHub, Zenodo software DOI, method specification, API/CLI docs, command index, source-distribution checks, software checklist, and code-for-review surface are present. | aligned | Verify release tag and reviewer-access links immediately before upload. |
| Algorithm or software description | Nature Methods software guidance expects usable source code, pseudocode, mathematical description, or compiled software where appropriate, with documentation and dependencies. | RhoDyn provides source code, mathematical Methods, API/CLI documentation, examples, backend/workbench parity, tests, and reproducibility commands. | aligned | Do not replace the method description with software-marketing language. |
| General applicability | Validation should demonstrate that the method travels beyond one narrow setting while retaining limits. | Synthetic truth cases, public calcium and ERK trajectories, public-derived endpoint/reserve/routed demonstrations, held-out bounded-coupling contexts, and inconclusive cases are visible in the package. | aligned | Do not claim universal residence regimes or automatic state discovery. |

Reporting Summary remains a human submission action. The answer bank can guide completion, but the official form requires author-confirmed transfer into the Springer Nature portal materials.

## Desk-rejection risk if this preflight drifts

The strongest risk is not the absence of a required surface, but loss of focus during final portal preparation. If the uploaded cover letter, Abstract, or author responses describe RhoDyn mainly as software packaging, as a universal residence detector, or as a hidden extension of the RhoA/microglia reference use case, the package becomes easier to triage away from Nature Methods. Keep the upload language tied to the Article-level method object, validation breadth, reproducibility surface, and explicit interpretation limits.
"""


def _reviewer_editor_fit_planner() -> str:
    return """# Reviewer and editor fit planner AUTHOR CONFIRMATION REQUIRED

This file is a collaborator-review aid for choosing reviewer suggestions, reviewer exclusions, and editor-facing fit language during Nature Methods upload. It does not nominate reviewers, infer conflicts, or add manuscript evidence. Author confirmation is required before any name, exclusion, or portal text is entered into the journal system.

## Purpose and boundary

RhoDyn should be evaluated as a computational method for live-cell perturbation data rather than as a software note or a single RhoA/microglia biology paper. Reviewer suggestions should therefore cover the method object, uncertainty logic, perturbation biology, software reproducibility, and biological reference-use-case scope. The RhoA/microglia reference use case should not dominate reviewer assignment.

## Expertise coverage needed

| Expertise area | Why it is needed | Package evidence | Suggested reviewer profile | Exclusion or conflict notes |
| --- | --- | --- | --- | --- |
| Live-cell signaling dynamics and reporter trajectories | The method compares residence, amplitude, dwell time, and segment behavior in live-cell traces. | Main text, Fig. 1-3, Supplementary Methods, trajectory schema, public calcium and ERK examples. | A reviewer experienced with live-cell reporters, signaling dynamics, or perturbation time courses. | Exclude only if the author team confirms a collaboration, competition, institutional conflict, or other journal-relevant conflict. |
| Computational methods and time-series state inference | RhoDyn is a decision workflow for declared residence states, amplitude comparators, uncertainty, and failure modes. | Methods, method specification, limitations matrix, synthetic truth cases, benchmark reports. | A quantitative reviewer who can assess time-series summaries, state definitions, uncertainty, and benchmark design. | Avoid reviewers who would evaluate only biological novelty without assessing the method definition. |
| Perturbation endpoint analysis and bounded-coupling decisions | Figures 4 and 5 extend the method beyond single-reporter trajectories into endpoint, reserve-like, and routed-output decisions. | Bounded-coupling Methods, source-data/statistics inventory, margin-sensitivity reports, endpoint demonstrations. | A reviewer familiar with perturbation biology, equivalence or bounded-effect reasoning, and endpoint-model comparison. | Do not suggest a reviewer who would require unreported wet-lab mechanisms for all effective parameters. |
| Bioimage, screening, or scientific-software reproducibility | The package includes figure-ready outputs, workbench routes, command-indexed reproduction, GitHub, Zenodo, and checksum surfaces. | Fig. 6, code-for-review file, software checklist, release checks, source-distribution and clean-room reports. | A reviewer who can judge reusable software, documented examples, release engineering, and reproducible scientific computing. | Exclude only with author-confirmed conflict, not because a reviewer may be technically demanding. |
| Statistical decision rules and uncertainty reporting | Passing, failing, and inconclusive calls are all part of the method claim. | Bounded-coupling decisions, interval summaries, ROPE-style fields where used, source-data/statistics inventory. | A reviewer who understands uncertainty, equivalence-margin logic, and the distinction between non-significance and equivalence. | Do not use reviewers whose likely critique depends on treating all non-significant contrasts as equivalence. |
| Biological reference-use-case expertise | The optional RhoA/microglia use case can test whether the method language remains biologically interpretable. | Reference-use-case wording, limitations, and controlled-access boundary statements. | A domain biologist may be useful after the method and software expertise are covered. | Domain expertise should not replace the quantitative and software-methods review mix. |

## Reviewer balance rule

Use a balanced reviewer set only after author confirmation. A strong set should include at least one live-cell signaling or perturbation-dynamics reviewer, one computational methods or time-series reviewer, and one software or reproducibility reviewer. Add a disease or cell-biology domain reviewer only if the method expertise is already represented.

## Suggested reviewer template

Complete one row per author-approved suggested reviewer.

| Field | Author-confirmed value |
| --- | --- |
| Reviewer name | [name] |
| Institution | [institution] |
| Email or ORCID if requested by portal | [email or ORCID] |
| Expertise match | [live-cell signaling, time-series methods, perturbation endpoints, reproducibility, statistics, or domain biology] |
| Why this reviewer can evaluate RhoDyn | [short evidence-based reason] |
| Conflict check | [author-confirmed no conflict, or do not suggest] |

## Exclusion template

Complete one row per author-approved exclusion.

| Field | Author-confirmed value |
| --- | --- |
| Excluded reviewer name | [name] |
| Institution | [institution] |
| Reason for exclusion | [collaboration, direct competition, conflict, confidentiality, or other journal-acceptable reason] |
| Scientific relevance of exclusion | [short reason if needed] |
| Author confirmation | [confirmed by author team] |

## Editor-facing fit note

Use this only as draft language for a portal note or cover-letter sentence if the journal provides a reviewer-fit field.

RhoDyn is best evaluated by reviewers spanning live-cell perturbation dynamics, computational method validation, statistical decision rules, and reproducible scientific software. The RhoA/microglia reference use case should not dominate reviewer assignment because the Article-level claim is the reusable residence-state inference method and its validation ladder across synthetic, public trajectory, endpoint, and software-reproducibility examples.

## Upload checks

- Confirm every suggested or excluded reviewer with all authors before upload.
- Do not infer conflicts from repository history, manuscript drafts, citation overlap, or personal assumptions.
- Do not suggest only RhoA, microglia, or Alzheimer's disease specialists unless the method-review expertise is already covered.
- Preserve the method claim during reviewer selection. RhoDyn is not submitted as a single-system biological discovery paper.
"""


def _software_reporting_checklist() -> str:
    return """# Nature Methods software-reporting checklist

This checklist maps the current RhoDyn package to Nature Methods software and algorithm reporting expectations. It is a review-support surface for the submitted computational method and does not add new analyses, figures, datasets, or manuscript claims.

Official guidance used. Nature Methods Article content type expects a novel method or tool with a full technical description and strong validation for performance, reproducibility, general applicability, and potential for discovering new biology. Nature Methods software guidance asks that central unpublished software be supplied in usable form, with source code or an equivalent mathematical/algorithmic description, documentation, sample data, expected output, version information, and license terms where appropriate.

| Reporting item | RhoDyn package evidence | Status | Residual action |
| --- | --- | --- | --- |
| Source code supplied for review | Public GitHub release `v0.1.0`, pinned commit `4b1211cadd1fb3af34a1ec3e21f62383ffd9e368`, and Zenodo version DOI `10.5281/zenodo.21036616`. | ready | Verify reviewer access to the public repository at upload. |
| Full algorithmic or mathematical description | Main Online Methods, Supplementary Information, `docs/stage7_method_specification.md`, `docs/stage7_limitations_matrix.md`, and `docs/api_reference.md` define input objects, residence windows, bounded coupling, reserve-like summaries, routed-output comparisons, uncertainty summaries, and failure modes. | ready | Preserve the distinction between declared windows and automatic state discovery during final edits. |
| Installation and user documentation | `README.md`, `docs/index.md`, `docs/input_schema_guide.md`, `docs/cli_reference.md`, `docs/api_reference.md`, `docs/example_workflows.md`, and `docs/reproducibility_card.md` describe installation, schemas, CLI/API use, and clean-room checks. | ready | Confirm final upload links point to the versioned release. |
| Sample data supplied | `examples/` plus public-derived case-study tables used by Stage 7 demonstrations provide trajectory, endpoint, reserve-like, and bounded-coupling inputs without redistributing controlled raw material. | ready | Do not add private or manuscript-controlled raw data to the software package. |
| Expected outputs documented | `manuscript/nature_methods/ledgers/reproducibility_command_index.md`, `code_for_review.md`, and Stage 7 gate reports define commands and expected outputs for synthetic cases, public signaling, endpoint/reserve/routing demonstrations, held-out validation, documentation, backend/workbench parity, and figure rendering. | ready | Keep command outputs tied to the cited release tag. |
| Software version and parameter recording | Release identity, command index, exported analysis bundles, backend job model, and package manifests preserve input schema, parameter choices, software version, checksums, and report exports. | ready | Check final reviewer bundle retains the command index. |
| License and reuse terms | RhoDyn is Apache-2.0. PanelForge figure rendering is MIT and pinned to `panelforge-figures` v3.14.1 with DOI `10.5281/zenodo.20811171`. | ready | Confirm license files remain in the release archive. |
| Web or service component | Backend and workbench surfaces are included as reproducible local/service code with parity tests. No hosted web service is claimed as required for evaluation. | ready | If a hosted demo is later offered, provide anonymous reviewer access separately. |
| Restrictions and boundaries | PyPI publication is not claimed for v0.1.0. RhoDyn is not presented as image segmentation, raw microscopy ingestion, disease prediction, or automatic mechanism discovery. | ready | Keep these boundaries in any cover-letter or portal wording. |
| Journal upload forms | Reporting Summary and portal metadata are registered as human submission actions rather than repository-derived scientific evidence. | human action | Complete the official Springer Nature forms before submission. |
"""


def _article_fit_checklist(main_text: str) -> str:
    abstract_words = _word_count(_assembled_section(main_text, "Abstract"))
    intro_results_discussion = "\n\n".join(
        _assembled_section(main_text, heading)
        for heading in ["Introduction", "Results", "Discussion"]
    )
    main_body_words = _word_count(intro_results_discussion)
    methods_words = _word_count(_assembled_section(main_text, "Online Methods"))
    display_items = main_text.count("#### Figure ")
    references = len(re.findall(r"^\d+\. ", _assembled_section(main_text, "References"), re.M))
    discussion_has_subheadings = bool(re.search(r"^### ", _assembled_section(main_text, "Discussion"), re.M))
    results_has_subheadings = bool(re.search(r"^### ", _assembled_section(main_text, "Results"), re.M))
    methods_has_subheadings = bool(re.search(r"^### ", _assembled_section(main_text, "Online Methods"), re.M))

    rows = [
        ("Content-type decision", "Nature Methods Article", "Selected because the package reports a novel computational method/tool with validation, software, biological demonstrations, and full method description.", "fit"),
        ("Rejected alternative", "Analysis", "Not selected because RhoDyn is not only a comparison of established methods; it defines and releases a method object.", "not selected"),
        ("Rejected alternative", "Resource", "Not selected because the central contribution is not only a dataset or software catalog.", "not selected"),
        ("Rejected alternative", "Brief Communication", "Not selected because the method requires formal definition, validation, software review surfaces, examples, and limitations.", "not selected"),
        ("Abstract length", f"{abstract_words} words", "Nature Methods Article limit is up to 150 words and unreferenced.", "pass" if abstract_words <= 150 and "(" not in _assembled_section(main_text, "Abstract") else "check"),
        ("Main text length", f"{main_body_words} words", "Nature Methods Article target is 3,000 words, with up to 5,000 words at editorial discretion, excluding abstract, Methods, references, and figure legends.", "pass" if main_body_words <= 3000 else "check"),
        ("Main display items", f"{display_items} figures", "Nature Methods Article limit is up to six main figures and/or tables.", "pass" if display_items <= 6 else "check"),
        ("Reference count", f"{references} references", "Nature Methods Article guidance typically recommends up to 50 references.", "pass" if references <= 50 else "check"),
        ("Article section order", "Abstract, unheaded Introduction text, Results, Discussion, Online Methods, availability, references, legends", "The assembled submission source keeps the Introduction text before Results without a visible Introduction heading, matching the Nature Methods Article structure.", "pass"),
        ("Results subheadings", "present" if results_has_subheadings else "absent", "Nature Methods permits topical Results subheadings.", "pass" if results_has_subheadings else "check"),
        ("Methods subheadings", "present" if methods_has_subheadings else "absent", "Nature Methods permits topical Online Methods subheadings.", "pass" if methods_has_subheadings else "check"),
        ("Discussion subheadings", "absent" if not discussion_has_subheadings else "present", "Nature Methods Article Discussion does not contain subheadings.", "pass" if not discussion_has_subheadings else "check"),
    ]
    lines = [
        "# Nature Methods Article-fit checklist",
        "",
        "This checklist makes the content-type and format fit of the current RhoDyn package visible for author review. It is a submission-support surface and does not add new analyses, figures, datasets, or manuscript claims.",
        "",
        "| Check | Current package evidence | Nature Methods relevance | Status |",
        "| --- | --- | --- | --- |",
    ]
    for check, evidence, relevance, status in rows:
        lines.append(f"| {check} | {evidence} | {relevance} | {status} |")
    lines.extend(
        [
            "",
            "Residual human action. Confirm final file naming, Reporting Summary, and portal metadata at upload. These are submission actions, not evidence gaps in the current manuscript package.",
        ]
    )
    return "\n".join(lines) + "\n"


def _author_declarations_checklist() -> str:
    return """# Author declarations REQUIRED

This checklist registers author-controlled declaration fields that must be completed before Nature Methods upload. It does not invent author, funding, competing-interest, ethics, or AI-use statements.

## Required declarations before upload

| Declaration | Required action | Current package evidence | Status |
| --- | --- | --- | --- |
| Acknowledgements and funding | Confirm final funding and acknowledgement wording, or confirm that no funding statement is needed. | No author-confirmed funding text is stored in the RhoDyn methods package. | human action |
| Author contributions | Complete the author contribution statement using the final author list and the contribution taxonomy expected by the journal. | The repository cannot infer author order or contribution roles. | human action |
| Title, author list, and affiliations | Complete the title page metadata, author order, affiliations, corresponding-author fields, ORCID fields, and double-blind review decision. | `title_author_metadata_AUTHOR_CONFIRMATION_REQUIRED.md` provides the required author-confirmation template. | human action |
| Competing interests | Provide the Nature Portfolio competing-interest statement for all authors. Use the journal's standard no-competing-interest statement only if true. | No author-confirmed competing-interest statement is stored in the package. | human action |
| Ethics and biological materials | Confirm that this methods Article adds no new human-participant, animal, or private wet-lab experiments, and that public source datasets remain governed by their source records. | Current package uses public-derived data and software demonstrations; no private new wet-lab data are claimed. | human action |
| AI-assisted content disclosure | Confirm whether any AI-assisted writing, analysis, or content-generation declaration is required and provide final journal-compliant wording if applicable. | `ai_disclosure_AUTHOR_CONFIRMATION_REQUIRED.md` provides author-confirmation draft options. This package does not insert an AI declaration automatically. | human action |
| Corresponding-author and ORCID fields | Complete corresponding-author, ORCID, affiliation, and portal-only metadata in the submission system. | Package keeps scientific surfaces separate from portal-only metadata. | human action |

Policy rationale. Nature Portfolio requires a competing-interest declaration for submitted manuscripts, and Springer Nature policy requires transparent AI-use declaration where applicable. These are author attestations and should be completed in the journal submission workflow rather than inferred from repository files.
"""


def _title_author_metadata_author_confirmation() -> str:
    return """# Title and author metadata AUTHOR CONFIRMATION REQUIRED

This file provides the author-controlled title-page and portal metadata template for the Nature Methods upload. It does not invent author names, author order, affiliations, ORCID records, contribution roles, or correspondence details.

## Manuscript title

Current package title. RhoDyn infers residence states in live-cell perturbation data

Author confirmation required. Confirm the final title before upload and ensure it matches the manuscript file, cover letter, portal metadata, and any figure or supplementary file labels.

## Author list

Complete the final author list in journal order.

| Order | Author name | Primary affiliation | Current address if different | ORCID | Equal contribution or group note |
| --- | --- | --- | --- | --- | --- |
| 1 | [author name] | [institution, department, city, country] | [if applicable] | [ORCID if used] | [if applicable] |
| 2 | [author name] | [institution, department, city, country] | [if applicable] | [ORCID if used] | [if applicable] |

Add or remove rows as needed after author approval.

## Correspondence and materials

| Field | Author-confirmed value |
| --- | --- |
| Corresponding author name | [name] |
| Corresponding author email | [email] |
| Corresponding author postal address | [address if required by portal] |
| Materials request contact | [name/email or same as corresponding author] |

## Double-blind review decision

Select one option before upload.

- Standard review. Keep author names and affiliations in the manuscript file and portal metadata.
- Double-blind review. Remove author-identifying information from the manuscript file and provide author affiliations and contact information in the cover letter, following the journal's double-blind instructions.

## Author approval statement for upload

Use only after all authors have confirmed the final package.

All authors have approved the submitted manuscript, agree with the author list and order, and agree with submission to Nature Methods.

## Upload decision

Before journal upload, transfer the completed author-confirmed fields into the manuscript file or portal fields required by the selected review mode. Do not infer these fields from repository history, commit metadata, emails, or previous manuscript drafts.
"""


def _reporting_summary_answer_bank_author_confirmation() -> str:
    return """# Reporting Summary answer bank AUTHOR CONFIRMATION REQUIRED

This file is a field-ready support surface for completing the official Springer Nature Reporting Summary. It is not the completed journal form. Authors must transfer only author-confirmed answers into the official PDF or portal form and must check the final form before submission.

## Source of the requested fields

Nature Portfolio asks authors to complete a reporting summary where relevant, including statistics, software and code, data availability, study design, sample size, data exclusions, replication, randomization, blinding, and relevant materials or methods categories. The official form also states that fields should not be completed with "not applicable" or "n/a". Use a specific explanation when a field does not apply to this methods Article.

## Journal metadata fields

| Reporting Summary field | Draft answer or action | Author confirmation |
| --- | --- | --- |
| Corresponding author(s) | Complete with the final corresponding author name(s) after author approval. | required |
| Last updated by author(s) | Complete with the author who finalizes the official form and the final date. | required |
| Manuscript title | RhoDyn infers residence states in live-cell perturbation data. Confirm final title against the manuscript and portal metadata. | required |

## Statistics

| Reporting Summary field | Draft answer or evidence source | Author confirmation |
| --- | --- | --- |
| Exact sample size for each group or condition | Sample sizes for benchmark and case-study analyses are reported in `source_data_and_statistics_inventory.csv`, the Online Methods, and figure legends where applicable. Confirm the final values against the generated figure legends and tables before upload. | required |
| Distinct samples or repeated measurements | The manuscript distinguishes trajectory-level repeated time measurements from endpoint tables, synthetic benchmark rows, and public-derived examples. Confirm that the final form states the relevant unit for each analysis. | required |
| Statistical tests and sidedness | The Online Methods describe residence scoring, amplitude comparators, bounded-coupling decisions, reserve-like endpoint summaries, uncertainty intervals, and reduced-architecture comparisons. Confirm all tests and sidedness are reflected in the form. | required |
| Covariates tested | No hidden covariate model is introduced by the submission package. Any covariates or grouping variables used for a specific case study should be copied from the Online Methods and source-data/statistics inventory. | required |
| Assumptions and multiple-comparison corrections | The manuscript describes margin choices, uncertainty handling, and interpretation boundaries for bounded-coupling and model-comparison examples. Confirm any correction procedures or assumptions in the official form. | required |
| Statistical parameters and uncertainty | Effects, intervals, and decision thresholds are reported in figure legends, Online Methods, and the statistics inventory. Confirm that confidence intervals, posterior summaries, and decision thresholds match the final package. | required |
| Bayesian analyses | Bayesian or posterior-mass language should be included only where used by a specific analysis surface. Confirm priors and computation details from the Methods before completing this field. | required |
| Hierarchical or complex designs | The method distinguishes time-series, endpoint, public-derived, and synthetic-truth examples. Confirm that any grouped or repeated structure is stated at the analysis unit used by the manuscript. | required |

## Software and code

| Reporting Summary field | Draft answer or evidence source | Author confirmation |
| --- | --- | --- |
| Data collection | This methods Article does not introduce new wet-lab data collection software. Public-derived and synthetic examples are analyzed from tabular inputs described in the manuscript and support files. Confirm if any author-supplied reference-case data collection software is disclosed separately. | required |
| Data analysis | RhoDyn v0.1.0 is the analysis software. Public source code is available at https://github.com/renatosocodato/rhodyn and the citable software archive is https://doi.org/10.5281/zenodo.21036616. PanelForge v3.14.1 is used for figure rendering and is archived at https://doi.org/10.5281/zenodo.20811171. | required |
| Custom algorithms or central software | RhoDyn is the central method and is available to editors and reviewers through the public repository, Zenodo release, documented command index, tests, and example inputs. | required |

## Data

| Reporting Summary field | Draft answer or evidence source | Author confirmation |
| --- | --- | --- |
| Public datasets and accession identifiers | Public-derived input records and software/example data are identified in the Data availability section, code-for-review surface, source-data/statistics inventory, and reference list. Confirm that all final URLs and DOIs resolve before upload. | required |
| Restrictions on data availability | The main software package is public. Any optional RhoA/microglia reference case that is not publicly redistributable should remain scoped as reviewer-access or controlled-access material and should not be represented as a public dataset unless authors provide the appropriate repository record. | required |
| Minimum dataset for replication | The minimum dataset for the public RhoDyn method examples is the released example data, synthetic benchmark outputs, documented command index, and citable software archive. Confirm whether any optional reference-case data are included in the journal upload package. | required |

## Life-science study design

| Reporting Summary field | Draft answer or evidence source | Author confirmation |
| --- | --- | --- |
| Sample size | Sample sizes are inherited from public examples, synthetic benchmark designs, and any optional reference-use case. No repository-derived author decision should be used to justify sample size beyond the evidence described in the manuscript. | required |
| Data exclusions | Use the Methods and source-data/statistics inventory to state any declared filtering, quality-control, schema validation, or exclusion rule. If no exclusions apply to a given example, state that no data were excluded for that analysis. | required |
| Replication | The public method examples are reproducible through CLI workflows, tests, generated benchmark reports, and public release archives. Confirm whether biological replication applies to any optional reference-use case. | required |
| Randomization | Synthetic generators use seeded construction where stated. Public-derived examples are not randomized experiments performed by this manuscript package. State the applicable design rather than using a generic response. | required |
| Blinding | The software demonstrations and public-derived analyses are computational examples rather than blinded wet-lab experiments. If any optional reference case involved blinding, report it from the source study or author-confirmed records. | required |

## Materials and experimental systems

| Reporting Summary field | Draft answer or evidence source | Author confirmation |
| --- | --- | --- |
| Antibodies | Not relevant to the public RhoDyn methods package unless an optional reference-use case reports antibody data. | required |
| Eukaryotic cell lines | Not newly generated or experimentally manipulated by the RhoDyn methods package. If the optional RhoA/microglia reference case is included, report cell-line details from the source record only. | required |
| Animals and other organisms | No new animal or organism experiments are performed by the RhoDyn methods package. Any optional reference-case animal or organism information must come from the source study or author-confirmed records. | required |
| Human participants or clinical data | The public RhoDyn package does not introduce new human-participant or clinical datasets. Any third-party human-derived data used as a public example should be described through its source record and access terms. | required |
| Dual-use research of concern | The package implements computational analysis of live-cell perturbation data and does not create agents, protocols, or information intended for harmful misuse. Authors should confirm this before upload. | required |
| Plants, palaeontology, archaeology, field work | Not relevant to the current methods Article because these systems are not used. State the reason in the official form rather than using "n/a". | required |

## Method-specific categories

| Reporting Summary field | Draft answer or evidence source | Author confirmation |
| --- | --- | --- |
| ChIP-seq | Not used in this methods Article. | required |
| Flow cytometry | Not used in this methods Article. | required |
| MRI-based neuroimaging | Not used in this methods Article. | required |

## Final author checks

Before submission, verify that the official Reporting Summary matches the main manuscript, Supplementary Information, source-data/statistics inventory, code-for-review surface, and final author declarations. Do not use this answer bank to strengthen any manuscript claim. It is a transfer aid for reporting transparency only.
"""


def _ai_disclosure_author_confirmation() -> str:
    return """# AI disclosure AUTHOR CONFIRMATION REQUIRED

This file provides draft wording options for the Nature Methods upload. It does not assert final AI use, does not replace author review, and must not be copied into the manuscript or portal unless all authors confirm the exact tools, scope, and wording.

## Why this file exists

Springer Nature guidance states that Large Language Models do not satisfy authorship criteria and that use of an LLM should be documented in the Methods section or in a suitable alternative manuscript location when applicable. This package therefore separates the journal-facing disclosure decision from the scientific manuscript text.

## Option A. AI-assisted writing, editing, code, or figure-support tools were used

During preparation of this manuscript, the authors used [tool name, provider, and model or configuration if known] for [editing, formatting, proofreading, code assistance, figure preparation, or other exact use]. The authors reviewed and edited all outputs and take full responsibility for the content. The tools were not used to generate primary data, alter source datasets, perform undisclosed analyses, or make autonomous scientific interpretations unless explicitly stated and documented elsewhere in the manuscript.

Use this option only after replacing the bracketed text with author-confirmed details.

## Option B. No AI-assisted tools were used for manuscript preparation

The authors did not use generative AI or AI-assisted technologies to write, edit, analyze, or generate manuscript content.

Use this option only if it is true for all authors and all manuscript-production steps.

## Upload decision

Select one option, revise it to match the actual author-confirmed record, and place the final wording in the Methods section or journal-designated declaration field if required by the submission system. If the final statement differs from either option, preserve the same boundaries by naming the tool, naming the task, confirming author responsibility, and avoiding any unsupported claim that an AI tool generated data or made scientific interpretations.
"""


def _manifest_json(generated_utc: str, checks: list[dict[str, Any]], package_dir: Path) -> dict[str, Any]:
    package_files = [
        (SUBMISSION / path.name).relative_to(ROOT).as_posix()
        for path in sorted(package_dir.glob("*"))
        if path.is_file()
    ]
    return {
        "stage": "9.27",
        "title": "Submission package assembly",
        "generated_utc": generated_utc,
        "commit": _git_sha(),
        "source_package_root": "manuscript/nature_methods",
        "package_root": "manuscript/nature_methods/submission_package",
        "package_files": package_files,
        "checks": checks,
        "next_substage": "9.28",
        "not_started": [
            "manuscript/nature_methods/submission_package/pi_review_packet.md",
            "manuscript/nature_methods/stage9_completion_report.md",
        ],
    }


def _readiness_checklist(checks: list[dict[str, Any]]) -> str:
    check_map = {item["name"]: item["passed"] for item in checks}
    lines = [
        "# Submission readiness checklist",
        "",
        "This checklist prepares the Nature Methods Article package for collaborator review. It does not replace the final journal submission portal review.",
        "",
        "| Item | Status | Note |",
        "| --- | --- | --- |",
        f"| Main manuscript source | {'ready' if check_map.get('main_text_present') else 'blocked'} | `main_text_for_submission.md` assembles Abstract, unheaded Introduction text, Results, Discussion, Online Methods, availability text, references, and figure legends. |",
        f"| Supplementary Information source | {'ready' if check_map.get('supplement_present') else 'blocked'} | `supplementary_information_for_submission.md` assembles Supplementary Methods, supplementary figure legends, supplementary table captions, and a compact traceability note. |",
        f"| Main figures | {'ready' if check_map.get('figure_files_present') else 'blocked'} | Six main display items are present in PDF, PNG, and SVG. |",
        f"| Reporting Summary | {'registered' if check_map.get('reporting_summary_present') else 'blocked'} | The required Reporting Summary placeholder is present. The final Springer Nature form remains a human submission action. |",
        f"| Reporting Summary answer bank | {'registered' if check_map.get('reporting_summary_answer_bank_present') else 'blocked'} | `reporting_summary_answer_bank_AUTHOR_CONFIRMATION_REQUIRED.md` maps the current package evidence to official Reporting Summary fields for author-confirmed transfer into the journal form. |",
        f"| Author declarations | {'registered' if check_map.get('author_declarations_present') else 'blocked'} | `author_declarations_REQUIRED.md` records author-controlled declarations that must be completed before upload. |",
        f"| AI disclosure draft | {'registered' if check_map.get('ai_disclosure_draft_present') else 'blocked'} | `ai_disclosure_AUTHOR_CONFIRMATION_REQUIRED.md` provides draft wording options that require author confirmation before use. |",
        f"| Title and author metadata | {'registered' if check_map.get('title_author_metadata_present') else 'blocked'} | `title_author_metadata_AUTHOR_CONFIRMATION_REQUIRED.md` records the author-list, affiliation, correspondence, ORCID, and review-mode fields that must be author-confirmed. |",
        f"| Code for review | {'ready' if check_map.get('code_for_review_present') else 'blocked'} | `code_for_review.md` records release identity and reproducibility commands. |",
        f"| Editor-triage note | {'ready' if check_map.get('editor_triage_note_present') else 'blocked'} | `editor_triage_note_for_cover_letter.md` gives a cover-letter-ready Nature Methods fit argument. |",
        f"| Editorial pitch | {'ready' if check_map.get('editorial_pitch_present') else 'blocked'} | `editorial_pitch_for_submission.md` contains cover-letter and presubmission-inquiry drafts. |",
        f"| Cover-letter submission draft | {'registered' if check_map.get('cover_letter_draft_present') else 'blocked'} | `cover_letter_for_submission_AUTHOR_CONFIRMATION_REQUIRED.md` provides a final upload-facing draft that keeps Article fit, validation breadth, software reproducibility, and claim boundaries together for author confirmation. |",
        f"| Prior-art positioning matrix | {'ready' if check_map.get('prior_art_positioning_matrix_present') else 'blocked'} | `prior_art_positioning_matrix.md` distinguishes RhoDyn from related dynamic-state, trajectory, imaging, and software-method literature without adding new manuscript claims. |",
        f"| Validation breadth map | {'ready' if check_map.get('validation_breadth_map_present') else 'blocked'} | `validation_breadth_and_boundary_map.md` condenses the synthetic, public trajectory, endpoint, held-out, and software-reproducibility validation ladder while preserving claim boundaries. |",
        f"| Editor-objection response map | {'ready' if check_map.get('editor_objection_response_map_present') else 'blocked'} | `editor_objection_response_map.md` links likely desk-review objections to existing evidence and claim boundaries. |",
        f"| Two-minute editor triage simulation | {'ready' if check_map.get('editor_two_minute_triage_simulation_present') else 'blocked'} | `editor_two_minute_triage_simulation.md` checks whether the title, Abstract, cover letter, and figure spine communicate the method claim quickly. |",
        f"| Current Nature Methods policy preflight | {'ready' if check_map.get('current_policy_preflight_present') else 'blocked'} | `current_nature_methods_policy_preflight.md` maps the package to current Article, reporting, data/code, and software guidance. |",
        f"| Reviewer and editor fit planner | {'registered' if check_map.get('reviewer_editor_fit_planner_present') else 'blocked'} | `reviewer_editor_fit_planner_AUTHOR_CONFIRMATION_REQUIRED.md` helps authors choose reviewer expertise and exclusions without inventing names or shifting the package toward a single use case. |",
        f"| Software-reporting checklist | {'ready' if check_map.get('software_reporting_checklist_present') else 'blocked'} | `software_reporting_checklist.md` maps RhoDyn to Nature Methods software and algorithm reporting expectations. |",
        f"| Article-fit checklist | {'ready' if check_map.get('article_fit_checklist_present') else 'blocked'} | `article_fit_checklist.md` records content-type fit, word counts, display count, references, and section structure. |",
        f"| Reader-surface hygiene | {'ready' if check_map.get('reader_surface_hygiene_passed') else 'blocked'} | Main manuscript and Supplementary Information surfaces are free of internal IDs and build-language tokens. |",
        f"| Package safety scan | {'ready' if check_map.get('package_safety_scan_clear') else 'blocked'} | Package files were scanned for local machine paths and token-like strings. |",
        f"| Consistency audit | {'ready' if check_map.get('package_consistency_audit_passed') else 'blocked'} | Package-level consistency checks passed. |",
        "",
        "Human actions before journal upload. Complete the official Springer Nature Reporting Summary form using author-confirmed answers, author declarations, corresponding-author and portal metadata, journal-specific file naming checks, and final author approval of the assembled main text and Supplementary Information.",
    ]
    return "\n".join(lines) + "\n"


def _submission_manifest(generated_utc: str) -> str:
    rows = [
        ("Main manuscript", "main_text_for_submission.md", "Reader source for Article text, availability, references, and figure legends."),
        ("Supplementary Information", "supplementary_information_for_submission.md", "Reader source for Supplementary Methods, supplementary figure legends, and supplementary table captions."),
        ("References", "references_for_submission.bib", "BibTeX library matching the human-readable reference list."),
        ("Main figures", "figure_file_inventory.csv", "Inventory of six main figures rendered as PDF, PNG, and SVG."),
        ("Source data and statistics", "source_data_and_statistics_inventory.csv", "Review-support inventory for statistics and source-data bindings."),
        ("Reporting Summary", "reporting_summary_REQUIRED.md", "Required journal form placeholder pending human completion."),
        ("Reporting Summary answer bank", "reporting_summary_answer_bank_AUTHOR_CONFIRMATION_REQUIRED.md", "Author-confirmation answer bank mapping current evidence to official Reporting Summary fields."),
        ("Author declarations", "author_declarations_REQUIRED.md", "Required author declaration checklist pending human completion."),
        ("AI disclosure draft", "ai_disclosure_AUTHOR_CONFIRMATION_REQUIRED.md", "Author-confirmation wording options for any required AI-assisted content disclosure."),
        ("Title and author metadata", "title_author_metadata_AUTHOR_CONFIRMATION_REQUIRED.md", "Author-confirmation template for title-page, author-list, affiliation, correspondence, ORCID, and review-mode fields."),
        ("Code for review", "code_for_review.md", "Release identity and reproducibility-command surface."),
        ("Editor-triage note", "editor_triage_note_for_cover_letter.md", "Cover-letter-ready Nature Methods fit, validation, and claim-boundary note."),
        ("Editorial pitch", "editorial_pitch_for_submission.md", "Cover-letter and presubmission-inquiry drafts for Nature Methods editorial triage."),
        ("Cover-letter submission draft", "cover_letter_for_submission_AUTHOR_CONFIRMATION_REQUIRED.md", "Author-confirmation cover-letter draft foregrounding Article fit, validation breadth, software reproducibility, and scoped claims."),
        ("Prior-art positioning matrix", "prior_art_positioning_matrix.md", "Novelty-boundary comparison against related dynamic-state, trajectory, imaging, and software-method literature."),
        ("Validation breadth map", "validation_breadth_and_boundary_map.md", "Validation-ladder and boundary map across synthetic, public trajectory, endpoint, held-out, and software-reproducibility tests."),
        ("Editor-objection response map", "editor_objection_response_map.md", "Desk-review objection map linking likely objections to existing package evidence and wording boundaries."),
        ("Two-minute editor triage simulation", "editor_two_minute_triage_simulation.md", "First-pass editor-read simulation for title, Abstract, cover-letter opening, figure spine, and claim boundaries."),
        ("Current Nature Methods policy preflight", "current_nature_methods_policy_preflight.md", "Source-linked preflight against current Article, Reporting Summary, data/code availability, and software guidance."),
        ("Reviewer and editor fit planner", "reviewer_editor_fit_planner_AUTHOR_CONFIRMATION_REQUIRED.md", "Author-confirmation planner for reviewer expertise coverage, suggested-reviewer fields, exclusions, and editor-fit wording."),
        ("Software-reporting checklist", "software_reporting_checklist.md", "Nature Methods software and algorithm reporting cross-check."),
        ("Article-fit checklist", "article_fit_checklist.md", "Nature Methods Article content-type and format cross-check."),
        ("Readiness checklist", "submission_readiness_checklist.md", "Collaborator handoff checklist."),
        ("Consistency audit", "package_consistency_audit.md", "Package assembly checks."),
    ]
    lines = [
        "# Submission package manifest",
        "",
        f"Generated UTC. {generated_utc}",
        f"Git commit. {_git_sha()}",
        "",
        "| Component | File | Role |",
        "| --- | --- | --- |",
    ]
    for row in rows:
        lines.append(f"| {row[0]} | `{row[1]}` | {row[2]} |")
    lines.extend(
        [
            "",
            "Scope. This package assembles the current Nature Methods Article surfaces for collaborator review. It does not create the PI review packet, submit the manuscript, or close Stage 9.",
        ]
    )
    return "\n".join(lines) + "\n"


def _scan_patterns(paths: list[Path], patterns: list[re.Pattern[str]]) -> list[str]:
    hits: list[str] = []
    for path in paths:
        if not path.exists():
            continue
        body = path.read_text(encoding="utf-8", errors="ignore")
        for pattern in patterns:
            match = pattern.search(body)
            if match:
                hits.append(f"{path.relative_to(ROOT).as_posix()} matched {pattern.pattern}")
    return hits


def _audit(generated_utc: str, package_dir: Path) -> dict[str, Any]:
    missing_inputs = [path.relative_to(ROOT).as_posix() for path in REQUIRED_READER_INPUTS if not path.exists()]
    stage928_authorized = (GATES / "9.28.json").exists()
    closed_refresh = _closed_stage9_refresh_allowed()
    forbidden_downstream = [
        path
        for path in FORBIDDEN_DOWNSTREAM_PATHS
        if path.exists()
        and not (stage928_authorized and path == SUBMISSION / "pi_review_packet.md")
        and not closed_refresh
    ]
    missing_downstream = [path.relative_to(ROOT).as_posix() for path in forbidden_downstream]
    gate_926 = _read_json(GATE_926) if GATE_926.exists() else {}
    gate_925b = _read_json(GATE_925B) if GATE_925B.exists() else {}
    gate_921 = _read_json(GATE_921) if GATE_921.exists() else {}
    gate_923 = _read_json(GATE_923) if GATE_923.exists() else {}
    gate_96b = _read_json(GATE_96B) if GATE_96B.exists() else {}
    figure_rows = _figure_inventory()
    reader_paths = [
        package_dir / "main_text_for_submission.md",
        package_dir / "supplementary_information_for_submission.md",
    ]
    package_paths = [path for path in package_dir.glob("*") if path.is_file()]
    reader_hits = _scan_patterns(reader_paths, READER_FORBIDDEN_PATTERNS)
    package_hits = _scan_patterns(package_paths, PACKAGE_FORBIDDEN_PATTERNS)
    checks = [
        {
            "name": "stage_9_26_gate_passed",
            "passed": gate_926.get("pass") is True and gate_926.get("next_substage") == "9.27",
            "detail": "Stage 9.26 internal peer-review gate passes and points to package assembly",
        },
        {
            "name": "required_inputs_present",
            "passed": not missing_inputs,
            "detail": f"missing_inputs={missing_inputs}",
        },
        {
            "name": "main_text_present",
            "passed": (package_dir / "main_text_for_submission.md").exists(),
            "detail": "Main manuscript source assembled",
        },
        {
            "name": "supplement_present",
            "passed": (package_dir / "supplementary_information_for_submission.md").exists(),
            "detail": "Supplementary Information source assembled",
        },
        {
            "name": "reader_surface_hygiene_passed",
            "passed": gate_925b.get("pass") is True and not reader_hits,
            "detail": f"reader_hits={reader_hits}",
        },
        {
            "name": "cross_document_consistency_gate_passed",
            "passed": gate_921.get("pass") is True,
            "detail": "Stage 9.21 cross-document consistency gate remains passing",
        },
        {
            "name": "legend_gate_passed",
            "passed": gate_923.get("pass") is True,
            "detail": "Stage 9.23 figure legend and caption gate remains passing",
        },
        {
            "name": "figure_files_present",
            "passed": bool(figure_rows) and all(str(row["exists"]) == "true" for row in figure_rows) and len(figure_rows) == 18,
            "detail": f"figure_file_rows={len(figure_rows)}",
        },
        {
            "name": "panelforge_status_bound",
            "passed": gate_96b.get("pass") is True and len(gate_96b.get("rendered_figures", [])) == 6,
            "detail": "Stage 9.6b has six rendered main display items",
        },
        {
            "name": "reporting_summary_present",
            "passed": (package_dir / "reporting_summary_REQUIRED.md").exists(),
            "detail": "Reporting Summary requirement placeholder is present",
        },
        {
            "name": "reporting_summary_answer_bank_present",
            "passed": (package_dir / "reporting_summary_answer_bank_AUTHOR_CONFIRMATION_REQUIRED.md").exists()
            and "AUTHOR CONFIRMATION REQUIRED" in (package_dir / "reporting_summary_answer_bank_AUTHOR_CONFIRMATION_REQUIRED.md").read_text(encoding="utf-8")
            and "Statistics" in (package_dir / "reporting_summary_answer_bank_AUTHOR_CONFIRMATION_REQUIRED.md").read_text(encoding="utf-8")
            and "Software and code" in (package_dir / "reporting_summary_answer_bank_AUTHOR_CONFIRMATION_REQUIRED.md").read_text(encoding="utf-8")
            and "Life-science study design" in (package_dir / "reporting_summary_answer_bank_AUTHOR_CONFIRMATION_REQUIRED.md").read_text(encoding="utf-8")
            and "Materials and experimental systems" in (package_dir / "reporting_summary_answer_bank_AUTHOR_CONFIRMATION_REQUIRED.md").read_text(encoding="utf-8"),
            "detail": "Reporting Summary answer bank maps statistics, software, data, study design, and materials fields to author-confirmed package evidence",
        },
        {
            "name": "author_declarations_present",
            "passed": (package_dir / "author_declarations_REQUIRED.md").exists()
            and "Competing interests" in (package_dir / "author_declarations_REQUIRED.md").read_text(encoding="utf-8")
            and "AI-assisted content disclosure" in (package_dir / "author_declarations_REQUIRED.md").read_text(encoding="utf-8")
            and "human action" in (package_dir / "author_declarations_REQUIRED.md").read_text(encoding="utf-8"),
            "detail": "Author declarations checklist records competing-interest, contribution, funding, ethics/materials, AI-use, and portal-only human actions",
        },
        {
            "name": "ai_disclosure_draft_present",
            "passed": (package_dir / "ai_disclosure_AUTHOR_CONFIRMATION_REQUIRED.md").exists()
            and "AUTHOR CONFIRMATION REQUIRED" in (package_dir / "ai_disclosure_AUTHOR_CONFIRMATION_REQUIRED.md").read_text(encoding="utf-8")
            and "does not assert final AI use" in (package_dir / "ai_disclosure_AUTHOR_CONFIRMATION_REQUIRED.md").read_text(encoding="utf-8")
            and "Option A" in (package_dir / "ai_disclosure_AUTHOR_CONFIRMATION_REQUIRED.md").read_text(encoding="utf-8")
            and "Option B" in (package_dir / "ai_disclosure_AUTHOR_CONFIRMATION_REQUIRED.md").read_text(encoding="utf-8"),
            "detail": "AI disclosure draft provides author-confirmation wording options without inserting a manuscript declaration automatically",
        },
        {
            "name": "title_author_metadata_present",
            "passed": (package_dir / "title_author_metadata_AUTHOR_CONFIRMATION_REQUIRED.md").exists()
            and "AUTHOR CONFIRMATION REQUIRED" in (package_dir / "title_author_metadata_AUTHOR_CONFIRMATION_REQUIRED.md").read_text(encoding="utf-8")
            and "Author list" in (package_dir / "title_author_metadata_AUTHOR_CONFIRMATION_REQUIRED.md").read_text(encoding="utf-8")
            and "Correspondence and materials" in (package_dir / "title_author_metadata_AUTHOR_CONFIRMATION_REQUIRED.md").read_text(encoding="utf-8")
            and "Double-blind review decision" in (package_dir / "title_author_metadata_AUTHOR_CONFIRMATION_REQUIRED.md").read_text(encoding="utf-8"),
            "detail": "Title and author metadata template records author-controlled manuscript-file and portal fields without inventing author details",
        },
        {
            "name": "code_for_review_present",
            "passed": (package_dir / "code_for_review.md").exists() and "Reproducibility commands" in (package_dir / "code_for_review.md").read_text(encoding="utf-8"),
            "detail": "Code-for-review surface includes reproducibility commands",
        },
        {
            "name": "editor_triage_note_present",
            "passed": (package_dir / "editor_triage_note_for_cover_letter.md").exists()
            and "not the broad observation that cell signaling is dynamic" in (package_dir / "editor_triage_note_for_cover_letter.md").read_text(encoding="utf-8"),
            "detail": "Editor-triage note foregrounds Nature Methods fit and claim boundaries",
        },
        {
            "name": "editorial_pitch_present",
            "passed": (package_dir / "editorial_pitch_for_submission.md").exists()
            and "Cover-letter draft" in (package_dir / "editorial_pitch_for_submission.md").read_text(encoding="utf-8")
            and "Cover-letter upload checklist" in (package_dir / "editorial_pitch_for_submission.md").read_text(encoding="utf-8")
            and "not under consideration by another journal" in (package_dir / "editorial_pitch_for_submission.md").read_text(encoding="utf-8")
            and "Presubmission-inquiry draft" in (package_dir / "editorial_pitch_for_submission.md").read_text(encoding="utf-8"),
            "detail": "Editorial pitch includes cover-letter, author-confirmation, and presubmission-inquiry drafts",
        },
        {
            "name": "cover_letter_draft_present",
            "passed": (package_dir / "cover_letter_for_submission_AUTHOR_CONFIRMATION_REQUIRED.md").exists()
            and "AUTHOR CONFIRMATION REQUIRED" in (package_dir / "cover_letter_for_submission_AUTHOR_CONFIRMATION_REQUIRED.md").read_text(encoding="utf-8")
            and "Article-level computational method" in (package_dir / "cover_letter_for_submission_AUTHOR_CONFIRMATION_REQUIRED.md").read_text(encoding="utf-8")
            and "validation ladder is designed to avoid a single-case methods claim" in (package_dir / "cover_letter_for_submission_AUTHOR_CONFIRMATION_REQUIRED.md").read_text(encoding="utf-8")
            and "Residence windows are declared analysis choices" in (package_dir / "cover_letter_for_submission_AUTHOR_CONFIRMATION_REQUIRED.md").read_text(encoding="utf-8")
            and "RhoDyn v0.1.0 is publicly available" in (package_dir / "cover_letter_for_submission_AUTHOR_CONFIRMATION_REQUIRED.md").read_text(encoding="utf-8")
            and "authors must confirm related-manuscript status" in (package_dir / "cover_letter_for_submission_AUTHOR_CONFIRMATION_REQUIRED.md").read_text(encoding="utf-8"),
            "detail": "Cover-letter submission draft keeps Article fit, validation breadth, software reproducibility, and claim boundaries together for author confirmation",
        },
        {
            "name": "prior_art_positioning_matrix_present",
            "passed": (package_dir / "prior_art_positioning_matrix.md").exists()
            and "Prior-art positioning matrix" in (package_dir / "prior_art_positioning_matrix.md").read_text(encoding="utf-8")
            and "dynamic-state, trajectory, imaging, and software-method literature" in (package_dir / "prior_art_positioning_matrix.md").read_text(encoding="utf-8")
            and "should not be positioned as the first method to treat live-cell signals as dynamic" in (package_dir / "prior_art_positioning_matrix.md").read_text(encoding="utf-8")
            and "does not add citations, performance results, biological datasets, or manuscript claims" in (package_dir / "prior_art_positioning_matrix.md").read_text(encoding="utf-8"),
            "detail": "Prior-art positioning matrix preserves novelty calibration against related methods without adding new evidence",
        },
        {
            "name": "validation_breadth_map_present",
            "passed": (package_dir / "validation_breadth_and_boundary_map.md").exists()
            and "Validation breadth and boundary map" in (package_dir / "validation_breadth_and_boundary_map.md").read_text(encoding="utf-8")
            and "does not add data, analyses, citations, figures, datasets, performance claims, or manuscript text" in (package_dir / "validation_breadth_and_boundary_map.md").read_text(encoding="utf-8")
            and "Known-truth synthetic regimes" in (package_dir / "validation_breadth_and_boundary_map.md").read_text(encoding="utf-8")
            and "Public live-cell trajectory examples" in (package_dir / "validation_breadth_and_boundary_map.md").read_text(encoding="utf-8")
            and "Public-derived endpoint and paired-reporter demonstrations" in (package_dir / "validation_breadth_and_boundary_map.md").read_text(encoding="utf-8")
            and "Held-out contexts and margin sensitivity" in (package_dir / "validation_breadth_and_boundary_map.md").read_text(encoding="utf-8")
            and "Software and reproducibility parity" in (package_dir / "validation_breadth_and_boundary_map.md").read_text(encoding="utf-8")
            and "It does not claim that every biological system contains a residence regime" in (package_dir / "validation_breadth_and_boundary_map.md").read_text(encoding="utf-8"),
            "detail": "Validation breadth map makes the method-validation ladder visible while preserving non-universality boundaries",
        },
        {
            "name": "editor_objection_response_map_present",
            "passed": (package_dir / "editor_objection_response_map.md").exists()
            and "Editor-objection response map" in (package_dir / "editor_objection_response_map.md").read_text(encoding="utf-8")
            and "does not add evidence, citations, figures, datasets, performance claims, or manuscript text" in (package_dir / "editor_objection_response_map.md").read_text(encoding="utf-8")
            and "likely Nature Methods desk-review objections" in (package_dir / "editor_objection_response_map.md").read_text(encoding="utf-8")
            and "If answering an objection would require new data, new benchmarking, or a stronger biological claim" in (package_dir / "editor_objection_response_map.md").read_text(encoding="utf-8"),
            "detail": "Editor-objection response map links likely desk-review objections to existing evidence and claim boundaries",
        },
        {
            "name": "editor_two_minute_triage_simulation_present",
            "passed": (package_dir / "editor_two_minute_triage_simulation.md").exists()
            and "Two-minute editor triage simulation" in (package_dir / "editor_two_minute_triage_simulation.md").read_text(encoding="utf-8")
            and "does not add evidence, citations, analyses, figures, datasets, performance claims, or manuscript text" in (package_dir / "editor_two_minute_triage_simulation.md").read_text(encoding="utf-8")
            and "What an editor can see quickly" in (package_dir / "editor_two_minute_triage_simulation.md").read_text(encoding="utf-8")
            and "The current package should be readable as a Nature Methods computational-methods Article" in (package_dir / "editor_two_minute_triage_simulation.md").read_text(encoding="utf-8")
            and "If an editor can answer these three questions in the first two minutes" in (package_dir / "editor_two_minute_triage_simulation.md").read_text(encoding="utf-8"),
            "detail": "Two-minute editor triage simulation checks first-pass method fit, validation breadth, and claim boundaries",
        },
        {
            "name": "current_policy_preflight_present",
            "passed": (package_dir / "current_nature_methods_policy_preflight.md").exists()
            and "Current Nature Methods policy preflight" in (package_dir / "current_nature_methods_policy_preflight.md").read_text(encoding="utf-8")
            and "does not add evidence, citations, analyses, figures, datasets, performance claims, or manuscript text" in (package_dir / "current_nature_methods_policy_preflight.md").read_text(encoding="utf-8")
            and "Article is a report describing a novel method or tool" in (package_dir / "current_nature_methods_policy_preflight.md").read_text(encoding="utf-8")
            and "Abstract up to 150 words" in (package_dir / "current_nature_methods_policy_preflight.md").read_text(encoding="utf-8")
            and "Code and algorithm availability" in (package_dir / "current_nature_methods_policy_preflight.md").read_text(encoding="utf-8")
            and "Reporting Summary remains a human submission action" in (package_dir / "current_nature_methods_policy_preflight.md").read_text(encoding="utf-8"),
            "detail": "Current Nature Methods policy preflight maps Article, reporting, data/code, and software requirements to package evidence",
        },
        {
            "name": "reviewer_editor_fit_planner_present",
            "passed": (package_dir / "reviewer_editor_fit_planner_AUTHOR_CONFIRMATION_REQUIRED.md").exists()
            and "Reviewer and editor fit planner" in (package_dir / "reviewer_editor_fit_planner_AUTHOR_CONFIRMATION_REQUIRED.md").read_text(encoding="utf-8")
            and "does not nominate reviewers, infer conflicts, or add manuscript evidence" in (package_dir / "reviewer_editor_fit_planner_AUTHOR_CONFIRMATION_REQUIRED.md").read_text(encoding="utf-8")
            and "Expertise coverage needed" in (package_dir / "reviewer_editor_fit_planner_AUTHOR_CONFIRMATION_REQUIRED.md").read_text(encoding="utf-8")
            and "Suggested reviewer template" in (package_dir / "reviewer_editor_fit_planner_AUTHOR_CONFIRMATION_REQUIRED.md").read_text(encoding="utf-8")
            and "Exclusion template" in (package_dir / "reviewer_editor_fit_planner_AUTHOR_CONFIRMATION_REQUIRED.md").read_text(encoding="utf-8")
            and "The RhoA/microglia reference use case should not dominate reviewer assignment" in (package_dir / "reviewer_editor_fit_planner_AUTHOR_CONFIRMATION_REQUIRED.md").read_text(encoding="utf-8"),
            "detail": "Reviewer/editor planner keeps reviewer suggestions and exclusions author-confirmed while preserving method-first reviewer coverage",
        },
        {
            "name": "software_reporting_checklist_present",
            "passed": (package_dir / "software_reporting_checklist.md").exists()
            and "Nature Methods software-reporting checklist" in (package_dir / "software_reporting_checklist.md").read_text(encoding="utf-8")
            and "Source code supplied for review" in (package_dir / "software_reporting_checklist.md").read_text(encoding="utf-8")
            and "Sample data supplied" in (package_dir / "software_reporting_checklist.md").read_text(encoding="utf-8"),
            "detail": "Software-reporting checklist maps source code, algorithm description, documentation, sample data, expected outputs, license, and versioning",
        },
        {
            "name": "article_fit_checklist_present",
            "passed": (package_dir / "article_fit_checklist.md").exists()
            and "Nature Methods Article-fit checklist" in (package_dir / "article_fit_checklist.md").read_text(encoding="utf-8")
            and "Content-type decision" in (package_dir / "article_fit_checklist.md").read_text(encoding="utf-8")
            and "Main display items" in (package_dir / "article_fit_checklist.md").read_text(encoding="utf-8"),
            "detail": "Article-fit checklist records content-type fit, word counts, display count, references, and section structure",
        },
        {
            "name": "package_safety_scan_clear",
            "passed": not package_hits,
            "detail": f"package_hits={package_hits}",
        },
        {
            "name": "no_downstream_pi_or_closure_started",
            "passed": not missing_downstream,
            "detail": (
                "Closed Stage 9.29 package refresh allowed existing downstream surfaces"
                if closed_refresh and not missing_downstream
                else f"downstream_paths={missing_downstream}"
            ),
        },
    ]
    checks.append(
        {
            "name": "package_consistency_audit_passed",
            "passed": all(item["passed"] for item in checks),
            "detail": "All package prerequisites, reader-surface, figure, reporting, code, and safety checks pass",
        }
    )
    return {
        "generated_utc": generated_utc,
        "checks": checks,
        "missing_inputs": missing_inputs,
        "reader_hits": reader_hits,
        "package_hits": package_hits,
        "downstream_paths": missing_downstream,
        "figure_rows": figure_rows,
        "source_rows": _source_inventory(),
    }


def _package_audit_md(audit: dict[str, Any]) -> str:
    lines = [
        "# Package consistency audit",
        "",
        f"Generated UTC. {audit['generated_utc']}",
        "",
        "## Result",
        "",
        f"Status. {'pass' if all(item['passed'] for item in audit['checks']) else 'fail'}",
        "",
        "## Checks",
        "",
        "| Check | Pass | Detail |",
        "| --- | --- | --- |",
    ]
    for item in audit["checks"]:
        lines.append(f"| {item['name']} | {str(item['passed']).lower()} | {item['detail']} |")
    lines.extend(
        [
            "",
            "## Figure assembly status",
            "",
            f"Six main display items are represented by {len(audit['figure_rows'])} rendered figure files across PDF, PNG, and SVG formats.",
            "",
            "## Interpretation boundary",
            "",
            "The package is a collaborator-review assembly of the current manuscript and supporting surfaces. It does not constitute final journal upload approval, final Reporting Summary completion, or external peer-review acceptance.",
        ]
    )
    return "\n".join(lines) + "\n"


def _gate_payload(audit: dict[str, Any]) -> dict[str, Any]:
    return {
        "substage": "9.27",
        "title": "Submission package assembly",
        "status": "pass" if all(item["passed"] for item in audit["checks"]) else "fail",
        "pass": all(item["passed"] for item in audit["checks"]),
        "generated_utc": audit["generated_utc"],
        "commit": _git_sha(),
        "next_substage": "9.28",
        "checks": audit["checks"],
        "package_files": [
            path.relative_to(ROOT).as_posix()
            for key, path in OUTPUTS.items()
            if key != "gate" and path.parent == SUBMISSION
        ],
        "reader_surface_files": [
            "manuscript/nature_methods/submission_package/main_text_for_submission.md",
            "manuscript/nature_methods/submission_package/supplementary_information_for_submission.md",
        ],
        "figure_file_count": len(audit["figure_rows"]),
        "source_inventory_rows": len(audit["source_rows"]),
        "reporting_summary_status": "placeholder_present_final_form_human_action",
        "scope_boundary": "Submission package assembly only. No PI review packet, final journal upload, new analysis, new figure, new biological claim, or Stage 9 closure is created.",
    }


def _stage_outputs(generated_utc: str) -> tuple[dict[str, Any], dict[str, Any]]:
    if STAGING.exists():
        shutil.rmtree(STAGING)
    STAGING.mkdir(parents=True, exist_ok=True)
    staging_submission = STAGING / SUBMISSION.relative_to(WORKSPACE)
    staging_gates = STAGING / GATES.relative_to(WORKSPACE)
    staging_submission.mkdir(parents=True, exist_ok=True)
    staging_gates.mkdir(parents=True, exist_ok=True)

    main_text = _assemble_main_text()
    _write_text(staging_submission / "main_text_for_submission.md", main_text)
    _write_text(staging_submission / "supplementary_information_for_submission.md", _assemble_supplement())
    _write_text(staging_submission / "code_for_review.md", _code_for_review())
    _write_text(staging_submission / "editor_triage_note_for_cover_letter.md", _editor_triage_note())
    _write_text(staging_submission / "editorial_pitch_for_submission.md", _editorial_pitch())
    _write_text(staging_submission / "cover_letter_for_submission_AUTHOR_CONFIRMATION_REQUIRED.md", _cover_letter_for_submission())
    _write_text(staging_submission / "prior_art_positioning_matrix.md", _prior_art_positioning_matrix())
    _write_text(staging_submission / "validation_breadth_and_boundary_map.md", _validation_breadth_map())
    _write_text(staging_submission / "editor_objection_response_map.md", _editor_objection_response_map())
    _write_text(staging_submission / "editor_two_minute_triage_simulation.md", _editor_two_minute_triage_simulation())
    _write_text(staging_submission / "current_nature_methods_policy_preflight.md", _current_policy_preflight())
    _write_text(staging_submission / "reviewer_editor_fit_planner_AUTHOR_CONFIRMATION_REQUIRED.md", _reviewer_editor_fit_planner())
    _write_text(staging_submission / "software_reporting_checklist.md", _software_reporting_checklist())
    _write_text(staging_submission / "article_fit_checklist.md", _article_fit_checklist(main_text))
    _write_text(staging_submission / "author_declarations_REQUIRED.md", _author_declarations_checklist())
    _write_text(staging_submission / "ai_disclosure_AUTHOR_CONFIRMATION_REQUIRED.md", _ai_disclosure_author_confirmation())
    _write_text(staging_submission / "title_author_metadata_AUTHOR_CONFIRMATION_REQUIRED.md", _title_author_metadata_author_confirmation())
    _write_text(staging_submission / "reporting_summary_answer_bank_AUTHOR_CONFIRMATION_REQUIRED.md", _reporting_summary_answer_bank_author_confirmation())
    _write_text(staging_submission / "references_for_submission.bib", _submission_bib())
    _write_csv(
        staging_submission / "figure_file_inventory.csv",
        _figure_inventory(),
        ["fig_id", "format", "path", "exists", "size_bytes", "sha256", "engine_version", "engine_commit", "placement"],
    )
    _write_csv(
        staging_submission / "source_data_and_statistics_inventory.csv",
        _source_inventory(),
        ["record_type", "record_id", "display_or_table", "source_or_command", "summary", "boundary"],
    )
    shutil.copy2(SUBMISSION / "reporting_summary_REQUIRED.md", staging_submission / "reporting_summary_REQUIRED.md")
    audit = _audit(generated_utc, staging_submission)
    _write_text(staging_submission / "package_consistency_audit.md", _package_audit_md(audit))
    _write_text(staging_submission / "submission_readiness_checklist.md", _readiness_checklist(audit["checks"]))
    _write_text(staging_submission / "submission_manifest.md", _submission_manifest(generated_utc))
    package_json = _manifest_json(generated_utc, audit["checks"], staging_submission)
    _write_json(staging_submission / "submission_package_manifest.json", package_json)
    gate = _gate_payload(audit)
    _write_json(staging_gates / "9.27.json", gate)
    return audit, gate


def _promote_from_staging() -> None:
    for name, target in OUTPUTS.items():
        source = STAGING / target.relative_to(WORKSPACE)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)


def _quarantine_staging() -> str:
    if QUARANTINE.exists():
        shutil.rmtree(QUARANTINE)
    QUARANTINE.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(STAGING), str(QUARANTINE))
    return QUARANTINE.relative_to(ROOT).as_posix()


def _update_registry() -> None:
    registry = _read_json(REGISTRY_PATH)
    registry["next_substage"] = "9.28"
    registry["updated_utc"] = _now()
    for item in registry.get("substages", []):
        if item.get("id") == "9.27":
            item["status"] = "complete_submission_package_assembled"
    _write_json(REGISTRY_PATH, registry)


def _upsert_completed_substage(memory: dict[str, Any], checks: list[dict[str, Any]]) -> None:
    record = {
        "substage": "9.27",
        "status": "pass",
        "pass": True,
        "gate_verdict_path": "manuscript/nature_methods/gate_verdicts/9.27.json",
        "validation_outcome": "Submission package assembled with reader-clean main text, Supplementary Information, figure inventory, source-data/statistics inventory, code-for-review, cover-letter submission draft, prior-art positioning, validation breadth map, editor-objection response map, two-minute editor triage simulation, current Nature Methods policy preflight, reviewer/editor fit planner, Reporting Summary placeholder and answer bank, and readiness checklist",
        "evidence_dependencies": [
            "manuscript/nature_methods/gate_verdicts/9.26.json",
            "manuscript/nature_methods/audits/internal_peer_review_simulation.md",
            "manuscript/nature_methods/audits/reader_surface_hygiene_report.md",
            "manuscript/nature_methods/gate_verdicts/9.21.json",
            "manuscript/nature_methods/gate_verdicts/9.23.json",
        ],
        "files_created_or_modified": [path.relative_to(ROOT).as_posix() for path in OUTPUTS.values()],
        "remaining_blockers": [
            "Final Springer Nature Reporting Summary form remains a human submission action, with the answer bank available for author-confirmed transfer",
            "PI review packet has not started",
            "Stage 9 closure has not started",
        ],
        "checks": checks,
    }
    entries = [
        item
        for item in memory.get("completed_substages", [])
        if not (isinstance(item, dict) and item.get("substage") == "9.27") and item != "9.27"
    ]
    entries.append(record)
    memory["completed_substages"] = entries


def _update_stage9_memory(generated_utc: str, checks: list[dict[str, Any]]) -> None:
    memory = _read_json(MEMORY_PATH)
    memory["generated_utc"] = generated_utc
    memory["current_substage"] = "9.27"
    memory["submission_package_started"] = True
    memory["status"] = "stage9_27_submission_package_assembled"
    memory["current_gate"] = "Stage 9.27 assembled the collaborator-review submission package"
    memory["next_substage"] = "9.28"
    memory["next_substage_authorized"] = False
    memory["stage9_active_gate"] = "Stage 9.27 Submission package assembly complete; final PI review not started"
    memory["stage9_27_checks"] = checks
    artifacts = memory.setdefault("artifacts", [])
    for artifact in [path.relative_to(ROOT).as_posix() for path in OUTPUTS.values()]:
        if artifact not in artifacts:
            artifacts.append(artifact)
    memory["gate"] = [
        "Stage 9.-1 contract and schema files exist and pass the scaffold checker.",
        "Stage 9.0 through Stage 9.27 are complete through submission package assembly.",
        "Stage 9.28 and Stage 9.29 remain not started.",
        "No PI review packet or Stage 9 completion report is created in this pass.",
        "The package contains reader-clean main text, Supplementary Information, code-for-review, cover-letter submission draft, prior-art positioning matrix, validation breadth map, editor-objection response map, two-minute editor triage simulation, current Nature Methods policy preflight, reviewer/editor fit planner, figure inventory, source-data/statistics inventory, Reporting Summary placeholder and answer bank, author declarations checklist, and readiness checklist.",
    ]
    memory["scope_rule"] = (
        "Stage 9 has completed evidence intake, guidance, corpus, narrative spine, claim freeze, paragraph and figure planning, "
        "PanelForge rendering, supplementary planning, drafting, availability, references, consistency, statistics, legends, polish, "
        "reader-surface hygiene, internal peer review, and submission package assembly. Do not start the PI review packet or Stage 9 closure without explicit substage authorization."
    )
    _upsert_completed_substage(memory, checks)
    _write_json(MEMORY_PATH, memory)


def _update_roadmap_memory() -> None:
    memory = _read_json(ROADMAP_MEMORY_PATH)
    current = memory.setdefault("current_position", {})
    current["active_stage"] = "Stage 9.27 Submission package assembly complete; final PI review not started"
    current["stage9_active_gate"] = "Stage 9.27 Submission package assembly complete; final PI review not started"
    current["after_stage9_27_submission_package_assembly"] = (
        "Stage 9.27 assembled the collaborator-review Nature Methods package from the reader-clean main text, Supplementary Information, figures, "
        "references, code-for-review surface, cover-letter submission draft, prior-art positioning matrix, validation breadth map, editor-objection response map, two-minute editor triage simulation, current Nature Methods policy preflight, reviewer/editor fit planner, source-data/statistics inventory, Reporting Summary placeholder and answer bank, author declarations checklist, and readiness checklist."
    )
    current["current_gate"] = "Submission package assembled for collaborator review"
    current["next_stage"] = "Stage 9.28 Final human PI review packet"
    for stage in memory.get("stage_lock", []):
        if not isinstance(stage, dict) or stage.get("stage") != 9:
            continue
        stage["status"] = "stage9_27_submission_package_assembled"
        stage["current_gate"] = "Stage 9.27 assembled the collaborator-review submission package"
        stage["scope_rule"] = (
            "Stage 9 has completed through submission package assembly. Final human PI review and Stage 9 closure remain not started."
        )
        artifacts = stage.setdefault("artifacts", [])
        for artifact in [path.relative_to(ROOT).as_posix() for path in OUTPUTS.values()] + [
            "scripts/run_stage9_27_submission_package_assembly.py"
        ]:
            if artifact not in artifacts:
                artifacts.append(artifact)
        gate = stage.setdefault("gate", [])
        review_gate = "Stage 9.27 assembled the collaborator-review package with reader-clean manuscript surfaces and package-level consistency checks."
        if review_gate not in gate:
            gate.append(review_gate)
        for subphase in stage.get("subphases", []):
            if isinstance(subphase, dict) and subphase.get("id") == "9.27":
                subphase["status"] = "complete_submission_package_assembled"
                subphase["evidence"] = "manuscript/nature_methods/gate_verdicts/9.27.json"
    _write_json(ROADMAP_MEMORY_PATH, memory)


def _replace(body: str, old: str, new: str) -> str:
    return body.replace(old, new) if old in body else body


def _update_docs() -> None:
    README_PATH.write_text(
        """# Nature Methods manuscript workspace

This directory is the Stage 9 manuscript-assembly workspace for RhoDyn.

Current status. Stage 9.27 submission package assembly complete.

The workspace now contains the authorized manuscript components through collaborator-review package assembly. Evidence intake, venue guidance, methods-paper corpus analysis, narrative spine, claim freeze, paragraph planning, figure planning, deterministic main-figure rendering, supplementary display planning, section contracts, front matter, Results, Introduction, Discussion, Methods, availability statements, Supplementary Methods, supplementary table/source-data binding, reference audit, cross-document consistency audit, statistical-language audit, figure legend/caption audit, editorial polish passes I and II, reader-surface hygiene, internal peer review, and submission package assembly are present.

The next unstarted step is Stage 9.28 final human PI review packet. The package currently includes `submission_package/main_text_for_submission.md`, `submission_package/supplementary_information_for_submission.md`, `submission_package/code_for_review.md`, `submission_package/editor_triage_note_for_cover_letter.md`, `submission_package/editorial_pitch_for_submission.md`, `submission_package/cover_letter_for_submission_AUTHOR_CONFIRMATION_REQUIRED.md`, `submission_package/prior_art_positioning_matrix.md`, `submission_package/validation_breadth_and_boundary_map.md`, `submission_package/editor_objection_response_map.md`, `submission_package/editor_two_minute_triage_simulation.md`, `submission_package/current_nature_methods_policy_preflight.md`, `submission_package/reviewer_editor_fit_planner_AUTHOR_CONFIRMATION_REQUIRED.md`, `submission_package/software_reporting_checklist.md`, `submission_package/article_fit_checklist.md`, `submission_package/author_declarations_REQUIRED.md`, `submission_package/ai_disclosure_AUTHOR_CONFIRMATION_REQUIRED.md`, `submission_package/title_author_metadata_AUTHOR_CONFIRMATION_REQUIRED.md`, `submission_package/reporting_summary_REQUIRED.md`, `submission_package/reporting_summary_answer_bank_AUTHOR_CONFIRMATION_REQUIRED.md`, `submission_package/figure_file_inventory.csv`, `submission_package/source_data_and_statistics_inventory.csv`, `submission_package/submission_readiness_checklist.md`, `submission_package/package_consistency_audit.md`, and `submission_package/submission_package_manifest.json`.

The official Springer Nature Reporting Summary form remains a human submission action. The PI review packet and Stage 9 closure report have not started.

PanelForge figure rendering has already been exercised through the authorized Stage 9.6b deterministic rendering lane. The placeholder under `tools/panelforge-figures/` is not a clone, `.venv-panelforge` is not created by this workspace, and no local figure-engine repository is vendored here.
""",
        encoding="utf-8",
    )
    if PLAN_PATH.exists():
        body = PLAN_PATH.read_text(encoding="utf-8")
        body = _replace(
            body,
            "through Stage 9.26. It does not begin submission package assembly, final PI review, or Stage 9 closure.",
            "through Stage 9.27. It has assembled the collaborator-review submission package. Final PI review and Stage 9 closure have not started.",
        )
        body = _replace(
            body,
            "Stage 9.26 registers `audits/internal_peer_review_simulation.md`, `audits/reviewer_action_matrix.csv`, and `gate_verdicts/9.26.json`, and stress-tests the reader-clean manuscript from eight reviewer perspectives. The current state intentionally does not create the full submission-package files.",
            "Stage 9.26 registers `audits/internal_peer_review_simulation.md`, `audits/reviewer_action_matrix.csv`, and `gate_verdicts/9.26.json`, and stress-tests the reader-clean manuscript from eight reviewer perspectives. Stage 9.27 registers the collaborator-review submission package, `submission_package/submission_readiness_checklist.md`, and `gate_verdicts/9.27.json`. The current state intentionally does not create the PI review packet or Stage 9 completion report.",
        )
        body = _replace(
            body,
            "| 9.27 | Submission package assembly | not_started | Assemble complete manuscript and submission package after hygiene gate. |",
            "| 9.27 | Submission package assembly | complete_submission_package_assembled | Assemble complete manuscript and submission package after hygiene gate. |",
        )
        PLAN_PATH.write_text(body, encoding="utf-8")
    if ROADMAP_PATH.exists():
        body = ROADMAP_PATH.read_text(encoding="utf-8")
        body = _replace(
            body,
            "Stage 9.25 has completed editorial polish pass II, Stage 9.25b has\ncompleted reader-surface hygiene, and Stage 9.26 has completed internal peer\nreview simulation. Final package assembly remains not started.",
            "Stage 9.25 has completed editorial polish pass II, Stage 9.25b has\ncompleted reader-surface hygiene, Stage 9.26 has completed internal peer review\nsimulation, and Stage 9.27 has completed collaborator-review package assembly.\nFinal PI review and Stage 9 closure remain not started.",
        )
        body = _replace(
            body,
            "| Stage 9. Nature Methods manuscript assembly | Stage 9.26 Internal peer review simulation complete, submission package assembly not started. | The current boundary is evidence intake, official venue-guidance registration, representative methods-paper corpus analysis, narrative-spine selection, claim freeze, paragraph-level claim planning, main figure-spine planning, deterministic PanelForge rendering, supplementary display planning, section-contract planning, front-matter strategy, Results architecture, Results drafting, Introduction literature binding, Discussion interpretation mapping, Discussion drafting, Methods architecture, Methods drafting, availability assembly, Supplementary Methods drafting, supplementary table/source-data binding, reference-library/citation audit, cross-document consistency audit, statistical-language audit, figure legend/caption audit, editorial polish passes I and II, reader-surface hygiene, and internal peer review simulation only. Do not start final submission packaging without explicit substage authorization. |",
            "| Stage 9. Nature Methods manuscript assembly | Stage 9.27 Submission package assembly complete, final PI review not started. | The current boundary is evidence intake, official venue-guidance registration, representative methods-paper corpus analysis, narrative-spine selection, claim freeze, paragraph-level claim planning, main figure-spine planning, deterministic PanelForge rendering, supplementary display planning, section-contract planning, front-matter strategy, Results architecture, Results drafting, Introduction literature binding, Discussion interpretation mapping, Discussion drafting, Methods architecture, Methods drafting, availability assembly, Supplementary Methods drafting, supplementary table/source-data binding, reference-library/citation audit, cross-document consistency audit, statistical-language audit, figure legend/caption audit, editorial polish passes I and II, reader-surface hygiene, internal peer review simulation, and submission package assembly. Do not start final PI review or Stage 9 closure without explicit substage authorization. |",
        )
        body = _replace(
            body,
            "Stage 9.24 Editorial polish pass I has been completed. Stage 9.25 Editorial polish pass II has been completed. Stage 9.25b Reader-surface hygiene has been completed. Stage 9.26 Internal peer review simulation has been completed. Stage 9.27 Submission package assembly remains the next unstarted manuscript step. Final package assembly remains not started.",
            "Stage 9.24 Editorial polish pass I has been completed. Stage 9.25 Editorial polish pass II has been completed. Stage 9.25b Reader-surface hygiene has been completed. Stage 9.26 Internal peer review simulation has been completed. Stage 9.27 Submission package assembly has been completed. Stage 9.28 Final human PI review packet remains the next unstarted manuscript step. Stage 9 closure remains not started.",
        )
        ROADMAP_PATH.write_text(body, encoding="utf-8")


def run() -> dict[str, Any]:
    generated_utc = _now()
    audit, gate = _stage_outputs(generated_utc)
    if not gate["pass"]:
        quarantine = _quarantine_staging()
        return {
            "status": "failed",
            "substage": "9.27",
            "quarantine": quarantine,
            "checks": audit["checks"],
            "next_substage": "9.27",
        }
    _promote_from_staging()
    shutil.rmtree(STAGING)
    if QUARANTINE.exists():
        shutil.rmtree(QUARANTINE)
    _update_registry()
    _update_stage9_memory(generated_utc, audit["checks"])
    _update_roadmap_memory()
    _update_docs()
    return {
        "status": "completed",
        "substage": "9.27",
        "outputs": [path.relative_to(ROOT).as_posix() for path in OUTPUTS.values()],
        "checks": audit["checks"],
        "next_substage": "9.28",
        "figure_file_count": len(audit["figure_rows"]),
        "source_inventory_rows": len(audit["source_rows"]),
    }


def main() -> int:
    result = run()
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] == "completed" else 1


if __name__ == "__main__":
    raise SystemExit(main())

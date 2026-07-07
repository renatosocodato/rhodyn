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
        _section("Introduction", SECTIONS / "introduction.md"),
        _section("Results", SECTIONS / "results.md"),
        _section("Discussion", SECTIONS / "discussion.md"),
        _section("Online Methods", SECTIONS / "methods.md"),
        _section("Data availability", SECTIONS / "data_availability.md"),
        _section("Code availability", SECTIONS / "code_availability.md"),
        _references_markdown(),
        _main_legend_block(),
    ]
    return "\n".join(part.strip() for part in parts if part.strip()) + "\n"


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

We submit "RhoDyn infers residence states in live-cell perturbation data" as a computational methods Article for consideration in Nature Methods. RhoDyn addresses a common bottleneck in live-cell perturbation biology. Time-lapse reporters are routinely reduced to endpoints, peaks, thresholds, or generic trajectory features, which can obscure whether the relevant biological information lies in how long a cell remains inside a response regime rather than how high the signal becomes. RhoDyn turns that question into a reviewable analysis object.

The method defines residence windows, dwell fraction, dwell time, segment count, amplitude comparators, bounded-coupling margins, reserve-like endpoint coordinates, routed-output alternatives, and uncertainty summaries in one reproducible workflow. The central advance is not the general claim that cell signaling is dynamic. It is a practical decision framework that tells users when residence adds information beyond amplitude, when a simpler summary is sufficient, and when the supplied data do not support a stronger interpretation.

The validation strategy is built for a methods journal. The manuscript includes known-truth synthetic regimes, public DRG calcium trajectories, public ERK reporter trajectories, public-derived endpoint and paired-reporter demonstrations, held-out bounded-coupling contexts, margin-sensitivity cases, inconclusive examples, and parity across Python, command-line, backend, workbench, export-bundle, source-distribution, checksum, GitHub, and Zenodo surfaces. The RhoA/microglia work is treated as a reference use case rather than as hidden evidence for the methods Article.

We believe the manuscript fits Nature Methods because it presents a reusable computational method with immediate practical relevance for live-cell signaling, imaging, perturbation, and screening studies. The paper is deliberately scoped. A residence window is a declared analysis choice, not an automatically discovered biological state. A bounded-coupling result means equivalence within a stated margin and context, not absence of all coupling. Reserve-like endpoint summaries remain tied to the measured assay, and routed-output comparisons constrain tested alternatives without identifying direct biochemical edges.

The software is publicly available as RhoDyn v0.1.0 with GitHub and Zenodo release records, documented commands, public-derived example tables, tests, figure-ready outputs, and reviewable reproducibility surfaces. We have included data and code availability statements, a Reporting Summary placeholder for final portal completion, a code-for-review surface, figure inventories, and source-data/statistics inventories.

Sincerely,

The authors

## Presubmission-inquiry draft

RhoDyn is a computational method for residence-state inference in live-cell perturbation data. It is designed for situations in which endpoint, peak, mean, or threshold summaries may miss the time a cell spends inside a biologically declared response window. The method defines dwell fraction, dwell time, segment count, amplitude comparators, bounded-coupling margins, reserve-like endpoint coordinates, routed-output alternatives, and uncertainty summaries as inspectable outputs.

The proposed Nature Methods Article would emphasize method definition and validation rather than a new primary disease-biology claim. The evidence ladder includes known-truth synthetic regimes, public calcium and ERK live-cell reporter trajectories, public-derived endpoint and paired-reporter demonstrations, held-out bounded-coupling contexts, margin-sensitivity checks, inconclusive examples, and software parity across Python, command-line, backend, workbench, export bundle, source distribution, checksums, GitHub, and Zenodo release surfaces.

The main editorial point is that RhoDyn does not claim novelty for live-cell dynamics, trajectory inference, or morphodynamic embedding broadly. Instead, it contributes a practical decision framework for determining when residence carries state information beyond amplitude, when endpoint or amplitude summaries are sufficient, and when evidence is insufficient. The manuscript is scoped to avoid overclaiming. Declared windows are not automatically discovered states, bounded coupling is margin- and context-limited, reserve-like summaries are tied to measured endpoints, and routed-output comparisons do not identify biochemical edges.

We would value the editors' view on whether this framing fits Nature Methods as an Article describing a reusable computational method for live-cell perturbation biology.
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
        f"| Main manuscript source | {'ready' if check_map.get('main_text_present') else 'blocked'} | `main_text_for_submission.md` assembles Abstract, Introduction, Results, Discussion, Online Methods, availability text, references, and figure legends. |",
        f"| Supplementary Information source | {'ready' if check_map.get('supplement_present') else 'blocked'} | `supplementary_information_for_submission.md` assembles Supplementary Methods, supplementary figure legends, supplementary table captions, and a compact traceability note. |",
        f"| Main figures | {'ready' if check_map.get('figure_files_present') else 'blocked'} | Six main display items are present in PDF, PNG, and SVG. |",
        f"| Reporting Summary | {'registered' if check_map.get('reporting_summary_present') else 'blocked'} | The required Reporting Summary placeholder is present. The final Springer Nature form remains a human submission action. |",
        f"| Code for review | {'ready' if check_map.get('code_for_review_present') else 'blocked'} | `code_for_review.md` records release identity and reproducibility commands. |",
        f"| Editor-triage note | {'ready' if check_map.get('editor_triage_note_present') else 'blocked'} | `editor_triage_note_for_cover_letter.md` gives a cover-letter-ready Nature Methods fit argument. |",
        f"| Editorial pitch | {'ready' if check_map.get('editorial_pitch_present') else 'blocked'} | `editorial_pitch_for_submission.md` contains cover-letter and presubmission-inquiry drafts. |",
        f"| Reader-surface hygiene | {'ready' if check_map.get('reader_surface_hygiene_passed') else 'blocked'} | Main manuscript and Supplementary Information surfaces are free of internal IDs and build-language tokens. |",
        f"| Package safety scan | {'ready' if check_map.get('package_safety_scan_clear') else 'blocked'} | Package files were scanned for local machine paths and token-like strings. |",
        f"| Consistency audit | {'ready' if check_map.get('package_consistency_audit_passed') else 'blocked'} | Package-level consistency checks passed. |",
        "",
        "Human actions before journal upload. Complete the official Springer Nature Reporting Summary form, choose the final corresponding-author and portal metadata, verify any journal-specific file naming rules, and review the assembled main text and Supplementary Information for final author approval.",
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
        ("Code for review", "code_for_review.md", "Release identity and reproducibility-command surface."),
        ("Editor-triage note", "editor_triage_note_for_cover_letter.md", "Cover-letter-ready Nature Methods fit, validation, and claim-boundary note."),
        ("Editorial pitch", "editorial_pitch_for_submission.md", "Cover-letter and presubmission-inquiry drafts for Nature Methods editorial triage."),
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
            and "Presubmission-inquiry draft" in (package_dir / "editorial_pitch_for_submission.md").read_text(encoding="utf-8"),
            "detail": "Editorial pitch includes cover-letter and presubmission-inquiry drafts",
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

    _write_text(staging_submission / "main_text_for_submission.md", _assemble_main_text())
    _write_text(staging_submission / "supplementary_information_for_submission.md", _assemble_supplement())
    _write_text(staging_submission / "code_for_review.md", _code_for_review())
    _write_text(staging_submission / "editor_triage_note_for_cover_letter.md", _editor_triage_note())
    _write_text(staging_submission / "editorial_pitch_for_submission.md", _editorial_pitch())
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
        "validation_outcome": "Submission package assembled with reader-clean main text, Supplementary Information, figure inventory, source-data/statistics inventory, code-for-review, Reporting Summary placeholder, and readiness checklist",
        "evidence_dependencies": [
            "manuscript/nature_methods/gate_verdicts/9.26.json",
            "manuscript/nature_methods/audits/internal_peer_review_simulation.md",
            "manuscript/nature_methods/audits/reader_surface_hygiene_report.md",
            "manuscript/nature_methods/gate_verdicts/9.21.json",
            "manuscript/nature_methods/gate_verdicts/9.23.json",
        ],
        "files_created_or_modified": [path.relative_to(ROOT).as_posix() for path in OUTPUTS.values()],
        "remaining_blockers": [
            "Final Springer Nature Reporting Summary form remains a human submission action",
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
        "The package contains reader-clean main text, Supplementary Information, code-for-review, figure inventory, source-data/statistics inventory, Reporting Summary placeholder, and readiness checklist.",
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
        "references, code-for-review surface, source-data/statistics inventory, Reporting Summary placeholder, and readiness checklist."
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

The next unstarted step is Stage 9.28 final human PI review packet. The package currently includes `submission_package/main_text_for_submission.md`, `submission_package/supplementary_information_for_submission.md`, `submission_package/code_for_review.md`, `submission_package/editor_triage_note_for_cover_letter.md`, `submission_package/editorial_pitch_for_submission.md`, `submission_package/figure_file_inventory.csv`, `submission_package/source_data_and_statistics_inventory.csv`, `submission_package/submission_readiness_checklist.md`, `submission_package/package_consistency_audit.md`, and `submission_package/submission_package_manifest.json`.

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

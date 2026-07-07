"""Run Stage 9.25b reader-surface hygiene.

Stage 9.25b removes internal manuscript-assembly tokens from the draft
reader-facing surfaces before the peer-review simulation and full package
assembly steps. The pass keeps scientific wording, figure calls, limitations,
availability identifiers, and reproducibility details intact while moving
paragraph IDs, claim IDs, source-artifact IDs, and stage metadata out of the
reader-facing Markdown.
"""

from __future__ import annotations

import csv
import json
import re
import shutil
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT / "manuscript" / "nature_methods"
SECTIONS_DIR = WORKSPACE / "sections"
FIGURES_DIR = WORKSPACE / "figures"
SUPPLEMENTARY_DIR = WORKSPACE / "supplementary"
AUDITS_DIR = WORKSPACE / "audits"
GATE_DIR = WORKSPACE / "gate_verdicts"
STAGING_DIR = WORKSPACE / "_staging" / "9.25b"
QUARANTINE_DIR = WORKSPACE / "_quarantine" / "9.25b"
MEMORY_PATH = ROOT / "docs" / "stage9_execution_memory.json"
ROADMAP_MEMORY_PATH = ROOT / "docs" / "roadmap_execution_memory.json"
REGISTRY_PATH = WORKSPACE / "contracts" / "stage9_substage_registry.json"
PLAN_PATH = ROOT / "docs" / "stage9_manuscript_assembly_plan.md"
ROADMAP_PATH = ROOT / "docs" / "roadmap.md"
README_PATH = WORKSPACE / "README.md"
CITATION_LEDGER = WORKSPACE / "refs" / "introduction_citation_ledger.csv"

GATE_925 = GATE_DIR / "9.25.json"

READER_SURFACES = [
    SECTIONS_DIR / "abstract.md",
    SECTIONS_DIR / "introduction.md",
    SECTIONS_DIR / "results.md",
    SECTIONS_DIR / "discussion.md",
    SECTIONS_DIR / "methods.md",
    SECTIONS_DIR / "data_availability.md",
    SECTIONS_DIR / "code_availability.md",
    FIGURES_DIR / "figure_legends.md",
    SUPPLEMENTARY_DIR / "supplementary_methods.md",
]

OUTPUTS = {
    "audit": AUDITS_DIR / "reader_surface_hygiene_report.md",
    "gate": GATE_DIR / "9.25b.json",
}

FORBIDDEN_DOWNSTREAM_PATHS = [
    AUDITS_DIR / "internal_peer_review_simulation.md",
    AUDITS_DIR / "reviewer_action_matrix.csv",
    WORKSPACE / "submission_package" / "pi_review_packet.md",
    WORKSPACE / "submission_package" / "submission_readiness_checklist.md",
    WORKSPACE / "stage9_completion_report.md",
]

INTERNAL_ID_RE = re.compile(r"\b(?:PARA|CLM|MTH|FIG|SFIG|STBL|STAT|ART|SUPP|REF)-\d{3,4}\b")
COMMENT_RE = re.compile(r"<!--.*?-->\s*", flags=re.S)
REF_CALL_RE = re.compile(r"\((REF-\d{4}(?:;\s*REF-\d{4})*)\)")
LOCAL_PATH_RE = re.compile("(" + "/Us" + "ers/|" + "/Vol" + "umes/|" + "Library/" + "LaunchAgents|" + "file" + "://)")
SECRET_RE = re.compile(r"\b(?:sk-[A-Za-z0-9_-]{20,}|" + "ghp" + r"_[A-Za-z0-9_]{20,}|" + "github" + r"_pat_[A-Za-z0-9_]{20,})\b")

FORBIDDEN_VISIBLE_PHRASES = [
    "Stage 9",
    "stage9",
    "stage=",
    "draft_version",
    "generated_utc",
    "para_ids",
    "claim_ids",
    "methods_stmt_ids",
    "source_artifacts",
    "repo_paths",
    "unit_id",
    "figure_id",
    "reader-surface hygiene",
    "internal peer-review simulation",
    "PI review packet",
    "submission-readiness checklist",
    "stage9 completion",
    "manifest S3 provenance",
    "S3 provenance",
    "audit trail",
    "artifact lineage",
]

UNSAFE_SCIENTIFIC_PHRASES = [
    "universal residence law",
    "guarantees",
    "proves",
    "absence of all coupling",
    "proof of no crosstalk",
    "no crosstalk",
    "true biological reserve",
    "direct live metabolic reserve assay",
    "literal molecular edge",
    "RhoDyn generated the original",
    "PyPI publication is claimed",
]

REQUIRED_READER_TERMS = [
    "residence-state",
    "bounded-coupling",
    "reserve-like",
    "routed-output",
    "inconclusive",
    "not a causal mechanism",
    "not proof that all coupling is absent",
    "not direct assays of unmeasured biological reserve capacity",
    "does not identify direct biochemical interactions",
    "not a new biological result",
    "RhoDyn v0.1.0",
    "10.5281/zenodo.21036616",
    "10.5281/zenodo.21036615",
]

REQUIRED_SURFACE_PHRASES = {
    SECTIONS_DIR / "abstract.md": ["# Abstract", "RhoDyn therefore provides a reproducible route"],
    SECTIONS_DIR / "introduction.md": [
        "(1-4)",
        "(10,11)",
        "(1-9)",
        "(11,12)",
        "explicit checks that allow each component to be tested in sequence",
    ],
    SECTIONS_DIR / "results.md": [
        "The held-out analysis therefore keeps pass and inconclusive outcomes side by side",
        "A reusable method also needs to remain inspectable",
    ],
    SECTIONS_DIR / "discussion.md": ["Reproducibility evidence strengthens the method"],
    SECTIONS_DIR / "methods.md": ["Methods section refer to RhoDyn v0.1.0"],
    SECTIONS_DIR / "data_availability.md": ["10.5281/zenodo.21036615"],
    SECTIONS_DIR / "code_availability.md": ["10.5281/zenodo.21036616", "10.5281/zenodo.20811171"],
    FIGURES_DIR / "figure_legends.md": ["Non-example panels collect ambiguous regimes"],
    SUPPLEMENTARY_DIR / "supplementary_methods.md": ["Supplementary Methods"],
}


def _now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _git_sha() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    except (OSError, subprocess.CalledProcessError):
        return "unknown"


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _citation_numbers() -> dict[str, int]:
    with CITATION_LEDGER.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    return {row["ref_id"]: index for index, row in enumerate(rows, start=1)}


def _format_numeric_refs(numbers: list[int]) -> str:
    ranges: list[str] = []
    start = prev = numbers[0]
    for number in numbers[1:]:
        if number == prev + 1:
            prev = number
            continue
        if prev - start >= 2:
            ranges.append(f"{start}-{prev}")
        elif prev == start:
            ranges.append(str(start))
        else:
            ranges.extend([str(start), str(prev)])
        start = prev = number
    if prev - start >= 2:
        ranges.append(f"{start}-{prev}")
    elif prev == start:
        ranges.append(str(start))
    else:
        ranges.extend([str(start), str(prev)])
    return "(" + ",".join(ranges) + ")"


def _replace_ref_calls(text: str, ref_numbers: dict[str, int]) -> str:
    def repl(match: re.Match[str]) -> str:
        refs = [token.strip() for token in match.group(1).split(";")]
        missing = [ref for ref in refs if ref not in ref_numbers]
        if missing:
            raise KeyError(f"Unknown reference token(s): {missing}")
        return _format_numeric_refs([ref_numbers[ref] for ref in refs])

    return REF_CALL_RE.sub(repl, text)


def _strip_html_comments(text: str) -> tuple[str, int]:
    comments = COMMENT_RE.findall(text)
    cleaned = COMMENT_RE.sub("", text)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned).strip() + "\n"
    return cleaned, len(comments)


def _clean_abstract(text: str) -> str:
    if "## Abstract" in text:
        text = text.split("## Abstract", 1)[1].strip()
    elif "# Abstract" in text:
        text = text.split("# Abstract", 1)[1].strip()
    return "# Abstract\n\n" + text.strip() + "\n"


def _clean_surfaces() -> tuple[dict[Path, str], dict[str, Any]]:
    ref_numbers = _citation_numbers()
    cleaned: dict[Path, str] = {}
    removed_comments: dict[str, int] = {}
    ref_replacements: dict[str, int] = {}
    for path in READER_SURFACES:
        original = path.read_text(encoding="utf-8")
        text, count = _strip_html_comments(original)
        removed_comments[path.relative_to(ROOT).as_posix()] = count
        if path == SECTIONS_DIR / "abstract.md":
            text = _clean_abstract(text)
        before_refs = len(re.findall(r"REF-\d{4}", text))
        if before_refs:
            text = _replace_ref_calls(text, ref_numbers)
        ref_replacements[path.relative_to(ROOT).as_posix()] = before_refs
        cleaned[path] = text
    return cleaned, {"removed_comments": removed_comments, "ref_replacements": ref_replacements}


def _figure_calls(text: str) -> list[str]:
    return re.findall(r"\((?:Fig\.|Supplementary Fig\.|Supplementary Table)[^)]+\)", text)


def _terminal_figure_calls(text: str) -> list[str]:
    return re.findall(r"[^.!?]*\((?:Fig\.|Supplementary Fig\.|Supplementary Table)[^)]+\)\.", text)


def _line_hits(path: Path, text: str, patterns: list[str]) -> list[str]:
    hits: list[str] = []
    for line_no, line in enumerate(text.splitlines(), start=1):
        lower = line.lower()
        for pattern in patterns:
            if pattern.lower() in lower:
                hits.append(f"{path.relative_to(ROOT).as_posix()}:{line_no}:{pattern}")
    return hits


def _regex_line_hits(path: Path, text: str, regex: re.Pattern[str]) -> list[str]:
    hits: list[str] = []
    for line_no, line in enumerate(text.splitlines(), start=1):
        if regex.search(line):
            hits.append(f"{path.relative_to(ROOT).as_posix()}:{line_no}:{regex.search(line).group(0)}")
    return hits


def _audit_surfaces(before: dict[Path, str], after: dict[Path, str], hygiene: dict[str, Any]) -> dict[str, Any]:
    gate_925 = _read_json(GATE_925) if GATE_925.exists() else {}
    combined = "\n\n".join(after.values())
    before_results_calls = _figure_calls(COMMENT_RE.sub("", before[SECTIONS_DIR / "results.md"]))
    after_results_calls = _figure_calls(after[SECTIONS_DIR / "results.md"])
    before_legend_calls = _figure_calls(COMMENT_RE.sub("", before[FIGURES_DIR / "figure_legends.md"]))
    after_legend_calls = _figure_calls(after[FIGURES_DIR / "figure_legends.md"])

    comment_hits = [path.relative_to(ROOT).as_posix() for path, text in after.items() if "<!--" in text or "-->" in text]
    internal_id_hits = [
        hit
        for path, text in after.items()
        for hit in _regex_line_hits(path, text, INTERNAL_ID_RE)
    ]
    stage_language_hits = [
        hit
        for path, text in after.items()
        for hit in _line_hits(path, text, FORBIDDEN_VISIBLE_PHRASES)
    ]
    unsafe_hits = [
        hit
        for path, text in after.items()
        for hit in _line_hits(path, text, UNSAFE_SCIENTIFIC_PHRASES)
    ]
    local_path_hits = [
        hit
        for path, text in after.items()
        for hit in _regex_line_hits(path, text, LOCAL_PATH_RE)
    ]
    secret_hits = [
        hit
        for path, text in after.items()
        for hit in _regex_line_hits(path, text, SECRET_RE)
    ]
    terminal_calls = {
        path.relative_to(ROOT).as_posix(): _terminal_figure_calls(text)
        for path, text in after.items()
        if _terminal_figure_calls(text)
    }
    missing_required_terms = [
        term for term in REQUIRED_READER_TERMS if term.lower() not in combined.lower()
    ]
    missing_surface_phrases = {
        path.relative_to(ROOT).as_posix(): [phrase for phrase in phrases if phrase not in after[path]]
        for path, phrases in REQUIRED_SURFACE_PHRASES.items()
        if path in after and any(phrase not in after[path] for phrase in phrases)
    }
    figure_call_errors: list[str] = []
    if before_results_calls != after_results_calls:
        figure_call_errors.append("sections/results.md")
    if before_legend_calls != after_legend_calls:
        figure_call_errors.append("figures/figure_legends.md")

    downstream_paths = [path.relative_to(ROOT).as_posix() for path in FORBIDDEN_DOWNSTREAM_PATHS if path.exists()]
    panel_s3_crossrefs = [
        hit
        for path in [FIGURES_DIR / "figure_legends.md", SUPPLEMENTARY_DIR / "supplementary_methods.md"]
        for hit in _line_hits(path, after[path], ["manifest S3 provenance", "S3 provenance"])
    ]
    abstract_stage_header_present = "Stage 9" in after[SECTIONS_DIR / "abstract.md"] or "Strategy version" in after[SECTIONS_DIR / "abstract.md"]

    checks = [
        {
            "name": "stage_9_25_gate_passed",
            "passed": gate_925.get("pass") is True and gate_925.get("next_substage") == "9.25b",
            "detail": "Stage 9.25 editorial polish pass II gate is present and points to Stage 9.25b",
        },
        {
            "name": "reader_comments_removed",
            "passed": not comment_hits,
            "detail": f"comment_hits={comment_hits}; removed_comments={hygiene['removed_comments']}",
        },
        {
            "name": "internal_ids_absent_from_reader_surfaces",
            "passed": not internal_id_hits,
            "detail": f"internal_id_hits={internal_id_hits}; ref_replacements={hygiene['ref_replacements']}",
        },
        {
            "name": "stage_and_build_language_absent",
            "passed": not stage_language_hits and not abstract_stage_header_present,
            "detail": f"stage_language_hits={stage_language_hits}; abstract_stage_header_present={abstract_stage_header_present}",
        },
        {
            "name": "legends_and_captions_free_of_lineage_language",
            "passed": not panel_s3_crossrefs and "manifest" not in after[FIGURES_DIR / "figure_legends.md"].lower(),
            "detail": f"panel_s3_crossrefs={panel_s3_crossrefs}",
        },
        {
            "name": "meaning_and_figure_flow_preserved",
            "passed": not figure_call_errors and not terminal_calls and not missing_required_terms and not missing_surface_phrases,
            "detail": f"figure_call_errors={figure_call_errors}; terminal_calls={terminal_calls}; missing_required_terms={missing_required_terms}; missing_surface_phrases={missing_surface_phrases}",
        },
        {
            "name": "claim_boundaries_preserved",
            "passed": not unsafe_hits,
            "detail": f"unsafe_hits={unsafe_hits}",
        },
        {
            "name": "local_path_and_secret_scan_clear",
            "passed": not local_path_hits and not secret_hits,
            "detail": f"local_path_hits={local_path_hits}; secret_hits={secret_hits}",
        },
        {
            "name": "no_internal_peer_review_or_package_started",
            "passed": not downstream_paths,
            "detail": f"downstream_paths={downstream_paths}",
        },
    ]
    return {
        "generated_utc": _now(),
        "commit": _git_sha(),
        "checks": checks,
        "comment_hits": comment_hits,
        "internal_id_hits": internal_id_hits,
        "stage_language_hits": stage_language_hits,
        "unsafe_hits": unsafe_hits,
        "local_path_hits": local_path_hits,
        "secret_hits": secret_hits,
        "terminal_calls": terminal_calls,
        "missing_required_terms": missing_required_terms,
        "missing_surface_phrases": missing_surface_phrases,
        "figure_call_errors": figure_call_errors,
        "downstream_paths": downstream_paths,
        "panel_s3_crossrefs": panel_s3_crossrefs,
        "abstract_stage_header_present": abstract_stage_header_present,
        "hygiene_actions": hygiene,
        "recursive_rounds": [
            {"round": 1, "focus": "hidden metadata and HTML-comment removal", "status": "pass" if not comment_hits else "fail"},
            {"round": 2, "focus": "internal ID and REF token removal from reader surfaces", "status": "pass" if not internal_id_hits else "fail"},
            {"round": 3, "focus": "stage, lineage, and figure-caption leakage scan", "status": "pass" if not stage_language_hits and not panel_s3_crossrefs else "fail"},
            {"round": 4, "focus": "scientific boundary, citation, figure-call, and availability preservation", "status": "pass" if not unsafe_hits and not figure_call_errors and not missing_required_terms and not missing_surface_phrases else "fail"},
        ],
    }


def _audit_text(analysis: dict[str, Any]) -> str:
    checks_rows = "\n".join(
        f"| {item['name']} | {'pass' if item['passed'] else 'fail'} | {item['detail']} |"
        for item in analysis["checks"]
    )
    comments_rows = "\n".join(
        f"| {path} | {count} | {analysis['hygiene_actions']['ref_replacements'].get(path, 0)} |"
        for path, count in analysis["hygiene_actions"]["removed_comments"].items()
    )
    rounds_rows = "\n".join(
        f"| {item['round']} | {item['focus']} | {item['status']} |"
        for item in analysis["recursive_rounds"]
    )
    return f"""<!-- READER-SURFACE-HYGIENE stage=9.25b generated={analysis['generated_utc']} commit={analysis['commit']} -->
# Stage 9.25b reader-surface hygiene report

Stage 9.25b cleans the manuscript-facing surfaces after the second editorial polish pass. The pass removes internal paragraph IDs, claim IDs, method-statement IDs, reference tokens, source-artifact IDs, stage metadata, and HTML comments from the reader-facing Markdown. It does not change the evidence set, statistics, figures, source data, model outputs, figure calls, biological examples, or interpretation limits.

## Summary

The hygiene pass completed four recursive checks. Hidden comments were removed from the manuscript surfaces, Introduction reference tokens were converted to readable numbered citation calls, the abstract now opens as a clean reader-facing abstract, and figure legends remain free of lineage language. Code and data availability still retain public DOIs, repository URLs, and reproducibility commands where they are scientifically and practically required.

## Recursive hygiene rounds

| Round | Focus | Status |
|---|---|---|
{rounds_rows}

## Gate checks

| Check | Status | Detail |
|---|---|---|
{checks_rows}

## Reader-surface cleanup

| Surface | Hidden comments removed | Internal REF tokens replaced |
|---|---:|---:|
{comments_rows}

## Scope boundary

This stage is a reader-surface hygiene pass only. It preserves the method claim that residence-state inference, bounded-coupling decisions, reserve-like endpoint summaries, routed-output comparisons, and reproducibility checks are reviewable under declared inputs and limits. It does not add new biological evidence, start the internal peer-review simulation, assemble the submission package, or promote any claim beyond the retained evidence set.
"""


def _gate_payload(analysis: dict[str, Any]) -> dict[str, Any]:
    return {
        "substage": "9.25b",
        "title": "Reader-surface hygiene gate",
        "generated_utc": analysis["generated_utc"],
        "commit": analysis["commit"],
        "pass": all(item["passed"] for item in analysis["checks"]),
        "checks": analysis["checks"],
        "comment_hits": analysis["comment_hits"],
        "internal_id_hits": analysis["internal_id_hits"],
        "stage_language_hits": analysis["stage_language_hits"],
        "unsafe_hits": analysis["unsafe_hits"],
        "local_path_hits": analysis["local_path_hits"],
        "secret_hits": analysis["secret_hits"],
        "terminal_calls": analysis["terminal_calls"],
        "missing_required_terms": analysis["missing_required_terms"],
        "missing_surface_phrases": analysis["missing_surface_phrases"],
        "figure_call_errors": analysis["figure_call_errors"],
        "downstream_paths": analysis["downstream_paths"],
        "panel_s3_crossrefs": analysis["panel_s3_crossrefs"],
        "hygiene_actions": analysis["hygiene_actions"],
        "recursive_rounds": analysis["recursive_rounds"],
        "outputs": [
            "manuscript/nature_methods/audits/reader_surface_hygiene_report.md",
            "manuscript/nature_methods/gate_verdicts/9.25b.json",
            *[path.relative_to(ROOT).as_posix() for path in READER_SURFACES],
        ],
        "scope_boundary": "Reader-surface hygiene only. No new evidence, analyses, statistics, model outputs, figures, figure numbering, claim expansion, internal peer-review simulation, PI packet, readiness checklist, or final package assembly.",
        "next_substage": "9.26",
    }


def _stage_outputs(after: dict[Path, str], analysis: dict[str, Any], gate: dict[str, Any]) -> None:
    for path, text in after.items():
        staged = STAGING_DIR / path.relative_to(WORKSPACE)
        staged.parent.mkdir(parents=True, exist_ok=True)
        staged.write_text(text, encoding="utf-8")
    audit_path = STAGING_DIR / OUTPUTS["audit"].relative_to(WORKSPACE)
    gate_path = STAGING_DIR / OUTPUTS["gate"].relative_to(WORKSPACE)
    audit_path.parent.mkdir(parents=True, exist_ok=True)
    gate_path.parent.mkdir(parents=True, exist_ok=True)
    audit_path.write_text(_audit_text(analysis), encoding="utf-8")
    _write_json(gate_path, gate)


def _promote_from_staging() -> None:
    for path in [*READER_SURFACES, *OUTPUTS.values()]:
        staged = STAGING_DIR / path.relative_to(WORKSPACE)
        path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(staged, path)


def _quarantine_staging() -> Path:
    QUARANTINE_DIR.parent.mkdir(parents=True, exist_ok=True)
    if QUARANTINE_DIR.exists():
        shutil.rmtree(QUARANTINE_DIR)
    shutil.move(str(STAGING_DIR), str(QUARANTINE_DIR))
    return QUARANTINE_DIR


def _update_registry() -> None:
    registry = _read_json(REGISTRY_PATH)
    for substage in registry.get("substages", []):
        if substage.get("id") == "9.25b":
            substage["status"] = "complete_reader_surface_hygiene_bound"
    registry["last_completed_substage"] = "9.25b"
    registry["next_substage"] = "9.26"
    _write_json(REGISTRY_PATH, registry)


def _upsert_completed_substage(memory: dict[str, Any], checks: list[dict[str, Any]]) -> None:
    record = {
        "substage": "9.25b",
        "status": "pass",
        "pass": True,
        "gate_verdict_path": "manuscript/nature_methods/gate_verdicts/9.25b.json",
        "validation_outcome": "Reader-facing manuscript surfaces are free of internal IDs, stage metadata, hidden comments, and lineage language",
        "evidence_dependencies": [
            "manuscript/nature_methods/gate_verdicts/9.25.json",
            "manuscript/nature_methods/refs/introduction_citation_ledger.csv",
            "manuscript/nature_methods/sections/abstract.md",
            "manuscript/nature_methods/sections/introduction.md",
            "manuscript/nature_methods/sections/results.md",
            "manuscript/nature_methods/sections/discussion.md",
            "manuscript/nature_methods/sections/methods.md",
            "manuscript/nature_methods/sections/data_availability.md",
            "manuscript/nature_methods/sections/code_availability.md",
            "manuscript/nature_methods/figures/figure_legends.md",
            "manuscript/nature_methods/supplementary/supplementary_methods.md",
        ],
        "files_created_or_modified": [
            "manuscript/nature_methods/audits/reader_surface_hygiene_report.md",
            "manuscript/nature_methods/gate_verdicts/9.25b.json",
            *[path.relative_to(ROOT).as_posix() for path in READER_SURFACES],
        ],
        "remaining_blockers": [
            "Internal peer-review simulation has not started",
            "Full manuscript and submission-package assembly have not started beyond authorized preparation surfaces",
        ],
        "checks": checks,
    }
    entries = [item for item in memory.get("completed_substages", []) if item.get("substage") != "9.25b"]
    entries.append(record)
    memory["completed_substages"] = entries


def _update_stage9_memory(generated_utc: str, checks: list[dict[str, Any]]) -> None:
    memory = _read_json(MEMORY_PATH)
    memory["generated_utc"] = generated_utc
    memory["current_substage"] = "9.25b"
    memory["reader_surface_hygiene_started"] = True
    memory["status"] = "stage9_25b_reader_surface_hygiene_bound"
    memory["current_gate"] = "Stage 9.25b reader-surface hygiene removed internal reader-facing scaffold language"
    memory["next_substage"] = "9.26"
    memory["next_substage_authorized"] = False
    memory["stage9_active_gate"] = "Stage 9.25b Reader-surface hygiene complete; internal peer review not started"
    memory["stage9_25b_checks"] = checks
    artifacts = memory.setdefault("artifacts", [])
    for artifact in [
        "manuscript/nature_methods/audits/reader_surface_hygiene_report.md",
        "manuscript/nature_methods/gate_verdicts/9.25b.json",
    ]:
        if artifact not in artifacts:
            artifacts.append(artifact)
    memory["gate"] = [
        "Stage 9.-1 contract and schema files exist and pass the scaffold checker.",
        "Stage 9.0 through Stage 9.25b are complete through reader-surface hygiene.",
        "Stage 9.26 through Stage 9.29 remain not started.",
        "No internal peer-review simulation, PI review packet, submission readiness checklist, or final package assembly is created in this pass.",
        "Reader-facing surfaces no longer expose internal IDs, hidden metadata, stage language, or lineage wording.",
    ]
    memory["scope_rule"] = (
        "Stage 9 has completed evidence intake, venue-guidance registration, representative methods-paper corpus analysis, "
        "narrative-spine selection, claim freeze, paragraph-level claim planning, main figure-spine planning, deterministic "
        "PanelForge rendering, supplementary display planning, section-contract planning, title/abstract strategy, Results "
        "architecture, Results drafting, Introduction literature binding, Discussion interpretation mapping, Discussion drafting, "
        "Methods architecture, Methods drafting, availability assembly, Supplementary Methods drafting, supplementary table/source-data "
        "binding, reference-library/citation audit, cross-document consistency audit, statistical/quantitative language audit, "
        "figure legend/caption audit, editorial polish passes I and II, and reader-surface hygiene only. Do not start internal peer review, "
        "review response, or final submission package without explicit substage authorization."
    )
    _upsert_completed_substage(memory, checks)
    _write_json(MEMORY_PATH, memory)


def _update_roadmap_memory() -> None:
    memory = _read_json(ROADMAP_MEMORY_PATH)
    current = memory.setdefault("current_position", {})
    current["active_stage"] = "Stage 9.25b Reader-surface hygiene complete; internal peer review not started"
    current["stage9_active_gate"] = "Stage 9.25b Reader-surface hygiene complete; internal peer review not started"
    current["after_stage9_25b_reader_surface_hygiene"] = (
        "Stage 9.25b removed internal IDs, hidden comments, stage metadata, and lineage wording from reader-facing manuscript surfaces. "
        "It preserved figure-call flow, availability identifiers, claim boundaries, and the evidence set, and did not start internal peer review or package assembly."
    )
    current["current_gate"] = "Reader-facing surfaces cleaned without evidence-layer changes"
    current["next_stage"] = "Stage 9.26 Internal peer review simulation"
    for stage in memory.get("stage_lock", []):
        if not isinstance(stage, dict) or stage.get("stage") != 9:
            continue
        stage["status"] = "stage9_25b_reader_surface_hygiene_bound"
        stage["current_gate"] = "Stage 9.25b reader-surface hygiene removed internal manuscript-assembly tokens"
        stage["scope_rule"] = (
            "Stage 9 has completed evidence intake, venue-guidance registration, representative methods-paper corpus analysis, "
            "narrative-spine selection, claim freeze, paragraph-level claim planning, main figure-spine planning, deterministic "
            "PanelForge rendering, supplementary display planning, section-contract planning, front-matter strategy, Results architecture, "
            "Results drafting, Introduction literature binding, Discussion interpretation mapping, Discussion drafting, Methods architecture, "
            "Methods drafting, availability assembly, Supplementary Methods drafting, supplementary table/source-data binding, reference-library/citation audit, "
            "cross-document consistency audit, statistical-language audit, figure legend/caption audit, editorial polish passes I and II, and reader-surface hygiene only. "
            "Do not start internal peer review, review response, or final submission packaging without explicit substage authorization."
        )
        artifacts = stage.setdefault("artifacts", [])
        for artifact in [
            "manuscript/nature_methods/audits/reader_surface_hygiene_report.md",
            "manuscript/nature_methods/gate_verdicts/9.25b.json",
            "scripts/run_stage9_25b_reader_surface_hygiene.py",
        ]:
            if artifact not in artifacts:
                artifacts.append(artifact)
        gate = stage.setdefault("gate", [])
        hygiene_gate = "Stage 9.25b removed internal reader-surface tokens while preserving evidence boundaries and figure-call flow."
        if hygiene_gate not in gate:
            gate.append(hygiene_gate)
        for subphase in stage.get("subphases", []):
            if isinstance(subphase, dict) and subphase.get("id") == "9.25b":
                subphase["status"] = "complete_reader_surface_hygiene_bound"
                subphase["evidence"] = "manuscript/nature_methods/gate_verdicts/9.25b.json"
    _write_json(ROADMAP_MEMORY_PATH, memory)


def _replace_once(body: str, old: str, new: str) -> str:
    return body.replace(old, new) if old in body else body


def _update_docs() -> None:
    README_PATH.write_text(
        """# Nature Methods manuscript workspace

This directory is the Stage 9 manuscript-assembly workspace for RhoDyn.

Current status. Stage 9.25b reader-surface hygiene complete.

The workspace now contains the authorized manuscript components through reader-surface hygiene. Evidence intake, venue guidance, methods-paper corpus analysis, narrative spine, claim freeze, paragraph planning, figure planning, deterministic main-figure rendering, supplementary display planning, section contracts, front matter, Results, Introduction, Discussion, Methods, availability statements, Supplementary Methods, supplementary table/source-data binding, reference audit, cross-document consistency audit, statistical-language audit, figure legend/caption audit, editorial polish passes I and II, and reader-surface hygiene are present.

The next unstarted step is Stage 9.26 internal peer review simulation. Final manuscript assembly, PI review packet, submission-readiness checklist, and final package assembly have not started.

PanelForge figure rendering has already been exercised through the authorized Stage 9.6b deterministic rendering lane. The placeholder under `tools/panelforge-figures/` is not a clone, `.venv-panelforge` is not created by this workspace, and no local figure-engine repository is vendored here.
""",
        encoding="utf-8",
    )
    if PLAN_PATH.exists():
        body = PLAN_PATH.read_text(encoding="utf-8")
        body = _replace_once(
            body,
            "Stage 9.25 registers `audits/editorial_pass_2.md` and `gate_verdicts/9.25.json`, and tightens venue-style readability without changing evidence bindings. The current state intentionally does not create the reader-surface hygiene gate, internal peer-review simulation, or full submission-package files.",
            "Stage 9.25 registers `audits/editorial_pass_2.md` and `gate_verdicts/9.25.json`, and tightens venue-style readability without changing evidence bindings. Stage 9.25b registers `audits/reader_surface_hygiene_report.md` and `gate_verdicts/9.25b.json`, and removes internal reader-surface tokens without changing evidence bindings. The current state intentionally does not create the internal peer-review simulation or full submission-package files.",
        )
        body = _replace_once(
            body,
            "| 9.25b | Reader-surface hygiene gate | not_started | Strip internal IDs and build-language from reader-facing surfaces before assembly. |",
            "| 9.25b | Reader-surface hygiene gate | complete_reader_surface_hygiene_bound | Strip internal IDs and build-language from reader-facing surfaces before assembly. |",
        )
        PLAN_PATH.write_text(body, encoding="utf-8")
    if ROADMAP_PATH.exists():
        body = ROADMAP_PATH.read_text(encoding="utf-8")
        body = _replace_once(
            body,
            "and Stage 9.25 has completed editorial polish pass II. Reader-surface\nhygiene, internal peer review, and final package assembly remain not started.",
            "Stage 9.25 has completed editorial polish pass II, and Stage 9.25b has\ncompleted reader-surface hygiene. Internal peer review and final package assembly\nremain not started.",
        )
        body = _replace_once(
            body,
            "| Stage 9. Nature Methods manuscript assembly | Stage 9.25 Editorial polish pass II complete, reader-surface hygiene not started. | The current boundary is evidence intake, official venue-guidance registration, representative methods-paper corpus analysis, narrative-spine selection, claim freeze, paragraph-level claim planning, main figure-spine planning, deterministic PanelForge rendering, supplementary display planning, section-contract planning, front-matter strategy, Results architecture, Results drafting, Introduction literature binding, Discussion interpretation mapping, Discussion drafting, Methods architecture, Methods drafting, availability assembly, Supplementary Methods drafting, supplementary table/source-data binding, reference-library/citation audit, cross-document consistency audit, statistical-language audit, figure legend/caption audit, and editorial polish passes I and II only. Do not start reader-surface hygiene, internal peer review, review response, or final submission packaging without explicit substage authorization. |",
            "| Stage 9. Nature Methods manuscript assembly | Stage 9.25b Reader-surface hygiene complete, internal peer review not started. | The current boundary is evidence intake, official venue-guidance registration, representative methods-paper corpus analysis, narrative-spine selection, claim freeze, paragraph-level claim planning, main figure-spine planning, deterministic PanelForge rendering, supplementary display planning, section-contract planning, front-matter strategy, Results architecture, Results drafting, Introduction literature binding, Discussion interpretation mapping, Discussion drafting, Methods architecture, Methods drafting, availability assembly, Supplementary Methods drafting, supplementary table/source-data binding, reference-library/citation audit, cross-document consistency audit, statistical-language audit, figure legend/caption audit, editorial polish passes I and II, and reader-surface hygiene only. Do not start internal peer review, review response, or final submission packaging without explicit substage authorization. |",
        )
        body = _replace_once(
            body,
            "Stage 9.10 Results subsection architecture has been completed. Stage 9.11 Results drafting pass has been completed. Stage 9.12 Introduction literature binding has been completed. Stage 9.13 Discussion interpretation map has been completed. Stage 9.14 Discussion drafting pass has been completed. Stage 9.15 Methods architecture has been completed. Stage 9.16 Methods drafting pass has been completed. Stage 9.17 software, data, and code availability assembly has been completed. Stage 9.18 Supplementary Methods drafting has been completed. Stage 9.19 Supplementary tables and source-data binding has been completed. Stage 9.20 Reference library and citation audit has been completed. Stage 9.21 Cross-document consistency audit has been completed. Stage 9.22 Statistical and quantitative language audit has been completed. Stage 9.23 Figure legend and caption audit has been completed. Stage 9.24 Editorial polish pass I has been completed. Stage 9.25 Editorial polish pass II has been completed. Stage 9.25b Reader-surface hygiene gate remains the next unstarted manuscript step. Final package assembly remains not started.",
            "Stage 9.10 Results subsection architecture has been completed. Stage 9.11 Results drafting pass has been completed. Stage 9.12 Introduction literature binding has been completed. Stage 9.13 Discussion interpretation map has been completed. Stage 9.14 Discussion drafting pass has been completed. Stage 9.15 Methods architecture has been completed. Stage 9.16 Methods drafting pass has been completed. Stage 9.17 software, data, and code availability assembly has been completed. Stage 9.18 Supplementary Methods drafting has been completed. Stage 9.19 Supplementary tables and source-data binding has been completed. Stage 9.20 Reference library and citation audit has been completed. Stage 9.21 Cross-document consistency audit has been completed. Stage 9.22 Statistical and quantitative language audit has been completed. Stage 9.23 Figure legend and caption audit has been completed. Stage 9.24 Editorial polish pass I has been completed. Stage 9.25 Editorial polish pass II has been completed. Stage 9.25b Reader-surface hygiene has been completed. Stage 9.26 Internal peer review simulation remains the next unstarted manuscript step. Final package assembly remains not started.",
        )
        ROADMAP_PATH.write_text(body, encoding="utf-8")


def run() -> dict[str, Any]:
    if STAGING_DIR.exists():
        shutil.rmtree(STAGING_DIR)
    STAGING_DIR.mkdir(parents=True, exist_ok=True)
    before = {path: path.read_text(encoding="utf-8") for path in READER_SURFACES}
    after, hygiene = _clean_surfaces()
    analysis = _audit_surfaces(before, after, hygiene)
    gate = _gate_payload(analysis)
    _stage_outputs(after, analysis, gate)
    if not gate["pass"]:
        quarantine = _quarantine_staging()
        return {
            "status": "failed",
            "substage": "9.25b",
            "quarantine": quarantine.relative_to(ROOT).as_posix(),
            "checks": analysis["checks"],
            "next_substage": "9.25b",
        }
    _promote_from_staging()
    shutil.rmtree(STAGING_DIR)
    if QUARANTINE_DIR.exists():
        shutil.rmtree(QUARANTINE_DIR)
    _update_registry()
    _update_stage9_memory(analysis["generated_utc"], analysis["checks"])
    _update_roadmap_memory()
    _update_docs()
    return {
        "status": "completed",
        "substage": "9.25b",
        "outputs": [
            "manuscript/nature_methods/audits/reader_surface_hygiene_report.md",
            "manuscript/nature_methods/gate_verdicts/9.25b.json",
        ],
        "checks": analysis["checks"],
        "next_substage": "9.26",
    }


def main() -> int:
    result = run()
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] == "completed" else 1


if __name__ == "__main__":
    raise SystemExit(main())

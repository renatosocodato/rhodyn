"""Run Stage 9.25 editorial polish pass II.

Stage 9.25 performs a final venue-style readability pass over the current
Nature Methods manuscript surfaces. It removes residual process-like phrasing
from reader-facing prose, varies repetitive legend openings, and preserves the
evidence bindings, paragraph identifiers, figure calls, and interpretation
limits established through Stage 9.24.
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT / "manuscript" / "nature_methods"
SECTIONS_DIR = WORKSPACE / "sections"
FIGURES_DIR = WORKSPACE / "figures"
AUDITS_DIR = WORKSPACE / "audits"
GATE_DIR = WORKSPACE / "gate_verdicts"
STAGING_DIR = WORKSPACE / "_staging" / "9.25"
QUARANTINE_DIR = WORKSPACE / "_quarantine" / "9.25"
MEMORY_PATH = ROOT / "docs" / "stage9_execution_memory.json"
ROADMAP_MEMORY_PATH = ROOT / "docs" / "roadmap_execution_memory.json"
REGISTRY_PATH = WORKSPACE / "contracts" / "stage9_substage_registry.json"
PLAN_PATH = ROOT / "docs" / "stage9_manuscript_assembly_plan.md"
ROADMAP_PATH = ROOT / "docs" / "roadmap.md"
README_PATH = WORKSPACE / "README.md"

GATE_924 = GATE_DIR / "9.24.json"

SURFACE_PATHS = [
    SECTIONS_DIR / "introduction.md",
    SECTIONS_DIR / "results.md",
    SECTIONS_DIR / "discussion.md",
    SECTIONS_DIR / "methods.md",
    FIGURES_DIR / "figure_legends.md",
]

OUTPUTS = {
    "audit": AUDITS_DIR / "editorial_pass_2.md",
    "gate": GATE_DIR / "9.25.json",
}

FORBIDDEN_DOWNSTREAM_PATHS = [
    AUDITS_DIR / "reader_surface_hygiene_report.md",
    AUDITS_DIR / "internal_peer_review_simulation.md",
    AUDITS_DIR / "reviewer_action_matrix.csv",
    WORKSPACE / "submission_package" / "pi_review_packet.md",
    WORKSPACE / "submission_package" / "submission_readiness_checklist.md",
    WORKSPACE / "stage9_completion_report.md",
]

UNSAFE_PHRASES = [
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

REQUIRED_LIMIT_TERMS = [
    "declared biological window",
    "not a causal mechanism",
    "amplitude and endpoint summaries remain useful",
    "inconclusive",
    "slower or context-specific coupling",
    "reserve-like",
    "measured endpoint",
    "direct biochemical interactions",
    "not a new biological result",
    "retained evidence set",
]

PROCESS_PHRASES = [
    "figure-locked order",
    "final Results step",
    "Results unit",
    "Methods draft",
    "method claim",
    "software evidence",
    "decision state",
    "automatic equivalence engine",
]

REPLACEMENTS: dict[Path, list[tuple[str, str]]] = {
    SECTIONS_DIR / "introduction.md": [
        (
            "RhoDyn is designed to make those decisions reproducible across Python, command-line, backend, workbench, and archive surfaces, with explicit reproducibility checks, before the Results tests each component in figure-locked order.",
            "RhoDyn is designed to make those decisions reproducible across Python, command-line, backend, workbench, and archive surfaces, with explicit checks that allow each component to be tested in sequence.",
        ),
    ],
    SECTIONS_DIR / "results.md": [
        (
            "The held-out Results unit therefore keeps pass and inconclusive states side by side, which is essential for using RhoDyn as a decision framework rather than an automatic equivalence engine.",
            "The held-out analysis therefore keeps pass and inconclusive outcomes side by side, which is essential for using RhoDyn as a decision framework rather than an automatic equivalence label.",
        ),
        (
            "The final Results step asks whether the method can be inspected and reproduced through the software surfaces a user would actually encounter.",
            "A reusable method also needs to remain inspectable through the software surfaces a user would actually encounter.",
        ),
        (
            "These results support cross-surface reproducibility for the retained evidence set and close the Results section by making RhoDyn's computational decisions inspectable rather than merely available as code.",
            "These results support cross-surface reproducibility for the retained evidence set by making RhoDyn's computational decisions inspectable rather than merely available as code.",
        ),
    ],
    SECTIONS_DIR / "discussion.md": [
        (
            "The public trajectory demonstrations extend that method claim beyond the motivating RhoA/microglia reference use case without turning it into a universal biological rule.",
            "The public trajectory demonstrations extend that method contribution beyond the motivating RhoA/microglia reference use case without turning it into a universal biological rule.",
        ),
        (
            "Bounded-coupling decisions are useful only when the margin, uncertainty rule, grouping level, and decision state are declared before interpretation, and the held-out ERK/Akt contexts show why inconclusive cases must remain visible.",
            "Bounded-coupling decisions are useful only when the margin, uncertainty rule, grouping level, and decision outcome are declared before interpretation, and the held-out ERK/Akt contexts show why inconclusive cases must remain visible.",
        ),
        (
            "RhoDyn's software evidence strengthens the method by making those decisions inspectable across use surfaces.",
            "Reproducibility evidence strengthens the method by making those decisions inspectable across use surfaces.",
        ),
    ],
    SECTIONS_DIR / "methods.md": [
        (
            "All analyses in this Methods draft refer to RhoDyn v0.1.0 and to the locked evidence snapshot `stage7.8-methods-readiness@242f06c49e8310b81ac1c06a270bb6810f3f4cfc` dated 2026-06-30.",
            "All analyses in this Methods section refer to RhoDyn v0.1.0 and to the evidence snapshot dated 2026-06-30.",
        ),
        (
            "RhoDyn v0.1.0 was the software boundary used for the Methods evidence surface.",
            "RhoDyn v0.1.0 defines the software boundary for the analyses reported here.",
        ),
    ],
    FIGURES_DIR / "figure_legends.md": [
        (
            "Panels expand the main method-object figure with tidy trajectory and endpoint schemas, residence-window metric definitions, executable positive and negative truth cases, and boundary examples where the supplied input does not support interpretation.",
            "Expanded method-object panels place tidy trajectory and endpoint schemas, residence-window metric definitions, executable positive and negative truth cases, and boundary examples next to the main display.",
        ),
        (
            "Panels provide the known-truth benchmark grid, residence-versus-amplitude comparisons, reduced-summary comparisons, and negative or ambiguous cases that sit behind the compressed synthetic benchmark figure.",
            "The known-truth benchmark grid, residence-versus-amplitude comparisons, reduced-summary comparisons, and negative or ambiguous cases provide the detailed support for the synthetic benchmark display.",
        ),
        (
            "Panels document the public-data adapter contract, DRG calcium and ERK GPCR residence-amplitude summaries, and the window or uncertainty sensitivity analyses used to scope the public reporter demonstrations.",
            "Public-data adapter panels document the DRG calcium and ERK GPCR residence-amplitude summaries and the window or uncertainty sensitivity analyses used to scope the public reporter demonstrations.",
        ),
        (
            "Panels show the endpoint pairing contract, declared margin table, bounded-coupling interval display, and inconclusive decision examples used to keep coupling claims tied to the stated margin and context.",
            "Endpoint-pairing panels show the declared margin table, bounded-coupling interval display, and inconclusive decision examples that keep coupling claims tied to the stated margin and context.",
        ),
        (
            "Panels separate measured endpoint components, the reserve-like coordinate construction, uncertainty summaries, and label-scope boundaries so that buffering language remains tied to the measured assay.",
            "Measured endpoint panels separate reserve-like coordinate construction, uncertainty summaries, and label-scope boundaries so that buffering language remains tied to the assay.",
        ),
        (
            "Panels provide the routed architecture matrix, reduced-alternative comparison, residual profile, and decision-boundary table behind the endpoint model-comparison display.",
            "The routed-output supplement provides the architecture matrix, reduced-alternative comparison, residual profile, and decision-boundary table behind the endpoint model-comparison display.",
        ),
        (
            "Panels show the fixed held-out plan, pass contexts, margin-boundary inconclusive contexts, margin sensitivity, and controlled-access notes that prevent held-out validation from becoming a single unqualified score.",
            "Held-out validation panels show the fixed analysis plan, pass contexts, margin-boundary inconclusive contexts, margin sensitivity, and controlled-access notes that prevent validation from becoming a single unqualified score.",
        ),
        (
            "Panels document cross-surface parity, export-bundle contents, clean-room reproduction summaries, archive records, checksums, and usability-path boundaries for the retained evidence surfaces.",
            "Cross-surface reproducibility panels document parity, export-bundle contents, clean-room reproduction summaries, archive records, checksums, and usability-path boundaries for the retained evidence surfaces.",
        ),
        (
            "Panels collect non-example cases, ambiguous regimes, claim-strength caps, and recommended wording boundaries so that limitations remain visible without carrying the main argument.",
            "Non-example panels collect ambiguous regimes, claim-strength caps, and recommended wording boundaries so that limitations remain visible without carrying the main argument.",
        ),
    ],
}

FINAL_PHRASES = {
    SECTIONS_DIR / "introduction.md": [
        "explicit checks that allow each component to be tested in sequence",
    ],
    SECTIONS_DIR / "results.md": [
        "The held-out analysis therefore keeps pass and inconclusive outcomes side by side",
        "A reusable method also needs to remain inspectable",
        "rather than merely available as code",
    ],
    SECTIONS_DIR / "discussion.md": [
        "method contribution beyond the motivating RhoA/microglia reference use case",
        "decision outcome are declared before interpretation",
        "Reproducibility evidence strengthens the method",
    ],
    SECTIONS_DIR / "methods.md": [
        "Methods section refer to RhoDyn v0.1.0",
        "defines the software boundary for the analyses reported here",
    ],
    FIGURES_DIR / "figure_legends.md": [
        "Expanded method-object panels place tidy trajectory",
        "Non-example panels collect ambiguous regimes",
    ],
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


def _strip_comments(text: str) -> str:
    return re.sub(r"<!--.*?-->", "", text, flags=re.S)


def _para_ids(text: str) -> list[str]:
    return sorted(set(re.findall(r"PARA-[A-Z]+-\d{3}", text)))


def _claim_ids(text: str) -> list[str]:
    return sorted(set(re.findall(r"CLM-\d{4}", text)))


def _figure_calls(text: str) -> list[str]:
    visible = _strip_comments(text)
    return re.findall(r"\((?:Fig\.|Supplementary Fig\.|Supplementary Table)[^)]+\)", visible)


def _terminal_figure_calls(text: str) -> list[str]:
    visible = _strip_comments(text)
    return re.findall(r"[^.!?]*\((?:Fig\.|Supplementary Fig\.|Supplementary Table)[^)]+\)\.", visible)


def _sentence_starts(text: str) -> Counter[str]:
    visible = _strip_comments(text)
    starts: Counter[str] = Counter()
    for sentence in re.split(r"(?<=[.!?])\s+", visible):
        sentence = sentence.strip()
        if not sentence or sentence.startswith("#"):
            continue
        match = re.match(r"([A-Z][A-Za-z']+)", sentence)
        if match:
            starts[match.group(1)] += 1
    return starts


def _max_paragraph_words(text: str) -> int:
    visible = _strip_comments(text)
    paragraphs = [p.strip() for p in visible.split("\n\n") if p.strip() and not p.lstrip().startswith("#")]
    return max((len(re.findall(r"\b\w+\b", paragraph)) for paragraph in paragraphs), default=0)


def _max_consecutive_sentence_start(text: str) -> int:
    visible = _strip_comments(text)
    starts: list[str] = []
    for sentence in re.split(r"(?<=[.!?])\s+", visible):
        sentence = sentence.strip()
        if not sentence or sentence.startswith("#"):
            continue
        match = re.match(r"([A-Z][A-Za-z']+)", sentence)
        if match:
            starts.append(match.group(1))
    longest = 0
    current = 0
    previous = None
    for start in starts:
        current = current + 1 if start == previous else 1
        longest = max(longest, current)
        previous = start
    return longest


def _apply_replacements(text: str, replacements: list[tuple[str, str]]) -> tuple[str, list[str]]:
    applied: list[str] = []
    for index, (old, new) in enumerate(replacements, start=1):
        if old in text:
            text = text.replace(old, new)
            applied.append(f"replacement_{index}")
        elif new in text:
            applied.append(f"replacement_{index}_already_present")
    return text, applied


def _build_polished_surfaces() -> tuple[dict[Path, str], dict[str, list[str]]]:
    polished: dict[Path, str] = {}
    applied: dict[str, list[str]] = {}
    for path in SURFACE_PATHS:
        text = path.read_text(encoding="utf-8")
        if path in REPLACEMENTS:
            text, applied_items = _apply_replacements(text, REPLACEMENTS[path])
            applied[path.relative_to(ROOT).as_posix()] = applied_items
        polished[path] = text
    return polished, applied


def _audit_surfaces(before: dict[Path, str], after: dict[Path, str], applied: dict[str, list[str]]) -> dict[str, Any]:
    gate_924 = _read_json(GATE_924) if GATE_924.exists() else {}
    paragraph_errors: list[str] = []
    claim_id_errors: list[str] = []
    figure_call_errors: list[str] = []
    for path in [SECTIONS_DIR / "introduction.md", SECTIONS_DIR / "results.md", SECTIONS_DIR / "discussion.md", SECTIONS_DIR / "methods.md"]:
        if _para_ids(before[path]) != _para_ids(after[path]):
            paragraph_errors.append(path.relative_to(ROOT).as_posix())
        if _claim_ids(before[path]) != _claim_ids(after[path]):
            claim_id_errors.append(path.relative_to(ROOT).as_posix())
    for path in [SECTIONS_DIR / "results.md", FIGURES_DIR / "figure_legends.md"]:
        if _figure_calls(before[path]) != _figure_calls(after[path]):
            figure_call_errors.append(path.relative_to(ROOT).as_posix())

    combined_visible = "\n\n".join(_strip_comments(text) for text in after.values())
    unsafe_hits = [phrase for phrase in UNSAFE_PHRASES if phrase.lower() in combined_visible.lower()]
    missing_limits = [term for term in REQUIRED_LIMIT_TERMS if term.lower() not in combined_visible.lower()]
    process_hits = [phrase for phrase in PROCESS_PHRASES if phrase.lower() in combined_visible.lower()]
    reader_stage_hits = [
        path.relative_to(ROOT).as_posix()
        for path, text in after.items()
        if "Stage 9" in _strip_comments(text) or "stage9" in _strip_comments(text)
    ]
    terminal_calls = {
        path.relative_to(ROOT).as_posix(): _terminal_figure_calls(text)
        for path, text in after.items()
        if _terminal_figure_calls(text)
    }
    final_phrase_missing = {
        path.relative_to(ROOT).as_posix(): [
            f"final_phrase_{index}"
            for index, phrase in enumerate(FINAL_PHRASES.get(path, []), start=1)
            if phrase not in after[path]
        ]
        for path in SURFACE_PATHS
    }
    final_phrase_missing = {path: missing for path, missing in final_phrase_missing.items() if missing}
    starts = {path.relative_to(ROOT).as_posix(): dict(_sentence_starts(text).most_common(6)) for path, text in after.items()}
    max_words = {path.relative_to(ROOT).as_posix(): _max_paragraph_words(text) for path, text in after.items()}
    max_repeated_starts = {
        path.relative_to(ROOT).as_posix(): _max_consecutive_sentence_start(text)
        for path, text in after.items()
    }
    style_errors: list[str] = []
    for path, words in max_words.items():
        if words > 170:
            style_errors.append(f"{path}:max_paragraph_words={words}")
    for path, count in max_repeated_starts.items():
        if count > 3:
            style_errors.append(f"{path}:max_repeated_sentence_start={count}")
    legend_visible = _strip_comments(after[FIGURES_DIR / "figure_legends.md"])
    if len(re.findall(r"\bPanels\b", legend_visible)) > 0:
        style_errors.append("figure_legends:remaining_Panels_sentence_start")
    downstream_paths = [path.relative_to(ROOT).as_posix() for path in FORBIDDEN_DOWNSTREAM_PATHS if path.exists()]

    checks = [
        {
            "name": "stage_9_24_gate_passed",
            "passed": gate_924.get("pass") is True and gate_924.get("next_substage") == "9.25",
            "detail": "Stage 9.24 editorial polish pass I gate is present and points to Stage 9.25",
        },
        {
            "name": "meaning_preserved",
            "passed": not paragraph_errors and not claim_id_errors and not figure_call_errors,
            "detail": f"paragraph_errors={paragraph_errors}; claim_id_errors={claim_id_errors}; figure_call_errors={figure_call_errors}",
        },
        {
            "name": "style_metrics_pass_thresholds",
            "passed": not style_errors,
            "detail": f"style_errors={style_errors}",
        },
        {
            "name": "no_claim_broadened",
            "passed": not unsafe_hits and not missing_limits,
            "detail": f"unsafe_hits={unsafe_hits}; missing_limit_terms={missing_limits}",
        },
        {
            "name": "venue_style_replacements_resolved",
            "passed": not final_phrase_missing and not process_hits,
            "detail": f"final_phrase_missing={final_phrase_missing}; process_hits={process_hits}",
        },
        {
            "name": "dynamic_figure_call_flow_preserved",
            "passed": not terminal_calls,
            "detail": f"terminal_figure_calls={terminal_calls}",
        },
        {
            "name": "reader_surface_stage_language_absent",
            "passed": not reader_stage_hits,
            "detail": f"reader_stage_hits={reader_stage_hits}",
        },
        {
            "name": "no_reader_hygiene_or_package_started",
            "passed": not downstream_paths,
            "detail": f"downstream_paths={downstream_paths}",
        },
    ]
    return {
        "generated_utc": _now(),
        "commit": _git_sha(),
        "checks": checks,
        "replacement_applied": applied,
        "paragraph_errors": paragraph_errors,
        "claim_id_errors": claim_id_errors,
        "figure_call_errors": figure_call_errors,
        "style_errors": style_errors,
        "unsafe_hits": unsafe_hits,
        "missing_limits": missing_limits,
        "process_hits": process_hits,
        "terminal_calls": terminal_calls,
        "reader_stage_hits": reader_stage_hits,
        "downstream_paths": downstream_paths,
        "sentence_starts": starts,
        "max_paragraph_words": max_words,
        "max_repeated_sentence_starts": max_repeated_starts,
        "recursive_rounds": [
            {"round": 1, "focus": "venue-style process phrase removal", "status": "pass" if not process_hits else "fail"},
            {"round": 2, "focus": "paragraph rhythm and repeated-start thresholds", "status": "pass" if not style_errors else "fail"},
            {"round": 3, "focus": "meaning, claim-strength, and limitation retention", "status": "pass" if not unsafe_hits and not missing_limits and not paragraph_errors and not claim_id_errors else "fail"},
            {"round": 4, "focus": "figure-call flow and downstream-boundary check", "status": "pass" if not terminal_calls and not downstream_paths else "fail"},
        ],
    }


def _audit_text(analysis: dict[str, Any]) -> str:
    checks_rows = "\n".join(
        f"| {item['name']} | {'pass' if item['passed'] else 'fail'} | {item['detail']} |"
        for item in analysis["checks"]
    )
    starts_rows = "\n".join(
        f"| {path} | {starts} | {analysis['max_paragraph_words'][path]} | {analysis['max_repeated_sentence_starts'][path]} |"
        for path, starts in analysis["sentence_starts"].items()
    )
    replacement_rows = "\n".join(
        f"| {path} | {', '.join(items) if items else 'already at final style'} |"
        for path, items in analysis["replacement_applied"].items()
    )
    rounds_rows = "\n".join(
        f"| {item['round']} | {item['focus']} | {item['status']} |" for item in analysis["recursive_rounds"]
    )
    return f"""<!-- EDITORIAL-PASS-2 stage=9.25 generated={analysis['generated_utc']} commit={analysis['commit']} -->
# Stage 9.25 editorial polish pass II

Stage 9.25 performs the second reader-facing polish loop after editorial polish pass I. The pass removes residual process-like phrasing, tightens venue-style readability, varies supplementary-legend openings, and preserves the current evidence boundaries. It does not change statistics, figures, source data, model outputs, figure numbering, or method claims.

## Summary

The second editorial polish pass completed four recursive checks. Paragraph IDs, claim IDs, and Results figure calls were preserved. Paragraph lengths and repeated-start metrics remained within threshold. Claim-strength caps and limitation language stayed present, and no reader-surface hygiene gate, peer-review simulation, PI packet, readiness checklist, or final package assembly was started.

## Recursive polish rounds

| Round | Focus | Status |
|---|---|---|
{rounds_rows}

## Gate checks

| Check | Status | Detail |
|---|---|---|
{checks_rows}

## Style metrics

| Surface | Most common sentence starts | Maximum paragraph words | Maximum repeated sentence start |
|---|---|---:|---:|
{starts_rows}

## Replacements applied

| Surface | Replacement status |
|---|---|
{replacement_rows}

## Scope boundary

This stage modifies reader-facing prose for venue-style flow only. It does not broaden the residence, bounded-coupling, reserve-like, routed-output, or reproducibility claims. It keeps inconclusive outcomes visible and preserves the distinction between demonstrated software reproducibility and new biological evidence.
"""


def _gate_payload(analysis: dict[str, Any]) -> dict[str, Any]:
    return {
        "substage": "9.25",
        "title": "Editorial polish pass II",
        "generated_utc": analysis["generated_utc"],
        "commit": analysis["commit"],
        "pass": all(item["passed"] for item in analysis["checks"]),
        "checks": analysis["checks"],
        "paragraph_errors": analysis["paragraph_errors"],
        "claim_id_errors": analysis["claim_id_errors"],
        "figure_call_errors": analysis["figure_call_errors"],
        "style_errors": analysis["style_errors"],
        "unsafe_hits": analysis["unsafe_hits"],
        "missing_limits": analysis["missing_limits"],
        "process_hits": analysis["process_hits"],
        "terminal_calls": analysis["terminal_calls"],
        "reader_stage_hits": analysis["reader_stage_hits"],
        "downstream_paths": analysis["downstream_paths"],
        "recursive_rounds": analysis["recursive_rounds"],
        "outputs": [
            "manuscript/nature_methods/audits/editorial_pass_2.md",
            "manuscript/nature_methods/gate_verdicts/9.25.json",
            "manuscript/nature_methods/sections/introduction.md",
            "manuscript/nature_methods/sections/results.md",
            "manuscript/nature_methods/sections/discussion.md",
            "manuscript/nature_methods/sections/methods.md",
            "manuscript/nature_methods/figures/figure_legends.md",
        ],
        "scope_boundary": "Editorial polish pass II only. No new evidence, analyses, statistics, model outputs, figures, figure numbering, claim expansion, reader-surface hygiene report, PI packet, readiness checklist, or final package assembly.",
        "next_substage": "9.25b",
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
    for path in [*SURFACE_PATHS, *OUTPUTS.values()]:
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
        if substage.get("id") == "9.25":
            substage["status"] = "complete_editorial_polish_pass_2_bound"
    registry["last_completed_substage"] = "9.25"
    registry["next_substage"] = "9.25b"
    _write_json(REGISTRY_PATH, registry)


def _upsert_completed_substage(memory: dict[str, Any], checks: list[dict[str, Any]]) -> None:
    record = {
        "substage": "9.25",
        "status": "pass",
        "pass": True,
        "gate_verdict_path": "manuscript/nature_methods/gate_verdicts/9.25.json",
        "validation_outcome": "Venue-style readability polish completed without changing evidence bindings",
        "evidence_dependencies": [
            "manuscript/nature_methods/gate_verdicts/9.24.json",
            "manuscript/nature_methods/ledgers/claim_strength_rules.md",
            "manuscript/nature_methods/ledgers/non_claims_and_scope_boundaries.md",
            "manuscript/nature_methods/sections/introduction.md",
            "manuscript/nature_methods/sections/results.md",
            "manuscript/nature_methods/sections/discussion.md",
            "manuscript/nature_methods/sections/methods.md",
            "manuscript/nature_methods/figures/figure_legends.md",
        ],
        "files_created_or_modified": [
            "manuscript/nature_methods/audits/editorial_pass_2.md",
            "manuscript/nature_methods/gate_verdicts/9.25.json",
            "manuscript/nature_methods/sections/introduction.md",
            "manuscript/nature_methods/sections/results.md",
            "manuscript/nature_methods/sections/discussion.md",
            "manuscript/nature_methods/sections/methods.md",
            "manuscript/nature_methods/figures/figure_legends.md",
        ],
        "remaining_blockers": [
            "Reader-surface hygiene gate remains downstream",
            "Internal peer-review simulation has not started",
            "Full submission-package assembly has not started beyond the Reporting Summary requirement placeholder",
        ],
        "checks": checks,
    }
    entries = [item for item in memory.get("completed_substages", []) if item.get("substage") != "9.25"]
    entries.append(record)
    memory["completed_substages"] = entries


def _update_stage9_memory(generated_utc: str, checks: list[dict[str, Any]]) -> None:
    memory = _read_json(MEMORY_PATH)
    memory["generated_utc"] = generated_utc
    memory["current_substage"] = "9.25"
    memory["editorial_polish_pass_2_started"] = True
    memory["status"] = "stage9_25_editorial_polish_pass_2_bound"
    memory["current_gate"] = "Stage 9.25 editorial polish pass II preserved meaning and tightened venue style"
    memory["next_substage"] = "9.25b"
    memory["next_substage_authorized"] = False
    memory["stage9_active_gate"] = "Stage 9.25 Editorial polish pass II complete; reader-surface hygiene not started"
    memory["stage9_25_checks"] = checks
    artifacts = memory.setdefault("artifacts", [])
    for artifact in [
        "manuscript/nature_methods/audits/editorial_pass_2.md",
        "manuscript/nature_methods/gate_verdicts/9.25.json",
    ]:
        if artifact not in artifacts:
            artifacts.append(artifact)
    memory["gate"] = [
        "Stage 9.-1 contract and schema files exist and pass the scaffold checker.",
        "Stage 9.0 through Stage 9.25 are complete through editorial polish pass II.",
        "Stage 9.25b and Stage 9.26 through Stage 9.29 remain not started.",
        "No reader-surface hygiene report, internal peer-review simulation, PI review packet, or submission readiness checklist is created in this pass.",
        "Meaning, claim-strength caps, limitations, and Results figure-call order remain intact.",
    ]
    memory["scope_rule"] = (
        "Stage 9 has completed evidence intake, venue-guidance registration, representative methods-paper corpus analysis, "
        "narrative-spine selection, claim freeze, paragraph-level claim planning, main figure-spine planning, deterministic "
        "PanelForge rendering, supplementary display planning, section-contract planning, title/abstract strategy, Results "
        "architecture, Results drafting, Introduction literature binding, Discussion interpretation mapping, Discussion drafting, "
        "Methods architecture, Methods drafting, availability assembly, Supplementary Methods drafting, supplementary table/source-data "
        "binding, reference-library/citation audit, cross-document consistency audit, statistical/quantitative language audit, "
        "figure legend/caption audit, and editorial polish passes I and II only. Do not start reader-surface hygiene, internal peer review, "
        "or final submission package without explicit substage authorization."
    )
    _upsert_completed_substage(memory, checks)
    _write_json(MEMORY_PATH, memory)


def _update_roadmap_memory() -> None:
    memory = _read_json(ROADMAP_MEMORY_PATH)
    current = memory.setdefault("current_position", {})
    current["active_stage"] = "Stage 9.25 Editorial polish pass II complete; reader-surface hygiene not started"
    current["stage9_active_gate"] = "Stage 9.25 Editorial polish pass II complete; reader-surface hygiene not started"
    current["after_stage9_25_editorial_polish_pass_2"] = (
        "Stage 9.25 tightened venue-style readability, removed residual process-like phrasing, varied supplementary-legend openings, "
        "and preserved paragraph IDs, claim IDs, Results figure calls, limitations, statistics, figures, and evidence bindings. "
        "It did not start the reader-surface hygiene gate, peer-review simulation, or final package assembly."
    )
    current["current_gate"] = "Editorial polish pass II completed without evidence-layer changes"
    current["next_stage"] = "Stage 9.25b Reader-surface hygiene gate"
    for stage in memory.get("stage_lock", []):
        if not isinstance(stage, dict) or stage.get("stage") != 9:
            continue
        stage["status"] = "stage9_25_editorial_polish_pass_2_bound"
        stage["current_gate"] = "Stage 9.25 polish preserved meaning and tightened venue-style readability"
        stage["scope_rule"] = (
            "Stage 9 has completed evidence intake, venue-guidance registration, representative methods-paper corpus analysis, "
            "narrative-spine selection, claim freeze, paragraph-level claim planning, main figure-spine planning, deterministic "
            "PanelForge rendering, supplementary display planning, section-contract planning, front-matter strategy, Results architecture, "
            "Results drafting, Introduction literature binding, Discussion interpretation mapping, Discussion drafting, Methods architecture, "
            "Methods drafting, availability assembly, Supplementary Methods drafting, supplementary table/source-data binding, reference-library/citation audit, "
            "cross-document consistency audit, statistical-language audit, figure legend/caption audit, and editorial polish passes I and II only. "
            "Do not start reader-surface hygiene, internal peer review, or final submission packaging without explicit substage authorization."
        )
        artifacts = stage.setdefault("artifacts", [])
        for artifact in [
            "manuscript/nature_methods/audits/editorial_pass_2.md",
            "manuscript/nature_methods/gate_verdicts/9.25.json",
            "scripts/run_stage9_25_editorial_polish_pass2.py",
        ]:
            if artifact not in artifacts:
                artifacts.append(artifact)
        gate = stage.setdefault("gate", [])
        polish_gate = "Stage 9.25 tightened venue-style readability while preserving meaning, figure-call order, and claim boundaries."
        if polish_gate not in gate:
            gate.append(polish_gate)
        for subphase in stage.get("subphases", []):
            if isinstance(subphase, dict) and subphase.get("id") == "9.25":
                subphase["status"] = "complete_editorial_polish_pass_2_bound"
                subphase["evidence"] = "manuscript/nature_methods/gate_verdicts/9.25.json"
    _write_json(ROADMAP_MEMORY_PATH, memory)


def _replace_once(body: str, old: str, new: str) -> str:
    return body.replace(old, new) if old in body else body


def _update_docs() -> None:
    README_PATH.write_text(
        """# Nature Methods manuscript workspace

This directory is the Stage 9 manuscript-assembly workspace for RhoDyn.

Current status. Stage 9.25 editorial polish pass II complete.

The workspace now contains the authorized manuscript components through the second editorial polish pass. Evidence intake, venue guidance, methods-paper corpus analysis, narrative spine, claim freeze, paragraph planning, figure planning, deterministic main-figure rendering, supplementary display planning, section contracts, front matter, Results, Introduction, Discussion, Methods, availability statements, Supplementary Methods, supplementary table/source-data binding, reference audit, cross-document consistency audit, statistical-language audit, figure legend/caption audit, and editorial polish passes I and II are present.

The next unstarted step is Stage 9.25b reader-surface hygiene gate. Final manuscript assembly, PI review packet, submission-readiness checklist, internal peer-review simulation, and final package assembly have not started.

PanelForge figure rendering has already been exercised through the authorized Stage 9.6b deterministic rendering lane. The placeholder under `tools/panelforge-figures/` is not a clone, `.venv-panelforge` is not created by this workspace, and no local figure-engine repository is vendored here.
""",
        encoding="utf-8",
    )
    if PLAN_PATH.exists():
        body = PLAN_PATH.read_text(encoding="utf-8")
        body = _replace_once(
            body,
            "Stage 9.24 registers `audits/editorial_pass_1.md` and `gate_verdicts/9.24.json`, and polishes section and legend cadence without changing evidence bindings. The current state intentionally does not create editorial-polish pass II, reader-surface hygiene, or full submission-package files.",
            "Stage 9.24 registers `audits/editorial_pass_1.md` and `gate_verdicts/9.24.json`, and polishes section and legend cadence without changing evidence bindings. Stage 9.25 registers `audits/editorial_pass_2.md` and `gate_verdicts/9.25.json`, and tightens venue-style readability without changing evidence bindings. The current state intentionally does not create the reader-surface hygiene gate, internal peer-review simulation, or full submission-package files.",
        )
        body = _replace_once(
            body,
            "| 9.25 | Editorial polish pass II | not_started | Tune venue style and readability without broadening claims. |",
            "| 9.25 | Editorial polish pass II | complete_editorial_polish_pass_2_bound | Tune venue style and readability without broadening claims. |",
        )
        PLAN_PATH.write_text(body, encoding="utf-8")
    if ROADMAP_PATH.exists():
        body = ROADMAP_PATH.read_text(encoding="utf-8")
        body = _replace_once(
            body,
            "and table captions, and Stage 9.24 has completed editorial polish pass I.\nEditorial polish pass II, reader-surface hygiene, and final package assembly\nremain not started.",
            "and table captions, Stage 9.24 has completed editorial polish pass I,\nand Stage 9.25 has completed editorial polish pass II. Reader-surface\nhygiene, internal peer review, and final package assembly remain not started.",
        )
        body = _replace_once(
            body,
            "| Stage 9. Nature Methods manuscript assembly | Stage 9.24 Editorial polish pass I complete, editorial polish pass II not started. | The current boundary is evidence intake, official venue-guidance registration, representative methods-paper corpus analysis, narrative-spine selection, claim freeze, paragraph-level claim planning, main figure-spine planning, deterministic PanelForge rendering, supplementary display planning, section-contract planning, front-matter strategy, Results architecture, Results drafting, Introduction literature binding, Discussion interpretation mapping, Discussion drafting, Methods architecture, Methods drafting, availability assembly, Supplementary Methods drafting, supplementary table/source-data binding, reference-library/citation audit, cross-document consistency audit, statistical-language audit, figure legend/caption audit, and editorial polish pass I only. Do not start editorial polish pass II, reader-surface hygiene, review response, or final submission packaging without explicit substage authorization. |",
            "| Stage 9. Nature Methods manuscript assembly | Stage 9.25 Editorial polish pass II complete, reader-surface hygiene not started. | The current boundary is evidence intake, official venue-guidance registration, representative methods-paper corpus analysis, narrative-spine selection, claim freeze, paragraph-level claim planning, main figure-spine planning, deterministic PanelForge rendering, supplementary display planning, section-contract planning, front-matter strategy, Results architecture, Results drafting, Introduction literature binding, Discussion interpretation mapping, Discussion drafting, Methods architecture, Methods drafting, availability assembly, Supplementary Methods drafting, supplementary table/source-data binding, reference-library/citation audit, cross-document consistency audit, statistical-language audit, figure legend/caption audit, and editorial polish passes I and II only. Do not start reader-surface hygiene, internal peer review, review response, or final submission packaging without explicit substage authorization. |",
        )
        body = _replace_once(
            body,
            "Stage 9.10 Results subsection architecture has been completed. Stage 9.11 Results drafting pass has been completed. Stage 9.12 Introduction literature binding has been completed. Stage 9.13 Discussion interpretation map has been completed. Stage 9.14 Discussion drafting pass has been completed. Stage 9.15 Methods architecture has been completed. Stage 9.16 Methods drafting pass has been completed. Stage 9.17 software, data, and code availability assembly has been completed. Stage 9.18 Supplementary Methods drafting has been completed. Stage 9.19 Supplementary tables and source-data binding has been completed. Stage 9.20 Reference library and citation audit has been completed. Stage 9.21 Cross-document consistency audit has been completed. Stage 9.22 Statistical and quantitative language audit has been completed. Stage 9.23 Figure legend and caption audit has been completed. Stage 9.24 Editorial polish pass I has been completed. Stage 9.25 Editorial polish pass II remains the next unstarted manuscript step. Final package assembly remains not started.",
            "Stage 9.10 Results subsection architecture has been completed. Stage 9.11 Results drafting pass has been completed. Stage 9.12 Introduction literature binding has been completed. Stage 9.13 Discussion interpretation map has been completed. Stage 9.14 Discussion drafting pass has been completed. Stage 9.15 Methods architecture has been completed. Stage 9.16 Methods drafting pass has been completed. Stage 9.17 software, data, and code availability assembly has been completed. Stage 9.18 Supplementary Methods drafting has been completed. Stage 9.19 Supplementary tables and source-data binding has been completed. Stage 9.20 Reference library and citation audit has been completed. Stage 9.21 Cross-document consistency audit has been completed. Stage 9.22 Statistical and quantitative language audit has been completed. Stage 9.23 Figure legend and caption audit has been completed. Stage 9.24 Editorial polish pass I has been completed. Stage 9.25 Editorial polish pass II has been completed. Stage 9.25b Reader-surface hygiene gate remains the next unstarted manuscript step. Final package assembly remains not started.",
        )
        ROADMAP_PATH.write_text(body, encoding="utf-8")


def run() -> dict[str, Any]:
    if STAGING_DIR.exists():
        shutil.rmtree(STAGING_DIR)
    STAGING_DIR.mkdir(parents=True, exist_ok=True)
    before = {path: path.read_text(encoding="utf-8") for path in SURFACE_PATHS}
    after, applied = _build_polished_surfaces()
    analysis = _audit_surfaces(before, after, applied)
    gate = _gate_payload(analysis)
    _stage_outputs(after, analysis, gate)
    if not gate["pass"]:
        quarantine = _quarantine_staging()
        return {
            "status": "failed",
            "substage": "9.25",
            "quarantine": quarantine.relative_to(ROOT).as_posix(),
            "checks": analysis["checks"],
            "next_substage": "9.25",
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
        "substage": "9.25",
        "outputs": [
            "manuscript/nature_methods/audits/editorial_pass_2.md",
            "manuscript/nature_methods/gate_verdicts/9.25.json",
        ],
        "checks": analysis["checks"],
        "next_substage": "9.25b",
    }


def main() -> int:
    result = run()
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] == "completed" else 1


if __name__ == "__main__":
    raise SystemExit(main())

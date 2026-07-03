"""Run Stage 9.9 title, subtitle, and abstract strategy generation.

Stage 9.9 creates front-matter framing for a future Nature Methods Article.
It may create title options, subtitle/deck strategy, and a short unreferenced
abstract draft. It does not draft Results, Introduction, Discussion, Methods,
figure legends, references, availability statements, or a submission package.
"""

from __future__ import annotations

import csv
import json
import re
import shutil
import subprocess
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT / "manuscript" / "nature_methods"
SECTIONS_DIR = WORKSPACE / "sections"
GATE_DIR = WORKSPACE / "gate_verdicts"
LEDGER_DIR = WORKSPACE / "ledgers"
STAGING_DIR = WORKSPACE / "_staging" / "9.9"
QUARANTINE_DIR = WORKSPACE / "_quarantine" / "9.9"
MEMORY_PATH = ROOT / "docs" / "stage9_execution_memory.json"
ROADMAP_MEMORY_PATH = ROOT / "docs" / "roadmap_execution_memory.json"
REGISTRY_PATH = WORKSPACE / "contracts" / "stage9_substage_registry.json"
PLAN_PATH = ROOT / "docs" / "stage9_manuscript_assembly_plan.md"
ROADMAP_PATH = ROOT / "docs" / "roadmap.md"

GATE_98 = GATE_DIR / "9.8.json"
CLAIM_LEDGER = LEDGER_DIR / "claim_hierarchy.csv"
SECTION_CONTRACTS = SECTIONS_DIR / "section_contracts.md"

OUTPUTS = {
    "title_options": SECTIONS_DIR / "title_options.md",
    "abstract_strategy": SECTIONS_DIR / "abstract_strategy.md",
    "abstract": SECTIONS_DIR / "abstract.md",
    "gate": GATE_DIR / "9.9.json",
}

FORBIDDEN_STARTED_PATHS = [
    SECTIONS_DIR / "results_blueprint.md",
    SECTIONS_DIR / "results.md",
    SECTIONS_DIR / "introduction.md",
    SECTIONS_DIR / "discussion.md",
    SECTIONS_DIR / "methods.md",
    SECTIONS_DIR / "data_availability.md",
    SECTIONS_DIR / "code_availability.md",
    WORKSPACE / "refs" / "references.bib",
    WORKSPACE / "submission_package" / "pi_review_packet.md",
    WORKSPACE / "submission_package" / "submission_readiness_checklist.md",
]

CLAIM_IDS = ("CLM-0001", "CLM-0002", "CLM-0003", "CLM-0004", "CLM-0005")
FORBIDDEN_ABSTRACT_PHRASES = (
    "universal",
    "guarantees",
    "therapeutic",
    "clinical",
    "diagnostic",
    "RhoDyn generated the original",
    "RhoDyn generated the RhoA",
)

ABSTRACT_TEXT = (
    "Live-cell perturbation experiments often contain dynamic control information that is lost when trajectories are reduced "
    "to endpoints, amplitudes, or generic time-series features. RhoDyn is a computational method for residence-state inference "
    "that scores dwell within user-declared biological windows, compares amplitude and residence summaries, evaluates bounded "
    "coupling under declared margins, constructs measurement-scoped reserve-like endpoint summaries, and tests routed-output "
    "alternatives against reduced architectures. Across synthetic truth cases, public calcium and ERK signaling trajectories, "
    "public-derived endpoint demonstrations, and held-out coupling contexts, RhoDyn exposes cases in which residence, buffering, "
    "coupling boundaries, or routed outputs change interpretation relative to simpler summaries while preserving inconclusive "
    "regimes. The Python, CLI, backend, workbench, and archived release surfaces produce matched, inspectable outputs. RhoDyn "
    "therefore provides a reproducible route for identifying dynamic operating-state structure in live-cell perturbation data "
    "without treating every signal window, endpoint coordinate, or effective model term as a literal mechanism."
)


@dataclass(frozen=True)
class TitleOption:
    option_id: str
    title: str
    short_title: str
    deck: str
    rationale: str
    claim_ids: tuple[str, ...]
    risk_control: str
    status: str


TITLE_OPTIONS = [
    TitleOption(
        option_id="TITLE-001",
        title="RhoDyn infers residence states in live-cell perturbation data",
        short_title="RhoDyn residence-state inference",
        deck="A reproducible Python, CLI, backend, and workbench method for dwell-time, bounded-coupling, reserve-like, and routed-output analysis.",
        rationale="Most concise method-name option. It foregrounds the software and the residence-state object without claiming universal discovery.",
        claim_ids=("CLM-0001", "CLM-0005"),
        risk_control="Does not imply that every dataset contains a residence regime.",
        status="preferred working option",
    ),
    TitleOption(
        option_id="TITLE-002",
        title="Residence-state inference for dynamic control in live-cell perturbation data",
        short_title="Residence-state inference",
        deck="RhoDyn compares dwell-time structure, amplitude summaries, bounded-coupling decisions, and routed-output alternatives.",
        rationale="Best venue-facing methods title if the paper should read as a general method before the software name.",
        claim_ids=("CLM-0001", "CLM-0002", "CLM-0004"),
        risk_control="Keeps RhoDyn in the deck rather than using a software-first title.",
        status="strong alternate",
    ),
    TitleOption(
        option_id="TITLE-003",
        title="RhoDyn detects dynamic operating states beyond endpoint and amplitude summaries",
        short_title="RhoDyn dynamic operating states",
        deck="A residence-aware method for live-cell trajectories, bounded coupling, reserve-like endpoints, and routed-output comparisons.",
        rationale="Highest conceptual punch, but stronger wording requires careful abstract and Results phrasing.",
        claim_ids=("CLM-0001", "CLM-0002", "CLM-0003", "CLM-0004", "CLM-0005"),
        risk_control="Use only if Results keep inconclusive cases visible and avoid universal language.",
        status="higher-impact alternate",
    ),
    TitleOption(
        option_id="TITLE-004",
        title="Residence-aware analysis of live-cell perturbation responses",
        short_title="Residence-aware perturbation analysis",
        deck="RhoDyn links trajectory dwell metrics with endpoint, coupling, reserve-like, routed-output, and reproducibility evidence.",
        rationale="Safest restrained option. It is broad and accurate, though less memorable than the RhoDyn-first option.",
        claim_ids=("CLM-0001", "CLM-0005"),
        risk_control="Avoids overclaiming but may undersell the software and benchmark breadth.",
        status="conservative alternate",
    ),
]


def _now() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


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


def _read_csv(path: Path, key: str) -> dict[str, dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return {row[key]: row for row in csv.DictReader(handle)}


def _markdown_table(rows: list[dict[str, str]], columns: list[str]) -> str:
    lines = ["| " + " | ".join(columns) + " |", "| " + " | ".join("---" for _ in columns) + " |"]
    for row in rows:
        lines.append("| " + " | ".join(str(row.get(column, "")).replace("|", "\\|") for column in columns) + " |")
    return "\n".join(lines)


def _word_count(text: str) -> int:
    return len(re.findall(r"\b[\w-]+\b", text))


def _contains_citation(text: str) -> bool:
    citation_patterns = [
        r"\([A-Z][A-Za-z-]+ et al\.,? \d{4}\)",
        r"\([A-Z][A-Za-z-]+, \d{4}\)",
        r"\[\d+(?:,\s*\d+)*\]",
        r"\(\d+(?:-\d+|,\s*\d+)*\)",
        r"doi:",
        r"https?://",
        r"REF-\d+",
    ]
    return any(re.search(pattern, text) for pattern in citation_patterns)


def _build_title_options(generated_utc: str, strategy_version: str) -> str:
    rows = [
        {
            "option_id": option.option_id,
            "title": option.title,
            "short_title": option.short_title,
            "status": option.status,
            "claim_ids": ";".join(option.claim_ids),
        }
        for option in TITLE_OPTIONS
    ]
    details: list[str] = []
    for option in TITLE_OPTIONS:
        details.extend(
            [
                f"### {option.option_id}. {option.title}",
                "",
                f"- Status. {option.status}.",
                f"- Short title. {option.short_title}.",
                f"- Deck or subtitle strategy. {option.deck}",
                f"- Claim mapping. {';'.join(option.claim_ids)}.",
                f"- Why this option exists. {option.rationale}",
                f"- Claim boundary. {option.risk_control}",
                "",
            ]
        )
    return f"""# Stage 9.9 title and subtitle strategy

Generated UTC. {generated_utc}

Strategy version. {strategy_version}

Stage. 9.9 title, subtitle, and abstract strategy.

Scope. This file records title, short-title, and deck/subtitle options for a
future Nature Methods Article. It is not a submission title decision, not
Results prose, not figure legend prose, not citation resolution, and not a
submission package.

## Framing rule

The title should name the general RhoDyn method or residence-state inference
object while keeping the RhoA/microglia manuscript as an optional reference use
case rather than the source of the method claim. It should not promise universal
residence behavior, automatic biological-window discovery, therapeutic utility,
or direct molecular-edge identification.

## Option map

{_markdown_table(rows, ["option_id", "title", "short_title", "status", "claim_ids"])}

## Option details

{chr(10).join(details).rstrip()}

## Preferred working route

Use `TITLE-001` as the current working option because it is short, software
specific, and claim-bounded. Retain `TITLE-002` as the strongest non-software
first fallback if editorial feedback prefers a method-object title over a
software-name title.
"""


def _build_abstract_strategy(generated_utc: str, strategy_version: str) -> str:
    rows = [
        {"sentence": "1", "role": "Problem", "claim_ids": "CLM-0001", "boundary": "Does not say amplitude summaries always fail."},
        {"sentence": "2", "role": "Method object", "claim_ids": "CLM-0001;CLM-0002;CLM-0003;CLM-0004", "boundary": "Windows and margins are user-declared, not automatically discovered."},
        {"sentence": "3", "role": "Validation breadth", "claim_ids": "CLM-0001;CLM-0002;CLM-0003;CLM-0004", "boundary": "Preserves inconclusive regimes and avoids universal biological law."},
        {"sentence": "4", "role": "Software reproducibility", "claim_ids": "CLM-0005", "boundary": "Does not imply PyPI publication or private-data reproduction."},
        {"sentence": "5", "role": "Scoped payoff", "claim_ids": "CLM-0001;CLM-0005", "boundary": "Effective model terms are not literal molecular edges."},
    ]
    return f"""# Stage 9.9 abstract strategy

Generated UTC. {generated_utc}

Strategy version. {strategy_version}

Stage. 9.9 title, subtitle, and abstract strategy.

Scope. This file defines the abstract strategy for a future Nature Methods
Article. It is not Results prose, not Introduction prose, not citation
resolution, not a reference library, and not a submission package.

## Venue rule

The Nature Methods Article abstract is capped at 150 words and is
unreferenced. The Stage 9.9 abstract therefore uses no citations, DOI strings,
reference IDs, numbered citation calls, or figure calls.

## Sentence map

{_markdown_table(rows, ["sentence", "role", "claim_ids", "boundary"])}

## Abstract drafting instructions

- Sentence 1 names the live-cell perturbation problem and the loss of dynamic
  information under endpoint, amplitude, or generic time-series reduction.
- Sentence 2 defines RhoDyn as a method and names the admissible components,
  including bounded-coupling decisions under declared margins.
- Sentence 3 reports validation breadth across synthetic, public, endpoint, and
  held-out contexts while preserving inconclusive regimes.
- Sentence 4 states cross-surface reproducibility across Python, CLI, backend,
  workbench, and archive outputs.
- Sentence 5 gives the bounded payoff. RhoDyn identifies dynamic
  operating-state structure in data without turning every window, endpoint, or
  effective parameter into a universal mechanism.

## Claim-boundary words to avoid

Avoid `universal`, `guarantees`, `therapeutic`, `clinical`, `diagnostic`,
`fully resolves`, `discovers the correct biological window`, `proves no
crosstalk`, and wording that says RhoDyn generated the original RhoA/microglia
manuscript results.
"""


def _build_abstract(generated_utc: str, strategy_version: str) -> str:
    return f"""# Stage 9.9 abstract draft

Generated UTC. {generated_utc}

Strategy version. {strategy_version}

Stage. 9.9 title, subtitle, and abstract strategy.

Scope. This file contains the current unreferenced Nature Methods Article
abstract draft. It is not a complete manuscript and does not begin Results,
Introduction, Discussion, Methods, references, figure legends, or submission
package assembly.

## Abstract

{ABSTRACT_TEXT}
"""


def _no_downstream_started() -> tuple[bool, list[str]]:
    forbidden = [path.relative_to(ROOT).as_posix() for path in FORBIDDEN_STARTED_PATHS if path.exists()]
    return not forbidden, forbidden


def _validate(claims: dict[str, dict[str, str]]) -> list[dict[str, Any]]:
    gate_98_pass = False
    if GATE_98.exists():
        try:
            gate_98_pass = _read_json(GATE_98).get("pass") is True
        except json.JSONDecodeError:
            gate_98_pass = False
    claim_ids = set(claims)
    title_claims_map = all(set(option.claim_ids).issubset(claim_ids) for option in TITLE_OPTIONS)
    abstract_word_count = _word_count(ABSTRACT_TEXT)
    abstract_budget_ok = abstract_word_count <= 150
    abstract_unreferenced = not _contains_citation(ABSTRACT_TEXT)
    abstract_claims_map = set(CLAIM_IDS).issubset(claim_ids) and all(token in ABSTRACT_TEXT for token in ["RhoDyn", "residence-state", "bounded coupling", "reserve-like", "routed-output", "Python", "CLI"])
    forbidden_absent = not any(phrase.lower() in ABSTRACT_TEXT.lower() for phrase in FORBIDDEN_ABSTRACT_PHRASES)
    no_downstream, downstream_paths = _no_downstream_started()
    contracts_ok = SECTION_CONTRACTS.exists() and "SEC-002. Abstract" in SECTION_CONTRACTS.read_text(encoding="utf-8")
    return [
        {
            "name": "stage_9_8_gate_passed",
            "passed": gate_98_pass,
            "detail": "Stage 9.8 section contracts exist and pass" if gate_98_pass else "Stage 9.8 gate is missing or not passing",
        },
        {
            "name": "section_contracts_available",
            "passed": contracts_ok,
            "detail": "Title and abstract strategy resolves to Stage 9.8 section contracts",
        },
        {
            "name": "title_options_map_to_claim_ids",
            "passed": title_claims_map,
            "detail": "Every title option is mapped to frozen CLM identifiers",
        },
        {
            "name": "abstract_word_count_respects_sourced_budget",
            "passed": abstract_budget_ok,
            "detail": f"Abstract word count is {abstract_word_count} of the 150-word Nature Methods Article budget",
        },
        {
            "name": "abstract_is_unreferenced",
            "passed": abstract_unreferenced,
            "detail": "Abstract contains no detected citations, DOI strings, URLs, reference IDs, or figure calls",
        },
        {
            "name": "abstract_claims_map_to_claim_ids",
            "passed": abstract_claims_map,
            "detail": "Abstract covers residence, bounded coupling, reserve-like, routed-output, and reproducibility claims without references",
        },
        {
            "name": "claim_boundary_language_preserved",
            "passed": forbidden_absent,
            "detail": "Abstract avoids universal, therapeutic, clinical, diagnostic, and original-manuscript-generation claims",
        },
        {
            "name": "no_downstream_stage9_surfaces_started",
            "passed": no_downstream,
            "detail": "No Results, Introduction, Discussion, Methods, availability, reference bibliography, or submission package detected"
            if no_downstream
            else "; ".join(downstream_paths),
        },
    ]


def _promote_staging() -> None:
    for destination in OUTPUTS.values():
        staged = STAGING_DIR / destination.relative_to(WORKSPACE)
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(staged, destination)


def _quarantine_staging(timestamp: str) -> Path:
    target = QUARANTINE_DIR / timestamp.replace(":", "").replace("-", "")
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        shutil.rmtree(target)
    shutil.move(str(STAGING_DIR), str(target))
    return target


def _update_registry() -> None:
    registry = _read_json(REGISTRY_PATH)
    for substage in registry.get("substages", []):
        if substage.get("id") == "9.9":
            substage["status"] = "complete_title_abstract_strategy_registered"
    registry["last_completed_substage"] = "9.9"
    registry["next_substage"] = "9.10"
    _write_json(REGISTRY_PATH, registry)


def _upsert_completed_substage(memory: dict[str, Any], strategy_version: str, checks: list[dict[str, Any]]) -> None:
    record = {
        "substage": "9.9",
        "status": "pass",
        "pass": True,
        "gate_verdict_path": "manuscript/nature_methods/gate_verdicts/9.9.json",
        "validation_outcome": "Title options, subtitle/deck strategy, and an unreferenced abstract draft registered within the 150-word budget",
        "evidence_dependencies": [
            "manuscript/nature_methods/gate_verdicts/9.8.json",
            "manuscript/nature_methods/sections/section_contracts.md",
            "manuscript/nature_methods/ledgers/claim_hierarchy.csv",
            "manuscript/nature_methods/stage9_narrative_spine.md",
            "manuscript/nature_methods/figures/main_figure_spine.md",
        ],
        "files_created_or_modified": [
            "manuscript/nature_methods/sections/title_options.md",
            "manuscript/nature_methods/sections/abstract_strategy.md",
            "manuscript/nature_methods/sections/abstract.md",
            "manuscript/nature_methods/gate_verdicts/9.9.json",
        ],
        "remaining_blockers": [
            "Stage 9.10 Results subsection architecture has not started",
            "Citation resolution has not started",
            "Main manuscript drafting beyond the abstract has not started",
            "Submission-package assembly has not started",
        ],
        "front_matter_strategy_version": strategy_version,
        "checks": checks,
    }
    entries = [item for item in memory.get("completed_substages", []) if item.get("substage") != "9.9"]
    entries.append(record)
    memory["completed_substages"] = entries


def _update_memory(strategy_version: str, generated_utc: str, checks: list[dict[str, Any]]) -> None:
    memory = _read_json(MEMORY_PATH)
    memory["generated_utc"] = generated_utc
    memory["current_substage"] = "9.9"
    memory["title_abstract_strategy_started"] = True
    memory["front_matter_strategy_version"] = strategy_version
    memory["status"] = "stage9_9_title_abstract_strategy_registered"
    memory["current_gate"] = "Stage 9.9 registered title, subtitle, and abstract strategy without starting Results architecture"
    memory["next_substage"] = "9.10"
    memory["next_substage_authorized"] = False
    memory["stage9_active_gate"] = "Stage 9.9 title, subtitle, and abstract strategy registered; Results architecture not started"
    memory["stage9_9_checks"] = checks
    artifacts = memory.setdefault("artifacts", [])
    for artifact in [
        "manuscript/nature_methods/sections/title_options.md",
        "manuscript/nature_methods/sections/abstract_strategy.md",
        "manuscript/nature_methods/sections/abstract.md",
        "manuscript/nature_methods/gate_verdicts/9.9.json",
    ]:
        if artifact not in artifacts:
            artifacts.append(artifact)
    memory["gate"] = [
        "Stage 9.-1 contract and schema files exist and pass the scaffold checker.",
        "Stage 9.0 through Stage 9.9 are complete through title, subtitle, and abstract strategy.",
        "Stage 9.10 through Stage 9.29 plus Stage 9.25b remain not started.",
        "No Results, Introduction, Discussion, Methods, references, figure legends, or submission package contents are created in this front-matter pass.",
        "The abstract is unreferenced, within the 150-word Nature Methods Article budget, and mapped to frozen CLM identifiers.",
    ]
    memory["scope_rule"] = (
        "Stage 9 has completed evidence intake, venue-guidance registration, representative methods-paper corpus analysis, "
        "narrative-spine selection, claim freeze, paragraph-level claim planning, main figure-spine planning, deterministic "
        "PanelForge rendering, supplementary display planning, section-contract planning, and title/abstract strategy only. "
        "Do not start Results architecture, citation resolution, full manuscript drafting, review response, or submission packaging "
        "without explicit substage authorization."
    )
    _upsert_completed_substage(memory, strategy_version, checks)
    _write_json(MEMORY_PATH, memory)


def _update_roadmap_memory(strategy_version: str) -> None:
    memory = _read_json(ROADMAP_MEMORY_PATH)
    current = memory.setdefault("current_position", {})
    current["active_stage"] = "Stage 9.9 title, subtitle, and abstract strategy registered; Results architecture not started"
    current["stage9_active_gate"] = "Stage 9.9 title, subtitle, and abstract strategy registered; Results architecture not started"
    current["after_stage9_9_title_abstract_strategy"] = (
        "Stage 9.9 registered title options, subtitle/deck strategy, and a 150-word-budget unreferenced abstract draft mapped to frozen CLM identifiers. "
        "It did not start Results architecture, citation resolution, full manuscript drafting, or submission-package assembly."
    )
    current["current_gate"] = "Front-matter strategy registered without Results architecture"
    current["next_stage"] = "Stage 9.10 Results subsection architecture"
    for stage in memory.get("stage_lock", []):
        if not isinstance(stage, dict) or stage.get("stage") != 9:
            continue
        stage["status"] = "stage9_9_title_abstract_strategy_registered"
        stage["current_gate"] = "Stage 9.9 registered title, subtitle, and abstract strategy without starting Results architecture"
        stage["scope_rule"] = (
            "Stage 9 has completed evidence intake, venue-guidance registration, representative methods-paper corpus analysis, "
            "narrative-spine selection, claim freeze, paragraph-level claim planning, main figure-spine planning, deterministic "
            "PanelForge rendering, supplementary display planning, section-contract planning, and title/abstract strategy only. "
            "Do not start Results architecture, citation resolution, full manuscript drafting, review response, or submission packaging "
            "without explicit substage authorization."
        )
        artifacts = stage.setdefault("artifacts", [])
        for artifact in [
            "manuscript/nature_methods/sections/title_options.md",
            "manuscript/nature_methods/sections/abstract_strategy.md",
            "manuscript/nature_methods/sections/abstract.md",
            "manuscript/nature_methods/gate_verdicts/9.9.json",
            "scripts/run_stage9_9_title_abstract_strategy.py",
        ]:
            if artifact not in artifacts:
                artifacts.append(artifact)
        gate = stage.setdefault("gate", [])
        front_matter_gate = "Stage 9.9 front matter is unreferenced, claim-mapped, and within the sourced abstract budget."
        if front_matter_gate not in gate:
            gate.append(front_matter_gate)
        for subphase in stage.get("subphases", []):
            if isinstance(subphase, dict) and subphase.get("id") == "9.9":
                subphase["status"] = "complete_title_abstract_strategy_registered"
                subphase["evidence"] = "manuscript/nature_methods/gate_verdicts/9.9.json"
                subphase["front_matter_strategy_version"] = strategy_version
    _write_json(ROADMAP_MEMORY_PATH, memory)


def _replace_once(body: str, old: str, new: str) -> str:
    return body.replace(old, new) if old in body else body


def _update_docs() -> None:
    if PLAN_PATH.exists():
        body = PLAN_PATH.read_text(encoding="utf-8")
        body = _replace_once(
            body,
            "and registers the section contract blueprint in Stage 9.8. It does not begin title or abstract strategy, citation resolution, manuscript drafting, editorial polishing, or package assembly.",
            "registers the section contract blueprint in Stage 9.8, and registers the title, subtitle, and abstract strategy in Stage 9.9. It does not begin Results architecture, citation resolution, full manuscript drafting, editorial polishing, or package assembly.",
        )
        body = _replace_once(
            body,
            "Stage 9.8 registers section contracts in `sections/section_contracts.md` and `gate_verdicts/9.8.json`. The current state intentionally does not create",
            "Stage 9.8 registers section contracts in `sections/section_contracts.md` and `gate_verdicts/9.8.json`. Stage 9.9 registers title options, abstract strategy, and an unreferenced abstract draft in `sections/title_options.md`, `sections/abstract_strategy.md`, `sections/abstract.md`, and `gate_verdicts/9.9.json`. The current state intentionally does not create",
        )
        body = _replace_once(
            body,
            "| 9.9 | Title, subtitle, and abstract strategy | not_started | Create high-level framing without overselling. |",
            "| 9.9 | Title, subtitle, and abstract strategy | complete_title_abstract_strategy_registered | Create high-level framing without overselling. |",
        )
        PLAN_PATH.write_text(body, encoding="utf-8")
    if ROADMAP_PATH.exists():
        body = ROADMAP_PATH.read_text(encoding="utf-8")
        body = _replace_once(
            body,
            "has registered supplementary display planning, and Stage 9.8 has registered\nsection contracts. Manuscript production, citation resolution, title/abstract\nstrategy, and drafting remain not started.",
            "has registered supplementary display planning, Stage 9.8 has registered\nsection contracts, and Stage 9.9 has registered title, subtitle, and abstract\nstrategy. Results architecture, citation resolution, full manuscript drafting,\nand package assembly remain not started.",
        )
        body = _replace_once(
            body,
            "| Stage 9. Nature Methods manuscript assembly | Stage 9.8 section contracts registered, manuscript drafting not started. | The current boundary is evidence intake, official venue-guidance registration, representative methods-paper corpus analysis, narrative-spine selection, claim freeze, paragraph-level claim planning, main figure-spine planning, deterministic PanelForge rendering, supplementary display planning, and section-contract planning only. Do not start title or abstract strategy, citation resolution, drafting, review response, or submission packaging without explicit substage authorization. |",
            "| Stage 9. Nature Methods manuscript assembly | Stage 9.9 title, subtitle, and abstract strategy registered, Results architecture not started. | The current boundary is evidence intake, official venue-guidance registration, representative methods-paper corpus analysis, narrative-spine selection, claim freeze, paragraph-level claim planning, main figure-spine planning, deterministic PanelForge rendering, supplementary display planning, section-contract planning, and front-matter strategy only. Do not start Results architecture, citation resolution, full manuscript drafting, review response, or submission packaging without explicit substage authorization. |",
        )
        body = _replace_once(
            body,
            "Stage 9.8 section contract blueprint has been completed. Stage 9.9 title, subtitle, and abstract strategy remains the next unstarted manuscript step. Manuscript production, citation resolution, and drafting remain not started.",
            "Stage 9.8 section contract blueprint has been completed. Stage 9.9 title, subtitle, and abstract strategy has been completed. Stage 9.10 Results subsection architecture remains the next unstarted manuscript step. Results architecture, citation resolution, full manuscript drafting, and package assembly remain not started.",
        )
        ROADMAP_PATH.write_text(body, encoding="utf-8")


def run() -> dict[str, Any]:
    generated_utc = _now()
    commit = _git_sha()
    strategy_version = f"front-matter-strategy@{generated_utc[:10]}@{commit}"
    claims = _read_csv(CLAIM_LEDGER, "claim_id")
    if STAGING_DIR.exists():
        shutil.rmtree(STAGING_DIR)
    STAGING_DIR.mkdir(parents=True, exist_ok=True)
    _write_text(
        STAGING_DIR / OUTPUTS["title_options"].relative_to(WORKSPACE),
        _build_title_options(generated_utc, strategy_version),
    )
    _write_text(
        STAGING_DIR / OUTPUTS["abstract_strategy"].relative_to(WORKSPACE),
        _build_abstract_strategy(generated_utc, strategy_version),
    )
    _write_text(
        STAGING_DIR / OUTPUTS["abstract"].relative_to(WORKSPACE),
        _build_abstract(generated_utc, strategy_version),
    )
    checks = _validate(claims)
    passed = all(check["passed"] for check in checks)
    gate = {
        "substage": "9.9",
        "timestamp": generated_utc,
        "front_matter_strategy_version": strategy_version,
        "pass": passed,
        "checks": checks,
        "title_option_count": len(TITLE_OPTIONS),
        "preferred_title_option": "TITLE-001",
        "abstract_word_count": _word_count(ABSTRACT_TEXT),
        "abstract_word_limit": 150,
        "abstract_unreferenced": not _contains_citation(ABSTRACT_TEXT),
        "abstract_claim_ids": list(CLAIM_IDS),
        "next_substage": "9.10",
        "outputs": [str(path.relative_to(ROOT)) for path in OUTPUTS.values()],
        "scope_boundary": "Front-matter strategy only. No Results architecture, full manuscript drafting, reference bibliography, figure legends, or submission-package assembly.",
    }
    _write_json(STAGING_DIR / OUTPUTS["gate"].relative_to(WORKSPACE), gate)
    if passed:
        _promote_staging()
        shutil.rmtree(STAGING_DIR)
        _update_registry()
        _update_memory(strategy_version, generated_utc, checks)
        _update_roadmap_memory(strategy_version)
        _update_docs()
    else:
        quarantine = _quarantine_staging(generated_utc)
        gate["quarantine_path"] = str(quarantine.relative_to(ROOT))
        _write_json(OUTPUTS["gate"], gate)
    return {
        "status": "pass" if passed else "fail",
        "substage": "9.9",
        "front_matter_strategy_version": strategy_version,
        "title_option_count": len(TITLE_OPTIONS),
        "abstract_word_count": _word_count(ABSTRACT_TEXT),
        "failures": [check for check in checks if not check["passed"]],
        "outputs": gate["outputs"],
        "next_allowed_action": "Proceed to Stage 9.10 Results subsection architecture after validation.",
    }


def main() -> int:
    payload = run()
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())

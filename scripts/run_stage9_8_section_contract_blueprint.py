"""Run Stage 9.8 section contract blueprint generation.

Stage 9.8 defines the allowed manuscript section surfaces before prose
drafting begins. It does not draft the abstract, title, Results, Introduction,
Discussion, Methods, references, figure legends, or submission package.
"""

from __future__ import annotations

import csv
import json
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
STAGING_DIR = WORKSPACE / "_staging" / "9.8"
QUARANTINE_DIR = WORKSPACE / "_quarantine" / "9.8"
MEMORY_PATH = ROOT / "docs" / "stage9_execution_memory.json"
ROADMAP_MEMORY_PATH = ROOT / "docs" / "roadmap_execution_memory.json"
REGISTRY_PATH = WORKSPACE / "contracts" / "stage9_substage_registry.json"
PLAN_PATH = ROOT / "docs" / "stage9_manuscript_assembly_plan.md"
ROADMAP_PATH = ROOT / "docs" / "roadmap.md"

GATE_97 = GATE_DIR / "9.7.json"
CLAIM_LEDGER = LEDGER_DIR / "claim_hierarchy.csv"
PARAGRAPH_LEDGER = LEDGER_DIR / "paragraph_claim_ledger.csv"
FIGURE_LEDGER = LEDGER_DIR / "figure_to_claim_to_artifact.csv"
SUPPLEMENTARY_LEDGER = LEDGER_DIR / "supplementary_callout_ledger.csv"

OUTPUTS = {
    "section_contracts": SECTIONS_DIR / "section_contracts.md",
    "gate": GATE_DIR / "9.8.json",
}

FORBIDDEN_STARTED_PATHS = [
    SECTIONS_DIR / "title_options.md",
    SECTIONS_DIR / "abstract_strategy.md",
    SECTIONS_DIR / "abstract.md",
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


@dataclass(frozen=True)
class SectionContract:
    section_id: str
    surface: str
    nature_methods_rule: str
    planned_role: str
    required_content: tuple[str, ...]
    prohibited_content: tuple[str, ...]
    claim_ids: tuple[str, ...]
    figure_ids: tuple[str, ...]
    supplementary_ids: tuple[str, ...]
    topical_subheadings: tuple[str, ...]
    word_budget: str
    source_constraints: tuple[str, ...]
    downstream_stage: str


SECTION_CONTRACTS = [
    SectionContract(
        section_id="SEC-001",
        surface="Title and short title",
        nature_methods_rule="Front matter only; title strategy is deferred to Stage 9.9.",
        planned_role="Name the general RhoDyn method without implying the software generated the RhoA/microglia manuscript.",
        required_content=("method name", "general method object", "no unresolved venue claim"),
        prohibited_content=("draft title options", "citation claims", "marketing language"),
        claim_ids=("CLM-0001", "CLM-0005"),
        figure_ids=(),
        supplementary_ids=(),
        topical_subheadings=(),
        word_budget="deferred to Stage 9.9",
        source_constraints=("VENUE-001", "VENUE-002"),
        downstream_stage="9.9",
    ),
    SectionContract(
        section_id="SEC-002",
        surface="Abstract",
        nature_methods_rule="Nature Methods Article abstract up to 150 words and unreferenced.",
        planned_role="State the method object, validation breadth, and scoped biological utility without citation or result-list overload.",
        required_content=("RhoDyn method object", "validation breadth", "software availability boundary", "no references"),
        prohibited_content=("citations", "over-150-word abstract", "claims beyond CLM strength caps"),
        claim_ids=("CLM-0001", "CLM-0002", "CLM-0003", "CLM-0004", "CLM-0005"),
        figure_ids=("FIG-001", "FIG-002", "FIG-003", "FIG-004", "FIG-005", "FIG-006"),
        supplementary_ids=(),
        topical_subheadings=(),
        word_budget="maximum 150 words; unreferenced",
        source_constraints=("VENUE-003",),
        downstream_stage="9.9",
    ),
    SectionContract(
        section_id="SEC-003",
        surface="Introduction",
        nature_methods_rule="Introduction appears without a heading in the Article structure.",
        planned_role="Establish why endpoint, amplitude, and generic time-series summaries miss residence-state decisions in live-cell perturbation biology.",
        required_content=("problem statement", "method gap", "RhoDyn premise", "scope of public demonstrations"),
        prohibited_content=("topical subheadings", "unresolved citations", "RhoA paper as sole evidence"),
        claim_ids=("CLM-0001", "CLM-0002"),
        figure_ids=(),
        supplementary_ids=(),
        topical_subheadings=(),
        word_budget="main-text budget share; target 450-650 words before editorial compression",
        source_constraints=("VENUE-004", "VENUE-006", "VENUE-007"),
        downstream_stage="9.12",
    ),
    SectionContract(
        section_id="SEC-004",
        surface="Results",
        nature_methods_rule="Results should be divided by topical subheadings.",
        planned_role="Present the evidence-bearing display sequence in locked FIG-001 through FIG-006 order.",
        required_content=("topical subheadings", "figure-locked order", "claim IDs", "visible inconclusive contexts"),
        prohibited_content=("narrative-only subsections", "uncited supplementary-only central evidence", "claims exceeding strength caps"),
        claim_ids=("CLM-0001", "CLM-0002", "CLM-0003", "CLM-0004", "CLM-0005"),
        figure_ids=("FIG-001", "FIG-002", "FIG-003", "FIG-004", "FIG-005", "FIG-006"),
        supplementary_ids=("SUPP-001", "SUPP-002", "SUPP-003", "SUPP-004", "SUPP-005", "SUPP-006", "SUPP-007", "SUPP-008"),
        topical_subheadings=(
            "Method object and executable truth cases",
            "Residence-amplitude separation in public live-cell trajectories",
            "Bounded coupling under declared margins",
            "Reserve-like endpoint buffering",
            "Routed-output architecture comparison",
            "Held-out validation and software reproducibility",
        ),
        word_budget="main-text budget share; target 1,600-2,100 words before editorial compression",
        source_constraints=("VENUE-004", "VENUE-005", "VENUE-006", "VENUE-008"),
        downstream_stage="9.10",
    ),
    SectionContract(
        section_id="SEC-005",
        surface="Discussion",
        nature_methods_rule="Discussion does not contain subheadings.",
        planned_role="Synthesize method contribution, biological scope, non-claims, limitations, and future use without adding new evidence.",
        required_content=("main contribution", "scope boundaries", "biological interpretation limits", "software maturity limits"),
        prohibited_content=("subheadings", "new results", "universal residence law", "therapeutic claims"),
        claim_ids=("CLM-0001", "CLM-0005"),
        figure_ids=("FIG-001", "FIG-006"),
        supplementary_ids=("SUPP-007", "SUPP-009"),
        topical_subheadings=(),
        word_budget="main-text budget share; target 650-900 words before editorial compression",
        source_constraints=("VENUE-004", "VENUE-006"),
        downstream_stage="9.13",
    ),
    SectionContract(
        section_id="SEC-006",
        surface="Online Methods",
        nature_methods_rule="Methods should be divided by topical subheadings and contain details needed for interpretation and replication.",
        planned_role="Make RhoDyn inputs, algorithms, uncertainty decisions, benchmarks, and software surfaces reconstructable.",
        required_content=("topical subheadings", "input schemas", "decision rules", "uncertainty", "software versioning"),
        prohibited_content=("unscoped biological mechanisms", "hidden parameter choices", "reader-facing internal IDs"),
        claim_ids=("CLM-0001", "CLM-0002", "CLM-0003", "CLM-0004", "CLM-0005"),
        figure_ids=("FIG-001", "FIG-002", "FIG-003", "FIG-004", "FIG-005", "FIG-006"),
        supplementary_ids=("SUPP-001", "SUPP-002", "SUPP-003", "SUPP-004", "SUPP-005", "SUPP-006", "SUPP-008"),
        topical_subheadings=(
            "Input schemas and preprocessing",
            "Residence windows and amplitude comparators",
            "Bounded-coupling and uncertainty decisions",
            "Reserve-like endpoint construction",
            "Routed-output model comparison",
            "Software surfaces, versioning, and reproducibility",
        ),
        word_budget="Methods budget target up to 3,000 words unless technical detail requires supplement",
        source_constraints=("VENUE-006", "VENUE-015", "VENUE-016"),
        downstream_stage="9.15",
    ),
    SectionContract(
        section_id="SEC-007",
        surface="Data availability",
        nature_methods_rule="Data availability statement is required for datasets needed to interpret, verify, and extend the research.",
        planned_role="Separate public examples, controlled-access inputs, derived tables, and optional RhoA/microglia reference-use artifacts.",
        required_content=("public datasets", "derived tables", "controlled-access boundaries", "archive links"),
        prohibited_content=("private data promises", "local paths", "unavailable raw-data claims"),
        claim_ids=("CLM-0005",),
        figure_ids=("FIG-006",),
        supplementary_ids=("SUPP-008",),
        topical_subheadings=(),
        word_budget="availability statement; concise and complete",
        source_constraints=("VENUE-010", "VENUE-011"),
        downstream_stage="9.17",
    ),
    SectionContract(
        section_id="SEC-008",
        surface="Code availability",
        nature_methods_rule="Original code necessary to interpret and replicate conclusions requires a code availability statement and permanent identifier.",
        planned_role="State repository, release version, Zenodo DOI, license, command index, and archive boundary.",
        required_content=("GitHub release", "Zenodo DOI", "license", "version", "reproducibility commands"),
        prohibited_content=("GitHub-only archive claim", "PyPI publication claim", "private-data reproduction claim"),
        claim_ids=("CLM-0005",),
        figure_ids=("FIG-006",),
        supplementary_ids=("SUPP-008",),
        topical_subheadings=(),
        word_budget="availability statement; concise and complete",
        source_constraints=("VENUE-012", "VENUE-013", "VENUE-014"),
        downstream_stage="9.17",
    ),
    SectionContract(
        section_id="SEC-009",
        surface="Acknowledgements and funding",
        nature_methods_rule="Back matter; no Stage 9.8 prose drafting.",
        planned_role="Reserve a back-matter slot without inventing funding or contribution details.",
        required_content=("funding placeholder policy", "human-authored confirmation requirement"),
        prohibited_content=("invented funders", "unconfirmed contribution claims"),
        claim_ids=(),
        figure_ids=(),
        supplementary_ids=(),
        topical_subheadings=(),
        word_budget="back matter",
        source_constraints=("VENUE-018",),
        downstream_stage="9.27",
    ),
    SectionContract(
        section_id="SEC-010",
        surface="Author contributions",
        nature_methods_rule="Back matter; no Stage 9.8 prose drafting.",
        planned_role="Reserve contribution taxonomy for later human-confirmed authorship input.",
        required_content=("author-role confirmation requirement",),
        prohibited_content=("invented author roles",),
        claim_ids=(),
        figure_ids=(),
        supplementary_ids=(),
        topical_subheadings=(),
        word_budget="back matter",
        source_constraints=("VENUE-018",),
        downstream_stage="9.27",
    ),
    SectionContract(
        section_id="SEC-011",
        surface="Competing interests",
        nature_methods_rule="Back matter; no Stage 9.8 prose drafting.",
        planned_role="Reserve competing-interest statement for later human-confirmed input.",
        required_content=("competing-interest confirmation requirement",),
        prohibited_content=("invented declarations",),
        claim_ids=(),
        figure_ids=(),
        supplementary_ids=(),
        topical_subheadings=(),
        word_budget="back matter",
        source_constraints=("VENUE-018",),
        downstream_stage="9.27",
    ),
    SectionContract(
        section_id="SEC-012",
        surface="References",
        nature_methods_rule="Article references are typically recommended up to 50.",
        planned_role="Reserve citation library scope for Stage 9.20 without creating references.bib now.",
        required_content=("resolved reference IDs", "claim-linked citation support", "methods-paper and venue-policy support"),
        prohibited_content=("unresolved citation placeholders", "uncited bibliography padding", "references.bib before Stage 9.20"),
        claim_ids=("CLM-0001", "CLM-0002", "CLM-0003", "CLM-0004", "CLM-0005"),
        figure_ids=(),
        supplementary_ids=(),
        topical_subheadings=(),
        word_budget="typically up to 50 references",
        source_constraints=("VENUE-007",),
        downstream_stage="9.20",
    ),
    SectionContract(
        section_id="SEC-013",
        surface="Figure legends",
        nature_methods_rule="Legends should begin with a brief title sentence and describe what is depicted.",
        planned_role="Reserve concise legends for the six main figures and future supplementary displays.",
        required_content=("title sentence", "what is depicted", "sample-size/statistical definitions where reported"),
        prohibited_content=("Results prose", "Methods overload", "internal IDs in reader-facing legends"),
        claim_ids=("CLM-0001", "CLM-0002", "CLM-0003", "CLM-0004", "CLM-0005"),
        figure_ids=("FIG-001", "FIG-002", "FIG-003", "FIG-004", "FIG-005", "FIG-006"),
        supplementary_ids=("SUPP-001", "SUPP-002", "SUPP-003", "SUPP-004", "SUPP-005", "SUPP-006", "SUPP-007", "SUPP-008", "SUPP-009"),
        topical_subheadings=(),
        word_budget="legend-specific budget handled in Stage 9.23",
        source_constraints=("VENUE-016", "VENUE-017"),
        downstream_stage="9.23",
    ),
    SectionContract(
        section_id="SEC-014",
        surface="Supplementary Information",
        nature_methods_rule="Articles may be accompanied by supplementary information.",
        planned_role="Bind supplementary items to cited support roles without replacing main evidence.",
        required_content=("planned SUPP items", "methods depth", "extended benchmark tables", "interpretation boundaries"),
        prohibited_content=("uncited data dump", "central evidence moved out of main figures", "unrendered legend prose at Stage 9.8"),
        claim_ids=("CLM-0001", "CLM-0002", "CLM-0003", "CLM-0004", "CLM-0005"),
        figure_ids=("FIG-001", "FIG-002", "FIG-003", "FIG-004", "FIG-005", "FIG-006"),
        supplementary_ids=("SUPP-001", "SUPP-002", "SUPP-003", "SUPP-004", "SUPP-005", "SUPP-006", "SUPP-007", "SUPP-008", "SUPP-009"),
        topical_subheadings=(),
        word_budget="SI depth handled after main section contracts",
        source_constraints=("VENUE-008", "VENUE-015", "VENUE-016"),
        downstream_stage="9.18",
    ),
    SectionContract(
        section_id="SEC-015",
        surface="Reporting Summary and software checklist",
        nature_methods_rule="Life-science manuscripts and new central code require reporting and software-review details.",
        planned_role="Reserve submission-support forms without assembling the submission package now.",
        required_content=("Reporting Summary placeholder", "software submission checklist", "reviewable code details"),
        prohibited_content=("completed submission package", "unchecked claims", "unverified checklist assertions"),
        claim_ids=("CLM-0005",),
        figure_ids=("FIG-006",),
        supplementary_ids=("SUPP-008",),
        topical_subheadings=(),
        word_budget="submission support; handled outside main text",
        source_constraints=("VENUE-009", "VENUE-012", "VENUE-018"),
        downstream_stage="9.17",
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


def _join(values: tuple[str, ...]) -> str:
    return "; ".join(values) if values else "none"


def _markdown_table(rows: list[dict[str, str]], columns: list[str]) -> str:
    lines = ["| " + " | ".join(columns) + " |", "| " + " | ".join("---" for _ in columns) + " |"]
    for row in rows:
        lines.append("| " + " | ".join(str(row.get(column, "")).replace("|", "\\|") for column in columns) + " |")
    return "\n".join(lines)


def _build_contracts(generated_utc: str, contract_version: str) -> str:
    rows = [
        {
            "section_id": section.section_id,
            "surface": section.surface,
            "downstream_stage": section.downstream_stage,
            "word_budget": section.word_budget,
            "subheading_rule": "required" if section.topical_subheadings else "prohibited/none",
            "source_constraints": _join(section.source_constraints),
        }
        for section in SECTION_CONTRACTS
    ]
    detail: list[str] = []
    for section in SECTION_CONTRACTS:
        detail.extend(
            [
                f"### {section.section_id}. {section.surface}",
                "",
                f"- Nature Methods rule. {section.nature_methods_rule}",
                f"- Planned role. {section.planned_role}",
                f"- Required content. {_join(section.required_content)}.",
                f"- Prohibited content. {_join(section.prohibited_content)}.",
                f"- Claim IDs. {_join(section.claim_ids)}.",
                f"- Main figure IDs. {_join(section.figure_ids)}.",
                f"- Supplementary item IDs. {_join(section.supplementary_ids)}.",
                f"- Topical subheadings. {_join(section.topical_subheadings)}.",
                f"- Word budget. {section.word_budget}.",
                f"- Source constraints. {_join(section.source_constraints)}.",
                f"- Downstream drafting or assembly stage. {section.downstream_stage}.",
                "",
            ]
        )
    return f"""# Stage 9.8 section contract blueprint

Generated UTC. {generated_utc}

Section-contract version. {contract_version}

Stage. 9.8 section contract blueprint.

Scope. This file defines manuscript section contracts for a future Nature
Methods Article. It is not a title draft, not an abstract draft, not
Introduction prose, not Results prose, not Discussion prose, not Methods prose,
not a reference library, and not a submission package.

## Contract rule

Each section contract states the surface, venue rule, planned role, required
content, prohibited content, claim links, display-item links, supplementary
support, subheading rule, word-budget target, and downstream stage. The
contracts are planning objects only. They prevent premature drafting and make
the future manuscript structure checkable before scientific prose is written.

## Section map

{_markdown_table(rows, ["section_id", "surface", "downstream_stage", "word_budget", "subheading_rule", "source_constraints"])}

## Section contracts

{chr(10).join(detail).rstrip()}

## Venue-bound structure rules

- Abstract. Maximum 150 words and unreferenced.
- Introduction. No heading in the Nature Methods Article structure.
- Results. Topical subheadings are required.
- Discussion. Subheadings are prohibited.
- Online Methods. Topical subheadings are required and must support interpretation and replication.
- References. Citation resolution is deferred to Stage 9.20 and no `references.bib` is created here.
- Availability and reporting surfaces. Data, code, Reporting Summary, and software-checklist content is deferred to Stage 9.17.

## Non-drafting boundary

Stage 9.8 creates only this contract file and its gate verdict. It does not
create reader-facing manuscript prose or a reference bibliography.
"""


def _no_downstream_started() -> tuple[bool, list[str]]:
    forbidden = [path.relative_to(ROOT).as_posix() for path in FORBIDDEN_STARTED_PATHS if path.exists()]
    return not forbidden, forbidden


def _validate(
    claims: dict[str, dict[str, str]],
    paragraphs: dict[str, dict[str, str]],
    figures: dict[str, dict[str, str]],
    supplementary: dict[str, dict[str, str]],
) -> list[dict[str, Any]]:
    gate_97_pass = False
    if GATE_97.exists():
        try:
            gate_97_pass = _read_json(GATE_97).get("pass") is True
        except json.JSONDecodeError:
            gate_97_pass = False
    section_ids = [section.section_id for section in SECTION_CONTRACTS]
    surfaces = {section.surface for section in SECTION_CONTRACTS}
    every_section_has_contract = (
        len(SECTION_CONTRACTS) == 15
        and len(section_ids) == len(set(section_ids))
        and {"Abstract", "Introduction", "Results", "Discussion", "Online Methods"}.issubset(surfaces)
        and all(section.required_content and section.prohibited_content and section.downstream_stage for section in SECTION_CONTRACTS)
    )
    section_by_surface = {section.surface: section for section in SECTION_CONTRACTS}
    results_methods_subheadings = (
        len(section_by_surface["Results"].topical_subheadings) >= 4
        and len(section_by_surface["Online Methods"].topical_subheadings) >= 4
    )
    discussion_no_subheadings = not section_by_surface["Discussion"].topical_subheadings and "subheadings" in " ".join(section_by_surface["Discussion"].prohibited_content).lower()
    abstract = section_by_surface["Abstract"]
    abstract_budget_ok = "150" in abstract.word_budget and "unreferenced" in abstract.word_budget and "VENUE-003" in abstract.source_constraints
    claim_ids = set(claims)
    figure_ids = set(figures)
    supp_ids = set(supplementary)
    paragraphs_have_sections = {"Introduction", "Results", "Methods", "Discussion"}.issubset({row["section"] for row in paragraphs.values()})
    links_resolve = all(
        set(section.claim_ids).issubset(claim_ids)
        and set(section.figure_ids).issubset(figure_ids)
        and set(section.supplementary_ids).issubset(supp_ids)
        for section in SECTION_CONTRACTS
    ) and paragraphs_have_sections
    no_downstream, downstream_paths = _no_downstream_started()
    return [
        {
            "name": "stage_9_7_gate_passed",
            "passed": gate_97_pass,
            "detail": "Stage 9.7 supplementary display planning exists and passes" if gate_97_pass else "Stage 9.7 gate is missing or not passing",
        },
        {
            "name": "every_section_has_a_contract",
            "passed": every_section_has_contract,
            "detail": "Fifteen manuscript, back-matter, legend, SI, and reporting surfaces have explicit contracts",
        },
        {
            "name": "results_and_methods_require_topical_subheadings",
            "passed": results_methods_subheadings,
            "detail": "Results and Online Methods contracts include topical subheading plans",
        },
        {
            "name": "discussion_prohibits_subheadings",
            "passed": discussion_no_subheadings,
            "detail": "Discussion contract has no topical subheadings and explicitly prohibits them",
        },
        {
            "name": "abstract_contract_follows_sourced_budget",
            "passed": abstract_budget_ok,
            "detail": "Abstract contract is capped at 150 words and unreferenced under VENUE-003",
        },
        {
            "name": "contracts_link_to_locked_claims_figures_and_supplements",
            "passed": links_resolve,
            "detail": "Section contracts resolve to locked CLM, FIG, SUPP, and paragraph-planning surfaces",
        },
        {
            "name": "no_downstream_stage9_surfaces_started",
            "passed": no_downstream,
            "detail": "No title, abstract, Results, Introduction, Discussion, Methods, reference bibliography, or submission package detected"
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
        if substage.get("id") == "9.8":
            substage["status"] = "complete_section_contract_blueprint_registered"
    registry["last_completed_substage"] = "9.8"
    registry["next_substage"] = "9.9"
    _write_json(REGISTRY_PATH, registry)


def _upsert_completed_substage(memory: dict[str, Any], contract_version: str, checks: list[dict[str, Any]]) -> None:
    record = {
        "substage": "9.8",
        "status": "pass",
        "pass": True,
        "gate_verdict_path": "manuscript/nature_methods/gate_verdicts/9.8.json",
        "validation_outcome": "Section contracts registered with venue subheading, abstract, budget, and non-drafting rules",
        "evidence_dependencies": [
            "manuscript/nature_methods/gate_verdicts/9.7.json",
            "manuscript/nature_methods/ledgers/claim_hierarchy.csv",
            "manuscript/nature_methods/ledgers/paragraph_claim_ledger.csv",
            "manuscript/nature_methods/ledgers/figure_to_claim_to_artifact.csv",
            "manuscript/nature_methods/ledgers/supplementary_callout_ledger.csv",
            "manuscript/nature_methods/refs/nature_methods_guidance_register.md",
        ],
        "files_created_or_modified": [
            "manuscript/nature_methods/sections/section_contracts.md",
            "manuscript/nature_methods/gate_verdicts/9.8.json",
        ],
        "remaining_blockers": [
            "Stage 9.9 title, subtitle, and abstract strategy has not started",
            "Citation resolution has not started",
            "Manuscript drafting has not started",
            "Submission-package assembly has not started",
        ],
        "section_contract_version": contract_version,
        "checks": checks,
    }
    entries = [item for item in memory.get("completed_substages", []) if item.get("substage") != "9.8"]
    entries.append(record)
    memory["completed_substages"] = entries


def _update_memory(contract_version: str, generated_utc: str, checks: list[dict[str, Any]]) -> None:
    memory = _read_json(MEMORY_PATH)
    memory["generated_utc"] = generated_utc
    memory["current_substage"] = "9.8"
    memory["section_contracts_started"] = True
    memory["section_contract_version"] = contract_version
    memory["status"] = "stage9_8_section_contract_blueprint_registered"
    memory["current_gate"] = "Stage 9.8 registered section contracts without starting manuscript prose"
    memory["next_substage"] = "9.9"
    memory["next_substage_authorized"] = False
    memory["stage9_active_gate"] = "Stage 9.8 section contracts registered; manuscript drafting not started"
    memory["stage9_8_checks"] = checks
    artifacts = memory.setdefault("artifacts", [])
    for artifact in [
        "manuscript/nature_methods/sections/section_contracts.md",
        "manuscript/nature_methods/gate_verdicts/9.8.json",
    ]:
        if artifact not in artifacts:
            artifacts.append(artifact)
    memory["gate"] = [
        "Stage 9.-1 contract and schema files exist and pass the scaffold checker.",
        "Stage 9.0 through Stage 9.8 are complete through section contract planning.",
        "Stage 9.9 through Stage 9.29 plus Stage 9.25b remain not started.",
        "No title, abstract, manuscript draft sections, reference bibliography, or submission package contents are created in this section-contract pass.",
        "Abstract, Introduction, Results, Discussion, Online Methods, availability, references, legends, SI, and reporting surfaces have contract rules before prose drafting.",
    ]
    memory["scope_rule"] = (
        "Stage 9 has completed evidence intake, venue-guidance registration, representative methods-paper corpus analysis, "
        "narrative-spine selection, claim freeze, paragraph-level claim planning, main figure-spine planning, deterministic "
        "PanelForge rendering, supplementary display planning, and section-contract planning only. Do not start title/abstract "
        "strategy, citation resolution, drafting, review response, or submission packaging without explicit substage authorization."
    )
    _upsert_completed_substage(memory, contract_version, checks)
    _write_json(MEMORY_PATH, memory)


def _update_roadmap_memory(contract_version: str) -> None:
    memory = _read_json(ROADMAP_MEMORY_PATH)
    current = memory.setdefault("current_position", {})
    current["active_stage"] = "Stage 9.8 section contracts registered; manuscript drafting not started"
    current["stage9_active_gate"] = "Stage 9.8 section contracts registered; manuscript drafting not started"
    current["after_stage9_8_section_contracts"] = (
        "Stage 9.8 registered manuscript section contracts for Abstract, Introduction, Results, Discussion, Online Methods, "
        "availability, back matter, references, legends, Supplementary Information, and reporting surfaces. It did not draft prose, "
        "resolve citations, or assemble a submission package."
    )
    for stage in memory.get("stage_lock", []):
        if not isinstance(stage, dict) or stage.get("stage") != 9:
            continue
        stage["status"] = "stage9_8_section_contract_blueprint_registered"
        stage["current_gate"] = "Stage 9.8 registered section contracts without starting manuscript prose"
        stage["scope_rule"] = (
            "Stage 9 has completed evidence intake, venue-guidance registration, representative methods-paper corpus analysis, "
            "narrative-spine selection, claim freeze, paragraph-level claim planning, main figure-spine planning, deterministic "
            "PanelForge rendering, supplementary display planning, and section-contract planning only. Do not start title/abstract "
            "strategy, citation resolution, drafting, review response, or submission packaging without explicit substage authorization."
        )
        artifacts = stage.setdefault("artifacts", [])
        for artifact in [
            "manuscript/nature_methods/sections/section_contracts.md",
            "manuscript/nature_methods/gate_verdicts/9.8.json",
            "scripts/run_stage9_8_section_contract_blueprint.py",
        ]:
            if artifact not in artifacts:
                artifacts.append(artifact)
        gate = stage.setdefault("gate", [])
        section_gate = "Stage 9.8 section contracts bind Abstract, Results, Discussion, and Methods venue rules before prose drafting."
        if section_gate not in gate:
            gate.append(section_gate)
        for subphase in stage.get("subphases", []):
            if isinstance(subphase, dict) and subphase.get("id") == "9.8":
                subphase["status"] = "complete_section_contract_blueprint_registered"
                subphase["evidence"] = "manuscript/nature_methods/gate_verdicts/9.8.json"
                subphase["section_contract_version"] = contract_version
    _write_json(ROADMAP_MEMORY_PATH, memory)


def _replace_once(body: str, old: str, new: str) -> str:
    return body.replace(old, new) if old in body else body


def _update_docs() -> None:
    if PLAN_PATH.exists():
        body = PLAN_PATH.read_text(encoding="utf-8")
        body = _replace_once(
            body,
            "and registers the supplementary display plan in Stage 9.7. It does not begin section contracts, citation resolution, manuscript drafting, editorial polishing, or package assembly.",
            "registers the supplementary display plan in Stage 9.7, and registers the section contract blueprint in Stage 9.8. It does not begin title or abstract strategy, citation resolution, manuscript drafting, editorial polishing, or package assembly.",
        )
        body = _replace_once(
            body,
            "Stage 9.7 registers supplementary display support in `supplementary/supplementary_item_plan.md`, `ledgers/supplementary_callout_ledger.csv`, `figures/figures.manifest.yaml`, and `gate_verdicts/9.7.json`. The current state intentionally does not create",
            "Stage 9.7 registers supplementary display support in `supplementary/supplementary_item_plan.md`, `ledgers/supplementary_callout_ledger.csv`, `figures/figures.manifest.yaml`, and `gate_verdicts/9.7.json`. Stage 9.8 registers section contracts in `sections/section_contracts.md` and `gate_verdicts/9.8.json`. The current state intentionally does not create",
        )
        body = _replace_once(
            body,
            "| 9.8 | Section contract blueprint | not_started | Define every manuscript section and venue structural rule before writing. |",
            "| 9.8 | Section contract blueprint | complete_section_contract_blueprint_registered | Define every manuscript section and venue structural rule before writing. |",
        )
        PLAN_PATH.write_text(body, encoding="utf-8")
    if ROADMAP_PATH.exists():
        body = ROADMAP_PATH.read_text(encoding="utf-8")
        body = _replace_once(
            body,
            "PanelForge figure-engine integration is complete as Stage 9.6b, and\nStage 9.7 has registered supplementary display planning. Manuscript\nproduction, citation resolution, section contracts, and drafting remain not\nstarted.",
            "PanelForge figure-engine integration is complete as Stage 9.6b, Stage 9.7\nhas registered supplementary display planning, and Stage 9.8 has registered\nsection contracts. Manuscript production, citation resolution, title/abstract\nstrategy, and drafting remain not started.",
        )
        body = _replace_once(
            body,
            "| Stage 9. Nature Methods manuscript assembly | Stage 9.7 supplementary display planning registered, manuscript production not started. | The current boundary is evidence intake, official venue-guidance registration, representative methods-paper corpus analysis, narrative-spine selection, claim freeze, paragraph-level claim planning, main figure-spine planning, deterministic PanelForge rendering, and supplementary display planning only. Do not start section contracts, citation resolution, drafting, review response, or submission packaging without explicit substage authorization. |",
            "| Stage 9. Nature Methods manuscript assembly | Stage 9.8 section contracts registered, manuscript drafting not started. | The current boundary is evidence intake, official venue-guidance registration, representative methods-paper corpus analysis, narrative-spine selection, claim freeze, paragraph-level claim planning, main figure-spine planning, deterministic PanelForge rendering, supplementary display planning, and section-contract planning only. Do not start title or abstract strategy, citation resolution, drafting, review response, or submission packaging without explicit substage authorization. |",
        )
        body = _replace_once(
            body,
            "Stage 9.2 representative methods-paper corpus has been completed. Stage 9.3 narrative spine has been completed. Stage 9.4 claim freeze has been completed. Stage 9.5 paragraph-level claim ledger has been completed. Stage 9.6 figure-first manuscript spine has been completed. Stage 9.6b PanelForge rendering has been completed. Stage 9.7 supplementary display planning has been completed. Stage 9.8 section contract blueprint remains the next unstarted manuscript step. Manuscript production, citation resolution, and drafting remain not started.",
            "Stage 9.2 representative methods-paper corpus has been completed. Stage 9.3 narrative spine has been completed. Stage 9.4 claim freeze has been completed. Stage 9.5 paragraph-level claim ledger has been completed. Stage 9.6 figure-first manuscript spine has been completed. Stage 9.6b PanelForge rendering has been completed. Stage 9.7 supplementary display planning has been completed. Stage 9.8 section contract blueprint has been completed. Stage 9.9 title, subtitle, and abstract strategy remains the next unstarted manuscript step. Manuscript production, citation resolution, and drafting remain not started.",
        )
        ROADMAP_PATH.write_text(body, encoding="utf-8")


def run() -> dict[str, Any]:
    generated_utc = _now()
    commit = _git_sha()
    contract_version = f"section-contracts@{generated_utc[:10]}@{commit}"
    claims = _read_csv(CLAIM_LEDGER, "claim_id")
    paragraphs = _read_csv(PARAGRAPH_LEDGER, "para_id")
    figures = _read_csv(FIGURE_LEDGER, "fig_id")
    supplementary = _read_csv(SUPPLEMENTARY_LEDGER, "supp_id")
    if STAGING_DIR.exists():
        shutil.rmtree(STAGING_DIR)
    STAGING_DIR.mkdir(parents=True, exist_ok=True)
    _write_text(
        STAGING_DIR / OUTPUTS["section_contracts"].relative_to(WORKSPACE),
        _build_contracts(generated_utc, contract_version),
    )
    checks = _validate(claims, paragraphs, figures, supplementary)
    passed = all(check["passed"] for check in checks)
    gate = {
        "substage": "9.8",
        "timestamp": generated_utc,
        "section_contract_version": contract_version,
        "pass": passed,
        "checks": checks,
        "section_contract_count": len(SECTION_CONTRACTS),
        "results_subheading_count": len([s for s in SECTION_CONTRACTS if s.surface == "Results"][0].topical_subheadings),
        "methods_subheading_count": len([s for s in SECTION_CONTRACTS if s.surface == "Online Methods"][0].topical_subheadings),
        "discussion_subheading_count": len([s for s in SECTION_CONTRACTS if s.surface == "Discussion"][0].topical_subheadings),
        "abstract_word_limit": 150,
        "abstract_unreferenced": True,
        "next_substage": "9.9",
        "outputs": [str(path.relative_to(ROOT)) for path in OUTPUTS.values()],
        "scope_boundary": "Section contract planning only. No title options, abstract draft, Results, Introduction, Discussion, Methods prose, references, or submission-package assembly.",
    }
    _write_json(STAGING_DIR / OUTPUTS["gate"].relative_to(WORKSPACE), gate)
    if passed:
        _promote_staging()
        shutil.rmtree(STAGING_DIR)
        _update_registry()
        _update_memory(contract_version, generated_utc, checks)
        _update_roadmap_memory(contract_version)
        _update_docs()
    else:
        quarantine = _quarantine_staging(generated_utc)
        gate["quarantine_path"] = str(quarantine.relative_to(ROOT))
        _write_json(OUTPUTS["gate"], gate)
    return {
        "status": "pass" if passed else "fail",
        "substage": "9.8",
        "section_contract_version": contract_version,
        "section_contract_count": len(SECTION_CONTRACTS),
        "failures": [check for check in checks if not check["passed"]],
        "outputs": gate["outputs"],
        "next_allowed_action": "Proceed to Stage 9.9 title, subtitle, and abstract strategy after validation.",
    }


def main() -> int:
    payload = run()
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())

"""Run Stage 9.12 Introduction literature-binding pass.

Stage 9.12 drafts a citation-bound Introduction from the Stage 9.8 section
contract and the Stage 9.11 Results boundary. It resolves Introduction
citations to stable reference IDs and a local citation ledger, but it does not
create the full reference library, Discussion, Methods, figure legends, or a
submission package.
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
REFS_DIR = WORKSPACE / "refs"
GATE_DIR = WORKSPACE / "gate_verdicts"
STAGING_DIR = WORKSPACE / "_staging" / "9.12"
QUARANTINE_DIR = WORKSPACE / "_quarantine" / "9.12"
MEMORY_PATH = ROOT / "docs" / "stage9_execution_memory.json"
ROADMAP_MEMORY_PATH = ROOT / "docs" / "roadmap_execution_memory.json"
REGISTRY_PATH = WORKSPACE / "contracts" / "stage9_substage_registry.json"
PLAN_PATH = ROOT / "docs" / "stage9_manuscript_assembly_plan.md"
ROADMAP_PATH = ROOT / "docs" / "roadmap.md"

GATE_911 = GATE_DIR / "9.11.json"
SECTION_CONTRACTS = SECTIONS_DIR / "section_contracts.md"

OUTPUTS = {
    "introduction": SECTIONS_DIR / "introduction.md",
    "ledger": REFS_DIR / "introduction_citation_ledger.csv",
    "gate": GATE_DIR / "9.12.json",
}

FORBIDDEN_STARTED_PATHS = [
    SECTIONS_DIR / "discussion.md",
    SECTIONS_DIR / "methods.md",
    SECTIONS_DIR / "data_availability.md",
    SECTIONS_DIR / "code_availability.md",
    REFS_DIR / "references.bib",
    WORKSPACE / "submission_package" / "pi_review_packet.md",
    WORKSPACE / "submission_package" / "submission_readiness_checklist.md",
]

FORBIDDEN_INTRO_PHRASES = (
    "universal",
    "guarantees",
    "therapeutic",
    "clinical",
    "diagnostic",
    "RhoDyn generated the original",
    "absence of all coupling",
    "proof of no crosstalk",
    "true biological reserve",
    "literal molecular edge",
)


@dataclass(frozen=True)
class Citation:
    ref_id: str
    citation_label: str
    title: str
    doi_or_pmid: str
    source_type: str
    claim_id: str
    paragraph_ids: str
    source_file: str
    supports_external_claim: str


CITATIONS = [
    Citation(
        ref_id="REF-0001",
        citation_label="Saelens et al. 2019",
        title="A comparison of single-cell trajectory inference methods",
        doi_or_pmid="10.1038/s41587-019-0071-9",
        source_type="methods",
        claim_id="CLM-0001",
        paragraph_ids="PARA-INTRO-001",
        source_file="manuscript/nature_methods/refs/_cache/methods_corpus/mp-004.crossref.json",
        supports_external_claim="Shared benchmarks clarify when trajectory summaries answer different biological questions.",
    ),
    Citation(
        ref_id="REF-0002",
        citation_label="Bergen et al. 2020",
        title="Generalizing RNA velocity to transient cell states through dynamical modeling",
        doi_or_pmid="10.1038/s41587-020-0591-3",
        source_type="methods",
        claim_id="CLM-0001",
        paragraph_ids="PARA-INTRO-001",
        source_file="manuscript/nature_methods/refs/_cache/methods_corpus/mp-006.crossref.json",
        supports_external_claim="Dynamic cell-state methods can expose transient regimes not visible to static summaries alone.",
    ),
    Citation(
        ref_id="REF-0003",
        citation_label="Moon et al. 2019",
        title="Visualizing structure and transitions in high-dimensional biological data",
        doi_or_pmid="10.1038/s41587-019-0336-3",
        source_type="methods",
        claim_id="CLM-0001",
        paragraph_ids="PARA-INTRO-001",
        source_file="manuscript/nature_methods/refs/_cache/methods_corpus/mp-007.crossref.json",
        supports_external_claim="State-space visualization methods help interpret biological transitions but require quantitative support.",
    ),
    Citation(
        ref_id="REF-0004",
        citation_label="Lange et al. 2022",
        title="CellRank for directed single-cell fate mapping",
        doi_or_pmid="10.1038/s41592-021-01346-6",
        source_type="methods",
        claim_id="CLM-0001",
        paragraph_ids="PARA-INTRO-001",
        source_file="manuscript/nature_methods/refs/_cache/methods_corpus/mp-003.crossref.json",
        supports_external_claim="Formal inference objects make dynamic biological interpretation inspectable.",
    ),
    Citation(
        ref_id="REF-0005",
        citation_label="Stringer et al. 2021",
        title="Cellpose: a generalist algorithm for cellular segmentation",
        doi_or_pmid="10.1038/s41592-020-01018-x",
        source_type="methods",
        claim_id="CLM-0002",
        paragraph_ids="PARA-INTRO-002",
        source_file="manuscript/nature_methods/refs/_cache/methods_corpus/mp-001.crossref.json",
        supports_external_claim="Reusable methods papers pair formal method behavior with broad examples and accessible software.",
    ),
    Citation(
        ref_id="REF-0006",
        citation_label="Palla et al. 2022",
        title="Squidpy: a scalable framework for spatial omics analysis",
        doi_or_pmid="10.1038/s41592-021-01358-2",
        source_type="methods",
        claim_id="CLM-0002",
        paragraph_ids="PARA-INTRO-002",
        source_file="manuscript/nature_methods/refs/_cache/methods_corpus/mp-002.crossref.json",
        supports_external_claim="Workbench-like methods require transparent data objects, analysis outputs, and reproducibility routes.",
    ),
    Citation(
        ref_id="REF-0007",
        citation_label="Gayoso et al. 2022",
        title="A Python library for probabilistic analysis of single-cell omics data",
        doi_or_pmid="10.1038/s41587-021-01206-w",
        source_type="methods",
        claim_id="CLM-0002",
        paragraph_ids="PARA-INTRO-002",
        source_file="manuscript/nature_methods/refs/_cache/methods_corpus/mp-005.crossref.json",
        supports_external_claim="Package architecture and uncertainty-aware outputs are part of a reviewable method claim.",
    ),
    Citation(
        ref_id="REF-0008",
        citation_label="Mathis et al. 2018",
        title="DeepLabCut: markerless pose estimation of user-defined body parts with deep learning",
        doi_or_pmid="10.1038/s41593-018-0209-y",
        source_type="methods",
        claim_id="CLM-0002",
        paragraph_ids="PARA-INTRO-002",
        source_file="manuscript/nature_methods/refs/_cache/methods_corpus/mp-008.crossref.json",
        supports_external_claim="A methods contribution should make user-facing adoption and reproducible outputs visible.",
    ),
    Citation(
        ref_id="REF-0009",
        citation_label="Copperman et al. 2023",
        title="Morphodynamical cell state description via live-cell imaging trajectory embedding",
        doi_or_pmid="10.1038/s42003-023-04837-8",
        source_type="methods",
        claim_id="CLM-0001;CLM-0002",
        paragraph_ids="PARA-INTRO-002",
        source_file="manuscript/nature_methods/refs/_cache/reference_library/10.1038_s42003-023-04837-8.csl.json",
        supports_external_claim="Live-cell morphodynamic trajectory embedding is established prior art for time-lapse cell-state analysis.",
    ),
    Citation(
        ref_id="REF-0010",
        citation_label="von Buchholtz 2025 dataset",
        title="Public DRG calcium imaging archive used as a live-cell signaling demonstration",
        doi_or_pmid="10.5281/zenodo.14907827",
        source_type="dataset",
        claim_id="CLM-0001",
        paragraph_ids="PARA-INTRO-001",
        source_file="docs/stage7_public_data_adapters.md",
        supports_external_claim="Public DRG calcium traces provide an independent calcium trajectory demonstration.",
    ),
    Citation(
        ref_id="REF-0011",
        citation_label="Wan et al. 2021 dataset",
        title="Public ERK GPCR and paired ERK/Akt live-cell reporter archive",
        doi_or_pmid="10.5281/zenodo.5836623",
        source_type="dataset",
        claim_id="CLM-0001;CLM-0002",
        paragraph_ids="PARA-INTRO-001;PARA-INTRO-002",
        source_file="docs/stage7_public_data_adapters.md",
        supports_external_claim="Public ERK GPCR and ERK/Akt reporter traces support trajectory and bounded-coupling demonstrations.",
    ),
    Citation(
        ref_id="REF-0012",
        citation_label="Seal et al. 2023 dataset",
        title="Public Cell Painting and MitoTox endpoint archive",
        doi_or_pmid="10.5281/zenodo.10011861",
        source_type="dataset",
        claim_id="CLM-0002",
        paragraph_ids="PARA-INTRO-002",
        source_file="docs/stage7_endpoint_reserve_routing_demonstrations.md",
        supports_external_claim="Public endpoint data support reserve-like and routed-output demonstrations.",
    ),
]


INTRODUCTION_PARAGRAPHS = [
    {
        "para_ids": ("PARA-INTRO-001",),
        "claim_ids": ("CLM-0001",),
        "refs": ("REF-0001", "REF-0002", "REF-0003", "REF-0004"),
        "text": (
            "Live-cell perturbation experiments increasingly measure the temporal structure of signaling, morphology, and fate-associated reporters, "
            "yet many analysis workflows still reduce those records to endpoints, peaks, thresholds, or generic trajectory features. "
            "Benchmarking and dynamical single-cell methods have made it clear that computational summaries can change biological interpretation when they preserve transition structure rather than only static position (REF-0001; REF-0002; REF-0003; REF-0004). "
            "The unresolved problem for perturbation biology is more specific. A cell can show a high peak, a similar endpoint, or the same apparent state assignment while spending different amounts of time in the operating range that matters for the experiment. "
            "A method that treats that time-in-state behavior as an explicit object is therefore needed to ask when residence carries information that amplitude summaries miss."
        ),
    },
    {
        "para_ids": ("PARA-INTRO-001",),
        "claim_ids": ("CLM-0001",),
        "refs": ("REF-0010", "REF-0011"),
        "text": (
            "RhoDyn addresses this gap by defining residence-state inference for tidy live-cell trajectories and paired endpoint inputs. "
            "For a declared biological window, it separates dwell fraction, dwell time, and segment count from peak, endpoint, mean activity, latency, and threshold-style comparators. "
            "That separation is deliberately scoped. The window is not automatically discovered by the software, and a residence summary is not a causal mechanism by itself. "
            "Instead, RhoDyn makes the comparison inspectable so users can see whether a calcium, kinase, or other reporter trajectory changes interpretation when time spent in a declared response interval is placed beside amplitude. "
            "The current evidence set uses public DRG calcium and ERK GPCR reporter trajectories as independent live-cell demonstrations beyond the RhoA/microglia reference use case (REF-0010; REF-0011)."
        ),
    },
    {
        "para_ids": ("PARA-INTRO-002",),
        "claim_ids": ("CLM-0002",),
        "refs": ("REF-0005", "REF-0006", "REF-0007", "REF-0008", "REF-0009"),
        "text": (
            "A residence method also has to report when the supplied data do not justify a stronger conclusion. "
            "Successful computational methods papers typically combine a formal input object, benchmark comparisons, visible uncertainty, software surfaces, and examples that expose both strengths and limits (REF-0005; REF-0006; REF-0007; REF-0008; REF-0009). "
            "RhoDyn follows that pattern by returning bounded-coupling decisions only under declared margins and uncertainty support, keeping margin-sensitive contrasts inconclusive, and treating reserve-like summaries as measurement-scoped endpoint coordinates. "
            "It also compares routed-output alternatives against reduced architectures without treating effective parameters as direct biochemical interactions."
        ),
    },
    {
        "para_ids": ("PARA-INTRO-002",),
        "claim_ids": ("CLM-0002",),
        "refs": ("REF-0011", "REF-0012"),
        "text": (
            "The resulting manuscript is therefore a methods Article rather than a new primary disease-biology claim. "
            "Its public demonstrations include paired ERK/Akt reporter trajectories for bounded coupling and Cell Painting/MitoTox endpoint tables for reserve-like and routed-output analyses (REF-0011; REF-0012). "
            "Across those examples, the central question is not whether every biological system contains a residence regime. "
            "It is whether a reviewable method can preserve dynamic operating-state information, reveal cases where amplitude or endpoint summaries are sufficient, and withhold interpretation when the data do not resolve the boundary. "
            "RhoDyn is designed to make those decisions reproducible across Python, command-line, backend, workbench, and archive surfaces, with explicit reproducibility checks, before the Results tests each component in figure-locked order."
        ),
    },
]


LEDGER_FIELDS = [
    "ref_id",
    "citation_label",
    "title",
    "doi_or_pmid",
    "resolved",
    "access_date",
    "source_type",
    "claim_id",
    "paragraph_ids",
    "source_file",
    "supports_external_claim",
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


def _write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=LEDGER_FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def _word_count(text: str) -> int:
    return len(re.findall(r"\b[\w-]+\b", text))


def _visible_text(text: str) -> str:
    return "\n".join(line for line in text.splitlines() if not line.startswith("<!--")).strip()


def _citation_rows(access_date: str) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for citation in CITATIONS:
        source_path = ROOT / citation.source_file
        rows.append(
            {
                "ref_id": citation.ref_id,
                "citation_label": citation.citation_label,
                "title": citation.title,
                "doi_or_pmid": citation.doi_or_pmid,
                "resolved": "true" if source_path.exists() and citation.doi_or_pmid else "false",
                "access_date": access_date,
                "source_type": citation.source_type,
                "claim_id": citation.claim_id,
                "paragraph_ids": citation.paragraph_ids,
                "source_file": citation.source_file,
                "supports_external_claim": citation.supports_external_claim,
            }
        )
    return rows


def _build_introduction(generated_utc: str, draft_version: str) -> str:
    blocks = [
        f"<!-- INTRODUCTION-DRAFT stage=9.12 generated_utc={generated_utc} draft_version={draft_version} -->",
        "",
    ]
    for paragraph in INTRODUCTION_PARAGRAPHS:
        blocks.extend(
            [
                (
                    "<!-- "
                    f"para_ids={';'.join(paragraph['para_ids'])} "
                    f"claim_ids={';'.join(paragraph['claim_ids'])} "
                    f"refs={';'.join(paragraph['refs'])}"
                    " -->"
                ),
                "",
                str(paragraph["text"]),
                "",
            ]
        )
    return "\n".join(blocks)


def _citation_tokens(text: str) -> list[str]:
    return re.findall(r"REF-\d{4}", text)


def _no_downstream_started() -> tuple[bool, list[str]]:
    forbidden = [path.relative_to(ROOT).as_posix() for path in FORBIDDEN_STARTED_PATHS if path.exists()]
    return not forbidden, forbidden


def _validate(introduction_text: str, citation_rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    gate_911_pass = False
    if GATE_911.exists():
        try:
            gate_911_pass = _read_json(GATE_911).get("pass") is True
        except json.JSONDecodeError:
            gate_911_pass = False
    section_contract_ok = SECTION_CONTRACTS.exists() and "SEC-003. Introduction" in SECTION_CONTRACTS.read_text(encoding="utf-8")
    visible = _visible_text(introduction_text)
    word_count = _word_count(visible)
    citation_set = set(_citation_tokens(visible))
    ledger_refs = {row["ref_id"] for row in citation_rows}
    resolved_refs = {row["ref_id"] for row in citation_rows if row["resolved"] == "true"}
    unresolved = sorted(citation_set - resolved_refs)
    uncited_ledger_refs = sorted(ledger_refs - citation_set)
    para_comments = re.findall(r"para_ids=([^ ]+)", introduction_text)
    covered_para_ids = sorted({item for group in para_comments for item in group.split(";") if item})
    source_types = [row["source_type"] for row in citation_rows]
    review_share = source_types.count("review") / len(source_types) if source_types else 1.0
    forbidden_absent = not any(phrase.lower() in visible.lower() for phrase in FORBIDDEN_INTRO_PHRASES)
    required_terms = all(
        phrase in visible
        for phrase in [
            "residence-state",
            "amplitude",
            "bounded-coupling",
            "reserve-like",
            "routed-output",
            "RhoDyn",
            "inconclusive",
        ]
    )
    no_headings = not any(line.startswith("#") for line in visible.splitlines())
    mapped_claim_ids = {claim_id for row in citation_rows for claim_id in row["claim_id"].split(";") if claim_id}
    source_files_exist = all((ROOT / row["source_file"]).exists() for row in citation_rows)
    no_downstream, downstream_paths = _no_downstream_started()
    return [
        {
            "name": "stage_9_11_gate_passed",
            "passed": gate_911_pass,
            "detail": "Stage 9.11 Results draft exists and passes" if gate_911_pass else "Stage 9.11 gate is missing or not passing",
        },
        {
            "name": "introduction_contract_available",
            "passed": section_contract_ok,
            "detail": "Stage 9.8 Introduction section contract is available",
        },
        {
            "name": "introduction_word_budget_and_structure_hold",
            "passed": 450 <= word_count <= 650 and no_headings and len(para_comments) == len(INTRODUCTION_PARAGRAPHS),
            "detail": f"Introduction visible word count: {word_count}; headings present: {not no_headings}",
        },
        {
            "name": "all_introduction_citations_resolve",
            "passed": bool(citation_set) and not unresolved and not uncited_ledger_refs and source_files_exist,
            "detail": f"cited={len(citation_set)} unresolved={unresolved} uncited_ledger_refs={uncited_ledger_refs}",
        },
        {
            "name": "external_claims_map_to_reference_ids",
            "passed": covered_para_ids == ["PARA-INTRO-001", "PARA-INTRO-002"]
            and mapped_claim_ids == {"CLM-0001", "CLM-0002"}
            and all(row["supports_external_claim"] for row in citation_rows),
            "detail": f"covered_para_ids={';'.join(covered_para_ids)} mapped_claim_ids={';'.join(sorted(mapped_claim_ids))}",
        },
        {
            "name": "review_source_share_under_threshold",
            "passed": review_share <= 0.25,
            "detail": f"review_source_share={review_share:.3f}",
        },
        {
            "name": "strength_caps_hold",
            "passed": forbidden_absent and required_terms,
            "detail": "Introduction preserves residence, bounded-coupling, reserve-like, routed-output, inconclusive, and reproducibility boundaries",
        },
        {
            "name": "no_full_reference_library_or_downstream_surfaces_started",
            "passed": no_downstream,
            "detail": "No references.bib, Discussion, Methods, figure legends, or submission package detected"
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
        if substage.get("id") == "9.12":
            substage["status"] = "complete_introduction_literature_bound"
    registry["last_completed_substage"] = "9.12"
    registry["next_substage"] = "9.13"
    _write_json(REGISTRY_PATH, registry)


def _upsert_completed_substage(memory: dict[str, Any], draft_version: str, checks: list[dict[str, Any]]) -> None:
    record = {
        "substage": "9.12",
        "status": "pass",
        "pass": True,
        "gate_verdict_path": "manuscript/nature_methods/gate_verdicts/9.12.json",
        "validation_outcome": "Introduction draft registered with resolved reference IDs and citation ledger",
        "evidence_dependencies": [
            "manuscript/nature_methods/gate_verdicts/9.11.json",
            "manuscript/nature_methods/sections/section_contracts.md",
            "manuscript/nature_methods/refs/representative_methods_papers.md",
            "docs/stage7_public_data_adapters.md",
            "docs/stage7_endpoint_reserve_routing_demonstrations.md",
        ],
        "files_created_or_modified": [
            "manuscript/nature_methods/sections/introduction.md",
            "manuscript/nature_methods/refs/introduction_citation_ledger.csv",
            "manuscript/nature_methods/gate_verdicts/9.12.json",
        ],
        "remaining_blockers": [
            "Stage 9.13 Discussion interpretation map has not started",
            "Full reference library and citation audit have not started",
            "Online Methods and figure legends have not started",
            "Submission-package assembly has not started",
        ],
        "introduction_draft_version": draft_version,
        "checks": checks,
    }
    entries = [item for item in memory.get("completed_substages", []) if item.get("substage") != "9.12"]
    entries.append(record)
    memory["completed_substages"] = entries


def _update_memory(draft_version: str, generated_utc: str, checks: list[dict[str, Any]]) -> None:
    memory = _read_json(MEMORY_PATH)
    memory["generated_utc"] = generated_utc
    memory["current_substage"] = "9.12"
    memory["introduction_literature_binding_started"] = True
    memory["introduction_draft_version"] = draft_version
    memory["status"] = "stage9_12_introduction_literature_bound"
    memory["current_gate"] = "Stage 9.12 registered citation-bound Introduction without starting full reference library"
    memory["next_substage"] = "9.13"
    memory["next_substage_authorized"] = False
    memory["stage9_active_gate"] = "Stage 9.12 Introduction literature binding complete; Discussion interpretation map not started"
    memory["stage9_12_checks"] = checks
    artifacts = memory.setdefault("artifacts", [])
    for artifact in [
        "manuscript/nature_methods/sections/introduction.md",
        "manuscript/nature_methods/refs/introduction_citation_ledger.csv",
        "manuscript/nature_methods/gate_verdicts/9.12.json",
    ]:
        if artifact not in artifacts:
            artifacts.append(artifact)
    memory["gate"] = [
        "Stage 9.-1 contract and schema files exist and pass the scaffold checker.",
        "Stage 9.0 through Stage 9.12 are complete through Introduction literature binding.",
        "Stage 9.13 through Stage 9.29 plus Stage 9.25b remain not started.",
        "No Discussion, Methods, full reference library, figure legends, or submission package contents are created in this Introduction pass.",
        "Every Introduction citation resolves to a reference ID in the Introduction citation ledger.",
    ]
    memory["scope_rule"] = (
        "Stage 9 has completed evidence intake, venue-guidance registration, representative methods-paper corpus analysis, "
        "narrative-spine selection, claim freeze, paragraph-level claim planning, main figure-spine planning, deterministic "
        "PanelForge rendering, supplementary display planning, section-contract planning, title/abstract strategy, Results "
        "subsection architecture, Results drafting, and Introduction literature binding only. Do not start Discussion, Methods, "
        "full reference library, figure legends, review response, or submission packaging without explicit substage authorization."
    )
    _upsert_completed_substage(memory, draft_version, checks)
    _write_json(MEMORY_PATH, memory)


def _update_roadmap_memory(draft_version: str) -> None:
    memory = _read_json(ROADMAP_MEMORY_PATH)
    current = memory.setdefault("current_position", {})
    current["active_stage"] = "Stage 9.12 Introduction literature binding complete; Discussion interpretation map not started"
    current["stage9_active_gate"] = "Stage 9.12 Introduction literature binding complete; Discussion interpretation map not started"
    current["after_stage9_12_introduction_literature_binding"] = (
        "Stage 9.12 registered a citation-bound Introduction and citation ledger with resolved reference IDs. "
        "It did not start the full reference library, Discussion, Methods, figure legends, or submission-package assembly."
    )
    current["current_gate"] = "Introduction literature binding complete without full reference library"
    current["next_stage"] = "Stage 9.13 Discussion interpretation map"
    for stage in memory.get("stage_lock", []):
        if not isinstance(stage, dict) or stage.get("stage") != 9:
            continue
        stage["status"] = "stage9_12_introduction_literature_bound"
        stage["current_gate"] = "Stage 9.12 registered citation-bound Introduction without starting full reference library"
        stage["scope_rule"] = (
            "Stage 9 has completed evidence intake, venue-guidance registration, representative methods-paper corpus analysis, "
            "narrative-spine selection, claim freeze, paragraph-level claim planning, main figure-spine planning, deterministic "
            "PanelForge rendering, supplementary display planning, section-contract planning, front-matter strategy, Results architecture, "
            "Results drafting, and Introduction literature binding only. Do not start Discussion, Methods, full reference library, "
            "figure legends, review response, or submission packaging without explicit substage authorization."
        )
        artifacts = stage.setdefault("artifacts", [])
        for artifact in [
            "manuscript/nature_methods/sections/introduction.md",
            "manuscript/nature_methods/refs/introduction_citation_ledger.csv",
            "manuscript/nature_methods/gate_verdicts/9.12.json",
            "scripts/run_stage9_12_introduction_literature_binding.py",
        ]:
            if artifact not in artifacts:
                artifacts.append(artifact)
        gate = stage.setdefault("gate", [])
        intro_gate = "Stage 9.12 Introduction cites resolved reference IDs and keeps review-source share under threshold."
        if intro_gate not in gate:
            gate.append(intro_gate)
        for subphase in stage.get("subphases", []):
            if isinstance(subphase, dict) and subphase.get("id") == "9.12":
                subphase["status"] = "complete_introduction_literature_bound"
                subphase["evidence"] = "manuscript/nature_methods/gate_verdicts/9.12.json"
                subphase["introduction_draft_version"] = draft_version
    _write_json(ROADMAP_MEMORY_PATH, memory)


def _replace_once(body: str, old: str, new: str) -> str:
    return body.replace(old, new) if old in body else body


def _update_docs() -> None:
    if PLAN_PATH.exists():
        body = PLAN_PATH.read_text(encoding="utf-8")
        body = _replace_once(
            body,
            "registers Results subsection architecture in Stage 9.10, and registers a Results draft in Stage 9.11. It does not begin Introduction literature binding, citation resolution, Discussion, Methods, editorial polishing, or package assembly.",
            "registers Results subsection architecture in Stage 9.10, registers a Results draft in Stage 9.11, and registers a citation-bound Introduction in Stage 9.12. It does not begin Discussion, Methods, full reference-library assembly, editorial polishing, or package assembly.",
        )
        body = _replace_once(
            body,
            "Stage 9.11 registers Results prose in `sections/results.md` and `gate_verdicts/9.11.json`. The current state intentionally does not create `sections/introduction.md`, `sections/discussion.md`, `sections/methods.md`, `refs/references.bib`, or submission-package files.",
            "Stage 9.11 registers Results prose in `sections/results.md` and `gate_verdicts/9.11.json`. Stage 9.12 registers Introduction prose in `sections/introduction.md`, `refs/introduction_citation_ledger.csv`, and `gate_verdicts/9.12.json`. The current state intentionally does not create `sections/discussion.md`, `sections/methods.md`, `refs/references.bib`, or submission-package files.",
        )
        body = _replace_once(
            body,
            "| 9.12 | Introduction literature binding | not_started | Draft citation-bound Introduction through resolved references. |",
            "| 9.12 | Introduction literature binding | complete_introduction_literature_bound | Draft citation-bound Introduction through resolved references. |",
        )
        PLAN_PATH.write_text(body, encoding="utf-8")
    if ROADMAP_PATH.exists():
        body = ROADMAP_PATH.read_text(encoding="utf-8")
        body = _replace_once(
            body,
            "9.10 has registered Results subsection architecture, and Stage 9.11 has\nregistered Results drafting. Introduction literature binding, citation\nresolution, Discussion, Methods, and package assembly remain not started.",
            "9.10 has registered Results subsection architecture, Stage 9.11 has\nregistered Results drafting, and Stage 9.12 has registered Introduction\nliterature binding. Discussion, Methods, full reference-library assembly, and\npackage assembly remain not started.",
        )
        body = _replace_once(
            body,
            "| Stage 9. Nature Methods manuscript assembly | Stage 9.11 Results drafting pass registered, Introduction literature binding not started. | The current boundary is evidence intake, official venue-guidance registration, representative methods-paper corpus analysis, narrative-spine selection, claim freeze, paragraph-level claim planning, main figure-spine planning, deterministic PanelForge rendering, supplementary display planning, section-contract planning, front-matter strategy, Results architecture, and Results drafting only. Do not start Introduction, citation resolution, Discussion, Methods, figure legends, review response, or submission packaging without explicit substage authorization. |",
            "| Stage 9. Nature Methods manuscript assembly | Stage 9.12 Introduction literature binding complete, Discussion interpretation map not started. | The current boundary is evidence intake, official venue-guidance registration, representative methods-paper corpus analysis, narrative-spine selection, claim freeze, paragraph-level claim planning, main figure-spine planning, deterministic PanelForge rendering, supplementary display planning, section-contract planning, front-matter strategy, Results architecture, Results drafting, and Introduction literature binding only. Do not start Discussion, Methods, full reference-library assembly, figure legends, review response, or submission packaging without explicit substage authorization. |",
        )
        body = _replace_once(
            body,
            "Stage 9.10 Results subsection architecture has been completed. Stage 9.11 Results drafting pass has been completed. Stage 9.12 Introduction literature binding remains the next unstarted manuscript step. Introduction, citation resolution, Discussion, Methods, and package assembly remain not started.",
            "Stage 9.10 Results subsection architecture has been completed. Stage 9.11 Results drafting pass has been completed. Stage 9.12 Introduction literature binding has been completed. Stage 9.13 Discussion interpretation map remains the next unstarted manuscript step. Discussion, Methods, full reference-library assembly, and package assembly remain not started.",
        )
        ROADMAP_PATH.write_text(body, encoding="utf-8")


def run() -> dict[str, Any]:
    generated_utc = _now()
    access_date = generated_utc[:10]
    commit = _git_sha()
    draft_version = f"introduction-draft@{generated_utc[:10]}@{commit}"
    if STAGING_DIR.exists():
        shutil.rmtree(STAGING_DIR)
    STAGING_DIR.mkdir(parents=True, exist_ok=True)
    introduction_text = _build_introduction(generated_utc, draft_version)
    citation_rows = _citation_rows(access_date)
    _write_text(STAGING_DIR / OUTPUTS["introduction"].relative_to(WORKSPACE), introduction_text)
    _write_csv(STAGING_DIR / OUTPUTS["ledger"].relative_to(WORKSPACE), citation_rows)
    checks = _validate(introduction_text, citation_rows)
    passed = all(check["passed"] for check in checks)
    visible = _visible_text(introduction_text)
    citation_tokens = sorted(set(_citation_tokens(visible)))
    source_types = [row["source_type"] for row in citation_rows]
    review_share = source_types.count("review") / len(source_types) if source_types else 1.0
    gate = {
        "substage": "9.12",
        "timestamp": generated_utc,
        "introduction_draft_version": draft_version,
        "pass": passed,
        "checks": checks,
        "paragraph_count": len(INTRODUCTION_PARAGRAPHS),
        "para_ids": sorted({para_id for paragraph in INTRODUCTION_PARAGRAPHS for para_id in paragraph["para_ids"]}),
        "claim_ids": ["CLM-0001", "CLM-0002"],
        "citation_ids": citation_tokens,
        "citation_count": len(citation_tokens),
        "review_source_share": review_share,
        "review_source_threshold": 0.25,
        "introduction_word_count": _word_count(visible),
        "next_substage": "9.13",
        "outputs": [str(path.relative_to(ROOT)) for path in OUTPUTS.values()],
        "scope_boundary": "Citation-bound Introduction only. No full reference library, Discussion, Methods, figure legends, or submission-package assembly.",
    }
    _write_json(STAGING_DIR / OUTPUTS["gate"].relative_to(WORKSPACE), gate)
    if passed:
        _promote_staging()
        shutil.rmtree(STAGING_DIR)
        _update_registry()
        _update_memory(draft_version, generated_utc, checks)
        _update_roadmap_memory(draft_version)
        _update_docs()
    else:
        quarantine = _quarantine_staging(generated_utc)
        gate["quarantine_path"] = str(quarantine.relative_to(ROOT))
        _write_json(OUTPUTS["gate"], gate)
    return {
        "status": "pass" if passed else "fail",
        "substage": "9.12",
        "introduction_draft_version": draft_version,
        "paragraph_count": len(INTRODUCTION_PARAGRAPHS),
        "introduction_word_count": _word_count(visible),
        "citation_count": len(citation_tokens),
        "review_source_share": review_share,
        "failures": [check for check in checks if not check["passed"]],
        "outputs": gate["outputs"],
        "next_allowed_action": "Proceed to Stage 9.13 Discussion interpretation map after validation and explicit authorization.",
    }


def main() -> int:
    payload = run()
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())

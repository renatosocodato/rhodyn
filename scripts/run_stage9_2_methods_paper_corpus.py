"""Run Stage 9.2 representative methods-paper corpus registration.

Stage 9.2 creates a structural corpus of successful computational methods
papers. It records how strong methods papers present novelty, benchmarking,
biological demonstrations, software, limitations, and availability. It does not
create a bibliography, draft manuscript prose, render figures, or assemble a
submission package.
"""

from __future__ import annotations

import json
import shutil
import subprocess
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from urllib.error import URLError
from urllib.parse import quote
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT / "manuscript" / "nature_methods"
REFS_DIR = WORKSPACE / "refs"
AUDIT_DIR = WORKSPACE / "audits"
GATE_DIR = WORKSPACE / "gate_verdicts"
CACHE_DIR = REFS_DIR / "_cache" / "methods_corpus"
STAGING_DIR = WORKSPACE / "_staging" / "9.2"
QUARANTINE_DIR = WORKSPACE / "_quarantine" / "9.2"
MEMORY_PATH = ROOT / "docs" / "stage9_execution_memory.json"
ROADMAP_MEMORY_PATH = ROOT / "docs" / "roadmap_execution_memory.json"
REGISTRY_PATH = WORKSPACE / "contracts" / "stage9_substage_registry.json"
PLAN_PATH = ROOT / "docs" / "stage9_manuscript_assembly_plan.md"
ROADMAP_PATH = ROOT / "docs" / "roadmap.md"
GATE_9_1 = GATE_DIR / "9.1.json"

OUTPUTS = {
    "corpus": REFS_DIR / "representative_methods_papers.md",
    "archetype": AUDIT_DIR / "methods_paper_archetype_analysis.md",
    "gate": GATE_DIR / "9.2.json",
}

FORBIDDEN_STARTED_PATHS = [
    WORKSPACE / "sections" / "results.md",
    WORKSPACE / "sections" / "introduction.md",
    WORKSPACE / "sections" / "discussion.md",
    WORKSPACE / "sections" / "methods.md",
    WORKSPACE / "sections" / "abstract.md",
    WORKSPACE / "sections" / "data_availability.md",
    WORKSPACE / "sections" / "code_availability.md",
    WORKSPACE / "refs" / "references.bib",
    WORKSPACE / "submission_package" / "pi_review_packet.md",
    WORKSPACE / "submission_package" / "submission_readiness_checklist.md",
    WORKSPACE / "figures" / ".panelforge_commit",
    WORKSPACE / "audits" / "panelforge_render_report.md",
    ROOT / ".venv-panelforge",
    ROOT / "tools" / "panelforge-figures" / ".git",
]

PLANNED_DOI_COUNT = 8
REQUIRED_AXES = ("novelty", "benchmarks", "biology", "software", "limitations", "availability")


@dataclass(frozen=True)
class CorpusPaper:
    paper_id: str
    title: str
    doi: str
    url: str
    journal: str
    year: str
    method_class: str
    novelty: str
    benchmarks: str
    biology: str
    software: str
    limitations: str
    availability: str
    pattern_for_rhodyn: str


PAPERS = [
    CorpusPaper(
        paper_id="MP-001",
        title="Cellpose: a generalist algorithm for cellular segmentation",
        doi="10.1038/s41592-020-01018-x",
        url="https://www.nature.com/articles/s41592-020-01018-x",
        journal="Nature Methods",
        year="2021",
        method_class="generalist image segmentation",
        novelty="Generalist cellular segmentation model positioned against the narrow-specialist bottleneck in microscopy analysis.",
        benchmarks="Compares segmentation behavior across diverse image types and against established specialist approaches.",
        biology="Demonstrates value across heterogeneous cellular imaging contexts rather than one biological specimen.",
        software="Provides user-facing software access and a reusable computational workflow.",
        limitations="Generality depends on image regimes represented by training and validation examples; domain mismatch remains a boundary.",
        availability="Publishes data/software access routes sufficient for reuse and benchmarking.",
        pattern_for_rhodyn="Lead with a general biological bottleneck, then prove practical generality through diverse benchmarks and accessible software.",
    ),
    CorpusPaper(
        paper_id="MP-002",
        title="Squidpy: a scalable framework for spatial omics analysis",
        doi="10.1038/s41592-021-01358-2",
        url="https://www.nature.com/articles/s41592-021-01358-2",
        journal="Nature Methods",
        year="2022",
        method_class="spatial-omics analysis platform",
        novelty="Unifies spatial molecular data processing, graph analysis, image features, and neighborhood statistics in one scalable framework.",
        benchmarks="Uses scalable computation and multiple data modalities to show that the framework handles practical spatial-omics workloads.",
        biology="Connects method behavior to tissue organization, cell neighborhoods, and spatial biological questions.",
        software="Frames the contribution as documented, reusable, and interoperable software rather than as a one-off analysis script.",
        limitations="Usefulness depends on input data quality, modality-specific assumptions, and correct interpretation of spatial statistics.",
        availability="Provides package, documentation, processed examples, and reproducibility routes.",
        pattern_for_rhodyn="Present RhoDyn as a coherent workbench around stable method objects, not as unrelated functions.",
    ),
    CorpusPaper(
        paper_id="MP-003",
        title="CellRank for directed single-cell fate mapping",
        doi="10.1038/s41592-021-01346-6",
        url="https://www.nature.com/articles/s41592-021-01346-6",
        journal="Nature Methods",
        year="2022",
        method_class="single-cell fate inference",
        novelty="Defines a formal inference object for directed fate mapping by combining transition dynamics and terminal-state probabilities.",
        benchmarks="Assesses behavior through comparisons, uncertainty, and applications that test fate-direction inference.",
        biology="Uses biological systems where cell fate progression is interpretable and experimentally meaningful.",
        software="Provides an installable analysis package with examples, tutorials, and reproducible notebooks.",
        limitations="Inference depends on assumptions linking molecular state geometry to future fate probabilities.",
        availability="Records software and data access paths for reproducing examples and extending analyses.",
        pattern_for_rhodyn="Define residence-state inference as a formal method object with explicit assumptions and uncertainty.",
    ),
    CorpusPaper(
        paper_id="MP-004",
        title="A comparison of single-cell trajectory inference methods",
        doi="10.1038/s41587-019-0071-9",
        url="https://www.nature.com/articles/s41587-019-0071-9",
        journal="Nature Biotechnology",
        year="2019",
        method_class="benchmarking and method selection",
        novelty="Benchmarks a crowded trajectory-inference field with standardized tasks, wrappers, datasets, and decision criteria.",
        benchmarks="Uses many synthetic and real datasets to compare accuracy, scalability, stability, and usability across methods.",
        biology="Keeps biological trajectory use cases visible while centering method-selection evidence.",
        software="Provides common interfaces and resources that make external method comparison reproducible.",
        limitations="Benchmark conclusions depend on chosen datasets, metrics, and task definitions.",
        availability="Makes benchmarking inputs, wrappers, and outputs accessible for reuse.",
        pattern_for_rhodyn="Benchmark RhoDyn against amplitude-only, endpoint-only, threshold-only, and generic time-series summaries on shared inputs.",
    ),
    CorpusPaper(
        paper_id="MP-005",
        title="A Python library for probabilistic analysis of single-cell omics data",
        doi="10.1038/s41587-021-01206-w",
        url="https://www.nature.com/articles/s41587-021-01206-w",
        journal="Nature Biotechnology",
        year="2022",
        method_class="probabilistic single-cell software platform",
        novelty="Builds a model family and developer/user interface for probabilistic single-cell analysis rather than one isolated model.",
        benchmarks="Evaluates model behavior across tasks and demonstrates advantages of reusable probabilistic abstractions.",
        biology="Shows how uncertainty-aware modeling improves interpretable biological analysis across single-cell contexts.",
        software="Emphasizes package architecture, API stability, documentation, and extensibility.",
        limitations="Interpretation depends on model assumptions, data preprocessing, and task-specific validation.",
        availability="Provides package, documentation, examples, and versioned software access.",
        pattern_for_rhodyn="Make uncertainty and API stability visible so biological users can reproduce every reported decision.",
    ),
    CorpusPaper(
        paper_id="MP-006",
        title="Generalizing RNA velocity to transient cell states through dynamical modeling",
        doi="10.1038/s41587-020-0591-3",
        url="https://www.nature.com/articles/s41587-020-0591-3",
        journal="Nature Biotechnology",
        year="2020",
        method_class="dynamical single-cell modeling",
        novelty="Extends RNA velocity from steady-state assumptions to transient dynamical regimes.",
        benchmarks="Compares dynamical modeling against simpler velocity assumptions and tests behavior across biological transitions.",
        biology="Uses transient cell-state systems where time-dependent interpretation is the central biological issue.",
        software="Provides a reusable computational implementation for velocity and latent-time analysis.",
        limitations="Dynamical interpretation depends on model identifiability and assumptions about transcriptional kinetics.",
        availability="Provides software and example data routes that support reproduction of core analyses.",
        pattern_for_rhodyn="Frame dwell/residence as a dynamic state variable that can outperform endpoint summaries only under declared assumptions.",
    ),
    CorpusPaper(
        paper_id="MP-007",
        title="Visualizing structure and transitions in high-dimensional biological data",
        doi="10.1038/s41587-019-0336-3",
        url="https://www.nature.com/articles/s41587-019-0336-3",
        journal="Nature Biotechnology",
        year="2019",
        method_class="manifold and transition visualization",
        novelty="Provides a geometry-preserving visualization approach for structure and transitions in high-dimensional biological data.",
        benchmarks="Compares visualization behavior against alternative embeddings on synthetic and biological examples.",
        biology="Connects computational geometry to interpretable developmental and cellular transition structure.",
        software="Provides reusable software for applying the method to new biological datasets.",
        limitations="Visual structure must not be overread as mechanism without supporting validation.",
        availability="Makes implementation and example analyses available for reuse.",
        pattern_for_rhodyn="Keep visualization subordinate to quantitative residence and coupling decisions, while still making state-space intuition readable.",
    ),
    CorpusPaper(
        paper_id="MP-008",
        title="DeepLabCut: markerless pose estimation of user-defined body parts with deep learning",
        doi="10.1038/s41593-018-0209-y",
        url="https://www.nature.com/articles/s41593-018-0209-y",
        journal="Nature Neuroscience",
        year="2018",
        method_class="deep-learning behavior tracking",
        novelty="Turns markerless pose estimation into a user-trainable method for diverse behavioral experiments.",
        benchmarks="Evaluates pose-estimation accuracy and generalization across species, body parts, and experimental contexts.",
        biology="Demonstrates how a computational method enables biological behavior measurement at scale.",
        software="Provides accessible software so non-specialist users can train and deploy the method.",
        limitations="Performance depends on labeled training examples, image quality, and domain transfer.",
        availability="Provides public code and workflow information for adoption and reproduction.",
        pattern_for_rhodyn="Treat usability as part of the method evidence, especially when biologists must inspect parameters and reproduce decisions.",
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


def _fetch_crossref(paper: CorpusPaper, accessed_utc: str, cache_root: Path) -> dict[str, Any]:
    url = f"https://api.crossref.org/works/{quote(paper.doi, safe='')}"
    request = Request(
        url,
        headers={
            "User-Agent": "RhoDyn Stage 9.2 methods-paper corpus register",
            "Accept": "application/json",
        },
    )
    try:
        with urlopen(request, timeout=30) as response:
            payload = json.loads(response.read().decode("utf-8"))
            http_status = int(getattr(response, "status", 200))
    except (URLError, json.JSONDecodeError) as exc:
        return {
            "paper_id": paper.paper_id,
            "doi": paper.doi,
            "url": url,
            "accessed_utc": accessed_utc,
            "status": "fetch_failed",
            "error": str(exc),
        }
    message = payload.get("message", {}) if isinstance(payload, dict) else {}
    title = str((message.get("title") or [""])[0])
    container = str((message.get("container-title") or [""])[0])
    title_ok = paper.title.lower() in title.lower() or title.lower() in paper.title.lower()
    journal_ok = paper.journal.lower() == container.lower()
    status = "fetched" if http_status == 200 and title_ok and journal_ok else "fetched_with_metadata_mismatch"
    cache_payload = {
        "paper_id": paper.paper_id,
        "doi": paper.doi,
        "expected_title": paper.title,
        "expected_journal": paper.journal,
        "crossref_title": title,
        "crossref_journal": container,
        "crossref_url": url,
        "accessed_utc": accessed_utc,
        "http_status": http_status,
        "status": status,
        "message": message,
    }
    cache_path = cache_root / f"{paper.paper_id.lower()}.crossref.json"
    _write_json(cache_path, cache_payload)
    return {**cache_payload, "cache_file": str((CACHE_DIR / cache_path.name).relative_to(ROOT))}


def _markdown_table(rows: list[dict[str, str]], columns: list[str]) -> str:
    lines = ["| " + " | ".join(columns) + " |", "| " + " | ".join("---" for _ in columns) + " |"]
    for row in rows:
        lines.append("| " + " | ".join(str(row.get(column, "")).replace("|", "\\|") for column in columns) + " |")
    return "\n".join(lines)


def _paper_rows(metadata: list[dict[str, Any]]) -> list[dict[str, str]]:
    meta_by_id = {record["paper_id"]: record for record in metadata}
    rows: list[dict[str, str]] = []
    for paper in PAPERS:
        record = meta_by_id.get(paper.paper_id, {})
        rows.append(
            {
                "id": paper.paper_id,
                "paper": paper.title,
                "journal_year": f"{paper.journal} {paper.year}",
                "doi": paper.doi,
                "method_class": paper.method_class,
                "metadata_status": str(record.get("status", "missing")),
                "cache": str(record.get("cache_file", "")),
            }
        )
    return rows


def _axis_rows() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for paper in PAPERS:
        rows.append(
            {
                "id": paper.paper_id,
                "novelty": paper.novelty,
                "benchmarks": paper.benchmarks,
                "biology": paper.biology,
                "software": paper.software,
                "limitations": paper.limitations,
                "availability": paper.availability,
                "rhodyn_pattern": paper.pattern_for_rhodyn,
            }
        )
    return rows


def _build_corpus_markdown(metadata: list[dict[str, Any]], generated_utc: str) -> str:
    return f"""# Representative methods-paper corpus

Generated UTC. {generated_utc}

Stage. 9.2 representative methods-paper corpus.

Scope. This corpus identifies structural patterns from successful computational
methods papers. It is not a reference library for manuscript citation, does not
create `refs/references.bib`, and does not draft RhoDyn manuscript text.

Planned DOI count. {PLANNED_DOI_COUNT}

## DOI-verified corpus

{_markdown_table(_paper_rows(metadata), ["id", "paper", "journal_year", "doi", "method_class", "metadata_status", "cache"])}

## Structural extraction axes

{_markdown_table(_axis_rows(), ["id", "novelty", "benchmarks", "biology", "software", "limitations", "availability", "rhodyn_pattern"])}

## Corpus boundary

These examples define manuscript architecture patterns only. They do not
establish RhoDyn claims, do not substitute for RhoDyn evidence, and do not imply
that RhoDyn generated any prior biological manuscript.
"""


def _build_archetype_markdown(generated_utc: str, checks: list[dict[str, Any]]) -> str:
    check_rows = [
        {
            "check": str(check["name"]),
            "status": "pass" if check["passed"] else "fail",
            "detail": str(check["detail"]),
        }
        for check in checks
    ]
    archetype_rows = [
        {
            "archetype_feature": "Method object appears early",
            "seen_in": "Cellpose, CellRank, scvi-tools, scVelo",
            "rhodyn_implication": "Stage 9.3 should define RhoDyn as residence-state inference for live-cell perturbation data before listing demonstrations.",
        },
        {
            "archetype_feature": "Benchmarks use shared inputs and simpler alternatives",
            "seen_in": "Trajectory benchmark, Cellpose, PHATE, scVelo",
            "rhodyn_implication": "Stage 9.6 and Stage 9.10 should show amplitude-only, endpoint-only, threshold-only, and generic time-series alternatives on the same inputs.",
        },
        {
            "archetype_feature": "Biological demonstrations span more than one system",
            "seen_in": "CellRank, Squidpy, Cellpose, DeepLabCut",
            "rhodyn_implication": "RhoDyn should treat the RhoA/microglia case as depth and use public Stage 7 systems as generality evidence.",
        },
        {
            "archetype_feature": "Software adoption is part of the evidence",
            "seen_in": "scvi-tools, Squidpy, DeepLabCut, Cellpose",
            "rhodyn_implication": "Stage 9.17 must keep install, API, tutorials, version, DOI archive, and command-level reproducibility visible.",
        },
        {
            "archetype_feature": "Limitations are scoped to method assumptions",
            "seen_in": "scVelo, PHATE, trajectory benchmark, CellRank",
            "rhodyn_implication": "RhoDyn should state when residence, reserve-like, bounded-coupling, or routed-output claims are not identifiable from a dataset.",
        },
        {
            "archetype_feature": "Availability supports extension, not only replication",
            "seen_in": "All retained corpus papers",
            "rhodyn_implication": "Stage 9.17 should separate public examples, release archive, DOI, optional reference case, and restricted data boundaries.",
        },
    ]
    return f"""# Methods-paper archetype analysis

Generated UTC. {generated_utc}

## Gate predicate results

{_markdown_table(check_rows, ["check", "status", "detail"])}

## Cross-paper archetype features

{_markdown_table(archetype_rows, ["archetype_feature", "seen_in", "rhodyn_implication"])}

## Narrative pressure for Stage 9.3

The corpus supports a Nature Methods Article architecture in which RhoDyn is
introduced as a method object first, benchmarked against simpler summaries on
shared inputs, demonstrated across public biological systems, and then tied to
software availability and limitations. Stage 9.3 should decide the exact
narrative spine and content-type fit using the sourced venue constraints from
Stage 9.1 and the structural corpus recorded here.
"""


def _validate(metadata: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rendered = [
        path
        for path in (WORKSPACE / "figures" / "rendered").rglob("*")
        if path.is_file() and path.suffix.lower() in {".png", ".pdf", ".svg"}
    ]
    gate_9_1_pass = False
    if GATE_9_1.exists():
        try:
            gate_9_1_pass = _read_json(GATE_9_1).get("pass") is True
        except json.JSONDecodeError:
            gate_9_1_pass = False
    unique_dois = {paper.doi.lower() for paper in PAPERS}
    metadata_ok = len(metadata) == len(PAPERS) and all(record.get("status") == "fetched" for record in metadata)
    axis_ok = all(all(str(getattr(paper, axis)).strip() for axis in REQUIRED_AXES) for paper in PAPERS)
    no_downstream = not any(path.exists() for path in FORBIDDEN_STARTED_PATHS) and not rendered
    return [
        {
            "name": "stage_9_1_gate_passed",
            "passed": gate_9_1_pass,
            "detail": "Stage 9.1 venue guidance exists and passes" if gate_9_1_pass else "Stage 9.1 gate is missing or not passing",
        },
        {
            "name": "corpus_has_planned_doi_count",
            "passed": len(PAPERS) == PLANNED_DOI_COUNT and len(unique_dois) == PLANNED_DOI_COUNT and metadata_ok,
            "detail": f"{len(unique_dois)} unique DOI records verified against planned count {PLANNED_DOI_COUNT}",
        },
        {
            "name": "each_entry_records_required_axes",
            "passed": axis_ok,
            "detail": "Every corpus entry records novelty, benchmarks, biology, software, limitations, and availability",
        },
        {
            "name": "archetype_synthesis_exists",
            "passed": True,
            "detail": "Archetype synthesis generated from cross-paper method, benchmark, biology, software, limitation, and availability patterns",
        },
        {
            "name": "no_downstream_stage9_surfaces_started",
            "passed": no_downstream,
            "detail": "No manuscript sections, reference bibliography, submission package, PanelForge clone, runtime environment, or rendered figures detected",
        },
    ]


def _promote_staging(metadata: list[dict[str, Any]]) -> None:
    for destination in OUTPUTS.values():
        staged = STAGING_DIR / destination.relative_to(WORKSPACE)
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(staged, destination)
    for record in metadata:
        destination = ROOT / str(record["cache_file"])
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
        if substage.get("id") == "9.2":
            substage["status"] = "completed"
    registry["last_completed_substage"] = "9.2"
    _write_json(REGISTRY_PATH, registry)


def _update_memory(corpus_version: str, generated_utc: str, checks: list[dict[str, Any]]) -> None:
    memory = _read_json(MEMORY_PATH)
    memory["generated_utc"] = generated_utc
    memory["current_substage"] = "9.2"
    memory["representative_methods_corpus_started"] = True
    memory["representative_methods_corpus_version"] = corpus_version
    memory["status"] = "stage9_2_methods_corpus_registered"
    memory["next_substage"] = "9.3"
    memory["next_substage_authorized"] = False
    memory["stage9_2_checks"] = checks
    memory.setdefault("completed_substages", [])
    if not any(item.get("substage") == "9.2" for item in memory["completed_substages"]):
        memory["completed_substages"].append(
            {
                "substage": "9.2",
                "status": "pass",
                "pass": True,
                "gate_verdict_path": "manuscript/nature_methods/gate_verdicts/9.2.json",
                "validation_outcome": "Representative computational methods-paper corpus registered for Stage 9 manuscript architecture",
                "evidence_dependencies": [
                    "manuscript/nature_methods/gate_verdicts/9.1.json",
                    "Crossref DOI metadata for the eight retained corpus papers",
                ],
                "files_created_or_modified": [
                    "manuscript/nature_methods/refs/representative_methods_papers.md",
                    "manuscript/nature_methods/audits/methods_paper_archetype_analysis.md",
                    "manuscript/nature_methods/refs/_cache/methods_corpus/",
                    "manuscript/nature_methods/gate_verdicts/9.2.json",
                ],
                "remaining_blockers": [
                    "Stage 9.3 archetype/content-type/narrative-spine decision has not started",
                    "Stage 9.4 claim freeze has not started",
                    "Stage 9.6 figure-to-claim contract has not started",
                    "Stage 9.6b PanelForge rendering remains blocked until Stage 9.6 passes",
                    "Manuscript drafting and reference library construction remain not started",
                ],
            }
        )
    _write_json(MEMORY_PATH, memory)


def _update_roadmap_memory(corpus_version: str) -> None:
    memory = _read_json(ROADMAP_MEMORY_PATH)
    current = memory.setdefault("current_position", {})
    current["active_stage"] = "Stage 9.2 methods-paper corpus registered; manuscript production not started"
    current["stage9_active_gate"] = "Stage 9.2 methods-paper corpus registered; manuscript production not started"
    current["after_stage9_2_methods_corpus"] = (
        "Stage 9.2 registered an eight-DOI representative computational methods-paper corpus and "
        "extracted cross-paper archetype features. Stage 9.3 narrative-spine selection, citation "
        "resolution, manuscript drafting, figure rendering, PanelForge execution, and submission-package "
        "assembly remain not started."
    )
    for stage in memory.get("stage_lock", []):
        if not isinstance(stage, dict) or stage.get("stage") != 9:
            continue
        stage["status"] = "stage9_2_methods_corpus_registered"
        stage["current_gate"] = "Stage 9.2 methods-paper corpus registered; manuscript production not started"
        stage["scope_rule"] = (
            "Stage 9 has completed evidence intake, venue-guidance registration, and representative "
            "methods-paper corpus analysis only. Do not start narrative-spine selection, citation "
            "resolution, drafting, figure rendering, review response, or submission packaging without "
            "explicit substage authorization."
        )
        artifacts = stage.setdefault("artifacts", [])
        for artifact in [
            "manuscript/nature_methods/refs/representative_methods_papers.md",
            "manuscript/nature_methods/audits/methods_paper_archetype_analysis.md",
            "manuscript/nature_methods/refs/_cache/methods_corpus/",
            "manuscript/nature_methods/gate_verdicts/9.2.json",
            "scripts/run_stage9_2_methods_paper_corpus.py",
        ]:
            if artifact not in artifacts:
                artifacts.append(artifact)
        gate = stage.setdefault("gate", [])
        corpus_gate = "Stage 9.2 representative methods-paper corpus is registered from DOI-verified metadata."
        if corpus_gate not in gate:
            gate.append(corpus_gate)
        for subphase in stage.get("subphases", []):
            if isinstance(subphase, dict) and subphase.get("id") == "9.2":
                subphase["status"] = "complete_methods_corpus_registered"
                subphase["evidence"] = "manuscript/nature_methods/gate_verdicts/9.2.json"
                subphase["corpus_version"] = corpus_version
    _write_json(ROADMAP_MEMORY_PATH, memory)


def _update_docs() -> None:
    if PLAN_PATH.exists():
        body = PLAN_PATH.read_text(encoding="utf-8")
        body = body.replace(
            "This repository state serializes the entire Stage 9 v2.1 plan, completes the contract/schema scaffold, completes the Stage 9.0 evidence lock, and registers official Nature Methods venue guidance in Stage 9.1. It does not begin literature lookup, representative-paper corpus construction, manuscript drafting, editorial polishing, PanelForge rendering, or package assembly.",
            "This repository state serializes the entire Stage 9 v2.1 plan, completes the contract/schema scaffold, completes the Stage 9.0 evidence lock, registers official Nature Methods venue guidance in Stage 9.1, and registers the representative methods-paper corpus in Stage 9.2. It does not begin citation resolution, manuscript drafting, editorial polishing, PanelForge rendering, or package assembly.",
        )
        body = body.replace(
            "Stage 9.1 registers official Nature Methods, Nature Portfolio, and Springer Nature guidance in `refs/nature_methods_guidance_register.md`, `refs/_cache/`, `audits/venue_policy_constraints.md`, and `gate_verdicts/9.1.json`. The current state intentionally does not create",
            "Stage 9.1 registers official Nature Methods, Nature Portfolio, and Springer Nature guidance in `refs/nature_methods_guidance_register.md`, `refs/_cache/`, `audits/venue_policy_constraints.md`, and `gate_verdicts/9.1.json`. Stage 9.2 registers the representative computational methods-paper corpus in `refs/representative_methods_papers.md`, `refs/_cache/methods_corpus/`, `audits/methods_paper_archetype_analysis.md`, and `gate_verdicts/9.2.json`. The current state intentionally does not create",
        )
        body = body.replace(
            "| 9.2 | Representative methods-paper corpus | not_started | Create a structural corpus of successful computational methods papers. |",
            "| 9.2 | Representative methods-paper corpus | complete_methods_corpus_registered | Create a structural corpus of successful computational methods papers. |",
        )
        PLAN_PATH.write_text(body, encoding="utf-8")
    if ROADMAP_PATH.exists():
        body = ROADMAP_PATH.read_text(encoding="utf-8")
        body = body.replace(
            "| Stage 9. Nature Methods manuscript assembly | Stage 9.1 venue guidance registered, manuscript production not started. | The current boundary is evidence intake plus official venue-guidance registration only, with PanelForge reserved as a future Stage 9.6b rendering dependency. Do not start the representative methods-paper corpus, citation resolution, figure rendering, drafting, review response, or submission packaging without explicit substage authorization. |",
            "| Stage 9. Nature Methods manuscript assembly | Stage 9.2 methods-paper corpus registered, manuscript production not started. | The current boundary is evidence intake, official venue-guidance registration, and representative methods-paper corpus analysis only, with PanelForge reserved as a future Stage 9.6b rendering dependency. Do not start narrative-spine selection, citation resolution, figure rendering, drafting, review response, or submission packaging without explicit substage authorization. |",
        )
        body = body.replace(
            "Stage 9.2 remains the next unstarted manuscript step.",
            "Stage 9.2 representative methods-paper corpus has been completed. Stage 9.3 remains the next unstarted manuscript step.",
        )
        ROADMAP_PATH.write_text(body, encoding="utf-8")


def run() -> dict[str, Any]:
    generated_utc = _now()
    commit = _git_sha()
    corpus_version = f"methods-corpus@{generated_utc[:10]}@{commit}"
    if STAGING_DIR.exists():
        shutil.rmtree(STAGING_DIR)
    STAGING_DIR.mkdir(parents=True, exist_ok=True)
    cache_root = STAGING_DIR / CACHE_DIR.relative_to(WORKSPACE)
    cache_root.mkdir(parents=True, exist_ok=True)

    metadata = [_fetch_crossref(paper, generated_utc, cache_root) for paper in PAPERS]
    checks = _validate(metadata)
    passed = all(check["passed"] for check in checks)
    gate = {
        "substage": "9.2",
        "timestamp": generated_utc,
        "corpus_version": corpus_version,
        "pass": passed,
        "checks": checks,
        "planned_doi_count": PLANNED_DOI_COUNT,
        "verified_doi_count": sum(record.get("status") == "fetched" for record in metadata),
        "outputs": [str(path.relative_to(ROOT)) for path in OUTPUTS.values()]
        + [str((CACHE_DIR / f"{paper.paper_id.lower()}.crossref.json").relative_to(ROOT)) for paper in PAPERS],
        "scope_boundary": "Methods-paper corpus analysis only. No reference bibliography, citation resolution, drafting, figure rendering, PanelForge execution, or submission-package assembly.",
    }

    _write_text(STAGING_DIR / OUTPUTS["corpus"].relative_to(WORKSPACE), _build_corpus_markdown(metadata, generated_utc))
    _write_text(STAGING_DIR / OUTPUTS["archetype"].relative_to(WORKSPACE), _build_archetype_markdown(generated_utc, checks))
    _write_json(STAGING_DIR / OUTPUTS["gate"].relative_to(WORKSPACE), gate)

    if passed:
        _promote_staging(metadata)
        shutil.rmtree(STAGING_DIR)
        _update_registry()
        _update_memory(corpus_version, generated_utc, checks)
        _update_roadmap_memory(corpus_version)
        _update_docs()
    else:
        quarantine = _quarantine_staging(generated_utc)
        gate["quarantine_path"] = str(quarantine.relative_to(ROOT))
        _write_json(OUTPUTS["gate"], gate)

    return {
        "status": "pass" if passed else "fail",
        "substage": "9.2",
        "corpus_version": corpus_version,
        "planned_doi_count": PLANNED_DOI_COUNT,
        "verified_doi_count": gate["verified_doi_count"],
        "failures": [check for check in checks if not check["passed"]],
        "outputs": gate["outputs"],
    }


def main() -> int:
    payload = run()
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())

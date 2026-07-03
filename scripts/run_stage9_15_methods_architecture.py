"""Run Stage 9.15 Methods architecture.

Stage 9.15 builds the Online Methods structure from repository implementation
and Stage 7 artifacts. It creates a blueprint and a methods-to-code ledger,
but it does not draft the Methods prose, the full reference library, figure
legends, or a submission package.
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
LEDGERS_DIR = WORKSPACE / "ledgers"
GATE_DIR = WORKSPACE / "gate_verdicts"
STAGING_DIR = WORKSPACE / "_staging" / "9.15"
QUARANTINE_DIR = WORKSPACE / "_quarantine" / "9.15"
MEMORY_PATH = ROOT / "docs" / "stage9_execution_memory.json"
ROADMAP_MEMORY_PATH = ROOT / "docs" / "roadmap_execution_memory.json"
REGISTRY_PATH = WORKSPACE / "contracts" / "stage9_substage_registry.json"
PLAN_PATH = ROOT / "docs" / "stage9_manuscript_assembly_plan.md"
ROADMAP_PATH = ROOT / "docs" / "roadmap.md"
SECTION_CONTRACTS = SECTIONS_DIR / "section_contracts.md"
EVIDENCE_MANIFEST = LEDGERS_DIR / "stage9_evidence_manifest.csv"
METHODS_SCHEMA = WORKSPACE / "contracts" / "ledger_schemas" / "methods_to_code.schema.json"
PROJECT_BINDING = WORKSPACE / "contracts" / "stage9_project_binding.json"
GATE_914 = GATE_DIR / "9.14.json"

OUTPUTS = {
    "blueprint": SECTIONS_DIR / "methods_blueprint.md",
    "ledger": LEDGERS_DIR / "methods_to_code_ledger.csv",
    "gate": GATE_DIR / "9.15.json",
}

FORBIDDEN_STARTED_PATHS = [
    SECTIONS_DIR / "methods.md",
    SECTIONS_DIR / "data_availability.md",
    SECTIONS_DIR / "code_availability.md",
    WORKSPACE / "refs" / "references.bib",
    WORKSPACE / "figures" / "figure_legends.md",
    WORKSPACE / "submission_package" / "reporting_summary_REQUIRED.md",
    WORKSPACE / "submission_package" / "pi_review_packet.md",
    WORKSPACE / "submission_package" / "submission_readiness_checklist.md",
]

METHODS_SUBHEADINGS = (
    "Input schemas and preprocessing",
    "Residence windows and amplitude comparators",
    "Bounded-coupling and uncertainty decisions",
    "Reserve-like endpoint construction",
    "Routed-output model comparison",
    "Software surfaces, versioning, and reproducibility",
)

DATASET_VERSION = "stage7.8-methods-readiness@242f06c49e8310b81ac1c06a270bb6810f3f4cfc"
DATASET_DATE = "2026-06-30"


@dataclass(frozen=True)
class MethodStatement:
    stmt_id: str
    subheading: str
    method_role: str
    claim_ids: tuple[str, ...]
    art_id: str
    repo_path: str
    command: str
    dataset_reference: str
    interpretation_boundary: str
    drafting_instruction: str


METHOD_STATEMENTS = (
    MethodStatement(
        stmt_id="MTH-0001",
        subheading="Input schemas and preprocessing",
        method_role="Define tidy trajectory, endpoint, reserve, and coupling-interval input records with explicit validation issues.",
        claim_ids=("CLM-0001", "CLM-0002", "CLM-0003", "CLM-0004"),
        art_id="ART-0016",
        repo_path="src/rhodyn/schema.py",
        command=f"PYTHONPATH=src python3 -m unittest tests.test_schema; dataset_version={DATASET_VERSION}; dataset_date={DATASET_DATE}",
        dataset_reference="RhoDyn schema definitions and Stage 7 method specification locked on 2026-06-30.",
        interpretation_boundary="Input validation identifies malformed tables but cannot rescue missing biological grouping, time units, or merged trace identities.",
        drafting_instruction="Describe accepted columns, optional replicate fields, and failure behavior before any analysis-specific method.",
    ),
    MethodStatement(
        stmt_id="MTH-0002",
        subheading="Residence windows and amplitude comparators",
        method_role="Compute dwell fraction, dwell time, segment count, endpoint, peak, mean, and window-sensitivity summaries.",
        claim_ids=("CLM-0001",),
        art_id="ART-0029",
        repo_path="src/rhodyn/residence.py",
        command=f"PYTHONPATH=src python3 scripts/run_stage7_2_benchmark_harness.py; dataset_version={DATASET_VERSION}; dataset_date={DATASET_DATE}",
        dataset_reference="Synthetic residence benchmark tables generated from Stage 7.2 truth and baseline cases on 2026-06-30.",
        interpretation_boundary="Residence windows are declared analysis choices and do not by themselves identify a causal biological state.",
        drafting_instruction="State the window definition, dwell metrics, amplitude comparators, and required sensitivity reporting.",
    ),
    MethodStatement(
        stmt_id="MTH-0003",
        subheading="Residence windows and amplitude comparators",
        method_role="Adapt public DRG calcium and ERK GPCR trajectories into the same residence-amplitude workflow.",
        claim_ids=("CLM-0001",),
        art_id="ART-0032",
        repo_path="scripts/run_stage7_3_public_signaling.py",
        command="PYTHONPATH=src python3 scripts/run_stage7_3_public_signaling.py; dataset_version=Zenodo:10.5281/zenodo.14907827+10.5281/zenodo.5836623; dataset_date=2026-06-30-derived",
        dataset_reference="DRG calcium Zenodo 10.5281/zenodo.14907827 and ERK GPCR Zenodo 10.5281/zenodo.5836623, converted to derived trajectory tables on 2026-06-30.",
        interpretation_boundary="Public examples test portability of the analysis object and do not establish a universal residence regime.",
        drafting_instruction="Report public-source DOI, derived-table policy, grouping variables, declared windows, and uncertainty summaries.",
    ),
    MethodStatement(
        stmt_id="MTH-0004",
        subheading="Bounded-coupling and uncertainty decisions",
        method_role="Evaluate bounded-coupling decisions with declared margins, interval support, TOST, ROPE, and visible inconclusive states where available.",
        claim_ids=("CLM-0002",),
        art_id="ART-0037",
        repo_path="src/rhodyn/coupling.py",
        command="PYTHONPATH=src python3 scripts/run_stage7_4_endpoint_reserve_routing.py; dataset_version=Zenodo:10.5281/zenodo.5836623-derived; dataset_date=2026-06-30",
        dataset_reference="ERK/Akt bounded-coupling rows derived from Wan 2021 public Zenodo 10.5281/zenodo.5836623 and Stage 7.4 outputs.",
        interpretation_boundary="A passing bounded-coupling decision means equivalence inside the declared margin and context, not proof that all coupling is absent.",
        drafting_instruction="Define margin, interval decision, TOST/ROPE threshold when used, grouping level, and inconclusive handling.",
    ),
    MethodStatement(
        stmt_id="MTH-0005",
        subheading="Reserve-like endpoint construction",
        method_role="Construct reserve-like endpoint coordinates and uncertainty summaries from measured endpoint tables.",
        claim_ids=("CLM-0003",),
        art_id="ART-0039",
        repo_path="src/rhodyn/reserve.py",
        command="PYTHONPATH=src python3 scripts/run_stage7_4_endpoint_reserve_routing.py; dataset_version=public-derived-cell-painting-fixture; dataset_date=2026-06-30",
        dataset_reference="Cell Painting mitotoxicity endpoint rows retained as public-derived Stage 7.4 demonstration tables on 2026-06-30.",
        interpretation_boundary="Reserve-like coordinates remain tied to the measured endpoint and are not direct assays of unmeasured biological reserve capacity.",
        drafting_instruction="Use reserve-like language, define scaling bounds, and state the measured endpoint that anchors the coordinate.",
    ),
    MethodStatement(
        stmt_id="MTH-0006",
        subheading="Routed-output model comparison",
        method_role="Rank reduced endpoint architectures by residual objective and information criteria.",
        claim_ids=("CLM-0004",),
        art_id="ART-0038",
        repo_path="src/rhodyn/compare.py",
        command="PYTHONPATH=src python3 scripts/run_stage7_4_endpoint_reserve_routing.py; dataset_version=public-derived-cell-painting-fixture; dataset_date=2026-06-30",
        dataset_reference="Cell Painting routed-output comparison rows and reduced-alternative decisions retained from Stage 7.4.",
        interpretation_boundary="Model comparison can reject reduced alternatives in the tested endpoint setting but does not identify direct biochemical interactions.",
        drafting_instruction="Describe candidate alternatives, residual objective, ranking rule, and near-tie reporting.",
    ),
    MethodStatement(
        stmt_id="MTH-0007",
        subheading="Bounded-coupling and uncertainty decisions",
        method_role="Apply fixed thresholds and predeclared margins to held-out ERK/Akt paired-reporter contexts.",
        claim_ids=("CLM-0002",),
        art_id="ART-0042",
        repo_path="scripts/run_stage7_5_heldout_validation.py",
        command="PYTHONPATH=src python3 scripts/run_stage7_5_heldout_validation.py; dataset_version=Zenodo:10.5281/zenodo.5836623-heldout; dataset_date=2026-06-30",
        dataset_reference="Held-out inhibitor contexts derived from Wan 2021 public Zenodo 10.5281/zenodo.5836623 on 2026-06-30.",
        interpretation_boundary="Held-out pass and inconclusive contexts are both method outputs; margin-boundary cases cannot be promoted to equivalence.",
        drafting_instruction="State fixed thresholds, held-out contexts, bootstrap level, pass/inconclusive reporting, and controlled-access note policy.",
    ),
    MethodStatement(
        stmt_id="MTH-0008",
        subheading="Residence windows and amplitude comparators",
        method_role="Provide stochastic timing utilities and first-passage summaries for method demonstrations where timing is model-derived or trajectory-derived.",
        claim_ids=("CLM-0001",),
        art_id="ART-0025",
        repo_path="src/rhodyn/sim.py",
        command=f"PYTHONPATH=src python3 -m unittest tests.test_models_sim_compare; dataset_version={DATASET_VERSION}; dataset_date={DATASET_DATE}",
        dataset_reference="Stage 7.1 synthetic truth cases and simulation utilities locked on 2026-06-30.",
        interpretation_boundary="Stochastic timing summaries are not measured cell death, hazard, or injury unless the input endpoint directly supports that interpretation.",
        drafting_instruction="Define first-passage, Gillespie, and tau-leap utilities as method support, with clear model-derived language.",
    ),
    MethodStatement(
        stmt_id="MTH-0009",
        subheading="Software surfaces, versioning, and reproducibility",
        method_role="Expose Python, CLI, backend, workbench, report, and bundle outputs with versioned parameters and checksums.",
        claim_ids=("CLM-0005",),
        art_id="ART-0022",
        repo_path="src/rhodyn/backend_core.py",
        command="PYTHONPATH=src python3 scripts/run_stage7_6_methods_reproducibility.py; dataset_version=RhoDyn-v0.1.0-source-distribution; dataset_date=2026-07-03",
        dataset_reference="RhoDyn v0.1.0 source-distribution reproduction and export-surface parity checked through Stage 7.6 and Stage 7.7.",
        interpretation_boundary="Software reproducibility supports inspection of demonstrated analyses, not a new biological result or private-data reproduction claim.",
        drafting_instruction="Describe API, CLI, backend, workbench, export bundle, checksum, and version surfaces without claiming PyPI publication.",
    ),
)


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


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _visible_text(text: str) -> str:
    return "\n".join(line for line in text.splitlines() if not line.startswith("<!--")).strip()


def _word_count(text: str) -> int:
    return len(re.findall(r"\b[\w-]+\b", text))


def _evidence_artifacts() -> set[str]:
    return {row["art_id"] for row in _read_csv(EVIDENCE_MANIFEST)}


def _schema_fields() -> list[str]:
    schema = _read_json(METHODS_SCHEMA)
    return list(schema["required"])


def _ledger_rows(commit: str) -> list[dict[str, str]]:
    return [
        {
            "methods_stmt_id": statement.stmt_id,
            "art_id": statement.art_id,
            "repo_path": statement.repo_path,
            "commit": commit,
            "command": statement.command,
        }
        for statement in METHOD_STATEMENTS
    ]


def _build_blueprint(generated_utc: str, architecture_version: str) -> str:
    binding = _read_json(PROJECT_BINDING)
    lines = [
        f"<!-- METHODS-BLUEPRINT stage=9.15 generated_utc={generated_utc} architecture_version={architecture_version} -->",
        "",
        "# Stage 9.15 Methods architecture",
        "",
        f"Generated UTC. {generated_utc}",
        "",
        f"Architecture version. {architecture_version}",
        "",
        "Scope. This file defines the Online Methods architecture for the future Nature Methods Article. It is not Methods prose, not a full reference library, not figure legends, not a Reporting Summary, and not a submission package.",
        "",
        f"Software version. {binding['software_name']} {binding['software_version']}.",
        "",
        f"Default locked evidence dataset reference. dataset_version={DATASET_VERSION}; dataset_date={DATASET_DATE}. Public-source derived demonstrations override this default in the statement map when a Zenodo DOI-specific source is used.",
        "",
        "## Methods architecture rule",
        "",
        "Every future Methods subsection must name its input object, executable implementation, data or benchmark version, uncertainty or decision rule, and interpretation boundary before prose is drafted. The Methods draft must remain reconstructable from the methods-to-code ledger and from the locked Stage 7 evidence artifacts.",
        "",
        "## Planned Online Methods order",
        "",
    ]
    for index, subheading in enumerate(METHODS_SUBHEADINGS, start=1):
        statement_ids = [statement.stmt_id for statement in METHOD_STATEMENTS if statement.subheading == subheading]
        lines.append(f"{index}. {subheading}. Methods statement IDs. {'; '.join(statement_ids)}.")
    lines.extend(
        [
            "",
            "## Methods statement map",
            "",
            "| methods_stmt_id | future_methods_subheading | claim_ids | evidence_artifact | repository_implementation | dataset_reference | interpretation_boundary |",
            "| --- | --- | --- | --- | --- | --- | --- |",
        ]
    )
    for statement in METHOD_STATEMENTS:
        lines.append(
            "| "
            + " | ".join(
                [
                    statement.stmt_id,
                    statement.subheading,
                    "; ".join(statement.claim_ids),
                    statement.art_id,
                    statement.repo_path,
                    statement.dataset_reference,
                    statement.interpretation_boundary,
                ]
            )
            + " |"
        )
    lines.extend(["", "## Drafting instructions", ""])
    for statement in METHOD_STATEMENTS:
        lines.append(f"- {statement.stmt_id}. {statement.drafting_instruction}")
    lines.extend(
        [
            "",
            "## Boundaries that must survive Methods drafting",
            "",
            "- Residence windows are declared and sensitivity-tested analysis choices, not automatically discovered causal mechanisms.",
            "- Bounded-coupling claims require declared margins, uncertainty support, and visible inconclusive cases, and do not exclude all slower or context-specific coupling.",
            "- Reserve-like coordinates must remain scoped to measured endpoint behavior unless a direct reserve assay is supplied.",
        "- Routed-output comparisons constrain reduced alternatives in tested endpoint demonstrations but do not identify direct biochemical interactions.",
            "- Software reproducibility demonstrates inspectable reruns of retained Stage 7 evidence, not new biological evidence or private-data reproduction.",
        ]
    )
    return "\n".join(lines)


def _no_downstream_started() -> tuple[bool, list[str]]:
    forbidden = [path.relative_to(ROOT).as_posix() for path in FORBIDDEN_STARTED_PATHS if path.exists()]
    return not forbidden, forbidden


def _validate(blueprint_text: str, ledger_rows: list[dict[str, str]], commit: str) -> list[dict[str, Any]]:
    gate_914_pass = False
    if GATE_914.exists():
        try:
            gate_914_pass = _read_json(GATE_914).get("pass") is True
        except json.JSONDecodeError:
            gate_914_pass = False
    contract_body = SECTION_CONTRACTS.read_text(encoding="utf-8") if SECTION_CONTRACTS.exists() else ""
    evidence_artifacts = _evidence_artifacts() if EVIDENCE_MANIFEST.exists() else set()
    schema_fields = _schema_fields() if METHODS_SCHEMA.exists() else []
    row_fields_ok = all(set(row) == set(schema_fields) for row in ledger_rows)
    ids = [row["methods_stmt_id"] for row in ledger_rows]
    methods_ids_ok = len(ids) == len(set(ids)) and all(re.fullmatch(r"MTH-[0-9]{4}", value) for value in ids)
    repo_paths_ok = all((ROOT / row["repo_path"]).exists() for row in ledger_rows)
    commit_ok = all(row["commit"] == commit and re.fullmatch(r"[0-9a-f]{40}", row["commit"]) for row in ledger_rows)
    commands_ok = all("dataset_version=" in row["command"] and "dataset_date=" in row["command"] for row in ledger_rows)
    artifacts_ok = all(row["art_id"] in evidence_artifacts for row in ledger_rows)
    claim_coverage = sorted({claim for statement in METHOD_STATEMENTS for claim in statement.claim_ids})
    subheading_coverage = sorted({statement.subheading for statement in METHOD_STATEMENTS})
    blueprint_contains_required = all(subheading in blueprint_text for subheading in METHODS_SUBHEADINGS) and all(
        statement.stmt_id in blueprint_text and statement.interpretation_boundary in blueprint_text for statement in METHOD_STATEMENTS
    )
    no_downstream, downstream_paths = _no_downstream_started()
    forbidden_phrases = (
        "absence of all coupling",
        "true biological reserve",
        "literal molecular edge",
        "RhoDyn generated the original",
        "Methods prose starts here",
    )
    forbidden_absent = not any(phrase.lower() in blueprint_text.lower() for phrase in forbidden_phrases)
    return [
        {
            "name": "stage_9_14_gate_passed",
            "passed": gate_914_pass,
            "detail": "Stage 9.14 Discussion drafting exists and passes" if gate_914_pass else "Stage 9.14 gate is missing or not passing",
        },
        {
            "name": "online_methods_contract_available",
            "passed": "SEC-006. Online Methods" in contract_body and all(subheading in contract_body for subheading in METHODS_SUBHEADINGS),
            "detail": "Stage 9.8 Online Methods contract and topical subheadings are available",
        },
        {
            "name": "methods_to_code_ledger_validates",
            "passed": bool(ledger_rows) and row_fields_ok and methods_ids_ok,
            "detail": f"ledger_rows={len(ledger_rows)} schema_fields={';'.join(schema_fields)}",
        },
        {
            "name": "methods_statements_map_to_repo_path_and_commit",
            "passed": repo_paths_ok and commit_ok and artifacts_ok,
            "detail": f"repo_paths_ok={repo_paths_ok} commit={commit} artifacts_ok={artifacts_ok}",
        },
        {
            "name": "dataset_references_include_version_and_date",
            "passed": commands_ok and "dataset_version=" in blueprint_text and DATASET_DATE in blueprint_text,
            "detail": "All ledger commands contain dataset_version and dataset_date, and the blueprint records source dates",
        },
        {
            "name": "all_claims_and_methods_subheadings_covered",
            "passed": claim_coverage == ["CLM-0001", "CLM-0002", "CLM-0003", "CLM-0004", "CLM-0005"]
            and subheading_coverage == sorted(METHODS_SUBHEADINGS),
            "detail": f"claim_coverage={';'.join(claim_coverage)} subheading_count={len(subheading_coverage)}",
        },
        {
            "name": "methods_blueprint_preserves_interpretation_boundaries",
            "passed": blueprint_contains_required and forbidden_absent,
            "detail": "Methods blueprint names statement IDs, code surfaces, data references, and scoped boundaries",
        },
        {
            "name": "no_methods_prose_or_downstream_package_started",
            "passed": no_downstream,
            "detail": "No methods.md, references.bib, figure legends, availability surfaces, or submission package detected"
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
        if substage.get("id") == "9.15":
            substage["status"] = "complete_methods_architecture_registered"
    registry["last_completed_substage"] = "9.15"
    registry["next_substage"] = "9.16"
    _write_json(REGISTRY_PATH, registry)


def _upsert_completed_substage(memory: dict[str, Any], architecture_version: str, checks: list[dict[str, Any]]) -> None:
    record = {
        "substage": "9.15",
        "status": "pass",
        "pass": True,
        "gate_verdict_path": "manuscript/nature_methods/gate_verdicts/9.15.json",
        "validation_outcome": "Online Methods architecture and methods-to-code ledger registered without drafting Methods prose",
        "evidence_dependencies": [
            "manuscript/nature_methods/gate_verdicts/9.14.json",
            "manuscript/nature_methods/sections/section_contracts.md",
            "manuscript/nature_methods/ledgers/stage9_evidence_manifest.csv",
            "docs/stage7_methods_evidence_index.md",
            "case_studies/stage7_methods_readiness/claim_evidence_crosswalk.tsv",
        ],
        "files_created_or_modified": [
            "manuscript/nature_methods/sections/methods_blueprint.md",
            "manuscript/nature_methods/ledgers/methods_to_code_ledger.csv",
            "manuscript/nature_methods/gate_verdicts/9.15.json",
        ],
        "remaining_blockers": [
            "Stage 9.16 Methods drafting pass has not started",
            "Software, data, and code availability assembly has not started",
            "Full reference library and citation audit have not started",
            "Figure legends have not started",
            "Submission-package assembly has not started",
        ],
        "methods_architecture_version": architecture_version,
        "checks": checks,
    }
    entries = [item for item in memory.get("completed_substages", []) if item.get("substage") != "9.15"]
    entries.append(record)
    memory["completed_substages"] = entries


def _update_memory(architecture_version: str, generated_utc: str, checks: list[dict[str, Any]]) -> None:
    memory = _read_json(MEMORY_PATH)
    memory["generated_utc"] = generated_utc
    memory["current_substage"] = "9.15"
    memory["methods_architecture_started"] = True
    memory["methods_drafting_started"] = False
    memory["methods_architecture_version"] = architecture_version
    memory["status"] = "stage9_15_methods_architecture_registered"
    memory["current_gate"] = "Stage 9.15 registered Methods architecture without drafting Methods"
    memory["next_substage"] = "9.16"
    memory["next_substage_authorized"] = False
    memory["stage9_active_gate"] = "Stage 9.15 Methods architecture complete; Methods drafting not started"
    memory["stage9_15_checks"] = checks
    artifacts = memory.setdefault("artifacts", [])
    for artifact in [
        "manuscript/nature_methods/sections/methods_blueprint.md",
        "manuscript/nature_methods/ledgers/methods_to_code_ledger.csv",
        "manuscript/nature_methods/gate_verdicts/9.15.json",
    ]:
        if artifact not in artifacts:
            artifacts.append(artifact)
    memory["gate"] = [
        "Stage 9.-1 contract and schema files exist and pass the scaffold checker.",
        "Stage 9.0 through Stage 9.15 are complete through Methods architecture.",
        "Stage 9.16 through Stage 9.29 plus Stage 9.25b remain not started.",
        "No methods.md, full reference library, figure legends, availability surfaces, or submission package contents are created in this Methods architecture pass.",
        "The Methods architecture maps every Methods statement to code, commit, command, evidence artifact, dataset version/date, and interpretation boundary.",
    ]
    memory["scope_rule"] = (
        "Stage 9 has completed evidence intake, venue-guidance registration, representative methods-paper corpus analysis, "
        "narrative-spine selection, claim freeze, paragraph-level claim planning, main figure-spine planning, deterministic "
        "PanelForge rendering, supplementary display planning, section-contract planning, title/abstract strategy, Results "
        "subsection architecture, Results drafting, Introduction literature binding, Discussion interpretation mapping, "
        "Discussion drafting, and Methods architecture only. Do not start Methods drafting, availability assembly, full "
        "reference library, figure legends, review response, or submission packaging without explicit substage authorization."
    )
    _upsert_completed_substage(memory, architecture_version, checks)
    _write_json(MEMORY_PATH, memory)


def _update_roadmap_memory(architecture_version: str) -> None:
    memory = _read_json(ROADMAP_MEMORY_PATH)
    current = memory.setdefault("current_position", {})
    current["active_stage"] = "Stage 9.15 Methods architecture complete; Methods drafting not started"
    current["stage9_active_gate"] = "Stage 9.15 Methods architecture complete; Methods drafting not started"
    current["after_stage9_15_methods_architecture"] = (
        "Stage 9.15 registered the Online Methods architecture and methods-to-code ledger. "
        "It mapped Methods statements to repo paths, commit, commands, evidence artifacts, and dataset version/date fields. "
        "It did not draft methods.md, assemble availability statements, resolve the full reference library, write figure legends, or package the submission."
    )
    current["current_gate"] = "Methods architecture complete without Methods prose"
    current["next_stage"] = "Stage 9.16 Methods drafting pass"
    for stage in memory.get("stage_lock", []):
        if not isinstance(stage, dict) or stage.get("stage") != 9:
            continue
        stage["status"] = "stage9_15_methods_architecture_registered"
        stage["current_gate"] = "Stage 9.15 registered Methods architecture without drafting Methods"
        stage["scope_rule"] = (
            "Stage 9 has completed evidence intake, venue-guidance registration, representative methods-paper corpus analysis, "
            "narrative-spine selection, claim freeze, paragraph-level claim planning, main figure-spine planning, deterministic "
            "PanelForge rendering, supplementary display planning, section-contract planning, front-matter strategy, Results architecture, "
            "Results drafting, Introduction literature binding, Discussion interpretation mapping, Discussion drafting, and Methods architecture only. "
            "Do not start Methods drafting, availability assembly, full reference library, figure legends, review response, or submission packaging without explicit substage authorization."
        )
        artifacts = stage.setdefault("artifacts", [])
        for artifact in [
            "manuscript/nature_methods/sections/methods_blueprint.md",
            "manuscript/nature_methods/ledgers/methods_to_code_ledger.csv",
            "manuscript/nature_methods/gate_verdicts/9.15.json",
            "scripts/run_stage9_15_methods_architecture.py",
        ]:
            if artifact not in artifacts:
                artifacts.append(artifact)
        gate = stage.setdefault("gate", [])
        methods_gate = "Stage 9.15 Methods architecture maps statements to code, commit, command, dataset version/date, and evidence artifacts."
        if methods_gate not in gate:
            gate.append(methods_gate)
        for subphase in stage.get("subphases", []):
            if isinstance(subphase, dict) and subphase.get("id") == "9.15":
                subphase["status"] = "complete_methods_architecture_registered"
                subphase["evidence"] = "manuscript/nature_methods/gate_verdicts/9.15.json"
                subphase["methods_architecture_version"] = architecture_version
    _write_json(ROADMAP_MEMORY_PATH, memory)


def _replace_once(body: str, old: str, new: str) -> str:
    return body.replace(old, new) if old in body else body


def _update_docs() -> None:
    if PLAN_PATH.exists():
        body = PLAN_PATH.read_text(encoding="utf-8")
        body = _replace_once(
            body,
            "| 9.15 | Methods architecture | not_started | Build Methods structure from repository implementation and Stage 7 artifacts. |",
            "| 9.15 | Methods architecture | complete_methods_architecture_registered | Build Methods structure from repository implementation and Stage 7 artifacts. |",
        )
        body = _replace_once(
            body,
            "Stage 9.14 registers no-subheading Discussion prose in `sections/discussion.md` and `gate_verdicts/9.14.json`. The current state intentionally does not create `sections/methods.md`, `refs/references.bib`, or submission-package files.",
            "Stage 9.14 registers no-subheading Discussion prose in `sections/discussion.md` and `gate_verdicts/9.14.json`. Stage 9.15 registers Methods architecture in `sections/methods_blueprint.md`, `ledgers/methods_to_code_ledger.csv`, and `gate_verdicts/9.15.json`. The current state intentionally does not create `sections/methods.md`, `refs/references.bib`, figure legends, availability statements, or submission-package files.",
        )
        PLAN_PATH.write_text(body, encoding="utf-8")
    if ROADMAP_PATH.exists():
        body = ROADMAP_PATH.read_text(encoding="utf-8")
        body = _replace_once(
            body,
            "| Stage 9. Nature Methods manuscript assembly | Stage 9.14 Discussion drafting pass complete, Online Methods not started. | The current boundary is evidence intake, official venue-guidance registration, representative methods-paper corpus analysis, narrative-spine selection, claim freeze, paragraph-level claim planning, main figure-spine planning, deterministic PanelForge rendering, supplementary display planning, section-contract planning, front-matter strategy, Results architecture, Results drafting, Introduction literature binding, Discussion interpretation mapping, and Discussion drafting only. Do not start Online Methods, full reference-library assembly, figure legends, review response, or submission packaging without explicit substage authorization. |",
            "| Stage 9. Nature Methods manuscript assembly | Stage 9.15 Methods architecture complete, Methods drafting not started. | The current boundary is evidence intake, official venue-guidance registration, representative methods-paper corpus analysis, narrative-spine selection, claim freeze, paragraph-level claim planning, main figure-spine planning, deterministic PanelForge rendering, supplementary display planning, section-contract planning, front-matter strategy, Results architecture, Results drafting, Introduction literature binding, Discussion interpretation mapping, Discussion drafting, and Methods architecture only. Do not start Methods drafting, availability assembly, full reference-library assembly, figure legends, review response, or submission packaging without explicit substage authorization. |",
        )
        body = _replace_once(
            body,
            "Stage 9.10 Results subsection architecture has been completed. Stage 9.11 Results drafting pass has been completed. Stage 9.12 Introduction literature binding has been completed. Stage 9.13 Discussion interpretation map has been completed. Stage 9.14 Discussion drafting pass has been completed. Stage 9.15 Online Methods contract implementation remains the next unstarted manuscript step. Methods, full reference-library assembly, and package assembly remain not started.",
            "Stage 9.10 Results subsection architecture has been completed. Stage 9.11 Results drafting pass has been completed. Stage 9.12 Introduction literature binding has been completed. Stage 9.13 Discussion interpretation map has been completed. Stage 9.14 Discussion drafting pass has been completed. Stage 9.15 Methods architecture has been completed. Stage 9.16 Methods drafting pass remains the next unstarted manuscript step. Methods prose, availability assembly, full reference-library assembly, figure legends, and package assembly remain not started.",
        )
        ROADMAP_PATH.write_text(body, encoding="utf-8")


def run() -> dict[str, Any]:
    generated_utc = _now()
    commit = _git_sha()
    architecture_version = f"methods-architecture@{generated_utc[:10]}@{commit}"
    if STAGING_DIR.exists():
        shutil.rmtree(STAGING_DIR)
    STAGING_DIR.mkdir(parents=True, exist_ok=True)
    blueprint_text = _build_blueprint(generated_utc, architecture_version)
    ledger_rows = _ledger_rows(commit)
    _write_text(STAGING_DIR / OUTPUTS["blueprint"].relative_to(WORKSPACE), blueprint_text)
    _write_csv(STAGING_DIR / OUTPUTS["ledger"].relative_to(WORKSPACE), ledger_rows, _schema_fields())
    checks = _validate(blueprint_text, ledger_rows, commit)
    passed = all(check["passed"] for check in checks)
    visible = _visible_text(blueprint_text)
    gate = {
        "substage": "9.15",
        "timestamp": generated_utc,
        "methods_architecture_version": architecture_version,
        "pass": passed,
        "checks": checks,
        "methods_statement_count": len(METHOD_STATEMENTS),
        "methods_subheading_count": len(METHODS_SUBHEADINGS),
        "methods_blueprint_word_count": _word_count(visible),
        "ledger_row_count": len(ledger_rows),
        "claim_ids": ["CLM-0001", "CLM-0002", "CLM-0003", "CLM-0004", "CLM-0005"],
        "next_substage": "9.16",
        "outputs": [str(path.relative_to(ROOT)) for path in OUTPUTS.values()],
        "scope_boundary": "Methods architecture only. No methods.md, full reference library, figure legends, availability statements, Reporting Summary, or submission-package assembly.",
    }
    _write_json(STAGING_DIR / OUTPUTS["gate"].relative_to(WORKSPACE), gate)
    if passed:
        _promote_staging()
        shutil.rmtree(STAGING_DIR)
        _update_registry()
        _update_memory(architecture_version, generated_utc, checks)
        _update_roadmap_memory(architecture_version)
        _update_docs()
    else:
        quarantine = _quarantine_staging(generated_utc)
        gate["quarantine_path"] = str(quarantine.relative_to(ROOT))
        _write_json(OUTPUTS["gate"], gate)
    return {
        "status": "pass" if passed else "fail",
        "substage": "9.15",
        "methods_architecture_version": architecture_version,
        "methods_statement_count": len(METHOD_STATEMENTS),
        "ledger_row_count": len(ledger_rows),
        "methods_blueprint_word_count": _word_count(visible),
        "failures": [check for check in checks if not check["passed"]],
        "outputs": gate["outputs"],
        "next_allowed_action": "Proceed to Stage 9.16 Methods drafting pass after validation and explicit authorization.",
    }


def main() -> int:
    payload = run()
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())

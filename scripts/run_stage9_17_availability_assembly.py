"""Run Stage 9.17 software, data, and code availability assembly.

Stage 9.17 creates reader-facing data/code availability statements, a
reproducibility command index, and a Reporting Summary requirement placeholder.
It does not create the full reference library, figure legends, Supplementary
Methods, or the final submission package.
"""

from __future__ import annotations

import csv
import json
import re
import shutil
import subprocess
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT / "manuscript" / "nature_methods"
SECTIONS_DIR = WORKSPACE / "sections"
LEDGERS_DIR = WORKSPACE / "ledgers"
GATE_DIR = WORKSPACE / "gate_verdicts"
SUBMISSION_DIR = WORKSPACE / "submission_package"
STAGING_DIR = WORKSPACE / "_staging" / "9.17"
QUARANTINE_DIR = WORKSPACE / "_quarantine" / "9.17"
MEMORY_PATH = ROOT / "docs" / "stage9_execution_memory.json"
ROADMAP_MEMORY_PATH = ROOT / "docs" / "roadmap_execution_memory.json"
REGISTRY_PATH = WORKSPACE / "contracts" / "stage9_substage_registry.json"
PLAN_PATH = ROOT / "docs" / "stage9_manuscript_assembly_plan.md"
ROADMAP_PATH = ROOT / "docs" / "roadmap.md"
PROJECT_BINDING = WORKSPACE / "contracts" / "stage9_project_binding.json"
GATE_916 = GATE_DIR / "9.16.json"
ZENODO_REPORT = ROOT / "docs" / "zenodo_publication_report.json"
PUBLIC_RELEASE_REPORT = ROOT / "docs" / "public_release_integrity_report.json"
STAGE7_COMMANDS = ROOT / "case_studies" / "stage7_methods_reproducibility" / "methods_reproducibility_commands.tsv"

OUTPUTS = {
    "data_availability": SECTIONS_DIR / "data_availability.md",
    "code_availability": SECTIONS_DIR / "code_availability.md",
    "command_index": LEDGERS_DIR / "reproducibility_command_index.md",
    "reporting_summary": SUBMISSION_DIR / "reporting_summary_REQUIRED.md",
    "gate": GATE_DIR / "9.17.json",
}

FORBIDDEN_STARTED_PATHS = [
    WORKSPACE / "refs" / "references.bib",
    WORKSPACE / "figures" / "figure_legends.md",
    WORKSPACE / "supplementary" / "supplementary_methods.md",
    SUBMISSION_DIR / "pi_review_packet.md",
    SUBMISSION_DIR / "submission_readiness_checklist.md",
]

PUBLIC_DATA_SOURCES = (
    {
        "label": "DRG calcium live-cell trajectories",
        "record": "https://zenodo.org/records/14907827",
        "doi": "10.5281/zenodo.14907827",
        "derived_outputs": "case_studies/stage7_public_signaling/drg_calcium_*",
    },
    {
        "label": "ERK GPCR and ERK/Akt reporter trajectories",
        "record": "https://zenodo.org/records/5836623",
        "doi": "10.5281/zenodo.5836623",
        "derived_outputs": "case_studies/stage7_public_signaling/erk_gpcr_* and case_studies/stage7_endpoint_reserve_routing/erk_akt_*",
    },
    {
        "label": "Cell Painting and MitoTox endpoint tables",
        "record": "https://zenodo.org/records/10011861",
        "doi": "10.5281/zenodo.10011861",
        "derived_outputs": "case_studies/stage7_endpoint_reserve_routing/cell_painting_*",
    },
)

OPTIONAL_RHOA_REFERENCE_CASE = {
    "repo": "https://github.com/renatosocodato/windowed_rhoA_model",
    "commit": "e63cc93a4b23d8b3d27cf25136b00d53fa6144f4",
    "software_doi": "10.5281/zenodo.19796404",
    "data_doi": "10.5281/zenodo.19796406",
}

DATASET_VERSION = "stage7.8-methods-readiness@242f06c49e8310b81ac1c06a270bb6810f3f4cfc"
DATASET_DATE = "2026-06-30"
SOFTWARE_VERSION = "v0.1.0"

FORBIDDEN_VISIBLE_PHRASES = (
    "upon request",
    "available on request",
    "available from the authors",
    "data not shown",
    "contact the authors",
    "/" + "Users/",
    "/" + "Volumes/",
    "Library/" + "LaunchAgents",
    "s" + "k-",
    "g" + "hp_",
    "github" + "_pat_",
)


@dataclass(frozen=True)
class ReleaseFacts:
    repo_url: str
    release_url: str
    release_tag: str
    release_commit: str
    version_doi: str
    concept_doi: str
    record_url: str
    license_name: str
    pypi_status: str
    panelforge_name: str
    panelforge_version_doi: str
    panelforge_concept_doi: str
    panelforge_repo: str
    panelforge_ref: str
    panelforge_render_cmd: str
    panelforge_validate_cmd: str
    panelforge_install_alt: str
    panelforge_license: str


@dataclass(frozen=True)
class CommandRow:
    command_id: str
    art_id: str
    command: str
    expected_output: str
    software_version: str
    purpose: str


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


def _git_commit_exists(commit: str) -> bool:
    result = subprocess.run(
        ["git", "cat-file", "-t", commit],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    return result.returncode == 0 and result.stdout.strip() == "commit"


def _git_tag_commit(tag: str) -> str:
    result = subprocess.run(
        ["git", "rev-parse", f"{tag}^{{commit}}"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    return result.stdout.strip() if result.returncode == 0 else ""


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_text(path: Path, body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body.rstrip() + "\n", encoding="utf-8")


def _read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def _visible_text(text: str) -> str:
    return "\n".join(line for line in text.splitlines() if not line.startswith("<!--")).strip()


def _url_resolves(url: str, timeout: float = 12.0) -> dict[str, Any]:
    headers = {"User-Agent": "RhoDyn-stage9-availability-check/0.1"}
    for method in ("HEAD", "GET"):
        request = urllib.request.Request(url, method=method, headers=headers)
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                return {
                    "url": url,
                    "method": method,
                    "status": response.status,
                    "final_url": response.geturl(),
                    "resolved": 200 <= response.status < 400,
                }
        except urllib.error.HTTPError as exc:
            if method == "HEAD" and exc.code in {403, 405}:
                continue
            return {
                "url": url,
                "method": method,
                "status": exc.code,
                "final_url": getattr(exc, "url", url),
                "resolved": 200 <= exc.code < 400,
                "error": str(exc),
            }
        except urllib.error.URLError as exc:
            if method == "HEAD":
                continue
            return {
                "url": url,
                "method": method,
                "status": None,
                "final_url": url,
                "resolved": False,
                "error": str(exc.reason),
            }
    return {"url": url, "status": None, "final_url": url, "resolved": False, "error": "unresolved"}


def _release_facts() -> ReleaseFacts:
    binding = _read_json(PROJECT_BINDING)
    publication = _read_json(ZENODO_REPORT)
    public_release = _read_json(PUBLIC_RELEASE_REPORT)
    figure_engine = binding.get("figure_engine_binding", {})
    return ReleaseFacts(
        repo_url=str(binding["repo_url"]),
        release_url=str(publication["github_release"]),
        release_tag=str(publication["release_tag"]),
        release_commit=str(publication["release_commit"]),
        version_doi=str(publication["version_doi"]),
        concept_doi=str(publication["concept_doi"]),
        record_url=str(publication["record_url"]),
        license_name="Apache-2.0",
        pypi_status="not claimed for RhoDyn v0.1.0",
        panelforge_name=str(figure_engine["name"]),
        panelforge_version_doi=str(figure_engine["version_doi"]),
        panelforge_concept_doi=str(figure_engine["concept_doi"]),
        panelforge_repo=str(figure_engine["repo_url"]),
        panelforge_ref=str(figure_engine["pinned_ref"]),
        panelforge_render_cmd=str(figure_engine["render_cmd"]),
        panelforge_validate_cmd=str(figure_engine["validate_cmd"]),
        panelforge_install_alt=str(figure_engine["install_alt"]),
        panelforge_license=str(figure_engine["license"]),
    )


def _doi_url(doi: str) -> str:
    return f"https://doi.org/{doi}"


def _command_rows(facts: ReleaseFacts) -> list[CommandRow]:
    source_rows = _read_tsv(STAGE7_COMMANDS) if STAGE7_COMMANDS.exists() else []
    rows: list[CommandRow] = []
    for idx, row in enumerate(source_rows, start=1):
        phase = row.get("phase", f"stage7-{idx}").lower().replace(" ", "-")
        rows.append(
            CommandRow(
                command_id=f"CMD-{idx:03d}",
                art_id=f"ART-REPRO-{idx:03d}",
                command=row["command"],
                expected_output=row["purpose"],
                software_version=SOFTWARE_VERSION,
                purpose=f"{row['phase']} evidence regeneration",
            )
        )
    extra_rows = [
        CommandRow(
            command_id="CMD-008",
            art_id="ART-REPRO-008",
            command="python scripts/run_stage7_7_usability_rehearsal.py",
            expected_output="case_studies/stage7_usability_rehearsal/stage7_7_usability_gate_report.json",
            software_version=SOFTWARE_VERSION,
            purpose="Workbench usability and report-export parity",
        ),
        CommandRow(
            command_id="CMD-009",
            art_id="ART-REPRO-009",
            command="python scripts/run_stage7_8_methods_readiness.py",
            expected_output="case_studies/stage7_methods_readiness/stage7_8_methods_readiness_gate_report.json",
            software_version=SOFTWARE_VERSION,
            purpose="Methods-evidence readiness package",
        ),
        CommandRow(
            command_id="CMD-010",
            art_id="ART-REPRO-010",
            command="python scripts/check_release.py",
            expected_output="release validation report printed to stdout",
            software_version=SOFTWARE_VERSION,
            purpose="Release-surface integrity check",
        ),
        CommandRow(
            command_id="CMD-011",
            art_id="ART-REPRO-011",
            command=facts.panelforge_render_cmd,
            expected_output="manuscript/nature_methods/figures/rendered/FIG-001 through FIG-006 in PDF, PNG, and SVG",
            software_version=f"{facts.panelforge_name} {facts.panelforge_ref}; DOI {facts.panelforge_version_doi}",
            purpose="Render the figure panels used by the methods-manuscript display spine",
        ),
        CommandRow(
            command_id="CMD-012",
            art_id="ART-REPRO-012",
            command=facts.panelforge_validate_cmd,
            expected_output="figure manifest validation output",
            software_version=f"{facts.panelforge_name} {facts.panelforge_ref}; DOI {facts.panelforge_version_doi}",
            purpose="Validate the figure manifest before rendering",
        ),
    ]
    return rows + extra_rows


def _build_data_availability(facts: ReleaseFacts, generated_utc: str) -> str:
    public_lines = "\n".join(
        f"- {source['label']}. Source record {source['record']}; DOI {_doi_url(source['doi'])}; retained derived outputs `{source['derived_outputs']}`."
        for source in PUBLIC_DATA_SOURCES
    )
    return f"""<!-- DATA-AVAILABILITY stage=9.17 generated_utc={generated_utc} -->

# Data availability

The evidence tables used for the RhoDyn Nature Methods Article are retained with the RhoDyn {SOFTWARE_VERSION} source release and software archive. The citable release is available from {facts.repo_url} and the Zenodo version DOI {_doi_url(facts.version_doi)}. The concept DOI {_doi_url(facts.concept_doi)} resolves to the current RhoDyn software concept. The released repository contains synthetic truth cases, public-derived trajectory tables, public-derived endpoint tables, reserve-like summaries, bounded-coupling summaries, routed-output comparison outputs, held-out validation outputs, checksums, and report files needed to inspect the manuscript evidence set.

Public source datasets used to construct the retained derived demonstrations are:

{public_lines}

Raw public source archives are not duplicated in the repository when they can be recovered from their public records. The retained derived tables preserve the identifiers, condition fields, time or endpoint variables, grouping fields when available, declared analysis parameters, and output summaries required to reproduce the RhoDyn method demonstrations. Controlled-access or private microscopy data are not required for the RhoDyn method-evidence claims in this Article.

The RhoA/microglia manuscript materials are treated as an optional biological reference use case rather than as hidden inputs to the RhoDyn methods evidence. That separate reference case is available at {OPTIONAL_RHOA_REFERENCE_CASE['repo']} pinned to commit `{OPTIONAL_RHOA_REFERENCE_CASE['commit']}`, with software archive DOI {_doi_url(OPTIONAL_RHOA_REFERENCE_CASE['software_doi'])} and data/replication DOI {_doi_url(OPTIONAL_RHOA_REFERENCE_CASE['data_doi'])}. Those materials illustrate a motivating biological context, but the RhoDyn package, benchmarks, and public demonstrations do not depend on manuscript-private raw microscopy or unpublished model files.
"""


def _build_code_availability(facts: ReleaseFacts, generated_utc: str) -> str:
    return f"""<!-- CODE-AVAILABILITY stage=9.17 generated_utc={generated_utc} -->

# Code availability

RhoDyn source code is available at {facts.repo_url}. The citable software release used for this Article is {SOFTWARE_VERSION}, GitHub release {facts.release_url}, pinned to commit `{facts.release_commit}` and archived at Zenodo version DOI {_doi_url(facts.version_doi)}. The Zenodo concept DOI {_doi_url(facts.concept_doi)} resolves to the latest RhoDyn software record, and the public record for this version is {facts.record_url}. The release is distributed under the {facts.license_name} license and includes the Python package, command-line interface, backend service code, workbench interface, documentation, tests, synthetic examples, public-derived case-study tables, and reproducibility scripts.

The versioned release is the authoritative code record for this Article. PyPI publication is not claimed for {SOFTWARE_VERSION}; package-index distribution remains a later release decision. The reproducibility commands in `manuscript/nature_methods/ledgers/reproducibility_command_index.md` define the reviewable routes used to regenerate the retained evidence surfaces from the released repository.

Figure rendering used {facts.panelforge_name} {facts.panelforge_ref}. The citable PanelForge version DOI is {_doi_url(facts.panelforge_version_doi)}, the concept DOI is {_doi_url(facts.panelforge_concept_doi)}, and the source repository is {facts.panelforge_repo}. The figure render command recorded for this Article is `{facts.panelforge_render_cmd}` and the corresponding manifest-validation command is `{facts.panelforge_validate_cmd}`. A reproducible install route for the pinned renderer is `{facts.panelforge_install_alt}`. PanelForge is distributed under the {facts.panelforge_license} license.
"""


def _build_command_index(rows: list[CommandRow], facts: ReleaseFacts, generated_utc: str) -> str:
    lines = [
        f"<!-- REPRODUCIBILITY-COMMAND-INDEX stage=9.17 generated_utc={generated_utc} -->",
        "",
        "# Reproducibility command index",
        "",
        f"Commands are run from the root of the RhoDyn repository at release tag `{facts.release_tag}` and commit `{facts.release_commit}` unless a command states a different tool boundary. RhoDyn commands use RhoDyn {SOFTWARE_VERSION}. PanelForge commands use {facts.panelforge_name} {facts.panelforge_ref} with version DOI {_doi_url(facts.panelforge_version_doi)}.",
        "",
        "| Command ID | Analysis output | Command | Expected output | Software version | Purpose |",
        "|---|---|---|---|---|---|",
    ]
    for row in rows:
        lines.append(
            f"| {row.command_id} | {row.art_id} | `{row.command}` | {row.expected_output} | {row.software_version} | {row.purpose} |"
        )
    lines.extend(
        [
            "",
            "The command index is a manuscript-facing map of the reproducibility routes. It does not replace the source release, the Zenodo archive, or the public source records listed in the availability statements.",
        ]
    )
    return "\n".join(lines)


def _build_reporting_summary(facts: ReleaseFacts, generated_utc: str) -> str:
    return f"""<!-- REPORTING-SUMMARY-REQUIRED stage=9.17 generated_utc={generated_utc} -->

# Reporting Summary REQUIRED

Nature Methods requires a Reporting Summary for this Article. This file registers that requirement before final submission-package assembly. It is not the completed journal form and does not replace the Springer Nature Reporting Summary template.

## Registered scope

- Manuscript target. Nature Methods Article.
- Software method. RhoDyn {SOFTWARE_VERSION}.
- Citable software record. {_doi_url(facts.version_doi)}.
- Public repository. {facts.repo_url}.
- Pinned release commit. `{facts.release_commit}`.
- Code availability section. `manuscript/nature_methods/sections/code_availability.md`.
- Data availability section. `manuscript/nature_methods/sections/data_availability.md`.
- Reproducibility command index. `manuscript/nature_methods/ledgers/reproducibility_command_index.md`.
- Panel renderer record. {facts.panelforge_name} {facts.panelforge_ref}, DOI {_doi_url(facts.panelforge_version_doi)}.

## Completion requirement before submission

The final Reporting Summary must be completed during the submission-package stage with the study design, statistics, software, code availability, data availability, biological materials, and method-specific reporting fields required by Nature Methods. The current file exists only to prevent omission of that required form from downstream package assembly.
"""


def _no_forbidden_phrases(texts: dict[str, str]) -> tuple[bool, list[str]]:
    failures: list[str] = []
    for name, text in texts.items():
        visible = _visible_text(text).lower()
        for phrase in FORBIDDEN_VISIBLE_PHRASES:
            if phrase.lower() in visible:
                failures.append(f"{name}: {phrase}")
    return not failures, failures


def _no_downstream_started() -> tuple[bool, list[str]]:
    forbidden = [path.relative_to(ROOT).as_posix() for path in FORBIDDEN_STARTED_PATHS if path.exists()]
    return not forbidden, forbidden


def _validate_command_rows(rows: list[CommandRow]) -> tuple[bool, list[str]]:
    failures: list[str] = []
    required_ids = {"command_id", "art_id", "command", "expected_output", "software_version"}
    for row in rows:
        payload = row.__dict__
        missing = [field for field in required_ids if not payload.get(field)]
        if missing:
            failures.append(f"{row.command_id or 'unknown'} missing {','.join(missing)}")
    if len({row.command_id for row in rows}) != len(rows):
        failures.append("command IDs must be unique")
    if len(rows) < 10:
        failures.append("command index must include Stage 7, release, and PanelForge commands")
    return not failures, failures


def _validate(texts: dict[str, str], rows: list[CommandRow], facts: ReleaseFacts, url_checks: list[dict[str, Any]], commit: str) -> list[dict[str, Any]]:
    gate_916_pass = False
    if GATE_916.exists():
        try:
            gate_916_pass = _read_json(GATE_916).get("pass") is True
        except json.JSONDecodeError:
            gate_916_pass = False
    forbidden_ok, forbidden_hits = _no_forbidden_phrases(texts)
    downstream_ok, downstream_paths = _no_downstream_started()
    command_rows_ok, command_row_failures = _validate_command_rows(rows)
    all_visible = "\n".join(_visible_text(text) for text in texts.values())
    urls_ok = all(item.get("resolved") for item in url_checks)
    release_tag_commit = _git_tag_commit(facts.release_tag)
    commit_ok = _git_commit_exists(facts.release_commit) and release_tag_commit == facts.release_commit
    reporting = texts["reporting_summary"]
    panel_required = facts.panelforge_version_doi in all_visible and facts.panelforge_render_cmd in all_visible
    availability_required = all(
        phrase in all_visible
        for phrase in [
            facts.repo_url,
            facts.release_commit,
            facts.version_doi,
            facts.concept_doi,
            facts.record_url,
            OPTIONAL_RHOA_REFERENCE_CASE["commit"],
            OPTIONAL_RHOA_REFERENCE_CASE["data_doi"],
            "10.5281/zenodo.14907827",
            "10.5281/zenodo.5836623",
            "10.5281/zenodo.10011861",
        ]
    )
    return [
        {
            "name": "stage_9_16_gate_passed",
            "passed": gate_916_pass,
            "detail": "Stage 9.16 Methods drafting exists and passes" if gate_916_pass else "Stage 9.16 gate is missing or not passing",
        },
        {
            "name": "doi_and_repo_urls_resolve",
            "passed": urls_ok,
            "detail": url_checks,
        },
        {
            "name": "release_commit_pinned",
            "passed": commit_ok,
            "detail": f"release_commit={facts.release_commit} tag_commit={release_tag_commit} current_commit={commit}",
        },
        {
            "name": "availability_identifiers_present",
            "passed": availability_required,
            "detail": "software, source data, public examples, and optional RhoA reference-case identifiers are present",
        },
        {
            "name": "no_upon_request_or_local_path_language",
            "passed": forbidden_ok,
            "detail": "No upon-request wording, local path, LaunchAgent path, or credential-like token found" if forbidden_ok else "; ".join(forbidden_hits),
        },
        {
            "name": "reporting_summary_registered_required",
            "passed": "Reporting Summary REQUIRED" in reporting and "not the completed journal form" in reporting,
            "detail": "Reporting Summary requirement is registered without completing the final submission form",
        },
        {
            "name": "panelforge_version_and_render_command_recorded",
            "passed": panel_required,
            "detail": f"PanelForge DOI {facts.panelforge_version_doi}; render command {facts.panelforge_render_cmd}",
        },
        {
            "name": "command_index_schema_fields_present",
            "passed": command_rows_ok,
            "detail": "Command rows include command_id, art_id, command, expected_output, and software_version"
            if command_rows_ok
            else "; ".join(command_row_failures),
        },
        {
            "name": "no_reference_legend_supplement_or_full_package_started",
            "passed": downstream_ok,
            "detail": "No references.bib, figure legends, Supplementary Methods, PI packet, or readiness checklist detected"
            if downstream_ok
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
        if substage.get("id") == "9.17":
            substage["status"] = "complete_availability_assembled"
    registry["last_completed_substage"] = "9.17"
    registry["next_substage"] = "9.18"
    _write_json(REGISTRY_PATH, registry)


def _upsert_completed_substage(memory: dict[str, Any], checks: list[dict[str, Any]]) -> None:
    record = {
        "substage": "9.17",
        "status": "pass",
        "pass": True,
        "gate_verdict_path": "manuscript/nature_methods/gate_verdicts/9.17.json",
        "validation_outcome": "Data availability, code availability, reproducibility command index, and Reporting Summary requirement registered",
        "evidence_dependencies": [
            "manuscript/nature_methods/gate_verdicts/9.16.json",
            "docs/zenodo_publication_report.json",
            "docs/public_release_integrity_report.json",
            "manuscript/nature_methods/contracts/stage9_project_binding.json",
            "case_studies/stage7_methods_reproducibility/methods_reproducibility_commands.tsv",
        ],
        "files_created_or_modified": [
            "manuscript/nature_methods/sections/data_availability.md",
            "manuscript/nature_methods/sections/code_availability.md",
            "manuscript/nature_methods/ledgers/reproducibility_command_index.md",
            "manuscript/nature_methods/submission_package/reporting_summary_REQUIRED.md",
            "manuscript/nature_methods/gate_verdicts/9.17.json",
        ],
        "remaining_blockers": [
            "Full reference library and citation audit have not started",
            "Figure legends have not started",
            "Supplementary Methods have not started",
            "Full submission-package assembly has not started beyond the Reporting Summary requirement placeholder",
        ],
        "checks": checks,
    }
    entries = [item for item in memory.get("completed_substages", []) if item.get("substage") != "9.17"]
    entries.append(record)
    memory["completed_substages"] = entries


def _update_memory(generated_utc: str, checks: list[dict[str, Any]]) -> None:
    memory = _read_json(MEMORY_PATH)
    memory["generated_utc"] = generated_utc
    memory["current_substage"] = "9.17"
    memory["availability_assembly_started"] = True
    memory["reporting_summary_placeholder_started"] = True
    memory["status"] = "stage9_17_availability_assembled"
    memory["current_gate"] = "Stage 9.17 registered data/code availability and Reporting Summary placeholder"
    memory["next_substage"] = "9.18"
    memory["next_substage_authorized"] = False
    memory["stage9_active_gate"] = "Stage 9.17 availability assembly complete; Supplementary Methods not started"
    memory["stage9_17_checks"] = checks
    artifacts = memory.setdefault("artifacts", [])
    for artifact in [
        "manuscript/nature_methods/sections/data_availability.md",
        "manuscript/nature_methods/sections/code_availability.md",
        "manuscript/nature_methods/ledgers/reproducibility_command_index.md",
        "manuscript/nature_methods/submission_package/reporting_summary_REQUIRED.md",
        "manuscript/nature_methods/gate_verdicts/9.17.json",
    ]:
        if artifact not in artifacts:
            artifacts.append(artifact)
    memory["gate"] = [
        "Stage 9.-1 contract and schema files exist and pass the scaffold checker.",
        "Stage 9.0 through Stage 9.17 are complete through availability assembly.",
        "Stage 9.18 through Stage 9.29 plus Stage 9.25b remain not started.",
        "No full reference library, figure legends, supplementary methods, PI review packet, or submission readiness checklist are created in this availability pass.",
        "Reporting Summary is registered as required but not completed as the final journal form.",
    ]
    memory["scope_rule"] = (
        "Stage 9 has completed evidence intake, venue-guidance registration, representative methods-paper corpus analysis, "
        "narrative-spine selection, claim freeze, paragraph-level claim planning, main figure-spine planning, deterministic "
        "PanelForge rendering, supplementary display planning, section-contract planning, title/abstract strategy, Results "
        "subsection architecture, Results drafting, Introduction literature binding, Discussion interpretation mapping, "
        "Discussion drafting, Methods architecture, Methods drafting, and availability assembly only. Do not start the full "
        "reference library, figure legends, supplementary methods, or final submission package without explicit substage authorization."
    )
    _upsert_completed_substage(memory, checks)
    _write_json(MEMORY_PATH, memory)


def _update_roadmap_memory() -> None:
    memory = _read_json(ROADMAP_MEMORY_PATH)
    current = memory.setdefault("current_position", {})
    current["active_stage"] = "Stage 9.17 availability assembly complete; Supplementary Methods not started"
    current["stage9_active_gate"] = "Stage 9.17 availability assembly complete; Supplementary Methods not started"
    current["after_stage9_17_availability_assembly"] = (
        "Stage 9.17 registered data availability, code availability, reproducibility command index, and the required Reporting Summary placeholder. "
        "It did not assemble the full reference library, write figure legends, create Supplementary Methods, or complete the final submission package."
    )
    current["current_gate"] = "Availability assembly complete without full submission-package assembly"
    current["next_stage"] = "Stage 9.18 Supplementary Methods drafting"
    for stage in memory.get("stage_lock", []):
        if not isinstance(stage, dict) or stage.get("stage") != 9:
            continue
        stage["status"] = "stage9_17_availability_assembled"
        stage["current_gate"] = "Stage 9.17 registered data/code availability and Reporting Summary placeholder"
        stage["scope_rule"] = (
            "Stage 9 has completed evidence intake, venue-guidance registration, representative methods-paper corpus analysis, "
            "narrative-spine selection, claim freeze, paragraph-level claim planning, main figure-spine planning, deterministic "
            "PanelForge rendering, supplementary display planning, section-contract planning, front-matter strategy, Results architecture, "
            "Results drafting, Introduction literature binding, Discussion interpretation mapping, Discussion drafting, Methods architecture, "
            "Methods drafting, and availability assembly only. Do not start the full reference library, figure legends, review response, "
            "supplementary methods, or final submission packaging without explicit substage authorization."
        )
        artifacts = stage.setdefault("artifacts", [])
        for artifact in [
            "manuscript/nature_methods/sections/data_availability.md",
            "manuscript/nature_methods/sections/code_availability.md",
            "manuscript/nature_methods/ledgers/reproducibility_command_index.md",
            "manuscript/nature_methods/submission_package/reporting_summary_REQUIRED.md",
            "manuscript/nature_methods/gate_verdicts/9.17.json",
            "scripts/run_stage9_17_availability_assembly.py",
        ]:
            if artifact not in artifacts:
                artifacts.append(artifact)
        gate = stage.setdefault("gate", [])
        availability_gate = "Stage 9.17 availability assembly registers exact software, data, code, command-index, and Reporting Summary requirement surfaces."
        if availability_gate not in gate:
            gate.append(availability_gate)
        for subphase in stage.get("subphases", []):
            if isinstance(subphase, dict) and subphase.get("id") == "9.17":
                subphase["status"] = "complete_availability_assembled"
                subphase["evidence"] = "manuscript/nature_methods/gate_verdicts/9.17.json"
    _write_json(ROADMAP_MEMORY_PATH, memory)


def _replace_once(body: str, old: str, new: str) -> str:
    return body.replace(old, new) if old in body else body


def _update_docs() -> None:
    if PLAN_PATH.exists():
        body = PLAN_PATH.read_text(encoding="utf-8")
        body = _replace_once(
            body,
            "Stage 9.15 registers Methods architecture in `sections/methods_blueprint.md`, `ledgers/methods_to_code_ledger.csv`, and `gate_verdicts/9.15.json`. Stage 9.16 registers Methods prose in `sections/methods.md` and `gate_verdicts/9.16.json`. The current state intentionally does not create availability statements, `refs/references.bib`, figure legends, supplementary methods, or submission-package files.",
            "Stage 9.15 registers Methods architecture in `sections/methods_blueprint.md`, `ledgers/methods_to_code_ledger.csv`, and `gate_verdicts/9.15.json`. Stage 9.16 registers Methods prose in `sections/methods.md` and `gate_verdicts/9.16.json`. Stage 9.17 registers data availability, code availability, the reproducibility command index, and the required Reporting Summary placeholder. The current state intentionally does not create `refs/references.bib`, figure legends, Supplementary Methods, or full submission-package files.",
        )
        body = _replace_once(
            body,
            "| 9.17 | Software, data, and code availability assembly | not_started | Create precise availability statements and required Reporting Summary placeholder. |",
            "| 9.17 | Software, data, and code availability assembly | complete_availability_assembled | Create precise availability statements and required Reporting Summary placeholder. |",
        )
        PLAN_PATH.write_text(body, encoding="utf-8")
    if ROADMAP_PATH.exists():
        body = ROADMAP_PATH.read_text(encoding="utf-8")
        body = _replace_once(
            body,
            "Stage 9.14 has registered Discussion drafting, Stage 9.15 has registered\nMethods architecture, and Stage 9.16 has registered Methods prose.\nAvailability assembly, full reference-library assembly, figure legends,\nsupplementary methods, and package assembly remain not started.",
            "Stage 9.14 has registered Discussion drafting, Stage 9.15 has registered\nMethods architecture, Stage 9.16 has registered Methods prose, and Stage 9.17\nhas registered data/code availability plus the required Reporting Summary\nplaceholder. Full reference-library assembly, figure legends, supplementary\nmethods, and final package assembly remain not started.",
        )
        body = _replace_once(
            body,
            "| Stage 9. Nature Methods manuscript assembly | Stage 9.16 Methods drafting complete, availability assembly not started. | The current boundary is evidence intake, official venue-guidance registration, representative methods-paper corpus analysis, narrative-spine selection, claim freeze, paragraph-level claim planning, main figure-spine planning, deterministic PanelForge rendering, supplementary display planning, section-contract planning, front-matter strategy, Results architecture, Results drafting, Introduction literature binding, Discussion interpretation mapping, Discussion drafting, Methods architecture, and Methods drafting only. Do not start availability assembly, full reference-library assembly, figure legends, review response, supplementary methods, or submission packaging without explicit substage authorization. |",
            "| Stage 9. Nature Methods manuscript assembly | Stage 9.17 availability assembly complete, Supplementary Methods not started. | The current boundary is evidence intake, official venue-guidance registration, representative methods-paper corpus analysis, narrative-spine selection, claim freeze, paragraph-level claim planning, main figure-spine planning, deterministic PanelForge rendering, supplementary display planning, section-contract planning, front-matter strategy, Results architecture, Results drafting, Introduction literature binding, Discussion interpretation mapping, Discussion drafting, Methods architecture, Methods drafting, and availability assembly only. Do not start full reference-library assembly, figure legends, review response, supplementary methods, or final submission packaging without explicit substage authorization. |",
        )
        body = _replace_once(
            body,
            "Stage 9.10 Results subsection architecture has been completed. Stage 9.11 Results drafting pass has been completed. Stage 9.12 Introduction literature binding has been completed. Stage 9.13 Discussion interpretation map has been completed. Stage 9.14 Discussion drafting pass has been completed. Stage 9.15 Methods architecture has been completed. Stage 9.16 Methods drafting pass has been completed. Stage 9.17 software, data, and code availability assembly remains the next unstarted manuscript step. Availability assembly, full reference-library assembly, figure legends, supplementary methods, and package assembly remain not started.",
            "Stage 9.10 Results subsection architecture has been completed. Stage 9.11 Results drafting pass has been completed. Stage 9.12 Introduction literature binding has been completed. Stage 9.13 Discussion interpretation map has been completed. Stage 9.14 Discussion drafting pass has been completed. Stage 9.15 Methods architecture has been completed. Stage 9.16 Methods drafting pass has been completed. Stage 9.17 software, data, and code availability assembly has been completed. Stage 9.18 Supplementary Methods drafting remains the next unstarted manuscript step. Full reference-library assembly, figure legends, supplementary methods, and final package assembly remain not started.",
        )
        ROADMAP_PATH.write_text(body, encoding="utf-8")


def run() -> dict[str, Any]:
    generated_utc = _now()
    commit = _git_sha()
    facts = _release_facts()
    rows = _command_rows(facts)
    urls = [
        facts.repo_url,
        facts.release_url,
        _doi_url(facts.version_doi),
        _doi_url(facts.concept_doi),
        facts.record_url,
        _doi_url(facts.panelforge_version_doi),
        _doi_url(facts.panelforge_concept_doi),
    ]
    url_checks = [_url_resolves(url) for url in urls]
    if STAGING_DIR.exists():
        shutil.rmtree(STAGING_DIR)
    STAGING_DIR.mkdir(parents=True, exist_ok=True)
    texts = {
        "data_availability": _build_data_availability(facts, generated_utc),
        "code_availability": _build_code_availability(facts, generated_utc),
        "command_index": _build_command_index(rows, facts, generated_utc),
        "reporting_summary": _build_reporting_summary(facts, generated_utc),
    }
    for key, text in texts.items():
        _write_text(STAGING_DIR / OUTPUTS[key].relative_to(WORKSPACE), text)
    checks = _validate(texts, rows, facts, url_checks, commit)
    passed = all(check["passed"] for check in checks)
    gate = {
        "substage": "9.17",
        "timestamp": generated_utc,
        "pass": passed,
        "checks": checks,
        "software_version": SOFTWARE_VERSION,
        "release_commit": facts.release_commit,
        "release_tag": facts.release_tag,
        "software_version_doi": facts.version_doi,
        "software_concept_doi": facts.concept_doi,
        "panel_engine": facts.panelforge_name,
        "panel_engine_version_doi": facts.panelforge_version_doi,
        "panel_engine_render_command": facts.panelforge_render_cmd,
        "command_count": len(rows),
        "public_data_source_count": len(PUBLIC_DATA_SOURCES),
        "reporting_summary_required": True,
        "next_substage": "9.18",
        "outputs": [str(path.relative_to(ROOT)) for path in OUTPUTS.values()],
        "scope_boundary": "Availability assembly only. No references.bib, figure legends, Supplementary Methods, PI packet, readiness checklist, or full submission-package assembly.",
    }
    _write_json(STAGING_DIR / OUTPUTS["gate"].relative_to(WORKSPACE), gate)
    if passed:
        _promote_staging()
        shutil.rmtree(STAGING_DIR)
        _update_registry()
        _update_memory(generated_utc, checks)
        _update_roadmap_memory()
        _update_docs()
    else:
        quarantine = _quarantine_staging(generated_utc)
        gate["quarantine_path"] = str(quarantine.relative_to(ROOT))
        _write_json(OUTPUTS["gate"], gate)
    return {
        "status": "pass" if passed else "fail",
        "substage": "9.17",
        "release_commit": facts.release_commit,
        "command_count": len(rows),
        "url_checks": url_checks,
        "failures": [check for check in checks if not check["passed"]],
        "outputs": gate["outputs"],
        "next_allowed_action": "Proceed to Stage 9.18 Supplementary Methods drafting after validation and explicit authorization.",
    }


def main() -> int:
    payload = run()
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())

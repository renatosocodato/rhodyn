"""Run Stage 9.1 venue guidance source registration.

Stage 9.1 binds the Nature Methods manuscript assembly process to current,
official venue and portfolio guidance. It caches the source pages, extracts the
submission constraints that matter for the RhoDyn methods manuscript, and keeps
all downstream manuscript drafting, reference-library construction, figure
rendering, and submission-package assembly blocked.
"""

from __future__ import annotations

import hashlib
import html
import json
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from urllib.error import URLError
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT / "manuscript" / "nature_methods"
REFS_DIR = WORKSPACE / "refs"
CACHE_DIR = REFS_DIR / "_cache"
AUDIT_DIR = WORKSPACE / "audits"
GATE_DIR = WORKSPACE / "gate_verdicts"
STAGING_DIR = WORKSPACE / "_staging" / "9.1"
QUARANTINE_DIR = WORKSPACE / "_quarantine" / "9.1"
MEMORY_PATH = ROOT / "docs" / "stage9_execution_memory.json"
ROADMAP_MEMORY_PATH = ROOT / "docs" / "roadmap_execution_memory.json"
REGISTRY_PATH = WORKSPACE / "contracts" / "stage9_substage_registry.json"
PLAN_PATH = ROOT / "docs" / "stage9_manuscript_assembly_plan.md"
ROADMAP_PATH = ROOT / "docs" / "roadmap.md"
GATE_9_0 = GATE_DIR / "9.0.json"

OUTPUTS = {
    "register": REFS_DIR / "nature_methods_guidance_register.md",
    "audit": AUDIT_DIR / "venue_policy_constraints.md",
    "gate": GATE_DIR / "9.1.json",
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


@dataclass(frozen=True)
class SourceSpec:
    source_id: str
    title: str
    url: str
    cache_stem: str
    required_phrases: tuple[str, ...]


SOURCES = [
    SourceSpec(
        source_id="NMETH-AIMS",
        title="Nature Methods aims and scope",
        url="https://www.nature.com/nmeth/aims",
        cache_stem="nmeth_aims_scope",
        required_phrases=(
            "novel methods and significant improvements",
            "strong validation",
            "performance in comparison to available approaches",
            "Computational, statistical and machine learning methods",
        ),
    ),
    SourceSpec(
        source_id="NMETH-CONTENT",
        title="Nature Methods content types",
        url="https://www.nature.com/nmeth/content",
        cache_stem="nmeth_content_types",
        required_phrases=(
            "Article",
            "Abstract – up to 150 words",
            "Main text – 3,000 words",
            "up to 5,000 words",
            "Display items – up to 6 figures",
            "Discussion does not contain subheadings",
        ),
    ),
    SourceSpec(
        source_id="NMETH-SUBMISSION",
        title="Nature Methods submission guidelines",
        url="https://www.nature.com/nmeth/submission-guidelines",
        cache_stem="nmeth_submission_guidelines",
        required_phrases=(
            "What you need to know before initial submission",
            "make sure Nature Methods is the most suitable journal",
            "Read and understand our policies",
            "Preparing your material for initial submission",
        ),
    ),
    SourceSpec(
        source_id="NMETH-EDITORIAL",
        title="Nature Methods editorial policies",
        url="https://www.nature.com/nmeth/editorial-policies",
        cache_stem="nmeth_editorial_policies",
        required_phrases=(
            "Reporting Summary",
            "Software submission checklist",
            "new code that is central to the paper",
        ),
    ),
    SourceSpec(
        source_id="NPORT-REPORTING",
        title="Nature Portfolio reporting standards",
        url="https://www.nature.com/nature-portfolio/editorial-policies/reporting-standards",
        cache_stem="nature_portfolio_reporting_standards",
        required_phrases=(
            "materials, data, code, and associated protocols",
            "reporting summary documents",
            "Data availability statements",
        ),
    ),
    SourceSpec(
        source_id="NATURE-INITIAL",
        title="Nature initial-submission format guidance",
        url="https://www.nature.com/nature/for-authors/initial-submission",
        cache_stem="nature_initial_submission",
        required_phrases=(
            "Methods",
            "Data availability",
            "Code availability",
            "Figure legends",
            "EXACT n values",
        ),
    ),
    SourceSpec(
        source_id="SN-CODE",
        title="Springer Nature research-code policy",
        url="https://www.springernature.com/gp/open-science/code-policy",
        cache_stem="springer_nature_code_policy",
        required_phrases=(
            "Code Availability Statement",
            "permanent identifier",
            "GitHub link only is not sufficient",
            "peer reviewers",
        ),
    ),
]


VENUE_CONSTRAINTS = [
    {
        "constraint_id": "VENUE-001",
        "topic": "Nature Methods Article fit",
        "requirement": "Article submissions should report a novel method or tool with full technical description and strong validation showing performance, reproducibility, broad applicability, and potential for discovering new biology.",
        "implication": "RhoDyn must be presented as a general computational method, with the RhoA/microglia use case framed as one biological demonstration rather than as the method's only source of value.",
        "source_id": "NMETH-CONTENT",
        "source_phrase": "full technical descriptions",
    },
    {
        "constraint_id": "VENUE-002",
        "topic": "Aims and scope",
        "requirement": "Nature Methods prioritizes methodological advances for life-science research, including computational, statistical, machine-learning, analysis, modeling, and visualization methods.",
        "implication": "The manuscript should emphasize the method object, executable workflow, benchmarking, uncertainty, and biological demonstrations, not a software marketing narrative.",
        "source_id": "NMETH-AIMS",
        "source_phrase": "Computational, statistical and machine learning methods",
    },
    {
        "constraint_id": "VENUE-003",
        "topic": "Abstract budget",
        "requirement": "Article abstract up to 150 words and unreferenced.",
        "implication": "Stage 9.9 must draft a concise, unreferenced method abstract and block citation-heavy or result-list abstracts.",
        "source_id": "NMETH-CONTENT",
        "source_phrase": "Abstract – up to 150 words",
    },
    {
        "constraint_id": "VENUE-004",
        "topic": "Main text budget",
        "requirement": "Article main text target is 3,000 words, with up to 5,000 words at editorial discretion, excluding abstract, Methods, references, and figure legends.",
        "implication": "Stage 9 section contracts must track word budgets and reserve extra length for method definition, benchmarks, and biological applications only where justified.",
        "source_id": "NMETH-CONTENT",
        "source_phrase": "Main text – 3,000 words",
    },
    {
        "constraint_id": "VENUE-005",
        "topic": "Display-item budget",
        "requirement": "Article display items are limited to up to six figures and/or tables.",
        "implication": "Stage 9.6 must keep the main display spine at six or fewer total main figures/tables and move technical detail into supplementary material.",
        "source_id": "NMETH-CONTENT",
        "source_phrase": "Display items – up to 6 figures",
    },
    {
        "constraint_id": "VENUE-006",
        "topic": "Article section structure",
        "requirement": "Article structure is Introduction without heading, Results, Discussion, and Online Methods. Results and Methods can use topical subheadings, while Discussion has no subheadings.",
        "implication": "Stage 9.8 must block Discussion subheadings and preserve Results/Methods subheading logic.",
        "source_id": "NMETH-CONTENT",
        "source_phrase": "Discussion does not contain subheadings",
    },
    {
        "constraint_id": "VENUE-007",
        "topic": "Reference scope",
        "requirement": "Article references are typically recommended up to 50.",
        "implication": "Stage 9.20 must keep reference selection tight and citation-bearing claims explicit.",
        "source_id": "NMETH-CONTENT",
        "source_phrase": "we typically recommend up to 50",
    },
    {
        "constraint_id": "VENUE-008",
        "topic": "Supplementary information",
        "requirement": "Articles may be accompanied by supplementary information.",
        "implication": "Stage 9.7 and 9.18 should move technical derivations, extended benchmarks, and implementation checks to cited supplementary material rather than overloading the main text.",
        "source_id": "NMETH-CONTENT",
        "source_phrase": "supplementary information",
    },
    {
        "constraint_id": "VENUE-009",
        "topic": "Reporting Summary",
        "requirement": "Life-science manuscripts require a Reporting Summary for editors and reviewers, with accepted summaries published alongside the paper.",
        "implication": "Stage 9.17 must include a Reporting Summary placeholder and route quantitative design details to the appropriate form.",
        "source_id": "NPORT-REPORTING",
        "source_phrase": "reporting summary documents",
    },
    {
        "constraint_id": "VENUE-010",
        "topic": "Data availability",
        "requirement": "Data availability statements are required and must make the minimum dataset needed to interpret, verify, and extend the research transparent.",
        "implication": "Stage 9.17 must map every public and controlled input, derived table, benchmark output, and RhoA/microglia reference-use artifact to a clear availability statement.",
        "source_id": "NPORT-REPORTING",
        "source_phrase": "Data availability statements",
    },
    {
        "constraint_id": "VENUE-011",
        "topic": "Material, code, and protocol sharing",
        "requirement": "Materials, data, code, and associated protocols should be made promptly available, with restrictions disclosed to editors and in the manuscript.",
        "implication": "Stage 9.17 must distinguish open software, public examples, restricted or controlled-access data, and optional biological reference-case inputs.",
        "source_id": "NPORT-REPORTING",
        "source_phrase": "materials, data, code, and associated protocols",
    },
    {
        "constraint_id": "VENUE-012",
        "topic": "Software submission checklist",
        "requirement": "Manuscripts with new code central to the paper require software details sufficient for peer-review evaluation.",
        "implication": "RhoDyn code, versioning, installation route, command index, tests, and example outputs must remain reviewable before submission package assembly.",
        "source_id": "NMETH-EDITORIAL",
        "source_phrase": "Software submission checklist",
    },
    {
        "constraint_id": "VENUE-013",
        "topic": "Code availability statement",
        "requirement": "Original research articles containing new code necessary to interpret and replicate the conclusions require a Code Availability Statement.",
        "implication": "Stage 9.17 must include repository, release, archive DOI, license, and reproducibility details for RhoDyn.",
        "source_id": "SN-CODE",
        "source_phrase": "Code Availability Statement",
    },
    {
        "constraint_id": "VENUE-014",
        "topic": "Permanent code identifier",
        "requirement": "A GitHub link alone is not sufficient for code archiving. A permanent identifier such as a Zenodo DOI is recommended.",
        "implication": "The manuscript should cite the RhoDyn release archive DOI alongside the GitHub repository, not only a mutable repository URL.",
        "source_id": "SN-CODE",
        "source_phrase": "GitHub link only is not sufficient",
    },
    {
        "constraint_id": "VENUE-015",
        "topic": "Methods reproducibility",
        "requirement": "Methods should contain the elements necessary for interpretation and replication.",
        "implication": "Stage 9.15 and 9.16 must bind method definitions, assumptions, parameters, grouping rules, and execution commands to Stage 7 outputs.",
        "source_id": "NATURE-INITIAL",
        "source_phrase": "elements necessary for interpretation and replication",
    },
    {
        "constraint_id": "VENUE-016",
        "topic": "Statistics reporting",
        "requirement": "Statistical reporting should name tests, one- or two-tailed design where relevant, error-bar definitions, and exact sample sizes.",
        "implication": "Stage 9.22 must diff every numeric claim against locked outputs and require exact n, uncertainty, and decision rules where reported.",
        "source_id": "NATURE-INITIAL",
        "source_phrase": "EXACT n values",
    },
    {
        "constraint_id": "VENUE-017",
        "topic": "Figure legends",
        "requirement": "Figure legends should remain concise, include a title sentence, describe the figure, and be understandable in isolation.",
        "implication": "Stage 9.23 must keep legends self-contained while preventing legends from becoming Methods or Results prose.",
        "source_id": "NATURE-INITIAL",
        "source_phrase": "Figure legends",
    },
    {
        "constraint_id": "VENUE-018",
        "topic": "Initial submission hygiene",
        "requirement": "Initial submissions should be complete, readable, and aligned with editorial policies before review.",
        "implication": "Stage 9.27 cannot assemble the submission package until cross-document consistency, citation, statistical language, and reader-surface hygiene gates pass.",
        "source_id": "NMETH-SUBMISSION",
        "source_phrase": "What you need to know before initial submission",
    },
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


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_text(path: Path, body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body.rstrip() + "\n", encoding="utf-8")


def _html_to_text(raw_html: str) -> str:
    body = re.sub(r"<(script|style).*?</\1>", " ", raw_html, flags=re.IGNORECASE | re.DOTALL)
    body = re.sub(r"<[^>]+>", " ", body)
    body = html.unescape(body)
    body = re.sub(r"\s+", " ", body)
    return body.strip()


def _fetch_source(source: SourceSpec, accessed_utc: str, cache_root: Path) -> dict[str, Any]:
    request = Request(
        source.url,
        headers={
            "User-Agent": "Mozilla/5.0 RhoDyn Stage 9.1 venue guidance register",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        },
    )
    try:
        with urlopen(request, timeout=30) as response:
            raw = response.read().decode("utf-8", "ignore")
            status = int(getattr(response, "status", 200))
    except URLError as exc:
        return {
            "source_id": source.source_id,
            "title": source.title,
            "url": source.url,
            "accessed_utc": accessed_utc,
            "status": "fetch_failed",
            "http_status": "error",
            "error": str(exc),
            "cache_text": "",
            "cache_file": "",
            "metadata_file": "",
            "sha256": "",
            "required_phrases_found": [],
            "required_phrases_missing": list(source.required_phrases),
        }

    text = _html_to_text(raw)
    lowered = text.lower()
    found = [phrase for phrase in source.required_phrases if phrase.lower() in lowered]
    missing = [phrase for phrase in source.required_phrases if phrase.lower() not in lowered]
    text_path = cache_root / f"{source.cache_stem}.txt"
    meta_path = cache_root / f"{source.cache_stem}.meta.json"
    final_text_path = CACHE_DIR / f"{source.cache_stem}.txt"
    final_meta_path = CACHE_DIR / f"{source.cache_stem}.meta.json"
    metadata = {
        "source_id": source.source_id,
        "title": source.title,
        "url": source.url,
        "accessed_utc": accessed_utc,
        "http_status": status,
        "cache_file": str(final_text_path.relative_to(ROOT)),
        "metadata_file": str(final_meta_path.relative_to(ROOT)),
        "byte_count": len(text.encode("utf-8")),
        "sha256": _sha256_text(text),
        "required_phrases_found": found,
        "required_phrases_missing": missing,
        "status": "fetched" if not missing and status == 200 else "fetched_with_missing_phrases",
    }
    _write_text(text_path, text)
    _write_json(meta_path, metadata)
    return {**metadata, "cache_text": text}


def _markdown_table(rows: list[dict[str, str]], columns: list[str]) -> str:
    lines = ["| " + " | ".join(columns) + " |", "| " + " | ".join("---" for _ in columns) + " |"]
    for row in rows:
        lines.append("| " + " | ".join(str(row.get(column, "")).replace("|", "\\|") for column in columns) + " |")
    return "\n".join(lines)


def _source_map(records: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {str(record["source_id"]): record for record in records}


def _excerpt(record: dict[str, Any], phrase: str, span: int = 210) -> str:
    text = str(record.get("cache_text", ""))
    index = text.lower().find(phrase.lower())
    if index < 0:
        return ""
    start = max(0, index - span)
    end = min(len(text), index + len(phrase) + span)
    return text[start:end].strip()


def _constraints_with_sources(records: list[dict[str, Any]]) -> list[dict[str, str]]:
    by_source = _source_map(records)
    rows: list[dict[str, str]] = []
    for item in VENUE_CONSTRAINTS:
        source = by_source[item["source_id"]]
        phrase = str(item.get("source_phrase") or (source["required_phrases_found"][0] if source.get("required_phrases_found") else item["topic"]))
        rows.append(
            {
                **{key: str(value) for key, value in item.items()},
                "source_url": str(source["url"]),
                "source_cache": str(source["cache_file"]),
                "accessed_utc": str(source["accessed_utc"]),
                "source_excerpt": _excerpt(source, str(phrase)),
            }
        )
    return rows


def _build_register(records: list[dict[str, Any]], constraints: list[dict[str, str]], generated_utc: str) -> str:
    source_rows = [
        {
            "source_id": str(record["source_id"]),
            "title": str(record["title"]),
            "url": str(record["url"]),
            "accessed_utc": str(record["accessed_utc"]),
            "cache_file": str(record["cache_file"]),
            "sha256": str(record["sha256"])[:16],
            "status": str(record["status"]),
        }
        for record in records
    ]
    constraint_rows = [
        {
            "constraint_id": row["constraint_id"],
            "topic": row["topic"],
            "requirement": row["requirement"],
            "source_id": row["source_id"],
            "stage9_implication": row["implication"],
        }
        for row in constraints
    ]
    return f"""# Nature Methods guidance register

Generated UTC. {generated_utc}

Stage. 9.1 venue guidance source register.

Scope. This file binds the RhoDyn Nature Methods manuscript process to official
Nature Methods, Nature Portfolio, and Springer Nature guidance available at the
listed URLs on the access date. It does not start literature lookup, reference
library construction, manuscript drafting, figure rendering, or submission
package assembly.

## Cached official sources

{_markdown_table(source_rows, ["source_id", "title", "url", "accessed_utc", "cache_file", "sha256", "status"])}

## Venue constraints for downstream Stage 9 work

{_markdown_table(constraint_rows, ["constraint_id", "topic", "requirement", "source_id", "stage9_implication"])}

## Article budget now bound for future stages

- Content type. Nature Methods Article.
- Abstract. Up to 150 words, unreferenced.
- Main text. 3,000 words, with up to 5,000 words at editorial discretion,
  excluding abstract, Methods, references, and figure legends.
- Display items. Up to six figures and/or tables.
- Structure. Introduction without heading, Results, Discussion, and Online
  Methods.
- Subheadings. Results and Methods can use topical subheadings. Discussion does
  not contain subheadings.
- References. Typically up to 50.
- Methods, data, code, software, statistics, figure legends, and Reporting
  Summary obligations are captured in the constraints table above.
"""


def _build_audit(records: list[dict[str, Any]], constraints: list[dict[str, str]], checks: list[dict[str, Any]], generated_utc: str) -> str:
    check_rows = [
        {
            "check": str(check["name"]),
            "status": "pass" if check["passed"] else "fail",
            "detail": str(check["detail"]),
        }
        for check in checks
    ]
    excerpt_rows = [
        {
            "constraint_id": row["constraint_id"],
            "source_id": row["source_id"],
            "excerpt": row["source_excerpt"],
        }
        for row in constraints
    ]
    source_ids = ", ".join(record["source_id"] for record in records)
    return f"""# Venue policy constraints audit

Generated UTC. {generated_utc}

Official source IDs. {source_ids}

## Gate predicate results

{_markdown_table(check_rows, ["check", "status", "detail"])}

## Verification excerpts

{_markdown_table(excerpt_rows, ["constraint_id", "source_id", "excerpt"])}

## Interpretation for RhoDyn manuscript assembly

The downstream manuscript must be a Nature Methods Article about a general
computational method for life-science data, supported by validation, biological
demonstrations, and reviewable software. The RhoA/microglia work can serve as a
biological depth case, but the manuscript must not imply that the original paper
was generated by RhoDyn. Stage 9.1 only registers venue rules. Stage 9.2 remains
the next unstarted step and will build a representative methods-paper corpus
before any drafting.
"""


def _validate(records: list[dict[str, Any]], constraints: list[dict[str, str]], generated_utc: str) -> list[dict[str, Any]]:
    by_source = _source_map(records)
    rendered = [
        path
        for path in (WORKSPACE / "figures" / "rendered").rglob("*")
        if path.is_file() and path.suffix.lower() in {".png", ".pdf", ".svg"}
    ]
    gate_9_0_pass = False
    if GATE_9_0.exists():
        try:
            gate_9_0_pass = _read_json(GATE_9_0).get("pass") is True
        except json.JSONDecodeError:
            gate_9_0_pass = False
    records_ok = all(record.get("status") == "fetched" and record.get("url") and record.get("accessed_utc") for record in records)

    def staged_or_final_exists(rel_value: object) -> bool:
        rel_path = Path(str(rel_value))
        final = ROOT / rel_path
        staged = STAGING_DIR / rel_path.relative_to(WORKSPACE.relative_to(ROOT))
        return final.exists() or staged.exists()

    cache_files_ok = all(
        staged_or_final_exists(record.get("cache_file", ""))
        and staged_or_final_exists(record.get("metadata_file", ""))
        for record in records
    )
    content_constraint_ids = {row["constraint_id"] for row in constraints if row["source_id"] == "NMETH-CONTENT"}
    official_urls = [str(record.get("url", "")) for record in records]
    constraints_ok = len(constraints) >= 18 and all(row.get("source_url") in official_urls and row.get("source_excerpt") for row in constraints)
    today = datetime.now(UTC).date().isoformat()
    freshness_ok = all(str(record.get("accessed_utc", "")).startswith(today) for record in records)
    no_downstream = not any(path.exists() for path in FORBIDDEN_STARTED_PATHS) and not rendered

    return [
        {
            "name": "stage_9_0_gate_passed",
            "passed": gate_9_0_pass,
            "detail": "Stage 9.0 evidence lock exists and passes" if gate_9_0_pass else "Stage 9.0 gate is missing or not passing",
        },
        {
            "name": "official_sources_fetched",
            "passed": records_ok,
            "detail": f"{sum(record.get('status') == 'fetched' for record in records)} of {len(SOURCES)} official pages fetched with required phrases",
        },
        {
            "name": "content_type_budget_is_sourced",
            "passed": {"VENUE-001", "VENUE-003", "VENUE-004", "VENUE-005", "VENUE-006", "VENUE-007"}.issubset(content_constraint_ids),
            "detail": "Article fit, abstract, main text, display item, structure, and reference constraints are sourced from Nature Methods content guidance",
        },
        {
            "name": "cached_sources_have_url_and_access_date",
            "passed": records_ok and cache_files_ok,
            "detail": f"{len(records)} cached source records include URL, access date, text cache, metadata, and hash",
        },
        {
            "name": "verified_venue_constraints_are_explicit",
            "passed": constraints_ok,
            "detail": f"{len(constraints)} venue constraints registered with source excerpts",
        },
        {
            "name": "freshness_assertion_passes",
            "passed": freshness_ok,
            "detail": f"All source access dates match run date {today}",
        },
        {
            "name": "no_downstream_stage9_surfaces_started",
            "passed": no_downstream,
            "detail": "No manuscript sections, reference bibliography, submission package, PanelForge clone, runtime environment, or rendered figures detected",
        },
    ]


def _promote_staging(records: list[dict[str, Any]]) -> None:
    for destination in OUTPUTS.values():
        staged = STAGING_DIR / destination.relative_to(WORKSPACE)
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(staged, destination)
    for record in records:
        for key in ["cache_file", "metadata_file"]:
            destination = ROOT / str(record[key])
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
        if substage.get("id") == "9.1":
            substage["status"] = "completed"
    registry["last_completed_substage"] = "9.1"
    _write_json(REGISTRY_PATH, registry)


def _update_memory(guidance_version: str, generated_utc: str, checks: list[dict[str, Any]]) -> None:
    memory = _read_json(MEMORY_PATH)
    memory["generated_utc"] = generated_utc
    memory["current_substage"] = "9.1"
    memory["venue_guidance_started"] = True
    memory["venue_guidance_version"] = guidance_version
    memory["status"] = "stage9_1_guidance_registered"
    memory["next_substage"] = "9.2"
    memory["next_substage_authorized"] = False
    memory["stage9_1_checks"] = checks
    memory.setdefault("completed_substages", [])
    if not any(item.get("substage") == "9.1" for item in memory["completed_substages"]):
        memory["completed_substages"].append(
            {
                "substage": "9.1",
                "status": "pass",
                "pass": True,
                "gate_verdict_path": "manuscript/nature_methods/gate_verdicts/9.1.json",
                "validation_outcome": "Official Nature Methods and Springer Nature guidance registered for Stage 9 manuscript assembly",
                "evidence_dependencies": [
                    "manuscript/nature_methods/gate_verdicts/9.0.json",
                    "https://www.nature.com/nmeth/content",
                    "https://www.nature.com/nmeth/aims",
                    "https://www.nature.com/nmeth/editorial-policies",
                    "https://www.springernature.com/gp/open-science/code-policy",
                ],
                "files_created_or_modified": [
                    "manuscript/nature_methods/refs/nature_methods_guidance_register.md",
                    "manuscript/nature_methods/refs/_cache/",
                    "manuscript/nature_methods/audits/venue_policy_constraints.md",
                    "manuscript/nature_methods/gate_verdicts/9.1.json",
                ],
                "remaining_blockers": [
                    "Stage 9.2 representative methods-paper corpus has not started",
                    "Stage 9.3 narrative-spine decision has not started",
                    "Stage 9.6 figure-to-claim contract has not started",
                    "Stage 9.6b PanelForge rendering remains blocked until Stage 9.6 passes",
                    "Manuscript drafting and reference library construction remain not started",
                ],
            }
        )
    _write_json(MEMORY_PATH, memory)


def _update_roadmap_memory(guidance_version: str) -> None:
    memory = _read_json(ROADMAP_MEMORY_PATH)
    current = memory.setdefault("current_position", {})
    current["active_stage"] = "Stage 9.1 venue guidance registered; manuscript production not started"
    current["stage9_active_gate"] = "Stage 9.1 venue guidance registered; manuscript production not started"
    current["after_stage9_1_guidance_register"] = (
        "Stage 9.1 cached official Nature Methods, Nature Portfolio, and Springer Nature guidance, "
        "registered Article-format constraints, and kept citation resolution, manuscript drafting, "
        "figure rendering, PanelForge execution, and submission-package assembly not started."
    )
    for stage in memory.get("stage_lock", []):
        if not isinstance(stage, dict) or stage.get("stage") != 9:
            continue
        stage["status"] = "stage9_1_guidance_registered"
        stage["current_gate"] = "Stage 9.1 venue guidance registered; manuscript production not started"
        stage["scope_rule"] = (
            "Stage 9 has completed evidence intake and venue-guidance registration only. "
            "Do not start representative corpus, citation resolution, drafting, figure rendering, "
            "review response, or submission packaging without explicit substage authorization."
        )
        artifacts = stage.setdefault("artifacts", [])
        for artifact in [
            "manuscript/nature_methods/refs/nature_methods_guidance_register.md",
            "manuscript/nature_methods/refs/_cache/",
            "manuscript/nature_methods/audits/venue_policy_constraints.md",
            "manuscript/nature_methods/gate_verdicts/9.1.json",
            "scripts/run_stage9_1_venue_guidance_register.py",
        ]:
            if artifact not in artifacts:
                artifacts.append(artifact)
        gate = stage.setdefault("gate", [])
        guidance_gate = "Stage 9.1 venue guidance is registered from official cached sources."
        if guidance_gate not in gate:
            gate.append(guidance_gate)
        for subphase in stage.get("subphases", []):
            if isinstance(subphase, dict) and subphase.get("id") == "9.1":
                subphase["status"] = "complete_guidance_registered"
                subphase["evidence"] = "manuscript/nature_methods/gate_verdicts/9.1.json"
                subphase["guidance_version"] = guidance_version
    _write_json(ROADMAP_MEMORY_PATH, memory)


def _update_docs() -> None:
    if PLAN_PATH.exists():
        body = PLAN_PATH.read_text(encoding="utf-8")
        body = body.replace(
            "This repository state serializes the entire Stage 9 v2.1 plan, completes the contract/schema scaffold, and completes the Stage 9.0 evidence lock. It does not begin literature lookup, manuscript drafting, editorial polishing, PanelForge rendering, or package assembly.",
            "This repository state serializes the entire Stage 9 v2.1 plan, completes the contract/schema scaffold, completes the Stage 9.0 evidence lock, and registers official Nature Methods venue guidance in Stage 9.1. It does not begin literature lookup, representative-paper corpus construction, manuscript drafting, editorial polishing, PanelForge rendering, or package assembly.",
        )
        body = body.replace(
            "- Venue target. Nature Methods Article, pending live venue-guidance verification in Stage 9.1.",
            "- Venue target. Nature Methods Article, verified against cached official guidance in Stage 9.1.",
        )
        body = body.replace(
            "Stage 9.0 then locked the completed Stage 7.8 evidence package into `ledgers/stage9_evidence_manifest.csv`, `ledgers/stage9_evidence_lock.md`, `ledgers/stage7_output_contract.md`, and `gate_verdicts/9.0.json`. The current state intentionally does not create",
            "Stage 9.0 then locked the completed Stage 7.8 evidence package into `ledgers/stage9_evidence_manifest.csv`, `ledgers/stage9_evidence_lock.md`, `ledgers/stage7_output_contract.md`, and `gate_verdicts/9.0.json`. Stage 9.1 registers official Nature Methods, Nature Portfolio, and Springer Nature guidance in `refs/nature_methods_guidance_register.md`, `refs/_cache/`, `audits/venue_policy_constraints.md`, and `gate_verdicts/9.1.json`. The current state intentionally does not create",
        )
        body = body.replace(
            "| 9.1 | Venue guidance source register | not_started | Bind manuscript process to official and cached Nature Methods guidance. |",
            "| 9.1 | Venue guidance source register | complete_guidance_registered | Bind manuscript process to official and cached Nature Methods guidance. |",
        )
        PLAN_PATH.write_text(body, encoding="utf-8")
    if ROADMAP_PATH.exists():
        body = ROADMAP_PATH.read_text(encoding="utf-8")
        body = body.replace(
            "| Stage 9. Nature Methods manuscript assembly | Stage 9.0 evidence locked, manuscript production not started. | The current boundary is evidence intake only, with PanelForge reserved as a future Stage 9.6b rendering dependency. Do not start venue guidance, citation resolution, figure rendering, drafting, review response, or submission packaging without explicit substage authorization. |",
            "| Stage 9. Nature Methods manuscript assembly | Stage 9.1 venue guidance registered, manuscript production not started. | The current boundary is evidence intake plus official venue-guidance registration only, with PanelForge reserved as a future Stage 9.6b rendering dependency. Do not start the representative methods-paper corpus, citation resolution, figure rendering, drafting, review response, or submission packaging without explicit substage authorization. |",
        )
        ROADMAP_PATH.write_text(body, encoding="utf-8")


def run() -> dict[str, Any]:
    generated_utc = _now()
    commit = _git_sha()
    guidance_version = f"nature-methods-guidance@{generated_utc[:10]}@{commit}"
    if STAGING_DIR.exists():
        shutil.rmtree(STAGING_DIR)
    STAGING_DIR.mkdir(parents=True, exist_ok=True)
    cache_root = STAGING_DIR / CACHE_DIR.relative_to(WORKSPACE)
    cache_root.mkdir(parents=True, exist_ok=True)

    records = [_fetch_source(source, generated_utc, cache_root) for source in SOURCES]
    constraints = _constraints_with_sources(records) if all(record.get("status") == "fetched" for record in records) else []
    checks = _validate(records, constraints, generated_utc)
    passed = all(check["passed"] for check in checks)
    gate = {
        "substage": "9.1",
        "timestamp": generated_utc,
        "guidance_version": guidance_version,
        "pass": passed,
        "checks": checks,
        "source_count": len(records),
        "constraint_count": len(constraints),
        "outputs": [str(path.relative_to(ROOT)) for path in OUTPUTS.values()] + [
            str((CACHE_DIR / f"{source.cache_stem}.txt").relative_to(ROOT)) for source in SOURCES
        ]
        + [str((CACHE_DIR / f"{source.cache_stem}.meta.json").relative_to(ROOT)) for source in SOURCES],
        "scope_boundary": "Venue-guidance registration only. No representative corpus, citation resolution, drafting, figure rendering, PanelForge execution, or submission-package assembly.",
    }

    _write_text(STAGING_DIR / OUTPUTS["register"].relative_to(WORKSPACE), _build_register(records, constraints, generated_utc))
    _write_text(STAGING_DIR / OUTPUTS["audit"].relative_to(WORKSPACE), _build_audit(records, constraints, checks, generated_utc))
    _write_json(STAGING_DIR / OUTPUTS["gate"].relative_to(WORKSPACE), gate)

    if passed:
        _promote_staging(records)
        shutil.rmtree(STAGING_DIR)
        _update_registry()
        _update_memory(guidance_version, generated_utc, checks)
        _update_roadmap_memory(guidance_version)
        _update_docs()
    else:
        quarantine = _quarantine_staging(generated_utc)
        gate["quarantine_path"] = str(quarantine.relative_to(ROOT))
        _write_json(OUTPUTS["gate"], gate)

    return {
        "status": "pass" if passed else "fail",
        "substage": "9.1",
        "guidance_version": guidance_version,
        "source_count": len(records),
        "constraint_count": len(constraints),
        "failures": [check for check in checks if not check["passed"]],
        "outputs": gate["outputs"],
    }


def main() -> int:
    payload = run()
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())

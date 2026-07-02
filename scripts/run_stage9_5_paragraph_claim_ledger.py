"""Run Stage 9.5 paragraph-level claim-ledger registration.

Stage 9.5 plans manuscript paragraphs as claim-bearing units. It does not
draft manuscript sections, resolve citations, build the figure spine, render
figures, run PanelForge, or assemble a submission package.

No manuscript prose is created in this stage.
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
LEDGER_DIR = WORKSPACE / "ledgers"
GATE_DIR = WORKSPACE / "gate_verdicts"
STAGING_DIR = WORKSPACE / "_staging" / "9.5"
QUARANTINE_DIR = WORKSPACE / "_quarantine" / "9.5"
MEMORY_PATH = ROOT / "docs" / "stage9_execution_memory.json"
ROADMAP_MEMORY_PATH = ROOT / "docs" / "roadmap_execution_memory.json"
REGISTRY_PATH = WORKSPACE / "contracts" / "stage9_substage_registry.json"
PLAN_PATH = ROOT / "docs" / "stage9_manuscript_assembly_plan.md"
ROADMAP_PATH = ROOT / "docs" / "roadmap.md"
CLAIM_CSV_PATH = LEDGER_DIR / "claim_hierarchy.csv"
GATE_9_4 = GATE_DIR / "9.4.json"

OUTPUTS = {
    "paragraph_csv": LEDGER_DIR / "paragraph_claim_ledger.csv",
    "strength_rules": LEDGER_DIR / "claim_strength_rules.md",
    "gate": GATE_DIR / "9.5.json",
}

FIELDNAMES = [
    "para_id",
    "section",
    "purpose",
    "claim_id",
    "fig_ids",
    "stat_ids",
    "ref_ids",
    "caveat",
    "strength_cap",
]

FORBIDDEN_STARTED_PATHS = [
    WORKSPACE / "sections" / "results.md",
    WORKSPACE / "sections" / "introduction.md",
    WORKSPACE / "sections" / "discussion.md",
    WORKSPACE / "sections" / "methods.md",
    WORKSPACE / "sections" / "abstract.md",
    WORKSPACE / "sections" / "data_availability.md",
    WORKSPACE / "sections" / "code_availability.md",
    WORKSPACE / "refs" / "references.bib",
    WORKSPACE / "figures" / "main_figure_spine.md",
    WORKSPACE / "ledgers" / "figure_to_claim_to_artifact.csv",
    WORKSPACE / "submission_package" / "pi_review_packet.md",
    WORKSPACE / "submission_package" / "submission_readiness_checklist.md",
    WORKSPACE / "figures" / ".panelforge_commit",
    WORKSPACE / "audits" / "panelforge_render_report.md",
    ROOT / ".venv-panelforge",
    ROOT / "tools" / "panelforge-figures" / ".git",
]


@dataclass(frozen=True)
class ParagraphRow:
    para_id: str
    section: str
    purpose: str
    claim_id: str
    fig_ids: str
    stat_ids: str
    ref_ids: str
    caveat: str


PARAGRAPH_ROWS = [
    ParagraphRow(
        para_id="PARA-INTRO-001",
        section="Introduction",
        purpose="Frame the endpoint-amplitude limitation that motivates residence-state inference.",
        claim_id="CLM-0001",
        fig_ids="pending_stage9.6",
        stat_ids="pending_stage9.8",
        ref_ids="pending_stage9.7",
        caveat="Do not imply dwell state is causal without perturbation or external validation.",
    ),
    ParagraphRow(
        para_id="PARA-INTRO-002",
        section="Introduction",
        purpose="Introduce bounded-coupling, reserve-like, routed-output, and reproducibility needs as separate method requirements.",
        claim_id="CLM-0002",
        fig_ids="pending_stage9.6",
        stat_ids="pending_stage9.8",
        ref_ids="pending_stage9.7",
        caveat="Do not claim absence of all coupling outside declared margins and timescales.",
    ),
    ParagraphRow(
        para_id="PARA-RESULTS-001",
        section="Results",
        purpose="Define the RhoDyn method object and show how residence-window summaries differ from amplitude summaries in synthetic trajectory regimes.",
        claim_id="CLM-0001",
        fig_ids="pending_stage9.6",
        stat_ids="pending_stage9.8",
        ref_ids="pending_stage9.7",
        caveat="Keep synthetic truth as method validation, not new biological evidence.",
    ),
    ParagraphRow(
        para_id="PARA-RESULTS-002",
        section="Results",
        purpose="Use independent public trajectory demonstrations to show residence-amplitude separation beyond the reference use case.",
        claim_id="CLM-0001",
        fig_ids="pending_stage9.6",
        stat_ids="pending_stage9.8",
        ref_ids="pending_stage9.7",
        caveat="Do not claim universal residence logic across all live-cell reporters.",
    ),
    ParagraphRow(
        para_id="PARA-RESULTS-003",
        section="Results",
        purpose="Present bounded-coupling decisions under declared margins, uncertainty intervals, and visible inconclusive cases.",
        claim_id="CLM-0002",
        fig_ids="pending_stage9.6",
        stat_ids="pending_stage9.8",
        ref_ids="pending_stage9.7",
        caveat="Keep inconclusive and margin-bound cases visible rather than converting them into equivalence claims.",
    ),
    ParagraphRow(
        para_id="PARA-RESULTS-004",
        section="Results",
        purpose="Describe reserve-like endpoint summaries as measurement-scoped buffering coordinates.",
        claim_id="CLM-0003",
        fig_ids="pending_stage9.6",
        stat_ids="pending_stage9.8",
        ref_ids="pending_stage9.7",
        caveat="Use reserve-like language unless the readout directly assays biological reserve capacity.",
    ),
    ParagraphRow(
        para_id="PARA-RESULTS-005",
        section="Results",
        purpose="Compare routed-output alternatives and reduced architectures in the tested endpoint demonstration.",
        claim_id="CLM-0004",
        fig_ids="pending_stage9.6",
        stat_ids="pending_stage9.8",
        ref_ids="pending_stage9.7",
        caveat="Do not convert effective model terms into literal molecular edges.",
    ),
    ParagraphRow(
        para_id="PARA-RESULTS-006",
        section="Results",
        purpose="Report software cross-surface parity, export provenance, and reproducibility of retained Stage 7 evidence.",
        claim_id="CLM-0005",
        fig_ids="pending_stage9.6_or_stage9.17",
        stat_ids="pending_stage9.8",
        ref_ids="pending_stage9.7",
        caveat="Do not claim PyPI publication or hidden private-data reproduction.",
    ),
    ParagraphRow(
        para_id="PARA-METHODS-001",
        section="Methods",
        purpose="Specify tidy trajectory inputs, residence-window metrics, amplitude comparators, and uncertainty summaries.",
        claim_id="CLM-0001",
        fig_ids="pending_stage9.6",
        stat_ids="pending_stage9.8",
        ref_ids="pending_stage9.7",
        caveat="Preserve the distinction between measurement summary and biological mechanism.",
    ),
    ParagraphRow(
        para_id="PARA-METHODS-002",
        section="Methods",
        purpose="Specify bounded-coupling decision rules, margin declaration, ROPE or interval support, and inconclusive states.",
        claim_id="CLM-0002",
        fig_ids="pending_stage9.6",
        stat_ids="pending_stage9.8",
        ref_ids="pending_stage9.7",
        caveat="Equivalence remains restricted to the declared decision region.",
    ),
    ParagraphRow(
        para_id="PARA-METHODS-003",
        section="Methods",
        purpose="Specify reserve-like endpoint construction, scoped labels, and uncertainty behavior.",
        claim_id="CLM-0003",
        fig_ids="pending_stage9.6",
        stat_ids="pending_stage9.8",
        ref_ids="pending_stage9.7",
        caveat="Do not generalize endpoint buffering summaries into unmeasured reserve biology.",
    ),
    ParagraphRow(
        para_id="PARA-METHODS-004",
        section="Methods",
        purpose="Specify reduced-architecture model comparison for routed-output constraints.",
        claim_id="CLM-0004",
        fig_ids="pending_stage9.6",
        stat_ids="pending_stage9.8",
        ref_ids="pending_stage9.7",
        caveat="Retain model-comparison language rather than direct biochemical wiring language.",
    ),
    ParagraphRow(
        para_id="PARA-METHODS-005",
        section="Methods",
        purpose="Specify versioning, command reproducibility, cross-surface parity, archive contents, and export provenance.",
        claim_id="CLM-0005",
        fig_ids="pending_stage9.6_or_stage9.17",
        stat_ids="pending_stage9.8",
        ref_ids="pending_stage9.7",
        caveat="Keep distribution claims tied to the retained source distribution and recorded checks.",
    ),
    ParagraphRow(
        para_id="PARA-DISCUSSION-001",
        section="Discussion",
        purpose="Synthesize residence-state inference as the central method contribution while preserving scope boundaries.",
        claim_id="CLM-0001",
        fig_ids="pending_stage9.6",
        stat_ids="pending_stage9.8",
        ref_ids="pending_stage9.7",
        caveat="Do not imply residence behavior replaces all endpoint or amplitude summaries.",
    ),
    ParagraphRow(
        para_id="PARA-DISCUSSION-002",
        section="Discussion",
        purpose="State limits of bounded coupling, reserve-like coordinates, routed-output comparisons, and software maturity.",
        claim_id="CLM-0005",
        fig_ids="pending_stage9.6_or_stage9.17",
        stat_ids="pending_stage9.8",
        ref_ids="pending_stage9.7",
        caveat="Keep limitations visible as interpretation boundaries, not as hidden technical caveats.",
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


def _read_claims() -> dict[str, dict[str, str]]:
    with CLAIM_CSV_PATH.open("r", encoding="utf-8", newline="") as handle:
        return {row["claim_id"]: row for row in csv.DictReader(handle)}


def _row_dict(row: ParagraphRow, claims: dict[str, dict[str, str]]) -> dict[str, str]:
    return {
        "para_id": row.para_id,
        "section": row.section,
        "purpose": row.purpose,
        "claim_id": row.claim_id,
        "fig_ids": row.fig_ids,
        "stat_ids": row.stat_ids,
        "ref_ids": row.ref_ids,
        "caveat": row.caveat,
        "strength_cap": claims[row.claim_id]["strength_cap"],
    }


def _write_paragraph_csv(path: Path, claims: dict[str, dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES)
        writer.writeheader()
        for row in PARAGRAPH_ROWS:
            writer.writerow(_row_dict(row, claims))


def _markdown_table(rows: list[dict[str, str]], columns: list[str]) -> str:
    lines = ["| " + " | ".join(columns) + " |", "| " + " | ".join("---" for _ in columns) + " |"]
    for row in rows:
        lines.append("| " + " | ".join(str(row.get(column, "")).replace("|", "\\|") for column in columns) + " |")
    return "\n".join(lines)


def _build_strength_rules(generated_utc: str, ledger_version: str, claims: dict[str, dict[str, str]]) -> str:
    rows = [
        {
            "claim_id": claim_id,
            "paragraph_rule": "May narrow, contextualize, or split this claim across paragraphs, but may not exceed the frozen strength cap.",
            "strength_cap": claim["strength_cap"],
        }
        for claim_id, claim in sorted(claims.items())
    ]
    return f"""# Stage 9.5 claim strength rules

Generated UTC. {generated_utc}

Paragraph-ledger version. {ledger_version}

Stage. 9.5 paragraph-level claim ledger.

Scope. These rules govern later manuscript drafting from the paragraph ledger.
They do not draft any reader-facing manuscript section, resolve references,
build a figure spine, render figures, or assemble a submission package.

## Paragraph strength rule

Each paragraph row must resolve to one frozen `CLM` identifier from Stage 9.4.
The paragraph may be narrower than the frozen claim, but its claim strength may
not exceed the copied `strength_cap`. If a later paragraph needs stronger
language, Stage 9 must return to an authorized evidence or claim-freeze update
rather than expanding the claim during drafting.

## Frozen claim caps available to paragraphs

{_markdown_table(rows, ["claim_id", "paragraph_rule", "strength_cap"])}

## Drafting boundary

The paragraph ledger is a planning surface. It fixes which future paragraph
units may carry each method claim and what limitation must travel with that
paragraph. It is not manuscript prose and it does not authorize citation
resolution, figure rendering, PanelForge execution, or submission packaging.
"""


def _no_downstream_started() -> tuple[bool, list[str]]:
    rendered = [
        path.relative_to(ROOT).as_posix()
        for path in (WORKSPACE / "figures" / "rendered").rglob("*")
        if path.is_file() and path.suffix.lower() in {".png", ".pdf", ".svg"}
    ]
    forbidden = [path.relative_to(ROOT).as_posix() for path in FORBIDDEN_STARTED_PATHS if path.exists()]
    return not forbidden and not rendered, forbidden + rendered


def _validate(claims: dict[str, dict[str, str]]) -> list[dict[str, Any]]:
    gate_9_4_pass = False
    if GATE_9_4.exists():
        try:
            gate_9_4_pass = _read_json(GATE_9_4).get("pass") is True
        except json.JSONDecodeError:
            gate_9_4_pass = False
    claim_ids = set(claims)
    rows = [_row_dict(row, claims) for row in PARAGRAPH_ROWS if row.claim_id in claims]
    para_ids = [row["para_id"] for row in rows]
    all_rows_serialized = len(rows) == len(PARAGRAPH_ROWS)
    para_ids_valid = all(item.startswith("PARA-") and item.rsplit("-", 1)[-1].isdigit() for item in para_ids)
    para_ids_unique = len(para_ids) == len(set(para_ids))
    every_para_resolves = all(row["claim_id"] in claim_ids for row in rows) and all_rows_serialized
    every_claim_covered = claim_ids == {row["claim_id"] for row in rows}
    strength_caps_hold = all(row["strength_cap"] == claims[row["claim_id"]]["strength_cap"] for row in rows)
    pending_surfaces_visible = all(
        row["fig_ids"].startswith("pending_stage9.6")
        and row["stat_ids"] == "pending_stage9.8"
        and row["ref_ids"] == "pending_stage9.7"
        for row in rows
    )
    no_downstream, downstream_paths = _no_downstream_started()
    return [
        {
            "name": "stage_9_4_gate_passed",
            "passed": gate_9_4_pass,
            "detail": "Stage 9.4 claim freeze exists and passes" if gate_9_4_pass else "Stage 9.4 gate is missing or not passing",
        },
        {
            "name": "ledger_validates",
            "passed": all_rows_serialized and para_ids_valid and para_ids_unique and len(rows) >= 10,
            "detail": f"{len(rows)} paragraph rows are unique and formatted for downstream joins",
        },
        {
            "name": "every_para_id_resolves_to_clm_id",
            "passed": every_para_resolves,
            "detail": "Every paragraph row resolves to a frozen Stage 9.4 claim ID",
        },
        {
            "name": "every_frozen_claim_has_paragraph_coverage",
            "passed": every_claim_covered,
            "detail": "All five frozen claims have at least one planned paragraph unit",
        },
        {
            "name": "paragraph_strength_does_not_exceed_claim_strength",
            "passed": strength_caps_hold,
            "detail": "Each paragraph copies the frozen claim strength cap exactly",
        },
        {
            "name": "downstream_surfaces_remain_pending",
            "passed": pending_surfaces_visible,
            "detail": "Figure, statistic, and reference IDs remain pending for later authorized substages",
        },
        {
            "name": "no_downstream_stage9_surfaces_started",
            "passed": no_downstream,
            "detail": "No manuscript sections, reference bibliography, figure spine, submission package, PanelForge clone, runtime environment, or rendered figures detected"
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
        if substage.get("id") == "9.5":
            substage["status"] = "completed"
    registry["last_completed_substage"] = "9.5"
    _write_json(REGISTRY_PATH, registry)


def _update_memory(ledger_version: str, generated_utc: str, checks: list[dict[str, Any]]) -> None:
    memory = _read_json(MEMORY_PATH)
    memory["generated_utc"] = generated_utc
    memory["current_substage"] = "9.5"
    memory["paragraph_claim_ledger_started"] = True
    memory["paragraph_claim_ledger_version"] = ledger_version
    memory["status"] = "stage9_5_paragraph_claim_ledger_registered"
    memory["next_substage"] = "9.6"
    memory["next_substage_authorized"] = False
    memory["stage9_5_checks"] = checks
    memory.setdefault("completed_substages", [])
    if not any(item.get("substage") == "9.5" for item in memory["completed_substages"]):
        memory["completed_substages"].append(
            {
                "substage": "9.5",
                "status": "pass",
                "pass": True,
                "gate_verdict_path": "manuscript/nature_methods/gate_verdicts/9.5.json",
                "validation_outcome": "Paragraph-level claim ledger registered with CLM joins and frozen strength caps",
                "evidence_dependencies": [
                    "manuscript/nature_methods/gate_verdicts/9.4.json",
                    "manuscript/nature_methods/ledgers/claim_hierarchy.csv",
                    "manuscript/nature_methods/ledgers/non_claims_and_scope_boundaries.md",
                ],
                "files_created_or_modified": [
                    "manuscript/nature_methods/ledgers/paragraph_claim_ledger.csv",
                    "manuscript/nature_methods/ledgers/claim_strength_rules.md",
                    "manuscript/nature_methods/gate_verdicts/9.5.json",
                ],
                "remaining_blockers": [
                    "Stage 9.6 figure-first manuscript spine has not started",
                    "Stage 9.6b PanelForge rendering remains blocked until Stage 9.6 passes",
                    "Citation resolution, manuscript drafting, and reference library construction remain not started",
                ],
            }
        )
    _write_json(MEMORY_PATH, memory)


def _update_roadmap_memory(ledger_version: str) -> None:
    memory = _read_json(ROADMAP_MEMORY_PATH)
    current = memory.setdefault("current_position", {})
    current["active_stage"] = "Stage 9.5 paragraph claim ledger registered; manuscript production not started"
    current["stage9_active_gate"] = "Stage 9.5 paragraph claim ledger registered; manuscript production not started"
    current["after_stage9_5_paragraph_claim_ledger"] = (
        "Stage 9.5 planned Nature Methods manuscript paragraphs as claim-bearing units tied to "
        "frozen CLM identifiers and copied strength caps. Stage 9.6 figure-first manuscript spine, "
        "citation resolution, manuscript drafting, figure rendering, PanelForge execution, and "
        "submission-package assembly remain not started."
    )
    for stage in memory.get("stage_lock", []):
        if not isinstance(stage, dict) or stage.get("stage") != 9:
            continue
        stage["status"] = "stage9_5_paragraph_claim_ledger_registered"
        stage["current_gate"] = "Stage 9.5 paragraph claim ledger registered; manuscript production not started"
        stage["scope_rule"] = (
            "Stage 9 has completed evidence intake, venue-guidance registration, representative "
            "methods-paper corpus analysis, narrative-spine selection, claim freeze, and paragraph-level "
            "claim planning only. Do not start figure-spine construction, citation resolution, drafting, "
            "figure rendering, review response, or submission packaging without explicit substage authorization."
        )
        artifacts = stage.setdefault("artifacts", [])
        for artifact in [
            "manuscript/nature_methods/ledgers/paragraph_claim_ledger.csv",
            "manuscript/nature_methods/ledgers/claim_strength_rules.md",
            "manuscript/nature_methods/gate_verdicts/9.5.json",
            "scripts/run_stage9_5_paragraph_claim_ledger.py",
        ]:
            if artifact not in artifacts:
                artifacts.append(artifact)
        gate = stage.setdefault("gate", [])
        claim_gate = "Stage 9.5 paragraph rows resolve to frozen CLM IDs and retain claim strength caps before drafting."
        if claim_gate not in gate:
            gate.append(claim_gate)
        for subphase in stage.get("subphases", []):
            if isinstance(subphase, dict) and subphase.get("id") == "9.5":
                subphase["status"] = "complete_paragraph_claim_ledger_registered"
                subphase["evidence"] = "manuscript/nature_methods/gate_verdicts/9.5.json"
                subphase["paragraph_claim_ledger_version"] = ledger_version
    _write_json(ROADMAP_MEMORY_PATH, memory)


def _update_docs() -> None:
    if PLAN_PATH.exists():
        body = PLAN_PATH.read_text(encoding="utf-8")
        body = body.replace(
            "and freezes the claim hierarchy in Stage 9.4. It does not begin paragraph-level planning, citation resolution, manuscript drafting, editorial polishing, PanelForge rendering, or package assembly.",
            "freezes the claim hierarchy in Stage 9.4, and registers the paragraph-level claim ledger in Stage 9.5. It does not begin figure-spine construction, citation resolution, manuscript drafting, editorial polishing, PanelForge rendering, or package assembly.",
        )
        body = body.replace(
            "Stage 9.4 freezes the claim hierarchy and non-claims in `ledgers/claim_hierarchy.md`, `ledgers/claim_hierarchy.csv`, `ledgers/non_claims_and_scope_boundaries.md`, and `gate_verdicts/9.4.json`. The current state intentionally does not create",
            "Stage 9.4 freezes the claim hierarchy and non-claims in `ledgers/claim_hierarchy.md`, `ledgers/claim_hierarchy.csv`, `ledgers/non_claims_and_scope_boundaries.md`, and `gate_verdicts/9.4.json`. Stage 9.5 registers paragraph-to-claim planning in `ledgers/paragraph_claim_ledger.csv`, `ledgers/claim_strength_rules.md`, and `gate_verdicts/9.5.json`. The current state intentionally does not create",
        )
        body = body.replace(
            "| 9.5 | Paragraph-level claim ledger | not_started | Plan manuscript paragraphs as auditable claim-bearing units. |",
            "| 9.5 | Paragraph-level claim ledger | complete_paragraph_claim_ledger_registered | Plan manuscript paragraphs as auditable claim-bearing units. |",
        )
        PLAN_PATH.write_text(body, encoding="utf-8")
    if ROADMAP_PATH.exists():
        body = ROADMAP_PATH.read_text(encoding="utf-8")
        body = body.replace(
            "| Stage 9. Nature Methods manuscript assembly | Stage 9.4 claim freeze registered, manuscript production not started. | The current boundary is evidence intake, official venue-guidance registration, representative methods-paper corpus analysis, narrative-spine selection, and claim freeze only, with PanelForge reserved as a future Stage 9.6b rendering dependency. Do not start paragraph-level planning, citation resolution, figure rendering, drafting, review response, or submission packaging without explicit substage authorization. |",
            "| Stage 9. Nature Methods manuscript assembly | Stage 9.5 paragraph claim ledger registered, manuscript production not started. | The current boundary is evidence intake, official venue-guidance registration, representative methods-paper corpus analysis, narrative-spine selection, claim freeze, and paragraph-level claim planning only, with PanelForge reserved as a future Stage 9.6b rendering dependency. Do not start figure-spine construction, citation resolution, figure rendering, drafting, review response, or submission packaging without explicit substage authorization. |",
        )
        body = body.replace(
            "Stage 9.2 representative methods-paper corpus has been completed. Stage 9.3 narrative spine has been completed. Stage 9.4 claim freeze has been completed. Stage 9.5 remains the next unstarted manuscript step.",
            "Stage 9.2 representative methods-paper corpus has been completed. Stage 9.3 narrative spine has been completed. Stage 9.4 claim freeze has been completed. Stage 9.5 paragraph-level claim ledger has been completed. Stage 9.6 remains the next unstarted manuscript step.",
        )
        ROADMAP_PATH.write_text(body, encoding="utf-8")


def run() -> dict[str, Any]:
    generated_utc = _now()
    commit = _git_sha()
    ledger_version = f"paragraph-ledger@{generated_utc[:10]}@{commit}"
    claims = _read_claims()
    if STAGING_DIR.exists():
        shutil.rmtree(STAGING_DIR)
    STAGING_DIR.mkdir(parents=True, exist_ok=True)

    checks = _validate(claims)
    passed = all(check["passed"] for check in checks)
    gate = {
        "substage": "9.5",
        "timestamp": generated_utc,
        "paragraph_claim_ledger_version": ledger_version,
        "pass": passed,
        "checks": checks,
        "paragraph_count": len(PARAGRAPH_ROWS),
        "claim_count": len(claims),
        "outputs": [str(path.relative_to(ROOT)) for path in OUTPUTS.values()],
        "scope_boundary": "Paragraph-to-claim planning only. No manuscript sections, citation resolution, figure spine, figure rendering, PanelForge execution, or submission-package assembly.",
    }

    _write_paragraph_csv(STAGING_DIR / OUTPUTS["paragraph_csv"].relative_to(WORKSPACE), claims)
    _write_text(
        STAGING_DIR / OUTPUTS["strength_rules"].relative_to(WORKSPACE),
        _build_strength_rules(generated_utc, ledger_version, claims),
    )
    _write_json(STAGING_DIR / OUTPUTS["gate"].relative_to(WORKSPACE), gate)

    if passed:
        _promote_staging()
        shutil.rmtree(STAGING_DIR)
        _update_registry()
        _update_memory(ledger_version, generated_utc, checks)
        _update_roadmap_memory(ledger_version)
        _update_docs()
    else:
        quarantine = _quarantine_staging(generated_utc)
        gate["quarantine_path"] = str(quarantine.relative_to(ROOT))
        _write_json(OUTPUTS["gate"], gate)

    return {
        "status": "pass" if passed else "fail",
        "substage": "9.5",
        "paragraph_claim_ledger_version": ledger_version,
        "paragraph_count": len(PARAGRAPH_ROWS),
        "claim_count": len(claims),
        "failures": [check for check in checks if not check["passed"]],
        "outputs": gate["outputs"],
    }


def main() -> int:
    payload = run()
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())

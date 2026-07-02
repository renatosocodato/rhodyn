"""Run Stage 9.4 manuscript claim-freeze registration.

Stage 9.4 freezes the central RhoDyn methods-paper claims with stable claim
IDs, evidence artifact links, and strength caps. It does not draft manuscript
paragraphs, build a figure spine, resolve citations, render figures, or assemble
a submission package.
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
STAGING_DIR = WORKSPACE / "_staging" / "9.4"
QUARANTINE_DIR = WORKSPACE / "_quarantine" / "9.4"
MEMORY_PATH = ROOT / "docs" / "stage9_execution_memory.json"
ROADMAP_MEMORY_PATH = ROOT / "docs" / "roadmap_execution_memory.json"
REGISTRY_PATH = WORKSPACE / "contracts" / "stage9_substage_registry.json"
PLAN_PATH = ROOT / "docs" / "stage9_manuscript_assembly_plan.md"
ROADMAP_PATH = ROOT / "docs" / "roadmap.md"
EVIDENCE_MANIFEST_PATH = LEDGER_DIR / "stage9_evidence_manifest.csv"
GATE_9_3 = GATE_DIR / "9.3.json"

OUTPUTS = {
    "claim_md": LEDGER_DIR / "claim_hierarchy.md",
    "claim_csv": LEDGER_DIR / "claim_hierarchy.csv",
    "non_claims": LEDGER_DIR / "non_claims_and_scope_boundaries.md",
    "gate": GATE_DIR / "9.4.json",
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
class FrozenClaim:
    claim_id: str
    source_claim_id: str
    claim: str
    class_: str
    confidence: str
    evidence_art_ids: tuple[str, ...]
    fig_ids: str
    location: str
    strength_cap: str
    limitation: str


CLAIMS = [
    FrozenClaim(
        claim_id="CLM-0001",
        source_claim_id="C1",
        claim="Residence-window summaries can expose time-in-state behavior that amplitude summaries miss.",
        class_="central_method_claim",
        confidence="supported_for_methods_drafting",
        evidence_art_ids=("ART-0027", "ART-0029", "ART-0032", "ART-0033", "ART-0034"),
        fig_ids="pending_stage9.6",
        location="Results/Methods",
        strength_cap="May claim residence summaries reveal time-in-state structure beyond amplitude summaries in tested trajectory regimes.",
        limitation="Do not claim that dwell state causes downstream biology without perturbation or external validation.",
    ),
    FrozenClaim(
        claim_id="CLM-0002",
        source_claim_id="C2",
        claim="Bounded-coupling decisions require predeclared margins, uncertainty intervals, and ROPE or interval support when supplied.",
        class_="central_method_claim",
        confidence="supported_with_inconclusive_contexts_visible",
        evidence_art_ids=("ART-0036", "ART-0037", "ART-0041", "ART-0042", "ART-0043", "ART-0048"),
        fig_ids="pending_stage9.6",
        location="Results/Methods",
        strength_cap="May claim bounded coupling is decision-ready only under declared margins, uncertainty, and visible inconclusive cases.",
        limitation="Do not claim absence of all crosstalk, slower coupling, or universal biochemical equivalence.",
    ),
    FrozenClaim(
        claim_id="CLM-0003",
        source_claim_id="C3",
        claim="Reserve-like summaries can be integrated when the readout is scoped to the measured endpoint.",
        class_="central_method_claim",
        confidence="supported_with_reserve_like_language",
        evidence_art_ids=("ART-0036", "ART-0039", "ART-0040", "ART-0049", "ART-0050"),
        fig_ids="pending_stage9.6",
        location="Results/Methods",
        strength_cap="May claim reserve-like endpoint summaries are interpretable when scoped to the measured readout.",
        limitation="Do not call a reserve-like coordinate biological reserve unless the measurement directly assays reserve capacity.",
    ),
    FrozenClaim(
        claim_id="CLM-0004",
        source_claim_id="C4",
        claim="Reduced-architecture comparison can expose when simpler endpoint mappings do not satisfy routed-output constraints.",
        class_="central_method_claim",
        confidence="supported_without_molecular_edge_claim",
        evidence_art_ids=("ART-0036", "ART-0038", "ART-0040", "ART-0051"),
        fig_ids="pending_stage9.6",
        location="Results/Methods",
        strength_cap="May claim reduced alternatives can fail routed-output constraints in the tested endpoint demonstration.",
        limitation="Do not convert effective model parameters into literal molecular edges.",
    ),
    FrozenClaim(
        claim_id="CLM-0005",
        source_claim_id="C5",
        claim="The current RhoDyn release can reproduce retained Stage 7 evidence from a source distribution and expose user-facing export provenance.",
        class_="software_reproducibility_claim",
        confidence="supported_for_software_reproducibility_claim",
        evidence_art_ids=("ART-0006", "ART-0007", "ART-0010", "ART-0011", "ART-0018", "ART-0021", "ART-0022", "ART-0023", "ART-0024", "ART-0045", "ART-0046", "ART-0047", "ART-0052", "ART-0053"),
        fig_ids="pending_stage9.6_or_stage9.17",
        location="Methods/Availability",
        strength_cap="May claim source-distribution reproduction, cross-surface parity, and export provenance for retained Stage 7 evidence.",
        limitation="Do not claim PyPI publication or hidden private-data reproduction.",
    ),
]

NON_CLAIMS = [
    {
        "id": "NC-001",
        "boundary": "RhoDyn did not generate the original RhoA/microglia manuscript results.",
        "reason": "The manuscript remains an optional reference use case, not the source of the software generality claim.",
    },
    {
        "id": "NC-002",
        "boundary": "RhoDyn does not discover the correct biological residence window by itself.",
        "reason": "Residence windows require predeclared biological justification, sensitivity analysis, or independent support.",
    },
    {
        "id": "NC-003",
        "boundary": "Bounded coupling is not proof of no crosstalk.",
        "reason": "Equivalence decisions are restricted to declared margins, timescales, measurements, and uncertainty support.",
    },
    {
        "id": "NC-004",
        "boundary": "Reserve-like summaries are not automatically biological reserve.",
        "reason": "The reserve language must track whether the readout directly measures buffering capacity.",
    },
    {
        "id": "NC-005",
        "boundary": "Reduced-architecture parameters are not literal molecular edges.",
        "reason": "The method compares effective alternatives and routed-output constraints, not direct biochemical wiring.",
    },
    {
        "id": "NC-006",
        "boundary": "Stage 9.4 does not claim Nature Methods acceptance or venue sufficiency.",
        "reason": "Venue fit is a planning decision, not a publication outcome.",
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


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_text(path: Path, body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body.rstrip() + "\n", encoding="utf-8")


def _markdown_table(rows: list[dict[str, str]], columns: list[str]) -> str:
    lines = ["| " + " | ".join(columns) + " |", "| " + " | ".join("---" for _ in columns) + " |"]
    for row in rows:
        lines.append("| " + " | ".join(str(row.get(column, "")).replace("|", "\\|") for column in columns) + " |")
    return "\n".join(lines)


def _read_evidence_manifest() -> dict[str, dict[str, str]]:
    if not EVIDENCE_MANIFEST_PATH.exists():
        return {}
    with EVIDENCE_MANIFEST_PATH.open("r", encoding="utf-8", newline="") as handle:
        return {row["art_id"]: row for row in csv.DictReader(handle)}


def _write_claim_csv(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = ["claim_id", "class", "confidence", "evidence_art_ids", "fig_ids", "location", "strength_cap"]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for claim in CLAIMS:
            writer.writerow(
                {
                    "claim_id": claim.claim_id,
                    "class": claim.class_,
                    "confidence": claim.confidence,
                    "evidence_art_ids": ";".join(claim.evidence_art_ids),
                    "fig_ids": claim.fig_ids,
                    "location": claim.location,
                    "strength_cap": claim.strength_cap,
                }
            )


def _build_claim_markdown(generated_utc: str, claim_version: str) -> str:
    rows = [
        {
            "claim_id": claim.claim_id,
            "source": claim.source_claim_id,
            "claim": claim.claim,
            "evidence": "; ".join(claim.evidence_art_ids),
            "strength_cap": claim.strength_cap,
            "limitation": claim.limitation,
        }
        for claim in CLAIMS
    ]
    return f"""# Stage 9.4 claim hierarchy

Generated UTC. {generated_utc}

Claim-freeze version. {claim_version}

Stage. 9.4 manuscript claim freeze.

Scope. This ledger freezes the central RhoDyn methods-paper claims that can be
used in later paragraph, figure, and Methods planning. It is not manuscript
prose, not a figure plan, and not a reference bibliography.

## Frozen central claims

{_markdown_table(rows, ["claim_id", "source", "claim", "evidence", "strength_cap", "limitation"])}

## Strength-cap rule

Later manuscript paragraphs may narrow these claims but may not exceed the
listed strength cap. A paragraph, figure, or legend that needs a stronger claim
must return to a later authorized evidence step rather than silently expanding
the claim.
"""


def _build_non_claims_markdown(generated_utc: str) -> str:
    return f"""# Non-claims and scope boundaries

Generated UTC. {generated_utc}

Stage. 9.4 manuscript claim freeze.

These boundaries define what the RhoDyn Nature Methods manuscript should not
claim from the current evidence package.

{_markdown_table(NON_CLAIMS, ["id", "boundary", "reason"])}

## Use in later drafting

The non-claims list is binding for Stage 9.5 and later drafting stages. Claims
can be narrowed for clarity, but these boundaries should not be removed unless a
later authorized analysis explicitly changes the evidence base.
"""


def _no_downstream_started() -> tuple[bool, list[str]]:
    rendered = [
        path.relative_to(ROOT).as_posix()
        for path in (WORKSPACE / "figures" / "rendered").rglob("*")
        if path.is_file() and path.suffix.lower() in {".png", ".pdf", ".svg"}
    ]
    forbidden = [path.relative_to(ROOT).as_posix() for path in FORBIDDEN_STARTED_PATHS if path.exists()]
    return not forbidden and not rendered, forbidden + rendered


def _validate() -> list[dict[str, Any]]:
    gate_9_3_pass = False
    if GATE_9_3.exists():
        try:
            gate_9_3_pass = _read_json(GATE_9_3).get("pass") is True
        except json.JSONDecodeError:
            gate_9_3_pass = False
    evidence = _read_evidence_manifest()
    evidence_ids = set(evidence)
    all_claim_ids_unique = len({claim.claim_id for claim in CLAIMS}) == len(CLAIMS)
    claim_ids_valid = all(claim.claim_id.startswith("CLM-") and len(claim.claim_id) == 8 for claim in CLAIMS)
    central_claims_have_evidence = all(set(claim.evidence_art_ids).issubset(evidence_ids) and claim.evidence_art_ids for claim in CLAIMS)
    strength_caps_present = all(claim.strength_cap and claim.limitation for claim in CLAIMS)
    non_claims_non_empty = len(NON_CLAIMS) >= 5 and all(item["boundary"] and item["reason"] for item in NON_CLAIMS)
    no_downstream, downstream_paths = _no_downstream_started()
    return [
        {
            "name": "stage_9_3_gate_passed",
            "passed": gate_9_3_pass,
            "detail": "Stage 9.3 narrative spine exists and passes" if gate_9_3_pass else "Stage 9.3 gate is missing or not passing",
        },
        {
            "name": "claim_hierarchy_validates",
            "passed": all_claim_ids_unique and claim_ids_valid and len(CLAIMS) == 5,
            "detail": "Five stable CLM IDs are unique and formatted for downstream joins",
        },
        {
            "name": "every_central_claim_has_evidence",
            "passed": central_claims_have_evidence,
            "detail": "All frozen central claims resolve to locked Stage 9 ART IDs",
        },
        {
            "name": "every_claim_has_strength_cap",
            "passed": strength_caps_present,
            "detail": "Every frozen claim has a strength cap and an explicit limitation",
        },
        {
            "name": "non_claims_ledger_is_non_empty",
            "passed": non_claims_non_empty,
            "detail": f"{len(NON_CLAIMS)} non-claims and scope boundaries registered",
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
        if substage.get("id") == "9.4":
            substage["status"] = "completed"
    registry["last_completed_substage"] = "9.4"
    _write_json(REGISTRY_PATH, registry)


def _update_memory(claim_version: str, generated_utc: str, checks: list[dict[str, Any]]) -> None:
    memory = _read_json(MEMORY_PATH)
    memory["generated_utc"] = generated_utc
    memory["current_substage"] = "9.4"
    memory["claim_freeze_started"] = True
    memory["claim_freeze_version"] = claim_version
    memory["status"] = "stage9_4_claim_freeze_registered"
    memory["next_substage"] = "9.5"
    memory["next_substage_authorized"] = False
    memory["stage9_4_checks"] = checks
    memory.setdefault("completed_substages", [])
    if not any(item.get("substage") == "9.4" for item in memory["completed_substages"]):
        memory["completed_substages"].append(
            {
                "substage": "9.4",
                "status": "pass",
                "pass": True,
                "gate_verdict_path": "manuscript/nature_methods/gate_verdicts/9.4.json",
                "validation_outcome": "Claim hierarchy, evidence links, strength caps, and non-claims registered before drafting",
                "evidence_dependencies": [
                    "manuscript/nature_methods/gate_verdicts/9.3.json",
                    "manuscript/nature_methods/ledgers/stage9_evidence_manifest.csv",
                    "case_studies/stage7_methods_readiness/claim_evidence_crosswalk.tsv",
                ],
                "files_created_or_modified": [
                    "manuscript/nature_methods/ledgers/claim_hierarchy.md",
                    "manuscript/nature_methods/ledgers/claim_hierarchy.csv",
                    "manuscript/nature_methods/ledgers/non_claims_and_scope_boundaries.md",
                    "manuscript/nature_methods/gate_verdicts/9.4.json",
                ],
                "remaining_blockers": [
                    "Stage 9.5 paragraph-level claim ledger has not started",
                    "Stage 9.6 figure-to-claim contract has not started",
                    "Stage 9.6b PanelForge rendering remains blocked until Stage 9.6 passes",
                    "Manuscript drafting and reference library construction remain not started",
                ],
            }
        )
    _write_json(MEMORY_PATH, memory)


def _update_roadmap_memory(claim_version: str) -> None:
    memory = _read_json(ROADMAP_MEMORY_PATH)
    current = memory.setdefault("current_position", {})
    current["active_stage"] = "Stage 9.4 claim freeze registered; manuscript production not started"
    current["stage9_active_gate"] = "Stage 9.4 claim freeze registered; manuscript production not started"
    current["after_stage9_4_claim_freeze"] = (
        "Stage 9.4 froze five central RhoDyn methods-paper claims with evidence artifact links, "
        "strength caps, and explicit non-claims. Stage 9.5 paragraph claim ledger, citation "
        "resolution, manuscript drafting, figure rendering, PanelForge execution, and submission-package "
        "assembly remain not started."
    )
    for stage in memory.get("stage_lock", []):
        if not isinstance(stage, dict) or stage.get("stage") != 9:
            continue
        stage["status"] = "stage9_4_claim_freeze_registered"
        stage["current_gate"] = "Stage 9.4 claim freeze registered; manuscript production not started"
        stage["scope_rule"] = (
            "Stage 9 has completed evidence intake, venue-guidance registration, representative "
            "methods-paper corpus analysis, narrative-spine selection, and claim freeze only. Do not "
            "start paragraph-level planning, citation resolution, drafting, figure rendering, review "
            "response, or submission packaging without explicit substage authorization."
        )
        artifacts = stage.setdefault("artifacts", [])
        for artifact in [
            "manuscript/nature_methods/ledgers/claim_hierarchy.md",
            "manuscript/nature_methods/ledgers/claim_hierarchy.csv",
            "manuscript/nature_methods/ledgers/non_claims_and_scope_boundaries.md",
            "manuscript/nature_methods/gate_verdicts/9.4.json",
            "scripts/run_stage9_4_claim_freeze.py",
        ]:
            if artifact not in artifacts:
                artifacts.append(artifact)
        gate = stage.setdefault("gate", [])
        claim_gate = "Stage 9.4 claim hierarchy is frozen with evidence links and strength caps before drafting."
        if claim_gate not in gate:
            gate.append(claim_gate)
        for subphase in stage.get("subphases", []):
            if isinstance(subphase, dict) and subphase.get("id") == "9.4":
                subphase["status"] = "complete_claim_freeze_registered"
                subphase["evidence"] = "manuscript/nature_methods/gate_verdicts/9.4.json"
                subphase["claim_freeze_version"] = claim_version
    _write_json(ROADMAP_MEMORY_PATH, memory)


def _update_docs() -> None:
    if PLAN_PATH.exists():
        body = PLAN_PATH.read_text(encoding="utf-8")
        body = body.replace(
            "and registers the Nature Methods Article narrative spine in Stage 9.3. It does not begin claim freeze, citation resolution, manuscript drafting, editorial polishing, PanelForge rendering, or package assembly.",
            "registers the Nature Methods Article narrative spine in Stage 9.3, and freezes the claim hierarchy in Stage 9.4. It does not begin paragraph-level planning, citation resolution, manuscript drafting, editorial polishing, PanelForge rendering, or package assembly.",
        )
        body = body.replace(
            "Stage 9.3 registers the Nature Methods Article narrative spine in `stage9_narrative_spine.md`, `audits/venue_fit_rationale.md`, and `gate_verdicts/9.3.json`. The current state intentionally does not create",
            "Stage 9.3 registers the Nature Methods Article narrative spine in `stage9_narrative_spine.md`, `audits/venue_fit_rationale.md`, and `gate_verdicts/9.3.json`. Stage 9.4 freezes the claim hierarchy and non-claims in `ledgers/claim_hierarchy.md`, `ledgers/claim_hierarchy.csv`, `ledgers/non_claims_and_scope_boundaries.md`, and `gate_verdicts/9.4.json`. The current state intentionally does not create",
        )
        body = body.replace(
            "| 9.4 | Manuscript claim freeze | not_started | Freeze claim hierarchy with stable CLM IDs and strength caps. |",
            "| 9.4 | Manuscript claim freeze | complete_claim_freeze_registered | Freeze claim hierarchy with stable CLM IDs and strength caps. |",
        )
        PLAN_PATH.write_text(body, encoding="utf-8")
    if ROADMAP_PATH.exists():
        body = ROADMAP_PATH.read_text(encoding="utf-8")
        body = body.replace(
            "| Stage 9. Nature Methods manuscript assembly | Stage 9.3 narrative spine registered, manuscript production not started. | The current boundary is evidence intake, official venue-guidance registration, representative methods-paper corpus analysis, and narrative-spine selection only, with PanelForge reserved as a future Stage 9.6b rendering dependency. Do not start claim freeze, citation resolution, figure rendering, drafting, review response, or submission packaging without explicit substage authorization. |",
            "| Stage 9. Nature Methods manuscript assembly | Stage 9.4 claim freeze registered, manuscript production not started. | The current boundary is evidence intake, official venue-guidance registration, representative methods-paper corpus analysis, narrative-spine selection, and claim freeze only, with PanelForge reserved as a future Stage 9.6b rendering dependency. Do not start paragraph-level planning, citation resolution, figure rendering, drafting, review response, or submission packaging without explicit substage authorization. |",
        )
        body = body.replace(
            "Stage 9.2 representative methods-paper corpus has been completed. Stage 9.3 narrative spine has been completed. Stage 9.4 remains the next unstarted manuscript step.",
            "Stage 9.2 representative methods-paper corpus has been completed. Stage 9.3 narrative spine has been completed. Stage 9.4 claim freeze has been completed. Stage 9.5 remains the next unstarted manuscript step.",
        )
        ROADMAP_PATH.write_text(body, encoding="utf-8")


def run() -> dict[str, Any]:
    generated_utc = _now()
    commit = _git_sha()
    claim_version = f"claim-freeze@{generated_utc[:10]}@{commit}"
    if STAGING_DIR.exists():
        shutil.rmtree(STAGING_DIR)
    STAGING_DIR.mkdir(parents=True, exist_ok=True)

    checks = _validate()
    passed = all(check["passed"] for check in checks)
    gate = {
        "substage": "9.4",
        "timestamp": generated_utc,
        "claim_freeze_version": claim_version,
        "pass": passed,
        "checks": checks,
        "claim_count": len(CLAIMS),
        "non_claim_count": len(NON_CLAIMS),
        "outputs": [str(path.relative_to(ROOT)) for path in OUTPUTS.values()],
        "scope_boundary": "Claim hierarchy and non-claims registration only. No paragraph ledger, citation resolution, drafting, figure rendering, PanelForge execution, or submission-package assembly.",
    }

    _write_text(STAGING_DIR / OUTPUTS["claim_md"].relative_to(WORKSPACE), _build_claim_markdown(generated_utc, claim_version))
    _write_claim_csv(STAGING_DIR / OUTPUTS["claim_csv"].relative_to(WORKSPACE))
    _write_text(STAGING_DIR / OUTPUTS["non_claims"].relative_to(WORKSPACE), _build_non_claims_markdown(generated_utc))
    _write_json(STAGING_DIR / OUTPUTS["gate"].relative_to(WORKSPACE), gate)

    if passed:
        _promote_staging()
        shutil.rmtree(STAGING_DIR)
        _update_registry()
        _update_memory(claim_version, generated_utc, checks)
        _update_roadmap_memory(claim_version)
        _update_docs()
    else:
        quarantine = _quarantine_staging(generated_utc)
        gate["quarantine_path"] = str(quarantine.relative_to(ROOT))
        _write_json(OUTPUTS["gate"], gate)

    return {
        "status": "pass" if passed else "fail",
        "substage": "9.4",
        "claim_freeze_version": claim_version,
        "claim_count": len(CLAIMS),
        "non_claim_count": len(NON_CLAIMS),
        "failures": [check for check in checks if not check["passed"]],
        "outputs": gate["outputs"],
    }


def main() -> int:
    payload = run()
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())

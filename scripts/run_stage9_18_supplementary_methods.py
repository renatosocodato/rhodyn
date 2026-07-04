"""Run Stage 9.18 Supplementary Methods drafting.

Stage 9.18 moves technical depth into a structured Supplementary Methods
surface linked to planned supplementary support items. It does not create
supplementary tables, figure legends, the full reference library, or the final
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
LEDGERS_DIR = WORKSPACE / "ledgers"
SUPPLEMENTARY_DIR = WORKSPACE / "supplementary"
GATE_DIR = WORKSPACE / "gate_verdicts"
STAGING_DIR = WORKSPACE / "_staging" / "9.18"
QUARANTINE_DIR = WORKSPACE / "_quarantine" / "9.18"
MEMORY_PATH = ROOT / "docs" / "stage9_execution_memory.json"
ROADMAP_MEMORY_PATH = ROOT / "docs" / "roadmap_execution_memory.json"
REGISTRY_PATH = WORKSPACE / "contracts" / "stage9_substage_registry.json"
PLAN_PATH = ROOT / "docs" / "stage9_manuscript_assembly_plan.md"
ROADMAP_PATH = ROOT / "docs" / "roadmap.md"
SUPPLEMENTARY_PLAN = SUPPLEMENTARY_DIR / "supplementary_item_plan.md"
SUPPLEMENTARY_CALLOUT_LEDGER = LEDGERS_DIR / "supplementary_callout_ledger.csv"
CLAIM_HIERARCHY = LEDGERS_DIR / "claim_hierarchy.csv"
RESULTS_PATH = SECTIONS_DIR / "results.md"
METHODS_PATH = SECTIONS_DIR / "methods.md"
DISCUSSION_PATH = SECTIONS_DIR / "discussion.md"
GATE_917 = GATE_DIR / "9.17.json"

OUTPUTS = {
    "supplementary_methods": SUPPLEMENTARY_DIR / "supplementary_methods.md",
    "gate": GATE_DIR / "9.18.json",
}

FORBIDDEN_STARTED_PATHS = [
    WORKSPACE / "refs" / "references.bib",
    WORKSPACE / "figures" / "figure_legends.md",
    SUPPLEMENTARY_DIR / "supplementary_tables_plan.md",
    WORKSPACE / "submission_package" / "pi_review_packet.md",
    WORKSPACE / "submission_package" / "submission_readiness_checklist.md",
]

FORBIDDEN_VISIBLE_PHRASES = (
    "universal residence law",
    "automatic mechanism-discovery",
    "true biological reserve",
    "literal molecular edge",
    "absence of all coupling",
    "private-data reproduction claim",
    "PyPI publication is claimed",
    "therapeutic",
)

REQUIRED_BOUNDARY_PHRASES = (
    "not independent biological evidence",
    "not proof that all coupling is absent",
    "not direct assays of unmeasured biological reserve capacity",
    "does not identify direct biochemical interactions",
    "does not imply PyPI publication",
    "not a universal biological rule",
)


@dataclass(frozen=True)
class SupplementaryBlock:
    heading: str
    supp_ids: tuple[str, ...]
    claim_ids: tuple[str, ...]
    source_artifacts: tuple[str, ...]
    text: str


SUPPLEMENTARY_BLOCKS = (
    SupplementaryBlock(
        heading="Supplementary Methods 1. Input contracts, method definitions, and truth cases",
        supp_ids=("SUPP-001", "SUPP-002"),
        claim_ids=("CLM-0001", "CLM-0005"),
        source_artifacts=("ART-0016", "ART-0017", "ART-0025", "ART-0026", "ART-0027", "ART-0028", "ART-0029", "ART-0030", "ART-0031"),
        text=(
            "The supplementary input-contract section makes the method object reconstructable from table structure before any biological interpretation is attached. "
            "Trajectory inputs retain `cell_id`, non-negative `time`, `condition`, numeric `signal`, and optional grouping fields such as `replicate`; endpoint-model rows retain `model`, `endpoint`, `observed`, `predicted`, and optional non-negative `weight`; reserve-like and bounded-coupling rows retain the measured response or contrast fields needed for their own decision rules. "
            "This section also records the declared window indicator \\(I_W(t_k)\\), residence time \\(R_T=\\sum_k \\Delta t_k I_W(t_k)\\), residence fraction \\(R_F=R_T/\\sum_k \\Delta t_k\\), dwell-segment count, and amplitude comparators used in the main Methods. "
            "Synthetic positive, negative, and ambiguous truth cases are kept with the same schema so reviewers can see when residence-state inference changes the decision, when it agrees with amplitude summaries, and when the input is insufficient. "
            "These supplementary items support method definition and benchmark behavior only; they are not independent biological evidence."
        ),
    ),
    SupplementaryBlock(
        heading="Supplementary Methods 2. Public live-cell signaling adapters",
        supp_ids=("SUPP-003",),
        claim_ids=("CLM-0001",),
        source_artifacts=("ART-0032", "ART-0033", "ART-0034", "ART-0035"),
        text=(
            "The public-adapter section specifies how retained DRG calcium and ERK GPCR reporter tables were converted into the same tidy trajectory object used for synthetic truth cases. "
            "Adapters preserve the public source record, trace or object identifier, condition label, sampled time, reporter signal, and available grouping fields before residence, amplitude, window-sensitivity, and uncertainty summaries are calculated. "
            "The DRG calcium route uses the public source DOI 10.5281/zenodo.14907827, and the ERK GPCR route uses DOI 10.5281/zenodo.5836623. "
            "The supplementary sensitivity summaries expose how a declared window changes residence calls, which makes fragile and unresolved regions visible rather than promoting a single preferred threshold. "
            "The purpose is to show that the same analysis object can be applied to independent public live-cell reporters; it is not a universal biological rule for all calcium, ERK, kinase, or GTPase trajectories."
        ),
    ),
    SupplementaryBlock(
        heading="Supplementary Methods 3. Bounded-coupling decisions and held-out contexts",
        supp_ids=("SUPP-004", "SUPP-007"),
        claim_ids=("CLM-0002",),
        source_artifacts=("ART-0036", "ART-0037", "ART-0040", "ART-0041", "ART-0042", "ART-0043", "ART-0044", "ART-0048"),
        text=(
            "The bounded-coupling supplementary section preserves the predeclared contrast, uncertainty interval, grouping level, and biological margin that must be present before a contrast can be interpreted. "
            "For an estimate \\(\\hat\\delta\\), interval \\([L,U]\\), and positive margin \\(\\Delta\\), the interval decision passes only when \\(-\\Delta \\le L \\le U \\le \\Delta\\); where posterior samples or a ROPE mass are available, the reported decision also records whether the declared posterior mass threshold is met. "
            "Held-out ERK/Akt contexts reuse fixed thresholds and margins from the preceding evidence stage, then report pass, fail, and inconclusive states side by side. "
            "The supplementary margin-sensitivity records show when the decision depends on a narrow choice of \\(\\Delta\\), and access-boundary notes identify cases where retained derived tables represent source material that is not redistributed. "
            "A passing bounded-coupling decision is therefore equivalence within a declared margin and context, not proof that all coupling is absent."
        ),
    ),
    SupplementaryBlock(
        heading="Supplementary Methods 4. Reserve-like endpoint construction",
        supp_ids=("SUPP-005",),
        claim_ids=("CLM-0003",),
        source_artifacts=("ART-0039", "ART-0049", "ART-0050"),
        text=(
            "The reserve-like supplementary section separates the measured endpoint coordinate from broader biological reserve language. "
            "Response series are baseline-normalized as \\(F/F_0(t)=F(t)/\\bar F_0\\), where \\(\\bar F_0\\) is calculated from declared baseline samples. "
            "The retained bounded coordinate is \\(H=\\mathrm{clip}(1-(\\max(F/F_0)-f_{\\min})/(f_{\\max}-f_{\\min}),0,1)\\), with larger values indicating that the observed response remained closer to the low-response bound under the supplied scale. "
            "Uncertainty summaries and label-scope tables are retained so the reader can see whether a reserve-like statement is supported by the measured endpoint or should remain descriptive. "
            "These outputs are not direct assays of unmeasured biological reserve capacity."
        ),
    ),
    SupplementaryBlock(
        heading="Supplementary Methods 5. Routed-output reduced-architecture comparison",
        supp_ids=("SUPP-006",),
        claim_ids=("CLM-0004",),
        source_artifacts=("ART-0038", "ART-0051"),
        text=(
            "The routed-output supplementary section records how endpoint rows are used to compare candidate readout architectures. "
            "For each model \\(m\\), observed endpoint \\(y_j\\), prediction \\(\\hat y_{jm}\\), and optional weight \\(w_j\\), RhoDyn computes \\(RSS_m=\\sum_j w_j(y_j-\\hat y_{jm})^2\\), RMSE, AIC, and BIC, then sorts alternatives by BIC and residual structure. "
            "Reduced alternatives are retained explicitly so a successful routed-output architecture is compared against simpler endpoint summaries rather than interpreted in isolation. "
            "Residual profiles and decision-boundary tables show which endpoint constraints are satisfied or missed under the tested alternatives. "
            "This constrains the measured readout architecture but does not identify direct biochemical interactions."
        ),
    ),
    SupplementaryBlock(
        heading="Supplementary Methods 6. Software parity, export bundles, and archive reproduction",
        supp_ids=("SUPP-008",),
        claim_ids=("CLM-0005",),
        source_artifacts=("ART-0010", "ART-0021", "ART-0022", "ART-0023", "ART-0024", "ART-0045", "ART-0046", "ART-0047", "ART-0052", "ART-0053"),
        text=(
            "The software-reproducibility supplementary section describes how the same retained examples are exercised through Python, command-line, backend, and workbench surfaces. "
            "Each export bundle is expected to include input rows, schema information, grouping fields when available, effective parameters, result JSON, result rows, Markdown report text, and file checksums. "
            "The source-distribution clean-room route rebuilds selected evidence outputs from the released archive and compares deterministic tables against retained snapshots. "
            "The archive-manifest and checksum records make the release inspectable as a software object rather than as a transient development state. "
            "This supports reproducibility of the retained evidence surfaces and does not imply PyPI publication, regulatory qualification, or private-data reproduction."
        ),
    ),
    SupplementaryBlock(
        heading="Supplementary Methods 7. Non-example cases and interpretation boundaries",
        supp_ids=("SUPP-009",),
        claim_ids=("CLM-0001", "CLM-0002", "CLM-0003", "CLM-0004", "CLM-0005"),
        source_artifacts=("ART-0017",),
        text=(
            "The interpretation-boundary section collects cases in which RhoDyn should withhold, narrow, or downgrade a claim. "
            "Examples include missing time units, missing condition labels, insufficient sampling density, absent grouping structure, undeclared biological windows, undeclared bounded-coupling margins, and endpoint data that cannot distinguish reduced alternatives. "
            "Ambiguous synthetic regimes and margin-boundary public cases are treated as valid outputs because they mark where residence, coupling, reserve-like, or routed-output interpretation is not resolved by the available data. "
            "Recommended wording keeps each result tied to its measured object, declared window, margin, grouping level, and model alternative. "
            "This section is a claim-boundary support surface, not a new result or a tool that infers mechanism without a declared measurement and model context."
        ),
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


def _visible_text(text: str) -> str:
    return "\n".join(line for line in text.splitlines() if not line.startswith("<!--")).strip()


def _word_count(text: str) -> int:
    return len(re.findall(r"\b[\w-]+\b", text))


def _claim_ids() -> set[str]:
    return {row["claim_id"] for row in _read_csv(CLAIM_HIERARCHY)}


def _callout_map() -> dict[str, str]:
    return {row["supp_id"]: row["callout_location"] for row in _read_csv(SUPPLEMENTARY_CALLOUT_LEDGER)}


def _build_supplementary_methods(generated_utc: str, draft_version: str) -> str:
    callout_map = _callout_map()
    lines = [
        f"<!-- SUPPLEMENTARY-METHODS-DRAFT stage=9.18 generated_utc={generated_utc} draft_version={draft_version} -->",
        "",
        "# Supplementary Methods",
        "",
        "These Supplementary Methods expand the technical details behind the planned supplementary support items while preserving the main Article as the evidence-bearing surface. They provide schema, decision-rule, sensitivity, model-comparison, and software-reproducibility detail that is callable from the Results, Online Methods, and Discussion through the planned supplementary-item callouts. The sections below do not add new biological claims, new datasets, new model outputs, or new figure legends.",
        "",
    ]
    for block in SUPPLEMENTARY_BLOCKS:
        callouts = sorted({callout_map.get(supp_id, "") for supp_id in block.supp_ids if callout_map.get(supp_id)})
        lines.extend(
            [
                f"## {block.heading}",
                "",
                (
                    "<!-- "
                    f"supp_ids={';'.join(block.supp_ids)} "
                    f"claim_ids={';'.join(block.claim_ids)} "
                    f"main_text_callouts={';'.join(callouts)} "
                    f"source_artifacts={';'.join(block.source_artifacts)}"
                    " -->"
                ),
                "",
                block.text,
                "",
            ]
        )
    return "\n".join(lines)


def _no_downstream_started() -> tuple[bool, list[str]]:
    forbidden = [path.relative_to(ROOT).as_posix() for path in FORBIDDEN_STARTED_PATHS if path.exists()]
    return not forbidden, forbidden


def _callout_locations_are_represented(text: str) -> tuple[bool, list[str]]:
    callout_map = _callout_map()
    missing: list[str] = []
    results_text = RESULTS_PATH.read_text(encoding="utf-8") if RESULTS_PATH.exists() else ""
    methods_text = METHODS_PATH.read_text(encoding="utf-8") if METHODS_PATH.exists() else ""
    discussion_text = DISCUSSION_PATH.read_text(encoding="utf-8") if DISCUSSION_PATH.exists() else ""
    main_text = "\n".join([results_text, methods_text, discussion_text])
    for supp_id, locations in callout_map.items():
        if supp_id not in text:
            missing.append(f"{supp_id}: not covered")
            continue
        for location in [item.strip() for item in locations.split(";") if item.strip()]:
            if location.startswith("PARA-METHODS-"):
                if "methods_stmt_ids=" not in methods_text:
                    missing.append(f"{supp_id}: {location} has no Methods route")
            elif location not in main_text:
                missing.append(f"{supp_id}: {location} absent from main text")
    return not missing, missing


def _validate(supplementary_text: str, commit: str) -> list[dict[str, Any]]:
    gate_917_pass = False
    if GATE_917.exists():
        try:
            gate_917_pass = _read_json(GATE_917).get("pass") is True
        except json.JSONDecodeError:
            gate_917_pass = False
    visible = _visible_text(supplementary_text)
    claim_ids = _claim_ids() if CLAIM_HIERARCHY.exists() else set()
    hidden_claim_ids = {
        item
        for group in re.findall(r"claim_ids=([^ ]+)", supplementary_text)
        for item in group.split(";")
        if item
    }
    hidden_supp_ids = {
        item
        for group in re.findall(r"supp_ids=([^ ]+)", supplementary_text)
        for item in group.split(";")
        if item
    }
    callout_ok, callout_failures = _callout_locations_are_represented(supplementary_text)
    downstream_ok, downstream_paths = _no_downstream_started()
    required_supp_ids = {f"SUPP-{idx:03d}" for idx in range(1, 10)}
    required_boundaries_ok = all(phrase in visible for phrase in REQUIRED_BOUNDARY_PHRASES)
    forbidden_absent = not any(phrase.lower() in visible.lower() for phrase in FORBIDDEN_VISIBLE_PHRASES)
    visible_internal_ids_absent = not re.search(r"\b(CLM|ART|SUPP|PARA|FIG|STBL|SFIG)-\d{3,4}\b", visible)
    return [
        {
            "name": "stage_9_17_gate_passed",
            "passed": gate_917_pass,
            "detail": "Stage 9.17 availability assembly exists and passes" if gate_917_pass else "Stage 9.17 gate is missing or not passing",
        },
        {
            "name": "supplementary_plan_and_callout_ledger_available",
            "passed": SUPPLEMENTARY_PLAN.exists() and SUPPLEMENTARY_CALLOUT_LEDGER.exists(),
            "detail": "Stage 9.7 supplementary item plan and callout ledger are available",
        },
        {
            "name": "all_supplementary_items_covered",
            "passed": hidden_supp_ids == required_supp_ids,
            "detail": f"covered_supp_ids={';'.join(sorted(hidden_supp_ids))}",
        },
        {
            "name": "claim_ids_limited_to_claim_freeze",
            "passed": bool(claim_ids) and hidden_claim_ids <= claim_ids and {"CLM-0001", "CLM-0002", "CLM-0003", "CLM-0004", "CLM-0005"} <= hidden_claim_ids,
            "detail": f"hidden_claim_ids={';'.join(sorted(hidden_claim_ids))}",
        },
        {
            "name": "items_callable_from_main_text",
            "passed": callout_ok,
            "detail": "All SUPP items retain planned main-text callout routes" if callout_ok else "; ".join(callout_failures),
        },
        {
            "name": "interpretation_boundaries_preserved",
            "passed": required_boundaries_ok and forbidden_absent and visible_internal_ids_absent,
            "detail": f"word_count={_word_count(visible)}",
        },
        {
            "name": "no_references_legends_tables_or_package_started",
            "passed": downstream_ok,
            "detail": "No references.bib, figure legends, supplementary tables plan, PI packet, or readiness checklist detected"
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
        if substage.get("id") == "9.18":
            substage["status"] = "complete_supplementary_methods_drafted"
    registry["last_completed_substage"] = "9.18"
    registry["next_substage"] = "9.19"
    _write_json(REGISTRY_PATH, registry)


def _upsert_completed_substage(memory: dict[str, Any], draft_version: str, checks: list[dict[str, Any]]) -> None:
    record = {
        "substage": "9.18",
        "status": "pass",
        "pass": True,
        "gate_verdict_path": "manuscript/nature_methods/gate_verdicts/9.18.json",
        "validation_outcome": "Supplementary Methods drafted from the planned supplementary support map without adding new claim IDs",
        "evidence_dependencies": [
            "manuscript/nature_methods/gate_verdicts/9.17.json",
            "manuscript/nature_methods/supplementary/supplementary_item_plan.md",
            "manuscript/nature_methods/ledgers/supplementary_callout_ledger.csv",
            "manuscript/nature_methods/ledgers/claim_hierarchy.csv",
        ],
        "files_created_or_modified": [
            "manuscript/nature_methods/supplementary/supplementary_methods.md",
            "manuscript/nature_methods/gate_verdicts/9.18.json",
        ],
        "remaining_blockers": [
            "Supplementary table/source-data binding has not started",
            "Full reference library and citation audit have not started",
            "Figure legends have not started",
            "Full submission-package assembly has not started beyond the Reporting Summary requirement placeholder",
        ],
        "supplementary_methods_version": draft_version,
        "checks": checks,
    }
    entries = [item for item in memory.get("completed_substages", []) if item.get("substage") != "9.18"]
    entries.append(record)
    memory["completed_substages"] = entries


def _update_memory(draft_version: str, generated_utc: str, checks: list[dict[str, Any]]) -> None:
    memory = _read_json(MEMORY_PATH)
    memory["generated_utc"] = generated_utc
    memory["current_substage"] = "9.18"
    memory["supplementary_methods_started"] = True
    memory["status"] = "stage9_18_supplementary_methods_drafted"
    memory["current_gate"] = "Stage 9.18 registered Supplementary Methods without supplementary tables"
    memory["next_substage"] = "9.19"
    memory["next_substage_authorized"] = False
    memory["stage9_active_gate"] = "Stage 9.18 Supplementary Methods complete; supplementary tables and source-data binding not started"
    memory["stage9_18_checks"] = checks
    artifacts = memory.setdefault("artifacts", [])
    for artifact in [
        "manuscript/nature_methods/supplementary/supplementary_methods.md",
        "manuscript/nature_methods/gate_verdicts/9.18.json",
    ]:
        if artifact not in artifacts:
            artifacts.append(artifact)
    memory["gate"] = [
        "Stage 9.-1 contract and schema files exist and pass the scaffold checker.",
        "Stage 9.0 through Stage 9.18 are complete through Supplementary Methods drafting.",
        "Stage 9.19 through Stage 9.29 plus Stage 9.25b remain not started.",
        "No supplementary table/source-data binding, full reference library, figure legends, PI review packet, or submission readiness checklist are created in this Supplementary Methods pass.",
        "Supplementary Methods map to planned SUPP callout routes and use only frozen CLM identifiers.",
    ]
    memory["scope_rule"] = (
        "Stage 9 has completed evidence intake, venue-guidance registration, representative methods-paper corpus analysis, "
        "narrative-spine selection, claim freeze, paragraph-level claim planning, main figure-spine planning, deterministic "
        "PanelForge rendering, supplementary display planning, section-contract planning, title/abstract strategy, Results "
        "subsection architecture, Results drafting, Introduction literature binding, Discussion interpretation mapping, "
        "Discussion drafting, Methods architecture, Methods drafting, availability assembly, and Supplementary Methods drafting only. "
        "Do not start supplementary tables, source-data binding, the full reference library, figure legends, or final submission package without explicit substage authorization."
    )
    _upsert_completed_substage(memory, draft_version, checks)
    _write_json(MEMORY_PATH, memory)


def _update_roadmap_memory(draft_version: str) -> None:
    memory = _read_json(ROADMAP_MEMORY_PATH)
    current = memory.setdefault("current_position", {})
    current["active_stage"] = "Stage 9.18 Supplementary Methods complete; supplementary tables and source-data binding not started"
    current["stage9_active_gate"] = "Stage 9.18 Supplementary Methods complete; supplementary tables and source-data binding not started"
    current["after_stage9_18_supplementary_methods"] = (
        "Stage 9.18 registered Supplementary Methods prose for the planned SUPP support items. "
        "It did not assemble supplementary tables/source-data binding, resolve the full reference library, write figure legends, or complete the final submission package."
    )
    current["current_gate"] = "Supplementary Methods drafted without supplementary table binding"
    current["next_stage"] = "Stage 9.19 Supplementary tables and source-data binding"
    for stage in memory.get("stage_lock", []):
        if not isinstance(stage, dict) or stage.get("stage") != 9:
            continue
        stage["status"] = "stage9_18_supplementary_methods_drafted"
        stage["current_gate"] = "Stage 9.18 registered Supplementary Methods without supplementary tables"
        stage["scope_rule"] = (
            "Stage 9 has completed evidence intake, venue-guidance registration, representative methods-paper corpus analysis, "
            "narrative-spine selection, claim freeze, paragraph-level claim planning, main figure-spine planning, deterministic "
            "PanelForge rendering, supplementary display planning, section-contract planning, front-matter strategy, Results architecture, "
            "Results drafting, Introduction literature binding, Discussion interpretation mapping, Discussion drafting, Methods architecture, "
            "Methods drafting, availability assembly, and Supplementary Methods drafting only. Do not start supplementary tables/source-data binding, "
            "the full reference library, figure legends, review response, or final submission packaging without explicit substage authorization."
        )
        artifacts = stage.setdefault("artifacts", [])
        for artifact in [
            "manuscript/nature_methods/supplementary/supplementary_methods.md",
            "manuscript/nature_methods/gate_verdicts/9.18.json",
            "scripts/run_stage9_18_supplementary_methods.py",
        ]:
            if artifact not in artifacts:
                artifacts.append(artifact)
        gate = stage.setdefault("gate", [])
        supplementary_gate = "Stage 9.18 Supplementary Methods maps planned SUPP support items to frozen claims without opening table, legend, reference, or package assembly."
        if supplementary_gate not in gate:
            gate.append(supplementary_gate)
        for subphase in stage.get("subphases", []):
            if isinstance(subphase, dict) and subphase.get("id") == "9.18":
                subphase["status"] = "complete_supplementary_methods_drafted"
                subphase["evidence"] = "manuscript/nature_methods/gate_verdicts/9.18.json"
                subphase["supplementary_methods_version"] = draft_version
    _write_json(ROADMAP_MEMORY_PATH, memory)


def _replace_once(body: str, old: str, new: str) -> str:
    return body.replace(old, new) if old in body else body


def _update_docs() -> None:
    if PLAN_PATH.exists():
        body = PLAN_PATH.read_text(encoding="utf-8")
        body = _replace_once(
            body,
            "Stage 9.17 registers data availability, code availability, the reproducibility command index, and the required Reporting Summary placeholder. The current state intentionally does not create `refs/references.bib`, figure legends, Supplementary Methods, or full submission-package files.",
            "Stage 9.17 registers data availability, code availability, the reproducibility command index, and the required Reporting Summary placeholder. Stage 9.18 registers Supplementary Methods prose in `supplementary/supplementary_methods.md` and `gate_verdicts/9.18.json`. The current state intentionally does not create supplementary tables, source-data binding, `refs/references.bib`, figure legends, or full submission-package files.",
        )
        body = _replace_once(
            body,
            "| 9.18 | Supplementary Methods drafting | not_started | Move technical depth into structured Supplementary Methods. |",
            "| 9.18 | Supplementary Methods drafting | complete_supplementary_methods_drafted | Move technical depth into structured Supplementary Methods. |",
        )
        PLAN_PATH.write_text(body, encoding="utf-8")
    if ROADMAP_PATH.exists():
        body = ROADMAP_PATH.read_text(encoding="utf-8")
        body = _replace_once(
            body,
            "has registered data/code availability plus the required Reporting Summary\nplaceholder. Full reference-library assembly, figure legends, supplementary\nmethods, and final package assembly remain not started.",
            "has registered data/code availability plus the required Reporting Summary\nplaceholder, and Stage 9.18 has registered Supplementary Methods. Supplementary\ntable/source-data binding, full reference-library assembly, figure legends, and\nfinal package assembly remain not started.",
        )
        body = _replace_once(
            body,
            "| Stage 9. Nature Methods manuscript assembly | Stage 9.17 availability assembly complete, Supplementary Methods not started. | The current boundary is evidence intake, official venue-guidance registration, representative methods-paper corpus analysis, narrative-spine selection, claim freeze, paragraph-level claim planning, main figure-spine planning, deterministic PanelForge rendering, supplementary display planning, section-contract planning, front-matter strategy, Results architecture, Results drafting, Introduction literature binding, Discussion interpretation mapping, Discussion drafting, Methods architecture, Methods drafting, and availability assembly only. Do not start full reference-library assembly, figure legends, review response, supplementary methods, or final submission packaging without explicit substage authorization. |",
            "| Stage 9. Nature Methods manuscript assembly | Stage 9.18 Supplementary Methods complete, supplementary tables and source-data binding not started. | The current boundary is evidence intake, official venue-guidance registration, representative methods-paper corpus analysis, narrative-spine selection, claim freeze, paragraph-level claim planning, main figure-spine planning, deterministic PanelForge rendering, supplementary display planning, section-contract planning, front-matter strategy, Results architecture, Results drafting, Introduction literature binding, Discussion interpretation mapping, Discussion drafting, Methods architecture, Methods drafting, availability assembly, and Supplementary Methods drafting only. Do not start supplementary tables/source-data binding, full reference-library assembly, figure legends, review response, or final submission packaging without explicit substage authorization. |",
        )
        body = _replace_once(
            body,
            "Stage 9.10 Results subsection architecture has been completed. Stage 9.11 Results drafting pass has been completed. Stage 9.12 Introduction literature binding has been completed. Stage 9.13 Discussion interpretation map has been completed. Stage 9.14 Discussion drafting pass has been completed. Stage 9.15 Methods architecture has been completed. Stage 9.16 Methods drafting pass has been completed. Stage 9.17 software, data, and code availability assembly has been completed. Stage 9.18 Supplementary Methods drafting remains the next unstarted manuscript step. Full reference-library assembly, figure legends, supplementary methods, and final package assembly remain not started.",
            "Stage 9.10 Results subsection architecture has been completed. Stage 9.11 Results drafting pass has been completed. Stage 9.12 Introduction literature binding has been completed. Stage 9.13 Discussion interpretation map has been completed. Stage 9.14 Discussion drafting pass has been completed. Stage 9.15 Methods architecture has been completed. Stage 9.16 Methods drafting pass has been completed. Stage 9.17 software, data, and code availability assembly has been completed. Stage 9.18 Supplementary Methods drafting has been completed. Stage 9.19 Supplementary tables and source-data binding remains the next unstarted manuscript step. Supplementary table/source-data binding, full reference-library assembly, figure legends, and final package assembly remain not started.",
        )
        ROADMAP_PATH.write_text(body, encoding="utf-8")


def run() -> dict[str, Any]:
    generated_utc = _now()
    commit = _git_sha()
    draft_version = f"supplementary-methods-draft@{generated_utc[:10]}@{commit}"
    if STAGING_DIR.exists():
        shutil.rmtree(STAGING_DIR)
    STAGING_DIR.mkdir(parents=True, exist_ok=True)
    supplementary_text = _build_supplementary_methods(generated_utc, draft_version)
    _write_text(STAGING_DIR / OUTPUTS["supplementary_methods"].relative_to(WORKSPACE), supplementary_text)
    checks = _validate(supplementary_text, commit)
    passed = all(check["passed"] for check in checks)
    visible = _visible_text(supplementary_text)
    hidden_supp_ids = sorted(
        {
            item
            for group in re.findall(r"supp_ids=([^ ]+)", supplementary_text)
            for item in group.split(";")
            if item
        }
    )
    hidden_claim_ids = sorted(
        {
            item
            for group in re.findall(r"claim_ids=([^ ]+)", supplementary_text)
            for item in group.split(";")
            if item
        }
    )
    gate = {
        "substage": "9.18",
        "timestamp": generated_utc,
        "supplementary_methods_version": draft_version,
        "pass": passed,
        "checks": checks,
        "supplementary_methods_word_count": _word_count(visible),
        "supplementary_methods_section_count": len(SUPPLEMENTARY_BLOCKS),
        "supp_ids": hidden_supp_ids,
        "claim_ids": hidden_claim_ids,
        "next_substage": "9.19",
        "outputs": [str(path.relative_to(ROOT)) for path in OUTPUTS.values()],
        "scope_boundary": "Supplementary Methods only. No supplementary tables/source-data binding, references.bib, figure legends, PI packet, readiness checklist, or final submission-package assembly.",
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
        "substage": "9.18",
        "supplementary_methods_version": draft_version,
        "supplementary_methods_word_count": _word_count(visible),
        "supplementary_methods_section_count": len(SUPPLEMENTARY_BLOCKS),
        "failures": [check for check in checks if not check["passed"]],
        "outputs": gate["outputs"],
        "next_allowed_action": "Proceed to Stage 9.19 supplementary tables and source-data binding after validation and explicit authorization.",
    }


def main() -> int:
    payload = run()
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())

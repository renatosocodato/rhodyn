"""Run Stage 9.16 Methods drafting pass.

Stage 9.16 converts the Stage 9.15 Methods architecture into reader-facing
Online Methods prose. It does not create availability statements, the full
reference library, figure legends, supplementary methods, or a submission
package.
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
STAGING_DIR = WORKSPACE / "_staging" / "9.16"
QUARANTINE_DIR = WORKSPACE / "_quarantine" / "9.16"
MEMORY_PATH = ROOT / "docs" / "stage9_execution_memory.json"
ROADMAP_MEMORY_PATH = ROOT / "docs" / "roadmap_execution_memory.json"
REGISTRY_PATH = WORKSPACE / "contracts" / "stage9_substage_registry.json"
PLAN_PATH = ROOT / "docs" / "stage9_manuscript_assembly_plan.md"
ROADMAP_PATH = ROOT / "docs" / "roadmap.md"
PROJECT_BINDING = WORKSPACE / "contracts" / "stage9_project_binding.json"
SECTION_CONTRACTS = SECTIONS_DIR / "section_contracts.md"
METHODS_BLUEPRINT = SECTIONS_DIR / "methods_blueprint.md"
METHODS_LEDGER = LEDGERS_DIR / "methods_to_code_ledger.csv"
EVIDENCE_MANIFEST = LEDGERS_DIR / "stage9_evidence_manifest.csv"
GATE_915 = GATE_DIR / "9.15.json"

OUTPUTS = {
    "methods": SECTIONS_DIR / "methods.md",
    "gate": GATE_DIR / "9.16.json",
}

FORBIDDEN_STARTED_PATHS = [
    SECTIONS_DIR / "data_availability.md",
    SECTIONS_DIR / "code_availability.md",
    WORKSPACE / "refs" / "references.bib",
    WORKSPACE / "figures" / "figure_legends.md",
    WORKSPACE / "supplementary" / "supplementary_methods.md",
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

FORBIDDEN_VISIBLE_PHRASES = (
    "standard methods",
    "standard pipeline",
    "default settings",
    "as described previously",
    "as described elsewhere",
    "manufacturer's instructions",
    "using default",
    "absence of all coupling",
    "true biological reserve",
    "literal molecular edge",
    "RhoDyn generated the original",
)

REQUIRED_VISIBLE_BOUNDARIES = (
    "declared analysis choice",
    "not proof that all coupling is absent",
    "not direct assays of unmeasured biological reserve capacity",
    "does not identify direct biochemical interactions",
    "RhoDyn v0.1.0",
    "stage7.8-methods-readiness@242f06c49e8310b81ac1c06a270bb6810f3f4cfc",
)

DATASET_VERSION = "stage7.8-methods-readiness@242f06c49e8310b81ac1c06a270bb6810f3f4cfc"
DATASET_DATE = "2026-06-30"


@dataclass(frozen=True)
class MethodsBlock:
    subheading: str | None
    methods_ids: tuple[str, ...]
    claim_ids: tuple[str, ...]
    repo_paths: tuple[str, ...]
    text: str


METHODS_BLOCKS = (
    MethodsBlock(
        subheading=None,
        methods_ids=("MTH-0001", "MTH-0002", "MTH-0003", "MTH-0004", "MTH-0005", "MTH-0006", "MTH-0007", "MTH-0008", "MTH-0009"),
        claim_ids=("CLM-0001", "CLM-0002", "CLM-0003", "CLM-0004", "CLM-0005"),
        repo_paths=("src/rhodyn/schema.py", "src/rhodyn/residence.py", "src/rhodyn/coupling.py", "src/rhodyn/reserve.py", "src/rhodyn/compare.py", "src/rhodyn/sim.py", "src/rhodyn/backend_core.py"),
        text=(
            f"All analyses in this Methods draft refer to RhoDyn v0.1.0 and to the locked evidence snapshot `{DATASET_VERSION}` dated {DATASET_DATE}. "
            "The software implements residence-aware interpretation of biological trajectories and endpoint perturbation tables. "
            "The manuscript use cases are treated as reproducible demonstrations of the method object, not as evidence that the software generated the motivating RhoA/microglia manuscript. "
            "Each analysis route returns a structured result, the effective parameters used to produce it, and a boundary statement describing what the result can and cannot support."
        ),
    ),
    MethodsBlock(
        subheading="Input schemas and preprocessing",
        methods_ids=("MTH-0001",),
        claim_ids=("CLM-0001", "CLM-0002", "CLM-0003", "CLM-0004"),
        repo_paths=("src/rhodyn/schema.py",),
        text=(
            "Input tables were parsed as typed tidy records before any residence, coupling, reserve-like, or model-comparison calculation. "
            "Trajectory rows required `cell_id`, non-negative `time`, `condition`, and numeric `signal`, with `replicate` retained when supplied. "
            "Endpoint model-comparison rows required `model`, `endpoint`, `observed`, and `predicted`, with optional non-negative `weight`. "
            "Reserve-like rows required `sample_id`, `time`, `condition`, and `response`, and bounded-coupling rows required `contrast`, `estimate`, `ci_low`, `ci_high`, and positive `margin`, with optional `rope_mass`. "
            "Rows with missing identifiers, missing columns, non-finite numeric values, negative time, or invalid margins were returned with validation issues rather than silently coerced. "
            "This preprocessing protects trace identity and biological grouping, but it cannot reconstruct missing time units, missing condition labels, or replicate structure that was not present in the input."
        ),
    ),
    MethodsBlock(
        subheading="Residence windows and amplitude comparators",
        methods_ids=("MTH-0002",),
        claim_ids=("CLM-0001",),
        repo_paths=("src/rhodyn/residence.py",),
        text=(
            "Residence analysis used a declared signal interval \\(W=[\\ell,h]\\), where \\(\\ell<h\\), as the biological window to be tested. "
            "For each sampled value \\(x(t_k)\\), RhoDyn evaluated \\(I_W(t_k)=1\\) when \\(\\ell \\le x(t_k) \\le h\\) and \\(I_W(t_k)=0\\) otherwise. "
            "For ordered samples, residence time was computed as \\(R_T=\\sum_k \\Delta t_k I_W(t_k)\\), where \\(\\Delta t_k=t_{k+1}-t_k\\), and residence fraction was \\(R_F=R_T/\\sum_k \\Delta t_k\\). "
            "The same trace also retained mean signal, maximum signal, minimum signal, total time, and the number of contiguous in-window dwell segments. "
            "The residence window is therefore a declared analysis choice, not an automatically discovered causal state."
        ),
    ),
    MethodsBlock(
        subheading=None,
        methods_ids=("MTH-0002", "MTH-0003"),
        claim_ids=("CLM-0001",),
        repo_paths=("src/rhodyn/residence.py", "scripts/run_stage7_3_public_signaling.py"),
        text=(
            "Amplitude comparators were calculated on the same tidy trajectories so that residence and simpler summaries could be compared without changing the input object. "
            "The public DRG calcium and ERK GPCR demonstrations were converted into this schema from Zenodo sources 10.5281/zenodo.14907827 and 10.5281/zenodo.5836623, respectively. "
            "Derived tables preserved condition, trace identity, time, signal, and available grouping variables, and each demonstration reported window sensitivity and uncertainty summaries rather than a single unqualified residence call. "
            "These public examples test whether the residence-amplitude comparison travels across reporter systems. They do not establish a universal residence regime for every signaling trajectory."
        ),
    ),
    MethodsBlock(
        subheading=None,
        methods_ids=("MTH-0008",),
        claim_ids=("CLM-0001",),
        repo_paths=("src/rhodyn/sim.py",),
        text=(
            "Synthetic timing utilities were used to provide positive, negative, and ambiguous truth cases for the method. "
            "First-passage summaries used \\(\\tau=\\inf\\{t:x(t)\\ge q\\}\\) for above-threshold events, with the analogous definition for below-threshold events. "
            "Stochastic simulations used simple Gillespie and tau-leap helpers only as method-support examples. "
            "Those timing outputs are model-derived or trajectory-derived summaries, not measured cell death, injury, or molecular hazard rates unless a supplied endpoint directly measures those quantities."
        ),
    ),
    MethodsBlock(
        subheading="Bounded-coupling and uncertainty decisions",
        methods_ids=("MTH-0004",),
        claim_ids=("CLM-0002",),
        repo_paths=("src/rhodyn/coupling.py",),
        text=(
            "Bounded-coupling decisions were made only after a contrast estimate, uncertainty interval, and positive biological margin had been declared. "
            "For an estimated contrast \\(\\hat\\delta\\), interval \\([L,U]\\), and margin \\(\\Delta>0\\), interval equivalence passed when \\(-\\Delta \\le L \\le U \\le \\Delta\\). "
            "When posterior samples or a ROPE mass were available, the decision also required \\(P(|\\delta|\\le \\Delta)\\ge 0.95\\), unless a different threshold was explicitly supplied. "
            "For raw arrays, one-sample or Welch two-sample TOST decisions required both one-sided tests to pass at the declared alpha and the confidence interval to remain inside \\(\\pm\\Delta\\). "
            "A passing decision means equivalence within the stated margin and context, not proof that all coupling is absent."
        ),
    ),
    MethodsBlock(
        subheading=None,
        methods_ids=("MTH-0007",),
        claim_ids=("CLM-0002",),
        repo_paths=("scripts/run_stage7_5_heldout_validation.py",),
        text=(
            "Held-out paired-reporter contexts used the same bounded-coupling decision rule with fixed thresholds, fixed margins, and recorded grouping choices. "
            "Each context was reported as passing, failing, or inconclusive, and margin-boundary cases were kept visible rather than promoted to equivalence. "
            "Bootstrap and interval summaries were interpreted at the declared grouping level. "
            "Controlled-access boundaries were recorded when a source input could be inspected only through derived tables or notes. "
            "This convention makes inconclusive evidence a valid method output rather than a failed analysis."
        ),
    ),
    MethodsBlock(
        subheading="Reserve-like endpoint construction",
        methods_ids=("MTH-0005",),
        claim_ids=("CLM-0003",),
        repo_paths=("src/rhodyn/reserve.py",),
        text=(
            "Reserve-like summaries were constructed only for response series where the measured endpoint could support a buffering-style interpretation. "
            "Signals were baseline-normalized as \\(F/F_0(t)=F(t)/\\bar F_0\\), where \\(\\bar F_0\\) was the mean of the declared baseline points. "
            "A bounded coordinate was then computed as \\(H=\\mathrm{clip}(1-(\\max(F/F_0)-f_{\\min})/(f_{\\max}-f_{\\min}),0,1)\\). "
            "Larger values indicate that the observed response remained closer to the low-response bound under the supplied scaling. "
            "These values are reserve-like endpoint coordinates tied to the measured assay and are not direct assays of unmeasured biological reserve capacity."
        ),
    ),
    MethodsBlock(
        subheading="Routed-output model comparison",
        methods_ids=("MTH-0006",),
        claim_ids=("CLM-0004",),
        repo_paths=("src/rhodyn/compare.py",),
        text=(
            "Routed-output comparisons used endpoint rows containing observed values, model-predicted values, model labels, endpoint labels, and optional weights. "
            "For each candidate architecture \\(m\\), RhoDyn computed \\(RSS_m=\\sum_j w_j(y_j-\\hat y_{jm})^2\\), RMSE, AIC, and BIC. "
            "The reported ranking sorted candidate architectures by BIC and then by residual sum of squares. "
            "Reduced alternatives were interpreted as tested endpoint architectures, not as exhaustive mechanistic possibilities. "
            "A retained routed-output model constrains the readout structure under the supplied endpoints but does not identify direct biochemical interactions."
        ),
    ),
    MethodsBlock(
        subheading="Software surfaces, versioning, and reproducibility",
        methods_ids=("MTH-0009",),
        claim_ids=("CLM-0005",),
        repo_paths=("src/rhodyn/backend_core.py",),
        text=(
            "RhoDyn v0.1.0 was the software boundary used for the Methods evidence surface. "
            "The public GitHub release and Zenodo version DOI 10.5281/zenodo.21036616 define the citable software record, while the concept DOI 10.5281/zenodo.21036615 resolves to the current RhoDyn software concept. "
            "Python, command-line, backend, and workbench routes were checked for parity on retained examples, and export bundles retained input rows, schema information, grouping fields, effective parameters, result tables, reports, and file checksums. "
            "The source-distribution clean-room route rebuilt selected evidence outputs from the packaged archive and compared deterministic tables against committed snapshots. "
            "This supports reproducibility of the demonstrated analyses, not a new biological result, hidden private-data reproduction claim, or package-index publication claim."
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


def _build_methods(generated_utc: str, draft_version: str) -> str:
    lines = [
        f"<!-- METHODS-DRAFT stage=9.16 generated_utc={generated_utc} draft_version={draft_version} -->",
        "",
        "# Online Methods",
        "",
    ]
    for block in METHODS_BLOCKS:
        if block.subheading:
            lines.extend([f"## {block.subheading}", ""])
        lines.extend(
            [
                (
                    "<!-- "
                    f"methods_stmt_ids={';'.join(block.methods_ids)} "
                    f"claim_ids={';'.join(block.claim_ids)} "
                    f"repo_paths={';'.join(block.repo_paths)}"
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


def _ledger_methods_ids() -> set[str]:
    return {row["methods_stmt_id"] for row in _read_csv(METHODS_LEDGER)}


def _evidence_versions() -> set[str]:
    return {row["evidence_version"] for row in _read_csv(EVIDENCE_MANIFEST)}


def _validate(methods_text: str, commit: str) -> list[dict[str, Any]]:
    gate_915_pass = False
    if GATE_915.exists():
        try:
            gate_915_pass = _read_json(GATE_915).get("pass") is True
        except json.JSONDecodeError:
            gate_915_pass = False
    visible = _visible_text(methods_text)
    binding = _read_json(PROJECT_BINDING) if PROJECT_BINDING.exists() else {}
    software_version = str(binding.get("software_version", ""))
    expected_methods_ids = _ledger_methods_ids() if METHODS_LEDGER.exists() else set()
    comment_ids = {
        item
        for group in re.findall(r"methods_stmt_ids=([^ ]+)", methods_text)
        for item in group.split(";")
        if item
    }
    claim_ids = {
        item
        for group in re.findall(r"claim_ids=([^ ]+)", methods_text)
        for item in group.split(";")
        if item
    }
    paragraph_comments = re.findall(r"methods_stmt_ids=([^ ]+)", methods_text)
    visible_internal_ids_absent = not re.search(r"\b(MTH|ART|CLM)-\d{4}\b", visible)
    subheadings_present = all(f"## {subheading}" in methods_text for subheading in METHODS_SUBHEADINGS)
    forbidden_absent = not any(phrase.lower() in visible.lower() for phrase in FORBIDDEN_VISIBLE_PHRASES)
    boundaries_present = all(phrase in visible for phrase in REQUIRED_VISIBLE_BOUNDARIES)
    version_ok = software_version == "v0.1.0" and "RhoDyn v0.1.0" in visible and DATASET_VERSION in visible
    evidence_version_ok = _evidence_versions() == {DATASET_VERSION} if EVIDENCE_MANIFEST.exists() else False
    ledger_rows = _read_csv(METHODS_LEDGER) if METHODS_LEDGER.exists() else []
    ledger_commit_ok = all(re.fullmatch(r"[0-9a-f]{40}", row.get("commit", "")) for row in ledger_rows)
    ledger_dataset_ok = all("dataset_version=" in row.get("command", "") for row in ledger_rows)
    no_downstream, downstream_paths = _no_downstream_started()
    return [
        {
            "name": "stage_9_15_gate_passed",
            "passed": gate_915_pass,
            "detail": "Stage 9.15 Methods architecture exists and passes" if gate_915_pass else "Stage 9.15 gate is missing or not passing",
        },
        {
            "name": "methods_architecture_inputs_available",
            "passed": METHODS_BLUEPRINT.exists() and METHODS_LEDGER.exists() and "SEC-006. Online Methods" in SECTION_CONTRACTS.read_text(encoding="utf-8"),
            "detail": "Methods blueprint, methods-to-code ledger, and Online Methods contract are available",
        },
        {
            "name": "every_methods_claim_has_statement_id",
            "passed": bool(expected_methods_ids) and comment_ids == expected_methods_ids and len(paragraph_comments) == len(METHODS_BLOCKS)
            and claim_ids == {"CLM-0001", "CLM-0002", "CLM-0003", "CLM-0004", "CLM-0005"},
            "detail": f"covered_methods_ids={';'.join(sorted(comment_ids))} paragraph_count={len(paragraph_comments)}",
        },
        {
            "name": "software_version_matches_evidence_manifest",
            "passed": version_ok and evidence_version_ok and ledger_commit_ok and ledger_dataset_ok,
            "detail": f"software_version={software_version} evidence_versions={';'.join(sorted(_evidence_versions())) if EVIDENCE_MANIFEST.exists() else 'missing'} commit={commit}",
        },
        {
            "name": "undefined_standard_methods_phrasing_absent",
            "passed": forbidden_absent and visible_internal_ids_absent,
            "detail": "Visible Methods prose avoids vague methods phrasing and hides internal IDs in comments only",
        },
        {
            "name": "methods_subheadings_and_boundaries_present",
            "passed": subheadings_present and boundaries_present and 900 <= _word_count(visible) <= 3000,
            "detail": f"word_count={_word_count(visible)} subheading_count={sum(f'## {item}' in methods_text for item in METHODS_SUBHEADINGS)}",
        },
        {
            "name": "no_availability_references_legends_or_package_started",
            "passed": no_downstream,
            "detail": "No availability statements, references.bib, figure legends, supplementary methods, or submission package detected"
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
        if substage.get("id") == "9.16":
            substage["status"] = "complete_methods_drafted"
    registry["last_completed_substage"] = "9.16"
    registry["next_substage"] = "9.17"
    _write_json(REGISTRY_PATH, registry)


def _upsert_completed_substage(memory: dict[str, Any], draft_version: str, checks: list[dict[str, Any]]) -> None:
    record = {
        "substage": "9.16",
        "status": "pass",
        "pass": True,
        "gate_verdict_path": "manuscript/nature_methods/gate_verdicts/9.16.json",
        "validation_outcome": "Reviewer-reconstructable Methods prose registered from Stage 9.15 Methods architecture",
        "evidence_dependencies": [
            "manuscript/nature_methods/gate_verdicts/9.15.json",
            "manuscript/nature_methods/sections/methods_blueprint.md",
            "manuscript/nature_methods/ledgers/methods_to_code_ledger.csv",
            "manuscript/nature_methods/sections/section_contracts.md",
        ],
        "files_created_or_modified": [
            "manuscript/nature_methods/sections/methods.md",
            "manuscript/nature_methods/gate_verdicts/9.16.json",
        ],
        "remaining_blockers": [
            "Stage 9.17 software, data, and code availability assembly has not started",
            "Full reference library and citation audit have not started",
            "Figure legends have not started",
            "Supplementary Methods have not started",
            "Submission-package assembly has not started",
        ],
        "methods_draft_version": draft_version,
        "checks": checks,
    }
    entries = [item for item in memory.get("completed_substages", []) if item.get("substage") != "9.16"]
    entries.append(record)
    memory["completed_substages"] = entries


def _update_memory(draft_version: str, generated_utc: str, checks: list[dict[str, Any]]) -> None:
    memory = _read_json(MEMORY_PATH)
    memory["generated_utc"] = generated_utc
    memory["current_substage"] = "9.16"
    memory["methods_architecture_started"] = True
    memory["methods_drafting_started"] = True
    memory["methods_draft_version"] = draft_version
    memory["status"] = "stage9_16_methods_drafted"
    memory["current_gate"] = "Stage 9.16 registered Methods prose without availability assembly"
    memory["next_substage"] = "9.17"
    memory["next_substage_authorized"] = False
    memory["stage9_active_gate"] = "Stage 9.16 Methods drafting complete; availability assembly not started"
    memory["stage9_16_checks"] = checks
    artifacts = memory.setdefault("artifacts", [])
    for artifact in [
        "manuscript/nature_methods/sections/methods.md",
        "manuscript/nature_methods/gate_verdicts/9.16.json",
    ]:
        if artifact not in artifacts:
            artifacts.append(artifact)
    memory["gate"] = [
        "Stage 9.-1 contract and schema files exist and pass the scaffold checker.",
        "Stage 9.0 through Stage 9.16 are complete through Methods drafting.",
        "Stage 9.17 through Stage 9.29 plus Stage 9.25b remain not started.",
        "No availability statements, full reference library, figure legends, supplementary methods, or submission package contents are created in this Methods drafting pass.",
        "The Methods draft maps claim-bearing prose to Methods statement IDs in hidden comments while keeping visible prose reader-facing.",
    ]
    memory["scope_rule"] = (
        "Stage 9 has completed evidence intake, venue-guidance registration, representative methods-paper corpus analysis, "
        "narrative-spine selection, claim freeze, paragraph-level claim planning, main figure-spine planning, deterministic "
        "PanelForge rendering, supplementary display planning, section-contract planning, title/abstract strategy, Results "
        "subsection architecture, Results drafting, Introduction literature binding, Discussion interpretation mapping, "
        "Discussion drafting, Methods architecture, and Methods drafting only. Do not start availability assembly, full "
        "reference library, figure legends, review response, supplementary methods, or submission packaging without explicit substage authorization."
    )
    _upsert_completed_substage(memory, draft_version, checks)
    _write_json(MEMORY_PATH, memory)


def _update_roadmap_memory(draft_version: str) -> None:
    memory = _read_json(ROADMAP_MEMORY_PATH)
    current = memory.setdefault("current_position", {})
    current["active_stage"] = "Stage 9.16 Methods drafting complete; availability assembly not started"
    current["stage9_active_gate"] = "Stage 9.16 Methods drafting complete; availability assembly not started"
    current["after_stage9_16_methods_drafting"] = (
        "Stage 9.16 registered reviewer-reconstructable Online Methods prose from the Stage 9.15 blueprint. "
        "It did not assemble availability statements, resolve the full reference library, write figure legends, create Supplementary Methods, or package the submission."
    )
    current["current_gate"] = "Methods draft complete without availability assembly"
    current["next_stage"] = "Stage 9.17 Software, data, and code availability assembly"
    for stage in memory.get("stage_lock", []):
        if not isinstance(stage, dict) or stage.get("stage") != 9:
            continue
        stage["status"] = "stage9_16_methods_drafted"
        stage["current_gate"] = "Stage 9.16 registered Methods prose without availability assembly"
        stage["scope_rule"] = (
            "Stage 9 has completed evidence intake, venue-guidance registration, representative methods-paper corpus analysis, "
            "narrative-spine selection, claim freeze, paragraph-level claim planning, main figure-spine planning, deterministic "
            "PanelForge rendering, supplementary display planning, section-contract planning, front-matter strategy, Results architecture, "
            "Results drafting, Introduction literature binding, Discussion interpretation mapping, Discussion drafting, Methods architecture, "
            "and Methods drafting only. Do not start availability assembly, full reference library, figure legends, review response, supplementary methods, or submission packaging without explicit substage authorization."
        )
        artifacts = stage.setdefault("artifacts", [])
        for artifact in [
            "manuscript/nature_methods/sections/methods.md",
            "manuscript/nature_methods/gate_verdicts/9.16.json",
            "scripts/run_stage9_16_methods_drafting.py",
        ]:
            if artifact not in artifacts:
                artifacts.append(artifact)
        gate = stage.setdefault("gate", [])
        methods_gate = "Stage 9.16 Methods draft maps claim-bearing prose to Methods statement IDs and preserves software version boundaries."
        if methods_gate not in gate:
            gate.append(methods_gate)
        for subphase in stage.get("subphases", []):
            if isinstance(subphase, dict) and subphase.get("id") == "9.16":
                subphase["status"] = "complete_methods_drafted"
                subphase["evidence"] = "manuscript/nature_methods/gate_verdicts/9.16.json"
                subphase["methods_draft_version"] = draft_version
    _write_json(ROADMAP_MEMORY_PATH, memory)


def _replace_once(body: str, old: str, new: str) -> str:
    return body.replace(old, new) if old in body else body


def _update_docs() -> None:
    if PLAN_PATH.exists():
        body = PLAN_PATH.read_text(encoding="utf-8")
        body = _replace_once(
            body,
            "registers Results subsection architecture in Stage 9.10, registers a Results draft in Stage 9.11, and registers a citation-bound Introduction in Stage 9.12. It does not begin Discussion, Methods, full reference-library assembly, editorial polishing, or package assembly.",
            "registers Results subsection architecture in Stage 9.10, registers a Results draft in Stage 9.11, registers a citation-bound Introduction in Stage 9.12, registers the Discussion in Stage 9.14, registers Methods architecture in Stage 9.15, and registers Methods prose in Stage 9.16. It does not begin availability assembly, full reference-library assembly, figure legends, supplementary methods, editorial polishing, or package assembly.",
        )
        body = _replace_once(
            body,
            "Stage 9.15 registers Methods architecture in `sections/methods_blueprint.md`, `ledgers/methods_to_code_ledger.csv`, and `gate_verdicts/9.15.json`. The current state intentionally does not create `sections/methods.md`, `refs/references.bib`, figure legends, availability statements, or submission-package files.",
            "Stage 9.15 registers Methods architecture in `sections/methods_blueprint.md`, `ledgers/methods_to_code_ledger.csv`, and `gate_verdicts/9.15.json`. Stage 9.16 registers Methods prose in `sections/methods.md` and `gate_verdicts/9.16.json`. The current state intentionally does not create availability statements, `refs/references.bib`, figure legends, supplementary methods, or submission-package files.",
        )
        body = _replace_once(
            body,
            "| 9.16 | Methods drafting pass | not_started | Draft reviewer-reconstructable Methods. |",
            "| 9.16 | Methods drafting pass | complete_methods_drafted | Draft reviewer-reconstructable Methods. |",
        )
        PLAN_PATH.write_text(body, encoding="utf-8")
    if ROADMAP_PATH.exists():
        body = ROADMAP_PATH.read_text(encoding="utf-8")
        body = _replace_once(
            body,
            "Stage 9.14 has registered Discussion drafting. Methods, full reference-library\nassembly, and package assembly remain not started.",
            "Stage 9.14 has registered Discussion drafting, Stage 9.15 has registered\nMethods architecture, and Stage 9.16 has registered Methods prose.\nAvailability assembly, full reference-library assembly, figure legends,\nsupplementary methods, and package assembly remain not started.",
        )
        body = _replace_once(
            body,
            "| Stage 9. Nature Methods manuscript assembly | Stage 9.15 Methods architecture complete, Methods drafting not started. | The current boundary is evidence intake, official venue-guidance registration, representative methods-paper corpus analysis, narrative-spine selection, claim freeze, paragraph-level claim planning, main figure-spine planning, deterministic PanelForge rendering, supplementary display planning, section-contract planning, front-matter strategy, Results architecture, Results drafting, Introduction literature binding, Discussion interpretation mapping, Discussion drafting, and Methods architecture only. Do not start Methods drafting, availability assembly, full reference-library assembly, figure legends, review response, or submission packaging without explicit substage authorization. |",
            "| Stage 9. Nature Methods manuscript assembly | Stage 9.16 Methods drafting complete, availability assembly not started. | The current boundary is evidence intake, official venue-guidance registration, representative methods-paper corpus analysis, narrative-spine selection, claim freeze, paragraph-level claim planning, main figure-spine planning, deterministic PanelForge rendering, supplementary display planning, section-contract planning, front-matter strategy, Results architecture, Results drafting, Introduction literature binding, Discussion interpretation mapping, Discussion drafting, Methods architecture, and Methods drafting only. Do not start availability assembly, full reference-library assembly, figure legends, review response, supplementary methods, or submission packaging without explicit substage authorization. |",
        )
        body = _replace_once(
            body,
            "Stage 9.10 Results subsection architecture has been completed. Stage 9.11 Results drafting pass has been completed. Stage 9.12 Introduction literature binding has been completed. Stage 9.13 Discussion interpretation map has been completed. Stage 9.14 Discussion drafting pass has been completed. Stage 9.15 Methods architecture has been completed. Stage 9.16 Methods drafting pass remains the next unstarted manuscript step. Methods prose, availability assembly, full reference-library assembly, figure legends, and package assembly remain not started.",
            "Stage 9.10 Results subsection architecture has been completed. Stage 9.11 Results drafting pass has been completed. Stage 9.12 Introduction literature binding has been completed. Stage 9.13 Discussion interpretation map has been completed. Stage 9.14 Discussion drafting pass has been completed. Stage 9.15 Methods architecture has been completed. Stage 9.16 Methods drafting pass has been completed. Stage 9.17 software, data, and code availability assembly remains the next unstarted manuscript step. Availability assembly, full reference-library assembly, figure legends, supplementary methods, and package assembly remain not started.",
        )
        ROADMAP_PATH.write_text(body, encoding="utf-8")


def run() -> dict[str, Any]:
    generated_utc = _now()
    commit = _git_sha()
    draft_version = f"methods-draft@{generated_utc[:10]}@{commit}"
    if STAGING_DIR.exists():
        shutil.rmtree(STAGING_DIR)
    STAGING_DIR.mkdir(parents=True, exist_ok=True)
    methods_text = _build_methods(generated_utc, draft_version)
    _write_text(STAGING_DIR / OUTPUTS["methods"].relative_to(WORKSPACE), methods_text)
    checks = _validate(methods_text, commit)
    passed = all(check["passed"] for check in checks)
    visible = _visible_text(methods_text)
    gate = {
        "substage": "9.16",
        "timestamp": generated_utc,
        "methods_draft_version": draft_version,
        "pass": passed,
        "checks": checks,
        "methods_word_count": _word_count(visible),
        "methods_paragraph_count": len(METHODS_BLOCKS),
        "methods_statement_ids": sorted(_ledger_methods_ids()) if METHODS_LEDGER.exists() else [],
        "claim_ids": ["CLM-0001", "CLM-0002", "CLM-0003", "CLM-0004", "CLM-0005"],
        "software_version": "v0.1.0",
        "next_substage": "9.17",
        "outputs": [str(path.relative_to(ROOT)) for path in OUTPUTS.values()],
        "scope_boundary": "Methods prose only. No availability statements, references.bib, figure legends, Supplementary Methods, Reporting Summary, or submission-package assembly.",
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
        "substage": "9.16",
        "methods_draft_version": draft_version,
        "methods_word_count": _word_count(visible),
        "methods_paragraph_count": len(METHODS_BLOCKS),
        "failures": [check for check in checks if not check["passed"]],
        "outputs": gate["outputs"],
        "next_allowed_action": "Proceed to Stage 9.17 software, data, and code availability assembly after validation and explicit authorization.",
    }


def main() -> int:
    payload = run()
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())

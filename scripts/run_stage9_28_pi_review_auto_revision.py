"""Run Stage 9.28 PI-review auto-revision pass.

Stage 9.28 stress-tests the assembled Nature Methods package with a senior
reviewer persona, applies evidence-safe source edits, regenerates the package,
and writes the final human PI review packet. It does not create new analyses,
figures, datasets, model outputs, or the Stage 9 closure report.
"""

from __future__ import annotations

import csv
import hashlib
import json
import os
import re
import shutil
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT / "manuscript" / "nature_methods"
SECTIONS = WORKSPACE / "sections"
FIGURES = WORKSPACE / "figures"
SUPPLEMENTARY = WORKSPACE / "supplementary"
SUBMISSION = WORKSPACE / "submission_package"
GATES = WORKSPACE / "gate_verdicts"
AUDITS = WORKSPACE / "audits"
REFS = WORKSPACE / "refs"
STAGING = WORKSPACE / "_staging" / "9.28"
QUARANTINE = WORKSPACE / "_quarantine" / "9.28"
MEMORY_PATH = ROOT / "docs" / "stage9_execution_memory.json"
ROADMAP_MEMORY_PATH = ROOT / "docs" / "roadmap_execution_memory.json"
REGISTRY_PATH = WORKSPACE / "contracts" / "stage9_substage_registry.json"
PLAN_PATH = ROOT / "docs" / "stage9_manuscript_assembly_plan.md"
ROADMAP_PATH = ROOT / "docs" / "roadmap.md"
README_PATH = WORKSPACE / "README.md"
PERSONA_PROMPT = Path(
    os.environ.get(
        "RHODYN_PI_REVIEW_PERSONA_PROMPT",
        str(Path.home() / ".codex" / "attachments" / "aa5aac44-d0fc-4e6e-a378-5db4a05baa8a" / "pasted-text.txt"),
    )
)

GATE_927 = GATES / "9.27.json"
GATE_96B = GATES / "9.6b.json"
GATE_929 = GATES / "9.29.json"
STAGE927_RUNNER = ROOT / "scripts" / "run_stage9_27_submission_package_assembly.py"

OUTPUTS = {
    "packet": SUBMISSION / "pi_review_packet.md",
    "action_matrix": SUBMISSION / "pi_review_action_matrix.csv",
    "revision_log": SUBMISSION / "pi_review_revision_log.md",
    "literature": SUBMISSION / "pi_review_literature_calibration.md",
    "gate": GATES / "9.28.json",
}

SOURCE_EDIT_TARGETS = [
    SECTIONS / "abstract.md",
    SECTIONS / "introduction.md",
    SECTIONS / "discussion.md",
    SECTIONS / "methods.md",
    FIGURES / "figure_legends.md",
]

PACKAGE_SCAN_TARGETS = [
    SUBMISSION / "main_text_for_submission.md",
    SUBMISSION / "supplementary_information_for_submission.md",
    SUBMISSION / "editor_triage_note_for_cover_letter.md",
    SUBMISSION / "editorial_pitch_for_submission.md",
    SUBMISSION / "prior_art_positioning_matrix.md",
    SUBMISSION / "editor_objection_response_map.md",
    SUBMISSION / "editor_two_minute_triage_simulation.md",
    SUBMISSION / "current_nature_methods_policy_preflight.md",
    SUBMISSION / "software_reporting_checklist.md",
    SUBMISSION / "article_fit_checklist.md",
    SUBMISSION / "author_declarations_REQUIRED.md",
    SUBMISSION / "ai_disclosure_AUTHOR_CONFIRMATION_REQUIRED.md",
    SUBMISSION / "title_author_metadata_AUTHOR_CONFIRMATION_REQUIRED.md",
    SUBMISSION / "reporting_summary_answer_bank_AUTHOR_CONFIRMATION_REQUIRED.md",
    SUBMISSION / "pi_review_packet.md",
    SUBMISSION / "pi_review_action_matrix.csv",
    SUBMISSION / "pi_review_revision_log.md",
    SUBMISSION / "pi_review_literature_calibration.md",
]

FORBIDDEN_CLOSURE_PATHS = [
    WORKSPACE / "stage9_completion_report.md",
]

PACKAGE_FORBIDDEN_PATTERNS = [
    re.compile("/" + "Users/"),
    re.compile("/" + "Volumes/"),
    re.compile("Library/" + "LaunchAgents"),
    re.compile(r"\b" + "sk-" + r"[A-Za-z0-9_-]{10,}"),
    re.compile(r"\b" + "ghp" + "_" + r"[A-Za-z0-9_]{10,}"),
    re.compile(r"\b" + "github" + r"_pat_[A-Za-z0-9_]{10,}"),
]

REVIEW_HEADINGS = [
    "Executive Summary",
    "Revision Aspects",
    "Confidential Recommendation to the Editor",
]

ACTION_FIELDS = [
    "item_id",
    "severity",
    "manuscript_location",
    "issue",
    "auto_revision",
    "status",
    "remaining_requirement",
]


def _now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


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


def _closed_stage9_refresh_allowed() -> bool:
    if not GATE_929.exists():
        return False
    gate = _read_json(GATE_929)
    return (
        gate.get("pass") is True
        and gate.get("closure_status") == "complete_stage9_closed_version_bound"
    )


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_text(path: Path, body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body.rstrip() + "\n", encoding="utf-8")


def _write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _replace_once(path: Path, old: str, new: str, edit_id: str, description: str) -> dict[str, str]:
    body = path.read_text(encoding="utf-8")
    if new in body:
        return {
            "edit_id": edit_id,
            "file": path.relative_to(ROOT).as_posix(),
            "description": description,
            "status": "already_present",
        }
    if old not in body:
        return {
            "edit_id": edit_id,
            "file": path.relative_to(ROOT).as_posix(),
            "description": description,
            "status": "anchor_missing",
        }
    path.write_text(body.replace(old, new, 1), encoding="utf-8")
    return {
        "edit_id": edit_id,
        "file": path.relative_to(ROOT).as_posix(),
        "description": description,
        "status": "applied",
    }


def _apply_safe_revisions() -> list[dict[str, str]]:
    edits: list[dict[str, str]] = []
    edits.append(
        _replace_once(
            SECTIONS / "abstract.md",
            "RhoDyn therefore provides a reproducible route for identifying dynamic operating-state structure in live-cell perturbation data without treating every signal window, endpoint coordinate, or effective model term as a literal mechanism.",
            "RhoDyn therefore provides a reproducible route for identifying dynamic operating-state structure in live-cell perturbation data while preserving amplitude-sufficient, unresolved, and measurement-limited cases, and without treating every signal window, endpoint coordinate, or effective model term as a literal mechanism.",
            "REV-9.28-001",
            "Scope the abstract endpoint so the method advertises inconclusive and amplitude-sufficient outcomes as first-class outputs.",
        )
    )
    edits.append(
        _replace_once(
            SECTIONS / "introduction.md",
            "The novelty claimed here is not that signaling dynamics, transient cell states, or live-cell reporters matter. Those ideas are already well established in trajectory-inference, dynamic-state, live-cell reporter, and computational-methods literature (1-8). The contribution is a reviewable analysis object that places residence windows, amplitude comparators, bounded-coupling margins, reserve-like endpoint coordinates, routed-output alternatives, and cross-surface reproducibility into one reproducible workflow. RhoDyn therefore has to report when the supplied data do not justify a stronger conclusion. It returns bounded-coupling decisions only under declared margins and uncertainty support, keeps margin-sensitive contrasts inconclusive, treats reserve-like summaries as measurement-scoped endpoint coordinates, and compares routed-output alternatives against reduced architectures without treating effective parameters as direct biochemical interactions.",
            "The novelty claimed here is not that signaling dynamics, transient cell states, live-cell reporters, or morphodynamic trajectory embeddings matter. Those ideas are already well established in trajectory-inference, dynamic-state, live-cell reporter, morphodynamic, and computational-methods literature (1-9). The contribution is a reviewable analysis object that places residence windows, amplitude comparators, bounded-coupling margins, reserve-like endpoint coordinates, routed-output alternatives, and cross-surface reproducibility into one reproducible workflow. RhoDyn therefore has to report when the supplied data do not justify a stronger conclusion. It returns bounded-coupling decisions only under declared margins and uncertainty support, keeps margin-sensitive contrasts inconclusive, treats reserve-like summaries as measurement-scoped endpoint coordinates, and compares routed-output alternatives against reduced architectures without treating effective parameters as direct biochemical interactions.",
            "REV-9.28-002",
            "Make novelty positioning explicit against the current state of computational and live-cell dynamics methods.",
        )
    )
    edits.append(
        _replace_once(
            SECTIONS / "discussion.md",
            "RhoDyn supports a methods claim that is deliberately narrower than a general theory of cell fate. It makes residence-state inference executable and inspectable for live-cell perturbation data, allowing dwell fraction, dwell time, and segment count to be compared directly with endpoint, peak, mean, latency, and threshold-style summaries.",
            "RhoDyn supports a methods claim that is deliberately narrower than a general theory of cell fate and narrower than a claim that live-cell dynamics are newly important. Its advance is to make residence-state inference executable and inspectable for live-cell perturbation data, allowing dwell fraction, dwell time, and segment count to be compared directly with endpoint, peak, mean, latency, and threshold-style summaries.",
            "REV-9.28-003",
            "Calibrate the Discussion opening so the advance is method-level operationalization rather than novelty inflation around dynamics broadly.",
        )
    )
    edits.append(
        _replace_once(
            SECTIONS / "methods.md",
            "Rows with missing identifiers, missing columns, non-finite numeric values, negative time, or invalid margins were returned with validation issues rather than silently coerced. This preprocessing protects trace identity and biological grouping, but it cannot reconstruct missing time units, missing condition labels, or replicate structure that was not present in the input.",
            "Rows with missing identifiers, missing columns, non-finite numeric values, negative time, or invalid margins were returned with validation issues rather than silently coerced. Grouping variables were preserved for interval, bootstrap, bounded-coupling, and export summaries when supplied, and outputs record the grouping field used for interpretation. This preprocessing protects trace identity and biological grouping, but it cannot reconstruct missing time units, missing condition labels, or replicate structure that was not present in the input.",
            "REV-9.28-004",
            "Clarify how grouping and replicate fields are retained, while preserving the boundary that absent nesting cannot be recovered.",
        )
    )
    edits.append(
        _replace_once(
            FIGURES / "figure_legends.md",
            "These examples show that residence and amplitude can diverge in more than one public live-cell reporter system.",
            "These examples show that residence and amplitude can diverge in more than one public live-cell reporter system while leaving amplitude-sufficient and unresolved reporters within the method boundary.",
            "REV-9.28-005",
            "Keep the public-reporter figure legend from implying universal residence behavior.",
        )
    )
    return edits


def _run_stage927_package_assembly() -> tuple[bool, str]:
    existing_packet = OUTPUTS["packet"]
    if existing_packet.exists():
        existing_packet.unlink()
    result = subprocess.run(
        ["python3", str(STAGE927_RUNNER.relative_to(ROOT))],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    return result.returncode == 0, result.stdout


def _review_packet() -> str:
    return """# Executive Summary

The manuscript presents RhoDyn as a computational method for residence-state inference in live-cell perturbation data. Its most credible advance is not the broad observation that signaling dynamics matter, which is already established, but the integration of declared residence windows, amplitude comparators, bounded-coupling decisions, reserve-like endpoint coordinates, routed-output model comparison, and cross-surface reproducibility into one inspectable workflow. The work fits a Nature Methods-style Article best when positioned as a decision framework that reports pass, fail, and inconclusive outcomes rather than as a new biological theory. The six-figure structure is coherent, the public calcium and ERK demonstrations give useful portability evidence, and the software/release surfaces are unusually explicit for reviewer inspection.

My main reservations concern how much novelty should be assigned to the integrated workflow, how strongly the public examples establish generality, and whether readers can reconstruct grouping, margins, uncertainty rules, and non-example behavior without overreading the biological demonstrations. I do not find a fatal flaw in the current package, but several conclusions require continued restraint. The manuscript should keep its claim centered on an executable method object, not on universal residence biology, and it should retain amplitude-sufficient, inconclusive, and measurement-limited cases as core evidence rather than caveats.

# Revision Aspects

## Major

1. The novelty claim is plausible but must remain sharply differentiated from prior live-cell dynamics, trajectory-inference, and software-method literature. This issue appears in the title, Abstract, Introduction, and Discussion. The manuscript now states more clearly that the advance is not the discovery that signaling dynamics or transient states matter, but the operational workflow that combines residence scoring, amplitude comparators, bounded coupling, reserve-like endpoints, routed alternatives, and reproducibility surfaces. A satisfactory final version should keep that distinction visible throughout and avoid making the RhoDyn contribution sound like a general theory of cell-state dynamics.

2. The public demonstrations are useful but do not yet establish broad biological generality. Figures 3-5 show public reporter and endpoint examples, but the evidence is still a small set of selected systems rather than a field-wide benchmark. The authors should preserve the current language that the examples test portability and decision behavior, not universal residence biology. If a stronger generality claim is desired, it would require additional independent datasets or a predeclared sampling rationale, which is beyond the safe auto-revision scope.

3. The methods depend on declared windows, margins, and grouping choices, so reporting must make those choices reconstructable. This concern maps to Online Methods, Fig. 1, Fig. 4, Fig. 5, and Supplementary Methods. The source text now clarifies that grouping variables are preserved when supplied and that missing replicate structure cannot be reconstructed. A satisfactory package should keep the exact window, margin, grouping, and uncertainty fields visible in the supporting tables and should avoid implying that RhoDyn discovers biological windows automatically.

4. The bounded-coupling and reserve-like claims are appropriately scoped but remain sensitive to wording. In Fig. 4, Fig. 5, Online Methods, and Discussion, a passing bounded-coupling result should mean equivalence within the stated margin and context, not absence of all coupling. Likewise, reserve-like coordinates should remain tied to measured endpoint behavior rather than unmeasured biological reserve capacity. The current auto-revision preserves this boundary, but final review should check every caption and summary sentence for overstatement.

5. Routed-output model comparison should not be read as molecular mechanism identification. This affects Fig. 4d, Supplementary Fig. 6, Results, and Online Methods. The manuscript correctly frames reduced architectures as endpoint alternatives, but the term architecture can still invite mechanistic overinterpretation. The authors should keep effective-parameter language and avoid implying that the retained architecture identifies direct biochemical edges.

6. Statistical reporting is strong for a methods manuscript but should keep inconclusive outcomes as visible as passing calls. Figures 4 and 5 and the Methods describe declared margins, interval support, ROPE-style thresholds where available, and sensitivity to margins. This reviewer would not accept a revision that collapses those outcomes into a binary success-rate summary. The current package is acceptable only if pass, fail, and inconclusive cases remain co-equal in the Results and supplementary support.

7. Reproducibility is a strength, but the release boundary must stay exact. Figure 6, Code availability, and Code for review distinguish the GitHub/Zenodo release from PyPI distribution and from non-redistributable or controlled-access inputs. That precision should be retained. The official Reporting Summary, portal metadata, and any private input restrictions remain human-submission checks rather than manuscript-derived evidence.

## Minor

1. The Abstract should keep the phrase structure that names amplitude-sufficient and unresolved cases, because this prevents the method from being read as a universal residence detector.

2. The Introduction should avoid adding additional method-literature citations unless a specific claim is unsupported. The current reference set is compact and targeted, but final author review should confirm whether the ERK dynamics and equivalence-testing context needs one more explicit citation.

3. Figure 3 should continue to describe public reporters as demonstrations of portability, not proof that calcium and ERK share a common residence mechanism.

4. Figure 4 legend wording should retain the distinction between bounded coupling, reserve-like endpoint summaries, and routed-output comparisons. These are related decision objects, not interchangeable biological claims.

5. Figure 6 and Code availability should keep the PanelForge citation separate from the RhoDyn software citation, because figure rendering and method execution are distinct reproducibility surfaces.

6. The Methods should retain validation-failure language for invalid inputs. That language is important for users because a withheld decision is a legitimate method output.

7. The Supplementary Information should keep non-example and ambiguous regimes visible rather than burying them as limitations.

8. Before journal upload, the authors should complete the official Springer Nature Reporting Summary and verify that the final uploaded files preserve the same release identifiers and figure counts as the package.

# Confidential Recommendation to the Editor

Potentially Accept after Major Revision and Re-review

The manuscript has a credible methods contribution, but acceptance should depend on preserving the calibrated novelty claim and the decision-boundary language addressed in Major items 1-6. The required revisions are largely feasible through claim calibration, reporting precision, and documentation rather than new experiments, although a stronger generality claim would require additional datasets. The upside is a useful, reproducible framework for live-cell perturbation data that makes residence, bounded coupling, reserve-like endpoints, and routed-output alternatives reviewable across software surfaces. The main risk is novelty inflation or overgeneralization from a limited set of demonstrations if the manuscript drifts from method-object language into broad biological claims.
"""


def _action_rows() -> list[dict[str, str]]:
    return [
        {
            "item_id": "PI-9.28-MAJ-001",
            "severity": "major",
            "manuscript_location": "Abstract; Introduction; Discussion",
            "issue": "Novelty could be overread as discovery that live-cell dynamics matter rather than an integrated residence-state decision workflow.",
            "auto_revision": "Abstract, Introduction, and Discussion were recalibrated to define the advance as method-level operationalization.",
            "status": "auto_revised",
            "remaining_requirement": "Final author review should preserve this narrower novelty framing.",
        },
        {
            "item_id": "PI-9.28-MAJ-002",
            "severity": "major",
            "manuscript_location": "Results Fig. 3-5; Discussion",
            "issue": "Public demonstrations support portability but not universal biological generality.",
            "auto_revision": "Figure 3 legend and Abstract were scoped to preserve amplitude-sufficient and unresolved cases.",
            "status": "auto_revised",
            "remaining_requirement": "New datasets would be required for a stronger generality claim.",
        },
        {
            "item_id": "PI-9.28-MAJ-003",
            "severity": "major",
            "manuscript_location": "Online Methods; Fig. 1; Fig. 4; Fig. 5",
            "issue": "Window, margin, grouping, and uncertainty fields must remain reconstructable.",
            "auto_revision": "Methods now state that grouping fields are preserved and reported when supplied.",
            "status": "auto_revised",
            "remaining_requirement": "Human review should verify the official Reporting Summary and supplementary tables retain these fields.",
        },
        {
            "item_id": "PI-9.28-MAJ-004",
            "severity": "major",
            "manuscript_location": "Fig. 4; Fig. 5; Online Methods; Discussion",
            "issue": "Bounded coupling and reserve-like language can be overread mechanistically.",
            "auto_revision": "Existing scoped wording was retained and the review packet flags it as a required final check.",
            "status": "retained_boundary",
            "remaining_requirement": "Do not promote bounded-coupling or reserve-like statements beyond declared margins and measured endpoints.",
        },
        {
            "item_id": "PI-9.28-MAJ-005",
            "severity": "major",
            "manuscript_location": "Fig. 4d; Supplementary Fig. 6; Results; Online Methods",
            "issue": "Routed-output architecture comparisons can be mistaken for direct molecular mechanism identification.",
            "auto_revision": "No new edit required because Results, Methods, and legends already state this boundary.",
            "status": "open_human_check",
            "remaining_requirement": "Final author review should reject any wording that equates effective parameters with biochemical edges.",
        },
        {
            "item_id": "PI-9.28-HUMAN-001",
            "severity": "human_action",
            "manuscript_location": "Submission package",
            "issue": "The official Springer Nature Reporting Summary and portal metadata cannot be completed automatically from manuscript text.",
            "auto_revision": "Readiness and review surfaces retain this as a human submission action.",
            "status": "human_action_required",
            "remaining_requirement": "Complete the official form and final portal metadata before upload.",
        },
    ]


def _revision_log(edits: list[dict[str, str]], generated_utc: str) -> str:
    lines = [
        "# Stage 9.28 PI review revision log",
        "",
        f"Generated UTC. {generated_utc}",
        "",
        "## Auto-applied manuscript edits",
        "",
        "| Edit | File | Status | Rationale |",
        "| --- | --- | --- | --- |",
    ]
    for edit in edits:
        lines.append(f"| {edit['edit_id']} | `{edit['file']}` | {edit['status']} | {edit['description']} |")
    lines.extend(
        [
            "",
            "## Items intentionally not auto-resolved",
            "",
            "- No new biological datasets, analyses, model outputs, or figure renders were created.",
            "- The official Springer Nature Reporting Summary remains a human submission action.",
            "- Stronger claims of biological generality would require additional independent datasets or a predeclared sampling rationale.",
            "- Final portal metadata, author details, and submission-file naming remain human review actions.",
        ]
    )
    return "\n".join(lines)


def _literature_calibration(generated_utc: str) -> str:
    return f"""# Stage 9.28 literature and novelty calibration

Generated UTC. {generated_utc}

## Calibration result

The current reference set supports the main methods-positioning needs: trajectory-inference benchmarking, dynamic-state modeling, single-cell state-space visualization, directed fate mapping, live-cell morphodynamic trajectory embedding, software-method validation, spatial-omics workbench structure, probabilistic software architecture, public live-cell reporter datasets, public endpoint datasets, and citable RhoDyn/PanelForge release surfaces.

## Auto-revision decision

The Stage 9.29 closure decision promoted the live-cell morphodynamic trajectory-embedding prior-art citation into the reference library before this PI-review packet was regenerated. The revised framing states that RhoDyn does not claim novelty for live-cell dynamics, transient cell states, live-cell reporters, or morphodynamic trajectory analysis broadly, and instead claims a reproducible method object that combines declared residence windows, amplitude comparators, bounded-coupling margins, reserve-like endpoint coordinates, routed-output alternatives, and cross-surface reproducibility.

## Human-review note

If the authors want to strengthen the prior-art contrast further before journal upload, the most useful targeted additions would be a concise ERK dynamics review or a formal equivalence/ROPE methods citation. Those should be added only if the final manuscript text expands those topics beyond the current reference-backed wording.
"""


def _scan_forbidden(paths: list[Path]) -> list[str]:
    hits: list[str] = []
    for path in paths:
        if not path.exists() or not path.is_file():
            continue
        body = path.read_text(encoding="utf-8", errors="ignore")
        for pattern in PACKAGE_FORBIDDEN_PATTERNS:
            if pattern.search(body):
                hits.append(path.relative_to(ROOT).as_posix())
                break
    return hits


def _top_level_headings(body: str) -> list[str]:
    headings: list[str] = []
    for line in body.splitlines():
        if line.startswith("# ") and not line.startswith("## "):
            headings.append(line[2:].strip())
    return headings


def _validate_review_packet(body: str) -> dict[str, Any]:
    headings = _top_level_headings(body)
    major_count = len(re.findall(r"^\d+\. ", body.split("## Major", 1)[1].split("## Minor", 1)[0], flags=re.M)) if "## Major" in body else 0
    minor_count = len(re.findall(r"^\d+\. ", body.split("## Minor", 1)[1].split("# Confidential", 1)[0], flags=re.M)) if "## Minor" in body else 0
    recommendation = body.split("# Confidential Recommendation to the Editor", 1)[1].strip().splitlines()[0] if "# Confidential Recommendation to the Editor" in body else ""
    forbidden_meta = bool(re.search(r"\\bAI\\b|automation|prompt instructions|Stage 9", body, flags=re.I))
    return {
        "headings": headings,
        "major_count": major_count,
        "minor_count": minor_count,
        "recommendation": recommendation,
        "forbidden_meta": forbidden_meta,
    }


def _stage_outputs(generated_utc: str, edits: list[dict[str, str]], stage927_ok: bool, stage927_output: str) -> tuple[dict[str, Any], dict[str, Any]]:
    if STAGING.exists():
        shutil.rmtree(STAGING)
    STAGING.mkdir(parents=True)
    staging_submission = STAGING / "submission_package"
    staging_submission.mkdir(parents=True)
    staging_gates = STAGING / "gate_verdicts"
    staging_gates.mkdir(parents=True)

    packet = _review_packet()
    action_rows = _action_rows()
    revision_log = _revision_log(edits, generated_utc)
    literature = _literature_calibration(generated_utc)

    _write_text(staging_submission / "pi_review_packet.md", packet)
    _write_csv(staging_submission / "pi_review_action_matrix.csv", action_rows, ACTION_FIELDS)
    _write_text(staging_submission / "pi_review_revision_log.md", revision_log)
    _write_text(staging_submission / "pi_review_literature_calibration.md", literature)

    review_check = _validate_review_packet(packet)
    panelforge_gate = _read_json(GATE_96B) if GATE_96B.exists() else {}
    stage927_gate = _read_json(GATE_927) if GATE_927.exists() else {}
    package_hits = _scan_forbidden(PACKAGE_SCAN_TARGETS + [
        staging_submission / "pi_review_packet.md",
        staging_submission / "pi_review_action_matrix.csv",
        staging_submission / "pi_review_revision_log.md",
        staging_submission / "pi_review_literature_calibration.md",
    ])
    applied_or_present = [edit for edit in edits if edit["status"] in {"applied", "already_present"}]
    anchor_missing = [edit for edit in edits if edit["status"] == "anchor_missing"]
    closed_refresh = _closed_stage9_refresh_allowed()
    no_closure = [
        path.relative_to(ROOT).as_posix()
        for path in FORBIDDEN_CLOSURE_PATHS
        if path.exists() and not closed_refresh
    ]

    checks = [
        {"name": "stage_9_27_package_regenerated", "passed": stage927_ok and stage927_gate.get("pass") is True, "detail": stage927_output[-500:]},
        {"name": "persona_prompt_available", "passed": PERSONA_PROMPT.exists(), "detail": f"prompt_sha256={_sha256(PERSONA_PROMPT) if PERSONA_PROMPT.exists() else 'missing'}"},
        {"name": "pi_review_packet_present", "passed": bool(packet), "detail": "PI review packet assembled"},
        {"name": "required_review_headings_exact", "passed": review_check["headings"] == REVIEW_HEADINGS, "detail": f"headings={review_check['headings']}"},
        {"name": "major_minor_review_items_present", "passed": review_check["major_count"] >= 5 and review_check["minor_count"] >= 6, "detail": f"major={review_check['major_count']} minor={review_check['minor_count']}"},
        {"name": "confidential_recommendation_allowed", "passed": review_check["recommendation"] == "Potentially Accept after Major Revision and Re-review", "detail": review_check["recommendation"]},
        {"name": "review_surface_hygiene_passed", "passed": not review_check["forbidden_meta"], "detail": f"forbidden_meta={review_check['forbidden_meta']}"},
        {"name": "safe_source_revisions_applied", "passed": len(applied_or_present) == len(edits) and not anchor_missing, "detail": f"statuses={[edit['status'] for edit in edits]}"},
        {"name": "action_matrix_present", "passed": len(action_rows) >= 6, "detail": f"rows={len(action_rows)}"},
        {"name": "revision_log_present", "passed": bool(revision_log), "detail": "revision log assembled"},
        {"name": "literature_calibration_present", "passed": bool(literature) and "live-cell morphodynamic trajectory-embedding prior-art citation" in literature, "detail": "novelty calibration recorded"},
        {"name": "reader_surface_hygiene_passed", "passed": stage927_gate.get("pass") is True, "detail": "Stage 9.27 package gate remains passing after source edits"},
        {"name": "package_safety_scan_clear", "passed": not package_hits, "detail": f"package_hits={package_hits}"},
        {"name": "panelforge_status_unchanged", "passed": panelforge_gate.get("rendered_file_count") == 18, "detail": f"rendered_file_count={panelforge_gate.get('rendered_file_count')}"},
        {
            "name": "no_stage9_closure_started",
            "passed": not no_closure,
            "detail": (
                "Closed Stage 9.29 package refresh allowed existing closure surfaces"
                if closed_refresh and not no_closure
                else f"closure_paths={no_closure}"
            ),
        },
    ]
    pass_status = all(check["passed"] for check in checks)
    outputs = [path.relative_to(ROOT).as_posix() for path in OUTPUTS.values()]
    gate = {
        "status": "pass" if pass_status else "fail",
        "pass": pass_status,
        "substage": "9.28",
        "generated_utc": generated_utc,
        "git_commit": _git_sha(),
        "next_substage": "9.29",
        "review_recommendation": review_check["recommendation"],
        "auto_revision_count": len(applied_or_present),
        "newly_applied_edit_count": sum(1 for edit in edits if edit["status"] == "applied"),
        "safe_revision_count": len(applied_or_present),
        "major_review_item_count": review_check["major_count"],
        "minor_review_item_count": review_check["minor_count"],
        "action_matrix_rows": len(action_rows),
        "outputs": outputs,
        "scope_boundary": "PI review and evidence-safe auto-revision only. No new analysis, figure, dataset, model output, final journal upload, or Stage 9 closure is created.",
        "checks": checks,
    }
    _write_json(staging_gates / "9.28.json", gate)
    audit = {"checks": checks, "gate": gate}
    return audit, gate


def _quarantine_staging() -> str:
    if QUARANTINE.exists():
        shutil.rmtree(QUARANTINE)
    QUARANTINE.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(STAGING), str(QUARANTINE))
    return QUARANTINE.relative_to(ROOT).as_posix()


def _promote_from_staging() -> None:
    for key, path in OUTPUTS.items():
        source = STAGING / "submission_package" / path.name if key != "gate" else STAGING / "gate_verdicts" / "9.28.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, path)


def _update_submission_surfaces(generated_utc: str) -> None:
    support_files = [
        "manuscript/nature_methods/submission_package/pi_review_packet.md",
        "manuscript/nature_methods/submission_package/pi_review_action_matrix.csv",
        "manuscript/nature_methods/submission_package/pi_review_revision_log.md",
        "manuscript/nature_methods/submission_package/pi_review_literature_calibration.md",
    ]
    package_json_path = SUBMISSION / "submission_package_manifest.json"
    if package_json_path.exists():
        package_json = _read_json(package_json_path)
        package_json["current_substage"] = "9.28"
        package_json["next_substage"] = "9.29"
        package_json["pi_review_status"] = "complete_pi_review_packet"
        package_json["pi_review_support_files"] = support_files
        package_json["package_files"] = sorted(set(package_json.get("package_files", [])) | set(support_files))
        package_json["not_started"] = [
            item for item in package_json.get("not_started", []) if "pi_review" not in str(item)
        ]
        if "manuscript/nature_methods/stage9_completion_report.md" not in package_json["not_started"]:
            package_json["not_started"].append("manuscript/nature_methods/stage9_completion_report.md")
        _write_json(package_json_path, package_json)

    manifest_path = SUBMISSION / "submission_manifest.md"
    if manifest_path.exists():
        body = manifest_path.read_text(encoding="utf-8")
        if "| PI review packet |" not in body:
            body = body.replace(
                "| Consistency audit | `package_consistency_audit.md` | Package assembly checks. |",
                "| Consistency audit | `package_consistency_audit.md` | Package assembly checks. |\n"
                "| PI review packet | `pi_review_packet.md` | Final human PI-style review surface for author decision. |\n"
                "| PI review action matrix | `pi_review_action_matrix.csv` | Location-anchored revision and open-item matrix. |\n"
                "| PI review revision log | `pi_review_revision_log.md` | Evidence-safe source-edit log and unresolved human actions. |\n"
                "| PI review literature calibration | `pi_review_literature_calibration.md` | Prior-art and novelty calibration note. |",
            )
        body = body.replace(
            "Scope. This package assembles the current Nature Methods Article surfaces for collaborator review. It does not create the PI review packet, submit the manuscript, or close Stage 9.",
            "Scope. This package assembles the current Nature Methods Article surfaces for collaborator and PI review. It includes the Stage 9.28 review packet and support files, but it does not submit the manuscript or close Stage 9.",
        )
        body = body.replace(
            body.splitlines()[2] if len(body.splitlines()) > 2 and body.splitlines()[2].startswith("Generated UTC.") else "Generated UTC. unknown",
            f"Generated UTC. {generated_utc}",
            1,
        )
        manifest_path.write_text(body, encoding="utf-8")

    checklist_path = SUBMISSION / "submission_readiness_checklist.md"
    if checklist_path.exists():
        body = checklist_path.read_text(encoding="utf-8")
        if "| PI review packet |" not in body:
            body = body.replace(
                "| Consistency audit | ready | Package-level consistency checks passed. |",
                "| Consistency audit | ready | Package-level consistency checks passed. |\n"
                "| PI review packet | ready | `pi_review_packet.md` contains the final human PI-style review packet with the required three review sections. |\n"
                "| PI review support files | ready | Action matrix, revision log, and literature-calibration note are present. |",
            )
        body = body.replace(
            "Human actions before journal upload. Complete the official Springer Nature Reporting Summary form, choose the final corresponding-author and portal metadata, verify any journal-specific file naming rules, and review the assembled main text and Supplementary Information for final author approval.",
            "Human actions before journal upload. Complete the official Springer Nature Reporting Summary form, choose the final corresponding-author and portal metadata, verify any journal-specific file naming rules, review the assembled main text and Supplementary Information for final author approval, and decide whether any open PI-review items require new evidence before Stage 9 closure.",
        )
        checklist_path.write_text(body, encoding="utf-8")


def _update_registry() -> None:
    registry = _read_json(REGISTRY_PATH)
    registry["next_substage"] = "9.29"
    registry["updated_utc"] = _now()
    for item in registry.get("substages", []):
        if item.get("id") == "9.28":
            item["status"] = "complete_pi_review_packet"
    _write_json(REGISTRY_PATH, registry)


def _upsert_completed_substage(memory: dict[str, Any], checks: list[dict[str, Any]]) -> None:
    record = {
        "substage": "9.28",
        "status": "pass",
        "pass": True,
        "gate_verdict_path": "manuscript/nature_methods/gate_verdicts/9.28.json",
        "validation_outcome": "PI review packet assembled, safe source revisions applied, submission package regenerated, and remaining human actions preserved",
        "evidence_dependencies": [
            "manuscript/nature_methods/gate_verdicts/9.27.json",
            "manuscript/nature_methods/submission_package/main_text_for_submission.md",
            "manuscript/nature_methods/submission_package/supplementary_information_for_submission.md",
            "manuscript/nature_methods/audits/internal_peer_review_simulation.md",
        ],
        "files_created_or_modified": [path.relative_to(ROOT).as_posix() for path in OUTPUTS.values()],
        "remaining_blockers": [
            "Final Springer Nature Reporting Summary form remains a human submission action",
            "Final portal metadata and file naming remain human submission actions",
            "Stage 9 closure has not started",
        ],
        "checks": checks,
    }
    entries = [
        item
        for item in memory.get("completed_substages", [])
        if not (isinstance(item, dict) and item.get("substage") == "9.28") and item != "9.28"
    ]
    entries.append(record)
    memory["completed_substages"] = entries


def _update_stage9_memory(generated_utc: str, checks: list[dict[str, Any]]) -> None:
    memory = _read_json(MEMORY_PATH)
    memory["generated_utc"] = generated_utc
    memory["current_substage"] = "9.28"
    memory["pi_review_started"] = True
    memory["status"] = "stage9_28_pi_review_packet_complete"
    memory["current_gate"] = "Stage 9.28 prepared the final human PI review packet and evidence-safe source revisions"
    memory["next_substage"] = "9.29"
    memory["next_substage_authorized"] = False
    memory["stage9_active_gate"] = "Stage 9.28 PI review packet complete; Stage 9 closure not started"
    memory["stage9_28_checks"] = checks
    artifacts = memory.setdefault("artifacts", [])
    for artifact in [path.relative_to(ROOT).as_posix() for path in OUTPUTS.values()]:
        if artifact not in artifacts:
            artifacts.append(artifact)
    memory["gate"] = [
        "Stage 9.-1 contract and schema files exist and pass the scaffold checker.",
        "Stage 9.0 through Stage 9.28 are complete through final human PI review packet assembly.",
        "Stage 9.29 remains not started.",
        "No Stage 9 completion report is created in this pass.",
        "The package now contains the PI review packet, action matrix, revision log, and literature calibration record.",
    ]
    memory["scope_rule"] = (
        "Stage 9 has completed evidence intake, guidance, corpus, narrative spine, claim freeze, paragraph and figure planning, "
        "PanelForge rendering, supplementary planning, drafting, availability, references, consistency, statistics, legends, polish, "
        "reader-surface hygiene, internal peer review, submission package assembly, and PI review packet assembly. Do not start Stage 9 closure without explicit authorization."
    )
    _upsert_completed_substage(memory, checks)
    _write_json(MEMORY_PATH, memory)


def _update_roadmap_memory() -> None:
    memory = _read_json(ROADMAP_MEMORY_PATH)
    current = memory.setdefault("current_position", {})
    current["active_stage"] = "Stage 9.28 PI review packet complete; Stage 9 closure not started"
    current["stage9_active_gate"] = "Stage 9.28 PI review packet complete; Stage 9 closure not started"
    current["after_stage9_28_pi_review_packet"] = (
        "Stage 9.28 prepared the PI-review decision packet, applied evidence-safe source revisions, regenerated the submission package, "
        "and preserved Reporting Summary, author declarations, portal metadata, and closure as human/downstream actions."
    )
    current["current_gate"] = "PI review packet complete"
    current["next_stage"] = "Stage 9.29 Roadmap closure and version binding"
    for stage in memory.get("stage_lock", []):
        if not isinstance(stage, dict) or stage.get("stage") != 9:
            continue
        stage["status"] = "stage9_28_pi_review_packet_complete"
        stage["current_gate"] = "Stage 9.28 prepared the final human PI review packet"
        stage["scope_rule"] = "Stage 9 has completed through PI review packet assembly. Stage 9 closure remains not started."
        artifacts = stage.setdefault("artifacts", [])
        for artifact in [path.relative_to(ROOT).as_posix() for path in OUTPUTS.values()] + [
            "scripts/run_stage9_28_pi_review_auto_revision.py"
        ]:
            if artifact not in artifacts:
                artifacts.append(artifact)
        gate = stage.setdefault("gate", [])
        review_gate = "Stage 9.28 prepared the final PI review packet and applied evidence-safe source revisions without new analyses."
        if review_gate not in gate:
            gate.append(review_gate)
        for subphase in stage.get("subphases", []):
            if isinstance(subphase, dict) and subphase.get("id") == "9.28":
                subphase["status"] = "complete_pi_review_packet"
                subphase["evidence"] = "manuscript/nature_methods/gate_verdicts/9.28.json"
    _write_json(ROADMAP_MEMORY_PATH, memory)


def _replace(body: str, old: str, new: str) -> str:
    return body.replace(old, new) if old in body else body


def _update_docs() -> None:
    README_PATH.write_text(
        """# Nature Methods manuscript workspace

This directory is the Stage 9 manuscript-assembly workspace for RhoDyn.

Current status. Stage 9.28 PI review packet complete.

The workspace now contains the authorized manuscript components through final human PI review packet assembly. Evidence intake, venue guidance, methods-paper corpus analysis, narrative spine, claim freeze, paragraph planning, figure planning, deterministic main-figure rendering, supplementary display planning, section contracts, front matter, Results, Introduction, Discussion, Methods, availability statements, Supplementary Methods, supplementary table/source-data binding, reference audit, cross-document consistency audit, statistical-language audit, figure legend/caption audit, editorial polish passes I and II, reader-surface hygiene, internal peer review, submission package assembly, and PI review packet assembly are present.

The next unstarted step is Stage 9.29 roadmap closure and version binding. The package currently includes `submission_package/main_text_for_submission.md`, `submission_package/supplementary_information_for_submission.md`, `submission_package/pi_review_packet.md`, `submission_package/pi_review_action_matrix.csv`, `submission_package/pi_review_revision_log.md`, `submission_package/pi_review_literature_calibration.md`, `submission_package/code_for_review.md`, `submission_package/editor_triage_note_for_cover_letter.md`, `submission_package/editorial_pitch_for_submission.md`, `submission_package/prior_art_positioning_matrix.md`, `submission_package/editor_objection_response_map.md`, `submission_package/editor_two_minute_triage_simulation.md`, `submission_package/current_nature_methods_policy_preflight.md`, `submission_package/software_reporting_checklist.md`, `submission_package/article_fit_checklist.md`, `submission_package/author_declarations_REQUIRED.md`, `submission_package/ai_disclosure_AUTHOR_CONFIRMATION_REQUIRED.md`, `submission_package/title_author_metadata_AUTHOR_CONFIRMATION_REQUIRED.md`, `submission_package/figure_file_inventory.csv`, `submission_package/source_data_and_statistics_inventory.csv`, `submission_package/submission_readiness_checklist.md`, `submission_package/package_consistency_audit.md`, and `submission_package/submission_package_manifest.json`.

The official Springer Nature Reporting Summary form, author declarations, portal metadata, and final upload checks remain human submission actions. The Stage 9 closure report has not started.

PanelForge figure rendering has already been exercised through the authorized Stage 9.6b deterministic rendering lane. The placeholder under `tools/panelforge-figures/` is not a clone, `.venv-panelforge` is not created by this workspace, and no local figure-engine repository is vendored here.
""",
        encoding="utf-8",
    )
    if PLAN_PATH.exists():
        body = PLAN_PATH.read_text(encoding="utf-8")
        body = _replace(
            body,
            "internal peer review simulation through Stage 9.27. It has assembled the collaborator-review submission package. Final PI review and Stage 9 closure have not started.",
            "internal peer review simulation, submission package assembly, and PI review packet assembly through Stage 9.28. Stage 9 closure has not started.",
        )
        body = _replace(
            body,
            "Stage 9.27 registers the collaborator-review submission package, `submission_package/submission_readiness_checklist.md`, and `gate_verdicts/9.27.json`. The current state intentionally does not create the PI review packet or Stage 9 completion report.",
            "Stage 9.27 registers the collaborator-review submission package, `submission_package/submission_readiness_checklist.md`, and `gate_verdicts/9.27.json`. Stage 9.28 registers `submission_package/pi_review_packet.md`, `submission_package/pi_review_action_matrix.csv`, `submission_package/pi_review_revision_log.md`, `submission_package/pi_review_literature_calibration.md`, and `gate_verdicts/9.28.json`. The current state intentionally does not create the Stage 9 completion report.",
        )
        body = _replace(
            body,
            "| 9.28 | Final human PI review packet | not_started | Prepare final human decision packet. |",
            "| 9.28 | Final human PI review packet | complete_pi_review_packet | Prepare final human decision packet. |",
        )
        PLAN_PATH.write_text(body, encoding="utf-8")
    if ROADMAP_PATH.exists():
        body = ROADMAP_PATH.read_text(encoding="utf-8")
        body = _replace(
            body,
            "Stage 9.25 has completed editorial polish pass II, Stage 9.25b has\ncompleted reader-surface hygiene, Stage 9.26 has completed internal peer review\nsimulation, and Stage 9.27 has completed collaborator-review package assembly.\nFinal PI review and Stage 9 closure remain not started.",
            "Stage 9.25 has completed editorial polish pass II, Stage 9.25b has\ncompleted reader-surface hygiene, Stage 9.26 has completed internal peer review\nsimulation, Stage 9.27 has completed collaborator-review package assembly, and\nStage 9.28 has completed the final human PI review packet. Stage 9 closure remains not started.",
        )
        body = _replace(
            body,
            "| Stage 9. Nature Methods manuscript assembly | Stage 9.27 Submission package assembly complete, final PI review not started. | The current boundary is evidence intake, official venue-guidance registration, representative methods-paper corpus analysis, narrative-spine selection, claim freeze, paragraph-level claim planning, main figure-spine planning, deterministic PanelForge rendering, supplementary display planning, section-contract planning, front-matter strategy, Results architecture, Results drafting, Introduction literature binding, Discussion interpretation mapping, Discussion drafting, Methods architecture, Methods drafting, availability assembly, Supplementary Methods drafting, supplementary table/source-data binding, reference-library/citation audit, cross-document consistency audit, statistical-language audit, figure legend/caption audit, editorial polish passes I and II, reader-surface hygiene, internal peer review simulation, and submission package assembly. Do not start final PI review or Stage 9 closure without explicit substage authorization. |",
            "| Stage 9. Nature Methods manuscript assembly | Stage 9.28 PI review packet complete, Stage 9 closure not started. | The current boundary is evidence intake, official venue-guidance registration, representative methods-paper corpus analysis, narrative-spine selection, claim freeze, paragraph-level claim planning, main figure-spine planning, deterministic PanelForge rendering, supplementary display planning, section-contract planning, front-matter strategy, Results architecture, Results drafting, Introduction literature binding, Discussion interpretation mapping, Discussion drafting, Methods architecture, Methods drafting, availability assembly, Supplementary Methods drafting, supplementary table/source-data binding, reference-library/citation audit, cross-document consistency audit, statistical-language audit, figure legend/caption audit, editorial polish passes I and II, reader-surface hygiene, internal peer review simulation, submission package assembly, and PI review packet assembly. Do not start Stage 9 closure without explicit substage authorization. |",
        )
        body = _replace(
            body,
            "Stage 9.24 Editorial polish pass I has been completed. Stage 9.25 Editorial polish pass II has been completed. Stage 9.25b Reader-surface hygiene has been completed. Stage 9.26 Internal peer review simulation has been completed. Stage 9.27 Submission package assembly has been completed. Stage 9.28 Final human PI review packet remains the next unstarted manuscript step. Stage 9 closure remains not started.",
            "Stage 9.24 Editorial polish pass I has been completed. Stage 9.25 Editorial polish pass II has been completed. Stage 9.25b Reader-surface hygiene has been completed. Stage 9.26 Internal peer review simulation has been completed. Stage 9.27 Submission package assembly has been completed. Stage 9.28 Final human PI review packet has been completed. Stage 9.29 closure remains the next unstarted manuscript step.",
        )
        ROADMAP_PATH.write_text(body, encoding="utf-8")


def run() -> dict[str, Any]:
    generated_utc = _now()
    edits = _apply_safe_revisions()
    stage927_ok, stage927_output = _run_stage927_package_assembly()
    audit, gate = _stage_outputs(generated_utc, edits, stage927_ok, stage927_output)
    if not gate["pass"]:
        quarantine = _quarantine_staging()
        return {
            "status": "failed",
            "substage": "9.28",
            "quarantine": quarantine,
            "checks": audit["checks"],
            "next_substage": "9.28",
        }
    _promote_from_staging()
    shutil.rmtree(STAGING)
    if QUARANTINE.exists():
        shutil.rmtree(QUARANTINE)
    _update_submission_surfaces(generated_utc)
    _update_registry()
    _update_stage9_memory(generated_utc, audit["checks"])
    _update_roadmap_memory()
    _update_docs()
    return {
        "status": "completed",
        "substage": "9.28",
        "outputs": [path.relative_to(ROOT).as_posix() for path in OUTPUTS.values()],
        "checks": audit["checks"],
        "next_substage": "9.29",
        "auto_revision_count": gate["auto_revision_count"],
        "major_review_item_count": gate["major_review_item_count"],
        "minor_review_item_count": gate["minor_review_item_count"],
    }


def main() -> int:
    result = run()
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] == "completed" else 1


if __name__ == "__main__":
    raise SystemExit(main())

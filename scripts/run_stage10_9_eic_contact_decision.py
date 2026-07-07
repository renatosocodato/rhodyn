"""Run Stage 10.9 EIC-contact route decision.

Stage 10.9 converts the Stage 10 evidence ladder and Stage 10.8 red-team
result into an editor-contact route decision. It does not send any message and
does not add data, figures, benchmarks, or manuscript claims.
"""

from __future__ import annotations

import csv
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "case_studies" / "stage10_eic_contact_decision"
DOC_PATH = ROOT / "docs" / "stage10_9_eic_contact_decision.md"
GATE_REPORT = OUTPUT_DIR / "stage10_9_gate_report.json"
DECISION_MEMO = OUTPUT_DIR / "stage10_9_decision_memo.md"
ONE_PAGE_PITCH = OUTPUT_DIR / "stage10_9_one_page_pitch.md"
EMAIL_DRAFT = OUTPUT_DIR / "stage10_9_presubmission_email_draft_AUTHOR_REVIEW_REQUIRED.md"
ROUTE_MATRIX = OUTPUT_DIR / "stage10_9_route_decision_matrix.tsv"
CONTACT_MANIFEST = OUTPUT_DIR / "stage10_9_contact_package_manifest.tsv"

RED_TEAM_GATE = ROOT / "case_studies" / "stage10_eic_red_team" / "stage10_8_gate_report.json"
STAGE10_6_PITCH = ROOT / "manuscript" / "nature_methods" / "stage10_6" / "eic_pitch_v2.md"

SELECTED_ROUTE = "presubmission_query_author_review_required"
EXTERNAL_CONTACT_STATUS = "not_sent"

ROUTE_FIELDS = [
    "route",
    "decision",
    "rationale",
    "residual_risk",
    "required_human_action",
]

CONTACT_FIELDS = ["surface", "path", "role", "author_action_required"]

REQUIRED_MESSAGE_BEATS = [
    "method advance",
    "comparator classes",
    "public biological breadth",
    "held-out validation",
    "software reproducibility",
    "limits and not biology-only",
]


def _git_sha() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "unknown"


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _read_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_text(path: Path, body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body.rstrip() + "\n", encoding="utf-8")


def _write_tsv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def route_rows() -> list[dict[str, str]]:
    return [
        {
            "route": "full_submission",
            "decision": "not_selected_now",
            "rationale": "Stage 10.8 makes full submission viable, but direct submission still carries medium residual risk from unrendered Stage 10 figures and absence of prospective collaborator-blind validation.",
            "residual_risk": "medium",
            "required_human_action": "PI may override only after accepting the medium-risk items.",
        },
        {
            "route": SELECTED_ROUTE,
            "decision": "selected",
            "rationale": "Stage 10.8 cleared high-severity desk-rejection risks while retaining medium route uncertainty, making a concise presubmission query the lowest-risk editor-facing step.",
            "residual_risk": "medium_low",
            "required_human_action": "Author must review, edit, and explicitly authorize any external message before sending.",
        },
        {
            "route": "delay_for_another_dataset",
            "decision": "not_selected_now",
            "rationale": "Additional public or collaborator-blind evidence would strengthen the package, but Stage 10.3 and Stage 10.4 already satisfy the current breadth and held-out gates.",
            "residual_risk": "medium",
            "required_human_action": "Use only if the author team wants a stronger direct-submission posture before editor contact.",
        },
        {
            "route": "pivot_venue",
            "decision": "fallback_only",
            "rationale": "Pivot remains appropriate if Nature Methods reads RhoDyn primarily as workflow/software integration despite Stage 10 evidence.",
            "residual_risk": "medium",
            "required_human_action": "Hold as contingency after editor feedback or PI decision.",
        },
    ]


def contact_manifest_rows() -> list[dict[str, str]]:
    return [
        {
            "surface": "decision_memo",
            "path": DECISION_MEMO.relative_to(ROOT).as_posix(),
            "role": "records route choice and residual risks",
            "author_action_required": "review before any journal contact",
        },
        {
            "surface": "one_page_pitch",
            "path": ONE_PAGE_PITCH.relative_to(ROOT).as_posix(),
            "role": "EIC-safe presubmission pitch source",
            "author_action_required": "edit and approve before reuse",
        },
        {
            "surface": "email_draft",
            "path": EMAIL_DRAFT.relative_to(ROOT).as_posix(),
            "role": "optional presubmission email scaffold",
            "author_action_required": "must be reviewed and sent manually by author if used",
        },
        {
            "surface": "route_matrix",
            "path": ROUTE_MATRIX.relative_to(ROOT).as_posix(),
            "role": "route alternatives and rationale",
            "author_action_required": "none unless overriding selected route",
        },
    ]


def one_page_pitch_text() -> str:
    return """# Stage 10.9 one-page EIC-safe presubmission pitch

## Working title

Residence-state inference for live-cell perturbation data

## Pitch

RhoDyn is a residence-state inference method for live-cell perturbation biology that asks when time spent inside a declared biological response regime changes interpretation relative to endpoint, amplitude, threshold, and generic time-series summaries. It benchmarks that decision object against simple summaries, SciPy peak summaries, scikit-learn feature models, HMM state summaries, catch22-style, tsfresh-style, MiniROCKET-style, and ruptures-style comparator families, retaining cases where simpler summaries are sufficient rather than claiming universal superiority. Public demonstrations span DRG calcium dynamics, GPCR-linked ERK trajectories, Cell Painting/MitoTox endpoint profiling, and MLCI tracking, so the method is not presented as a single-system extension of the RhoA/microglia manuscript. A sealed no-retuning validation route preserves positive residence-divergence, comparator-sufficient, bounded-coupling, and inconclusive calls across held-out public-derived contexts. The software implementation makes the method inspectable through Python, command-line, API, workbench, checksum, and archive surfaces, but reproducibility supports the method claim rather than replacing it. The intended Nature Methods contribution is therefore not a biology-only manuscript and not a software wrapper; it is a scoped decision framework for deciding when residence, bounded coupling, reserve-like preservation, or routed-output structure changes interpretation, and when it does not.

## Residual boundaries for the editor-facing version

- Declared residence windows are analysis objects, not automatically discovered biological mechanisms.
- Held-out validation is no-retuning public-derived replay, not a prospective blinded collaborator study.
- Reserve-like and routed-output calls are measurement-scoped and effective-model decisions.
- Named feature and classifier baselines can be sufficient in some regimes.
"""


def email_draft_text() -> str:
    return """# Stage 10.9 presubmission email draft. Author review required

Subject. Presubmission inquiry for Nature Methods. Residence-state inference for live-cell perturbation data

Dear Nature Methods editorial team,

I am writing to ask whether the enclosed concept would be appropriate for a presubmission inquiry as a computational methods Article.

RhoDyn is a residence-state inference method for live-cell perturbation biology that asks when dwell inside a declared response regime changes interpretation relative to endpoint, amplitude, threshold, and generic time-series summaries. The package benchmarks this decision object against simple summaries, SciPy peak summaries, scikit-learn feature models, HMM state summaries, catch22-style, tsfresh-style, MiniROCKET-style, and ruptures-style comparator families, while preserving regimes where simpler summaries are sufficient. Public demonstrations span DRG calcium, GPCR-linked ERK, Cell Painting/MitoTox endpoints, and MLCI tracking, and a sealed no-retuning validation route preserves positive, comparator-sufficient, bounded-coupling, and inconclusive calls in held-out public-derived contexts. The software implementation is available through Python, command-line, API, workbench, checksum, and archive surfaces, but the proposed Article is framed around the method object rather than software availability alone. The main limitation is explicit. RhoDyn does not claim that every live-cell system contains a residence regime or that declared windows are mechanisms; it provides a reproducible decision route for determining when residence-state structure changes interpretation and when simpler summaries are adequate.

Would this scope fit Nature Methods for a presubmission evaluation?

Sincerely,

[Author name, affiliation, and contact details to be completed by the corresponding author]
"""


def _message_beat_status(pitch: str) -> dict[str, bool]:
    return {
        "method advance": "residence-state inference method" in pitch,
        "comparator classes": "SciPy peak summaries" in pitch
        and "scikit-learn feature models" in pitch
        and "HMM state summaries" in pitch,
        "public biological breadth": "DRG calcium" in pitch
        and "GPCR-linked ERK" in pitch
        and "Cell Painting/MitoTox" in pitch
        and "MLCI tracking" in pitch,
        "held-out validation": "sealed no-retuning validation" in pitch or "sealed no-retuning validation route" in pitch,
        "software reproducibility": "Python, command-line, API, workbench, checksum, and archive" in pitch,
        "limits and not biology-only": "not a biology-only manuscript" in pitch
        and "not a software wrapper" in pitch,
    }


def validate_stage10_9() -> dict[str, object]:
    red_team = _read_json(RED_TEAM_GATE) if RED_TEAM_GATE.exists() else {}
    red_team_gates = red_team.get("gates", {})
    red_team_summary = red_team.get("summary_metrics", {})
    pitch = one_page_pitch_text()
    beat_status = _message_beat_status(pitch)
    route_selection = {row["route"]: row["decision"] for row in route_rows()}
    gates = {
        "stage10_8_prerequisite_passed": red_team.get("status") == "pass"
        and isinstance(red_team_gates, dict)
        and all(red_team_gates.values()),
        "no_high_severity_risk_inherited": isinstance(red_team_summary, dict)
        and red_team_summary.get("unresolved_high_severity_count") == 0,
        "presubmission_route_selected": route_selection.get(SELECTED_ROUTE) == "selected",
        "full_submission_not_selected_without_pi_acceptance": route_selection.get("full_submission") == "not_selected_now",
        "six_message_beats_present": all(beat_status.values()),
        "old_package_contact_forbidden": "Stage 9.29 package alone" in decision_memo_text(),
        "external_contact_not_sent": EXTERNAL_CONTACT_STATUS == "not_sent",
        "author_review_required": "Author review required" in email_draft_text()
        and "author if used" in json.dumps(contact_manifest_rows()),
    }
    return {
        "stage": "10.9",
        "status": "pass" if all(gates.values()) else "fail",
        "generated_utc": _now(),
        "git_sha": _git_sha(),
        "selected_route": SELECTED_ROUTE,
        "external_contact_status": EXTERNAL_CONTACT_STATUS,
        "gates": gates,
        "message_beat_status": beat_status,
        "summary_metrics": {
            "route_count": len(route_rows()),
            "selected_route_count": sum(row["decision"] == "selected" for row in route_rows()),
            "message_beat_count": sum(beat_status.values()),
            "unresolved_high_severity_count_inherited": red_team_summary.get("unresolved_high_severity_count")
            if isinstance(red_team_summary, dict)
            else None,
        },
        "required_human_actions": [
            "PI or corresponding author must review and approve the presubmission query before any contact.",
            "Author must complete sender identity, affiliation, and contact details.",
            "Author must decide whether to attach or mention the Stage 10 one-page pitch.",
        ],
        "interpretation_boundary": "Stage 10.9 chooses an editor-contact route and prepares author-review surfaces. It does not send any message and does not add data, benchmarks, figures, or manuscript claims.",
        "next_phase": "Author review and optional EIC presubmission contact",
    }


def decision_memo_text() -> str:
    return """# Stage 10.9 EIC-contact decision memo

## Decision

Selected route. Presubmission-style contact with author review required.

Do not submit a full Nature Methods package directly from the current state unless the PI explicitly accepts the remaining medium-risk items around new rendered Stage 10 figures and absence of prospective collaborator-blind validation. Do not ask the EIC to reconsider the Stage 9.29 package alone.

## Rationale

Stage 10.8 found no unresolved high-severity desk-rejection risk in novelty, validation breadth, named benchmarking, or overclaiming. The remaining uncertainty is route risk, not evidence collapse. A presubmission query lets the editor evaluate the method-first framing while keeping the contact concise and reversible.

## What the presubmission pitch should foreground

1. RhoDyn as a residence-state inference method for live-cell perturbation data.
2. Named comparator families and cases where simpler summaries remain sufficient.
3. Public biological breadth across four counted systems.
4. Sealed no-retuning held-out validation with positive, comparator-sufficient, bounded-coupling, and inconclusive calls.
5. Reproducible software as support for the method, not as the primary scientific advance.
6. Explicit limits on mechanism discovery and universal-residence claims.

## What remains author-dependent

The external message is not sent by this stage. The corresponding author must decide whether to use the draft, alter the scope, attach the one-page pitch, delay for another dataset, or pursue a full submission instead.
"""


def doc_text(report: dict[str, object]) -> str:
    return f"""# Stage 10.9 EIC-contact decision

Stage 10.9 converts the completed Stage 10 evidence ladder into a route decision for Nature Methods editor contact.

## Selected route

`{report['selected_route']}`

## Contact status

`{report['external_contact_status']}`

## Outputs

- `case_studies/stage10_eic_contact_decision/stage10_9_decision_memo.md`
- `case_studies/stage10_eic_contact_decision/stage10_9_one_page_pitch.md`
- `case_studies/stage10_eic_contact_decision/stage10_9_presubmission_email_draft_AUTHOR_REVIEW_REQUIRED.md`
- `case_studies/stage10_eic_contact_decision/stage10_9_route_decision_matrix.tsv`
- `case_studies/stage10_eic_contact_decision/stage10_9_contact_package_manifest.tsv`
- `case_studies/stage10_eic_contact_decision/stage10_9_gate_report.json`

## Gate status

{report['status']}

## Boundary

{report['interpretation_boundary']}
"""


def run_stage10_9() -> dict[str, object]:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    _write_tsv(ROUTE_MATRIX, route_rows(), ROUTE_FIELDS)
    _write_tsv(CONTACT_MANIFEST, contact_manifest_rows(), CONTACT_FIELDS)
    _write_text(DECISION_MEMO, decision_memo_text())
    _write_text(ONE_PAGE_PITCH, one_page_pitch_text())
    _write_text(EMAIL_DRAFT, email_draft_text())
    report = validate_stage10_9()
    _write_json(GATE_REPORT, report)
    _write_text(DOC_PATH, doc_text(report))
    return report


if __name__ == "__main__":
    print(json.dumps(run_stage10_9(), indent=2, sort_keys=True))

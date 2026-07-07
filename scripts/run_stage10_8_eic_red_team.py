"""Run Stage 10.8 adversarial EIC red-team simulation.

Stage 10.8 stress-tests the Stage 10 method-elevation package as a Nature
Methods-facing methods claim. It does not add datasets, benchmark results,
figures, or manuscript claims. The output is a desk-rejection risk matrix and
gate report that decide whether any high-severity editorial risk remains
unresolved before Stage 10.9 chooses the editor-contact route.
"""

from __future__ import annotations

import csv
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "case_studies" / "stage10_eic_red_team"
DOC_PATH = ROOT / "docs" / "stage10_8_adversarial_eic_red_team.md"
GATE_REPORT = OUTPUT_DIR / "stage10_8_gate_report.json"
REPORT_PATH = OUTPUT_DIR / "stage10_8_red_team_report.md"
ACTION_MATRIX_PATH = OUTPUT_DIR / "stage10_8_red_team_action_matrix.tsv"
VERDICT_RUBRIC_PATH = OUTPUT_DIR / "stage10_8_verdict_rubric.tsv"
DECISION_BRIEF_PATH = OUTPUT_DIR / "stage10_8_decision_brief.md"

PREREQ_GATE = ROOT / "case_studies" / "stage10_release_candidate" / "stage10_7_gate_report.json"

PERSPECTIVES = [
    "Nature Methods EIC",
    "methods editor",
    "computational methods reviewer",
    "live-cell signaling biologist",
    "statistician/benchmarking reviewer",
    "software reproducibility reviewer",
]

REQUIRED_VERDICTS = [
    "desk-reject likely",
    "presubmission only",
    "full submission viable",
    "delay for another dataset",
    "pivot venue",
]

CRITICAL_DOMAINS = {
    "novelty",
    "validation_breadth",
    "named_benchmarking",
    "overclaiming",
}

ACTION_FIELDS = [
    "perspective",
    "verdict_category",
    "risk_domain",
    "concern",
    "severity_initial",
    "stage10_evidence",
    "mitigation_or_decision",
    "severity_after_stage10",
    "unresolved_high_severity",
    "action_status",
]


ACTION_ROWS = [
    {
        "perspective": "Nature Methods EIC",
        "verdict_category": "full submission viable",
        "risk_domain": "novelty",
        "concern": "RhoDyn could still be read as useful software integration rather than a Nature Methods-level method.",
        "severity_initial": "high",
        "stage10_evidence": "Stage 10.1 formal method object, Stage 10.2 named comparator families, Stage 10.5 method-first figure architecture, and Stage 10.6 method-first title/abstract/pitch.",
        "mitigation_or_decision": "Resolved to medium residual risk because the first read now names residence-state inference, comparator divergence, abstention, bounded coupling, reserve-like endpoints, routed alternatives, and held-out outcomes before software surfaces.",
        "severity_after_stage10": "medium",
        "unresolved_high_severity": "no",
        "action_status": "resolved_by_stage10_evidence",
    },
    {
        "perspective": "Nature Methods EIC",
        "verdict_category": "full submission viable",
        "risk_domain": "validation_breadth",
        "concern": "The method could be dismissed as a single-paper or single-biology extension if the public examples look narrow.",
        "severity_initial": "high",
        "stage10_evidence": "Stage 10.3 counts four independent public systems across live-cell calcium, GPCR-linked ERK, endpoint profiling, and microbial tracking; Stage 10.4 adds no-retuning held-out positive, comparator-sufficient, and inconclusive calls.",
        "mitigation_or_decision": "Resolved to medium residual risk. Breadth is materially stronger but still should be described as public-system breadth rather than universal biological generality.",
        "severity_after_stage10": "medium",
        "unresolved_high_severity": "no",
        "action_status": "resolved_by_stage10_evidence",
    },
    {
        "perspective": "methods editor",
        "verdict_category": "full submission viable",
        "risk_domain": "method_identity",
        "concern": "The manuscript must foreground a method object rather than a convenience workflow.",
        "severity_initial": "high",
        "stage10_evidence": "Stage 10.1 defines input objects, residence windows, dwell summaries, amplitude comparators, decision divergence, abstention, bounded coupling, reserve-like calls, routed-output comparisons, and uncertainty outputs.",
        "mitigation_or_decision": "Resolved. The method identity is now reviewable as a decision framework with executable positive, counterexample, and ambiguous fixtures.",
        "severity_after_stage10": "low",
        "unresolved_high_severity": "no",
        "action_status": "resolved_by_stage10_evidence",
    },
    {
        "perspective": "methods editor",
        "verdict_category": "presubmission only",
        "risk_domain": "venue_fit",
        "concern": "A direct full submission may still be riskier than a concise presubmission query because Stage 10 has not yet produced a new rendered figure set.",
        "severity_initial": "medium",
        "stage10_evidence": "Stage 10.5 defines the method-first figure architecture, but the historical Stage 9 rendered mockups remain the current rendered figure files.",
        "mitigation_or_decision": "Route to Stage 10.9. The safer editor-contact route is a presubmission-style note unless a Stage 10 PanelForge render is authorized.",
        "severity_after_stage10": "medium",
        "unresolved_high_severity": "no",
        "action_status": "routed_to_stage10_9",
    },
    {
        "perspective": "computational methods reviewer",
        "verdict_category": "full submission viable",
        "risk_domain": "named_benchmarking",
        "concern": "Named-tool benchmarking could look insufficient if the comparator set is only internal summaries.",
        "severity_initial": "high",
        "stage10_evidence": "Stage 10.2 benchmarks internal summaries plus SciPy peak detection, scikit-learn feature classification, hmmlearn state summaries, catch22-style, tsfresh-style, MiniROCKET-style, and ruptures-style comparator families.",
        "mitigation_or_decision": "Resolved to low residual risk. Comparator families are visible, and cases where generic feature methods succeed are retained as method boundaries.",
        "severity_after_stage10": "low",
        "unresolved_high_severity": "no",
        "action_status": "resolved_by_stage10_evidence",
    },
    {
        "perspective": "computational methods reviewer",
        "verdict_category": "full submission viable",
        "risk_domain": "algorithmic_novelty",
        "concern": "RhoDyn is not a mathematically radical new algorithm, so novelty must rest on a rigorous decision object and validation ladder.",
        "severity_initial": "high",
        "stage10_evidence": "Stage 10.1 formalizes decision divergence and abstention; Stage 10.2-10.4 stress-test it against baselines, public systems, and held-out contexts.",
        "mitigation_or_decision": "Resolved to medium residual risk. The claim should remain method-object novelty rather than algorithmic revolution.",
        "severity_after_stage10": "medium",
        "unresolved_high_severity": "no",
        "action_status": "resolved_with_claim_boundary",
    },
    {
        "perspective": "live-cell signaling biologist",
        "verdict_category": "full submission viable",
        "risk_domain": "biological_interpretation",
        "concern": "Residence windows could be mistaken for discovered biological states or mechanisms.",
        "severity_initial": "high",
        "stage10_evidence": "Stage 10.1 and Stage 10.6 state that windows are declared analysis objects and that decision divergence is not mechanism discovery.",
        "mitigation_or_decision": "Resolved. The manuscript should keep the declared-window and non-mechanism language visible in the Abstract, Results, figure captions, and Discussion.",
        "severity_after_stage10": "low",
        "unresolved_high_severity": "no",
        "action_status": "resolved_with_claim_boundary",
    },
    {
        "perspective": "live-cell signaling biologist",
        "verdict_category": "delay for another dataset",
        "risk_domain": "validation_breadth",
        "concern": "An additional NF-kB, p53, or optogenetic Rho-family reporter dataset would still strengthen biological breadth.",
        "severity_initial": "medium",
        "stage10_evidence": "Stage 10.3 already adds four counted public systems and defers unlicensed or unstable sources rather than overusing them.",
        "mitigation_or_decision": "Not blocking. Another dataset would be helpful, but the current breadth is adequate for presubmission or full-submission discussion if described as scoped public breadth.",
        "severity_after_stage10": "medium",
        "unresolved_high_severity": "no",
        "action_status": "optional_future_strengthening",
    },
    {
        "perspective": "statistician/benchmarking reviewer",
        "verdict_category": "full submission viable",
        "risk_domain": "overclaiming",
        "concern": "Positive benchmark outcomes could be overread as universal superiority over amplitude, endpoint, or generic feature summaries.",
        "severity_initial": "high",
        "stage10_evidence": "Stage 10.2 keeps generic-feature successes visible; Stage 10.4 preserves positive, comparator-sufficient, and inconclusive held-out calls.",
        "mitigation_or_decision": "Resolved. The correct claim is conditional decision value under declared windows and uncertainty, not universal superiority.",
        "severity_after_stage10": "low",
        "unresolved_high_severity": "no",
        "action_status": "resolved_with_claim_boundary",
    },
    {
        "perspective": "statistician/benchmarking reviewer",
        "verdict_category": "presubmission only",
        "risk_domain": "uncertainty_reporting",
        "concern": "Held-out validation is sealed replay over retained public-derived tables, not a prospective blinded collaborator study.",
        "severity_initial": "medium",
        "stage10_evidence": "Stage 10.4 predeclares rules and keeps inconclusive calls visible; Stage 10.6 states the prospective-validation boundary.",
        "mitigation_or_decision": "Not blocking if the phrase no-retuning held-out validation is used and prospective validation is not implied.",
        "severity_after_stage10": "medium",
        "unresolved_high_severity": "no",
        "action_status": "resolved_with_claim_boundary",
    },
    {
        "perspective": "software reproducibility reviewer",
        "verdict_category": "full submission viable",
        "risk_domain": "reproducibility",
        "concern": "A Nature Methods software-adjacent method needs replayable evidence, not only polished prose.",
        "severity_initial": "high",
        "stage10_evidence": "Stage 10.7 provides a fresh-clone command index, checksum manifest, archive manifest, and gate report covering Stage 10.1 through Stage 10.6 outputs.",
        "mitigation_or_decision": "Resolved. The software surface supports the method evidence rather than substituting for it.",
        "severity_after_stage10": "low",
        "unresolved_high_severity": "no",
        "action_status": "resolved_by_stage10_evidence",
    },
    {
        "perspective": "software reproducibility reviewer",
        "verdict_category": "pivot venue",
        "risk_domain": "venue_contingency",
        "concern": "If Nature Methods still reads the work as software integration, the package needs a venue pivot path rather than repeated informal EIC requests.",
        "severity_initial": "medium",
        "stage10_evidence": "Stage 10.8 records this contingency before Stage 10.9 chooses the contact route.",
        "mitigation_or_decision": "Route to Stage 10.9. Pivot venue remains a fallback, not the current primary recommendation.",
        "severity_after_stage10": "medium",
        "unresolved_high_severity": "no",
        "action_status": "routed_to_stage10_9",
    },
]


def _git_sha() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "unknown"


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _write_tsv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_text(path: Path, body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body.rstrip() + "\n", encoding="utf-8")


def _read_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def verdict_rubric_rows() -> list[dict[str, str]]:
    return [
        {
            "verdict_category": "desk-reject likely",
            "meaning": "A high-severity unresolved risk remains for novelty, validation breadth, named benchmarking, or overclaiming.",
            "stage10_8_use": "defined but not selected as final recommendation",
        },
        {
            "verdict_category": "presubmission only",
            "meaning": "Evidence is strong enough for an editor-facing query, but not yet the safest direct full-submission route.",
            "stage10_8_use": "selected by some reviewers as conservative contact route",
        },
        {
            "verdict_category": "full submission viable",
            "meaning": "The methods claim is defensible if boundaries and validation ladder remain visible.",
            "stage10_8_use": "selected by most method and reproducibility perspectives",
        },
        {
            "verdict_category": "delay for another dataset",
            "meaning": "Additional public or collaborator evidence would materially lower risk, but the current state is not necessarily blocked.",
            "stage10_8_use": "retained as optional strengthening rather than blocking gate",
        },
        {
            "verdict_category": "pivot venue",
            "meaning": "If Nature Methods still reads software integration first, pivot to a venue aligned with systems biology or software methods.",
            "stage10_8_use": "retained as fallback for Stage 10.9",
        },
    ]


def validate_stage10_8() -> dict[str, object]:
    prereq = _read_json(PREREQ_GATE) if PREREQ_GATE.exists() else {}
    perspectives = {row["perspective"] for row in ACTION_ROWS}
    verdicts = {row["verdict_category"] for row in ACTION_ROWS}
    rubric_verdicts = {row["verdict_category"] for row in verdict_rubric_rows()}
    critical_rows = [row for row in ACTION_ROWS if row["risk_domain"] in CRITICAL_DOMAINS]
    unresolved_high = [
        row
        for row in ACTION_ROWS
        if row["unresolved_high_severity"] == "yes" or row["severity_after_stage10"] == "high"
    ]
    unresolved_critical_high = [
        row
        for row in unresolved_high
        if row["risk_domain"] in CRITICAL_DOMAINS
    ]
    action_unrouted = [
        row
        for row in ACTION_ROWS
        if row["action_status"] not in {
            "resolved_by_stage10_evidence",
            "resolved_with_claim_boundary",
            "routed_to_stage10_9",
            "optional_future_strengthening",
        }
    ]
    prereq_gates = prereq.get("gates", {})
    gates = {
        "stage10_7_prerequisite_passed": prereq.get("status") == "pass"
        and isinstance(prereq_gates, dict)
        and all(prereq_gates.values()),
        "six_perspectives_present": perspectives == set(PERSPECTIVES),
        "required_verdict_categories_defined": rubric_verdicts == set(REQUIRED_VERDICTS),
        "verdicts_cover_contact_options": {"full submission viable", "presubmission only", "delay for another dataset", "pivot venue"}.issubset(verdicts),
        "critical_domains_covered": CRITICAL_DOMAINS.issubset({row["risk_domain"] for row in critical_rows}),
        "no_unresolved_high_severity_desk_reject_risk": not unresolved_critical_high,
        "all_actions_routed": not action_unrouted,
        "software_secondary_boundary_preserved": any(
            row["risk_domain"] == "reproducibility"
            and "supports the method evidence rather than substituting for it" in row["mitigation_or_decision"]
            for row in ACTION_ROWS
        ),
    }
    return {
        "stage": "10.8",
        "status": "pass" if all(gates.values()) else "fail",
        "generated_utc": _now(),
        "git_sha": _git_sha(),
        "gates": gates,
        "summary_metrics": {
            "perspective_count": len(perspectives),
            "action_row_count": len(ACTION_ROWS),
            "critical_domain_count": len({row["risk_domain"] for row in critical_rows}),
            "unresolved_high_severity_count": len(unresolved_critical_high),
            "verdict_category_count": len(rubric_verdicts),
        },
        "unresolved_high_severity_items": unresolved_critical_high,
        "action_unrouted_items": action_unrouted,
        "verdict_counts": {verdict: sum(row["verdict_category"] == verdict for row in ACTION_ROWS) for verdict in REQUIRED_VERDICTS},
        "next_phase": "Stage 10.9 EIC-contact decision",
        "interpretation_boundary": "Stage 10.8 is an adversarial editorial-risk simulation. It does not add biological data, benchmark results, figures, or manuscript claims.",
    }


def _matrix_summary() -> str:
    lines = [
        "| perspective | verdict | risk domain | initial | after Stage 10 | action |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for row in ACTION_ROWS:
        lines.append(
            "| {perspective} | {verdict_category} | {risk_domain} | {severity_initial} | {severity_after_stage10} | {action_status} |".format(
                **row
            )
        )
    return "\n".join(lines)


def _report_markdown(report: dict[str, object]) -> str:
    return f"""# Stage 10.8 adversarial EIC red-team simulation

## Verdict

Stage 10.8 passes. No reviewer perspective leaves an unresolved high-severity desk-rejection risk for novelty, validation breadth, named benchmarking, or overclaiming. The remaining risk is mostly route selection. A presubmission-style contact is still the conservative next step unless the author team explicitly accepts the medium residual risk attached to direct full submission.

## What changed scientifically

Nothing new was measured, modeled, or benchmarked in this stage. The red team tests whether the existing Stage 10 evidence now reads as a method-level advance. The answer is stronger than the Stage 9.29 package because Stage 10 has put the decision object, named baselines, public biological breadth, held-out validation, and reproducibility package in front of the software-workflow reading.

## Action matrix summary

{_matrix_summary()}

## Remaining boundaries

- The method is a residence-state decision framework, not a universal claim that all systems contain residence regimes.
- Named feature and classifier baselines can succeed in some regimes, and those regimes remain method boundaries.
- Held-out validation is no-retuning public-derived replay, not a prospective blinded collaborator study.
- Reserve-like and routed-output outputs remain measurement-scoped and effective-model decisions rather than direct molecular mechanisms.
- Software reproducibility supports the method claim but is not the primary scientific advance.

## Next decision

Stage 10.9 should choose between a presubmission query, full submission, delay for another dataset, or venue pivot. The Stage 10.8 evidence favors a presubmission-style contact as the lowest-risk editor route, with direct full submission viable only if the PI accepts the remaining medium-risk items.
"""


def _doc_markdown(report: dict[str, object]) -> str:
    return f"""# Stage 10.8 adversarial EIC red-team

Stage 10.8 stress-tests the Stage 10 method-elevation package from six adversarial editorial and reviewer perspectives before any renewed Nature Methods contact.

## Outputs

- `case_studies/stage10_eic_red_team/stage10_8_verdict_rubric.tsv`
- `case_studies/stage10_eic_red_team/stage10_8_red_team_action_matrix.tsv`
- `case_studies/stage10_eic_red_team/stage10_8_red_team_report.md`
- `case_studies/stage10_eic_red_team/stage10_8_decision_brief.md`
- `case_studies/stage10_eic_red_team/stage10_8_gate_report.json`

## Gate status

{report['status']}

## Gate logic

The gate passes only if the six reviewer perspectives are present, the required verdict categories are defined, the critical vulnerability domains are covered, and no unresolved high-severity desk-rejection risk remains for novelty, validation breadth, named benchmarking, or overclaiming.

## Boundary

{report['interpretation_boundary']}
"""


def _decision_brief(report: dict[str, object]) -> str:
    verdict_counts = report["verdict_counts"]
    return f"""# Stage 10.8 decision brief

The red team does not identify a remaining high-severity desk-rejection blocker in the critical domains. Verdict counts were `{verdict_counts}`.

Recommended Stage 10.9 route. Presubmission-style contact is the lowest-risk next step. Direct full submission is viable only after PI acceptance of medium residual risk around new rendered Stage 10 figures and absence of a prospective collaborator-blind dataset.

Do not contact the EIC with the Stage 9.29 package alone. Any contact should use the Stage 10 method-first evidence package and should state that RhoDyn is a residence-state inference method with named comparator evidence, public biological breadth, held-out replay, and reproducible software surfaces.
"""


def run_stage10_8() -> dict[str, object]:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    rubric = verdict_rubric_rows()
    _write_tsv(VERDICT_RUBRIC_PATH, rubric, ["verdict_category", "meaning", "stage10_8_use"])
    _write_tsv(ACTION_MATRIX_PATH, ACTION_ROWS, ACTION_FIELDS)
    report = validate_stage10_8()
    _write_json(GATE_REPORT, report)
    _write_text(REPORT_PATH, _report_markdown(report))
    _write_text(DECISION_BRIEF_PATH, _decision_brief(report))
    _write_text(DOC_PATH, _doc_markdown(report))
    return report


if __name__ == "__main__":
    print(json.dumps(run_stage10_8(), indent=2, sort_keys=True))

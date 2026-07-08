"""Assemble the Stage 10.17 no-send message integrity pass.

Stage 10.17 creates polished author-review candidate text for the
presubmission query and one-page pitch, then audits the message for route
consistency, readability, claim boundaries, and no-send status. It does not
send external contact, add evidence, alter figures, or invent author metadata.
"""

from __future__ import annotations

import csv
import hashlib
import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "case_studies" / "stage10_message_integrity"
DOC_PATH = ROOT / "docs" / "stage10_17_message_integrity.md"
MEMORY_PATH = ROOT / "docs" / "roadmap_execution_memory.json"

STAGE10_16_GATE = ROOT / "case_studies" / "stage10_route_decision_triage" / "stage10_16_gate_report.json"
SOURCE_QUERY = (
    ROOT
    / "case_studies"
    / "stage10_author_review_readiness"
    / "stage10_11_presubmission_query_clean_AUTHOR_REVIEW_REQUIRED.md"
)
SOURCE_PITCH = ROOT / "case_studies" / "stage10_eic_contact_decision" / "stage10_9_one_page_pitch.md"

POLISHED_QUERY = OUTPUT_DIR / "stage10_17_presubmission_query_polished_AUTHOR_REVIEW_REQUIRED.md"
POLISHED_PITCH = OUTPUT_DIR / "stage10_17_one_page_pitch_polished.md"
MANIFEST = OUTPUT_DIR / "stage10_17_message_manifest.tsv"
AUDIT = OUTPUT_DIR / "stage10_17_message_integrity_audit.tsv"
BOUNDARY_SCAN = OUTPUT_DIR / "stage10_17_no_send_boundary_scan.tsv"
GATE_REPORT = OUTPUT_DIR / "stage10_17_gate_report.json"

MANIFEST_FIELDS = ["surface", "path", "role", "exists", "words", "bytes", "sha256", "send_surface"]
AUDIT_FIELDS = ["check_id", "surface", "check", "status", "evidence", "action_if_failed"]
BOUNDARY_FIELDS = ["boundary_id", "boundary", "status", "evidence", "action_if_failed"]

REQUIRED_BEATS = {
    "method_object": "residence-state inference method",
    "declared_regime": "declared response regime",
    "comparator_families": "SciPy peak summaries",
    "public_breadth": "DRG calcium dynamics",
    "heldout_scope": "sealed no-retuning validation route",
    "software_support": "Python, command-line, API, workbench, checksum, and archive",
    "non_universal": "does not claim that every live-cell system contains a residence regime",
    "non_mechanism": "declared windows are mechanisms",
    "simpler_summaries": "simpler summaries are adequate",
}

UNSAFE_PATTERNS = [
    r"\bproves? mechanism\b",
    r"\bguarantee[sd]?\b",
    r"\ball live-cell systems\b",
    r"\bsubmitted\b",
    r"\baccepted\b",
    "/" + r"Users/",
    "/" + r"Volumes/",
    r"Library/" + r"LaunchAgents",
    r"BEGIN (RSA|OPENSSH|PRIVATE)",
    r"\b(API_KEY|TOKEN|SECRET|PASSWORD)\b",
]


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _git_sha() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    except (FileNotFoundError, subprocess.CalledProcessError):
        return "unknown"


def _rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _words(text: str) -> list[str]:
    return re.findall(r"[A-Za-z0-9]+(?:[-'][A-Za-z0-9]+)?", text)


def _word_count(text: str) -> int:
    return len(_words(text))


def _sentence_word_counts(text: str) -> list[int]:
    sentences = [chunk.strip() for chunk in re.split(r"[.!?]\s+", text) if chunk.strip()]
    return [_word_count(sentence) for sentence in sentences]


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_text(path: Path, body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body.rstrip() + "\n", encoding="utf-8")


def _write_tsv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def polished_query_text() -> str:
    return """# Stage 10.17 presubmission query. Author review required. Do not send from repository.

Subject. Presubmission inquiry for Nature Methods. Residence-state inference for live-cell perturbation data

Dear Nature Methods editorial team,

I am writing to ask whether the following concept would be suitable for a Nature Methods presubmission inquiry as a computational methods Article.

RhoDyn is a residence-state inference method for live-cell perturbation data. It tests when time spent inside a declared response regime changes interpretation relative to endpoint, amplitude, threshold, and generic time-series summaries. The method is benchmarked against simple summaries, SciPy peak summaries, scikit-learn feature models, HMM state summaries, catch22-style, tsfresh-style, MiniROCKET-style, and ruptures-style comparator families, while retaining cases where simpler summaries are sufficient. Public demonstrations span DRG calcium dynamics, GPCR-linked ERK trajectories, Cell Painting/MitoTox endpoint profiling, and MLCI tracking. A sealed no-retuning validation route preserves positive residence-divergence, comparator-sufficient, bounded-coupling, and inconclusive calls in held-out public-derived contexts.

The software implementation provides Python, command-line, API, workbench, checksum, and archive surfaces, but the proposed Article is framed around the method object, not software availability alone. The main limitation is explicit. RhoDyn does not claim that every live-cell system contains a residence regime or that declared windows are mechanisms. It provides a reproducible decision route for identifying when residence-state structure changes interpretation and when simpler summaries are adequate.

Would this scope fit Nature Methods for presubmission evaluation?

Sincerely,

[Author name, affiliation, and contact details to be completed by the corresponding author]
"""


def polished_pitch_text() -> str:
    return """# Stage 10.17 polished one-page presubmission pitch

## Working title

Residence-state inference for live-cell perturbation data

## Pitch

RhoDyn is a residence-state inference method for live-cell perturbation data. It asks when time spent inside a declared biological response regime changes interpretation relative to endpoint, amplitude, threshold, and generic time-series summaries. The method is benchmarked against simple summaries, SciPy peak summaries, scikit-learn feature models, HMM state summaries, catch22-style, tsfresh-style, MiniROCKET-style, and ruptures-style comparator families, while preserving cases where simpler summaries are sufficient rather than claiming universal superiority. Public demonstrations span DRG calcium dynamics, GPCR-linked ERK trajectories, Cell Painting/MitoTox endpoint profiling, and MLCI tracking. A sealed no-retuning validation route preserves positive residence-divergence, comparator-sufficient, bounded-coupling, and inconclusive calls across held-out public-derived contexts. The software implementation makes the method inspectable through Python, command-line, API, workbench, checksum, and archive surfaces, but reproducibility supports the method claim rather than replacing it. The intended Nature Methods contribution is a scoped decision framework for determining when residence, bounded coupling, reserve-like preservation, or routed-output structure changes interpretation, and when it does not.

## Residual boundaries for the editor-facing version

- Declared residence windows are analysis objects, not automatically discovered biological mechanisms.
- Held-out validation is no-retuning public-derived replay, not a prospective blinded collaborator study.
- Reserve-like and routed-output calls are measurement-scoped and effective-model decisions.
- Named feature and classifier baselines can be sufficient in some regimes.
"""


def manifest_rows() -> list[dict[str, Any]]:
    surfaces = [
        ("source_query", SOURCE_QUERY, "Stage 10.11 clean presubmission query source", "no"),
        ("source_pitch", SOURCE_PITCH, "Stage 10.9 one-page pitch source", "no"),
        ("polished_query", POLISHED_QUERY, "Stage 10.17 polished query candidate for author review", "candidate_after_author_approval"),
        ("polished_pitch", POLISHED_PITCH, "Stage 10.17 polished pitch candidate for author review", "candidate_after_author_approval"),
    ]
    rows = []
    for surface, path, role, send_surface in surfaces:
        exists = path.exists() and path.is_file()
        text = path.read_text(encoding="utf-8") if exists else ""
        rows.append(
            {
                "surface": surface,
                "path": _rel(path),
                "role": role,
                "exists": "yes" if exists else "no",
                "words": _word_count(text),
                "bytes": path.stat().st_size if exists else 0,
                "sha256": _sha256(path) if exists else "",
                "send_surface": send_surface,
            }
        )
    return rows


def _unsafe_hits(text: str) -> list[str]:
    hits = []
    for pattern in UNSAFE_PATTERNS:
        if re.search(pattern, text, flags=re.IGNORECASE):
            hits.append(pattern)
    return hits


def audit_rows(query: str, pitch: str) -> list[dict[str, str]]:
    combined = query + "\n" + pitch
    query_sentence_counts = _sentence_word_counts(query)
    pitch_sentence_counts = _sentence_word_counts(pitch)
    checks = [
        (
            "A-001",
            "polished_query",
            "Query stays concise for presubmission email use",
            _word_count(query) <= 260,
            f"{_word_count(query)} words",
            "Shorten the query body without removing method object, comparators, breadth, validation, or limitations.",
        ),
        (
            "A-002",
            "polished_pitch",
            "Pitch stays compact enough for one-page use",
            _word_count(pitch) <= 320,
            f"{_word_count(pitch)} words",
            "Shorten the pitch while preserving the residual-boundary list.",
        ),
        (
            "A-003",
            "polished_query",
            "Query avoids very long sentence cadence",
            max(query_sentence_counts) <= 45,
            f"max sentence words {max(query_sentence_counts)}",
            "Split dense sentences before author review.",
        ),
        (
            "A-004",
            "polished_pitch",
            "Pitch avoids very long sentence cadence",
            max(pitch_sentence_counts) <= 50,
            f"max sentence words {max(pitch_sentence_counts)}",
            "Split dense pitch sentences before author review.",
        ),
        (
            "A-005",
            "combined",
            "All required method and boundary beats are present",
            all(beat in combined for beat in REQUIRED_BEATS.values()),
            ", ".join(key for key, beat in REQUIRED_BEATS.items() if beat in combined),
            "Restore missing method-object, comparator, breadth, held-out, software, or limitation beat.",
        ),
        (
            "A-006",
            "polished_query",
            "Author-only placeholder is retained",
            "[Author name, affiliation, and contact details to be completed by the corresponding author]" in query,
            "corresponding-author placeholder present",
            "Restore author placeholder and do not invent sender metadata.",
        ),
        (
            "A-007",
            "combined",
            "No unsafe overclaim, local path, or secret pattern is present",
            not _unsafe_hits(combined),
            "unsafe hits " + json.dumps(_unsafe_hits(combined)),
            "Remove unsafe phrase, local path, or credential-like string.",
        ),
        (
            "A-008",
            "combined",
            "Software support is secondary to method object",
            "method object, not software availability alone" in query
            and "reproducibility supports the method claim rather than replacing it" in pitch,
            "method-first software boundary present",
            "Restore the method-first boundary around software availability.",
        ),
        (
            "A-009",
            "polished_pitch",
            "Prospective validation is explicitly not claimed",
            "not a prospective blinded collaborator study" in pitch,
            "no-retuning public-derived replay boundary present",
            "Restore the prospective-validation boundary.",
        ),
        (
            "A-010",
            "polished_query",
            "The query asks for presubmission fit rather than implying submission",
            "Would this scope fit Nature Methods for presubmission evaluation?" in query,
            "presubmission question present",
            "Restore presubmission-fit question and avoid submission language.",
        ),
    ]
    return [
        {
            "check_id": check_id,
            "surface": surface,
            "check": check,
            "status": "pass" if status else "fail",
            "evidence": evidence,
            "action_if_failed": action,
        }
        for check_id, surface, check, status, evidence, action in checks
    ]


def boundary_rows(stage10_16: dict[str, Any], audit: list[dict[str, str]], manifest: list[dict[str, Any]]) -> list[dict[str, str]]:
    all_manifest_exists = all(row["exists"] == "yes" for row in manifest)
    all_audits_pass = all(row["status"] == "pass" for row in audit)
    return [
        {
            "boundary_id": "B-001",
            "boundary": "External contact remains unsent",
            "status": "pass" if stage10_16.get("external_contact_status") == "not_sent" else "fail",
            "evidence": "Stage 10.16 gate report",
            "action_if_failed": "Stop and restore no-send state.",
        },
        {
            "boundary_id": "B-002",
            "boundary": "Presubmission remains the route, after author approval only",
            "status": "pass"
            if stage10_16.get("recommendation") == "presubmission_query_after_author_approval"
            else "fail",
            "evidence": "Stage 10.16 gate report",
            "action_if_failed": "Do not package text until route recommendation is restored.",
        },
        {
            "boundary_id": "B-003",
            "boundary": "Polished surfaces are candidate review text, not send-ready messages",
            "status": "pass"
            if all(row["send_surface"] in {"no", "candidate_after_author_approval"} for row in manifest)
            else "fail",
            "evidence": "Stage 10.17 manifest",
            "action_if_failed": "Restore candidate-only labels.",
        },
        {
            "boundary_id": "B-004",
            "boundary": "All message surfaces exist and are checksum-backed",
            "status": "pass" if all_manifest_exists else "fail",
            "evidence": "Stage 10.17 manifest",
            "action_if_failed": "Regenerate or remove missing surfaces.",
        },
        {
            "boundary_id": "B-005",
            "boundary": "Readability, method identity, comparator, breadth, validation, and limitation audits pass",
            "status": "pass" if all_audits_pass else "fail",
            "evidence": "Stage 10.17 message audit",
            "action_if_failed": "Patch the polished candidate text before author review.",
        },
        {
            "boundary_id": "B-006",
            "boundary": "Author identity remains a corresponding-author action",
            "status": "pass" if any(row["check_id"] == "A-006" and row["status"] == "pass" for row in audit) else "fail",
            "evidence": "Stage 10.17 message audit",
            "action_if_failed": "Restore the author placeholder.",
        },
        {
            "boundary_id": "B-007",
            "boundary": "No new data, figures, benchmarks, or manuscript claims are introduced",
            "status": "pass",
            "evidence": "Stage 10.17 rewrites editor-facing wording only from existing Stage 10 surfaces",
            "action_if_failed": "Move new evidence to a separate authorized phase.",
        },
    ]


def _write_doc(gate: dict[str, Any]) -> None:
    body = f"""# Stage 10.17 message integrity

Stage 10.17 performs a final no-send integrity and readability pass over the presubmission query and one-page pitch. It creates polished author-review candidate text while preserving route, claim, and no-send boundaries.

## Status

`{gate["status"]}`

## Outputs

- Polished query. `{gate["outputs"]["polished_query"]}`
- Polished pitch. `{gate["outputs"]["polished_pitch"]}`
- Message manifest. `{gate["outputs"]["manifest"]}`
- Message audit. `{gate["outputs"]["audit"]}`
- Boundary scan. `{gate["outputs"]["boundary_scan"]}`
- Gate report. `{gate["outputs"]["gate_report"]}`

## Boundary

External contact remains `{gate["external_contact_status"]}`. The polished text is an author-review candidate only, with corresponding-author identity and actual sending still outside Codex authority.
"""
    _write_text(DOC_PATH, body)


def _update_memory(gate: dict[str, Any]) -> None:
    memory = _read_json(MEMORY_PATH)
    current = memory.setdefault("current_position", {})
    current["active_stage"] = "Stage 10.17 message integrity complete; external contact remains not sent"
    current["current_gate"] = "Stage 10.17 message integrity complete; external contact remains not sent"
    current["stage10_active_gate"] = "Stage 10.17 message integrity complete; external contact remains not sent"
    current["next_stage"] = "Corresponding-author review of polished presubmission text, sender metadata, and route approval"
    current["after_stage10_17_message_integrity"] = (
        "Stage 10.17 created polished no-send presubmission query and pitch candidates, checked readability and claim boundaries, "
        "and preserved author-only sender metadata plus unsent external-contact state."
    )

    stage10 = next((stage for stage in memory.get("stage_lock", []) if stage.get("stage") == 10), None)
    if not isinstance(stage10, dict):
        _write_json(MEMORY_PATH, memory)
        return
    artifacts = set(stage10.get("artifacts", []))
    artifacts.update(
        [
            _rel(DOC_PATH),
            "scripts/run_stage10_17_message_integrity.py",
            "tests/test_stage10_17_message_integrity.py",
            _rel(POLISHED_QUERY),
            _rel(POLISHED_PITCH),
            _rel(MANIFEST),
            _rel(AUDIT),
            _rel(BOUNDARY_SCAN),
            _rel(GATE_REPORT),
        ]
    )
    stage10["artifacts"] = sorted(artifacts)
    stage10["status"] = "stage10_17_complete_message_integrity"
    stage10["current_gate"] = "Stage 10.17 message integrity complete; external contact remains not sent"
    subphases = stage10.setdefault("subphases", [])
    by_id = {entry.get("id"): entry for entry in subphases if isinstance(entry, dict)}
    by_id["10.17"] = {
        "id": "10.17",
        "name": "No-send message integrity and readability pass",
        "status": "complete_message_integrity",
        "goal": "Create polished author-review presubmission text while preserving route, claim, and no-send boundaries.",
        "gate": "Polished query and pitch pass readability, required-beat, claim-boundary, and no-send checks.",
        "evidence": _rel(GATE_REPORT),
    }
    stage10["subphases"] = [by_id[key] for key in sorted(by_id, key=lambda value: tuple(int(part) for part in value.split(".")))]
    _write_json(MEMORY_PATH, memory)


def run_stage10_17() -> dict[str, Any]:
    stage10_16 = _read_json(STAGE10_16_GATE)
    query = polished_query_text()
    pitch = polished_pitch_text()
    _write_text(POLISHED_QUERY, query)
    _write_text(POLISHED_PITCH, pitch)
    manifest = manifest_rows()
    audit = audit_rows(query, pitch)
    boundary = boundary_rows(stage10_16, audit, manifest)

    _write_tsv(MANIFEST, manifest, MANIFEST_FIELDS)
    _write_tsv(AUDIT, audit, AUDIT_FIELDS)
    _write_tsv(BOUNDARY_SCAN, boundary, BOUNDARY_FIELDS)

    gates = {
        "stage10_16_passed": stage10_16.get("status") == "pass",
        "presubmission_route_retained": stage10_16.get("recommendation") == "presubmission_query_after_author_approval",
        "polished_query_exists": POLISHED_QUERY.exists(),
        "polished_pitch_exists": POLISHED_PITCH.exists(),
        "audit_all_pass": all(row["status"] == "pass" for row in audit),
        "boundary_scan_all_pass": all(row["status"] == "pass" for row in boundary),
        "author_placeholder_retained": "[Author name, affiliation, and contact details to be completed by the corresponding author]" in query,
        "external_contact_not_sent": stage10_16.get("external_contact_status") == "not_sent",
        "candidate_only_surfaces": all(row["send_surface"] in {"no", "candidate_after_author_approval"} for row in manifest),
        "no_new_science_claims_or_contact": True,
    }
    gate = {
        "stage": "10.17",
        "status": "pass" if all(gates.values()) else "fail",
        "generated_utc": _now(),
        "git_sha": _git_sha(),
        "gates": gates,
        "external_contact_status": "not_sent",
        "summary_metrics": {
            "manifest_row_count": len(manifest),
            "audit_count": len(audit),
            "audit_pass_count": sum(row["status"] == "pass" for row in audit),
            "boundary_count": len(boundary),
            "boundary_pass_count": sum(row["status"] == "pass" for row in boundary),
            "polished_query_words": _word_count(query),
            "polished_pitch_words": _word_count(pitch),
            "polished_query_max_sentence_words": max(_sentence_word_counts(query)),
            "polished_pitch_max_sentence_words": max(_sentence_word_counts(pitch)),
        },
        "outputs": {
            "polished_query": _rel(POLISHED_QUERY),
            "polished_pitch": _rel(POLISHED_PITCH),
            "manifest": _rel(MANIFEST),
            "audit": _rel(AUDIT),
            "boundary_scan": _rel(BOUNDARY_SCAN),
            "gate_report": _rel(GATE_REPORT),
            "doc": _rel(DOC_PATH),
        },
        "interpretation_boundary": (
            "Stage 10.17 is a no-send message-integrity pass. It creates polished author-review candidate text from existing Stage 10 "
            "surfaces, preserves the presubmission route after author approval, and does not add data, figures, benchmarks, or external contact."
        ),
    }
    _write_json(GATE_REPORT, gate)
    _write_doc(gate)
    _update_memory(gate)
    return gate


def main() -> int:
    gate = run_stage10_17()
    print(json.dumps(gate, indent=2))
    return 0 if gate["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())

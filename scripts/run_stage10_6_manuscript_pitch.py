"""Build the Stage 10.6 method-first manuscript and pitch transformation.

Stage 10.6 turns the Stage 10.5 figure architecture into reader-facing
manuscript surfaces. It does not add evidence, rerender figures, or replace the
closed Stage 9 submission package. The outputs are the Stage 10 rescue draft
surfaces that should control the next manuscript/pitch rebuild.
"""

from __future__ import annotations

import csv
import json
import re
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STAGE_DIR = ROOT / "manuscript" / "nature_methods" / "stage10_6"
OUTPUT_DIR = ROOT / "case_studies" / "stage10_manuscript_pitch"
FIGURE_CROSSWALK = ROOT / "manuscript" / "nature_methods" / "figures" / "stage10_5_panel_evidence_crosswalk.csv"
STAGE10_5_GATE = ROOT / "case_studies" / "stage10_figure_architecture" / "stage10_5_gate_report.json"
DOC_PATH = ROOT / "docs" / "stage10_6_manuscript_pitch_transformation.md"
GATE_REPORT = OUTPUT_DIR / "stage10_6_gate_report.json"
BRIEF_PATH = OUTPUT_DIR / "stage10_6_manuscript_pitch_brief.md"

TITLE = "Residence-state inference for live-cell perturbation data"
DECK = (
    "RhoDyn formalizes dwell, coupling, reserve-like endpoint, and routed-output decisions "
    "against named baselines across public systems and held-out contexts."
)

ABSTRACT = (
    "Live-cell perturbation datasets are often interpreted through endpoints, peaks, amplitudes, thresholds, "
    "or generic time-series features, leaving unclear when time spent inside a biologically declared response "
    "regime changes the state assignment. We introduce RhoDyn, a residence-state inference method that represents "
    "trajectories and endpoint perturbation tables as explicit decision objects. RhoDyn compares dwell fraction, "
    "dwell time, segment count, and amplitude summaries, evaluates bounded reporter coupling under declared margins, "
    "constructs measurement-scoped reserve-like endpoint coordinates, tests routed-output alternatives against "
    "reduced architectures, and withholds calls when uncertainty or input structure is insufficient. In known-truth "
    "synthetic regimes, RhoDyn separates residence-positive, amplitude-sufficient, and ambiguous cases while named "
    "baseline families, including simple summaries, SciPy peak summaries, scikit-learn feature models, HMM state "
    "summaries, catch22-style, tsfresh-style, MiniROCKET-style, and ruptures-style comparators, define where simpler "
    "methods succeed. Public demonstrations span DRG calcium, GPCR-linked ERK, Cell Painting/MitoTox endpoints, and "
    "MLCI tracking, with sealed held-out contexts preserving positive, comparator-sufficient, and inconclusive "
    "decisions. RhoDyn is implemented across Python, command-line, API, workbench, and archived release surfaces with "
    "reproducible exports. The method therefore provides a reviewable route for deciding when residence, bounded "
    "coupling, reserve-like preservation, or routed-output structure changes interpretation relative to endpoint and "
    "amplitude summaries, without treating every declared window or fitted parameter as mechanism."
)

INTRO_BRIDGE = (
    "Live-cell experiments now routinely collect the temporal information needed to ask whether a perturbation changes "
    "state by altering signal magnitude, time in a response regime, reporter coupling, endpoint preservation, or output "
    "routing. The limiting step is no longer only data acquisition. It is the absence of a reviewable decision object that "
    "places those alternatives on the same input table, tests them against named baselines, and allows unsupported calls to "
    "remain unresolved. RhoDyn was developed to make that decision object explicit for live-cell perturbation biology."
)

RESULTS_SECTIONS = [
    (
        "RhoDyn defines residence-state inference as a decision object",
        "Figure 1",
        "A method claim must begin with the object being tested, not with a software interface. The Stage 10 method-object display (Fig. 1a-d) defines tidy trajectory, paired-reporter, and endpoint inputs, then links declared biological windows to dwell fraction, dwell time, segment count, amplitude comparators, decision divergence, and abstention. Executable positive, comparator-sufficient, and ambiguous fixtures show that RhoDyn can return a scoped call or withhold one using the same grammar. This first figure establishes the methodological object that later benchmarks and biological demonstrations stress-test.",
    ),
    (
        "Named baselines define when residence-state inference adds value",
        "Figure 2",
        "The next question is whether that decision object adds information beyond existing summary families. Known-truth benchmark regimes (Fig. 2a) separate residence-positive, amplitude-sufficient, and ambiguous cases before any biological example is used. Named comparator families (Fig. 2b), including simple summaries, SciPy peak summaries, scikit-learn feature models, HMM state summaries, catch22-style, tsfresh-style, MiniROCKET-style, and ruptures-style comparators, make the benchmark explicit rather than self-referential. Accuracy and boundary outcomes (Fig. 2c) then show where RhoDyn changes interpretation and where generic summaries can be sufficient. Public-input comparator summaries and runtime profiles (Fig. 2d,e) keep the comparison inspectable. The method claim is therefore not that RhoDyn always wins. It is that it defines when residence-state decisions differ from named alternatives and when they do not.",
    ),
    (
        "Public biological breadth tests portability across domains",
        "Figure 3",
        "After synthetic and named-baseline stress tests, the decisive breadth question is whether the decision object travels beyond one motivating biology. The public system matrix (Fig. 3a) records four counted independent public systems across live-cell calcium, GPCR-linked kinase signaling, endpoint morphology and cell-health profiling, and microbial tracking. DRG calcium trajectories (Fig. 3b) and ERK GPCR trajectories (Fig. 3c) test residence-amplitude behavior in independent reporter contexts. Cell Painting/MitoTox endpoint rows (Fig. 3d) test whether endpoint perturbation data can enter reduced-architecture and reserve-like analyses without being mislabeled as trajectories. MLCI tracking (Fig. 3e) provides a non-molecular trajectory stress test for schema portability, while source-eligibility records (Fig. 3f) keep deferred datasets out of counted evidence when license support is insufficient. The breadth result is deliberately scoped. It shows portability across public systems and domains, not that every system contains residence-state structure.",
    ),
    (
        "Endpoint and routed-output decisions extend the method beyond trajectories",
        "Figure 4",
        "Many perturbation studies produce endpoint or paired-reporter data rather than dense single-reporter trajectories, so the method must also define how those inputs can support constrained decisions. The endpoint schema and contrast contract (Fig. 4a) declares grouping, contrasts, margins, and readouts before interpretation. Bounded-coupling decisions (Fig. 4b) distinguish pass, fail, and inconclusive interval outcomes under declared margins rather than treating non-significance as equivalence. Reserve-like endpoint coordinates (Fig. 4c) remain tied to measured endpoint preservation, and routed-output model comparisons (Fig. 4d) test reduced alternatives without converting effective parameters into biochemical edges. Measurement-scope limits (Fig. 4e) make those boundaries visible. This extends RhoDyn beyond trajectory residence while preserving the distinction between decision support and mechanism discovery.",
    ),
    (
        "Held-out validation keeps pass, comparator-sufficient, and inconclusive outcomes visible",
        "Figure 5",
        "A method that only reports successes is not yet protected against editorial skepticism. The Stage 10 held-out display therefore begins with predeclared splits, thresholds, and margins (Fig. 5a), then reports positive, comparator-sufficient, and inconclusive held-out outcomes in the same decision table (Fig. 5b). Object-level held-out classifications (Fig. 5c) make the retained trajectory decisions inspectable, while the no-hidden-tuning gate status (Fig. 5d) records whether fixed rules were preserved. The final validation-boundary panel (Fig. 5e) states that sealed public-derived replay is not the same as a future prospective blinded collaborator study. This figure strengthens RhoDyn as a rule-preserving decision method because inconclusive and comparator-sufficient outcomes remain part of the result.",
    ),
    (
        "Reproducible software surfaces make the method inspectable",
        "Figure 6",
        "Only after the method and validation evidence are visible should the software surface carry the argument. Python, command-line, API, and workbench parity (Fig. 6a) show that user-facing routes delegate to the same stable outputs. Export bundles (Fig. 6b), clean-room reproduction (Fig. 6c), archive checksums (Fig. 6d), and user-path rehearsal (Fig. 6e) make decisions reviewable from input schema through report export. These panels support reproducibility and adoption. They are secondary to the method claim, and they should be read as the infrastructure that makes residence-state inference inspectable rather than as the scientific advance by themselves.",
    ),
]

DISCUSSION_LANDING = (
    "The Stage 10 evidence reframes RhoDyn around a testable method object. Its primary contribution is residence-state inference under declared biological windows, named comparator families, uncertainty rules, and explicit abstention, extended to bounded coupling, reserve-like endpoints, and routed-output alternatives. The validation breadth matters because the method produces positive, comparator-sufficient, and inconclusive outcomes across synthetic truth cases, public biological systems, and sealed held-out contexts. The software implementation is essential because it makes those decisions reproducible across Python, command-line, API, workbench, and archive surfaces. It is not the main scientific claim. The appropriate conclusion is that RhoDyn provides a reviewable route for deciding when dynamic operating-state structure changes interpretation relative to endpoint, amplitude, and generic time-series summaries, while preserving the cases where simpler summaries are sufficient or the evidence is unresolved."
)

COVER_LETTER_OPENING = (
    "We submit \"Residence-state inference for live-cell perturbation data\" as a computational methods Article describing RhoDyn, a decision method for asking when time spent inside a declared biological response regime changes interpretation relative to endpoint, amplitude, threshold, and generic time-series summaries. The advance is not that live-cell dynamics matter, and it is not software availability by itself. RhoDyn formalizes a residence-state decision object that combines declared windows, named baseline comparisons, bounded-coupling margins, reserve-like endpoint coordinates, routed-output alternatives, uncertainty, and abstention in one reproducible analysis route."
)

PRESUBMISSION_PITCH = (
    "RhoDyn is a residence-state inference method for live-cell perturbation biology. It addresses the common situation in which time-lapse or endpoint perturbation experiments are interpreted through endpoints, peaks, amplitudes, thresholds, or generic feature summaries even though time spent inside a biologically declared response regime may change the state assignment. The Stage 10 manuscript version leads with the method object, not the software interface: Figure 1 defines the residence-state decision grammar, Figure 2 benchmarks it against named baseline families, Figure 3 tests public biological breadth across four counted systems, Figure 4 extends the decision object to endpoint, bounded-coupling, reserve-like, and routed-output analyses, Figure 5 shows sealed held-out positive, comparator-sufficient, and inconclusive outcomes, and Figure 6 documents reproducible software surfaces. This ordering is intended to make clear that RhoDyn is not a wrapper around existing summaries. It is a reviewable method for deciding when residence-state structure changes interpretation and when it does not."
)

FORBIDDEN_PHRASES = [
    "universal residence",
    "guarantees",
    "proves no coupling",
    "absence of all coupling",
    "automatic state discovery",
    "mechanism-discovery engine",
    "literal biochemical edge",
    "RhoDyn generated the original",
]


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _write_text(path: Path, body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body.rstrip() + "\n", encoding="utf-8")


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str], *, delimiter: str = "\t") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, delimiter=delimiter, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def _word_count(text: str) -> int:
    return len(re.findall(r"\b[\w'-]+\b", text))


def render_title_abstract() -> str:
    return f"""# Stage 10.6 title and abstract route

## Preferred title

{TITLE}

## Deck

{DECK}

## Abstract

{ABSTRACT}

## Why this changes the first read

The Stage 9 title was accurate but still software-name first. The Stage 10.6 title is method-object first. It names residence-state inference and the live-cell perturbation data class directly, while the deck keeps RhoDyn visible as the implementation.
"""


def render_results() -> str:
    lines = ["# Stage 10.6 method-first Results draft", ""]
    for title, fig, body in RESULTS_SECTIONS:
        lines.extend([f"## {title}", "", body, ""])
    return "\n".join(lines).rstrip()


def render_discussion() -> str:
    return f"""# Stage 10.6 Discussion landing

{DISCUSSION_LANDING}
"""


def render_pitch() -> str:
    return f"""# Stage 10.6 EIC-facing pitch v2

## Cover-letter opening

{COVER_LETTER_OPENING}

## Presubmission pitch

{PRESUBMISSION_PITCH}

## Objection-control paragraph

The strongest anticipated objection is that RhoDyn could be read as useful software integration rather than a Nature Methods-level method. The Stage 10.6 pitch counters that objection by putting the decision object, named baselines, public biological breadth, and held-out validation before software maturity. It preserves the boundary that declared windows are analysis choices, bounded coupling is margin- and context-scoped, reserve-like outputs are endpoint-scoped, and routed-output parameters are not direct molecular edges.
"""


def render_main_text() -> str:
    results = render_results().replace("# Stage 10.6 method-first Results draft", "## Results")
    return f"""# {TITLE}

## Deck

{DECK}

## Abstract

{ABSTRACT}

## Introduction bridge

{INTRO_BRIDGE}

{results}

## Discussion landing

{DISCUSSION_LANDING}
"""


def change_matrix_rows() -> list[dict[str, str]]:
    return [
        {
            "surface": "title",
            "stage9_risk": "software-name-first framing could still read as workflow integration",
            "stage10_6_change": TITLE,
            "evidence_anchor": "manuscript/nature_methods/figures/stage10_5_method_first_figure_spine.md",
            "boundary": "does not claim that every system contains residence-state structure",
        },
        {
            "surface": "abstract",
            "stage9_risk": "validation breadth and named-baseline scope were present but not prominent enough",
            "stage10_6_change": "names baseline families, four public systems, sealed held-out outcomes, and implementation surfaces",
            "evidence_anchor": "case_studies/stage10_named_benchmarks/stage10_2_named_benchmark_report.json;case_studies/stage10_public_breadth/stage10_3_public_breadth_report.json;case_studies/stage10_heldout_validation/stage10_4_gate_report.json",
            "boundary": "preserves amplitude-sufficient and inconclusive cases",
        },
        {
            "surface": "results",
            "stage9_risk": "figure sequence could still seem balanced between examples and software",
            "stage10_6_change": "starts with method object, named baselines, and public breadth before endpoint extension, held-out validation, and software",
            "evidence_anchor": "manuscript/nature_methods/figures/stage10_5_panel_evidence_crosswalk.csv",
            "boundary": "software reproducibility is secondary support",
        },
        {
            "surface": "discussion",
            "stage9_risk": "method contribution could collapse into a useful decision workflow rather than a method claim",
            "stage10_6_change": "states residence-state inference under declared windows, named comparators, uncertainty, and abstention as primary contribution",
            "evidence_anchor": "docs/stage10_method_object_v2.md;docs/stage10_5_method_first_figure_architecture.md",
            "boundary": "does not present RhoDyn as a direct mechanism-discovery method",
        },
        {
            "surface": "cover letter and presubmission pitch",
            "stage9_risk": "editor may see software wrapper before method advance",
            "stage10_6_change": "leads with decision object, named baselines, public systems, held-out validation, then software reproducibility",
            "evidence_anchor": "docs/stage10_nature_methods_eic_rescue_roadmap.md",
            "boundary": "explicitly says software availability is not the advance by itself",
        },
    ]


def boundary_rows() -> list[dict[str, str]]:
    surfaces = {
        "title_abstract": render_title_abstract(),
        "results": render_results(),
        "discussion": render_discussion(),
        "pitch": render_pitch(),
        "main_text": render_main_text(),
    }
    rows: list[dict[str, str]] = []
    for phrase in FORBIDDEN_PHRASES:
        hits = [name for name, text in surfaces.items() if phrase.lower() in text.lower()]
        rows.append(
            {
                "boundary_phrase": phrase,
                "status": "pass" if not hits else "fail",
                "hits": ";".join(hits),
                "safe_boundary": "Do not overstate residence, bounded coupling, reserve-like endpoints, routed-output parameters, or software reproducibility.",
            }
        )
    return rows


def validate_stage10_6() -> dict[str, object]:
    rows = _read_csv(FIGURE_CROSSWALK)
    roles_by_fig = {fig: next(row["figure_role"] for row in rows if row["fig_id"] == fig) for fig in sorted({row["fig_id"] for row in rows})}
    gate10_5 = json.loads(STAGE10_5_GATE.read_text(encoding="utf-8"))
    all_text = "\n".join([render_title_abstract(), render_results(), render_discussion(), render_pitch(), render_main_text()])
    boundary = boundary_rows()
    fig_mentions = {f"Figure {i}": (f"Figure {i}" in all_text or f"Fig. {i}" in all_text) for i in range(1, 7)}
    gates = {
        "stage10_5_prerequisite_passed": gate10_5.get("status") == "pass",
        "title_is_method_first": TITLE.startswith("Residence-state inference") and "live-cell perturbation data" in TITLE,
        "abstract_names_baseline_breadth": all(term in ABSTRACT for term in ["SciPy", "scikit-learn", "HMM", "MiniROCKET", "ruptures-style"]),
        "abstract_names_public_breadth": all(term in ABSTRACT for term in ["DRG calcium", "GPCR-linked ERK", "Cell Painting/MitoTox", "MLCI tracking"]),
        "abstract_names_heldout_boundaries": all(term in ABSTRACT for term in ["positive", "comparator-sufficient", "inconclusive"]),
        "results_follow_stage10_5_figures": roles_by_fig.get("FIG-001") == "method_object_first" and roles_by_fig.get("FIG-006") == "software_reproducibility_secondary" and all(fig_mentions.values()),
        "pitch_rejects_software_wrapper_reading": "not a wrapper" in PRESUBMISSION_PITCH or "software availability by itself" in COVER_LETTER_OPENING,
        "boundaries_pass": all(row["status"] == "pass" for row in boundary),
    }
    status = "pass" if all(gates.values()) else "fail"
    return {
        "stage": "10.6",
        "status": status,
        "gates": gates,
        "summary_metrics": {
            "abstract_word_count": _word_count(ABSTRACT),
            "results_subsection_count": len(RESULTS_SECTIONS),
            "figure_mentions": sum(fig_mentions.values()),
            "change_matrix_rows": len(change_matrix_rows()),
            "boundary_rows": len(boundary),
        },
        "figure_roles": roles_by_fig,
        "interpretation_boundary": "Stage 10.6 is an evidence-presentation transformation. It does not add biological data, new benchmark results, new figures, or new software capabilities.",
        "next_phase": "Stage 10.7 benchmark-ready release candidate",
    }


def run_stage10_6() -> dict[str, object]:
    STAGE_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    _write_text(STAGE_DIR / "title_abstract_v2.md", render_title_abstract())
    _write_text(STAGE_DIR / "results_method_first_v2.md", render_results())
    _write_text(STAGE_DIR / "discussion_landing_v2.md", render_discussion())
    _write_text(STAGE_DIR / "eic_pitch_v2.md", render_pitch())
    _write_text(STAGE_DIR / "main_text_method_first_rescue_draft.md", render_main_text())
    _write_csv(STAGE_DIR / "stage10_6_change_matrix.tsv", change_matrix_rows(), ["surface", "stage9_risk", "stage10_6_change", "evidence_anchor", "boundary"])
    _write_csv(STAGE_DIR / "stage10_6_claim_boundary_audit.tsv", boundary_rows(), ["boundary_phrase", "status", "hits", "safe_boundary"])
    report = validate_stage10_6()
    _write_json(GATE_REPORT, report)
    brief = f"""# Stage 10.6 manuscript-pitch transformation brief

Stage 10.6 rewrites the manuscript and EIC-facing pitch around the method-first figure architecture. The preferred title is `{TITLE}`. The abstract now names named baseline families, four public demonstration systems, sealed held-out positive/comparator-sufficient/inconclusive outcomes, and the boundary that declared windows or fitted parameters are not mechanisms.

Status. {report['status']}.

Next phase. {report['next_phase']}.
"""
    _write_text(BRIEF_PATH, brief)
    doc = f"""# Stage 10.6 manuscript-pitch transformation

Stage 10.6 converts the Stage 10.5 figure architecture into reader-facing manuscript and pitch surfaces. It is a presentation and framing transformation only. It does not add evidence or replace the closed Stage 9 submission package.

## Preferred title

{TITLE}

## Primary message

RhoDyn should now be introduced as a residence-state inference method for live-cell perturbation data. Software reproducibility remains essential, but it is the implementation surface of the method rather than the primary scientific advance.

## Generated surfaces

- `manuscript/nature_methods/stage10_6/title_abstract_v2.md`
- `manuscript/nature_methods/stage10_6/results_method_first_v2.md`
- `manuscript/nature_methods/stage10_6/discussion_landing_v2.md`
- `manuscript/nature_methods/stage10_6/eic_pitch_v2.md`
- `manuscript/nature_methods/stage10_6/main_text_method_first_rescue_draft.md`
- `manuscript/nature_methods/stage10_6/stage10_6_change_matrix.tsv`
- `manuscript/nature_methods/stage10_6/stage10_6_claim_boundary_audit.tsv`

## Gate status

{report['status']}

## Boundary

{report['interpretation_boundary']}
"""
    _write_text(DOC_PATH, doc)
    return report


if __name__ == "__main__":
    print(json.dumps(run_stage10_6(), indent=2, sort_keys=True))

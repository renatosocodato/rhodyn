"""Build the Stage 10.5 method-first Nature Methods figure architecture.

Stage 10.5 does not render new panels. It converts the completed Stage 10
evidence tracks into an editor-facing figure spine where the method object,
named baselines, public biological breadth, and held-out validation are visible
before software maturity. The output is a PanelForge-ready architecture plan
with explicit evidence files and source scripts for every planned panel.
"""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "case_studies" / "stage10_figure_architecture"
FIGURE_DIR = ROOT / "manuscript" / "nature_methods" / "figures"
DOC_PATH = ROOT / "docs" / "stage10_5_method_first_figure_architecture.md"
SPINE_PATH = FIGURE_DIR / "stage10_5_method_first_figure_spine.md"
PANEL_CSV = FIGURE_DIR / "stage10_5_panel_evidence_crosswalk.csv"
SUPP_CSV = FIGURE_DIR / "stage10_5_supplementary_map.csv"
GATE_REPORT = OUTPUT_DIR / "stage10_5_gate_report.json"
BRIEF_PATH = OUTPUT_DIR / "stage10_5_figure_architecture_brief.md"


def _panel(
    *,
    fig_id: str,
    panel: str,
    figure_title: str,
    figure_role: str,
    panel_title: str,
    method_job: str,
    reader_takeaway: str,
    stage_anchor: str,
    vulnerability_addressed: str,
    evidence_files: list[str],
    source_scripts: list[str],
    render_recipe_hint: str,
    role_class: str,
) -> dict[str, str]:
    return {
        "fig_id": fig_id,
        "panel": panel,
        "panel_id": f"{fig_id}{panel}",
        "figure_title": figure_title,
        "figure_role": figure_role,
        "panel_title": panel_title,
        "method_job": method_job,
        "reader_takeaway": reader_takeaway,
        "stage_anchor": stage_anchor,
        "vulnerability_addressed": vulnerability_addressed,
        "evidence_files": ";".join(evidence_files),
        "source_scripts": ";".join(source_scripts),
        "render_recipe_hint": render_recipe_hint,
        "role_class": role_class,
    }


def stage10_5_panels() -> list[dict[str, str]]:
    panels: list[dict[str, str]] = []
    add = panels.append

    f1 = "Figure 1. RhoDyn formalizes residence-state inference as a decision object"
    add(
        _panel(
            fig_id="FIG-001",
            panel="A",
            figure_title=f1,
            figure_role="method_object_first",
            panel_title="Input objects and declared biological regimes",
            method_job="Define tidy trajectory, paired-reporter, and endpoint inputs before any biological interpretation.",
            reader_takeaway="RhoDyn begins with declared data objects, grouping fields, windows, margins, and failure rules rather than free-form post hoc summaries.",
            stage_anchor="10.1",
            vulnerability_addressed="method_novelty",
            evidence_files=["docs/stage10_method_object_v2.md", "src/rhodyn/method_object.py"],
            source_scripts=["scripts/run_stage10_1_method_object_v2.py"],
            render_recipe_hint="schema_flow",
            role_class="main_method_definition",
        )
    )
    add(
        _panel(
            fig_id="FIG-001",
            panel="B",
            figure_title=f1,
            figure_role="method_object_first",
            panel_title="Residence-comparator decision divergence",
            method_job="Show the central decision object that compares declared residence summaries against endpoint, amplitude, and generic comparator families.",
            reader_takeaway="The method-level advance is the explicit decision divergence and abstention grammar, not only software integration.",
            stage_anchor="10.1",
            vulnerability_addressed="method_novelty",
            evidence_files=["docs/stage10_method_object_v2.md", "case_studies/stage10_method_object_v2/stage10_1_method_object_decisions.csv"],
            source_scripts=["scripts/run_stage10_1_method_object_v2.py"],
            render_recipe_hint="equation_plus_decision_table",
            role_class="main_method_definition",
        )
    )
    add(
        _panel(
            fig_id="FIG-001",
            panel="C",
            figure_title=f1,
            figure_role="method_object_first",
            panel_title="Executable positive, negative, and ambiguous fixtures",
            method_job="Prove that the same method object can call residence-positive, comparator-sufficient, and unresolved cases.",
            reader_takeaway="RhoDyn is a scoped decision method because it can also withhold interpretation when inputs do not earn a call.",
            stage_anchor="10.1",
            vulnerability_addressed="method_novelty",
            evidence_files=["case_studies/stage10_method_object_v2/stage10_1_method_object_decisions.csv", "case_studies/stage10_method_object_v2/stage10_1_method_object_gate_report.json"],
            source_scripts=["scripts/run_stage10_1_method_object_v2.py", "tests/test_stage10_1_method_object_v2.py"],
            render_recipe_hint="truth_case_grid",
            role_class="main_method_validation",
        )
    )
    add(
        _panel(
            fig_id="FIG-001",
            panel="D",
            figure_title=f1,
            figure_role="method_object_first",
            panel_title="Abstention and failure-mode grammar",
            method_job="Make unsupported biological calls visible as formal outputs rather than hidden exclusions.",
            reader_takeaway="The method does not claim that every live-cell dataset has a residence regime or that every coupling is bounded.",
            stage_anchor="10.1",
            vulnerability_addressed="overclaim_boundary",
            evidence_files=["docs/stage10_1_api_gap_list.md", "case_studies/stage10_method_object_v2/stage10_1_method_object_brief.md"],
            source_scripts=["scripts/run_stage10_1_method_object_v2.py"],
            render_recipe_hint="failure_boundary_table",
            role_class="main_method_boundary",
        )
    )

    f2 = "Figure 2. Named baselines define when residence-state inference adds value"
    add(
        _panel(
            fig_id="FIG-002",
            panel="A",
            figure_title=f2,
            figure_role="named_baseline_benchmarking",
            panel_title="Known-truth regimes for benchmark stress tests",
            method_job="Set synthetic residence-positive, amplitude-sufficient, and ambiguous truth regimes before benchmarking.",
            reader_takeaway="Comparator performance is judged against declared truth structure rather than against a RhoDyn-only score.",
            stage_anchor="10.2",
            vulnerability_addressed="limited_named_tool_benchmarking",
            evidence_files=["case_studies/stage10_named_benchmarks/stage10_2_synthetic_named_baseline_benchmark.csv"],
            source_scripts=["scripts/run_stage10_2_named_benchmarking.py"],
            render_recipe_hint="truth_regime_matrix",
            role_class="main_benchmark",
        )
    )
    add(
        _panel(
            fig_id="FIG-002",
            panel="B",
            figure_title=f2,
            figure_role="named_baseline_benchmarking",
            panel_title="Named comparator families",
            method_job="Display simple summaries and named external-style baseline families side by side.",
            reader_takeaway="The benchmark includes amplitude, endpoint, AUC, peak, latency, threshold, SciPy peak, scikit-learn, HMM, catch22-style, tsfresh-style, MiniROCKET-style, and ruptures-style comparators.",
            stage_anchor="10.2",
            vulnerability_addressed="limited_named_tool_benchmarking",
            evidence_files=["case_studies/stage10_named_benchmarks/stage10_2_named_tool_availability.tsv", "case_studies/stage10_named_benchmarks/stage10_2_named_benchmark_report.json"],
            source_scripts=["scripts/run_stage10_2_named_benchmarking.py"],
            render_recipe_hint="baseline_family_ladder",
            role_class="main_benchmark",
        )
    )
    add(
        _panel(
            fig_id="FIG-002",
            panel="C",
            figure_title=f2,
            figure_role="named_baseline_benchmarking",
            panel_title="Accuracy and boundary outcomes",
            method_job="Compare RhoDyn decisions against named baseline performance and record where generic features succeed.",
            reader_takeaway="The paper should foreground both RhoDyn-positive regimes and regimes where named comparator families are sufficient.",
            stage_anchor="10.2",
            vulnerability_addressed="method_novelty",
            evidence_files=["case_studies/stage10_named_benchmarks/stage10_2_named_baseline_accuracy_summary.csv", "case_studies/stage10_named_benchmarks/stage10_2_failure_boundary_report.md"],
            source_scripts=["scripts/run_stage10_2_named_benchmarking.py"],
            render_recipe_hint="accuracy_heatmap_with_boundary_rows",
            role_class="main_benchmark",
        )
    )
    add(
        _panel(
            fig_id="FIG-002",
            panel="D",
            figure_title=f2,
            figure_role="named_baseline_benchmarking",
            panel_title="Public input benchmark summaries",
            method_job="Apply the same comparator framing to retained public DRG calcium and ERK GPCR inputs.",
            reader_takeaway="The method object and named baselines are evaluated on shared public inputs, not only synthetic fixtures.",
            stage_anchor="10.2",
            vulnerability_addressed="limited_named_tool_benchmarking",
            evidence_files=["case_studies/stage10_named_benchmarks/stage10_2_public_input_named_baseline_summary.csv"],
            source_scripts=["scripts/run_stage10_2_named_benchmarking.py"],
            render_recipe_hint="public_input_comparator_table",
            role_class="main_benchmark",
        )
    )
    add(
        _panel(
            fig_id="FIG-002",
            panel="E",
            figure_title=f2,
            figure_role="named_baseline_benchmarking",
            panel_title="Runtime and memory profile",
            method_job="Show practical compute cost for the method object and named feature families.",
            reader_takeaway="RhoDyn's methodological claim is separable from software maturity, but the benchmark remains computationally inspectable.",
            stage_anchor="10.2",
            vulnerability_addressed="software_secondary_support",
            evidence_files=["case_studies/stage10_named_benchmarks/stage10_2_runtime_memory.tsv"],
            source_scripts=["scripts/run_stage10_2_named_benchmarking.py"],
            render_recipe_hint="runtime_memory_stripplot",
            role_class="main_benchmark_support",
        )
    )

    f3 = "Figure 3. Public biological breadth tests portability across domains"
    add(
        _panel(
            fig_id="FIG-003",
            panel="A",
            figure_title=f3,
            figure_role="public_biological_breadth",
            panel_title="Independent public system matrix",
            method_job="Show counted source systems, biological domains, source access, and evidence roles.",
            reader_takeaway="The breadth claim rests on four counted independent public systems across at least three biological domains.",
            stage_anchor="10.3",
            vulnerability_addressed="small_public_biological_demonstration_count",
            evidence_files=["case_studies/stage10_public_breadth/stage10_3_public_system_matrix.tsv", "case_studies/stage10_public_breadth/stage10_3_public_breadth_report.json"],
            source_scripts=["scripts/run_stage10_3_public_biological_breadth.py"],
            render_recipe_hint="public_system_matrix",
            role_class="main_biological_breadth",
        )
    )
    add(
        _panel(
            fig_id="FIG-003",
            panel="B",
            figure_title=f3,
            figure_role="public_biological_breadth",
            panel_title="DRG calcium residence-amplitude divergence",
            method_job="Use a public calcium trajectory system to show a residence-versus-amplitude comparison outside the reference use case.",
            reader_takeaway="Residence and amplitude can diverge in neuronal calcium dynamics under declared window rules.",
            stage_anchor="7.3/10.3",
            vulnerability_addressed="small_public_biological_demonstration_count",
            evidence_files=["case_studies/stage7_public_signaling/drg_calcium_residence_amplitude_summary.csv", "case_studies/stage7_public_signaling/drg_calcium_uncertainty_summary.csv"],
            source_scripts=["scripts/run_stage7_3_public_signaling.py"],
            render_recipe_hint="trajectory_residence_amplitude_panel",
            role_class="main_biological_breadth",
        )
    )
    add(
        _panel(
            fig_id="FIG-003",
            panel="C",
            figure_title=f3,
            figure_role="public_biological_breadth",
            panel_title="ERK GPCR residence-amplitude divergence and sufficiency boundary",
            method_job="Use GPCR-linked ERK dynamics to show both residence/amplitude structure and comparator-sufficient boundaries.",
            reader_takeaway="RhoDyn's breadth is strengthened by systems where residence helps and systems where simpler summaries can be sufficient.",
            stage_anchor="7.3/10.4",
            vulnerability_addressed="small_public_biological_demonstration_count",
            evidence_files=["case_studies/stage7_public_signaling/erk_gpcr_residence_amplitude_summary.csv", "case_studies/stage10_heldout_validation/stage10_4_heldout_decisions.tsv"],
            source_scripts=["scripts/run_stage7_3_public_signaling.py", "scripts/run_stage10_4_heldout_validation.py"],
            render_recipe_hint="trajectory_boundary_comparison",
            role_class="main_biological_breadth",
        )
    )
    add(
        _panel(
            fig_id="FIG-003",
            panel="D",
            figure_title=f3,
            figure_role="public_biological_breadth",
            panel_title="Cell Painting and MitoTox endpoint architecture",
            method_job="Bring endpoint perturbation data into the same method frame without presenting it as trajectory evidence.",
            reader_takeaway="Public endpoint data can support reduced-architecture and reserve-like decisions when measurement scope is explicit.",
            stage_anchor="7.4/10.3",
            vulnerability_addressed="small_public_biological_demonstration_count",
            evidence_files=["case_studies/stage7_endpoint_reserve_routing/cell_painting_routed_model_comparison.csv", "case_studies/stage7_endpoint_reserve_routing/cell_painting_reserve_like_model_summary.csv"],
            source_scripts=["scripts/run_stage7_4_endpoint_reserve_routing.py"],
            render_recipe_hint="endpoint_architecture_panel",
            role_class="main_biological_breadth",
        )
    )
    add(
        _panel(
            fig_id="FIG-003",
            panel="E",
            figure_title=f3,
            figure_role="public_biological_breadth",
            panel_title="MLCI tracking residence-amplitude stress test",
            method_job="Use microbial live-cell tracking as a non-molecular trajectory stress test for schema portability and residence divergence.",
            reader_takeaway="The method can expose residence/amplitude divergence outside reporter kinase or calcium datasets, while the biological interpretation remains tracking-intensity scoped.",
            stage_anchor="10.3/10.4",
            vulnerability_addressed="small_public_biological_demonstration_count",
            evidence_files=["case_studies/stage10_public_breadth/stage10_3_mlci_tracking_residence_summary.csv", "case_studies/stage10_heldout_validation/stage10_4_trajectory_object_calls.csv"],
            source_scripts=["scripts/run_stage10_3_public_biological_breadth.py", "scripts/run_stage10_4_heldout_validation.py"],
            render_recipe_hint="tracking_residence_panel",
            role_class="main_biological_breadth",
        )
    )
    add(
        _panel(
            fig_id="FIG-003",
            panel="F",
            figure_title=f3,
            figure_role="public_biological_breadth",
            panel_title="Source eligibility and deferred datasets",
            method_job="Make source-access and license boundaries visible rather than silently adding weak demonstrations.",
            reader_takeaway="Birtwistle ERK/Akt is source-verified but deferred from counted release evidence because explicit license support is missing.",
            stage_anchor="10.3",
            vulnerability_addressed="overclaim_boundary",
            evidence_files=["case_studies/stage10_public_breadth/stage10_3_candidate_resolution.tsv", "case_studies/stage10_public_breadth/stage10_3_source_access_ledger.tsv", "case_studies/stage10_public_breadth/stage10_3_birtwistle_source_probe.json"],
            source_scripts=["scripts/run_stage10_3_public_biological_breadth.py"],
            render_recipe_hint="source_eligibility_table",
            role_class="main_boundary",
        )
    )

    f4 = "Figure 4. Endpoint, reserve-like, bounded-coupling, and routed-output decisions extend the method"
    for panel, title, job, takeaway, evidence, recipe in [
        (
            "A",
            "Endpoint input schema and contrast contract",
            "Define how endpoint perturbation rows carry grouping, contrast, margin, and readout fields.",
            "Endpoint use cases enter RhoDyn through declared contrasts rather than being forced into trajectory language.",
            ["case_studies/stage7_endpoint_reserve_routing/stage7_4_case_summary.tsv", "case_studies/stage7_endpoint_reserve_routing/cell_painting_tidy_endpoint_model_rows.csv"],
            "endpoint_schema_flow",
        ),
        (
            "B",
            "Bounded-coupling decisions under declared margins",
            "Show margin-bound ERK/Akt coupling calls with pass, fail, or inconclusive decisions.",
            "Bounded coupling is a context-scoped interval decision, not a claim of no biochemical interaction.",
            ["case_studies/stage7_endpoint_reserve_routing/erk_akt_bounded_coupling_decisions.csv", "case_studies/stage7_endpoint_reserve_routing/erk_akt_bounded_coupling_stage7_4_report.md"],
            "bounded_coupling_interval_table",
        ),
        (
            "C",
            "Reserve-like endpoint coordinate",
            "Tie buffering language to measured endpoint preservation rather than hidden latent reserve.",
            "Reserve-like calls remain measurement-scoped and uncertainty-aware.",
            ["case_studies/stage7_endpoint_reserve_routing/cell_painting_reserve_like_endpoint_rows.csv", "case_studies/stage7_endpoint_reserve_routing/cell_painting_reserve_like_uncertainty.csv"],
            "reserve_endpoint_uncertainty_panel",
        ),
        (
            "D",
            "Routed-output reduced-architecture comparison",
            "Compare candidate endpoint architectures against reduced alternatives.",
            "Routed-output support is earned only when reduced alternatives fail within the measured endpoint structure.",
            ["case_studies/stage7_endpoint_reserve_routing/cell_painting_routed_model_comparison.csv", "case_studies/stage7_endpoint_reserve_routing/cell_painting_reduced_alternative_decisions.tsv"],
            "architecture_comparison_matrix",
        ),
        (
            "E",
            "Measurement-scope limits",
            "State where endpoint, reserve-like, and routed-output decisions should abstain.",
            "The method extension is broad enough for endpoint data but still bounded by assay scope and declared alternatives.",
            ["case_studies/stage7_endpoint_reserve_routing/stage7_4_endpoint_reserve_routing_gate_report.json", "docs/stage7_endpoint_reserve_routing_demonstrations.md"],
            "endpoint_limitations_table",
        ),
    ]:
        add(
            _panel(
                fig_id="FIG-004",
                panel=panel,
                figure_title=f4,
                figure_role="endpoint_reserve_routing_extension",
                panel_title=title,
                method_job=job,
                reader_takeaway=takeaway,
                stage_anchor="7.4/10.5",
                vulnerability_addressed="method_generalization",
                evidence_files=evidence,
                source_scripts=["scripts/run_stage7_4_endpoint_reserve_routing.py"],
                render_recipe_hint=recipe,
                role_class="main_method_extension",
            )
        )

    f5 = "Figure 5. Sealed held-out validation shows pass, comparator-sufficient, and inconclusive outcomes"
    for panel, title, job, takeaway, evidence, recipe in [
        (
            "A",
            "Predeclared splits, thresholds, and margins",
            "Place training definitions and held-out contexts before the decision table.",
            "The validation panels are no-retuning challenges rather than retrospective optimization.",
            ["case_studies/stage10_heldout_validation/stage10_4_predeclaration.json", "case_studies/stage10_heldout_validation/stage10_4_predeclaration.md"],
            "predeclaration_flow",
        ),
        (
            "B",
            "Held-out decision table",
            "Show positive, negative or comparator-sufficient, and inconclusive calls in one panel.",
            "RhoDyn becomes stronger by preserving unsupported and comparator-sufficient outcomes alongside positive calls.",
            ["case_studies/stage10_heldout_validation/stage10_4_heldout_decisions.tsv"],
            "heldout_decision_matrix",
        ),
        (
            "C",
            "Object-level held-out trajectory calls",
            "Expose the MLCI and ERK object-level classifications behind held-out decisions.",
            "Held-out evidence is inspectable at the object level rather than only as a summary verdict.",
            ["case_studies/stage10_heldout_validation/stage10_4_trajectory_object_calls.csv"],
            "heldout_object_scatter",
        ),
        (
            "D",
            "No-hidden-tuning and gate status",
            "Render Stage 10.4 gates and hidden-tuning status as validation evidence.",
            "The held-out result is scoped but rule-preserving.",
            ["case_studies/stage10_heldout_validation/stage10_4_gate_report.json", "case_studies/stage10_heldout_validation/stage10_4_heldout_report.md"],
            "gate_status_table",
        ),
        (
            "E",
            "Prospective validation boundary",
            "State the remaining distinction between sealed replay and prospective blinded collaborator validation.",
            "Stage 10.4 lowers desk-rejection risk but does not replace future prospective external validation.",
            ["docs/stage10_4_heldout_validation.md", "case_studies/stage10_heldout_validation/stage10_4_gate_report.json"],
            "validation_boundary_panel",
        ),
    ]:
        add(
            _panel(
                fig_id="FIG-005",
                panel=panel,
                figure_title=f5,
                figure_role="heldout_validation",
                panel_title=title,
                method_job=job,
                reader_takeaway=takeaway,
                stage_anchor="10.4",
                vulnerability_addressed="heldout_validation",
                evidence_files=evidence,
                source_scripts=["scripts/run_stage10_4_heldout_validation.py"],
                render_recipe_hint=recipe,
                role_class="main_validation",
            )
        )

    f6 = "Figure 6. Reproducible software surfaces make the method inspectable"
    for panel, title, job, takeaway, evidence, scripts, recipe in [
        (
            "A",
            "Python, CLI, API, and workbench parity",
            "Show that interface surfaces delegate to the same stable method outputs.",
            "Software maturity supports inspectability after the method evidence has already been established.",
            ["case_studies/stage7_methods_reproducibility/cross_surface_parity.tsv"],
            ["scripts/run_stage7_6_methods_reproducibility.py"],
            "parity_table",
        ),
        (
            "B",
            "Analysis export bundle anatomy",
            "Show inputs, schema, parameters, outputs, figures, and checksums in the same bundle.",
            "The method reports are reproducible rather than hidden in session state.",
            ["case_studies/stage7_usability_rehearsal/export_examples_manifest.tsv"],
            ["scripts/run_stage7_7_usability_rehearsal.py"],
            "export_bundle_diagram",
        ),
        (
            "C",
            "Clean-room reproduction",
            "Document the source-distribution replay route for selected evidence outputs.",
            "A fresh environment can regenerate the retained method evidence surfaces.",
            ["case_studies/stage7_methods_reproducibility/stage7_6_methods_reproducibility_gate_report.json", "docs/clean_room_reproducibility_report.md"],
            ["scripts/run_stage7_6_methods_reproducibility.py", "scripts/run_clean_room_reproducibility.py"],
            "clean_room_flow",
        ),
        (
            "D",
            "Archive and checksum coverage",
            "Show release archive inventory and checksum coverage.",
            "The public release is citable and inspectable without importing private manuscript data.",
            ["case_studies/stage7_methods_reproducibility/release_archive_manifest.tsv", "docs/release_checksums.csv"],
            ["scripts/write_release_checksums.py"],
            "archive_checksum_panel",
        ),
        (
            "E",
            "User-path rehearsal",
            "Show biologist-facing and quantitative paths to the same reviewable outputs.",
            "Adoption evidence is presented as reproducibility support, not as the scientific advance itself.",
            ["case_studies/stage7_usability_rehearsal/user_path_findings.tsv", "case_studies/stage7_usability_rehearsal/stage7_7_usability_gate_report.json"],
            ["scripts/run_stage7_7_usability_rehearsal.py"],
            "user_path_panel",
        ),
    ]:
        add(
            _panel(
                fig_id="FIG-006",
                panel=panel,
                figure_title=f6,
                figure_role="software_reproducibility_secondary",
                panel_title=title,
                method_job=job,
                reader_takeaway=takeaway,
                stage_anchor="7.6/7.7",
                vulnerability_addressed="software_secondary_support",
                evidence_files=evidence,
                source_scripts=scripts,
                render_recipe_hint=recipe,
                role_class="software_after_method_evidence",
            )
        )

    return panels


def stage10_5_supplementary_map(panels: list[dict[str, str]]) -> list[dict[str, str]]:
    specs = [
        ("SUPP-001", "FIG-001C", "Method-object truth-case details", "Expanded positive, negative, and ambiguous fixture rows for trajectory, coupling, reserve-like, and routed-output decisions."),
        ("SUPP-002", "FIG-002B", "Named baseline implementation notes", "Detailed comparator-family availability, optional-package status, and simple-summary definitions."),
        ("SUPP-003", "FIG-002C", "Synthetic benchmark failure boundaries", "Cases where named baseline families succeed or where RhoDyn should abstain."),
        ("SUPP-004", "FIG-003A", "Public source access and eligibility", "Source DOI, license, retained-table, and deferred-source records for public demonstrations."),
        ("SUPP-005", "FIG-003D", "Endpoint model-comparison support", "Reduced-architecture ranking and reserve-like uncertainty tables behind endpoint panels."),
        ("SUPP-006", "FIG-005A", "Held-out predeclaration and fixed-rule audit", "Training/held-out splits, thresholds, margins, hidden-tuning status, and boundary wording."),
        ("SUPP-007", "FIG-006A", "Cross-surface parity and clean-room reproduction", "Python, CLI, backend, workbench, archive, and clean-room reproduction support."),
    ]
    panel_ids = {row["panel_id"] for row in panels}
    rows: list[dict[str, str]] = []
    for supp_id, parent_panel, title, role in specs:
        if parent_panel not in panel_ids:
            raise ValueError(f"orphan supplementary item {supp_id} references missing {parent_panel}")
        parent = next(row for row in panels if row["panel_id"] == parent_panel)
        rows.append(
            {
                "supp_id": supp_id,
                "parent_panel": parent_panel,
                "parent_figure": parent["fig_id"],
                "title": title,
                "role": role,
                "evidence_files": parent["evidence_files"],
                "source_scripts": parent["source_scripts"],
            }
        )
    return rows


def _write_csv(path: Path, rows: Iterable[dict[str, str]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_text(path: Path, body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body.rstrip() + "\n", encoding="utf-8")


def _missing_paths(rows: Iterable[dict[str, str]], field: str) -> list[str]:
    missing: list[str] = []
    for row in rows:
        for rel in row[field].split(";"):
            if rel and not (ROOT / rel).exists():
                missing.append(rel)
    return sorted(set(missing))


def validate_architecture(panels: list[dict[str, str]], supplementary: list[dict[str, str]]) -> dict[str, object]:
    figure_ids = sorted({row["fig_id"] for row in panels})
    roles_by_fig = {fig: next(row["figure_role"] for row in panels if row["fig_id"] == fig) for fig in figure_ids}
    role_counter = Counter(row["role_class"] for row in panels)
    vulnerability_counter = Counter(row["vulnerability_addressed"] for row in panels)
    first_three_roles = [roles_by_fig.get(fig) for fig in ["FIG-001", "FIG-002", "FIG-003"]]
    software_figures = sorted({row["fig_id"] for row in panels if "software" in row["role_class"] or "software" in row["figure_role"]})
    parent_counts = Counter(row["parent_panel"] for row in supplementary)
    missing_evidence = _missing_paths(panels + supplementary, "evidence_files")
    missing_scripts = _missing_paths(panels + supplementary, "source_scripts")
    gates = {
        "six_main_figures": len(figure_ids) == 6,
        "first_three_method_performance_breadth": first_three_roles == [
            "method_object_first",
            "named_baseline_benchmarking",
            "public_biological_breadth",
        ],
        "software_after_method_validation": software_figures == ["FIG-006"],
        "all_panels_have_existing_evidence": not missing_evidence,
        "all_panels_have_existing_scripts": not missing_scripts,
        "supplementary_items_have_one_parent": bool(supplementary) and all(count == 1 for count in parent_counts.values()),
        "stage10_4_heldout_visible_before_software": any(row["fig_id"] == "FIG-005" and row["stage_anchor"] == "10.4" for row in panels),
        "all_three_vulnerabilities_addressed": all(
            vulnerability_counter[key] > 0
            for key in [
                "method_novelty",
                "limited_named_tool_benchmarking",
                "small_public_biological_demonstration_count",
            ]
        ),
    }
    status = "pass" if all(gates.values()) else "fail"
    return {
        "stage": "10.5",
        "status": status,
        "gates": gates,
        "summary_metrics": {
            "figure_count": len(figure_ids),
            "panel_count": len(panels),
            "supplementary_item_count": len(supplementary),
            "method_or_validation_panel_count_before_software": sum(1 for row in panels if row["fig_id"] < "FIG-006"),
            "software_panel_count": role_counter["software_after_method_evidence"],
            "unique_evidence_file_count": len({rel for row in panels for rel in row["evidence_files"].split(";") if rel}),
            "unique_source_script_count": len({rel for row in panels for rel in row["source_scripts"].split(";") if rel}),
        },
        "figure_roles": roles_by_fig,
        "vulnerability_panel_counts": dict(vulnerability_counter),
        "missing_evidence_files": missing_evidence,
        "missing_source_scripts": missing_scripts,
        "interpretation_boundary": "Stage 10.5 is a figure-architecture and manuscript-display plan. It does not add new biological evidence, render new PanelForge figures, or replace the Stage 9 rendered mockups.",
        "next_phase": "Stage 10.6 manuscript and cover-letter pitch transformation",
    }


def _figure_summary_rows(panels: list[dict[str, str]]) -> list[tuple[str, str, str, str]]:
    rows: list[tuple[str, str, str, str]] = []
    for fig_id in sorted({row["fig_id"] for row in panels}):
        fig_panels = [row for row in panels if row["fig_id"] == fig_id]
        title = fig_panels[0]["figure_title"]
        role = fig_panels[0]["figure_role"]
        panel_list = "; ".join(f"{row['panel']}. {row['panel_title']}" for row in fig_panels)
        evidence = "; ".join(sorted({rel for row in fig_panels for rel in row["evidence_files"].split(";") if rel}))
        rows.append((fig_id, title, role, f"{panel_list}\nEvidence. {evidence}"))
    return rows


def render_markdown(panels: list[dict[str, str]], supplementary: list[dict[str, str]], gate_report: dict[str, object]) -> tuple[str, str, str]:
    figure_rows = _figure_summary_rows(panels)
    spine_lines = [
        "# Stage 10.5 method-first Nature Methods figure spine",
        "",
        "Stage. 10.5 method-first figure architecture.",
        "",
        "Scope. This blueprint supersedes the Stage 9 display spine for the next Nature Methods rescue draft. It does not render new panels. It tells the next PanelForge pass which evidence should be visible first.",
        "",
        "## Main figure sequence",
        "",
        "| figure | editorial job | panels and evidence |",
        "| --- | --- | --- |",
    ]
    for fig_id, title, role, details in figure_rows:
        spine_lines.append(f"| {fig_id} | {title}<br>{role} | {details.replace(chr(10), '<br>')} |")
    spine_lines.extend(
        [
            "",
            "## Method-first ordering rule",
            "",
            "Figures 1-3 establish the method object, named comparator behavior, and public biological breadth before any software-maturity figure appears. Figure 4 extends the method to endpoint, reserve-like, bounded-coupling, and routed-output decisions. Figure 5 shows held-out validation and uncertainty boundaries. Figure 6 then shows software parity, release, archive, and adoption support.",
            "",
            "## PanelForge promotion rule",
            "",
            "A future rendering pass should treat `manuscript/nature_methods/figures/stage10_5_panel_evidence_crosswalk.csv` as the active panel-to-evidence map. The historical Stage 9 rendered panels remain archived until a new Stage 10 PanelForge render is authorized.",
        ]
    )

    doc_lines = [
        "# Stage 10.5 method-first figure architecture",
        "",
        "Stage 10.5 converts the completed Stage 10 evidence tracks into a Nature Methods display spine that reads as a methodological advance before it reads as software maturity.",
        "",
        "## Why this figure architecture is different from Stage 9",
        "",
        "The Stage 9 figure set was coherent, but it balanced method, examples, and software too evenly. The Stage 10.5 version moves the vulnerable editorial points to the front. Figure 1 defines the decision object, Figure 2 shows named baselines, Figure 3 shows public biological breadth, Figure 4 shows endpoint and routed-output extensions, Figure 5 shows held-out validation, and Figure 6 supports reproducible software use.",
        "",
        "## Main figures",
        "",
        "| figure | role | biological or method message |",
        "| --- | --- | --- |",
    ]
    for fig_id, title, role, details in figure_rows:
        message = details.split("\n", 1)[0]
        doc_lines.append(f"| {fig_id} | {role} | {title}. {message} |")
    doc_lines.extend(
        [
            "",
            "## Supplementary support",
            "",
            "| supplementary item | parent panel | role |",
            "| --- | --- | --- |",
        ]
    )
    for row in supplementary:
        doc_lines.append(f"| {row['supp_id']} | {row['parent_panel']} | {row['role']} |")
    doc_lines.extend(
        [
            "",
            "## Gates",
            "",
            "| gate | status |",
            "| --- | --- |",
        ]
    )
    for key, value in gate_report["gates"].items():
        doc_lines.append(f"| {key} | {'pass' if value else 'fail'} |")
    doc_lines.extend(
        [
            "",
            "## Interpretation boundary",
            "",
            str(gate_report["interpretation_boundary"]),
        ]
    )

    brief_lines = [
        "# Stage 10.5 figure architecture brief",
        "",
        "The figure architecture now leads with the method object, named-baseline benchmarking, public biological breadth, and held-out validation. This directly addresses the main editorial risk that RhoDyn could be read as useful workflow integration rather than as a residence-state inference method.",
        "",
        f"Status. {gate_report['status']}.",
        "",
        "Summary metrics.",
        "",
    ]
    for key, value in gate_report["summary_metrics"].items():
        brief_lines.append(f"- {key}: {value}")
    brief_lines.extend(
        [
            "",
            "Next phase. Stage 10.6 should rehydrate the title, abstract, Results openers, limitations, cover letter, and EIC-facing pitch around this method-first figure sequence.",
        ]
    )
    return "\n".join(spine_lines), "\n".join(doc_lines), "\n".join(brief_lines)


def run_stage10_5() -> dict[str, object]:
    panels = stage10_5_panels()
    supplementary = stage10_5_supplementary_map(panels)
    gate_report = validate_architecture(panels, supplementary)
    panel_fields = [
        "fig_id",
        "panel",
        "panel_id",
        "figure_title",
        "figure_role",
        "panel_title",
        "method_job",
        "reader_takeaway",
        "stage_anchor",
        "vulnerability_addressed",
        "evidence_files",
        "source_scripts",
        "render_recipe_hint",
        "role_class",
    ]
    supp_fields = ["supp_id", "parent_panel", "parent_figure", "title", "role", "evidence_files", "source_scripts"]
    _write_csv(PANEL_CSV, panels, panel_fields)
    _write_csv(SUPP_CSV, supplementary, supp_fields)
    spine_md, doc_md, brief_md = render_markdown(panels, supplementary, gate_report)
    _write_text(SPINE_PATH, spine_md)
    _write_text(DOC_PATH, doc_md)
    _write_text(BRIEF_PATH, brief_md)
    _write_json(GATE_REPORT, gate_report)
    return gate_report


if __name__ == "__main__":
    report = run_stage10_5()
    print(json.dumps(report, indent=2, sort_keys=True))

"""Validate the Stage 9 scaffold-only manuscript workspace."""

from __future__ import annotations

import json
import csv
import re
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT / "manuscript" / "nature_methods"

REQUIRED_DIRS = [
    "sections",
    "figures",
    "figures/rendered",
    "tables",
    "supplementary",
    "refs",
    "refs/_cache",
    "audits",
    "ledgers",
    "submission_package",
    "contracts",
    "contracts/ledger_schemas",
    "gate_verdicts",
    "_staging",
    "_quarantine",
]
REQUIRED_REPO_DIRS = [
    "tools",
    "tools/panelforge-figures",
]

REQUIRED_FILES = [
    "docs/stage9_manuscript_assembly_plan.md",
    "docs/stage9_execution_memory.json",
    "scripts/run_stage9_0_evidence_intake_lock.py",
    "scripts/run_stage9_1_venue_guidance_register.py",
    "scripts/run_stage9_2_methods_paper_corpus.py",
    "scripts/run_stage9_3_narrative_spine.py",
    "scripts/run_stage9_4_claim_freeze.py",
    "scripts/run_stage9_5_paragraph_claim_ledger.py",
    "scripts/run_stage9_6_figure_spine.py",
    "scripts/run_stage9_6b_panelforge_rendering.py",
    "scripts/run_stage9_7_supplementary_display_plan.py",
    "scripts/run_stage9_8_section_contract_blueprint.py",
    "scripts/run_stage9_9_title_abstract_strategy.py",
    "scripts/run_stage9_10_results_architecture.py",
    "scripts/run_stage9_11_results_drafting.py",
    "scripts/run_stage9_12_introduction_literature_binding.py",
    "scripts/run_stage9_13_discussion_interpretation_map.py",
    "scripts/run_stage9_14_discussion_drafting.py",
    "scripts/run_stage9_15_methods_architecture.py",
    "scripts/run_stage9_16_methods_drafting.py",
    "scripts/run_stage9_17_availability_assembly.py",
    "scripts/run_stage9_18_supplementary_methods.py",
    "scripts/run_stage9_19_supplementary_tables.py",
    "scripts/run_stage9_20_reference_audit.py",
    "scripts/run_stage9_21_cross_document_consistency.py",
    "scripts/run_stage9_22_statistical_language_audit.py",
    "manuscript/nature_methods/README.md",
    "manuscript/nature_methods/contracts/id_namespace.md",
    "manuscript/nature_methods/contracts/machine_gate_spec.md",
    "manuscript/nature_methods/contracts/atomic_write_protocol.md",
    "manuscript/nature_methods/contracts/stage9_project_binding.json",
    "manuscript/nature_methods/contracts/stage9_substage_registry.json",
    "manuscript/nature_methods/contracts/ledger_schema_map.json",
    "manuscript/nature_methods/figures/figures.manifest.yaml",
    "manuscript/nature_methods/gate_verdicts/9.-1.json",
    "tools/panelforge-figures/STAGE9_PLACEHOLDER.md",
]

EXPECTED_SUBSTAGES = []
for value in [
    "9.-1",
    *[f"9.{idx}" for idx in range(0, 7)],
    "9.6b",
    *[f"9.{idx}" for idx in range(7, 26)],
    "9.25b",
    *[f"9.{idx}" for idx in range(26, 30)],
]:
    if value not in EXPECTED_SUBSTAGES:
        EXPECTED_SUBSTAGES.append(value)

EXPECTED_SCHEMAS = {
    "claim_hierarchy",
    "paragraph_claim_ledger",
    "figure_to_claim_to_artifact",
    "methods_to_code",
    "citation_claim_ledger",
    "statistic_ledger",
    "supplementary_callout_ledger",
    "stage9_evidence_manifest",
    "stage7_output_contract",
    "reviewer_action_matrix",
    "live_numbers_diff",
    "limitations_ledger",
    "reproducibility_command_index",
}

ID_PREFIXES = [
    "CLM-",
    "PARA-",
    "FIG-",
    "SFIG-",
    "TBL-",
    "STBL-",
    "ART-",
    "REF-",
    "STAT-",
    "SUPP-",
    "MTH-",
]

FORBIDDEN_DRAFTS = [
    "figures/figure_legends.md",
    "audits/figure_legend_audit.md",
    "submission_package/submission_readiness_checklist.md",
    "submission_package/pi_review_packet.md",
    "stage9_completion_report.md",
]
FORBIDDEN_RENDER_SUFFIXES = {".png", ".pdf", ".svg"}
STAGE96B_RENDER_OUTPUTS = {
    f"figures/rendered/FIG-00{idx}/FIG-00{idx}.{suffix}"
    for idx in range(1, 7)
    for suffix in ("pdf", "png", "svg")
}


def _read_json(path: Path, failures: list[str]) -> Any:
    if not path.exists():
        failures.append(f"missing JSON: {path.relative_to(ROOT)}")
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        failures.append(f"invalid JSON {path.relative_to(ROOT)}: {exc}")
        return {}


def _schema_ok(path: Path, failures: list[str]) -> None:
    schema = _read_json(path, failures)
    if not isinstance(schema, dict):
        failures.append(f"schema is not an object: {path.relative_to(ROOT)}")
        return
    for key in ["$schema", "title", "type", "required", "properties"]:
        if key not in schema:
            failures.append(f"schema missing {key}: {path.relative_to(ROOT)}")
    if schema.get("type") != "object":
        failures.append(f"schema type is not object: {path.relative_to(ROOT)}")
    if not isinstance(schema.get("required"), list) or not schema.get("required"):
        failures.append(f"schema required list is empty: {path.relative_to(ROOT)}")
    if not isinstance(schema.get("properties"), dict) or not schema.get("properties"):
        failures.append(f"schema properties are empty: {path.relative_to(ROOT)}")


def check_stage9_scaffold(root: Path = ROOT) -> dict[str, object]:
    failures: list[str] = []
    warnings: list[str] = []
    workspace = root / WORKSPACE.relative_to(ROOT)

    for rel in REQUIRED_DIRS:
        if not (workspace / rel).is_dir():
            failures.append(f"missing Stage 9 directory: manuscript/nature_methods/{rel}")
    for rel in REQUIRED_REPO_DIRS:
        if not (root / rel).is_dir():
            failures.append(f"missing Stage 9 repo directory: {rel}")
    for rel in REQUIRED_FILES:
        if not (root / rel).exists():
            failures.append(f"missing Stage 9 scaffold file: {rel}")

    binding = _read_json(workspace / "contracts" / "stage9_project_binding.json", failures)
    for field in ["method_name", "software_name", "software_version", "archive_doi", "repo_url", "venue", "content_type"]:
        value = str(binding.get(field, ""))
        if not value or "<" in value or ">" in value:
            failures.append(f"project binding field is unresolved: {field}")
    if binding.get("method_name") != "RhoDyn" or binding.get("software_name") != "RhoDyn":
        failures.append("project binding must bind Stage 9 to RhoDyn")
    figure_engine = binding.get("figure_engine_binding", {}) if isinstance(binding.get("figure_engine_binding", {}), dict) else {}
    if figure_engine.get("name") != "panelforge-figures":
        failures.append("project binding must include the panelforge-figures engine")
    if figure_engine.get("pinned_ref") != "v3.14.1":
        failures.append("PanelForge pinned ref must remain v3.14.1")
    if figure_engine.get("version_doi") != "10.5281/zenodo.20811171":
        failures.append("PanelForge version DOI must be 10.5281/zenodo.20811171")
    if figure_engine.get("execution_status") not in {
        "not_cloned_not_installed_not_rendered",
        "rendered_by_transient_pinned_install_no_repo_clone",
    }:
        failures.append("PanelForge execution status must record either the scaffold state or the transient Stage 9.6b render state")

    registry = _read_json(workspace / "contracts" / "stage9_substage_registry.json", failures)
    substages = registry.get("substages", []) if isinstance(registry, dict) else []
    ids = [item.get("id") for item in substages if isinstance(item, dict)]
    if ids != EXPECTED_SUBSTAGES:
        failures.append(f"Stage 9 substage registry IDs do not match expected sequence: {ids}")
    for item in substages:
        if not isinstance(item, dict):
            continue
        for key in ["id", "title", "objective", "outputs", "gate_predicates", "status"]:
            if key not in item:
                failures.append(f"substage missing {key}: {item.get('id', '?')}")
        if not item.get("outputs") or not item.get("gate_predicates"):
            failures.append(f"substage lacks outputs or gate predicates: {item.get('id', '?')}")

    schema_map = _read_json(workspace / "contracts" / "ledger_schema_map.json", failures)
    schema_names = set(schema_map) if isinstance(schema_map, dict) else set()
    if schema_names != EXPECTED_SCHEMAS:
        failures.append(f"ledger schema map does not match expected schemas: {sorted(schema_names)}")
    for name in EXPECTED_SCHEMAS:
        _schema_ok(workspace / "contracts" / "ledger_schemas" / f"{name}.schema.json", failures)
    figure_schema = _read_json(workspace / "contracts" / "ledger_schemas" / "figure_to_claim_to_artifact.schema.json", failures)
    figure_properties = figure_schema.get("properties", {}) if isinstance(figure_schema, dict) else {}
    for field in ["recipe", "render_path", "engine_version", "engine_commit", "drift_ok", "rejected_alternative"]:
        if field not in figure_properties:
            failures.append(f"figure ledger schema missing PanelForge field: {field}")

    namespace = (workspace / "contracts" / "id_namespace.md").read_text(encoding="utf-8") if (workspace / "contracts" / "id_namespace.md").exists() else ""
    for prefix in ID_PREFIXES:
        if prefix not in namespace:
            failures.append(f"ID namespace missing prefix: {prefix}")

    gate_files = sorted(path.name for path in (workspace / "gate_verdicts").glob("*.json")) if (workspace / "gate_verdicts").exists() else []
    allowed_gate_files = {"9.-1.json", "9.0.json", "9.1.json", "9.2.json", "9.3.json", "9.4.json", "9.5.json", "9.6.json", "9.6b.json", "9.7.json", "9.8.json", "9.9.json", "9.10.json", "9.11.json", "9.12.json", "9.13.json", "9.14.json", "9.15.json", "9.16.json", "9.17.json", "9.18.json", "9.19.json", "9.20.json", "9.21.json", "9.22.json"}
    unexpected_gate_files = [name for name in gate_files if name not in allowed_gate_files]
    if unexpected_gate_files:
        failures.append(f"Stage 9 must not contain post-9.22 gate verdicts before authorization: {unexpected_gate_files}")
    if "9.-1.json" not in gate_files:
        failures.append(f"Stage 9 scaffold must contain the 9.-1 gate verdict, found: {gate_files}")
    stage9_0_started = "9.0.json" in gate_files
    stage9_1_started = "9.1.json" in gate_files
    stage9_2_started = "9.2.json" in gate_files
    stage9_3_started = "9.3.json" in gate_files
    stage9_4_started = "9.4.json" in gate_files
    stage9_5_started = "9.5.json" in gate_files
    stage9_6_started = "9.6.json" in gate_files
    stage9_6b_started = "9.6b.json" in gate_files
    stage9_7_started = "9.7.json" in gate_files
    stage9_8_started = "9.8.json" in gate_files
    stage9_9_started = "9.9.json" in gate_files
    stage9_10_started = "9.10.json" in gate_files
    stage9_11_started = "9.11.json" in gate_files
    stage9_12_started = "9.12.json" in gate_files
    stage9_13_started = "9.13.json" in gate_files
    stage9_14_started = "9.14.json" in gate_files
    stage9_15_started = "9.15.json" in gate_files
    stage9_16_started = "9.16.json" in gate_files
    stage9_17_started = "9.17.json" in gate_files
    stage9_18_started = "9.18.json" in gate_files
    stage9_19_started = "9.19.json" in gate_files
    stage9_20_started = "9.20.json" in gate_files
    stage9_21_started = "9.21.json" in gate_files
    stage9_22_started = "9.22.json" in gate_files
    gate = _read_json(workspace / "gate_verdicts" / "9.-1.json", failures)
    if gate.get("pass") is not True or gate.get("substage") != "9.-1":
        failures.append("Stage 9.-1 gate verdict must pass")
    checks = gate.get("checks", []) if isinstance(gate.get("checks"), list) else []
    if not checks or not all(item.get("passed") is True for item in checks if isinstance(item, dict)):
        failures.append("Stage 9.-1 gate checks must all pass")

    memory = _read_json(root / "docs" / "stage9_execution_memory.json", failures)
    for flag in ["manuscript_drafting_started", "evidence_intake_started", "citation_resolution_started", "cross_document_consistency_started", "statistical_language_audit_started", "live_number_audit_started", "submission_package_started"]:
        if flag == "evidence_intake_started" and stage9_0_started:
            if memory.get(flag) is not True:
                failures.append("Stage 9 execution memory must record evidence_intake_started=true after 9.0")
            continue
        if flag == "citation_resolution_started" and stage9_20_started:
            if memory.get(flag) is not True:
                failures.append("Stage 9 execution memory must record citation_resolution_started=true after 9.20")
            continue
        if flag == "cross_document_consistency_started" and stage9_21_started:
            if memory.get(flag) is not True:
                failures.append("Stage 9 execution memory must record cross_document_consistency_started=true after 9.21")
            continue
        if flag in {"statistical_language_audit_started", "live_number_audit_started"} and stage9_22_started:
            if memory.get(flag) is not True:
                failures.append(f"Stage 9 execution memory must record {flag}=true after 9.22")
            continue
        if memory.get(flag) is not False:
            failures.append(f"Stage 9 scaffold memory must keep {flag}=false")
    if memory.get("figure_engine_clone_started") is not False:
        failures.append("Stage 9 memory must not record a committed PanelForge clone")
    if stage9_6b_started:
        for flag in ["figure_engine_install_started", "figure_rendering_started"]:
            if memory.get(flag) is not True:
                failures.append(f"Stage 9 execution memory must record {flag}=true after 9.6b")
    else:
        for flag in ["figure_engine_install_started", "figure_rendering_started"]:
            if memory.get(flag) is not False:
                failures.append(f"Stage 9 scaffold memory must keep {flag}=false before 9.6b")
    expected_memory_status = (
        "stage9_22_statistical_language_audit_bound"
        if stage9_22_started
        else "stage9_21_cross_document_consistency_bound"
        if stage9_21_started
        else "stage9_20_reference_library_bound"
        if stage9_20_started
        else "stage9_19_supplementary_tables_bound"
        if stage9_19_started
        else "stage9_18_supplementary_methods_drafted"
        if stage9_18_started
        else "stage9_17_availability_assembled"
        if stage9_17_started
        else "stage9_16_methods_drafted"
        if stage9_16_started
        else "stage9_15_methods_architecture_registered"
        if stage9_15_started
        else "stage9_14_discussion_drafted"
        if stage9_14_started
        else "stage9_13_discussion_interpretation_mapped"
        if stage9_13_started
        else "stage9_12_introduction_literature_bound"
        if stage9_12_started
        else "stage9_11_results_draft_registered"
        if stage9_11_started
        else "stage9_10_results_architecture_registered"
        if stage9_10_started
        else "stage9_9_title_abstract_strategy_registered"
        if stage9_9_started
        else "stage9_8_section_contract_blueprint_registered"
        if stage9_8_started
        else "stage9_7_supplementary_display_plan_registered"
        if stage9_7_started
        else "stage9_6b_panelforge_rendering_registered"
        if stage9_6b_started
        else "stage9_6_figure_spine_registered"
        if stage9_6_started
        else "stage9_5_paragraph_claim_ledger_registered"
        if stage9_5_started
        else "stage9_4_claim_freeze_registered"
        if stage9_4_started
        else "stage9_3_narrative_spine_registered"
        if stage9_3_started
        else "stage9_2_methods_corpus_registered"
        if stage9_2_started
        else "stage9_1_guidance_registered"
        if stage9_1_started
        else "stage9_0_evidence_locked"
        if stage9_0_started
        else "scaffold_serialized_not_started"
    )
    if memory.get("status") != expected_memory_status:
        failures.append(f"Stage 9 execution memory must record {expected_memory_status}")
    if memory.get("next_substage_authorized") is not False:
        failures.append("Stage 9 downstream substages must not be auto-authorized")
    if stage9_17_started:
        for flag in ["availability_assembly_started", "reporting_summary_placeholder_started"]:
            if memory.get(flag) is not True:
                failures.append(f"Stage 9 execution memory must record {flag}=true after 9.17")
    if stage9_18_started and memory.get("supplementary_methods_started") is not True:
        failures.append("Stage 9 execution memory must record supplementary_methods_started=true after 9.18")
    if stage9_19_started:
        for flag in ["supplementary_tables_started", "source_data_binding_started"]:
            if memory.get(flag) is not True:
                failures.append(f"Stage 9 execution memory must record {flag}=true after 9.19")
    if stage9_20_started and memory.get("reference_library_started") is not True:
        failures.append("Stage 9 execution memory must record reference_library_started=true after 9.20")

    if stage9_0_started:
        stage9_0_gate = _read_json(workspace / "gate_verdicts" / "9.0.json", failures)
        if stage9_0_gate.get("pass") is not True or stage9_0_gate.get("substage") != "9.0":
            failures.append("Stage 9.0 gate verdict must pass when present")
        for rel in [
            "ledgers/stage9_evidence_manifest.csv",
            "ledgers/stage9_evidence_lock.md",
            "ledgers/stage7_output_contract.md",
        ]:
            if not (workspace / rel).exists():
                failures.append(f"Stage 9.0 evidence-lock output missing: {rel}")
    else:
        for rel in [
            "ledgers/stage9_evidence_manifest.csv",
            "ledgers/stage9_evidence_lock.md",
            "ledgers/stage7_output_contract.md",
        ]:
            if (workspace / rel).exists():
                failures.append(f"Stage 9 scaffold-only state must not contain evidence-lock output before 9.0: {rel}")

    if stage9_1_started:
        stage9_1_gate = _read_json(workspace / "gate_verdicts" / "9.1.json", failures)
        if stage9_1_gate.get("pass") is not True or stage9_1_gate.get("substage") != "9.1":
            failures.append("Stage 9.1 gate verdict must pass when present")
        for rel in [
            "refs/nature_methods_guidance_register.md",
            "audits/venue_policy_constraints.md",
        ]:
            if not (workspace / rel).exists():
                failures.append(f"Stage 9.1 venue-guidance output missing: {rel}")
        cache_dir = workspace / "refs" / "_cache"
        cache_texts = sorted(path.name for path in cache_dir.glob("*.txt")) if cache_dir.exists() else []
        cache_meta = sorted(path.name for path in cache_dir.glob("*.meta.json")) if cache_dir.exists() else []
        if len(cache_texts) != 7 or len(cache_meta) != 7:
            failures.append("Stage 9.1 must cache seven official source text files and seven metadata files")
        if memory.get("venue_guidance_started") is not True:
            failures.append("Stage 9 execution memory must record venue_guidance_started=true after 9.1")
    else:
        for rel in [
            "refs/nature_methods_guidance_register.md",
            "audits/venue_policy_constraints.md",
        ]:
            if (workspace / rel).exists():
                failures.append(f"Stage 9 state must not contain venue-guidance output before 9.1: {rel}")

    if stage9_2_started:
        stage9_2_gate = _read_json(workspace / "gate_verdicts" / "9.2.json", failures)
        if stage9_2_gate.get("pass") is not True or stage9_2_gate.get("substage") != "9.2":
            failures.append("Stage 9.2 gate verdict must pass when present")
        for rel in [
            "refs/representative_methods_papers.md",
            "audits/methods_paper_archetype_analysis.md",
        ]:
            if not (workspace / rel).exists():
                failures.append(f"Stage 9.2 methods-paper corpus output missing: {rel}")
        corpus_cache_dir = workspace / "refs" / "_cache" / "methods_corpus"
        corpus_cache = sorted(corpus_cache_dir.glob("*.crossref.json")) if corpus_cache_dir.exists() else []
        if len(corpus_cache) != 8:
            failures.append("Stage 9.2 must cache eight Crossref metadata files")
        if memory.get("representative_methods_corpus_started") is not True:
            failures.append("Stage 9 execution memory must record representative_methods_corpus_started=true after 9.2")
    else:
        for rel in [
            "refs/representative_methods_papers.md",
            "audits/methods_paper_archetype_analysis.md",
        ]:
            if (workspace / rel).exists():
                failures.append(f"Stage 9 state must not contain methods-paper corpus output before 9.2: {rel}")
        if (workspace / "refs" / "_cache" / "methods_corpus").exists():
            failures.append("Stage 9 state must not contain methods-paper cache before 9.2")

    if stage9_3_started:
        stage9_3_gate = _read_json(workspace / "gate_verdicts" / "9.3.json", failures)
        if stage9_3_gate.get("pass") is not True or stage9_3_gate.get("substage") != "9.3":
            failures.append("Stage 9.3 gate verdict must pass when present")
        for rel in [
            "stage9_narrative_spine.md",
            "audits/venue_fit_rationale.md",
        ]:
            if not (workspace / rel).exists():
                failures.append(f"Stage 9.3 narrative-spine output missing: {rel}")
        if stage9_3_gate.get("content_type") != "Article":
            failures.append("Stage 9.3 must retain Nature Methods Article as the content type")
        if memory.get("narrative_spine_started") is not True:
            failures.append("Stage 9 execution memory must record narrative_spine_started=true after 9.3")
    else:
        for rel in [
            "stage9_narrative_spine.md",
            "audits/venue_fit_rationale.md",
        ]:
            if (workspace / rel).exists():
                failures.append(f"Stage 9 state must not contain narrative-spine output before 9.3: {rel}")

    if stage9_4_started:
        stage9_4_gate = _read_json(workspace / "gate_verdicts" / "9.4.json", failures)
        if stage9_4_gate.get("pass") is not True or stage9_4_gate.get("substage") != "9.4":
            failures.append("Stage 9.4 gate verdict must pass when present")
        for rel in [
            "ledgers/claim_hierarchy.md",
            "ledgers/claim_hierarchy.csv",
            "ledgers/non_claims_and_scope_boundaries.md",
        ]:
            if not (workspace / rel).exists():
                failures.append(f"Stage 9.4 claim-freeze output missing: {rel}")
        if stage9_4_gate.get("claim_count") != 5:
            failures.append("Stage 9.4 must freeze five central method claims")
        if stage9_4_gate.get("non_claim_count", 0) < 5:
            failures.append("Stage 9.4 must include a non-empty non-claims ledger")
        if memory.get("claim_freeze_started") is not True:
            failures.append("Stage 9 execution memory must record claim_freeze_started=true after 9.4")
    else:
        for rel in [
            "ledgers/claim_hierarchy.md",
            "ledgers/claim_hierarchy.csv",
            "ledgers/non_claims_and_scope_boundaries.md",
        ]:
            if (workspace / rel).exists():
                failures.append(f"Stage 9 state must not contain claim-freeze output before 9.4: {rel}")

    if stage9_5_started:
        stage9_5_gate = _read_json(workspace / "gate_verdicts" / "9.5.json", failures)
        if stage9_5_gate.get("pass") is not True or stage9_5_gate.get("substage") != "9.5":
            failures.append("Stage 9.5 gate verdict must pass when present")
        for rel in [
            "ledgers/paragraph_claim_ledger.csv",
            "ledgers/claim_strength_rules.md",
        ]:
            if not (workspace / rel).exists():
                failures.append(f"Stage 9.5 paragraph-ledger output missing: {rel}")
        if stage9_5_gate.get("paragraph_count", 0) < 10:
            failures.append("Stage 9.5 must register paragraph-level claim rows")
        if stage9_5_gate.get("claim_count") != 5:
            failures.append("Stage 9.5 must preserve the five frozen claims")
        if memory.get("paragraph_claim_ledger_started") is not True:
            failures.append("Stage 9 execution memory must record paragraph_claim_ledger_started=true after 9.5")
    else:
        for rel in [
            "ledgers/paragraph_claim_ledger.csv",
            "ledgers/claim_strength_rules.md",
        ]:
            if (workspace / rel).exists():
                failures.append(f"Stage 9 state must not contain paragraph-ledger output before 9.5: {rel}")

    if stage9_6_started:
        stage9_6_gate = _read_json(workspace / "gate_verdicts" / "9.6.json", failures)
        if stage9_6_gate.get("pass") is not True or stage9_6_gate.get("substage") != "9.6":
            failures.append("Stage 9.6 gate verdict must pass when present")
        for rel in [
            "figures/main_figure_spine.md",
            "ledgers/figure_to_claim_to_artifact.csv",
            "figures/display_item_plan.md",
        ]:
            if not (workspace / rel).exists():
                failures.append(f"Stage 9.6 figure-spine output missing: {rel}")
        if stage9_6_gate.get("main_display_count") != 6:
            failures.append("Stage 9.6 must register six main display items")
        if stage9_6_gate.get("main_display_budget") != 6:
            failures.append("Stage 9.6 must preserve the sourced six-display-item budget")
        if memory.get("figure_spine_started") is not True:
            failures.append("Stage 9 execution memory must record figure_spine_started=true after 9.6")
    else:
        for rel in [
            "figures/main_figure_spine.md",
            "ledgers/figure_to_claim_to_artifact.csv",
            "figures/display_item_plan.md",
        ]:
            if (workspace / rel).exists():
                failures.append(f"Stage 9 state must not contain figure-spine output before 9.6: {rel}")

    if stage9_6b_started:
        stage9_6b_gate = _read_json(workspace / "gate_verdicts" / "9.6b.json", failures)
        if stage9_6b_gate.get("pass") is not True or stage9_6b_gate.get("substage") != "9.6b":
            failures.append("Stage 9.6b gate verdict must pass when present")
        for rel in [
            "figures/.panelforge_commit",
            "audits/panelforge_render_report.md",
        ]:
            if not (workspace / rel).exists():
                failures.append(f"Stage 9.6b render output missing: {rel}")
        rendered_outputs = {
            path.relative_to(workspace).as_posix()
            for path in (workspace / "figures" / "rendered").rglob("*")
            if path.is_file() and path.suffix.lower() in FORBIDDEN_RENDER_SUFFIXES
        }
        if rendered_outputs != STAGE96B_RENDER_OUTPUTS:
            failures.append(f"Stage 9.6b must contain exactly the expected rendered files: {sorted(rendered_outputs)}")
        manifest = workspace / "figures" / "figures.manifest.yaml"
        if manifest.exists() and "scaffold_placeholder_not_renderable" in manifest.read_text(encoding="utf-8"):
            failures.append("Stage 9.6b figure manifest must be renderable, not the scaffold placeholder")
    else:
        for rel in [
            "figures/.panelforge_commit",
            "audits/panelforge_render_report.md",
        ]:
            if (workspace / rel).exists():
                failures.append(f"Stage 9 state must not contain PanelForge render output before 9.6b: {rel}")
        rendered_outputs = [
            path.relative_to(workspace).as_posix()
            for path in (workspace / "figures" / "rendered").rglob("*")
            if path.is_file() and path.suffix.lower() in FORBIDDEN_RENDER_SUFFIXES
        ]
        if rendered_outputs:
            failures.append(f"Stage 9 state must not render panels before 9.6b: {rendered_outputs}")
        manifest = workspace / "figures" / "figures.manifest.yaml"
        if manifest.exists() and "scaffold_placeholder_not_renderable" not in manifest.read_text(encoding="utf-8"):
            failures.append("Stage 9 figure manifest must remain a non-renderable scaffold placeholder before 9.6b")

    if stage9_7_started:
        stage9_7_gate = _read_json(workspace / "gate_verdicts" / "9.7.json", failures)
        if stage9_7_gate.get("pass") is not True or stage9_7_gate.get("substage") != "9.7":
            failures.append("Stage 9.7 gate verdict must pass when present")
        for rel in [
            "supplementary/supplementary_item_plan.md",
            "ledgers/supplementary_callout_ledger.csv",
        ]:
            if not (workspace / rel).exists():
                failures.append(f"Stage 9.7 supplementary-plan output missing: {rel}")
        if stage9_7_gate.get("supplementary_item_count") != 9:
            failures.append("Stage 9.7 must register nine supplementary support items")
        if stage9_7_gate.get("essential_item_count", 0) < 6:
            failures.append("Stage 9.7 must keep the essential supplementary support set populated")
        try:
            manifest_payload = json.loads((workspace / "figures" / "figures.manifest.yaml").read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            failures.append(f"Stage 9.7 figure manifest is not valid JSON/YAML subset: {exc}")
            manifest_payload = {}
        supplementary_items = manifest_payload.get("supplementary_items", []) if isinstance(manifest_payload, dict) else []
        if len(supplementary_items) != 9:
            failures.append("Stage 9.7 figure manifest must contain nine supplementary planning rows")
        if any(item.get("render_status") != "not_rendered_stage9.7_plan_only" for item in supplementary_items if isinstance(item, dict)):
            failures.append("Stage 9.7 supplementary rows must remain non-rendered planning metadata")
        if memory.get("supplementary_display_planning_started") is not True:
            failures.append("Stage 9 execution memory must record supplementary_display_planning_started=true after 9.7")
    else:
        for rel in [
            "supplementary/supplementary_item_plan.md",
            "ledgers/supplementary_callout_ledger.csv",
        ]:
            if (workspace / rel).exists():
                failures.append(f"Stage 9 state must not contain supplementary-plan output before 9.7: {rel}")

    if stage9_8_started:
        stage9_8_gate = _read_json(workspace / "gate_verdicts" / "9.8.json", failures)
        if stage9_8_gate.get("pass") is not True or stage9_8_gate.get("substage") != "9.8":
            failures.append("Stage 9.8 gate verdict must pass when present")
        if not (workspace / "sections" / "section_contracts.md").exists():
            failures.append("Stage 9.8 section-contract output missing: sections/section_contracts.md")
        contract_body = (workspace / "sections" / "section_contracts.md").read_text(encoding="utf-8") if (workspace / "sections" / "section_contracts.md").exists() else ""
        if stage9_8_gate.get("section_contract_count") != 15:
            failures.append("Stage 9.8 must register fifteen section contracts")
        if stage9_8_gate.get("abstract_word_limit") != 150 or stage9_8_gate.get("abstract_unreferenced") is not True:
            failures.append("Stage 9.8 abstract contract must preserve the 150-word unreferenced budget")
        if stage9_8_gate.get("results_subheading_count", 0) < 4 or stage9_8_gate.get("methods_subheading_count", 0) < 4:
            failures.append("Stage 9.8 must require topical subheadings for Results and Online Methods")
        if stage9_8_gate.get("discussion_subheading_count") != 0:
            failures.append("Stage 9.8 must prohibit Discussion subheadings")
        for phrase in [
            "Abstract. Maximum 150 words and unreferenced.",
            "Results. Topical subheadings are required.",
            "Discussion. Subheadings are prohibited.",
            "Online Methods. Topical subheadings are required",
            "not a title draft",
            "not Results prose",
        ]:
            if phrase not in contract_body:
                failures.append(f"Stage 9.8 section contracts missing phrase: {phrase}")
        if memory.get("section_contracts_started") is not True:
            failures.append("Stage 9 execution memory must record section_contracts_started=true after 9.8")
    else:
        if (workspace / "sections" / "section_contracts.md").exists():
            failures.append("Stage 9 state must not contain section contracts before 9.8")

    if stage9_9_started:
        stage9_9_gate = _read_json(workspace / "gate_verdicts" / "9.9.json", failures)
        if stage9_9_gate.get("pass") is not True or stage9_9_gate.get("substage") != "9.9":
            failures.append("Stage 9.9 gate verdict must pass when present")
        for rel in [
            "sections/title_options.md",
            "sections/abstract_strategy.md",
            "sections/abstract.md",
        ]:
            if not (workspace / rel).exists():
                failures.append(f"Stage 9.9 front-matter output missing: {rel}")
        abstract_body = (workspace / "sections" / "abstract.md").read_text(encoding="utf-8") if (workspace / "sections" / "abstract.md").exists() else ""
        title_body = (workspace / "sections" / "title_options.md").read_text(encoding="utf-8") if (workspace / "sections" / "title_options.md").exists() else ""
        strategy_body = (workspace / "sections" / "abstract_strategy.md").read_text(encoding="utf-8") if (workspace / "sections" / "abstract_strategy.md").exists() else ""
        if stage9_9_gate.get("abstract_word_count", 999) > 150:
            failures.append("Stage 9.9 abstract must stay within the 150-word Nature Methods budget")
        if stage9_9_gate.get("abstract_unreferenced") is not True:
            failures.append("Stage 9.9 abstract must be unreferenced")
        if stage9_9_gate.get("title_option_count", 0) < 3:
            failures.append("Stage 9.9 must register multiple title options")
        if set(stage9_9_gate.get("abstract_claim_ids", [])) != {"CLM-0001", "CLM-0002", "CLM-0003", "CLM-0004", "CLM-0005"}:
            failures.append("Stage 9.9 abstract must map to the five frozen CLM identifiers")
        for phrase in [
            "RhoDyn infers residence states in live-cell perturbation data",
            "preferred working option",
            "150 words",
            "unreferenced",
            "CLM-0001;CLM-0002;CLM-0003;CLM-0004",
            "Live-cell perturbation experiments",
            "not a complete manuscript",
        ]:
            combined = "\n".join([title_body, strategy_body, abstract_body])
            if phrase not in combined:
                failures.append(f"Stage 9.9 front-matter surfaces missing phrase: {phrase}")
        if memory.get("title_abstract_strategy_started") is not True:
            failures.append("Stage 9 execution memory must record title_abstract_strategy_started=true after 9.9")
    else:
        for rel in [
            "sections/title_options.md",
            "sections/abstract_strategy.md",
            "sections/abstract.md",
        ]:
            if (workspace / rel).exists():
                failures.append(f"Stage 9 state must not contain front-matter strategy output before 9.9: {rel}")

    if stage9_10_started:
        stage9_10_gate = _read_json(workspace / "gate_verdicts" / "9.10.json", failures)
        if stage9_10_gate.get("pass") is not True or stage9_10_gate.get("substage") != "9.10":
            failures.append("Stage 9.10 gate verdict must pass when present")
        if not (workspace / "sections" / "results_blueprint.md").exists():
            failures.append("Stage 9.10 Results architecture output missing: sections/results_blueprint.md")
        blueprint_body = (workspace / "sections" / "results_blueprint.md").read_text(encoding="utf-8") if (workspace / "sections" / "results_blueprint.md").exists() else ""
        if stage9_10_gate.get("results_unit_count") != 6:
            failures.append("Stage 9.10 must register six Results units")
        if stage9_10_gate.get("figure_ids") != ["FIG-001", "FIG-002", "FIG-003", "FIG-004", "FIG-005", "FIG-006"]:
            failures.append("Stage 9.10 Results units must follow FIG-001 through FIG-006")
        if set(stage9_10_gate.get("claim_ids", [])) != {"CLM-0001", "CLM-0002", "CLM-0003", "CLM-0004", "CLM-0005"}:
            failures.append("Stage 9.10 Results architecture must map to the five frozen CLM identifiers")
        for phrase in [
            "Results unit map",
            "RhoDyn defines residence-state inference as an executable method object",
            "Synthetic benchmarks separate residence structure from simpler summaries",
            "Public live-cell trajectories test residence-amplitude separation beyond the reference use case",
            "Endpoint demonstrations link bounded coupling, reserve-like buffering, and routed-output alternatives",
            "Held-out contexts expose bounded-coupling pass and inconclusive regimes",
            "Software parity and archive reproduction make the method inspectable",
            "Allowed conclusion",
            "Prohibited overclaim",
            "not Results prose",
        ]:
            if phrase not in blueprint_body:
                failures.append(f"Stage 9.10 Results blueprint missing phrase: {phrase}")
        if memory.get("results_architecture_started") is not True:
            failures.append("Stage 9 execution memory must record results_architecture_started=true after 9.10")
    else:
        if (workspace / "sections" / "results_blueprint.md").exists():
            failures.append("Stage 9 state must not contain Results architecture output before 9.10: sections/results_blueprint.md")

    if stage9_11_started:
        stage9_11_gate = _read_json(workspace / "gate_verdicts" / "9.11.json", failures)
        if stage9_11_gate.get("pass") is not True or stage9_11_gate.get("substage") != "9.11":
            failures.append("Stage 9.11 gate verdict must pass when present")
        results_path = workspace / "sections" / "results.md"
        if not results_path.exists():
            failures.append("Stage 9.11 Results draft output missing: sections/results.md")
            results_body = ""
        else:
            results_body = results_path.read_text(encoding="utf-8")
        if stage9_11_gate.get("paragraph_count") != 6:
            failures.append("Stage 9.11 must register six Results paragraphs")
        if stage9_11_gate.get("figure_callouts") != ["Fig. 1", "Fig. 2", "Fig. 3", "Fig. 4", "Fig. 5", "Fig. 6"]:
            failures.append("Stage 9.11 figure callouts must follow Fig. 1 through Fig. 6")
        if set(stage9_11_gate.get("claim_ids", [])) != {"CLM-0001", "CLM-0002", "CLM-0003", "CLM-0004", "CLM-0005"}:
            failures.append("Stage 9.11 Results draft must map to the five frozen CLM identifiers")
        for phrase in [
            "# Results",
            "Fig. 1a",
            "Fig. 6e",
            "PARA-RESULTS-001",
            "PARA-RESULTS-006",
            "bounded-coupling",
            "reserve-like",
            "routed-output",
            "cross-surface reproducibility",
        ]:
            if phrase not in results_body:
                failures.append(f"Stage 9.11 Results draft missing phrase: {phrase}")
        if memory.get("results_drafting_started") is not True:
            failures.append("Stage 9 execution memory must record results_drafting_started=true after 9.11")
    else:
        if (workspace / "sections" / "results.md").exists():
            failures.append("Stage 9 state must not contain Results draft output before 9.11: sections/results.md")

    if stage9_12_started:
        stage9_12_gate = _read_json(workspace / "gate_verdicts" / "9.12.json", failures)
        if stage9_12_gate.get("pass") is not True or stage9_12_gate.get("substage") != "9.12":
            failures.append("Stage 9.12 gate verdict must pass when present")
        intro_path = workspace / "sections" / "introduction.md"
        ledger_path = workspace / "refs" / "introduction_citation_ledger.csv"
        if not intro_path.exists():
            failures.append("Stage 9.12 Introduction output missing: sections/introduction.md")
            intro_body = ""
        else:
            intro_body = intro_path.read_text(encoding="utf-8")
        if not ledger_path.exists():
            failures.append("Stage 9.12 citation ledger output missing: refs/introduction_citation_ledger.csv")
            ledger_body = ""
        else:
            ledger_body = ledger_path.read_text(encoding="utf-8")
        word_count = stage9_12_gate.get("introduction_word_count", 0)
        if not (450 <= word_count <= 650):
            failures.append("Stage 9.12 Introduction must remain within the 450-650 word contract")
        if stage9_12_gate.get("citation_count") != 11:
            failures.append("Stage 9.12 Introduction must cite the eleven resolved reference IDs")
        if stage9_12_gate.get("review_source_share", 1.0) > stage9_12_gate.get("review_source_threshold", 0.25):
            failures.append("Stage 9.12 review-source share must remain under threshold")
        if stage9_12_gate.get("next_substage") != "9.13":
            failures.append("Stage 9.12 gate must point to Stage 9.13")
        for phrase in [
            "REF-0001",
            "REF-0011",
            "residence-state",
            "bounded-coupling",
            "reserve-like",
            "routed-output",
            "reproducibility",
        ]:
            if phrase not in intro_body:
                failures.append(f"Stage 9.12 Introduction missing phrase: {phrase}")
        for phrase in ["ref_id", "doi_or_pmid", "source_type", "resolved"]:
            if phrase not in ledger_body:
                failures.append(f"Stage 9.12 citation ledger missing field: {phrase}")
        if memory.get("introduction_literature_binding_started") is not True:
            failures.append("Stage 9 execution memory must record introduction_literature_binding_started=true after 9.12")
    else:
        for rel in [
            "sections/introduction.md",
            "refs/introduction_citation_ledger.csv",
        ]:
            if (workspace / rel).exists():
                failures.append(f"Stage 9 state must not contain Introduction literature-binding output before 9.12: {rel}")

    if stage9_13_started:
        stage9_13_gate = _read_json(workspace / "gate_verdicts" / "9.13.json", failures)
        if stage9_13_gate.get("pass") is not True or stage9_13_gate.get("substage") != "9.13":
            failures.append("Stage 9.13 gate verdict must pass when present")
        blueprint_path = workspace / "sections" / "discussion_blueprint.md"
        if not blueprint_path.exists():
            failures.append("Stage 9.13 Discussion map output missing: sections/discussion_blueprint.md")
            blueprint_body = ""
        else:
            blueprint_body = blueprint_path.read_text(encoding="utf-8")
        if stage9_13_gate.get("paragraph_count") != 5:
            failures.append("Stage 9.13 must register five Discussion map paragraphs")
        if stage9_13_gate.get("next_substage") != "9.14":
            failures.append("Stage 9.13 gate must point to Stage 9.14")
        for phrase in [
            "declared biological window",
            "not a causal mechanism",
            "inconclusive",
            "reserve-like",
            "measured endpoint",
            "direct biochemical interactions",
            "not a new biological result",
        ]:
            if phrase not in blueprint_body:
                failures.append(f"Stage 9.13 Discussion map missing phrase: {phrase}")
        if any(line.startswith("#") for line in "\n".join(line for line in blueprint_body.splitlines() if not line.startswith("<!--")).splitlines()):
            failures.append("Stage 9.13 Discussion map must not contain markdown subheadings")
        if memory.get("discussion_interpretation_map_started") is not True:
            failures.append("Stage 9 execution memory must record discussion_interpretation_map_started=true after 9.13")
    else:
        if (workspace / "sections" / "discussion_blueprint.md").exists():
            failures.append("Stage 9 state must not contain Discussion map output before 9.13: sections/discussion_blueprint.md")

    if stage9_14_started:
        stage9_14_gate = _read_json(workspace / "gate_verdicts" / "9.14.json", failures)
        if stage9_14_gate.get("pass") is not True or stage9_14_gate.get("substage") != "9.14":
            failures.append("Stage 9.14 gate verdict must pass when present")
        discussion_path = workspace / "sections" / "discussion.md"
        if not discussion_path.exists():
            failures.append("Stage 9.14 Discussion output missing: sections/discussion.md")
            discussion_body = ""
        else:
            discussion_body = discussion_path.read_text(encoding="utf-8")
        if not (650 <= stage9_14_gate.get("discussion_word_count", 0) <= 900):
            failures.append("Stage 9.14 Discussion must remain within the 650-900 word contract")
        if stage9_14_gate.get("paragraph_count") != 5:
            failures.append("Stage 9.14 must register five Discussion paragraphs")
        if stage9_14_gate.get("next_substage") != "9.15":
            failures.append("Stage 9.14 gate must point to Stage 9.15")
        for phrase in [
            "Future directions",
            "not a causal mechanism",
            "inconclusive",
            "reserve-like",
            "not a new biological result",
            "not an automatic mechanism-discovery engine",
        ]:
            if phrase not in discussion_body:
                failures.append(f"Stage 9.14 Discussion missing phrase: {phrase}")
        if any(line.startswith("#") for line in "\n".join(line for line in discussion_body.splitlines() if not line.startswith("<!--")).splitlines()):
            failures.append("Stage 9.14 Discussion must not contain markdown subheadings")
        if memory.get("discussion_drafting_started") is not True:
            failures.append("Stage 9 execution memory must record discussion_drafting_started=true after 9.14")
    else:
        if (workspace / "sections" / "discussion.md").exists():
            failures.append("Stage 9 state must not contain Discussion draft output before 9.14: sections/discussion.md")

    if stage9_15_started:
        stage9_15_gate = _read_json(workspace / "gate_verdicts" / "9.15.json", failures)
        if stage9_15_gate.get("pass") is not True or stage9_15_gate.get("substage") != "9.15":
            failures.append("Stage 9.15 gate verdict must pass when present")
        methods_blueprint_path = workspace / "sections" / "methods_blueprint.md"
        methods_ledger_path = workspace / "ledgers" / "methods_to_code_ledger.csv"
        if not methods_blueprint_path.exists():
            failures.append("Stage 9.15 Methods architecture output missing: sections/methods_blueprint.md")
            methods_blueprint_body = ""
        else:
            methods_blueprint_body = methods_blueprint_path.read_text(encoding="utf-8")
        if not methods_ledger_path.exists():
            failures.append("Stage 9.15 methods-to-code ledger missing: ledgers/methods_to_code_ledger.csv")
            methods_ledger_body = ""
        else:
            methods_ledger_body = methods_ledger_path.read_text(encoding="utf-8")
        if stage9_15_gate.get("methods_statement_count", 0) < 6:
            failures.append("Stage 9.15 must register at least six Methods statements")
        if stage9_15_gate.get("methods_subheading_count") != 6:
            failures.append("Stage 9.15 must preserve six Online Methods subheadings")
        if stage9_15_gate.get("ledger_row_count") != stage9_15_gate.get("methods_statement_count"):
            failures.append("Stage 9.15 ledger row count must match Methods statement count")
        if stage9_15_gate.get("next_substage") != "9.16":
            failures.append("Stage 9.15 gate must point to Stage 9.16")
        for phrase in [
            "dataset_version=",
            "dataset_date=",
            "Input schemas and preprocessing",
            "Residence windows and amplitude comparators",
            "Bounded-coupling and uncertainty decisions",
            "Reserve-like endpoint construction",
            "Routed-output model comparison",
            "Software surfaces, versioning, and reproducibility",
            "not proof that all coupling is absent",
            "not direct assays of unmeasured biological reserve capacity",
            "does not identify direct biochemical interactions",
        ]:
            if phrase not in methods_blueprint_body and phrase not in methods_ledger_body:
                failures.append(f"Stage 9.15 Methods architecture missing phrase: {phrase}")
        for field in ["methods_stmt_id", "art_id", "repo_path", "commit", "command"]:
            if field not in methods_ledger_body:
                failures.append(f"Stage 9.15 methods-to-code ledger missing field: {field}")
        if memory.get("methods_architecture_started") is not True:
            failures.append("Stage 9 execution memory must record methods_architecture_started=true after 9.15")
        if not stage9_16_started and memory.get("methods_drafting_started") is not False:
            failures.append("Stage 9 execution memory must keep methods_drafting_started=false after 9.15")
    else:
        for rel in [
            "sections/methods_blueprint.md",
            "ledgers/methods_to_code_ledger.csv",
        ]:
            if (workspace / rel).exists():
                failures.append(f"Stage 9 state must not contain Methods architecture output before 9.15: {rel}")

    if stage9_16_started:
        stage9_16_gate = _read_json(workspace / "gate_verdicts" / "9.16.json", failures)
        methods_path = workspace / "sections" / "methods.md"
        if stage9_16_gate.get("pass") is not True or stage9_16_gate.get("substage") != "9.16":
            failures.append("Stage 9.16 gate verdict must pass when present")
        if stage9_16_gate.get("next_substage") != "9.17":
            failures.append("Stage 9.16 gate must point to Stage 9.17")
        if not (900 <= stage9_16_gate.get("methods_word_count", 0) <= 3000):
            failures.append("Stage 9.16 Methods word count must remain within the 900-3000 word contract")
        expected_methods_ids = {f"MTH-{idx:04d}" for idx in range(1, 10)}
        if set(stage9_16_gate.get("methods_statement_ids", [])) != expected_methods_ids:
            failures.append("Stage 9.16 gate must cover MTH-0001 through MTH-0009")
        if stage9_16_gate.get("software_version") != "v0.1.0":
            failures.append("Stage 9.16 gate must preserve RhoDyn v0.1.0")
        if not methods_path.exists():
            failures.append("Stage 9.16 Methods output missing: sections/methods.md")
            methods_body = ""
        else:
            methods_body = methods_path.read_text(encoding="utf-8")
        visible_methods = "\n".join(line for line in methods_body.splitlines() if not line.startswith("<!--"))
        for phrase in [
            "Input schemas and preprocessing",
            "Residence windows and amplitude comparators",
            "Bounded-coupling and uncertainty decisions",
            "Reserve-like endpoint construction",
            "Routed-output model comparison",
            "Software surfaces, versioning, and reproducibility",
            "RhoDyn v0.1.0",
            "stage7.8-methods-readiness@242f06c49e8310b81ac1c06a270bb6810f3f4cfc",
            "not proof that all coupling is absent",
            "not direct assays of unmeasured biological reserve capacity",
            "does not identify direct biochemical interactions",
        ]:
            if phrase not in methods_body:
                failures.append(f"Stage 9.16 Methods draft missing phrase: {phrase}")
        if re.search(r"\b(MTH|ART|CLM)-\d{4}\b", visible_methods):
            failures.append("Stage 9.16 Methods draft must hide internal IDs from visible reader-facing prose")
        if memory.get("methods_drafting_started") is not True:
            failures.append("Stage 9 execution memory must record methods_drafting_started=true after 9.16")
    else:
        if (workspace / "sections" / "methods.md").exists():
            failures.append("Stage 9 state must not contain Methods draft output before 9.16: sections/methods.md")

    if stage9_17_started:
        stage9_17_gate = _read_json(workspace / "gate_verdicts" / "9.17.json", failures)
        data_path = workspace / "sections" / "data_availability.md"
        code_path = workspace / "sections" / "code_availability.md"
        command_path = workspace / "ledgers" / "reproducibility_command_index.md"
        reporting_path = workspace / "submission_package" / "reporting_summary_REQUIRED.md"
        if stage9_17_gate.get("pass") is not True or stage9_17_gate.get("substage") != "9.17":
            failures.append("Stage 9.17 gate verdict must pass when present")
        if stage9_17_gate.get("next_substage") != "9.18":
            failures.append("Stage 9.17 gate must point to Stage 9.18")
        if stage9_17_gate.get("software_version") != "v0.1.0":
            failures.append("Stage 9.17 gate must preserve RhoDyn v0.1.0")
        if stage9_17_gate.get("release_commit") != "4b1211cadd1fb3af34a1ec3e21f62383ffd9e368":
            failures.append("Stage 9.17 must pin the v0.1.0 release commit")
        if stage9_17_gate.get("software_version_doi") != "10.5281/zenodo.21036616":
            failures.append("Stage 9.17 must record the RhoDyn version DOI")
        if stage9_17_gate.get("software_concept_doi") != "10.5281/zenodo.21036615":
            failures.append("Stage 9.17 must record the RhoDyn concept DOI")
        if stage9_17_gate.get("panel_engine_version_doi") != "10.5281/zenodo.20811171":
            failures.append("Stage 9.17 must record the PanelForge version DOI")
        if stage9_17_gate.get("panel_engine_render_command") != "figures render manuscript/nature_methods/figures/figures.manifest.yaml":
            failures.append("Stage 9.17 must record the PanelForge render command")
        if stage9_17_gate.get("reporting_summary_required") is not True:
            failures.append("Stage 9.17 must register Reporting Summary as required")
        if stage9_17_gate.get("command_count", 0) < 10:
            failures.append("Stage 9.17 reproducibility command index must include the main regeneration routes")
        for rel, path in [
            ("sections/data_availability.md", data_path),
            ("sections/code_availability.md", code_path),
            ("ledgers/reproducibility_command_index.md", command_path),
            ("submission_package/reporting_summary_REQUIRED.md", reporting_path),
        ]:
            if not path.exists():
                failures.append(f"Stage 9.17 availability output missing: {rel}")
        data_body = data_path.read_text(encoding="utf-8") if data_path.exists() else ""
        code_body = code_path.read_text(encoding="utf-8") if code_path.exists() else ""
        command_body = command_path.read_text(encoding="utf-8") if command_path.exists() else ""
        reporting_body = reporting_path.read_text(encoding="utf-8") if reporting_path.exists() else ""
        combined = "\n".join([data_body, code_body, command_body, reporting_body])
        for phrase in [
            "https://github.com/renatosocodato/rhodyn",
            "4b1211cadd1fb3af34a1ec3e21f62383ffd9e368",
            "https://doi.org/10.5281/zenodo.21036616",
            "https://doi.org/10.5281/zenodo.21036615",
            "https://doi.org/10.5281/zenodo.14907827",
            "https://doi.org/10.5281/zenodo.5836623",
            "https://doi.org/10.5281/zenodo.10011861",
            "https://github.com/renatosocodato/windowed_rhoA_model",
            "e63cc93a4b23d8b3d27cf25136b00d53fa6144f4",
            "https://doi.org/10.5281/zenodo.19796406",
            "https://doi.org/10.5281/zenodo.20811171",
            "figures render manuscript/nature_methods/figures/figures.manifest.yaml",
            "Reporting Summary REQUIRED",
            "not the completed journal form",
        ]:
            if phrase not in combined:
                failures.append(f"Stage 9.17 availability surfaces missing phrase: {phrase}")
        for phrase in [
            "upon request",
            "available on request",
            "/" + "Users/",
            "/" + "Volumes/",
            "Library/" + "LaunchAgents",
            "s" + "k-",
            "g" + "hp_",
            "github" + "_pat_",
        ]:
            if phrase.lower() in combined.lower():
                failures.append(f"Stage 9.17 availability surfaces contain forbidden phrase: {phrase}")
        if "PyPI publication is not claimed" not in code_body:
            failures.append("Stage 9.17 Code availability must keep PyPI unclaimed for v0.1.0")
    else:
        for rel in [
            "sections/data_availability.md",
            "sections/code_availability.md",
            "ledgers/reproducibility_command_index.md",
            "submission_package/reporting_summary_REQUIRED.md",
        ]:
            if (workspace / rel).exists():
                failures.append(f"Stage 9 state must not contain availability output before 9.17: {rel}")

    if stage9_18_started:
        stage9_18_gate = _read_json(workspace / "gate_verdicts" / "9.18.json", failures)
        supplementary_path = workspace / "supplementary" / "supplementary_methods.md"
        if stage9_18_gate.get("pass") is not True or stage9_18_gate.get("substage") != "9.18":
            failures.append("Stage 9.18 gate verdict must pass when present")
        if stage9_18_gate.get("next_substage") != "9.19":
            failures.append("Stage 9.18 gate must point to Stage 9.19")
        if stage9_18_gate.get("supplementary_methods_section_count") != 7:
            failures.append("Stage 9.18 must register seven Supplementary Methods sections")
        if set(stage9_18_gate.get("supp_ids", [])) != {f"SUPP-{idx:03d}" for idx in range(1, 10)}:
            failures.append("Stage 9.18 must cover SUPP-001 through SUPP-009")
        if set(stage9_18_gate.get("claim_ids", [])) != {"CLM-0001", "CLM-0002", "CLM-0003", "CLM-0004", "CLM-0005"}:
            failures.append("Stage 9.18 must stay within the five frozen CLM identifiers")
        if not supplementary_path.exists():
            failures.append("Stage 9.18 Supplementary Methods output missing: supplementary/supplementary_methods.md")
            supplementary_body = ""
        else:
            supplementary_body = supplementary_path.read_text(encoding="utf-8")
        visible_supplementary = "\n".join(line for line in supplementary_body.splitlines() if not line.startswith("<!--"))
        for phrase in [
            "# Supplementary Methods",
            "Input contracts, method definitions, and truth cases",
            "Public live-cell signaling adapters",
            "Bounded-coupling decisions and held-out contexts",
            "Reserve-like endpoint construction",
            "Routed-output reduced-architecture comparison",
            "Software parity, export bundles, and archive reproduction",
            "Non-example cases and interpretation boundaries",
            "not independent biological evidence",
            "not proof that all coupling is absent",
            "not direct assays of unmeasured biological reserve capacity",
            "does not identify direct biochemical interactions",
            "does not imply PyPI publication",
            "not a universal biological rule",
        ]:
            if phrase not in supplementary_body:
                failures.append(f"Stage 9.18 Supplementary Methods missing phrase: {phrase}")
        for phrase in [
            "universal residence law",
            "automatic mechanism-discovery",
            "true biological reserve",
            "literal molecular edge",
            "absence of all coupling",
            "private-data reproduction claim",
            "PyPI publication is claimed",
        ]:
            if phrase.lower() in visible_supplementary.lower():
                failures.append(f"Stage 9.18 Supplementary Methods contains forbidden phrase: {phrase}")
        if re.search(r"\b(CLM|ART|SUPP|PARA|FIG|STBL|SFIG)-\d{3,4}\b", visible_supplementary):
            failures.append("Stage 9.18 Supplementary Methods must hide internal IDs from visible prose")
    else:
        if (workspace / "supplementary" / "supplementary_methods.md").exists():
            failures.append("Stage 9 state must not contain Supplementary Methods before 9.18: supplementary/supplementary_methods.md")

    if stage9_19_started:
        stage9_19_gate = _read_json(workspace / "gate_verdicts" / "9.19.json", failures)
        tables_path = workspace / "supplementary" / "supplementary_tables_plan.md"
        source_binding_path = workspace / "supplementary" / "source_data_binding_ledger.csv"
        statistic_ledger_path = workspace / "ledgers" / "statistic_ledger.csv"
        if stage9_19_gate.get("pass") is not True or stage9_19_gate.get("substage") != "9.19":
            failures.append("Stage 9.19 gate verdict must pass when present")
        if stage9_19_gate.get("next_substage") != "9.20":
            failures.append("Stage 9.19 gate must point to Stage 9.20")
        if stage9_19_gate.get("table_count") != 9:
            failures.append("Stage 9.19 must register nine supplementary table rows")
        if stage9_19_gate.get("statistic_row_count") != 19:
            failures.append("Stage 9.19 must register nineteen statistic rows")
        if set(stage9_19_gate.get("table_ids", [])) != {f"STBL-{idx:03d}" for idx in range(1, 10)}:
            failures.append("Stage 9.19 must cover STBL-001 through STBL-009")
        if set(stage9_19_gate.get("supp_ids", [])) != {f"SUPP-{idx:03d}" for idx in range(1, 10)}:
            failures.append("Stage 9.19 must cover SUPP-001 through SUPP-009")
        if set(stage9_19_gate.get("linked_figures", [])) != {f"FIG-{idx:03d}" for idx in range(1, 7)}:
            failures.append("Stage 9.19 must bind source tables to FIG-001 through FIG-006")
        for path, label in [
            (tables_path, "supplementary/supplementary_tables_plan.md"),
            (source_binding_path, "supplementary/source_data_binding_ledger.csv"),
            (statistic_ledger_path, "ledgers/statistic_ledger.csv"),
        ]:
            if not path.exists():
                failures.append(f"Stage 9.19 output missing: {label}")
        if tables_path.exists():
            tables_body = tables_path.read_text(encoding="utf-8")
            for phrase in [
                "Supplementary table and source-data binding plan",
                "Table evidence map",
                "Every planned table has a main-text callout route",
                "Every table references one or more statistic IDs",
                "Every table also records a figure-source mapping",
                "do not add new biological demonstrations",
                "turn model-derived coordinates into direct biological endpoints",
            ]:
                if phrase not in tables_body:
                    failures.append(f"Stage 9.19 table plan missing phrase: {phrase}")
        if source_binding_path.exists():
            with source_binding_path.open(newline="", encoding="utf-8") as handle:
                source_rows = list(csv.DictReader(handle))
            if len(source_rows) != 9:
                failures.append("Stage 9.19 source-data binding ledger must contain nine rows")
            covered_figures = {fig_id for row in source_rows for fig_id in row.get("linked_main_figures", "").split(";") if fig_id}
            if covered_figures != {f"FIG-{idx:03d}" for idx in range(1, 7)}:
                failures.append("Stage 9.19 source-data binding ledger must cover all six main figures")
            for row in source_rows:
                for field in ["callout_location", "role", "stat_ids", "source_artifacts", "source_paths", "panelforge_recipe", "render_paths", "interpretation_boundary"]:
                    if not row.get(field):
                        failures.append(f"Stage 9.19 source-data row {row.get('table_id')} missing {field}")
                for render_path in [item for item in row.get("render_paths", "").split(";") if item]:
                    if not (root / render_path).exists():
                        failures.append(f"Stage 9.19 render path is missing: {render_path}")
        if statistic_ledger_path.exists():
            with statistic_ledger_path.open(newline="", encoding="utf-8") as handle:
                stat_rows = list(csv.DictReader(handle))
            if len(stat_rows) != 19:
                failures.append("Stage 9.19 statistic ledger must contain nineteen rows")
            if {row.get("stat_id", "") for row in stat_rows} != {f"STAT-{idx:04d}" for idx in range(1, 20)}:
                failures.append("Stage 9.19 statistic ledger must cover STAT-0001 through STAT-0019")
            for row in stat_rows:
                for field in ["art_id", "fig_id", "value", "ci", "n", "test", "source_command", "manuscript_locations"]:
                    if not row.get(field):
                        failures.append(f"Stage 9.19 statistic row {row.get('stat_id')} missing {field}")
    else:
        for rel in [
            "supplementary/supplementary_tables_plan.md",
            "supplementary/source_data_binding_ledger.csv",
            "ledgers/statistic_ledger.csv",
        ]:
            if (workspace / rel).exists():
                failures.append(f"Stage 9 state must not contain supplementary table binding before 9.19: {rel}")

    if stage9_20_started:
        stage9_20_gate = _read_json(workspace / "gate_verdicts" / "9.20.json", failures)
        references_path = workspace / "refs" / "references.bib"
        citation_ledger_path = workspace / "refs" / "citation_claim_ledger.csv"
        reference_audit_path = workspace / "audits" / "reference_audit.md"
        if stage9_20_gate.get("pass") is not True or stage9_20_gate.get("substage") != "9.20":
            failures.append("Stage 9.20 gate verdict must pass when present")
        if stage9_20_gate.get("next_substage") != "9.21":
            failures.append("Stage 9.20 gate must point to Stage 9.21")
        if stage9_20_gate.get("reference_count") != 13:
            failures.append("Stage 9.20 must register thirteen references")
        if stage9_20_gate.get("reference_cap") != 50:
            failures.append("Stage 9.20 must retain the Nature Methods reference cap")
        expected_refs = {f"REF-{idx:04d}" for idx in range(1, 14)}
        if set(stage9_20_gate.get("ref_ids", [])) != expected_refs:
            failures.append("Stage 9.20 must cover REF-0001 through REF-0013")
        for path, label in [
            (references_path, "refs/references.bib"),
            (citation_ledger_path, "refs/citation_claim_ledger.csv"),
            (reference_audit_path, "audits/reference_audit.md"),
        ]:
            if not path.exists():
                failures.append(f"Stage 9.20 output missing: {label}")
        if references_path.exists():
            references_body = references_path.read_text(encoding="utf-8")
            for ref_id in sorted(expected_refs):
                if f"{{{ref_id}," not in references_body:
                    failures.append(f"Stage 9.20 references.bib missing entry for {ref_id}")
            for phrase in [
                "10.1038/s41587-019-0071-9",
                "10.5281/zenodo.14907827",
                "10.5281/zenodo.21036616",
                "10.5281/zenodo.20811171",
            ]:
                if phrase not in references_body:
                    failures.append(f"Stage 9.20 references.bib missing DOI: {phrase}")
        if citation_ledger_path.exists():
            with citation_ledger_path.open(newline="", encoding="utf-8") as handle:
                citation_rows = list(csv.DictReader(handle))
            if len(citation_rows) != 13:
                failures.append("Stage 9.20 citation-claim ledger must contain thirteen rows")
            if {row.get("ref_id", "") for row in citation_rows} != expected_refs:
                failures.append("Stage 9.20 citation-claim ledger must cover REF-0001 through REF-0013")
            source_types = {row.get("source_type", "") for row in citation_rows}
            if not {"methods", "dataset", "software"} <= source_types:
                failures.append("Stage 9.20 citation-claim ledger must include methods, dataset, and software source types")
            for row in citation_rows:
                for field in ["claim_id", "doi_or_pmid", "resolved", "access_date", "source_type", "paragraph_ids", "support_role", "retraction_check"]:
                    if not row.get(field):
                        failures.append(f"Stage 9.20 citation row {row.get('ref_id')} missing {field}")
                if row.get("resolved") != "true":
                    failures.append(f"Stage 9.20 citation row {row.get('ref_id')} is not resolved")
                if not row.get("doi_or_pmid", "").startswith("10."):
                    failures.append(f"Stage 9.20 citation row {row.get('ref_id')} lacks DOI-form identifier")
                if row.get("retraction_check") not in {"clear", "not_applicable_zenodo_record"}:
                    failures.append(f"Stage 9.20 citation row {row.get('ref_id')} has unresolved retraction status")
        if reference_audit_path.exists():
            audit_body = reference_audit_path.read_text(encoding="utf-8")
            for phrase in [
                "Reference count. 13 of 50",
                "DOI-resolved references. 13 of 13",
                "Retraction-check clear or not applicable. 13 of 13",
                "Source-type counts. dataset=3; methods=8; software=2",
                "does not add a new biological demonstration",
                "does not replace the later cross-document consistency audit",
            ]:
                if phrase not in audit_body:
                    failures.append(f"Stage 9.20 reference audit missing phrase: {phrase}")
        cache_dir = workspace / "refs" / "_cache" / "reference_library"
        cache_files = sorted(cache_dir.glob("*.json")) if cache_dir.exists() else []
        if len(cache_files) < 13:
            failures.append("Stage 9.20 must cache DOI metadata and relation checks for reference-library entries")
    else:
        for rel in [
            "refs/references.bib",
            "refs/citation_claim_ledger.csv",
            "audits/reference_audit.md",
            "refs/_cache/reference_library",
        ]:
            if (workspace / rel).exists():
                failures.append(f"Stage 9 state must not contain reference-library output before 9.20: {rel}")

    if stage9_21_started:
        stage9_21_gate = _read_json(workspace / "gate_verdicts" / "9.21.json", failures)
        cross_document_audit_path = workspace / "audits" / "cross_document_consistency_audit.md"
        if stage9_21_gate.get("pass") is not True or stage9_21_gate.get("substage") != "9.21":
            failures.append("Stage 9.21 gate verdict must pass when present")
        if stage9_21_gate.get("next_substage") != "9.22":
            failures.append("Stage 9.21 gate must point to Stage 9.22")
        expected_921_counts = {
            "claim_count": 5,
            "figure_count": 6,
            "statistic_count": 19,
            "reference_count": 13,
            "source_data_table_count": 9,
        }
        for field, expected in expected_921_counts.items():
            if stage9_21_gate.get(field) != expected:
                failures.append(f"Stage 9.21 gate must record {field}={expected}")
        for field in [
            "orphan_claims",
            "unknown_claim_refs",
            "orphan_figures",
            "unknown_figure_refs",
            "orphan_statistics",
            "unknown_statistic_refs",
            "dangling_references",
            "unknown_paragraph_refs",
            "unknown_table_refs",
            "strength_mismatches",
            "missing_render_paths",
            "bad_engine_rows",
            "missing_source_paths",
            "missing_binding_render_paths",
        ]:
            if stage9_21_gate.get(field) not in ([], None):
                failures.append(f"Stage 9.21 gate must have empty {field}")
        expected_checks = {
            "stage_9_20_gate_passed",
            "orphan_claim_set_empty",
            "orphan_figure_set_empty",
            "orphan_statistic_set_empty",
            "dangling_reference_set_empty",
            "version_and_strength_coherence_hold",
            "no_statistical_language_legend_or_package_started",
            "scope_boundary_preserved",
        }
        actual_checks = {
            item.get("name")
            for item in stage9_21_gate.get("checks", [])
            if isinstance(item, dict) and item.get("passed") is True
        }
        if actual_checks != expected_checks:
            failures.append(f"Stage 9.21 checks do not match expected checks: {sorted(actual_checks)}")
        if not cross_document_audit_path.exists():
            failures.append("Stage 9.21 output missing: audits/cross_document_consistency_audit.md")
        else:
            audit_body = cross_document_audit_path.read_text(encoding="utf-8")
            for phrase in [
                "The cross-document joins passed",
                "no orphan claims, no orphan main figures, no orphan statistic IDs, and no dangling references",
                "Cross-document joins only",
                "does not test live-number phrasing",
                "does not write figure legends",
            ]:
                if phrase not in audit_body:
                    failures.append(f"Stage 9.21 audit missing phrase: {phrase}")
    else:
        for rel in [
            "audits/cross_document_consistency_audit.md",
        ]:
            if (workspace / rel).exists():
                failures.append(f"Stage 9 state must not contain cross-document consistency output before 9.21: {rel}")

    if stage9_22_started:
        stage9_22_gate = _read_json(workspace / "gate_verdicts" / "9.22.json", failures)
        statistical_audit_path = workspace / "audits" / "statistical_language_audit.md"
        live_diff_path = workspace / "audits" / "live_numbers_diff.csv"
        statistic_ledger_path = workspace / "ledgers" / "statistic_ledger.csv"
        figure_ledger_path = workspace / "ledgers" / "figure_to_claim_to_artifact.csv"
        if stage9_22_gate.get("pass") is not True or stage9_22_gate.get("substage") != "9.22":
            failures.append("Stage 9.22 gate verdict must pass when present")
        if stage9_22_gate.get("next_substage") != "9.23":
            failures.append("Stage 9.22 gate must point to Stage 9.23")
        expected_922_counts = {
            "statistic_count": 19,
            "live_number_row_count": 19,
        }
        for field, expected in expected_922_counts.items():
            if stage9_22_gate.get(field) != expected:
                failures.append(f"Stage 9.22 gate must record {field}={expected}")
        updated_stat_ids = stage9_22_gate.get("updated_stat_ids", [])
        if stage9_22_gate.get("updated_statistic_count") != len(updated_stat_ids):
            failures.append("Stage 9.22 gate updated_statistic_count must match updated_stat_ids")
        if any(stat_id != "STAT-0018" for stat_id in updated_stat_ids):
            failures.append("Stage 9.22 gate may only update STAT-0018")
        if stage9_22_gate.get("failed_stat_ids") not in ([], None):
            failures.append("Stage 9.22 gate must have no failed statistic IDs")
        if stage9_22_gate.get("unsupported_quantitative_statements") not in ([], None):
            failures.append("Stage 9.22 gate must have no unsupported reader-facing quantitative statements")
        if stage9_22_gate.get("figure_stat_id_map_complete") is not True:
            failures.append("Stage 9.22 gate must complete the figure statistic-ID map")
        equivalence_language = stage9_22_gate.get("equivalence_language", {})
        if not isinstance(equivalence_language, dict) or equivalence_language.get("passed") is not True:
            failures.append("Stage 9.22 gate must pass the equivalence-language bounds check")
        expected_checks = {
            "stage_9_21_gate_passed",
            "every_statistic_recomputes_within_tolerance",
            "quantitative_statements_have_statistic_ids",
            "equivalence_claims_state_bounds",
            "live_numbers_diff_written",
            "no_figure_legend_or_package_started",
            "scope_boundary_preserved",
        }
        actual_checks = {
            item.get("name")
            for item in stage9_22_gate.get("checks", [])
            if isinstance(item, dict) and item.get("passed") is True
        }
        if actual_checks != expected_checks:
            failures.append(f"Stage 9.22 checks do not match expected checks: {sorted(actual_checks)}")
        for path, label in [
            (statistical_audit_path, "audits/statistical_language_audit.md"),
            (live_diff_path, "audits/live_numbers_diff.csv"),
        ]:
            if not path.exists():
                failures.append(f"Stage 9.22 output missing: {label}")
        if live_diff_path.exists():
            with live_diff_path.open(newline="", encoding="utf-8") as handle:
                diff_rows = list(csv.DictReader(handle))
            if len(diff_rows) != 19:
                failures.append("Stage 9.22 live-number diff must contain nineteen rows")
            source_manifest = root / "case_studies" / "stage7_methods_reproducibility" / "release_archive_manifest.tsv"
            expected_stat18 = None
            if source_manifest.exists():
                with source_manifest.open(newline="", encoding="utf-8") as handle:
                    source_rows = list(csv.DictReader(handle, delimiter="\t"))
                expected_stat18 = f"row_count={len(source_rows)}"
            stat18 = next((row for row in diff_rows if row.get("stat_id") == "STAT-0018"), None)
            if not stat18 or stat18.get("expected_value") != expected_stat18 or stat18.get("status") not in {"pass", "updated"}:
                failures.append("Stage 9.22 live-number diff must record STAT-0018 at the current archive manifest row count")
        if statistic_ledger_path.exists():
            with statistic_ledger_path.open(newline="", encoding="utf-8") as handle:
                stat_rows = {row.get("stat_id"): row for row in csv.DictReader(handle)}
            source_manifest = root / "case_studies" / "stage7_methods_reproducibility" / "release_archive_manifest.tsv"
            expected_stat18 = None
            if source_manifest.exists():
                with source_manifest.open(newline="", encoding="utf-8") as handle:
                    source_rows = list(csv.DictReader(handle, delimiter="\t"))
                expected_stat18 = f"row_count={len(source_rows)}"
            stat18 = stat_rows.get("STAT-0018", {})
            if stat18.get("value") != expected_stat18 or stat18.get("n") != expected_stat18:
                failures.append("Stage 9.22 statistic ledger must keep STAT-0018 aligned with the archive manifest row count")
        if figure_ledger_path.exists():
            figure_text = figure_ledger_path.read_text(encoding="utf-8")
            if "pending_stage9.22" in figure_text:
                failures.append("Stage 9.22 figure ledger must not retain pending_stage9.22 statistic IDs")
            expected_map = {
                "FIG-001": "STAT-0001;STAT-0002;STAT-0003;STAT-0019",
                "FIG-002": "STAT-0004;STAT-0005",
                "FIG-003": "STAT-0006;STAT-0007;STAT-0008",
                "FIG-004": "STAT-0009;STAT-0010;STAT-0011;STAT-0012;STAT-0013;STAT-0014",
                "FIG-005": "STAT-0015;STAT-0016",
                "FIG-006": "STAT-0017;STAT-0018",
            }
            with figure_ledger_path.open(newline="", encoding="utf-8") as handle:
                figure_rows = {row.get("fig_id"): row for row in csv.DictReader(handle)}
            for fig_id, expected in expected_map.items():
                if figure_rows.get(fig_id, {}).get("stat_ids") != expected:
                    failures.append(f"Stage 9.22 figure ledger must map {fig_id} to {expected}")
        if statistical_audit_path.exists():
            audit_body = statistical_audit_path.read_text(encoding="utf-8")
            for phrase in [
                "The live-number audit passed",
                "`STAT-0018`, the release-archive manifest file count",
                "bounded-coupling language remains scoped to declared margins",
                "does not write figure legends",
            ]:
                if phrase not in audit_body:
                    failures.append(f"Stage 9.22 audit missing phrase: {phrase}")
    else:
        for rel in [
            "audits/statistical_language_audit.md",
            "audits/live_numbers_diff.csv",
        ]:
            if (workspace / rel).exists():
                failures.append(f"Stage 9 state must not contain statistical-language output before 9.22: {rel}")

    for rel in FORBIDDEN_DRAFTS:
        if (workspace / rel).exists():
            failures.append(f"Stage 9 scaffold-only pass must not create manuscript/evidence artifact: {rel}")
    if (root / ".venv-panelforge").exists():
        failures.append("Stage 9 scaffold-only pass must not create .venv-panelforge")
    if (root / "tools" / "panelforge-figures" / ".git").exists():
        failures.append("Stage 9 scaffold-only pass must not clone panelforge-figures")
    placeholder = root / "tools" / "panelforge-figures" / "STAGE9_PLACEHOLDER.md"
    if placeholder.exists() and "Not cloned into this repository" not in placeholder.read_text(encoding="utf-8"):
        failures.append("PanelForge placeholder must state that the engine is not cloned into this repository")

    reader_surface_pattern = re.compile(r"(sections|submission_package)/(results|introduction|discussion|methods|abstract|main|supplement)", re.I)
    for path in workspace.rglob("*"):
        if path.is_file() and reader_surface_pattern.search(path.relative_to(workspace).as_posix()):
            rel = path.relative_to(workspace).as_posix()
            if rel.startswith("_quarantine/") or rel.startswith("_staging/"):
                continue
            if stage9_9_started and rel in {"sections/abstract.md", "sections/abstract_strategy.md"}:
                continue
            if stage9_10_started and rel == "sections/results_blueprint.md":
                continue
            if stage9_11_started and rel == "sections/results.md":
                continue
            if stage9_12_started and rel == "sections/introduction.md":
                continue
            if stage9_13_started and rel == "sections/discussion_blueprint.md":
                continue
            if stage9_14_started and rel == "sections/discussion.md":
                continue
            if stage9_15_started and rel == "sections/methods_blueprint.md":
                continue
            if stage9_16_started and rel == "sections/methods.md":
                continue
            if path.name != ".gitkeep":
                failures.append(f"reader-facing manuscript surface exists during scaffold-only pass: {path.relative_to(workspace)}")

    return {
        "status": "pass" if not failures else "fail",
        "failures": failures,
        "warnings": warnings,
        "checks": {
            "workspace_directories_present": "pass" if not any("directory" in item for item in failures) else "fail",
            "project_binding_resolved": "pass" if not any("project binding" in item for item in failures) else "fail",
            "figure_engine_binding_serialized": "pass" if not any("PanelForge" in item or "panelforge" in item for item in failures) else "fail",
            "substage_registry_complete": "pass" if ids == EXPECTED_SUBSTAGES else "fail",
            "ledger_schemas_valid": "pass" if not any("schema" in item for item in failures) else "fail",
            "contract_gate_passed": "pass" if gate.get("pass") is True else "fail",
            "scaffold_only_boundary_preserved": "pass" if not any("scaffold-only" in item or "reader-facing" in item for item in failures) else "fail",
        },
        "substage_count": len(ids),
        "schema_count": len(schema_names),
    }


def main() -> int:
    payload = check_stage9_scaffold()
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())

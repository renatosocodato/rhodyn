"""Validate the Stage 9 scaffold-only manuscript workspace."""

from __future__ import annotations

import json
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
    "scripts/run_stage9_6b_panelforge_rendering.py",
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
]

FORBIDDEN_DRAFTS = [
    "sections/results.md",
    "sections/introduction.md",
    "sections/discussion.md",
    "sections/methods.md",
    "sections/abstract.md",
    "sections/data_availability.md",
    "sections/code_availability.md",
    "refs/references.bib",
    "submission_package/submission_readiness_checklist.md",
    "submission_package/pi_review_packet.md",
    "stage9_completion_report.md",
    "figures/.panelforge_commit",
    "audits/panelforge_render_report.md",
]
FORBIDDEN_RENDER_SUFFIXES = {".png", ".pdf", ".svg"}


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
    if figure_engine.get("execution_status") != "not_cloned_not_installed_not_rendered":
        failures.append("PanelForge execution status must remain not cloned/install/rendered in scaffold")

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
    allowed_gate_files = {"9.-1.json", "9.0.json", "9.1.json", "9.2.json"}
    unexpected_gate_files = [name for name in gate_files if name not in allowed_gate_files]
    if unexpected_gate_files:
        failures.append(f"Stage 9 must not contain post-9.2 gate verdicts before authorization: {unexpected_gate_files}")
    if "9.-1.json" not in gate_files:
        failures.append(f"Stage 9 scaffold must contain the 9.-1 gate verdict, found: {gate_files}")
    stage9_0_started = "9.0.json" in gate_files
    stage9_1_started = "9.1.json" in gate_files
    stage9_2_started = "9.2.json" in gate_files
    gate = _read_json(workspace / "gate_verdicts" / "9.-1.json", failures)
    if gate.get("pass") is not True or gate.get("substage") != "9.-1":
        failures.append("Stage 9.-1 gate verdict must pass")
    checks = gate.get("checks", []) if isinstance(gate.get("checks"), list) else []
    if not checks or not all(item.get("passed") is True for item in checks if isinstance(item, dict)):
        failures.append("Stage 9.-1 gate checks must all pass")

    memory = _read_json(root / "docs" / "stage9_execution_memory.json", failures)
    for flag in ["manuscript_drafting_started", "evidence_intake_started", "citation_resolution_started", "submission_package_started"]:
        if flag == "evidence_intake_started" and stage9_0_started:
            if memory.get(flag) is not True:
                failures.append("Stage 9 execution memory must record evidence_intake_started=true after 9.0")
            continue
        if memory.get(flag) is not False:
            failures.append(f"Stage 9 scaffold memory must keep {flag}=false")
    for flag in ["figure_engine_clone_started", "figure_engine_install_started", "figure_rendering_started"]:
        if memory.get(flag) is not False:
            failures.append(f"Stage 9 scaffold memory must keep {flag}=false")
    expected_memory_status = (
        "stage9_2_methods_corpus_registered"
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

    for rel in FORBIDDEN_DRAFTS:
        if (workspace / rel).exists():
            failures.append(f"Stage 9 scaffold-only pass must not create manuscript/evidence artifact: {rel}")
    if (root / ".venv-panelforge").exists():
        failures.append("Stage 9 scaffold-only pass must not create .venv-panelforge")
    if (root / "tools" / "panelforge-figures" / ".git").exists():
        failures.append("Stage 9 scaffold-only pass must not clone panelforge-figures")
    rendered_outputs = [
        path.relative_to(workspace).as_posix()
        for path in (workspace / "figures" / "rendered").rglob("*")
        if path.is_file() and path.suffix.lower() in FORBIDDEN_RENDER_SUFFIXES
    ]
    if rendered_outputs:
        failures.append(f"Stage 9 scaffold-only pass must not render panels: {rendered_outputs}")
    manifest = workspace / "figures" / "figures.manifest.yaml"
    if manifest.exists() and "scaffold_placeholder_not_renderable" not in manifest.read_text(encoding="utf-8"):
        failures.append("Stage 9 figure manifest must remain a non-renderable scaffold placeholder")
    placeholder = root / "tools" / "panelforge-figures" / "STAGE9_PLACEHOLDER.md"
    if placeholder.exists() and "Not cloned, not installed, and not rendered" not in placeholder.read_text(encoding="utf-8"):
        failures.append("PanelForge placeholder must state that the engine is not cloned or rendered")

    reader_surface_pattern = re.compile(r"(sections|submission_package)/(results|introduction|discussion|methods|abstract|main|supplement)", re.I)
    for path in workspace.rglob("*"):
        if path.is_file() and reader_surface_pattern.search(path.relative_to(workspace).as_posix()):
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

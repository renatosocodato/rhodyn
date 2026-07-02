"""Scaffold Stage 9 Nature Methods manuscript assembly contracts.

This script serializes the Stage 9 manuscript-development roadmap into the
repository without beginning evidence intake, citation work, manuscript
drafting, or submission-package assembly. It executes only the Stage 9.-1
contract/schema layer. The v2.1 scaffold also records the future PanelForge
figure-rendering harness, but it does not clone the figure engine, create a
runtime environment, validate a real figure manifest, or render panels.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT / "manuscript" / "nature_methods"
SCHEMA_DIR = WORKSPACE / "contracts" / "ledger_schemas"

PROJECT_BINDING = {
    "scaffold_version": "2.1",
    "method_name": "RhoDyn",
    "method_object": "residence-aware interpretation of biological trajectories",
    "core_constructs": [
        "residence windows",
        "dwell metrics",
        "amplitude / endpoint comparators",
        "bounded coupling",
        "reserve-like summaries",
        "routed-output model comparison",
    ],
    "primary_model_system": "public live-cell signaling and perturbation benchmark systems",
    "software_name": "RhoDyn",
    "software_version": "v0.1.0",
    "archive_doi": "10.5281/zenodo.21036616",
    "concept_doi": "10.5281/zenodo.21036615",
    "repo_url": "https://github.com/renatosocodato/rhodyn",
    "venue": "Nature Methods",
    "content_type": "Article",
    "reporting_summary_required": True,
    "code_central": True,
    "stage9_scaffold_scope": "contract_schema_serialization_only",
    "venue_binding": {
        "venue": "Nature Methods",
        "content_type": "Article",
        "reporting_summary_required": True,
        "code_central": True,
    },
    "skills_in_use": {
        "ref_manager": True,
        "editorial_elevation": True,
        "publication_surface_hygiene": True,
    },
    "figure_engine_binding": {
        "name": "panelforge-figures",
        "repo_url": "https://github.com/renatosocodato/panelforge-figures",
        "pinned_ref": "v3.14.1",
        "version_doi": "10.5281/zenodo.20811171",
        "concept_doi": "10.5281/zenodo.20811170",
        "license": "MIT",
        "python": ">=3.11,<3.13",
        "install": 'pip install -e ".[dev]"',
        "install_alt": 'pip install "git+https://github.com/renatosocodato/panelforge-figures@v3.14.1"',
        "cli": "figures",
        "manifest": "manuscript/nature_methods/figures/figures.manifest.yaml",
        "render_cmd": "figures render figures.manifest.yaml",
        "validate_cmd": "figures validate figures.manifest.yaml",
        "telemetry": "off",
        "data_class": "research",
        "clone_path": "tools/panelforge-figures",
        "runtime_env": ".venv-panelforge",
        "execution_status": "not_cloned_not_installed_not_rendered",
    },
}

WORKSPACE_DIRECTORIES = [
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
REPO_DIRECTORIES = [
    "tools",
    "tools/panelforge-figures",
]
PLANNED_RUNTIME_DIRS = [
    ".venv-panelforge",
]

PATCH_LEDGER = [
    ("P1", "Machine-checkable gates", "Every substage emits a falsifiable gate verdict JSON."),
    ("P2", "Stable IDs and pinned ledger schemas", "Claims, paragraphs, figures, artifacts, references, and statistics use immutable IDs."),
    ("P3", "Atomic idempotent writes", "Substages stage, gate, promote, or quarantine without partially writing canonical outputs."),
    ("P4", "Citation anti-fabrication routing", "References are resolved through the future reference-management route before manuscript use."),
    ("P5", "Numbers-are-live provenance", "Reported statistics are recomputed from frozen artifacts before promotion."),
    ("P6", "Entry-gate ordering-loop fix", "Stage 9.0 checks Stage 7 headline-result coverage before claim freeze."),
    ("P7", "Reader-surface hygiene", "Publication-surface hygiene blocks internal scaffold leakage before package assembly."),
    ("P8", "Nature Methods venue corrections", "Content type, Reporting Summary, code review, subheading, reference, and discovery-fit rules are pinned downstream."),
    ("P9", "Scope-fork resolution", "Project-specific method nouns and venue choices live in the project binding block."),
    ("P10", "Figure-engine integration", "PanelForge is version-bound for future deterministic figure rendering through Stage 9.6b."),
]

FINAL_DELIVERABLES = [
    "Complete Nature Methods-aligned manuscript draft.",
    "Complete Methods and Supplementary Information drafts.",
    "Complete figure and table package plan with legends.",
    "Data, code, and software availability statements.",
    "Mandatory Reporting Summary registered for package assembly.",
    "Resolved literature and citation ledger.",
    "Claim-to-evidence, figure-to-artifact, methods-to-code, and statistic ledgers.",
    "PanelForge manifest, rendered panels, pinned engine commit, and render report after Stage 9.6b executes.",
    "Reproducibility command index.",
    "Contract and schema layer with all gate verdict JSON files.",
    "Cross-document consistency, statistical language, reader-surface hygiene, and internal peer-review reports.",
    "PI review packet, submission-readiness checklist, Stage 9 completion report, and updated roadmap memory.",
]

ID_NAMESPACES = [
    ("CLM-####", "claim", "claim hierarchy and downstream claim joins"),
    ("PARA-<section>-###", "paragraph", "planned or drafted manuscript paragraph"),
    ("FIG-###", "main figure", "main display item"),
    ("SFIG-###", "supplementary figure", "supplementary display item"),
    ("TBL-###", "main table", "main table"),
    ("STBL-###", "supplementary table", "supplementary table"),
    ("ART-####", "artifact", "Stage 7 evidence artifact"),
    ("REF-####", "reference", "resolved literature or venue reference"),
    ("STAT-####", "statistic", "single reported quantitative result"),
    ("SUPP-###", "supplementary item", "supplementary method/table/figure object"),
]

SUBSTAGES = [
    {
        "id": "9.-1",
        "title": "Contract and schema layer",
        "objective": "Make downstream gates machine-checkable and ledgers joinable before evidence intake.",
        "outputs": [
            "manuscript/nature_methods/contracts/id_namespace.md",
            "manuscript/nature_methods/contracts/ledger_schemas/*.json",
            "manuscript/nature_methods/contracts/machine_gate_spec.md",
            "manuscript/nature_methods/contracts/atomic_write_protocol.md",
            "docs/stage9_execution_memory.json",
        ],
        "gate_predicates": [
            "schema files are valid JSON objects with required field declarations",
            "namespace prefixes are defined",
            "workspace directories exist",
            "execution-memory loader is documented",
            "every declared Stage 9 ledger maps to exactly one schema",
        ],
        "status": "complete_scaffold_only",
    },
    {
        "id": "9.0",
        "title": "Stage 7 evidence intake and lock",
        "objective": "Confirm that manuscript assembly can begin from frozen, typed Stage 7 evidence.",
        "outputs": [
            "manuscript/nature_methods/ledgers/stage9_evidence_lock.md",
            "manuscript/nature_methods/ledgers/stage9_evidence_manifest.csv",
            "manuscript/nature_methods/ledgers/stage7_output_contract.md",
        ],
        "gate_predicates": [
            "entry artifacts resolve",
            "artifacts validate or are scoped out",
            "headline Stage 7 results map to ART IDs",
            "evidence_version is immutable",
        ],
        "status": "not_started",
    },
    {
        "id": "9.1",
        "title": "Venue guidance source register",
        "objective": "Bind manuscript process to official and cached Nature Methods guidance.",
        "outputs": [
            "manuscript/nature_methods/refs/nature_methods_guidance_register.md",
            "manuscript/nature_methods/refs/_cache/",
            "manuscript/nature_methods/audits/venue_policy_constraints.md",
        ],
        "gate_predicates": [
            "content-type budget is sourced",
            "cached sources have URL and access date",
            "verified venue constraints are explicit",
            "freshness assertion passes",
        ],
        "status": "not_started",
    },
    {
        "id": "9.2",
        "title": "Representative methods-paper corpus",
        "objective": "Create a structural corpus of successful computational methods papers.",
        "outputs": [
            "manuscript/nature_methods/refs/representative_methods_papers.md",
            "manuscript/nature_methods/audits/methods_paper_archetype_analysis.md",
        ],
        "gate_predicates": [
            "corpus has the planned DOI count",
            "each entry records novelty, benchmarks, biology, software, limitations, and availability",
            "archetype synthesis exists",
        ],
        "status": "not_started",
    },
    {
        "id": "9.3",
        "title": "Archetype, content type, and narrative spine",
        "objective": "Pin paper type, content type, and venue-fit decision before drafting.",
        "outputs": [
            "manuscript/nature_methods/stage9_narrative_spine.md",
            "manuscript/nature_methods/audits/venue_fit_rationale.md",
        ],
        "gate_predicates": [
            "content_type matches a sourced budget",
            "narrative spine exists",
            "discovery-versus-demonstration decision is evidence-bound",
        ],
        "status": "not_started",
    },
    {
        "id": "9.4",
        "title": "Manuscript claim freeze",
        "objective": "Freeze claim hierarchy with stable CLM IDs and strength caps.",
        "outputs": [
            "manuscript/nature_methods/ledgers/claim_hierarchy.md",
            "manuscript/nature_methods/ledgers/claim_hierarchy.csv",
            "manuscript/nature_methods/ledgers/non_claims_and_scope_boundaries.md",
        ],
        "gate_predicates": [
            "claim hierarchy validates",
            "every central claim has evidence",
            "every claim has a strength cap",
            "non-claims ledger is non-empty",
        ],
        "status": "not_started",
    },
    {
        "id": "9.5",
        "title": "Paragraph-level claim ledger",
        "objective": "Plan manuscript paragraphs as auditable claim-bearing units.",
        "outputs": [
            "manuscript/nature_methods/ledgers/paragraph_claim_ledger.csv",
            "manuscript/nature_methods/ledgers/claim_strength_rules.md",
        ],
        "gate_predicates": [
            "ledger validates",
            "every PARA ID resolves to a CLM ID",
            "paragraph strength does not exceed claim strength",
        ],
        "status": "not_started",
    },
    {
        "id": "9.6",
        "title": "Figure-first manuscript spine",
        "objective": "Build the manuscript around evidence-bearing display items before prose.",
        "outputs": [
            "manuscript/nature_methods/figures/main_figure_spine.md",
            "manuscript/nature_methods/ledgers/figure_to_claim_to_artifact.csv",
            "manuscript/nature_methods/figures/display_item_plan.md",
        ],
        "gate_predicates": [
            "figure ledger validates",
            "every figure resolves to claims and artifacts",
            "figure count respects sourced budget",
            "central evidence is not buried in supplement",
        ],
        "status": "not_started",
    },
    {
        "id": "9.6b",
        "title": "Figure rendering via PanelForge",
        "objective": "Prepare deterministic publication-grade figure rendering from the frozen figure-to-claim-to-artifact contract.",
        "outputs": [
            "manuscript/nature_methods/figures/figures.manifest.yaml",
            "manuscript/nature_methods/figures/rendered/<fig_id>/*.png|pdf|svg",
            "manuscript/nature_methods/figures/.panelforge_commit",
            "manuscript/nature_methods/ledgers/figure_to_claim_to_artifact.csv",
            "manuscript/nature_methods/audits/panelforge_render_report.md",
        ],
        "gate_predicates": [
            "figure engine version equals pinned ref",
            "figures validate passes for manifest",
            "every fig_id has an existing render_path",
            "every rendered entry records a recipe and rejected alternative",
            "S1 manifest keys contain no claim IDs, artifact IDs, or pipeline-state tokens",
            "gallery drift is passing or explicitly accepted",
        ],
        "status": "not_started",
    },
    {
        "id": "9.7",
        "title": "Supplementary display item plan",
        "objective": "Plan supplementary material as cited support rather than a data dump.",
        "outputs": [
            "manuscript/nature_methods/supplementary/supplementary_item_plan.md",
            "manuscript/nature_methods/ledgers/supplementary_callout_ledger.csv",
            "manuscript/nature_methods/figures/figures.manifest.yaml",
        ],
        "gate_predicates": [
            "supplementary ledger validates",
            "each item has callout and role",
            "essential items have main-text callouts",
        ],
        "status": "not_started",
    },
    {
        "id": "9.8",
        "title": "Section contract blueprint",
        "objective": "Define every manuscript section and venue structural rule before writing.",
        "outputs": ["manuscript/nature_methods/sections/section_contracts.md"],
        "gate_predicates": [
            "every section has a contract",
            "Results and Methods require topical subheadings",
            "Discussion prohibits subheadings",
            "Abstract contract follows sourced budget",
        ],
        "status": "not_started",
    },
    {
        "id": "9.9",
        "title": "Title, subtitle, and abstract strategy",
        "objective": "Create high-level framing without overselling.",
        "outputs": [
            "manuscript/nature_methods/sections/title_options.md",
            "manuscript/nature_methods/sections/abstract_strategy.md",
            "manuscript/nature_methods/sections/abstract.md",
        ],
        "gate_predicates": [
            "abstract word count respects sourced budget",
            "abstract citation style follows content type",
            "abstract claims map to claim IDs",
        ],
        "status": "not_started",
    },
    {
        "id": "9.10",
        "title": "Results subsection architecture",
        "objective": "Break Results into evidence-locked drafting units.",
        "outputs": ["manuscript/nature_methods/sections/results_blueprint.md"],
        "gate_predicates": [
            "each subsection maps to figure and artifact IDs",
            "allowed conclusion respects strength cap",
            "no subsection is narrative-only",
        ],
        "status": "not_started",
    },
    {
        "id": "9.11",
        "title": "Results drafting pass",
        "objective": "Draft Results in figure-locked order.",
        "outputs": ["manuscript/nature_methods/sections/results.md"],
        "gate_predicates": [
            "every Results paragraph has a PARA ID",
            "figure callouts resolve",
            "strength caps hold",
        ],
        "status": "not_started",
    },
    {
        "id": "9.12",
        "title": "Introduction literature binding",
        "objective": "Draft citation-bound Introduction through resolved references.",
        "outputs": [
            "manuscript/nature_methods/sections/introduction.md",
            "manuscript/nature_methods/refs/introduction_citation_ledger.csv",
        ],
        "gate_predicates": [
            "all Introduction citations resolve",
            "external claims map to reference IDs",
            "review-source share is under threshold",
        ],
        "status": "not_started",
    },
    {
        "id": "9.13",
        "title": "Discussion interpretation map",
        "objective": "Plan limitation-aware Discussion before drafting.",
        "outputs": ["manuscript/nature_methods/sections/discussion_blueprint.md"],
        "gate_predicates": [
            "Stage 7 limitations represented",
            "no limitation converted into strength without evidence",
            "map has no subheadings",
        ],
        "status": "not_started",
    },
    {
        "id": "9.14",
        "title": "Discussion drafting pass",
        "objective": "Draft balanced Discussion with no subheadings.",
        "outputs": ["manuscript/nature_methods/sections/discussion.md"],
        "gate_predicates": [
            "Discussion contains no subheadings",
            "limitations remain visible",
            "future directions are labeled",
        ],
        "status": "not_started",
    },
    {
        "id": "9.15",
        "title": "Methods architecture",
        "objective": "Build Methods structure from repository implementation and Stage 7 artifacts.",
        "outputs": [
            "manuscript/nature_methods/sections/methods_blueprint.md",
            "manuscript/nature_methods/ledgers/methods_to_code_ledger.csv",
        ],
        "gate_predicates": [
            "methods-to-code ledger validates",
            "methods statements map to repo path and commit",
            "dataset references include version and date",
        ],
        "status": "not_started",
    },
    {
        "id": "9.16",
        "title": "Methods drafting pass",
        "objective": "Draft reviewer-reconstructable Methods.",
        "outputs": ["manuscript/nature_methods/sections/methods.md"],
        "gate_predicates": [
            "every Methods claim has a methods statement ID",
            "software version matches evidence manifest",
            "undefined standard-methods phrasing absent",
        ],
        "status": "not_started",
    },
    {
        "id": "9.17",
        "title": "Software, data, and code availability assembly",
        "objective": "Create precise availability statements and required Reporting Summary placeholder.",
        "outputs": [
            "manuscript/nature_methods/sections/data_availability.md",
            "manuscript/nature_methods/sections/code_availability.md",
            "manuscript/nature_methods/ledgers/reproducibility_command_index.md",
            "manuscript/nature_methods/submission_package/reporting_summary_REQUIRED.md",
        ],
        "gate_predicates": [
            "DOI and repo URL resolve",
            "commit pinned",
            "no upon-request language",
            "Reporting Summary registered as required",
            "PanelForge version DOI and render command are recorded when figures have been rendered",
        ],
        "status": "not_started",
    },
    {
        "id": "9.18",
        "title": "Supplementary Methods drafting",
        "objective": "Move technical depth into structured Supplementary Methods.",
        "outputs": ["manuscript/nature_methods/supplementary/supplementary_methods.md"],
        "gate_predicates": [
            "items are callable from main text",
            "no new claim ID absent from claim freeze",
        ],
        "status": "not_started",
    },
    {
        "id": "9.19",
        "title": "Supplementary tables and source-data binding",
        "objective": "Build supplementary tables as reviewable evidence objects.",
        "outputs": [
            "manuscript/nature_methods/supplementary/supplementary_tables_plan.md",
            "manuscript/nature_methods/supplementary/",
        ],
        "gate_predicates": [
            "each table has callout and role",
            "figure-source mapping covers figures",
            "figure-source mapping records PanelForge recipe and render path after 9.6b",
            "statistics table references statistic IDs",
        ],
        "status": "not_started",
    },
    {
        "id": "9.20",
        "title": "Reference library and citation audit",
        "objective": "Resolve and audit complete reference library.",
        "outputs": [
            "manuscript/nature_methods/refs/references.bib",
            "manuscript/nature_methods/refs/citation_claim_ledger.csv",
            "manuscript/nature_methods/audits/reference_audit.md",
        ],
        "gate_predicates": [
            "references resolve with DOI or PMID",
            "retraction checks are clear or justified",
            "reference count respects cap",
            "references map to claims",
        ],
        "status": "not_started",
    },
    {
        "id": "9.21",
        "title": "Cross-document consistency audit",
        "objective": "Check manuscript consistency by relational joins over keyed ledgers.",
        "outputs": ["manuscript/nature_methods/audits/cross_document_consistency_audit.md"],
        "gate_predicates": [
            "orphan claim set empty",
            "orphan figure set empty",
            "orphan statistic set empty",
            "dangling reference set empty",
            "version and strength coherence hold",
        ],
        "status": "not_started",
    },
    {
        "id": "9.22",
        "title": "Statistical and quantitative language audit",
        "objective": "Recompute reported numbers from frozen artifacts and diff manuscript text.",
        "outputs": [
            "manuscript/nature_methods/audits/statistical_language_audit.md",
            "manuscript/nature_methods/audits/live_numbers_diff.csv",
            "manuscript/nature_methods/ledgers/statistic_ledger.csv",
        ],
        "gate_predicates": [
            "every statistic recomputes within tolerance",
            "quantitative statements have statistic IDs",
            "equivalence claims state bounds",
        ],
        "status": "not_started",
    },
    {
        "id": "9.23",
        "title": "Figure legend and caption audit",
        "objective": "Make display items self-contained and precise.",
        "outputs": [
            "manuscript/nature_methods/figures/figure_legends.md",
            "manuscript/nature_methods/audits/figure_legend_audit.md",
        ],
        "gate_predicates": [
            "each figure and table has legend",
            "legend statistics resolve",
            "legends do not assert absent claims",
            "legend seed text does not inherit PanelForge S3 provenance",
        ],
        "status": "not_started",
    },
    {
        "id": "9.24",
        "title": "Editorial polish pass I",
        "objective": "Improve scientific clarity without changing meaning.",
        "outputs": ["manuscript/nature_methods/audits/editorial_pass_1.md"],
        "gate_predicates": [
            "paragraph ID set unchanged",
            "strength caps hold",
            "limitations remain present",
        ],
        "status": "not_started",
    },
    {
        "id": "9.25",
        "title": "Editorial polish pass II",
        "objective": "Tune venue style and readability without broadening claims.",
        "outputs": ["manuscript/nature_methods/audits/editorial_pass_2.md"],
        "gate_predicates": [
            "meaning preserved",
            "style metrics pass thresholds",
            "no claim broadened",
        ],
        "status": "not_started",
    },
    {
        "id": "9.25b",
        "title": "Reader-surface hygiene gate",
        "objective": "Strip internal IDs and build-language from reader-facing surfaces before assembly.",
        "outputs": ["manuscript/nature_methods/audits/reader_surface_hygiene_report.md"],
        "gate_predicates": [
            "no internal ID tokens on reader-facing surfaces",
            "no stage or substage references on reader-facing surfaces",
            "legends and captions are free of lineage language",
            "PanelForge manifest S3 provenance is not cross-referenced from S1 reader-facing keys",
        ],
        "status": "not_started",
    },
    {
        "id": "9.26",
        "title": "Internal peer review simulation",
        "objective": "Stress-test the manuscript with eight reviewer perspectives.",
        "outputs": [
            "manuscript/nature_methods/audits/internal_peer_review_simulation.md",
            "manuscript/nature_methods/audits/reviewer_action_matrix.csv",
        ],
        "gate_predicates": [
            "all eight perspectives present",
            "blocking concerns have resolution status",
            "unsupported central claims are routed",
        ],
        "status": "not_started",
    },
    {
        "id": "9.27",
        "title": "Submission package assembly",
        "objective": "Assemble complete manuscript and submission package after hygiene gate.",
        "outputs": [
            "manuscript/nature_methods/submission_package/",
            "manuscript/nature_methods/submission_package/submission_readiness_checklist.md",
        ],
        "gate_predicates": [
            "required package elements exist",
            "reader-surface hygiene passed",
            "Reporting Summary present",
            "code-for-review present",
            "consistency audit passes over package",
        ],
        "status": "not_started",
    },
    {
        "id": "9.28",
        "title": "Final human PI review packet",
        "objective": "Prepare final human decision packet.",
        "outputs": ["manuscript/nature_methods/submission_package/pi_review_packet.md"],
        "gate_predicates": [
            "packet covers thesis, claims, figures, risks, limitations, objections, decisions, venue fit, and open items",
            "human-judgment items are explicit",
        ],
        "status": "not_started",
    },
    {
        "id": "9.29",
        "title": "Roadmap closure and version binding",
        "objective": "Close Stage 9 with package, evidence, release, and limitation versions bound.",
        "outputs": [
            "manuscript/nature_methods/stage9_completion_report.md",
            "docs/roadmap_execution_memory.json",
        ],
        "gate_predicates": [
            "every Stage 9 gate passes",
            "quarantine has no unresolved blocker",
            "package, evidence, and release versions are bound",
        ],
        "status": "not_started",
    },
]

SCHEMA_NAMES = [
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
]


def _now() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def _write_text(path: Path, body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body.rstrip() + "\n", encoding="utf-8")


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _schema(name: str, required: list[str], properties: dict[str, dict[str, Any]]) -> dict[str, Any]:
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": f"rhodyn.stage9.{name}.row.schema.json",
        "title": f"Stage 9 {name} row",
        "type": "object",
        "required": required,
        "properties": properties,
        "additionalProperties": False,
    }


def _schemas() -> dict[str, dict[str, Any]]:
    text = {"type": "string"}
    bool_like = {"type": "string", "enum": ["true", "false", "not_applicable", "pending"]}
    return {
        "claim_hierarchy": _schema(
            "claim_hierarchy",
            ["claim_id", "class", "confidence", "evidence_art_ids", "fig_ids", "location", "strength_cap"],
            {
                "claim_id": {"type": "string", "pattern": "^CLM-[0-9]{4}$"},
                "class": text,
                "confidence": text,
                "evidence_art_ids": text,
                "fig_ids": text,
                "location": text,
                "strength_cap": text,
            },
        ),
        "paragraph_claim_ledger": _schema(
            "paragraph_claim_ledger",
            ["para_id", "section", "purpose", "claim_id", "fig_ids", "stat_ids", "ref_ids", "caveat", "strength_cap"],
            {
                "para_id": {"type": "string", "pattern": "^PARA-[A-Za-z0-9_-]+-[0-9]{3}$"},
                "section": text,
                "purpose": text,
                "claim_id": {"type": "string"},
                "fig_ids": text,
                "stat_ids": text,
                "ref_ids": text,
                "caveat": text,
                "strength_cap": text,
            },
        ),
        "figure_to_claim_to_artifact": _schema(
            "figure_to_claim_to_artifact",
            [
                "fig_id",
                "claim_id",
                "art_ids",
                "stat_ids",
                "panel_structure",
                "placement",
                "recipe",
                "render_path",
                "engine_version",
                "engine_commit",
                "drift_ok",
                "rejected_alternative",
            ],
            {
                "fig_id": {"type": "string", "pattern": "^(FIG|SFIG)-[0-9]{3}$"},
                "claim_id": text,
                "art_ids": text,
                "stat_ids": text,
                "panel_structure": text,
                "placement": {"type": "string", "enum": ["main", "supp"]},
                "recipe": text,
                "render_path": text,
                "engine_version": text,
                "engine_commit": text,
                "drift_ok": bool_like,
                "rejected_alternative": text,
            },
        ),
        "methods_to_code": _schema(
            "methods_to_code",
            ["methods_stmt_id", "art_id", "repo_path", "commit", "command"],
            {
                "methods_stmt_id": {"type": "string"},
                "art_id": text,
                "repo_path": text,
                "commit": text,
                "command": text,
            },
        ),
        "citation_claim_ledger": _schema(
            "citation_claim_ledger",
            ["ref_id", "claim_id", "doi_or_pmid", "resolved", "access_date", "source_type"],
            {
                "ref_id": {"type": "string", "pattern": "^REF-[0-9]{4}$"},
                "claim_id": text,
                "doi_or_pmid": text,
                "resolved": bool_like,
                "access_date": text,
                "source_type": {"type": "string", "enum": ["primary", "methods", "review", "venue", "dataset"]},
            },
        ),
        "statistic_ledger": _schema(
            "statistic_ledger",
            ["stat_id", "art_id", "fig_id", "value", "ci", "n", "test", "source_command", "manuscript_locations"],
            {
                "stat_id": {"type": "string", "pattern": "^STAT-[0-9]{4}$"},
                "art_id": text,
                "fig_id": text,
                "value": text,
                "ci": text,
                "n": text,
                "test": text,
                "source_command": text,
                "manuscript_locations": text,
            },
        ),
        "supplementary_callout_ledger": _schema(
            "supplementary_callout_ledger",
            ["supp_id", "fig_id", "tbl_id", "callout_location", "role"],
            {
                "supp_id": {"type": "string", "pattern": "^SUPP-[0-9]{3}$"},
                "fig_id": text,
                "tbl_id": text,
                "callout_location": text,
                "role": {"type": "string", "enum": ["essential", "supportive", "archival"]},
            },
        ),
        "stage9_evidence_manifest": _schema(
            "stage9_evidence_manifest",
            ["art_id", "stage7_component", "path", "schema", "status", "evidence_version"],
            {
                "art_id": {"type": "string", "pattern": "^ART-[0-9]{4}$"},
                "stage7_component": text,
                "path": text,
                "schema": text,
                "status": text,
                "evidence_version": text,
            },
        ),
        "stage7_output_contract": _schema(
            "stage7_output_contract",
            ["component", "path", "schema", "required_for_stage9", "scope_status"],
            {
                "component": text,
                "path": text,
                "schema": text,
                "required_for_stage9": bool_like,
                "scope_status": text,
            },
        ),
        "reviewer_action_matrix": _schema(
            "reviewer_action_matrix",
            ["reviewer_perspective", "concern", "claim_id", "fig_id", "resolution_status", "resolution"],
            {
                "reviewer_perspective": text,
                "concern": text,
                "claim_id": text,
                "fig_id": text,
                "resolution_status": {"type": "string", "enum": ["resolved", "narrowed", "routed_upstream", "open"]},
                "resolution": text,
            },
        ),
        "live_numbers_diff": _schema(
            "live_numbers_diff",
            ["stat_id", "source_command", "expected_value", "manuscript_value", "rounding_tolerance", "status"],
            {
                "stat_id": text,
                "source_command": text,
                "expected_value": text,
                "manuscript_value": text,
                "rounding_tolerance": text,
                "status": text,
            },
        ),
        "limitations_ledger": _schema(
            "limitations_ledger",
            ["limitation_id", "claim_id", "scope", "manuscript_location", "retained"],
            {
                "limitation_id": text,
                "claim_id": text,
                "scope": text,
                "manuscript_location": text,
                "retained": bool_like,
            },
        ),
        "reproducibility_command_index": _schema(
            "reproducibility_command_index",
            ["command_id", "art_id", "command", "expected_output", "software_version"],
            {
                "command_id": text,
                "art_id": text,
                "command": text,
                "expected_output": text,
                "software_version": text,
            },
        ),
    }


def _id_namespace_md() -> str:
    rows = "\n".join(f"| `{prefix}` | {label} | {purpose} |" for prefix, label, purpose in ID_NAMESPACES)
    return f"""# Stage 9 ID namespace

Stage 9 uses stable identifiers so claims, paragraphs, figures, tables, references, statistics, and Stage 7 artifacts can be joined without relying on prose.

| Namespace | Object | Purpose |
|---|---|---|
{rows}

IDs are minted once, never reused, and never shown on reader-facing manuscript surfaces. Reader-facing prose must refer to the scientific object, not to the internal identifier.
"""


def _machine_gate_spec_md() -> str:
    return """# Stage 9 machine-gate specification

Every executable Stage 9 substage writes `manuscript/nature_methods/gate_verdicts/<substage>.json`.

Required fields.

- `substage`
- `checks`
- `pass`
- `timestamp`
- `evidence_version`

`pass` is the logical AND of all check rows. A substage may promote staged outputs only when `pass` is true. Failed staging output is moved to `_quarantine/<substage>/<timestamp>/` and the blocker is written to `docs/stage9_execution_memory.json`.

This scaffold executes only `9.-1`. Future gates are serialized in `contracts/stage9_substage_registry.json` but are not created as passing verdicts until their substages are actually run.

Stage 9.6b is the first substage allowed to clone `panelforge-figures`, create `.venv-panelforge`, write `.panelforge_commit`, validate a real `figures.manifest.yaml`, or render panels. The scaffold may only write placeholder paths and preparatory instructions for that future substage.
"""


def _atomic_protocol_md() -> str:
    return """# Stage 9 atomic write protocol

Stage 9 uses staged writes so manuscript-facing files are never partially written.

1. Load `docs/stage9_execution_memory.json` and the relevant keyed ledgers.
2. Write substage outputs only to `manuscript/nature_methods/_staging/<substage>/`.
3. Run the machine gate for the substage.
4. If the gate passes, promote staged files to canonical paths and record the promotion.
5. If the gate fails, move staging to `manuscript/nature_methods/_quarantine/<substage>/<timestamp>/` and stop.
6. Re-running a substage replaces only that substage's staging directory and must converge to the same canonical state given the same frozen evidence.

The current scaffold does not run Stage 9.0 evidence intake, does not create manuscript prose, and does not assemble a submission package.
"""


def _plan_md() -> str:
    table = "\n".join(
        f"| {item['id']} | {item['title']} | {item['status']} | {item['objective']} |"
        for item in SUBSTAGES
    )
    patch_rows = "\n".join(f"| {patch_id} | {title} | {summary} |" for patch_id, title, summary in PATCH_LEDGER)
    deliverable_rows = "\n".join(f"{idx}. {item}" for idx, item in enumerate(FINAL_DELIVERABLES, start=1))
    return f"""# Stage 9 Nature Methods manuscript assembly plan

Stage 9 converts the completed Stage 7 methods-program evidence package into a Nature Methods-oriented manuscript package. This repository state serializes the entire Stage 9 v2.1 plan and executes only the contract/schema scaffold. It does not begin evidence intake, literature lookup, manuscript drafting, editorial polishing, PanelForge rendering, or package assembly.

## Project binding

- Method. {PROJECT_BINDING['method_name']}.
- Method object. {PROJECT_BINDING['method_object']}.
- Software. {PROJECT_BINDING['software_name']} {PROJECT_BINDING['software_version']}.
- Repository. {PROJECT_BINDING['repo_url']}.
- Software archive DOI. {PROJECT_BINDING['archive_doi']}.
- Venue target. {PROJECT_BINDING['venue']} {PROJECT_BINDING['content_type']}, pending live venue-guidance verification in Stage 9.1.

## Non-execution boundary

This pass is scaffold-only. It creates the workspace, ID namespace, ledger schemas, gate convention, atomic-write protocol, substage registry, figure-engine binding, and execution memory. It intentionally does not create `sections/results.md`, `sections/introduction.md`, `sections/discussion.md`, `sections/methods.md`, `refs/references.bib`, submission-package files, or evidence-lock ledgers from Stage 9.0. It also does not clone PanelForge, create `.venv-panelforge`, validate a real figure manifest, or render panels.

## Patch ledger serialized from v2.1

| ID | Patch | Scaffold implication |
|---|---|---|
{patch_rows}

## Figure-engine binding

- Engine. {PROJECT_BINDING['figure_engine_binding']['name']}.
- Repository. {PROJECT_BINDING['figure_engine_binding']['repo_url']}.
- Pinned ref. {PROJECT_BINDING['figure_engine_binding']['pinned_ref']}.
- Version DOI. {PROJECT_BINDING['figure_engine_binding']['version_doi']}.
- Future clone path. `{PROJECT_BINDING['figure_engine_binding']['clone_path']}`.
- Future isolated environment. `{PROJECT_BINDING['figure_engine_binding']['runtime_env']}`.
- Future manifest. `{PROJECT_BINDING['figure_engine_binding']['manifest']}`.
- Scaffold status. `{PROJECT_BINDING['figure_engine_binding']['execution_status']}`.

## Serialized substages

| Substage | Title | Status | Objective |
|---|---|---|---|
{table}

## Final deliverables at Stage 9 completion

{deliverable_rows}

## Completion rule

Stage 9 must proceed substage by substage. A downstream substage may not promote outputs unless its `gate_verdicts/<substage>.json` reports `pass == true`. Polished prose, rendered figures, or package files may not substitute for missing evidence, failed predicates, unresolved identifiers, or an upstream scope problem.
"""


def _readme_md() -> str:
    return """# Nature Methods manuscript workspace

This directory is the Stage 9 manuscript-assembly workspace for RhoDyn.

Current status. Scaffold serialized only.

The contract/schema layer is present so future manuscript assembly can proceed substage by substage with machine gates, stable IDs, and atomic promotion. Reader-facing manuscript prose, evidence intake, citation resolution, figure legends, supplementary files, and submission package contents have not been generated yet.

PanelForge figure rendering is registered as a future Stage 9.6b dependency. The placeholder under `tools/panelforge-figures/` is not a clone, `.venv-panelforge` is not created by this scaffold, and no figure panels are rendered.
"""


def _figure_manifest_placeholder() -> str:
    return """# Stage 9.6b PanelForge manifest placeholder.
# This is not a renderable figure manifest.
# Stage 9.6b must replace this file after the figure-to-claim-to-artifact
# contract has passed and PanelForge has been cloned at the pinned ref.
manifest_status: scaffold_placeholder_not_renderable
figure_engine: panelforge-figures
pinned_ref: v3.14.1
version_doi: 10.5281/zenodo.20811171
figures: []
"""


def _panelforge_placeholder() -> str:
    return """# PanelForge placeholder

This directory is reserved for the Stage 9.6b local clone of
`panelforge-figures` at pinned ref `v3.14.1`.

Current status. Not cloned, not installed, and not rendered.

Do not place manuscript figures here. Stage 9.6b must replace this placeholder
with the actual engine clone only after the figure-to-claim-to-artifact
contract has passed.
"""


def _execution_memory() -> dict[str, Any]:
    return {
        "report_format": "rhodyn.stage9_execution_memory.v1",
        "generated_utc": _now(),
        "stage": 9,
        "status": "scaffold_serialized_not_started",
        "current_substage": "9.-1",
        "next_substage": "9.0",
        "next_substage_authorized": False,
        "project_binding": PROJECT_BINDING,
        "evidence_version": "not_set_until_stage9_0",
        "manuscript_drafting_started": False,
        "evidence_intake_started": False,
        "citation_resolution_started": False,
        "submission_package_started": False,
        "figure_engine_clone_started": False,
        "figure_engine_install_started": False,
        "figure_rendering_started": False,
        "figure_manifest_status": "scaffold_placeholder_not_renderable",
        "completed_substages": [
            {
                "substage": "9.-1",
                "status": "pass",
                "files_created_or_modified": [
                    "docs/stage9_manuscript_assembly_plan.md",
                    "docs/stage9_execution_memory.json",
                    "manuscript/nature_methods/contracts/",
                    "manuscript/nature_methods/figures/figures.manifest.yaml",
                    "tools/panelforge-figures/STAGE9_PLACEHOLDER.md",
                    "manuscript/nature_methods/gate_verdicts/9.-1.json",
                ],
                "evidence_dependencies": [],
                "gate_verdict_path": "manuscript/nature_methods/gate_verdicts/9.-1.json",
                "pass": True,
                "validation_outcome": "contract and schema scaffold serialized",
                "remaining_blockers": [
                    "Stage 9.0 evidence intake not authorized in this scaffold-only pass",
                    "Stage 9.1 venue guidance must be fetched from live official sources before drafting budgets are enforced",
                    "Stage 9.6b PanelForge clone, isolated install, manifest validation, and rendering are not authorized in this scaffold-only pass",
                    "ref-manager, editorial-elevation, and publication-surface-hygiene availability is not verified by this scaffold-only pass",
                ],
            }
        ],
        "substage_registry_path": "manuscript/nature_methods/contracts/stage9_substage_registry.json",
    }


def _gate_verdict() -> dict[str, Any]:
    return {
        "substage": "9.-1",
        "checks": [
            {
                "name": "schema_files_serialized",
                "predicate": "every declared ledger schema is written as JSON",
                "passed": True,
                "detail": f"{len(SCHEMA_NAMES)} schemas written under contracts/ledger_schemas",
            },
            {
                "name": "namespace_prefixes_defined",
                "predicate": "all Stage 9 ID namespace prefixes are documented",
                "passed": True,
                "detail": f"{len(ID_NAMESPACES)} namespaces documented",
            },
            {
                "name": "workspace_directories_initialized",
                "predicate": "required manuscript workspace directories exist",
                "passed": True,
                "detail": f"{len(WORKSPACE_DIRECTORIES) + len(REPO_DIRECTORIES)} directories initialized",
            },
            {
                "name": "figure_engine_binding_serialized",
                "predicate": "PanelForge binding is recorded but clone/install/render are not executed",
                "passed": True,
                "detail": "Stage 9.6b is serialized as a future rendering substage",
            },
            {
                "name": "execution_memory_initialized",
                "predicate": "docs/stage9_execution_memory.json exists and records scaffold-only boundary",
                "passed": True,
                "detail": "Stage 9.0 is not authorized by this pass",
            },
            {
                "name": "substage_registry_serialized",
                "predicate": "all Stage 9 substages are recorded with objectives, outputs, and gate predicates",
                "passed": True,
                "detail": f"{len(SUBSTAGES)} substages serialized",
            },
        ],
        "pass": True,
        "timestamp": _now(),
        "evidence_version": "not_set_until_stage9_0",
    }


def _stage9_roadmap_entry() -> dict[str, Any]:
    return {
        "stage": 9,
        "name": "Nature Methods manuscript assembly scaffold",
        "status": "stage9_scaffold_serialized_not_started",
        "current_gate": "Stage 9 scaffold serialized; manuscript production not started",
        "scope_rule": (
            "Stage 9 is currently limited to the 9.-1 contract/schema scaffold. Do not start evidence intake, "
            "citation resolution, drafting, figure rendering, review response, or submission packaging without explicit substage authorization."
        ),
        "substage_count": len(SUBSTAGES),
        "gate": [
            "Stage 9.-1 contract and schema files exist and pass the scaffold checker.",
            "Stage 9.0 through Stage 9.29 plus Stage 9.6b and Stage 9.25b remain not started.",
            "No manuscript draft sections, reference bibliography, evidence-lock ledgers, rendered figures, or submission package contents are created in this scaffold pass.",
        ],
        "artifacts": [
            "docs/stage9_manuscript_assembly_plan.md",
            "docs/stage9_execution_memory.json",
            "manuscript/nature_methods/README.md",
            "manuscript/nature_methods/contracts/",
            "manuscript/nature_methods/figures/figures.manifest.yaml",
            "manuscript/nature_methods/gate_verdicts/9.-1.json",
            "tools/panelforge-figures/STAGE9_PLACEHOLDER.md",
            "scripts/scaffold_stage9_manuscript_assembly.py",
            "scripts/check_stage9_scaffold.py",
            "tests/test_stage9_scaffold.py",
        ],
        "subphases": [
            {
                "id": item["id"],
                "name": item["title"],
                "goal": item["objective"],
                "gate": "; ".join(item.get("gate_predicates", [])),
                "status": item["status"] if item["id"] == "9.-1" else "not_started",
                "evidence": "manuscript/nature_methods/gate_verdicts/9.-1.json" if item["id"] == "9.-1" else "not_started",
            }
            for item in SUBSTAGES
        ],
    }


def _update_roadmap_execution_memory(root: Path) -> None:
    path = root / "docs" / "roadmap_execution_memory.json"
    if not path.exists():
        return
    payload = json.loads(path.read_text(encoding="utf-8"))
    current = payload.setdefault("current_position", {})
    current["active_stage"] = "Stage 9 scaffold serialized; manuscript production not started"
    current["after_stage7_7_8_recursive_hardening"] = (
        "Stage 7.7 and Stage 7.8 are recursively hardened against the Stage 7.6 release surface. "
        "The hardening verifies usability export bundles, methods-readiness crosswalk constants, validation report status, "
        "release checksum coverage, archive-manifest coverage, and the boundary that Stage 9 is limited to scaffold-only manuscript-assembly contracts."
    )
    current["after_stage9_scaffold_serialization"] = (
        "Stage 9 v2.1 has been serialized as a Nature Methods manuscript-assembly scaffold. "
        "Stage 9.-1 is complete as a contract/schema layer only. Stage 9.0 through Stage 9.29, including "
        "Stage 9.6b PanelForge rendering and Stage 9.25b reader-surface hygiene, remain not started. "
        "Manuscript production, evidence intake, citation resolution, figure rendering, and package assembly have not started."
    )
    current["stage7_active_gate"] = (
        "Stage 7.8 methods manuscript readiness package is complete and recursively hardened against Stage 7.6 release surfaces. "
        "Stage 8 remains conceptual product/commercial alignment and must not reshape the Stage 7 evidence path. "
        "Stage 9 is serialized only as a manuscript-assembly scaffold; no evidence intake, figure rendering, or drafting has started."
    )
    current["stage9_active_gate"] = "Stage 9 scaffold serialized; manuscript production not started"

    stage9 = _stage9_roadmap_entry()
    locks = [entry for entry in payload.get("stage_lock", []) if isinstance(entry, dict) and entry.get("stage") != 9]
    updated_locks = []
    inserted = False
    for entry in locks:
        if entry.get("stage") == 7:
            entry["current_gate"] = (
                "Stage 7.8 methods manuscript readiness package complete and recursively hardened against Stage 7.6 release surfaces. "
                "Stage 8 remains conceptual and cannot reshape the Stage 7 evidence path. Stage 9 is scaffolded only as a manuscript-assembly "
                "contract, with PanelForge reserved for future Stage 9.6b rendering and no manuscript production started."
            )
        updated_locks.append(entry)
        if entry.get("stage") == 8:
            updated_locks.append(stage9)
            inserted = True
    if not inserted:
        updated_locks.append(stage9)
    payload["stage_lock"] = updated_locks
    payload["updated"] = "2026-07-02"
    _write_json(path, payload)


def scaffold(root: Path = ROOT) -> dict[str, Any]:
    workspace = root / "manuscript" / "nature_methods"
    for rel in WORKSPACE_DIRECTORIES:
        path = workspace / rel
        path.mkdir(parents=True, exist_ok=True)
        gitkeep = path / ".gitkeep"
        if not any(path.iterdir()):
            gitkeep.write_text("", encoding="utf-8")
    for rel in REPO_DIRECTORIES:
        path = root / rel
        path.mkdir(parents=True, exist_ok=True)
        gitkeep = path / ".gitkeep"
        if not any(path.iterdir()):
            gitkeep.write_text("", encoding="utf-8")

    _write_text(root / "docs" / "stage9_manuscript_assembly_plan.md", _plan_md())
    _write_json(root / "docs" / "stage9_execution_memory.json", _execution_memory())
    _write_text(workspace / "README.md", _readme_md())
    _write_text(workspace / "contracts" / "id_namespace.md", _id_namespace_md())
    _write_text(workspace / "contracts" / "machine_gate_spec.md", _machine_gate_spec_md())
    _write_text(workspace / "contracts" / "atomic_write_protocol.md", _atomic_protocol_md())
    _write_text(workspace / "figures" / "figures.manifest.yaml", _figure_manifest_placeholder())
    _write_text(root / "tools" / "panelforge-figures" / "STAGE9_PLACEHOLDER.md", _panelforge_placeholder())
    _write_json(workspace / "contracts" / "stage9_project_binding.json", PROJECT_BINDING)
    _write_json(
        workspace / "contracts" / "stage9_substage_registry.json",
        {
            "scaffold_version": PROJECT_BINDING["scaffold_version"],
            "substage_count": len(SUBSTAGES),
            "patch_ledger": [
                {"id": patch_id, "title": title, "summary": summary}
                for patch_id, title, summary in PATCH_LEDGER
            ],
            "final_deliverables": FINAL_DELIVERABLES,
            "substages": SUBSTAGES,
        },
    )
    _write_json(workspace / "contracts" / "ledger_schema_map.json", {name: f"ledger_schemas/{name}.schema.json" for name in SCHEMA_NAMES})

    for name, schema in _schemas().items():
        _write_json(workspace / "contracts" / "ledger_schemas" / f"{name}.schema.json", schema)

    _write_json(workspace / "gate_verdicts" / "9.-1.json", _gate_verdict())
    _update_roadmap_execution_memory(root)

    return {
        "status": "pass",
        "workspace": "manuscript/nature_methods",
        "substage_count": len(SUBSTAGES),
        "schema_count": len(SCHEMA_NAMES),
        "executed_substage": "9.-1",
        "scaffold_only": True,
    }


def main() -> int:
    payload = scaffold(ROOT)
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

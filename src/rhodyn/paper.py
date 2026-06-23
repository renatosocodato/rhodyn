"""Optional manuscript case-study metadata and table adapter.

This module does not import or depend on the manuscript repository. It records
where a future user can obtain the public paper reproducibility assets and how
those assets should be treated by RhoDyn.
"""

from __future__ import annotations

from dataclasses import dataclass
from fnmatch import fnmatch
from pathlib import Path
from typing import Callable

from rhodyn.schema import (
    CouplingIntervalRecord,
    EndpointRecord,
    ReserveRecord,
    TrajectoryRecord,
    ValidationIssue,
    read_coupling_csv,
    read_endpoint_csv,
    read_reserve_csv,
    read_trajectory_csv,
)


PAPER_REPOSITORY = "https://github.com/renatosocodato/windowed_rhoA_model"
PAPER_RELEASE_COMMIT = "e63cc93a4b23d8b3d27cf25136b00d53fa6144f4"
PAPER_SOFTWARE_DOI = "10.5281/zenodo.19796404"
PAPER_DATA_DOI = "10.5281/zenodo.19796406"


@dataclass(frozen=True)
class PaperCaseStudy:
    """Metadata for the optional manuscript case study."""

    repository: str = PAPER_REPOSITORY
    release_commit: str = PAPER_RELEASE_COMMIT
    software_doi: str = PAPER_SOFTWARE_DOI
    data_doi: str = PAPER_DATA_DOI
    boundary: str = (
        "The manuscript repository and Zenodo data package are optional case-study inputs. "
        "They are not runtime dependencies, and RhoDyn did not generate the manuscript results."
    )


@dataclass(frozen=True)
class CaseStudyRole:
    """One released-table role that can be mapped into a RhoDyn schema."""

    name: str
    schema_kind: str
    description: str
    patterns: tuple[str, ...]


@dataclass(frozen=True)
class CaseStudyTable:
    """Validation summary for one discovered case-study table."""

    role: str
    schema_kind: str
    path: str
    rows: int
    issues: tuple[ValidationIssue, ...]


RecordSet = list[TrajectoryRecord] | list[EndpointRecord] | list[ReserveRecord] | list[CouplingIntervalRecord]
Reader = Callable[[str | Path], tuple[RecordSet, list[ValidationIssue]]]


ROLE_SPECS: tuple[CaseStudyRole, ...] = (
    CaseStudyRole(
        name="trajectory_tables",
        schema_kind="trajectory",
        description="tidy FRET or live-cell signal trajectories",
        patterns=("*trajectory*.csv", "*fret*.csv", "*live*cell*.csv", "trajectory_tables/*.csv"),
    ),
    CaseStudyRole(
        name="reserve_tables",
        schema_kind="reserve",
        description="calcium or other reserve-like response summaries",
        patterns=("*reserve*.csv", "*calcium*.csv", "reserve_tables/*.csv"),
    ),
    CaseStudyRole(
        name="endpoint_tables",
        schema_kind="endpoint",
        description="observed-versus-predicted endpoint summaries",
        patterns=("*endpoint*.csv", "endpoint_tables/*.csv"),
    ),
    CaseStudyRole(
        name="model_output_tables",
        schema_kind="endpoint",
        description="controller simulation or reduced-model comparison outputs already summarized as endpoint rows",
        patterns=("*model*output*.csv", "*model*comparison*.csv", "model_outputs/*.csv"),
    ),
    CaseStudyRole(
        name="coupling_tables",
        schema_kind="coupling",
        description="bounded-coupling interval or ROPE summaries",
        patterns=("*coupling*.csv", "*equivalence*.csv", "coupling_tables/*.csv"),
    ),
)


READERS: dict[str, Reader] = {
    "trajectory": read_trajectory_csv,
    "endpoint": read_endpoint_csv,
    "reserve": read_reserve_csv,
    "coupling": read_coupling_csv,
}


def paper_case_study_metadata() -> dict[str, str]:
    """Return paper case-study metadata as a plain dictionary."""

    case = PaperCaseStudy()
    return {
        "repository": case.repository,
        "release_commit": case.release_commit,
        "software_doi": case.software_doi,
        "data_doi": case.data_doi,
        "boundary": case.boundary,
    }


def expected_case_study_inputs() -> dict[str, str]:
    """Describe generic input roles for the paper-data adapter."""

    return {role.name: role.description for role in ROLE_SPECS}


def _matches_role(path: Path, root: Path, role: CaseStudyRole) -> bool:
    rel = path.relative_to(root).as_posix().lower()
    name = path.name.lower()
    return any(fnmatch(rel, pattern.lower()) or fnmatch(name, pattern.lower()) for pattern in role.patterns)


def _discover_role_tables(root: Path, role: CaseStudyRole) -> list[CaseStudyTable]:
    reader = READERS[role.schema_kind]
    tables: list[CaseStudyTable] = []
    if not root.exists():
        return tables
    for path in sorted(root.rglob("*.csv")):
        if path.name.startswith(".") or not _matches_role(path, root, role):
            continue
        rows, issues = reader(path)
        tables.append(
            CaseStudyTable(
                role=role.name,
                schema_kind=role.schema_kind,
                path=path.relative_to(root).as_posix(),
                rows=len(rows),
                issues=tuple(issues),
            )
        )
    return tables


def discover_case_study_inputs(root: str | Path) -> dict[str, list[CaseStudyTable]]:
    """Discover released CSV tables that match generic RhoDyn roles."""

    base = Path(root)
    return {role.name: _discover_role_tables(base, role) for role in ROLE_SPECS}


def read_case_study_tables(root: str | Path) -> dict[str, list[RecordSet]]:
    """Read valid discovered case-study tables by role.

    Tables with validation issues are skipped. Use `inspect_case_study_root()`
    when the issue details matter.
    """

    base = Path(root)
    payload: dict[str, list[RecordSet]] = {}
    discovered = discover_case_study_inputs(base)
    role_by_name = {role.name: role for role in ROLE_SPECS}
    for role_name, tables in discovered.items():
        role = role_by_name[role_name]
        reader = READERS[role.schema_kind]
        payload[role_name] = []
        for table in tables:
            if table.issues:
                continue
            rows, issues = reader(base / table.path)
            if not issues:
                payload[role_name].append(rows)
    return payload


def inspect_case_study_root(root: str | Path) -> dict[str, object]:
    """Inspect a local paper-data root for expected folders and table roles."""

    base = Path(root)
    expected = ["source_data", "supplementary", "results", "manuscript"]
    discovered = discover_case_study_inputs(base)
    return {
        "metadata": paper_case_study_metadata(),
        "root": str(base),
        "exists": base.exists(),
        "expected_roles": expected_case_study_inputs(),
        "folder_status": {name: (base / name).exists() for name in expected},
        "discovered_tables": discovered,
        "boundary": (
            "Discovered tables are local case-study inputs supplied by the user. "
            "They do not make the manuscript repository a RhoDyn dependency, and they do not imply "
            "that RhoDyn generated the manuscript results."
        ),
    }

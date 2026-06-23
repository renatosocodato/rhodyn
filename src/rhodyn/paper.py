"""Optional manuscript case-study metadata.

This module does not import or depend on the manuscript repository. It records
where a future user can obtain the public paper reproducibility assets and how
those assets should be treated by RhoDyn.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


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
    """Describe generic input roles for a future paper-data adapter."""

    return {
        "trajectory_tables": "tidy FRET or live-cell signal trajectories",
        "endpoint_tables": "observed-versus-predicted endpoint summaries",
        "reserve_tables": "calcium or other reserve-like response summaries",
        "model_outputs": "controller simulation and reduced-model comparison outputs",
    }


def inspect_case_study_root(root: str | Path) -> dict[str, object]:
    """Inspect a local paper-data root for expected high-level folders."""

    base = Path(root)
    expected = ["source_data", "supplementary", "results", "manuscript"]
    return {
        "root": str(base),
        "exists": base.exists(),
        "expected_roles": expected_case_study_inputs(),
        "folder_status": {name: (base / name).exists() for name in expected},
    }


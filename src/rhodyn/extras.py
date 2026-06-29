"""Optional dependency helpers.

The RhoDyn core package stays standard-library only. Optional extras extend
table handling, statistics, plotting, backend service deployment, and notebook
ergonomics without changing the base import path.
"""

from __future__ import annotations

from dataclasses import dataclass
from importlib.util import find_spec


@dataclass(frozen=True)
class OptionalExtra:
    """A named optional dependency group."""

    name: str
    packages: tuple[str, ...]
    purpose: str
    first_uses: tuple[str, ...]


OPTIONAL_EXTRAS: dict[str, OptionalExtra] = {
    "pandas": OptionalExtra(
        name="pandas",
        packages=("pandas",),
        purpose="faster and more ergonomic table loading, joins, and summaries",
        first_uses=("large trajectory tables", "paper case-study table adapters", "wide-to-tidy conversion"),
    ),
    "stats": OptionalExtra(
        name="stats",
        packages=("scipy",),
        purpose="richer statistical intervals, bootstrap utilities, and TOST helpers",
        first_uses=("Welch TOST", "bootstrap confidence intervals", "distribution diagnostics"),
    ),
    "plots": OptionalExtra(
        name="plots",
        packages=("matplotlib",),
        purpose="diagnostic plots for residence, reserve, coupling, and model comparison",
        first_uses=("residence traces", "margin-sensitivity curves", "model residual plots"),
    ),
    "backend": OptionalExtra(
        name="backend",
        packages=("fastapi", "httpx", "uvicorn"),
        purpose="stateless API service around frozen Stage 3 analysis surfaces",
        first_uses=("schema validation endpoint", "residence scoring endpoint", "model-comparison endpoint"),
    ),
    "notebooks": OptionalExtra(
        name="notebooks",
        packages=("jupyterlab",),
        purpose="interactive tutorial notebooks",
        first_uses=("synthetic workflows", "case-study walkthroughs"),
    ),
    "dev": OptionalExtra(
        name="dev",
        packages=("build", "mkdocs", "twine"),
        purpose="release engineering, documentation builds, and package publication dry runs",
        first_uses=("wheel and source builds", "documentation site builds", "PyPI publication checks"),
    ),
}


class MissingOptionalDependency(ImportError):
    """Raised when a function needs an optional dependency group."""


def extra_plan() -> list[OptionalExtra]:
    """Return the optional extras RhoDyn knows about."""

    return [OPTIONAL_EXTRAS[name] for name in sorted(OPTIONAL_EXTRAS)]


def missing_packages(extra: str) -> list[str]:
    """Return packages missing from an optional extra group."""

    if extra not in OPTIONAL_EXTRAS:
        known = ", ".join(sorted(OPTIONAL_EXTRAS))
        raise KeyError(f"unknown RhoDyn extra {extra!r}; known extras are {known}")
    return [package for package in OPTIONAL_EXTRAS[extra].packages if find_spec(package) is None]


def require_extra(extra: str, *, feature: str) -> None:
    """Raise a clear message when an optional dependency group is unavailable."""

    missing = missing_packages(extra)
    if not missing:
        return
    package_list = ", ".join(missing)
    raise MissingOptionalDependency(
        f"{feature} requires the rhodyn[{extra}] optional extra. "
        f"Install with `python -m pip install 'rhodyn[{extra}]'`. "
        f"Missing package(s): {package_list}."
    )

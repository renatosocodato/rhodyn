"""Run a deterministic dependency review for the RhoDyn release candidate.

This script performs an offline static review of declared Python optional extras
and the Node lockfile. It does not query vulnerability services by default, so it
is stable in clean-room environments. The report is a release gate for declared
surface hygiene rather than a substitute for a live advisory database scan before
publication.
"""

from __future__ import annotations

import argparse
import json
import re
import tomllib
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_JSON = Path("docs/dependency_review_report.json")
DEFAULT_MD = Path("docs/dependency_review_report.md")
REPORT_FORMAT = "rhodyn.dependency_review.v1"
BLOCKED_NAMES = {"httpx2", "sklearn", "tensorflow-gpu"}
VERSION_SPEC = re.compile(r"^([A-Za-z0-9_.-]+)(.*)$")


def _parse_req(req: str) -> tuple[str, str]:
    match = VERSION_SPEC.match(req.strip())
    if not match:
        return req, ""
    return match.group(1).lower(), match.group(2)


def review_dependencies(root: Path = ROOT) -> dict[str, Any]:
    pyproject_path = root / "pyproject.toml"
    package_lock_path = root / "package-lock.json"
    pyproject = tomllib.loads(pyproject_path.read_text(encoding="utf-8")) if pyproject_path.exists() else {}
    project = pyproject.get("project", {})
    core = project.get("dependencies", []) or []
    optional = project.get("optional-dependencies", {}) or {}
    python_records: list[dict[str, Any]] = []
    failures: list[str] = []
    warnings: list[str] = []

    if core:
        failures.append("core package dependencies are not empty")
    for group, requirements in sorted(optional.items()):
        for req in requirements:
            name, spec = _parse_req(req)
            record = {"ecosystem": "python", "group": group, "requirement": req, "name": name, "specifier": spec}
            python_records.append(record)
            if name in BLOCKED_NAMES:
                failures.append(f"blocked or suspicious Python dependency declared: {req}")
            if not spec:
                warnings.append(f"Python optional dependency has no version lower bound: {req}")
            if ">=" not in spec and name not in BLOCKED_NAMES:
                warnings.append(f"Python optional dependency lacks an explicit minimum version: {req}")

    node_records: list[dict[str, Any]] = []
    node_lock = json.loads(package_lock_path.read_text(encoding="utf-8")) if package_lock_path.exists() else {}
    packages = node_lock.get("packages", {}) if isinstance(node_lock, dict) else {}
    for path, payload in sorted(packages.items()):
        if not path or not isinstance(payload, dict):
            continue
        if path.startswith("node_modules/@"):
            parts = Path(path).parts
            name = f"{parts[-2]}/{parts[-1]}" if len(parts) >= 2 else path
        else:
            name = payload.get("name") or Path(path).name
        version = payload.get("version")
        dev = bool(payload.get("dev", False))
        node_records.append({"ecosystem": "node", "path": path, "name": name, "version": version, "dev": dev})
        if not version:
            warnings.append(f"Node lockfile package lacks version: {path}")
    if not package_lock_path.exists():
        warnings.append("package-lock.json is absent, so frontend dependency versions are not lockfile-reviewed")

    checks = {
        "pyproject_present": pyproject_path.exists(),
        "core_dependencies_empty": core == [],
        "optional_dependencies_declared": bool(optional),
        "no_blocked_dependency_names": not any(record["name"] in BLOCKED_NAMES for record in python_records),
        "node_lockfile_present": package_lock_path.exists(),
        "node_dependencies_locked": package_lock_path.exists() and all(record.get("version") for record in node_records),
        "playwright_is_dev_only": any(record["name"] == "@playwright/test" and record["dev"] for record in node_records),
        "static_review_completed": True,
    }
    failures.extend(name for name, ok in checks.items() if not ok)
    return {
        "report_format": REPORT_FORMAT,
        "generated_utc": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "status": "pass" if not failures else "fail",
        "checks": checks,
        "failures": sorted(set(failures)),
        "warnings": sorted(set(warnings)),
        "python_dependency_count": len(python_records),
        "node_dependency_count": len(node_records),
        "python_dependencies": python_records,
        "node_dependencies": node_records,
        "interpretation_boundary": "This is an offline static dependency review. A live advisory scan should still be run immediately before public release if credentials and network policy allow it.",
    }


def _write_markdown(payload: dict[str, Any], out: Path) -> None:
    lines = [
        "# Dependency-review report",
        "",
        f"Overall status. {payload['status']}",
        f"Python optional dependencies reviewed. {payload['python_dependency_count']}",
        f"Node lockfile packages reviewed. {payload['node_dependency_count']}",
        "",
        "## Checks",
        "",
    ]
    for name, ok in payload["checks"].items():
        lines.append(f"- {name}. {'pass' if ok else 'fail'}")
    if payload["warnings"]:
        lines.extend(["", "## Warnings", ""])
        for warning in payload["warnings"]:
            lines.append(f"- {warning}")
    if payload["failures"]:
        lines.extend(["", "## Failures", ""])
        for failure in payload["failures"]:
            lines.append(f"- {failure}")
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--json", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--md", type=Path, default=DEFAULT_MD)
    args = parser.parse_args()
    root = args.root.resolve()
    payload = review_dependencies(root)
    json_path = root / args.json
    md_path = root / args.md
    json_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    _write_markdown(payload, md_path)
    print(json.dumps({"status": payload["status"], "json": args.json.as_posix(), "md": args.md.as_posix()}, indent=2))
    return 0 if payload["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())

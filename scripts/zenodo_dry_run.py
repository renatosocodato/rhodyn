"""Run a Zenodo software-record dry run for RhoDyn.

The script validates local Zenodo metadata, citation metadata, release notes, and
checksum manifests. It also verifies that a source distribution can be built as
the archive payload. It never contacts Zenodo and never publishes a record.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
import tomllib
import venv
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_JSON = Path("docs/zenodo_dry_run_report.json")
DEFAULT_MD = Path("docs/zenodo_dry_run_report.md")
REPORT_FORMAT = "rhodyn.zenodo_dry_run.v1"


def _python_bin(venv_dir: Path) -> Path:
    return venv_dir / "bin" / "python"


def _sanitize(text: str, root: Path, temp_root: Path) -> str:
    return text.replace(str(root), ".").replace(str(temp_root), "$ZENODO_DRY_RUN")


def _run(cmd: list[str], *, cwd: Path, root: Path, temp_root: Path) -> dict[str, Any]:
    proc = subprocess.run(cmd, cwd=cwd, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    return {
        "command": [_sanitize(part, root, temp_root) for part in cmd],
        "cwd": _sanitize(str(cwd), root, temp_root),
        "returncode": proc.returncode,
        "stdout": _sanitize(proc.stdout, root, temp_root)[-6000:],
        "stderr": _sanitize(proc.stderr, root, temp_root)[-6000:],
        "status": "pass" if proc.returncode == 0 else "fail",
    }


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def run_zenodo_dry_run(root: Path = ROOT) -> dict[str, Any]:
    generated_byproducts = [root / "build", root / "src" / "rhodyn.egg-info"]
    preexisting_byproducts = {path: path.exists() for path in generated_byproducts}
    temp_root = Path(tempfile.mkdtemp(prefix="rhodyn_zenodo_dry_run_"))
    commands: list[dict[str, Any]] = []
    try:
        zenodo_path = root / ".zenodo.json"
        citation_path = root / "CITATION.cff"
        checksums_path = root / "docs" / "release_checksums.json"
        pyproject_path = root / "pyproject.toml"
        release_notes_path = root / "docs" / "release_notes_v0.1.0.md"
        zenodo = _read_json(zenodo_path) if zenodo_path.exists() else {}
        checksums = _read_json(checksums_path) if checksums_path.exists() else {}
        pyproject = tomllib.loads(pyproject_path.read_text(encoding="utf-8")) if pyproject_path.exists() else {}
        project = pyproject.get("project", {})
        citation = citation_path.read_text(encoding="utf-8") if citation_path.exists() else ""
        release_notes = release_notes_path.read_text(encoding="utf-8") if release_notes_path.exists() else ""

        build_env = temp_root / "build-env"
        dist_dir = temp_root / "dist"
        venv.EnvBuilder(with_pip=True, clear=True).create(build_env)
        build_python = _python_bin(build_env)
        commands.append(_run([str(build_python), "-m", "pip", "install", "--upgrade", "pip"], cwd=root, root=root, temp_root=temp_root))
        commands.append(_run([str(build_python), "-m", "pip", "install", "build>=1.2"], cwd=root, root=root, temp_root=temp_root))
        commands.append(_run([str(build_python), "-m", "build", "--sdist", "--outdir", str(dist_dir), str(root)], cwd=root, root=root, temp_root=temp_root))
        artifacts = sorted(path.name for path in dist_dir.glob("*")) if dist_dir.exists() else []

        checks = {
            "zenodo_metadata_present": zenodo_path.exists(),
            "zenodo_upload_type_software": zenodo.get("upload_type") == "software",
            "zenodo_title_names_rhodyn": "rhodyn" in str(zenodo.get("title", "")).lower(),
            "zenodo_creators_present": bool(zenodo.get("creators")),
            "zenodo_description_present": bool(zenodo.get("description")),
            "zenodo_license_present": bool(zenodo.get("license")),
            "citation_file_present": citation_path.exists(),
            "citation_names_rhodyn": "RhoDyn" in citation,
            "citation_version_matches_package": f"version: {project.get('version')}" in citation,
            "release_notes_present": release_notes_path.exists() and "RhoDyn v0.1.0" in release_notes,
            "checksum_manifest_present": checksums_path.exists() and bool(checksums.get("files")),
            "sdist_archive_built": any(name.endswith(".tar.gz") for name in artifacts),
            "no_zenodo_upload_attempted": True,
        }
        failures = [name for name, ok in checks.items() if not ok]
        failures.extend(f"command_failed::{i}::{step['command']}" for i, step in enumerate(commands) if step["status"] != "pass")
        return {
            "report_format": REPORT_FORMAT,
            "generated_utc": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
            "status": "pass" if not failures else "fail",
            "checks": checks,
            "failures": failures,
            "commands": commands,
            "distribution_artifacts": artifacts,
            "zenodo_metadata_summary": {
                "title": zenodo.get("title"),
                "upload_type": zenodo.get("upload_type"),
                "license": zenodo.get("license"),
                "creator_count": len(zenodo.get("creators", [])) if isinstance(zenodo.get("creators"), list) else 0,
            },
            "interpretation_boundary": "This dry run validates the local software-record payload only. It does not create, upload, reserve, or publish a Zenodo record.",
        }
    finally:
        shutil.rmtree(temp_root, ignore_errors=True)
        for path, existed_before in preexisting_byproducts.items():
            if not existed_before and path.exists():
                shutil.rmtree(path, ignore_errors=True)


def _write_markdown(payload: dict[str, Any], out: Path) -> None:
    lines = [
        "# Zenodo dry-run report",
        "",
        f"Overall status. {payload['status']}",
        "",
        "This dry run validates the local Zenodo software metadata and confirms that a source archive can be built. It does not upload or publish anything to Zenodo.",
        "",
        "## Checks",
        "",
    ]
    for name, ok in payload["checks"].items():
        lines.append(f"- {name}. {'pass' if ok else 'fail'}")
    lines.extend(["", "## Archive artifacts", ""])
    for artifact in payload["distribution_artifacts"]:
        lines.append(f"- {artifact}")
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
    payload = run_zenodo_dry_run(root)
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

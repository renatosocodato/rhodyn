"""Run an offline-safe PyPI packaging dry run for RhoDyn.

The script builds the source distribution and wheel in a temporary directory,
validates package metadata with twine, installs the built wheel in a separate
fresh environment, and exercises the installed CLI. It never uploads to PyPI or
TestPyPI.
"""

from __future__ import annotations

import argparse
import json
import os
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
DEFAULT_JSON = Path("docs/pypi_dry_run_report.json")
DEFAULT_MD = Path("docs/pypi_dry_run_report.md")
REPORT_FORMAT = "rhodyn.pypi_dry_run.v1"


def _python_bin(venv_dir: Path) -> Path:
    return venv_dir / ("Scripts/python.exe" if os.name == "nt" else "bin/python")


def _sanitize(text: str, root: Path, temp_root: Path) -> str:
    return text.replace(str(root), ".").replace(str(temp_root), "$PYPI_DRY_RUN")


def _run(cmd: list[str], *, cwd: Path, root: Path, temp_root: Path) -> dict[str, Any]:
    proc = subprocess.run(
        cmd,
        cwd=cwd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    return {
        "command": [_sanitize(part, root, temp_root) for part in cmd],
        "cwd": _sanitize(str(cwd), root, temp_root),
        "returncode": proc.returncode,
        "stdout": _sanitize(proc.stdout, root, temp_root)[-6000:],
        "stderr": _sanitize(proc.stderr, root, temp_root)[-6000:],
        "status": "pass" if proc.returncode == 0 else "fail",
    }


def _metadata(root: Path) -> dict[str, Any]:
    data = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))
    project = data.get("project", {})
    return {
        "name": project.get("name"),
        "version": project.get("version"),
        "requires_python": project.get("requires-python"),
        "core_dependencies": project.get("dependencies", []),
        "optional_dependency_groups": sorted((project.get("optional-dependencies") or {}).keys()),
    }


def run_pypi_dry_run(root: Path = ROOT) -> dict[str, Any]:
    generated_byproducts = [root / "build", root / "src" / "rhodyn.egg-info"]
    preexisting_byproducts = {path: path.exists() for path in generated_byproducts}
    temp_root = Path(tempfile.mkdtemp(prefix="rhodyn_pypi_dry_run_"))
    commands: list[dict[str, Any]] = []
    try:
        build_env = temp_root / "build-env"
        install_env = temp_root / "install-env"
        dist_dir = temp_root / "dist"
        venv.EnvBuilder(with_pip=True, clear=True).create(build_env)
        build_python = _python_bin(build_env)
        commands.append(_run([str(build_python), "-m", "pip", "install", "--upgrade", "pip"], cwd=root, root=root, temp_root=temp_root))
        commands.append(_run([str(build_python), "-m", "pip", "install", "build>=1.2", "twine>=5.0"], cwd=root, root=root, temp_root=temp_root))
        commands.append(_run([str(build_python), "-m", "build", "--sdist", "--wheel", "--outdir", str(dist_dir), str(root)], cwd=root, root=root, temp_root=temp_root))
        artifacts = sorted(path.name for path in dist_dir.glob("*")) if dist_dir.exists() else []
        artifact_paths = sorted(dist_dir.glob("*")) if dist_dir.exists() else []
        if artifact_paths:
            commands.append(_run([str(build_python), "-m", "twine", "check", "--strict", *map(str, artifact_paths)], cwd=root, root=root, temp_root=temp_root))
        else:
            commands.append({
                "command": ["twine", "check", "--strict", "$PYPI_DRY_RUN/dist/*"],
                "cwd": ".",
                "returncode": 1,
                "stdout": "",
                "stderr": "no distribution artifacts were built",
                "status": "fail",
            })

        wheel_paths = sorted(dist_dir.glob("*.whl")) if dist_dir.exists() else []
        venv.EnvBuilder(with_pip=True, clear=True).create(install_env)
        install_python = _python_bin(install_env)
        commands.append(_run([str(install_python), "-m", "pip", "install", "--upgrade", "pip"], cwd=root, root=root, temp_root=temp_root))
        if wheel_paths:
            commands.append(_run([str(install_python), "-m", "pip", "install", str(wheel_paths[0])], cwd=root, root=root, temp_root=temp_root))
            commands.append(_run([str(install_python), "-c", "import rhodyn; print(rhodyn.__version__)"], cwd=root, root=root, temp_root=temp_root))
            commands.append(_run([str(install_python), "-m", "rhodyn.cli", "--help"], cwd=root, root=root, temp_root=temp_root))
        else:
            commands.append({
                "command": ["python", "-m", "pip", "install", "$PYPI_DRY_RUN/dist/*.whl"],
                "cwd": ".",
                "returncode": 1,
                "stdout": "",
                "stderr": "no wheel artifact was built",
                "status": "fail",
            })

        meta = _metadata(root)
        checks = {
            "metadata_name_is_rhodyn": meta["name"] == "rhodyn",
            "metadata_version_is_0_1_0": meta["version"] == "0.1.0",
            "core_dependencies_empty": meta["core_dependencies"] == [],
            "sdist_built": any(name.endswith(".tar.gz") for name in artifacts),
            "wheel_built": any(name.endswith(".whl") for name in artifacts),
            "twine_check_passed": any("twine" in " ".join(step["command"]) and step["status"] == "pass" for step in commands),
            "installed_wheel_imported": any(step["command"][-1] == "import rhodyn; print(rhodyn.__version__)" and step["status"] == "pass" for step in commands),
            "installed_cli_help_passed": any(step["command"][-1] == "--help" and step["status"] == "pass" for step in commands),
            "no_upload_attempted": True,
        }
        failures = [name for name, ok in checks.items() if not ok]
        failures.extend(f"command_failed::{i}::{step['command']}" for i, step in enumerate(commands) if step["status"] != "pass")
        return {
            "report_format": REPORT_FORMAT,
            "generated_utc": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
            "status": "pass" if not failures else "fail",
            "metadata": meta,
            "artifacts": artifacts,
            "checks": checks,
            "failures": failures,
            "commands": commands,
            "interpretation_boundary": "This dry run validates packaging and installation only. It does not upload to PyPI or change RhoDyn analysis behavior.",
        }
    finally:
        shutil.rmtree(temp_root, ignore_errors=True)
        for path, existed_before in preexisting_byproducts.items():
            if not existed_before and path.exists():
                shutil.rmtree(path, ignore_errors=True)


def _write_markdown(payload: dict[str, Any], out: Path) -> None:
    lines = [
        "# PyPI dry-run report",
        "",
        f"Overall status. {payload['status']}",
        "",
        "This dry run built the source distribution and wheel, checked metadata with twine, installed the wheel in a fresh environment, and exercised the installed CLI without uploading to PyPI or TestPyPI.",
        "",
        "## Checks",
        "",
    ]
    for name, ok in payload["checks"].items():
        lines.append(f"- {name}. {'pass' if ok else 'fail'}")
    lines.extend(["", "## Distribution artifacts", ""])
    for artifact in payload["artifacts"]:
        lines.append(f"- {artifact}")
    lines.extend(["", "## Command summary", ""])
    for step in payload["commands"]:
        lines.append(f"- {step['status']}. `{' '.join(step['command'])}`")
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
    payload = run_pypi_dry_run(root)
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

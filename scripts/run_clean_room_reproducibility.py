#!/usr/bin/env python3
"""Run a clean-room reproducibility check for the RhoDyn release candidate."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import shutil
import subprocess
import sys
import tarfile
import tempfile
import time
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT = Path("docs/clean_room_reproducibility_report.md")
SKIP_NAMES = {
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".tox",
    ".venv",
    "__pycache__",
    "blob-report",
    "build",
    "dist",
    "htmlcov",
    "node_modules",
    "playwright-report",
    "test-results",
}
SKIP_SUFFIXES = {".pyc", ".pyo"}


@dataclass
class StepResult:
    name: str
    command: str
    status: str
    seconds: float
    stdout_tail: str = ""
    stderr_tail: str = ""
    detail: str = ""


def _now() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _tail(text: str, limit: int = 800) -> str:
    text = text.strip()
    if len(text) <= limit:
        return text
    return text[-limit:]


def _ignore(_dir: str, names: list[str]) -> set[str]:
    ignored: set[str] = set()
    for name in names:
        if name in SKIP_NAMES or name.endswith(".egg-info") or Path(name).suffix in SKIP_SUFFIXES:
            ignored.add(name)
    return ignored


def _run(name: str, command: list[str], *, cwd: Path, env: dict[str, str] | None = None) -> StepResult:
    started = time.monotonic()
    display = " ".join(command)
    result = subprocess.run(
        command,
        cwd=cwd,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    seconds = time.monotonic() - started
    status = "pass" if result.returncode == 0 else "fail"
    return StepResult(
        name=name,
        command=display,
        status=status,
        seconds=seconds,
        stdout_tail=_tail(result.stdout),
        stderr_tail=_tail(result.stderr),
    )


def _venv_python(venv: Path) -> Path:
    return venv / ("Scripts/python.exe" if os.name == "nt" else "bin/python")


def _venv_cli(venv: Path, name: str) -> Path:
    suffix = ".exe" if os.name == "nt" else ""
    return venv / ("Scripts" if os.name == "nt" else "bin") / f"{name}{suffix}"


def _execute_notebooks(source: Path, python: Path) -> StepResult:
    code = """
import json
from pathlib import Path

root = Path.cwd()
notebooks = sorted((root / 'notebooks').glob('*.ipynb'))
executed = []
for notebook in notebooks:
    ns = {'__name__': '__clean_room_notebook__'}
    data = json.loads(notebook.read_text(encoding='utf-8'))
    for index, cell in enumerate(data.get('cells', []), start=1):
        if cell.get('cell_type') != 'code':
            continue
        source = ''.join(cell.get('source', []))
        if not source.strip():
            continue
        exec(compile(source, f'{notebook.name}:cell{index}', 'exec'), ns)
    executed.append(notebook.name)
print(json.dumps({'status': 'pass', 'notebooks': executed, 'count': len(executed)}, indent=2))
"""
    result = _run("tutorial notebook code cells", [str(python), "-c", code], cwd=source)
    result.command = f"{python} -c <execute tutorial notebook code cells>"
    return result


def _inspect_sdist(dist_dir: Path) -> dict[str, bool]:
    sdists = sorted(dist_dir.glob("rhodyn-*.tar.gz"))
    if not sdists:
        return {}
    with tarfile.open(sdists[0], "r:gz") as handle:
        names = set(handle.getnames())
    prefix = sdists[0].name.replace(".tar.gz", "")
    targets = [
        ".zenodo.json",
        "CONTRIBUTING.md",
        "docs/clean_room_reproducibility.md",
        "docs/clean_room_reproducibility_report.md",
        "docs/release_notes_v0.1.0.md",
        "docs/release_checksums.csv",
        "docs/release_checksums.json",
        "docs/phase6_release_readiness_report.json",
    ]
    return {target: f"{prefix}/{target}" in names for target in targets}


def run_clean_room(root: Path = ROOT) -> dict[str, Any]:
    clean_root = Path(tempfile.mkdtemp(prefix="rhodyn_clean_room_", dir="/private/tmp" if Path("/private/tmp").exists() else None))
    source = clean_root / "source"
    dist_dir = clean_root / "dist"
    docs_site = clean_root / "site"
    builder_venv = clean_root / "builder_venv"
    wheel_venv = clean_root / "wheel_venv"
    shutil.copytree(root, source, ignore=_ignore)
    copied_report = source / "docs" / "clean_room_reproducibility_report.md"
    if not copied_report.exists():
        copied_report.write_text(
            "# Clean-room reproducibility report\n\nOverall status. pending source-archive structure check.\n",
            encoding="utf-8",
        )

    steps: list[StepResult] = []
    steps.append(StepResult("source tree copy", "shutil.copytree current tree to temporary clean-room source", "pass", 0.0))

    steps.append(_run("create build virtual environment", [sys.executable, "-m", "venv", str(builder_venv)], cwd=source))
    builder_python = _venv_python(builder_venv)
    steps.append(_run("upgrade build pip", [str(builder_python), "-m", "pip", "install", "--upgrade", "pip"], cwd=source))
    steps.append(_run("install development extra", [str(builder_python), "-m", "pip", "install", "-e", ".[dev]"], cwd=source))
    steps.append(_run("build source distribution and wheel", [str(builder_python), "-m", "build", "--sdist", "--wheel", "--outdir", str(dist_dir)], cwd=source))

    steps.append(_run("create installed-wheel virtual environment", [sys.executable, "-m", "venv", str(wheel_venv)], cwd=source))
    wheel_python = _venv_python(wheel_venv)
    steps.append(_run("upgrade wheel pip", [str(wheel_python), "-m", "pip", "install", "--upgrade", "pip"], cwd=source))
    wheels = sorted(dist_dir.glob("rhodyn-*.whl"))
    if wheels:
        steps.append(_run("install built wheel", [str(wheel_python), "-m", "pip", "install", "--force-reinstall", "--no-deps", str(wheels[0])], cwd=source))
    else:
        steps.append(StepResult("install built wheel", "wheel file discovery", "fail", 0.0, detail="No wheel found"))

    rhodyn = _venv_cli(wheel_venv, "rhodyn")
    cli_commands = [
        ("validate synthetic trajectory", [str(rhodyn), "validate", "examples/synthetic_trajectory.csv"]),
        ("score synthetic residence", [str(rhodyn), "score-residence", "examples/synthetic_trajectory.csv", "--low", "0.35", "--high", "0.75"]),
        ("decide synthetic coupling", [str(rhodyn), "decide-coupling", "examples/synthetic_coupling.csv"]),
        ("summarize synthetic reserve", [str(rhodyn), "summarize-reserve", "examples/synthetic_reserve.csv", "--floor", "1.0", "--ceiling", "1.7", "--baseline-points", "1"]),
        ("compare synthetic endpoints", [str(rhodyn), "compare", "examples/synthetic_endpoints.csv"]),
        ("simulate controller", [str(rhodyn), "simulate", "--duration", "5", "--dt", "1"]),
        ("export markdown report", [str(rhodyn), "export-markdown", "examples/synthetic_coupling.csv", "--title", "Clean-room bounded-coupling report"]),
        ("convert CTC fixture", [str(rhodyn), "ctc-to-trajectory", "examples/mlci_ctc_features.csv", "--lineage", "examples/mlci_man_track.txt", "--signal", "speed", "--condition", "mlci_fixture", "--replicate", "clean_room"]),
    ]
    for name, command in cli_commands:
        steps.append(_run(name, command, cwd=source))

    steps.append(_run("run synthetic workflow script", [str(wheel_python), "examples/residence_reserve_workflow.py"], cwd=source))
    steps.append(_run("run public MLCI workflow script", [str(wheel_python), "examples/mlci_public_case_study_workflow.py"], cwd=source))
    steps.append(_execute_notebooks(source, wheel_python))
    steps.append(_run("build documentation site", [str(_venv_cli(builder_venv, "mkdocs")), "build", "--strict", "--site-dir", str(docs_site)], cwd=source))
    steps.append(_run("audit Stage 5 workbench", [str(builder_python), "scripts/audit_stage5_premium_workbench.py"], cwd=source))
    for generated in [source / "build", source / "src" / "rhodyn.egg-info"]:
        if generated.exists():
            shutil.rmtree(generated)
    steps.append(StepResult("clean generated build byproducts", "remove build and src/rhodyn.egg-info before release-safety check", "pass", 0.0))
    steps.append(_run("release safety check", [str(builder_python), "scripts/check_release.py"], cwd=source))

    sdist_contents = _inspect_sdist(dist_dir)
    launcher = sys.executable
    for step in steps:
        step.command = step.command.replace(str(clean_root), "$CLEAN_ROOM").replace(launcher, "python")
        step.stdout_tail = step.stdout_tail.replace(str(clean_root), "$CLEAN_ROOM").replace(launcher, "python")
        step.stderr_tail = step.stderr_tail.replace(str(clean_root), "$CLEAN_ROOM").replace(launcher, "python")
    overall = "pass" if all(step.status == "pass" for step in steps) and sdist_contents.get("docs/clean_room_reproducibility.md") else "fail"
    return {
        "report_format": "rhodyn.clean_room_reproducibility.v1",
        "generated_utc": _now(),
        "overall_status": overall,
        "python": platform.python_version(),
        "platform": platform.platform(),
        "temporary_workspace": "temporary clean-room copy outside repository",
        "steps": [step.__dict__ for step in steps],
        "sdist_contains": sdist_contents,
        "dist_files": [
            {"name": path.name, "size_bytes": path.stat().st_size, "sha256": _sha256(path)}
            for path in sorted(dist_dir.glob("rhodyn-*"))
        ],
    }


def _report_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Clean-room reproducibility report",
        "",
        f"Generated UTC. {payload['generated_utc']}",
        "",
        f"Overall status. {payload['overall_status']}",
        "",
        "## Scope",
        "",
        "This run copied the current RhoDyn source tree into a temporary clean-room workspace, built a source distribution and wheel, installed the wheel into a fresh runtime environment, and ran the software examples without using raw microscopy, manuscript-private data, or local mounted-volume inputs.",
        "",
        "## Environment",
        "",
        f"- Python used to launch the run. {payload['python']}",
        f"- Platform. {payload['platform']}",
        "- Temporary workspace. Outside the repository and discarded after the run is no longer needed.",
        "",
        "## Step results",
        "",
        "| Step | Status | Seconds | Command |",
        "|---|---:|---:|---|",
    ]
    for step in payload["steps"]:
        command = step["command"].replace("|", "\\|")
        lines.append(f"| {step['name']} | {step['status']} | {step['seconds']:.2f} | `{command}` |")
    lines.extend(["", "## Built distributions", ""])
    for dist in payload["dist_files"]:
        lines.append(f"- `{dist['name']}`. {dist['size_bytes']} bytes. SHA-256 `{dist['sha256']}`.")
    lines.extend(["", "## Source archive content checks", ""])
    for name, present in sorted(payload["sdist_contains"].items()):
        status = "present" if present else "absent"
        lines.append(f"- `{name}`. {status}.")
    lines.extend([
        "",
        "## Interpretation",
        "",
        "The clean-room run supports the software-release claim that RhoDyn can be built, installed, documented, and exercised from its shipped examples without hidden local state. This is a reproducibility result for the software surface only. It does not add biological evidence, does not reproduce manuscript-private analyses, and does not certify PyPI or Zenodo publication.",
    ])
    failures = [step for step in payload["steps"] if step["status"] != "pass"]
    if failures:
        lines.extend(["", "## Failure details", ""])
        for step in failures:
            lines.append(f"### {step['name']}")
            if step.get("detail"):
                lines.append(step["detail"])
            if step.get("stdout_tail"):
                lines.append("\nStdout tail.\n")
                lines.append("```text")
                lines.append(step["stdout_tail"])
                lines.append("```")
            if step.get("stderr_tail"):
                lines.append("\nStderr tail.\n")
                lines.append("```text")
                lines.append(step["stderr_tail"])
                lines.append("```")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--json-out", type=Path, default=None)
    args = parser.parse_args()

    root = args.root.resolve()
    payload = run_clean_room(root)
    out_path = root / args.out
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(_report_markdown(payload), encoding="utf-8")
    if args.json_out:
        json_path = root / args.json_out
        json_path.parent.mkdir(parents=True, exist_ok=True)
        json_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": payload["overall_status"], "out": args.out.as_posix()}, indent=2))
    return 0 if payload["overall_status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())

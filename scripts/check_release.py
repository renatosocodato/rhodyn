"""Release-safety checks for the private RhoDyn package."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REQUIRED_FILES = [
    "README.md",
    "LICENSE",
    "NOTICE",
    "CITATION.cff",
    "CHANGELOG.md",
    "REPRODUCING.md",
    "pyproject.toml",
    "docs/roadmap.md",
    "docs/roadmap_execution_memory.json",
    "scripts/audit_stage4_service_contract.py",
    "scripts/audit_stage4_upload_stress.py",
    "scripts/audit_stage4_docker_smoke.py",
    "scripts/freeze_stage4_api_contract.py",
    "scripts/audit_stage5_frontend_scaffold.py",
    "scripts/audit_stage5_upload_flow_parity.py",
    "api/stage4/openapi.json",
    "api/stage4/frontend_contract.json",
    "api/stage4/contract_manifest.json",
    "docs/stage4_closeout.md",
    "docs/stage5_frontend.md",
    "docs/stage5_public_mlci_workflow.md",
    "frontend/stage5/index.html",
    "frontend/stage5/styles.css",
    "frontend/stage5/app.js",
    "examples/mlci_public_intensity_trajectory.csv",
]
LEAK_PATTERNS = [
    re.compile("/" + "Users/"),
    re.compile("/" + "Volumes/"),
    re.compile("Library/" + "LaunchAgents"),
    re.compile(r"sk-[A-Za-z0-9]"),
    re.compile("ghp" + r"_[A-Za-z0-9_]+"),
    re.compile("github" + r"_pat_[A-Za-z0-9_]+"),
    re.compile(r"xox[baprs]-[A-Za-z0-9-]+"),
]
RAW_EXTENSIONS = {".lif", ".czi", ".nd2", ".oir", ".oib", ".lsm", ".tif", ".tiff", ".prism", ".xml"}
GENERATED_DIRS = {"dist", "build", "htmlcov", ".pytest_cache"}


def _text_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for path in root.rglob("*"):
        if ".git" in path.parts or not path.is_file():
            continue
        if path.suffix.lower() in {
            ".py",
            ".md",
            ".toml",
            ".yml",
            ".yaml",
            ".cff",
            ".txt",
            ".json",
            ".html",
            ".css",
            ".js",
            ".csv",
            ".in",
            ".ipynb",
            ".example",
            ".Dockerfile",
        }:
            files.append(path)
    return files


def _tracked_paths(root: Path) -> set[str] | None:
    try:
        result = subprocess.run(
            ["git", "ls-files"],
            cwd=root,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return None
    return {line.strip() for line in result.stdout.splitlines() if line.strip()}


def _tracked_or_unknown(rel: Path, tracked: set[str] | None) -> bool:
    if tracked is None:
        return True
    rel_text = rel.as_posix()
    prefix = rel_text.rstrip("/") + "/"
    return rel_text in tracked or any(path.startswith(prefix) for path in tracked)


def check_release(root: Path = ROOT) -> dict[str, object]:
    failures: list[str] = []
    warnings: list[str] = []
    tracked = _tracked_paths(root)

    for name in REQUIRED_FILES:
        if not (root / name).exists():
            failures.append(f"missing required release file: {name}")

    pyproject = (root / "pyproject.toml").read_text(encoding="utf-8") if (root / "pyproject.toml").exists() else ""
    if 'version = "0.1.0"' not in pyproject:
        failures.append("pyproject.toml does not declare version 0.1.0")
    if "dependencies = []" not in pyproject:
        failures.append("core dependencies are not empty")
    if "[project.optional-dependencies]" not in pyproject:
        failures.append("optional dependency groups are not declared")

    readme = (root / "README.md").read_text(encoding="utf-8") if (root / "README.md").exists() else ""
    if "The manuscript was not generated with RhoDyn" not in readme:
        failures.append("README does not preserve manuscript independence boundary")
    if "optional reference case study" not in readme:
        failures.append("README does not describe the manuscript package as an optional case study")

    memory_path = root / "docs" / "roadmap_execution_memory.json"
    gate_path = root / "case_studies" / "stage3_case_study_bank_gate_report.json"
    if memory_path.exists():
        try:
            memory = json.loads(memory_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            failures.append(f"roadmap execution memory is not valid JSON: {exc}")
            memory = {}
        current = memory.get("current_position", {}) if isinstance(memory, dict) else {}
        if current.get("active_stage") != "Stage 5. Frontend":
            failures.append("roadmap execution memory does not mark Stage 5 as the active stage")
        stages = {entry.get("stage"): entry for entry in memory.get("stage_lock", []) if isinstance(entry, dict)}
        if stages.get(3, {}).get("status") != "complete_for_current_gate":
            failures.append("roadmap execution memory does not keep Stage 3 complete for the current gate")
        if stages.get(4, {}).get("status") != "frozen_for_stage5":
            failures.append("roadmap execution memory does not mark Stage 4 frozen for Stage 5")
        if stages.get(5, {}).get("status") != "active_scaffold":
            failures.append("roadmap execution memory does not mark Stage 5 as active scaffold")
        if stages.get(7, {}).get("status") != "not_ready":
            failures.append("roadmap execution memory does not keep Stage 7 as not ready")
        if stages.get(8, {}).get("status") != "conceptual_only":
            failures.append("roadmap execution memory does not keep Stage 8 conceptual only")
    if gate_path.exists():
        try:
            gate = json.loads(gate_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            failures.append(f"Stage 3 gate report is not valid JSON: {exc}")
            gate = {}
        if gate.get("status") != "pass":
            failures.append("Stage 3 case-study gate report does not pass")
        boundary = str(gate.get("interpretation_boundary", ""))
        if "do not imply that RhoDyn generated" not in boundary:
            failures.append("Stage 3 gate report does not preserve manuscript-independence boundary")

    for path in _text_files(root):
        text = path.read_text(encoding="utf-8", errors="ignore")
        for pattern in LEAK_PATTERNS:
            if pattern.search(text):
                failures.append(f"possible local path or credential pattern in {path.relative_to(root)}")
                break

    for path in root.rglob("*"):
        if ".git" in path.parts:
            continue
        rel = path.relative_to(root)
        if path.is_dir() and path.name in GENERATED_DIRS:
            if _tracked_or_unknown(rel, tracked):
                failures.append(f"generated directory should not be committed: {rel}")
            else:
                warnings.append(f"ignoring untracked generated directory: {rel}")
        if path.is_dir() and path.name.endswith(".egg-info"):
            if _tracked_or_unknown(rel, tracked):
                failures.append(f"egg-info directory should not be committed: {rel}")
            else:
                warnings.append(f"ignoring untracked egg-info directory: {rel}")
        if path.is_file() and path.suffix.lower() in RAW_EXTENSIONS and _tracked_or_unknown(rel, tracked):
            failures.append(f"raw or manuscript-private data-like file should not be packaged: {rel}")


    for script, label in [
        ("scripts/audit_stage5_frontend_scaffold.py", "Stage 5 frontend scaffold audit"),
        ("scripts/audit_stage5_upload_flow_parity.py", "Stage 5 upload-flow parity audit"),
    ]:
        check = subprocess.run(
            [sys.executable, script],
            cwd=root,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        if check.returncode != 0:
            detail = (check.stdout or check.stderr).strip()
            failures.append(f"{label} does not pass: {detail[:1200]}")

    if not (root / ".github" / "workflows" / "package.yml").exists():
        warnings.append("package build workflow is missing")

    return {
        "status": "pass" if not failures else "fail",
        "failures": failures,
        "warnings": warnings,
    }


def main() -> int:
    payload = check_release()
    print(json.dumps(payload, indent=2))
    return 0 if payload["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())

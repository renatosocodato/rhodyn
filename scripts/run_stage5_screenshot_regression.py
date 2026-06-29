"""Run the Stage 5 Playwright screenshot regression and write a release report."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_JSON = Path("docs/screenshot_regression_report.json")
DEFAULT_MD = Path("docs/screenshot_regression_report.md")
REPORT_FORMAT = "rhodyn.stage5_screenshot_regression.v1"


def _sanitize(text: str, root: Path) -> str:
    return text.replace(str(root), ".")[-8000:]


def _run(command: list[str], root: Path) -> dict[str, Any]:
    proc = subprocess.run(command, cwd=root, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    return {
        "command": command,
        "returncode": proc.returncode,
        "stdout_tail": _sanitize(proc.stdout, root),
        "stderr_tail": _sanitize(proc.stderr, root),
        "status": "pass" if proc.returncode == 0 else "fail",
    }


def run_screenshot_regression(root: Path = ROOT) -> dict[str, Any]:
    steps = [_run(["npm", "ci"], root), _run(["npm", "run", "test:stage5"], root)]
    combined = "\n".join(step["stdout_tail"] + "\n" + step["stderr_tail"] for step in steps)
    passed_match = re.search(r"(\d+) passed", combined)
    checks = {
        "npm_ci_passed": steps[0]["status"] == "pass",
        "playwright_screenshot_suite_passed": steps[1]["status"] == "pass",
        "stage5_visual_spec_present": (root / "tests" / "playwright" / "stage5.visual.spec.mjs").exists(),
        "desktop_and_mobile_projects_configured": "chromium-desktop" in (root / "playwright.config.mjs").read_text(encoding="utf-8") and "chromium-mobile" in (root / "playwright.config.mjs").read_text(encoding="utf-8"),
    }
    failures = [name for name, ok in checks.items() if not ok]
    return {
        "report_format": REPORT_FORMAT,
        "generated_utc": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "status": "pass" if not failures else "fail",
        "checks": checks,
        "failures": failures,
        "passed_test_count": int(passed_match.group(1)) if passed_match else None,
        "steps": steps,
        "interpretation_boundary": "This browser regression exercises the Stage 5 workbench UI with synthetic and public-example fixtures. It does not change RhoDyn analysis behavior.",
    }


def _write_markdown(payload: dict[str, Any], out: Path) -> None:
    lines = [
        "# Stage 5 screenshot-regression report",
        "",
        f"Overall status. {payload['status']}",
        f"Passed tests. {payload['passed_test_count']}",
        "",
        "## Checks",
        "",
    ]
    for name, ok in payload["checks"].items():
        lines.append(f"- {name}. {'pass' if ok else 'fail'}")
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
    payload = run_screenshot_regression(root)
    json_path = root / args.json
    md_path = root / args.md
    json_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    _write_markdown(payload, md_path)
    print(json.dumps({"status": payload["status"], "json": args.json.as_posix(), "md": args.md.as_posix(), "passed_test_count": payload["passed_test_count"]}, indent=2))
    return 0 if payload["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())

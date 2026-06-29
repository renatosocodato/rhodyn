"""Check local documentation links for the RhoDyn release surface.

Remote URLs are syntax-checked by default and are not fetched. Pass
``--check-remote`` to issue HTTP HEAD/GET requests, but the default release gate
is intentionally offline-stable.
"""

from __future__ import annotations

import argparse
import json
import re
import urllib.request
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_JSON = Path("docs/broken_link_scan_report.json")
DEFAULT_MD = Path("docs/broken_link_scan_report.md")
REPORT_FORMAT = "rhodyn.docs_link_scan.v1"
LINK_PATTERN = re.compile(r"(?<!!)\[([^\]]+)\]\(([^)]+)\)")
BARE_URL_PATTERN = re.compile(r"(?<!\()\bhttps?://[^\s)`]+")
MKDOCS_NAV_PATTERN = re.compile(r"^\s*-\s*[^:]+:\s*([^#\n]+\.md)\s*$", re.MULTILINE)
REMOTE_SCHEMES = {"http", "https", "mailto"}
DOC_SUFFIXES = {".md", ".ipynb"}
SKIP_DIRS = {".git", "build", "dist", "node_modules", "site", "playwright-report", "test-results"}


def _iter_docs(root: Path) -> list[Path]:
    paths = []
    for base in [root / "README.md", root / "REPRODUCING.md", root / "CONTRIBUTING.md", root / "CHANGELOG.md"]:
        if base.exists():
            paths.append(base)
    for directory in [root / "docs", root / "case_studies"]:
        if not directory.exists():
            continue
        for path in directory.rglob("*"):
            if any(part in SKIP_DIRS for part in path.parts):
                continue
            if path.is_file() and path.suffix in DOC_SUFFIXES:
                paths.append(path)
    return sorted(set(paths))


def _strip_anchor(target: str) -> tuple[str, str]:
    if "#" in target:
        path, anchor = target.split("#", 1)
        return path, anchor
    return target, ""


def _check_remote(url: str) -> tuple[bool, str]:
    if url.startswith("mailto:"):
        return True, "mailto syntax only"
    try:
        req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "rhodyn-link-check/0.1"})
        with urllib.request.urlopen(req, timeout=8) as response:
            return response.status < 400, f"HTTP {response.status}"
    except Exception as first_exc:  # noqa: BLE001 - report diagnostics, then try GET.
        try:
            req = urllib.request.Request(url, method="GET", headers={"User-Agent": "rhodyn-link-check/0.1"})
            with urllib.request.urlopen(req, timeout=8) as response:
                return response.status < 400, f"HTTP {response.status} after GET fallback"
        except Exception as second_exc:  # noqa: BLE001
            return False, f"{type(first_exc).__name__}; GET fallback {type(second_exc).__name__}"


def scan_docs_links(root: Path = ROOT, *, check_remote: bool = False) -> dict[str, Any]:
    records: list[dict[str, Any]] = []
    failures: list[str] = []
    def record_link(source: Path, raw_target: str, *, base_dir: Path) -> None:
        if not raw_target or raw_target.startswith("#"):
            return
        path_target, _anchor = _strip_anchor(raw_target)
        parsed = urlparse(path_target)
        rel_source = source.relative_to(root).as_posix() if source.is_relative_to(root) else source.as_posix()
        if parsed.scheme in REMOTE_SCHEMES:
            if check_remote:
                ok, detail = _check_remote(path_target)
                status = "pass" if ok else "fail"
            else:
                ok = bool(parsed.scheme == "mailto" or (parsed.netloc and parsed.scheme in {"http", "https"}))
                status = "pass" if ok else "fail"
                detail = "remote URL syntax checked only"
        elif parsed.scheme:
            ok = True
            status = "pass"
            detail = f"non-web scheme {parsed.scheme} left untouched"
        else:
            local = (base_dir / path_target).resolve()
            try:
                local.relative_to(root.resolve())
                inside_root = True
            except ValueError:
                inside_root = False
            ok = inside_root and local.exists()
            status = "pass" if ok else "fail"
            detail = "local target exists" if ok else "local target missing or escapes repository"
        record = {"source": rel_source, "target": raw_target, "status": status, "detail": detail}
        records.append(record)
        if not ok:
            failures.append(f"{rel_source} -> {raw_target}: {detail}")

    for source in _iter_docs(root):
        text = source.read_text(encoding="utf-8", errors="ignore")
        for match in LINK_PATTERN.finditer(text):
            record_link(source, match.group(2).strip(), base_dir=source.parent)
        for match in BARE_URL_PATTERN.finditer(text):
            record_link(source, match.group(0).strip().rstrip(".,"), base_dir=source.parent)

    mkdocs_path = root / "mkdocs.yml"
    if mkdocs_path.exists():
        mkdocs_text = mkdocs_path.read_text(encoding="utf-8", errors="ignore")
        for match in MKDOCS_NAV_PATTERN.finditer(mkdocs_text):
            record_link(mkdocs_path, match.group(1).strip(), base_dir=root / "docs")
        for match in BARE_URL_PATTERN.finditer(mkdocs_text):
            record_link(mkdocs_path, match.group(0).strip().rstrip(".,"), base_dir=root)
    return {
        "report_format": REPORT_FORMAT,
        "generated_utc": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "status": "pass" if not failures else "fail",
        "check_remote": check_remote,
        "link_count": len(records),
        "failures": failures,
        "records": records,
        "interpretation_boundary": "This scan verifies documentation link integrity only. Remote links are syntax-checked unless --check-remote is passed.",
    }


def _write_markdown(payload: dict[str, Any], out: Path) -> None:
    lines = [
        "# Documentation link-scan report",
        "",
        f"Overall status. {payload['status']}",
        f"Links scanned. {payload['link_count']}",
        f"Remote fetch enabled. {payload['check_remote']}",
        "",
    ]
    if payload["failures"]:
        lines.extend(["## Failures", ""])
        for failure in payload["failures"]:
            lines.append(f"- {failure}")
    else:
        lines.append("No broken local documentation links were detected.")
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--json", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--md", type=Path, default=DEFAULT_MD)
    parser.add_argument("--check-remote", action="store_true", help="Fetch remote HTTP(S) links. Default only checks URL syntax.")
    args = parser.parse_args()
    root = args.root.resolve()
    payload = scan_docs_links(root, check_remote=args.check_remote)
    json_path = root / args.json
    md_path = root / args.md
    json_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    _write_markdown(payload, md_path)
    print(json.dumps({"status": payload["status"], "json": args.json.as_posix(), "md": args.md.as_posix(), "link_count": payload["link_count"]}, indent=2))
    return 0 if payload["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())

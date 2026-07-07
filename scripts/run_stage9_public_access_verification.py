"""Verify public-access URLs exposed by the Nature Methods package.

This networked check is intentionally separate from the default offline release
checks. It probes only URLs visible in the Stage 9 submission-package Markdown
surfaces and writes a stable report for final author review.
"""

from __future__ import annotations

import json
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT / "manuscript" / "nature_methods"
SUBMISSION = WORKSPACE / "submission_package"
AUDITS = WORKSPACE / "audits"
JSON_OUT = AUDITS / "nature_methods_public_access_verification.json"
MD_OUT = AUDITS / "nature_methods_public_access_verification.md"

REPORT_FORMAT = "rhodyn.stage9_public_access_verification.v1"
URL_RE = re.compile(r"https?://[^\s<>)]+")
TRAILING_PUNCTUATION = "`'\".,;:"
FORBIDDEN_PUBLIC_REFERENCE_PATTERNS = [
    "github.com/renatosocodato/windowed_rhoA_model",
    "doi.org/10.5281/zenodo.19796404",
    "doi.org/10.5281/zenodo.19796406",
]


def _now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _submission_markdown_files() -> list[Path]:
    return sorted(path for path in SUBMISSION.glob("*.md") if path.is_file())


def _clean_url(raw: str) -> str:
    return raw.rstrip(TRAILING_PUNCTUATION)


def _normalization_reason(url: str) -> str:
    if re.match(r"https://github\.com/[^/\s]+/[^/@\s]+@[^/\s]+$", url):
        return "normalized_pip_vcs_github_ref"
    return "none"


def _normalized_url(url: str) -> str:
    match = re.match(r"https://github\.com/(?P<owner>[^/\s]+)/(?P<repo>[^/@\s]+)@(?P<ref>[^/\s]+)$", url)
    if match:
        return f"https://github.com/{match.group('owner')}/{match.group('repo')}/tree/{match.group('ref')}"
    return url


def _extract_urls() -> list[dict[str, str]]:
    records: list[dict[str, str]] = []
    seen: set[tuple[str, str]] = set()
    for path in _submission_markdown_files():
        text = path.read_text(encoding="utf-8")
        for match in URL_RE.finditer(text):
            raw = _clean_url(match.group(0))
            normalized = _normalized_url(raw)
            key = (path.relative_to(ROOT).as_posix(), raw)
            if key in seen:
                continue
            seen.add(key)
            records.append(
                {
                    "source": path.relative_to(ROOT).as_posix(),
                    "raw_url": raw,
                    "url": normalized,
                    "normalization": _normalization_reason(raw),
                }
            )
    return records


def _probe_url(url: str, timeout: int = 25) -> dict[str, Any]:
    for method in ["HEAD", "GET"]:
        request = Request(url, method=method, headers={"User-Agent": "rhodyn-stage9-public-access-check/1.0"})
        try:
            with urlopen(request, timeout=timeout) as response:
                if method == "GET":
                    response.read(1024)
                return {
                    "ok": 200 <= response.status < 400,
                    "method": method,
                    "status_code": response.status,
                    "resolved_url": response.geturl(),
                    "error": "",
                }
        except HTTPError as exc:
            last_error = {
                "ok": False,
                "method": method,
                "status_code": exc.code,
                "resolved_url": getattr(exc, "url", url),
                "error": str(exc),
            }
        except URLError as exc:
            last_error = {
                "ok": False,
                "method": method,
                "status_code": None,
                "resolved_url": url,
                "error": str(exc),
            }
    return last_error


def build_report() -> dict[str, Any]:
    url_records = _extract_urls()
    checked: list[dict[str, Any]] = []
    for record in url_records:
        probe = _probe_url(record["url"])
        checked.append({**record, **probe})

    package_text = "\n".join(path.read_text(encoding="utf-8") for path in _submission_markdown_files())
    forbidden_public_reference_hits = [
        pattern for pattern in FORBIDDEN_PUBLIC_REFERENCE_PATTERNS if pattern in package_text
    ]
    failed_urls = [row for row in checked if not row["ok"]]
    required_expected = [
        "https://github.com/renatosocodato/rhodyn",
        "https://github.com/renatosocodato/rhodyn/releases/tag/v0.1.0",
        "https://doi.org/10.5281/zenodo.21036616",
        "https://doi.org/10.5281/zenodo.21036615",
        "https://doi.org/10.5281/zenodo.14907827",
        "https://doi.org/10.5281/zenodo.5836623",
        "https://doi.org/10.5281/zenodo.10011861",
        "https://github.com/renatosocodato/panelforge-figures",
        "https://doi.org/10.5281/zenodo.20811171",
        "https://doi.org/10.5281/zenodo.20811170",
    ]
    observed = {row["url"] for row in checked} | {row["raw_url"] for row in checked}
    missing_expected = [url for url in required_expected if url not in observed]
    failures = []
    if failed_urls:
        failures.append("one_or_more_public_urls_failed")
    if forbidden_public_reference_hits:
        failures.append("unresolved_reference_use_case_links_remain_public_facing")
    if missing_expected:
        failures.append("expected_public_release_or_dataset_url_missing")
    return {
        "report_format": REPORT_FORMAT,
        "generated_utc": _now(),
        "status": "pass" if not failures else "fail",
        "source_files": [path.relative_to(ROOT).as_posix() for path in _submission_markdown_files()],
        "url_count": len(checked),
        "checked_urls": checked,
        "failed_urls": failed_urls,
        "forbidden_public_reference_hits": forbidden_public_reference_hits,
        "missing_expected_urls": missing_expected,
        "checks": {
            "all_visible_public_urls_resolve": not failed_urls,
            "unresolved_optional_reference_case_links_not_advertised": not forbidden_public_reference_hits,
            "expected_release_dataset_and_renderer_urls_present": not missing_expected,
        },
        "failures": failures,
        "interpretation_boundary": (
            "This report verifies public URL accessibility for the Nature Methods submission-package surfaces. "
            "It does not upload files, alter DOI records, modify GitHub or Zenodo state, or certify journal acceptance."
        ),
    }


def _write_markdown(report: dict[str, Any]) -> None:
    lines = [
        "# Nature Methods public-access verification",
        "",
        f"Generated UTC. `{report['generated_utc']}`.",
        "",
        f"Status. `{report['status']}`.",
        "",
        "## Checks",
        "",
    ]
    for name, passed in report["checks"].items():
        lines.append(f"- {name}. {'pass' if passed else 'fail'}.")
    lines.extend(["", "## Public URLs checked", "", "| source | URL | resolved URL | status |", "|---|---|---|---|"])
    for row in report["checked_urls"]:
        status = f"{row['status_code']} via {row['method']}" if row.get("status_code") else row.get("error", "unresolved")
        raw_note = "" if row["raw_url"] == row["url"] else f" from `{row['raw_url']}`"
        lines.append(f"| `{row['source']}` | {row['url']}{raw_note} | {row.get('resolved_url', '')} | {status} |")
    lines.extend(
        [
            "",
            "## Reference-use-case boundary",
            "",
            "The optional RhoA/microglia reference-use-case records are not advertised as public URLs in the Nature Methods package unless the repository and DOI records resolve publicly or through reviewer-access links.",
            "",
            "## Boundary",
            "",
            report["interpretation_boundary"],
        ]
    )
    MD_OUT.parent.mkdir(parents=True, exist_ok=True)
    MD_OUT.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def main() -> int:
    report = build_report()
    JSON_OUT.parent.mkdir(parents=True, exist_ok=True)
    JSON_OUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    _write_markdown(report)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())

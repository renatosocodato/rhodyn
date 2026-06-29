"""Check public GitHub and Zenodo accessibility for the RhoDyn release.

This script is intentionally separate from the default offline release safety
check. It performs network requests against public URLs and writes a compact
report that the offline Phase 6 audit can consume later.
"""

from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
REPORT_FORMAT = "rhodyn.public_release_integrity.v1"
OWNER = "renatosocodato"
REPO = "rhodyn"
TAG = "v0.1.0"
REPO_URL = f"https://github.com/{OWNER}/{REPO}"
REPO_API_URL = f"https://api.github.com/repos/{OWNER}/{REPO}"
RELEASE_URL = f"{REPO_URL}/releases/tag/{TAG}"
RELEASE_API_URL = f"{REPO_API_URL}/releases/tags/{TAG}"
TAG_ARCHIVE_URL = f"{REPO_URL}/archive/refs/tags/{TAG}.tar.gz"
ZENODO_RECORD_URL = "https://zenodo.org/records/21036616"
ZENODO_API_URL = "https://zenodo.org/api/records/21036616"
VERSION_DOI_URL = "https://doi.org/10.5281/zenodo.21036616"
CONCEPT_DOI_URL = "https://doi.org/10.5281/zenodo.21036615"
EXPECTED_ASSETS = {
    "rhodyn-0.1.0.tar.gz",
    "rhodyn-0.1.0-py3-none-any.whl",
    "rhodyn-v0.1.0-release-checksums.csv",
    "rhodyn-v0.1.0-release-checksums.json",
}


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _request(url: str, *, method: str = "GET", timeout: int = 30) -> dict[str, Any]:
    request = Request(url, method=method, headers={"User-Agent": "rhodyn-public-release-check/1.0"})
    try:
        with urlopen(request, timeout=timeout) as response:
            body = response.read() if method == "GET" else b""
            return {
                "ok": 200 <= response.status < 400,
                "status_code": response.status,
                "url": url,
                "resolved_url": response.geturl(),
                "body": body.decode("utf-8", errors="replace") if body else "",
            }
    except HTTPError as exc:
        return {"ok": False, "status_code": exc.code, "url": url, "resolved_url": getattr(exc, "url", url), "error": str(exc), "body": ""}
    except URLError as exc:
        return {"ok": False, "status_code": None, "url": url, "resolved_url": url, "error": str(exc), "body": ""}


def _json_get(url: str) -> tuple[dict[str, Any], dict[str, Any] | None]:
    result = _request(url)
    if not result["ok"]:
        return result, None
    try:
        return result, json.loads(result.get("body", ""))
    except json.JSONDecodeError as exc:
        result["ok"] = False
        result["error"] = f"invalid JSON response: {exc}"
        return result, None


def _local_git_commit(tag: str) -> str | None:
    try:
        result = subprocess.run(
            ["git", "rev-list", "-n", "1", tag],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return None
    return result.stdout.strip() or None


def _asset_head(asset_url: str) -> dict[str, Any]:
    # HEAD avoids downloading release assets while still proving public access.
    result = _request(asset_url, method="HEAD")
    if result["ok"]:
        result.pop("resolved_url", None)  # do not record signed redirect URLs.
        return result
    fallback = _request(asset_url, method="GET")
    fallback.pop("body", None)
    fallback.pop("resolved_url", None)
    return fallback


def build_report() -> dict[str, Any]:
    failures: list[str] = []
    warnings: list[str] = []

    repo_probe, repo_payload = _json_get(REPO_API_URL)
    release_probe, release_payload = _json_get(RELEASE_API_URL)
    tag_archive_probe = _request(TAG_ARCHIVE_URL, method="HEAD")
    zenodo_probe, zenodo_payload = _json_get(ZENODO_API_URL)
    version_doi_probe = _request(VERSION_DOI_URL)
    concept_doi_probe = _request(CONCEPT_DOI_URL)

    asset_reports: list[dict[str, Any]] = []
    asset_names: set[str] = set()
    if release_payload:
        for asset in release_payload.get("assets", []):
            name = str(asset.get("name", ""))
            browser_download_url = str(asset.get("browser_download_url", ""))
            asset_names.add(name)
            access = _asset_head(browser_download_url) if browser_download_url else {"ok": False, "status_code": None, "url": "", "error": "missing browser_download_url"}
            asset_reports.append(
                {
                    "name": name,
                    "size": asset.get("size"),
                    "state": asset.get("state"),
                    "download_url": browser_download_url,
                    "public_access_status": access.get("status_code"),
                    "public_access_ok": bool(access.get("ok")),
                }
            )

    local_tag_commit = _local_git_commit(TAG)
    release_target = str(release_payload.get("target_commitish", "")) if release_payload else ""
    zenodo_metadata = zenodo_payload.get("metadata", {}) if zenodo_payload else {}
    zenodo_files = {str(item.get("key") or item.get("filename") or "") for item in (zenodo_payload.get("files", []) if zenodo_payload else [])}

    checks = {
        "github_repo_api_public": bool(repo_probe.get("ok") and repo_payload and repo_payload.get("private") is False),
        "github_repo_html_public": _request(REPO_URL, method="HEAD").get("ok"),
        "github_release_api_public": bool(release_probe.get("ok") and release_payload and not release_payload.get("draft", True)),
        "github_release_html_public": _request(RELEASE_URL, method="HEAD").get("ok"),
        "github_release_not_prerelease": bool(release_payload and release_payload.get("prerelease") is False),
        "github_tag_archive_public": bool(tag_archive_probe.get("ok")),
        "github_release_expected_assets_present": EXPECTED_ASSETS.issubset(asset_names),
        "github_release_expected_assets_public": all(item.get("public_access_ok") for item in asset_reports if item.get("name") in EXPECTED_ASSETS) and EXPECTED_ASSETS.issubset(asset_names),
        "local_tag_exists": local_tag_commit is not None,
        "zenodo_record_api_public": bool(zenodo_probe.get("ok") and zenodo_payload),
        "zenodo_record_html_public": _request(ZENODO_RECORD_URL, method="HEAD").get("ok"),
        "zenodo_version_doi_resolves": bool(version_doi_probe.get("ok") and "zenodo.org" in str(version_doi_probe.get("resolved_url", ""))),
        "zenodo_concept_doi_resolves": bool(concept_doi_probe.get("ok") and "zenodo.org" in str(concept_doi_probe.get("resolved_url", ""))),
        "zenodo_metadata_version_matches": zenodo_metadata.get("version") == "0.1.0",
        "zenodo_metadata_resource_type_software": (zenodo_metadata.get("resource_type") or {}).get("type") == "software",
        "zenodo_expected_assets_present": EXPECTED_ASSETS.issubset(zenodo_files),
    }

    if release_target and local_tag_commit and release_target not in {TAG, local_tag_commit, "main"}:
        warnings.append(f"GitHub release target_commitish is {release_target!r}; local {TAG} resolves to {local_tag_commit}.")

    for name, passed in checks.items():
        if not passed:
            failures.append(name)

    report = {
        "report_format": REPORT_FORMAT,
        "generated_utc": _now(),
        "status": "pass" if not failures else "fail",
        "checks": checks,
        "failures": failures,
        "warnings": warnings,
        "github": {
            "repository": REPO_URL,
            "visibility": "public" if checks["github_repo_api_public"] else "not_verified_public",
            "release_url": RELEASE_URL,
            "tag": TAG,
            "local_tag_commit": local_tag_commit,
            "release_target_commitish": release_target,
            "tag_archive_url": TAG_ARCHIVE_URL,
            "asset_names": sorted(asset_names),
            "assets": asset_reports,
        },
        "zenodo": {
            "record_url": ZENODO_RECORD_URL,
            "api_url": ZENODO_API_URL,
            "version_doi": "10.5281/zenodo.21036616",
            "concept_doi": "10.5281/zenodo.21036615",
            "version_doi_resolved_url": version_doi_probe.get("resolved_url"),
            "concept_doi_resolved_url": concept_doi_probe.get("resolved_url"),
            "metadata_version": zenodo_metadata.get("version"),
            "metadata_resource_type": zenodo_metadata.get("resource_type"),
            "file_names": sorted(name for name in zenodo_files if name),
        },
        "interpretation_boundary": "This report verifies public accessibility of the v0.1.0 software release surfaces. It does not upload to PyPI, mutate GitHub or Zenodo records, or change RhoDyn analysis behavior.",
    }
    return report


def _write_markdown(report: dict[str, Any], path: Path) -> None:
    checks = report.get("checks", {})
    lines = [
        "# Public release integrity report",
        "",
        f"Generated UTC. {report.get('generated_utc', '')}",
        "",
        f"Overall status. {report.get('status')}",
        "",
        "## Public release surfaces",
        "",
        f"- GitHub repository. {report['github']['repository']}",
        f"- GitHub release. {report['github']['release_url']}",
        f"- Git tag. {report['github']['tag']} at `{report['github']['local_tag_commit']}`",
        f"- Zenodo version DOI. https://doi.org/{report['zenodo']['version_doi']}",
        f"- Zenodo concept DOI. https://doi.org/{report['zenodo']['concept_doi']}",
        f"- Zenodo record. {report['zenodo']['record_url']}",
        "",
        "## Checks",
        "",
    ]
    for name in sorted(checks):
        lines.append(f"- {name}. {'pass' if checks[name] else 'fail'}")
    if report.get("warnings"):
        lines.extend(["", "## Warnings", ""])
        lines.extend(f"- {warning}" for warning in report["warnings"])
    lines.extend(["", "## Boundary", "", str(report.get("interpretation_boundary", "")), ""])
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Check public accessibility of RhoDyn v0.1.0 release surfaces.")
    parser.add_argument("--json-out", default="docs/public_release_integrity_report.json")
    parser.add_argument("--md-out", default="docs/public_release_integrity_report.md")
    args = parser.parse_args()
    report = build_report()
    json_path = ROOT / args.json_out
    md_path = ROOT / args.md_out
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    _write_markdown(report, md_path)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())

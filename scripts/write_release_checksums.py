"""Write checksum manifests for RhoDyn release-critical surfaces."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CSV = Path("docs/release_checksums.csv")
DEFAULT_JSON = Path("docs/release_checksums.json")
SKIP_DIRS = {
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    "__pycache__",
    "blob-report",
    "build",
    "dist",
    "htmlcov",
    "node_modules",
    "playwright-report",
    "test-results",
}
SKIP_FILES = {
    "docs/release_checksums.csv",
    "docs/release_checksums.json",
    "docs/phase6_release_readiness_report.json",
}
INCLUDED_PREFIXES = (
    ".github/workflows/",
    "api/",
    "case_studies/",
    "deploy/",
    "docs/",
    "examples/",
    "frontend/",
    "notebooks/",
    "scripts/",
    "src/",
    "tests/",
)
ROOT_FILES = {
    ".zenodo.json",
    "CHANGELOG.md",
    "CITATION.cff",
    "CONTRIBUTING.md",
    "LICENSE",
    "MANIFEST.in",
    "NOTICE",
    "README.md",
    "REPRODUCING.md",
    "mkdocs.yml",
    "package-lock.json",
    "package.json",
    "playwright.config.mjs",
    "pyproject.toml",
}
TEXTLIKE_SUFFIXES = {
    "",
    ".cff",
    ".css",
    ".csv",
    ".Dockerfile",
    ".example",
    ".html",
    ".in",
    ".ipynb",
    ".js",
    ".json",
    ".md",
    ".mjs",
    ".py",
    ".toml",
    ".txt",
    ".tsv",
    ".yaml",
    ".yml",
    ".zip",
}


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _should_include(path: Path, root: Path) -> bool:
    rel = path.relative_to(root).as_posix()
    if rel in SKIP_FILES:
        return False
    if any(part in SKIP_DIRS for part in path.relative_to(root).parts):
        return False
    if path.name == ".DS_Store" or path.name.startswith("~$"):
        return False
    if rel in ROOT_FILES:
        return True
    if rel.startswith(INCLUDED_PREFIXES):
        return path.suffix in TEXTLIKE_SUFFIXES or path.name.endswith(".Dockerfile")
    return False


def collect_checksums(root: Path = ROOT) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for path in sorted(root.rglob("*")):
        if not path.is_file() or not _should_include(path, root):
            continue
        rel = path.relative_to(root).as_posix()
        rows.append(
            {
                "path": rel,
                "size_bytes": path.stat().st_size,
                "sha256": _sha256(path),
            }
        )
    return rows


def write_manifests(root: Path, csv_path: Path, json_path: Path) -> dict[str, object]:
    rows = collect_checksums(root)
    csv_abs = root / csv_path
    json_abs = root / json_path
    csv_abs.parent.mkdir(parents=True, exist_ok=True)
    json_abs.parent.mkdir(parents=True, exist_ok=True)
    with csv_abs.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["path", "size_bytes", "sha256"], lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    payload = {
        "report_format": "rhodyn.release_checksums.v1",
        "generated_utc": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "root": ".",
        "file_count": len(rows),
        "files": rows,
    }
    json_abs.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--csv", type=Path, default=DEFAULT_CSV)
    parser.add_argument("--json", type=Path, default=DEFAULT_JSON)
    args = parser.parse_args()
    payload = write_manifests(args.root.resolve(), args.csv, args.json)
    print(json.dumps({"status": "pass", "file_count": payload["file_count"], "csv": args.csv.as_posix(), "json": args.json.as_posix()}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

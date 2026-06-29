# RhoDyn v0.1.0 public release checklist

RhoDyn `v0.1.0` is a public software release through GitHub and Zenodo. It is
not a public scientific-claim surface and does not replace the manuscript
reproducibility repository. Phase 6 remains active for post-release hardening.
RhoDyn can now be cited through the GitHub release archive and Zenodo software
record, while PyPI publication remains intentionally unclaimed until a separate
package-index upload is completed.

## Phase 6 release horizon

### 6.1 Release boundary

- The first official release is a Python library plus CLI for residence-window
  scoring, bounded coupling, reserve summaries, reduced-architecture
  comparison, uncertainty, diagnostics, reports, and the Stage 5 workbench.
- The release must not contain manuscript-private data, hidden local paths, raw
  microscopy, or claims that RhoDyn generated the RhoA/microglia manuscript.

Gate. Boundary text appears in README, roadmap, release notes, and archive
metadata before any public/citable release.

### 6.2 Packaging

- `pyproject.toml` is clean and contains the CLI entry point.
- Wheel and source distribution build successfully.
- Optional extras include the retained user paths, including stats, plots,
  backend, notebooks, all, and dev when the dev toolchain is finalized.
- Installed outputs expose the package version.

Gate. Install from a fresh clone and run examples from scratch.

### 6.3 Documentation

- README quickstart is current.
- API reference, CLI reference, input-schema guide, interpretation guide,
  tutorials, example reports, and reproducibility card exist.

Gate. A biologist can run the basic workflow, and a quantitative user can audit
parameters without reading the source code first.

### 6.4 Release automation

- CI covers supported Python versions.
- Package build, docs build, Docker build, tests, browser regression, and
  release-safety checks run from CI.
- Changelog, citation metadata, license, contribution docs, and release
  checklist are maintained.

Gate. Every release surface builds from CI, not from a local machine.

### 6.5 Archive and citation

- GitHub release is public.
- Zenodo version DOI and concept DOI for RhoDyn resolve publicly.
- `CITATION.cff`, release notes, source archive, release assets, and checksum
  manifest are complete.

Gate. The archive contains only intended software and public examples, and the
GitHub repository, release page, tag archive, release assets, Zenodo record, and
DOI links resolve without authentication.

### 6.6 Clean-room reproducibility

- Fresh clone.
- Fresh virtual environment.
- Installed wheel.
- CLI examples.
- Tutorial notebooks.
- Documentation build.
- Stage 5 workbench run.
- Report export.

Gate. No step depends on the developer's local machine.

### 6.7 Final ultra-hardening

- Local path and secret scans.
- Dependency vulnerability review.
- Broken-link documentation scan.
- Screenshot regression.
- CLI/API parity.
- Docker parity.
- PyPI dry run.
- Zenodo dry run.
- Frontend/backend output parity.

Gate. All official release surfaces pass together. The current final-hardening
evidence is recorded in `docs/final_release_hardening.md`,
`docs/public_release_integrity_report.md`, and the paired PyPI dry-run, Zenodo
publication, Zenodo dry-run, link-scan, dependency-review, Docker, screenshot,
and clean-room reports.

## Required before or after a public archive

- README, LICENSE, NOTICE, CITATION, CHANGELOG, and REPRODUCING files are
  present.
- `pyproject.toml` reports version `0.1.0`.
- The source package imports without optional dependencies.
- Unit tests pass.
- Source distribution and wheel build successfully.
- Wheel and source distribution install in a clean environment.
- `scripts/check_release.py` reports no release-safety failures.
- `scripts/audit_phase6_release_readiness.py` reports Phase 6 readiness with
  no unresolved public-release gaps.
- `scripts/check_public_release_integrity.py` verifies the public GitHub and
  Zenodo release surfaces after publication.
- GitHub Actions tests pass on `main`.

## Distribution decision

The first public archive is GitHub plus Zenodo. The current citable software
record is the Zenodo version DOI `10.5281/zenodo.21036616`, with concept DOI
`10.5281/zenodo.21036615`. PyPI remains a later distribution decision and is
not claimed by the v0.1.0 public release.

## Safety boundary

The release package must not contain raw microscopy files, manuscript-private
materials, local machine paths, credentials, mounted-volume paths, or generated
debug outputs. The manuscript repository and Zenodo data package remain cited
as optional case-study inputs only.

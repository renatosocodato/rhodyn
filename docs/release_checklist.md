# Private v0.1.0 release checklist

RhoDyn `v0.1.0` is a private software hardening release. It is not a public
scientific claim surface and does not replace the manuscript reproducibility
repository. Phase 6 is active, and the hardening gates can pass before publication. RhoDyn should not be described as professionally citable until the release-candidate evidence is paired with an intentional version tag, GitHub archive, and Zenodo software record.

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

- GitHub release is prepared.
- Zenodo DOI for RhoDyn itself is prepared.
- `CITATION.cff`, release notes, source archive, and checksum manifest are
  complete.

Gate. The archive contains only intended software and public examples.

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

Gate. All official release surfaces pass together. The current final-hardening evidence is recorded in `docs/final_release_hardening.md` and the paired PyPI, Zenodo, link-scan, and dependency-review reports.

## Required before a private archive

- README, LICENSE, NOTICE, CITATION, CHANGELOG, and REPRODUCING files are
  present.
- `pyproject.toml` reports version `0.1.0`.
- The source package imports without optional dependencies.
- Unit tests pass.
- Source distribution and wheel build successfully.
- Wheel and source distribution install in a clean environment.
- `scripts/check_release.py` reports no release-safety failures.
- `scripts/audit_phase6_release_readiness.py` reports the remaining Phase 6
  readiness gaps before any release is cut.
- GitHub Actions tests pass on `main`.

## Distribution decision

The first private archive should remain GitHub-only until the Phase 6 archive
and citation checks are complete. A Zenodo software mirror can be created after
the public API stabilizes and after deciding whether RhoDyn should receive an
independent DOI separate from the manuscript software archive.

## Safety boundary

The release package must not contain raw microscopy files, manuscript-private
materials, local machine paths, credentials, mounted-volume paths, or generated
debug outputs. The manuscript repository and Zenodo data package remain cited
as optional case-study inputs only.

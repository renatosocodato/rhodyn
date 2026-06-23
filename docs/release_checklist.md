# Private v0.1.0 release checklist

RhoDyn `v0.1.0` is a private software hardening release. It is not a public
scientific claim surface and does not replace the manuscript reproducibility
repository.

## Required before a private archive

- README, LICENSE, NOTICE, CITATION, CHANGELOG, and REPRODUCING files are present.
- `pyproject.toml` reports version `0.1.0`.
- The source package imports without optional dependencies.
- Unit tests pass.
- Source distribution and wheel build successfully.
- Wheel and source distribution install in a clean environment.
- `scripts/check_release.py` reports no release-safety failures.
- GitHub Actions tests pass on `main`.

## Distribution decision

The first private archive should remain GitHub-only. A Zenodo software mirror
can be created later after the public API stabilizes and after deciding whether
RhoDyn should receive an independent DOI separate from the manuscript software
archive.

## Safety boundary

The release package must not contain raw microscopy files, manuscript-private
materials, local machine paths, credentials, mounted-volume paths, or generated
debug outputs. The manuscript repository and Zenodo data package remain cited as
optional case-study inputs only.

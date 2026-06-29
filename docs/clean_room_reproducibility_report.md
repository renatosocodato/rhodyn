# Clean-room reproducibility report

Generated UTC. 2026-06-29T14:10:04.146441Z

Overall status. pass

## Scope

This run copied the current RhoDyn source tree into a temporary clean-room workspace, built a source distribution and wheel, installed the wheel into a fresh runtime environment, and ran the software examples without using raw microscopy, manuscript-private data, or local mounted-volume inputs.

## Environment

- Python used to launch the run. 3.14.3
- Platform. macOS-26.5.1-arm64-arm-64bit-Mach-O
- Temporary workspace. Outside the repository and discarded after the run is no longer needed.

## Step results

| Step | Status | Seconds | Command |
|---|---:|---:|---|
| source tree copy | pass | 0.00 | `shutil.copytree current tree to temporary clean-room source` |
| create build virtual environment | pass | 1.25 | `python -m venv $CLEAN_ROOM/builder_venv` |
| upgrade build pip | pass | 0.84 | `$CLEAN_ROOM/builder_venv/bin/python -m pip install --upgrade pip` |
| install development extra | pass | 3.49 | `$CLEAN_ROOM/builder_venv/bin/python -m pip install -e .[dev]` |
| build source distribution and wheel | pass | 2.03 | `$CLEAN_ROOM/builder_venv/bin/python -m build --sdist --wheel --outdir $CLEAN_ROOM/dist` |
| create installed-wheel virtual environment | pass | 1.21 | `python -m venv $CLEAN_ROOM/wheel_venv` |
| upgrade wheel pip | pass | 0.85 | `$CLEAN_ROOM/wheel_venv/bin/python -m pip install --upgrade pip` |
| install built wheel | pass | 0.25 | `$CLEAN_ROOM/wheel_venv/bin/python -m pip install --force-reinstall --no-deps $CLEAN_ROOM/dist/rhodyn-0.1.0-py3-none-any.whl` |
| validate synthetic trajectory | pass | 0.35 | `$CLEAN_ROOM/wheel_venv/bin/rhodyn validate examples/synthetic_trajectory.csv` |
| score synthetic residence | pass | 0.07 | `$CLEAN_ROOM/wheel_venv/bin/rhodyn score-residence examples/synthetic_trajectory.csv --low 0.35 --high 0.75` |
| decide synthetic coupling | pass | 0.07 | `$CLEAN_ROOM/wheel_venv/bin/rhodyn decide-coupling examples/synthetic_coupling.csv` |
| summarize synthetic reserve | pass | 0.07 | `$CLEAN_ROOM/wheel_venv/bin/rhodyn summarize-reserve examples/synthetic_reserve.csv --floor 1.0 --ceiling 1.7 --baseline-points 1` |
| compare synthetic endpoints | pass | 0.07 | `$CLEAN_ROOM/wheel_venv/bin/rhodyn compare examples/synthetic_endpoints.csv` |
| simulate controller | pass | 0.06 | `$CLEAN_ROOM/wheel_venv/bin/rhodyn simulate --duration 5 --dt 1` |
| export markdown report | pass | 0.06 | `$CLEAN_ROOM/wheel_venv/bin/rhodyn export-markdown examples/synthetic_coupling.csv --title Clean-room bounded-coupling report` |
| convert CTC fixture | pass | 0.06 | `$CLEAN_ROOM/wheel_venv/bin/rhodyn ctc-to-trajectory examples/mlci_ctc_features.csv --lineage examples/mlci_man_track.txt --signal speed --condition mlci_fixture --replicate clean_room` |
| run synthetic workflow script | pass | 0.06 | `$CLEAN_ROOM/wheel_venv/bin/python examples/residence_reserve_workflow.py` |
| run public MLCI workflow script | pass | 0.07 | `$CLEAN_ROOM/wheel_venv/bin/python examples/mlci_public_case_study_workflow.py` |
| tutorial notebook code cells | pass | 0.06 | `$CLEAN_ROOM/wheel_venv/bin/python -c <execute tutorial notebook code cells>` |
| build documentation site | pass | 0.80 | `$CLEAN_ROOM/builder_venv/bin/mkdocs build --strict --site-dir $CLEAN_ROOM/site` |
| audit Stage 5 workbench | pass | 0.02 | `$CLEAN_ROOM/builder_venv/bin/python scripts/audit_stage5_premium_workbench.py` |
| clean generated build byproducts | pass | 0.00 | `remove build and src/rhodyn.egg-info before release-safety check` |
| release safety check | pass | 0.65 | `$CLEAN_ROOM/builder_venv/bin/python scripts/check_release.py` |

## Built distributions

- `rhodyn-0.1.0-py3-none-any.whl`. 55221 bytes. SHA-256 `291698c8c14df76d8189844d2dac3118ecba009f7c9b2188b95e8b81a4d8e8ac`.
- `rhodyn-0.1.0.tar.gz`. 421907 bytes. SHA-256 `4309e07afb74fca2e552b1d5508ccaff55b07318263a8b2f9a71f80e5f689f69`.

## Source archive content checks

- `.zenodo.json`. present.
- `CONTRIBUTING.md`. present.
- `docs/clean_room_reproducibility.md`. present.
- `docs/clean_room_reproducibility_report.md`. present.
- `docs/phase6_release_readiness_report.json`. absent.
- `docs/release_checksums.csv`. present.
- `docs/release_checksums.json`. present.
- `docs/release_notes_v0.1.0.md`. present.

## Interpretation

The clean-room run supports the software-release claim that RhoDyn can be built, installed, documented, and exercised from its shipped examples without hidden local state. This is a reproducibility result for the software surface only. It does not add biological evidence, does not reproduce manuscript-private analyses, and does not certify PyPI or Zenodo publication.

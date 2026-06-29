# PyPI dry-run report

Overall status. pass

This dry run built the source distribution and wheel, checked metadata with twine, installed the wheel in a fresh environment, and exercised the installed CLI without uploading to PyPI or TestPyPI.

## Checks

- metadata_name_is_rhodyn. pass
- metadata_version_is_0_1_0. pass
- core_dependencies_empty. pass
- sdist_built. pass
- wheel_built. pass
- twine_check_passed. pass
- installed_wheel_imported. pass
- installed_cli_help_passed. pass
- no_upload_attempted. pass

## Distribution artifacts

- rhodyn-0.1.0-py3-none-any.whl
- rhodyn-0.1.0.tar.gz

## Command summary

- pass. `$PYPI_DRY_RUN/build-env/bin/python -m pip install --upgrade pip`
- pass. `$PYPI_DRY_RUN/build-env/bin/python -m pip install build>=1.2 twine>=5.0`
- pass. `$PYPI_DRY_RUN/build-env/bin/python -m build --sdist --wheel --outdir $PYPI_DRY_RUN/dist .`
- pass. `$PYPI_DRY_RUN/build-env/bin/python -m twine check --strict $PYPI_DRY_RUN/dist/rhodyn-0.1.0-py3-none-any.whl $PYPI_DRY_RUN/dist/rhodyn-0.1.0.tar.gz`
- pass. `$PYPI_DRY_RUN/install-env/bin/python -m pip install --upgrade pip`
- pass. `$PYPI_DRY_RUN/install-env/bin/python -m pip install $PYPI_DRY_RUN/dist/rhodyn-0.1.0-py3-none-any.whl`
- pass. `$PYPI_DRY_RUN/install-env/bin/python -c import rhodyn; print(rhodyn.__version__)`
- pass. `$PYPI_DRY_RUN/install-env/bin/python -m rhodyn.cli --help`

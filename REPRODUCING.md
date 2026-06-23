# Reproducing the scaffold checks

RhoDyn `v0.1.0` is intentionally lightweight and uses only the Python standard
library.

```bash
python3 -m unittest discover tests
python3 -m compileall src tests
python3 -m pip install -e .
rhodyn validate examples/synthetic_trajectory.csv
rhodyn score-residence examples/synthetic_trajectory.csv --low 0.35 --high 0.75
rhodyn simulate --duration 5 --dt 1
rhodyn compare examples/synthetic_endpoints.csv
```

The manuscript reproduction repository remains separate:

- repository: `https://github.com/renatosocodato/windowed_rhoA_model`
- release commit: `e63cc93a4b23d8b3d27cf25136b00d53fa6144f4`
- software archive DOI: `10.5281/zenodo.19796404`
- data package DOI: `10.5281/zenodo.19796406`

Those resources are optional case-study inputs for future RhoDyn examples. They
are not required for the RhoDyn scaffold tests.


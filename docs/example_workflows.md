# Synthetic example workflows

The examples in this repository use synthetic data only. They are designed to
show the RhoDyn analysis pattern without requiring manuscript data, private
microscopy files, or a paper reproduction bundle.

## Residence-window scoring

The trajectory example contains tidy live-cell signaling rows with `cell_id`,
`time`, `condition`, `signal`, and `replicate` columns. Running

```bash
rhodyn score-residence examples/synthetic_trajectory.csv --low 0.35 --high 0.75
```

reports how long each synthetic cell remains inside the declared signaling
window. The biological lesson is narrow: residence and mean amplitude can carry
different information even when the input table is small.

## Reserve-style buffering

The reserve example contains a synthetic response trace per sample.

```bash
rhodyn validate examples/synthetic_reserve.csv --kind reserve
```

The notebook-style workflow normalizes each response to `F/F0` and maps the
peak response to a bounded reserve coordinate. This is a reserve-like summary,
not a direct injury or fate measurement.

## Bounded coupling

The coupling example contains interval summaries supplied by the user.

```bash
rhodyn validate examples/synthetic_coupling.csv --kind coupling
```

RhoDyn can classify whether the interval sits inside a declared margin and,
when supplied, whether posterior mass satisfies a ROPE threshold. The result is
a bounded-coupling decision under the stated margin, not proof that two
pathways never communicate.

## Reduced-model comparison

The endpoint example compares observed and predicted endpoint values from toy
controller alternatives.

```bash
rhodyn compare examples/synthetic_endpoints.csv
```

The model ranking summarizes endpoint compatibility. It does not turn fitted
or effective parameters into literal molecular edges.

## Run the full dependency-free walkthrough

```bash
PYTHONPATH=src python examples/residence_reserve_workflow.py
```

The script prints four sections: residence, reserve, bounded coupling, and
reduced-model comparison. Each section includes a short interpretation note so
users can distinguish measured synthetic inputs from model-derived summaries.

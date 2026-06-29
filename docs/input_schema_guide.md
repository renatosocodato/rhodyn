# Input schema guide

RhoDyn uses tidy CSV tables so a result can be reproduced from explicit rows,
parameter choices, and software version. Column names are intentionally small
and stable across the Python API, CLI, backend, and workbench.

## Trajectory table

Use trajectory rows for live-cell or time-series signals.

| column | required | meaning |
| --- | --- | --- |
| `cell_id` | yes | Cell, track, or trajectory identifier. |
| `time` | yes | Non-negative time coordinate. |
| `condition` | yes | Treatment, genotype, ligand, or context label. |
| `signal` | yes | Numeric signal to score for amplitude and residence. |
| `replicate` | no | Well, donor, batch, sequence, field, or biological replicate label. |

Example.

```csv
cell_id,time,condition,signal,replicate
a,0,control,0.20,well1
a,1,control,0.50,well1
```

## Endpoint table

Use endpoint rows when comparing reduced architectures or model alternatives.

| column | required | meaning |
| --- | --- | --- |
| `model` | yes | Name of the candidate architecture. |
| `endpoint` | yes | Endpoint or constraint being compared. |
| `observed` | yes | Observed endpoint value. |
| `predicted` | yes | Predicted endpoint value for that model. |
| `weight` | no | Non-negative weighting factor. Defaults to 1.0. |

Model comparison ranks each model by weighted residual compatibility. It does
not infer a literal molecular edge from the winning label.

## Reserve table

Use reserve rows when a sample has a response trace that can be normalized and
converted into a bounded reserve-like coordinate.

| column | required | meaning |
| --- | --- | --- |
| `sample_id` | yes | Sample, cell, well, or trace identifier. |
| `time` | yes | Non-negative time coordinate. |
| `condition` | yes | Treatment, genotype, ligand, or context label. |
| `response` | yes | Numeric response value. |
| `replicate` | no | Well, donor, batch, or acquisition label. |

The CLI groups reserve rows by condition and sample. If normalization is on,
the first `baseline_points` values define `F/F0`.

## Coupling table

Use coupling rows when an uncertainty interval is already available for a
contrast.

| column | required | meaning |
| --- | --- | --- |
| `contrast` | yes | Name of the comparison. |
| `estimate` | yes | Contrast estimate. |
| `ci_low` | yes | Lower uncertainty bound. |
| `ci_high` | yes | Upper uncertainty bound. |
| `margin` | yes | Positive biological-negligibility margin. |
| `rope_mass` | no | Posterior mass inside the margin, when available. |

A passing row means the interval lies inside the declared margin and, when
`rope_mass` is supplied, the posterior mass clears the configured threshold.

## Validation behavior

The readers return two objects, records and validation issues. Missing required
columns, empty identifiers, non-finite numbers, negative times, and non-positive
margin values are reported as issues. CLI validation exits with status 0 when
no issues are present and status 1 when issues are found.

## Replicate and grouping practice

RhoDyn keeps replicate labels visible but does not infer the biological
replicate structure for the user. When bootstrap, permutation, or higher-level
modeling is used, group labels should represent the exchangeability unit, such
as donor, well, field, plate, sequence, or batch.

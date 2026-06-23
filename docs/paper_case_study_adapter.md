# Paper-data adapter

RhoDyn includes a paper-data adapter so a future tutorial can demonstrate the
toolkit on public manuscript release tables supplied by the user.

The adapter records and reports:

- manuscript reproducibility repository;
- release commit;
- software archive DOI;
- data package DOI;
- expected input table roles.

It deliberately does not ship manuscript data and does not make the manuscript
repository a runtime dependency. The manuscript remains scientifically
independent from RhoDyn.

## Use

After the paper release is public and stable, point the adapter at a local copy
of the released data package.

```bash
rhodyn paper-case-study --data-root /path/to/zenodo_data
```

The adapter recursively scans CSV files whose names match generic biological
roles and validates them against RhoDyn schemas.

| role | schema |
| --- | --- |
| `trajectory_tables` | live-cell trajectory schema |
| `reserve_tables` | reserve-like response schema |
| `endpoint_tables` | observed-versus-predicted endpoint schema |
| `model_output_tables` | endpoint schema for summarized model outputs |
| `coupling_tables` | bounded-coupling interval schema |

Tables with validation issues are reported rather than interpreted. The adapter
does not read raw microscopy, Excel workbooks, or manuscript figure files.

## Boundary

The case study can demonstrate that RhoDyn expresses analysis patterns similar
to those used in the manuscript. It should not imply that RhoDyn generated the
manuscript figures, statistics, or biological conclusions.

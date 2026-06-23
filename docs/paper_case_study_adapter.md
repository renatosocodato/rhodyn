# Paper-data adapter stub

RhoDyn includes a paper-data adapter stub so a future tutorial can demonstrate
the toolkit on the public manuscript release.

The adapter records:

- manuscript reproducibility repository;
- release commit;
- software archive DOI;
- data package DOI;
- expected input table roles.

It deliberately does not ship manuscript data and does not make the manuscript
repository a runtime dependency. The manuscript remains scientifically
independent from RhoDyn.

## Intended future use

After the paper release is public and stable, the adapter can support a command
such as:

```bash
rhodyn paper-case-study --data-root /path/to/zenodo_data
```

The adapter should then map released tables into generic RhoDyn schemas.

## Boundary

The case study can demonstrate that RhoDyn expresses analysis patterns similar
to those used in the manuscript. It should not imply that RhoDyn generated the
manuscript figures, statistics, or biological conclusions.


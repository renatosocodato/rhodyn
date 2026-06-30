# Stage 7.4 endpoint, reserve-like, and routed-output demonstrations

Stage 7.4 extends the methods-program evidence lane beyond single-reporter trajectory summaries. It uses retained public-derived tables from two selected public resources.

- Seal et al. 2023 Cell Painting plus MitoTox endpoints, Zenodo DOI `10.5281/zenodo.10011861`, for perturbation endpoint model comparison, routed-output alternatives, and a scoped cell-health endpoint preservation coordinate.
- Wan et al. 2021 ERK/Akt paired KTR trajectories, Zenodo DOI `10.5281/zenodo.5836623`, for declared-margin bounded coupling of paired reporter residence summaries.

## Regenerate

```bash
python scripts/run_stage7_4_endpoint_reserve_routing.py
```

The runner reads retained public-derived tables. It does not retain public source CSV or ZIP payloads and does not use manuscript-private data.

## Outputs

- `case_studies/stage7_endpoint_reserve_routing/candidate_ranking.tsv`
- `case_studies/stage7_endpoint_reserve_routing/cell_painting_tidy_endpoint_model_rows.csv`
- `case_studies/stage7_endpoint_reserve_routing/cell_painting_routed_model_comparison.csv`
- `case_studies/stage7_endpoint_reserve_routing/cell_painting_reduced_alternative_decisions.tsv`
- `case_studies/stage7_endpoint_reserve_routing/cell_painting_reserve_like_endpoint_rows.csv`
- `case_studies/stage7_endpoint_reserve_routing/cell_painting_reserve_like_model_summary.csv`
- `case_studies/stage7_endpoint_reserve_routing/cell_painting_reserve_like_uncertainty.csv`
- `case_studies/stage7_endpoint_reserve_routing/erk_akt_bounded_coupling_decisions.csv`
- `case_studies/stage7_endpoint_reserve_routing/stage7_4_case_summary.tsv`
- `case_studies/stage7_endpoint_reserve_routing/stage7_4_endpoint_reserve_routing_gate_report.json`
- `case_studies/stage7_endpoint_reserve_routing/stage7_4_provenance.json`

## Routed-output demonstration

The Cell Painting/MitoTox endpoint case compares endpoint prevalence, one-dimensional morphology magnitude, single-compartment morphology, and a routed Cells/Cytoplasm/Nuclei compartment architecture. The retained routed model is `compartment_route_5nn`. It ranks first by BIC, with delta BIC 248.56 against endpoint prevalence and 331.52 against one-dimensional morphology magnitude.

The biological interpretation is bounded. The public endpoint table contains perturbation structure retained by a routed compartment summary. This is not drug-mechanism inference and not a live dynamic-state measurement.

## Reserve-like endpoint demonstration

The reserve-like coordinate is scoped to MitoTox cell-health endpoint preservation. It uses only `apoptosis up`, `cytotoxicity BLA`, `cytotoxicity SRB`, `mitochondrial disruption up`, and `proliferation decrease`. For each compound, the coordinate is one minus the mean burden-label activity, so larger values mean greater endpoint-level preservation.

This label is deliberately narrow. It is a reserve-like endpoint summary, not live metabolic reserve, calcium reserve, or viability kinetics.

## Bounded-coupling demonstration

The ERK/Akt case tests paired ERK-minus-Akt high-state residence under a declared +/-0.20 residence-fraction margin. The UK context passes as a primary context-limited bounded-coupling case. Histamine and S1P remain outside the promoted bounded-coupling claim under the same rule.

This means RhoDyn can preserve both passing and non-passing contexts in the same public paired-reporter dataset. Passing does not mean biochemical equivalence, and failing does not mean uncoupling is absent in every timescale or ligand context.

## Gate

The Stage 7.4 gate passes because at least one public case supports bounded coupling and one public endpoint case distinguishes a routed model from reduced alternatives. The stop condition is not triggered because the non-trajectory endpoint table does distinguish declared reduced alternatives.

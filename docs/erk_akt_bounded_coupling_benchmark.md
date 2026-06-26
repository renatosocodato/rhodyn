# ERK/Akt public bounded-coupling benchmark

This Stage 3D benchmark uses the public Wan 2021 ERK/GPCR source-data archive
to test whether paired ERK and Akt residence summaries remain bounded in the
same cells under a declared residence-margin rule.

The benchmark is deliberately narrow. It is a public case study for bounded
coupling of derived residence summaries, not a claim that ERK and Akt are
biochemically equivalent and not evidence for absence of all GPCR pathway
crosstalk.

## Source

Source record: https://zenodo.org/records/5836623

DOI: https://doi.org/10.5281/zenodo.5836623

License: CC-BY-4.0

Source archive: `Figure_3.zip`

Source member tables:

- `Figure_3/Data/ALL_UK.csv`
- `Figure_3/Data/ALL_S1P.csv`
- `Figure_3/Data/ALL_His.csv`

RhoDyn downloads the source archive in memory and writes only derived benchmark
tables. The source ZIP and member CSV files are not retained in the repository.

## Regeneration

```bash
python scripts/fetch_erk_akt_bounded_coupling.py
```

The default settings retain up to 60 DMSO-control cells per ligand context and
define separate ERK and Akt high-state residence thresholds from the retained
record 75th percentiles. These thresholds are analytical operating points for a
public benchmark. They are not universal ERK or Akt activation thresholds.

## Derived outputs

- `case_studies/erk_gpcr_erk_akt_residence_summary.csv`
- `case_studies/erk_gpcr_erk_akt_bounded_coupling.csv`
- `case_studies/erk_gpcr_erk_akt_bounded_coupling.provenance.json`
- `case_studies/erk_gpcr_erk_akt_margin_sensitivity.csv`
- `case_studies/erk_gpcr_erk_akt_threshold_sensitivity.csv`
- `case_studies/erk_gpcr_erk_akt_hardening_report.json`

The residence table contains 180 paired single-cell summaries, with 60 cells
from each ligand context. Each row reports ERK residence, Akt residence, and the
paired ERK-minus-Akt residence contrast.

The coupling table applies one-sample TOST to the paired ERK-minus-Akt
residence contrast under a declared +/-0.20 residence-fraction margin.

The sensitivity tables test two possible fragilities. The margin-sensitivity
table re-runs the decision across margins from 0.05 to 0.30 residence-fraction
units. The threshold-sensitivity table re-runs the decision across high-state
quantile thresholds from 0.60 to 0.85. The hardening report summarizes the
minimum passing margin, threshold-grid behavior, and the replicate structure of
the selected public slice.

## Biological readout

The UK context falls inside the declared margin, so it provides the public
bounded-coupling example needed for the Stage 3 evidence bank. The S1P and
histamine contexts do not pass the same bounded-coupling decision rule. The
mixed all-ligand contrast also falls inside the margin, but it combines
ligand-specific directional effects and should be treated as a summary check
rather than as the biological conclusion.

This means the Stage 3D result is context-limited. RhoDyn can show a bounded
ERK/Akt residence contrast in one public GPCR context, while also preserving
ligand contexts where the same bounded-coupling interpretation is not
supported. That is scientifically useful because it demonstrates both a passing
bounded-coupling case and the software's ability to avoid upgrading every
paired trajectory comparison into an equivalence claim.

## Hardening result

The primary UK conclusion is not driven by a single high-state threshold. UK
passes across the threshold grid from the 60th through 85th retained-record
percentiles. It also passes at margins of 0.10 residence-fraction units and
larger, so the primary +/-0.20 margin is not the smallest setting that can make
UK pass.

S1P and histamine do not pass the primary +/-0.20 margin at any threshold in
the tested grid. They only pass when the margin is widened beyond the primary
decision rule, which keeps them outside the Stage 3D bounded-coupling claim.

The selected public DMSO-control slice contains one experiment label per ligand
context. That means within-ligand leave-one-replicate sensitivity is not
available for this case study. Rather than hiding that limitation, the retained
hardening report records it and keeps the biological conclusion scoped to a
public benchmark, not a definitive GPCR-ligand generalization.

## Stage 3 role

Together with the DRG calcium residence/amplitude benchmark, the ERK/GPCR
residence/amplitude benchmark, and the Cell Painting/MitoTox model-comparison
benchmark, this public bounded-coupling case closes the v0.3 Stage 3 evidence
bank. It does not imply that RhoDyn generated the RhoA/microglia manuscript
results. The manuscript remains a reference use case, not the source of
software generality.

## Higher-order expansion routes after Stage 3D

The next scientific expansion should not change the Stage 3D closure decision.
It should add breadth after the backend contract exists. The strongest later
routes are a public NF-kB or ERK perturbation dataset for another bounded
coupling example, a calcium or viability dataset that supports a true reserve
coordinate, and a larger multi-reporter live-cell dataset where residence,
amplitude, and routed outputs can be compared under shared perturbations. These
are Stage 7 evidence-expansion routes, not prerequisites for starting Stage 4.

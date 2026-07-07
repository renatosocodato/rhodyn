# Stage 10.3 public biological breadth

Stage 10.3 addresses the second Nature Methods desk-rejection vulnerability in the Stage 10 roadmap. Stage 10.2 made named comparator behavior visible. Stage 10.3 asks whether the method story has enough public biological breadth to read as a general residence-state inference method rather than a polished workflow around one biological paper.

## Command

```bash
python3 scripts/run_stage10_3_public_biological_breadth.py
```

The runner writes outputs to `case_studies/stage10_public_breadth/`.

## Counted systems

The gate counts independent public systems only when the source is public, the derived output is retained or already retained in the repository, and the source can be reused without obvious release-surface risk.

| system | public source | biological domain | Stage 10.3 role |
| --- | --- | --- | --- |
| DRG calcium | Zenodo DOI `10.5281/zenodo.14907827` | excitable-neuron calcium dynamics | retained public trajectory case where residence and peak calcium can diverge |
| Wan ERK/KTR GPCR | Zenodo DOI `10.5281/zenodo.5836623` | GPCR-linked kinase dynamics | retained public trajectory case with residence-only and amplitude-only top-quartile cells |
| Cell Painting/MitoTox | Zenodo DOI `10.5281/zenodo.10011861` | perturbation endpoint morphology and cell-health profiling | retained routed-output and endpoint-preservation case |
| MLCI tracking | Zenodo DOI `10.5281/zenodo.7260137` | microbial live-cell tracking | new Stage 10 public breadth case using tracking-derived intensity trajectories |

The Wan ERK/AKT bounded-coupling rows remain important method evidence, but they are not counted as an additional independent public system because they come from the same source family as the ERK GPCR case. This keeps the breadth count conservative.

## Candidate withholding

The Birtwistle ERK/AKT cell-division GitHub repository is source-verified in this phase. Its MATLAB files are readable and biologically useful, but no explicit repository license was detected through the GitHub API. Stage 10.3 therefore records the source as a strong future candidate and does not retain derivative trajectory tables or count it as a release-ready public system.

NF-kB and ESC ERK/AKT/STAT3 candidates remain deferred until a stable, license-clear, schema-readable trajectory source is identified.

## Outputs

| output | purpose |
| --- | --- |
| `stage10_3_public_system_matrix.tsv` | Counted systems, biological domains, primary result, and claim boundary. |
| `stage10_3_mlci_tracking_residence_summary.csv` | Stage 10 MLCI tracking-derived residence and amplitude summary. |
| `stage10_3_candidate_resolution.tsv` | Counted, deferred, and source-verified-but-withheld candidate decisions. |
| `stage10_3_source_access_ledger.tsv` | Public source URLs, licenses, access status, and counted status. |
| `stage10_3_birtwistle_source_probe.json` | Public source probe for the deferred ERK/AKT cell-division candidate. |
| `stage10_3_public_breadth_brief.md` | Human-readable biological breadth summary. |
| `stage10_3_public_breadth_report.json` | Gate report. |

## Current result

The current gate report passes. It counts four independent public systems across four biological domains. Two systems are beyond the earlier DRG calcium and ERK GPCR trajectory examples: Cell Painting/MitoTox and MLCI tracking. The retained evidence includes residence/amplitude divergence, amplitude-sufficient or negative cases, endpoint/routed-output structure, and declared-margin bounded-coupling evidence.

The biological interpretation remains bounded. Stage 10.3 does not show that every live-cell system has a residence regime, and it does not treat tracking intensity or endpoint preservation as molecular signaling. It shows that RhoDyn can represent multiple public biological input classes while keeping unsupported sources and overextended interpretations out of the counted evidence set.

## Gate interpretation

Stage 10.3 materially reduces the public-breadth vulnerability, but it does not close the full Stage 10 rescue program. The next required step is Stage 10.4, a stricter held-out or blinded validation route with predeclared windows, margins, grouping, and uncertainty rules.

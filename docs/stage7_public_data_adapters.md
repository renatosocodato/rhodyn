# Stage 7.3 public-data adapters

Stage 7.3 selects public live-cell signaling datasets only when source access, metadata, grouping, and preprocessing are explicit enough to support residence-state interpretation. The adapters download public source files in memory and write derived trajectory and summary tables under `case_studies/stage7_public_signaling/`. Raw public source archives are not retained in the repository.

## Selection outcome

The selected public signaling systems are:

| dataset | source | signal | grouping retained | reason selected |
| --- | --- | --- | --- | --- |
| `drg_calcium_vonbuchholtz2025` | von Buchholtz 2025, Zenodo DOI `10.5281/zenodo.14907827` | DRG neuron calcium `deltaF/F0` | mouse, ganglion, ROI, episode condition | Excitable-neuron calcium traces provide a public live-cell system where peak calcium and high-calcium residence can diverge. |
| `erk_gpcr_wan2021` | Wan et al. 2021, Zenodo DOI `10.5281/zenodo.5836623` | ERK KTR cytoplasm-to-nucleus ratio | experiment, ligand, inhibitor, slide, position, source object | GPCR-driven kinase trajectories provide a second public signaling system where peak ERK and high-ERK residence can diverge. |

The candidate ranking table is `case_studies/stage7_public_signaling/candidate_ranking.tsv`. The NF-kB watchlist remains deferred because source URL, license, schema, and grouping are not verified enough for this phase.

## Adapter commands

```bash
python scripts/run_stage7_3_public_signaling.py
```

The runner creates tidy trajectory tables, residence-versus-amplitude summaries, window-sensitivity tables, grouped bootstrap summaries, provenance records, and case reports for the selected datasets.

## Interpretation boundary

These adapters demonstrate RhoDyn on independent public live-cell signaling systems. They do not imply that RhoDyn generated the RhoA/microglia manuscript results, and the declared high-state windows should be read as analytical thresholds rather than calibrated universal activation boundaries.

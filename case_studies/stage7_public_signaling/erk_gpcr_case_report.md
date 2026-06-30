# Stage 7.3 ERK GPCR public signaling demonstration

## Source and access

Dataset. `erk_gpcr_wan2021`.

Source citation. Wan et al. 2021, Zenodo DOI 10.5281/zenodo.5836623.

Access route. https://zenodo.org/records/5836623.

## Metadata, grouping, and preprocessing

Metadata. The retained rows preserve ligand, inhibitor, concentration, experiment, slide, position, source-object, time, and ERK KTR signal fields.

Grouping. Experiment is retained as the primary grouping field for bootstrap uncertainty, while ligand and imaging metadata remain available for interpretation.

Preprocessing. The adapter downloads the Figure 3 archive in memory, selects DMSO-control His, S1P, and UK ligand traces, and converts CN_ERK records into tidy trajectories.

The Stage 7.3 tidy trajectory table contains 4320 time-resolved rows and the residence-amplitude summary contains 180 cell-level or episode-level rows.

## Residence versus amplitude result

The selected table contains 34 rows in the joint top quartile, 11 amplitude-only top-quartile rows, 11 residence-only top-quartile rows, and 124 rows in neither top quartile. The amplitude-only plus residence-only mismatch count is 22.

What RhoDyn adds. Peak ERK KTR and high-ERK residence separate in single-cell trajectories. RhoDyn reports cells whose peak activity is high without sustained residence and cells whose residence is high without being peak-ranked.

Interpretation boundary. The high-ERK threshold is an analytical selected-record quantile, not a calibrated universal ERK activation boundary. The case does not infer GPCR mechanism or ligand-specific causality.

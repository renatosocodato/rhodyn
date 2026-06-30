# Stage 7.3 DRG calcium public signaling demonstration

## Source and access

Dataset. `drg_calcium_vonbuchholtz2025`.

Source citation. von Buchholtz 2025, Zenodo DOI 10.5281/zenodo.14907827.

Access route. https://zenodo.org/records/14907827.

## Metadata, grouping, and preprocessing

Metadata. The retained rows preserve cell, mouse, ganglion, ROI, episode condition, time, and calcium signal fields.

Grouping. Mouse and ganglion fields are retained for biological grouping; bootstrap uncertainty uses mouse as the grouping unit.

Preprocessing. The adapter downloads trace and metadata CSV files in memory, keeps a bounded 120-cell subset, and converts each 200-frame episode into a tidy trajectory.

The Stage 7.3 tidy trajectory table contains 72000 time-resolved rows and the residence-amplitude summary contains 360 cell-level or episode-level rows.

## Residence versus amplitude result

The selected table contains 74 rows in the joint top quartile, 16 amplitude-only top-quartile rows, 16 residence-only top-quartile rows, and 254 rows in neither top quartile. The amplitude-only plus residence-only mismatch count is 32.

What RhoDyn adds. Peak calcium and time spent in the declared high-calcium window are not interchangeable. The residence-only and amplitude-only rows show that endpoint amplitude can miss sustained high-state occupancy and that sustained occupancy can occur without being the peak-ranked response.

Interpretation boundary. The high-calcium window is a declared analytical threshold. The case does not assign stimulus identity, infer pain mechanism, or claim a calibrated biological calcium activation boundary.

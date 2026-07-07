# Stage 10.4 held-out validation predeclaration

Stage 10.4 evaluates RhoDyn as a no-retuning decision method. The challenge is sealed as a replay over public-derived tables already retained in the repository. It is stricter than a figure caption because the train splits, held-out contexts, thresholds, margins, and outcome classes are written before the Stage 10.4 output tables are interpreted.

## Trajectory rule

Training rows define the 75th-percentile amplitude and residence thresholds. Held-out rows are then classified as amplitude-high, residence-high, both, or neither. A held-out case is called positive when the high-set Jaccard overlap is at most 0.5 and at least 2 held-out objects are discordant. A case is called negative when the high-set Jaccard overlap is at least 0.75. Other cases remain inconclusive.

## Fixed challenges

- MLCI tracking. Train on replicate 00 and hold out replicate 01.
- ERK GPCR trajectories. Train on lexically sorted even-index ligands and hold out the remaining ligand.
- ERK/Akt paired reporter coupling. Reuse the Stage 7.5 non-DMSO held-out plan with fixed DMSO-derived thresholds and the fixed +/-0.20 ERK-minus-Akt residence margin.

## Boundary

This stage is not a prospective blind collaborator study. It is a sealed replay that tests whether already-retained public examples preserve positive, negative, and inconclusive decisions under fixed rules. It does not show universal RhoDyn superiority and does not identify molecular mechanisms.

# Stage 10.4 held-out validation

Stage 10.4 addresses the third validation vulnerability in the Nature Methods rescue roadmap. Stages 10.2 and 10.3 make named baselines and public biological breadth visible. Stage 10.4 asks whether RhoDyn can preserve positive, negative, and inconclusive decisions under fixed rules rather than post hoc tuning.

## Command

```bash
python3 scripts/run_stage10_4_heldout_validation.py
```

The runner writes outputs to `case_studies/stage10_heldout_validation/`.

## Challenge design

This phase is a sealed replay over public-derived tables already retained in the repository. It is not a prospective blind collaborator study. The scientific value is that train splits, held-out contexts, thresholds, margins, and outcome classes are fixed before the Stage 10.4 tables are interpreted.

| challenge | training rule | held-out rule | expected decision class |
| --- | --- | --- | --- |
| MLCI tracking | replicate 00 defines amplitude and residence thresholds | replicate 01 is held out | positive residence/amplitude divergence |
| ERK GPCR trajectories | lexically sorted even-index ligands define thresholds | remaining ligand is held out | negative or comparator-sufficient boundary |
| ERK/Akt paired reporter coupling | Stage 7.4 DMSO-control thresholds and +/-0.20 margin remain fixed | Stage 7.5 non-DMSO inhibitor contexts | positive bounded-coupling and inconclusive margin-boundary contexts |

## Outputs

| output | purpose |
| --- | --- |
| `stage10_4_predeclaration.json` | Machine-readable train/held-out split, threshold, margin, and decision rules. |
| `stage10_4_predeclaration.md` | Reader-facing predeclaration. |
| `stage10_4_heldout_decisions.tsv` | Held-out decision table with positive, negative, and inconclusive calls. |
| `stage10_4_trajectory_object_calls.csv` | Object-level held-out amplitude/residence calls for trajectory challenges. |
| `stage10_4_heldout_report.md` | Reader-facing held-out validation report. |
| `stage10_4_gate_report.json` | Gate report. |

## Current result

The current gate report passes. It records two positive held-out calls, one negative or comparator-sufficient call, and one inconclusive held-out call. This is important for the method claim because RhoDyn is not being shown as a success-only classifier. The same decision framework can identify a residence-divergence case, preserve a bounded-coupling pass, call a comparator-sufficient boundary, and withhold a margin-boundary result.

## Biological boundary

Stage 10.4 strengthens no-retuning evidence, but it remains scoped. It does not prove that every public biological system contains a residence regime, does not prove RhoDyn always outperforms simpler summaries, and does not replace a prospective blinded collaborator validation. The result supports the narrower claim that RhoDyn can carry fixed decision rules across held-out public contexts while preserving pass, boundary, and inconclusive outcomes.

## Next step

Stage 10.5 should translate Stages 10.1 through 10.4 into a method-first Nature Methods figure architecture. The first figures should now foreground the formal decision object, named baselines, public biological breadth, and held-out validation before the software workbench.

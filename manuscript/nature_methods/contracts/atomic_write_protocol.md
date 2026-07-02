# Stage 9 atomic write protocol

Stage 9 uses staged writes so manuscript-facing files are never partially written.

1. Load `docs/stage9_execution_memory.json` and the relevant keyed ledgers.
2. Write substage outputs only to `manuscript/nature_methods/_staging/<substage>/`.
3. Run the machine gate for the substage.
4. If the gate passes, promote staged files to canonical paths and record the promotion.
5. If the gate fails, move staging to `manuscript/nature_methods/_quarantine/<substage>/<timestamp>/` and stop.
6. Re-running a substage replaces only that substage's staging directory and must converge to the same canonical state given the same frozen evidence.

The current scaffold does not run Stage 9.0 evidence intake, does not create manuscript prose, and does not assemble a submission package.

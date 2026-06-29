# Clean-room reproducibility protocol

This protocol defines the Phase 6.6 clean-room target for the RhoDyn v0.1.0
release candidate. It verifies that the software can be built, installed, and
used from a fresh environment without relying on the developer's active Python
site packages, local build products, raw manuscript data, or mounted volumes.

## Scope

The clean-room run validates the standalone RhoDyn software surface. It uses the
small synthetic examples, public derived case-study tables, tutorial notebooks,
frozen API fixtures, documentation, and Stage 5 static workbench that are meant
to ship with the software archive. It does not use raw microscopy files,
manuscript-private workbooks, manuscript figure assets, or the paper repository.

## Expected environment

- A fresh copy of the current repository tree.
- A fresh build virtual environment for `rhodyn[dev]`.
- A fresh installed-wheel virtual environment for the runtime CLI checks.
- Temporary build, docs, and report outputs outside the repository.

The protocol may be run from the repository root with this command.

```bash
python scripts/run_clean_room_reproducibility.py --out docs/clean_room_reproducibility_report.md
```

## Required checks

The clean-room report must show that each step passed.

1. Copy the current source tree into a temporary clean-room directory while
   excluding `.git`, build directories, virtual environments, browser reports,
   and generated debug outputs.
2. Create a fresh build virtual environment and install `rhodyn[dev]` from the
   copied tree.
3. Build both the source distribution and wheel into a temporary `dist` folder.
4. Create a second fresh virtual environment and install the built wheel without
   reusing the editable source tree.
5. Run the installed `rhodyn` CLI on the bundled synthetic trajectory, coupling,
   reserve, endpoint, simulation, and Markdown report-export examples.
6. Run the synthetic workflow script from the installed wheel environment.
7. Execute the code cells in the tutorial notebooks with the installed wheel.
8. Build the documentation site with `mkdocs build --strict`.
9. Run the Stage 5 workbench static audit to confirm the frontend surface remains
   wired to the frozen API contract.
10. Confirm that the run uses only software-package examples and public derived
    tables, not manuscript-private or raw microscopy inputs.

## Passing interpretation

A passing report means that a user can start from the source archive, build the
package, install the wheel, run the core examples, inspect tutorial code, build
the documentation, and verify the static workbench without hidden local state.
It does not certify a public PyPI upload, Zenodo deposition, dependency review,
or broken-link scan. Those checks remain Phase 6.7.

## Biological interpretation boundary

RhoDyn outputs residence, coupling, reserve, uncertainty, simulation, and model
comparison summaries from user-supplied tables. A clean-room pass demonstrates
software reproducibility only. It does not add new biological evidence, does not
reproduce manuscript-private analyses, and does not convert example outputs into
general biological claims.

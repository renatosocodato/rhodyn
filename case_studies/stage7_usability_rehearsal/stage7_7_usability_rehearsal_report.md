# Stage 7.7 user-path findings

The rehearsal found that the public tutorial and workbench route can support an interpretable residence-versus-amplitude example, and that the bounded-coupling fixture is reproducible through Python, CLI, backend, and bundle exports.
Biologist residence task and Quantitative bounded-coupling task outcomes are recorded separately so the Python, CLI, and backend reproduction path remains visible.
This is not a new biological demonstration.

## Findings

| Persona | Task | Status | Finding | Fix applied |
|---|---|---|---|---|
| biologist | biologist_public_mlci_residence_amplitude | pass | Using the declared intensity window, public MLCI trajectories include residence-rich tracks that are not top-quartile by mean intensity and top-amplitude tracks that do not dwell in the window. The result is interpretable as a residence-versus-amplitude software example, not as molecular activity or disease-state biology. | none_required |
| quantitative_user | quantitative_cli_python_backend_reproduction | pass | The bounded-coupling fixture reproduces the same pass decision for rock_src and the same non-pass decision for myh10_src across Python, CLI, and backend outputs. | bundle provenance extended with input schema and grouping metadata |
| biologist_and_quantitative_user | stage5_workbench_public_flow_static_check | pass | Workbench exposes public MLCI workflow, schema inspection, parameter payload, route preview, and JSON/CSV/Markdown/bundle exports. | none_required |

## Export inspection

The exported analysis bundles include declared parameters, input schema, grouping summary, software version, submitted rows, exact result JSON, result rows, Markdown report, and payload checksums.

## Scope

Stage 7.7 tests whether declared users can run, inspect, export, and interpret existing RhoDyn results. It does not add a new biological system, does not add a new analysis route, and does not add a manuscript claim.

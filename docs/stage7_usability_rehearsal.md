# Stage 7.7 usability rehearsal protocol

Stage 7.7 tests whether a biologist and a quantitative user can reach RhoDyn decisions without reading source code.
The public MLCI path and bounded-coupling fixture are used as usability evidence, not as a new biological demonstration.

## Tasks

| Persona | Task | Input | Expected decision |
|---|---|---|---|
| biologist | biologist_public_mlci_residence_amplitude | `examples/mlci_public_intensity_trajectory.csv` | identify that residence-window occupancy and mean intensity are separable in the public intensity workflow |
| quantitative_user | quantitative_cli_python_backend_reproduction | `examples/synthetic_coupling.csv` | reproduce bounded-coupling pass for rock_src and non-pass for myh10_src |

## Gate status

Overall status. pass

## Validation checkpoints

- stage7_6_prerequisite_complete. pass.
- biologist_task_reaches_interpretable_decision. pass.
- quantitative_user_reproduces_cli_python_backend_output. pass.
- workbench_public_tutorial_flow_present. pass.
- exports_include_parameters_schema_grouping_version. pass.
- tutorial_or_interface_fixes_preserve_analysis_contract. pass.
- no_unvalidated_analysis_routes_added. pass.
- stop_condition_user_cannot_interpret_result. not_triggered.

## Interpretation boundary

Stage 7.7 tests whether declared users can run, inspect, export, and interpret existing RhoDyn results. It does not add a new biological system, does not add a new analysis route, and does not add a manuscript claim.

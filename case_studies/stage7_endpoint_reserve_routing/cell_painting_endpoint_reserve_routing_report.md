# Stage 7.4 Cell Painting/MitoTox endpoint and reserve-like demonstration

This case uses public Seal et al. 2023 Cell Painting morphology profiles paired with nine MitoTox endpoint labels. RhoDyn treats the data as perturbation endpoints rather than live-cell trajectories.

## Routed-output model comparison

The retained routed architecture is `compartment_route_5nn`. It keeps Cells, Cytoplasm, and Nuclei compartment magnitudes as separate route coordinates before endpoint prediction. The routed model ranks 1 by BIC. Against endpoint prevalence, delta BIC is 248.56. Against one-dimensional morphology magnitude, delta BIC is 331.517.

The biological readout is narrow. Public perturbation endpoint labels contain structure that is better retained by a routed compartment summary than by endpoint prevalence or one-dimensional morphology magnitude. This does not identify drug mechanism and does not treat Cell Painting morphology as a live controller measurement.

## Reserve-like endpoint coordinate

The reserve-like summary uses only cell-health burden labels: apoptosis up, cytotoxicity BLA, cytotoxicity SRB, mitochondrial disruption up, proliferation decrease. For each compound, the coordinate is one minus the mean burden-label activity, so larger values mean greater endpoint-level preservation. The mean coordinate is 0.853191 with a 95% bootstrap interval from 0.835258 to 0.870213 across 658 compounds.

This is a biologically scoped reserve-like endpoint demonstration. It reports cell-health endpoint preservation in a public perturbation table, not live metabolic reserve, calcium reserve, or viability kinetics.

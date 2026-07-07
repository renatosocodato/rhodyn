"""Run Stage 9.24 editorial polish pass I.

Stage 9.24 improves reader-facing cadence, claim strength, and section flow
without changing evidence bindings, paragraph IDs, statistics, figures, or
biological-method claims. It is intentionally a bounded editorial pass rather
than a new analysis step.
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT / "manuscript" / "nature_methods"
SECTIONS_DIR = WORKSPACE / "sections"
AUDITS_DIR = WORKSPACE / "audits"
GATE_DIR = WORKSPACE / "gate_verdicts"
FIGURES_DIR = WORKSPACE / "figures"
STAGING_DIR = WORKSPACE / "_staging" / "9.24"
QUARANTINE_DIR = WORKSPACE / "_quarantine" / "9.24"
MEMORY_PATH = ROOT / "docs" / "stage9_execution_memory.json"
ROADMAP_MEMORY_PATH = ROOT / "docs" / "roadmap_execution_memory.json"
REGISTRY_PATH = WORKSPACE / "contracts" / "stage9_substage_registry.json"
PLAN_PATH = ROOT / "docs" / "stage9_manuscript_assembly_plan.md"
ROADMAP_PATH = ROOT / "docs" / "roadmap.md"
README_PATH = WORKSPACE / "README.md"

GATE_923 = GATE_DIR / "9.23.json"

SURFACE_PATHS = [
    SECTIONS_DIR / "introduction.md",
    SECTIONS_DIR / "results.md",
    SECTIONS_DIR / "discussion.md",
    SECTIONS_DIR / "methods.md",
    FIGURES_DIR / "figure_legends.md",
]

OUTPUTS = {
    "audit": AUDITS_DIR / "editorial_pass_1.md",
    "gate": GATE_DIR / "9.24.json",
}

FORBIDDEN_DOWNSTREAM_PATHS = [
    AUDITS_DIR / "editorial_pass_2.md",
    AUDITS_DIR / "reader_surface_hygiene_report.md",
    WORKSPACE / "submission_package" / "pi_review_packet.md",
    WORKSPACE / "submission_package" / "submission_readiness_checklist.md",
    WORKSPACE / "stage9_completion_report.md",
]

UNSAFE_PHRASES = [
    "universal residence law",
    "automatic mechanism-discovery",
    "guarantees",
    "proves",
    "absence of all coupling",
    "proof of no crosstalk",
    "no crosstalk",
    "true biological reserve",
    "direct live metabolic reserve assay",
    "literal molecular edge",
    "RhoDyn generated the original",
    "PyPI publication is claimed",
]

REQUIRED_LIMIT_TERMS = [
    "declared biological window",
    "not a causal mechanism",
    "amplitude and endpoint summaries remain useful",
    "inconclusive",
    "slower or context-specific coupling",
    "reserve-like",
    "measured endpoint",
    "direct biochemical interactions",
    "not a new biological result",
    "retained evidence set",
]

REPLACEMENTS = {
    SECTIONS_DIR / "introduction.md": [
        (
            "Live-cell perturbation experiments increasingly measure the temporal structure of signaling, morphology, and fate-associated reporters, yet many analysis workflows still reduce those records to endpoints, peaks, thresholds, or generic trajectory features. Benchmarking and dynamical single-cell methods have made it clear that computational summaries can change biological interpretation when they preserve transition structure rather than only static position (REF-0001; REF-0002; REF-0003; REF-0004). The unresolved problem for perturbation biology is more specific. A cell can show a high peak, a similar endpoint, or the same apparent state assignment while spending different amounts of time in the operating range that matters for the experiment. A method that treats that time-in-state behavior as an explicit object is therefore needed to ask when residence carries information that amplitude summaries miss.",
            "Live-cell perturbation experiments increasingly record the temporal structure of signaling, morphology, and fate-associated reporters, but those records are still often collapsed to endpoints, peaks, thresholds, or generic trajectory features. Benchmarking and dynamical single-cell methods show that biological interpretation can change when a summary preserves transition structure rather than only static position (REF-0001; REF-0002; REF-0003; REF-0004). The practical problem for perturbation biology is that two cells can share a high peak, a similar endpoint, or the same apparent state assignment while spending different amounts of time in the operating range that matters for the experiment. A method that treats time in state as an explicit object is therefore needed to test when residence carries information that amplitude summaries miss.",
        ),
        (
            "The resulting manuscript is therefore a methods Article rather than a new primary disease-biology claim. Its public demonstrations include paired ERK/Akt reporter trajectories for bounded coupling and Cell Painting/MitoTox endpoint tables for reserve-like and routed-output analyses (REF-0011; REF-0012). Across those examples, the central question is not whether every biological system contains a residence regime. It is whether a reviewable method can preserve dynamic operating-state information, reveal cases where amplitude or endpoint summaries are sufficient, and withhold interpretation when the data do not resolve the boundary. RhoDyn is designed to make those decisions reproducible across Python, command-line, backend, workbench, and archive surfaces, with explicit reproducibility checks, before the Results tests each component in figure-locked order.",
            "The manuscript is therefore a methods Article rather than a new primary disease-biology claim. Its public demonstrations include paired ERK/Akt reporter trajectories for bounded coupling and Cell Painting/MitoTox endpoint tables for reserve-like and routed-output analyses (REF-0011; REF-0012). Across those examples, the central question is not whether every biological system contains a residence regime. It is whether a reviewable method can preserve dynamic operating-state information, reveal cases where amplitude or endpoint summaries are sufficient, and withhold interpretation when the data do not resolve the boundary. RhoDyn is designed to make those decisions reproducible across Python, command-line, backend, workbench, and archive surfaces, with explicit reproducibility checks, before the Results tests each component in figure-locked order.",
        ),
        (
            "Live-cell perturbation experiments increasingly record the temporal structure of signaling, morphology, and fate-associated reporters, but those records are still often collapsed to endpoints, peaks, thresholds, or generic trajectory features. Benchmarking and dynamical single-cell methods show that biological interpretation can change when a summary preserves transition structure rather than only static position (REF-0001; REF-0002; REF-0003; REF-0004). The practical problem for perturbation biology is that two cells can share a high peak, a similar endpoint, or the same apparent state assignment while spending different amounts of time in the operating range that matters for the experiment. A method that treats time in state as an explicit object is therefore needed to test when residence carries information that amplitude summaries miss.",
            "Live-cell perturbation experiments increasingly record the temporal structure of signaling, morphology, and fate-associated reporters, but those records are still often collapsed to endpoints, peaks, thresholds, or generic trajectory features. Benchmarking and dynamical single-cell methods show that biological interpretation can change when a summary preserves transition structure rather than only static position (REF-0001; REF-0002; REF-0003; REF-0004). For perturbation biology, the practical problem is that two cells can share a high peak, a similar endpoint, or the same apparent state assignment while spending different amounts of time in the operating range that matters for the experiment. A method that treats time in state as an explicit object is therefore needed to test when residence carries information that amplitude summaries miss.",
        ),
    ],
    SECTIONS_DIR / "results.md": [
        (
            "RhoDyn first had to be defined as a method object rather than as a collection of post hoc trajectory summaries. The input contract and workflow schematic (Fig. 1a) specify tidy trajectory or endpoint tables, declared biological windows, replicate variables, and exportable decision outputs. The residence-window panel (Fig. 1b) separates dwell fraction, dwell time, and segment count from peak, endpoint, and average amplitude, making time-in-state an explicit summary of the supplied trajectory rather than a hidden fitted state. Boundary cases (Fig. 1c) identify inputs that remain unresolved when time, condition, replicate, or window definitions are missing. Executable truth cases (Fig. 1d) then provide positive, negative, and ambiguous examples in which the same API returns a result or withholds one. This establishes RhoDyn as an inspectable residence-state analysis object with explicit failure modes, and it creates the need to test whether those summaries change interpretation relative to simpler baselines.",
            "Before examples could be interpreted, RhoDyn required a formal analysis object rather than a collection of post hoc trajectory summaries. In the input contract and workflow schematic (Fig. 1a), tidy trajectory and endpoint tables are linked to declared biological windows, replicate variables, and exportable decisions. The residence-window summary panel (Fig. 1b) then separates dwell fraction, dwell time, and segment count from peak, endpoint, and average amplitude, making time in state a visible property of the supplied trajectory rather than an implicit fitted state. Boundary cases for incomplete inputs (Fig. 1c) show when missing time, condition, replicate, or window definitions should prevent interpretation. Executable truth cases (Fig. 1d) complete the definition by showing positive, negative, and ambiguous examples in which the same API returns a result or withholds one. The section therefore establishes RhoDyn as an inspectable residence-state analysis object with explicit failure modes, setting up the benchmark question of when those summaries change interpretation relative to simpler baselines.",
        ),
        (
            "Known synthetic regimes provide the first controlled test because the correct interpretation is available before any biological example is considered. The regime grid (Fig. 2a) places amplitude-like, residence-like, ambiguous, and negative cases on shared simulated inputs. Comparing residence and amplitude summaries on those inputs (Fig. 2b) shows when dwell within a declared window changes the state assignment relative to endpoint, peak, or mean activity. The reduced-alternative comparison (Fig. 2c) asks whether simpler summaries can reproduce the same decision structure, while the negative and ambiguous cases (Fig. 2d) keep unsupported calls visible instead of forcing classification. Together, these benchmarks support residence-state inference in tested trajectory regimes while preserving cases where RhoDyn should remain inconclusive.",
            "Synthetic regimes provide the first controlled test because the correct interpretation is known before any biological example is considered. The regime grid (Fig. 2a) places amplitude-like, residence-like, ambiguous, and negative cases on matched simulated inputs. On those same traces, the residence-versus-amplitude comparison (Fig. 2b) shows when dwell inside a declared window changes the state assignment relative to endpoint, peak, or mean activity. Reduced-alternative comparisons (Fig. 2c) test whether simpler summaries can reproduce the same decision structure. Negative and ambiguous cases (Fig. 2d) keep unsupported calls visible rather than forcing classification. These benchmarks support residence-state inference in the tested trajectory regimes while preserving cases where RhoDyn should remain inconclusive.",
        ),
        (
            "After synthetic truth cases, independent public trajectories tested whether the same analysis object could expose residence-amplitude separation outside the reference use case. The public-data adapter map (Fig. 3a) shows how external calcium and ERK time-series tables are converted into the tidy input schema without changing their biological provenance. In the DRG calcium example (Fig. 3b), residence summaries capture time spent inside the declared response window separately from the amplitude of the calcium trace. In the ERK GPCR example (Fig. 3c), the same comparison separates window occupancy from peak or endpoint signaling. Window-sensitivity and uncertainty summaries (Fig. 3d) then show whether the interpretation is stable, fragile, or unresolved as the declared window changes. These public examples support the claim that residence and amplitude can diverge in more than one live-cell signaling system, without implying that residence summaries replace amplitude analysis for every reporter.",
            "Independent public trajectories then tested whether the same analysis object could expose residence-amplitude separation outside the reference use case. The public-data adapter map (Fig. 3a) shows how external calcium and ERK time-series tables enter the tidy input schema while retaining their biological context. In the DRG calcium demonstration (Fig. 3b), residence summaries capture time spent inside the declared response window separately from calcium-trace amplitude. In the ERK GPCR demonstration (Fig. 3c), the same comparison separates window occupancy from peak or endpoint signaling. Window-sensitivity and uncertainty summaries (Fig. 3d) show whether each interpretation is stable, fragile, or unresolved as the declared window changes. These public examples support residence-amplitude divergence in more than one live-cell signaling system, without implying that residence summaries replace amplitude analysis for every reporter.",
        ),
        (
            "Trajectory summaries do not cover all perturbation biology, so the next test moved to endpoint and paired-reporter inputs. The endpoint schema contract (Fig. 4a) defines the grouping, contrast, margin, and readout fields needed before any bounded-coupling or model-comparison decision is made. Bounded-coupling decisions under declared margins (Fig. 4b) distinguish passing, failing, and inconclusive contrasts rather than treating a non-significant difference as equivalence. The reserve-like coordinate (Fig. 4c) is explicitly tied to the measured endpoint, so the draft can describe buffering-like behavior without claiming unmeasured biological reserve capacity. Routed-output reduced-architecture comparisons (Fig. 4d) test whether simpler alternatives satisfy the observed endpoint structure, and the limitations panel (Fig. 4e) records which mechanistic interpretations remain outside the measured scope. This extends RhoDyn from trajectory residence scoring to endpoint decision support, while keeping coupling, reserve-like, and routed-output claims conditional on declared margins, uncertainty, and model alternatives.",
            "Perturbation biology also produces endpoint and paired-reporter inputs that cannot be reduced to trajectory residence alone. The endpoint schema contract (Fig. 4a) defines grouping, contrast, margin, and readout fields before any bounded-coupling or model-comparison decision is made. Under those declared margins, the bounded-coupling decision panel (Fig. 4b) distinguishes passing, failing, and inconclusive contrasts rather than treating a non-significant difference as equivalence. The reserve-like coordinate (Fig. 4c) remains tied to the measured endpoint, allowing buffering-like behavior to be described without claiming unmeasured biological reserve capacity. Routed-output reduced-architecture comparisons (Fig. 4d) test whether simpler alternatives satisfy the observed endpoint structure, and the limitation panel (Fig. 4e) states which mechanistic interpretations remain outside the measured scope. This extends RhoDyn from trajectory residence scoring to endpoint decision support while keeping coupling, reserve-like, and routed-output claims conditional on declared margins, uncertainty, and model alternatives.",
        ),
        (
            "The final Results step asks whether the method can be inspected and reproduced through the software surfaces a user would actually encounter. The parity panel (Fig. 6a) compares Python, CLI, backend, and workbench outputs for the retained evidence paths. The export-bundle view (Fig. 6b) shows that inputs, parameter choices, summaries, figures, and reports are written together rather than hidden in session state. Source-distribution clean-room reproduction (Fig. 6c) tests the archived package from an installable release boundary, while the archive and checksum panel (Fig. 6d) records the release identity and file-level reproducibility surface. The adoption and user-path rehearsal (Fig. 6e) then checks whether a biologist-facing and a quantitative workflow can reach the same reviewable outputs. These results support cross-surface reproducibility for the retained Stage 7 evidence and close the Results section by making RhoDyn's computational decisions inspectable rather than merely available as code.",
            "The final Results step asks whether the method can be inspected and reproduced through the software surfaces a user would actually encounter. The parity panel (Fig. 6a) compares Python, command-line, backend, and workbench outputs for the retained evidence paths. The export-bundle view (Fig. 6b) shows that inputs, parameter choices, summaries, figures, and reports are written together rather than hidden in session state. Source-distribution clean-room reproduction (Fig. 6c) tests the archived package from an installable release boundary, while the archive and checksum panel (Fig. 6d) records the release identity and file-level reproducibility surface. The adoption and user-path rehearsal (Fig. 6e) then checks whether biologist-facing and quantitative workflows can reach the same reviewable outputs. These results support cross-surface reproducibility for the retained evidence set and close the Results section by making RhoDyn's computational decisions inspectable rather than merely available as code.",
        ),
        (
            "Before examples could be interpreted, RhoDyn required a formal analysis object rather than a collection of post hoc trajectory summaries. In the input contract and workflow schematic (Fig. 1a), tidy trajectory and endpoint tables are linked to declared biological windows, replicate variables, and exportable decisions. The residence-window summary panel (Fig. 1b) then separates dwell fraction, dwell time, and segment count from peak, endpoint, and average amplitude, making time in state a visible property of the supplied trajectory rather than an implicit fitted state. Boundary cases for incomplete inputs (Fig. 1c) show when missing time, condition, replicate, or window definitions should prevent interpretation. Executable truth cases (Fig. 1d) complete the definition by showing positive, negative, and ambiguous examples in which the same API returns a result or withholds one. The section therefore establishes RhoDyn as an inspectable residence-state analysis object with explicit failure modes, setting up the benchmark question of when those summaries change interpretation relative to simpler baselines.",
            "Before examples could be interpreted, RhoDyn required a formal analysis object rather than a collection of post hoc trajectory summaries. In the input contract and workflow schematic (Fig. 1a), tidy trajectory and endpoint tables are linked to declared biological windows, replicate variables, and exportable decisions. In the residence-window summary panel (Fig. 1b), dwell fraction, dwell time, and segment count are separated from peak, endpoint, and average amplitude, making time in state a visible property of the supplied trajectory rather than an implicit fitted state. Boundary cases for incomplete inputs (Fig. 1c) show when missing time, condition, replicate, or window definitions should prevent interpretation. Executable truth cases (Fig. 1d) complete the definition by showing positive, negative, and ambiguous examples in which the same API returns a result or withholds one. Together, these definitions establish RhoDyn as an inspectable residence-state analysis object with explicit failure modes, setting up the benchmark question of when those summaries change interpretation relative to simpler baselines.",
        ),
        (
            "Synthetic regimes provide the first controlled test because the correct interpretation is known before any biological example is considered. The regime grid (Fig. 2a) places amplitude-like, residence-like, ambiguous, and negative cases on matched simulated inputs. On those same traces, the residence-versus-amplitude comparison (Fig. 2b) shows when dwell inside a declared window changes the state assignment relative to endpoint, peak, or mean activity. Reduced-alternative comparisons (Fig. 2c) test whether simpler summaries can reproduce the same decision structure. Negative and ambiguous cases (Fig. 2d) keep unsupported calls visible rather than forcing classification. These benchmarks support residence-state inference in the tested trajectory regimes while preserving cases where RhoDyn should remain inconclusive.",
            "Synthetic regimes provide the first controlled test because the correct interpretation is known before any biological example is considered. Within the regime grid (Fig. 2a), amplitude-like, residence-like, ambiguous, and negative cases are placed on matched simulated inputs. On those same traces, the residence-versus-amplitude comparison (Fig. 2b) shows when dwell inside a declared window changes the state assignment relative to endpoint, peak, or mean activity. Reduced-alternative comparisons (Fig. 2c) test whether simpler summaries can reproduce the same decision structure. Negative and ambiguous cases (Fig. 2d) keep unsupported calls visible rather than forcing classification. These benchmarks support residence-state inference in the tested trajectory regimes while preserving cases where RhoDyn should remain inconclusive.",
        ),
        (
            "Perturbation biology also produces endpoint and paired-reporter inputs that cannot be reduced to trajectory residence alone. The endpoint schema contract (Fig. 4a) defines grouping, contrast, margin, and readout fields before any bounded-coupling or model-comparison decision is made. Under those declared margins, the bounded-coupling decision panel (Fig. 4b) distinguishes passing, failing, and inconclusive contrasts rather than treating a non-significant difference as equivalence. The reserve-like coordinate (Fig. 4c) remains tied to the measured endpoint, allowing buffering-like behavior to be described without claiming unmeasured biological reserve capacity. Routed-output reduced-architecture comparisons (Fig. 4d) test whether simpler alternatives satisfy the observed endpoint structure, and the limitation panel (Fig. 4e) states which mechanistic interpretations remain outside the measured scope. This extends RhoDyn from trajectory residence scoring to endpoint decision support while keeping coupling, reserve-like, and routed-output claims conditional on declared margins, uncertainty, and model alternatives.",
            "Perturbation biology also produces endpoint and paired-reporter inputs that cannot be reduced to trajectory residence alone. In the endpoint schema contract (Fig. 4a), grouping, contrast, margin, and readout fields are defined before any bounded-coupling or model-comparison decision is made. Under those declared margins, the bounded-coupling decision panel (Fig. 4b) distinguishes passing, failing, and inconclusive contrasts rather than treating a non-significant difference as equivalence. For the reserve-like coordinate (Fig. 4c), the readout remains tied to the measured endpoint, allowing buffering-like behavior to be described without claiming unmeasured biological reserve capacity. Routed-output reduced-architecture comparisons (Fig. 4d) test whether simpler alternatives satisfy the observed endpoint structure, and the limitation panel (Fig. 4e) states which mechanistic interpretations remain outside the measured scope. This extends RhoDyn from trajectory residence scoring to endpoint decision support while keeping coupling, reserve-like, and routed-output claims conditional on declared margins, uncertainty, and model alternatives.",
        ),
        (
            "The final Results step asks whether the method can be inspected and reproduced through the software surfaces a user would actually encounter. The parity panel (Fig. 6a) compares Python, command-line, backend, and workbench outputs for the retained evidence paths. The export-bundle view (Fig. 6b) shows that inputs, parameter choices, summaries, figures, and reports are written together rather than hidden in session state. Source-distribution clean-room reproduction (Fig. 6c) tests the archived package from an installable release boundary, while the archive and checksum panel (Fig. 6d) records the release identity and file-level reproducibility surface. The adoption and user-path rehearsal (Fig. 6e) then checks whether biologist-facing and quantitative workflows can reach the same reviewable outputs. These results support cross-surface reproducibility for the retained evidence set and close the Results section by making RhoDyn's computational decisions inspectable rather than merely available as code.",
            "The final Results step asks whether the method can be inspected and reproduced through the software surfaces a user would actually encounter. The parity panel (Fig. 6a) compares Python, command-line, backend, and workbench outputs for the retained evidence paths. In the export-bundle view (Fig. 6b), inputs, parameter choices, summaries, figures, and reports are written together rather than hidden in session state. Source-distribution clean-room reproduction (Fig. 6c) tests the archived package from an installable release boundary, while the archive and checksum panel (Fig. 6d) records the release identity and file-level reproducibility surface. The adoption and user-path rehearsal (Fig. 6e) then checks whether biologist-facing and quantitative workflows can reach the same reviewable outputs. These results support cross-surface reproducibility for the retained evidence set and close the Results section by making RhoDyn's computational decisions inspectable rather than merely available as code.",
        ),
    ],
    SECTIONS_DIR / "discussion.md": [
        (
            "RhoDyn supports a methods claim that is deliberately narrower than a general theory of cell fate. The work makes residence-state inference an executable and inspectable object for live-cell perturbation data, so dwell fraction, dwell time, and segment count can be compared directly with endpoint, peak, mean, latency, and threshold-style summaries. That comparison matters because time spent inside a declared biological window can alter the interpretation of a trajectory even when amplitude summaries remain similar. At the same time, the declared window is not discovered automatically by the software, and residence is not a causal mechanism by itself. The appropriate conclusion is therefore not that residence replaces amplitude. It is that RhoDyn gives users a controlled way to ask when residence carries additional state information and when amplitude and endpoint summaries remain useful.",
            "RhoDyn supports a methods claim that is deliberately narrower than a general theory of cell fate. It makes residence-state inference executable and inspectable for live-cell perturbation data, allowing dwell fraction, dwell time, and segment count to be compared directly with endpoint, peak, mean, latency, and threshold-style summaries. The comparison matters because time spent inside a declared biological window can alter the interpretation of a trajectory even when amplitude summaries remain similar. The declared window, however, is not discovered automatically by the software, and residence is not a causal mechanism by itself. The appropriate conclusion is not that residence replaces amplitude. It is that RhoDyn gives users a controlled way to ask when residence carries additional state information and when amplitude and endpoint summaries remain useful.",
        ),
        (
            "RhoDyn's software evidence strengthens the method by making those decisions inspectable across use surfaces. The retained Stage 7 evidence can be regenerated through the source-distribution clean-room route, checked across Python, command-line, backend, and workbench paths, and exported with input schemas, parameter choices, summaries, figures, reports, and checksums. This supports software reproducibility for the demonstrated analyses, not a new biological result, regulatory qualification, or hidden private-data reproduction claim. It also leaves distribution boundaries visible. PyPI remains a later distribution decision, controlled-access inputs remain access-limited, and non-redistributable source material must be represented by reviewable derived tables or notes rather than silently absorbed into the method.",
            "RhoDyn's software evidence strengthens the method by making those decisions inspectable across use surfaces. The retained evidence set can be regenerated through the source-distribution clean-room route, checked across Python, command-line, backend, and workbench paths, and exported with input schemas, parameter choices, summaries, figures, reports, and checksums. This supports software reproducibility for the demonstrated analyses, not a new biological result, regulatory qualification, or hidden private-data reproduction claim. It also leaves distribution boundaries visible. Package-index distribution remains a later decision, controlled-access inputs remain access-limited, and non-redistributable source material must be represented by reviewable derived tables or notes rather than silently absorbed into the method.",
        ),
        (
            "Future directions are therefore methodological as much as biological. Applications should predeclare residence windows, bounded-coupling margins, grouping levels, uncertainty rules, and reduced alternatives, then report pass, fail, and inconclusive outcomes with equal visibility. New biological systems can sharpen the method by showing when residence, reserve-like endpoints, or routed outputs add information and when simpler summaries are sufficient. The most informative next demonstrations will be those that preserve replicate structure, expose enough sampling density to justify a declared window, and include perturbation designs capable of separating timing from amplitude. Equally useful will be negative examples in which RhoDyn returns the same conclusion as a simpler endpoint method, because those cases define where extra dynamic structure is unnecessary. The present evidence supports RhoDyn as a decision framework for dynamic operating-state interpretation in live-cell perturbation biology. RhoDyn is not an automatic mechanism-discovery engine, a substitute for perturbation experiments, or a claim that one dynamical summary is privileged in every cell-state problem.",
            "Future directions are therefore methodological as much as biological. Applications should predeclare residence windows, bounded-coupling margins, grouping levels, uncertainty rules, and reduced alternatives, then report pass, fail, and inconclusive outcomes with equal visibility. New biological systems can sharpen the method by showing when residence, reserve-like endpoints, or routed outputs add information and when simpler summaries are sufficient. The most informative demonstrations will preserve replicate structure, provide enough sampling density to justify a declared window, and include perturbation designs capable of separating timing from amplitude. Equally useful will be negative examples in which RhoDyn returns the same conclusion as a simpler endpoint method, because those cases define where extra dynamic structure is unnecessary. The present evidence supports RhoDyn as a decision framework for dynamic operating-state interpretation in live-cell perturbation biology. RhoDyn is not a mechanism-discovery engine, a substitute for perturbation experiments, or a claim that one dynamical summary is privileged in every cell-state problem.",
        ),
        (
            "The same restraint is essential for the non-trajectory demonstrations. Bounded-coupling decisions are useful only when the margin, uncertainty rule, grouping level, and decision state are declared before interpretation, and the held-out ERK/Akt contexts show why inconclusive cases must remain visible. A passing bounded-coupling result supports equivalence within the stated margin and context, not the exclusion of slower or context-specific coupling. Reserve-like summaries are likewise interpretable only as coordinates tied to the measured endpoint, not as direct assays of unmeasured biological reserve capacity. Routed-output comparisons can show that reduced alternatives fail the tested endpoint constraints, but effective model parameters should not be treated as direct biochemical interactions.",
            "That restraint also governs the non-trajectory demonstrations. Bounded-coupling decisions are useful only when the margin, uncertainty rule, grouping level, and decision state are declared before interpretation, and the held-out ERK/Akt contexts show why inconclusive cases must remain visible. A passing bounded-coupling result supports equivalence within the stated margin and context, not the exclusion of slower or context-specific coupling. Reserve-like summaries are likewise interpretable only as coordinates tied to the measured endpoint, not as direct assays of unmeasured biological reserve capacity. Routed-output comparisons can show that reduced alternatives fail the tested endpoint constraints, but effective model parameters should not be treated as direct biochemical interactions.",
        ),
        (
            "Future directions are therefore methodological as much as biological. Applications should predeclare residence windows, bounded-coupling margins, grouping levels, uncertainty rules, and reduced alternatives, then report pass, fail, and inconclusive outcomes with equal visibility. New biological systems can sharpen the method by showing when residence, reserve-like endpoints, or routed outputs add information and when simpler summaries are sufficient. The most informative demonstrations will preserve replicate structure, provide enough sampling density to justify a declared window, and include perturbation designs capable of separating timing from amplitude. Equally useful will be negative examples in which RhoDyn returns the same conclusion as a simpler endpoint method, because those cases define where extra dynamic structure is unnecessary. The present evidence supports RhoDyn as a decision framework for dynamic operating-state interpretation in live-cell perturbation biology. RhoDyn is not a mechanism-discovery engine, a substitute for perturbation experiments, or a claim that one dynamical summary is privileged in every cell-state problem.",
            "Future directions are therefore methodological as much as biological. Applications should predeclare residence windows, bounded-coupling margins, grouping levels, uncertainty rules, and reduced alternatives, then report pass, fail, and inconclusive outcomes with equal visibility. New biological systems can sharpen the method by showing when residence, reserve-like endpoints, or routed outputs add information and when simpler summaries are sufficient. The most informative demonstrations will preserve replicate structure, provide enough sampling density to justify a declared window, and include perturbation designs capable of separating timing from amplitude. Equally useful will be negative examples in which RhoDyn returns the same conclusion as a simpler endpoint method, because those cases define where extra dynamic structure is unnecessary. Taken together, the present evidence supports RhoDyn as a decision framework for dynamic operating-state interpretation in live-cell perturbation biology. RhoDyn is not a mechanism-discovery engine, a substitute for perturbation experiments, or a claim that one dynamical summary is privileged in every cell-state problem.",
        ),
    ],
    SECTIONS_DIR / "methods.md": [
        (
            "All analyses in this Methods draft refer to RhoDyn v0.1.0 and to the locked evidence snapshot `stage7.8-methods-readiness@242f06c49e8310b81ac1c06a270bb6810f3f4cfc` dated 2026-06-30. The software implements residence-aware interpretation of biological trajectories and endpoint perturbation tables. The manuscript use cases are treated as reproducible demonstrations of the method object, not as evidence that the software generated the motivating RhoA/microglia manuscript. Each analysis route returns a structured result, the effective parameters used to produce it, and a boundary statement describing what the result can and cannot support.",
            "All analyses in this Methods draft refer to RhoDyn v0.1.0 and to the locked evidence snapshot `stage7.8-methods-readiness@242f06c49e8310b81ac1c06a270bb6810f3f4cfc` dated 2026-06-30. The software implements residence-aware interpretation of biological trajectories and endpoint perturbation tables. The manuscript use cases are reproducible demonstrations of the method object, not evidence that the software generated the motivating RhoA/microglia manuscript. Each analysis route returns a structured result, the effective parameters used to produce it, and a boundary statement describing what the result can and cannot support.",
        ),
        (
            "The source-distribution clean-room route rebuilt selected evidence outputs from the packaged archive and compared deterministic tables against committed snapshots. This supports reproducibility of the demonstrated analyses, not a new biological result, hidden private-data reproduction claim, or package-index publication claim.",
            "The source-distribution clean-room route rebuilt selected evidence outputs from the packaged archive and compared deterministic tables against committed snapshots. This supports reproducibility of the demonstrated analyses, not a new biological result, hidden private-data reproduction claim, or package-index distribution claim.",
        ),
    ],
    FIGURES_DIR / "figure_legends.md": [
        (
            "The figure establishes the analysis object and its boundaries before any biological demonstration is considered.",
            "The figure establishes the analysis object and its boundaries before biological demonstrations are interpreted.",
        ),
        (
            "The figure supports residence-state inference in tested trajectory regimes while preserving cases where the method should remain inconclusive.",
            "The figure supports residence-state inference in tested trajectory regimes while preserving cases where the method should remain inconclusive.",
        ),
        (
            "The figure supports reproducibility of the demonstrated analyses without turning software availability into a new biological result.",
            "The figure supports reproducibility of the demonstrated analyses without turning software availability into a new biological result.",
        ),
    ],
}

FINAL_REPLACEMENT_PHRASES = {
    SECTIONS_DIR / "introduction.md": [
        "For perturbation biology, the practical problem",
    ],
    SECTIONS_DIR / "results.md": [
        "Together, these definitions establish RhoDyn",
        "Within the regime grid",
        "In the endpoint schema contract",
        "For the reserve-like coordinate",
        "In the export-bundle view",
    ],
    SECTIONS_DIR / "discussion.md": [
        "That restraint also governs",
        "Taken together, the present evidence supports RhoDyn",
    ],
    SECTIONS_DIR / "methods.md": [
        "not evidence that the software generated",
        "package-index distribution claim",
    ],
    FIGURES_DIR / "figure_legends.md": [
        "before biological demonstrations are interpreted",
    ],
}


def _now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _git_sha() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    except (OSError, subprocess.CalledProcessError):
        return "unknown"


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _strip_comments(text: str) -> str:
    return re.sub(r"<!--.*?-->", "", text, flags=re.S)


def _para_ids(text: str) -> list[str]:
    return sorted(set(re.findall(r"PARA-[A-Z]+-\d{3}", text)))


def _sentence_starts(text: str) -> Counter[str]:
    visible = _strip_comments(text)
    starts: Counter[str] = Counter()
    for sentence in re.split(r"(?<=[.!?])\s+", visible):
        sentence = sentence.strip()
        if not sentence or sentence.startswith("#"):
            continue
        match = re.match(r"([A-Z][A-Za-z']+)", sentence)
        if match:
            starts[match.group(1)] += 1
    return starts


def _max_paragraph_words(text: str) -> int:
    visible = _strip_comments(text)
    paragraphs = [p.strip() for p in visible.split("\n\n") if p.strip() and not p.lstrip().startswith("#")]
    return max((len(re.findall(r"\b\w+\b", paragraph)) for paragraph in paragraphs), default=0)


def _terminal_figure_calls(text: str) -> list[str]:
    visible = _strip_comments(text)
    return re.findall(r"[^.!?]*\((?:Fig\.|Supplementary Fig\.|Supplementary Table)[^)]+\)\.", visible)


def _apply_replacements(text: str, replacements: list[tuple[str, str]]) -> tuple[str, list[str], list[str]]:
    applied: list[str] = []
    missing: list[str] = []
    for index, (old, new) in enumerate(replacements, start=1):
        if old in text:
            text = text.replace(old, new)
            applied.append(f"replacement_{index}")
        elif new in text:
            applied.append(f"replacement_{index}_already_present")
        else:
            missing.append(f"replacement_{index}")
    return text, applied, missing


def _build_polished_surfaces() -> dict[Path, str]:
    polished: dict[Path, str] = {}
    for path in SURFACE_PATHS:
        text = path.read_text(encoding="utf-8")
        if path in REPLACEMENTS:
            text, _, _ = _apply_replacements(text, REPLACEMENTS[path])
        polished[path] = text
    return polished


def _audit_surfaces(before: dict[Path, str], after: dict[Path, str]) -> dict[str, Any]:
    gate_923 = _read_json(GATE_923) if GATE_923.exists() else {}
    replacement_missing: dict[str, list[str]] = {}
    replacement_applied: dict[str, list[str]] = {}
    for path in SURFACE_PATHS:
        if path in REPLACEMENTS:
            _, applied, missing = _apply_replacements(before[path], REPLACEMENTS[path])
            replacement_applied[path.relative_to(ROOT).as_posix()] = applied
        missing_final_phrases = [
            f"final_phrase_{index}"
            for index, phrase in enumerate(FINAL_REPLACEMENT_PHRASES.get(path, []), start=1)
            if phrase not in after[path]
        ]
        if missing_final_phrases:
            replacement_missing[path.relative_to(ROOT).as_posix()] = missing_final_phrases

    paragraph_errors: list[str] = []
    for path in [SECTIONS_DIR / "introduction.md", SECTIONS_DIR / "results.md", SECTIONS_DIR / "discussion.md", SECTIONS_DIR / "methods.md"]:
        if _para_ids(before[path]) != _para_ids(after[path]):
            paragraph_errors.append(path.relative_to(ROOT).as_posix())

    combined_visible = "\n\n".join(_strip_comments(text) for text in after.values())
    unsafe_hits = [phrase for phrase in UNSAFE_PHRASES if phrase.lower() in combined_visible.lower()]
    missing_limits = [term for term in REQUIRED_LIMIT_TERMS if term.lower() not in combined_visible.lower()]
    terminal_calls = {
        path.relative_to(ROOT).as_posix(): _terminal_figure_calls(text)
        for path, text in after.items()
        if _terminal_figure_calls(text)
    }
    starts = {path.relative_to(ROOT).as_posix(): dict(_sentence_starts(text).most_common(5)) for path, text in after.items()}
    max_words = {path.relative_to(ROOT).as_posix(): _max_paragraph_words(text) for path, text in after.items()}
    downstream_paths = [path.relative_to(ROOT).as_posix() for path in FORBIDDEN_DOWNSTREAM_PATHS if path.exists()]
    reader_stage_hits = []
    for path, text in after.items():
        visible = _strip_comments(text)
        if "Stage 9" in visible or "stage9" in visible:
            reader_stage_hits.append(path.relative_to(ROOT).as_posix())

    checks = [
        {
            "name": "stage_9_23_gate_passed",
            "passed": gate_923.get("pass") is True and gate_923.get("next_substage") == "9.24",
            "detail": "Stage 9.23 figure legend and caption gate is present and points to Stage 9.24",
        },
        {
            "name": "paragraph_id_set_unchanged",
            "passed": not paragraph_errors,
            "detail": f"paragraph_id_errors={paragraph_errors}",
        },
        {
            "name": "strength_caps_hold",
            "passed": not unsafe_hits,
            "detail": f"unsafe_hits={unsafe_hits}",
        },
        {
            "name": "limitations_remain_present",
            "passed": not missing_limits,
            "detail": f"missing_limit_terms={missing_limits}",
        },
        {
            "name": "dynamic_figure_call_flow_preserved",
            "passed": not terminal_calls,
            "detail": f"terminal_figure_calls={terminal_calls}",
        },
        {
            "name": "reader_surface_stage_language_absent",
            "passed": not reader_stage_hits,
            "detail": f"reader_stage_hits={reader_stage_hits}",
        },
        {
            "name": "recursive_editorial_replacements_resolved",
            "passed": not replacement_missing,
            "detail": f"replacement_missing={replacement_missing}",
        },
        {
            "name": "no_downstream_stage_started",
            "passed": not downstream_paths,
            "detail": f"downstream_paths={downstream_paths}",
        },
    ]
    return {
        "generated_utc": _now(),
        "commit": _git_sha(),
        "checks": checks,
        "replacement_applied": replacement_applied,
        "replacement_missing": replacement_missing,
        "paragraph_errors": paragraph_errors,
        "unsafe_hits": unsafe_hits,
        "missing_limits": missing_limits,
        "terminal_calls": terminal_calls,
        "reader_stage_hits": reader_stage_hits,
        "downstream_paths": downstream_paths,
        "sentence_starts": starts,
        "max_paragraph_words": max_words,
        "recursive_rounds": [
            {
                "round": 1,
                "focus": "cadence and sentence flow",
                "status": "pass" if not terminal_calls else "fail",
            },
            {
                "round": 2,
                "focus": "claim-strength and limitation retention",
                "status": "pass" if not unsafe_hits and not missing_limits else "fail",
            },
            {
                "round": 3,
                "focus": "reader-surface leakage and downstream-boundary check",
                "status": "pass" if not reader_stage_hits and not downstream_paths else "fail",
            },
        ],
    }


def _audit_text(analysis: dict[str, Any]) -> str:
    checks_rows = "\n".join(
        f"| {item['name']} | {'pass' if item['passed'] else 'fail'} | {item['detail']} |"
        for item in analysis["checks"]
    )
    starts_rows = "\n".join(
        f"| {path} | {starts} | {analysis['max_paragraph_words'][path]} |"
        for path, starts in analysis["sentence_starts"].items()
    )
    replacement_rows = "\n".join(
        f"| {path} | {', '.join(items)} |" for path, items in analysis["replacement_applied"].items()
    )
    rounds_rows = "\n".join(
        f"| {item['round']} | {item['focus']} | {item['status']} |" for item in analysis["recursive_rounds"]
    )
    return f"""<!-- EDITORIAL-PASS-1 stage=9.24 generated={analysis['generated_utc']} commit={analysis['commit']} -->
# Stage 9.24 editorial polish pass I

Stage 9.24 performs the first reader-facing polish loop after the figure legend and caption audit. The pass improves cadence, reduces mechanical transitions, and keeps claim language inside the frozen method boundaries. It does not change evidence files, statistics, figures, model outputs, figure numbering, or the biological-method claims.

## Summary

The editorial polish pass completed three recursive checks. Paragraph IDs were preserved, claim-strength caps remained intact, limitations stayed present, and no downstream editorial polish, reader-hygiene gate, PI packet, readiness checklist, or final package assembly was started.

## Recursive polish rounds

| Round | Focus | Status |
|---|---|---|
{rounds_rows}

## Gate checks

| Check | Status | Detail |
|---|---|---|
{checks_rows}

## Cadence metrics

| Surface | Most common sentence starts | Maximum paragraph words |
|---|---|---|
{starts_rows}

## Replacements applied

| Surface | Replacement status |
|---|---|
{replacement_rows}

## Scope boundary

This stage modifies reader-facing prose for flow only. It does not broaden the residence, bounded-coupling, reserve-like, routed-output, or reproducibility claims. It keeps inconclusive outcomes visible and preserves the distinction between demonstrated software reproducibility and new biological evidence.
"""


def _gate_payload(analysis: dict[str, Any]) -> dict[str, Any]:
    return {
        "substage": "9.24",
        "title": "Editorial polish pass I",
        "generated_utc": analysis["generated_utc"],
        "commit": analysis["commit"],
        "pass": all(item["passed"] for item in analysis["checks"]),
        "checks": analysis["checks"],
        "paragraph_errors": analysis["paragraph_errors"],
        "unsafe_hits": analysis["unsafe_hits"],
        "missing_limits": analysis["missing_limits"],
        "terminal_calls": analysis["terminal_calls"],
        "reader_stage_hits": analysis["reader_stage_hits"],
        "downstream_paths": analysis["downstream_paths"],
        "recursive_rounds": analysis["recursive_rounds"],
        "outputs": [
            "manuscript/nature_methods/audits/editorial_pass_1.md",
            "manuscript/nature_methods/gate_verdicts/9.24.json",
            "manuscript/nature_methods/sections/introduction.md",
            "manuscript/nature_methods/sections/results.md",
            "manuscript/nature_methods/sections/discussion.md",
            "manuscript/nature_methods/sections/methods.md",
            "manuscript/nature_methods/figures/figure_legends.md",
        ],
        "scope_boundary": "Editorial polish only. No new evidence, analyses, statistics, model outputs, figures, figure numbering, claim expansion, PI packet, readiness checklist, or final package assembly.",
        "next_substage": "9.25",
    }


def _stage_outputs(after: dict[Path, str], analysis: dict[str, Any], gate: dict[str, Any]) -> None:
    for path, text in after.items():
        staged = STAGING_DIR / path.relative_to(WORKSPACE)
        staged.parent.mkdir(parents=True, exist_ok=True)
        staged.write_text(text, encoding="utf-8")
    audit_path = STAGING_DIR / OUTPUTS["audit"].relative_to(WORKSPACE)
    gate_path = STAGING_DIR / OUTPUTS["gate"].relative_to(WORKSPACE)
    audit_path.parent.mkdir(parents=True, exist_ok=True)
    gate_path.parent.mkdir(parents=True, exist_ok=True)
    audit_path.write_text(_audit_text(analysis), encoding="utf-8")
    _write_json(gate_path, gate)


def _promote_from_staging() -> None:
    for path in [*SURFACE_PATHS, *OUTPUTS.values()]:
        staged = STAGING_DIR / path.relative_to(WORKSPACE)
        path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(staged, path)


def _quarantine_staging() -> Path:
    QUARANTINE_DIR.parent.mkdir(parents=True, exist_ok=True)
    if QUARANTINE_DIR.exists():
        shutil.rmtree(QUARANTINE_DIR)
    shutil.move(str(STAGING_DIR), str(QUARANTINE_DIR))
    return QUARANTINE_DIR


def _update_registry() -> None:
    registry = _read_json(REGISTRY_PATH)
    for substage in registry.get("substages", []):
        if substage.get("id") == "9.24":
            substage["status"] = "complete_editorial_polish_pass_1_bound"
    registry["last_completed_substage"] = "9.24"
    registry["next_substage"] = "9.25"
    _write_json(REGISTRY_PATH, registry)


def _upsert_completed_substage(memory: dict[str, Any], checks: list[dict[str, Any]]) -> None:
    record = {
        "substage": "9.24",
        "status": "pass",
        "pass": True,
        "gate_verdict_path": "manuscript/nature_methods/gate_verdicts/9.24.json",
        "validation_outcome": "Reader-facing cadence and claim-strength polish completed without changing evidence bindings",
        "evidence_dependencies": [
            "manuscript/nature_methods/gate_verdicts/9.23.json",
            "manuscript/nature_methods/ledgers/claim_strength_rules.md",
            "manuscript/nature_methods/ledgers/non_claims_and_scope_boundaries.md",
            "manuscript/nature_methods/sections/introduction.md",
            "manuscript/nature_methods/sections/results.md",
            "manuscript/nature_methods/sections/discussion.md",
            "manuscript/nature_methods/sections/methods.md",
            "manuscript/nature_methods/figures/figure_legends.md",
        ],
        "files_created_or_modified": [
            "manuscript/nature_methods/audits/editorial_pass_1.md",
            "manuscript/nature_methods/gate_verdicts/9.24.json",
            "manuscript/nature_methods/sections/introduction.md",
            "manuscript/nature_methods/sections/results.md",
            "manuscript/nature_methods/sections/discussion.md",
            "manuscript/nature_methods/sections/methods.md",
            "manuscript/nature_methods/figures/figure_legends.md",
        ],
        "remaining_blockers": [
            "Editorial polish pass II has not started",
            "Reader-surface hygiene gate remains downstream",
            "Full submission-package assembly has not started beyond the Reporting Summary requirement placeholder",
        ],
        "checks": checks,
    }
    entries = [item for item in memory.get("completed_substages", []) if item.get("substage") != "9.24"]
    entries.append(record)
    memory["completed_substages"] = entries


def _update_stage9_memory(generated_utc: str, checks: list[dict[str, Any]]) -> None:
    memory = _read_json(MEMORY_PATH)
    memory["generated_utc"] = generated_utc
    memory["current_substage"] = "9.24"
    memory["editorial_polish_pass_1_started"] = True
    memory["status"] = "stage9_24_editorial_polish_pass_1_bound"
    memory["current_gate"] = "Stage 9.24 editorial polish pass I preserved paragraph IDs, claim caps, and limitations"
    memory["next_substage"] = "9.25"
    memory["next_substage_authorized"] = False
    memory["stage9_active_gate"] = "Stage 9.24 Editorial polish pass I complete; editorial polish pass II not started"
    memory["stage9_24_checks"] = checks
    artifacts = memory.setdefault("artifacts", [])
    for artifact in [
        "manuscript/nature_methods/audits/editorial_pass_1.md",
        "manuscript/nature_methods/gate_verdicts/9.24.json",
    ]:
        if artifact not in artifacts:
            artifacts.append(artifact)
    memory["gate"] = [
        "Stage 9.-1 contract and schema files exist and pass the scaffold checker.",
        "Stage 9.0 through Stage 9.24 are complete through editorial polish pass I.",
        "Stage 9.25, Stage 9.25b, and Stage 9.26 through Stage 9.29 remain not started.",
        "No editorial polish pass II, reader-surface hygiene report, PI review packet, or submission readiness checklist is created in this pass.",
        "Paragraph IDs, claim-strength caps, and limitations remain intact.",
    ]
    memory["scope_rule"] = (
        "Stage 9 has completed evidence intake, venue-guidance registration, representative methods-paper corpus analysis, "
        "narrative-spine selection, claim freeze, paragraph-level claim planning, main figure-spine planning, deterministic "
        "PanelForge rendering, supplementary display planning, section-contract planning, title/abstract strategy, Results "
        "architecture, Results drafting, Introduction literature binding, Discussion interpretation mapping, Discussion drafting, "
        "Methods architecture, Methods drafting, availability assembly, Supplementary Methods drafting, supplementary table/source-data "
        "binding, reference-library/citation audit, cross-document consistency audit, statistical/quantitative language audit, "
        "figure legend/caption audit, and editorial polish pass I only. Do not start editorial polish pass II, reader-surface hygiene, "
        "or final submission package without explicit substage authorization."
    )
    _upsert_completed_substage(memory, checks)
    _write_json(MEMORY_PATH, memory)


def _update_roadmap_memory() -> None:
    memory = _read_json(ROADMAP_MEMORY_PATH)
    current = memory.setdefault("current_position", {})
    current["active_stage"] = "Stage 9.24 Editorial polish pass I complete; editorial polish pass II not started"
    current["stage9_active_gate"] = "Stage 9.24 Editorial polish pass I complete; editorial polish pass II not started"
    current["after_stage9_24_editorial_polish_pass_1"] = (
        "Stage 9.24 polished reader-facing section cadence and figure-legend flow while preserving paragraph IDs, claim-strength caps, "
        "limitations, statistics, figures, and evidence bindings. It did not start editorial polish pass II, the reader-surface hygiene gate, or final package assembly."
    )
    current["current_gate"] = "Editorial polish pass I completed without evidence-layer changes"
    current["next_stage"] = "Stage 9.25 Editorial polish pass II"
    for stage in memory.get("stage_lock", []):
        if not isinstance(stage, dict) or stage.get("stage") != 9:
            continue
        stage["status"] = "stage9_24_editorial_polish_pass_1_bound"
        stage["current_gate"] = "Stage 9.24 polish preserved paragraph IDs, claim-strength caps, and limitation language"
        stage["scope_rule"] = (
            "Stage 9 has completed evidence intake, venue-guidance registration, representative methods-paper corpus analysis, "
            "narrative-spine selection, claim freeze, paragraph-level claim planning, main figure-spine planning, deterministic "
            "PanelForge rendering, supplementary display planning, section-contract planning, front-matter strategy, Results architecture, "
            "Results drafting, Introduction literature binding, Discussion interpretation mapping, Discussion drafting, Methods architecture, "
            "Methods drafting, availability assembly, Supplementary Methods drafting, supplementary table/source-data binding, reference-library/citation audit, "
            "cross-document consistency audit, statistical-language audit, figure legend/caption audit, and editorial polish pass I only. Do not start editorial polish pass II, reader-surface hygiene, review response, or final submission packaging without explicit substage authorization."
        )
        artifacts = stage.setdefault("artifacts", [])
        for artifact in [
            "manuscript/nature_methods/audits/editorial_pass_1.md",
            "manuscript/nature_methods/gate_verdicts/9.24.json",
            "scripts/run_stage9_24_editorial_polish_pass1.py",
        ]:
            if artifact not in artifacts:
                artifacts.append(artifact)
        gate = stage.setdefault("gate", [])
        polish_gate = "Stage 9.24 polished reader-facing cadence while preserving paragraph IDs, claim caps, and limitations."
        if polish_gate not in gate:
            gate.append(polish_gate)
        for subphase in stage.get("subphases", []):
            if isinstance(subphase, dict) and subphase.get("id") == "9.24":
                subphase["status"] = "complete_editorial_polish_pass_1_bound"
                subphase["evidence"] = "manuscript/nature_methods/gate_verdicts/9.24.json"
    _write_json(ROADMAP_MEMORY_PATH, memory)


def _replace_once(body: str, old: str, new: str) -> str:
    return body.replace(old, new) if old in body else body


def _update_docs() -> None:
    README_PATH.write_text(
        """# Nature Methods manuscript workspace

This directory is the Stage 9 manuscript-assembly workspace for RhoDyn.

Current status. Stage 9.24 editorial polish pass I complete.

The workspace now contains the authorized manuscript components through the first editorial polish pass. Evidence intake, venue guidance, methods-paper corpus analysis, narrative spine, claim freeze, paragraph planning, figure planning, deterministic main-figure rendering, supplementary display planning, section contracts, front matter, Results, Introduction, Discussion, Methods, availability statements, Supplementary Methods, supplementary table/source-data binding, reference audit, cross-document consistency audit, statistical-language audit, figure legend/caption audit, and editorial polish pass I are present.

The next unstarted step is Stage 9.25 editorial polish pass II. The reader-surface hygiene gate, final manuscript assembly, PI review packet, submission-readiness checklist, and final package assembly have not started.

PanelForge figure rendering has already been exercised through the authorized Stage 9.6b deterministic rendering lane. The placeholder under `tools/panelforge-figures/` is not a clone, `.venv-panelforge` is not created by this workspace, and no local figure-engine repository is vendored here.
""",
        encoding="utf-8",
    )
    if PLAN_PATH.exists():
        body = PLAN_PATH.read_text(encoding="utf-8")
        body = _replace_once(
            body,
            "Stage 9.23 registers `figures/figure_legends.md`, `audits/figure_legend_audit.md`, and `gate_verdicts/9.23.json`. The current state intentionally does not create editorial-polish reports or full submission-package files.",
            "Stage 9.23 registers `figures/figure_legends.md`, `audits/figure_legend_audit.md`, and `gate_verdicts/9.23.json`. Stage 9.24 registers `audits/editorial_pass_1.md` and `gate_verdicts/9.24.json`, and polishes section and legend cadence without changing evidence bindings. The current state intentionally does not create editorial-polish pass II, reader-surface hygiene, or full submission-package files.",
        )
        body = _replace_once(
            body,
            "| 9.24 | Editorial polish pass I | not_started | Improve scientific clarity without changing meaning. |",
            "| 9.24 | Editorial polish pass I | complete_editorial_polish_pass_1_bound | Improve scientific clarity without changing meaning. |",
        )
        PLAN_PATH.write_text(body, encoding="utf-8")
    if ROADMAP_PATH.exists():
        body = ROADMAP_PATH.read_text(encoding="utf-8")
        body = _replace_once(
            body,
            "Stage 9.18 has registered Supplementary Methods, Stage 9.19 has\nregistered supplementary table/source-data binding, Stage 9.20 has registered\nthe reference library and citation audit, Stage 9.21 has registered the\ncross-document consistency audit, Stage 9.22 has registered the statistical\nand quantitative language audit, and Stage 9.23 has registered figure legends\nand table captions. Editorial polish and final package assembly remain not\nstarted.",
            "Stage 9.18 has registered Supplementary Methods, Stage 9.19 has\nregistered supplementary table/source-data binding, Stage 9.20 has registered\nthe reference library and citation audit, Stage 9.21 has registered the\ncross-document consistency audit, Stage 9.22 has registered the statistical\nand quantitative language audit, Stage 9.23 has registered figure legends\nand table captions, and Stage 9.24 has completed editorial polish pass I.\nEditorial polish pass II, reader-surface hygiene, and final package assembly\nremain not started.",
        )
        body = _replace_once(
            body,
            "| Stage 9. Nature Methods manuscript assembly | Stage 9.23 Figure legend and caption audit complete, editorial polish pass I not started. | The current boundary is evidence intake, official venue-guidance registration, representative methods-paper corpus analysis, narrative-spine selection, claim freeze, paragraph-level claim planning, main figure-spine planning, deterministic PanelForge rendering, supplementary display planning, section-contract planning, front-matter strategy, Results architecture, Results drafting, Introduction literature binding, Discussion interpretation mapping, Discussion drafting, Methods architecture, Methods drafting, availability assembly, Supplementary Methods drafting, supplementary table/source-data binding, reference-library/citation audit, cross-document consistency audit, statistical-language audit, and figure legend/caption audit only. Do not start editorial polish, review response, or final submission packaging without explicit substage authorization. |",
            "| Stage 9. Nature Methods manuscript assembly | Stage 9.24 Editorial polish pass I complete, editorial polish pass II not started. | The current boundary is evidence intake, official venue-guidance registration, representative methods-paper corpus analysis, narrative-spine selection, claim freeze, paragraph-level claim planning, main figure-spine planning, deterministic PanelForge rendering, supplementary display planning, section-contract planning, front-matter strategy, Results architecture, Results drafting, Introduction literature binding, Discussion interpretation mapping, Discussion drafting, Methods architecture, Methods drafting, availability assembly, Supplementary Methods drafting, supplementary table/source-data binding, reference-library/citation audit, cross-document consistency audit, statistical-language audit, figure legend/caption audit, and editorial polish pass I only. Do not start editorial polish pass II, reader-surface hygiene, review response, or final submission packaging without explicit substage authorization. |",
        )
        body = _replace_once(
            body,
            "Stage 9.10 Results subsection architecture has been completed. Stage 9.11 Results drafting pass has been completed. Stage 9.12 Introduction literature binding has been completed. Stage 9.13 Discussion interpretation map has been completed. Stage 9.14 Discussion drafting pass has been completed. Stage 9.15 Methods architecture has been completed. Stage 9.16 Methods drafting pass has been completed. Stage 9.17 software, data, and code availability assembly has been completed. Stage 9.18 Supplementary Methods drafting has been completed. Stage 9.19 Supplementary tables and source-data binding has been completed. Stage 9.20 Reference library and citation audit has been completed. Stage 9.21 Cross-document consistency audit has been completed. Stage 9.22 Statistical and quantitative language audit has been completed. Stage 9.23 Figure legend and caption audit has been completed. Stage 9.24 Editorial polish pass I remains the next unstarted manuscript step. Final package assembly remains not started.",
            "Stage 9.10 Results subsection architecture has been completed. Stage 9.11 Results drafting pass has been completed. Stage 9.12 Introduction literature binding has been completed. Stage 9.13 Discussion interpretation map has been completed. Stage 9.14 Discussion drafting pass has been completed. Stage 9.15 Methods architecture has been completed. Stage 9.16 Methods drafting pass has been completed. Stage 9.17 software, data, and code availability assembly has been completed. Stage 9.18 Supplementary Methods drafting has been completed. Stage 9.19 Supplementary tables and source-data binding has been completed. Stage 9.20 Reference library and citation audit has been completed. Stage 9.21 Cross-document consistency audit has been completed. Stage 9.22 Statistical and quantitative language audit has been completed. Stage 9.23 Figure legend and caption audit has been completed. Stage 9.24 Editorial polish pass I has been completed. Stage 9.25 Editorial polish pass II remains the next unstarted manuscript step. Final package assembly remains not started.",
        )
        ROADMAP_PATH.write_text(body, encoding="utf-8")


def run() -> dict[str, Any]:
    if STAGING_DIR.exists():
        shutil.rmtree(STAGING_DIR)
    STAGING_DIR.mkdir(parents=True, exist_ok=True)

    before = {path: path.read_text(encoding="utf-8") for path in SURFACE_PATHS}
    after = _build_polished_surfaces()
    analysis = _audit_surfaces(before, after)
    gate = _gate_payload(analysis)
    _stage_outputs(after, analysis, gate)

    if not gate["pass"]:
        quarantine = _quarantine_staging()
        return {
            "status": "failed",
            "substage": "9.24",
            "quarantine": quarantine.relative_to(ROOT).as_posix(),
            "checks": analysis["checks"],
            "next_substage": "9.24",
        }

    _promote_from_staging()
    shutil.rmtree(STAGING_DIR)
    _update_registry()
    _update_stage9_memory(analysis["generated_utc"], analysis["checks"])
    _update_roadmap_memory()
    _update_docs()
    return {
        "status": "completed",
        "substage": "9.24",
        "outputs": [
            "manuscript/nature_methods/audits/editorial_pass_1.md",
            "manuscript/nature_methods/gate_verdicts/9.24.json",
        ],
        "checks": analysis["checks"],
        "next_substage": "9.25",
    }


def main() -> int:
    result = run()
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] == "completed" else 1


if __name__ == "__main__":
    raise SystemExit(main())

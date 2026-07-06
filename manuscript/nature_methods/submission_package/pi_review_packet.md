# Executive Summary

The manuscript presents RhoDyn as a computational method for residence-state inference in live-cell perturbation data. Its most credible advance is not the broad observation that signaling dynamics matter, which is already established, but the integration of declared residence windows, amplitude comparators, bounded-coupling decisions, reserve-like endpoint coordinates, routed-output model comparison, and cross-surface reproducibility into one inspectable workflow. The work fits a Nature Methods-style Article best when positioned as a decision framework that reports pass, fail, and inconclusive outcomes rather than as a new biological theory. The six-figure structure is coherent, the public calcium and ERK demonstrations give useful portability evidence, and the software/release surfaces are unusually explicit for reviewer inspection.

My main reservations concern how much novelty should be assigned to the integrated workflow, how strongly the public examples establish generality, and whether readers can reconstruct grouping, margins, uncertainty rules, and non-example behavior without overreading the biological demonstrations. I do not find a fatal flaw in the current package, but several conclusions require continued restraint. The manuscript should keep its claim centered on an executable method object, not on universal residence biology, and it should retain amplitude-sufficient, inconclusive, and measurement-limited cases as core evidence rather than caveats.

# Revision Aspects

## Major

1. The novelty claim is plausible but must remain sharply differentiated from prior live-cell dynamics, trajectory-inference, and software-method literature. This issue appears in the title, Abstract, Introduction, and Discussion. The manuscript now states more clearly that the advance is not the discovery that signaling dynamics or transient states matter, but the operational workflow that combines residence scoring, amplitude comparators, bounded coupling, reserve-like endpoints, routed alternatives, and reproducibility surfaces. A satisfactory final version should keep that distinction visible throughout and avoid making the RhoDyn contribution sound like a general theory of cell-state dynamics.

2. The public demonstrations are useful but do not yet establish broad biological generality. Figures 3-5 show public reporter and endpoint examples, but the evidence is still a small set of selected systems rather than a field-wide benchmark. The authors should preserve the current language that the examples test portability and decision behavior, not universal residence biology. If a stronger generality claim is desired, it would require additional independent datasets or a predeclared sampling rationale, which is beyond the safe auto-revision scope.

3. The methods depend on declared windows, margins, and grouping choices, so reporting must make those choices reconstructable. This concern maps to Online Methods, Fig. 1, Fig. 4, Fig. 5, and Supplementary Methods. The source text now clarifies that grouping variables are preserved when supplied and that missing replicate structure cannot be reconstructed. A satisfactory package should keep the exact window, margin, grouping, and uncertainty fields visible in the supporting tables and should avoid implying that RhoDyn discovers biological windows automatically.

4. The bounded-coupling and reserve-like claims are appropriately scoped but remain sensitive to wording. In Fig. 4, Fig. 5, Online Methods, and Discussion, a passing bounded-coupling result should mean equivalence within the stated margin and context, not absence of all coupling. Likewise, reserve-like coordinates should remain tied to measured endpoint behavior rather than unmeasured biological reserve capacity. The current auto-revision preserves this boundary, but final review should check every caption and summary sentence for overstatement.

5. Routed-output model comparison should not be read as molecular mechanism identification. This affects Fig. 4d, Supplementary Fig. 6, Results, and Online Methods. The manuscript correctly frames reduced architectures as endpoint alternatives, but the term architecture can still invite mechanistic overinterpretation. The authors should keep effective-parameter language and avoid implying that the retained architecture identifies direct biochemical edges.

6. Statistical reporting is strong for a methods manuscript but should keep inconclusive outcomes as visible as passing calls. Figures 4 and 5 and the Methods describe declared margins, interval support, ROPE-style thresholds where available, and sensitivity to margins. This reviewer would not accept a revision that collapses those outcomes into a binary success-rate summary. The current package is acceptable only if pass, fail, and inconclusive cases remain co-equal in the Results and supplementary support.

7. Reproducibility is a strength, but the release boundary must stay exact. Figure 6, Code availability, and Code for review distinguish the GitHub/Zenodo release from PyPI distribution and from non-redistributable or controlled-access inputs. That precision should be retained. The official Reporting Summary, portal metadata, and any private input restrictions remain human-submission checks rather than manuscript-derived evidence.

## Minor

1. The Abstract should keep the phrase structure that names amplitude-sufficient and unresolved cases, because this prevents the method from being read as a universal residence detector.

2. The Introduction should avoid adding additional method-literature citations unless a specific claim is unsupported. The current reference set is compact and targeted, but final author review should confirm whether the ERK dynamics and equivalence-testing context needs one more explicit citation.

3. Figure 3 should continue to describe public reporters as demonstrations of portability, not proof that calcium and ERK share a common residence mechanism.

4. Figure 4 legend wording should retain the distinction between bounded coupling, reserve-like endpoint summaries, and routed-output comparisons. These are related decision objects, not interchangeable biological claims.

5. Figure 6 and Code availability should keep the PanelForge citation separate from the RhoDyn software citation, because figure rendering and method execution are distinct reproducibility surfaces.

6. The Methods should retain validation-failure language for invalid inputs. That language is important for users because a withheld decision is a legitimate method output.

7. The Supplementary Information should keep non-example and ambiguous regimes visible rather than burying them as limitations.

8. Before journal upload, the authors should complete the official Springer Nature Reporting Summary and verify that the final uploaded files preserve the same release identifiers and figure counts as the package.

# Confidential Recommendation to the Editor

Potentially Accept after Major Revision and Re-review

The manuscript has a credible methods contribution, but acceptance should depend on preserving the calibrated novelty claim and the decision-boundary language addressed in Major items 1-6. The required revisions are largely feasible through claim calibration, reporting precision, and documentation rather than new experiments, although a stronger generality claim would require additional datasets. The upside is a useful, reproducible framework for live-cell perturbation data that makes residence, bounded coupling, reserve-like endpoints, and routed-output alternatives reviewable across software surfaces. The main risk is novelty inflation or overgeneralization from a limited set of demonstrations if the manuscript drifts from method-object language into broad biological claims.

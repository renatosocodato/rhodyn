# Stage 10.14 final figure-direction inspection

## Decision

The Stage 10.14 review renders should not be accepted as the final Nature Methods figure-production direction. They are acceptable as a review scaffold for the six-figure logic, panel ordering, and recipe-diversification strategy, but they do not yet meet the final figure contract.

## Accepted Direction

- The six-figure manuscript logic is coherent.
- The panel coverage matches the intended Nature Methods story.
- The Stage 10.21 recipe binding gives the figures enough visual diversity to avoid a copy-paste template feel.
- The current review PNG, SVG, and PDF exports are useful for manuscript-level review.
- No non-white content was detected touching the 12 px outer image edge in the review PNGs.

## Not Final Yet

- The review PDFs use embedded DejaVu Type 3 fonts rather than Helvetica.
- The SVGs retain repeated review-only text blocks such as `Purpose`, `Reader readout`, and `Stage 10`.
- The figures carry too much prose inside panels for a final Nature Methods figure set.
- Footnote-like stage labels remain visible and should be pruned from the final production surface.
- The current visual pass checks outer-edge safety, but it does not yet prove annotation-to-data collision safety inside each panel.
- The PNGs are review companions, not the final high-resolution figure contract.

## Final PanelForge Contract

The next production pass should render the final PanelForge figures as vector-native PDFs with companion high-resolution PNGs. Each final figure must use Helvetica or a Helvetica-compatible embedded sans-serif font. Panel titles should be short, instructive, evidence-bound, and descriptive. In-panel text should be limited to labels, axis text, short legends, and essential annotations. Review-only language should be absent from the final figures.

The final visual guard should fail on any of the following conditions.

- PDF fonts are not Helvetica or an approved Helvetica-compatible embedded font.
- SVG/PDF text includes `Purpose`, `Reader readout`, `Stage 10`, internal stage identifiers, or footnote-like review labels.
- Any panel annotation overlaps plotted data, legends, axes, or panel edges.
- Any non-intentional content touches the outer figure edge.
- Any panel repeats a template-like composition without a data-driven reason.
- Any panel title becomes a conceptual slogan rather than a concrete readout description.

## Production Interpretation

The scientific figure narrative is in the right order, but the current render layer is still explanatory rather than publication-native. The next step is not to redesign the manuscript logic. It is to produce a minimalist final render pass that preserves the six-figure structure while removing review scaffolding and enforcing final typography.

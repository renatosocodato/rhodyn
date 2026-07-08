# Stage 10.13 rendered method figures

Stage 10.13 renders the method-first figure architecture from the Stage 10.5 panel crosswalk into a separate Stage 10 output package. The historical Stage 9 rendered mockups remain unchanged.

## Status

`pass`

## Rendered package

- Manifest. `case_studies/stage10_rendered_figures/stage10_13_figures.manifest.yaml`
- Rendered files. `18`
- Figures. `6`
- Planned panels. `30`
- PanelForge. `v3.14.1` with DOI `10.5281/zenodo.20811171`

## Biological and manuscript boundary

This step improves visual readiness for the Nature Methods method-first package. It does not add a new biological dataset, alter benchmark decisions, change the manuscript claims, overwrite the Stage 9 figure renders, or send editor contact.

## Outputs

- `case_studies/stage10_rendered_figures/stage10_13_figures.manifest.yaml`
- `case_studies/stage10_rendered_figures/rendered`
- `case_studies/stage10_rendered_figures/stage10_13_render_inventory.tsv`
- `case_studies/stage10_rendered_figures/stage10_13_panel_coverage.tsv`
- `case_studies/stage10_rendered_figures/stage10_13_render_report.md`
- `case_studies/stage10_rendered_figures/stage10_13_gate_report.json`
- `docs/stage10_13_rendered_method_figures.md`

## Command log

```text
$ $TMPDIR/panelforge-temp validate $RHO_DYN_ROOT/case_studies/stage10_rendered_figures/stage10_13_figures.manifest.yaml
✓ manifest is valid
$ $TMPDIR/panelforge-temp render $RHO_DYN_ROOT/case_studies/stage10_rendered_figures/stage10_13_figures.manifest.yaml
rendered 18 output files
  case_studies/stage10_rendered_figures/rendered/FIG-001/FIG-001.pdf
  case_studies/stage10_rendered_figures/rendered/FIG-001/FIG-001.png
  case_studies/stage10_rendered_figures/rendered/FIG-001/FIG-001.svg
  case_studies/stage10_rendered_figures/rendered/FIG-002/FIG-002.pdf
  case_studies/stage10_rendered_figures/rendered/FIG-002/FIG-002.png
  case_studies/stage10_rendered_figures/rendered/FIG-002/FIG-002.svg
  case_studies/stage10_rendered_figures/rendered/FIG-003/FIG-003.pdf
  case_studies/stage10_rendered_figures/rendered/FIG-003/FIG-003.png
  case_studies/stage10_rendered_figures/rendered/FIG-003/FIG-003.svg
  case_studies/stage10_rendered_figures/rendered/FIG-004/FIG-004.pdf
  case_studies/stage10_rendered_figures/rendered/FIG-004/FIG-004.png
  case_studies/stage10_rendered_figures/rendered/FIG-004/FIG-004.svg
  case_studies/stage10_rendered_figures/rendered/FIG-005/FIG-005.pdf
  case_studies/stage10_rendered_figures/rendered/FIG-005/FIG-005.png
  case_studies/stage10_rendered_figures/rendered/FIG-005/FIG-005.svg
  case_studies/stage10_rendered_figures/rendered/FIG-006/FIG-006.pdf
  case_studies/stage10_rendered_figures/rendered/FIG-006/FIG-006.png
  case_studies/stage10_rendered_figures/rendered/FIG-006/FIG-006.svg
INFO fontTools.subset: maxp pruned
INFO fontTools.subset: cmap pruned
WARNING fontTools.ttLib.tables._p_o_s_t: 1 extra bytes in post.stringData array
INFO fontTools.subset: kern pruned
INFO fontTools.subset: post pruned
INFO fontTools.subset: Zapf dropped
INFO fontTools.subset: feat dropped
INFO fontTools.subset: meta dropped
INFO fontTools.subset: morx dropped
WARNING fontTools.ttLib.tables._h_e_a_d: 'created' timestamp seems very low; regarding as unix timestamp
INFO fontTools.subset: glyf pruned
INFO fontTools.subset: Added gid0 to subset
INFO fontTools.subset: Added first four glyphs to subset
INFO fontTools.subset: Closing glyph list over 'glyf': 39 glyphs before
INFO fontTools.subset: Glyph names: ['.notdef', '.null', 'B', 'D', 'I', 'R', 'a', 'b', 'bullet', 'c', 'comma', 'd', 'e', 'f', 'g', 'h', 'hyphen', 'i', 'j', 'l', 'm', 'n', 'nonmarkingreturn', 'o', 'one', 'p', 'period', 'q', 'r', 's', 'space', 't', 'u', 'v', 'w', 'x', 'y', 'z', 'zero']
INFO fontTools.subset: Glyph IDs:   [0, 1, 2, 3, 15, 16, 17, 19, 20, 37, 39, 44, 53, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 135]
INFO fontTools.subset: Closed glyph list over 'glyf': 39 glyphs after
INFO fontTools.subset: Glyph names: ['.notdef', '.null', 'B', 'D', 'I', 'R', 'a', 'b', 'bullet', 'c', 'comma', 'd', 'e', 'f', 'g', 'h', 'hyphen', 'i', 'j', 'l', 'm', 'n', 'nonmarkingreturn', 'o', 'one', 'p', 'period', 'q', 'r', 's', 'space', 't', 'u', 'v', 'w', 'x', 'y', 'z', 'zero']
INFO fontTools.subset: Glyph IDs:   [0, 1, 2, 3, 15, 16, 17, 19, 20, 37, 39, 44, 53, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 135]
INFO fontTools.subset: Retaining 39 glyphs
INFO fontTools.subset: head subsetting not needed
INFO fontTools.subset: hhea subsetting not needed
INFO fontTools.subset: maxp subsetting not needed
INFO fontTools.subset: OS/2 subsetting not needed
INFO fontTools.subset: hmtx subsetted
INFO fontTools.subset: hdmx subsetted
INFO fontTools.subset: cmap subsetted
INFO fontTools.subset: fpgm subsetting not needed
INFO fontTools.subset: prep subsetting not needed
INFO fontTools.subset: cvt  subsetting not needed
INFO fontTools.subset: loca subsetting not needed
INFO fontTools.subset: kern subsetted
INFO fontTools.subset: post subsetted
INFO fontTools.subset: prop subsetted
INFO fontTools.subset: name subsetting not needed
INFO fontTools.subset: glyf subsetted
INFO fontTools.subset: head pruned
INFO fontTools.subset: OS/2 Unicode ranges pruned: [0, 31]
INFO fontTools.subset: OS/2 CodePage ranges pruned: [0]
INFO fontTools.subset: glyf pruned
INFO fontTools.subset: name pruned
INFO fontTools.subset: maxp pruned
INFO fontTools.subset: cmap pruned
WARNING fontTools.ttLib.tables._p_o_s_t: 1 extra bytes in post.stringData array
INFO fontTools.subset: kern pruned
INFO fontTools.subset: post pruned
INFO fontTools.subset: Zapf dropped
INFO fontTools.subset: feat dropped
INFO fontTools.subset: meta dropped
INFO fontTools.subset: morx dropped
WARNING fontTools.ttLib.tables._h_e_a_d: 'created' timestamp seems very low; regarding as unix timestamp
INFO fontTools.subset: glyf pruned
INFO fontTools.subset: Added gid0 to subset
INFO fontTools.subset: Added first four glyphs to subset
INFO fontTools.subset: Closing glyph list over 'glyf': 6 glyphs before
INFO fontTools.subset: Glyph names: ['.notdef', '.null', 'fi', 'fl', 'nonmarkingreturn', 'space']
INFO fontTools.subset: Glyph IDs:   [0, 1, 2, 3, 192, 193]
INFO fontTools.subset: Closed glyph list over 'glyf': 6 glyphs after
INFO fontTools.subset: Glyph names: ['.notdef', '.null', 'fi', 'fl', 'nonmarkingreturn', 'space']
INFO fontTools.subset: Glyph IDs:   [0, 1, 2, 3, 192, 193]
INFO fontTools.subset: Retaining 6 glyphs
INFO fontTools.subset: head subsetting not needed
INFO fontTools.subset: hhea subsetting not needed
INFO fontTools.subset: maxp subsetting not needed
INFO fontTools.subset: OS/2 subsetting not needed
INFO fontTools.subset: hmtx subsetted
INFO fontTools.subset: hdmx subsetted
INFO fontTools.subset: cmap subsetted
INFO fontTools.subset: fpgm subsetting not needed
INFO fontTools.subset: prep subsetting not needed
INFO fontTools.subset: cvt  subsetting not needed
INFO fontTools.subset: loca subsetting not needed
INFO fontTools.subset: kern subsetted to empty; dropped
INFO fontTools.subset: post subsetted
INFO fontTools.subset: prop subsetted
INFO fontTools.subset: name subsetting not needed
INFO fontTools.subset: glyf subsetted
INFO fontTools.subset: head pruned
INFO fontTools.subset: OS/2 Unicode ranges pruned: [62]
INFO fontTools.subset: OS/2 CodePage ranges pruned: [0]
INFO fontTools.subset: glyf pruned
INFO fontTools.subset: name pruned
INFO fontTools.subset: maxp pruned
INFO fontTools.subset: cmap pruned
WARNING fontTools.ttLib.tables._p_o_s_t: 1 extra bytes in post.stringData array
INFO fontTools.subset: kern pruned
INFO fontTools.subset: post pruned
INFO fontTools.subset: Zapf dropped
INFO fontTools.subset: feat dropped
INFO fontTools.subset: meta dropped
INFO fontTools.subset: morx dropped
INFO fontTools.subset: glyf pruned
INFO fontTools.subset: Added gid0 to subset
INFO fontTools.subset: Added first four glyphs to subset
INFO fontTools.subset: Closing glyph list over 'glyf': 43 glyphs before
INFO fontTools.subset: Glyph names: ['.notdef', '.null', 'A', 'B', 'C', 'D', 'E', 'I', 'N', 'R', 'Y', 'a', 'asciitilde', 'b', 'c', 'comma', 'd', 'e', 'f', 'g', 'h', 'hyphen', 'i', 'j', 'l', 'm', 'n', 'nonmarkingreturn', 'o', 'one', 'p', 'periodcentered', 'q', 'r', 's', 'space', 't', 'three', 'u', 'v', 'x', 'y', 'z']
INFO fontTools.subset: Glyph IDs:   [0, 1, 2, 3, 15, 16, 20, 22, 36, 37, 38, 39, 40, 44, 49, 53, 60, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 91, 92, 93, 97, 195]
INFO fontTools.subset: Closed glyph list over 'glyf': 43 glyphs after
INFO fontTools.subset: Glyph names: ['.notdef', '.null', 'A', 'B', 'C', 'D', 'E', 'I', 'N', 'R', 'Y', 'a', 'asciitilde', 'b', 'c', 'comma', 'd', 'e', 'f', 'g', 'h', 'hyphen', 'i', 'j', 'l', 'm', 'n', 'nonmarkingreturn', 'o', 'one', 'p', 'periodcentered', 'q', 'r', 's', 'space', 't', 'three', 'u', 'v', 'x', 'y', 'z']
INFO fontTools.subset: Glyph IDs:   [0, 1, 2, 3, 15, 16, 20, 22, 36, 37, 38, 39, 40, 44, 49, 53, 60, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 91, 92, 93, 97, 195]
INFO fontTools.subset: Retaining 43 glyphs
INFO fontTools.subset: head subsetting not needed
INFO fontTools.subset: hhea subsetting not needed
INFO fontTools.subset: maxp subsetting not needed
INFO fontTools.subset: OS/2 subsetting not needed
INFO fontTools.subset: hmtx subsetted
INFO fontTools.subset: cmap subsetted
INFO fontTools.subset: fpgm subsetting not needed
INFO fontTools.subset: prep subsetting not needed
INFO fontTools.subset: cvt  subsetting not needed
INFO fontTools.subset: loca subsetting not needed
INFO fontTools.subset: kern subsetted
INFO fontTools.subset: post subsetted
INFO fontTools.subset: prop subsetted
INFO fontTools.subset: name subsetting not needed
INFO fontTools.subset: glyf subsetted
INFO fontTools.subset: head pruned
INFO fontTools.subset: OS/2 Unicode ranges pruned: [0, 1]
INFO fontTools.subset: OS/2 CodePage ranges pruned: [0]
INFO fontTools.subset: glyf pruned
INFO fontTools.subset: name pruned
INFO fontTools.subset: maxp pruned
INFO fontTools.subset: cmap pruned
WARNING fontTools.ttLib.tables._p_o_s_t: 1 extra bytes in post.stringData array
INFO fontTools.subset: kern pruned
INFO fontTools.subset: post pruned
INFO fontTools.subset: Zapf dropped
INFO fontTools.subset: feat dropped
INFO fontTools.subset: meta dropped
INFO fontTools.subset: morx dropped
INFO fontTools.subset: glyf pruned
INFO fontTools.subset: Added gid0 to subset
INFO fontTools.subset: Added first four glyphs to subset
INFO fontTools.subset: Closing glyph list over 'glyf': 5 glyphs before
INFO fontTools.subset: Glyph names: ['.notdef', '.null', 'fi', 'nonmarkingreturn', 'space']
INFO fontTools.subset: Glyph IDs:   [0, 1, 2, 3, 192]
INFO fontTools.subset: Closed glyph list over 'glyf': 5 glyphs after
INFO fontTools.subset: Glyph names: ['.notdef', '.null', 'fi', 'nonmarkingreturn', 'space']
INFO fontTools.subset: Glyph IDs:   [0, 1, 2, 3, 192]
INFO fontTools.subset: Retaining 5 glyphs
INFO fontTools.subset: head subsetting not needed
INFO fontTools.subset: hhea subsetting not needed
INFO fontTools.subset: maxp subsetting not needed
INFO fontTools.subset: OS/2 subsetting not needed
INFO fontTools.subset: hmtx subsetted
INFO fontTools.subset: cmap subsetted
INFO fontTools.subset: fpgm subsetting not needed
INFO fontTools.subset: prep subsetting not needed
INFO fontTools.subset: cvt  subsetting not needed
INFO fontTools.subset: loca subsetting not needed
INFO fontTools.subset: kern subsetted to empty; dropped
INFO fontTools.subset: post subsetted
INFO fontTools.subset: prop subsetted
INFO fontTools.subset: name subsetting not needed
INFO fontTools.subset: glyf subsetted
INFO fontTools.subset: head pruned
INFO fontTools.subset: OS/2 Unicode ranges pruned: [62]
INFO fontTools.subset: OS/2 CodePage ranges pruned: [0]
INFO fontTools.subset: glyf pruned
INFO fontTools.subset: name pruned
INFO fontTools.subset: maxp pruned
INFO fontTools.subset: cmap pruned
WARNING fontTools.ttLib.tables._p_o_s_t: 1 extra bytes in post.stringData array
INFO fontTools.subset: kern pruned
INFO fontTools.subset: post pruned
INFO fontTools.subset: Zapf dropped
INFO fontTools.subset: feat dropped
INFO fontTools.subset: meta dropped
INFO fontTools.subset: morx dropped
WARNING fontTools.ttLib.tables._h_e_a_d: 'created' timestamp seems very low; regarding as unix timestamp
INFO fontTools.subset: glyf pruned
INFO fontTools.subset: Added gid0 to subset
INFO fontTools.subset: Added first four glyphs to subset
INFO fontTools.subset: Closing glyph list over 'glyf': 22 glyphs before
INFO fontTools.subset: Glyph names: ['.notdef', '.null', 'N', 'Y', 'a', 'asciitilde', 'c', 'e', 'equal', 'i', 'l', 'nonmarkingreturn', 'o', 'p', 'periodcentered', 'q', 'r', 's', 'space', 't', 'u', 'v']
INFO fontTools.subset: Glyph IDs:   [0, 1, 2, 3, 32, 49, 60, 68, 70, 72, 76, 79, 82, 83, 84, 85, 86, 87, 88, 89, 97, 195]
INFO fontTools.subset: Closed glyph list over 'glyf': 22 glyphs after
INFO fontTools.subset: Glyph names: ['.notdef', '.null', 'N', 'Y', 'a', 'asciitilde', 'c', 'e', 'equal', 'i', 'l', 'nonmarkingreturn', 'o', 'p', 'periodcentered', 'q', 'r', 's', 'space', 't', 'u', 'v']
INFO fontTools.subset: Glyph IDs:   [0, 1, 2, 3, 32, 49, 60, 68, 70, 72, 76, 79, 82, 83, 84, 85, 86, 87, 88, 89, 97, 195]
INFO fontTools.subset: Retaining 22 glyphs
INFO fontTools.subset: head subsetting not needed
INFO fontTools.subset: hhea subsetting not needed
INFO fontTools.subset: maxp subsetting not needed
INFO fontTools.subset: OS/2 subsetting not needed
INFO fontTools.subset: hmtx subsetted
INFO fontTools.subset: hdmx subsetted
INFO fontTools.subset: cmap subsetted
INFO fontTools.subset: fpgm subsetting not needed
INFO fontTools.subset: prep subsetting not needed
INFO fontTools.subset: cvt  subsetting not needed
INFO fontTools.subset: loca subsetting not needed
INFO fontTools.subset: kern subsetted
INFO fontTools.subset: post subsetted
INFO fontTools.subset: prop subsetted
INFO fontTools.subset: name subsetting not needed
INFO fontTools.subset: glyf subsetted
INFO fontTools.subset: head pruned
INFO fontTools.subset: OS/2 Unicode ranges pruned: [0, 1]
INFO fontTools.subset: OS/2 CodePage ranges pruned: [0]
INFO fontTools.subset: glyf pruned
INFO fontTools.subset: name pruned
INFO fontTools.subset: maxp pruned
INFO fontTools.subset: cmap pruned
WARNING fontTools.ttLib.tables._p_o_s_t: 1 extra bytes in post.stringData array
INFO fontTools.subset: kern pruned
INFO fontTools.subset: post pruned
INFO fontTools.subset: Zapf dropped
INFO fontTools.subset: feat dropped
INFO fontTools.subset: meta dropped
INFO fontTools.subset: morx dropped
WARNING fontTools.ttLib.tables._h_e_a_d: 'created' timestamp seems very low; regarding as unix timestamp
INFO fontTools.subset: glyf pruned
INFO fontTools.subset: Added gid0 to subset
INFO fontTools.subset: Added first four glyphs to subset
INFO fontTools.subset: Closing glyph list over 'glyf': 49 glyphs before
INFO fontTools.subset: Glyph names: ['.notdef', '.null', 'A', 'B', 'C', 'D', 'Deltagreek', 'I', 'N', 'R', 'a', 'b', 'bullet', 'c', 'd', 'e', 'eight', 'equal', 'f', 'four', 'g', 'h', 'hyphen', 'i', 'j', 'k', 'l', 'm', 'n', 'nine', 'nonmarkingreturn', 'o', 'one', 'p', 'period', 'r', 's', 'seven', 'space', 't', 'three', 'two', 'u', 'v', 'w', 'x', 'y', 'z', 'zero']
INFO fontTools.subset: Glyph IDs:   [0, 1, 2, 3, 16, 17, 19, 20, 21, 22, 23, 26, 27, 28, 32, 36, 37, 38, 39, 44, 49, 53, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 85, 86, 87, 88, 89, 90, 91, 92, 93, 135, 1091]
INFO fontTools.subset: Closed glyph list over 'glyf': 49 glyphs after
INFO fontTools.subset: Glyph names: ['.notdef', '.null', 'A', 'B', 'C', 'D', 'Deltagreek', 'I', 'N', 'R', 'a', 'b', 'bullet', 'c', 'd', 'e', 'eight', 'equal', 'f', 'four', 'g', 'h', 'hyphen', 'i', 'j', 'k', 'l', 'm', 'n', 'nine', 'nonmarkingreturn', 'o', 'one', 'p', 'period', 'r', 's', 'seven', 'space', 't', 'three', 'two', 'u', 'v', 'w', 'x', 'y', 'z', 'zero']
INFO fontTools.subset: Glyph IDs:   [0, 1, 2, 3, 16, 17, 19, 20, 21, 22, 23, 26, 27, 28, 32, 36, 37, 38, 39, 44, 49, 53, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 85, 86, 87, 88, 89, 90, 91, 92, 93, 135, 1091]
INFO fontTools.subset: Retaining 49 glyphs
INFO fontTools.subset: head subsetting not needed
INFO fontTools.subset: hhea subsetting not needed
INFO fontTools.subset: maxp subsetting not needed
INFO fontTools.subset: OS/2 subsetting not needed
INFO fontTools.subset: hmtx subsetted
INFO fontTools.subset: hdmx subsetted
INFO fontTools.subset: cmap subsetted
INFO fontTools.subset: fpgm subsetting not needed
INFO fontTools.subset: prep subsetting not needed
INFO fontTools.subset: cvt  subsetting not needed
INFO fontTools.subset: loca subsetting not needed
INFO fontTools.subset: kern subsetted
INFO fontTools.subset: post subsetted
INFO fontTools.subset: prop subsetted
INFO fontTools.subset: name subsetting not needed
INFO fontTools.subset: glyf subsetted
INFO fontTools.subset: head pruned
INFO fontTools.subset: OS/2 Unicode ranges pruned: [0, 7, 31]
INFO fontTools.subset: OS/2 CodePage ranges pruned: [0]
INFO fontTools.subset: glyf pruned
INFO fontTools.subset: name pruned
INFO fontTools.subset: maxp pruned
INFO fontTools.subset: cmap pruned
WARNING fontTools.ttLib.tables._p_o_s_t: 1 extra bytes in post.stringData array
INFO fontTools.subset: kern pruned
INFO fontTools.subset: post pruned
INFO fontTools.subset: Zapf dropped
INFO fontTools.subset: feat dropped
INFO fontTools.subset: meta dropped
INFO fontTools.subset: morx dropped
WARNING fontTools.ttLib.tables._h_e_a_d: 'created' timestamp seems very low; regarding as unix timestamp
INFO fontTools.subset: glyf pruned
INFO fontTools.subset: Added gid0 to subset
INFO fontTools.subset: Added first four glyphs to subset
INFO fontTools.subset: Closing glyph list over 'glyf': 5 glyphs before
INFO fontTools.subset: Glyph names: ['.notdef', '.null', 'fi', 'nonmarkingreturn', 'space']
INFO fontTools.subset: Glyph IDs:   [0, 1, 2, 3, 192]
INFO fontTools.subset: Closed glyph list over 'glyf': 5 glyphs after
INFO fontTools.subset: Glyph names: ['.notdef', '.null', 'fi', 'nonmarkingreturn', 'space']
INFO fontTools.subset: Glyph IDs:   [0, 1, 2, 3, 192]
INFO fontTools.subset: Retaining 5 glyphs
INFO fontTools.subset: head subsetting not needed
INFO fontTools.subset: hhea subsetting not needed
INFO fontTools.subset: maxp subsetting not needed
INFO fontTools.subset: OS/2 subsetting not needed
INFO fontTools.subset: hmtx subsetted
INFO fontTools.subset: hdmx subsetted
INFO fontTools.subset: cmap subsetted
INFO fontTools.subset: fpgm subsetting not needed
INFO fontTools.subset: prep subsetting not needed
INFO fontTools.subset: cvt  subsetting not needed
INFO fontTools.subset: loca subsetting not needed
INFO fontTools.subset: kern subsetted to empty; dropped
INFO fontTools.subset: post subsetted
INFO fontTools.subset: prop subsetted
INFO fontTools.subset: name subsetting not needed
INFO fontTools.subset: glyf subsetted
INFO fontTools.subset: head pruned
INFO fontTools.subset: OS/2 Unicode ranges pruned: [62]
INFO fontTools.subset: OS/2 CodePage ranges pruned: [0]
INFO fontTools.subset: glyf pruned
INFO fontTools.subset: name pruned
INFO fontTools.subset: maxp pruned
INFO fontTools.subset: cmap pruned
WARNING fontTools.ttLib.tables._p_o_s_t: 1 extra bytes in post.stringData array
INFO fontTools.subset: kern pruned
INFO fontTools.subset: post pruned
INFO fontTools.subset: Zapf dropped
INFO fontTools.subset: feat dropped
INFO fontTools.subset: meta dropped
INFO fontTools.subset: morx dropped
INFO fontTools.subset: glyf pruned
INFO fontTools.subset: Added gid0 to subset
INFO fontTools.subset: Added first four glyphs to subset
INFO fontTools.subset: Closing glyph list over 'glyf': 51 glyphs before
INFO fontTools.subset: Glyph names: ['.notdef', '.null', 'A', 'B', 'C', 'D', 'Deltagreek', 'E', 'I', 'K', 'N', 'P', 'R', 'Y', 'a', 'asciitilde', 'b', 'c', 'comma', 'd', 'e', 'equal', 'f', 'five', 'four', 'g', 'h', 'hyphen', 'i', 'k', 'l', 'm', 'n', 'nonmarkingreturn', 'o', 'one', 'p', 'period', 'periodcentered', 'q', 'r', 's', 'space', 't', 'three', 'two', 'u', 'v', 'w', 'y', 'zero']
INFO fontTools.subset: Glyph IDs:   [0, 1, 2, 3, 15, 16, 17, 19, 20, 21, 22, 23, 24, 32, 36, 37, 38, 39, 40, 44, 46, 49, 51, 53, 60, 68, 69, 70, 71, 72, 73, 74, 75, 76, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 92, 97, 195, 1091]
INFO fontTools.subset: Closed glyph list over 'glyf': 51 glyphs after
INFO fontTools.subset: Glyph names: ['.notdef', '.null', 'A', 'B', 'C', 'D', 'Deltagreek', 'E', 'I', 'K', 'N', 'P', 'R', 'Y', 'a', 'asciitilde', 'b', 'c', 'comma', 'd', 'e', 'equal', 'f', 'five', 'four', 'g', 'h', 'hyphen', 'i', 'k', 'l', 'm', 'n', 'nonmarkingreturn', 'o', 'one', 'p', 'period', 'periodcentered', 'q', 'r', 's', 'space', 't', 'three', 'two', 'u', 'v', 'w', 'y', 'zero']
INFO fontTools.subset: Glyph IDs:   [0, 1, 2, 3, 15, 16, 17, 19, 20, 21, 22, 23, 24, 32, 36, 37, 38, 39, 40, 44, 46, 49, 51, 53, 60, 68, 69, 70, 71, 72, 73, 74, 75, 76, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 92, 97, 195, 1091]
INFO fontTools.subset: Retaining 51 glyphs
INFO fontTools.subset: head subsetting not needed
INFO fontTools.subset: hhea subsetting not needed
INFO fontTools.subset: maxp subsetting not needed
INFO fontTools.subset: OS/2 subsetting not needed
INFO fontTools.subset: hmtx subsetted
INFO fontTools.subset: cmap subsetted
INFO fontTools.subset: fpgm subsetting not needed
INFO fontTools.subset: prep subsetting not needed
INFO fontTools.subset: cvt  subsetting not needed
INFO fontTools.subset: loca subsetting not needed
INFO fontTools.subset: kern subsetted
INFO fontTools.subset: post subsetted
INFO fontTools.subset: prop subsetted
INFO fontTools.subset: name subsetting not needed
INFO fontTools.subset: glyf subsetted
INFO fontTools.subset: head pruned
INFO fontTools.subset: OS/2 Unicode ranges pruned: [0, 1, 7]
INFO fontTools.subset: OS/2 CodePage ranges pruned: [0]
INFO fontTools.subset: glyf pruned
INFO fontTools.subset: name pruned
INFO fontTools.subset: maxp pruned
INFO fontTools.subset: cmap pruned
WARNING fontTools.ttLib.tables._p_o_s_t: 1 extra bytes in post.stringData array
INFO fontTools.subset: kern pruned
INFO fontTools.subset: post pruned
INFO fontTools.subset: Zapf dropped
INFO fontTools.subset: feat dropped
INFO fontTools.subset: meta dropped
INFO fontTools.subset: morx dropped
INFO fontTools.subset: glyf pruned
INFO fontTools.subset: Added gid0 to subset
INFO fontTools.subset: Added first four glyphs to subset
INFO fontTools.subset: Closing glyph list over 'glyf': 5 glyphs before
INFO fontTools.subset: Glyph names: ['.notdef', '.null', 'fi', 'nonmarkingreturn', 'space']
INFO fontTools.subset: Glyph IDs:   [0, 1, 2, 3, 192]
INFO fontTools.subset: Closed glyph list over 'glyf': 5 glyphs after
INFO fontTools.subset: Glyph names: ['.notdef', '.null', 'fi', 'nonmarkingreturn', 'space']
INFO fontTools.subset: Glyph IDs:   [0, 1, 2, 3, 192]
INFO fontTools.subset: Retaining 5 glyphs
INFO fontTools.subset: head subsetting not needed
INFO fontTools.subset: hhea subsetting not needed
INFO fontTools.subset: maxp subsetting not needed
INFO fontTools.subset: OS/2 subsetting not needed
INFO fontTools.subset: hmtx subsetted
INFO fontTools.subset: cmap subsetted
INFO fontTools.subset: fpgm subsetting not needed
INFO fontTools.subset: prep subsetting not needed
INFO fontTools.subset: cvt  subsetting not needed
INFO fontTools.subset: loca subsetting not needed
INFO fontTools.subset: kern subsetted to empty; dropped
INFO fontTools.subset: post subsetted
INFO fontTools.subset: prop subsetted
INFO fontTools.subset: name subsetting not needed
INFO fontTools.subset: glyf subsetted
INFO fontTools.subset: head pruned
INFO fontTools.subset: OS/2 Unicode ranges pruned: [62]
INFO fontTools.subset: OS/2 CodePage ranges pruned: [0]
INFO fontTools.subset: glyf pruned
INFO fontTools.subset: name pruned
INFO fontTools.subset: maxp pruned
INFO fontTools.subset: cmap pruned
WARNING fontTools.ttLib.tables._p_o_s_t: 1 extra bytes in post.stringData array
INFO fontTools.subset: kern pruned
INFO fontTools.subset: post pruned
INFO fontTools.subset: Zapf dropped
INFO fontTools.subset: feat dropped
INFO fontTools.subset: meta dropped
INFO fontTools.subset: morx dropped
WARNING fontTools.ttLib.tables._h_e_a_d: 'created' timestamp seems very low; regarding as unix timestamp
INFO fontTools.subset: glyf pruned
INFO fontTools.subset: Added gid0 to subset
INFO fontTools.subset: Added first four glyphs to subset
INFO fontTools.subset: Closing glyph list over 'glyf': 22 glyphs before
INFO fontTools.subset: Glyph names: ['.notdef', '.null', 'N', 'Y', 'a', 'asciitilde', 'c', 'e', 'equal', 'i', 'l', 'nonmarkingreturn', 'o', 'p', 'periodcentered', 'q', 'r', 's', 'space', 't', 'u', 'v']
INFO fontTools.subset: Glyph IDs:   [0, 1, 2, 3, 32, 49, 60, 68, 70, 72, 76, 79, 82, 83, 84, 85, 86, 87, 88, 89, 97, 195]
INFO fontTools.subset: Closed glyph list over 'glyf': 22 glyphs after
INFO fontTools.subset: Glyph names: ['.notdef', '.null', 'N', 'Y', 'a', 'asciitilde', 'c', 'e', 'equal', 'i', 'l', 'nonmarkingreturn', 'o', 'p', 'periodcentered', 'q', 'r', 's', 'space', 't', 'u', 'v']
INFO fontTools.subset: Glyph IDs:   [0, 1, 2, 3, 32, 49, 60, 68, 70, 72, 76, 79, 82, 83, 84, 85, 86, 87, 88, 89, 97, 195]
INFO fontTools.subset: Retaining 22 glyphs
INFO fontTools.subset: head subsetting not needed
INFO fontTools.subset: hhea subsetting not needed
INFO fontTools.subset: maxp subsetting not needed
INFO fontTools.subset: OS/2 subsetting not needed
INFO fontTools.subset: hmtx subsetted
INFO fontTools.subset: hdmx subsetted
INFO fontTools.subset: cmap subsetted
INFO fontTools.subset: fpgm subsetting not needed
INFO fontTools.subset: prep subsetting not needed
INFO fontTools.subset: cvt  subsetting not needed
INFO fontTools.subset: loca subsetting not needed
INFO fontTools.subset: kern subsetted
INFO fontTools.subset: post subsetted
INFO fontTools.subset: prop subsetted
INFO fontTools.subset: name subsetting not needed
INFO fontTools.subset: glyf subsetted
INFO fontTools.subset: head pruned
INFO fontTools.subset: OS/2 Unicode ranges pruned: [0, 1]
INFO fontTools.subset: OS/2 CodePage ranges pruned: [0]
INFO fontTools.subset: glyf pruned
INFO fontTools.subset: name pruned
INFO fontTools.subset: maxp pruned
INFO fontTools.subset: cmap pruned
WARNING fontTools.ttLib.tables._p_o_s_t: 1 extra bytes in post.stringData array
INFO fontTools.subset: kern pruned
INFO fontTools.subset: post pruned
INFO fontTools.subset: Zapf dropped
INFO fontTools.subset: feat dropped
INFO fontTools.subset: meta dropped
INFO fontTools.subset: morx dropped
WARNING fontTools.ttLib.tables._h_e_a_d: 'created' timestamp seems very low; regarding as unix timestamp
INFO fontTools.subset: glyf pruned
INFO fontTools.subset: Added gid0 to subset
INFO fontTools.subset: Added first four glyphs to subset
INFO fontTools.subset: Closing glyph list over 'glyf': 44 glyphs before
INFO fontTools.subset: Glyph names: ['.notdef', '.null', 'S', 'T', 'a', 'b', 'c', 'comma', 'd', 'e', 'eight', 'equal', 'f', 'five', 'four', 'g', 'h', 'i', 'l', 'm', 'n', 'nine', 'nonmarkingreturn', 'o', 'one', 'p', 'parenleft', 'parenright', 'percent', 'period', 'r', 's', 'seven', 'six', 'space', 't', 'three', 'two', 'u', 'v', 'w', 'x', 'z', 'zero']
INFO fontTools.subset: Glyph IDs:   [0, 1, 2, 3, 8, 11, 12, 15, 17, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 32, 54, 55, 68, 69, 70, 71, 72, 73, 74, 75, 76, 79, 80, 81, 82, 83, 85, 86, 87, 88, 89, 90, 91, 93]
INFO fontTools.subset: Closed glyph list over 'glyf': 44 glyphs after
INFO fontTools.subset: Glyph names: ['.notdef', '.null', 'S', 'T', 'a', 'b', 'c', 'comma', 'd', 'e', 'eight', 'equal', 'f', 'five', 'four', 'g', 'h', 'i', 'l', 'm', 'n', 'nine', 'nonmarkingreturn', 'o', 'one', 'p', 'parenleft', 'parenright', 'percent', 'period', 'r', 's', 'seven', 'six', 'space', 't', 'three', 'two', 'u', 'v', 'w', 'x', 'z', 'zero']
INFO fontTools.subset: Glyph IDs:   [0, 1, 2, 3, 8, 11, 12, 15, 17, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 32, 54, 55, 68, 69, 70, 71, 72, 73, 74, 75, 76, 79, 80, 81, 82, 83, 85, 86, 87, 88, 89, 90, 91, 93]
INFO fontTools.subset: Retaining 44 glyphs
INFO fontTools.subset: head subsetting not needed
INFO fontTools.subset: hhea subsetting not needed
INFO fontTools.subset: maxp subsetting not needed
INFO fontTools.subset: OS/2 subsetting not needed
INFO fontTools.subset: hmtx subsetted
INFO fontTools.subset: hdmx subsetted
INFO fontTools.subset: cmap subsetted
INFO fontTools.subset: fpgm subsetting not needed
INFO fontTools.subset: prep subsetting not needed
INFO fontTools.subset: cvt  subsetting not needed
INFO fontTools.subset: loca subsetting not needed
INFO fontTools.subset: kern subsetted
INFO fontTools.subset: post subsetted
INFO fontTools.subset: prop subsetted
INFO fontTools.subset: name subsetting not needed
INFO fontTools.subset: glyf subsetted
INFO fontTools.subset: head pruned
INFO fontTools.subset: OS/2 Unicode ranges pruned: [0]
INFO fontTools.subset: OS/2 CodePage ranges pruned: [0]
INFO fontTools.subset: glyf pruned
INFO fontTools.subset: name pruned
INFO fontTools.subset: maxp pruned
INFO fontTools.subset: cmap pruned
WARNING fontTools.ttLib.tables._p_o_s_t: 1 extra bytes in post.stringData array
INFO fontTools.subset: kern pruned
INFO fontTools.subset: post pruned
INFO fontTools.subset: Zapf dropped
INFO fontTools.subset: feat dropped
INFO fontTools.subset: meta dropped
INFO fontTools.subset: morx dropped
WARNING fontTools.ttLib.tables._h_e_a_d: 'created' timestamp seems very low; regarding as unix timestamp
INFO fontTools.subset: glyf pruned
INFO fontTools.subset: Added gid0 to subset
INFO fontTools.subset: Added first four glyphs to subset
INFO fontTools.subset: Closing glyph list over 'glyf': 5 glyphs before
INFO fontTools.subset: Glyph names: ['.notdef', '.null', 'fi', 'nonmarkingreturn', 'space']
INFO fontTools.subset: Glyph IDs:   [0, 1, 2, 3, 192]
INFO fontTools.subset: Closed glyph list over 'glyf': 5 glyphs after
INFO fontTools.subset: Glyph names: ['.notdef', '.null', 'fi', 'nonmarkingreturn', 'space']
INFO fontTools.subset: Glyph IDs:   [0, 1, 2, 3, 192]
INFO fontTools.subset: Retaining 5 glyphs
INFO fontTools.subset: head subsetting not needed
INFO fontTools.subset: hhea subsetting not needed
INFO fontTools.subset: maxp subsetting not needed
INFO fontTools.subset: OS/2 subsetting not needed
INFO fontTools.subset: hmtx subsetted
INFO fontTools.subset: hdmx subsetted
INFO fontTools.subset: cmap subsetted
INFO fontTools.subset: fpgm subsetting not needed
INFO fontTools.subset: prep subsetting not needed
INFO fontTools.subset: cvt  subsetting not needed
INFO fontTools.subset: loca subsetting not needed
INFO fontTools.subset: kern subsetted to empty; dropped
INFO fontTools.subset: post subsetted
INFO fontTools.subset: prop subsetted
INFO fontTools.subset: name subsetting not needed
INFO fontTools.subset: glyf subsetted
INFO fontTools.subset: head pruned
INFO fontTools.subset: OS/2 Unicode ranges pruned: [62]
INFO fontTools.subset: OS/2 CodePage ranges pruned: [0]
INFO fontTools.subset: glyf pruned
INFO fontTools.subset: name pruned
INFO fontTools.subset: maxp pruned
INFO fontTools.subset: cmap pruned
WARNING fontTools.ttLib.tables._p_o_s_t: 1 extra bytes in post.stringData array
INFO fontTools.subset: kern pruned
INFO fontTools.subset: post pruned
INFO fontTools.subset: Zapf dropped
INFO fontTools.subset: feat dropped
INFO fontTools.subset: meta dropped
INFO fontTools.subset: morx dropped
INFO fontTools.subset: glyf pruned
INFO fontTools.subset: Added gid0 to subset
INFO fontTools.subset: Added first four glyphs to subset
INFO fontTools.subset: Closing glyph list over 'glyf': 51 glyphs before
INFO fontTools.subset: Glyph names: ['.notdef', '.null', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'I', 'K', 'L', 'M', 'N', 'P', 'R', 'S', 'T', 'Y', 'a', 'asciitilde', 'b', 'c', 'comma', 'd', 'e', 'emdash', 'f', 'g', 'h', 'hyphen', 'i', 'k', 'l', 'm', 'n', 'nonmarkingreturn', 'o', 'one', 'p', 'periodcentered', 'q', 'r', 's', 'space', 't', 'three', 'u', 'v', 'x', 'y']
INFO fontTools.subset: Glyph IDs:   [0, 1, 2, 3, 15, 16, 20, 22, 36, 37, 38, 39, 40, 41, 42, 44, 46, 47, 48, 49, 51, 53, 54, 55, 60, 68, 69, 70, 71, 72, 73, 74, 75, 76, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 91, 92, 97, 179, 195]
INFO fontTools.subset: Closed glyph list over 'glyf': 51 glyphs after
INFO fontTools.subset: Glyph names: ['.notdef', '.null', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'I', 'K', 'L', 'M', 'N', 'P', 'R', 'S', 'T', 'Y', 'a', 'asciitilde', 'b', 'c', 'comma', 'd', 'e', 'emdash', 'f', 'g', 'h', 'hyphen', 'i', 'k', 'l', 'm', 'n', 'nonmarkingreturn', 'o', 'one', 'p', 'periodcentered', 'q', 'r', 's', 'space', 't', 'three', 'u', 'v', 'x', 'y']
INFO fontTools.subset: Glyph IDs:   [0, 1, 2, 3, 15, 16, 20, 22, 36, 37, 38, 39, 40, 41, 42, 44, 46, 47, 48, 49, 51, 53, 54, 55, 60, 68, 69, 70, 71, 72, 73, 74, 75, 76, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 91, 92, 97, 179, 195]
INFO fontTools.subset: Retaining 51 glyphs
INFO fontTools.subset: head subsetting not needed
INFO fontTools.subset: hhea subsetting not needed
INFO fontTools.subset: maxp subsetting not needed
INFO fontTools.subset: OS/2 subsetting not needed
INFO fontTools.subset: hmtx subsetted
INFO fontTools.subset: cmap subsetted
INFO fontTools.subset: fpgm subsetting not needed
INFO fontTools.subset: prep subsetting not needed
INFO fontTools.subset: cvt  subsetting not needed
INFO fontTools.subset: loca subsetting not needed
INFO fontTools.subset: kern subsetted
INFO fontTools.subset: post subsetted
INFO fontTools.subset: prop subsetted
INFO fontTools.subset: name subsetting not needed
INFO fontTools.subset: glyf subsetted
INFO fontTools.subset: head pruned
INFO fontTools.subset: OS/2 Unicode ranges pruned: [0, 1, 31]
INFO fontTools.subset: OS/2 CodePage ranges pruned: [0]
INFO fontTools.subset: glyf pruned
INFO fontTools.subset: name pruned
INFO fontTools.subset: maxp pruned
INFO fontTools.subset: cmap pruned
WARNING fontTools.ttLib.tables._p_o_s_t: 1 extra bytes in post.stringData array
INFO fontTools.subset: kern pruned
INFO fontTools.subset: post pruned
INFO fontTools.subset: Zapf dropped
INFO fontTools.subset: feat dropped
INFO fontTools.subset: meta dropped
INFO fontTools.subset: morx dropped
INFO fontTools.subset: glyf pruned
INFO fontTools.subset: Added gid0 to subset
INFO fontTools.subset: Added first four glyphs to subset
INFO fontTools.subset: Closing glyph list over 'glyf': 5 glyphs before
INFO fontTools.subset: Glyph names: ['.notdef', '.null', 'fi', 'nonmarkingreturn', 'space']
INFO fontTools.subset: Glyph IDs:   [0, 1, 2, 3, 192]
INFO fontTools.subset: Closed glyph list over 'glyf': 5 glyphs after
INFO fontTools.subset: Glyph names: ['.notdef', '.null', 'fi', 'nonmarkingreturn', 'space']
INFO fontTools.subset: Glyph IDs:   [0, 1, 2, 3, 192]
INFO fontTools.subset: Retaining 5 glyphs
INFO fontTools.subset: head subsetting not needed
INFO fontTools.subset: hhea subsetting not needed
INFO fontTools.subset: maxp subsetting not needed
INFO fontTools.subset: OS/2 subsetting not needed
INFO fontTools.subset: hmtx subsetted
INFO fontTools.subset: cmap subsetted
INFO fontTools.subset: fpgm subsetting not needed
INFO fontTools.subset: prep subsetting not needed
INFO fontTools.subset: cvt  subsetting not needed
INFO fontTools.subset: loca subsetting not needed
INFO fontTools.subset: kern subsetted to empty; dropped
INFO fontTools.subset: post subsetted
INFO fontTools.subset: prop subsetted
INFO fontTools.subset: name subsetting not needed
INFO fontTools.subset: glyf subsetted
INFO fontTools.subset: head pruned
INFO fontTools.subset: OS/2 Unicode ranges pruned: [62]
INFO fontTools.subset: OS/2 CodePage ranges pruned: [0]
INFO fontTools.subset: glyf pruned
INFO fontTools.subset: name pruned
INFO fontTools.subset: maxp pruned
INFO fontTools.subset: cmap pruned
WARNING fontTools.ttLib.tables._p_o_s_t: 1 extra bytes in post.stringData array
INFO fontTools.subset: kern pruned
INFO fontTools.subset: post pruned
INFO fontTools.subset: Zapf dropped
INFO fontTools.subset: feat dropped
INFO fontTools.subset: meta dropped
INFO fontTools.subset: morx dropped
WARNING fontTools.ttLib.tables._h_e_a_d: 'created' timestamp seems very low; regarding as unix timestamp
INFO fontTools.subset: glyf pruned
INFO fontTools.subset: Added gid0 to subset
INFO fontTools.subset: Added first four glyphs to subset
INFO fontTools.subset: Closing glyph list over 'glyf': 22 glyphs before
INFO fontTools.subset: Glyph names: ['.notdef', '.null', 'N', 'Y', 'a', 'asciitilde', 'c', 'e', 'equal', 'i', 'l', 'nonmarkingreturn', 'o', 'p', 'periodcentered', 'q', 'r', 's', 'space', 't', 'u', 'v']
INFO fontTools.subset: Glyph IDs:   [0, 1, 2, 3, 32, 49, 60, 68, 70, 72, 76, 79, 82, 83, 84, 85, 86, 87, 88, 89, 97, 195]
INFO fontTools.subset: Closed glyph list over 'glyf': 22 glyphs after
INFO fontTools.subset: Glyph names: ['.notdef', '.null', 'N', 'Y', 'a', 'asciitilde', 'c', 'e', 'equal', 'i', 'l', 'nonmarkingreturn', 'o', 'p', 'periodcentered', 'q', 'r', 's', 'space', 't', 'u', 'v']
INFO fontTools.subset: Glyph IDs:   [0, 1, 2, 3, 32, 49, 60, 68, 70, 72, 76, 79, 82, 83, 84, 85, 86, 87, 88, 89, 97, 195]
INFO fontTools.subset: Retaining 22 glyphs
INFO fontTools.subset: head subsetting not needed
INFO fontTools.subset: hhea subsetting not needed
INFO fontTools.subset: maxp subsetting not needed
INFO fontTools.subset: OS/2 subsetting not needed
INFO fontTools.subset: hmtx subsetted
INFO fontTools.subset: hdmx subsetted
INFO fontTools.subset: cmap subsetted
INFO fontTools.subset: fpgm subsetting not needed
INFO fontTools.subset: prep subsetting not needed
INFO fontTools.subset: cvt  subsetting not needed
INFO fontTools.subset: loca subsetting not needed
INFO fontTools.subset: kern subsetted
INFO fontTools.subset: post subsetted
INFO fontTools.subset: prop subsetted
INFO fontTools.subset: name subsetting not needed
INFO fontTools.subset: glyf subsetted
INFO fontTools.subset: head pruned
INFO fontTools.subset: OS/2 Unicode ranges pruned: [0, 1]
INFO fontTools.subset: OS/2 CodePage ranges pruned: [0]
INFO fontTools.subset: glyf pruned
INFO fontTools.subset: name pruned
INFO fontTools.subset: maxp pruned
INFO fontTools.subset: cmap pruned
WARNING fontTools.ttLib.tables._p_o_s_t: 1 extra bytes in post.stringData array
INFO fontTools.subset: kern pruned
INFO fontTools.subset: post pruned
INFO fontTools.subset: Zapf dropped
INFO fontTools.subset: feat dropped
INFO fontTools.subset: meta dropped
INFO fontTools.subset: morx dropped
WARNING fontTools.ttLib.tables._h_e_a_d: 'created' timestamp seems very low; regarding as unix timestamp
INFO fontTools.subset: glyf pruned
INFO fontTools.subset: Added gid0 to subset
INFO fontTools.subset: Added first four glyphs to subset
INFO fontTools.subset: Closing glyph list over 'glyf': 59 glyphs before
INFO fontTools.subset: Glyph names: ['.notdef', '.null', 'A', 'B', 'C', 'D', 'Deltagreek', 'E', 'I', 'O', 'R', 'S', 'T', 'a', 'b', 'c', 'comma', 'd', 'e', 'eight', 'equal', 'f', 'five', 'four', 'g', 'h', 'i', 'j', 'l', 'm', 'minus', 'n', 'nine', 'nonmarkingreturn', 'o', 'one', 'p', 'parenleft', 'parenright', 'period', 'q', 'quotesingle', 'r', 's', 'seven', 'six', 'slash', 'space', 't', 'three', 'two', 'u', 'underscore', 'v', 'w', 'x', 'y', 'z', 'zero']
INFO fontTools.subset: Glyph IDs:   [0, 1, 2, 3, 10, 11, 12, 15, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 32, 36, 37, 38, 39, 40, 44, 50, 53, 54, 55, 66, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 239, 1091]
INFO fontTools.subset: Closed glyph list over 'glyf': 59 glyphs after
INFO fontTools.subset: Glyph names: ['.notdef', '.null', 'A', 'B', 'C', 'D', 'Deltagreek', 'E', 'I', 'O', 'R', 'S', 'T', 'a', 'b', 'c', 'comma', 'd', 'e', 'eight', 'equal', 'f', 'five', 'four', 'g', 'h', 'i', 'j', 'l', 'm', 'minus', 'n', 'nine', 'nonmarkingreturn', 'o', 'one', 'p', 'parenleft', 'parenright', 'period', 'q', 'quotesingle', 'r', 's', 'seven', 'six', 'slash', 'space', 't', 'three', 'two', 'u', 'underscore', 'v', 'w', 'x', 'y', 'z', 'zero']
INFO fontTools.subset: Glyph IDs:   [0, 1, 2, 3, 10, 11, 12, 15, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 32, 36, 37, 38, 39, 40, 44, 50, 53, 54, 55, 66, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 239, 1091]
INFO fontTools.subset: Retaining 59 glyphs
INFO fontTools.subset: head subsetting not needed
INFO fontTools.subset: hhea subsetting not needed
INFO fontTools.subset: maxp subsetting not needed
INFO fontTools.subset: OS/2 subsetting not needed
INFO fontTools.subset: hmtx subsetted
INFO fontTools.subset: hdmx subsetted
INFO fontTools.subset: cmap subsetted
INFO fontTools.subset: fpgm subsetting not needed
INFO fontTools.subset: prep subsetting not needed
INFO fontTools.subset: cvt  subsetting not needed
INFO fontTools.subset: loca subsetting not needed
INFO fontTools.subset: kern subsetted
INFO fontTools.subset: post subsetted
INFO fontTools.subset: prop subsetted
INFO fontTools.subset: name subsetting not needed
INFO fontTools.subset: glyf subsetted
INFO fontTools.subset: head pruned
INFO fontTools.subset: OS/2 Unicode ranges pruned: [0, 7, 38]
INFO fontTools.subset: OS/2 CodePage ranges pruned: [0]
INFO fontTools.subset: glyf pruned
INFO fontTools.subset: name pruned
INFO fontTools.subset: maxp pruned
INFO fontTools.subset: cmap pruned
WARNING fontTools.ttLib.tables._p_o_s_t: 1 extra bytes in post.stringData array
INFO fontTools.subset: kern pruned
INFO fontTools.subset: post pruned
INFO fontTools.subset: Zapf dropped
INFO fontTools.subset: feat dropped
INFO fontTools.subset: meta dropped
INFO fontTools.subset: morx dropped
WARNING fontTools.ttLib.tables._h_e_a_d: 'created' timestamp seems very low; regarding as unix timestamp
INFO fontTools.subset: glyf pruned
INFO fontTools.subset: Added gid0 to subset
INFO fontTools.subset: Added first four glyphs to subset
INFO fontTools.subset: Closing glyph list over 'glyf': 6 glyphs before
INFO fontTools.subset: Glyph names: ['.notdef', '.null', 'fi', 'fl', 'nonmarkingreturn', 'space']
INFO fontTools.subset: Glyph IDs:   [0, 1, 2, 3, 192, 193]
INFO fontTools.subset: Closed glyph list over 'glyf': 6 glyphs after
INFO fontTools.subset: Glyph names: ['.notdef', '.null', 'fi', 'fl', 'nonmarkingreturn', 'space']
INFO fontTools.subset: Glyph IDs:   [0, 1, 2, 3, 192, 193]
INFO fontTools.subset: Retaining 6 glyphs
INFO fontTools.subset: head subsetting not needed
INFO fontTools.subset: hhea subsetting not needed
INFO fontTools.subset: maxp subsetting not needed
INFO fontTools.subset: OS/2 subsetting not needed
INFO fontTools.subset: hmtx subsetted
INFO fontTools.subset: hdmx subsetted
INFO fontTools.subset: cmap subsetted
INFO fontTools.subset: fpgm subsetting not needed
INFO fontTools.subset: prep subsetting not needed
INFO fontTools.subset: cvt  subsetting not needed
INFO fontTools.subset: loca subsetting not needed
INFO fontTools.subset: kern subsetted to empty; dropped
INFO fontTools.subset: post subsetted
INFO fontTools.subset: prop subsetted
INFO fontTools.subset: name subsetting not needed
INFO fontTools.subset: glyf subsetted
INFO fontTools.subset: head pruned
INFO fontTools.subset: OS/2 Unicode ranges pruned: [62]
INFO fontTools.subset: OS/2 CodePage ranges pruned: [0]
INFO fontTools.subset: glyf pruned
INFO fontTools.subset: name pruned
INFO fontTools.subset: maxp pruned
INFO fontTools.subset: cmap pruned
WARNING fontTools.ttLib.tables._p_o_s_t: 1 extra bytes in post.stringData array
INFO fontTools.subset: kern pruned
INFO fontTools.subset: post pruned
INFO fontTools.subset: Zapf dropped
INFO fontTools.subset: feat dropped
INFO fontTools.subset: meta dropped
INFO fontTools.subset: morx dropped
INFO fontTools.subset: glyf pruned
INFO fontTools.subset: Added gid0 to subset
INFO fontTools.subset: Added first four glyphs to subset
INFO fontTools.subset: Closing glyph list over 'glyf': 55 glyphs before
INFO fontTools.subset: Glyph names: ['.notdef', '.null', 'A', 'B', 'C', 'D', 'Deltagreek', 'E', 'I', 'M', 'N', 'O', 'R', 'S', 'T', 'Y', 'a', 'asciitilde', 'b', 'bracketleft', 'bracketright', 'c', 'comma', 'd', 'e', 'equal', 'f', 'g', 'h', 'hyphen', 'i', 'k', 'l', 'm', 'n', 'nine', 'nonmarkingreturn', 'o', 'one', 'p', 'parenleft', 'parenright', 'period', 'periodcentered', 'q', 'r', 's', 'space', 't', 'three', 'two', 'u', 'v', 'x', 'zero']
INFO fontTools.subset: Glyph IDs:   [0, 1, 2, 3, 11, 12, 15, 16, 17, 19, 20, 21, 22, 28, 32, 36, 37, 38, 39, 40, 44, 48, 49, 50, 53, 54, 55, 60, 62, 64, 68, 69, 70, 71, 72, 73, 74, 75, 76, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 91, 97, 195, 1091]
INFO fontTools.subset: Closed glyph list over 'glyf': 55 glyphs after
INFO fontTools.subset: Glyph names: ['.notdef', '.null', 'A', 'B', 'C', 'D', 'Deltagreek', 'E', 'I', 'M', 'N', 'O', 'R', 'S', 'T', 'Y', 'a', 'asciitilde', 'b', 'bracketleft', 'bracketright', 'c', 'comma', 'd', 'e', 'equal', 'f', 'g', 'h', 'hyphen', 'i', 'k', 'l', 'm', 'n', 'nine', 'nonmarkingreturn', 'o', 'one', 'p', 'parenleft', 'parenright', 'period', 'periodcentered', 'q', 'r', 's', 'space', 't', 'three', 'two', 'u', 'v', 'x', 'zero']
INFO fontTools.subset: Glyph IDs:   [0, 1, 2, 3, 11, 12, 15, 16, 17, 19, 20, 21, 22, 28, 32, 36, 37, 38, 39, 40, 44, 48, 49, 50, 53, 54, 55, 60, 62, 64, 68, 69, 70, 71, 72, 73, 74, 75, 76, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 91, 97, 195, 1091]
INFO fontTools.subset: Retaining 55 glyphs
INFO fontTools.subset: head subsetting not needed
INFO fontTools.subset: hhea subsetting not needed
INFO fontTools.subset: maxp subsetting not needed
INFO fontTools.subset: OS/2 subsetting not needed
INFO fontTools.subset: hmtx subsetted
INFO fontTools.subset: cmap subsetted
INFO fontTools.subset: fpgm subsetting not needed
INFO fontTools.subset: prep subsetting not needed
INFO fontTools.subset: cvt  subsetting not needed
INFO fontTools.subset: loca subsetting not needed
INFO fontTools.subset: kern subsetted
INFO fontTools.subset: post subsetted
INFO fontTools.subset: prop subsetted
INFO fontTools.subset: name subsetting not needed
INFO fontTools.subset: glyf subsetted
INFO fontTools.subset: head pruned
INFO fontTools.subset: OS/2 Unicode ranges pruned: [0, 1, 7]
INFO fontTools.subset: OS/2 CodePage ranges pruned: [0]
INFO fontTools.subset: glyf pruned
INFO fontTools.subset: name pruned
INFO fontTools.subset: maxp pruned
INFO fontTools.subset: cmap pruned
WARNING fontTools.ttLib.tables._p_o_s_t: 1 extra bytes in post.stringData array
INFO fontTools.subset: kern pruned
INFO fontTools.subset: post pruned
INFO fontTools.subset: Zapf dropped
INFO fontTools.subset: feat dropped
INFO fontTools.subset: meta dropped
INFO fontTools.subset: morx dropped
INFO fontTools.subset: glyf pruned
INFO fontTools.subset: Added gid0 to subset
INFO fontTools.subset: Added first four glyphs to subset
INFO fontTools.subset: Closing glyph list over 'glyf': 5 glyphs before
INFO fontTools.subset: Glyph names: ['.notdef', '.null', 'fi', 'nonmarkingreturn', 'space']
INFO fontTools.subset: Glyph IDs:   [0, 1, 2, 3, 192]
INFO fontTools.subset: Closed glyph list over 'glyf': 5 glyphs after
INFO fontTools.subset: Glyph names: ['.notdef', '.null', 'fi', 'nonmarkingreturn', 'space']
INFO fontTools.subset: Glyph IDs:   [0, 1, 2, 3, 192]
INFO fontTools.subset: Retaining 5 glyphs
INFO fontTools.subset: head subsetting not needed
INFO fontTools.subset: hhea subsetting not needed
INFO fontTools.subset: maxp subsetting not needed
INFO fontTools.subset: OS/2 subsetting not needed
INFO fontTools.subset: hmtx subsetted
INFO fontTools.subset: cmap subsetted
INFO fontTools.subset: fpgm subsetting not needed
INFO fontTools.subset: prep subsetting not needed
INFO fontTools.subset: cvt  subsetting not needed
INFO fontTools.subset: loca subsetting not needed
INFO fontTools.subset: kern subsetted to empty; dropped
INFO fontTools.subset: post subsetted
INFO fontTools.subset: prop subsetted
INFO fontTools.subset: name subsetting not needed
INFO fontTools.subset: glyf subsetted
INFO fontTools.subset: head pruned
INFO fontTools.subset: OS/2 Unicode ranges pruned: [62]
INFO fontTools.subset: OS/2 CodePage ranges pruned: [0]
INFO fontTools.subset: glyf pruned
INFO fontTools.subset: name pruned
INFO fontTools.subset: maxp pruned
INFO fontTools.subset: cmap pruned
WARNING fontTools.ttLib.tables._p_o_s_t: 1 extra bytes in post.stringData array
INFO fontTools.subset: kern pruned
INFO fontTools.subset: post pruned
INFO fontTools.subset: Zapf dropped
INFO fontTools.subset: feat dropped
INFO fontTools.subset: meta dropped
INFO fontTools.subset: morx dropped
WARNING fontTools.ttLib.tables._h_e_a_d: 'created' timestamp seems very low; regarding as unix timestamp
INFO fontTools.subset: glyf pruned
INFO fontTools.subset: Added gid0 to subset
INFO fontTools.subset: Added first four glyphs to subset
INFO fontTools.subset: Closing glyph list over 'glyf': 22 glyphs before
INFO fontTools.subset: Glyph names: ['.notdef', '.null', 'N', 'Y', 'a', 'asciitilde', 'c', 'e', 'equal', 'i', 'l', 'nonmarkingreturn', 'o', 'p', 'periodcentered', 'q', 'r', 's', 'space', 't', 'u', 'v']
INFO fontTools.subset: Glyph IDs:   [0, 1, 2, 3, 32, 49, 60, 68, 70, 72, 76, 79, 82, 83, 84, 85, 86, 87, 88, 89, 97, 195]
INFO fontTools.subset: Closed glyph list over 'glyf': 22 glyphs after
INFO fontTools.subset: Glyph names: ['.notdef', '.null', 'N', 'Y', 'a', 'asciitilde', 'c', 'e', 'equal', 'i', 'l', 'nonmarkingreturn', 'o', 'p', 'periodcentered', 'q', 'r', 's', 'space', 't', 'u', 'v']
INFO fontTools.subset: Glyph IDs:   [0, 1, 2, 3, 32, 49, 60, 68, 70, 72, 76, 79, 82, 83, 84, 85, 86, 87, 88, 89, 97, 195]
INFO fontTools.subset: Retaining 22 glyphs
INFO fontTools.subset: head subsetting not needed
INFO fontTools.subset: hhea subsetting not needed
INFO fontTools.subset: maxp subsetting not needed
INFO fontTools.subset: OS/2 subsetting not needed
INFO fontTools.subset: hmtx subsetted
INFO fontTools.subset: hdmx subsetted
INFO fontTools.subset: cmap subsetted
INFO fontTools.subset: fpgm subsetting not needed
INFO fontTools.subset: prep subsetting not needed
INFO fontTools.subset: cvt  subsetting not needed
INFO fontTools.subset: loca subsetting not needed
INFO fontTools.subset: kern subsetted
INFO fontTools.subset: post subsetted
INFO fontTools.subset: prop subsetted
INFO fontTools.subset: name subsetting not needed
INFO fontTools.subset: glyf subsetted
INFO fontTools.subset: head pruned
INFO fontTools.subset: OS/2 Unicode ranges pruned: [0, 1]
INFO fontTools.subset: OS/2 CodePage ranges pruned: [0]
INFO fontTools.subset: glyf pruned
INFO fontTools.subset: name pruned
INFO fontTools.subset: maxp pruned
INFO fontTools.subset: cmap pruned
WARNING fontTools.ttLib.tables._p_o_s_t: 1 extra bytes in post.stringData array
INFO fontTools.subset: kern pruned
INFO fontTools.subset: post pruned
INFO fontTools.subset: Zapf dropped
INFO fontTools.subset: feat dropped
INFO fontTools.subset: meta dropped
INFO fontTools.subset: morx dropped
WARNING fontTools.ttLib.tables._h_e_a_d: 'created' timestamp seems very low; regarding as unix timestamp
INFO fontTools.subset: glyf pruned
INFO fontTools.subset: Added gid0 to subset
INFO fontTools.subset: Added first four glyphs to subset
INFO fontTools.subset: Closing glyph list over 'glyf': 49 glyphs before
INFO fontTools.subset: Glyph names: ['.notdef', '.null', 'C', 'O', 'P', 'S', 'T', 'a', 'b', 'c', 'd', 'e', 'equal', 'f', 'five', 'four', 'g', 'h', 'hyphen', 'i', 'l', 'm', 'minus', 'n', 'nine', 'nonmarkingreturn', 'o', 'one', 'p', 'parenleft', 'parenright', 'period', 'q', 'quotesingle', 'r', 's', 'six', 'slash', 'space', 't', 'two', 'u', 'underscore', 'v', 'w', 'x', 'y', 'z', 'zero']
INFO fontTools.subset: Glyph IDs:   [0, 1, 2, 3, 10, 11, 12, 16, 17, 18, 19, 20, 21, 23, 24, 25, 28, 32, 38, 50, 51, 54, 55, 66, 68, 69, 70, 71, 72, 73, 74, 75, 76, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 239]
INFO fontTools.subset: Closed glyph list over 'glyf': 49 glyphs after
INFO fontTools.subset: Glyph names: ['.notdef', '.null', 'C', 'O', 'P', 'S', 'T', 'a', 'b', 'c', 'd', 'e', 'equal', 'f', 'five', 'four', 'g', 'h', 'hyphen', 'i', 'l', 'm', 'minus', 'n', 'nine', 'nonmarkingreturn', 'o', 'one', 'p', 'parenleft', 'parenright', 'period', 'q', 'quotesingle', 'r', 's', 'six', 'slash', 'space', 't', 'two', 'u', 'underscore', 'v', 'w', 'x', 'y', 'z', 'zero']
INFO fontTools.subset: Glyph IDs:   [0, 1, 2, 3, 10, 11, 12, 16, 17, 18, 19, 20, 21, 23, 24, 25, 28, 32, 38, 50, 51, 54, 55, 66, 68, 69, 70, 71, 72, 73, 74, 75, 76, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 239]
INFO fontTools.subset: Retaining 49 glyphs
INFO fontTools.subset: head subsetting not needed
INFO fontTools.subset: hhea subsetting not needed
INFO fontTools.subset: maxp subsetting not needed
INFO fontTools.subset: OS/2 subsetting not needed
INFO fontTools.subset: hmtx subsetted
INFO fontTools.subset: hdmx subsetted
INFO fontTools.subset: cmap subsetted
INFO fontTools.subset: fpgm subsetting not needed
INFO fontTools.subset: prep subsetting not needed
INFO fontTools.subset: cvt  subsetting not needed
INFO fontTools.subset: loca subsetting not needed
INFO fontTools.subset: kern subsetted
INFO fontTools.subset: post subsetted
INFO fontTools.subset: prop subsetted
INFO fontTools.subset: name subsetting not needed
INFO fontTools.subset: glyf subsetted
INFO fontTools.subset: head pruned
INFO fontTools.subset: OS/2 Unicode ranges pruned: [0, 38]
INFO fontTools.subset: OS/2 CodePage ranges pruned: [0]
INFO fontTools.subset: glyf pruned
INFO fontTools.subset: name pruned
INFO fontTools.subset: maxp pruned
INFO fontTools.subset: cmap pruned
WARNING fontTools.ttLib.tables._p_o_s_t: 1 extra bytes in post.stringData array
INFO fontTools.subset: kern pruned
INFO fontTools.subset: post pruned
INFO fontTools.subset: Zapf dropped
INFO fontTools.subset: feat dropped
INFO fontTools.subset: meta dropped
INFO fontTools.subset: morx dropped
WARNING fontTools.ttLib.tables._h_e_a_d: 'created' timestamp seems very low; regarding as unix timestamp
INFO fontTools.subset: glyf pruned
INFO fontTools.subset: Added gid0 to subset
INFO fontTools.subset: Added first four glyphs to subset
INFO fontTools.subset: Closing glyph list over 'glyf': 6 glyphs before
INFO fontTools.subset: Glyph names: ['.notdef', '.null', 'fi', 'fl', 'nonmarkingreturn', 'space']
INFO fontTools.subset: Glyph IDs:   [0, 1, 2, 3, 192, 193]
INFO fontTools.subset: Closed glyph list over 'glyf': 6 glyphs after
INFO fontTools.subset: Glyph names: ['.notdef', '.null', 'fi', 'fl', 'nonmarkingreturn', 'space']
INFO fontTools.subset: Glyph IDs:   [0, 1, 2, 3, 192, 193]
INFO fontTools.subset: Retaining 6 glyphs
INFO fontTools.subset: head subsetting not needed
INFO fontTools.subset: hhea subsetting not needed
INFO fontTools.subset: maxp subsetting not needed
INFO fontTools.subset: OS/2 subsetting not needed
INFO fontTools.subset: hmtx subsetted
INFO fontTools.subset: hdmx subsetted
INFO fontTools.subset: cmap subsetted
INFO fontTools.subset: fpgm subsetting not needed
INFO fontTools.subset: prep subsetting not needed
INFO fontTools.subset: cvt  subsetting not needed
INFO fontTools.subset: loca subsetting not needed
INFO fontTools.subset: kern subsetted to empty; dropped
INFO fontTools.subset: post subsetted
INFO fontTools.subset: prop subsetted
INFO fontTools.subset: name subsetting not needed
INFO fontTools.subset: glyf subsetted
INFO fontTools.subset: head pruned
INFO fontTools.subset: OS/2 Unicode ranges pruned: [62]
INFO fontTools.subset: OS/2 CodePage ranges pruned: [0]
INFO fontTools.subset: glyf pruned
INFO fontTools.subset: name pruned
INFO fontTools.subset: maxp pruned
INFO fontTools.subset: cmap pruned
WARNING fontTools.ttLib.tables._p_o_s_t: 1 extra bytes in post.stringData array
INFO fontTools.subset: kern pruned
INFO fontTools.subset: post pruned
INFO fontTools.subset: Zapf dropped
INFO fontTools.subset: feat dropped
INFO fontTools.subset: meta dropped
INFO fontTools.subset: morx dropped
INFO fontTools.subset: glyf pruned
INFO fontTools.subset: Added gid0 to subset
INFO fontTools.subset: Added first four glyphs to subset
INFO fontTools.subset: Closing glyph list over 'glyf': 55 glyphs before
INFO fontTools.subset: Glyph names: ['.notdef', '.null', 'A', 'B', 'C', 'D', 'E', 'H', 'N', 'O', 'P', 'R', 'S', 'T', 'Y', 'a', 'asciitilde', 'b', 'bracketleft', 'bracketright', 'c', 'comma', 'd', 'e', 'equal', 'f', 'g', 'h', 'hyphen', 'i', 'j', 'l', 'm', 'n', 'nonmarkingreturn', 'o', 'one', 'p', 'parenleft', 'parenright', 'period', 'periodcentered', 'q', 'r', 's', 'space', 't', 'three', 'two', 'u', 'v', 'w', 'x', 'y', 'zero']
INFO fontTools.subset: Glyph IDs:   [0, 1, 2, 3, 11, 12, 15, 16, 17, 19, 20, 21, 22, 32, 36, 37, 38, 39, 40, 43, 49, 50, 51, 53, 54, 55, 60, 62, 64, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 97, 195]
INFO fontTools.subset: Closed glyph list over 'glyf': 55 glyphs after
INFO fontTools.subset: Glyph names: ['.notdef', '.null', 'A', 'B', 'C', 'D', 'E', 'H', 'N', 'O', 'P', 'R', 'S', 'T', 'Y', 'a', 'asciitilde', 'b', 'bracketleft', 'bracketright', 'c', 'comma', 'd', 'e', 'equal', 'f', 'g', 'h', 'hyphen', 'i', 'j', 'l', 'm', 'n', 'nonmarkingreturn', 'o', 'one', 'p', 'parenleft', 'parenright', 'period', 'periodcentered', 'q', 'r', 's', 'space', 't', 'three', 'two', 'u', 'v', 'w', 'x', 'y', 'zero']
INFO fontTools.subset: Glyph IDs:   [0, 1, 2, 3, 11, 12, 15, 16, 17, 19, 20, 21, 22, 32, 36, 37, 38, 39, 40, 43, 49, 50, 51, 53, 54, 55, 60, 62, 64, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 97, 195]
INFO fontTools.subset: Retaining 55 glyphs
INFO fontTools.subset: head subsetting not needed
INFO fontTools.subset: hhea subsetting not needed
INFO fontTools.subset: maxp subsetting not needed
INFO fontTools.subset: OS/2 subsetting not needed
INFO fontTools.subset: hmtx subsetted
INFO fontTools.subset: cmap subsetted
INFO fontTools.subset: fpgm subsetting not needed
INFO fontTools.subset: prep subsetting not needed
INFO fontTools.subset: cvt  subsetting not needed
INFO fontTools.subset: loca subsetting not needed
INFO fontTools.subset: kern subsetted
INFO fontTools.subset: post subsetted
INFO fontTools.subset: prop subsetted
INFO fontTools.subset: name subsetting not needed
INFO fontTools.subset: glyf subsetted
INFO fontTools.subset: head pruned
INFO fontTools.subset: OS/2 Unicode ranges pruned: [0, 1]
INFO fontTools.subset: OS/2 CodePage ranges pruned: [0]
INFO fontTools.subset: glyf pruned
INFO fontTools.subset: name pruned
INFO fontTools.subset: maxp pruned
INFO fontTools.subset: cmap pruned
WARNING fontTools.ttLib.tables._p_o_s_t: 1 extra bytes in post.stringData array
INFO fontTools.subset: kern pruned
INFO fontTools.subset: post pruned
INFO fontTools.subset: Zapf dropped
INFO fontTools.subset: feat dropped
INFO fontTools.subset: meta dropped
INFO fontTools.subset: morx dropped
INFO fontTools.subset: glyf pruned
INFO fontTools.subset: Added gid0 to subset
INFO fontTools.subset: Added first four glyphs to subset
INFO fontTools.subset: Closing glyph list over 'glyf': 5 glyphs before
INFO fontTools.subset: Glyph names: ['.notdef', '.null', 'fi', 'nonmarkingreturn', 'space']
INFO fontTools.subset: Glyph IDs:   [0, 1, 2, 3, 192]
INFO fontTools.subset: Closed glyph list over 'glyf': 5 glyphs after
INFO fontTools.subset: Glyph names: ['.notdef', '.null', 'fi', 'nonmarkingreturn', 'space']
INFO fontTools.subset: Glyph IDs:   [0, 1, 2, 3, 192]
INFO fontTools.subset: Retaining 5 glyphs
INFO fontTools.subset: head subsetting not needed
INFO fontTools.subset: hhea subsetting not needed
INFO fontTools.subset: maxp subsetting not needed
INFO fontTools.subset: OS/2 subsetting not needed
INFO fontTools.subset: hmtx subsetted
INFO fontTools.subset: cmap subsetted
INFO fontTools.subset: fpgm subsetting not needed
INFO fontTools.subset: prep subsetting not needed
INFO fontTools.subset: cvt  subsetting not needed
INFO fontTools.subset: loca subsetting not needed
INFO fontTools.subset: kern subsetted to empty; dropped
INFO fontTools.subset: post subsetted
INFO fontTools.subset: prop subsetted
INFO fontTools.subset: name subsetting not needed
INFO fontTools.subset: glyf subsetted
INFO fontTools.subset: head pruned
INFO fontTools.subset: OS/2 Unicode ranges pruned: [62]
INFO fontTools.subset: OS/2 CodePage ranges pruned: [0]
INFO fontTools.subset: glyf pruned
INFO fontTools.subset: name pruned
INFO fontTools.subset: maxp pruned
INFO fontTools.subset: cmap pruned
WARNING fontTools.ttLib.tables._p_o_s_t: 1 extra bytes in post.stringData array
INFO fontTools.subset: kern pruned
INFO fontTools.subset: post pruned
INFO fontTools.subset: Zapf dropped
INFO fontTools.subset: feat dropped
INFO fontTools.subset: meta dropped
INFO fontTools.subset: morx dropped
WARNING fontTools.ttLib.tables._h_e_a_d: 'created' timestamp seems very low; regarding as unix timestamp
INFO fontTools.subset: glyf pruned
INFO fontTools.subset: Added gid0 to subset
INFO fontTools.subset: Added first four glyphs to subset
INFO fontTools.subset: Closing glyph list over 'glyf': 22 glyphs before
INFO fontTools.subset: Glyph names: ['.notdef', '.null', 'N', 'Y', 'a', 'asciitilde', 'c', 'e', 'equal', 'i', 'l', 'nonmarkingreturn', 'o', 'p', 'periodcentered', 'q', 'r', 's', 'space', 't', 'u', 'v']
INFO fontTools.subset: Glyph IDs:   [0, 1, 2, 3, 32, 49, 60, 68, 70, 72, 76, 79, 82, 83, 84, 85, 86, 87, 88, 89, 97, 195]
INFO fontTools.subset: Closed glyph list over 'glyf': 22 glyphs after
INFO fontTools.subset: Glyph names: ['.notdef', '.null', 'N', 'Y', 'a', 'asciitilde', 'c', 'e', 'equal', 'i', 'l', 'nonmarkingreturn', 'o', 'p', 'periodcentered', 'q', 'r', 's', 'space', 't', 'u', 'v']
INFO fontTools.subset: Glyph IDs:   [0, 1, 2, 3, 32, 49, 60, 68, 70, 72, 76, 79, 82, 83, 84, 85, 86, 87, 88, 89, 97, 195]
INFO fontTools.subset: Retaining 22 glyphs
INFO fontTools.subset: head subsetting not needed
INFO fontTools.subset: hhea subsetting not needed
INFO fontTools.subset: maxp subsetting not needed
INFO fontTools.subset: OS/2 subsetting not needed
INFO fontTools.subset: hmtx subsetted
INFO fontTools.subset: hdmx subsetted
INFO fontTools.subset: cmap subsetted
INFO fontTools.subset: fpgm subsetting not needed
INFO fontTools.subset: prep subsetting not needed
INFO fontTools.subset: cvt  subsetting not needed
INFO fontTools.subset: loca subsetting not needed
INFO fontTools.subset: kern subsetted
INFO fontTools.subset: post subsetted
INFO fontTools.subset: prop subsetted
INFO fontTools.subset: name subsetting not needed
INFO fontTools.subset: glyf subsetted
INFO fontTools.subset: head pruned
INFO fontTools.subset: OS/2 Unicode ranges pruned: [0, 1]
INFO fontTools.subset: OS/2 CodePage ranges pruned: [0]
INFO fontTools.subset: glyf pruned
INFO fontTools.subset: name pruned
INFO fontTools.subset: maxp pruned
INFO fontTools.subset: cmap pruned
WARNING fontTools.ttLib.tables._p_o_s_t: 1 extra bytes in post.stringData array
INFO fontTools.subset: kern pruned
INFO fontTools.subset: post pruned
INFO fontTools.subset: Zapf dropped
INFO fontTools.subset: feat dropped
INFO fontTools.subset: meta dropped
INFO fontTools.subset: morx dropped
WARNING fontTools.ttLib.tables._h_e_a_d: 'created' timestamp seems very low; regarding as unix timestamp
INFO fontTools.subset: glyf pruned
INFO fontTools.subset: Added gid0 to subset
INFO fontTools.subset: Added first four glyphs to subset
INFO fontTools.subset: Closing glyph list over 'glyf': 37 glyphs before
INFO fontTools.subset: Glyph names: ['.notdef', '.null', 'A', 'D', 'S', 'T', 'a', 'b', 'c', 'comma', 'd', 'e', 'f', 'g', 'h', 'hyphen', 'i', 'l', 'm', 'n', 'nonmarkingreturn', 'o', 'p', 'period', 'r', 's', 'seven', 'six', 'slash', 'space', 't', 'u', 'v', 'w', 'x', 'y', 'z']
INFO fontTools.subset: Glyph IDs:   [0, 1, 2, 3, 15, 16, 17, 18, 25, 26, 36, 39, 54, 55, 68, 69, 70, 71, 72, 73, 74, 75, 76, 79, 80, 81, 82, 83, 85, 86, 87, 88, 89, 90, 91, 92, 93]
INFO fontTools.subset: Closed glyph list over 'glyf': 37 glyphs after
INFO fontTools.subset: Glyph names: ['.notdef', '.null', 'A', 'D', 'S', 'T', 'a', 'b', 'c', 'comma', 'd', 'e', 'f', 'g', 'h', 'hyphen', 'i', 'l', 'm', 'n', 'nonmarkingreturn', 'o', 'p', 'period', 'r', 's', 'seven', 'six', 'slash', 'space', 't', 'u', 'v', 'w', 'x', 'y', 'z']
INFO fontTools.subset: Glyph IDs:   [0, 1, 2, 3, 15, 16, 17, 18, 25, 26, 36, 39, 54, 55, 68, 69, 70, 71, 72, 73, 74, 75, 76, 79, 80, 81, 82, 83, 85, 86, 87, 88, 89, 90, 91, 92, 93]
INFO fontTools.subset: Retaining 37 glyphs
INFO fontTools.subset: head subsetting not needed
INFO fontTools.subset: hhea subsetting not needed
INFO fontTools.subset: maxp subsetting not needed
INFO fontTools.subset: OS/2 subsetting not needed
INFO fontTools.subset: hmtx subsetted
INFO fontTools.subset: hdmx subsetted
INFO fontTools.subset: cmap subsetted
INFO fontTools.subset: fpgm subsetting not needed
INFO fontTools.subset: prep subsetting not needed
INFO fontTools.subset: cvt  subsetting not needed
INFO fontTools.subset: loca subsetting not needed
INFO fontTools.subset: kern subsetted
INFO fontTools.subset: post subsetted
INFO fontTools.subset: prop subsetted
INFO fontTools.subset: name subsetting not needed
INFO fontTools.subset: glyf subsetted
INFO fontTools.subset: head pruned
INFO fontTools.subset: OS/2 Unicode ranges pruned: [0]
INFO fontTools.subset: OS/2 CodePage ranges pruned: [0]
INFO fontTools.subset: glyf pruned
INFO fontTools.subset: name pruned
INFO fontTools.subset: maxp pruned
INFO fontTools.subset: cmap pruned
WARNING fontTools.ttLib.tables._p_o_s_t: 1 extra bytes in post.stringData array
INFO fontTools.subset: kern pruned
INFO fontTools.subset: post pruned
INFO fontTools.subset: Zapf dropped
INFO fontTools.subset: feat dropped
INFO fontTools.subset: meta dropped
INFO fontTools.subset: morx dropped
WARNING fontTools.ttLib.tables._h_e_a_d: 'created' timestamp seems very low; regarding as unix timestamp
INFO fontTools.subset: glyf pruned
INFO fontTools.subset: Added gid0 to subset
INFO fontTools.subset: Added first four glyphs to subset
INFO fontTools.subset: Closing glyph list over 'glyf': 6 glyphs before
INFO fontTools.subset: Glyph names: ['.notdef', '.null', 'fi', 'fl', 'nonmarkingreturn', 'space']
INFO fontTools.subset: Glyph IDs:   [0, 1, 2, 3, 192, 193]
INFO fontTools.subset: Closed glyph list over 'glyf': 6 glyphs after
INFO fontTools.subset: Glyph names: ['.notdef', '.null', 'fi', 'fl', 'nonmarkingreturn', 'space']
INFO fontTools.subset: Glyph IDs:   [0, 1, 2, 3, 192, 193]
INFO fontTools.subset: Retaining 6 glyphs
INFO fontTools.subset: head subsetting not needed
INFO fontTools.subset: hhea subsetting not needed
INFO fontTools.subset: maxp subsetting not needed
INFO fontTools.subset: OS/2 subsetting not needed
INFO fontTools.subset: hmtx subsetted
INFO fontTools.subset: hdmx subsetted
INFO fontTools.subset: cmap subsetted
INFO fontTools.subset: fpgm subsetting not needed
INFO fontTools.subset: prep subsetting not needed
INFO fontTools.subset: cvt  subsetting not needed
INFO fontTools.subset: loca subsetting not needed
INFO fontTools.subset: kern subsetted to empty; dropped
INFO fontTools.subset: post subsetted
INFO fontTools.subset: prop subsetted
INFO fontTools.subset: name subsetting not needed
INFO fontTools.subset: glyf subsetted
INFO fontTools.subset: head pruned
INFO fontTools.subset: OS/2 Unicode ranges pruned: [62]
INFO fontTools.subset: OS/2 CodePage ranges pruned: [0]
INFO fontTools.subset: glyf pruned
INFO fontTools.subset: name pruned
INFO fontTools.subset: maxp pruned
INFO fontTools.subset: cmap pruned
WARNING fontTools.ttLib.tables._p_o_s_t: 1 extra bytes in post.stringData array
INFO fontTools.subset: kern pruned
INFO fontTools.subset: post pruned
INFO fontTools.subset: Zapf dropped
INFO fontTools.subset: feat dropped
INFO fontTools.subset: meta dropped
INFO fontTools.subset: morx dropped
INFO fontTools.subset: glyf pruned
INFO fontTools.subset: Added gid0 to subset
INFO fontTools.subset: Added first four glyphs to subset
INFO fontTools.subset: Closing glyph list over 'glyf': 46 glyphs before
INFO fontTools.subset: Glyph names: ['.notdef', '.null', 'A', 'B', 'C', 'D', 'E', 'I', 'L', 'N', 'P', 'R', 'U', 'Y', 'a', 'asciitilde', 'b', 'c', 'comma', 'd', 'e', 'f', 'g', 'h', 'hyphen', 'i', 'k', 'l', 'm', 'n', 'nonmarkingreturn', 'o', 'one', 'p', 'periodcentered', 'q', 'r', 's', 'space', 't', 'three', 'u', 'v', 'w', 'x', 'y']
INFO fontTools.subset: Glyph IDs:   [0, 1, 2, 3, 15, 16, 20, 22, 36, 37, 38, 39, 40, 44, 47, 49, 51, 53, 56, 60, 68, 69, 70, 71, 72, 73, 74, 75, 76, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 97, 195]
INFO fontTools.subset: Closed glyph list over 'glyf': 46 glyphs after
INFO fontTools.subset: Glyph names: ['.notdef', '.null', 'A', 'B', 'C', 'D', 'E', 'I', 'L', 'N', 'P', 'R', 'U', 'Y', 'a', 'asciitilde', 'b', 'c', 'comma', 'd', 'e', 'f', 'g', 'h', 'hyphen', 'i', 'k', 'l', 'm', 'n', 'nonmarkingreturn', 'o', 'one', 'p', 'periodcentered', 'q', 'r', 's', 'space', 't', 'three', 'u', 'v', 'w', 'x', 'y']
INFO fontTools.subset: Glyph IDs:   [0, 1, 2, 3, 15, 16, 20, 22, 36, 37, 38, 39, 40, 44, 47, 49, 51, 53, 56, 60, 68, 69, 70, 71, 72, 73, 74, 75, 76, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 97, 195]
INFO fontTools.subset: Retaining 46 glyphs
INFO fontTools.subset: head subsetting not needed
INFO fontTools.subset: hhea subsetting not needed
INFO fontTools.subset: maxp subsetting not needed
INFO fontTools.subset: OS/2 subsetting not needed
INFO fontTools.subset: hmtx subsetted
INFO fontTools.subset: cmap subsetted
INFO fontTools.subset: fpgm subsetting not needed
INFO fontTools.subset: prep subsetting not needed
INFO fontTools.subset: cvt  subsetting not needed
INFO fontTools.subset: loca subsetting not needed
INFO fontTools.subset: kern subsetted
INFO fontTools.subset: post subsetted
INFO fontTools.subset: prop subsetted
INFO fontTools.subset: name subsetting not needed
INFO fontTools.subset: glyf subsetted
INFO fontTools.subset: head pruned
INFO fontTools.subset: OS/2 Unicode ranges pruned: [0, 1]
INFO fontTools.subset: OS/2 CodePage ranges pruned: [0]
INFO fontTools.subset: glyf pruned
INFO fontTools.subset: name pruned
INFO fontTools.subset: maxp pruned
INFO fontTools.subset: cmap pruned
WARNING fontTools.ttLib.tables._p_o_s_t: 1 extra bytes in post.stringData array
INFO fontTools.subset: kern pruned
INFO fontTools.subset: post pruned
INFO fontTools.subset: Zapf dropped
INFO fontTools.subset: feat dropped
INFO fontTools.subset: meta dropped
INFO fontTools.subset: morx dropped
WARNING fontTools.ttLib.tables._h_e_a_d: 'created' timestamp seems very low; regarding as unix timestamp
INFO fontTools.subset: glyf pruned
INFO fontTools.subset: Added gid0 to subset
INFO fontTools.subset: Added first four glyphs to subset
INFO fontTools.subset: Closing glyph list over 'glyf': 22 glyphs before
INFO fontTools.subset: Glyph names: ['.notdef', '.null', 'N', 'Y', 'a', 'asciitilde', 'c', 'e', 'equal', 'i', 'l', 'nonmarkingreturn', 'o', 'p', 'periodcentered', 'q', 'r', 's', 'space', 't', 'u', 'v']
INFO fontTools.subset: Glyph IDs:   [0, 1, 2, 3, 32, 49, 60, 68, 70, 72, 76, 79, 82, 83, 84, 85, 86, 87, 88, 89, 97, 195]
INFO fontTools.subset: Closed glyph list over 'glyf': 22 glyphs after
INFO fontTools.subset: Glyph names: ['.notdef', '.null', 'N', 'Y', 'a', 'asciitilde', 'c', 'e', 'equal', 'i', 'l', 'nonmarkingreturn', 'o', 'p', 'periodcentered', 'q', 'r', 's', 'space', 't', 'u', 'v']
INFO fontTools.subset: Glyph IDs:   [0, 1, 2, 3, 32, 49, 60, 68, 70, 72, 76, 79, 82, 83, 84, 85, 86, 87, 88, 89, 97, 195]
INFO fontTools.subset: Retaining 22 glyphs
INFO fontTools.subset: head subsetting not needed
INFO fontTools.subset: hhea subsetting not needed
INFO fontTools.subset: maxp subsetting not needed
INFO fontTools.subset: OS/2 subsetting not needed
INFO fontTools.subset: hmtx subsetted
INFO fontTools.subset: hdmx subsetted
INFO fontTools.subset: cmap subsetted
INFO fontTools.subset: fpgm subsetting not needed
INFO fontTools.subset: prep subsetting not needed
INFO fontTools.subset: cvt  subsetting not needed
INFO fontTools.subset: loca subsetting not needed
INFO fontTools.subset: kern subsetted
INFO fontTools.subset: post subsetted
INFO fontTools.subset: prop subsetted
INFO fontTools.subset: name subsetting not needed
INFO fontTools.subset: glyf subsetted
INFO fontTools.subset: head pruned
INFO fontTools.subset: OS/2 Unicode ranges pruned: [0, 1]
INFO fontTools.subset: OS/2 CodePage ranges pruned: [0]
INFO fontTools.subset: glyf pruned
INFO fontTools.subset: name pruned
INFO panelforge_figures.manifest.resolver: render_manifest: produced 18 files; registry={'actin_microtubule_morphometry': 49, 'biophysics_scaling': 51, 'calcium_signaling': 15, 'clinical_cohort': 15, 'cryoem_and_structure': 15, 'diffusion_and_tracking': 15, 'dose_response_pharmacology': 15, 'fret_biosensors': 18, 'gillespie_stochastic': 15, 'grant_and_conceptual': 16, 'intravital_imaging': 61, 'meta_and_diagnostic': 27, 'mixed_effects_models': 20, 'network_and_pathway': 15, 'omics_differential': 22, 'redox_imaging': 15, 'rhogtpase_dynamics': 18, 'sensitivity_analysis': 15, 'single_cell_embeddings': 15, 'spatial_statistics': 16}
```

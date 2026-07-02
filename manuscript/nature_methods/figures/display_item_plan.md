# Stage 9.6 display item plan

Generated UTC. 2026-07-02T11:28:38.370369Z

Figure-spine version. figure-spine@2026-07-02@51275ccd63146d72934216cf132768738f132e89

## Display budget decision

| constraint | decision | stage |
| --- | --- | --- |
| Nature Methods Article display budget | Use six main display items, which is the sourced upper bound. | Stage 9.6 |
| Central evidence should not be buried | All five frozen central claims appear in at least one main figure. | Stage 9.6 |
| Rendering must be deterministic | PanelForge rendering is deferred to Stage 9.6b with pinned version v3.14.1. | Stage 9.6b |
| Supplementary display material | Supplementary display planning is deferred to Stage 9.7 after the main spine is locked. | Stage 9.7 |

## Main versus supplementary placement

The current spine uses `FIG-001` through `FIG-006` as main display items. No
supplementary figure is created in Stage 9.6. Stage 9.7 may add supplementary
items only after checking that main claims remain visible in the main paper.

## Stage 9.6b dependency

The display contract intentionally records future recipes and render paths, but
does not create rendered files. Panel images, graphical recipes, drift checks,
and rejected visual alternatives belong to the next rendering substage.

# Stage 9 ID namespace

Stage 9 uses stable identifiers so claims, paragraphs, figures, tables, references, statistics, and Stage 7 artifacts can be joined without relying on prose.

| Namespace | Object | Purpose |
|---|---|---|
| `CLM-####` | claim | claim hierarchy and downstream claim joins |
| `PARA-<section>-###` | paragraph | planned or drafted manuscript paragraph |
| `FIG-###` | main figure | main display item |
| `SFIG-###` | supplementary figure | supplementary display item |
| `TBL-###` | main table | main table |
| `STBL-###` | supplementary table | supplementary table |
| `ART-####` | artifact | Stage 7 evidence artifact |
| `REF-####` | reference | resolved literature or venue reference |
| `STAT-####` | statistic | single reported quantitative result |
| `SUPP-###` | supplementary item | supplementary method/table/figure object |

IDs are minted once, never reused, and never shown on reader-facing manuscript surfaces. Reader-facing prose must refer to the scientific object, not to the internal identifier.

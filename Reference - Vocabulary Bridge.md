# Reference - Vocabulary Bridge

A translation table between **how Shawn (architect) talks** and **how this repo (software) talks**. Use it both ways: map Shawn's request to repo concepts before acting, and explain repo output back in his terms. Plain meaning in the third column.

## Topo pilot terms

| Architect / Shawn says | Repo / code / Tapir term | What it actually is |
|---|---|---|
| Topo, topography, the site surface | **Mesh** (Archicad Mesh element); `CreateMeshes` | The 3D terrain object the pilot builds — one element |
| Contour lines, topo lines (what the drawing set should show) | **sublines** in the payload; "level lines" / `ridges=UserDefined` | Each survey contour fed in as a line Archicad keeps visible, instead of hiding it |
| The "smooth blob" / triangulated look (what Shawn does *not* want on sheets) | **free-TIN**; `SUBLINE_MODE = "points"` | Archicad triangulating between points and showing the facets — wrong for documentation |
| Property line, lot boundary | **PL layer**; `polygonCoordinates` (the perimeter) | The outline polygon of the mesh; pilot walks the survey's `PL` layer into a closed loop |
| The skirt / vertical sides of the topo | **skirt**; `skirtType = "SolidBodyWithSkirt"`, `skirtLevel` | The walls dropped from the mesh edge down to a base level |
| Elevation labels / spot elevations on contours | **texts**; `CreateTexts` (merged upstream as ENZYME-APD#391, not yet in a stock release — treat as fork-only until a Tapir release ships it) | Standalone text placed at each contour's elevation value |
| "Show user-defined ridges" / "all ridges smooth" (Mesh tool settings) | `ridges` / `showLines` payload fields (draft PR ENZYME-APD#395, not yet in a stock release — treat as fork-only until shipped), or the **Mesh tool default** trick | The display setting that produces clean contour lines instead of triangulation |
| Survey file from the surveyor | **DWG / DXF**; read with `ezdxf` | The "before" file; pipeline converts DWG→DXF (ODA File Converter) then reads DXF |
| — (no common architect term) | **payload** | The JSON document sent to Archicad describing what to create |
| — | **concave hull** (`shapely`) | A fallback way to derive a perimeter from the contour points if there's no property line |

## Platform terms

| Term | What it is |
|---|---|
| **Tapir** | The Archicad add-on that exposes ~134 JSON commands on top of Archicad's small official API. Everything here talks to it. See [[Research - Tapir Command Reference]]. |
| **The fork** | Scott's custom build of Tapir originally adding 6 commands/fields; 3 are now upstreamed (`CreateTexts` merged, `GoToView` (formerly `OpenView`) + `CreateMeshes` `ridges`/`showLines` as draft PRs), 3 still fork-only — see CLAUDE.md. **Assume Shawn doesn't have any of them yet** (the upstreamed three still need to ship in a Tapir release). Stock Tapir = the public release. |
| **MCP** | The bridge that lets Claude call Tapir commands directly. |
| **Stock / degraded path** | Running the pilot on public Tapir without the fork — see [[Guide - Stock Tapir (No Fork)]]. |
| **Endpoint `127.0.0.1:19723`** | The local socket Tapir listens on; the scripts POST here. |

## Documentation / drawing-set terms (relevant to the detail-import idea)

| Architect says | Tapir command | Notes |
|---|---|---|
| Detail (independent detail viewpoint) | `CreateDetails` | Creates the empty detail container, not its content |
| Worksheet | `CreateWorksheets` | Same — container only |
| Layout / sheet | `CreateLayouts` | Layout Book page (+ master layout) |
| Drawing placed on a sheet | `CreateDrawings` | Places a drawing **from an internal navigator view** — not from an external file |
| Hotlink module / merged module / `.mod` file | `GetHotlinks` (**read-only**) | There is **no** command to place/merge a `.mod`. Injecting a detail library this way isn't possible with current Tapir — would need a new fork command. |

## When in doubt

If Shawn names something not in this table, check [[Research - Tapir Command Reference]] for the matching command, and confirm it's not one of the fork-dependent items (see CLAUDE.md for the current list — 4 still fork-only, 2 upstreamed but not yet in a Tapir release) before suggesting it.

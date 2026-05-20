# Source - Inferred Parameters in the Topo Pilot

What did the pilot *actually have to invent* vs. read from the input? Done 2026-05-19, after the v4 mesh matched Shawn's dimensions to <0.5%. Useful for scoping how much of the pilot is "data conversion" vs. "human intuition baked in as constants."

## Tally

- **3 parameters** are read straight from the input DWG/DXF.
- **3 parameters** are inferred from the surveyor's conventions (would change with a different surveyor).
- **6 parameters** are inferred from Shawn's example file (would change with PBW's preferences, or per-project).
- **2 parameters** are arbitrary defaults that happened to work.

So out of ~14 distinct choices in the script, **only 3 are determined by the input** — the geometry itself. The other 11 are conventions encoded as constants.

## The full breakdown

### Read from the input (3)
| Parameter | Source |
|---|---|
| Contour polyline geometry (X, Y vertices) | DXF `LWPOLYLINE.get_points()` |
| Contour elevation per polyline | DXF `LWPOLYLINE.dxf.elevation` |
| All other contour data extent | derived from the above |

This is the genuinely *automatic* part. Everything below is a guess.

### Inferred from this surveyor's conventions (3)
Would break or need adjustment with a different survey firm.

| Constant | Value | Why this and not else |
|---|---|---|
| `CONTOUR_LAYERS` | `{"CONT-HGH", "CONT-NML"}` | Foley Associates' naming. Other firms might use `TOPO`, `CONTOUR`, `EL-100`, etc. |
| `FOOT_TO_METER` applied unconditionally | 0.3048 | DXF `$INSUNITS = 0` (unitless), but Z values in the 9000s are clearly feet. Auto-detect possible via magnitude sniff, but currently hard-coded. |
| Contour Z is on the polyline's `elevation` attribute | trusted | Some surveyors deliver flat-Z polylines with elevation only in adjacent `MTEXT` labels — that would need OCR-style label-to-line matching. Foley does it the right way. |

### Inferred from Shawn's example file (6)
Would change with PBW's conventions, or per-project.

| Constant | Value | Source |
|---|---|---|
| `skirtType` | `"SolidBodyWithSkirt"` | Read back from Shawn's mesh #2. Two other options exist (`WithSkirt`, `SurfaceOnlyWithoutSkirt`). |
| `skirtLevel` (depth) | 100 ft / 30.48 m | Shawn's skirt was ~30 m. Could equally well be 5 ft, 50 ft. Purely cosmetic. |
| Perimeter strategy | concave hull of contour vertices | We tried PL layer first (the lot boundary); switched after observing Shawn's perimeter followed contour data extent, not property line. |
| `HULL_RATIO` | 0.2 | Tuning constant for Shapely's concave_hull. Looser values give simpler shapes (closer to a convex bbox); tighter values risk fragmentation. 0.2 produced 54 vertices vs. Shawn's 16, but the bbox matched. |
| Perimeter vertex Z | inherits its contour's Z (terrain-following) | Matches Shawn's pattern of perimeter Z varying with elevation. Earlier we used a flat base Z — that's also valid but produces a cliff at the boundary. |
| `CENTER_TO_ORIGIN` | True | Shawn translated his mesh to live near (0, 0). Could equally keep raw survey coords. |

### Arbitrary defaults that happened to work (2)
Probably don't matter, but worth flagging.

| Constant | Value | Reasoning |
|---|---|---|
| `floorIndex` | 0 (ground floor) | Default first story. Untested with other values. |
| ODA target DXF version | `"ACAD2018"` | Picked at random when wiring up the converter. Most modern DXF versions should work the same for our purposes. |

## What this means for productionization

The pilot demonstrates that **the data conversion itself is fully mechanical** — given a Foley-style DWG, the script reliably produces a correctly-shaped mesh. But to ship this as a tool for *any* PBW survey, the 11 inferred parameters need to either:

1. **Become explicit config** — a `pbw_topo_config.yaml` Shawn maintains, with the layer names, skirt preferences, hull aesthetics, etc.
2. **Become detected automatically** — e.g., scan all layers, find the ones with the most LWPOLYLINEs at varying Z (= contours).
3. **Become arguments** — `--skirt-depth 30 --hull-ratio 0.2 --center-to-origin`.

For a single-firm pilot (PBW only), option 1 is the smallest amount of work. For a "drop in any surveyor DWG" tool, option 2 is what would unlock generality.

**The bigger insight:** AI / LLM judgment is *not needed* in the geometry layer of this pipeline. Where AI does add value is in [[Research - Archicad MCPs|the orchestration]]: parsing free-form requests, surfacing the config knobs to the user in conversation, and explaining what choices the script is making. The mesh-building itself is deterministic Python.

Related: [[Source - Lot 44 Survey DWG]] for the data side, [[Research - Tapir Command Reference]] for the API side.

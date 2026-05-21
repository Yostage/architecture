# Source - Inferred Parameters in the Topo Pilot

What the pilot *reads from the input* vs. *invents as a constant* — i.e. how much is "data conversion" vs. "human intuition baked in." Done 2026-05-19 (after the v4 mesh matched Shawn's to <0.5%).

**Of ~14 distinct choices, only 3 are determined by the input geometry.** The other 11 are conventions encoded as constants: 3 from the surveyor, 6 from Shawn's example, 2 arbitrary.

## Read from the input (3) — the genuinely automatic part
| Parameter | Source |
|---|---|
| Contour polyline X,Y vertices | `LWPOLYLINE.get_points()` |
| Contour elevation per polyline | `LWPOLYLINE.dxf.elevation` |
| Contour data extent | derived from the above |

## Inferred from this surveyor's conventions (3) — break with a different firm
| Constant | Value | Why |
|---|---|---|
| `CONTOUR_LAYERS` | `{"CONT-HGH","CONT-NML"}` | Foley naming; others use `TOPO`, `CONTOUR`, `EL-100`… |
| `FOOT_TO_METER` applied unconditionally | 0.3048 | DXF `$INSUNITS=0` (unitless), but Z in the 9000s is clearly feet. Auto-detectable by magnitude; currently hard-coded. |
| Z lives on the polyline `elevation` attr | trusted | Some firms deliver flat-Z + label-only Z (needs OCR/matching). Foley does it right. |

## Inferred from Shawn's example (6) — change with PBW prefs / per-project
| Constant             | Value                                  | Source                                                                                      |
| -------------------- | -------------------------------------- | ------------------------------------------------------------------------------------------- |
| `skirtType`          | `"SolidBodyWithSkirt"`                 | read from Shawn's mesh (2 other options exist)                                              |
| `skirtLevel` (depth) | 100 ft / 30.48 m                       | Shawn's ~30 m; purely cosmetic                                                              |
| Perimeter strategy   | concave hull of contour vertices       | switched from PL layer after seeing his perimeter follows contour extent, not property line |
| `HULL_RATIO`         | 0.2                                    | Shapely concave_hull tuning; gave 54 vtx vs Shawn's 16, bbox matched                        |
| Perimeter vertex Z   | inherits contour Z (terrain-following) | matches Shawn; flat base Z also valid but makes a cliff                                     |
| `CENTER_TO_ORIGIN`   | True                                   | Shawn translated near (0,0); could keep raw coords                                          |

## Arbitrary defaults that happened to work (2)
`floorIndex = 0` (ground floor, untested otherwise); ODA target `"ACAD2018"` (picked at random; modern DXF versions equivalent here).

## For productionization
Data conversion itself is fully mechanical for a Foley-style DWG. To ship for *any* PBW survey, the 11 constants need to become **explicit config** (`pbw_topo_config.yaml` — smallest work for a single firm), **auto-detected** (scan layers for many-LWPOLYLINEs-at-varying-Z = contours — unlocks generality), or **CLI args**. **Key insight:** no LLM judgment is needed in the geometry layer — that's deterministic Python. AI's value is in [[Research - Archicad MCPs|orchestration]] (parsing requests, surfacing knobs conversationally). Related: [[Source - Lot 44 Survey DWG]], [[Research - Tapir Command Reference]].

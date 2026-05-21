# Source - Lot 44 Survey DWG (Shawn's "before" example)

Probed `survey topo test.dwg` (the **input** Shawn sent 2026-05-18) with ezdxf on 2026-05-19 — what a real surveyor delivery looks like. Companion `topo model example2.bpn` is the **after** (finished Archicad mesh).

## The site
Lot 44, Telluride Ski Ranches Filing 4C (Mountain Village, CO). Field-surveyed 2024-04-25 by Foley Associates (CO PLS #37970). Elevation **~9530–9614 ft**. 29 layers, 309 entities.

## Contour data (the load-bearing layers)
| Layer | Polylines | MTEXT | Z range | Step |
|---|---|---|---|---|
| `CONT-HGH` | 17 | 33 | 9530→9610 ft | 10 ft (index) |
| `CONT-NML` | 64 | 27 | 9532→9614 ft | 2 ft (minor) |

Plus `PTSPOT` (6 spot elevations), and decorative/contextual layers (buildings, trees, utilities, monuments, property lines, title block) — all ignorable for the mesh.

## Critical finding: contour Z is structured metadata, not just labels
Every contour polyline carries its elevation in its `LWPOLYLINE.dxf.elevation` (Z) attribute; the `MTEXT` labels are redundant human-readable copies. **Best case for automation** — no OCR, no label-to-line matching. Parse is ~20 lines of ezdxf. (Caveat: some surveyors deliver flat-Z polylines with elevation only in the label — the OCR-able worst case. Foley does it right; verify on other firms' DWGs before assuming.)

## End-to-end pilot — DONE 2026-05-19 (mesh), labels added later
DWG → DXF (ODA File Converter) → ezdxf parse → contours+Z → shapely concave-hull perimeter → ft→m → center to origin → `CreateMeshes` POST to Tapir (`127.0.0.1:19723`). Mesh dimensions match Shawn's example to **<0.5%** on every axis (X 150.0 vs 149.96 m, Y 107.59 vs 107.59 m, Z 56.33 vs 56.08 m). Contour-label step added later via forked Tapir `CreateTexts` — see [[Summary - Finishing the Pilot]].

```
.dwg → ODA → .dxf → ezdxf (~30 ln) → contours+Z + concave_hull (~5 ln)
     → ft→m → center → CreateMeshes JSON → POST → Archicad Mesh
```
Surface area: `dxf_to_createmeshes.py` (~190 ln) + `send_to_tapir.py` (~70 ln). No AI in the loop — pure data conversion.

## What we learned the hard way
1. **`level` is a Z offset, not a reference.** Per-vertex `z` is *added* to `level`. Sending absolute Z + a non-zero `level` doubles the altitude (v1 mesh ran Z=3→5834 m). Fix: keep coord Z relative to base, set `level` = absolute base (or `level=0` and center around it).
2. **`skirtLevel` is a positive depth, not absolute Z.** Pass `3.048` for a 10-ft skirt, not `base_z − 3.048`.
3. **Property line ≠ topo perimeter.** Surveys extend past the legal boundary. `shapely.concave_hull(pts, ratio=0.2)` of contour vertices gives the natural extent in one call, each hull vertex carrying its contour's Z (terrain-following). *(But the example2 teaching file uses the property line — genuinely ambiguous, ask Shawn. See [[Source - Proper Example2 Tutorial File]].)*
4. **Center to origin or you won't see it.** Survey coords are thousands of m from project origin → mesh lands outside default 3D view bounds. Subtract the centroid before sending.
5. **`SolidBodyWithSkirt` + deep (~30 m) skirt** is the natural residential look (per Shawn's example).
6. **Subline encoding (`SUBLINE_MODE`) is the converter half of the contour-line look.** `"polyline"` (current default) emits one connected subline per contour → Archicad stores them as user-defined ridges / level lines → clean contour lines (paired with the ridge-display setting). `"points"` (one subline per vertex) → Archicad free-TINs a smooth surface (matches the example's TIN look, which turned out to be Shawn's *stuck state*, not the goal). We switched to points in `3b40bd3`, then back to polyline once the goal was clear. Both carry the same 1185 samples; only connectivity differs. Canonical explanation: [[Summary - Finishing the Pilot]]; the look needs **both** the encoding and the display setting.

## Open questions for Shawn
Consolidated in [[Future Work]] (perimeter convention, skirt depth, Z-storage across surveyors, centering).

## Setup (reproducible)
- venv at `.venv` (Python 3.14.5), ezdxf 1.4.4.
- ODA File Converter 27.1.0 (`winget install ODA.ODAFileConverter`); cached DXF at `dxf_out/survey topo test.dxf`.
- Probe scripts: `probe_dxf.py` (inventory), `probe_contour_topology.py` (confirmed no closed contours → motivated hull). Pipeline: `dxf_to_createmeshes.py` + `send_to_tapir.py`; round-trip check `inspect_meshes.py`.

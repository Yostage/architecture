# Source - Lot 44 Survey DWG (Shawn's "before" example)

Probed `survey topo test.dwg` (the **before** file Shawn sent on 2026-05-18) using ezdxf on 2026-05-19. This is what a real surveyor delivery looks like for the topo pilot's input.

Companion file: `topo model example2.bpn` (the **after** — Archicad project with the finished 3D mesh).

## What the site is
- **Lot 44, Telluride Ski Ranches, Filing 4C** — Mountain Village, Colorado.
- Field-surveyed **2024-04-25** by Jeffrey C. Haskell, **Foley Associates, Inc.** (Colorado PLS #37970).
- File last touched 2026-05-08 in **AutoCAD Architecture 2015** by Shawn.
- Site bounded by Wapiti Road and Aspen Park Circle. Neighboring lots: 43, 45, 807-AR, 807-BR, 808.
- Elevation range: **~9530–9614 ft** (high-altitude — Telluride).
- Benchmark "CP BASE" at 9612.39 ft.

## File structure (29 layers, 309 entities, 1 modelspace)

### Contour data — the load-bearing layers
| Layer | Polylines | MTEXT labels | Z range | Step | Notes |
|---|---|---|---|---|---|
| `CONT-HGH` | **17 LWPolylines** | 33 labels | 9530 → 9610 ft | **10 ft** | Major/index contours |
| `CONT-NML` | **64 LWPolylines** | 27 labels | 9532 → 9614 ft | **2 ft** | Minor/intermediate contours |

Survey notes confirm: **"Contour interval is two feet."**

### Spot elevations
- `PTSPOT` layer: 6 MTEXT labels (`9613.09'`, `9612.70'`, `9612.35'`, etc.) + 6 circles + 12 lines.
- These are exact-point elevations (e.g., manhole rims, slab corners). The contours interpolate between them.

### Everything else (decorative / contextual)
- `E-BLDG` (existing buildings — line geometry)
- `E-TREES` (28 trees as block inserts; species/diameter in MTEXT — e.g. `40" SPRUCE`, `22" ASPEN`)
- `E-EP`, `E-TELE`, `E-WATER` (utilities — electric poles, CATV pedestals, fire hydrant)
- `MON` (13 survey monument blocks)
- `PL`, `PL-OTHR` (property lines + neighbor lot labels)
- `STREET` (street name MTEXT)
- `DESIGN` (a few lines + text — proposed-work artifacts)
- `WORDS`, `HEADING`, `LBL-LOT`, `north`, `VIEW`, `VIEWANG` — title block + legend + view annotations
- `CBD`, `ACAD_PROXY_ENTITY` — embedded proxy entities (probably Civil-3D objects from upstream surveyor tool)
- `Defpoints`, `0`, `INVISIBLE`, `MATCH`, `SCM`, `I` — Autodesk defaults + scratch

## The critical finding for the pilot

**Contour elevations are stored as structured metadata, not just text labels.**

Every contour polyline has its elevation in its `elevation` attribute (the LWPOLYLINE Z value). The matching `MTEXT` labels are redundant — they exist for the human reader, but the machine-readable Z is *already* on the polyline itself.

```
LWPOLYLINE on layer CONT-NML, elevation=9532.0, 12 vertices  ← Z is here
MTEXT on layer CONT-NML at point ..., text="9532"           ← human label, same value
```

This is the **best case** for automation:
- No OCR. No layer-name parsing. No label-to-polyline spatial matching.
- The script is essentially:
  ```python
  contours = [
      (lwpoly.get_points(), lwpoly.dxf.elevation)
      for lwpoly in msp.query("LWPOLYLINE[layer=='CONT-HGH' or layer=='CONT-NML']")
  ]
  ```
- Worth verifying on *more* surveyor DWGs before assuming this always holds. Some surveyors deliver contours as flat polylines (Z=0) with elevation only in the label — that's the OCR-able worst case. Foley Associates apparently does it the right way.

## What this means for the pilot architecture
- **Input parsing:** trivial. ~20 lines of ezdxf, no AI needed. Total automation candidate.
- **Mesh creation:** the polyline list + Z values is the exact shape Tapir's `CreateMeshes` should accept. (Schema for that command still needs verification — see [[Research - Tapir Command Reference]].)
- **Pre-step needed:** DWG → DXF via ODA File Converter. One-time per input file. Reliable.
- **Decorative layers can be ignored** for the mesh, but the surveyor block library (trees, monuments, utilities) might be a future automation candidate too — converting them into Archicad library objects.
- **Coordinate system note:** Z values are in feet (~9500). The mesh in Archicad needs the same units or a conversion. Confirm what unit system the `.pln` is set to before importing.

## Setup state (reproducible)
- Python venv at `D:\code\architecture\.venv` (Python 3.14.5).
- ezdxf 1.4.4 installed in venv.
- ODA File Converter 27.1.0 at `C:\Program Files\ODA\ODAFileConverter 27.1.0\ODAFileConverter.exe` (installed via `winget install ODA.ODAFileConverter`).
- Converted DXF cached at `D:\code\architecture\dxf_out\survey topo test.dxf`.
- Probe script at `D:\code\architecture\probe_dxf.py` — rerun with `.venv\Scripts\python.exe probe_dxf.py`.

## Open questions to resolve next
1. ~~**Does `CreateMeshes` accept ridge polylines with per-vertex Z, or only base-plane + per-node Z?**~~ **Resolved 2026-05-19.** Yes — it takes `sublines` as arrays of 3D coords. See [[Research - Tapir Command Reference]] for the schema. The pilot is a one-shot call, not a state machine.
2. ~~**What units is `topo model example2.bpn` configured for?**~~ **Resolved 2026-05-19.** `.pln` display unit is "feet and fractional inches" — matches the survey's feet. *But* Archicad's API **always** takes meters regardless of display unit (confirmed in Graphisoft community + API docs). So the prototype converts ft → m at the input boundary. 1 ft = 0.3048 m exactly. Survey Z range 9530–9614 ft → 2904.7–2930.4 m. X range 4984–5476 ft → 1519–1669 m. **Side effect:** the mesh will land ~1.5 km east of project origin — fine for a probe; can be offset to the project origin later via `SetGeoLocation` or a translation pass if it's awkward.
3. ~~**Mesh perimeter rule**~~ **Resolved 2026-05-19.** Tapir's `CreateMeshes` schema separates `polygonCoordinates` (the perimeter) from `sublines` (the interior contours) — the API enforces the distinction the manual workflow has to police by hand. Prototype now uses the **PL layer** as the perimeter: 4 LINEs + 1 ARC (50 ft radius, 83.6° sweep — the curve where Lot 44 meets the road). Assembly walks the segments by shared endpoints (with proximity clustering to absorb sub-mm precision noise at corners), tessellates the arc into 25 chord segments (~3 ft each), and emits 29 perimeter vertices. Caveat: contours may extend slightly beyond the lot lines (survey usually covers the road too); Archicad will probably clip sublines at the perimeter, but worth verifying when the mesh actually renders.

## Prototype state (2026-05-19)
- `dxf_to_createmeshes.py` — reads the DXF, emits the full `CreateMeshes` payload as JSON.
- Dry-run output:
  - **81 sublines** (matches 64 CONT-NML + 17 CONT-HGH)
  - **1,185 total subline vertices**
  - **43 unique elevations**, 9530.00 → 9614.00 ft
  - 4-pt bbox perimeter (placeholder)
  - 167 KB JSON
- Cached payload: `createmeshes_payload.json` — paste-ready for the Tapir endpoint once Archicad is running and a port is confirmed.

## End-to-end pilot status — DONE 2026-05-19
- ✅ DWG parsing
- ✅ DWG → DXF (ODA File Converter)
- ✅ DXF → CreateMeshes payload
- ✅ Units conversion (feet → meters)
- ✅ Concave-hull perimeter from contour vertices (matches Shawn's Magic-Wand workflow better than the PL layer)
- ✅ Centered to project origin
- ✅ POST to Tapir (port 19723, working)
- ✅ Verification — mesh dimensions match Shawn's example to **<0.5%** on every axis (X 150.0 vs 149.96 m, Y 107.59 vs 107.59 m, Z 56.33 vs 56.08 m)

## What we learned the hard way

1. **`CreateMeshes` `level` is a Z offset, not a reference.** Per-vertex `z` in `polygonCoordinates`/`sublines` is added to `level`. Sending absolute Z *plus* a non-zero `level` makes the mesh land at double altitude. v1 had mesh extending from Z=3 m to Z=5834 m. Fix: keep coord Z relative (0 at base) and set `level` to the absolute base — or set `level=0` and center everything around it.

2. **`skirtLevel` is a positive depth, not an absolute Z.** "Height of the skirt" in the schema is literal — pass `3.048` for a 10-ft skirt, not `base_z - 3.048`.

3. **Property line ≠ topo perimeter.** Property lines are a legal boundary; surveys extend past them (out to the road, the neighbor's edge). The right perimeter is the natural extent of the contour data. Concave hull (`shapely.concave_hull(pts, ratio=0.2)`) of all contour vertices does this in one call. Each hull vertex carries its source contour's Z, so the perimeter slopes with the terrain — same behavior as Shawn's manual Magic-Wand trace.

4. **Center to origin or you won't see it.** Surveyor's local coords are typically thousands of meters from any project origin. Sent as-is, the mesh is technically valid but lives outside Archicad's default 3D view bounds. Subtract the centroid before sending.

5. **`SolidBodyWithSkirt` + deep skirt (~30 m) is the natural-looking choice** for residential site topo, per Shawn's example.

6. **Subline encoding: single-point-per-vertex matches Shawn's visual style, not polyline-per-contour.** When we first sent sublines as polylines (one subline per contour, with multiple coords), Archicad respected the polyline connectivity and treated each contour as a *constrained ridge*. The resulting mesh had visible ridge bands following each contour line — geometrically faithful to the survey, but visibly sharper than Shawn's example. After switching to single-point sublines (each contour vertex emitted as its own one-coord subline), Archicad does a free TIN through the point cloud and produces the smooth-graded pancake look that matches Shawn's mesh. Verified via side-by-side screenshots 2026-05-19. Both encodings produce 1185 elevation samples in our data; the difference is whether Archicad knows they're connected. See [[Future Work]] for the option to revisit if anyone wants the higher-fidelity rendering.

## Pilot architecture (final)

```
.dwg
  → ODA File Converter             (one shell-out)
.dxf
  → ezdxf                          (~30 lines)
  → contour polylines + Z, lot data
  → shapely.concave_hull           (~5 lines)
  → terrain-following perimeter
  → ft → m conversion              (1 constant)
  → center to origin               (~10 lines)
CreateMeshes JSON payload
  → POST http://127.0.0.1:19723/   (1 urllib call)
Archicad 3D Mesh element
```

Total surface area: **dxf_to_createmeshes.py** (~190 lines) + **send_to_tapir.py** (~70 lines). No AI in the loop. Pure data conversion.

## Open questions for Shawn
1. Is **concave hull of contour data** an acceptable default perimeter, or does PBW have a convention (e.g., property line + 10-ft buffer, or always the road centerline)?
2. Skirt depth — is the **30 m / 100 ft** he used a deliberate choice for residential, or just whatever was handy?
3. Does the surveyor he works with **always store contour Z as polyline attribute** (true for Foley Associates), or do some deliver flat polylines + label-only Z?
4. Is **centering to project origin** the right default, or does PBW prefer keeping survey coords?

## Files involved (D:\code\architecture)
- `probe_dxf.py` — initial DXF inventory
- `probe_pl.py` — PL layer probe (now unused but kept for reference)
- `probe_contour_topology.py` — confirmed no closed contours, motivated hull approach
- `dxf_to_createmeshes.py` — the main pipeline
- `send_to_tapir.py` — POST/ping/fit/delete helpers
- `inspect_meshes.py` — round-trip verification
- `createmeshes_payload.json` — last generated payload
- `snapshots/{ours-v2, ours-v3, ours-v4, shawn}.json` — bbox + details snapshots for comparison

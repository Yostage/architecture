# Source - Proper Example2 (step-by-step tutorial file)

The `.pln` Shawn meant to send originally (he'd uploaded a backup `.bpn` by mistake; see [[Source - Shawn Topo Difference Video]]). Loaded 2026-05-20 via Tapir (port 19724) + three screenshots laid out as tutorial panels.

## What it is
A **simplified teaching file**, not the Lot 44 survey: a small (~36×15 m) rectangular lot, elevations rebased to round numbers (*"i set 100' at 0'"* → contours 100, 102 … 110). Tapir inventory: 2 Mesh (`TR-001`, `Site` — both SolidBodyWithSkirt, 9 sublines, 23-vertex perimeter), 3 Line, 36 Text, 16 Object. The "three pieces" are the three step-panels.

## The three steps (verbatim from the panels)
1. **"import survey linework and text"** — raw 2D contour polylines + elevation labels inside a dash-dot **property line** rectangle. No mesh.
2. **"add mesh to property boundary … press spacebar, click on polyline, select 'fit to all ridges' … repeat for each polyline."** — contours added to the mesh as ridges via Magic Wand.
3. **"Right click a contour node → 'z' value → assign elevation → assign to all."** — final: clean **black contour lines + elevation labels, no triangulation**, clipped to the property boundary. **The definitive desired output.**

## What it confirms / corrects
Confirms: output = mesh showing user-defined ridges (contour lines), not triangulation ✓; contour elevation labels are part of the deliverable ✓; our `"polyline"` subline approach mirrors his method (step 2 = one level line per contour, step 3 = subline Z) and our single `CreateMeshes` call does steps 2+3 at once ✓.

Corrects: **perimeter = the PROPERTY LINE here**, with contours clipped at it — not the concave hull we adopted. We switched to a hull because the *backup* `.bpn`'s mesh had an irregular 16-vertex perimeter (possibly a file artifact). Genuinely ambiguous which is PBW's standard → ask Shawn ([[Future Work]]).

## Status of the gaps it surfaced (all now closed)
The three things between us and a turnkey match to step 3 are resolved (see [[Summary - Finishing the Pilot]]):
1. **Display toggle** to user-defined ridges — done (tool-default inheritance + forked `CreateMeshes` `ridges` field).
2. **Contour labels** — done (forked `CreateTexts`, wired into `run_demo.py`).
3. **Perimeter source** (hull vs property line) — still the one open question; lean property line to match his method, confirm with Shawn.

## Is the "salmon" a crop of our Lot 44 DWG? No (confirmed 2026-05-20)
Scraped the example mesh's 9 contours (m→ft, translation-normalized) and matched against Lot 44 contours of equal point count: best matches 8–43 ft avg vertex deviation (a true crop would be sub-foot noise), error growing with line complexity — different curves, not the same line. **The salmon is a separate hand-built teaching dataset; no salmon DWG exists in or derivable from our files.** To reproduce it specifically we'd scrape the example mesh sublines, not look for a DWG. (Tested translation + reversal, not rotation; deviations make a rotated crop unlikely.)

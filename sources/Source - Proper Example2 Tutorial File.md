# Source - Proper Example2 (step-by-step tutorial file)

The `.pln` Shawn meant to send originally (he'd uploaded a backup `.bpn` by mistake; see [[Source - Shawn Topo Difference Video]]). Loaded and inspected 2026-05-20 via Tapir (port 19724) + three screenshots Shawn laid out as tutorial panels.

## What it actually is
**Not the full Lot 44 survey — a simplified teaching file** that walks the topo workflow in 3 steps on a small (~36 × 15 m) rectangular lot, with elevations rebased to round numbers (*"i set 100' at 0'"* → contours labeled 100, 102 … 110).

Tapir element inventory: **2 Mesh** (`TR - 001` 36.6×15.2×1.0 m; `Site` 36.6×15.2×6.1 m — both SolidBodyWithSkirt, 9 multi-point sublines, 23-vertex perimeter), 3 Line, 36 Text, 16 Object. The "three distinct pieces" you see are the three step-panels; only steps 2 and 3 carry meshes (step 1 is just linework + text).

## The three steps (verbatim from the panels)
1. **"step 1: import survey linework and text"** — raw 2D contour polylines (gray) with elevation labels (100–110) inside a dash-dot **property line** rectangle. No mesh yet.
2. **"1. add mesh to property boundary. 2. select mesh, select mesh tool, press spacebar, click on polyline, select 'fit to all ridges', click ok. repeat for each polyline."** — contours now olive = added to the mesh as ridges via Magic Wand.
3. **"Right click on a contour node and select the 'z' value icon … assign the elevation … select assign to all … i set 100' at 0'."** — final: clean **black contour lines + elevation labels, no triangulation**, clipped to the property boundary. **This is the definitive desired output.**

## Does it match our understanding? Mostly yes, with one correction
Confirms:
- **Output = mesh displaying user-defined ridges (contour lines), not triangulation.** ✓ (matches the video finding)
- **Contour elevation labels are part of the deliverable.** ✓ (the 100–110 labels — we flagged this; now confirmed)
- **Our polyline-subline approach mirrors his method exactly:** step 2 ("fit to all ridges" per polyline) = one level line per contour; step 3 ("assign elevation, assign to all") = the subline Z values. Our single `CreateMeshes` call does steps 2 + 3 together.

Corrects / re-opens:
- **Perimeter = the PROPERTY LINE, not a concave hull.** Step 2 is explicitly "add mesh to property *boundary*." Contours that run past the property line are simply clipped (visible in the screenshots — lines cross the dashed boundary and stop). We switched to a concave hull of contour vertices (commit history) because the *backup* `.bpn`'s big mesh had an irregular 16-vertex perimeter — but that may have been an artifact of that particular file. **This teaching file says property line.** Genuinely ambiguous which is the firm's standard → ask Shawn. See [[Future Work]].

## Implications for the pilot
- Our geometry creation already replicates the human steps 2 + 3 in one API call. Good.
- Three things stand between us and a turnkey match to step 3, all already tracked:
  1. **Display toggle** to "user-defined ridges" (tabled — not scriptable via current Tapir).
  2. **Contour labels** (not placed yet; data exists in the DWG MTEXT).
  3. **Perimeter source** — concave hull vs property line. Lean toward property line to match his method, but confirm.
- Net: this file *validates the target* and *confirms our method is the right shape*. It doesn't change that the remaining gaps are display + labels + the perimeter question.

("Salmon steak" = the visual: a clean rectangular mesh (the property boundary) with contour lines running through it like marbling. Matches the two rectangular teaching meshes Tapir found — no missing geometry.)

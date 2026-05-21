# Source - YouTube: ArchiCAD Topography (Arch Guide)

**Title:** ArchiCAD Tutorial: Create Topography - The EASY way
**Channel:** Arch Guide
**Length:** ~4 min
**Topic:** Using the **Mesh Tool** to create site topography / 3D terrain.

This is the tutorial Shawn linked as the *current manual process* for candidate #1 (3D topo from survey). Captured here as the baseline we'd be automating against.

## Manual process per the video

1. **Mesh tool basics** — works in 2D and 3D; start by creating a rectangular site mesh.
2. **Trace contours with Magic Wand** — `Spacebar + Click` on existing contour lines to trace them onto the mesh, picking up survey linework.
3. **Elevate points** — select a node, use *Elevate Mesh Point* from the pet palette, type the height.
4. **"Apply to All" checkbox** — when setting height for a contour line, this moves every node on that line to the same elevation in one shot. The critical productivity tip in the video.
5. **Boundary warning** — do NOT use *Apply to All* on the perimeter of the mesh; it flattens the entire edge to one elevation and destroys the slope.
6. **Mountainous terrain** — same workflow, just layer more contour levels.

## Synthesis vs. Shawn's email
- Shawn's email lists the same skeleton (import 2D lines → create mesh → eyedrop each line → delete lines) but at a coarser grain.
- The video's **Magic Wand + Apply-to-All** combo is the human productivity hack. Any automation needs to at least match it; ideally it eliminates the per-contour click+type cycle entirely.
- The **boundary edge case** is real: an automated tool has to distinguish "interior contour" from "perimeter node" or it'll silently flatten the site.

## Implications for automation
The *information* is already in the survey:
- Each contour line has an implicit Z (its label / layer / metadata).
- The mesh has a fixed perimeter that should NOT be touched.

So a topo automation should: parse contour lines + their elevation labels → snap to the mesh → set Z per contour → leave perimeter alone. That's a one-shot script, not even an AI task. AI would shine if elevation has to be inferred from CAD layer naming, line color conventions, or PDF surveys.

## Link
Original message link was a tracking redirect (dead). Find by title: "ArchiCAD Tutorial: Create Topography - The EASY way" (Arch Guide). Shawn's email also links a topo-process video: https://www.youtube.com/watch?v=1OprRjQEEiA

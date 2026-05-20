# Source - Shawn's "topo mesh difference" explainer video

Shawn recorded a 74-second screen-capture (`topo mesh differnce explanation.mp4`, sent 2026-05-20) explaining why our auto-generated mesh isn't drawing-set-ready. Transcribed locally with faster-whisper + frames sampled via ffmpeg on 2026-05-20.

## Transcript (verbatim)

> The main difference between what you generated, which I was able to do similarly with a script, is that it just shows a **triangulated mesh**, which is a quick import out of the box — which is nice, but to make it part of the drawing, **it needs to show just the topo lines and not the triangulation**.
>
> This was a step-by-step: import the 2D linework, create a mesh, **assign the topo lines to the mesh**, and then input the elevational information. So you can use this in the **site plan**, and you still have **editable nodes**, and you still have the **3D model**.
>
> And I just can't figure out how to do that without going through this process in Archicad — which involves manipulating 2D and 3D elements and inputting data, which it doesn't seem like the AI can do.

## What the frames show
- **~6 s (frame 003):** Plan view of the auto-generated TIN mesh — a dense web of triangulation lines covering the whole site. This is "ours" (and Shawn's equivalent script output). Quick, but unusable in a drawing.
- **~48 s (frame 024):** The DESIRED output — site plan with clean **topographic contour lines labeled by elevation** (100, 102, 104 … 110) and the property line. **No triangulation visible.** On-screen instruction: *"Right click on a contour node and select the 'z' value icon … assign the elevation … select assign to all … repeat for each contour. i set 100' at 0'."* Toolbar shows mesh model-view option "All Ridges Smooth."
- **~62 s (frame 031):** The 2D contour linework input stage — raw survey polylines + property line, before mesh creation.

## The actual requirement (this changes the pilot target)
Shawn's `topo model example2` mesh is **his stuck state, not his goal.** The real deliverable is a mesh that:
1. **Displays clean topographic contour lines** in plan (for the site plan drawing), NOT the triangulation.
2. Keeps **editable nodes**.
3. Keeps the **3D model**.

The triangulated TIN (what we built after switching to single-point sublines in commit `3b40bd3`) is explicitly the *wrong* output for production — it's only "ok for general design reference."

## Why this *might* be tractable for us (hypothesis, not yet verified)
- The clean-contour-line display likely comes from building the mesh with **contour polylines as user-defined ridges / level lines** — which is our *original* polyline-subline encoding (abandoned to match his TIN look). See [[Source - Lot 44 Survey DWG]] finding #6 and [[Future Work]] item on the `--ridges` flag. **Untested whether this alone reproduces frame 024.**
- Shawn believes the geometry creation is impossible via automation: *"AI sucks at MAKING anything"* (today) and *"[Tapir] can't create plines, it can only place AC objects"* (May 11). We *have* shown `CreateMeshes` works and can carry level lines — so the *creation* half is further along than he thinks. That's encouraging, but it's not the same as having produced his drawing-ready output.

## Open unknowns — results from testing 2026-05-20
1. **Does polyline-subline encoding make Archicad store contours as level lines?** ✅ **YES.** Sent the polyline payload (`SUBLINE_MODE = "polyline"`), read back via `GetDetailsOfElements`: all 82 sublines came back as multi-point level lines (2–40 pts each), zero exploded to single points. The structural prerequisite holds.
2. **Is there a display setting that shows level lines and hides triangulation in 2D plan?** ✅ **YES, it exists** (confirmed via Graphisoft community + tested manually). Mesh Settings → **Floor Plan and Section** panel → **"Show User-Defined Ridges"** (not "All Ridges"). 3D equivalent: Model panel → **"All Ridges Smooth."** Frame 024's toolbar showed "All Ridges Smooth," consistent.
3. **Does the 2D plan render clean contour lines?** 🟡 **Only after the manual toggle.** Out of the box, the created mesh's plan view showed **triangulation** (default = "Show All Ridges"). After manually switching to "User-Defined Ridges," it shows clean contour lines. So the geometry is right; the default display mode is wrong.
4. **Editable nodes / single mesh?** ✅ Single mesh element, nodes editable (standard Archicad mesh behavior).

## The remaining boundary: display setting is NOT scriptable via current Tapir
- `GetDetailsOfElements` does **not** expose the ridge-display flag (readback is identical before/after the manual change).
- `CreateMeshes` schema has no display field; `SetDetailsOfElements` only takes floor/layer/drawIndex/typeSpecificDetails. Searched `ElementCommands.cpp` for "ridge"/"contour"/"showLines" → **zero matches.** Tapir doesn't wrap it.
- The flag exists in Archicad's C++ `API_MeshType`, so it's a wrappable gap, not a hard limit.
- **Likely no-code workaround (UNTESTED, tabled 2026-05-20):** element creation inherits the **Mesh tool default** settings. If the tool default — or a PBW **Favorite** applied via Tapir's `ApplyFavoritesToElementDefaults` — is set to "User-Defined Ridges," new meshes should be born with clean-contour display. Worth testing later. See [[Future Work]].

## Also flagged: contour elevation labels
Frame 024 shows numbered contours (100, 102, … 110) + "property line." Shawn's narration only says "input the elevational information" (the Z heights, which we do), but a real site plan needs visible **contour labels**. Our pipeline discards the survey's `MTEXT` elevation labels (catalogued in [[Source - Lot 44 Survey DWG]]). Adding them is a data-we-already-have task — place via Tapir `CreateLabels` at each contour's MTEXT position. Confirm with Shawn whether he wants them auto-placed. See [[Future Work]].

## Net status
We can **create** the correct drawing-ready geometry (level-line mesh) fully programmatically. The two remaining gaps to a turnkey drawing-set output are both **tabled, not solved**: (a) the ridge-display toggle isn't scriptable via current Tapir (workaround via tool-default inheritance is plausible but untested), and (b) contour labels aren't placed yet.

(Frames + audio in `video_out/`, gitignored. This transcript is the durable artifact.)

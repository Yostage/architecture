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

## Why this is good news for us
- The clean-contour-line display comes from building the mesh with **contour polylines as user-defined ridges / level lines** — which is exactly our *original* polyline-subline encoding (the one we abandoned to match his TIN look). See [[Source - Lot 44 Survey DWG]] finding #6 and [[Future Work]] item on the `--ridges` flag.
- Shawn believes this is impossible via automation: *"AI sucks at MAKING anything"* (today) and *"[Tapir] can't create plines, it can only place AC objects"* (May 11). **Both are wrong** — our `CreateMeshes` pipeline works, and the polyline-subline encoding produces level lines, which is the structure he needs.
- The remaining unknown: getting the **mesh display set so plan shows level lines and hides triangulation**. Likely a Model View Option ("mesh display: user-defined ridges") + the mesh's own settings. Need to test whether Tapir can set it, or whether it's a project-level MVO toggle.

## Next test
Build the mesh from polyline-sublines (level lines = contours), then drive the mesh/MVO display to "topo lines only" and check the **2D plan view** matches frame 024. If it does, we've solved the exact thing Shawn got stuck on.

(Frames + audio in `video_out/`, gitignored. This transcript is the durable artifact.)

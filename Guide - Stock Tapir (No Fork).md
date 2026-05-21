# Guide - Stock Tapir (No Fork)

How to run the topo pilot on **public/stock Tapir**, without Scott's forked build. This is the expected path for Shawn. The geometry still works end-to-end; two display niceties become manual.

## What needs the fork (and what doesn't)

`CreateMeshes` itself is **stock** (Tapir 1.1.9+), so the core pilot — building the terrain mesh from the survey — works without the fork. Only these are fork-only:

| Step / feature | Command | Stock? |
|---|---|---|
| Build payloads from DXF | `dxf_to_createmeshes.py` (pure Python) | ✅ no Archicad needed |
| Sanity-check Tapir | `GetAddOnVersion` (`ping`) | ✅ stock |
| Clear prior output | `GetElementsByType` + `DeleteElements` (`clear`) | ✅ stock |
| Create the mesh | `CreateMeshes` (`send-mesh`) | ✅ stock |
| Clean contour-line display | `ridges` / `showLines` payload fields | ❌ **fork only** |
| Place elevation labels | `CreateTexts` (`send-texts`) | ❌ **fork only** |
| Frame it in the window | `FitInWindow` (`fit_latest_mesh.py`) | ✅ stock |

## The two degradations & how to handle them

### 1. Clean contour lines instead of triangulation

The generated mesh payload sets `ridges=UserDefined` and `showLines=true` — fork-only fields. On stock Tapir these are unrecognized, and depending on how strict your Tapir build is it will either **ignore** them (mesh still created, but it shows triangulation) or **reject** the whole payload. Either way, do this:

1. **Emit a stock-compatible payload.** Open `dxf_to_createmeshes.py` and set the toggle near the top:
   ```python
   STOCK_TAPIR = True
   ```
   When `True`, the two fork-only fields are omitted automatically — no hand-editing of the JSON. (Default is `False` = fork payload.)
2. **Get the clean look from the Mesh tool default instead.** Before running, in Archicad with **nothing selected**, open the **Mesh tool default settings** and set it to show **User-Defined Ridges** with **All Ridges Smooth**, then **save the project**. Meshes created afterward inherit that display, so the plan shows clean contour lines rather than the triangulated facets. This is the manual equivalent of what `ridges`/`showLines` do automatically on the fork.

### 2. Contour elevation labels

`CreateTexts` is fork-only, so the `send-texts` step **fails on stock Tapir**. But the label data is still generated: `createtexts_payload.json` lists every label's **text value and its position (x, y in meters)**. Use it as a key to **place the labels by hand** with Archicad's Text/Label tool. (Coordinates are centered to the project origin, matching where the mesh lands.)

## Step-by-step (stock run)

Run the steps individually rather than `run_demo.py` (which calls the fork-only `send-texts` and would error partway):

```
python dxf_to_createmeshes.py        # 1. build payloads (set STOCK_TAPIR = True first — see above)
python send_to_tapir.py ping         # 2. confirm Tapir answers
python send_to_tapir.py clear        # 3. clear prior meshes/texts/labels
python send_to_tapir.py send-mesh    # 4. create the mesh
                                      # 5. (skip send-texts) place labels by hand using createtexts_payload.json
python fit_latest_mesh.py            # 6. frame the mesh in the window
```

> Note: `run_demo.py` runs all steps including `send-texts`. If you run it on stock Tapir, the mesh is created first and the run errors only at the texts step — not catastrophic, but the steps above are cleaner.

## Net result without the fork

You still get the real deliverable — a property-line terrain mesh with clean contour-line display — just with **labels placed manually** and a **one-time Mesh-tool-default setup** instead of fully scripted. If Shawn wants the fully-automated version (auto labels, no manual default step), that needs Scott's forked Tapir; see [[Source - Tapir Fork Build Setup]] and the upstreaming status in [[Future Work]].

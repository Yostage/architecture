# Guide - Stock Tapir (No Fork)

How to run the topo pilot on **public/stock Tapir** — no forked build required.

> **Resolved (2026-06-01):** The whole pilot now runs on stock Tapir. **Tapir 1.5.0** shipped all three commands the pilot needed:
> - `CreateTexts` — ENZYME-APD#391 (elevation labels)
> - `CreateMeshes` `ridges` / `showLines` — #395 (clean contour-line display)
> - `ChangeWindow` + `navigatorItemId` — #398 (activate a saved view)
>
> **On Tapir 1.5.0 or newer, `run_demo.py` runs end-to-end with no workarounds.** The scripts call these as real APIs unconditionally. The rest of this guide — the two manual degradations — now applies **only if you're stuck on an older Tapir (≤1.4.x)**. The recommended fix is simply to **update Tapir to 1.5.0+**.

## Check your Tapir version

`python send_to_tapir.py ping` prints `GetAddOnVersion`. If it's **1.5.0 or newer**, you're done — just run `python run_demo.py`. If it's **1.4.x or older**, either update Tapir (recommended) or follow the legacy workarounds below.

## Running on current Tapir (1.5.0+)

```
python run_demo.py
```

Every step is stock: `CreateMeshes` with line-display fields, `CreateTexts` for labels, `FitInWindow`. No manual Archicad steps, no payload editing.

---

## Legacy: running on Tapir ≤ 1.4.x

`CreateMeshes` itself has been stock since Tapir 1.1.9, so the core pilot — building the terrain mesh from the survey — always worked. On Tapir releases **before 1.5.0**, only these two display features are missing:

| Step / feature | Command | Stock ≤1.4.x? |
|---|---|---|
| Build payloads from DXF | `dxf_to_createmeshes.py` (pure Python) | ✅ no Archicad needed |
| Sanity-check Tapir | `GetAddOnVersion` (`ping`) | ✅ stock |
| Clear prior output | `GetElementsByType` + `DeleteElements` (`clear`) | ✅ stock |
| Create the mesh | `CreateMeshes` (`send-mesh`) | ✅ stock |
| Clean contour-line display | `ridges` / `showLines` payload fields | ❌ 1.5.0+ only |
| Place elevation labels | `CreateTexts` (`send-texts`) | ❌ 1.5.0+ only |
| Frame it in the window | `FitInWindow` (`fit_latest_mesh.py`) | ✅ stock |

### The two degradations & how to handle them

#### 1. Clean contour lines instead of triangulation

The generated mesh payload sets `ridges=UserDefined` and `showLines=true`. On Tapir ≤1.4.x these fields are unrecognized, and depending on how strict your build is it will either **ignore** them (mesh still created, but it shows triangulation) or **reject** the whole payload. Workaround:

1. **Strip the two fields from the payload by hand.** The scripts no longer have a toggle for this (they target 1.5.0+); on old Tapir, after running `dxf_to_createmeshes.py`, delete the `"ridges"` and `"showLines"` lines from `createmeshes_payload.json` before sending. (Or just update Tapir.)
2. **Get the clean look from the Mesh tool default instead.** In Archicad with **nothing selected**, open the **Mesh tool default settings**, set it to show **User-Defined Ridges** with **All Ridges Smooth**, then **save the project**. Meshes created afterward inherit that display, so the plan shows clean contour lines rather than triangulated facets. This is the manual equivalent of what `ridges`/`showLines` do automatically.

#### 2. Contour elevation labels

`CreateTexts` doesn't exist on Tapir ≤1.4.x, so the `send-texts` step **fails**. But the label data is still generated: `createtexts_payload.json` lists every label's **text value and its position (x, y in meters)**. Use it as a key to **place the labels by hand** with Archicad's Text/Label tool. (Coordinates are centered to the project origin, matching where the mesh lands.)

### Step-by-step (legacy ≤1.4.x run)

Run the steps individually rather than `run_demo.py` (which calls `send-texts` and would error partway):

```
python dxf_to_createmeshes.py        # 1. build payloads (then strip ridges/showLines from the JSON)
python send_to_tapir.py ping         # 2. confirm Tapir answers
python send_to_tapir.py clear        # 3. clear prior meshes/texts/labels
python send_to_tapir.py send-mesh    # 4. create the mesh
                                      # 5. (skip send-texts) place labels by hand using createtexts_payload.json
python fit_latest_mesh.py            # 6. frame the mesh in the window
```

> Note: `run_demo.py` runs all steps including `send-texts`. On old Tapir the mesh is created first and the run errors only at the texts step — not catastrophic, but the steps above are cleaner.

## Bottom line

On **Tapir 1.5.0+** you get the full deliverable — a property-line terrain mesh with clean contour-line display and auto-placed labels — fully scripted. On older Tapir you get the same mesh, with labels placed manually and a one-time Mesh-tool-default setup. The fork is no longer required for any of this; see [[Source - Tapir Fork Build Setup]] for build history and the upstreaming record in [[Notes - Tapir Upstreaming]].

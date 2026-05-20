# Future Work

Captured during the topo pilot build (2026-05-18 → 2026-05-19). Items here are either gaps we hit, deferred improvements, or natural extensions. Roughly ordered by leverage.

## Asks of Shawn / PBW
Concrete questions to bring to the next conversation (copied from [[Source - Lot 44 Survey DWG]] for visibility):

1. Is **concave hull of contour data** an acceptable default perimeter, or does PBW have a convention (e.g., property line + 10-ft buffer, road centerline)?
2. Is the **30 m / 100 ft skirt** in the example file a deliberate residential default, or just one-off styling?
3. Do PBW's surveyors **always store contour Z as a polyline attribute** (Foley Associates does), or does anyone deliver flat-Z polylines with elevation only in the `MTEXT` label?
4. Is **centering to project origin** the right default, or do you keep raw survey coords?

## Tapir extensions we'd want
Gaps we found in the API that, if filled, would close the demo loop further. All are tractable C++ add-on extensions on top of the existing Tapir codebase (see [[Research - Tapir Command Reference]]).

1. **`Set3DProjection`** — set the live 3D camera's eye/target/view-cone/perspective-vs-parallel. Today there's `Set3DCutPlanes` and `FitInWindow` but no way to scripted-orient the camera. Underlying ACAPI exposes this; Tapir just hasn't wrapped it. *Hours of work.*
2. **`CreateView`** — save the current window's state as a named entry in the View Map. Tapir creates Layouts/Subsets/Drawings/Details/Worksheets but not Views. Without this we can't auto-create demo viewpoints. *Hours of work.*
3. **Saved-view activation via `ChangeWindow`** — current `ChangeWindow` only switches *window types*; it can't apply a saved View's settings (camera, layer combo, scale). Either extend `ChangeWindow` to accept a navigator-item ID, or add a sibling `OpenView` command. See `go_to_view.py` for the regression marker. *Hours of work.*

## Pilot productionization
Turning the topo pilot from a working demo into a tool PBW can actually use.

1. **Config layer for the 11 inferred parameters.** Out of ~14 distinct choices in the script, only 3 are read from the input ([[Source - Pilot Inferred Parameters]]). The other 11 (layer names, skirt depth/type, hull ratio, centering, etc.) are baked-in constants. Pick: `pbw_topo_config.yaml`, CLI args, or auto-detect heuristics — depending on Shawn's answers above.
2. **Surveyor-conventions auto-detect.** Scan all DWG layers; classify ones with many LWPOLYLINEs at varying Z as contour layers; flag others as decorative. Would let the pilot ingest any surveyor's DWG without hand-configured layer names.
3. **Auto-detect units.** Currently hardcoded `FOOT_TO_METER = 0.3048`. DXF `$INSUNITS` was unitless in this file; a magnitude sniff (Z values in the thousands → feet; tens → meters) would handle the common cases.
4. **Generality test against a second surveyor's DWG.** Foley Associates stores contour Z on the polyline attribute (best case). Confirm the pilot works on at least one other firm's delivery before claiming it as "general."
5. **OCR / label-matching variant** of the pilot for surveys with flat-Z polylines + `MTEXT` elevation labels. Probably needed for some surveyors. Spatial label-to-polyline matching is the core algorithm.

6. **Polyline-subline mode as a fidelity option.** The pilot currently emits one subline per contour vertex (matches Shawn's free-TIN visual style). Earlier we tried one subline per polyline (preserving the surveyor's contour-line connectivity as constrained ridges in Archicad) — the resulting mesh had visible ridge bands following each contour, geometrically more faithful but visually sharper. Worth keeping as a `--ridges` flag for cases where surveyor-fidelity matters more than matching PBW's house style. The change is a one-function diff in `extract_contour_sublines`. See [[Source - Lot 44 Survey DWG]] for the verified-by-screenshot finding.

## Other Archicad pilots Shawn flagged
From [[Email - Archicad Bizniss]], in priority order per Shawn:

1. **Interior Elevation setup** (his pick for "highest bang for buck"). Bonus: Shawn's example file already contains 4 Interior Elevation markers we noticed during `inspect_all` — that file is *also* a candidate demo for this pilot. Ground for the next probe.
2. **Detail import / generation.** v1: pull standard details from a library. v2: parametrically generate details from wall/floor assembly inputs. The v2 ask is where AI value-add is highest; v1 is closer to template-fetching.

## Contour elevation labels (blocked on a Tapir gap)
The drawing-set output needs elevation numbers on each contour (frame 024). We extract them fine — the survey's `MTEXT` labels on `CONT-HGH`/`CONT-NML` give text + position, and `dxf_to_createmeshes.py` emits a `CreateLabels` payload (`send_to_tapir.py send-labels`). **But Tapir's `CreateLabels` can't place clean standalone text** (verified 2026-05-20): with only a `text` field it creates an empty label shell with **no library part bound** (null GUID, GDL params unreadable), so nothing renders except a stray leader line to the origin — "rays from origin," no visible numbers. Tried recreating after setting a no-leader label default; no change (the missing library-part binding is the root cause, not the leader). Paths forward:
1. **Tapir extension / different command** — needs a way to bind a text-label library part (e.g. the "General Label" / text GDL) when creating, or a true `CreateText` command. Tapir has no `CreateText` today.
2. **Tool-default + favorite** — possibly assign a working text-label favorite to the Label tool default first, then create; untested and may still not bind via the API.
3. **Place as a different element** — e.g., draw the labels as text inside the DWG→DXF stage and import differently. Out of current scope.
Until one of these, labels stay a **manual step** and are not run by `run_demo.py`.

## Demo polish
Smaller things that would make the live demo crisper.

1. **Auto-create a "Demo View" in the new project** so each demo run lands at a known camera angle, not at floor-plan default. Blocked on the `CreateView` Tapir extension above.
2. **Single-command setup** for a fresh checkout: a script that `py -m venv .venv && pip install -r requirements.txt && python ODA_check.py && python regenerate_dxf.py` so a teammate can clone and run in one go.
3. **Make `dxf_to_createmeshes.py` testable** — add a smoke test that loads a known DXF and asserts the output payload's dimensions match the snapshot, so future refactors don't silently regress.

## Wiring into Claude / MCP
The pilot today is a pair of Python scripts. To turn it into the demo Shawn imagines ("AI does the topo from a survey"), the natural next move:

1. **Drop the pipeline into the Tapir MCP server** ([[Research - Archicad MCPs]] — `SzamosiMate/tapir-archicad-MCP` is the recommended one). Define a `topo_from_survey` MCP tool that takes a DWG path and runs the pipeline. Then Claude (Desktop or Code) can call it directly from a chat.
2. **Claude Agent SDK / Claude Code slash command** — `/topo-mesh <dwg-path>` that wraps the same pipeline. Lower setup cost than MCP for a single user; same outcome.

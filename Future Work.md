# Future Work

Captured during the topo pilot build (2026-05-18 → 2026-05-19). Items here are either gaps we hit, deferred improvements, or natural extensions. Roughly ordered by leverage.

## Asks of Shawn / PBW
Concrete questions to bring to the next conversation (copied from [[Source - Lot 44 Survey DWG]] for visibility):

1. Is **concave hull of contour data** an acceptable default perimeter, or does PBW have a convention (e.g., property line + 10-ft buffer, road centerline)?
2. Is the **30 m / 100 ft skirt** in the example file a deliberate residential default, or just one-off styling?
3. Do PBW's surveyors **always store contour Z as a polyline attribute** (Foley Associates does), or does anyone deliver flat-Z polylines with elevation only in the `MTEXT` label?
4. Is **centering to project origin** the right default, or do you keep raw survey coords?

## Tapir extensions — IMPLEMENTED 2026-05-20 (pending validation)
All six gaps below were implemented on the fork (branch `tapir-backlog-commands`, pushed to github.com/Yostage/tapir-archicad-automation), compiling green. **Runtime validation deferred** — needs deploy + Archicad restart + `Test/test_examples.py`. See [[Source - Tapir Fork Build Setup]] for specifics.

1. ✅ **`Set3DProjection`** — perspective camera (eye/target/viewCone/rollAngle) via `ACAPI_View_Change3DProjectionSets`. *(Verify: azimuth/distance derivation from camera→target; needs a 3D window.)*
2. ✅ **`CreateView`** — save current window to the View Map (`ACAPI_Navigator_NewNavigatorView`). *(Verify: "save current window" semantics; root placement only — subfolder parent is a follow-up.)*
3. ✅ **`OpenView`** — activate a saved view (GetNavigatorItem → `ACAPI_Database_ChangeCurrentDatabase`). Replaces the `ChangeWindow` limitation noted in `go_to_view.py`.
4. ✅ **`CreateTexts`** — standalone Text elements; closes the contour-label gap (below).
5. ✅ **`CreateMeshes` ridge fields** (`ridges`/`showLines`) — drawing-set display at creation; removes the tool-default-inheritance workaround once validated.
6. ✅ **`SetModelViewOptions`** — apply a named MVO (`ACAPI_Navigator_ChangeViewOptions`).

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

## Contour elevation labels — addressed by CreateTexts (pending validation)
The drawing-set output needs elevation numbers on each contour (frame 024). We extract them fine — the survey's `MTEXT` labels on `CONT-HGH`/`CONT-NML` give text + position, and `dxf_to_createmeshes.py` emits a payload. The original blocker: Tapir's `CreateLabels` couldn't place clean standalone text (empty label shell, no library part bound → "rays from origin," no visible numbers; the missing library-part binding was the root cause, not the leader).

**Resolved by the new `CreateTexts` command** (2026-05-20, [[Source - Tapir Fork Build Setup]]): it creates standalone `API_TextID` Text elements with proper text-memo handling — no leader, no library-part dependency. Once the fork is deployed and validated, the pilot's label step switches from `CreateLabels` to `CreateTexts` (place a text at each contour's MTEXT position). Until validated, labels remain a manual step in the stock-Tapir pipeline.

## Demo polish
Smaller things that would make the live demo crisper.

1. **Auto-create a "Demo View" in the new project** so each demo run lands at a known camera angle, not at floor-plan default. Blocked on the `CreateView` Tapir extension above.
2. **Single-command setup** for a fresh checkout: a script that `py -m venv .venv && pip install -r requirements.txt && python ODA_check.py && python regenerate_dxf.py` so a teammate can clone and run in one go.
3. **Make `dxf_to_createmeshes.py` testable** — add a smoke test that loads a known DXF and asserts the output payload's dimensions match the snapshot, so future refactors don't silently regress.

## Wiring into Claude / MCP
The pilot today is a pair of Python scripts. To turn it into the demo Shawn imagines ("AI does the topo from a survey"), the natural next move:

1. **Drop the pipeline into the Tapir MCP server** ([[Research - Archicad MCPs]] — `SzamosiMate/tapir-archicad-MCP` is the recommended one). Define a `topo_from_survey` MCP tool that takes a DWG path and runs the pipeline. Then Claude (Desktop or Code) can call it directly from a chat.
2. **Claude Agent SDK / Claude Code slash command** — `/topo-mesh <dwg-path>` that wraps the same pipeline. Lower setup cost than MCP for a single user; same outcome.

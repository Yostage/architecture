# Future Work

Captured during the topo pilot build (2026-05-18 → 2026-05-19). Items here are either gaps we hit, deferred improvements, or natural extensions. Roughly ordered by leverage.

## Asks of Shawn / PBW
Concrete questions to bring to the next conversation (copied from [[Source - Lot 44 Survey DWG]] for visibility):

1. Is **concave hull of contour data** an acceptable default perimeter, or does PBW have a convention (e.g., property line + 10-ft buffer, road centerline)?
2. Is the **30 m / 100 ft skirt** in the example file a deliberate residential default, or just one-off styling?
3. Do PBW's surveyors **always store contour Z as a polyline attribute** (Foley Associates does), or does anyone deliver flat-Z polylines with elevation only in the `MTEXT` label?
4. Is **centering to project origin** the right default, or do you keep raw survey coords?

## Tapir extensions — IMPLEMENTED + VALIDATED 2026-05-20; CreateTexts upstreamed 2026-05-21
All six gaps below were implemented on the fork (branch `tapir-backlog-commands`, github.com/Yostage/tapir-archicad-automation). **5 of 6 validated working** against the deployed fork; CreateView is WIP (item 2). **CreateTexts — the pilot-critical one — is split into a clean upstream PR ([ENZYME-APD#391](https://github.com/ENZYME-APD/tapir-archicad-automation/pull/391)), green across the AC25–29 × Win+Mac matrix, marked ready for review.** The other four are queued as follow-up per-command PRs. See [[Source - Tapir Fork Build Setup]] and [[Summary - Finishing the Pilot]].

1. ✅ **`Set3DProjection`** — VALIDATED 2026-05-20 (perspective, from a 3D window).
2. 🔧 **`CreateView`** — implemented but `NewNavigatorView` returns `0x8106006a`; WIP. **Next:** seed `sourceGuid`/`itemType` from the current Project-Map navigator item before the call. Lowest value (OpenView covers navigation). See [[Source - Tapir Fork Build Setup]].
3. ✅ **`OpenView`** — VALIDATED 2026-05-20 (activated an existing view). Replaces the `ChangeWindow` limitation in `go_to_view.py`.
4. ✅ **`CreateTexts`** — VALIDATED 2026-05-20; closes the contour-label gap (below).
5. ✅ **`CreateMeshes` ridge fields** (`ridges`/`showLines`) — VALIDATED 2026-05-20; lets the pilot set the drawing-set display at creation instead of the tool-default trick.
6. ✅ **`SetModelViewOptions`** — VALIDATED 2026-05-20 (applied a named MVO).

**Cleanups:** ✅ global `ADDON_VERSION` bumped to 1.4.2 (was 1.4.0 while the commands were already 1.4.2). ⬜ Still open: make the reload loop hands-off by suppressing the startup "load assets from library" modal (see [[Source - Tapir Fork Build Setup]]).

## Pilot productionization
Turning the topo pilot from a working demo into a tool PBW can actually use.

1. **Config layer for the 11 inferred parameters.** Out of ~14 distinct choices in the script, only 3 are read from the input ([[Source - Pilot Inferred Parameters]]). The other 11 (layer names, skirt depth/type, hull ratio, centering, etc.) are baked-in constants. Pick: `pbw_topo_config.yaml`, CLI args, or auto-detect heuristics — depending on Shawn's answers above.
2. **Surveyor-conventions auto-detect.** Scan all DWG layers; classify ones with many LWPOLYLINEs at varying Z as contour layers; flag others as decorative. Would let the pilot ingest any surveyor's DWG without hand-configured layer names.
3. **Auto-detect units.** Currently hardcoded `FOOT_TO_METER = 0.3048`. DXF `$INSUNITS` was unitless in this file; a magnitude sniff (Z values in the thousands → feet; tens → meters) would handle the common cases.
4. **Generality test against a second surveyor's DWG.** Foley Associates stores contour Z on the polyline attribute (best case). Confirm the pilot works on at least one other firm's delivery before claiming it as "general."
5. **OCR / label-matching variant** of the pilot for surveys with flat-Z polylines + `MTEXT` elevation labels. Probably needed for some surveyors. Spatial label-to-polyline matching is the core algorithm.

6. **Subline encoding is a `SUBLINE_MODE` switch in `dxf_to_createmeshes.py`** (`extract_contour_sublines`). The pilot now defaults to **`"polyline"`** — one connected subline per contour, which Archicad stores as user-defined ridges / level lines; this is what produces the clean contour-line drawing-set output (paired with the ridge-display setting). The **`"points"`** mode (one subline per vertex → Archicad free-TINs a smooth surface, matching the example file's TIN look) remains as the alternative. We oscillated between them — commit `3b40bd3` switched to points to match Shawn's example before his video clarified that the smooth TIN was his *stuck state, not the goal*, so we switched back. Promote `SUBLINE_MODE` to a `--tin`/`--ridges` CLI flag if both outputs are wanted. See [[Source - Lot 44 Survey DWG]] and [[Summary - Finishing the Pilot]].

## Other Archicad pilots Shawn flagged
From [[Email - Archicad Bizniss]], in priority order per Shawn:

1. **Interior Elevation setup** (his pick for "highest bang for buck"). Bonus: Shawn's example file already contains 4 Interior Elevation markers we noticed during `inspect_all` — that file is *also* a candidate demo for this pilot. Ground for the next probe.
2. **Detail import / generation.** v1: pull standard details from a library. v2: parametrically generate details from wall/floor assembly inputs. The v2 ask is where AI value-add is highest; v1 is closer to template-fetching.

## Contour elevation labels — RESOLVED by CreateTexts (validated 2026-05-20, wired into run_demo)
The drawing-set output needs elevation numbers on each contour (frame 024). We extract them fine — the survey's `MTEXT` labels on `CONT-HGH`/`CONT-NML` give text + position, and `dxf_to_createmeshes.py` emits a payload. The original blocker: Tapir's `CreateLabels` couldn't place clean standalone text (empty label shell, no library part bound → "rays from origin," no visible numbers; the missing library-part binding was the root cause, not the leader).

**Resolved by the new `CreateTexts` command** (validated 2026-05-20, [[Source - Tapir Fork Build Setup]]): it creates standalone `API_TextID` Text elements with proper text-memo handling — no leader, no library-part dependency. The pilot's label step now uses `CreateTexts` (a text at each contour's MTEXT position), folded into the single `run_demo.py` flow (the "send-texts" step). `CreateTexts` is the command upstreamed as [ENZYME-APD#391](https://github.com/ENZYME-APD/tapir-archicad-automation/pull/391).

## Demo polish
Smaller things that would make the live demo crisper.

1. **Auto-create a "Demo View" in the new project** so each demo run lands at a known camera angle, not at floor-plan default. Blocked on the `CreateView` Tapir extension above.
2. **Single-command setup** for a fresh checkout: a script that `py -m venv .venv && pip install -r requirements.txt && python ODA_check.py && python regenerate_dxf.py` so a teammate can clone and run in one go.
3. **Make `dxf_to_createmeshes.py` testable** — add a smoke test that loads a known DXF and asserts the output payload's dimensions match the snapshot, so future refactors don't silently regress.

## Wiring into Claude / MCP
The pilot today is a pair of Python scripts. To turn it into the demo Shawn imagines ("AI does the topo from a survey"), the natural next move:

1. **Drop the pipeline into the Tapir MCP server** ([[Research - Archicad MCPs]] — `SzamosiMate/tapir-archicad-MCP` is the recommended one). Define a `topo_from_survey` MCP tool that takes a DWG path and runs the pipeline. Then Claude (Desktop or Code) can call it directly from a chat.
2. **Claude Agent SDK / Claude Code slash command** — `/topo-mesh <dwg-path>` that wraps the same pipeline. Lower setup cost than MCP for a single user; same outcome.

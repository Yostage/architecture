# Future Work

Gaps, deferred improvements, and extensions from the topo pilot build (2026-05-18 → 2026-05-21). Roughly ordered by leverage.

## Asks of Shawn / PBW
1. Is **concave hull of contour data** an acceptable default perimeter, or does PBW have a convention (property line + buffer, road centerline)? *(The example2 teaching file uses the property line — see [[Source - Proper Example2 Tutorial File]].)*
2. Is the **30 m / 100 ft skirt** a deliberate residential default or one-off styling?
3. Do PBW's surveyors **always store contour Z as a polyline attribute** (Foley does), or does anyone deliver flat-Z polylines with label-only elevation?
4. Is **centering to project origin** the right default, or keep raw survey coords?

## Tapir extensions — DONE (status; detail in [[Source - Tapir Fork Build Setup]])
All six implemented on the fork; **5/6 validated** (CreateView the holdout). Upstream status as of 2026-05-27:
- ✅ **`CreateTexts`** — merged [ENZYME-APD#391](https://github.com/ENZYME-APD/tapir-archicad-automation/pull/391).
- 🟡 **`OpenView`** — draft PR [ENZYME-APD#394](https://github.com/ENZYME-APD/tapir-archicad-automation/pull/394); fork CI matrix 10/10 green, awaiting maintainer review.
- 🟡 **`CreateMeshes` line-display fields** (`ridges`, `showLines`, plus expansion `contourPen`, `levelPen`, `lineTypeIndex`) — draft PR [ENZYME-APD#395](https://github.com/ENZYME-APD/tapir-archicad-automation/pull/395); fork CI 10/10 green, awaiting maintainer review. **Once merged + shipped, the full topo demo runs on stock Tapir** (this PR closes the last pilot-critical gap; the others are non-pilot primitives).
- 🔧 **`CreateView`** — `NewNavigatorView` returns `0x8106006a`; WIP, lowest value (OpenView covers navigation). **Next:** seed `sourceGuid`/`itemType` from the current Project-Map item before the call. Not in the upstream queue.
- **Queued per-command PRs:** Set3DProjection, SetModelViewOptions (both non-pilot primitives; lower urgency).
- ⬜ **Reload loop not hands-off:** suppress the startup "load assets from library" modal (pre-embed library, or use a project that doesn't trigger it).

*(Contour-label gap — RESOLVED by the forked `CreateTexts`, wired into `run_demo.py`. See [[Summary - Finishing the Pilot]].)*

## Pilot productionization
Turning the demo into a tool PBW can use. Only 3 of ~14 choices are read from input ([[Source - Pilot Inferred Parameters]]); the other 11 are baked-in constants.
1. **Config layer for the 11 inferred params** — `pbw_topo_config.yaml`, CLI args, or auto-detect, depending on Shawn's answers above.
2. **Surveyor-conventions auto-detect** — classify layers with many LWPOLYLINEs at varying Z as contours; ingest any DWG without hand-configured layer names.
3. **Auto-detect units** — magnitude sniff (Z in thousands → feet; tens → meters) instead of hardcoded `FOOT_TO_METER`.
4. **Generality test against a second surveyor's DWG** before claiming "general."
5. **OCR / label-matching variant** for surveys with flat-Z polylines + `MTEXT` labels (spatial label-to-polyline matching).
6. **Subline encoding** is a `SUBLINE_MODE` switch (`dxf_to_createmeshes.py`): default `"polyline"` (level lines → contour-line output) vs `"points"` (free-TIN smooth). Promote to a `--tin`/`--ridges` CLI flag if both outputs are wanted. See [[Source - Lot 44 Survey DWG]] #6.

## Other Archicad pilots Shawn flagged ([[Email - Archicad Bizniss]])
1. **Interior Elevation setup** — his "highest bang for buck." Bonus: his example file already has 4 IE markers (noticed via `inspect_all`); good ground for the next probe.
2. **Detail import / generation** — v1 pull from a library (template-fetching); v2 parametrically generate from assembly inputs (highest AI value-add).

## Demo polish
1. **Auto-create a "Demo View"** so each run lands at a known camera angle. Blocked on `CreateView` (above).
2. **Single-command setup** for a fresh checkout (venv + install + ODA check + regenerate DXF).
3. **Make `dxf_to_createmeshes.py` testable** — smoke test asserting payload dimensions match a snapshot.

## Wiring into Claude / MCP
1. **Drop the pipeline into the Tapir MCP server** ([[Research - Archicad MCPs]], `SzamosiMate/tapir-archicad-MCP`) as a `topo_from_survey` tool taking a DWG path.
2. **Claude Code slash command** `/topo-mesh <dwg-path>` wrapping the same pipeline — lower setup cost for a single user.

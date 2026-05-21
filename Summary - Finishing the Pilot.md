# Summary — Finishing the Pilot

What it took to get the topo-from-survey pilot from "working demo with one manual step" to fully functional, and to send the key piece upstream. 2026-05-18 → 2026-05-21. Details: [[Source - Tapir Fork Build Setup]], [[Future Work]], [[Source - Lot 44 Survey DWG]].

## The blocker: contour labels
By 2026-05-19 the pilot was geometrically complete — `run_demo.py` built a topo mesh from the DWG matching Shawn's example to <0.5% on every axis. The one gap: the drawing-set needs each contour's **elevation number** (frame 024). We extract them fine (the survey's `MTEXT` labels). The blocker was Tapir: **`CreateLabels` can't place clean standalone text** — with no library part bound it makes an empty label shell ("rays from origin," no numbers). Stock Tapir had no plain-Text command. So finishing meant **extending Tapir**, which meant building it from source.

## 1. From-source Tapir build (the prerequisite)
Forked `ENZYME-APD/tapir-archicad-automation` → `D:\code\tapir-fork`, compiling to `TapirAddOn_AC29_Win.apx`. Toolchain was most of the effort, with one key gotcha: **VS 2026 installs the v180 toolset, but the AC29 DevKit hard-`#error`s unless v143** (`Definitions.hpp:149`, needs `1930 ≤ _MSC_VER < 1950`) — had to add the "MSVC v143" component. Plus CMake 4.3.2 (knows the VS 2026 generator) and the AC29 API DevKit. Full toolchain + install-pain notes in [[Source - Tapir Fork Build Setup]].

## 2. Six commands (the one that closes the gap + five more)
On branch `tapir-backlog-commands`, registered at v1.4.2 with examples:
1. **`CreateTexts`** — *load-bearing.* Standalone `API_TextID` Text via the CreateLabels memo path; no leader, no library-part dependency. What the label step needed.
2. **`CreateMeshes` ridge fields** (`ridges`/`showLines`) — set the "user-defined ridges only" display at creation.
3. **`Set3DProjection`** — perspective camera (new file `ProjectionCommands.cpp`; CMake globs `Sources/`).
4. **`CreateView`** — save window to View Map *(WIP, see below)*.
5. **`OpenView`** — activate a saved view; replaces the `ChangeWindow` limit.
6. **`SetModelViewOptions`** — apply a named MVO.

## 3. Reload/validate loop
User-writable `Deploy\` folder registered in the Add-On Manager (official Tapir removed) so the fork hot-loads without UAC; `reload_and_test.py` drives save→quit→redeploy→relaunch→test. **Caveat:** `TestProject.pla` pops a modal "load assets from library" dialog that blocks the JSON API, so the loop isn't fully hands-off; the `.apx` lock also lingers briefly after the API drops, so the deploy-copy retries.

## 4. Validation — 5 of 6
Against the deployed fork: ✅ CreateTexts (incl. multi-line; the risky memo path passed first try — **label gap closed**), ✅ CreateMeshes ridges, ✅ Set3DProjection, ✅ SetModelViewOptions, ✅ OpenView. ❌ **CreateView** — `NewNavigatorView` returns `0x8106006a`; the bare `API_NavigatorItem` needs `sourceGuid`/`itemType` seeded from the current Project-Map item. WIP, lowest value (OpenView covers navigation).

## 5. Cross-version CI
The fork inherited upstream's **Mac × Win × AC25–29** matrix; with only the AC29 DevKit locally, version issues surfaced only in CI. `ACAPI_View_*3DProjectionSets`, `ACAPI_Navigator_NewNavigatorView`, `ACAPI_Navigator_*ViewOptions` don't exist in older DevKits → guarded those three Execute bodies at `#if defined(ServerMainVers_2900)` with a stub (**those 3 are AC29-only**) + `(void)parameters;` for MSVC `/WX`. CreateTexts, the mesh ridge fields, and OpenView build on all versions unchanged.

## 6. Wire into the pilot
Label step switched from `CreateLabels` to `CreateTexts` (a Text at each contour's MTEXT position), folded into `run_demo.py` ("send-texts"). The contour-line **look** needs two halves: the converter's `SUBLINE_MODE="polyline"` encoding (level-line geometry) **and** the ridge-display setting (`ridges=UserDefined`, now in the payload) — neither alone reproduces frame 024. Pilot is now complete end-to-end.

## 7. Upstream the key piece (2026-05-21)
Upstream merges one command per PR, so the messy dev branch is split into clean per-command branches off `origin/main`.
- **PR #391** — `feat(texts): add CreateTexts` — https://github.com/ENZYME-APD/tapir-archicad-automation/pull/391 — one commit (4 files, +175/−0), no other-command contamination; CreateView WIP and `build_ac29.bat` dropped. Ready for review.
- The Yostage repo had to be **deleted and re-forked** (it was a standalone repo, not a real fork → cross-repo PRs blocked).
- **Verified green on the full AC25–29 × Win+Mac matrix** by running CI in the fork (first-time-contributor PRs can't trigger upstream CI without a maintainer's approval click).

## What remains
- **Pilot productionization** ([[Future Work]]): config layer for the 11 baked-in params, surveyor-conventions + units auto-detect, second-DWG generality test, MCP/slash-command wiring. None block the demo.
- **Upstream:** four more per-command PRs queued (CreateMeshes ridges, Set3DProjection, OpenView, SetModelViewOptions); CreateView stays WIP.
- **Ask Shawn:** perimeter convention, skirt default, Z-storage, centering ([[Future Work]]).

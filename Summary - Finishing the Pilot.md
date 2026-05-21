# Summary — Finishing the Pilot

What it actually took to get the topo-from-survey pilot from "working demo with one
manual step" to "fully functional," and to send the key piece upstream. Spans
2026-05-18 → 2026-05-21. Details live in [[Source - Tapir Fork Build Setup]],
[[Future Work]], and [[Source - Lot 44 Survey DWG]]; this is the through-line.

## The one thing standing in the way: contour labels

By 2026-05-19 the pilot was geometrically complete — `run_demo.py` built a topo mesh
from the survey DWG end-to-end, matching Shawn's example file to <0.5% on every axis.
The single remaining gap was the drawing-set requirement that **each contour show its
elevation number** (frame 024). We already extracted the numbers fine (the survey's
`MTEXT` labels on `CONT-HGH`/`CONT-NML` give text + position).

The blocker was Tapir itself: **`CreateLabels` can't place clean standalone text.** With
no library part bound it produced an empty label shell ("rays from origin," no visible
numbers) — the missing library-part binding was the root cause, not the leader. Stock
Tapir had no command to place a plain Text element. So finishing the pilot meant
**extending Tapir**, which meant building it from source.

## 1. Stand up a from-source Tapir build (the unglamorous prerequisite)

Forked `ENZYME-APD/tapir-archicad-automation` to `D:\code\tapir-fork` and got it
compiling locally to `TapirAddOn_AC29_Win.apx`. The toolchain was most of the effort:

- **VS 2026 Build Tools (v18)** + C++ workload — the CMake generator is
  `"Visual Studio 18 2026"`.
- **The v143 gotcha (key blocker):** VS 2026 installs the v180 toolset, but the AC29
  DevKit hard-`#error`s unless v143 is used (`Definitions.hpp:149`, requires
  `1930 ≤ _MSC_VER < 1950`). Had to add the individual component "MSVC v143 - VS 2022
  C++ build tools." v180 is a compile-time block, not an ABI gamble — decision recorded
  to stay on v143.
- **CMake 4.3.2** (knows the VS 2026 generator) + the **AC29 API DevKit** (public GitHub
  download, unzipped to `Build/DevKits/AC29`).
- Install pain worth remembering: don't launch the VS installer detached (corrupts the
  instance); winget won't `--add` components to an already-registered product — use the
  VS Installer GUI. Full notes in [[Source - Tapir Fork Build Setup]].

## 2. Build the command that closes the gap (plus five more)

Implemented six backlog commands on branch `tapir-backlog-commands`, registered in
`AddOnMain.cpp` at v1.4.2, each with an example in `Examples/`:

1. **`CreateTexts`** — *the load-bearing one.* Standalone `API_TextID` Text elements with
   proper text-memo handling (reuses the CreateLabels memo path; no leader, no
   library-part dependency). This is what the pilot's label step needed.
2. **`CreateMeshes` ridge fields** (`ridges`/`showLines`) — sets the drawing-set
   "user-defined ridges only" display *at creation*, replacing a tool-default-inheritance
   trick.
3. **`Set3DProjection`** — perspective camera (`ProjectionCommands.cpp`, a new file;
   CMake globs `Sources/` so it's auto-picked up).
4. **`CreateView`** — save current window to the View Map *(see WIP below)*.
5. **`OpenView`** — activate a saved view; replaces the `ChangeWindow` limitation in
   `go_to_view.py`.
6. **`SetModelViewOptions`** — apply a named MVO.

## 3. Make a tight reload/validate loop

Set up a user-writable `Deploy\` folder registered in Archicad's Add-On Manager (official
Tapir removed from Program Files) so the fork hot-loads without UAC. `reload_and_test.py`
drives save → clean-quit → redeploy → relaunch → test. **Caveat:** relaunching with
`TestProject.pla` pops a modal "load assets from library" dialog that blocks the JSON API,
so the loop isn't fully hands-off for this project; the `.apx` file lock also lingers
briefly after the API goes down, so the deploy-copy retries until it releases.

## 4. Validation — 5 of 6 working

Against the deployed fork (`127.0.0.1:19723`):
- ✅ **CreateTexts** — created Text elements incl. multi-line; the riskiest (memo
  allocation) passed first try. **Contour-label gap closed.**
- ✅ CreateMeshes ridges/showLines, ✅ Set3DProjection, ✅ SetModelViewOptions,
  ✅ OpenView — all confirmed.
- ❌ **CreateView** — `NewNavigatorView` returns `0x8106006a` even from a savable window;
  the bare `API_NavigatorItem` needs `sourceGuid`/`itemType` seeded from the current
  Project-Map item. **WIP, lowest value** (OpenView covers navigation).

## 5. Cross-version CI

The fork inherited upstream's **Mac × Windows × AC25–29** matrix. Having only the AC29
DevKit locally, version issues only surfaced in CI:
- `ACAPI_View_*3DProjectionSets`, `ACAPI_Navigator_NewNavigatorView`, and
  `ACAPI_Navigator_*ViewOptions` don't exist in older DevKits → guarded those three
  Execute bodies at `#if defined(ServerMainVers_2900)` with a "requires Archicad 29" stub.
  **Those three are AC29-only**; the others compile everywhere.
- MSVC `/WX` flags unused parameters (C2220) in the stub branches → `(void) parameters;`.
- **CreateTexts, the mesh ridge fields, and OpenView build on all versions unchanged** —
  including the pilot-critical CreateTexts.

## 6. Wire it into the pilot

With CreateTexts validated, the pilot's label step switches from `CreateLabels` to
`CreateTexts` — place a Text at each contour's MTEXT position — folded into the single
`run_demo.py` flow. The pilot is now functionally complete end-to-end, labels included.

## 7. Upstream the key piece (2026-05-21)

Cleaned the messy multi-command dev branch into a single focused PR for the load-bearing
command (upstream merges one command per PR):
- New branch `feat/create-texts` off `origin/main`, one clean
  `feat(texts): add CreateTexts command…` commit (4 files, +175/−0), no contamination
  from the other commands, CreateView WIP and the personal `build_ac29.bat` dropped.
- The Yostage repo had to be **deleted and re-forked** — it was a standalone repo, not a
  real GitHub fork, so cross-repo PRs were blocked.
- Verified **green across the full AC25–29 × Win+Mac matrix** by running CI in the fork
  (first-time-contributor PRs can't trigger upstream CI without a maintainer's approval).
- **PR #391** — https://github.com/ENZYME-APD/tapir-archicad-automation/pull/391 — open,
  marked ready for review. Awaiting maintainer approval + merge.

## What remains

- **Pilot:** productionization items in [[Future Work]] — config layer for the 11 baked-in
  parameters, surveyor-conventions auto-detect, units auto-detect, second-DWG generality
  test, MCP/slash-command wiring. None block the demo.
- **Tapir upstream:** four more per-command PRs queued (CreateMeshes ridges,
  Set3DProjection, OpenView, SetModelViewOptions); CreateView stays WIP on
  `tapir-backlog-commands`.
- **Open questions for Shawn/PBW** (perimeter convention, skirt default, Z-storage,
  centering) — listed in [[Future Work]] and [[Source - Lot 44 Survey DWG]].

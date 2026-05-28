# Source - Tapir Fork Build Setup

Local from-source build of the Tapir add-on (2026-05-20) so we can extend it ([[Future Work]] gaps — `CreateTexts` for labels, mesh display flag, etc.). Narrative arc in [[Summary - Finishing the Pilot]]; this is the reproducible detail.

## Where
- Fork: `D:\code\tapir-fork` (upstream `ENZYME-APD/tapir-archicad-automation`).
- Output: `archicad-addon/Build/AC29/RelWithDebInfo/TapirAddOn_AC29_Win.apx` (~2.7 MB).
- AC29-only build helper `Tools/build_ac29.bat` (stock `build_all_win.bat` builds all of 25–29; we only need 29). *Not upstreamed — local only.*

## Toolchain (what had to be installed)
1. **VS 2026 Build Tools (v18)** + C++ workload (`Microsoft.VisualStudio.Workload.VCTools`). The generator is `"Visual Studio 18 2026"`.
2. **v143 toolset — THE KEY GOTCHA.** VS 2026's VCTools installs **v180** (MSVC 14.51), but the AC29 DevKit hard-`#error`s unless v143 (`Support/Modules/GSRoot/Definitions.hpp:149`, requires `1930 ≤ _MSC_VER < 1950`). Add the component "MSVC v143 - VS 2022 C++ x64/x86 build tools" (MSVC 14.44). v180 is a compile-time block, not an ABI gamble — and no newer DevKit supports it, so we stay on v143.
3. **CMake 4.3.2** (`Kitware.CMake`, machine scope) — recent enough to know the VS 2026 generator.
4. **AC29 API DevKit** — public GitHub download, no login: `archicad-api-devkit/releases/.../API.Development.Kit.WIN.29.3000.zip`, unzipped to `Build/DevKits/AC29`.

## Install pain (so we don't repeat it)
- **Don't launch the VS installer detached** (`Start-Process … -Verb RunAs` without `-Wait`) → left a corrupted half-bootstrapped instance, had to repair via the GUI.
- **winget won't `--add` components to an already-registered product** (returns "already installed", skips). Use the VS Installer GUI (Modify → Individual components → search "v143").
- `setup.exe` has no `--wait` flag (winget-only) → exit 87 if passed.

## Build commands (reproducible)
```powershell
cd D:\code\tapir-fork\archicad-addon\Tools
python download_and_unzip.py https://github.com/GRAPHISOFT/archicad-api-devkit/releases/download/29.3000/API.Development.Kit.WIN.29.3000.zip ../Build/DevKits/AC29
cmake -B ../Build/AC29 -G "Visual Studio 18 2026" -A x64 -T v143 -DAC_VERSION=29 -DAC_API_DEVKIT_DIR="..\Build\DevKits\AC29\Support" ..
cmake --build ../Build/AC29 --config RelWithDebInfo
```
Iteration loop: edit `Sources/*Commands.cpp` + register in `AddOnMain.cpp` → incremental `cmake --build` → copy `.apx` to the Deploy folder → restart Archicad (~30–60 s, the slow step) → test via Python.

## Six backlog commands (2026-05-20) — registered at v1.4.2, examples in `Examples/`
1. **CreateTexts** — standalone Text (`API_TextID`), reuses CreateLabels memo path. Closes the contour-label gap. (`ElementCreationCommands.cpp`)
2. **CreateMeshes ridge fields** — `ridges` (AllSharp/AllSmooth/UserDefined → `smoothRidges`) + `showLines`; sets the drawing-set display at creation.
3. **Set3DProjection** — `ACAPI_View_Change3DProjectionSets` (`ProjectionCommands.cpp`, new file; CMake auto-globs `Sources/`).
4. **CreateView** — `ACAPI_Navigator_NewNavigatorView` (`NavigatorCommands.cpp`).
5. **OpenView** — GetNavigatorItem → `ACAPI_Database_ChangeCurrentDatabase`. *(Switched to `ACAPI_View_GoToView` during upstreaming and renamed to **GoToView** — see [[Notes - Tapir Upstreaming]].)*
6. **SetModelViewOptions** — `ACAPI_Navigator_ChangeViewOptions`.

## Validation (2026-05-20, against the deployed fork via Deploy-folder hot-load)
User-writable `Deploy\` registered in Archicad's Add-On Manager (official Tapir removed) so the fork loads without UAC. **5 of 6 working:**
- ✅ **CreateTexts** — created Text incl. multi-line; riskiest (memo) passed first try. **Label gap closed.**
- ✅ CreateMeshes `ridges:"UserDefined"`+`showLines`, ✅ Set3DProjection, ✅ SetModelViewOptions ("01 Site"), ✅ OpenView ("Site" view) *(later renamed GoToView)*.
- ❌ **CreateView** — `NewNavigatorView` returns `0x8106006a` even from a savable window. Fixed two masking bugs (set nav item `db` to current; relaxed response schema so the real error surfaces) but create still fails — bare `API_NavigatorItem` needs `sourceGuid`/`itemType` from the current Project-Map item. WIP, lowest value.

## Cross-version CI (Mac × Win × AC25–29, green 2026-05-20)
Only had the AC29 DevKit locally, so version issues showed only in CI:
- `ACAPI_View_*3DProjectionSets`, `ACAPI_Navigator_NewNavigatorView`, `ACAPI_Navigator_*ViewOptions` absent from older DevKits → guarded those three Execute bodies at `#if defined(ServerMainVers_2900)` + "requires AC29" stub. **Those 3 are AC29-only** (threshold could drop if confirmed on an older DevKit).
- MSVC `/WX` flags unused params (C2220) in the stubs → `(void) parameters;` (clang ignored via `-Wno-unused-parameter`, so Mac passed first).
- **CreateTexts, mesh ridge fields, and OpenView (now GoToView) build on all versions unchanged.**

**Reload-loop caveat:** relaunching with `TestProject.pla` pops a modal "load assets from library" dialog that blocks the JSON API until dismissed — loop isn't fully hands-off. Archicad also holds the `.apx` lock briefly after the API drops, so the deploy-copy retries. To fully automate: pre-embed the library, or use a project that doesn't trigger the dialog.

## Upstreaming (2026-05-21)
One command per PR (upstream convention) → clean per-command branches off `origin/main`.
- **First PR: `CreateTexts`** — [ENZYME-APD#391](https://github.com/ENZYME-APD/tapir-archicad-automation/pull/391), branch `feat/create-texts`, single `feat(texts):` commit (4 files, +175/−0). CreateView WIP + `build_ac29.bat` dropped (kept on `tapir-backlog-commands`).
- **Fork deleted and re-forked** — `Yostage/tapir-archicad-automation` was a standalone repo, not a real GitHub fork, so cross-repo PRs were blocked until re-forked.
- **Verified green on the full AC25–29 × Win+Mac matrix** by running CI in the fork (first-time-contributor PRs can't trigger upstream CI without maintainer approval). PR marked ready for review.
- **Queued:** CreateMeshes ridges, Set3DProjection (AC29-guarded), OpenView (later renamed GoToView), SetModelViewOptions (AC29-guarded).
- Global `ADDON_VERSION` bumped 1.4.0 → 1.4.2 (was lagging the per-command versions), committed to the dev branch with `reload_and_test.py`.

## Upstreaming status, conventions, review patterns
See **[[Notes - Tapir Upstreaming]]** for the current PR-by-PR status, the inferred upstream conventions (one-per-PR, draft-first, fork-side CI iteration), the maintainer's review patterns (no duplicated blocks, no `static_cast` to API types, match the nearest sibling command), and per-command lessons learned. This file (Source -) is just the local build/deploy mechanics; that file (Notes -) is the active state of the upstreaming initiative.

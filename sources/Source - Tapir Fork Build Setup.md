# Source - Tapir Fork Build Setup (local builds working)

Stood up a local build of the Tapir add-on from source on 2026-05-20, so we can extend it (the gaps in [[Future Work]] — `CreateTexts` for labels, mesh display flag, etc.). Confirmed: produces `TapirAddOn_AC29_Win.apx` (2.7 MB).

## Where
- Fork cloned at `D:\code\tapir-fork` (upstream `ENZYME-APD/tapir-archicad-automation`).
- Build output: `D:\code\tapir-fork\archicad-addon\Build\AC29\RelWithDebInfo\TapirAddOn_AC29_Win.apx`.
- AC29-only build helper added: `archicad-addon/Tools/build_ac29.bat` (stock `build_all_win.bat` builds all of 25–29; we only need 29).

## Toolchain (what actually had to be installed)
1. **VS 2026 Build Tools** — winget `Microsoft.VisualStudio.BuildTools` (v18). The CMake generator the build uses is `"Visual Studio 18 2026"`, so it wants v18 specifically.
2. **C++ workload** (`Microsoft.VisualStudio.Workload.VCTools`).
3. **v143 toolset** — THE KEY GOTCHA. On VS 2026 the VCTools workload installs the **v180** toolset (MSVC 14.51), but the **AC29 DevKit hard-`#error`s unless v143 is used** (`Support/Modules/GSRoot/Definitions.hpp:149`). Had to add the individual component **"MSVC v143 - VS 2022 C++ x64/x86 build tools"** (installs MSVC 14.44.35207). Building with v180 fails outright — not an ABI gamble, a compile-time block.
4. **CMake 4.3.2** — winget `Kitware.CMake` (machine scope; user scope had "no applicable installer"). Needs to be recent enough to know the `Visual Studio 18 2026` generator (4.3.2 does; it's even the default).
5. **AC29 API DevKit** — public GitHub download, no login: `archicad-api-devkit/releases/download/29.3000/API.Development.Kit.WIN.29.3000.zip`. Unzipped to `Build/DevKits/AC29`; CMake points at its `Support` subdir.
6. Python (already present) — used by the DevKit's resource-compile step.

## Install pain notes (so we don't repeat them)
- **Don't launch the VS installer detached.** First attempt (`Start-Process winget -Verb RunAs` without `-Wait`) left a half-bootstrapped, corrupted instance (`_Instances` empty, modify → exit 1, no logs). Had to repair via the VS Installer GUI.
- **winget won't add components to an already-registered product** — it returns "already installed" and skips `--add`. Use the VS Installer GUI (Modify) or `setup.exe modify` for components.
- **`setup.exe` has no `--wait` flag** (that's a winget-override flag) → exit 87 if passed.
- The GUI (Modify → Individual components → search "v143") was the reliable path for adding toolsets when the CLI fought us.

## Build commands (reproducible)
```powershell
# one-time: DevKit
cd D:\code\tapir-fork\archicad-addon\Tools
python download_and_unzip.py https://github.com/GRAPHISOFT/archicad-api-devkit/releases/download/29.3000/API.Development.Kit.WIN.29.3000.zip ../Build/DevKits/AC29

# configure + build (CMake on PATH at C:\Program Files\CMake\bin)
cmake -B ../Build/AC29 -G "Visual Studio 18 2026" -A x64 -T v143 -DAC_VERSION=29 -DAC_API_DEVKIT_DIR="..\Build\DevKits\AC29\Support" ..
cmake --build ../Build/AC29 --config RelWithDebInfo
```
Output `.apx` → deploy by copying into `C:\Program Files\GRAPHISOFT\Archicad 29\Add-Ons\` (elevated), restart Archicad. Same place we put the official build earlier.

## Iteration loop (for adding a command)
edit `Sources/*Commands.cpp` + register in `AddOnMain.cpp` → `cmake --build ... --config RelWithDebInfo` (incremental, fast) → copy `.apx` to Add-Ons → restart Archicad → test via our Python (`send_to_tapir.py`). Restart is the slow step (~30–60 s).

## Status
Build environment is fully working. Next: write `CreateTexts` (the contour-labels gap — see [[Source - Shawn Topo Difference Video]] and [[Future Work]]) as the first real extension, since labels are the one remaining gap in the topo pilot.

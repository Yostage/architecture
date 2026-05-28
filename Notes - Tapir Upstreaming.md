# Notes - Tapir Upstreaming

Working notes for contributing the six Tapir commands built for the Archicad pilot ([[CLAUDE]]) back to upstream **ENZYME-APD/tapir-archicad-automation**. The fork lives at `D:\code\tapir-fork` (separate repo from this vault).

**Why:** The pilot needed six new Tapir JSON commands. Rather than keep them local-only, the working ones go upstream. Upstream merges **one command per PR** (e.g. CreateLamps, RebuildView each their own PR), so the messy multi-command dev branch gets split into clean per-command PRs.

## Status

As of 2026-05-28:

| PR | Command | State | Notes |
|----|---------|-------|-------|
| [#391](https://github.com/ENZYME-APD/tapir-archicad-automation/pull/391) | `CreateTexts` | ✅ **MERGED** (2026-05-24) into `origin/main` as `a0c519d` | Review feedback addressed pre-merge (extract `ParseJustificationString` + `SetTextContentAndParagraphs`) |
| [#394](https://github.com/ENZYME-APD/tapir-archicad-automation/pull/394) | `GoToView` (renamed from `OpenView` 2026-05-28) | 🟡 OPEN, redundancy-with-`ChangeWindow` question raised + answered | Branch `Yostage:feat/open-view` (kept the branch name), latest commit `1acdcd6`. AC27+ guarded (`ACAPI_View_GoToView` not on AC25/26). Renamed to match the underlying C API and to avoid `OpenProject`-style file-load implication. |
| [#395](https://github.com/ENZYME-APD/tapir-archicad-automation/pull/395) | `CreateMeshes` line-display fields | 🟡 OPEN, changes requested → addressed | Branch `Yostage:feat/mesh-display-fields`, latest commit `ec623c0`. Fix: `levelPen`/`contourPen` changed from `Int32`+cast to `short` directly. |
| — | `CreateView` | 🔧 WIP, lowest priority | Returns `0x8106006a` from `NewNavigatorView`; GoToView covers nav. Not in upstream queue. |
| — | `Set3DProjection` | ⬜ Queued | AC29-guarded; non-pilot primitive |
| — | `SetModelViewOptions` | ⬜ Queued | AC29-guarded (check `MigrationHelper.hpp` first); non-pilot primitive |

`tapir-backlog-commands` is the dev branch / safe backup holding all six commands including the CreateView WIP and the personal `build_ac29.bat` (also not upstreamed).

## Where things live

- **Fork repo on disk**: `D:\code\tapir-fork`
- **Git remotes**: `origin` = ENZYME-APD (upstream), `fork` = Yostage. The Yostage repo had to be **deleted and re-forked** (2026-05-20) because it was a standalone repo, not a real GitHub fork — cross-repo PRs were blocked until then.
- **Local AC29 build**: `cmake --build archicad-addon/Build/AC29 --config RelWithDebInfo` (DevKit at `archicad-addon/Build/DevKits/AC29`; CMake globs `Sources/` so new `.cpp` files need no `CMakeLists` edit).
- **Hot-reload Tapir into a running Archicad**: Tapir-self-`QuitArchicad` → wait for `:19723` socket to close → `cp Build/AC29/RelWithDebInfo/TapirAddOn_AC29_Win.apx Deploy/` → relaunch `C:\Program Files\Graphisoft\Archicad 29\Archicad.exe`. `Deploy/` is the custom add-on dir Archicad is pointed at (not in the system Add-Ons folder). Socket comes back up in ~25-30s; verify the new command is loaded via `API.IsAddOnCommandAvailable`. The `archicad-addon/Tools/update_addon_and_restart_archicad.py` script does the same thing if you prefer.

See [[Source - Tapir Fork Build Setup]] for full build mechanics.

## Upstreaming conventions

No `CONTRIBUTING.md` exists in upstream; the conventions below are inferred from merged PRs and the review thread:

- **One command per PR** — clean per-command branches off `origin/main`, single conventional-commit (`feat(scope): ...`).
- **Open as draft first** — first-time-contributor PRs can't trigger upstream CI without maintainer approval, so verify the matrix on the fork before flipping to ready.
- **CI matrix**: `.github/workflows/archicad_addon_build_check.yml` triggers `on: [push, pull_request]` and builds AC25-29 × Win+Mac × Debug+RelWithDebInfo = 20 jobs (10 if counting one config per matrix cell). All must pass.
- **Fork-side CI iteration pattern**: push to `ci/<name>-check` throwaway branch first to run the full matrix on the fork (workflow triggers on push). Iterate without involving the maintainer. Only after green, push to `feat/<name>` and open the upstream PR. Established by CreateTexts; reused by GoToView. Delete the throwaway branch once the real one is up.
- **`MigrationHelper.hpp`** provides inline shims for newer APIs absent in older DevKits (e.g. `ACAPI_Navigator_GetNavigatorItem`, `ACAPI_Database_ChangeCurrentDatabase`). **Check it before adding a `#if defined (ServerMainVers_NNNN)` guard** — the migration helper may already cover the version delta. Only add a guard if the API is genuinely new (e.g. `ACAPI_Navigator_NewNavigatorView` is AC29-only).
- **Each new command needs an example script in `Examples/`.** Pattern for IDs: use built-in `API.GetNavigatorItemTree` to enumerate (NOT a Tapir command). See `get_and_set_view_settings.py` for the recursive walker idiom.
- **Error message style**: no trailing periods (match existing `"navigatorItemId is corrupt or missing"`, not `"...missing."`).
- **Version string in `RegisterCommand<>`**: looks like add-on version when the command was authored, not strictly monotonic. Match the latest semantically (CreateTexts and GoToView both used `"1.4.2"`).
- **Naming the verb**: `Open*` is for loading from disk (`OpenProject`); `Change*` is for in-project navigation (`ChangeWindow`); for thin wrappers over a C API, prefer the API's own verb (`ACAPI_View_GoToView` → `GoToView`). Avoid colloquial Archicad-UI terms ("open this view") if Tapir's convention disagrees.

## Maintainer review patterns (tlorantfy)

Lessons from the per-command review thread — apply these *before* opening the next PR so we don't burn a review round on them.

- **No duplicated blocks across commands** — if ~15+ lines look like another command's, extract a free function and call it from both. Surfaced on #391 between `CreateLabels` and `CreateTexts`; fixed by introducing a shared helper.
- **Extract small parsers/converters by name** — when mapping a JSON string to an enum (e.g. justification, ridge mode), spin it out as `Parse{Thing}String(GS::UniString) → API_{Thing}TypeID` so other commands can reuse it. tlorantfy explicitly named the expected signature on #391.
- **Avoid `static_cast` to API types — pick the right C++ type from the start.** The Archicad API uses `short` for pen indices and other small ints. Declare the local as `short` (or whichever API type the field expects) and pass it to `parameters.Get` directly — don't read into `Int32` then cast. tlorantfy flagged this on #395 (`levelPen`). Existing precedent in the same file: `short linePenIndex` in `CreatePolyLinesCommand` (`ElementCreationCommands.cpp:646`).
- **Match the idiom of the nearest sibling command** — if the PR claims to follow another command's shape (we said #395 mirrored `CreatePolyLines`), actually mirror it. The cast slip on #395 was a self-inflicted divergence from the very precedent the PR body cited.
- **Pre-flight duplication grep**: before opening any PR, `git grep` for the C++ APIs your command calls. If existing call sites share a non-trivial idiom (~5+ lines AND duplicate error messages), extract a helper in the same PR. Skip the round-trip by doing it upfront. *Caveat:* if extraction would touch unrelated commands or the shared part is only 2 lines, leave the duplication.
- **Tone of the thread**: tlorantfy is polite and specific, gives the exact rename/signature he wants. Acknowledge, push the fix as a new commit on the same branch, and reply that it's addressed; he re-reviews and approves quickly (turnaround on #391 was same-day).

## Lessons learned per command

### CreateMeshes (#395)
- **Scope expansion**: The original backlog scope was just `ridges`+`showLines` (~2 fields, ~25 LOC). Following Scott's question "is there some reasonable expansion to make it a better PR?", inventoried `API_MeshType` for natural siblings and proposed 3 expansion tiers (line-display / drawing-set look / full appearance). Picked the middle "line-display" tier — kept the PR coherent (one concept: how mesh lines look) while doubling the new-field count past "this is just a tweak" risk. **For future narrow backlog commands**: scan the relevant API struct for natural sibling fields under the same conceptual umbrella, present tiers, let user pick.
- **Screenshot skill for visual verification**: Visual verification via the screenshot skill (`~/.claude/skills/screenshot/`) catches what return-code checking can't. Default-mesh vs styled-mesh side-by-side screenshot showed magenta lines as concrete proof the fields flow to rendering. Use `-WindowTitle '*project name*' -BringToFront -DelayMs 800` for Archicad — `-ProcessName Archicad` alone may capture a side-panel sub-window instead of the document canvas if Chrome or another app is in front.
- **OpenProject quoting**: When calling Tapir's `OpenProject` from bash/curl, Windows backslashes in `projectFilePath` get eaten by shell escaping → "invalid JSON format" error. Use Python (`urllib.request` + `json.dumps`) for any path-containing Tapir call rather than constructing JSON in the shell.

### GoToView (#394, originally named OpenView)
- **False start #1**: The backlog code used `ACAPI_Database_ChangeCurrentDatabase(&navigatorItem.db)` for view activation. That changes the *logical* current database but does NOT reactivate the UI window — the API returns success, the data layer switches, but the user sees no visible change. The correct API is **`ACAPI_View_GoToView(guidStr)`** which is the canonical UI-level view activation (`ACAPI_View.h`). Always test view-changing commands visually, not just by checking the return code. The bug would have shipped if Scott hadn't asked "I'm not sure I saw anything."
- **False start #2**: After switching to GoToView, the AC29-only local build still passed but the fork CI matrix failed on AC25/AC26 with `error C3861: 'ACAPI_View_GoToView': identifier not found`. The throwaway-CI iteration pattern caught this exactly as pre-flight review predicted ("don't assert AC25 availability without checking"). **Key insight on version macros**: each DevKit's `ACAPinc.h` defines `ServerMainVers_NNNN` for its own version *and all earlier versions*, so `#if defined (ServerMainVers_2700)` is TRUE on AC27+ DevKits and FALSE on AC25/26. Use this pattern for any API that's not available on every DevKit in the matrix.
- **Helper extraction skipped**: No `Parse...` helper extraction in #394 because duplication is only 2 lines + different surrounding envelopes (passed pre-flight grep).
- **Naming arc**: Originally opened as `OpenView` because the Archicad UI calls this "open the view." tlorantfy then asked whether the command is redundant with `GetDatabaseIdFromNavigatorItemId` + `ChangeWindow`. It isn't — `ChangeWindow` switches the underlying database/window but doesn't apply the View's saved settings (layer combo, scale, MVO, dim, zoom), which is what `ACAPI_View_GoToView` does (Graphisoft docs: "simulates the action when you open a view from the Project Navigator"). Renamed to `GoToView` 2026-05-28 to match the C API and to avoid the `OpenProject` (file-from-disk) verb collision. Branch name kept as `feat/open-view` for PR continuity.

### CreateTexts (#391)
- **Helper extraction came from review, not pre-flight**: `ParseJustificationString` and `SetTextContentAndParagraphs` were extracted post-review at tlorantfy's request. Going forward, do the duplication grep before opening the PR.
- **Re-fork required**: The original `Yostage/tapir-archicad-automation` repo was a standalone clone, not a GitHub fork. Cross-repo PRs were blocked until it was deleted and re-forked from `ENZYME-APD/tapir-archicad-automation`.

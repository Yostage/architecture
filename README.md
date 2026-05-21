# Architecture Vault

Workspace for the **Archicad automation** project with Shawn Kemna (PBW Architects).

## Running the topo pilot demo

Pre-reqs (one-time): Python 3.12+, ODA File Converter, Archicad 29 with the **forked Tapir** loaded (`D:\code\tapir-fork`; needed for the `ridges` mesh field + `CreateTexts` labels — see [[Source - Tapir Fork Build Setup]]), the DWG/DXF in place.

```powershell
py -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe run_demo.py
```

`run_demo.py` regenerates the payloads, clears existing meshes/texts, POSTs the mesh (with `ridges=UserDefined` → clean contour lines, not triangulation) and the contour elevation labels (`CreateTexts`), then fits the window — fully scripted, no manual Archicad steps. Hit **F3** for 3D, **O** for orbit.

*Stock-Tapir fallback (no fork): set the Mesh tool DEFAULT to "Show User-Defined Ridges" + "All Ridges Smooth" with nothing selected and save the project, so recreated meshes inherit the clean-contour display; labels can't be auto-placed.*

Background: [[Summary - Finishing the Pilot]] (what it took), [[Source - Lot 44 Survey DWG]] (pipeline), [[Source - Shawn Topo Difference Video]] (why the display matters), [[Source - Pilot Inferred Parameters]] (encoded constants).

## Goal
Find high-leverage Archicad workflows to automate via AI / MCP integration, starting with discrete pilots that prove value before tackling broader process changes.

## Index
- [[Email - Archicad Bizniss]] — running thread with Shawn (Apr–May 2026)
- [[Source - YouTube Topography Mesh]] — Arch Guide tutorial summary (current manual process for topo)
- [[Source - Lot 44 Survey DWG]] — probe of Shawn's example survey DWG (the "before" file)
- [[Source - Pilot Inferred Parameters]] — what the pilot actually has to infer vs. read from the input (3 read, 11 inferred)
- [[Source - Shawn Topo Difference Video]] — Shawn's 2026-05-20 explainer: drawing-set output needs topo LINES, not triangulation
- [[Source - Proper Example2 Tutorial File]] — the real .pln: a 3-step tutorial; step 3 = definitive target (clean contour lines + labels, property-line perimeter)
- [[Source - Tapir Fork Build Setup]] — local build of the Tapir add-on works (toolchain, gotchas, build commands, iteration loop)
- [[Research - Archicad MCPs]] — survey of MCP servers and AI plugins for Archicad
- [[Research - Tapir Command Reference]] — full inventory of Tapir JSON commands (~134, all 14 groups)
- [[Research - Competitor BIM AI Integrations]] — how Archicad stacks up vs Revit / Rhino / Vectorworks
- [[Synthesis - Automation Opportunities]] — pilot candidates ranked, with a recommended starting point
- [[Summary - Finishing the Pilot]] — what it took to close the contour-label gap: Tapir fork build, the six commands, validation, cross-version CI, and upstreaming CreateTexts (PR #391)
- [[Future Work]] — gaps, Tapir extensions to upstream, asks of Shawn, next pilots

## Stakeholders
- **Shawn Kemna** — principal, PBW Architects (`shawn@pbwarchitects.com`). Domain expert, has Archicad v29 installed, rusty on day-to-day production but knows the firm's workflows.
- **Scott** (me) — software / automation side.

## Context (as of 2026-05-04)
- PBW does mostly single-family residential — less repetition than commercial, so automation candidates need to be picked carefully.
- Archicad's built-in AI assistant (v29) is weak — basically a "find tool" / command helper. Real leverage is via the **Tapir add-on + MCP**.
- Shawn proposed three concrete candidates: 3D topo from survey, interior elevation setup, detail import/generation.

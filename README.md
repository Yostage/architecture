# Architecture Vault

Workspace for the **Archicad automation** project with Shawn Kemna (PBW Architects).

## Running the topo pilot demo

Pre-reqs (one-time): Python 3.12+, ODA File Converter, Archicad 29 with Tapir add-on installed, the DWG/DXF in place.

```powershell
py -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
```

**Demo workflow:** keep ONE configured demo project — set the **Mesh tool default** to "Show User-Defined Ridges" (Floor Plan and Section) + "All Ridges Smooth" (Model) with nothing selected, then **save the project**. Open it in Archicad (Tapir loaded), then:

```powershell
.venv\Scripts\python.exe run_demo.py
```

The script regenerates the payload, deletes all existing meshes/labels, recreates the mesh, and fits the window. The recreated mesh **inherits the saved Mesh tool default**, so the plan shows clean contour lines (no triangulation) with no per-run toggling. Hit **F3** for 3D, **O** for orbit. See [[Source - Lot 44 Survey DWG]] for the full pipeline writeup, [[Source - Shawn Topo Difference Video]] for why the display default matters, and [[Source - Pilot Inferred Parameters]] for the constants the pilot encodes.

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
- [[Future Work]] — gaps, Tapir extensions to upstream, asks of Shawn, next pilots

## Stakeholders
- **Shawn Kemna** — principal, PBW Architects (`shawn@pbwarchitects.com`). Domain expert, has Archicad v29 installed, rusty on day-to-day production but knows the firm's workflows.
- **Scott** (me) — software / automation side.

## Context (as of 2026-05-04)
- PBW does mostly single-family residential — less repetition than commercial, so automation candidates need to be picked carefully.
- Archicad's built-in AI assistant (v29) is weak — basically a "find tool" / command helper. Real leverage is via the **Tapir add-on + MCP**.
- Shawn proposed three concrete candidates: 3D topo from survey, interior elevation setup, detail import/generation.

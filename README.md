# Architecture Vault

Workspace for the **Archicad automation** project with Shawn Kemna (PBW Architects).

## Goal
Find high-leverage Archicad workflows to automate via AI / MCP integration, starting with discrete pilots that prove value before tackling broader process changes.

## Index
- [[Email - Archicad Bizniss]] — running thread with Shawn (Apr–May 2026)
- [[Source - YouTube Topography Mesh]] — Arch Guide tutorial summary (current manual process for topo)
- [[Source - Lot 44 Survey DWG]] — probe of Shawn's example survey DWG (the "before" file)
- [[Source - Pilot Inferred Parameters]] — what the pilot actually has to infer vs. read from the input (3 read, 11 inferred)
- [[Research - Archicad MCPs]] — survey of MCP servers and AI plugins for Archicad
- [[Research - Tapir Command Reference]] — full inventory of Tapir JSON commands (~134, all 14 groups)
- [[Research - Competitor BIM AI Integrations]] — how Archicad stacks up vs Revit / Rhino / Vectorworks
- [[Synthesis - Automation Opportunities]] — pilot candidates ranked, with a recommended starting point

## Stakeholders
- **Shawn Kemna** — principal, PBW Architects (`shawn@pbwarchitects.com`). Domain expert, has Archicad v29 installed, rusty on day-to-day production but knows the firm's workflows.
- **Scott** (me) — software / automation side.

## Context (as of 2026-05-04)
- PBW does mostly single-family residential — less repetition than commercial, so automation candidates need to be picked carefully.
- Archicad's built-in AI assistant (v29) is weak — basically a "find tool" / command helper. Real leverage is via the **Tapir add-on + MCP**.
- Shawn proposed three concrete candidates: 3D topo from survey, interior elevation setup, detail import/generation.

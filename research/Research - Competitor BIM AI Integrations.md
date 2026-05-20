# Research - Competitor BIM AI integrations

How Archicad's AI/MCP story stacks up against competitors. Done 2026-05-04.

## Short answer
**Yes — Revit's integration is materially easier and more polished than Archicad's.** Revit 2027 ships an **official, first-party MCP server built into the product** (no add-on, no Tapir, no Python). Archicad has nothing official; both Archicad MCP options require installing the community Tapir add-on first.

## Ranked by ease of Claude integration

### 1. Revit (Autodesk) — easiest *(if on 2027)*
- **Revit 2027 has a built-in MCP server.** One-time setup in Claude Desktop, no plugin to install.
- Claude reads live model data (rooms, areas, doors, parameters) from an open project.
- Multiple community MCPs also exist (`revit-mcp/revit-mcp`, `PiggyAndrew/revit_mcp`) for older versions.
- Autodesk also published a **cloud-side MCP** ("AEC Data Model MCP server") on Autodesk Platform Services for queries against cloud BIM data — a path Archicad has no equivalent for.

### 2. Rhino / Grasshopper — easy, mature
- `RhinoMcpServer` connects Rhino to Claude over MCP for natural-language modeling.
- Rhino's scripting story (RhinoCommon, Grasshopper, Rhino.Inside) was already strong, so MCP wrappers are thin.
- Active discussion of using MCP to drive **Rhino.Inside.Revit** workflows — i.e. orchestrate Revit *via* Rhino with AI.

### 3. Archicad — community-only, requires Tapir
- See [[Research - Archicad MCPs]]. Two community MCPs, both wrap the **Tapir add-on**. No first-party support.
- Graphisoft community has an active wishlist asking for native MCP — not delivered as of May 2026.

### 4. Vectorworks / others — laggards
- No notable MCP servers surfaced in search.
- Generally seen as behind Revit and Rhino on programmatic AI access.

## Implication for the PBW project
The pure-engineering answer is "use Revit." But that's not the question. PBW already runs Archicad, has files in Archicad, has trained staff on Archicad. **Switching BIM platforms to chase a smoother MCP is not a real option** — it's a multi-year migration.

What's worth communicating to Shawn:
- **The Archicad ecosystem is genuinely behind** on AI integration. We're not imagining it.
- **The Tapir + community MCP path is the only realistic on-ramp** for Archicad today.
- **It still works.** Tapir exposes 137 commands; Claude can drive them. The 90% of value (automating the workflows in Shawn's email) is achievable on Archicad — it just costs more setup than Revit would.
- **Watch Graphisoft for native MCP.** If/when they ship it, much of the toolchain we build on Tapir will simplify.

## Sources
- [Revit 2027: built-in MCP server in practice — BIMsmith blog](https://blog.bimsmith.com/Revit-2027-What-the-Built-In-MCP-Server-Actually-Does-in-Practice)
- [revit-mcp/revit-mcp on GitHub](https://github.com/revit-mcp/revit-mcp)
- [PiggyAndrew/revit_mcp on GitHub](https://github.com/PiggyAndrew/revit_mcp)
- [Talk to Your BIM — Autodesk Platform Services blog](https://aps.autodesk.com/blog/talk-your-bim-exploring-aec-data-model-mcp-server-claude)
- [archilabs.ai — Revit MCP overview](https://archilabs.ai/posts/revit-model-context-protocol)
- [Local MCP for Rhino.Inside.Revit — McNeel Forum](https://discourse.mcneel.com/t/local-mcp-server-to-drive-rhino-inside-revit-workflows-with-ai/215629)
- [6 MCP Servers for 3D — Snyk](https://snyk.io/articles/6-mcp-servers-for-using-ai-to-generate-3d-models/)
- [Graphisoft community wishlist for native MCP](https://community.graphisoft.com/t5/Wishlist/MCP-Protocol-Integration-for-Archicad-Critical-for-Competitive/idi-p/669090)

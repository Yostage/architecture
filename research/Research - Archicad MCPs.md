# Research - Archicad MCPs and Claude plugins

Survey of what currently exists for wiring Claude (or any LLM agent) into Archicad. Done 2026-05-04.

> **Update (2026-05-20):** The pilot drove Tapir directly over HTTP (`127.0.0.1:19723`), not via an MCP server, and we **forked Tapir** to add commands (the predicted "fork if we hit a ceiling" path) — see [[Source - Tapir Fork Build Setup]]. MCP wrapping is still future work ([[Future Work]]).

## TL;DR
- Two community MCP servers exist; both rely on the **Tapir add-on** as the actual bridge into Archicad. Tapir is the load-bearing dependency, not the MCP wrapper.
- **`SzamosiMate/tapir-archicad-MCP`** is the more substantial of the two — exposes 137 commands (Tapir + official JSON API merged) and ships local semantic search so the LLM can discover the right tool.
- **`lgradisar/archicad-mcp`** is a thinner wrapper around Tapir's JSON commands; lets you add custom tools in `custom_tools.py`.
- Graphisoft has **no first-party MCP** yet. There's a [community wishlist post](https://community.graphisoft.com/t5/Wishlist/MCP-Protocol-Integration-for-Archicad-Critical-for-Competitive/idi-p/669090) pushing for one.
- The Archicad v29 built-in **AI Assistant** is essentially a smart command-finder. Confirms Shawn's read.

## Core dependency: Tapir Add-On
- Open-source Archicad add-on that extends Archicad's official JSON API with many more commands.
- Both MCP servers are fundamentally Tapir wrappers.
- **Has to be installed in Archicad before any of this works.** First step of any pilot.

## Option A — `SzamosiMate/tapir-archicad-MCP` *(recommended)*
Repo: https://github.com/SzamosiMate/tapir-archicad-MCP

- **137 tools** auto-generated from Tapir + official JSON API.
- **Local semantic search** (sentence-transformers + faiss-cpu) — the LLM does a two-step *discover → call* flow, so it doesn't have to load all 137 schemas into context.
- 100% local — no data leaves the machine, no API keys.
- Multi-instance: can drive multiple running Archicads at once.
- Install: Python 3.12+, `uv`, edit `claude_desktop_config.json`, run via `uvx --from tapir-archicad-mcp archicad-server`.
- **Maturity caveat**: README explicitly says "early stage / experimental."

## Option B — `lgradisar/archicad-mcp`
Repo: https://github.com/lgradisar/archicad-mcp

- Thinner: auto-compiles Tapir JSON commands into MCP tools.
- Extension point: add custom tools in `custom_tools.py`.
- Install: clone, `uv sync`, configure `claude_desktop_config.json` with repo path + Python path.
- Better fit if we want to **author our own bespoke tools** (e.g. an "import survey topo" macro) rather than expose the whole Tapir surface.

## Other AI tools (non-MCP, mostly tangential)
From [myarchitectai.com — 8 Best AI Tools for Archicad in 2026](https://www.myarchitectai.com/blog/archicad-ai-tools): mostly rendering / image-gen / concept tools (MyArchitectAI, Lookx, etc.). None of them automate production drafting, which is what Shawn actually wants.

## Claude Code plugins / Agent SDK
- Claude Code's plugin system is general-purpose; could host a slash command like `/topo-mesh` that invokes the Tapir MCP under the hood.
- **Claude Agent SDK** could wrap the same Tapir API directly without going through MCP — more code to write, but tighter control. Worth considering if the MCP layer becomes a bottleneck.

## Recommendation for our pilot
1. Install **Tapir add-on** in Archicad v29.
2. Stand up **`SzamosiMate/tapir-archicad-MCP`** in Claude Desktop. Lowest-effort path to "Claude can talk to Archicad."
3. If we hit ceiling (missing commands, custom workflows that span multiple commands), drop down to **`lgradisar/archicad-mcp`** and write custom tools — or fork Tapir and add Archicad commands directly.

## Sources
- [tapir-archicad-MCP (SzamosiMate)](https://github.com/SzamosiMate/tapir-archicad-MCP)
- [archicad-mcp (lgradisar)](https://github.com/lgradisar/archicad-mcp)
- [Archicad × Claude Desktop on LobeHub](https://lobehub.com/mcp/tiagoengdigital-archicad-mcp-claude)
- [ArchiCAD MCP Server overview — Skywork](https://skywork.ai/skypage/en/archicad-ai-engineer-bim/1980493499208421376)
- [PulseMCP — Archicad MCP Server](https://www.pulsemcp.com/servers/lgradisar-archicad)
- [Graphisoft community wishlist for official MCP](https://community.graphisoft.com/t5/Wishlist/MCP-Protocol-Integration-for-Archicad-Critical-for-Competitive/idi-p/669090)
- [8 Best AI Tools for Archicad in 2026](https://www.myarchitectai.com/blog/archicad-ai-tools)
- [Revit MCP comparison — archilabs.ai](https://archilabs.ai/posts/revit-model-context-protocol)

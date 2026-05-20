# Synthesis - Automation Opportunities

Synthesis of [[Email - Archicad Bizniss]], [[Source - YouTube Topography Mesh]], and [[Research - Archicad MCPs]]. Goal: answer Shawn's open question — "discrete topo pilot OR higher-level map of possibilities?" The honest answer is **both, in that order**.

## Big picture
The leverage isn't "Archicad has AI." It's **"Archicad has a scriptable JSON API (via Tapir) that an LLM can drive."** Once that bridge is up, every workflow Shawn listed reduces to: *can the LLM combine the right Tapir commands?* That reframes the question from "what can AI do" to "which manual workflows are bottlenecked on rote command-chaining."

## Three tiers of automation we can offer

### Tier 1 — Deterministic macros (no AI needed)
Workflows where the inputs are structured and the output is mechanical. AI is overkill; a Python script over the Tapir API gets it done and is maintainable. **Topo mesh fits here.** The video confirms the manual process is just: trace each contour, type its elevation, don't touch the perimeter. All of that is deterministic if we can read elevations off the survey.

### Tier 2 — LLM-assisted workflows
Workflows where inputs are messy or judgment is required, but the operations themselves are well-defined. **Interior elevations fit here.** Naming follows a pattern (`ROOM NAME <Orientation>`) but the LLM has to know which rooms are which, what counts as "interior," and the right scale per project. View/sheet navigation is rote once the LLM knows the targets.

### Tier 3 — Knowledge-augmented generation
Workflows where the firm has tacit standards. **Detail generation fits here.** The v2 ask (generate a wall-assembly detail from parameters) is genuinely an AI problem — needs a library of past details + LLM reasoning to compose new ones.

## Mapping Shawn's three candidates

| # | Candidate | Tier | Effort | Payoff | Notes |
|---|-----------|------|--------|--------|-------|
| 1 | 3D topo from survey | **1** (deterministic) | Low | Medium | Best as a *learning pilot* — proves Tapir+MCP works end-to-end. |
| 2 | Interior elevations | **2** (LLM-assisted) | Medium | **High** | Shawn's "biggest bang for buck." Repetitive, navigation-heavy, low learning value to do by hand. |
| 3 | Detail import → generation | **1 → 3** | Low → High | Medium → High | v1 (database import) is easy. v2 (generation) is a real research project. |

## Recommendation
**Two-track approach:**

### Track A: Topo pilot (1–2 weeks, low risk)
- Install Tapir add-on in Archicad v29.
- Stand up `SzamosiMate/tapir-archicad-MCP` in Claude Desktop.
- Ship a `/topo-mesh` workflow: input survey DWG → output 3D mesh with correct contour elevations and untouched perimeter.
- **Real goal of the pilot is not the topo tool itself** — it's to validate the toolchain (Tapir → MCP → Claude → Archicad), confirm what the API actually exposes, and surface the gaps before we scope IE work.

### Track B: Interior elevations scoping
- In parallel with Track A, have Shawn record a screen capture of him doing IE setup on a real project end-to-end.
- Catalog every Tapir command we'd need; identify gaps.
- IE setup is the highest-value target per Shawn, but it crosses Project Map / View Map / Layouts — touchier API surface than topo. Worth scoping before committing.

### Track C (later): Detail library
- Park v1 (detail import from a curated file) as a follow-on once Tracks A and B are established.
- v2 (generation) needs a corpus of past details — should be a separate conversation about what data PBW has and is willing to feed in.

## Risks / unknowns
- **Tapir surface area**: 137 commands sounds broad, but neither MCP advertises specific support for sheets/layouts. Topo and IE both need verification that the necessary commands exist.
- **Single-family = less repetition**: Shawn already flagged this. Tools that are amazing on a 50-room commercial project may save 10 minutes on a single-family. We should pick workflows that hit *every* project (IE setup does) rather than ones that only shine on big jobs.
- **MCP server maturity**: Both options say "experimental." Expect to upstream bug fixes or fork.
- **SketchUp integration**: Shawn just connected it on Apr 30. Worth asking what he's using it for — if it overlaps with topo (importing 3D site geometry from SketchUp), it might change the topo pilot scope.

## Next conversation with Shawn
1. Pitch the two-track plan.
2. Confirm he can install Tapir add-on (or that we can on his machine).
3. Ask for a screen-capture of an IE setup on a real project.
4. Ask what he's doing with SketchUp now that it's connected.

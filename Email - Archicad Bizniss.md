# Email - Archicad Bizniss

Thread between Shawn Kemna (PBW Architects) and Scott, Apr 28 – May 4, 2026.

## 2026-04-28 — Shawn (kickoff)
- Wants to first understand what current Archicad already does before scoping automation.
- Hasn't done full production in several years; will canvass the office for ideas.
- Two broad camps for automation:
	1. Elements **generated from the BIM model** (plans, sections, elevations)
	2. **2D drafted elements**
- Has Archicad **v29** installed, hasn't tested its built-in AI assistant.
- Reviews the **v29 AI Assistant** as limited: mostly find-and-select tool / command helper.
	- https://www.youtube.com/watch?v=n-4f_1xY8A8
	- https://www.youtube.com/watch?v=w6at_tJbIXg
	- https://www.youtube.com/watch?v=zoMa4kll_Hw
- Notes Archicad lags other BIM software for AI; flags community **Archicad MCP Server** but found examples underwhelming / hard to follow.
	- https://skywork.ai/skypage/en/archicad-ai-engineer-bim/1980493499208421376
	- https://www.myarchitectai.com/blog/archicad-ai-tools

## 2026-04-30 — Scott
- "Looks like they added SketchUp integration today."

## 2026-04-30 — Shawn
- "Oooh. Just connected it." — wired up the SketchUp integration immediately.

## 2026-05-04 — Shawn (the real meat)
After office meeting + thinking. Key framing: **single-family residential has less repetition than larger projects**, so automation candidates are narrower. Pick discrete wins.

Three candidates, ordered by how he framed them:

### 1. 3D topo model from survey *(suggested as a discrete starter)*
Convert 2D linework from surveyors into a 3D mesh.
- Reference video for current process: https://www.youtube.com/watch?v=1OprRjQEEiA
- Steps today:
	1. Import 2D topo lines
	2. Create mesh over lines
	3. Eyedrop-select each line, convert to mesh topo, input height offset
	4. Delete 2D lines

### 2. Interior elevation setup *(Shawn flags as highest bang-for-buck)*
Repetitive, time-consuming, low learning value, but trickier — involves view/sheet navigation.
- Steps today:
	1. Select IE tag from menu, edit settings before placing
	2. Reference ID → `IE |`
	3. Name → `ROOM NAME <OrientationShort>`
	4. Place rectangle just beyond interior surfaces to generate tag
	5. In Organizer: drag views from Project Map → Views (under INTERIOR ELEVATION folder)
	6. Select all → settings: scale, layer combination, zooming = Fit in Window, etc.
	7. Drag views onto sheet (multi-drag auto-lays-out)

### 3. Detail import / generation
- Many details are similar/identical project-to-project.
- v1 ask: select details and import from a database.
- v2 ask: **generate** details from input parameters (wall assembly, floor assembly, trim detail).
- Current "automated" process: keep a separate file of standard details open, import views via Organizer between files.

## Open question Shawn left on the table
> "If you're still interested, I think the 3d topo mesh is a good, discreet one to start OR another angle is we just talk higher level of different methods you see to automate things and what are the broad possibilities."

→ Need to come back with: a recommended starter pilot **and** a higher-level map of what's possible. See [[Synthesis - Automation Opportunities]].

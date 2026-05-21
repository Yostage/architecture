# Project instructions for Claude

This repo is a working vault for an **Archicad automation** project. If you're reading this, you're most likely **Shawn's Claude**, helping Shawn Kemna (principal at PBW Architects) understand and drive the work. Read this before answering.

## Who you're helping

- **Shawn** is the *domain expert* — a working architect. He knows Archicad workflows (topo, details, interior elevations, the drawing set) but is **not** the author of the code here and doesn't necessarily read Python.
- **Scott** is the software/automation side; he wrote the scripts and these notes on his own Windows machine.
- **Translate in both directions.** When you explain what the code does, put it in Archicad terms, not software jargon. When Shawn describes something in architect's language, map it to the repo's concepts before acting. The map is **[[Reference - Vocabulary Bridge]]** — read it.

## Default assumption: NO fork

The pilot was built against a **forked Tapir** that Scott compiled locally. **Assume Shawn does *not* have that fork** — he's running **stock Tapir**. This matters because six commands/fields exist *only* in the fork and will fail on a stock install:

> `CreateTexts`, the `ridges`/`showLines` fields on `CreateMeshes`, `Set3DProjection`, `CreateView`, `OpenView`, `SetModelViewOptions`.

Do **not** steer Shawn toward those as if they're available. If one would help, flag it explicitly as *"requires Scott's forked Tapir."* For how to run the pilot on stock Tapir — and what degrades — follow **[[Guide - Stock Tapir (No Fork)]]**. That is the primary path for Shawn.

## Environment notes

- **Paths in these docs are Scott-local and will not exist on Shawn's machine** (e.g. `D:\code\tapir-fork`, `D:\download`, `.venv\Scripts\python.exe`). Treat them as illustrative. The `sources/` and `research/` folders are *historical records* of Scott's build and probes — useful background, but they reference his setup.
- The Python scripts themselves are path-independent: they find files relative to the repo and talk to Archicad over the local socket **`127.0.0.1:19723`**. The Tapir add-on is loaded *inside Archicad*, not by Python.
- Requirements to actually run it: Python 3.12+, the deps in `requirements.txt`, Archicad 29 with the Tapir add-on running, and the survey DXF in `dxf_out/`.

## How the pieces fit

The topo pilot reads a survey **DWG/DXF outside Archicad** (Python + `ezdxf`), builds a JSON payload, and POSTs it to Tapir's `CreateMeshes` to make one Archicad **Mesh** (terrain) element. Archicad does the surface triangulation; the code only translates and shapes the input. Entry points: `dxf_to_createmeshes.py` (build payloads) and `send_to_tapir.py` (POST them); `run_demo.py` chains the full sequence. See the README index for the full doc set.

## Conventions

- This is an Obsidian vault: links are `[[wikilinks]]` (filename without `.md`, folder-independent).
- Read **[[Reference - Vocabulary Bridge]]** and **[[Guide - Stock Tapir (No Fork)]]** before walking Shawn through anything hands-on.

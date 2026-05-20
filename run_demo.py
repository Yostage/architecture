"""
End-to-end topo pilot demo runner.

Regenerates the mesh + labels payloads from the DXF, POSTs both to Tapir, then
fits the Archicad window to the mesh. Single command, no copy/paste.

Pre-reqs:
  - Python venv with requirements.txt installed (.venv/Scripts/python.exe)
  - Archicad 29 running with the Tapir add-on, listening on 127.0.0.1:19723
  - A project open (use a fresh empty one for a clean demo)
  - dxf_out/survey topo test.dxf present (produced from the DWG via ODA File Converter)

Produces: a property-line mesh with contour level lines.

Workflow: keep ONE configured demo project (Mesh tool DEFAULT set to "Show
User-Defined Ridges" + "All Ridges Smooth", then saved). At runtime this script
deletes all meshes/labels and recreates them, so the recreated mesh INHERITS the
preserved display default and shows clean contour lines in plan — no per-run
toggling needed. (Set the default with nothing selected: double-click the Mesh
tool → Mesh Default Settings; the title must say "Default", not "Selection".)

Contour elevation labels are not placed here — Tapir's CreateLabels can't bind a
standalone text label (see Future Work.md).

Run:
  .venv\\Scripts\\python.exe run_demo.py
"""

import subprocess
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

HERE = Path(__file__).parent
PY = sys.executable


def step(label: str, *args: str) -> None:
    print(f"\n=== {label} ===")
    result = subprocess.run([PY, *args], cwd=HERE)
    if result.returncode != 0:
        sys.exit(f"Step failed: {label}")


def main():
    step("Regenerate payloads", "dxf_to_createmeshes.py")
    step("Ping Tapir", "send_to_tapir.py", "ping")
    # Clear prior demo output so re-runs stay clean (idempotent). NOTE: this
    # deletes ALL meshes/texts/labels in the project — intended for the demo
    # project, not a real working file.
    step("Clear existing meshes/texts/labels", "send_to_tapir.py", "clear")
    step("POST mesh (ridges=UserDefined -> clean contour-line display)", "send_to_tapir.py", "send-mesh")
    # Contour elevation labels via forked Tapir 1.4.2 CreateTexts (standalone
    # Text elements — supersedes the old CreateLabels approach that couldn't
    # place clean text). Requires the fork loaded; see Source - Tapir Fork Build Setup.
    step("POST contour elevation labels (CreateTexts)", "send_to_tapir.py", "send-texts")
    step("Fit the most recently created mesh in window", "fit_latest_mesh.py")
    print("\nDone. Mesh (property-line perimeter, user-defined ridges) + contour")
    print("elevation labels placed — fully scripted, no manual tool-default step.")
    print("Switch to plan for the drawing-set view; F3 for 3D, O to orbit.")


if __name__ == "__main__":
    main()
